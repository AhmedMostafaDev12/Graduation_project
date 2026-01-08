import json
import wave
import os
from vosk import Model, KaldiRecognizer
from text_extractor import extract_task_from_text
from audio_utils import convert_to_wav, is_wav_format

# Lazy loading: only load model when needed
vosk_model = None

def _get_vosk_model():
    """Lazy load Vosk model on first use."""
    global vosk_model
    if vosk_model is None:
        print("Loading Vosk model...")
        # TODO: Update this path to your downloaded Vosk model directory
        # Download models from: https://alphacephei.com/vosk/models
        # Recommended: vosk-model-en-us-0.22 (1.8GB) or vosk-model-small-en-us-0.15 (40MB)
        vosk_model = Model("C:\\Users\\USER\\Desktop\\Sentry_AI\\backend\\app\\services\\task_extraction\\vosk-model-ar-0.22-linto-1.1.0")
        print("Vosk model ready")
    return vosk_model

def process_audio(audio_path: str) -> list[dict]:
    """
    Process audio file using Vosk + LangChain

    Pipeline:
    1. Convert audio to WAV format if needed
    2. Vosk transcription (offline)
    3. LangChain + OLLAMA extraction

    Input: Audio path (any format supported by moviepy)
    Output: List of tasks
    """
    print(f" Processing audio: {audio_path}")

    # Convert to WAV if needed
    wav_path = audio_path
    if not is_wav_format(audio_path):
        wav_path = convert_to_wav(audio_path)

    try:
        # Step 1: Transcribe with Vosk
        print("  Transcribing with Vosk...")
        model = _get_vosk_model()

        # Open audio file
        wf = wave.open(wav_path, "rb")

        # Verify audio format
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("    Audio must be WAV format mono PCM.")
            wf.close()
            raise ValueError("Audio file must be WAV format, mono, 16-bit PCM")

        # Create recognizer with sample rate from audio file
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)  # Enable word-level timestamps

        # Process audio in chunks
        transcript_parts = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                if "text" in result and result["text"]:
                    transcript_parts.append(result["text"])

        # Get final result
        final_result = json.loads(rec.FinalResult())
        if "text" in final_result and final_result["text"]:
            transcript_parts.append(final_result["text"])

        wf.close()

        # Combine all transcript parts
        transcript = " ".join(transcript_parts)

        # Save transcript to uploads/audio directory
        # Create uploads/audio directory if it doesn't exist
        uploads_dir = os.path.join(os.path.dirname(__file__), "utils", "uploads", "audio")
        os.makedirs(uploads_dir, exist_ok=True)

        # Create transcript filename
        audio_filename = os.path.basename(audio_path)
        transcript_filename = os.path.splitext(audio_filename)[0] + "_transcript.txt"
        transcript_file = os.path.join(uploads_dir, transcript_filename)

        # Save original transcript
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"    Original transcript saved to: {transcript_file}")

        print(f"    Transcript: {len(transcript)} characters")

        # Extract tasks with translation and enhancement
        tasks, enhanced_text = extract_task_from_text(transcript, translate=True)

        # Save enhanced/translated version
        enhanced_filename = os.path.splitext(audio_filename)[0] + "_enhanced.txt"
        enhanced_file = os.path.join(uploads_dir, enhanced_filename)
        with open(enhanced_file, "w", encoding="utf-8") as f:
            f.write(enhanced_text)
        print(f"    Enhanced transcript saved to: {enhanced_file}")

        return tasks

    finally:
        # Clean up converted file if we created one
        if wav_path != audio_path and os.path.exists(wav_path):
            os.remove(wav_path)
            print(f"    Cleaned up temporary file: {wav_path}")


if __name__ == "__main__":
    # Test audio processing
    test_audio_path = r"C:\Users\USER\Documents\Sound Recordings\Recording (3).m4a"
    tasks = process_audio(test_audio_path)
   