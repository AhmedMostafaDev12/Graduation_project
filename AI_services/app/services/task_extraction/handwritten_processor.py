"""
Handwritten Notes Processor
============================

This processor is specifically designed for extracting tasks from handwritten notes.
It uses OCR (Tesseract) to recognize handwritten text and then extracts tasks.

Best for:
- Handwritten notes on paper (scanned or photographed)
- Whiteboard images
- Sticky notes
- Handwritten to-do lists

Supported formats:
- Images: PNG, JPG, JPEG, BMP, TIFF
- PDF: Scanned documents with handwritten content
"""

from pathlib import Path
from typing import List, Dict
import tempfile
import os

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: pytesseract or PIL not installed. OCR will not work.")
    print("Install with: pip install pytesseract pillow pdf2image")

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("Warning: pdf2image not installed. PDF processing will be limited.")
    print("Install with: pip install pdf2image")

from text_extractor import extract_task_from_text

# Poppler path configuration for Windows
POPPLER_PATH = r"C:\Users\USER\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"


def preprocess_image_for_handwriting(image_path: str) -> Image.Image:
    """
    Preprocess image to improve OCR accuracy for handwritten text.

    Applies:
    - Grayscale conversion
    - Contrast enhancement
    - Sharpening
    - Noise reduction

    Args:
        image_path: Path to image file

    Returns:
        Preprocessed PIL Image
    """
    # Open image
    image = Image.open(image_path)

    # Convert to grayscale
    image = image.convert('L')

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)

    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)

    # Reduce noise
    image = image.filter(ImageFilter.MedianFilter(size=3))

    return image


def extract_text_from_handwritten_image(image_path: str, preprocess: bool = True) -> str:
    """
    Extract text from handwritten image using OCR.

    Args:
        image_path: Path to image file
        preprocess: Whether to preprocess image for better OCR (default: True)

    Returns:
        Extracted text as string
    """
    if not OCR_AVAILABLE:
        raise ImportError("pytesseract or PIL not installed")

    try:
        print(f"  Processing handwritten image: {Path(image_path).name}")

        # Preprocess image if requested
        if preprocess:
            print("    Preprocessing image for handwriting recognition...")
            image = preprocess_image_for_handwriting(image_path)
        else:
            image = Image.open(image_path)

        # Configure Tesseract for handwriting
        # PSM 6: Assume a single uniform block of text
        # PSM 4: Assume a single column of text of variable sizes
        custom_config = r'--oem 3 --psm 6'

        print("    Running OCR with handwriting optimization...")
        text = pytesseract.image_to_string(image, config=custom_config)

        print(f"    Extracted {len(text)} characters")
        return text.strip()

    except Exception as e:
        print(f"    Error performing OCR: {e}")
        return ""


def extract_text_from_handwritten_pdf(pdf_path: str, preprocess: bool = True) -> str:
    """
    Extract text from PDF containing handwritten content.

    Pipeline:
    1. Convert PDF pages to images
    2. Preprocess images for handwriting
    3. Run OCR on each page
    4. Combine all text

    Args:
        pdf_path: Path to PDF file
        preprocess: Whether to preprocess images (default: True)

    Returns:
        Combined extracted text from all pages
    """
    if not PDF2IMAGE_AVAILABLE or not OCR_AVAILABLE:
        raise ImportError("pdf2image and pytesseract are required")

    print(f"  Processing handwritten PDF: {Path(pdf_path).name}")

    # Create temp directory for images
    temp_dir = tempfile.mkdtemp()

    try:
        # Convert PDF to images
        print("    Converting PDF to images...")

        if os.path.exists(POPPLER_PATH):
            # High DPI for better handwriting recognition
            images = convert_from_path(pdf_path, dpi=400, poppler_path=POPPLER_PATH)
        else:
            images = convert_from_path(pdf_path, dpi=400)

        print(f"    Converted {len(images)} pages")

        # Process each page
        all_text = []

        for i, image in enumerate(images, 1):
            print(f"    Processing page {i}/{len(images)}...")

            # Save to temp file
            temp_image_path = os.path.join(temp_dir, f"page_{i}.png")
            image.save(temp_image_path, "PNG")

            # Extract text from this page
            page_text = extract_text_from_handwritten_image(temp_image_path, preprocess)

            if page_text:
                all_text.append(f"--- Page {i} ---\n{page_text}")

        # Combine all text
        combined_text = "\n\n".join(all_text)
        print(f"  Total text extracted: {len(combined_text)} characters")

        return combined_text

    finally:
        # Clean up temp images
        try:
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
        except:
            pass


