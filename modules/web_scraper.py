import re
from urllib.parse import urlparse, parse_qs
from core.database import nx_db, RegistryCreate, TagCreate
from rich.console import Console

console = Console()

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

def ingest_web_resource(url: str, tags: list[str], db_target=nx_db):
    """
    Determina si la URL es de YouTube o una página web genérica,
    extrae el contenido y lo guarda en la base de datos especificada (Local o Staging).
    """
    if not requests or not BeautifulSoup:
        console.print("[bold white on red]Faltan librerías. Por favor instala: requests y beautifulsoup4[/]")
        return None

    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    if "youtube.com" in domain or "youtu.be" in domain:
        try:
            return _ingest_youtube(url, parsed_url, tags, db_target)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]⚠️  Descarga de YouTube interrumpida (Ctrl+C).[/bold yellow]")
            return None
    else:
        try:
            return _ingest_generic_web(url, tags, db_target)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]⚠️  Descarga web interrumpida (Ctrl+C).[/bold yellow]")
            return None

def _get_youtube_video_id(url: str, parsed_url) -> str:
    """Extrae el ID del video de YouTube a partir de la URL."""
    if "youtu.be" in parsed_url.netloc:
        return parsed_url.path.lstrip('/')
    if "youtube.com" in parsed_url.netloc:
        qs = parse_qs(parsed_url.query)
        if 'v' in qs:
            return qs['v'][0]
    return ""

def _ingest_youtube(url: str, parsed_url, tags: list[str], db_target):
    """Extrae título y subtítulos de un video de YouTube."""
    if not YouTubeTranscriptApi or not yt_dlp:
        console.print("[bold white on red]Faltan librerías para YouTube. Instala: youtube-transcript-api y yt-dlp[/]")
        return None
        
    video_id = _get_youtube_video_id(url, parsed_url)
    if not video_id:
        console.print(f"[yellow]No se pudo extraer de ID de video de YouTube para: {url}[/yellow]")
        return None
        
    title = f"YouTube Video ({video_id})"
    content_raw = ""
    
    # Intentar obtener métricas y metadatos usando yt-dlp
    meta_info = {"video_id": video_id, "platform": "youtube"}
    try:
        class MyLogger:
            def debug(self, msg): pass
            def warning(self, msg): pass
            def error(self, msg): pass

        ydl_opts = {
            'quiet': True, 
            'no_warnings': True, 
            'logger': MyLogger(),
            'extract_flat': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if info_dict:
                title = info_dict.get('title', title)
                meta_info.update({
                    "channel": info_dict.get('uploader'),
                    "duration": info_dict.get('duration'),
                    "view_count": info_dict.get('view_count'),
                    "upload_date": info_dict.get('upload_date'),
                    "description": info_dict.get('description', '')[:500] # Primeras lineas
                })
    except Exception as e:
        # Fallback silencioso para el título si yt-dlp falla
        pass

    # Obtener transcripción
    try:
        # Intenta primero español, luego inglés si falla u otros.
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        # Buscar transcript manual antes de los generados (idioma es o en)
        try:
            transcript = transcript_list.find_manually_created_transcript(['es', 'en'])
        except Exception:
            # Si no encuentra manual, agarrar cualquiera o el generado
            try:
                transcript = transcript_list.find_generated_transcript(['es', 'en'])
            except:
                # Si no hay es/en, agarrar el primero disponible
                transcript = next(iter(transcript_list))
            
        full_transcript = transcript.fetch()
        
        text_fragments = [item.text if hasattr(item, "text") else item["text"] for item in full_transcript]
        content_raw = " ".join(text_fragments)
        
        if len(content_raw) > 50000:
            content_raw = content_raw[:49997] + "..."
            
    except Exception as e:
        error_msg = str(e).split('\n')[0] or type(e).__name__
        console.print(f"[yellow]Aviso: No se pudo obtener la transcripción. Se guardará sin texto base. ({error_msg})[/yellow]")
        content_raw = "(Video guardado sin Transcripción Disponible)."

    # Insertar en BD
    try:
        data = RegistryCreate(
            type="youtube",
            title=title,
            path_url=url,
            content_raw=content_raw,
            meta_info=meta_info
        )
        reg = db_target.create_registry(data)
        
        # Asociar tags
        for t in tags:
            db_target.add_tag(reg.id, TagCreate(value=t))
            
        return reg
    except Exception as e:
        console.print(f"[bold white on red]Error guardando en base de datos: {e}[/]")
        return None

def get_playlist_video_urls(playlist_url: str):
    """
    Usa yt-dlp para obtener todas las URLs de videos de una playlist.
    """
    urls = []
    try:
        class MyLogger:
            def debug(self, msg): pass
            def warning(self, msg): pass
            def error(self, msg): pass

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'logger': MyLogger(),
            'extract_flat': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
            if 'entries' in playlist_info:
                for entry in playlist_info['entries']:
                    if entry.get('url'):
                        # yt-dlp a veces devuelve solo el ID o el path, aseguramos URL completa
                        video_url = entry['url']
                        if not video_url.startswith('http'):
                            video_url = f"https://www.youtube.com/watch?v={video_url}"
                        urls.append(video_url)
    except Exception as e:
        console.print(f"[red]Error extrayendo playlist: {e}[/]")
    return urls

def batch_ingest_urls(urls_list: list[str], tags: list[str], db_target=nx_db):
    """
    Procesa un lote de URLs secuencialmente.
    Retorna (un proceso exitoso, un proceso fallido).
    """
    total = len(urls_list)
    success = []
    failed = []
    
    try:
        for i, url in enumerate(urls_list):
            url = url.strip()
            if not url: continue
            
            console.print(f"\n[bold cyan][{i+1}/{total}][/] Procesando: [dim]{url}[/]")
            reg = ingest_web_resource(url, tags, db_target=db_target)
            if reg:
                success.append(reg)
            else:
                failed.append(url)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]⚠️  Proceso de ingesta por lote interrumpido por el usuario (Ctrl+C).[/bold yellow]")
        console.print(f"[white]Se han guardado {len(success)}/{(i+1) if 'i' in locals() else len(urls_list)} registros procesados hasta ahora.[/white]")
            
    return success, failed


