
import os
import sys
import pickle
import json
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Asegurar que el directorio raíz de Nexus esté en el PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from core.database import SessionLocal, Registry

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def cleanup_youtube_queue():
    db = SessionLocal()
    
    # 1. Obtener URLs de videos que YA estan en Nexus Core y tienen resumen (completados)
    completed_videos = db.query(Registry.path_url).filter(
        Registry.type == 'youtube',
        Registry.summary != None,
        Registry.summary != '',
        ~Registry.summary.like('Sin resumen%')
    ).all()
    
    completed_urls = {r.path_url for r in completed_videos}
    
    if not completed_urls:
        print("No se encontraron videos completados para limpiar.")
        return

    print(f"Buscando {len(completed_urls)} videos en tus playlists para eliminar...")

    # 2. Autenticar
    creds = None
    token_path = os.path.join(root_dir, 'token.pickle')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Error: Requiere re-autenticacion manual. Ejecuta el Dashboard [6] primero.")
            return

    youtube = build('youtube', 'v3', credentials=creds)

    # 3. Obtener Playlists del usuario
    try:
        # Primero revisamos las de la cola
        QUEUE_FILE = r"G:\Mi unidad\Nexus_Staging\playlists_queue.txt"
        playlist_ids = []
        if os.path.exists(QUEUE_FILE):
             with open(QUEUE_FILE, 'r') as f:
                for line in f:
                    if 'list=' in line:
                        pid = line.split('list=')[-1].split('&')[0]
                        playlist_ids.append(pid)
        
        # Tambien incluimos el "Watch Later" (especial)
        # Nota: El ID de Watch Later suele ser 'WL', pero la API a veces requiere buscarla por nombre.
        # Por ahora usaremos las de la cola.
        
        total_deleted = 0
        for pid in set(playlist_ids):
            print(f"Escaneando playlist ID: {pid}")
            
            # Listar items de la playlist
            request = youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=pid,
                maxResults=50
            )
            response = request.execute()
            
            for item in response.get('items', []):
                v_id = item['contentDetails']['videoId']
                v_url = f"https://www.youtube.com/watch?v={v_id}"
                item_id = item['id']
                
                if v_url in completed_urls:
                    print(f"  [BORRANDO] {item['snippet']['title']}")
                    youtube.playlistItems().delete(id=item_id).execute()
                    total_deleted += 1
                    
        print(f"\nLimpieza completada. Se eliminaron {total_deleted} videos de YouTube.")
        
    except Exception as e:
        print(f"Error durante la limpieza: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_youtube_queue()
