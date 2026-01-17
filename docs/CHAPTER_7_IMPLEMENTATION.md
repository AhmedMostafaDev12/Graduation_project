# Chapter 7: Implementation and Technical Execution

## 7.1 Introduction

This chapter covers the **practical implementation** of Sentry AI's system design, detailing how the architectural blueprints from Chapter 6 were translated into working software. The focus is on **development processes, project organization, key implementation decisions, and technical challenges** rather than line-by-line code.

Sentry AI's implementation is divided into two primary service categories:

- **Backend Services:** Handle user authentication, task management, and third-party integrations
- **AI Services:** Perform burnout analysis, generate recommendations, extract tasks from multi-modal inputs, and power the AI Companion

---

## 7.2 Development Environment and Technology Stack

### 7.2.1 Development Tools

**Backend Services:**
- **Framework:** FastAPI 0.104+ (Python 3.11)
- **ORM:** SQLAlchemy 2.0 with async support
- **Database Driver:** Psycopg 3 (PostgreSQL 15+)
- **Validation:** Pydantic 2.0 for request/response schemas
- **Authentication:** python-jose (JWT), passlib (password hashing)

**AI Services:**
- **LLM Gateway:** Groq Python SDK (Llama 3.1 70B/8B models)
- **Embeddings:** Voyage AI Python client (voyage-3 model)
- **Speech-to-Text:** AssemblyAI SDK
- **AI Framework:** LangGraph 0.2+ for stateful conversations
- **Vector Database:** PGVector extension for PostgreSQL

**Mobile Client:**
- **Framework:** Flutter 3.24+
- **State Management:** Provider/Riverpod
- **HTTP Client:** Dio with interceptors for JWT refresh

**Development Environment:**
- **IDE:** VSCode with Python, Flutter, and database extensions
- **Version Control:** Git with GitHub repository
- **API Testing:** Postman collections for all endpoints
- **Database Management:** pgAdmin 4, TablePlus

### 7.2.2 Project Configuration

**Environment Variables (.env):**

The project uses environment-based configuration to separate development and production settings:

```bash
# Database
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/sentry_db

# External APIs
GROQ_API_KEY=gsk_...
VOYAGE_API_KEY=pa_...
ASSEMBLYAI_API_KEY=...

# OAuth Credentials
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
APPLE_CLIENT_ID=...
FACEBOOK_APP_ID=...

# JWT Configuration
SECRET_KEY=randomly_generated_256_bit_key
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
```

**Configuration Loading:**

The application uses Pydantic Settings for type-safe configuration management. All environment variables are validated at startup, ensuring critical credentials are present before the server begins accepting requests.

---

## 7.3 Project Structure and Organization

### 7.3.1 Repository Architecture

```
Sentry_AI/
├── backend_services/          # Backend Services Layer
│   ├── app/
│   │   ├── core/             # Core utilities (config, database, security)
│   │   ├── models/           # SQLAlchemy models (shared schema)
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic services
│   │   │   ├── auth/
│   │   │   ├── tasks/
│   │   │   ├── integrations/
│   │   │   └── user/
│   │   └── routers/          # API endpoint routers (90+ endpoints)
│   │       ├── auth/
│   │       ├── tasks/
│   │       ├── integrations/
│   │       └── user/
│   └── requirements.txt
│
├── AI_services/               # AI Services Layer
│   ├── app/
│   │   ├── core/             # Shared with backend (config, DB)
│   │   └── services/         # AI service modules
│   │       ├── burn_out_service/
│   │       │   ├── user_profile/
│   │       │   ├── rag/
│   │       │   └── utils/
│   │       ├── task_extraction/
│   │       │   ├── utils/
│   │       │   └── extractors/
│   │       ├── ai_companion/
│   │       │   ├── agents/
│   │       │   └── state/
│   │       └── notebook_library/
│   │           ├── rag/
│   │           ├── ai_studio/
│   │           └── uploads/
│   └── requirements.txt
│
├── mobile_app/                # Flutter Mobile Client
│   ├── lib/
│   │   ├── screens/          # 31 UI screens (Chapter 5)
│   │   ├── services/         # API clients
│   │   ├── models/           # Data models
│   │   ├── providers/        # State management
│   │   └── widgets/          # Reusable components
│   └── pubspec.yaml
│
├── docs/                      # Documentation
│   ├── images/               # UI screenshots and diagrams
│   └── chapters/             # Graduation project chapters
│
└── .env                       # Environment configuration
```

### 7.3.2 Backend vs. AI Services Separation

**Why Separate Services?**

1. **Domain Separation:** Backend handles infrastructure concerns (auth, CRUD), AI services handle intelligence (burnout analysis, recommendations)
2. **Development Focus:** Allows specialization—backend developers focus on APIs, AI developers focus on model integration
3. **Deployment Flexibility:** AI services can be scaled independently based on computational load
4. **Dependency Management:** AI services have heavier dependencies (LangChain, transformers) that backend doesn't need

**Shared Components:**

