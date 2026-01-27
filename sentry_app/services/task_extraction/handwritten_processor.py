"""
Handwritten Notes Processor
============================

This processor is specifically designed for extracting tasks from handwritten notes.
It uses Groq Vision API (meta-llama/llama-4-scout-17b-16e-instruct) to directly extract tasks
from handwritten images without needing OCR preprocessing.

Best for:
- Handwritten notes on paper (scanned or photographed)
- Whiteboard images
- Sticky notes
- Handwritten to-do lists

Supported formats:
- Images: PNG, JPG, JPEG, BMP, TIFF
- PDF: Scanned documents with handwritten content

Benefits over OCR (Tesseract):
- Better handwriting recognition
- Direct task extraction (no OCR preprocessing needed)
- Understands context and formatting
- Handles mixed handwriting styles
- Supports multiple languages
"""

from pathlib import Path
from typing import List, Dict
import tempfile
import os
import base64

from PIL import Image
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("Warning: pdf2image not installed. PDF processing will be limited.")
    print("Install with: pip install pdf2image")

# Poppler path configuration for Windows
POPPLER_PATH = r"C:\Users\USER\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"

# Initialize Groq Vision LLM
vision_llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
    max_tokens=2048
)

json_parser = JsonOutputParser()


def extract_tasks_from_handwritten_image(image_path: str) -> List[dict]:
    """
    Extract tasks from handwritten image using Groq Vision API.

    This directly processes the image without OCR preprocessing.
    The vision model reads handwriting and extracts structured tasks.

    Args:
        image_path: Path to handwritten image file

    Returns:
        List of extracted tasks
    """
    print(f"  Processing handwritten image with Groq Vision: {Path(image_path).name}")

    # Encode image to base64
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode()

    # Create prompt for task extraction with enhanced time extraction
    prompt = """You are an expert task extraction AI analyzing handwritten notes. Extract all tasks, to-dos, and action items with precise temporal information.

CRITICAL INSTRUCTIONS FOR TIME EXTRACTION:
1. **Start Time & End Time**: When you see time ranges like "from 5:00 to 6:00", "3pm to 4pm", "at 9:30 until 10:00":
   - Extract start_time in 24-hour format (HH:MM)
   - Extract end_time in 24-hour format (HH:MM)
   - Convert PM times correctly (5:00 PM → 17:00, 6:00 PM → 18:00)

2. **Estimated Hours**: Calculate duration from time ranges:
   - "5:00 to 6:00" → 1 hour
   - "3pm to 5pm" → 2 hours
   - If explicit duration mentioned ("2 hour meeting"), use that

3. **Deadline/Due Date**: Extract dates in YYYY-MM-DD format from phrases like:
   - "by Friday" → calculate the date
   - "due tomorrow" → calculate tomorrow's date
   - "on January 15" → convert to YYYY-MM-DD
   - If only time mentioned (no date), set deadline to null

4. **Title vs Description**:
   - Title: What needs to be done (short, actionable)
   - Description: Only additional context NOT already in other fields (location, notes, etc.)
   - DO NOT put time/date information in description if it belongs in start_time/end_time/deadline

5. **Priority**: Infer from urgency words:
   - "urgent", "ASAP", "immediately" → URGENT
   - "important", "soon", "priority" → HIGH
   - Everything else → MEDIUM or LOW

6. **Category**: Infer from context:
   - Sports, games → could be "meeting" (if scheduled) or "general"
   - Work tasks → "assignment" or "project"
   - Exams, tests → "exam"
   - Meetings, calls → "meeting"

7. **Handwriting-specific tips**:
   - Read all handwritten text carefully
   - Extract each distinct task/to-do item
   - Handle unclear or messy handwriting gracefully

Return ONLY valid JSON in this exact format:
{
  "tasks": [
    {
      "title": "task title",
      "description": "additional notes (NOT times/dates)",
      "assignee": "person name or null",
      "deadline": "YYYY-MM-DD or null",
      "start_time": "HH:MM or null",
      "end_time": "HH:MM or null",
      "estimated_hours": float or null,
      "priority": "URGENT|HIGH|MEDIUM|LOW or null",
      "category": "assignment|meeting|exam|project|general"
    }
  ]
}

IMPORTANT: Return ONLY the JSON object, no additional text or explanations."""

    try:
        # Create multimodal message with image
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                }
            ]
        )

        # Invoke Groq Vision
        response = vision_llm.invoke([message])

        # Parse JSON response
        result = json_parser.parse(response.content)
        tasks = result.get("tasks", [])

        print(f"    Extracted {len(tasks)} tasks from handwriting")
        return tasks

    except Exception as e:
        print(f"    Error processing handwritten image: {e}")
        return []


