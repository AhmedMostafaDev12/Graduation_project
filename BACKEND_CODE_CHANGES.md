# Backend Code Changes Summary

## Files Modified

### ✅ 1. backend_services/app/models.py

**Changes:**
- Updated `Task` model to match AI's tasks table schema
- Changed `deadline` → `due_date`
- Added AI-specific fields:
  - `task_type` ('task' or 'meeting')
  - `start_time`, `end_time` (for meetings)
  - `assigned_to`, `can_delegate`, `estimated_hours`
  - `is_recurring`, `is_optional`, `attendees`
- Changed `added_at` → `created_at`
- Added imports: `Text`, `Float`, `datetime`

**Key Changes:**
```python
# BEFORE
deadline = Column(TIMESTAMP(timezone=True), nullable=False)
added_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

# AFTER
due_date = Column(DateTime, nullable=True)
start_time = Column(DateTime, nullable=True)
end_time = Column(DateTime, nullable=True)
task_type = Column(String, default='task')
created_at = Column(DateTime, default=datetime.utcnow)
# ... plus AI analysis fields
```

---

### ✅ 2. backend_services/app/schemas.py

**Changes:**

#### TaskCreate Schema:
- Changed `deadline: datetime` → `due_date: Optional[datetime] = None`
- Made `category` optional
- Added `task_type: str = "task"`
- Added all AI integration fields (start_time, end_time, assigned_to, etc.)

```python
# BEFORE
class TaskCreate(BaseModel):
    title: str
    category: str
    description: Optional[str] = ""
    status: str
    priority: str
    deadline: datetime

# AFTER
class TaskCreate(BaseModel):
    title: str
    category: Optional[str] = None
    description: Optional[str] = ""
    task_type: str = "task"
    status: str
    priority: str
    due_date: Optional[datetime] = None  # ← Changed
    # Plus: start_time, end_time, assigned_to, can_delegate,
    #       estimated_hours, is_recurring, is_optional, attendees
```

#### TaskRead Schema:
- Changed `deadline` → `due_date`
- Made `category` and `source` optional
- Added `task_type` field
- Added all AI fields
- Added `created_at` and `updated_at` timestamps

```python
# BEFORE
class TaskRead(BaseModel):
    id: int
    user_id: int
    title: str
    category: str
    status: str
    priority: str
    deadline: datetime  # ← Changed to due_date
    source: str

# AFTER
class TaskRead(BaseModel):
    id: int
    user_id: int
    title: str
    category: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[datetime] = None  # ← Changed
    source: Optional[str] = None
    # Plus all AI fields and timestamps
```

---

### ✅ 3. backend_services/app/routers/task.py

**No changes required!**

The task router code works as-is because:
- It uses `schemas.TaskCreate` and `schemas.TaskRead` which we updated
- SQLAlchemy ORM automatically maps the new fields
- The `**task.dict()` unpacking handles all fields

**However, note these behaviors:**

1. **Line 66** - Manual `updated_at` setting:
   ```python
   updated_at.updated_at = datetime.now()  # This still works
   ```
   The SQLAlchemy model also has `onupdate=datetime.utcnow`, so this is redundant but harmless.

2. **Line 20** - Source is hardcoded:
   ```python
   task = models.Task(**task.dict(), user_id=current_user.id, source="sentry")
   ```
   This correctly sets `source="sentry"` for backend-created tasks.

---

## Database Migration Required

**Before starting the backend service, run:**

```bash
psql -U your_username -d sentry_ai -f database_migration.sql
```

This will:
- Create the unified tasks table schema
- Add users, auth_providers, integrations, uploads tables
- Link everything with foreign keys

---

## Testing the Changes

### 1. Start the Backend Service

```bash
cd backend_services
uvicorn app.main:app --port 5000 --reload
```

**Expected:** Should start without errors.

### 2. Test Task Creation

```bash
# Login first
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Create task with new schema
curl -X POST http://localhost:5000/api/tasks/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing new schema",
    "task_type": "task",
    "status": "pending",
    "priority": "high",
    "category": "Development",
    "due_date": "2025-12-30T10:00:00"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Test Task",
  "description": "Testing new schema",
  "task_type": "task",
  "status": "pending",
  "priority": "high",
  "category": "Development",
  "due_date": "2025-12-30T10:00:00",
  "source": "sentry",
  "assigned_to": null,
  "can_delegate": true,
  "estimated_hours": null,
  "is_recurring": false,
  "is_optional": false,
  "attendees": null,
  "created_at": "2025-12-29T12:00:00",
  "updated_at": "2025-12-29T12:00:00"
}
```

### 3. Verify Database

```sql
-- Check tasks table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'tasks'
ORDER BY ordinal_position;

-- Should show: due_date, task_type, start_time, end_time, etc.
```

### 4. Test AI Service Integration

```bash
# Start task extraction service
cd AI_services/app/services/task_extraction
uvicorn main:app --port 8003 --reload

# Extract tasks from file
curl -X POST http://localhost:8003/api/extract/text \
  -F "file=@test.txt" \
  -F "user_id=1" \
  -F "save_to_db=true"

# Verify extracted tasks appear in same table
curl http://localhost:5000/api/tasks/ \
  -H "Authorization: Bearer <token>"
```

**Expected:** Backend and AI services both read/write to the same tasks table.

---

## Breaking Changes

### ⚠️ Frontend Updates Needed

If you have a frontend application, update API calls:

**OLD:**
```javascript
// Creating task
fetch('/api/tasks/', {
  method: 'POST',
  body: JSON.stringify({
    title: 'My Task',
    deadline: '2025-12-30T10:00:00',  // ❌ Old field
    category: 'Development'  // ❌ Was required
  })
})
```

**NEW:**
```javascript
// Creating task
fetch('/api/tasks/', {
  method: 'POST',
  body: JSON.stringify({
    title: 'My Task',
    due_date: '2025-12-30T10:00:00',  // ✅ New field
    category: 'Development',  // ✅ Now optional
    task_type: 'task',  // ✅ New field
    status: 'pending',
    priority: 'high'
  })
})
```

**Response changes:**
```javascript
// Task object now includes
{
  due_date,      // Instead of 'deadline'
  created_at,    // Instead of 'added_at'
  task_type,     // New field
  assigned_to,   // New AI fields
  can_delegate,
  estimated_hours,
  is_recurring,
  is_optional,
  start_time,
  end_time,
  attendees
}
```

---

## Rollback Plan

If you need to rollback:

1. **Restore old model:**
   ```bash
   git checkout HEAD -- backend_services/app/models.py
   git checkout HEAD -- backend_services/app/schemas.py
   ```

2. **Restore old database schema:**
   - Run database backup restoration
   - Or manually drop and recreate tables

---

## Next Steps

After verifying these changes work:

1. ✅ Backend code updated
2. ⏳ Run database migration (`database_migration.sql`)
3. ⏳ Test backend service
4. ⏳ Test AI services
5. ⏳ Update frontend (if applicable)
6. ⏳ Add authentication to AI services (see main integration guide)
7. ⏳ Implement service-to-service communication

---

## Summary

**What changed:**
- `deadline` → `due_date` (everywhere)
- `added_at` → `created_at`
- Added AI analysis fields to Task model and schemas
- Made `category` and `source` optional

**What stayed the same:**
- All API endpoints (`/api/tasks/`, etc.)
- Authentication flow
- CRUD operations
- Database table name (`tasks`)

**Compatibility:**
- ✅ Backend and AI services now use **same schema**
- ✅ Tasks created by either service appear in unified table
- ✅ Both services can read each other's tasks
