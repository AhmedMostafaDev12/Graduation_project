# Quick Start Guide - Task Extraction Service

## 🚀 Starting the Service

The Task Extraction Service runs **independently** on **port 8003** (separate from your main burnout detection service on port 8000).

### Option 1: Using the Startup Script (Easiest)

**Windows:**
```bash
cd backend\app\services\task_extraction
start_service.bat
```

**Linux/Mac:**
```bash
cd backend/app/services/task_extraction
chmod +x start_service.sh
./start_service.sh
```

### Option 2: Using Python Directly

```bash
cd backend/app/services/task_extraction
python main.py
```

### Option 3: Using Uvicorn

```bash
cd backend/app/services/task_extraction
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

## ✅ Verify It's Running

Once started, you should see:

```
================================================================================
SERVICE READY
================================================================================

API Documentation: http://localhost:8003/docs
Service Info:      http://localhost:8003/
Health Check:      http://localhost:8003/health
```

Open your browser and go to:
- **API Docs**: http://localhost:8003/docs
- **Service Info**: http://localhost:8003/

## 📡 Using the API

### 1. Extract Tasks from a File

**Using cURL:**
```bash
curl -X POST "http://localhost:8003/api/tasks/extract-tasks" \
  -F "file=@document.pdf" \
  -F "user_id=123" \
  -F "save_to_db=true"
```

**Using Python:**
```python
import requests

files = {"file": open("document.pdf", "rb")}
data = {"user_id": 123, "save_to_db": True}

response = requests.post(
    "http://localhost:8003/api/tasks/extract-tasks",
    files=files,
    data=data
)

result = response.json()
print(f"Extracted {result['tasks_extracted']} tasks!")
```

**Using Postman:**
1. Set method to `POST`
2. URL: `http://localhost:8003/api/tasks/extract-tasks`
3. Go to Body → form-data
4. Add key `file` (type: File), select your file
5. Add key `user_id` (type: Text), value: `123`
6. Add key `save_to_db` (type: Text), value: `true`
7. Click Send

### 2. Extract from Multiple Files (Batch)

```bash
curl -X POST "http://localhost:8003/api/tasks/extract-tasks/batch" \
  -F "files=@document1.pdf" \
  -F "files=@audio.mp3" \
  -F "files=@notes.jpg" \
  -F "user_id=123"
```

### 3. Get Extraction History

```bash
curl "http://localhost:8003/api/tasks/extraction-history/123?limit=10"
```

### 4. Health Check

```bash
curl "http://localhost:8003/health"
```

## 📋 Response Example

```json
{
  "success": true,
  "tasks_extracted": 3,
  "tasks_saved": 3,
  "tasks": [
    {
      "title": "Complete project proposal",
      "description": "Write and submit the Q1 project proposal",
      "priority": "HIGH",
      "deadline": "2025-01-15",
      "assignee": "John Doe",
      "category": "project",
      "estimated_hours": 8.0
    },
    {
      "title": "Review code changes",
      "description": "Review PR #234 and provide feedback",
      "priority": "MEDIUM",
      "deadline": "2025-01-10",
      "assignee": "Jane Smith",
      "category": "assignment",
      "estimated_hours": 2.0
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

## 🔧 Configuration

The service uses environment variables from your `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/database

# Ollama Models
OLLAMA_TEXT_MODEL="llama3.1:8b"
OLLAMA_VISION_MODEL="llava"

# Optional: Service Configuration
TASK_EXTRACTION_HOST=0.0.0.0
TASK_EXTRACTION_PORT=8003
API_RELOAD=true
```

## 🏗️ Architecture

```
Your System:
├── Main Burnout Service (Port 8000)
│   └── backend/app/services/burn_out_service/api/main.py
│
└── Task Extraction Service (Port 8003) ← NEW!
    └── backend/app/services/task_extraction/main.py

Both services:
✓ Run independently
✓ Share the same database
✓ Can communicate with each other
✓ Have separate API documentation
```

## 📞 Connecting Services

Your main burnout service can call the task extraction service:

```python
import requests

# From your main service (port 8000), call task extraction (port 8003)
response = requests.post(
    "http://localhost:8003/api/tasks/extract-tasks",
    files={"file": file_content},
    data={"user_id": user_id}
)

tasks = response.json()
```

## 🛠️ Troubleshooting

### Service won't start
```bash
# Check if port 8003 is already in use
netstat -ano | findstr :8003  # Windows
lsof -i :8003                  # Linux/Mac

# Kill the process if needed
taskkill /PID <PID> /F         # Windows
kill -9 <PID>                  # Linux/Mac
```

### Database connection error
```bash
# Check your .env file
# Make sure DATABASE_URL is correct
# Test connection:
psql postgresql://user:pass@localhost:5432/database
```

### Ollama not running
```bash
# Start Ollama
ollama serve

# Check if models are installed
ollama list

# Pull models if needed
ollama pull llama3.1:8b
ollama pull llava
```

### Import errors
```bash
# Install dependencies
pip install -r requirements.txt

# Make sure you're in the right directory
cd backend/app/services/task_extraction
```

## 📚 Next Steps

1. **Test the service**: Try uploading different file types
2. **Check the docs**: Visit http://localhost:8003/docs
3. **Monitor health**: Check http://localhost:8003/health
4. **View logs**: Watch the console for processing details

## 🎯 Supported File Types

| Type | Extensions | Example |
|------|-----------|---------|
| Audio | MP3, WAV, M4A, OGG | `meeting.mp3` |
| Documents | PDF, DOCX, DOC | `report.pdf` |
| Images | PNG, JPG, JPEG, BMP | `whiteboard.jpg` |
| Handwritten | PNG, JPG (handwriting) | `notes.jpg` |
| Text | TXT, MD | `tasks.txt` |

## 💡 Tips

- **Large files**: Max upload size is 100 MB
- **Batch processing**: Process up to 10 files at once
- **Translation**: Automatically translates non-English text
- **Database**: All tasks are saved with status "Todo"
- **Validation**: Tasks are validated before saving

---

Need help? Check the full documentation in [README.md](README.md)
