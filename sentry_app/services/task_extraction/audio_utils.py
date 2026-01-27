"""
Audio utility functions for audio file format conversion.

Note: AssemblyAI accepts most audio formats directly, so conversion is typically
not needed. These utilities are kept for edge cases where format conversion helps.
"""
import os
from moviepy.editor import AudioFileClip


def convert_to_wav(input_path: str, output_path: str = None) -> str:
    """
    Convert audio file to WAV format (16kHz mono).

    Note: AssemblyAI accepts most formats directly, so this is typically not needed.
    Kept for edge cases or preprocessing requirements.

    Args:
        input_path: Path to input audio file (mp3, m4a, etc.)
        output_path: Optional output path. If None, creates temp file.

    Returns:
        Path to converted WAV file
    """
    if output_path is None:
        # Create output path with .wav extension
        base = os.path.splitext(input_path)[0]
        output_path = f"{base}_converted.wav"

    print(f"  Converting {input_path} to WAV format...")

    # Load audio and convert to mono, 16kHz
    audio = AudioFileClip(input_path)
    audio.write_audiofile(
        output_path,
        fps=16000,  # 16kHz sample rate
        nbytes=2,   # 16-bit
        codec='pcm_s16le',  # PCM signed 16-bit little-endian
        ffmpeg_params=["-ac", "1"]  # Mono
    )
    audio.close()

    print(f"  ✅ Converted to: {output_path}")
    return output_path


def is_wav_format(audio_path: str) -> bool:
    """Check if file is already in WAV format."""
    return audio_path.lower().endswith('.wav')
