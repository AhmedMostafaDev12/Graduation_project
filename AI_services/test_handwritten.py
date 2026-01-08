"""
Test Handwritten Notes Task Extraction
=======================================

This script tests the handwritten notes processor.
It extracts tasks from handwritten content in images or PDFs.
"""

import sys
import os
from pathlib import Path

# Add the task_extraction directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'services', 'task_extraction'))

try:
    from handwritten_processor import process_handwritten_notes
    HANDWRITTEN_AVAILABLE = True
except ImportError as e:
    HANDWRITTEN_AVAILABLE = False
    print(f"❌ Error importing handwritten processor: {e}")
    print("\nMake sure you have installed:")
    print("  pip install pytesseract pillow pdf2image")
    sys.exit(1)


def display_tasks(tasks: list):
    """Display extracted tasks in a formatted way"""
    if not tasks:
        print("\n📝 No tasks were extracted")
        print("\nPossible reasons:")
        print("  - The handwriting might not be clear enough")
        print("  - The image quality might be too low")
        print("  - There might not be any tasks in the content")
        print("\nTips:")
        print("  - Try scanning at higher resolution (300+ DPI)")
        print("  - Ensure good lighting and contrast")
        print("  - Write more clearly")
        return

    print(f"\n{'='*60}")
    print(f"EXTRACTED TASKS ({len(tasks)})")
    print(f"{'='*60}\n")

    for i, task in enumerate(tasks, 1):
        print(f"Task {i}:")
        print(f"  Title:       {task.get('title', 'N/A')}")
        print(f"  Description: {task.get('description', 'N/A')}")
        print(f"  Assignee:    {task.get('assignee', 'Not specified')}")
        print(f"  Deadline:    {task.get('deadline', 'Not specified')}")
        print(f"  Priority:    {task.get('priority', 'Not specified')}")
        print(f"  Category:    {task.get('category', 'general')}")
        print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_handwritten.py <file_path> [options]")
        print("\nArguments:")
        print("  file_path              Path to handwritten notes (image or PDF)")
        print("\nOptions:")
        print("  --no-preprocess        Disable image preprocessing")
        print("  --no-translate         Skip translation (for English only)")
        print("\nSupported formats:")
        print("  - Images: PNG, JPG, JPEG, BMP, TIFF")
        print("  - PDF: Scanned documents with handwritten content")
        print("\nExamples:")
        print("  python test_handwritten.py notes.jpg")
        print("  python test_handwritten.py scanned_notes.pdf")
        print("  python test_handwritten.py notes.jpg --no-preprocess")
        print("  python test_handwritten.py notes.jpg --no-translate")
        return

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return

    # Parse options
    preprocess = "--no-preprocess" not in sys.argv
    translate = "--no-translate" not in sys.argv

    # Get file info
    ext = Path(file_path).suffix.lower()

    print("=" * 60)
    print("HANDWRITTEN NOTES TASK EXTRACTION TEST")
    print("=" * 60)
    print(f"File:         {file_path}")
    print(f"Type:         {ext}")
    print(f"Preprocessing: {'Enabled' if preprocess else 'Disabled'}")
    print(f"Translation:   {'Enabled' if translate else 'Disabled'}")
    print("=" * 60)

    # Validate file type
    if ext == '.pdf':
        print("\n📄 Processing PDF with handwritten content...")
    elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']:
        print("\n🖼️  Processing handwritten image...")
    else:
        print(f"\n❌ Unsupported file type: {ext}")
        print("Supported: .pdf, .png, .jpg, .jpeg, .bmp, .tiff")
        return

    # Process handwritten notes
    print("\n🔍 Starting OCR and task extraction...\n")

    tasks = process_handwritten_notes(
        file_path,
        preprocess=preprocess,
        translate=translate
    )

    # Display results
    display_tasks(tasks)

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total tasks extracted: {len(tasks)}")

    if tasks:
        # Count by priority
        priorities = {}
        for task in tasks:
            priority = task.get('priority', 'Not specified')
            priorities[priority] = priorities.get(priority, 0) + 1

        print(f"\nBy Priority:")
        for priority, count in sorted(priorities.items()):
            print(f"  {priority}: {count}")

        # Count by category
        categories = {}
        for task in tasks:
            category = task.get('category', 'general')
            categories[category] = categories.get(category, 0) + 1

        print(f"\nBy Category:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count}")

    print("\n✅ Handwritten notes processing complete!")


if __name__ == "__main__":
    main()