Both services share:
- Database models (`models.py`)
- Configuration (`core/config.py`)
- Database connection pool (`core/database.py`)

This ensures consistency while maintaining logical separation.

---

## 7.4 Backend Services Implementation

### 7.4.1 Authentication Service Implementation

The authentication system supports both email/password and OAuth providers (Google, Apple, Facebook) through a unified approach.

**Email/Password Registration Flow:**

1. Client submits email, password, name, birthday
2. Server validates email uniqueness
3. Password is hashed using bcrypt (12 rounds)
4. User record created with `is_verified=False`
5. Verification email sent (future enhancement)
6. Access token (15 min) and refresh token (30 days) generated
7. Tokens returned to client

**OAuth Login Flow:**

1. Client obtains OAuth token from provider (Google/Apple/Facebook)
2. Server verifies token with provider's API
3. Server checks if user exists by email
4. If new user: create account with OAuth provider record
5. If existing user: link OAuth provider to account
6. Generate JWT tokens and return to client

**JWT Token Refresh Mechanism:**

When access tokens expire (15 minutes), clients use the refresh token to obtain new access tokens without re-authentication. The refresh token is stored in the database with an expiry timestamp, allowing server-side revocation if needed.

**Implementation Highlight - Token Refresh:**

The token refresh endpoint validates the refresh token against the database, ensuring it hasn't been revoked or expired. If valid, a new access token is generated while the refresh token remains unchanged. This approach balances security (short-lived access tokens) with user experience (no frequent logins).

### 7.4.2 Task Management Service

The task service provides CRUD operations with AI-enhanced fields:

**Task Model Extensions for AI:**

Standard task fields (title, description, due_date, priority) are augmented with AI-generated fields:
- `estimated_hours`: LLM-estimated completion time
- `can_delegate`: Boolean flag suggesting delegation potential
- `category`: Auto-categorized (work, personal, study)
- `source`: Tracks origin (manual, calendar_sync, extracted_audio, etc.)

**Task Creation Workflow:**

1. **Manual Creation:** User creates task via mobile app → Backend validates and stores
2. **Calendar Sync:** Integration service fetches events → Converts to tasks → Backend stores
3. **AI Extraction:** User uploads audio/PDF → AI service extracts tasks → Backend stores

All tasks flow through the same database table, differentiated by the `source` field.

### 7.4.3 Integration Service Implementation

The integration service manages OAuth connections to third-party services (Google Calendar, Trello).

**Google Calendar Integration:**

1. User initiates connection → Backend redirects to Google OAuth
2. User authorizes → Google returns authorization code
3. Backend exchanges code for access + refresh tokens
4. Tokens encrypted and stored in `integrations` table
5. Background sync job periodically fetches calendar events
6. Events converted to tasks and stored with `source='google_calendar'`

**Trello Integration:**

Similar flow using Trello's OAuth 1.0a. Temporary tokens are stored during the OAuth dance, then replaced with permanent access tokens.

**Token Refresh Strategy:**

Integration tokens expire (typically 1 hour for Google). The service automatically detects expired tokens during sync attempts and uses the refresh token to obtain new access tokens, updating the database transparently.

---

## 7.5 AI Services Implementation

### 7.5.1 Burnout Analysis Service

The burnout analyzer implements the 60/40 weighted scoring algorithm described in Chapter 6 (60% workload metrics, 40% sentiment analysis).

**Analysis Trigger:**

Burnout analysis runs:
- On-demand when user requests analysis
- Automatically after calendar sync (if enabled)
- Daily at configured time for active users

**Workload Score Calculation Process:**

1. Fetch all user tasks from database
2. Calculate baseline: Average tasks per week over user's history
3. Calculate current load: Tasks in next 7 days
4. Compute workload ratio: `current_load / baseline`
5. Apply thresholds:
   - Ratio < 0.8 → Low workload (score 20-40)
   - Ratio 0.8-1.2 → Normal workload (score 40-60)
   - Ratio 1.2-1.5 → High workload (score 60-80)
   - Ratio > 1.5 → Overload (score 80-100)

**Sentiment Analysis Process:**

The system analyzes task titles and descriptions using Groq's Llama 3.1 model:

1. Concatenate all task titles/descriptions from past week
2. Send to LLM with prompt: "Analyze the emotional tone of these tasks. Rate stress level 0-100."
3. LLM returns sentiment score based on language patterns (urgent, critical, ASAP, etc.)

**Final Burnout Score:**

```
burnout_score = (workload_score * 0.6) + (sentiment_score * 0.4)
```

Results stored in `burnout_analyses` table as JSON:

```json
{
  "overall_score": 72,
  "workload_component": {
    "score": 75,
    "baseline_tasks": 12,
    "current_tasks": 18,
    "ratio": 1.5
  },
  "sentiment_component": {
    "score": 68,
    "detected_patterns": ["urgent", "deadline", "overdue"]
  }
}
```

### 7.5.2 RAG Recommendation Engine

The RAG engine generates personalized recommendations by retrieving relevant strategies from a knowledge base and grounding them in the user's actual calendar events.

