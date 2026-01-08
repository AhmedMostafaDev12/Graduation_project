"""
Test Unstructured Document Extraction Only
===========================================

This script tests the OLD document processor (using Unstructured library)
to see what text/content it extracts WITHOUT task extraction.
"""

import sys
import os
from pathlib import Path

# Add the task_extraction directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'services', 'task_extraction'))

# Configure Poppler path for Windows (required for hi_res strategy)
POPPLER_PATH = r"C:\Users\USER\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"
if os.path.exists(POPPLER_PATH):
    os.environ['PATH'] = POPPLER_PATH + os.pathsep + os.environ.get('PATH', '')
    print(f"[OK] Poppler path configured: {POPPLER_PATH}")
else:
    print(f"[WARNING] Poppler not found at {POPPLER_PATH}")

try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.partition.auto import partition
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False
    print(" Error: unstructured not installed")
    print("Install with: pip install unstructured")
    sys.exit(1)


def extract_text_from_pdf_unstructured(pdf_path: str) -> tuple[str, dict]:
    """Extract text from PDF using Unstructured library

    Returns:
        tuple: (extracted_text, statistics_dict)
    """
    print(f"\n Processing PDF with Unstructured: {pdf_path}")

    try:
        print("   Partitioning PDF...")
        # Use PDF-specific parser with hi_res strategy for better image/table extraction
        # Options: "fast" (text only), "hi_res" (better for images/tables), "ocr_only" (scanned docs)
        elements = partition_pdf(
            filename=pdf_path,
            strategy="hi_res",  # High-resolution strategy for images and tables
            infer_table_structure=True,  # Extract tables
        )

        print(f"    Extracted {len(elements)} total elements")

        # Count element types
        element_type_counts = {}
        for elem in elements:
            elem_type = type(elem).__name__
            element_type_counts[elem_type] = element_type_counts.get(elem_type, 0) + 1

        # Display element types breakdown
        print(f"\n    Element Types Breakdown:")
        for elem_type, count in sorted(element_type_counts.items()):
            print(f"      - {elem_type}: {count}")

        # Categorize elements
        texts = []
        tables = []
        images = []

        for element in elements:
            element_type = str(type(element).__name__)

            if "Table" in element_type:
                if hasattr(element, 'metadata') and hasattr(element.metadata, 'text_as_html'):
                    tables.append(f"[TABLE]\n{element.metadata.text_as_html}\n")
                elif hasattr(element, 'text'):
                    tables.append(f"[TABLE]\n{element.text}\n")
            elif "Image" in element_type:
                images.append(f"[IMAGE DETECTED]\n")
            else:
                # Regular text element
                if hasattr(element, 'text'):
                    texts.append(element.text)

        print(f"\n    Content Summary:")
        print(f"      - Text partitions: {len(texts)}")
        print(f"      - Tables: {len(tables)}")
        print(f"      - Images: {len(images)}")

        # Combine all text
        all_content = []

        if texts:
            all_content.append("=== TEXT CONTENT ===\n")
            all_content.append("\n\n".join(texts))

        if tables:
            all_content.append("\n\n=== TABLES ===\n")
            all_content.extend(tables)

        if images:
            all_content.append("\n\n=== IMAGES ===\n")
            all_content.extend(images)

        # Create statistics dictionary
        stats = {
            "total_elements": len(elements),
            "element_types": element_type_counts,
            "text_partitions": len(texts),
            "tables": len(tables),
            "images": len(images)
        }

        return "\n".join(all_content), stats

    except Exception as e:
        print(f"    Error: {e}")
        import traceback
        traceback.print_exc()
        return "", {}


def extract_text_from_document_unstructured(doc_path: str) -> str:
    """Extract text from any document using Unstructured library"""
    print(f"\n📝 Processing document with Unstructured: {doc_path}")

    try:
        print("   Partitioning document...")
        # Use auto parser for non-PDF files
        elements = partition(
            filename=doc_path,
            chunking_strategy="by_title",
            max_characters=10000,
            combine_text_under_n_chars=2000,
            new_after_n_chars=6000,
        )

        print(f"    Extracted {len(elements)} elements")

        # Extract text from elements
        texts = []
        for element in elements:
            if hasattr(element, 'text'):
                texts.append(element.text)

        return "\n\n".join(texts)

    except Exception as e:
        print(f"    Error: {e}")
        import traceback
        traceback.print_exc()
        return ""


def save_extracted_text(text: str, output_path: str):
    """Save extracted text to file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"\n Saved extracted text to: {output_path}")
    except Exception as e:
        print(f"\n Error saving text: {e}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_unstructured_extraction.py <file_path>")
        print("\nSupported formats:")
        print("  - PDF files (.pdf)")
        print("  - DOCX files (.docx)")
        print("  - Text files (.txt, .md)")
        print("\nExample:")
        print("  python test_unstructured_extraction.py document.pdf")
        return

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f" Error: File not found: {file_path}")
        return

    # Get file extension
    ext = Path(file_path).suffix.lower()

    print("="*60)
    print("UNSTRUCTURED TEXT EXTRACTION TEST")
    print("="*60)
    print(f"File: {file_path}")
    print(f"Type: {ext}")
    print("="*60)

    # Extract text based on file type
    stats = {}
    if ext == '.pdf':
        extracted_text, stats = extract_text_from_pdf_unstructured(file_path)
    elif ext in ['.docx', '.txt', '.md', '.doc']:
        extracted_text = extract_text_from_document_unstructured(file_path)
    else:
        print(f"\n Unsupported file type: {ext}")
        print("Supported: .pdf, .docx, .txt, .md")
        return

    # Display results
    print("\n" + "="*60)
    print("EXTRACTED TEXT")
    print("="*60)

    if extracted_text:
        print(f"\n{extracted_text}")

        print("\n" + "="*60)
        print("DETAILED STATISTICS")
        print("="*60)
        print(f"Total characters: {len(extracted_text)}")
        print(f"Total lines: {len(extracted_text.splitlines())}")
        print(f"Total words: {len(extracted_text.split())}")

        # Display extraction stats if available
        if stats:
            print(f"\nExtraction Details:")
            print(f"  Total elements extracted: {stats.get('total_elements', 0)}")
            print(f"  Text partitions: {stats.get('text_partitions', 0)}")
            print(f"  Tables found: {stats.get('tables', 0)}")
            print(f"  Images detected: {stats.get('images', 0)}")

            if stats.get('element_types'):
                print(f"\n  Element type breakdown:")
                for elem_type, count in sorted(stats['element_types'].items()):
                    print(f"    - {elem_type}: {count}")

        # Save to file
        output_file = f"{Path(file_path).stem}_unstructured_output.txt"
        save_extracted_text(extracted_text, output_file)

        print("\n Unstructured extraction complete!")

    else:
        print("\n No text extracted")


if __name__ == "__main__":
    main()
