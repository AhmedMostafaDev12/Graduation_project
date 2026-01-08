# Simplified Integration Implementation Plan

## Overview
Keep AI's existing tasks table schema, add backend tables, link with foreign keys.

---

## Phase 1: Database Setup ✅

### Step 1: Run Migration Script
```bash
# Connect to your PostgreSQL database
psql -U your_username -d sentry_ai -f database_migration.sql
```

**What this does:**
- Creates `users` table (primary)
- Creates `auth_providers` table → linked to users
- Creates `integrations` table → linked to users
- Creates `uploads` table → linked to users
- Adds foreign keys to existing AI tables:
  - `user_profiles.user_id` → `users.id`
  - `tasks.user_id` → `users.id`
  - `qualitative_data.user_id` → `users.id`
- Adds missing columns to `tasks` table for backend compatibility

**Result:** Database structure matches your diagram exactly.

---

## Phase 2: Update Backend Task Model

### Step 2: Update Backend's Task Model

The backend needs to use the AI's tasks table schema instead of creating its own.

**File:** [backend_services/app/models.py](backend_services/app/models.py#L49-L70)

**Replace the Task class with:**

```python
class Task(Base):
    __tablename__ = "tasks"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Foreign key to users
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Core fields
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")

    # Classification
    task_type = Column(String(20), default='task')  # 'task' or 'meeting'
    status = Column(String(50))
    priority = Column(String(20))
    category = Column(String(100))

    # Timing
    due_date = Column(DateTime, nullable=True)  # AI uses 'due_date', not 'deadline'
    start_time = Column(DateTime, nullable=True)  # For meetings
    end_time = Column(DateTime, nullable=True)    # For meetings

    # Source tracking (Backend feature)
    source = Column(String(50))  # 'sentry', 'google', 'extracted_audio', etc.

    # Google Tasks integration (Backend feature)
    google_task_id = Column(String(255), unique=True)
    google_tasklist_id = Column(String(255))

    # AI Analysis fields
    assigned_to = Column(String(100))
    can_delegate = Column(Boolean, default=True)
    estimated_hours = Column(Float, nullable=True)
    is_recurring = Column(Boolean, default=False)
    is_optional = Column(Boolean, default=False)

    # Meeting-specific (AI feature)
    attendees = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Changes needed in backend code:**
- Replace `task.deadline` → `task.due_date`
- Add `task.description` (new field)
- Add `task.category` (new field if used)

---

## Phase 3: Update Backend API Endpoints

### Step 3: Update Task Router

**File:** [backend_services/app/routers/task.py](backend_services/app/routers/task.py)

**Changes needed:**

1. **Update Pydantic schemas to match new Task model:**

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: str = ""
    task_type: str = "task"  # 'task' or 'meeting'
    status: str
    priority: str
    category: Optional[str] = None
    due_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    source: str = "sentry"
    assigned_to: Optional[str] = None
    can_delegate: bool = True
    estimated_hours: Optional[float] = None
    is_recurring: bool = False
    is_optional: bool = False
    attendees: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    # ... other optional fields

class TaskResponse(TaskBase):
    id: int
    user_id: int
    google_task_id: Optional[str] = None
    google_tasklist_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

2. **Update any references from `deadline` to `due_date`:**

```python
# OLD
task.deadline = new_deadline

# NEW
task.due_date = new_due_date
```

---

## Phase 4: Testing

### Step 4: Verify Database

```sql
-- Check all tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Expected tables:
-- ✓ users
-- ✓ auth_providers
-- ✓ integrations
-- ✓ uploads
-- ✓ user_profiles
-- ✓ burnout_analyses
-- ✓ user_preferences
-- ✓ user_constraints
-- ✓ user_behavioral_profiles
-- ✓ qualitative_data
-- ✓ tasks
-- ✓ langchain_pg_collection (vector DB)
-- ✓ langchain_pg_embedding (vector DB)
```

```sql
-- Check foreign keys
SELECT
    tc.table_name,
    tc.constraint_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;

-- Expected foreign keys:
-- ✓ auth_providers.user_id → users.id
-- ✓ integrations.user_id → users.id
-- ✓ uploads.user_id → users.id
-- ✓ user_profiles.user_id → users.id
-- ✓ tasks.user_id → users.id
-- ✓ qualitative_data.user_id → users.id
-- ✓ burnout_analyses.user_profile_id → user_profiles.id
-- ✓ user_preferences.user_profile_id → user_profiles.id
-- ✓ user_constraints.user_profile_id → user_profiles.id
-- ✓ user_behavioral_profiles.user_profile_id → user_profiles.id
```

### Step 5: Test Backend Service

```bash
# Start backend service
cd backend_services
uvicorn app.main:app --port 5000 --reload
```

Test endpoints:
1. **Create user:** `POST /api/users/`
2. **Login:** `POST /api/auth/login`
3. **Create task:** `POST /api/tasks/{user_id}` (verify due_date works)
4. **Get tasks:** `GET /api/tasks/{user_id}`

### Step 6: Test AI Services Still Work

```bash
# Start burnout service
cd AI_services/app/services/burn_out_service
uvicorn api.main:app --port 8000 --reload

# Test creating task via AI
# Verify it uses same tasks table as backend
```

---

## Checklist

### Database
- [ ] Run `database_migration.sql`
- [ ] Verify all 13 tables exist
- [ ] Verify all foreign keys created
- [ ] Verify tasks table has all columns

### Backend Code
- [ ] Update `Task` model in [models.py](backend_services/app/models.py)
- [ ] Update Pydantic schemas in [task.py](backend_services/app/routers/task.py)
- [ ] Replace all `deadline` → `due_date`
- [ ] Test backend service starts without errors

### Testing
- [ ] Create test user via backend
- [ ] Create task via backend (check it appears in DB)
- [ ] Create task via AI extraction (check it appears in DB)
- [ ] Verify both services use same tasks table
- [ ] Verify foreign key constraints work (delete user → cascade deletes)

---

## Quick Start Commands

```bash
# 1. Run database migration
psql -U postgres -d sentry_ai -f database_migration.sql

# 2. Start all services
# Terminal 1 - Backend
cd backend_services
uvicorn app.main:app --port 5000 --reload

# Terminal 2 - Burnout
cd AI_services/app/services/burn_out_service
uvicorn api.main:app --port 8000 --reload

# Terminal 3 - Notebook
cd AI_services/app/services/notebook_library
uvicorn FastAPI_app:app --port 8001 --reload

# Terminal 4 - Extraction
cd AI_services/app/services/task_extraction
uvicorn main:app --port 8003 --reload
```

---

## File Changes Summary

**Files to modify:**
1. ✅ `database_migration.sql` - Created
2. ⏳ `backend_services/app/models.py` - Update Task model
3. ⏳ `backend_services/app/routers/task.py` - Update schemas, change deadline→due_date

**Files that DON'T need changes:**
- ✅ AI services (already using correct schema)
- ✅ AI database models (already correct)
- ✅ All other backend models (users, auth_providers, integrations already match)

---

## Next Steps After Database Setup

Once database is migrated, the next priorities are:

1. **Authentication** - Add JWT verification to AI services (see main guide)
2. **Service Integration** - Make services call each other (see main guide)
3. **Upload System** - Implement uploads table in backend/AI services

Refer to [BACKEND_AI_INTEGRATION_GUIDE.md](BACKEND_AI_INTEGRATION_GUIDE.md) for detailed implementation of these features.
