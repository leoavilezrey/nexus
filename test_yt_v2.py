
import youtube_transcript_api
print(f"Library contents: {dir(youtube_transcript_api)}")
from youtube_transcript_api import YouTubeTranscriptApi
print(f"YouTubeTranscriptApi contents: {dir(YouTubeTranscriptApi)}")
try:
    video_id = "DrkDfUxl_EM"
    # Try the way it's used in the app
    ytt_api = YouTubeTranscriptApi()
    print(f"Instance created: {ytt_api}")
    transcript_list = ytt_api.list(video_id)
    print(f"Transcript list found: {transcript_list}")
    transcript = transcript_list.find_generated_transcript(['es', 'en'])
    print(f"Transcript object: {transcript}")
    full_transcript = transcript.fetch()
    print(f"Type of full_transcript: {type(full_transcript)}")
    if full_transcript:
        item = full_transcript[0]
        print(f"Type of item: {type(item)}")
        print(f"Item contents: {item}")
        try:
            print(f"item['text'] = {item['text']}")
        except Exception as e:
            print(f"Error accessing ['text']: {e}")
            print(f"Item attributes: {dir(item)}")
except Exception as e:
    print(f"Execution error: {e}")
