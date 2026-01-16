from pathlib import Path
from typing import List, Dict
from text_extractor import extract_task_from_text
from vision_extractor import extract_tasks_from_image
import tempfile
import base64
import os

# Poppler path configuration for Windows (required for hi_res strategy)
POPPLER_PATH = r"C:\Users\USER\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"
if os.path.exists(POPPLER_PATH):
    os.environ['PATH'] = POPPLER_PATH + os.pathsep + os.environ.get('PATH', '')
    print(f"[OK] Poppler path configured: {POPPLER_PATH}")
else:
    print(f"[WARNING] Poppler not found at {POPPLER_PATH}")
    print(f"[INFO] PDF processing may fail. Please install Poppler or update POPPLER_PATH")

# Download required NLTK data
try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('averaged_perceptron_tagger_eng', quiet=True)
except Exception as e:
    print(f"Warning: Could not download NLTK data: {e}")

print("Document processor ready")

def extract_images_from_pdf(pdf_path: str) -> List[str]:
    """
    Extract images from PDF using PyMuPDF (fitz).
    Returns list of image paths (saved to temp files).
    """
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        image_paths = []

        print(f"  Extracting images from PDF with PyMuPDF...")
        print(f"    PDF has {len(doc)} pages")

        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)

            print(f"    Page {page_num + 1}: found {len(image_list)} images")

            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    # Save to temp file
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    temp_file.write(image_bytes)
                    temp_file.close()

                    image_paths.append(temp_file.name)
                except Exception as e:
                    print(f"      Warning: Could not extract image {img_index + 1} from page {page_num + 1}: {e}")
                    continue

        doc.close()
        print(f"     Extracted {len(image_paths)} images total")
        return image_paths

    except ImportError:
        print("  Warning: PyMuPDF (fitz) not installed. Skipping image extraction.")
        print("  Install with: pip install PyMuPDF")
        return []
    except Exception as e:
        print(f"  Error extracting images: {e}")
        return []

def categorize_elements(raw_elements) -> tuple:
    """
    Categorize elements into text, tables, and images.
    Based on clean_final_rag_v3.ipynb implementation.
    """
    texts = []
    tables = []
    images = []

    for element in raw_elements:
        element_type = str(type(element).__name__)

        # Check for direct Table elements
        if "Table" in element_type:
            if hasattr(element, 'metadata') and hasattr(element.metadata, 'text_as_html'):
                tables.append({
                    'content': element.metadata.text_as_html,
                    'type': 'table'
                })
            continue

        # Check for direct Image elements
        if "Image" in element_type:
            if hasattr(element, 'metadata') and hasattr(element.metadata, 'image_base64'):
                # Only add if base64 data is actually present
                if element.metadata.image_base64 is not None:
                    images.append({
                        'content': element.metadata.image_base64,
                        'type': 'image',
                        'metadata': element.metadata
                    })
            continue

        # Handle CompositeElement
        if element_type == "CompositeElement":
            # Check if this composite element contains tables or images
            if hasattr(element, 'metadata') and hasattr(element.metadata, 'orig_elements'):
                chunk_els = element.metadata.orig_elements

                has_table = False
                has_image = False

                for el in chunk_els:
                    if "Table" in str(type(el)):
                        has_table = True
                        # Extract table HTML
                        if hasattr(el.metadata, 'text_as_html'):
                            tables.append({
                                'content': el.metadata.text_as_html,
                                'type': 'table'
                            })

                    if "Image" in str(type(el)):
                        has_image = True
                        # Extract image base64 (only if data is present)
                        if hasattr(el.metadata, 'image_base64') and el.metadata.image_base64 is not None:
                            images.append({
                                'content': el.metadata.image_base64,
                                'type': 'image',
                                'metadata': el.metadata
                            })

                # If no table or image, treat as text
                if not has_table and not has_image:
                    texts.append(element)
            else:
                # Regular text element
                texts.append(element)
        else:
            # All other element types are treated as text
            texts.append(element)

    return texts, tables, images

