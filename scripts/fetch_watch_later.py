
import os
import pickle
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Permisos
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
QUEUE_FILE = r"G:\Mi unidad\Nexus_Staging\playlists_queue.txt"

def fetch_watch_later_videos():
    creds = None
    token_path = 'token.pickle'
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    youtube = build('youtube', 'v3', credentials=creds)

    print("🔎 Listando tus playlists disponibles...")
    try:
        playlists_request = youtube.playlists().list(
            part="snippet,contentDetails",
            mine=True,
            maxResults=50
        )
        playlists_response = playlists_request.execute()
        
        print("\n--- Playlists Encontradas ---")
        found_ids = []
        for pl in playlists_response.get('items', []):
            title = pl['snippet']['title']
            p_id = pl['id']
            print(f"📌 {title} (ID: {p_id})")
            found_ids.append((p_id, title))
        print("-----------------------------\n")

        if not found_ids:
            print("⚠️ No se encontraron playlists accesibles en esta cuenta.")
            return

        video_urls = []
        
        for p_id, p_title in found_ids:
            print(f"🚀 Extrayendo videos de: {p_title}...")
            next_page_token = None
            playlist_count = 0
            
            while playlist_count < 50 and len(video_urls) < 150: # Limite total y por playlist
                request = youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=p_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                response = request.execute()
                
                items = response.get('items', [])
                if not items: break

                for item in items:
                    v_id = item['contentDetails']['videoId']
                    v_url = f"https://www.youtube.com/watch?v={v_id}"
                    if v_url not in video_urls:
                        video_urls.append(v_url)
                        playlist_count += 1
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token or len(video_urls) >= 150:
                    break
            
            print(f"   ✅ +{playlist_count} videos añadidos.")

        if video_urls:
            print(f"\n✨ Total recolectado: {len(video_urls)} videos.")
            
            os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
            with open(QUEUE_FILE, 'a') as f:
                for url in video_urls:
                    f.write(url + "\n")
            
            print(f"🚀 URLs inyectadas en la cola de Nexus: {QUEUE_FILE}")
        else:
            print("⚠️ No se pudieron extraer videos de ninguna playlist.")
            
    except Exception as e:
        print(f"❌ Error en la comunicación con YouTube: {e}")


if __name__ == "__main__":
    fetch_watch_later_videos()
