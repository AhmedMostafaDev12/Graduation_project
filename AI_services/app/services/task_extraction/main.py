"""
Task Extraction Service - FastAPI Application
==============================================

Standalone FastAPI service for task extraction from various file types.

Runs on port 8003 (separate from the main burnout detection service)

Features:
- Extract tasks from audio files (MP3, WAV, M4A, etc.)
- Extract tasks from documents (PDF, DOCX, TXT, etc.)
- Extract tasks from images (PNG, JPG, etc.)
- Extract tasks from handwritten notes
- Save tasks directly to database
- Valid JSON output

Author: Sentry AI Team
Date: 2025
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))


# ============================================================================
# LIFESPAN CONTEXT (for startup/shutdown)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context for startup and shutdown events.
    """
    # Startup
    print("\n" + "="*80)
    print("STARTING TASK EXTRACTION SERVICE")
    print("="*80)
    print("\nConfiguration:")
    print(f"  Port:         8003")
    print(f"  Database:     {os.getenv('DATABASE_URL', 'Not configured')[:50]}...")
    print(f"  Text Model:   {os.getenv('OLLAMA_TEXT_MODEL', 'llama3.1:8b')}")
    print(f"  Vision Model: {os.getenv('OLLAMA_VISION_MODEL', 'llava')}")

    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print(f"  Ollama:       Running ✓")
        else:
            print(f"  Ollama:       Not responding")
    except:
        print(f"  Ollama:       Not running (vision features disabled)")

    # Check database
    try:
        from sqlalchemy import create_engine
        engine = create_engine(os.getenv("DATABASE_URL"))
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print(f"  Database:     Connected ✓")
    except Exception as e:
        print(f"  Database:     Error: {str(e)[:50]}")

    print("\n" + "="*80)
    print("SERVICE READY")
    print("="*80)
    print(f"\nAPI Documentation: http://localhost:8003/docs")
    print(f"Service Info:      http://localhost:8003/")
    print(f"Health Check:      http://localhost:8003/health")
    print("\nEndpoints:")
    print("  POST /api/tasks/extract-tasks           - Extract from single file")
    print("  POST /api/tasks/extract-tasks/batch     - Extract from multiple files")
    print("  GET  /api/tasks/extraction-history/{id} - Get extraction history")
    print("  GET  /api/tasks/health                  - Service health check")
    print("\n" + "="*80 + "\n")

    yield

    # Shutdown
    print("\n" + "="*80)
    print("SHUTTING DOWN TASK EXTRACTION SERVICE")
    print("="*80 + "\n")


# ============================================================================
# CREATE FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Sentry AI - Task Extraction Service",
    description="""
    ## Task Extraction Service

    Extract tasks from any file type and save them to the database.

    ### Supported File Types

    - **Audio**: MP3, WAV, M4A, OGG, FLAC (via Vosk transcription)
    - **Documents**: PDF, DOCX, DOC (via Unstructured parsing)
    - **Images**: PNG, JPG, JPEG, BMP, TIFF (via LLaVa vision)
    - **Handwritten**: Handwritten notes and scanned documents (via OCR)
    - **Text**: TXT, MD (direct extraction)

    ### Features

    - **Multi-language Support**: Automatic translation to English
    - **Database Integration**: Direct save to PostgreSQL
    - **Batch Processing**: Process multiple files at once
    - **Valid JSON Output**: Fully validated with Pydantic
    - **Error Handling**: Comprehensive error messages and warnings

    ### AI Models Used

    - **Text Extraction**: Llama 3.1 8B (Ollama)
    - **Vision Extraction**: LLaVa (Ollama)
    - **Speech Recognition**: Vosk (offline, supports Arabic/English)
    - **OCR**: Tesseract (for handwritten/scanned docs)

    ### Quick Start

    ```bash
    # Extract tasks from file
    curl -X POST "http://localhost:8003/api/tasks/extract-tasks" \\
      -F "file=@document.pdf" \\
      -F "user_id=123"
    ```

    ### Response Format

    ```json
    {
      "success": true,
      "tasks_extracted": 5,
      "tasks_saved": 5,
      "tasks": [...],
      "source_file": "document.pdf",
      "processor_used": "document",
      "processing_time_seconds": 12.34
    }
    ```
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================================
# CORS CONFIGURATION
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev
        "http://localhost:8000",  # Main API
        "http://localhost:8003",  # This service
        os.getenv("FRONTEND_URL", "*")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# FILE UPLOAD LIMITS
# ============================================================================

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    """Limit file upload size"""
    if request.method == "POST":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_FILE_SIZE:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024} MB"
                }
            )

    return await call_next(request)


# ============================================================================
# INCLUDE TASK EXTRACTION ROUTER
# ============================================================================

from task_extraction_api import router as task_extraction_router

app.include_router(task_extraction_router)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Sentry AI - Task Extraction Service",
        "version": "1.0.0",
        "status": "operational",
        "port": 8003,
        "documentation": "/docs",
        "endpoints": {
            "extract_single": "POST /api/tasks/extract-tasks",
            "extract_batch": "POST /api/tasks/extract-tasks/batch",
            "history": "GET /api/tasks/extraction-history/{user_id}",
            "health": "GET /api/tasks/health"
        },
        "supported_formats": {
            "audio": ["MP3", "WAV", "M4A", "OGG", "FLAC"],
            "documents": ["PDF", "DOCX", "DOC"],
            "images": ["PNG", "JPG", "JPEG", "BMP", "TIFF"],
            "text": ["TXT", "MD"]
        },
        "ai_models": {
            "text_extraction": os.getenv("OLLAMA_TEXT_MODEL", "llama3.1:8b"),
            "vision_extraction": os.getenv("OLLAMA_VISION_MODEL", "llava"),
            "speech_recognition": "Vosk (Arabic/English)",
            "ocr": "Tesseract"
        }
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Service health check"""
    health_status = {
        "service": "task-extraction",
        "status": "healthy",
        "port": 8003,
        "components": {}
    }

    # Check database connection
    try:
        from sqlalchemy import create_engine
        engine = create_engine(os.getenv("DATABASE_URL"))
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health_status["components"]["database"] = "connected"
    except Exception as e:
        health_status["components"]["database"] = f"error: {str(e)[:50]}"
        health_status["status"] = "degraded"

    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            health_status["components"]["ollama"] = "running"
        else:
            health_status["components"]["ollama"] = "not responding"
            health_status["status"] = "degraded"
    except:
        health_status["components"]["ollama"] = "not running"
        health_status["status"] = "degraded"

    # Check processors availability
    health_status["components"]["processors"] = {
        "audio": "available",
        "document": "available",
        "vision": "available" if health_status["components"]["ollama"] == "running" else "unavailable",
        "handwritten": "available",
        "text": "available"
    }

    return health_status


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    # Configuration
    host = os.getenv("TASK_EXTRACTION_HOST", "0.0.0.0")
    port = int(os.getenv("TASK_EXTRACTION_PORT", "8003"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"

    print(f"\nStarting Task Extraction Service...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}\n")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
