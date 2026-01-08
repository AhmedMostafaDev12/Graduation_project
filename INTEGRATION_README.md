# Sentry AI - Complete Integration Guide

**Last Updated:** 2025-12-29
**Version:** 2.0
**Status:** ✅ Fully Integrated

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [What Was Integrated](#what-was-integrated)
3. [Database Integration](#database-integration)
4. [Backend Code Updates](#backend-code-updates)
5. [AI Services Enhancements](#ai-services-enhancements)
6. [Service-to-Service Communication](#service-to-service-communication)
7. [API Endpoints Summary](#api-endpoints-summary)
8. [Setup & Configuration](#setup--configuration)
9. [Testing the Integration](#testing-the-integration)
10. [Architecture Diagrams](#architecture-diagrams)

---

## 📖 Overview

This document covers the complete integration of the Sentry AI platform, which unifies:
- **Backend Services** (Authentication, Task Management, User Management)
- **AI Services** (Burnout Analysis, Task Extraction, Notebook Library)

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Sentry AI Platform                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Backend (Port 5000)     Burnout (Port 8000)                │
│  ├─ Authentication       ├─ Auto-Analysis ✨ NEW            │
│  ├─ Task CRUD            ├─ Recommendations                 │
│  ├─ User Management      └─ Workload Tracking               │
│  └─ Integrations                                             │
│                                                               │
│  Task Extraction (8003)  Notebook Library (8001)            │
│  ├─ Audio → Tasks        ├─ Document Upload                 │
│  ├─ Document → Tasks     ├─ RAG Chat                        │
│  ├─ Image → Tasks        └─ Embeddings                      │
│  └─ Calls Backend ✨ NEW                                    │
│                                                               │
│  AI Companion (8002) ✨ NEW                                 │
│  ├─ Emotional Support    ├─ Task Queries                    │
│  ├─ Diary Processing     ├─ Burnout Checks                  │
│  ├─ Audio/Text Chat      └─ Task Creation                   │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│              Unified PostgreSQL Database                     │
│  ├─ users, auth_providers, integrations                     │
│  ├─ tasks (unified schema)                                  │
│  ├─ uploads (new - tracks all file uploads) ✨ NEW          │
│  ├─ qualitative_data (emotional entries) ✨ NEW             │
│  ├─ user_profiles, burnout_analyses                         │
│  └─ Vector DB (embeddings)                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔗 What Was Integrated

### Phase 1: Database Unification ✅

**Goal:** Create a single source of truth for all data

**Achievements:**
- ✅ Merged backend and AI database schemas
- ✅ Created unified `tasks` table with all fields from both systems
- ✅ Added `users`, `auth_providers`, `integrations` tables from backend
- ✅ Created new `uploads` table for file tracking
- ✅ Established foreign key relationships between all tables

**Key Decision:** Use `due_date` instead of `deadline` (AI's convention)

---

### Phase 2: Backend Code Updates ✅

**Goal:** Make backend compatible with AI services

**Achievements:**
- ✅ Updated Task model to match unified schema
- ✅ Changed `deadline` → `due_date` everywhere
- ✅ Added AI-specific fields (task_type, start_time, end_time, etc.)
- ✅ Preserved backend developer's new features (integration_provider_task_id, TempTrelloToken)

**Files Modified:**
- `backend_services/app/models.py` - Task model updated
- `backend_services/app/schemas.py` - TaskCreate and TaskRead schemas updated

---

### Phase 3: AI Services Enhancements ✅

**Goal:** Make AI services database-aware and integrated

#### 3.1 Burnout Service - Auto-Fetch Mode

**Problem:** Required manual JSON input for tasks/meetings
**Solution:** Added auto-fetch endpoint that reads directly from database

**New Endpoint:** `POST /api/burnout/analyze-auto/{user_id}`

**Before:**
```json
POST /api/burnout/analyze
{
  "user_id": 1,
  "quantitative_metrics": {
    "total_active_tasks": 15,
    "overdue_tasks": 5,
    ...
  },
  "qualitative_data": {...}
}
```

**After:**
```bash
POST /api/burnout/analyze-auto/1
# No request body needed! Everything auto-fetched from database
```

**Implementation:**
- Uses `get_complete_user_context()` from `task_database_integration.py`
- Auto-calculates metrics from tasks table
- Fetches qualitative data from qualitative_data table
- Returns complete analysis with task/meeting counts

**File Modified:** `AI_services/app/services/burn_out_service/api/routers/workload.py`

---

#### 3.2 Task Extraction - Upload Tracking

**Problem:** Files uploaded but not tracked in database
**Solution:** Record all uploads in `uploads` table with processing status

**What's Tracked:**
```python
{
  "user_id": 123,
  "filename": "meeting_notes.pdf",
  "file_path": "/tmp/tmpXXXX/meeting_notes.pdf",
  "file_size_bytes": 524288,
  "mime_type": "application/pdf",
  "upload_type": "document",  # audio/document/image/handwritten/text
  "processing_status": "completed",  # pending/processing/completed/failed
  "extraction_result": {
    "tasks_extracted": 5,
    "tasks_saved": 5,
    "processor_used": "document",
    "processing_time_seconds": 12.34
  },
  "uploaded_at": "2025-12-29T10:00:00",
  "processed_at": "2025-12-29T10:00:12"
}
```

**Benefits:**
- Complete audit trail of all extractions
- Track success/failure of processing
- Query upload history per user
- Store extraction results in JSONB for analytics

**File Modified:** `AI_services/app/services/task_extraction/task_extraction_api.py`

---

#### 3.3 Notebook Library - Upload Tracking & User Association

**Problem:** Document uploads not tracked, no user_id association
**Solution:** Require user_id parameter and record all uploads

**Breaking Change:** Both notebook endpoints now require `user_id` parameter

**Before:**
```javascript
POST /notebooks
Body: { file: File }
```

**After:**
```javascript
POST /notebooks
Body: {
  file: File,
  user_id: 123  // ← NOW REQUIRED
}
```

**What's Tracked:**
- User ownership of notebooks
- Document upload metadata
- Processing status
- Notebook ID and document ID linkage

**File Modified:** `AI_services/app/services/notebook_library/FastAPI_app.py`

---

### Phase 4: Service-to-Service Communication ✅

**Goal:** Make services automatically call each other for coordinated workflows

#### 4.1 Backend → Burnout Integration

**Trigger:** Any task create/update/delete
**Action:** Automatically run burnout analysis

**Implementation:**
```python
# In backend_services/app/routers/task.py

@router.post("/")
def create_task(...):
    # 1. Save task to database
    db.add(task)
    db.commit()

    # 2. Trigger burnout analysis
    trigger_burnout_analysis(current_user.id)  # ✨ NEW

    return task
```

**How it works:**
- `trigger_burnout_analysis()` calls `POST /api/burnout/analyze-auto/{user_id}`
- Non-blocking - logs errors but doesn't fail the request
- Uses environment variable `BURNOUT_SERVICE_URL` (defaults to localhost:8000)

**Applies to:**
- ✅ Task creation (`POST /api/tasks/`)
- ✅ Task update (`PUT /api/tasks/{task_id}`)
- ✅ Task deletion (`DELETE /api/tasks/{task_id}`)

**File Modified:** `backend_services/app/routers/task.py`

---

#### 4.2 Task Extraction → Backend Integration

**Previous:** Task Extraction saved directly to database (bypassed validation)
**Now:** Task Extraction calls Backend API (proper validation + triggers burnout)

**Implementation:**
```python
# In AI_services/.../unified_task_extractor.py

def _save_tasks_to_database(tasks, user_id):
    # Call backend service-to-service endpoint
    response = requests.post(
        f"{BACKEND_SERVICE_URL}/api/tasks/service/create",
        params={"user_id": user_id},
        json=task_data
    )
    # Backend validates, saves, and triggers burnout analysis
```

**New Backend Endpoint:**
```python
# In backend_services/app/routers/task.py

@router.post("/service/create")  # ✨ NEW - Service-to-service endpoint
def create_task_from_service(task: TaskCreate, user_id: int, ...):
    # No authentication required (internal service call)
    # Saves task and triggers burnout analysis
```

**Benefits:**
- ✅ Backend is single source of truth for task creation
- ✅ All validation happens in one place
- ✅ Burnout analysis automatically triggered
- ✅ Consistent workflow across all task sources

**Fallback:** If backend is unavailable, falls back to direct database save (with warning)

**Files Modified:**
- `AI_services/app/services/task_extraction/unified_task_extractor.py`
- `backend_services/app/routers/task.py`

---

## 🗄️ Database Integration

### Unified Tasks Table Schema

```sql
CREATE TABLE tasks (
    -- Primary key
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Core fields
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',

    -- Classification
    task_type VARCHAR(20) DEFAULT 'task',  -- 'task' or 'meeting'
    status VARCHAR(50),
    priority VARCHAR(20),
    category VARCHAR(100),

    -- Timing (AI convention: due_date, not deadline)
    due_date TIMESTAMP WITH TIME ZONE,
    start_time TIMESTAMP WITH TIME ZONE,  -- For meetings
    end_time TIMESTAMP WITH TIME ZONE,    -- For meetings

    -- Source tracking (Backend feature)
    source VARCHAR(50),  -- 'sentry', 'google', 'extracted', etc.

    -- Integration IDs (Backend feature)
    integration_provider_task_id VARCHAR(255) UNIQUE,
    google_task_id VARCHAR(255) UNIQUE,
    google_tasklist_id VARCHAR(255),

    -- AI Analysis fields
    assigned_to VARCHAR(100),
    can_delegate BOOLEAN DEFAULT TRUE,
    estimated_hours FLOAT,
    is_recurring BOOLEAN DEFAULT FALSE,
    is_optional BOOLEAN DEFAULT FALSE,

    -- Meeting-specific (AI feature)
    attendees TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_source ON tasks(source);
CREATE INDEX idx_tasks_integration_provider_id ON tasks(integration_provider_task_id);
```

### Uploads Table (NEW)

```sql
CREATE TABLE uploads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- File metadata
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100),

    -- Processing metadata
    upload_type VARCHAR(50) NOT NULL,  -- 'audio', 'document', 'image', 'notebook'
    processing_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
    extraction_result JSONB,  -- Store processing results

    -- Session tracking
    session_id VARCHAR(100),

    -- Timestamps
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Indexes
CREATE INDEX idx_uploads_user_id ON uploads(user_id);
CREATE INDEX idx_uploads_status ON uploads(processing_status);
CREATE INDEX idx_uploads_type ON uploads(upload_type);
```

### Database Relationships

```
users (PRIMARY)
├── user_profiles (user_id FK)
│   ├── burnout_analyses (user_profile_id FK)
│   ├── user_preferences (user_profile_id FK)
│   ├── user_constraints (user_profile_id FK)
│   └── user_behavioral_profiles (user_profile_id FK)
├── tasks (user_id FK)
├── qualitative_data (user_id FK)
├── auth_providers (user_id FK)
├── integrations (user_id FK)
└── uploads (user_id FK)
```

### Migration Scripts

**Run these SQL scripts in order:**

1. `database_migration.sql` - Main migration (users, tasks, uploads tables)
2. `backend_developer_changes.sql` - Backend developer's additions (integration_provider_task_id, temp_trello_tokens)

```bash
psql -U postgres -p 5433 -d sentry_ai -f database_migration.sql
psql -U postgres -p 5433 -d sentry_ai -f backend_developer_changes.sql
```

---

## 🔄 Backend Code Updates

### Files Modified

#### 1. `backend_services/app/models.py`

**Changes:**
- Updated Task model to match AI schema
- Changed `deadline` → `due_date`
- Changed `added_at` → `created_at`
- Added AI fields: `task_type`, `start_time`, `end_time`, `assigned_to`, `can_delegate`, `estimated_hours`, `is_recurring`, `is_optional`, `attendees`
- Preserved backend features: `integration_provider_task_id`, `google_task_id`

#### 2. `backend_services/app/schemas.py`

**Changes:**
- Updated `TaskCreate` schema: `deadline` → `due_date`, added AI fields
- Updated `TaskRead` schema: `deadline` → `due_date`, added AI fields and timestamps
- Made `category` optional
- Updated Pydantic config to `from_attributes = True` (Pydantic v2)

#### 3. `backend_services/app/routers/task.py`

**Major additions:**
- Added `trigger_burnout_analysis()` helper function
- Integrated burnout calls in create/update/delete endpoints
- Added new `/service/create` endpoint for internal service calls

**New imports:**
```python
import requests
import os
import logging
```

**New helper function:**
```python
def trigger_burnout_analysis(user_id: int):
    """
    Trigger burnout analysis after task changes.
    Non-blocking - logs errors but doesn't fail the request.
    """
    try:
        response = requests.post(
            f"{BURNOUT_SERVICE_URL}/api/burnout/analyze-auto/{user_id}",
            params={"store_history": True},
            timeout=5
        )
        if response.status_code == 200:
            logger.info(f"✅ Burnout analysis triggered for user {user_id}")
    except Exception as e:
        logger.error(f"❌ Error triggering burnout analysis: {e}")
```

**New endpoint:**
```python
@router.post("/service/create")
def create_task_from_service(task: TaskCreate, user_id: int, db: Session):
    """
    NO AUTHENTICATION - For service-to-service communication only
    """
    task_obj = models.Task(**task.dict(), user_id=user_id)
    db.add(task_obj)
    db.commit()
    trigger_burnout_analysis(user_id)
    return task_obj
```

---

## 🤖 AI Services Enhancements

### 1. Burnout Service

**File:** `AI_services/app/services/burn_out_service/api/routers/workload.py`

**New Endpoint:**
```python
@router.post("/burnout/analyze-auto/{user_id}")
async def analyze_burnout_auto(
    user_id: int,
    store_history: bool = True,
    db: Session = Depends(get_db)
):
    """
    Auto-fetch tasks from database and run burnout analysis.
    No manual input required!
    """
    from integrations.task_database_integration import get_complete_user_context

    # Auto-fetch all data from database
    context = get_complete_user_context(user_id=user_id, session=db)

    # Run analysis
    integration = BurnoutSystemIntegration(db)
    analysis_result = integration.analyze_user_burnout(
        user_id=user_id,
        quantitative_metrics=context['metrics'],        # Auto-calculated
        qualitative_data=context['qualitative_data'],   # Auto-fetched
        store_history=store_history
    )

    return {
        "status": "success",
        "data_source": "database",
        "tasks_analyzed": len(context['tasks']),
        "meetings_analyzed": len(context['meetings']),
        "analysis": analysis_result
    }
```

---

### 2. Task Extraction Service

**File:** `AI_services/app/services/task_extraction/task_extraction_api.py`

**Enhanced `process_file_extraction()` function:**

```python
async def process_file_extraction(...):
    # Save uploaded file
    content = await file.read()
    file_size = len(content)

    # Record upload in database (NEW)
    if save_to_db and db:
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
        db.flush()
        upload_id = upload_record.id

    # Extract tasks
    result = extractor.extract_and_save_tasks(...)

    # Update upload record with results (NEW)
    if upload_id:
        upload_record.processing_status = 'completed'
        upload_record.processed_at = datetime.utcnow()
        upload_record.extraction_result = {
            "tasks_extracted": result.tasks_extracted,
            "tasks_saved": result.tasks_saved,
            ...
        }
        db.commit()

    return response
```

**File:** `AI_services/app/services/task_extraction/unified_task_extractor.py`

**Replaced `_save_tasks_to_database()` method:**

```python
def _save_tasks_to_database(self, tasks, user_id):
    """
    Save tasks via Backend API (not direct database).
    Ensures validation and triggers burnout analysis.
    """
    BACKEND_SERVICE_URL = os.getenv("BACKEND_SERVICE_URL", "http://localhost:5000")

    for task in tasks:
        task_data = {
            "title": task.title,
            "description": task.description,
            "status": "Todo",
            "priority": task.priority,
            "due_date": task.deadline,
            "source": "extracted"
        }

        # Call backend service endpoint
        response = requests.post(
            f"{BACKEND_SERVICE_URL}/api/tasks/service/create",
            params={"user_id": user_id},
            json=task_data
        )

    # Fallback to direct DB if backend unavailable
    # See code for full implementation
```

---

### 3. Notebook Library Service

**File:** `AI_services/app/services/notebook_library/FastAPI_app.py`

**Updated endpoints to require `user_id`:**

```python
@app.post("/notebooks")
async def create_notebook(
    file: UploadFile = File(...),
    user_id: int = Form(...),  # ← NOW REQUIRED
    db: Session = Depends(get_db)
):
    # Save file
    content = await file.read()
    file_size = len(content)

    # Record upload in database (NEW)
    upload_record = Upload(
        user_id=user_id,
        filename=file.filename,
        file_path=file_path,
        file_size_bytes=file_size,
        upload_type='notebook',
        processing_status='processing'
    )
    db.add(upload_record)
    db.flush()

    # Process document
    result = processor.process_file(file_path, doc_id)

    # Update upload status (NEW)
    upload_record.processing_status = 'completed'
    upload_record.processed_at = datetime.utcnow()
    upload_record.extraction_result = {
        "notebook_id": notebook_id,
        "doc_id": doc_id,
        "result": result
    }
    db.commit()

    return {
        "notebook_id": notebook_id,
        "upload_id": upload_id  # ← NEW
    }
```

**Same changes applied to:** `POST /notebooks/{notebook_id}/documents`

---

## 📡 API Endpoints Summary

### Backend Service (Port 5000)

#### Task Management
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/tasks/` | Create task (triggers burnout) | Yes |
| GET | `/api/tasks/` | Get all user tasks | Yes |
| GET | `/api/tasks/{task_id}` | Get specific task | Yes |
| PUT | `/api/tasks/{task_id}` | Update task (triggers burnout) | Yes |
| DELETE | `/api/tasks/{task_id}` | Delete task (triggers burnout) | Yes |
| POST | `/api/tasks/service/create` | Create task from service (no auth) | No ⚠️ |

⚠️ **Security Note:** `/service/create` endpoint has no authentication for internal service calls. In production, add IP whitelist or service token validation.

---

### Burnout Service (Port 8000)

#### Burnout Analysis
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/burnout/analyze` | Manual analysis (requires JSON input) | No |
| POST | `/api/burnout/analyze-auto/{user_id}` | ✨ Auto-fetch mode (NEW) | No |
| GET | `/api/burnout/status/{user_id}` | Get burnout status | No |
| GET | `/api/burnout/history/{user_id}` | Get analysis history | No |

**New Auto-Fetch Endpoint:**
```bash
POST /api/burnout/analyze-auto/1?store_history=true

Response:
{
  "status": "success",
  "data_source": "database",
  "tasks_analyzed": 15,
  "meetings_analyzed": 6,
  "analysis": {
    "final_score": 65,
    "burnout_level": "MODERATE",
    ...
  }
}
```

---

### Task Extraction Service (Port 8003)

#### Extraction Endpoints (All now track uploads)
| Method | Endpoint | Description | Upload Tracking |
|--------|----------|-------------|-----------------|
| POST | `/api/tasks/extract/audio` | Extract from audio | ✅ Yes |
| POST | `/api/tasks/extract/document` | Extract from PDF/DOCX | ✅ Yes |
| POST | `/api/tasks/extract/image` | Extract from images | ✅ Yes |
| POST | `/api/tasks/extract/handwritten` | Extract from handwritten | ✅ Yes |
| POST | `/api/tasks/extract/text` | Extract from text | ✅ Yes |
| POST | `/api/tasks/extract/batch` | Batch extraction | ✅ Yes |
| GET | `/api/tasks/extraction-history/{user_id}` | Get history | N/A |

**Response now includes:**
```json
{
  "success": true,
  "tasks_extracted": 5,
  "tasks_saved": 5,
  "upload_id": 42,  // ← NEW
  "tasks": [...],
  ...
}
```

---

### Notebook Library Service (Port 8001)

#### Notebook Management (Now requires user_id)
| Method | Endpoint | Description | Breaking Change |
|--------|----------|-------------|-----------------|
| POST | `/notebooks` | Create notebook | ⚠️ Requires `user_id` |
| POST | `/notebooks/{id}/documents` | Upload document | ⚠️ Requires `user_id` |
| GET | `/notebooks` | List notebooks | No change |
| POST | `/notebooks/{id}/chat` | Chat with notebook | No change |

**Breaking Change Example:**
```javascript
// OLD (will fail now)
fetch('/notebooks', {
  method: 'POST',
  body: formData  // Only file
})

// NEW (required)
const formData = new FormData();
formData.append('file', file);
formData.append('user_id', userId);  // ← REQUIRED

fetch('/notebooks', {
  method: 'POST',
  body: formData
})
```

---

## ⚙️ Setup & Configuration

### Environment Variables

Create/update `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5433/sentry_ai
VECTOR_DB_URL=postgresql://postgres:password@localhost:5433/sentry_ai

# Service URLs
BACKEND_SERVICE_URL=http://localhost:5000
BURNOUT_SERVICE_URL=http://localhost:8000
NOTEBOOK_SERVICE_URL=http://localhost:8001
EXTRACTION_SERVICE_URL=http://localhost:8003

# JWT Authentication
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth2 (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Database Setup

```bash
# 1. Create database (if not exists)
createdb -U postgres -p 5433 sentry_ai

# 2. Run migrations
psql -U postgres -p 5433 -d sentry_ai -f database_migration.sql
psql -U postgres -p 5433 -d sentry_ai -f backend_developer_changes.sql

# 3. Verify tables
psql -U postgres -p 5433 -d sentry_ai -c "\dt"
# Should show: users, tasks, uploads, user_profiles, etc.
```

### Install Dependencies

```bash
# Backend
cd backend_services
pip install -r requirements.txt
pip install requests  # For service-to-service calls

# AI Services
cd ../AI_services
pip install -r requirements.txt
```

### Start All Services

**Option 1: Manual (Development)**

```bash
# Terminal 1 - Backend
cd backend_services
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload

# Terminal 2 - Burnout Service
cd AI_services/app/services/burn_out_service
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3 - Notebook Service
cd AI_services/app/services/notebook_library
uvicorn FastAPI_app:app --host 0.0.0.0 --port 8001 --reload

# Terminal 4 - Task Extraction
cd AI_services/app/services/task_extraction
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

**Option 2: Docker Compose (Production)**

```bash
docker-compose up -d
```

---

## 🧪 Testing the Integration

### Test 1: Backend → Burnout Integration

```bash
# 1. Create a user and login (get JWT token)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# 2. Create a task (should auto-trigger burnout analysis)
curl -X POST http://localhost:5000/api/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete integration",
    "status": "In Progress",
    "priority": "High",
    "due_date": "2025-12-30T10:00:00"
  }'

# 3. Check backend logs - should see:
# ✅ Burnout analysis triggered for user 1

# 4. Verify burnout analysis was created
curl http://localhost:8000/api/burnout/status/1
```

**Expected:** Burnout score updated automatically after task creation

---

### Test 2: Task Extraction → Backend → Burnout Flow

```bash
# 1. Upload document for task extraction
curl -X POST http://localhost:8003/api/tasks/extract/document \
  -F "file=@test_document.pdf" \
  -F "user_id=1" \
  -F "save_to_db=true"

# 2. Check response - should include upload_id
# Expected response:
{
  "success": true,
  "tasks_extracted": 3,
  "tasks_saved": 3,
  "upload_id": 42,  // ← Confirms upload tracked
  "tasks": [...]
}

# 3. Verify tasks in database
psql -d sentry_ai -c "SELECT * FROM tasks WHERE source = 'extracted';"

# 4. Verify upload tracked
psql -d sentry_ai -c "SELECT * FROM uploads WHERE id = 42;"

# 5. Verify burnout analysis was triggered
curl http://localhost:8000/api/burnout/status/1
```

**Expected:** Tasks created via backend API, upload tracked, burnout analysis updated

---

### Test 3: Burnout Auto-Fetch Mode

```bash
# 1. Create some tasks first
curl -X POST http://localhost:5000/api/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Task 1", "status": "Todo", "priority": "High"}'

# 2. Trigger auto-fetch burnout analysis
curl -X POST http://localhost:8000/api/burnout/analyze-auto/1?store_history=true

# Expected response:
{
  "status": "success",
  "data_source": "database",  // ← Auto-fetched
  "tasks_analyzed": 15,
  "meetings_analyzed": 3,
  "analysis": {
    "final_score": 45,
    "burnout_level": "MODERATE",
    ...
  }
}
```

**Expected:** Complete burnout analysis without providing any task data

---

### Test 4: Notebook Upload Tracking

```bash
# 1. Create notebook with user_id
curl -X POST http://localhost:8001/notebooks \
  -F "file=@lecture_notes.pdf" \
  -F "user_id=1"

# Expected response:
{
  "notebook_id": "abc-123",
  "notebook_name": "lecture_notes.pdf",
  "upload_id": 55,  // ← Upload tracked
  ...
}

# 2. Verify upload in database
psql -d sentry_ai -c "SELECT * FROM uploads WHERE upload_type = 'notebook';"

# Expected: Upload record with processing_status = 'completed'
```

---

### Test 5: Query Upload History

```sql
-- Get all uploads for a user
SELECT
    id,
    filename,
    upload_type,
    processing_status,
    uploaded_at,
    extraction_result->>'tasks_extracted' as tasks_extracted
FROM uploads
WHERE user_id = 1
ORDER BY uploaded_at DESC;

-- Get failed extractions
SELECT * FROM uploads
WHERE processing_status = 'failed'
AND user_id = 1;

-- Get extraction statistics
SELECT
    upload_type,
    COUNT(*) as total_uploads,
    SUM(CASE WHEN processing_status = 'completed' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN processing_status = 'failed' THEN 1 ELSE 0 END) as failed
FROM uploads
WHERE user_id = 1
GROUP BY upload_type;
```

---

## 📊 Architecture Diagrams

### Complete Workflow: User Uploads Audio

```
┌──────────┐
│  USER    │
└────┬─────┘
     │
     │ 1. Upload audio file
     ▼
┌─────────────────────┐
│ Task Extraction     │
│ (Port 8003)         │
└──────┬──────────────┘
       │
       │ 2. Extract tasks from audio
       │    (Vosk → Ollama)
       │
       │ 3. Record upload in uploads table ✨
       │
       │ 4. Call Backend API
       ▼
┌─────────────────────┐
│ Backend Service     │
│ (Port 5000)         │
└──────┬──────────────┘
       │
       │ 5. Validate tasks
       │
       │ 6. Save to tasks table
       │
       │ 7. Call Burnout Service
       ▼
┌─────────────────────┐
│ Burnout Service     │
│ (Port 8000)         │
└──────┬──────────────┘
       │
       │ 8. Auto-fetch tasks from database
       │
       │ 9. Calculate burnout score
       │
       │ 10. Generate recommendations
       │
       │ 11. Store in burnout_analyses table
       ▼
┌─────────────────────┐
│   Database          │
│   ✅ tasks          │
│   ✅ uploads        │
│   ✅ burnout_...    │
└─────────────────────┘
```

### Service Communication Pattern

```
┌──────────────────────────────────────────────────────────┐
│                   Service Mesh                            │
│                                                            │
│  ┌────────────┐                    ┌──────────────┐      │
│  │  Backend   │───────────────────>│   Burnout    │      │
│  │            │  POST /analyze-auto │              │      │
│  └────────────┘                    └──────────────┘      │
│       ▲                                                    │
│       │                                                    │
│       │ POST /service/create                              │
│       │                                                    │
│  ┌────────────┐                                           │
│  │ Task       │                                           │
│  │ Extraction │                                           │
│  └────────────┘                                           │
│                                                            │
└──────────────────────────────────────────────────────────┘
                           │
                           ▼
                   ┌───────────────┐
                   │   Database    │
                   │   (Unified)   │
                   └───────────────┘
```

---

## 📝 Summary Checklist

### What's Integrated ✅

#### Database Layer
- [x] Unified tasks table schema (due_date convention)
- [x] Added users, auth_providers, integrations tables
- [x] Created uploads table for file tracking
- [x] Established all foreign key relationships
- [x] Added backend developer's new features

#### Backend Service
- [x] Updated Task model to match AI schema
- [x] Changed deadline → due_date everywhere
- [x] Added service-to-service communication
- [x] Integrated burnout analysis triggers
- [x] Created /service/create endpoint

#### AI Services
- [x] Burnout: Auto-fetch endpoint (/analyze-auto)
- [x] Task Extraction: Upload tracking + backend integration
- [x] Notebook: Upload tracking + user association
- [x] All services use unified database

#### Service Communication
- [x] Backend → Burnout (auto-trigger on task changes)
- [x] Task Extraction → Backend → Burnout (full workflow)
- [x] Upload tracking across all services

---

## 🚀 Next Steps (Future Enhancements)

### Priority 1: Security
- [ ] Add authentication to AI service endpoints
- [ ] Implement JWT validation middleware
- [ ] Add IP whitelist for /service/create endpoint
- [ ] Implement service-to-service token validation

### Priority 2: Monitoring
- [ ] Add logging to all service calls
- [ ] Implement health check endpoints
- [ ] Set up Prometheus metrics
- [ ] Create Grafana dashboards

### Priority 3: Optimization
- [ ] Implement caching for burnout analysis
- [ ] Add background job queue for async processing
- [ ] Implement file cleanup job for old uploads
- [ ] Add retry logic for service calls

### Priority 4: Documentation
- [ ] Generate OpenAPI specs for all services
- [ ] Create Postman collections
- [ ] Write API usage examples
- [ ] Create developer onboarding guide

---

## 🐛 Troubleshooting

### Issue: Burnout analysis not triggered

**Symptom:** Task created but no burnout analysis happens

**Solutions:**
1. Check burnout service is running on port 8000
2. Verify `BURNOUT_SERVICE_URL` environment variable
3. Check backend logs for connection errors
4. Test burnout endpoint manually:
   ```bash
   curl -X POST http://localhost:8000/api/burnout/analyze-auto/1
   ```

---

### Issue: Task extraction fails to save tasks

**Symptom:** Tasks extracted but not saved to database

**Solutions:**
1. Check backend service is running on port 5000
2. Verify `BACKEND_SERVICE_URL` environment variable
3. Check task extraction logs for API errors
4. Verify /service/create endpoint works:
   ```bash
   curl -X POST "http://localhost:5000/api/tasks/service/create?user_id=1" \
     -H "Content-Type: application/json" \
     -d '{"title": "Test", "status": "Todo", "priority": "Medium"}'
   ```

---

### Issue: Uploads not being tracked

**Symptom:** Files processed but no records in uploads table

**Solutions:**
1. Verify database migration was run successfully
2. Check if uploads table exists:
   ```sql
   SELECT * FROM information_schema.tables WHERE table_name = 'uploads';
   ```
3. Check service logs for database errors
4. Verify database connection string in .env

---

### Issue: Foreign key constraint violations

**Symptom:** Error about user_id not existing in users table

**Solutions:**
1. Create users first before using AI services
2. Check if user exists:
   ```sql
   SELECT * FROM users WHERE id = 1;
   ```
3. If testing, create a test user:
   ```sql
   INSERT INTO users (email, is_verified) VALUES ('test@example.com', TRUE);
   ```

---

## 🤖 Phase 4: AI Companion Service ✨ NEW

### Overview

The AI Companion is a conversational chatbot that serves as a personal assistant for emotional support, task management, and burnout prevention.

**Port:** 8002

### Features

1. **Emotional Support**
   - Process diary entries and emotional check-ins
   - Save to `qualitative_data` table with sentiment analysis
   - Extract emotional themes using Ollama (Llama 3.1 8B)
   - Provide empathetic, supportive responses

2. **Task Management**
   - Query task statistics (total, by status, by priority)
   - Get summaries of upcoming/completed tasks
   - Create tasks from natural language
   - Identify overdue tasks

3. **Burnout Assistance**
   - Check current burnout status and score
   - Get personalized recommendations from RAG
   - Monitor warning signals

4. **Multi-Modal Input**
   - Text chat
   - Audio input (transcribed via Vosk)
   - Diary entry processing

### Architecture

The companion uses **LangGraph** to create an intelligent agent workflow:

```
User Message → [Classify Intent] → Route to Tool → Generate Response
                                    ↓
                    ┌───────────────┴───────────────┐
                    │                               │
            [Save Emotional]              [Get Task Stats]
                    │                               │
            [Get Burnout Status]          [Create Task]
                    │                               │
                    └───────────────┬───────────────┘
                                    ↓
                            [Respond with Ollama]
```

### Intent Classification

The agent automatically classifies messages:

- **emotional_support** - Sharing feelings, diary entries
- **task_query** - Asking about tasks
- **burnout_query** - Asking about burnout status
- **task_creation** - Creating new tasks
- **general_chat** - Everyday conversation

### Key Endpoints

#### POST /chat
```json
{
  "message": "I'm feeling overwhelmed with work",
  "user_id": 1
}
```

Response includes:
- Natural language response
- Sentiment analysis (if emotional)
- Action taken (intent classification)

#### POST /chat/audio
Upload audio file, get transcribed and processed response.

#### POST /diary
```json
{
  "content": "Today was tough...",
  "user_id": 1
}
```

Saves to `qualitative_data` and provides supportive feedback.

### Integration

The companion integrates with all other services:

- **Backend (5000)**: Task queries and creation
- **Burnout (8000)**: Status checks and recommendations
- **Extraction (8003)**: Natural language task parsing
- **Database**: Saves emotional data to `qualitative_data`

### Files

- `AI_services/app/services/ai_companion/main.py` - FastAPI app
- `AI_services/app/services/ai_companion/companion_agent.py` - LangGraph agent
- `AI_services/app/services/ai_companion/companion_tools.py` - Service integration tools
- `AI_services/app/services/ai_companion/README.md` - Detailed documentation

### Example Conversation

**User:** "I'm feeling really stressed about my workload"

**Companion:** "I hear you, and it's completely valid to feel stressed when you have a lot on your plate. You currently have 15 tasks with 3 overdue. Would you like me to show you your task breakdown or suggest some stress management strategies?"

*(Saves to qualitative_data with sentiment: "negative", themes: ["work_stress"])*

---

## 📚 Additional Resources

- **Database Schema:** See `database_migration.sql`
- **API Documentation:** Visit `/docs` endpoint on each service
- **Integration Guide:** See `BACKEND_AI_INTEGRATION_GUIDE.md`
- **Code Changes:** See `BACKEND_CODE_CHANGES.md`

---

## 👥 Contributors

- Backend Developer: Authentication, Task Management, Integrations
- AI Team: Burnout Analysis, Task Extraction, Notebook Library
- Integration Lead: Database unification, Service-to-service communication

---

## 📅 Version History

### v2.1 (2025-12-30) - AI Companion Added ✨ NEW
- ✅ AI Companion chatbot service (Port 8002)
- ✅ Emotional support and diary processing
- ✅ LangGraph-based intelligent agent
- ✅ Multi-modal input (text + audio)
- ✅ Integration with all existing services

### v2.0 (2025-12-29) - Complete Integration
- ✅ Unified database schema
- ✅ Service-to-service communication
- ✅ Upload tracking across all services
- ✅ Auto-fetch burnout analysis

### v1.0 (2025-12-XX) - Initial Separate Services
- Backend services (Auth, Tasks, Users)
- AI services (Burnout, Extraction, Notebook)
- Separate databases

---

**🎉 Integration Complete!** All services now work together seamlessly with a unified database and automatic workflow coordination.

For questions or issues, please refer to the troubleshooting section or check service logs.
