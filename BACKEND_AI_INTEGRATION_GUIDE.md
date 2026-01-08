# Sentry AI - Backend & AI Services Integration Guide

**Version:** 1.0
**Date:** 2025-12-28
**Status:** Integration Planning Complete

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [Database Integration Strategy](#database-integration-strategy)
4. [API Endpoint Analysis](#api-endpoint-analysis)
5. [Critical Integration Issues](#critical-integration-issues)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Technical Specifications](#technical-specifications)

---

## 1. Executive Summary

### Purpose
This document provides a comprehensive integration plan for merging the backend developer's authentication and task management system with the existing AI services (Burnout Analysis, Notebook Library, and Task Extraction).

### Current State
- **4 Independent Services**: Backend (port 5000), Burnout (8000), Notebook (8001), Task Extraction (8003)
- **2 Database Systems**: Main PostgreSQL DB + Vector DB with pgvector
- **NO Integration**: Services operate in complete isolation
- **NO Authentication on AI Services**: Critical security vulnerability

### Integration Goals
1. Unified authentication across all services using JWT + OAuth2
2. Database schema consolidation with proper foreign key relationships
3. Service-to-service communication for coordinated workflows
4. Persistent file upload system with audit trail
5. Centralized user management

---

## 2. System Architecture Overview

### 2.1 Service Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                        Sentry AI Platform                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │  Backend Service │  │ Burnout Service  │  │   Notebook    │ │
│  │    Port 5000     │  │    Port 8000     │  │  Port 8001    │ │
│  │  ─────────────   │  │  ─────────────   │  │  ──────────   │ │
│  │  • Auth (JWT)    │  │  • Analysis      │  │  • RAG Chat   │ │
│  │  • OAuth2        │  │  • Workload      │  │  • Embeddings │ │
│  │  • Users         │  │  • Recommends    │  │  • Documents  │ │
│  │  • Tasks CRUD    │  │  • Profile Mgmt  │  │               │ │
│  │  • Integrations  │  │                  │  │               │ │
│  └──────────────────┘  └──────────────────┘  └───────────────┘ │
│                                                                   │
│  ┌──────────────────┐                                           │
│  │   Extraction     │                                           │
│  │   Port 8003      │                                           │
│  │  ─────────────   │                                           │
│  │  • Audio         │                                           │
│  │  • Document      │                                           │
│  │  • Image/Video   │                                           │
│  │  • Handwritten   │                                           │
│  └──────────────────┘                                           │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                       Database Layer                             │
│  ┌────────────────────────┐  ┌─────────────────────────────┐   │
│  │  Main PostgreSQL DB    │  │  Vector DB (pgvector)       │   │
│  │  ───────────────────   │  │  ────────────────────────   │   │
│  │  • users               │  │  • langchain_pg_collection  │   │
│  │  • auth_providers      │  │  • langchain_pg_embedding   │   │
│  │  • integrations        │  │                             │   │
│  │  • tasks (merged)      │  │                             │   │
│  │  • uploads (new)       │  │                             │   │
│  │  • user_profiles       │  │                             │   │
│  │  • burnout_analyses    │  │                             │   │
│  │  • user_preferences    │  │                             │   │
│  │  • user_constraints    │  │                             │   │
│  │  • user_behavioral...  │  │                             │   │
│  │  • qualitative_data    │  │                             │   │
│  └────────────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | All 4 services |
| **Database** | PostgreSQL 14+ | Main data storage |
| **Vector DB** | pgvector extension | Embeddings for RAG |
| **ORM** | SQLAlchemy | Database access |
| **Authentication** | JWT + OAuth2 | User auth |
| **LLM** | Ollama (Llama 3.1 8B) | Text generation |
| **Vision Model** | LLaVa | Image analysis |
| **Speech Recognition** | Vosk | Offline audio transcription |
| **OCR** | Tesseract | Handwriting recognition |
| **Document Parser** | Unstructured | PDF/DOCX parsing |
| **RAG Framework** | LangChain + LangGraph | Agent workflows |
| **Embeddings** | HuggingFace sentence-transformers | Vector search |

---

## 3. Database Integration Strategy

### 3.1 Current Database State

**Main Database Tables (7 existing + 3 new = 10 total):**

**Existing AI Tables:**
1. `user_profiles` - Core user profile data for burnout analysis
2. `burnout_analyses` - Historical burnout analysis results
3. `user_preferences` - User work preferences and settings
4. `user_constraints` - Time/capacity constraints
5. `user_behavioral_profiles` - Learned behavioral patterns
6. `qualitative_data` - Free-text user feedback
7. `tasks` - AI-extracted and analyzed tasks

**New Backend Tables:**
8. `users` - Primary authentication and user data
9. `auth_providers` - OAuth provider linkage (Google/Apple/Facebook)
10. `integrations` - Third-party service tokens (Gmail, Calendar, Zoom)

**Proposed Additional Table:**
11. `uploads` - Persistent file upload tracking

**Vector Database Tables (2 existing):**
1. `langchain_pg_collection` - Document collections metadata
2. `langchain_pg_embedding` - Vector embeddings storage

### 3.2 Schema Relationships

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

### 3.3 Tasks Table Conflict Resolution

**Problem:** Two different `tasks` table schemas exist:

**Backend Schema (backend_services/app/models.py:49-70):**
```python
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    source = Column(String)  # "sentry" or "google"
    title = Column(String, nullable=False)
    description = Column(String, server_default="")
    status = Column(String, nullable=False)
    deadline = Column(TIMESTAMP(timezone=True), nullable=False)
    priority = Column(String, nullable=False)
    category = Column(String, nullable=False)
    google_task_id = Column(String, unique=True)
    google_tasklist_id = Column(String)
    added_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
```

**AI Schema (AI_services/.../integrations/task_database_integration.py:10-28):**
```python
class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False)
    task_type = Column(String(20), default='task')  # 'task' or 'meeting'
    status = Column(String(50))
    priority = Column(String(20))
    due_date = Column(DateTime, nullable=True)
    assigned_to = Column(String(100))
    can_delegate = Column(Boolean, default=True)
    estimated_hours = Column(Float, nullable=True)
    start_time = Column(DateTime, nullable=True)  # For meetings
    end_time = Column(DateTime, nullable=True)
    attendees = Column(Text, nullable=True)
    is_recurring = Column(Boolean, default=False)
    is_optional = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Recommended Solution: MERGE SCHEMAS**

Create a unified `tasks` table with all columns from both schemas:

```sql
CREATE TABLE tasks (
    -- Core fields (from both)
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',

    -- Status & Classification
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    category VARCHAR(100) NOT NULL,
    task_type VARCHAR(20) DEFAULT 'task',  -- 'task' or 'meeting'

    -- Timing
    deadline TIMESTAMP WITH TIME ZONE,  -- Also serves as due_date
    start_time TIMESTAMP WITH TIME ZONE,  -- For meetings
    end_time TIMESTAMP WITH TIME ZONE,    -- For meetings

    -- Source tracking (Backend)
    source VARCHAR(50) NOT NULL,  -- 'sentry', 'google', 'extracted_audio', etc.
    google_task_id VARCHAR(255) UNIQUE,
    google_tasklist_id VARCHAR(255),

    -- AI Analysis fields
    assigned_to VARCHAR(100),
    can_delegate BOOLEAN DEFAULT TRUE,
    estimated_hours FLOAT,
    is_recurring BOOLEAN DEFAULT FALSE,
    is_optional BOOLEAN DEFAULT FALSE,

    -- Meeting-specific (AI)
    attendees TEXT,

    -- Timestamps
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_source ON tasks(source);
```

### 3.4 Uploads Table Schema (NEW)

Currently, the backend uses an in-memory session system ([backend_services/app/routers/uploads/session_system.py:8-20](backend_services/app/routers/uploads/session_system.py#L8-L20)). This needs database persistence:

```sql
CREATE TABLE uploads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- File metadata
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,  -- Full path on disk
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100),

    -- Processing metadata
    upload_type VARCHAR(50) NOT NULL,  -- 'audio', 'document', 'image', 'video', 'handwritten'
    processing_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed'
    extraction_result JSONB,  -- Store extracted tasks or processing results

    -- Session tracking
    session_id VARCHAR(100),

    -- Timestamps
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,  -- For temporary files

    -- Audit
    deleted_at TIMESTAMP WITH TIME ZONE  -- Soft delete
);

-- Indexes
CREATE INDEX idx_uploads_user_id ON uploads(user_id);
CREATE INDEX idx_uploads_session_id ON uploads(session_id);
CREATE INDEX idx_uploads_status ON uploads(processing_status);
```

### 3.5 Database Migration Steps

1. **Add backend tables** (`users`, `auth_providers`, `integrations`)
2. **Create `uploads` table**
3. **Backup existing `tasks` table** to `tasks_backup`
4. **Drop old `tasks` table**
5. **Create merged `tasks` table** with unified schema
6. **Migrate data** from `tasks_backup` (if any production data exists)
7. **Add foreign key constraints** linking AI tables to `users.id`
8. **Update all SQLAlchemy models** to match new schemas

---

## 4. API Endpoint Analysis

### 4.1 Backend Service (Port 5000)

**Base URL:** `http://localhost:5000/api`

#### Authentication Endpoints
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/auth/login` | Email/password login | No |
| POST | `/auth/logout` | Invalidate tokens | Yes (JWT) |
| POST | `/auth/refresh-token` | Get new access token | Yes (Refresh) |
| POST | `/auth/forgot-password` | Request password reset | No |
| POST | `/auth/reset-password` | Complete password reset | No |
| POST | `/auth/verify-email` | Verify email with code | No |
| GET | `/auth/google` | Google OAuth login | No |
| GET | `/auth/google/callback` | Google OAuth callback | No |
| GET | `/auth/apple` | Apple OAuth login | No |
| POST | `/auth/apple/callback` | Apple OAuth callback | No |
| GET | `/auth/facebook` | Facebook OAuth login | No |
| GET | `/auth/facebook/callback` | Facebook OAuth callback | No |

#### User Management
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/users/` | Create new user | No |
| GET | `/users/{user_id}` | Get user details | Yes |
| PUT | `/users/{user_id}` | Update user profile | Yes |
| DELETE | `/users/{user_id}` | Delete user account | Yes |

#### Task Management (CRUD)
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/tasks/{user_id}` | Get all user tasks | Yes |
| POST | `/tasks/{user_id}` | Create new task | Yes |
| PUT | `/tasks/{user_id}/{task_id}` | Update task | Yes |
| DELETE | `/tasks/{user_id}/{task_id}` | Delete task | Yes |

#### Integrations
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/integrations/google/tasks/{user_id}/sync` | Sync Google Tasks | Yes |
| GET | `/zoom/meetings/{user_id}` | Get Zoom meetings | Yes |

#### File Uploads (Session-based)
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/uploads/create-session` | Create upload session | Yes |
| POST | `/uploads/session/{session_id}/upload` | Upload file | Yes |
| GET | `/uploads/session/{session_id}/files` | List session files | Yes |
| DELETE | `/uploads/session/{session_id}` | Delete session | Yes |

**Total Backend Endpoints:** ~30

### 4.2 Burnout Analysis Service (Port 8000)

**Base URL:** `http://localhost:8000/api`

**⚠️ CRITICAL: NO AUTHENTICATION ON ANY ENDPOINT**

#### Analysis Endpoints
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/burnout/analyze` | Perform burnout analysis | ❌ NO |
| GET | `/burnout/status/{user_id}` | Get burnout status | ❌ NO |
| GET | `/burnout/history/{user_id}` | Get analysis history | ❌ NO |
| POST | `/burnout/feedback` | Submit user feedback | ❌ NO |

#### Workload Management
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/workload/calculate` | Calculate workload metrics | ❌ NO |
| GET | `/workload/metrics/{user_id}` | Get workload metrics | ❌ NO |

#### Recommendations
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/recommendations/generate` | Generate recommendations | ❌ NO |
| GET | `/recommendations/{user_id}` | Get recommendations | ❌ NO |
| POST | `/recommendations/feedback` | Rate recommendation | ❌ NO |

#### User Profile Management
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/profile/create` | Create user profile | ❌ NO |
| GET | `/profile/{user_id}` | Get user profile | ❌ NO |
| PUT | `/profile/{user_id}` | Update profile | ❌ NO |
| POST | `/profile/{user_id}/preferences` | Set preferences | ❌ NO |
| POST | `/profile/{user_id}/constraints` | Set constraints | ❌ NO |

#### Health Check
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/health` | Service health | No |

**Total Burnout Service Endpoints:** ~20

### 4.3 Notebook Library Service (Port 8001)

**Base URL:** `http://localhost:8001/api`

**⚠️ CRITICAL: NO AUTHENTICATION ON ANY ENDPOINT**

#### Notebook Management
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/notebooks/create` | Create notebook | ❌ NO |
| GET | `/notebooks/{notebook_id}` | Get notebook | ❌ NO |
| DELETE | `/notebooks/{notebook_id}` | Delete notebook | ❌ NO |

#### Document Upload
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/notebooks/{notebook_id}/upload` | Upload document | ❌ NO |
| GET | `/notebooks/{notebook_id}/documents` | List documents | ❌ NO |

#### RAG Chat
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/notebooks/{notebook_id}/chat` | Query notebook | ❌ NO |

#### Health Check
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/health` | Service health | No |

**Total Notebook Service Endpoints:** ~7

### 4.4 Task Extraction Service (Port 8003)

**Base URL:** `http://localhost:8003/api`

**⚠️ CRITICAL: NO AUTHENTICATION ON ANY ENDPOINT**

#### Extraction Endpoints
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| POST | `/extract/audio` | Extract from audio | ❌ NO |
| POST | `/extract/document` | Extract from PDF/DOCX | ❌ NO |
| POST | `/extract/image` | Extract from image | ❌ NO |
| POST | `/extract/handwritten` | Extract from handwriting | ❌ NO |
| POST | `/extract/text` | Extract from raw text | ❌ NO |
| POST | `/extract/batch` | Batch extraction | ❌ NO |

#### Task History
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/tasks/history/{user_id}` | Get extraction history | ❌ NO |

#### Health Check
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/health` | Service health | No |

**Total Extraction Service Endpoints:** ~8

---

## 5. Critical Integration Issues

### 5.1 Priority 1: Security Vulnerabilities

#### Issue 1A: No Authentication on AI Services
**Severity:** CRITICAL
**Impact:** Any user can access any data without authentication

**Current State:**
- Burnout Service (port 8000): All 20 endpoints publicly accessible
- Notebook Service (port 8001): All 7 endpoints publicly accessible
- Task Extraction (port 8003): All 8 endpoints publicly accessible

**Example Vulnerability:**
```bash
# Anyone can access any user's burnout analysis
curl http://localhost:8000/api/burnout/status/123

# Anyone can query any user's notebooks
curl -X POST http://localhost:8000/api/notebooks/456/chat \
  -d '{"query": "Show me sensitive information"}'

# Anyone can see extracted tasks
curl http://localhost:8003/api/tasks/history/789
```

**Required Fix:**
Add JWT authentication middleware to all AI services:

```python
# Example for burnout service
from fastapi import Depends, HTTPException, Header
from jose import JWTError, jwt

async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Apply to all routes
@app.post("/api/burnout/analyze")
async def analyze_burnout(
    data: BurnoutAnalysisRequest,
    user_id: int = Depends(verify_token)
):
    # Verify request user_id matches token user_id
    if data.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    # ... rest of logic
```

#### Issue 1B: No User Validation
**Severity:** HIGH
**Impact:** Services accept non-existent user IDs

**Current State:**
AI services accept any `user_id` without checking if user exists in database.

**Example Problem:**
```python
# AI service accepts this even if user 99999 doesn't exist
response = requests.post(
    "http://localhost:8003/api/extract/audio",
    files={"file": audio_file},
    data={"user_id": 99999}
)
```

**Required Fix:**
Add user validation to all AI service endpoints:

```python
from sqlalchemy.orm import Session
from app.database import get_db

async def validate_user_exists(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user

# Use in endpoints
@app.post("/api/extract/audio")
async def extract_audio(
    user_id: int = Form(...),
    user: User = Depends(validate_user_exists),
    db: Session = Depends(get_db)
):
    # ... extraction logic
```

### 5.2 Priority 2: Integration Gaps

#### Issue 2A: No Service-to-Service Communication
**Severity:** HIGH
**Impact:** Services operate in silos, missing critical workflows

**Current Gaps:**

1. **Google Tasks Sync → Burnout Analysis**
   - Backend syncs Google Tasks ([backend_services/app/routers/integrations/google_tasks.py:85-120](backend_services/app/routers/integrations/google_tasks.py#L85-L120))
   - Tasks added to database
   - ❌ Burnout service never notified of new tasks
   - ❌ No workload recalculation triggered

2. **Task Extraction → Task CRUD**
   - Extraction service saves tasks directly to database ([AI_services/.../task_extraction_api.py:45-60](AI_services/app/services/task_extraction/task_extraction_api.py#L45-L60))
   - ❌ Backend's task validation skipped
   - ❌ Task creation webhooks not triggered
   - ❌ Google Tasks sync not updated

3. **Task CRUD → Burnout Analysis**
   - Backend creates/updates/deletes tasks ([backend_services/app/routers/task.py:30-80](backend_services/app/routers/task.py#L30-L80))
   - ❌ Burnout service not notified
   - ❌ Analysis becomes stale

4. **Notebook Upload → Uploads Table**
   - Notebook service accepts file uploads ([AI_services/.../FastAPI_app.py:120-150](AI_services/app/services/notebook_library/FastAPI_app.py#L120-L150))
   - ❌ Not recorded in uploads table
   - ❌ No audit trail

**Required Fix:**
Implement service-to-service HTTP calls:

```python
# Example: Backend notifies Burnout service after task changes
import httpd

BURNOUT_SERVICE_URL = "http://localhost:8000"

async def notify_burnout_service(user_id: int, event: str):
    """Notify burnout service of task changes"""
    try:
        response = requests.post(
            f"{BURNOUT_SERVICE_URL}/api/webhooks/task-update",
            json={
                "user_id": user_id,
                "event": event,  # 'created', 'updated', 'deleted', 'completed'
                "timestamp": datetime.utcnow().isoformat()
            },
            timeout=5
        )
        response.raise_for_status()
    except Exception as e:
        # Log error but don't fail the main request
        logger.error(f"Failed to notify burnout service: {e}")

# Use in task endpoints
@router.post("/api/tasks/{user_id}")
async def create_task(user_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    new_task = create_task_in_db(user_id, task, db)

    # Notify burnout service
    await notify_burnout_service(user_id, "created")

    return new_task
```

#### Issue 2B: Path Conflicts
**Severity:** MEDIUM
**Impact:** Routing confusion if services ever unified

**Conflicts:**
- Backend: `GET /api/tasks/{user_id}` - Get all tasks (CRUD)
- Extraction: `GET /api/tasks/history/{user_id}` - Get extraction history

**Note:** Currently not an issue since services on different ports, but will matter if:
- Deploying behind API Gateway
- Consolidating services
- Creating unified OpenAPI spec

**Recommended Fix:**
Namespace AI service endpoints:

```python
# Extraction service - add namespace
@router.get("/api/extraction/history/{user_id}")  # Changed from /api/tasks/history

# Burnout service - add namespace
@router.post("/api/burnout/analyze")  # Already namespaced ✓

# Notebook service - add namespace
@router.post("/api/notebooks/{id}/chat")  # Already namespaced ✓
```

### 5.3 Priority 3: Data Consistency Issues

#### Issue 3A: Tasks Table Schema Mismatch
**Status:** Documented in Section 3.3
**Resolution:** Merge schemas (SQL provided)

#### Issue 3B: No Upload Persistence
**Status:** Documented in Section 3.4
**Resolution:** Create uploads table (SQL provided)

#### Issue 3C: Duplicate User Profiles
**Severity:** MEDIUM
**Impact:** Backend's `users` table and AI's `user_profiles` table overlap

**Current State:**
- Backend `users` table: Email, password, name, birthday
- AI `user_profiles` table: Role, department, timezone, working hours

**Recommendation:**
Keep separate tables but link them:
- `users` = authentication data (backend owns)
- `user_profiles` = burnout analysis data (AI owns)
- Link: `user_profiles.user_id` → `users.id` (foreign key)

**Migration:**
```sql
-- Add foreign key if not exists
ALTER TABLE user_profiles
ADD CONSTRAINT fk_user_profiles_user_id
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Ensure user_id uniqueness (one profile per user)
ALTER TABLE user_profiles
ADD CONSTRAINT unique_user_profile
UNIQUE (user_id);
```

---

## 6. Implementation Roadmap

### Phase 1: Database Consolidation (Week 1)

**Tasks:**
1. ✅ Design merged tasks table schema
2. ✅ Design uploads table schema
3. Create Alembic migration scripts
4. Add backend tables (users, auth_providers, integrations)
5. Create uploads table
6. Backup existing tasks table
7. Create merged tasks table
8. Migrate existing task data
9. Add foreign key constraints to AI tables
10. Update all SQLAlchemy models

**Files to Modify:**
- Create: `alembic/versions/001_add_backend_tables.py`
- Create: `alembic/versions/002_create_uploads_table.py`
- Create: `alembic/versions/003_merge_tasks_table.py`
- Update: All `models.py` files in all 4 services

**Acceptance Criteria:**
- All tables visible in database
- Foreign key constraints enforced
- All services can connect to database
- No data loss from existing tables

### Phase 2: Authentication Integration (Week 1-2)

**Tasks:**
1. Create shared authentication library
2. Add JWT verification middleware to Burnout service
3. Add JWT verification middleware to Notebook service
4. Add JWT verification middleware to Extraction service
5. Update all AI endpoints to require authentication
6. Add user validation to all AI endpoints
7. Update API documentation (OpenAPI specs)
8. Test authentication flow end-to-end

**Files to Create:**
- `shared/auth_middleware.py` - Shared JWT verification
- `shared/user_validation.py` - Shared user existence check

**Files to Modify:**
- `AI_services/app/services/burn_out_service/api/main.py`
- `AI_services/app/services/notebook_library/FastAPI_app.py`
- `AI_services/app/services/task_extraction/main.py`

**Acceptance Criteria:**
- All AI endpoints return 401 without valid JWT
- All AI endpoints return 404 for non-existent users
- Frontend can authenticate and access all services
- Postman collection updated with auth examples

### Phase 3: Service Integration (Week 2-3)

**Tasks:**
1. Create service configuration file (URLs, timeouts)
2. Implement Backend → Burnout notification on task changes
3. Implement Extraction → Backend task creation flow
4. Implement Google Tasks Sync → Burnout trigger
5. Implement Notebook upload → uploads table recording
6. Add retry logic and error handling
7. Add integration health checks
8. Create integration monitoring dashboard

**Files to Create:**
- `shared/config.py` - Service URLs and settings
- `shared/service_client.py` - HTTP client with retry logic
- `backend_services/app/integrations/burnout_client.py`
- `AI_services/app/services/task_extraction/backend_client.py`

**Files to Modify:**
- `backend_services/app/routers/task.py` - Add burnout notifications
- `backend_services/app/routers/integrations/google_tasks.py` - Add burnout trigger
- `AI_services/app/services/task_extraction/task_extraction_api.py` - Call backend API
- `AI_services/app/services/notebook_library/FastAPI_app.py` - Record uploads

**Acceptance Criteria:**
- Task creation triggers burnout recalculation
- Task extraction creates tasks via backend API
- Google Tasks sync triggers analysis
- All uploads recorded in database
- Integration failures logged but don't break main flow

### Phase 4: Upload System Refactor (Week 3)

**Tasks:**
1. Replace session system with database-backed uploads
2. Update upload endpoints to use uploads table
3. Implement file cleanup job (delete expired files)
4. Add upload quota per user
5. Add file type validation
6. Implement virus scanning (optional)

**Files to Modify:**
- `backend_services/app/routers/uploads/session_system.py` - Refactor to use DB
- Create: `backend_services/app/routers/uploads/cleanup_job.py`

**Acceptance Criteria:**
- Uploads persist across server restarts
- Old files automatically cleaned up
- Users can view upload history
- File quotas enforced

### Phase 5: Testing & Documentation (Week 4)

**Tasks:**
1. Write integration tests for all services
2. Load testing on full workflow
3. Security audit (OWASP Top 10)
4. Update all API documentation
5. Create deployment guide
6. Create developer onboarding guide

**Files to Create:**
- `tests/integration/test_full_workflow.py`
- `docs/API_DOCUMENTATION.md`
- `docs/DEPLOYMENT_GUIDE.md`
- `docs/DEVELOPER_GUIDE.md`

**Acceptance Criteria:**
- 80%+ test coverage on integration points
- All security vulnerabilities resolved
- Documentation complete and reviewed
- New developers can set up environment in < 1 hour

### Phase 6: Deployment (Week 4)

**Tasks:**
1. Create Docker Compose for all services
2. Set up environment variables
3. Configure reverse proxy (Nginx)
4. Set up monitoring (Prometheus + Grafana)
5. Deploy to staging environment
6. User acceptance testing
7. Deploy to production

**Files to Create:**
- `docker-compose.yml` - All services orchestration
- `nginx.conf` - Reverse proxy configuration
- `prometheus.yml` - Metrics configuration
- `.env.example` - Environment variables template

**Acceptance Criteria:**
- All services running in Docker
- Single command startup
- Monitoring dashboards operational
- Zero downtime deployment process

---

## 7. Technical Specifications

### 7.1 Authentication Flow

```
┌────────┐                                   ┌─────────────────┐
│ Client │                                   │ Backend Service │
└───┬────┘                                   └────────┬────────┘
    │                                                  │
    │ 1. POST /api/auth/login                        │
    │   {email, password}                            │
    ├────────────────────────────────────────────────>│
    │                                                  │
    │                                        2. Verify credentials
    │                                           Check password hash
    │                                                  │
    │ 3. Return tokens                               │
    │   {access_token, refresh_token}                │
    │<────────────────────────────────────────────────┤
    │                                                  │
    │ 4. Store tokens in client                      │
    │                                                  │
    │                                                  │
┌───┴────┐                                   ┌────────┴────────┐
│ Client │                                   │   AI Service    │
└───┬────┘                                   └────────┬────────┘
    │                                                  │
    │ 5. POST /api/burnout/analyze                    │
    │    Authorization: Bearer <access_token>         │
    │    {user_id, task_data}                         │
    ├────────────────────────────────────────────────>│
    │                                                  │
    │                                        6. Verify JWT token
    │                                           Extract user_id
    │                                           Check user exists
    │                                                  │
    │ 7. Return analysis                             │
    │    {burnout_score, recommendations}            │
    │<────────────────────────────────────────────────┤
    │                                                  │
```

### 7.2 Service Integration Flow Example

**Scenario:** User uploads audio file for task extraction

```
┌────────┐     ┌─────────────┐     ┌────────────┐     ┌─────────────┐
│ Client │     │   Backend   │     │ Extraction │     │   Burnout   │
└───┬────┘     └──────┬──────┘     └─────┬──────┘     └──────┬──────┘
    │                 │                   │                   │
    │ 1. POST /api/extract/audio          │                   │
    │    (audio file, user_id, JWT)       │                   │
    ├─────────────────┼───────────────────>│                   │
    │                 │                   │                   │
    │                 │          2. Verify JWT & user exists  │
    │                 │<──────────────────┤                   │
    │                 │                   │                   │
    │                 │          3. Process audio             │
    │                 │             (Vosk → Ollama)           │
    │                 │                   │                   │
    │                 │          4. POST /api/tasks/{user_id} │
    │                 │<──────────────────┤                   │
    │                 │             (extracted tasks)         │
    │                 │                   │                   │
    │                 │ 5. Save to DB    │                   │
    │                 │    Record in uploads table           │
    │                 │                   │                   │
    │                 │ 6. POST /api/webhooks/task-update    │
    │                 ├──────────────────────────────────────>│
    │                 │    (user_id, event: "created")       │
    │                 │                   │                   │
    │                 │                   │         7. Trigger analysis
    │                 │                   │            Recalculate workload
    │                 │                   │                   │
    │ 8. Return results                  │                   │
    │<────────────────┼───────────────────┤                   │
    │ {tasks, upload_id}                 │                   │
    │                 │                   │                   │
```

### 7.3 Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sentry_ai
VECTOR_DB_URL=postgresql://user:password@localhost:5432/vector_db

# JWT Authentication
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth2
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/google/callback

FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
FACEBOOK_REDIRECT_URI=http://localhost:5000/api/auth/facebook/callback

APPLE_CLIENT_ID=your-apple-client-id
APPLE_KEY_ID=your-apple-key-id
APPLE_TEAM_ID=your-apple-team-id
APPLE_REDIRECT_URI=http://localhost:5000/api/auth/apple/callback

# Service URLs
BACKEND_SERVICE_URL=http://localhost:5000
BURNOUT_SERVICE_URL=http://localhost:8000
NOTEBOOK_SERVICE_URL=http://localhost:8001
EXTRACTION_SERVICE_URL=http://localhost:8003

# File Upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=100
ALLOWED_FILE_TYPES=.pdf,.docx,.txt,.mp3,.wav,.mp4,.jpg,.png

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_VISION_MODEL=llava

# Email (for verification)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Redis (optional - for caching/sessions)
REDIS_URL=redis://localhost:6379/0
```

### 7.4 Startup Script

Create `start_all_services.sh`:

```bash
#!/bin/bash

# Sentry AI - Start All Services
# This script starts all 4 microservices in the correct order

set -e

echo "🚀 Starting Sentry AI Platform..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check database connection
echo "📊 Checking database connection..."
psql $DATABASE_URL -c "SELECT 1;" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Error: Cannot connect to database"
    exit 1
fi

echo "✅ Database connection OK"

# Run migrations
echo "🔄 Running database migrations..."
cd backend_services
alembic upgrade head
cd ..

# Start services
echo "🌐 Starting Backend Service (Port 5000)..."
cd backend_services
uvicorn app.main:app --host 0.0.0.0 --port 5000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"
cd ..

sleep 2

echo "🧠 Starting Burnout Service (Port 8000)..."
cd AI_services/app/services/burn_out_service
uvicorn api.main:app --host 0.0.0.0 --port 8000 > ../../../../logs/burnout.log 2>&1 &
BURNOUT_PID=$!
echo "Burnout PID: $BURNOUT_PID"
cd ../../../..

sleep 2

echo "📚 Starting Notebook Service (Port 8001)..."
cd AI_services/app/services/notebook_library
uvicorn FastAPI_app:app --host 0.0.0.0 --port 8001 > ../../../../logs/notebook.log 2>&1 &
NOTEBOOK_PID=$!
echo "Notebook PID: $NOTEBOOK_PID"
cd ../../../..

sleep 2

echo "📝 Starting Task Extraction Service (Port 8003)..."
cd AI_services/app/services/task_extraction
uvicorn main:app --host 0.0.0.0 --port 8003 > ../../../../logs/extraction.log 2>&1 &
EXTRACTION_PID=$!
echo "Extraction PID: $EXTRACTION_PID"
cd ../../../..

sleep 3

# Health checks
echo "🏥 Running health checks..."

check_health() {
    local service=$1
    local port=$2
    local url="http://localhost:$port/health"

    if curl -s -f "$url" > /dev/null; then
        echo "✅ $service is healthy"
        return 0
    else
        echo "❌ $service failed health check"
        return 1
    fi
}

check_health "Backend" 5000
check_health "Burnout" 8000
check_health "Notebook" 8001
check_health "Extraction" 8003

echo ""
echo "✅ All services started successfully!"
echo ""
echo "📡 Service URLs:"
echo "   Backend:    http://localhost:5000/docs"
echo "   Burnout:    http://localhost:8000/docs"
echo "   Notebook:   http://localhost:8001/docs"
echo "   Extraction: http://localhost:8003/docs"
echo ""
echo "📊 Logs:"
echo "   tail -f logs/backend.log"
echo "   tail -f logs/burnout.log"
echo "   tail -f logs/notebook.log"
echo "   tail -f logs/extraction.log"
echo ""
echo "🛑 To stop all services:"
echo "   kill $BACKEND_PID $BURNOUT_PID $NOTEBOOK_PID $EXTRACTION_PID"
```

Make executable:
```bash
chmod +x start_all_services.sh
```

### 7.5 Docker Compose (Alternative)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: sentry
      POSTGRES_PASSWORD: sentry123
      POSTGRES_DB: sentry_ai
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    command: postgres -c shared_preload_libraries=vector

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend_services
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://sentry:sentry123@postgres:5432/sentry_ai
    ports:
      - "5000:5000"
    depends_on:
      - postgres
      - redis
    volumes:
      - ./uploads:/app/uploads
    command: uvicorn app.main:app --host 0.0.0.0 --port 5000

  burnout:
    build:
      context: ./AI_services/app/services/burn_out_service
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://sentry:sentry123@postgres:5432/sentry_ai
      BACKEND_SERVICE_URL: http://backend:5000
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    command: uvicorn api.main:app --host 0.0.0.0 --port 8000

  notebook:
    build:
      context: ./AI_services/app/services/notebook_library
      dockerfile: Dockerfile
    environment:
      VECTOR_DB_URL: postgresql://sentry:sentry123@postgres:5432/sentry_ai
      BACKEND_SERVICE_URL: http://backend:5000
    ports:
      - "8001:8001"
    depends_on:
      - postgres
    volumes:
      - ./uploads:/app/uploads
    command: uvicorn FastAPI_app:app --host 0.0.0.0 --port 8001

  extraction:
    build:
      context: ./AI_services/app/services/task_extraction
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://sentry:sentry123@postgres:5432/sentry_ai
      BACKEND_SERVICE_URL: http://backend:5000
    ports:
      - "8003:8003"
    depends_on:
      - postgres
    volumes:
      - ./uploads:/app/uploads
    command: uvicorn main:app --host 0.0.0.0 --port 8003

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

---

## 8. API Gateway (Optional Future Enhancement)

For production deployment, consider adding an API Gateway (Nginx or Kong) as single entry point:

```
                          ┌─────────────────┐
Client ─────────────────> │   API Gateway   │
                          │  (Port 80/443)  │
                          └────────┬────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
             ┌──────▼─────┐ ┌─────▼──────┐ ┌────▼──────┐
             │  Backend   │ │  Burnout   │ │  Notebook │
             │  Port 5000 │ │  Port 8000 │ │ Port 8001 │
             └────────────┘ └────────────┘ └───────────┘
                                   │
                            ┌──────▼─────────┐
                            │  Extraction    │
                            │  Port 8003     │
                            └────────────────┘
```

**Benefits:**
- Single TLS/SSL termination
- Unified CORS policy
- Rate limiting per user
- Request logging centralized
- Load balancing

**Nginx Configuration Example:**

```nginx
upstream backend {
    server localhost:5000;
}

upstream burnout {
    server localhost:8000;
}

upstream notebook {
    server localhost:8001;
}

upstream extraction {
    server localhost:8003;
}

server {
    listen 80;
    server_name api.sentryai.com;

    # Backend routes
    location /api/auth/ {
        proxy_pass http://backend;
    }

    location /api/users/ {
        proxy_pass http://backend;
    }

    location /api/tasks/ {
        proxy_pass http://backend;
    }

    # Burnout routes
    location /api/burnout/ {
        proxy_pass http://burnout;
    }

    # Notebook routes
    location /api/notebooks/ {
        proxy_pass http://notebook;
    }

    # Extraction routes
    location /api/extract/ {
        proxy_pass http://extraction;
    }
}
```

---

## 9. Monitoring & Observability

### 9.1 Health Check Endpoints

All services should implement:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "burnout-service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": check_db_connection(),
        "dependencies": {
            "ollama": check_ollama_connection(),
            "backend_service": check_backend_service()
        }
    }
```

### 9.2 Logging Standards

Use structured logging:

```python
import logging
import json

logger = logging.getLogger(__name__)

def log_request(user_id: int, endpoint: str, duration_ms: float):
    logger.info(json.dumps({
        "event": "api_request",
        "user_id": user_id,
        "endpoint": endpoint,
        "duration_ms": duration_ms,
        "timestamp": datetime.utcnow().isoformat()
    }))
```

### 9.3 Metrics to Track

- Request rate per endpoint
- Response times (p50, p95, p99)
- Error rates (4xx, 5xx)
- Database query times
- Ollama inference times
- User authentication failures
- Service-to-service call failures

---

## 10. Security Checklist

- [ ] JWT tokens use strong secret key (256-bit minimum)
- [ ] Passwords hashed with bcrypt (cost factor ≥ 12)
- [ ] HTTPS enforced in production
- [ ] CORS configured (not allow_origins=["*"])
- [ ] SQL injection protected (SQLAlchemy parameterized queries)
- [ ] File upload validation (type, size, content)
- [ ] Rate limiting on authentication endpoints
- [ ] Input validation on all endpoints
- [ ] User enumeration prevented (same error messages)
- [ ] Refresh tokens rotated on use
- [ ] Sensitive data not logged
- [ ] Environment variables not committed to git
- [ ] Database credentials rotated regularly
- [ ] OAuth redirect URIs validated
- [ ] CSRF protection on state-changing endpoints

---

## 11. Next Steps

### Immediate Actions (This Week)

1. **Review and approve this document** with team
2. **Set up development database** with pgvector extension
3. **Create Alembic migrations** for database schema changes
4. **Assign tasks** from Phase 1 to developers
5. **Set up project management board** (GitHub Projects / Jira)

### Before Development Starts

1. **Security review** - Ensure all team understands auth requirements
2. **Code style guide** - Establish linting and formatting standards
3. **Git workflow** - Define branching strategy (feature branches, PR reviews)
4. **Testing strategy** - Unit tests, integration tests, E2E tests

### Communication Plan

1. **Daily standups** (15 min) - Progress, blockers, coordination
2. **Weekly integration sync** - Cross-service testing
3. **Bi-weekly demos** - Show progress to stakeholders
4. **Documentation updates** - Keep this doc current as changes occur

---

## 12. Contact & Support

**Document Owner:** Integration Team
**Last Updated:** 2025-12-28
**Version:** 1.0

For questions or clarifications on this integration plan, please:
1. Check existing GitHub issues first
2. Create new issue with label `integration`
3. Tag relevant service owners

**Service Owners:**
- Backend Service: [TBD]
- Burnout Service: [TBD]
- Notebook Service: [TBD]
- Task Extraction: [TBD]

---

## Appendix A: File Structure After Integration

```
Sentry_AI/
├── backend_services/
│   ├── app/
│   │   ├── main.py                    # FastAPI app
│   │   ├── database.py                # DB connection
│   │   ├── models.py                  # SQLAlchemy models (UPDATED)
│   │   ├── routers/
│   │   │   ├── auth/
│   │   │   ├── task.py                # (UPDATED with burnout notifications)
│   │   │   ├── user.py
│   │   │   ├── integrations/
│   │   │   │   └── google_tasks.py    # (UPDATED with burnout trigger)
│   │   │   └── uploads/
│   │   │       └── session_system.py  # (UPDATED for DB persistence)
│   │   └── integrations/              # (NEW)
│   │       └── burnout_client.py      # (NEW) Service-to-service calls
│   ├── alembic/                       # (NEW) Database migrations
│   │   └── versions/
│   │       ├── 001_add_backend_tables.py
│   │       ├── 002_create_uploads_table.py
│   │       └── 003_merge_tasks_table.py
│   └── requirements.txt
│
├── AI_services/
│   └── app/
│       └── services/
│           ├── burn_out_service/
│           │   ├── api/
│           │   │   └── main.py        # (UPDATED with auth middleware)
│           │   ├── integrations/
│           │   │   └── task_database_integration.py  # (UPDATED model)
│           │   └── webhooks/          # (NEW)
│           │       └── task_update.py # (NEW) Receive notifications
│           │
│           ├── notebook_library/
│           │   └── FastAPI_app.py     # (UPDATED with auth + uploads table)
│           │
│           └── task_extraction/
│               ├── main.py             # (UPDATED with auth)
│               ├── task_extraction_api.py  # (UPDATED to call backend API)
│               └── backend_client.py   # (NEW) Service-to-service calls
│
├── shared/                            # (NEW) Shared libraries
│   ├── auth_middleware.py             # (NEW) JWT verification
│   ├── user_validation.py             # (NEW) User existence check
│   ├── config.py                      # (NEW) Service URLs
│   └── service_client.py              # (NEW) HTTP client with retry
│
├── docs/                              # (NEW)
│   ├── API_DOCUMENTATION.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── DEVELOPER_GUIDE.md
│
├── tests/                             # (NEW)
│   ├── integration/
│   │   └── test_full_workflow.py
│   └── unit/
│
├── docker-compose.yml                 # (NEW)
├── .env.example                       # (NEW)
├── start_all_services.sh              # (NEW)
├── BACKEND_AI_INTEGRATION_GUIDE.md    # This document
└── requirements.txt                   # Root dependencies
```

---

## Appendix B: Database ERD

```
┌─────────────┐
│    users    │ ◄────────────────┐
├─────────────┤                  │
│ id (PK)     │                  │
│ email       │                  │
│ password    │                  │
│ first_name  │                  │
│ last_name   │                  │
│ birthday    │                  │
└──────┬──────┘                  │
       │                         │
       │ 1:1                     │
       │                         │
       ▼                         │
┌──────────────────┐             │
│  user_profiles   │             │
├──────────────────┤             │
│ id (PK)          │             │
│ user_id (FK) ────┼─────────────┘
│ role             │
│ department       │
│ timezone         │
└─────────┬────────┘
          │
          │ 1:N
          │
     ┌────┴─────┬──────────┬────────────┬────────────┐
     ▼          ▼          ▼            ▼            ▼
┌─────────┐ ┌──────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐
│burnout  │ │user_ │ │user_     │ │user_     │ │qualit.  │
│analyses │ │prefs │ │constrs.  │ │behav.    │ │data     │
└─────────┘ └──────┘ └──────────┘ └──────────┘ └─────────┘


┌─────────────┐
│    users    │ ◄──────┐
└──────┬──────┘        │
       │ 1:N           │
       ▼               │
┌──────────────┐       │
│    tasks     │       │
├──────────────┤       │
│ id (PK)      │       │
│ user_id (FK) ├───────┘
│ title        │
│ description  │
│ status       │
│ deadline     │
│ priority     │
│ source       │  # 'sentry', 'google', 'extracted_audio', etc.
└──────────────┘


┌─────────────┐
│    users    │ ◄──────┐
└──────┬──────┘        │
       │ 1:N           │
       ▼               │
┌──────────────────┐   │
│ auth_providers   │   │
├──────────────────┤   │
│ id (PK)          │   │
│ user_id (FK) ────┼───┘
│ provider         │  # 'google', 'apple', 'facebook', 'email'
│ email            │
└──────────────────┘


┌─────────────┐
│    users    │ ◄──────┐
└──────┬──────┘        │
       │ 1:N           │
       ▼               │
┌──────────────────┐   │
│  integrations    │   │
├──────────────────┤   │
│ id (PK)          │   │
│ user_id (FK) ────┼───┘
│ service          │  # 'gmail', 'google_calendar', 'zoom', etc.
│ access_token     │
│ refresh_token    │
│ expiry           │
└──────────────────┘


┌─────────────┐
│    users    │ ◄──────┐
└──────┬──────┘        │
       │ 1:N           │
       ▼               │
┌──────────────────┐   │
│     uploads      │   │
├──────────────────┤   │
│ id (PK)          │   │
│ user_id (FK) ────┼───┘
│ filename         │
│ file_path        │
│ upload_type      │  # 'audio', 'document', 'image', etc.
│ processing_status│
│ extraction_result│  # JSONB
└──────────────────┘
```

---

**END OF DOCUMENT**
