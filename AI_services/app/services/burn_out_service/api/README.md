# Sentry AI - Burnout Detection API

Complete REST API for the AI-powered burnout detection and prevention system.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `burn_out_service` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/sentry_burnout_db
VECTOR_DB_URL=postgresql://user:password@localhost:5432/sentry_vector_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

### 3. Start the API Server

```bash
# From the burn_out_service directory
cd backend/app/services/burn_out_service
python -m api.main
```

Or use uvicorn directly:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 📋 API Endpoints Overview

### **Burnout Analysis** (`/api/burnout`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analysis/{user_id}` | Get latest burnout analysis |
| GET | `/trend/{user_id}` | Get burnout trend over time |
| GET | `/breakdown/{user_id}` | Get component breakdown |
| GET | `/insights/{user_id}` | Get primary issues and insights |
| GET | `/signals/{user_id}` | Get burnout warning signals |
| GET | `/recovery-plan/{user_id}` | Get structured recovery plan |
| GET | `/history/{user_id}` | Get historical analyses |

### **Workload & Data** (`/api`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workload/submit` | Submit workload metrics |
| POST | `/sentiment/submit` | Submit qualitative data |
| POST | `/burnout/analyze` | Trigger complete analysis |
| GET | `/workload/breakdown/{user_id}` | Get workload breakdown |

### **Recommendations** (`/api/recommendations`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{user_id}` | Get AI recommendations |
| POST | `/{recommendation_id}/feedback` | Submit feedback |

### **User Profile** (`/api/profile`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{user_id}` | Get user profile |
| PUT | `/{user_id}` | Update user profile |
| POST | `/{user_id}/learn-patterns` | Trigger pattern learning |

### **Integrations** (`/api/integrations`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks/sync` | Sync tasks from Jira/Asana |
| POST | `/calendar/sync` | Sync calendar events |
| POST | `/slack/messages` | Sync Slack messages |

### **Health Checks** (`/api/health`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Overall system health |
| GET | `/databases` | Database connectivity |
| GET | `/llm` | LLM service status |

---

## 🔄 Typical Workflow

### **Daily Analysis Flow**

```python
import requests

BASE_URL = "http://localhost:8000"
user_id = 123

# Step 1: Submit workload metrics
workload_data = {
    "user_id": user_id,
    "total_active_tasks": 15,
    "overdue_tasks": 5,
    "tasks_due_this_week": 10,
    "completion_rate": 0.75,
    "work_hours_today": 9.5,
    "work_hours_this_week": 48.0,
    "meetings_today": 6,
    "total_meeting_hours_today": 4.0,
    "back_to_back_meetings": 3,
    "weekend_work_sessions": 1,
    "late_night_sessions": 2,
    "consecutive_work_days": 12
}

response = requests.post(f"{BASE_URL}/api/workload/submit", json=workload_data)
print(response.json())

# Step 2: Submit qualitative data
qualitative_data = {
    "user_id": user_id,
    "meeting_transcripts": [
        "Feeling overwhelmed with the Q4 deadline",
        "Team is working late to meet sprint goals"
    ],
    "task_notes": [
        "This refactoring is taking longer than expected",
        "Blocked by dependencies from other teams"
    ],
    "user_check_ins": [
        "Feeling tired today, worked late last night"
    ]
}

response = requests.post(f"{BASE_URL}/api/sentiment/submit", json=qualitative_data)
print(response.json())

# Step 3: Trigger analysis
analyze_data = {
    "user_id": user_id,
    "quantitative_metrics": workload_data,
    "qualitative_data": qualitative_data,
    "store_history": True
}

response = requests.post(f"{BASE_URL}/api/burnout/analyze", json=analyze_data)
analysis = response.json()
print(f"Burnout Score: {analysis['analysis']['burnout']['final_score']}")

# Step 4: Get recommendations
response = requests.get(f"{BASE_URL}/api/recommendations/{user_id}")
recommendations = response.json()
print(f"Generated {len(recommendations['recommendations'])} recommendations")
```

---

## 📊 Response Examples

### Burnout Analysis Response

```json
{
  "user_id": 123,
  "analyzed_at": "2025-12-18T10:30:00Z",
  "final_score": 72.5,
  "level": "HIGH",
  "status_message": "High burnout detected - immediate action recommended",
  "components": {
    "workload_score": 75.0,
    "sentiment_adjustment": -5.0,
    "workload_contribution": 85.0,
    "sentiment_contribution": 15.0
  },
  "trend": {
    "direction": "rising",
    "change_percentage": 15.3,
    "change_points": 10.2,
    "days_at_current_level": 3
  }
}
```

### Recommendation Response

```json
{
  "user_id": 123,
  "generated_at": "2025-12-18T10:35:00Z",
  "burnout_level": "HIGH",
  "recommendations": [
    {
      "title": "Delegate Non-Critical Tasks",
      "priority": "HIGH",
      "description": "Review your current task list and identify items that can be delegated",
      "action_steps": [
        "List all active tasks with delegation potential",
        "Identify team members with capacity",
        "Schedule delegation conversations this week"
      ],
      "expected_impact": "Reduce workload by 20-30% within 1 week"
    }
  ],
  "metadata": {
    "strategies_retrieved": 5,
    "llm_model": "llama3.1:8b",
    "generation_time_seconds": 12.45
  }
}
```

---

## 🔌 Integration Examples

### Jira Webhook Integration

