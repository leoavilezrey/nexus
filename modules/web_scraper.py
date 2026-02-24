import re
from urllib.parse import urlparse, parse_qs
from core.database import nx_db, RegistryCreate, TagCreate

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

def ingest_web_resource(url: str, tags: list[str]) -> bool:
    """
    Determina si la URL es de YouTube o una página web genérica,
    extrae el contenido y lo guarda en la base de datos Nexus.
    Retorna True si tuvo éxito, False si falló.
    """
    if not requests or not BeautifulSoup:
        print("[bold white on red]Faltan librerías. Por favor instala: requests y beautifulsoup4[/]")
        return False

    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    if "youtube.com" in domain or "youtu.be" in domain:
        return _ingest_youtube(url, parsed_url, tags)
    else:
        return _ingest_generic_web(url, tags)

def _get_youtube_video_id(url: str, parsed_url) -> str:
    """Extrae el ID del video de YouTube a partir de la URL."""
    if "youtu.be" in parsed_url.netloc:
        return parsed_url.path.lstrip('/')
    if "youtube.com" in parsed_url.netloc:
        qs = parse_qs(parsed_url.query)
        if 'v' in qs:
            return qs['v'][0]
    return ""

def _ingest_youtube(url: str, parsed_url, tags: list[str]) -> bool:
    """Extrae título y subtítulos de un video de YouTube."""
    if not YouTubeTranscriptApi or not yt_dlp:
        print("[bold white on red]Faltan librerías para YouTube. Instala: youtube-transcript-api y yt-dlp[/]")
        return False
        
    video_id = _get_youtube_video_id(url, parsed_url)
    if not video_id:
        print(f"[yellow]No se pudo extraer de ID de video de YouTube para: {url}[/yellow]")
        return False
        
    title = f"YouTube Video ({video_id})"
    content_raw = ""
    
    # Intentar obtener el título usando yt-dlp
    try:
        ydl_opts = {
            'quiet': True, 
            'simulate': True, 
            'force_generic_extractor': False, 
            'no_warnings': True, 
            'extract_flat': True,
            'logger': None
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            if info_dict and 'title' in info_dict:
                 title = info_dict['title']
    except Exception as e:
        print(f"[yellow]Aviso: No se pudo obtener el título oficial vía yt-dlp. Usando ID fallback. Error: {str(e)}[/yellow]")

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
            transcript = transcript_list.find_generated_transcript(['es', 'en'])
            
        full_transcript = transcript.fetch()
        
        # Concatenar todos los fragmentos
        text_fragments = [item['text'] for item in full_transcript]
        content_raw = " ".join(text_fragments)
        
        # Limitar en Nexus V1 a ~50,000 caracteres para no romper LLM (aprox 1.5 hs de audio densos).
        # Aunque el schema lo soporta, el Agente y Active Recall lo prefieren no kilométrico.
        if len(content_raw) > 50000:
            content_raw = content_raw[:49997] + "..."
            
    except Exception as e:
        error_msg = str(e).split('\n')[0]
        print(f"[yellow]Aviso: No se pudo obtener la transcripción. Se guardará sin texto base. ({error_msg})[/yellow]")
        content_raw = "(Video guardado sin Transcripción Disponible)."

    # Insertar en BD
    try:
        data = RegistryCreate(
            type="youtube",
            title=title,
            path_url=url,
            content_raw=content_raw,
            meta_info={"video_id": video_id, "platform": "youtube"}
        )
        reg = nx_db.create_registry(data)
        
        # Asociar tags
        for t in tags:
            nx_db.add_tag(reg.id, TagCreate(value=t))
            
        return True
    except Exception as e:
        print(f"[bold white on red]Error guardando en base de datos: {e}[/]")
        return False


def _ingest_generic_web(url: str, tags: list[str]) -> bool:
    """Extrae título y párrafos limpiados de una página web."""
    try:
        # Añadir cabeceras comunes para evitar bloqueos básicos de web servers (403 Prohibidden)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"[yellow]Aviso: Ocurrió un error conectando a la página (puede requerir JS o estar bloqueada). Se guardará la URL huérfana. Error: {str(e)}[/yellow]")
        # Guardado básico de rescate para url
        try:
            reg = nx_db.create_registry(RegistryCreate(
                type="web", title=url, path_url=url, content_raw="Error al raspar el contenido web."
            ))
            for t in tags:
                nx_db.add_tag(reg.id, TagCreate(value=t))
            return True
        except:
             return False
             
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
        reg = nx_db.create_registry(data)
        
        for t in tags:
            nx_db.add_tag(reg.id, TagCreate(value=t))
            
        return True
    except Exception as e:
        print(f"[bold white on red]Error guardando en base de datos: {e}[/]")
        return False
