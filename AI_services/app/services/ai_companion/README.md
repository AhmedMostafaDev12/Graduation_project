# AI Companion Service 🤖

A conversational AI assistant that provides emotional support, task management assistance, and burnout prevention guidance.

## Overview

The AI Companion is an intelligent chatbot that serves as a personal assistant for users of the Sentry AI platform. It combines emotional intelligence with practical task management capabilities.

**Port:** 8002

## Features

### 1. **Emotional Support** 💙
- Process diary entries and emotional check-ins
- Save emotional content to `qualitative_data` table
- Perform sentiment analysis using Ollama (Llama 3.1 8B)
- Extract emotional themes and patterns
- Provide empathetic, supportive responses

### 2. **Task Management** ✅
- Query task statistics (total, by status, by priority)
- Get summaries of upcoming and completed tasks
- Identify overdue tasks and tasks due this week
- Calculate task completion rates
- Create tasks from natural language descriptions

### 3. **Burnout Analysis** 📊
- Check current burnout status and score
- Get component breakdown (workload, emotional exhaustion, etc.)
- Receive personalized recommendations from RAG system
- Identify warning signals

### 4. **General Assistance** 💬
- Answer everyday questions
- Provide guidance and suggestions
- Maintain conversational context

### 5. **Multi-Modal Input** 🎤
- Text chat interface
- Audio input (transcribed via Vosk)
- Diary entry processing

## Architecture

### Components

```
ai_companion/
├── main.py                  # FastAPI application
├── companion_agent.py       # LangGraph agent workflow
├── companion_tools.py       # Tools for interacting with services
├── requirements.txt
├── start_companion.bat
└── README.md
```

### LangGraph Workflow

The companion uses a LangGraph state machine to process user messages:

```
User Message
    ↓
[Classify Intent] ─→ emotional_support → [Save to DB] → [Respond]
    │
    ├─→ task_query → [Get Task Stats] → [Respond]
    │
    ├─→ burnout_query → [Get Burnout Data] → [Respond]
    │
    ├─→ task_creation → [Create Task] → [Respond]
    │
    └─→ general_chat → [Respond]
```

### Intent Classification

The agent automatically classifies user messages into these categories:

1. **emotional_support** - User sharing feelings, emotions, diary entries
2. **task_query** - Asking about tasks, statistics, summaries
3. **burnout_query** - Asking about burnout status, recommendations
4. **task_creation** - Wants to create a new task
5. **general_chat** - Everyday conversation and questions

## API Endpoints

### 1. Chat (Text)

```http
POST /chat
Content-Type: application/json

{
  "message": "I'm feeling overwhelmed with work",
  "user_id": 1,
  "conversation_id": "optional-conv-id"
}
```

**Response:**
```json
{
  "response": "I understand feeling overwhelmed can be really challenging...",
  "conversation_id": "conv_1234567890.123",
  "sentiment": "negative",
  "action_taken": "emotional_support"
}
```

### 2. Chat (Audio)

```http
POST /chat/audio
Content-Type: multipart/form-data

audio: <audio file>
user_id: 1
conversation_id: optional-conv-id
```

Audio is transcribed using Vosk, then processed as text chat.

### 3. Diary Entry

```http
POST /diary
Content-Type: application/json

{
  "content": "Today was a tough day at work...",
  "user_id": 1,
  "entry_date": "2025-01-15T10:30:00Z"  # optional
}
```

**Response:**
```json
{
  "status": "success",
  "entry_saved": true,
  "sentiment": "negative",
  "themes": ["work_stress", "fatigue"],
  "companion_response": "Thank you for sharing...",
  "entry_id": 42
}
```