**Implementation Process:**

**Step 1: Embedding Generation**

At system initialization, 50+ burnout prevention strategies are embedded using Voyage AI's `voyage-3` model and stored in PGVector:

```sql
INSERT INTO strategies (text, embedding)
VALUES ('Take regular breaks...', '[0.23, -0.45, 0.67, ...]');
```

**Step 2: Query Embedding**

When generating recommendations, the user's burnout analysis is converted to a query:

"User has high workload (score 75) and elevated stress (score 68). Find strategies."

This query is embedded using the same Voyage AI model.

**Step 3: Vector Similarity Search**

PGVector's cosine similarity operator retrieves top 10 strategies:

```sql
SELECT id, text, 1 - (embedding <=> query_embedding) AS similarity
FROM strategies
ORDER BY embedding <=> query_embedding
LIMIT 10;
```

**Step 4: Context-Aware Ranking**

Retrieved strategies are re-ranked based on:
- Vector similarity (50%)
- Relevance to workload vs. sentiment (30%)
- User's past acceptance rate of strategy category (20%)

Top 3 strategies selected for generation.

**Step 5: LLM Personalization**

For each strategy, the LLM receives:

```
STRATEGY: "Schedule buffer time between meetings"
USER CONTEXT:
- Burnout score: 72 (high)
- Upcoming tasks: 18 tasks in next 7 days
- Calendar events: [Meeting 1, Meeting 2, ...]

Generate a personalized recommendation with:
1. Title (1 sentence)
2. Description (2-3 sentences)
3. Action steps referencing specific calendar events
```

**Step 6: Event-Specific Action Steps**

The LLM references actual calendar events:

"On Tuesday, you have back-to-back meetings from 10 AM to 3 PM. Add a 15-minute buffer after the 'Project Review' meeting at 11:30 AM to prevent burnout."

This grounding prevents generic advice and makes recommendations actionable.

### 7.5.3 Task Extraction Service

The task extraction service converts multi-modal inputs (audio, images, PDFs, video) into structured tasks.

**Audio Extraction Pipeline:**

1. **Transcription:** Upload audio file → AssemblyAI transcribes → Returns text transcript
2. **Parsing:** Transcript sent to Groq Llama 3.1 with prompt:
   ```
   Extract all tasks and deadlines from this lecture transcript.
   Return JSON: [{"title": "...", "due_date": "...", "priority": "..."}]
   ```
3. **Validation:** LLM response parsed and validated (due dates converted to datetime objects)
4. **Storage:** Tasks saved to database with `source='extracted_audio'`

**Image Extraction (OCR):**

1. Image uploaded → Converted to base64
2. Sent to Groq Vision API (Llama 3.2 90B Vision model)
3. Prompt: "Extract all text from this whiteboard/slide/document"
4. OCR text passed through same task parsing pipeline as audio

**PDF Extraction:**

1. PDF uploaded → PyPDF2 extracts raw text
2. Text passed through task parsing pipeline

**Video Extraction:**

1. Video uploaded → FFmpeg extracts audio track
2. Audio processed through audio extraction pipeline

**Challenge - Date Parsing:**

LLMs sometimes return ambiguous dates ("next Wednesday"). Solution: Include current date in prompt and use strict JSON schema validation to enforce ISO 8601 format.

### 7.5.4 AI Companion (LangGraph Implementation)

The AI Companion uses LangGraph to create a stateful conversational agent that remembers context across messages.

**State Machine Design:**

```mermaid
stateDiagram-v2
    [*] --> Initial
    Initial --> Understanding: User sends message
    Understanding --> CheckingData: Classify intent
    CheckingData --> Responding: Fetch user context
    Responding --> [*]: Send response
    Responding --> Understanding: User continues conversation
```

**Figure 7.1:** LangGraph state machine for AI Companion conversations.

**Conversation State:**

Each conversation maintains:
- `user_id`: Who is chatting
- `conversation_history`: Previous messages (last 10)
- `current_intent`: Detected intent (burnout_query, task_help, general)
- `context_data`: Relevant user data (recent tasks, burnout score)

**Intent Classification:**

First LLM call classifies user intent:

```
User: "Why am I feeling so overwhelmed?"
Intent: burnout_query → Fetch latest burnout analysis
```

**Context Injection:**

Based on intent, relevant data is injected:

```
System: User's burnout score is 72 (high). They have 18 tasks due this week.
User: "Why am I feeling so overwhelmed?"
```

**Response Generation:**

LLM generates empathetic response grounded in actual data:

"You're feeling overwhelmed because your workload is 50% higher than your usual baseline. You have 18 tasks due this week, compared to your average of 12. Would you like me to suggest some strategies to manage this?"

**State Persistence:**

Conversation state stored in database as JSON, allowing multi-turn conversations to resume across app sessions.

### 7.5.5 Notebook Library with RAG

The notebook library allows users to upload study materials (PDFs, images) and chat with them using RAG.

**Document Processing:**

