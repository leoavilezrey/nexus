
import os
import json
import time
from datetime import datetime
from modules.web_scraper import get_playlist_video_urls, ingest_web_resource
from agents.deepseek_agent import deepseek_agent
from core.database import nx_db, RegistryCreate, CardCreate, TagCreate
from core.staging_db import staging_db
from rich.console import Console
from rich.progress import Progress

console = Console()

QUEUE_FILE = r"G:\Mi unidad\Nexus_Staging\playlists_queue.txt"
HISTORY_FILE = r"G:\Mi unidad\Nexus_Staging\playlists_history.json"

from modules.youtube_manager import YouTubeManager

def run_youtube_pipeline():
    """
    Ejecuta el plan de trabajo automatizado para playlists:
    1. Lee cola de playlists.
    2. Descarga a Staging (G:).
    3. Procesa con DeepSeek.
    4. Mueve a Nexus Local.
    5. Opcional: Elimina el video de la playlist de YouTube (via API).
    """
    # Asegurar que el Buffer de Staging esté inicializado
    staging_db.init_staging()

    yt_manager = None
    if os.path.exists('client_secrets.json'):
        try:
            # Forzamos un timeout corto para no bloquear el inicio si no hay red
            with console.status("[dim]Estableciendo conexión con YouTube API...[/dim]", spinner="dots"):
                yt_manager = YouTubeManager()
                console.print("[bold green]✓ Conexión con YouTube API establecida (Modo Gestión Activo).[/bold green]")
        except Exception as e:
            console.print(f"[yellow]Aviso: No se pudo conectar con YouTube API. Se usará Modo Scraping (Modo Rescate). {e}[/yellow]")
            yt_manager = None

    if not os.path.exists(QUEUE_FILE):
        console.print(f"[yellow]Aviso: No se encontro el archivo de cola en {QUEUE_FILE}[/yellow]")
        return

    # Cargar historial
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)

    with open(QUEUE_FILE, 'r') as f:
        playlists_urls = [line.strip() for line in f if line.strip() and line.strip() not in history]

    if not playlists_urls:
        console.print("[green]No hay nuevas playlists para procesar en la cola.[/green]")
        return

    console.print(f"[bold cyan]🚀 Iniciando Pipeline para {len(playlists_urls)} playlists...[/bold cyan]")

    for p_url in playlists_urls:
        console.print(f"\n[bold yellow]📂 Procesando Playlist:[/] {p_url}")
        
        videos_to_process = []
        playlist_id = None
        
        # Intentar obtener videos via API oficial si esta disponible
        if yt_manager:
            playlist_id = yt_manager.get_playlist_id_from_url(p_url)
            if playlist_id:
                videos_to_process = yt_manager.get_playlist_items(playlist_id)
        
        # Fallback a yt-dlp si la API fallo o no esta disponible
        if not videos_to_process:
            raw_urls = get_playlist_video_urls(p_url)
            if raw_urls:
                videos_to_process = [{'url': u, 'title': u, 'playlist_item_id': None} for u in raw_urls]
            else:
                # Si no es playlist, es un video individual. Lo agregamos para procesar.
                videos_to_process = [{'url': p_url, 'title': p_url, 'playlist_item_id': None}]

        console.print(f"   • {len(videos_to_process)} recursos detectados para procesar.")
        
        for v_data in videos_to_process:
            v_url = v_data['url']
            v_item_id = v_data['playlist_item_id']
            
            console.print(f"\n   [cyan]»[/] Procesando: [italic]{v_data['title']}[/italic]")
            
            # 2. Descarga masiva a Staging (G:)
            reg_staging = ingest_web_resource(v_url, ["pipeline_staging"], db_target=staging_db)
            
            if reg_staging:
                # 3. Procesamiento Inteligente con DeepSeek
                console.print(f"     • Generando Inteligencia con DeepSeek...")
                resumen, cards = deepseek_agent.process_content(reg_staging.title, reg_staging.content_raw)
                
                # 4. Centralizacion en Nexus (Local SSD)
                try:
                    data_final = RegistryCreate(
                        type="youtube",
                        title=reg_staging.title,
                        path_url=reg_staging.path_url,
                        content_raw=reg_staging.content_raw,
                        summary=resumen,
                        meta_info=reg_staging.meta_info,
                        is_flashcard_source=True
                    )
                    reg_nexus = nx_db.create_registry(data_final)
                    
                    # Agregar tags y cards
                    nx_db.add_tag(reg_nexus.id, TagCreate(value="YouTube_Pipeline"))
                    for c in cards:
                        nx_db.create_card(CardCreate(
                            parent_id=reg_nexus.id,
                            question=c['question'],
                            answer=c['answer'],
                            type="DeepSeek_AI"
                        ))
                    
                    console.print(f"     [bold green]✅ Centralizado en Nexus ID {reg_nexus.id}[/bold green]")
                    
                    # 5. ELIMINACIÓN DEL HISTORIAL DE YOUTUBE (Gestión de Cola)
                    if yt_manager and v_item_id:
                        if yt_manager.remove_video_from_playlist(v_item_id):
                            console.print(f"     [bold blue]🗑️  Video eliminado de la playlist de YouTube (Cola despejada).[/bold blue]")
                        else:
                            console.print(f"     [yellow]⚠️ No se pudo eliminar de YouTube, pero el dato ya esta en Nexus.[/yellow]")

                except Exception as e:
                    console.print(f"     [bold red]❌ Error moviendo a Nexus: {e}[/bold red]")
            else:
                console.print(f"     [bold red]⚠️  Fallo ingesta de video {v_url}[/bold red]")
            
            # Pequeña pausa para mitigar bloqueos de IP (Rate Limiting)
            time.sleep(2)

        # Actualizar historial local
        history.append(p_url)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
        
        console.print(f"[green]✓ Playlist {p_url} completada.[/green]")

    console.print("\n[bold green]🏁 Pipeline finalizado con exito.[/bold green]")
