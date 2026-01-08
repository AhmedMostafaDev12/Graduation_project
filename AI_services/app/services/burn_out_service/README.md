# Sentry AI - Intelligent Burnout Prevention System

**Tagline:** *Real-Time Calendar and Task-Aware Burnout Prevention*

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Architecture](#architecture)
4. [User Profile System](#user-profile-system)
5. [Database Schema](#database-schema)
6. [API Integration](#api-integration)
7. [Examples](#examples)
8. [Setup Guide](#setup-guide)

---

## Quick Start

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your database URLs

# 3. Initialize databases
python scripts/init_database.py

# 4. Populate vector database with strategies
python scripts/populate_strategies.py

# 5. Start Ollama (for LLM)
ollama serve
ollama pull llama3.1:8b
```

### Basic Usage

```python
from integrations.task_database_integration import get_complete_user_context
from user_profile.integration_services import BurnoutSystemIntegration
from recommendations.recommendation_engine import RecommendationEngine

# Step 1: Get user data from database
context = get_complete_user_context(user_id=123, session=db_session)

# Step 2: Analyze burnout
integration = BurnoutSystemIntegration(db_session)
analysis = integration.complete_daily_flow(
    user_id=123,
    quantitative_metrics=context['metrics'],
    qualitative_data=context['qualitative_data']
)

# Step 3: Generate event-specific recommendations
engine = RecommendationEngine()
recommendations = engine.generate_recommendations(
    burnout_analysis=analysis,
    user_profile_context=analysis['user_profile'],
    learned_patterns=analysis.get('learned_patterns'),
    calendar_events=context['meetings'],
    task_list=context['tasks']
)

# Print results
print(f"Burnout Level: {analysis['burnout']['level']}")
for rec in recommendations.recommendations:
    print(f"- {rec.title}")
```

---

## System Overview

### What It Does

Sentry AI monitors user workload and generates **event-specific, time-aware recommendations** to prevent burnout.

**Input (from your database):**
- Tasks (with priorities, deadlines, delegation status)
- Meetings (with times, attendees, optional flags)
- Qualitative data (sentiment notes, meeting transcripts)

**Output (actionable recommendations):**
- "Cancel your 3:30 PM 'Team Sync' meeting - it's optional"
- "Delegate 'Database Migration Script' to Alex"
- "Block 11:30 AM - 12:00 PM for a 30-minute walk"

### Key Features

1. **Real-Time Awareness** - References actual event names and times
2. **Automatic Metrics** - Calculates everything from database
3. **Event-Specific** - Not generic advice, exact actions
4. **Proactive** - Schedules recovery activities in calendar gaps
5. **Personalized** - Learns patterns, respects preferences

---

## Architecture

### System Flow

```
┌─────────────────────────────────────────────────────────┐
│ DATABASE (Your Backend)                                  │
│ - tasks table (tasks + meetings)                        │
│ - qualitative_data table (sentiment notes)              │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 1: Data Collection                                │
│ File: integrations/task_database_integration.py         │
│                                                          │
│ Output:                                                  │
│ - metrics: UserMetrics (auto-calculated)                │
│ - tasks: List[Dict] (actual tasks)                      │
│ - meetings: List[Dict] (actual calendar events)         │
│ - qualitative_data: QualitativeData                     │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 2: Burnout Analysis                               │
│ Files: user_profile/integration_services.py             │
│        core/workload_analyzer.py                        │
│        core/sentiment_analyzer.py                       │
│                                                          │
│ Process:                                                 │
│ 1. Analyze workload (quantitative) → score             │
│ 2. Analyze sentiment (qualitative) → score             │
│ 3. Combine → final burnout score                       │
│ 4. Determine level (GREEN/YELLOW/RED)                  │
│ 5. Learn patterns (baseline, triggers)                 │
│                                                          │
│ Output:                                                  │
│ - burnout_score: 0-100                                  │
│ - burnout_level: GREEN/YELLOW/RED                       │
│ - insights: Issues, indicators, signals                │
│ - learned_patterns: Baseline, triggers                 │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 3: Recommendation Generation                      │
│ Files: recommendations/recommendation_engine.py          │
│        recommendations/rag_retrieval.py                 │
│        recommendations/recommendation_generator.py       │
│                                                          │
│ Process:                                                 │
│ 1. Retrieve evidence-based strategies (RAG)            │
│ 2. Build LLM prompt with:                              │
│    - User profile                                       │
│    - Burnout analysis                                   │
│    - Actual calendar events                            │
│    - Actual tasks                                       │
│ 3. LLM generates event-specific recommendations        │
│                                                          │
│ Output:                                                  │
│ - Event-specific recommendations                        │
│ - Time-aware adjustments                               │
│ - Scheduled recovery plans                             │
└─────────────────────────────────────────────────────────┘
```

### Layer 1: Data Collection

**File:** `integrations/task_database_integration.py`

**Main Function:** `get_complete_user_context(user_id, session)`

**What it does:**
1. Retrieves tasks and meetings from database
2. Retrieves qualitative data (sentiment notes)
3. **Automatically calculates metrics** (no manual input needed):
   - `total_active_tasks` = COUNT(tasks WHERE status != 'Done')
   - `meetings_today` = COUNT(meetings WHERE date = TODAY)
   - `back_to_back_meetings` = calculated from meeting times

**Returns:**
```python
{
    'metrics': UserMetrics(...),           # Auto-calculated
    'tasks': [List of actual tasks],       # For recommendations
    'meetings': [List of actual meetings], # For recommendations
    'qualitative_data': QualitativeData()  # For sentiment analysis
}
```

---

### Layer 2: Burnout Analysis

**Main File:** `user_profile/integration_services.py`

**Main Function:** `complete_daily_flow(user_id, metrics, qualitative_data)`

**What it does:**
1. Gets user profile (preferences, constraints, learned patterns)
2. Analyzes workload from quantitative metrics → workload_score
3. Analyzes sentiment from qualitative data → sentiment_score
4. Combines scores (60% workload + 40% sentiment) → final_score
5. Determines burnout level:
   - Score < 40 → GREEN
   - Score 40-70 → YELLOW
   - Score > 70 → RED
6. Learns behavioral patterns (after 7+ days of data)
7. Saves analysis to database

**Returns:**
```python
{
    'user_id': 123,
    'user_profile': "USER PROFILE:\nName: Sarah Chen\n...",  # Formatted for LLM

    'burnout': {
        'final_score': 70.4,
        'level': 'RED',
        'insights': {
            'primary_issues': ['Too many meetings', 'Back-to-back meetings'],
            'stress_indicators': ['overwhelmed', 'exhaustion'],
            'burnout_signals': {'emotional_exhaustion': True, 'overwhelm': True}
        },
        'trend': {...},
        'alert_triggers': {...}
    },

    'learned_patterns': {
        'baseline_score': 42.0,
        'stress_triggers': ['back_to_back_meetings'],
        'workload_trend': 'increasing'
    }
}
```

---

### Layer 3: Recommendation Generation

**Main File:** `recommendations/recommendation_engine.py`

**Main Function:** `generate_recommendations(burnout_analysis, calendar_events, task_list)`

**What it does:**
1. Extracts context from burnout analysis
2. Builds RAG query and retrieves evidence-based strategies from vector database
3. Builds LLM prompt including:
   - User profile (preferences, constraints)
   - Burnout analysis
   - **Actual calendar events** with times
   - **Actual tasks** with details
4. LLM generates event-specific recommendations

**LLM receives:**
```
TODAY'S CALENDAR EVENTS:
1. 03:00 PM - 03:30 PM: "Code Review" (30 min)
2. 03:30 PM - 04:30 PM: "Team Sync" (60 min)
   → OPTIONAL - can decline | Recurring

CURRENT TASK LIST:
1. "Database Migration Script"
   Status: In Progress | Priority: High | Due: Tomorrow
   → CAN DELEGATE | Currently assigned to: Sarah Chen
```

**Returns:**
```python
[
    {
        "title": "Cancel 3:30 PM Team Sync Meeting",
        "description": "Your 'Team Sync' is OPTIONAL and creates back-to-back with Code Review",
        "action_steps": [
            "Decline '3:30 PM Team Sync (Weekly)' in calendar",
            "Use freed time for 30-min walk"
        ],
        "priority": "HIGH"
    },
    {
        "title": "Delegate Database Migration to Alex",
        "description": "You have 2 direct reports and this task can be delegated",
        "action_steps": [
            "Reassign 'Database Migration Script' to Alex",
            "Send context message"
        ],
        "priority": "CRITICAL"
    }
]
```

---

## User Profile System

The user profile system manages personalized information for each user.

### Database Tables

#### `user_profiles`
- Basic info: name, role, team size, can delegate
- Example: Sarah Chen, Senior SWE, 8 team members, 2 direct reports

#### `user_preferences`
- Communication style: direct, supportive, data-driven
- Accepted recommendation types: time_blocking, delegation
- Avoided recommendation types: meditation, therapy

#### `user_constraints`
- Active constraints: deadlines, PTO blocks, delegation blocks
- Example: "Q4 Launch (deadline) until 2025-12-15 - Cannot take PTO"

#### `behavioral_patterns`
- Learned baselines: baseline_burnout_score, avg_tasks_per_day
- Stress triggers: back_to_back_meetings, weekend_work
- Updated automatically after 7+ days of data

### Key Features

1. **Personalized Analysis**
   - Compares current score to user's personal baseline
   - Detects deviation from normal patterns

2. **Personalized Recommendations**
   - Respects preferences (suggests time_blocking, avoids meditation)
   - Respects constraints (doesn't suggest PTO during deadline)
   - Accounts for delegation ability

3. **Behavioral Learning**
   - Learns each user's "normal" workload
   - Identifies stress triggers unique to each user
   - Improves over time

---

## Database Schema

### For Your Backend Team

#### 1. `tasks` Table (stores both tasks AND meetings)

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    task_type VARCHAR(20) DEFAULT 'task',  -- 'task' or 'meeting'

    -- Common fields
    status VARCHAR(50),  -- 'Todo', 'In Progress', 'Done', 'Blocked'
    priority VARCHAR(20),  -- 'Low', 'Medium', 'High', 'Critical'
    due_date TIMESTAMP,
    assigned_to VARCHAR(100),
    can_delegate BOOLEAN DEFAULT TRUE,
    estimated_hours FLOAT,

    -- Meeting-specific (when task_type='meeting')
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    attendees TEXT,
    is_recurring BOOLEAN DEFAULT FALSE,
    is_optional BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_type ON tasks(task_type);
CREATE INDEX idx_tasks_status ON tasks(status);
```

**Example rows:**

```sql
-- Work task
INSERT INTO tasks (title, user_id, task_type, status, priority, due_date, can_delegate, estimated_hours)
VALUES ('Database Migration Script', 123, 'task', 'In Progress', 'High', '2025-12-13', TRUE, 4);

-- Meeting
INSERT INTO tasks (title, user_id, task_type, start_time, end_time, attendees, is_recurring, is_optional)
VALUES ('Team Sync', 123, 'meeting', '2025-12-12 15:30', '2025-12-12 16:30', 'team@company.com', TRUE, TRUE);
```

#### 2. `qualitative_data` Table

```sql
CREATE TABLE qualitative_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    entry_type VARCHAR(50),  -- 'meeting_transcript', 'task_note', 'user_check_in'
    content TEXT NOT NULL,
    sentiment_score FLOAT,
    task_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_qualitative_user_id ON qualitative_data(user_id);
CREATE INDEX idx_qualitative_entry_type ON qualitative_data(entry_type);
```

**Example rows:**

```sql
INSERT INTO qualitative_data (user_id, entry_type, content)
VALUES (123, 'meeting_transcript', 'Team feeling overwhelmed with Q4 deadline');

INSERT INTO qualitative_data (user_id, entry_type, content)
VALUES (123, 'user_check_in', 'Feeling exhausted today');
```

---

## API Integration

### Backend API Example

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from integrations.task_database_integration import get_complete_user_context
from user_profile.integration_services import BurnoutSystemIntegration
from recommendations.recommendation_engine import RecommendationEngine

router = APIRouter()

@router.post("/api/burnout/analyze")
def analyze_burnout(user_id: int, db: Session = Depends(get_db)):
    """
    Complete burnout analysis with event-specific recommendations.

    Everything is automatic - just provide user_id!
    """

    # Step 1: Get data from database (automatic)
    context = get_complete_user_context(user_id, db)

    # Step 2: Analyze burnout
    integration = BurnoutSystemIntegration(db)
    analysis = integration.complete_daily_flow(
        user_id=user_id,
        quantitative_metrics=context['metrics'],
        qualitative_data=context['qualitative_data']
    )

    # Step 3: Generate event-specific recommendations
    engine = RecommendationEngine()
    recommendations = engine.generate_recommendations(
        burnout_analysis=analysis,
        user_profile_context=analysis['user_profile'],
        learned_patterns=analysis.get('learned_patterns'),
        calendar_events=context['meetings'],
        task_list=context['tasks']
    )

    return {
        "user_id": user_id,
        "burnout_score": analysis['burnout']['final_score'],
        "burnout_level": analysis['burnout']['level'],
        "recommendations": [
            {
                "title": rec.title,
                "description": rec.description,
                "action_steps": rec.action_steps,
                "priority": rec.priority
            }
            for rec in recommendations.recommendations
        ]
    }
```

---

## Examples

See the `examples/` folder for complete examples:

- `examples/complete_flow.py` - Full end-to-end example
- `examples/workload_analysis.py` - Workload analyzer example
- `examples/recommendations.py` - Recommendation generation example

---

## Setup Guide

### 1. Environment Setup

Create `.env` file:

```bash
# Main database (user profiles, burnout analyses)
DATABASE_URL=postgresql://postgres:password@localhost:5433/sentry_burnout_db

# Vector database (RAG strategies)
VECTOR_DB_URL=postgresql://postgres:password@localhost:5433/burnout_recommendations

# LLM configuration
OLLAMA_MODEL=llama3.1:8b
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=2048
```

### 2. Database Initialization

```bash
# Create databases
createdb sentry_burnout_db
createdb burnout_recommendations

# Enable PGVector extension
psql burnout_recommendations -c "CREATE EXTENSION vector;"

# Run initialization script
python scripts/init_database.py
```

### 3. Populate Vector Database

```bash
# Populate with evidence-based strategies
python scripts/populate_strategies.py
```

### 4. Install Ollama

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull model
ollama pull llama3.1:8b
```

### 5. Test the System

```python
from examples.complete_flow import run_example

run_example()
```

---

## File Structure

```
burn_out_service/
├── core/                          # Core analysis logic
│   ├── workload_analyzer.py
│   └── sentiment_analyzer.py
│
├── integrations/                  # External integrations
│   └── task_database_integration.py
│
├── user_profile/                  # User profile management
│   ├── models.py
│   ├── schemas.py
│   ├── service.py
│   └── integration_services.py
│
├── recommendations/               # Recommendation system
│   ├── rag_retrieval.py
│   ├── recommendation_generator.py
│   └── recommendation_engine.py
│
├── data/strategies/               # Evidence-based strategies
│
├── examples/                      # Usage examples
│
├── scripts/                       # Utility scripts
│
├── README.md                      # This file
└── config.py                      # Configuration
```

---

## Benefits

| Traditional Systems | Sentry AI |
|-------------------|-----------|
| ❌ "You have too many meetings" | ✅ "Cancel your 3:30 PM 'Team Sync' meeting - it's optional" |
| ❌ "Delegate some tasks" | ✅ "Delegate 'Database Migration Script' to Alex" |
| ❌ "Take breaks" | ✅ "Block 11:30 AM - 12:00 PM for a 30-minute walk" |
| ❌ Generic advice | ✅ Actionable, time-aware, event-specific |
| ❌ Manual data entry | ✅ Automatic metric calculation |
| ❌ One-size-fits-all | ✅ Personalized to role, preferences, constraints |

---

## Support

For questions or issues:
- Check `examples/` folder for usage examples
- Review this README for architecture details
- Contact: sentry-ai@example.com

---

**Sentry AI - Preventing burnout, one specific recommendation at a time.** 🎯
