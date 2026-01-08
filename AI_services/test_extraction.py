"""
Simple test for task extraction services.
Just tests the extractors and prints the results.
"""

import sys
from pathlib import Path
import os

# Suppress gRPC/ALTS warnings from Google Cloud libraries
# Must be set BEFORE importing any Google libraries
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Additionally suppress stderr during imports to hide C++ level gRPC warnings
import warnings
warnings.filterwarnings('ignore')

# Fix encoding for Windows console to support emojis
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add to path
sys.path.insert(0, str(Path(__file__).parent / "app" / "services" / "task_extraction"))
sys.path.insert(0, str(Path(__file__).parent / "app" / "utils"))

# from app.services.task_extraction.document_processor import process_document
from app.services.task_extraction.video_processor import process_video
from app.services.task_extraction.audio_processor import process_audio
from app.services.task_extraction.image_processor import process_image
from app.services.task_extraction.dedublicator import deduplicate_tasks


def print_tasks(tasks, title="Tasks"):
    """Print tasks in a readable format."""
    print(f"\n{title}:")
    print("=" * 80)

    if not tasks:
        print("  No tasks found.")
        return

    for i, task in enumerate(tasks, 1):
        print(f"\n{i}. Task:")
        if isinstance(task, dict):
            for key, value in task.items():
                # Format the value for better readability
                if isinstance(value, str) and len(value) > 100:
                    # Truncate long strings
                    display_value = value[:100] + "..."
                else:
                    display_value = value
                print(f"   {key}: {display_value}")
        else:
            # If task is not a dict, just print it
            print(f"   {task}")
        print("-" * 80)


def test_document(file_path: str):
    """Test document extraction."""
    print(f"\n📄 Testing document: {file_path}")
    tasks = process_document(file_path)
    print(f"\nExtracted {len(tasks)} tasks before deduplication")
    unique_tasks = deduplicate_tasks(tasks)
    print(f"After deduplication: {len(unique_tasks)} unique tasks")
    print_tasks(unique_tasks, "Extracted Tasks")
    return unique_tasks


def test_video(file_path: str):
    """Test video extraction."""
    print(f"\n🎥 Testing video: {file_path}")
    tasks = process_video(file_path)
    unique_tasks = deduplicate_tasks(tasks)
    print(unique_tasks)
    return unique_tasks


def test_audio(file_path: str):
    """Test audio extraction."""
    print(f"\n🎵 Testing audio: {file_path}")
    tasks = process_audio(file_path)
    unique_tasks = deduplicate_tasks(tasks)
    print_tasks(unique_tasks)
    return unique_tasks

def test_image(file_path: str):
    "test image extraction"
    print(f"\n🎵 Testing image: {file_path}")
    tasks = process_image(file_path)
    print(f"\nExtracted {len(tasks)} tasks:")
    unique_tasks = deduplicate_tasks(tasks)
    print_tasks(unique_tasks)
    return unique_tasks

if __name__ == "__main__":
    print("="*80)
    print("TASK EXTRACTION TEST")
    print("="*80)

    # Test document with tables and images
    # Replace with your actual file path
    # test_document(r"C:\Users\USER\Documents\AI project template[1].pdf")
    # test_document(r"C:\Users\USER\Downloads\lec_4_new[1].pdf")

    # Test video
    # test_video("test_files/sample.mp4")

    # Test audio
    test_audio(r"C:\Users\USER\Documents\Sound Recordings\lecture.m4a")
    print("\n" + "="*80)
