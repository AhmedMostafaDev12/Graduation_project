"""
Audio Processor - AssemblyAI Integration
=========================================

Processes audio files using AssemblyAI for transcription and Groq for task extraction.

Pipeline:
1. Audio file (any format) → AssemblyAI transcription
2. Transcript → Groq LLM extracts tasks

Features:
- Multi-language auto-detection (100+ languages)
- Speaker diarization (who said what)
- No local model downloads required
- Cloud-based processing

Author: Sentry AI Team
Date: 2025
"""

import os
import assemblyai as aai  # type: ignore
from typing import List, Dict, Tuple
from dotenv import load_dotenv

# Import your existing text extractor (uses Groq)
try:
    from .text_extractor import extract_task_from_text
except ImportError:
    from sentry_app.services.task_extraction.text_extractor import extract_task_from_text

load_dotenv()


# ============================================================================
# ASSEMBLYAI CONFIGURATION
# ============================================================================

def _initialize_assemblyai():
    """Initialize AssemblyAI with API key from environment"""
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise ValueError(
            "ASSEMBLYAI_API_KEY not found in environment variables. "
            "Get your API key from https://www.assemblyai.com"
        )
    aai.settings.api_key = api_key
    print("[OK] AssemblyAI initialized")


# ============================================================================
# TRANSCRIPTION
# ============================================================================

def transcribe_audio(
    audio_path: str,
    enable_speaker_labels: bool = True,
    language_detection: bool = True
) -> Dict:
    """
    Transcribe audio file using AssemblyAI.

    Args:
        audio_path: Path to audio file (any format: mp3, m4a, wav, etc.)
        enable_speaker_labels: Enable speaker diarization (who said what)
        language_detection: Auto-detect language (supports 100+ languages)

    Returns:
        Dictionary with transcription results:
        {
            "text": "Full transcript",
            "utterances": [{"speaker": "A", "text": "...", "start": 0, "end": 1000}],
            "language": "en",
            "confidence": 0.95,
            "audio_duration": 120.5
        }
    """
    _initialize_assemblyai()

    print(f"\n{'='*80}")
    print(f"AUDIO TRANSCRIPTION - AssemblyAI")
    print(f"{'='*80}")
    print(f"File: {audio_path}")

    # Verify file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Configure transcription
    config = aai.TranscriptionConfig(
        speech_model=aai.SpeechModel.best,  # Use best quality model
        speaker_labels=enable_speaker_labels,  # Enable speaker diarization
        language_detection=language_detection,  # Auto-detect language
        punctuate=True,  # Add punctuation
        format_text=True  # Format text (capitalization, etc.)
    )

    print(f"  Uploading and transcribing...")
    print(f"  Speaker labels: {enable_speaker_labels}")
    print(f"  Language detection: {language_detection}")

    # Create transcriber and process
    transcriber = aai.Transcriber(config=config)
    transcript = transcriber.transcribe(audio_path)

    # Check for errors
    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(f"Transcription failed: {transcript.error}")

    print(f"\n  [OK] Transcription complete!")
    print(f"  Language: {getattr(transcript, 'language_code', 'auto-detected')}")
    print(f"  Duration: {transcript.audio_duration:.1f} seconds")
    print(f"  Confidence: {transcript.confidence:.2%}")
    print(f"  Characters: {len(transcript.text)}")

    # Build result dictionary
    result = {
        "text": transcript.text,
        "language": getattr(transcript, 'language_code', None),
        "confidence": transcript.confidence,
        "audio_duration": transcript.audio_duration,
        "utterances": []
    }

    # Add speaker-separated utterances if available
    if enable_speaker_labels and transcript.utterances:
        result["utterances"] = [
            {
                "speaker": utt.speaker,
                "text": utt.text,
                "start": utt.start,
                "end": utt.end,
                "confidence": utt.confidence
            }
            for utt in transcript.utterances
        ]
        print(f"  Speakers detected: {len(set(utt['speaker'] for utt in result['utterances']))}")

    return result


# ============================================================================
# TASK EXTRACTION PIPELINE
# ============================================================================