```python
# Jira webhook handler (your backend)
@app.post("/jira/webhook")
async def jira_webhook(payload: dict):
    # Extract user and task data from Jira payload
    user_email = payload["issue"]["fields"]["assignee"]["emailAddress"]
    user_id = get_user_id_from_email(user_email)

    # Fetch all user's tasks from Jira
    tasks = get_jira_tasks(user_email)

    # Sync to burnout API
    sync_payload = {
        "user_id": user_id,
        "tasks": tasks,
        "source": "jira",
        "synced_at": datetime.utcnow().isoformat()
    }

    requests.post(
        "http://localhost:8000/api/integrations/tasks/sync",
        json=sync_payload
    )
```

### Google Calendar Integration

```python
# Sync calendar events
from google.oauth2 import service_account
from googleapiclient.discovery import build

def sync_calendar_to_burnout_api(user_id, calendar_id):
    # Get events from Google Calendar
    service = build('calendar', 'v3', credentials=creds)
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=datetime.utcnow().isoformat() + 'Z',
        maxResults=50
    ).execute()

    events = events_result.get('items', [])

    # Convert to burnout API format
    sync_payload = {
        "user_id": user_id,
        "events": [
            {
                "id": event['id'],
                "title": event['summary'],
                "start_time": event['start']['dateTime'],
                "end_time": event['end']['dateTime'],
                "attendees": [a['email'] for a in event.get('attendees', [])],
                "is_recurring": 'recurrence' in event,
                "is_optional": False
            }
            for event in events
        ],
        "source": "google_calendar",
        "synced_at": datetime.utcnow().isoformat()
    }

    requests.post(
        "http://localhost:8000/api/integrations/calendar/sync",
        json=sync_payload
    )
```

---

## 🎨 Frontend Integration

### React Example

```javascript
// API client
const API_BASE_URL = 'http://localhost:8000';

// Fetch burnout analysis
async function getBurnoutAnalysis(userId) {
  const response = await fetch(`${API_BASE_URL}/api/burnout/analysis/${userId}`);
  const data = await response.json();
  return data;
}

// Fetch trend data
async function getBurnoutTrend(userId, period = '30days') {
  const response = await fetch(
    `${API_BASE_URL}/api/burnout/trend/${userId}?period=${period}`
  );
  const data = await response.json();
  return data;
}

// Display burnout score
function BurnoutScore({ userId }) {
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    getBurnoutAnalysis(userId).then(setAnalysis);
  }, [userId]);

  if (!analysis) return <div>Loading...</div>;

  return (
    <div>
      <h2>Burnout Score: {analysis.final_score}/100</h2>
      <p>Level: {analysis.level}</p>
      <p>Trend: {analysis.trend?.direction} ({analysis.trend?.change_percentage}%)</p>
    </div>
  );
}
```

---

## 🛠️ Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/api/health

# Get burnout analysis
curl http://localhost:8000/api/burnout/analysis/123

# Submit workload data
curl -X POST http://localhost:8000/api/workload/submit \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "total_active_tasks": 15,
    "overdue_tasks": 5,
    "work_hours_today": 9.5,
    "meetings_today": 6,
    "completion_rate": 0.75
  }'
```

### Using Postman

Import the OpenAPI spec from `http://localhost:8000/openapi.json` into Postman for a complete collection of API requests.

---

## 🔒 Security Considerations

### TODO: Authentication

Currently, the API does not implement authentication. For production:

1. **Add JWT Authentication**
2. **Implement API Key validation**
3. **Add rate limiting**
4. **Enable HTTPS**
5. **Add request validation**

### Environment Variables

Never commit `.env` files. Use environment-specific configuration:

- `.env.development`
- `.env.staging`
- `.env.production`

---

## 📈 Performance

### Expected Response Times

| Endpoint | Average Response Time |
|----------|----------------------|
| GET /burnout/analysis | 50-100ms |
| GET /recommendations | 10-30s (LLM generation) |
| POST /burnout/analyze | 2-5s (complete analysis) |
| POST /workload/submit | 10-50ms |

### Optimization Tips

1. **Cache recommendations** for 1 hour per user
2. **Use background tasks** for long-running operations
3. **Batch analysis** for multiple users
4. **Implement pagination** for history endpoints

---

## 🐛 Troubleshooting

### Database Connection Errors

```bash
# Check database is running
psql -h localhost -U user -d sentry_burnout_db

# Verify connection string in .env
echo $DATABASE_URL
```

### LLM Service Unavailable

```bash
# Check Ollama is running
ollama list

# Start Ollama
ollama serve

# Pull model if needed
ollama pull llama3.1:8b
```

### Import Errors

```bash
# Ensure you're in the correct directory
cd backend/app/services/burn_out_service

# Run with Python module syntax
python -m api.main
```

---

## 📝 Development

### Running in Development Mode

```bash
# Enable auto-reload
export API_RELOAD=true
python -m api.main
```

### Adding New Endpoints

1. Create route in appropriate router file (e.g., `api/routers/burnout.py`)
2. Add Pydantic models to `api/schemas/`
3. Import and include router in `api/main.py`
4. Test with `/docs` interactive UI

---

## 📚 Additional Resources

- **System Architecture**: See `SYSTEM_OVERVIEW.md`
- **Database Schema**: See `BACKEND_TEAM_DATABASE_SCHEMA.md`
- **Integration Guide**: See `recommendations_RAG/INTEGRATION_GUIDE.md`

---

## 🤝 Contributing

When adding new endpoints:

1. Follow REST conventions
2. Use appropriate HTTP methods (GET, POST, PUT, DELETE)
3. Add comprehensive docstrings
4. Include request/response examples
5. Add error handling
6. Update this README

---

## 📄 License

Copyright © 2025 Sentry AI Team