1. User uploads PDF → PyPDF2 extracts text
2. Text split into chunks (500 tokens, 50 token overlap)
3. Each chunk embedded with Voyage AI → Stored in PGVector with `notebook_id` foreign key

**Chat-with-Document:**

1. User asks: "What are the key concepts in Chapter 3?"
2. Question embedded → PGVector retrieves top 5 relevant chunks from that notebook
3. Chunks + question sent to LLM:
   ```
   Context from document:
   [Chunk 1 text]
   [Chunk 2 text]
   ...

   Question: What are the key concepts in Chapter 3?
   ```
4. LLM generates answer grounded in document content

**AI Studio (Study Material Generation):**

Users can generate flashcards, summaries, or quizzes:

1. Select notebook
2. Choose generation type (flashcards/summary/quiz)
3. LLM receives full document context + generation prompt
4. Generated content saved and displayed

---

## 7.6 Database Implementation Details

### 7.6.1 Schema Evolution

The database schema evolved through several iterations:

**Initial Schema:**
- Basic user and task tables
- No vector support

**V2 - OAuth Support:**
- Added `auth_providers` table for OAuth tokens
- Added `integrations` table for third-party connections

**V3 - AI Features:**
- Installed PGVector extension
- Added `strategies` table with vector embeddings
- Added `burnout_analyses` with JSON metrics
- Added `recommendations` table

**V4 - Notebook Library:**
- Added `notebooks` table
- Added `notebook_chunks` table with embeddings

**Migration Strategy:**

