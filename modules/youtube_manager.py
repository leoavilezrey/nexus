
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Permisos necesarios para gestionar playlists (Lectura y Escritura)
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

class YouTubeManager:
    """
    Gestor oficial de YouTube via Data API v3.
    Permite leer, listar y ELIMINAR videos de playlists (limpieza de cola).
    """
    def __init__(self, credentials_path='client_secrets.json', token_path='token.pickle'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.youtube = self._authenticate()

    def _authenticate(self):
        creds = None
        # El archivo token.pickle almacena los tokens de acceso y refresco del usuario
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Si no hay credenciales validas, pedir login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"No se encontro '{self.credentials_path}'. Necesitas descargar este archivo desde Google Cloud Console.")
                
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('youtube', 'v3', credentials=creds)

    def get_playlist_items(self, playlist_id):
        """Lista todos los videos (IDs y URLs) de una playlist."""
        videos = []
        request = self.youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=playlist_id,
            maxResults=50
        )
        response = request.execute()

        for item in response.get('items', []):
            video_id = item['contentDetails']['videoId']
            playlist_item_id = item['id'] # Necesario para eliminarlo luego
            title = item['snippet']['title']
            videos.append({
                'id': video_id,
                'playlist_item_id': playlist_item_id,
                'title': title,
                'url': f"https://www.youtube.com/watch?v={video_id}"
            })
        return videos

    def remove_video_from_playlist(self, playlist_item_id):
        """Elimina un video de la playlist usando su ID de item (no el ID de video)."""
        try:
            self.youtube.playlistItems().delete(id=playlist_item_id).execute()
            return True
        except Exception as e:
            print(f"Error al eliminar video de la playlist: {e}")
            return False

    def get_playlist_id_from_url(self, url):
        """Extrae el ID de la playlist de una URL."""
        from urllib.parse import urlparse, parse_qs
        query = urlparse(url).query
        params = parse_qs(query)
        return params.get('list', [None])[0]
