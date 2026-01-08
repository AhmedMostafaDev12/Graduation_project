"""
Test Unified Task Extraction
=============================

Test script for the unified task extraction service.
Demonstrates extracting tasks from various file types and saving to database.
"""

import sys
import os
from pathlib import Path

# Add service directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'services', 'task_extraction'))

from unified_task_extractor import extract_tasks_from_file, extract_tasks_to_json_file
import json


def print_result(result: dict):
    """Pretty print extraction result"""
    print(f"\n{'='*70}")
    print(f"EXTRACTION RESULT")
    print(f"{'='*70}")
    print(f"Success:         {result['success']}")
    print(f"Tasks Extracted: {result['tasks_extracted']}")
    print(f"Tasks Saved:     {result['tasks_saved']}")
    print(f"Source File:     {result['source_file']}")
    print(f"Source Type:     {result['source_type']}")
    print(f"Processor Used:  {result['processor_used']}")
    print(f"Processing Time: {result['processing_time_seconds']:.2f}s")

    if result['errors']:
        print(f"\nErrors:")
        for error in result['errors']:
            print(f"  - {error}")

    if result['warnings']:
        print(f"\nWarnings:")
        for warning in result['warnings']:
            print(f"  - {warning}")

    if result['tasks']:
        print(f"\n{'='*70}")
        print(f"EXTRACTED TASKS ({len(result['tasks'])})")
        print(f"{'='*70}\n")

        for i, task in enumerate(result['tasks'], 1):
            print(f"Task {i}:")
            print(f"  Title:       {task['title']}")
            print(f"  Description: {task.get('description', 'N/A')[:50]}...")
            print(f"  Priority:    {task.get('priority', 'N/A')}")
            print(f"  Deadline:    {task.get('deadline', 'N/A')}")
            print(f"  Assignee:    {task.get('assignee', 'N/A')}")
            print(f"  Category:    {task.get('category', 'N/A')}")
            print(f"  Est. Hours:  {task.get('estimated_hours', 'N/A')}")
            print()

    print(f"{'='*70}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_unified_extraction.py <file_path> [user_id] [options]")
        print("\nArguments:")
        print("  file_path              Path to file (any type)")
        print("  user_id                User ID (default: 1)")
        print("\nOptions:")
        print("  --no-db                Don't save to database")
        print("  --no-translate         Skip translation")
        print("  --save-json <file>     Save result to JSON file")
        print("\nSupported file types:")
        print("  - Audio: MP3, WAV, M4A, OGG, FLAC")
        print("  - Documents: PDF, DOCX, DOC")
        print("  - Images: PNG, JPG, JPEG, BMP, TIFF")
        print("  - Text: TXT, MD")
        print("\nExamples:")
        print("  python test_unified_extraction.py meeting.mp3")
        print("  python test_unified_extraction.py document.pdf 123")
        print("  python test_unified_extraction.py notes.jpg --no-db")
        print("  python test_unified_extraction.py tasks.txt --save-json output.json")
        return

    file_path = sys.argv[1]

    # Get user ID (default: 1)
    user_id = 1
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        user_id = int(sys.argv[2])

    # Parse options
    save_to_db = "--no-db" not in sys.argv
    translate = "--no-translate" not in sys.argv

    # Check for JSON output
    save_json = None
    if "--save-json" in sys.argv:
        idx = sys.argv.index("--save-json")
        if idx + 1 < len(sys.argv):
            save_json = sys.argv[idx + 1]

    # Validate file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return

    # Get file info
    file_info = Path(file_path)

    print(f"\n{'='*70}")
    print(f"UNIFIED TASK EXTRACTION TEST")
    print(f"{'='*70}")
    print(f"File:        {file_info.name}")
    print(f"Type:        {file_info.suffix}")
    print(f"Size:        {file_info.stat().st_size / 1024:.2f} KB")
    print(f"User ID:     {user_id}")
    print(f"Save to DB:  {save_to_db}")
    print(f"Translate:   {translate}")
    if save_json:
        print(f"JSON Output: {save_json}")
    print(f"{'='*70}\n")

    # Get database session if saving
    db_session = None
    if save_to_db:
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            from dotenv import load_dotenv

            load_dotenv()

            DATABASE_URL = os.getenv("DATABASE_URL")
            engine = create_engine(DATABASE_URL)
            SessionLocal = sessionmaker(bind=engine)
            db_session = SessionLocal()

            print("[DATABASE] Connected to database")

        except Exception as e:
            print(f"[WARNING] Could not connect to database: {e}")
            print("[INFO] Continuing without database save...")
            save_to_db = False

    # Extract tasks
    try:
        if save_json:
            # Save to JSON file
            output_file = extract_tasks_to_json_file(
                file_path=file_path,
                user_id=user_id,
                output_file=save_json,
                database_session=db_session,
                save_to_db=save_to_db
            )

            # Read and display result
            with open(output_file, 'r') as f:
                result = json.load(f)

        else:
            # Extract normally
            result = extract_tasks_from_file(
                file_path=file_path,
                user_id=user_id,
                database_session=db_session,
                save_to_db=save_to_db,
                translate=translate
            )

        # Display result
        print_result(result)

        # Success message
        if result['success']:
            print(f"✅ Successfully extracted {result['tasks_extracted']} tasks!")

            if save_to_db:
                print(f"✅ Saved {result['tasks_saved']} tasks to database!")

            if save_json:
                print(f"✅ Result saved to: {save_json}")
        else:
            print("❌ Extraction failed or no tasks found")

    except Exception as e:
        print(f"\n❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Close database session
        if db_session:
            db_session.close()


if __name__ == "__main__":
    main()
