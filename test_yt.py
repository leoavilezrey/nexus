
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    video_id = "DrkDfUxl_EM" # The one from the user request
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_generated_transcript(['es', 'en'])
    full_transcript = transcript.fetch()
    print(f"Type of full_transcript: {type(full_transcript)}")
    if len(full_transcript) > 0:
        print(f"Type of first item: {type(full_transcript[0])}")
        print(f"First item: {full_transcript[0]}")
        try:
            print(f"First item ['text']: {full_transcript[0]['text']}")
        except Exception as e:
            print(f"Error accessing ['text']: {e}")
except Exception as e:
    print(f"Global error: {e}")
