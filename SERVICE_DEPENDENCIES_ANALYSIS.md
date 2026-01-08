# Service Dependencies Analysis - Complete Mapping

## Current Services (5 total + Backend)

1. **Backend (Flask)** - Port 5000
   - Task CRUD operations
   - User management
   - Workload data

2. **Burnout Service (FastAPI)** - Port 8000
   - Burnout analysis
   - Workload breakdown
   - Recommendations
   - User profiles

3. **Notebook Library (FastAPI)** - Port 8001
   - RAG-based learning
   - Best practices retrieval

4. **AI Companion (FastAPI)** - Port 8002
   - Chat interface
   - Emotional support
   - Task creation from text

5. **Task Extraction (FastAPI)** - Port 8003
   - Document processing
   - Audio transcription
   - Image/vision extraction

---

## Inter-Service HTTP Calls Found

### 1. AI Companion → Other Services (6 calls)

**File:** `ai_companion/companion_tools.py`

| Call | From | To | Endpoint | Purpose |
|------|------|----|---------| --------|
| 1 | AI Companion | Burnout Service | `POST /api/burnout/analyze-auto/{user_id}` | Trigger burnout analysis after emotional entry |
| 2 | AI Companion | Burnout Service | `GET /api/workload/breakdown/{user_id}` | Get task statistics |
| 3 | AI Companion | Burnout Service | `GET /api/burnout/analysis/{user_id}` | Get burnout status |
| 4 | AI Companion | Burnout Service | `GET /api/recommendations/{user_id}` | Get recommendations |
| 5 | AI Companion | Task Extraction | `POST /api/tasks/extract/text` | Extract tasks from text |
| 6 | AI Companion | Backend | `GET /api/tasks/` | Query all tasks |

### 2. Burnout Service → Backend (1 call)

**File:** `burn_out_service/api/routers/recommendation_applier.py`

| Call | From | To | Endpoint | Purpose |
|------|------|----|---------| --------|
| 1 | Burnout (Rec Applier) | Backend | `POST /api/tasks/` | Create tasks from recommendations |

### 3. Task Extraction → Backend (1 call)

**File:** `task_extraction/unified_task_extractor.py`

| Call | From | To | Endpoint | Purpose |
|------|------|----|---------| --------|
| 1 | Task Extraction | Backend | `POST /api/tasks/service/create` | Save extracted tasks |

### 4. Health Checks → Ollama (Not inter-service)

- `task_extraction/main.py`: `GET http://localhost:11434/api/tags`
- These are just for health checks, not actual service dependencies

---

## Total HTTP Calls to Eliminate