def process_audio(
    audio_path: str,
    save_transcript: bool = True,
    translate: bool = True
) -> Tuple[List[Dict], str, Dict]:
    """
    Complete pipeline: Transcribe audio + Extract tasks.

    Pipeline:
    1. AssemblyAI transcription (cloud-based, multi-language)
    2. Groq LLM task extraction (with translation if needed)

    Args:
        audio_path: Path to audio file (any format)
        save_transcript: Save transcript to file
        translate: Translate non-English text to English

    Returns:
        Tuple of (tasks, transcript_text, transcription_metadata)
        - tasks: List of extracted task dictionaries
        - transcript_text: Full transcript text
        - transcription_metadata: Speaker info, language, etc.
    """
    print(f"\n{'='*80}")
    print(f"AUDIO TASK EXTRACTION PIPELINE")
    print(f"{'='*80}")
    print(f"Processing: {audio_path}")

    # Step 1: Transcribe with AssemblyAI
    print(f"\n[1/3] Transcribing audio with AssemblyAI...")
    transcription = transcribe_audio(audio_path, enable_speaker_labels=True)
    transcript_text = transcription["text"]

    # Save transcript if requested
    if save_transcript:
        save_transcript_to_file(audio_path, transcript_text, transcription)

    # Step 2: Extract tasks with Groq LLM
    print(f"\n[2/3] Extracting tasks with Groq LLM...")
    tasks, _ = extract_task_from_text(transcript_text, translate=translate)

    print(f"\n[3/3] Task extraction complete!")
    print(f"  [OK] Found {len(tasks)} tasks")

    # Display tasks summary
    if tasks:
        print(f"\n  Tasks extracted:")
        for i, task in enumerate(tasks, 1):
            print(f"    {i}. {task.get('title', 'Untitled')}")
            if task.get('deadline'):
                print(f"       Due: {task['deadline']}")
            if task.get('priority'):
                print(f"       Priority: {task['priority']}")

    print(f"\n{'='*80}")
    print(f"[OK] Audio Processing Complete!")
    print(f"{'='*80}\n")

    return tasks, transcript_text, transcription


def save_transcript_to_file(
    audio_path: str,
    transcript_text: str,
    transcription_metadata: Dict
):
    """
    Save transcript and metadata to files.

    Creates two files:
    1. {filename}_transcript.txt - Raw transcript
    2. {filename}_metadata.txt - Speaker info, language, etc.
    """
    # Create uploads/audio directory if it doesn't exist
    uploads_dir = os.path.join(
        os.path.dirname(__file__), "utils", "uploads", "audio"
    )
    os.makedirs(uploads_dir, exist_ok=True)

    # Generate filenames
    audio_filename = os.path.basename(audio_path)
    base_name = os.path.splitext(audio_filename)[0]

    # Save transcript
    transcript_file = os.path.join(uploads_dir, f"{base_name}_transcript.txt")
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript_text)
    print(f"  [OK] Transcript saved: {transcript_file}")

    # Save metadata (speaker info, language, etc.)
    metadata_file = os.path.join(uploads_dir, f"{base_name}_metadata.txt")
    with open(metadata_file, "w", encoding="utf-8") as f:
        f.write(f"Audio File: {audio_filename}\n")
        f.write(f"Language: {transcription_metadata.get('language') or 'unknown'}\n")
        f.write(f"Duration: {transcription_metadata.get('audio_duration', 0):.1f}s\n")
        f.write(f"Confidence: {transcription_metadata.get('confidence', 0):.2%}\n")
        f.write(f"\n{'='*60}\n")
        f.write(f"TRANSCRIPT\n")
        f.write(f"{'='*60}\n\n")

        # If speaker labels available, format with speakers
        if transcription_metadata.get('utterances'):
            f.write("Speaker-separated transcript:\n\n")
            for utt in transcription_metadata['utterances']:
                f.write(f"Speaker {utt['speaker']}: {utt['text']}\n\n")
        else:
            f.write(transcript_text)

    print(f"  [OK] Metadata saved: {metadata_file}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_transcript_only(audio_path: str) -> str:
    """Quick function to get just the transcript text"""
    transcription = transcribe_audio(audio_path)
    return transcription["text"]


def get_speakers(audio_path: str) -> List[Dict]:
    """Get speaker-separated utterances"""
    transcription = transcribe_audio(audio_path, enable_speaker_labels=True)
    return transcription.get("utterances", [])


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example of using the audio processor with AssemblyAI.
    """
    import sys

    # Example audio file (replace with your own)
    test_audio = r"C:\Users\USER\Documents\Sound Recordings\Recording (3).m4a"

    if len(sys.argv) > 1:
        test_audio = sys.argv[1]

    if not os.path.exists(test_audio):
        print(f"Error: File not found: {test_audio}")
        print(f"\nUsage: python audio_processor.py [audio_file]")
        sys.exit(1)

    try:
        # Process audio file
        tasks, transcript, metadata = process_audio(
            test_audio,
            save_transcript=True,
            translate=True
        )

        # Display results
        print(f"\n{'='*80}")
        print(f"RESULTS SUMMARY")
        print(f"{'='*80}")
        print(f"\nTranscript ({len(transcript)} chars):")
        print(f"{transcript[:500]}..." if len(transcript) > 500 else transcript)
        print(f"\nTasks: {len(tasks)}")
        for i, task in enumerate(tasks, 1):
            print(f"\n{i}. {task.get('title', 'Untitled')}")
            if task.get('description'):
                print(f"   {task['description']}")
            if task.get('deadline'):
                print(f"   Due: {task['deadline']}")
            if task.get('priority'):
                print(f"   Priority: {task['priority']}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