def extract_tasks_from_handwritten_pdf(pdf_path: str) -> List[dict]:
    """
    Extract tasks from PDF containing handwritten content.

    Pipeline:
    1. Convert PDF pages to images
    2. Process each image with Groq Vision
    3. Combine all extracted tasks

    Args:
        pdf_path: Path to PDF file with handwritten content

    Returns:
        Combined list of tasks from all pages
    """
    if not PDF2IMAGE_AVAILABLE:
        raise ImportError("pdf2image is required for PDF processing. Install with: pip install pdf2image")

    print(f"  Processing handwritten PDF: {Path(pdf_path).name}")

    # Create temp directory for images
    temp_dir = tempfile.mkdtemp()

    try:
        # Convert PDF to images
        print("    Converting PDF to images...")

        if os.path.exists(POPPLER_PATH):
            # High DPI for better handwriting recognition
            images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
        else:
            images = convert_from_path(pdf_path, dpi=300)

        print(f"    Converted {len(images)} pages")

        # Process each page
        all_tasks = []

        for i, image in enumerate(images, 1):
            print(f"    Processing page {i}/{len(images)}...")

            # Save to temp file
            temp_image_path = os.path.join(temp_dir, f"page_{i}.png")
            image.save(temp_image_path, "PNG")

            # Extract tasks from this page
            page_tasks = extract_tasks_from_handwritten_image(temp_image_path)

            # Add page number to each task
            for task in page_tasks:
                task["source_page"] = i

            all_tasks.extend(page_tasks)

        print(f"  Total tasks extracted from PDF: {len(all_tasks)}")
        return all_tasks

    finally:
        # Clean up temp images
        try:
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
        except:
            pass


def process_handwritten_notes(file_path: str) -> List[dict]:
    """
    Main function to extract tasks from handwritten notes.

    Uses Groq Vision API to directly read and extract tasks from:
    - Handwritten images (PNG, JPG, JPEG, BMP, TIFF)
    - PDFs with handwritten content

    Args:
        file_path: Path to handwritten notes (image or PDF)

    Returns:
        List of extracted tasks
    """
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        print(f"Error: File not found: {file_path}")
        return []

    ext = file_path_obj.suffix.lower()

    print(f"\n{'='*60}")
    print("HANDWRITTEN NOTES PROCESSOR (Groq Vision)")
    print(f"{'='*60}")
    print(f"File: {file_path_obj.name}")
    print(f"Type: {ext}")
    print(f"Model: meta-llama/llama-4-scout-17b-16e-instruct")
    print(f"{'='*60}\n")

    try:
        # Process based on file type
        if ext == '.pdf':
            if not PDF2IMAGE_AVAILABLE:
                print("Error: PDF processing requires pdf2image")
                print("Install with: pip install pdf2image")
                return []

            tasks = extract_tasks_from_handwritten_pdf(str(file_path))

        elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']:
            tasks = extract_tasks_from_handwritten_image(str(file_path))

        else:
            print(f"Unsupported file type: {ext}")
            print("Supported: PDF, PNG, JPG, JPEG, BMP, TIFF")
            return []

        # Display results
        print(f"\n  {'='*60}")
        print(f"  RESULTS")
        print(f"  {'='*60}")
        print(f"  Found {len(tasks)} tasks from handwritten notes")

        if tasks:
            print(f"\n  Tasks extracted:")
            for i, task in enumerate(tasks, 1):
                print(f"    {i}. {task.get('title', 'Untitled')}")
                if task.get('deadline'):
                    print(f"       Due: {task['deadline']}")
                if task.get('priority'):
                    print(f"       Priority: {task['priority']}")

        return tasks

    except Exception as e:
        print(f"Error processing handwritten notes: {e}")
        import traceback
        traceback.print_exc()
        return []


# Installation and configuration instructions
SETUP_INSTRUCTIONS = """
=============================================================================
HANDWRITTEN NOTES PROCESSOR - SETUP INSTRUCTIONS (Groq Vision)
=============================================================================

This processor uses Groq Vision API to directly extract tasks from
handwritten images without needing OCR installation.

REQUIREMENTS:
-------------

1. Python Packages:
   pip install langchain-groq groq pillow pdf2image

2. Groq API Key:
   - Get your free API key from: https://console.groq.com
   - Add to .env file: GROQ_API_KEY="your_key_here"

3. Poppler (for PDF processing only):

   Windows:
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases
   - Extract and update POPPLER_PATH in this file

   Linux:
   sudo apt-get install poppler-utils

   macOS:
   brew install poppler


USAGE:
------

from sentry_app.services.task_extraction.handwritten_processor import process_handwritten_notes

# Process handwritten image
tasks = process_handwritten_notes("notes.jpg")

# Process scanned PDF with handwriting
tasks = process_handwritten_notes("scanned_notes.pdf")


BENEFITS OVER OCR (Tesseract):
-------------------------------

✅ No Tesseract installation needed
✅ Better handwriting recognition
✅ Understands context (not just text extraction)
✅ Direct task extraction (no intermediate text step)
✅ Handles messy/unclear handwriting better
✅ Multi-language support built-in
✅ Cloud-based (no local resources needed)


TIPS FOR BEST RESULTS:
----------------------

1. Image Quality:
   - Use good lighting (no shadows)
   - Avoid blurry images
   - Higher resolution is better (300+ DPI for scans)

2. Handwriting:
   - Write clearly (but doesn't need to be perfect)
   - Dark ink on white/light paper works best
   - Avoid overlapping text

3. Scanning:
   - Scan straight (not tilted)
   - Use scanner bed instead of camera when possible
   - Clean the paper (no creases or stains)

4. Cost:
   - Groq free tier: 14,400 requests/day
   - Very affordable for production use

=============================================================================
"""


if __name__ == "__main__":
    print(SETUP_INSTRUCTIONS)
    print("\n✅ Groq Vision handwriting processor ready!")
    print("\nYou can now use:")
    print("  from sentry_app.services.task_extraction.handwritten_processor import process_handwritten_notes")
    print("  tasks = process_handwritten_notes('your_handwritten_notes.jpg')")
