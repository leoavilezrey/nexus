
import os
import sys
import json
import time
import logging
from datetime import datetime

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from core.database import SessionLocal, Registry, Card, Tag
from agents.deepseek_agent import deepseek_agent
from rich.console import Console

# Forzar salida UTF-8 para evitar errores de charmap en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

console = Console()

LOGS_DIR = os.path.join(root_dir, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, f"optimizacion_ia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def optimize_nexus_ia():
    db = SessionLocal()
    
    # 1. Identificar registros que necesitan trabajo de IA
    all_yt = db.query(Registry).filter(Registry.type == 'youtube').all()
    
    targets = []
    for reg in all_yt:
        # Detectar si tiene contenido real y no mensajes de bloqueo
        has_transcript = reg.content_raw and "Transcripcion Disponible" not in reg.content_raw and "IpBlocked" not in reg.content_raw and len(reg.content_raw) > 200
        has_summary = reg.summary and len(reg.summary) > 50 and "Sin resumen" not in reg.summary
        
        card_count = db.query(Card).filter(Card.parent_id == reg.id).count()
        has_cards = card_count > 0
        
        job = None
        if has_transcript and not has_summary:
            job = "FULL_IA"
        elif has_summary and not has_cards and has_transcript:
            job = "ONLY_CARDS"
        elif has_transcript and not has_cards:
            job = "ONLY_CARDS"
            
        if job:
            targets.append({'reg': reg, 'job': job})

    if not targets:
        console.print("[bold green]Todo al dia! No hay videos con transcripcion que necesiten IA actualmente.[/bold green]")
        return

    console.print(f"[bold cyan]Se encontraron {len(targets)} videos para optimizar con DeepSeek.[/bold cyan]")
    
    success_count = 0
    
    try:
        for item in targets:
            reg = item['reg']
            job = item['job']
            
            # Limpiar ttulo para evitar errores de renderizado
            clean_title = reg.title.encode('ascii', 'ignore').decode('ascii')[:60]
            console.print(f"\n[bold]Trabajando en ID {reg.id}:[/bold] {clean_title}...")
            console.print(f"  Tarea: [yellow]{job}[/yellow]")
            
            if job == "FULL_IA":
                resumen, cards = deepseek_agent.process_content(reg.title, reg.content_raw)
                if resumen and "Sin resumen" not in resumen:
                    reg.summary = resumen
                    db.query(Card).filter(Card.parent_id == reg.id).delete()
                    for c in cards:
                        db.add(Card(parent_id=reg.id, question=c['question'], answer=c['answer'], type="DeepSeek_AI"))
                    success_count += 1
                    console.print("  [green]Resumen y Flashcards generados.[/green]")
                else:
                    console.print("  [red]DeepSeek fallo en generar contenido completo.[/red]")

            elif job == "ONLY_CARDS":
                _, cards = deepseek_agent.process_content(reg.title, reg.content_raw)
                if cards:
                    db.query(Card).filter(Card.parent_id == reg.id).delete()
                    for c in cards:
                        db.add(Card(parent_id=reg.id, question=c['question'], answer=c['answer'], type="DeepSeek_AI"))
                    success_count += 1
                    console.print("  [green]Flashcards generadas exitosamente.[/green]")
                else:
                    console.print("  [red]No se pudieron generar las flashcards.[/red]")
            
            db.commit()
            time.sleep(2)

    except KeyboardInterrupt:
        console.print("\n[yellow]Proceso pausado por el usuario.[/yellow]")
    finally:
        db.close()
        console.print(f"\n[bold green]Fin del proceso. Actualizados: {success_count} registros.[/bold green]")

if __name__ == "__main__":
    optimize_nexus_ia()