def _ingest_generic_web(url: str, tags: list[str], db_target):
    """Extrae título y párrafos limpiados de una página web."""
    try:
        # Añadir cabeceras comunes para evitar bloqueos básicos de web servers (403 Prohibidden)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        console.print(f"[yellow]Aviso: Ocurrió un error conectando a la página (puede requerir JS o estar bloqueada). Se guardará la URL huérfana. Error: {str(e)}[/yellow]")
        # Guardado básico de rescate para url
        try:
            reg = db_target.create_registry(RegistryCreate(
                type="web", title=url, path_url=url, content_raw="Error al raspar el contenido web."
            ))
            for t in tags:
                db_target.add_tag(reg.id, TagCreate(value=t))
            return reg
        except:
             return None
             
    soup = BeautifulSoup(res.text, 'html.parser')

    # Obtener el Título
    title = soup.title.string.strip() if soup.title and soup.title.string else url

    # Limpiar tags basura que no aportan al raw text
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        tag.decompose()

    # Extraer texto de párrafos y divs de manera legible
    paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
    content_raw = "\n\n".join([p.get_text(separator=' ', strip=True) for p in paragraphs if p.get_text(strip=True)])
    
    if len(content_raw) > 50000:
            content_raw = content_raw[:49997] + "..."
            
    try:
        data = RegistryCreate(
            type="web",
            title=title,
            path_url=url,
            content_raw=content_raw,
            meta_info={"platform": "web"}
        )
        reg = db_target.create_registry(data)
        
        for t in tags:
            db_target.add_tag(reg.id, TagCreate(value=t))
            
        return reg
    except Exception as e:
        console.print(f"[bold white on red]Error guardando en base de datos: {e}[/]")
        return None
