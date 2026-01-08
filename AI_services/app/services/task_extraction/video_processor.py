from moviepy.editor import VideoFileClip
import tempfile
import os
from audio_processor import process_audio

def process_video(video_path: str) -> list[dict]:
    """
    process video using moviepy + whisper + Langchain

    pipeline:
    1. Extract audio (moviepy)
    2. Transcribe (Whisper)
    3. Extract task (Langchain + OLLAMA)

    Input: Video path
    Output: List of tasks
    """
    print(f"processing video: {video_path}")

    #Extract audio
    video = VideoFileClip(video_path)
    audio = video.audio

    temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    audio.write_audiofile(temp_audio.name, verbose=False, logger=None)
    
    print(f"    Audio extracted")

    try: 
        tasks = process_audio(temp_audio.name)
        return tasks
    finally:
        os.remove(temp_audio.name)