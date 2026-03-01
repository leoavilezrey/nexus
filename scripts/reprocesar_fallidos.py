
import os
import sys
import time
import json
import logging
from datetime import datetime

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from core.database import SessionLocal, Registry, Card, Tag, RegistryCreate, CardCreate, nx_db
from agents.deepseek_agent import deepseek_agent
from modules.web_scraper import ingest_web_resource
from modules.youtube_manager import YouTubeManager
from rich.console import Console

console = Console()

# Logs directory
LOGS_DIR = os.path.join(root_dir, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, f"reproceso_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def reprocess_incomplete_videos():
    db = SessionLocal()
    yt_manager = None
    
    # Authenticate YouTube for deletion
    try:
        if os.path.exists(os.path.join(root_dir, 'client_secrets.json')):
            yt_manager = YouTubeManager(
                credentials_path=os.path.join(root_dir, 'client_secrets.json'),
                token_path=os.path.join(root_dir, 'token.pickle')
            )
            console.print("[green]Conexion con YouTube API establecida para limpieza.[/green]")
    except Exception as e:
        console.print(f"[yellow]Aviso: No se pudo conectar con YouTube API para borrar videos: {e}[/yellow]")

    # 1. Identify videos to re-process (IpBlocked or no summary)
    # We look for those with "IpBlocked" in content_raw or very short content
    target_videos = db.query(Registry).filter(
        Registry.type == 'youtube',
        (Registry.content_raw.like('%IpBlocked%') | 
         Registry.content_raw.like('%Sin Transcripción Disponible%') |
         (Registry.summary == None) | (Registry.summary == ''))
    ).all()

    console.print(f"[cyan]Iniciando reprocesamiento de {len(target_videos)} videos...[/cyan]")
    logging.info(f"Iniciando reprocesamiento de {len(target_videos)} videos.")

    success_count = 0
    
    for reg in target_videos:
        console.print(f"\n[bold]Intentando corregir:[/bold] {reg.title[:60]}... (ID: {reg.id})")
        logging.info(f"Procesando ID {reg.id}: {reg.path_url}")
        
        # Clase Mock para capturar datos sin guardar en la BD real durante el scraping
        class MockDB:
            def create_registry(self, data): 
                # Retornamos un objeto que simula tener un ID para evitar el error en web_scraper
                from types import SimpleNamespace
                mock_reg = SimpleNamespace(**data.model_dump())
                mock_reg.id = 999
                return mock_reg
            def add_tag(self, id, tag): pass

        # 2. Re-scrape transcript
        try:
            # Ahora pasamos el MockDB para obtener el RegistryCreate object
            new_data = ingest_web_resource(reg.path_url, ["reproceso"], db_target=MockDB()) 
        except Exception as e:
            console.print(f"  [red]Error en scraping: {e}[/red]")
            new_data = None
        
        if new_data and hasattr(new_data, 'content_raw') and "IpBlocked" not in new_data.content_raw and len(new_data.content_raw) > 100:
            console.print("  [green]✓ Transcripcion recuperada exitosamente.[/green]")
            logging.info(f"ID {reg.id}: Transcripcion recuperada.")
            
            # 3. Generate IA Content
            console.print("  • Generando Inteligencia con DeepSeek...")
            resumen, cards = deepseek_agent.process_content(new_data.title, new_data.content_raw)
            
            if resumen and "Sin resumen" not in resumen:
                # 4. Update Database
                reg.content_raw = new_data.content_raw
                reg.summary = resumen
                reg.title = new_data.title # Update title if it was fallback
                
                # Delete old cards if any
                db.query(Card).filter(Card.parent_id == reg.id).delete()
                
                # Add new cards
                for c in cards:
                    db.add(Card(
                        parent_id=reg.id,
                        question=c['question'],
                        answer=c['answer'],
                        type="DeepSeek_AI"
                    ))
                
                db.commit()
                console.print(f"  [bold green]✅ Registro actualizado con éxito.[/bold green]")
                logging.info(f"ID {reg.id}: IA Generada y DB actualizada.")
                success_count += 1
                
                # 5. Optional: Deletion from YouTube
                # This is tricky because we don't have the playlist_item_id anymore.
                # However, if it's the Watch Later or a known playlist, we could search for it.
                # Since the user asked to "borra del historial de youtube los videos que se han bajao en totalidad",
                # and deletion needs a specific playlistItem_id, we'll log that we need manual deletion if not found.
                logging.info(f"ID {reg.id}: Listo para eliminacion manual o futura.")
            else:
                console.print("  [yellow]⚠️ DeepSeek no pudo generar contenido util todavia.[/yellow]")
                logging.warning(f"ID {reg.id}: DeepSeek fallo o devolvio vacio.")
        else:
            console.print("  [yellow]ℹ Sigue bloqueado o sin transcripcion.[/yellow]")
            logging.error(f"ID {reg.id}: Fallo re-scraped (Sigue Bloqueado).")

        time.sleep(10) # Delay aumentado a 10s para intentar evitar bloqueos de IP

    db.close()
    console.print(f"\n[bold green]🏁 Reproceso finalizado. Exitosos: {success_count}/{len(target_videos)}[/bold green]")
    console.print(f"Ver log detallado en: {LOG_FILE}")

if __name__ == "__main__":
    reprocess_incomplete_videos()