def process_handwritten_notes(file_path: str, preprocess: bool = True, translate: bool = True) -> List[dict]:
    """
    Main function to extract tasks from handwritten notes.

    Pipeline:
    1. Detect file type (image or PDF)
    2. Apply OCR with handwriting optimization
    3. Extract tasks from recognized text

    Args:
        file_path: Path to handwritten notes (image or PDF)
        preprocess: Whether to preprocess images for better OCR (default: True)
        translate: Whether to translate non-English text (default: True)

    Returns:
        List of extracted tasks
    """
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        print(f"Error: File not found: {file_path}")
        return []

    ext = file_path_obj.suffix.lower()

    print(f"\n{'='*60}")
    print("HANDWRITTEN NOTES PROCESSOR")
    print(f"{'='*60}")
    print(f"File: {file_path_obj.name}")
    print(f"Type: {ext}")
    print(f"Preprocessing: {'Enabled' if preprocess else 'Disabled'}")
    print(f"Translation: {'Enabled' if translate else 'Disabled'}")
    print(f"{'='*60}\n")

    try:
        # Extract text based on file type
        if ext == '.pdf':
            if not PDF2IMAGE_AVAILABLE or not OCR_AVAILABLE:
                print("Error: PDF processing requires pdf2image and pytesseract")
                print("Install with: pip install pdf2image pytesseract pillow")
                return []

            text = extract_text_from_handwritten_pdf(str(file_path), preprocess)

        elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']:
            if not OCR_AVAILABLE:
                print("Error: Image processing requires pytesseract and PIL")
                print("Install with: pip install pytesseract pillow")
                return []

            text = extract_text_from_handwritten_image(str(file_path), preprocess)

        else:
            print(f"Unsupported file type: {ext}")
            print("Supported: PDF, PNG, JPG, JPEG, BMP, TIFF")
            return []

        # Check if we got any text
        if not text or len(text.strip()) < 5:
            print("  No text extracted from handwritten notes")
            print("  Tips:")
            print("    - Ensure the image is clear and well-lit")
            print("    - Try scanning at higher resolution (300+ DPI)")
            print("    - Make sure handwriting is legible")
            return []

        print(f"\n  OCR Results:")
        print(f"    Extracted {len(text)} characters")
        print(f"    Extracted {len(text.split())} words")

        # Extract tasks from text
        print("\n  Extracting tasks from handwritten text...")
        tasks, enhanced_text = extract_task_from_text(text, translate=translate)

        print(f"\n  {'='*60}")
        print(f"  RESULTS")
        print(f"  {'='*60}")
        print(f"  Found {len(tasks)} tasks from handwritten notes")

        if tasks:
            print(f"\n  Tasks extracted:")
            for i, task in enumerate(tasks, 1):
                print(f"    {i}. {task.get('title', 'Untitled')}")

        return tasks

    except Exception as e:
        print(f"Error processing handwritten notes: {e}")
        import traceback
        traceback.print_exc()
        return []


# Installation and configuration instructions
SETUP_INSTRUCTIONS = """
=============================================================================
HANDWRITTEN NOTES PROCESSOR - SETUP INSTRUCTIONS
=============================================================================

This processor is optimized for extracting tasks from handwritten content.

REQUIREMENTS:
-------------

1. Python Packages:
   pip install pytesseract pillow pdf2image

2. Tesseract OCR Engine:

   Windows:
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location (C:\\Program Files\\Tesseract-OCR)
   - Add to PATH or set pytesseract.pytesseract.tesseract_cmd

   Linux:
   sudo apt-get install tesseract-ocr

   macOS:
   brew install tesseract

3. Poppler (for PDF processing):

   Windows:
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases
   - Extract and update POPPLER_PATH in this file

   Linux:
   sudo apt-get install poppler-utils

   macOS:
   brew install poppler


USAGE:
------

from handwritten_processor import process_handwritten_notes

# Process handwritten image
tasks = process_handwritten_notes("notes.jpg")

# Process scanned PDF with handwriting
tasks = process_handwritten_notes("scanned_notes.pdf")

# Disable image preprocessing (if OCR is worse with it)
tasks = process_handwritten_notes("notes.jpg", preprocess=False)

# Skip translation (for English handwriting only)
tasks = process_handwritten_notes("notes.jpg", translate=False)


TIPS FOR BEST RESULTS:
----------------------

1. Image Quality:
   - Use high resolution (300+ DPI for scans)
   - Ensure good lighting (no shadows)
   - Avoid blurry images

2. Handwriting:
   - Write clearly and legibly
   - Use good contrast (dark pen on white paper)
   - Avoid overlapping text

3. Scanning:
   - Scan straight (not tilted)
   - Use scanner bed instead of camera when possible
   - Clean the paper (no creases or stains)

4. Preprocessing:
   - Usually improves accuracy
   - Disable if results are worse (preprocess=False)

=============================================================================
"""


if __name__ == "__main__":
    print(SETUP_INSTRUCTIONS)

    # Test if everything is installed
    if OCR_AVAILABLE and PDF2IMAGE_AVAILABLE:
        print("\n All dependencies are installed!")
        print("\nYou can now use:")
        print("  from handwritten_processor import process_handwritten_notes")
        print("  tasks = process_handwritten_notes('your_handwritten_notes.jpg')")
    else:
        print("\n Some dependencies are missing. See instructions above.")