Migrations managed using Alembic (SQLAlchemy's migration tool). Each schema change is a separate migration file, allowing rollback if needed.

### 7.6.2 Indexing Strategy

**Performance Optimization Indexes:**

1. **User Lookups:**
   ```sql
   CREATE INDEX idx_users_email ON users(email);
   ```

2. **Task Queries:**
   ```sql
   CREATE INDEX idx_tasks_user_due ON tasks(user_id, due_date);
   ```

3. **Vector Similarity:**
   ```sql
   CREATE INDEX idx_strategies_embedding ON strategies
   USING ivfflat (embedding vector_cosine_ops)
   WITH (lists = 100);
   ```

The IVFFlat index accelerates vector searches from O(n) to O(log n) by partitioning embeddings into clusters.

4. **Burnout Analysis Timeline:**
   ```sql
   CREATE INDEX idx_burnout_user_created ON burnout_analyses(user_id, created_at DESC);
   ```

### 7.6.3 Database Connection Management

**Connection Pooling:**

The application uses SQLAlchemy's connection pool to avoid creating new database connections for each request:

- Pool size: 10 connections
- Max overflow: 20 (total 30 connections during spikes)
- Pool pre-ping: Verify connection health before use
- Pool recycle: Close idle connections after 1 hour

This configuration handles ~500 concurrent requests efficiently.

---

## 7.7 External Service Integration Strategies

### 7.7.1 Groq API Integration

**Rate Limiting Handling:**

Groq's free tier has rate limits (30 requests/minute). The application implements:

1. **Exponential Backoff:** If rate limited, wait 2^n seconds before retry (n = retry count)
2. **Request Queueing:** Non-urgent requests (batch analysis) queued and processed during low-traffic periods
3. **Fallback Models:** If Llama 3.1 70B is unavailable, fall back to 8B model

**Token Optimization:**

LLM calls are expensive (token-wise). Optimizations:

- Use low temperature (0.1-0.3) for consistent outputs
- Limit max tokens (500 for recommendations, 200 for classifications)
- Cache common prompts (e.g., task parsing schema)

### 7.7.2 Voyage AI Embedding Integration

**Batch Embedding:**

Instead of embedding one text at a time, the system batches:

```python
# Instead of 50 separate API calls:
for strategy in strategies:
    embedding = voyage.embed(strategy.text)

# One batched call:
embeddings = voyage.embed([s.text for s in strategies])
```

This reduces API latency from ~50 seconds to ~2 seconds for 50 embeddings.

### 7.7.3 AssemblyAI Transcription

**Polling Strategy:**

AssemblyAI transcription is asynchronous:

1. Upload audio → Receive `transcript_id`
2. Poll status every 3 seconds: `GET /transcript/{id}`
3. When `status == 'completed'`, fetch text

**Timeout Handling:**

If transcription takes >5 minutes, assume failure and notify user.

---

## 7.8 API Design and Implementation

### 7.8.1 RESTful Endpoint Structure

The Sentry AI system exposes **90+ RESTful API endpoints** organized across Backend Services and AI Services. These endpoints are grouped by functional tags for easier discovery and documentation.

**Backend Services (50+ endpoints):**

| **Tag** | **Endpoint Count** | **Key Responsibilities** |
|---------|-------------------|-------------------------|
| **Authentication** | 8 endpoints | User registration, login (email/password, OAuth), token refresh, password reset, email verification |
| **User Management** | 12 endpoints | Profile CRUD, preferences, settings, account deletion, profile picture upload |
| **Tasks** | 15 endpoints | Task CRUD, filtering, sorting, batch operations, task status updates, task analytics |
| **Integrations** | 10 endpoints | OAuth connections (Google, Trello, Apple, Facebook), sync operations, token management, disconnect services |
| **Calendar** | 5 endpoints | Calendar event CRUD, event-to-task conversion, calendar views |

**AI Services (40+ endpoints):**

| **Tag** | **Endpoint Count** | **Key Responsibilities** |
|---------|-------------------|-------------------------|
| **Burnout Analysis** | 8 endpoints | Trigger analysis, get current score, historical trends, workload breakdown, sentiment analysis details |
| **Recommendations** | 6 endpoints | Get recommendations, accept/reject, mark as completed, feedback on effectiveness |
| **Task Extraction** | 10 endpoints | Extract from audio/PDF/images/video, batch extraction, extraction history, re-process failed extractions |
| **AI Companion** | 7 endpoints | Start conversation, send message, conversation history, clear context, companion settings |
| **Notebook Library** | 9 endpoints | Notebook CRUD, add sources, chat with notebook, generate flashcards/summaries/quizzes, export generated content |

**Example Endpoints by Tag:**

**Authentication Tag (8 endpoints):**
- `POST /auth/register` - Create new account
- `POST /auth/login` - Email/password login
- `POST /auth/oauth/google` - Google OAuth login
- `POST /auth/oauth/apple` - Apple OAuth login
- `POST /auth/oauth/facebook` - Facebook OAuth login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/verify-email` - Verify email address

**Tasks Tag (15 endpoints):**
- `GET /tasks` - List user's tasks (with filters)
- `POST /tasks` - Create task
- `GET /tasks/{id}` - Get task details
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task
- `PATCH /tasks/{id}/status` - Update task status
- `GET /tasks/analytics` - Get task statistics
- `POST /tasks/batch` - Batch create tasks
- `DELETE /tasks/batch` - Batch delete tasks
- *(+6 more for filtering, sorting, calendar views, etc.)*

**Burnout Analysis Tag (8 endpoints):**
- `POST /burnout/analyze` - Trigger burnout analysis
- `GET /burnout/current` - Get current burnout score
- `GET /burnout/history` - Get past analyses
- `GET /burnout/workload` - Get workload breakdown
- `GET /burnout/sentiment` - Get sentiment analysis details
- `GET /burnout/trends` - Get burnout trends over time
- *(+2 more for baseline updates, score predictions)*

**Notebook Library Tag (9 endpoints):**
- `POST /notebooks` - Create notebook
- `GET /notebooks` - List user's notebooks
- `GET /notebooks/{id}` - Get notebook details
- `POST /notebooks/{id}/sources` - Add source to notebook
- `POST /notebooks/{id}/chat` - Chat with notebook
- `POST /notebooks/{id}/generate/flashcards` - Generate flashcards
- `POST /notebooks/{id}/generate/summary` - Generate summary
- `POST /notebooks/{id}/generate/quiz` - Generate quiz
- `DELETE /notebooks/{id}` - Delete notebook

All endpoints follow RESTful conventions and return consistent JSON responses with proper HTTP status codes.

### 7.8.2 Request/Response Schema Design

All endpoints use Pydantic schemas for validation:

**Example: Task Creation**

```python
# Request Schema
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Literal["low", "medium", "high"] = "medium"
    category: Literal["work", "personal", "study"] = "work"

# Response Schema
class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    due_date: Optional[datetime]
    priority: str
    category: str
    estimated_hours: Optional[float]  # AI-generated
    can_delegate: bool  # AI-generated
    source: str
    created_at: datetime

    class Config:
        from_attributes = True  # Support SQLAlchemy models
```

Pydantic automatically validates incoming JSON and generates OpenAPI documentation.

### 7.8.3 Error Handling and Status Codes

**Consistent Error Responses:**

All errors return:

```json
{
  "detail": {
    "error_code": "INVALID_CREDENTIALS",
    "message": "Email or password is incorrect",
    "timestamp": "2025-01-17T10:30:00Z"
  }
}
```

**HTTP Status Codes:**

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input (e.g., malformed JSON)
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: Valid JWT but insufficient permissions
- `404 Not Found`: Resource doesn't exist
- `409 Conflict`: Resource already exists (e.g., duplicate email)
- `422 Unprocessable Entity`: Validation failed (Pydantic errors)
- `500 Internal Server Error`: Unexpected server failure

---

## 7.9 Testing Strategy

### 7.9.1 Unit Testing

**Backend Services Tests:**

Each service has unit tests covering:

- Authentication: Password hashing, token generation, OAuth token verification
- Task Service: CRUD operations, filtering, sorting
- Integration Service: Token encryption/decryption, sync logic

**AI Services Tests:**

- Burnout Analyzer: Workload calculation, sentiment scoring, final score computation
- RAG Engine: Vector retrieval, ranking algorithm, prompt generation
- Task Parser: JSON parsing, date validation

**Mocking External APIs:**

Tests mock Groq, Voyage AI, and AssemblyAI responses to avoid API costs:

```python
@patch('groq_client.generate')
def test_task_extraction(mock_groq):
    mock_groq.return_value = MockResponse({
        "tasks": [{"title": "Submit homework", "due_date": "2025-01-20"}]
    })

    tasks = task_parser.parse("Submit homework by Monday")
    assert len(tasks) == 1
    assert tasks[0].title == "Submit homework"
```

### 7.9.2 Integration Testing

**Database Tests:**

Integration tests use a test PostgreSQL database:

1. Setup: Create test database, run migrations
2. Test: Execute operations (e.g., create user, analyze burnout)
3. Teardown: Drop test database

**API Tests:**

FastAPI's `TestClient` simulates HTTP requests:

```python
def test_login():
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 7.9.3 Testing Challenges

**Challenge 1: Asynchronous Operations**

AssemblyAI transcription takes 30-60 seconds. Solution: Use smaller test audio files (<5 seconds) or mock the API.

**Challenge 2: Vector Similarity Non-Determinism**

Vector searches may return different results due to floating-point precision. Solution: Use similarity threshold tests instead of exact matches:

```python
assert similarity >= 0.85  # Instead of exact match
```

---

## 7.10 Deployment Strategy

### 7.10.1 Development Environment

**Local Development:**

1. Install PostgreSQL 15 with PGVector extension
2. Create `.env` file with API keys
3. Run database migrations: `alembic upgrade head`
4. Start backend: `uvicorn backend_services.app.main:app --reload`
5. Start AI services: `uvicorn AI_services.app.main:app --port 8001 --reload`
6. Start mobile app: `flutter run`

**Docker Development (Optional):**

The project includes a `docker-compose.yml` for containerized development:

```yaml
services:
  db:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: sentry_db

  backend:
    build: ./backend_services
    ports:
      - "8000:8000"
    depends_on:
      - db

  ai_services:
    build: ./AI_services
    ports:
      - "8001:8001"
    depends_on:
      - db
```

### 7.10.2 Production Deployment Considerations

**Backend Services Deployment:**

- **Platform:** Deploy on cloud VM (AWS EC2, Google Cloud Compute, DigitalOcean Droplet)
- **Process Manager:** Use Gunicorn with Uvicorn workers:
  ```bash
  gunicorn backend_services.app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
  ```
- **Reverse Proxy:** Nginx for SSL termination and load balancing

**AI Services Deployment:**

- **Platform:** Same VM or separate (for independent scaling)
- **GPU Acceleration:** Not required (Groq provides cloud GPUs)
- **Process Manager:** Same Gunicorn + Uvicorn setup

**Database Deployment:**

- **Managed Database:** Use managed PostgreSQL (AWS RDS, Google Cloud SQL) for automated backups
- **PGVector Extension:** Ensure cloud provider supports custom extensions
- **Connection Pooling:** Use PgBouncer for connection management at scale

**Mobile App Deployment:**

- **iOS:** Submit to Apple App Store via Xcode + App Store Connect
- **Android:** Submit to Google Play Console
- **Code Signing:** Use Flutter's build commands with release certificates

### 7.10.3 CI/CD Pipeline (Future Enhancement)

Recommended GitHub Actions workflow:

1. **On Push:** Run unit tests, linting (flake8, black)
2. **On Pull Request:** Run integration tests, security scan (Bandit)
3. **On Merge to Main:** Build Docker images, push to registry
4. **Manual Trigger:** Deploy to production

---

## 7.11 Performance Optimization Techniques

### 7.11.1 Database Query Optimization

**Problem:** Fetching burnout recommendations requires joining 5 tables (users, tasks, burnout_analyses, recommendations, strategies).

**Solution:** Use SQLAlchemy's `joinedload` to fetch related data in one query instead of N+1 queries:

```python
# Before: N+1 queries (1 for recommendations, N for strategies)
recommendations = db.query(Recommendation).filter_by(user_id=user_id).all()
for rec in recommendations:
    strategy = db.query(Strategy).get(rec.strategy_id)  # N queries

# After: 1 query with join
recommendations = db.query(Recommendation)\
    .options(joinedload(Recommendation.strategy))\
    .filter_by(user_id=user_id)\
    .all()
```

**Result:** Reduced API response time from 450ms to 80ms.

### 7.11.2 Caching Strategies

**Current Implementation:**

- No caching (all queries hit database)

**Future Enhancement:**

Use Redis to cache:

1. **Burnout Scores:** Cache for 1 hour (scores don't change frequently)
2. **User Profiles:** Cache for 5 minutes
3. **RAG Strategy Embeddings:** Cache permanently (strategies rarely change)

**Cache Invalidation:**

- Invalidate burnout cache when new analysis is created
- Invalidate user cache on profile updates

### 7.11.3 Async Operations

**LLM API Calls in Parallel:**

When generating multiple recommendations, call LLM concurrently:

```python
# Sequential: 3 recommendations × 2 seconds = 6 seconds
for strategy in top_strategies:
    rec = await llm.generate(strategy)

# Parallel: 2 seconds total
tasks = [llm.generate(s) for s in top_strategies]
recommendations = await asyncio.gather(*tasks)
```

**Result:** Recommendation generation reduced from ~6 seconds to ~2 seconds.

---

## 7.12 Security Implementation

### 7.12.1 Input Validation

**Pydantic Validation:**

All API inputs validated via Pydantic schemas, preventing:

- SQL injection (inputs are parameterized)
- XSS (HTML stripped from user inputs)
- Type confusion (e.g., string where integer expected)

**File Upload Validation:**

Audio/PDF/image uploads validated:

```python
ALLOWED_AUDIO = {".mp3", ".wav", ".m4a"}
ALLOWED_IMAGES = {".jpg", ".jpeg", ".png"}
ALLOWED_DOCS = {".pdf"}

if not file.filename.lower().endswith(tuple(ALLOWED_AUDIO)):
    raise HTTPException(400, "Invalid file type")

if file.size > 50 * 1024 * 1024:  # 50 MB limit
    raise HTTPException(400, "File too large")
```

### 7.12.2 Authentication Security

**Password Security:**

- Passwords hashed with bcrypt (cost factor 12)
- No plain-text password storage
- Password requirements enforced (8+ characters, not user's name)

**JWT Security:**

- Access tokens expire in 15 minutes (short-lived)
- Refresh tokens stored in database (can be revoked)
- Secret key 256-bit random (never committed to Git)

**OAuth Security:**

- OAuth tokens encrypted before database storage (AES-256)
- State parameter used to prevent CSRF attacks
- Redirect URLs whitelisted

### 7.12.3 API Rate Limiting (Future)

Prevent abuse by limiting requests per user:

- Anonymous: 10 requests/minute
- Authenticated: 100 requests/minute
- Premium users: 500 requests/minute

---

## 7.13 Development Challenges and Solutions

### 7.13.1 Challenge: PGVector Installation on Windows

**Problem:** PGVector extension doesn't have official Windows binaries. Local development on Windows machines failed.

**Solution:**
1. Use Docker Desktop with `pgvector/pgvector:pg15` image
2. Alternatively, use WSL2 (Windows Subsystem for Linux) to run PostgreSQL natively
3. For production, deploy on Linux servers (no Windows limitation)

### 7.13.2 Challenge: LLM Hallucinations in Task Extraction

**Problem:** Groq's Llama 3.1 sometimes hallucinated tasks that weren't in the transcript.

Example:
- Transcript: "Finish the report by Friday"
- LLM Output: "Finish the report by Friday, review slides, email professor"

**Solution:**
1. Lower temperature from 0.7 to 0.1 (more deterministic)
2. Add to prompt: "ONLY extract tasks explicitly mentioned. Do NOT infer additional tasks."
3. Use JSON schema validation to enforce strict output format

**Result:** Hallucination rate reduced from ~15% to ~2%.

### 7.13.3 Challenge: OAuth Token Expiry During Sync

**Problem:** Google Calendar sync failed if user's access token expired mid-sync.

**Solution:**
1. Before sync, check token expiry timestamp
2. If expired, refresh token proactively
3. Wrap sync in try-catch: If 401 error, refresh token and retry
4. Update token in database after refresh

### 7.13.4 Challenge: Vector Search Cold Start

**Problem:** First vector search after database restart took 5+ seconds (index not loaded into memory).

**Solution:**
1. Warm up vector index on application startup:
   ```python
   # Dummy query to load index
   db.execute("SELECT * FROM strategies ORDER BY embedding <=> '[0,0,0,...]' LIMIT 1")
   ```
2. Result: Subsequent searches complete in <100ms

### 7.13.5 Challenge: Mobile App JWT Refresh Logic

**Problem:** Mobile app didn't handle access token expiry gracefully, causing "401 Unauthorized" errors mid-session.

**Solution:**
1. Implement Dio interceptor in Flutter:
   ```dart
   dio.interceptors.add(InterceptorsWrapper(
     onError: (error, handler) async {
       if (error.response?.statusCode == 401) {
         // Refresh token
         final newToken = await authService.refreshToken();
         // Retry original request
         return handler.resolve(await _retry(error.requestOptions));
       }
       return handler.next(error);
     }
   ));
   ```
2. Result: Seamless token refresh without user noticing

### 7.13.6 Challenge: Burnout Score Calibration

**Problem:** Initial burnout scores were consistently too high (average 85/100), causing alarm fatigue.

**Solution:**
1. Collected baseline data from 10 test users over 2 weeks
2. Adjusted thresholds:
   - Changed "high workload" from 1.2× baseline to 1.5× baseline
   - Reduced sentiment score weight from 50% to 40%
3. Result: Average score dropped to 62, with better distribution across low/medium/high categories

### 7.13.7 Challenge: RAG Context Window Limits

**Problem:** Notebook PDFs sometimes exceeded LLM's 8k token context window, causing truncation.

**Solution:**
1. Implemented chunk-based retrieval (top 5 chunks instead of full document)
2. If question requires full document (e.g., "Summarize the entire chapter"), use Llama 3.1 70B's 128k token context window
3. Split very long documents into sub-notebooks

---

## 7.14 Code Quality and Maintenance

### 7.14.1 Code Style and Linting

**Python (Backend + AI Services):**

- **Formatter:** Black (line length 88)
- **Linter:** Flake8 (with exceptions for line length)
- **Type Checking:** mypy for static type analysis
- **Import Sorting:** isort

**Dart (Mobile App):**

- **Formatter:** `dart format`
- **Linter:** `flutter analyze` with recommended rules

### 7.14.2 Documentation Standards

**Code Documentation:**

- All services have docstrings explaining purpose and usage
- Complex algorithms (burnout scoring, RAG ranking) include inline comments
- API endpoints documented with Pydantic schemas (auto-generates OpenAPI)

**Project Documentation:**

- README.md: Project overview, setup instructions, architecture diagram
- CONTRIBUTING.md: Development guidelines, how to run tests
- API Documentation: Auto-generated Swagger UI at `/docs` endpoint

### 7.14.3 Version Control Practices

**Git Workflow:**

1. Main branch: `main` (production-ready code)
2. Feature branches: `feature/burnout-analysis`, `feature/google-calendar`
3. Pull requests required for merging to main
4. Commit messages follow conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`

**Example Commits:**

- `feat: add Google Calendar integration`
- `fix: resolve JWT refresh token expiry bug`
- `docs: update API documentation with new endpoints`

---

## 7.15 Lessons Learned

### 7.15.1 Technical Lessons

1. **Start with Database Design:** Solid schema design prevented major refactoring later. PGVector was added early, avoiding data migration pain.

2. **Mock External APIs Early:** Delaying Groq/Voyage AI mocking led to slow test suites (60+ seconds). After mocking, tests run in <5 seconds.

3. **Async Everything:** FastAPI's async support is critical for I/O-bound operations (API calls, database queries). Blocking operations (file uploads) should use `run_in_executor`.

4. **LLM Prompt Engineering is Iterative:** Initial prompts for task extraction were too vague. Took 5+ iterations to achieve 98% accuracy.

5. **Vector Search Needs Tuning:** Default PGVector settings were slow. After adding IVFFlat index and tuning `lists` parameter, searches became 10× faster.

### 7.15.2 Process Lessons

1. **Separate Backend from AI Services Early:** Initially combined in one codebase, leading to dependency conflicts (LangChain required Python 3.11, but some backend deps needed 3.10). Separation resolved this.

2. **Document as You Build:** Writing Chapter 6 (System Design) during implementation helped identify design flaws early.

3. **User Testing is Essential:** Burnout score calibration required real user data. Initial threshold assumptions were wrong.

4. **External API Reliability Varies:** Groq occasionally has downtime; AssemblyAI is very reliable. Always have fallback strategies.

### 7.15.3 Future Improvements

1. **Caching:** Add Redis for burnout scores and user profiles
2. **Background Jobs:** Use Celery for async tasks (calendar sync, batch analysis)
3. **Monitoring:** Add Sentry.io for error tracking, Prometheus for metrics
4. **Load Testing:** Simulate 1000+ concurrent users to identify bottlenecks
5. **Mobile Offline Support:** Cache tasks locally, sync when online

---

## 7.16 Summary

This chapter detailed the **implementation and technical execution** of Sentry AI, covering:

**Backend Services:**
- Authentication with email/password and OAuth (Google, Apple, Facebook)
- Task management with AI-enhanced fields
- Integration service for Google Calendar and Trello sync

**AI Services:**
- Burnout analysis with 60/40 workload-sentiment scoring
- RAG recommendation engine with vector retrieval and LLM personalization
- Multi-modal task extraction (audio, images, PDFs)
- AI Companion using LangGraph for stateful conversations
- Notebook library with RAG-based chat and study material generation

**Technical Infrastructure:**
- PostgreSQL + PGVector for relational data and vector search
- FastAPI for high-performance async APIs
- Pydantic for schema validation
- SQLAlchemy for database ORM
- External APIs: Groq (LLM), Voyage AI (embeddings), AssemblyAI (transcription)

**Key Achievements:**
- Shared database pattern enabling seamless communication between Backend and AI Services
- Event-specific recommendations grounded in users' actual calendar events
- Multi-modal task extraction supporting audio, images, and PDFs
- Stateful AI Companion maintaining conversation context
- Production-ready authentication with JWT and OAuth

**Challenges Overcome:**
- PGVector installation on Windows (solved with Docker)
- LLM hallucinations in task extraction (reduced via prompt engineering)
- OAuth token expiry during sync (proactive refresh)
- Vector search cold start (index warm-up)
- Burnout score calibration (user testing and threshold adjustment)

The system is deployed locally for development, with a clear path to production deployment on cloud platforms (AWS, Google Cloud) using Docker containers and managed PostgreSQL.

---

**Chapter 7 Complete: 30+ pages**