### 4. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ai-companion",
  "version": "1.0.0",
  "capabilities": [
    "emotional_support",
    "task_statistics",
    "burnout_analysis",
    "task_creation",
    "general_assistance"
  ]
}
```

## Tools

The companion agent has access to these tools:

### 1. `save_emotional_entry()`
- Saves emotional content to `qualitative_data` table
- Performs sentiment analysis via Ollama
- Extracts emotional themes

### 2. `get_task_statistics()`
- Queries backend for all user tasks
- Calculates statistics (total, by status, by priority, overdue, etc.)

### 3. `get_task_summary()`
- Gets upcoming tasks sorted by due date
- Gets recently completed tasks
- Gets high-priority tasks

### 4. `get_burnout_status()`
- Queries burnout service for current status
- Returns burnout score, level, component breakdown

### 5. `get_recent_recommendations()`
- Queries burnout service for personalized recommendations
- Returns strategies from RAG system

### 6. `create_task_from_text()`
- Uses task extraction service to parse natural language
- Creates tasks in backend database
- Returns created task details

## Example Conversations

### Emotional Support
**User:** "I'm feeling really stressed about my workload"

**Companion:** "I hear you, and it's completely valid to feel stressed when you have a lot on your plate. Managing workload can be challenging. Would you like me to show you your current task breakdown so we can see what's on your plate?"

*(Saves to qualitative_data with sentiment: "negative", themes: ["work_stress"])*

### Task Statistics
**User:** "How many tasks do I have?"

**Companion:** "You currently have 15 tasks total. Here's the breakdown: 8 are in progress, 5 are completed, and 2 are in your Todo list. You have 3 tasks due this week and 1 overdue task. Your completion rate is 33.3%."

### Task Creation
**User:** "Remind me to finish the report by Friday"

**Companion:** "I've created a task for you: 'Finish the report' with a due date of this Friday. The task has been added to your list with normal priority."

### Burnout Check
**User:** "Am I burning out?"

**Companion:** "Based on your recent activity, your burnout status is YELLOW with a score of 62/100. The main factors are workload intensity (high) and emotional exhaustion (moderate). I recommend taking breaks between tasks and considering delegating some work. Would you like to see specific recommendations?"

## Service Integration

The companion integrates with:

1. **Backend Service (Port 5000)**
   - Task CRUD operations
   - User authentication
   - Task statistics

2. **Burnout Service (Port 8000)**
   - Burnout analysis
   - Recommendations from RAG
   - Status monitoring

3. **Task Extraction Service (Port 8003)**
   - Natural language task parsing
   - Text extraction from files

4. **Database**
   - `qualitative_data` table for emotional entries
   - `tasks` table for task queries
   - `users` table for user data

## Setup

### Prerequisites

- Python 3.10+
- PostgreSQL database
- Ollama with `llama3.1:8b` model
- Backend, Burnout, and Task Extraction services running

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/sentry_ai
BACKEND_SERVICE_URL=http://localhost:5000
BURNOUT_SERVICE_URL=http://localhost:8000
EXTRACTION_SERVICE_URL=http://localhost:8003
```

3. Install Ollama and pull the model:
```bash
ollama pull llama3.1:8b
```

### Running the Service

**Windows:**
```bash
start_companion.bat
```

**Linux/Mac:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

The service will be available at `http://localhost:8002`

## Database Schema

### qualitative_data Table

```sql
CREATE TABLE qualitative_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entry_type VARCHAR(50),  -- 'diary_entry', 'conversation', 'feeling_check_in'
    content TEXT NOT NULL,
    sentiment_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Testing

### Manual Testing

1. **Health Check:**
```bash
curl http://localhost:8002/health
```

2. **Text Chat:**
```bash
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How many tasks do I have?",
    "user_id": 1
  }'
```

3. **Diary Entry:**
```bash
curl -X POST http://localhost:8002/diary \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Today was stressful but productive",
    "user_id": 1
  }'
```

## Troubleshooting

### Ollama Connection Issues

**Error:** `subprocess timeout` when calling Ollama

**Solution:**
1. Ensure Ollama is running: `ollama serve`
2. Pull the model: `ollama pull llama3.1:8b`
3. Test manually: `ollama run llama3.1:8b "Hello"`

### Service Connection Errors

**Error:** `Connection refused` to backend/burnout/extraction services

**Solution:**
1. Verify services are running on correct ports
2. Check `BACKEND_SERVICE_URL` and other URLs in `.env`
3. Test connectivity: `curl http://localhost:5000/health`

### Database Errors

**Error:** `table "qualitative_data" does not exist`

**Solution:**
1. Run database migrations (see `database_migration.sql`)
2. Verify `DATABASE_URL` is correct
3. Check database connection: `psql $DATABASE_URL -c "\dt"`

## Future Enhancements

### Planned Features

1. **Conversation History**
   - Store conversation messages in database
   - Allow users to review past conversations
   - Maintain context across sessions

2. **Voice Output**
   - Text-to-speech responses
   - Support for voice-only interactions

3. **Proactive Check-ins**
   - Scheduled well-being check-ins
   - Automatic burnout alerts
   - Task deadline reminders

4. **Enhanced Emotional Intelligence**
   - Multi-turn emotional conversations
   - Crisis detection and intervention
   - Mood tracking over time

5. **Personalization**
   - Learn user preferences
   - Adapt communication style
   - Custom response templates

## Technical Details

### LLM Configuration

**Model:** Llama 3.1 8B (via Ollama)
**Temperature:** Default (0.7)
**Max Tokens:** Default
**Timeout:** 30 seconds for responses

### Performance

- Average response time: 2-5 seconds (depends on Ollama)
- Concurrent requests: Handled by FastAPI async
- Database queries: < 100ms typically

### Security Considerations

- **TODO:** Add JWT authentication
- **TODO:** Rate limiting for chat endpoints
- **TODO:** Input sanitization for SQL injection prevention
- **TODO:** Content moderation for inappropriate messages

## Contributing

When adding new features:

1. Add new tools to `companion_tools.py`
2. Update the agent workflow in `companion_agent.py`
3. Add corresponding endpoints in `main.py`
4. Update this README with examples
5. Test thoroughly with different user intents

## License

Part of the Sentry AI platform.

---

**Service:** AI Companion
**Version:** 1.0.0
**Port:** 8002
**Status:** Production Ready ✅