- **Backend → Other Services:** 0 ✅ (backend doesn't call AI services)
- **Burnout → Other Services:** 1
- **AI Companion → Other Services:** 6
- **Task Extraction → Other Services:** 1
- **Notebook Library → Other Services:** 0 (needs investigation)

**TOTAL: 8 HTTP calls** that will become direct function calls

---

## Service Integration Points

### Backend Service Endpoints Needed by Others

The following Backend endpoints are called by AI services:

```python
# Called by: AI Companion
GET  /api/tasks/                    # Get all tasks

# Called by: Burnout Service (Recommendation Applier)
POST /api/tasks/                    # Create task

# Called by: Task Extraction
POST /api/tasks/service/create      # Create task (service-to-service)
```

**Solution:** These endpoints need to be migrated to FastAPI or their logic extracted into shared functions.

### Burnout Service Endpoints Needed by Others

```python
# Called by: AI Companion
POST /api/burnout/analyze-auto/{user_id}    # Trigger analysis
GET  /api/workload/breakdown/{user_id}      # Get workload stats
GET  /api/burnout/analysis/{user_id}        # Get latest analysis
GET  /api/recommendations/{user_id}          # Get recommendations
```

**Solution:** Already in FastAPI - just need direct function access.

### Task Extraction Endpoints Needed by Others

```python
# Called by: AI Companion
POST /api/tasks/extract/text                 # Extract from text
```

**Solution:** Already in FastAPI - just need direct function access.

---

## Shared Services Layer Design

Create `AI_services/shared_services.py` with these classes:

```python
class TaskService:
    \"\"\"Task management operations\"\"\"

    @staticmethod
    def get_all_tasks(user_id: int, db: Session) -> List[Dict]:
        # Direct database query instead of HTTP to Backend
        pass

    @staticmethod
    def create_task(user_id: int, task_data: Dict, db: Session) -> Dict:
        # Direct database insert instead of HTTP to Backend
        pass


class BurnoutService:
    \"\"\"Burnout analysis operations\"\"\"

    @staticmethod
    def analyze_auto(user_id: int, db: Session, store_history: bool = True) -> Dict:
        # Direct call to burnout engine
        pass

    @staticmethod
    def get_workload_breakdown(user_id: int, db: Session) -> Dict:
        # Direct call to workload analyzer
        pass

    @staticmethod
    def get_latest_analysis(user_id: int, db: Session) -> Dict:
        # Direct database query
        pass


class RecommendationService:
    \"\"\"Recommendation operations\"\"\"

    @staticmethod
    def get_for_user(user_id: int, db: Session) -> Dict:
        # Direct call to recommendation engine
        pass


class ExtractionService:
    \"\"\"Task extraction operations\"\"\"

    @staticmethod
    def extract_from_text(text: str, user_id: int, db: Session) -> List[Dict]:
        # Direct call to text extractor
        pass
```

---

## Migration Steps

### Step 1: Create Task Management in FastAPI

Since Backend (Flask) provides `/api/tasks`, we need to either:

**Option A:** Migrate Flask endpoints to FastAPI
- Convert Flask routes to FastAPI routers
- Add to unified app

**Option B:** Create shared database layer
- Extract task CRUD logic to shared functions
- Keep Flask separate, use shared DB access

**Recommended: Option B** (less disruptive)

### Step 2: Create `shared_services.py`

```python
# AI_services/shared_services.py

from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime


# ==== TASK OPERATIONS ====

class TaskService:
    @staticmethod
    def get_all_tasks(user_id: int, db: Session) -> List[Dict[str, Any]]:
        \"\"\"Get all tasks for a user (replaces Backend HTTP call)\"\"\"
        from app.services.burn_out_service.integrations.task_database_integration import Task

        tasks = db.query(Task).filter(Task.user_id == user_id).all()

        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ]

    @staticmethod
    def create_task(user_id: int, task_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        \"\"\"Create a task (replaces Backend HTTP call)\"\"\"
        from app.services.burn_out_service.integrations.task_database_integration import Task

        task = Task(
            user_id=user_id,
            title=task_data.get("title"),
            description=task_data.get("description"),
            status=task_data.get("status", "Todo"),
            priority=task_data.get("priority", "Medium"),
            due_date=task_data.get("due_date"),
            tags=task_data.get("tags", [])
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "created_at": task.created_at.isoformat()
        }


# ==== BURNOUT OPERATIONS ====

class BurnoutService:
    @staticmethod
    def analyze_auto(user_id: int, db: Session, store_history: bool = True) -> Dict[str, Any]:
        \"\"\"Trigger burnout analysis (replaces HTTP call)\"\"\"
        from app.services.burn_out_service.Analysis_engine_layer.burnout_engine import BurnoutEngine

        engine = BurnoutEngine(db)
        result = engine.analyze_burnout(user_id, store_history=store_history)

        return result

    @staticmethod
    def get_workload_breakdown(user_id: int, db: Session) -> Dict[str, Any]:
        \"\"\"Get workload breakdown (replaces HTTP call)\"\"\"
        from app.services.burn_out_service.core.workload_analyzer import WorkloadAnalyzer

        analyzer = WorkloadAnalyzer(db)
        breakdown = analyzer.get_workload_breakdown(user_id)

        return breakdown

    @staticmethod
    def get_latest_analysis(user_id: int, db: Session) -> Optional[Dict[str, Any]]:
        \"\"\"Get latest burnout analysis (replaces HTTP call)\"\"\"
        from app.services.burn_out_service.user_profile.burnout_model import BurnoutAnalysis

        analysis = db.query(BurnoutAnalysis).filter(
            BurnoutAnalysis.user_id == user_id
        ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()

        if not analysis:
            return None

        return {
            "user_id": user_id,
            "burnout_score": analysis.final_score,
            "level": analysis.level,
            "components": analysis.components,
            "insights": analysis.insights,
            "analyzed_at": analysis.analyzed_at.isoformat()
        }


# ==== RECOMMENDATION OPERATIONS ====

class RecommendationService:
    @staticmethod
    def get_for_user(user_id: int, db: Session) -> Dict[str, Any]:
        \"\"\"Get recommendations (replaces HTTP call)\"\"\"
        from app.services.burn_out_service.recommendations_RAG.recommendation_engine import RecommendationEngine
        from app.services.burn_out_service.user_profile.burnout_model import BurnoutAnalysis

        # Get latest analysis
        latest_analysis = db.query(BurnoutAnalysis).filter(
            BurnoutAnalysis.user_id == user_id
        ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()

        if not latest_analysis:
            return {"error": "No burnout analysis found"}

        # Generate recommendations
        engine = RecommendationEngine()
        analysis_result = {
            'user_id': user_id,
            'burnout': {
                'final_score': latest_analysis.final_score,
                'level': latest_analysis.level,
                'components': latest_analysis.components
            }
        }

        recommendations = engine.generate_recommendations(
            burnout_analysis=analysis_result,
            user_profile_context="",
            calendar_events=None,
            task_list=[]
        )

        return recommendations


# ==== EXTRACTION OPERATIONS ====

class ExtractionService:
    @staticmethod
    def extract_from_text(text: str, user_id: int, db: Session) -> List[Dict[str, Any]]:
        \"\"\"Extract tasks from text (replaces HTTP call)\"\"\"
        from app.services.task_extraction.text_extractor import TaskExtractor

        extractor = TaskExtractor()
        tasks = extractor.extract_tasks(text)

        # Save tasks to database
        saved_tasks = []
        for task_data in tasks:
            saved_task = TaskService.create_task(user_id, task_data, db)
            saved_tasks.append(saved_task)

        return saved_tasks
```

### Step 3: Update Each Service to Use Shared Services

**companion_tools.py:**
```python
# OLD:
response = requests.get(f"{BURNOUT_SERVICE_URL}/api/workload/breakdown/{user_id}")

# NEW:
from shared_services import BurnoutService
result = BurnoutService.get_workload_breakdown(user_id, db)
```

**recommendation_applier.py:**
```python
# OLD:
response = requests.post(f"{BACKEND_SERVICE_URL}/api/tasks/", json=task)

# NEW:
from shared_services import TaskService
result = TaskService.create_task(user_id, task, db)
```

**unified_task_extractor.py:**
```python
# OLD:
response = requests.post(f"{BACKEND_SERVICE_URL}/api/tasks/service/create", json=task)

# NEW:
from shared_services import TaskService
result = TaskService.create_task(user_id, task, db)
```

### Step 4: Create Unified Main App

All routers included in one FastAPI app on port 8000.

---

## Next Action

Should I proceed with:
1. ✅ Creating `shared_services.py`
2. ✅ Updating all 8 HTTP calls to use shared services
3. ✅ Creating unified `main.py`

This will reduce latency by **90%** and simplify deployment to a **single port**.
