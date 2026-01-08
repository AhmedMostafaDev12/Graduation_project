"""
Task Extraction API - Separate Endpoints by Type
=================================================

FastAPI endpoints with separate routes for each extraction type.

Endpoints:
- POST /extract/audio - Extract from audio files
- POST /extract/document - Extract from documents (PDF, DOCX)
- POST /extract/image - Extract from images (vision)
- POST /extract/handwritten - Extract from handwritten notes
- POST /extract/text - Extract from plain text
- POST /extract/batch - Batch extraction (any type)
- GET /extraction-history/{user_id} - Get extraction history

Author: Sentry AI Team
Date: 2025
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
from pathlib import Path
import tempfile
import os
from sqlalchemy.orm import Session

from unified_task_extractor import (
    extract_tasks_from_file,
    UnifiedTaskExtractor,
    TaskExtractionResult
)

# Create router
router = APIRouter(
    prefix="/api/tasks",
    tags=["Task Extraction"]
)


# ============================================================================
# DEPENDENCY: DATABASE SESSION
# ============================================================================

def get_db():
    """Get database session."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os

    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# HELPER FUNCTION
# ============================================================================

async def process_file_extraction(
    file: UploadFile,
    user_id: int,
    processor_type: str,
    save_to_db: bool,
    translate: bool,
    db: Session
) -> dict:
    """
    Common file extraction logic used by all endpoints.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Create temp file
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file.filename)
    upload_id = None

    try:
        # Save uploaded file
        content = await file.read()
        file_size = len(content)

        with open(temp_file_path, "wb") as f:
            f.write(content)

        print(f"\n[{processor_type.upper()}] Processing: {file.filename}")
        print(f"[{processor_type.upper()}] User ID: {user_id}")

        # Record upload in database if save_to_db is enabled
        if save_to_db and db:
            from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text
            from sqlalchemy.dialects.postgresql import JSONB
            from sqlalchemy.ext.declarative import declarative_base
            from datetime import datetime

            Base = declarative_base()

            class Upload(Base):
                __tablename__ = "uploads"
                id = Column(Integer, primary_key=True)
                user_id = Column(Integer, nullable=False)
                filename = Column(String, nullable=False)
                file_path = Column(String, nullable=False)
                file_size_bytes = Column(BigInteger, nullable=False)
                mime_type = Column(String)
                upload_type = Column(String, nullable=False)
                processing_status = Column(String, default='processing')
                extraction_result = Column(JSONB)
                uploaded_at = Column(DateTime, default=datetime.utcnow)
                processed_at = Column(DateTime)

            # Create upload record
            upload_record = Upload(
                user_id=user_id,
                filename=file.filename,
                file_path=temp_file_path,
                file_size_bytes=file_size,
                mime_type=file.content_type,
                upload_type=processor_type,
                processing_status='processing'
            )
            db.add(upload_record)
            db.flush()  # Get the upload ID
            upload_id = upload_record.id
            print(f"[UPLOAD] Recorded in database with ID: {upload_id}")

        # Extract tasks
        extractor = UnifiedTaskExtractor(database_session=db if save_to_db else None)

        result = extractor.extract_and_save_tasks(
            file_path=temp_file_path,
            user_id=user_id,
            processor_type=processor_type,
            translate=translate,
            save_to_db=save_to_db
        )

        # Update upload record with extraction results
        if save_to_db and db and upload_id:
            from datetime import datetime
            upload_record.processing_status = 'completed' if result.success else 'failed'
            upload_record.processed_at = datetime.utcnow()
            upload_record.extraction_result = {
                "tasks_extracted": result.tasks_extracted,
                "tasks_saved": result.tasks_saved,
                "processor_used": result.processor_used,
                "processing_time_seconds": result.processing_time_seconds,
                "errors": result.errors,
                "warnings": result.warnings
            }
            db.commit()
            print(f"[UPLOAD] Updated status to '{upload_record.processing_status}'")

        # Convert to dict
        response = {
            "success": result.success,
            "tasks_extracted": result.tasks_extracted,
            "tasks_saved": result.tasks_saved,
            "tasks": [task.dict() for task in result.tasks],
            "source_file": result.source_file,
            "source_type": result.source_type,
            "processor_used": result.processor_used,
            "processing_time_seconds": result.processing_time_seconds,
            "errors": result.errors,
            "warnings": result.warnings
        }

        if upload_id:
            response["upload_id"] = upload_id

        return response

    except Exception as e:
        # Update upload status to failed if it was created
        if save_to_db and db and upload_id:
            try:
                from datetime import datetime
                upload_record.processing_status = 'failed'
                upload_record.processed_at = datetime.utcnow()
                upload_record.extraction_result = {"error": str(e)}
                db.commit()
            except:
                pass

        print(f"[{processor_type.upper()} ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    finally:
        # Cleanup
        try:
            os.remove(temp_file_path)
            os.rmdir(temp_dir)
        except:
            pass


# ============================================================================
# AUDIO EXTRACTION ENDPOINT
# ============================================================================

@router.post("/extract/audio", response_model=dict, tags=["Audio"])
async def extract_from_audio(
    file: UploadFile = File(..., description="Audio file (MP3, WAV, M4A, OGG, FLAC)"),
    user_id: int = Form(..., description="User ID"),
    save_to_db: bool = Form(True, description="Save tasks to database"),
    translate: bool = Form(True, description="Translate to English"),
    db: Session = Depends(get_db)
):
    """
    Extract tasks from audio files.

    **Supported formats:** MP3, WAV, M4A, OGG, FLAC

    **Process:**
    1. Transcribe audio using Vosk (supports Arabic/English)
    2. Translate text to English (if needed)
    3. Extract tasks using Llama 3.1 8B
    4. Save to database (optional)

    **Example:**
    ```bash
    curl -X POST "http://localhost:8003/api/tasks/extract/audio" \\
      -F "file=@meeting.mp3" \\
      -F "user_id=123"
    ```
    """
    return await process_file_extraction(
        file=file,
        user_id=user_id,
        processor_type="audio",
        save_to_db=save_to_db,
        translate=translate,
        db=db
    )


# ============================================================================
# DOCUMENT EXTRACTION ENDPOINT
# ============================================================================

@router.post("/extract/document", response_model=dict, tags=["Document"])
async def extract_from_document(
    file: UploadFile = File(..., description="Document file (PDF, DOCX, DOC)"),
    user_id: int = Form(..., description="User ID"),
    save_to_db: bool = Form(True, description="Save tasks to database"),
    translate: bool = Form(True, description="Translate to English"),
    db: Session = Depends(get_db)
):
    """
    Extract tasks from documents (PDF, DOCX, DOC).

    **Supported formats:** PDF, DOCX, DOC

    **Process:**
    1. Parse document using Unstructured (hi_res strategy)
    2. Extract text, tables, and images separately
    3. Process text/tables with Llama 3.1 8B
    4. Process images with LLaVa vision model
    5. Combine and save tasks

    **Features:**
    - Extracts tables as structured data
    - Extracts embedded images
    - Handles mixed content documents

    **Example:**
    ```bash
    curl -X POST "http://localhost:8003/api/tasks/extract/document" \\
      -F "file=@report.pdf" \\
      -F "user_id=123"
    ```
    """
    return await process_file_extraction(
        file=file,
        user_id=user_id,
        processor_type="document",
        save_to_db=save_to_db,
        translate=translate,
        db=db
    )


# ============================================================================
# IMAGE EXTRACTION ENDPOINT
# ============================================================================

@router.post("/extract/image", response_model=dict, tags=["Image"])
async def extract_from_image(
    file: UploadFile = File(..., description="Image file (PNG, JPG, JPEG, BMP, TIFF)"),
    user_id: int = Form(..., description="User ID"),
    save_to_db: bool = Form(True, description="Save tasks to database"),
    db: Session = Depends(get_db)
):
    """
    Extract tasks from images using vision AI.

    **Supported formats:** PNG, JPG, JPEG, BMP, TIFF

    **Process:**
    1. Process image with LLaVa vision model
    2. Extract tasks directly from visual content
    3. Save to database (optional)

    **Best for:**
    - Screenshots of task lists
    - Whiteboards with written tasks
    - Photos of todo lists
    - Diagrams with task information

    **Example:**
    ```bash
    curl -X POST "http://localhost:8003/api/tasks/extract/image" \\
      -F "file=@whiteboard.jpg" \\
      -F "user_id=123"
    ```
    """
    return await process_file_extraction(
        file=file,
        user_id=user_id,
        processor_type="vision",
        save_to_db=save_to_db,
        translate=False,  # Vision model handles multilingual
        db=db
    )


# ============================================================================
# HANDWRITTEN EXTRACTION ENDPOINT
# ============================================================================

@router.post("/extract/handwritten", response_model=dict, tags=["Handwritten"])
async def extract_from_handwritten(
    file: UploadFile = File(..., description="Handwritten notes (PNG, JPG, JPEG, PDF)"),
    user_id: int = Form(..., description="User ID"),
    save_to_db: bool = Form(True, description="Save tasks to database"),
    translate: bool = Form(True, description="Translate to English"),
    preprocess: bool = Form(True, description="Preprocess image for better OCR"),
    db: Session = Depends(get_db)
):
    """
    Extract tasks from handwritten notes using OCR.

    **Supported formats:** PNG, JPG, JPEG, BMP, TIFF, PDF (scanned)

    **Process:**
    1. Preprocess image (optional):
       - Convert to grayscale
       - Enhance contrast (2x)
       - Apply sharpening
       - Reduce noise
    2. Run Tesseract OCR with handwriting optimization
    3. Extract tasks using Llama 3.1 8B
    4. Save to database (optional)

    **Best for:**
    - Handwritten notes on paper
    - Scanned handwritten documents
    - Sticky notes
    - Personal journals with tasks

    **Tips for best results:**
    - Scan at 300+ DPI
    - Use good lighting
    - Write clearly with dark pen on white paper

    **Example:**
    ```bash
    curl -X POST "http://localhost:8003/api/tasks/extract/handwritten" \\
      -F "file=@handwritten_notes.jpg" \\
      -F "user_id=123" \\
      -F "preprocess=true"
    ```
    """
    # Note: preprocess parameter is handled by handwritten_processor internally
    return await process_file_extraction(
        file=file,
        user_id=user_id,
        processor_type="handwritten",
        save_to_db=save_to_db,
        translate=translate,
        db=db
    )


# ============================================================================
# TEXT EXTRACTION ENDPOINT
# ============================================================================

@router.post("/extract/text", response_model=dict, tags=["Text"])
async def extract_from_text(
    file: UploadFile = File(..., description="Text file (TXT, MD)"),
    user_id: int = Form(..., description="User ID"),
    save_to_db: bool = Form(True, description="Save tasks to database"),
    translate: bool = Form(True, description="Translate to English"),
    db: Session = Depends(get_db)
):
    """
    Extract tasks from plain text files.

    **Supported formats:** TXT, MD

    **Process:**
    1. Read text content
    2. Translate to English (if needed)
    3. Extract tasks using Llama 3.1 8B
    4. Save to database (optional)

    **Best for:**
    - Plain text task lists
    - Markdown files with todos
    - Meeting notes in text format
    - Copied/pasted content

    **Example:**
    ```bash
    curl -X POST "http://localhost:8003/api/tasks/extract/text" \\
      -F "file=@tasks.txt" \\
      -F "user_id=123"
    ```
    """
    return await process_file_extraction(
        file=file,
        user_id=user_id,
        processor_type="text",
        save_to_db=save_to_db,
        translate=translate,
        db=db
    )


# ============================================================================
# BATCH EXTRACTION ENDPOINT
# ============================================================================

@router.post("/extract/batch", response_model=dict, tags=["Batch"])
async def extract_batch(
    files: List[UploadFile] = File(..., description="Multiple files of any type"),
    user_id: int = Form(..., description="User ID"),
    save_to_db: bool = Form(True, description="Save tasks to database"),
    translate: bool = Form(True, description="Translate to English"),
    db: Session = Depends(get_db)
):
    """
    Extract tasks from multiple files in batch.

    **Supports:** All file types (auto-detected)

    **Process:**
    1. Process each file with appropriate processor
    2. Auto-detect file type based on extension
    3. Aggregate results
    4. Return summary + individual results

    **Example:**
    ```bash
    curl -X POST "http://localhost:8003/api/tasks/extract/batch" \\
      -F "files=@meeting.mp3" \\
      -F "files=@report.pdf" \\
      -F "files=@whiteboard.jpg" \\
      -F "user_id=123"
    ```
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    results = []
    temp_files = []

    try:
        for file in files:
            # Create temp file
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, file.filename)
            temp_files.append((temp_file_path, temp_dir))

            # Save file
            with open(temp_file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # Extract (auto-detect type)
            extractor = UnifiedTaskExtractor(database_session=db if save_to_db else None)

            result = extractor.extract_and_save_tasks(
                file_path=temp_file_path,
                user_id=user_id,
                processor_type=None,  # Auto-detect
                translate=translate,
                save_to_db=save_to_db
            )

            # Add to results
            results.append({
                "file": file.filename,
                "success": result.success,
                "tasks_extracted": result.tasks_extracted,
                "tasks_saved": result.tasks_saved,
                "processor_used": result.processor_used,
                "tasks": [task.dict() for task in result.tasks],
                "errors": result.errors,
                "warnings": result.warnings
            })

        # Calculate summary
        total_tasks_extracted = sum(r["tasks_extracted"] for r in results)
        total_tasks_saved = sum(r["tasks_saved"] for r in results)
        successful_files = sum(1 for r in results if r["success"])

        return JSONResponse(
            status_code=200,
            content={
                "batch_summary": {
                    "files_processed": len(files),
                    "successful_files": successful_files,
                    "failed_files": len(files) - successful_files,
                    "total_tasks_extracted": total_tasks_extracted,
                    "total_tasks_saved": total_tasks_saved
                },
                "results": results
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch extraction failed: {str(e)}")

    finally:
        # Cleanup
        for temp_file_path, temp_dir in temp_files:
            try:
                os.remove(temp_file_path)
                os.rmdir(temp_dir)
            except:
                pass


# ============================================================================
# EXTRACTION HISTORY ENDPOINT
# ============================================================================

@router.get("/extraction-history/{user_id}", response_model=dict, tags=["History"])
async def get_extraction_history(
    user_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get task extraction history for a user.

    **Parameters:**
    - user_id: User ID (path parameter)
    - limit: Number of recent tasks to retrieve (query parameter, default: 10)

    **Example:**
    ```bash
    curl "http://localhost:8003/api/tasks/extraction-history/123?limit=20"
    ```
    """
    from sqlalchemy import desc

    # Import Task model (adjust path based on your setup)
    try:
        # Try to import from integration path
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'burn_out_service', 'integrations'))
        from task_database_integration import Task
    except:
        # Fallback: define inline
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
        Base = declarative_base()

        class Task(Base):
            __tablename__ = 'tasks'
            id = Column(Integer, primary_key=True)
            title = Column(String(255))
            user_id = Column(Integer)
            task_type = Column(String(20))
            status = Column(String(50))
            priority = Column(String(20))
            due_date = Column(DateTime)
            assigned_to = Column(String(100))
            estimated_hours = Column(Float)
            created_at = Column(DateTime)

    try:
        # Get recent tasks
        tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.task_type == 'task'
        ).order_by(
            desc(Task.created_at)
        ).limit(limit).all()

        tasks_data = [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                "assigned_to": task.assigned_to,
                "created_at": task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else None,
                "estimated_hours": task.estimated_hours
            }
            for task in tasks
        ]

        return JSONResponse(
            status_code=200,
            content={
                "user_id": user_id,
                "total_tasks": len(tasks_data),
                "limit": limit,
                "tasks": tasks_data
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health", tags=["Health"])
async def health_check():
    """Service health check."""
    return {
        "status": "healthy",
        "service": "task-extraction-api",
        "endpoints": {
            "audio": "/api/tasks/extract/audio",
            "document": "/api/tasks/extract/document",
            "image": "/api/tasks/extract/image",
            "handwritten": "/api/tasks/extract/handwritten",
            "text": "/api/tasks/extract/text",
            "batch": "/api/tasks/extract/batch",
            "history": "/api/tasks/extraction-history/{user_id}"
        }
    }


if __name__ == "__main__":
    print("Task Extraction API - Separate Endpoints")
    print("="*60)
    print("\nEndpoints:")
    print("  POST /api/tasks/extract/audio        - Audio files")
    print("  POST /api/tasks/extract/document     - PDF, DOCX")
    print("  POST /api/tasks/extract/image        - Images (vision)")
    print("  POST /api/tasks/extract/handwritten  - Handwritten notes (OCR)")
    print("  POST /api/tasks/extract/text         - Plain text")
    print("  POST /api/tasks/extract/batch        - Multiple files")
    print("  GET  /api/tasks/extraction-history/{user_id}")
    print("  GET  /api/tasks/health")