def process_document(document_path: str) -> List[dict]:
    """
    Process document file using Unstructured + LangChain + Google Gemini

    Pipeline:
    1. Extract text, tables, and images from document (PDF, DOCX, TXT, etc.)
    2. Parse and chunk the content
    3. Extract tasks from text using text_extractor
    4. Extract tasks from images using vision_extractor
    5. Process tables as structured text

    Input: Document path (PDF, DOCX, TXT, etc.)
    Output: List of tasks from all sources
    """
    print(f"Processing document: {document_path}")

    # Step 1: Parse document with Unstructured
    print("  Parsing document with Unstructured...")

    file_path = Path(document_path)

    if not file_path.exists():
        print(f"   Error: File not found: {document_path}")
        return []

    try:
        # Import unstructured libraries only when needed
        from unstructured.partition.pdf import partition_pdf
        from unstructured.partition.auto import partition

        # Check file type and use appropriate parser
        if file_path.suffix.lower() == '.pdf':
            # Use PDF-specific parser with hi_res strategy for better table extraction
            # Strategies: "fast" (text only), "hi_res" (images/tables), "ocr_only" (scanned)
            # Note: Image extraction disabled to reduce API calls on free tier models
            elements = partition_pdf(
                filename=str(file_path),
                strategy="hi_res",  # High-resolution for better extraction
                infer_table_structure=True,  # Extract tables
                extract_images_in_pdf=False,  # DISABLED: Don't detect images (saves API calls)
                extract_image_block_types=["Table"],  # Only extract tables, not images
                extract_image_block_to_payload=False,  # DISABLED: Don't extract image data
            )
        else:
            # Use auto parser for other document types (DOCX, TXT, etc.)
            elements = partition(
                filename=str(file_path),
                chunking_strategy="by_title",
                max_characters=10000,
                combine_text_under_n_chars=2000,
                new_after_n_chars=6000,
            )

        print(f"    Extracted {len(elements)} elements from document")

        # Debug: Print element types
        print("  Element types found:")
        element_types = {}
        for elem in elements:
            elem_type = type(elem).__name__
            element_types[elem_type] = element_types.get(elem_type, 0) + 1
        for elem_type, count in element_types.items():
            print(f"    - {elem_type}: {count}")

        # Step 2: Categorize elements by type
        print("  Categorizing elements...")
        texts, tables, images = categorize_elements(elements)

        print(f"    Text chunks: {len(texts)}")
        print(f"    Tables: {len(tables)}")
        print(f"    Images: {len(images)}")

        all_tasks = []

        # Step 3: Extract tasks from text
        if texts:
            print("  Extracting tasks from text...")
            text_content = "\n\n".join([
                elem.text if hasattr(elem, 'text') else str(elem)
                for elem in texts
            ])
            print(f"    Combined text: {len(text_content)} characters")

            text_tasks, _ = extract_task_from_text(text_content, translate=False)
            all_tasks.extend(text_tasks)
            print(f"    Found {len(text_tasks)} tasks from text")

        # Step 4: Extract tasks from tables
        if tables:
            print("  Extracting tasks from tables...")
            table_content = "\n\n".join([
                f"Table:\n{table['content']}"
                for table in tables
            ])

            table_tasks, _ = extract_task_from_text(table_content, translate=False)
            all_tasks.extend(table_tasks)
            print(f"    Found {len(table_tasks)} tasks from tables")

        # Step 5: Extract tasks from images using vision
        # DISABLED: Image extraction disabled to reduce API calls on free tier
        # Images are no longer extracted from documents (set extract_images_in_pdf=False above)
        image_tasks_count = 0

        if images:
            print("  [SKIPPED] Image task extraction disabled to save API quota")
            print(f"           Found {len(images)} images but skipping vision API calls")
            # Image processing commented out to avoid API usage on free tier
            # Uncomment the code below to re-enable image task extraction
            """
            print("  Extracting tasks from images with vision...")

            for i, image_data in enumerate(images):
                try:
                    # Decode base64 image and save to temp file
                    image_b64 = image_data['content']
                    image_bytes = base64.b64decode(image_b64)

                    # Create temp file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                        tmp_file.write(image_bytes)
                        tmp_path = tmp_file.name

                    # Extract tasks from image
                    image_tasks = extract_tasks_from_image(tmp_path)
                    all_tasks.extend(image_tasks)
                    image_tasks_count += len(image_tasks)

                    # Clean up temp file
                    Path(tmp_path).unlink(missing_ok=True)

                except Exception as e:
                    print(f"    Warning: Could not process image {i+1}: {e}")
                    continue

            print(f"    Found {image_tasks_count} tasks from {len(images)} images")
            """

        # Step 6: For PDFs, also extract images directly with PyMuPDF
        # Note: This can extract MANY images (logos, icons, decorative elements)
        # Only enable if Unstructured image extraction failed
        # Disabled by default for faster processing
        ENABLE_PYMUPDF_FALLBACK = False  # Set to True if you need it

        if ENABLE_PYMUPDF_FALLBACK and file_path.suffix.lower() == '.pdf':
            pdf_image_paths = extract_images_from_pdf(str(file_path))

            if pdf_image_paths:
                print("  Extracting tasks from PDF images with vision...")

                for img_path in pdf_image_paths:
                    try:
                        # Extract tasks from image
                        image_tasks = extract_tasks_from_image(img_path)
                        all_tasks.extend(image_tasks)
                        image_tasks_count += len(image_tasks)

                        # Clean up temp file
                        Path(img_path).unlink(missing_ok=True)

                    except Exception as e:
                        print(f"    Warning: Could not process PDF image: {e}")
                        # Try to clean up anyway
                        try:
                            Path(img_path).unlink(missing_ok=True)
                        except:
                            pass
                        continue

                print(f"    Found additional {image_tasks_count} tasks from PDF images")
        elif file_path.suffix.lower() == '.pdf' and not ENABLE_PYMUPDF_FALLBACK:
            print("  [SKIPPED] PyMuPDF image extraction (disabled for performance)")
            print("           Set ENABLE_PYMUPDF_FALLBACK=True to enable it")

        print(f"\n   Total tasks extracted: {len(all_tasks)}")
        return all_tasks

    except Exception as e:
        print(f"   Error processing document: {e}")
        import traceback
        traceback.print_exc()
        return []
