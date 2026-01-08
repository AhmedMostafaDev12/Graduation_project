# Task Extraction Service

Complete task extraction system that processes ANY input type and saves tasks to your database with valid JSON output.

## 🎯 Features

- **Multi-format Support**: Audio, Documents, Images, Handwritten Notes, Text
- **Automatic Type Detection**: Intelligently selects the right processor
- **Database Integration**: Direct save to PostgreSQL tasks table
- **Valid JSON Output**: Fully validated with Pydantic models
- **Translation Support**: Automatic translation from any language to English
- **FastAPI Endpoints**: Ready-to-use REST API
- **Batch Processing**: Handle multiple files at once

## 📁 Architecture

```
task_extraction/
├── unified_task_extractor.py    # Main unified service
├── task_extraction_api.py        # FastAPI endpoints
│
├── audio_processor.py            # Vosk → Arabic/English transcription
├── document_processor.py         # Unstructured → Tables, images, text
├── document_processor_ocr.py     # Tesseract OCR → Scanned docs
├── handwritten_processor.py      # OCR optimized → Handwritten notes
├── vision_extractor.py           # LLaVa → Image task extraction
├── text_extractor.py             # Llama → Text task extraction
│
└── audio_utils.py                # Audio format conversion
```

## 🚀 Quick Start

### 1. Extract Tasks from Any File

```python
from unified_task_extractor import extract_tasks_from_file
from sqlalchemy.orm import Session

# Extract and save to database
result = extract_tasks_from_file(
    file_path="meeting_recording.mp3",
    user_id=123,
    database_session=db_session,
    save_to_db=True
)

print(f"Extracted {result['tasks_extracted']} tasks")
print(f"Saved {result['tasks_saved']} tasks to database")
```

### 2. Using the API

```bash
# Start your FastAPI server
uvicorn main:app --reload

# Extract tasks from file
curl -X POST "http://localhost:8000/api/tasks/extract-tasks" \
  -F "file=@meeting_notes.pdf" \
  -F "user_id=123" \
  -F "save_to_db=true"
```

### 3. Test Script

```bash
# Extract from any file type
python test_unified_extraction.py document.pdf

# With specific user ID
python test_unified_extraction.py notes.mp3 456

# Save to JSON file
python test_unified_extraction.py tasks.txt --save-json output.json

# Without database save
python test_unified_extraction.py image.jpg --no-db
```

## 📋 Supported File Types

| Type | Extensions | Processor | AI Model |
|------|-----------|-----------|----------|
| **Audio** | MP3, WAV, M4A, OGG, FLAC | Vosk + Llama | Vosk (transcription) + Llama 3.1 8B (extraction) |
| **Documents** | PDF, DOCX, DOC | Unstructured + Llama/LLaVa | Llama 3.1 8B (text) + LLaVa (images) |
| **Images** | PNG, JPG, JPEG, BMP, TIFF | LLaVa Vision | LLaVa (multimodal) |
| **Handwritten** | PNG, JPG (handwriting), PDF (scanned) | Tesseract OCR + Llama | Tesseract + Llama 3.1 8B |
| **Text** | TXT, MD | Direct extraction | Llama 3.1 8B |

## 🔧 Configuration

### Environment Variables

```bash
# .env file
DATABASE_URL=postgresql://user:pass@localhost:5432/database
OLLAMA_TEXT_MODEL="llama3.1:8b"      # For text extraction
OLLAMA_VISION_MODEL="llava"           # For image extraction
```

### Database Schema

Tasks are saved to the `tasks` table:

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    task_type VARCHAR(20) DEFAULT 'task',
    status VARCHAR(50) DEFAULT 'Todo',
    priority VARCHAR(20),
    due_date TIMESTAMP,
    assigned_to VARCHAR(100),
    can_delegate BOOLEAN DEFAULT TRUE,
    estimated_hours FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 📊 Response Format

### Success Response

```json
{
  "success": true,
  "tasks_extracted": 5,
  "tasks_saved": 5,
  "tasks": [
    {
      "title": "Complete project proposal",
      "description": "Write and submit the Q1 project proposal",
      "priority": "HIGH",
      "deadline": "2025-01-15",
      "assignee": "John Doe",
      "category": "project",
      "estimated_hours": 8.0
    }
  ],
  "source_file": "meeting_notes.pdf",
  "source_type": "document",
  "processor_used": "document",
  "processing_time_seconds": 12.34,
  "errors": [],
  "warnings": []
}
```

## 🔌 API Endpoints

### POST /api/tasks/extract-tasks

Extract tasks from single file.

**Request:**
```
Content-Type: multipart/form-data

file: File
user_id: Integer
save_to_db: Boolean (optional, default: true)
translate: Boolean (optional, default: true)
processor_type: String (optional: 'audio', 'document', 'vision', 'handwritten', 'text')
```

**Response:** TaskExtractionResult (JSON)

### POST /api/tasks/extract-tasks/batch

Extract tasks from multiple files.

**Request:**
```
Content-Type: multipart/form-data

files: File[]
user_id: Integer
save_to_db: Boolean (optional)
translate: Boolean (optional)
```

**Response:** Batch summary with individual results

### GET /api/tasks/extraction-history/{user_id}

Get recent extracted tasks for user.

**Parameters:**
- `user_id`: User ID (path)
- `limit`: Number of tasks (query, default: 10)

**Response:** List of tasks

## 🎨 Processing Pipeline

```mermaid
graph TD
    A[Upload File] --> B{Detect Type}
    B -->|Audio| C[Vosk Transcription]
    B -->|Document| D[Unstructured Parser]
    B -->|Image| E[LLaVa Vision]
    B -->|Handwritten| F[Tesseract OCR]
    B -->|Text| G[Direct Input]

    C --> H[Translation if needed]
    D --> I{Content Type}
    F --> H
    G --> H

    I -->|Text/Tables| H
    I -->|Images| E

    H --> J[Llama Task Extraction]
    E --> K[LLaVa Task Extraction]

    J --> L[Validate Tasks]
    K --> L

    L --> M[Save to Database]
    M --> N[JSON Response]
```

