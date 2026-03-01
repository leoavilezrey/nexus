
from youtube_transcript_api import YouTubeTranscriptApi
import sys

def test_logic(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        try:
            transcript = transcript_list.find_manually_created_transcript(['es', 'en'])
        except Exception:
            transcript = transcript_list.find_generated_transcript(['es', 'en'])
            
        full_transcript = transcript.fetch()
        
        # The new logic
        text_fragments = [item.text if hasattr(item, "text") else item["text"] for item in full_transcript]
        content_raw = " ".join(text_fragments)
        
        print(f"Successfully extracted {len(content_raw)} characters.")
        print(f"Snippet: {content_raw[:100]}...")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    video_id = "DrkDfUxl_EM"
    test_logic(video_id)