## 🧪 Processor Details

### Audio Processor
- **Model**: Vosk (offline speech recognition)
- **Languages**: Arabic, English (expandable)
- **Features**: Format conversion (MP3→WAV), transcription save
- **Output**: Transcribed text → Task extraction

### Document Processor (Unstructured)
- **Strategy**: hi_res (best for images/tables)
- **Features**: Table extraction, image detection, text parsing
- **Routing**: Text/tables → Llama, Images → LLaVa
- **Best for**: PDFs, DOCX with mixed content

### Vision Extractor (LLaVa)
- **Model**: LLaVa (multimodal vision-language model)
- **Features**: Understands images with text
- **Best for**: Screenshots, whiteboards, diagrams, photos of tasks

### Handwritten Processor
- **Model**: Tesseract OCR
- **Features**: Image preprocessing, handwriting optimization
- **Preprocessing**: Grayscale, contrast enhancement, sharpening, noise reduction
- **Best for**: Handwritten notes, scanned paper, sticky notes

### OCR Document Processor
- **Model**: Tesseract OCR
- **Features**: PDF → Images → OCR → Text
- **Best for**: Scanned typed documents
- **DPI**: 300 (configurable)

## 🛠️ Installation

### Required Packages

```bash
pip install -r requirements.txt
```

### System Dependencies

**Tesseract OCR** (for handwritten/scanned docs):
```bash
# Windows
Download from: https://github.com/UB-Mannheim/tesseract/wiki

# Linux
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

**Poppler** (for PDF processing):
```bash
# Windows
Download from: https://github.com/oschwartz10612/poppler-windows/releases

# Linux
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

**Vosk Models** (for audio):
```bash
# Download Arabic model
wget https://alphacephei.com/vosk/models/vosk-model-ar-0.22-linto-1.1.0.zip
unzip vosk-model-ar-0.22-linto-1.1.0.zip -d models/
```

**Ollama Models**:
```bash
# Install Llama for text
ollama pull llama3.1:8b

# Install LLaVa for vision
ollama pull llava
```

## 📝 Usage Examples

### Python

```python
# 1. Extract from audio
result = extract_tasks_from_file("meeting.mp3", user_id=123, database_session=db)

# 2. Extract from PDF
result = extract_tasks_from_file("report.pdf", user_id=123, database_session=db)

# 3. Extract from handwritten notes
result = extract_tasks_from_file("notes.jpg", user_id=123, database_session=db)

# 4. Save to JSON file
from unified_task_extractor import extract_tasks_to_json_file

extract_tasks_to_json_file(
    file_path="tasks.txt",
    user_id=123,
    output_file="output.json",
    database_session=db
)

# 5. Without database
result = extract_tasks_from_file(
    file_path="notes.txt",
    user_id=123,
    save_to_db=False
)
```

### cURL

```bash
# Single file extraction
curl -X POST "http://localhost:8000/api/tasks/extract-tasks" \
  -F "file=@meeting.mp3" \
  -F "user_id=123"

# Batch extraction
curl -X POST "http://localhost:8000/api/tasks/extract-tasks/batch" \
  -F "files=@file1.pdf" \
  -F "files=@file2.mp3" \
  -F "files=@file3.jpg" \
  -F "user_id=123"

# Get extraction history
curl "http://localhost:8000/api/tasks/extraction-history/123?limit=20"
```

## 🔍 Validation

All extracted tasks are validated with Pydantic:

- **Title**: Required, 1-255 characters
- **Priority**: Normalized to LOW, MEDIUM, HIGH, URGENT, CRITICAL
- **Category**: Normalized to assignment, meeting, exam, project, general
- **Deadline**: Validated and converted to YYYY-MM-DD format
- **Estimated Hours**: Must be >= 0

Invalid tasks are logged as warnings but don't stop the process.

## 🏗️ Integration with FastAPI

Add to your main FastAPI app:

```python
from fastapi import FastAPI
from app.services.task_extraction.task_extraction_api import router

app = FastAPI()
app.include_router(router)

# Now available at /api/tasks/*
```

## 📈 Performance

Typical processing times:
- **Text file**: 1-2 seconds
- **Audio (5 min)**: 10-15 seconds
- **PDF (10 pages)**: 15-30 seconds
- **Image**: 3-5 seconds
- **Handwritten notes**: 5-10 seconds

## 🔒 Security

- File uploads are stored in temp directories and cleaned up
- Input validation with Pydantic models
- SQL injection prevention with SQLAlchemy ORM
- File size limits (configure in FastAPI)

## 🐛 Troubleshooting

**Poppler not found:**
```python
# Update POPPLER_PATH in document_processor_ocr.py and handwritten_processor.py
POPPLER_PATH = r"C:\path\to\poppler\bin"
```

**Vosk model not found:**
```bash
# Download and place in models/ directory
# Update path in audio_processor.py if needed
```

**Database connection failed:**
```bash
# Check DATABASE_URL in .env
# Ensure PostgreSQL is running
```

**Ollama not responding:**
```bash
# Start Ollama service
ollama serve

# Check if models are installed
ollama list
```

## 📚 Additional Resources

- [Vosk Documentation](https://alphacephei.com/vosk/)
- [Unstructured.io Docs](https://unstructured-io.github.io/unstructured/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [Ollama Models](https://ollama.ai/library)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

This is an internal Sentry AI service. For questions or improvements, contact the development team.

---

**Sentry AI Team** | 2025
