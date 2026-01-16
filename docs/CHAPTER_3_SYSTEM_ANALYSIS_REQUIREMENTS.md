# 3. SYSTEM ANALYSIS AND REQUIREMENTS

This chapter presents a comprehensive analysis of the Sentry AI system, including the examination of current approaches to burnout management, the proposed system solution, feasibility assessment, and detailed functional and non-functional requirements. Use case diagrams and descriptions provide a structured view of system interactions.

---

## 3.1 System Analysis

### 3.1.1 Current System Analysis

Currently, individuals and organizations rely on fragmented approaches to address burnout:

**Manual Self-Assessment:**
- Users periodically complete burnout questionnaires (e.g., MBI)
- Results are static snapshots without continuous monitoring
- No integration with actual workload data
- Requires conscious effort and is often neglected

**Generic Wellness Applications:**
- Apps like Headspace and Calm provide meditation and relaxation content
- One-size-fits-all recommendations regardless of individual context
- No connection to task management or calendar systems
- Focus on symptoms rather than root causes

**Separate Productivity Tools:**
- Task managers (Todoist, Asana) track work without health awareness
- Calendar apps schedule meetings without workload consideration
- No burnout indicators or preventive alerts
- Users must manually recognize overload patterns

**Organizational Approaches:**
- Annual employee wellness surveys
- Reactive intervention after burnout symptoms appear
- Generic wellness programs without personalization
- Limited real-time visibility into team workload

**Limitations of Current Approaches:**

| Limitation | Impact |
|------------|--------|
| No real-time monitoring | Burnout detected too late |
| Generic recommendations | Low user engagement and compliance |
| Disconnected data sources | Incomplete picture of burnout factors |
| Manual data entry required | User burden reduces adoption |
| No personalization | Irrelevant suggestions ignored |
| Reactive rather than proactive | Intervention after damage occurs |

### 3.1.2 Proposed System Analysis

Sentry AI addresses these limitations through an integrated, AI-powered approach:

**Automated Data Collection:**
- Direct integration with task databases and calendar systems
- Automatic metric calculation (no manual entry required)
- Continuous monitoring rather than periodic snapshots
- Qualitative data capture through AI companion conversations

**Multi-Dimensional Analysis:**
- Quantitative workload analysis (tasks, meetings, deadlines)
- Qualitative sentiment analysis (emotional check-ins, diary entries)
- Behavioral pattern learning over time
- Comprehensive burnout scoring with trend detection

**Evidence-Based Recommendations:**
- RAG retrieval from curated strategy guidebook
- Grounded in validated psychological research
- Event-specific guidance referencing actual calendar and tasks
- Personalized to user role, preferences, and constraints

**Conversational AI Support:**
- Natural language interaction through AI companion
- Emotional support and empathetic responses
- Task creation through conversation
- Accessible mental health guidance

**Multi-Modal Task Extraction:**
- Process audio recordings, documents, images, handwritten notes
- Automatic task database population
- Reduced manual data entry burden
- Support for diverse input preferences

### 3.1.3 Feasibility Study

**Technical Feasibility:**

| Component | Technology | Availability |
|-----------|------------|--------------|
| LLM Processing | Groq API (Llama 3.1) | ✓ Available |
| Vector Database | PostgreSQL + PGVector | ✓ Available |
| Embeddings | Voyage AI | ✓ Available |
| Audio Transcription | AssemblyAI | ✓ Available |
| Document Processing | Unstructured.io | ✓ Available |
| OCR | Tesseract | ✓ Open Source |
| API Framework | FastAPI | ✓ Open Source |
| Agent Framework | LangGraph | ✓ Available |

The system leverages mature, well-documented technologies with active community support. All components are either open-source or available through affordable API services.

**Operational Feasibility:**
- Users interact through familiar interfaces (chat, file upload)
- Minimal training required for basic functionality
- Integrates with existing workflow rather than replacing it
- Gradual adoption possible (start with one service, expand over time)

**Economic Feasibility:**
- Cloud deployment enables pay-per-use pricing
- Open-source components minimize licensing costs
- API costs scale with usage (cost-effective for small deployments)
- Potential ROI through reduced burnout-related productivity loss

---

## 3.2 Functional Requirements

This section details the functional requirements organized by system service.

### 3.2.1 User Authentication and Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | System shall allow users to register with email and password | High |
| FR-1.2 | System shall support OAuth authentication (Google, Facebook, Apple) | Medium |
| FR-1.3 | System shall authenticate users using JWT tokens | High |
| FR-1.4 | System shall allow users to reset password via email | High |
| FR-1.5 | System shall maintain user sessions with configurable expiration | Medium |
| FR-1.6 | System shall allow users to update profile information | Medium |
| FR-1.7 | System shall support email verification for new accounts | Medium |

### 3.2.2 Task and Calendar Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | System shall allow users to create, read, update, and delete tasks | High |
| FR-2.2 | System shall support task attributes: title, description, priority, due date, status | High |
| FR-2.3 | System shall support meeting/event entries with start time, end time, attendees | High |
| FR-2.4 | System shall mark tasks as delegatable or non-delegatable | Medium |
| FR-2.5 | System shall mark meetings as optional or required | Medium |
| FR-2.6 | System shall track task completion status and history | High |
| FR-2.7 | System shall calculate task statistics (total, overdue, due this week) | High |
| FR-2.8 | System shall support recurring meetings | Medium |
| FR-2.9 | System shall allow task assignment to team members | Medium |

### 3.2.3 Burnout Analysis Service

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | System shall calculate burnout score from quantitative metrics | High |
| FR-3.2 | System shall analyze sentiment from qualitative data | High |
| FR-3.3 | System shall combine scores into final burnout assessment (60% workload, 40% sentiment) | High |
| FR-3.4 | System shall classify burnout level as GREEN, YELLOW, or RED | High |
| FR-3.5 | System shall identify primary burnout factors and stress indicators | High |
| FR-3.6 | System shall track burnout score trends over time | Medium |
| FR-3.7 | System shall detect deviation from user's personal baseline | Medium |
| FR-3.8 | System shall generate alerts when burnout reaches critical levels | High |
| FR-3.9 | System shall store burnout analysis history for each user | Medium |

### 3.2.4 Recommendation Generation Service

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | System shall retrieve relevant strategies from vector database using RAG | High |
| FR-4.2 | System shall generate personalized recommendations based on burnout analysis | High |
| FR-4.3 | System shall reference specific calendar events in recommendations | High |
| FR-4.4 | System shall reference specific tasks in recommendations | High |
| FR-4.5 | System shall respect user preferences (accepted/avoided recommendation types) | Medium |
| FR-4.6 | System shall respect user constraints (deadlines, PTO blocks) | Medium |
| FR-4.7 | System shall provide action steps for each recommendation | High |
| FR-4.8 | System shall prioritize recommendations by urgency | Medium |
| FR-4.9 | System shall track recommendation application status | Medium |

### 3.2.5 AI Companion Service

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | System shall accept text messages from users | High |
| FR-5.2 | System shall classify user intent (emotional support, task query, burnout query, task creation, general chat) | High |
| FR-5.3 | System shall provide empathetic responses to emotional content | High |
| FR-5.4 | System shall save emotional entries to qualitative data table | High |
| FR-5.5 | System shall perform sentiment analysis on user messages | Medium |
| FR-5.6 | System shall respond to queries about task statistics | High |
| FR-5.7 | System shall respond to queries about burnout status | High |
| FR-5.8 | System shall create tasks from natural language descriptions | Medium |
| FR-5.9 | System shall maintain conversation context within a session | Medium |
| FR-5.10 | System shall accept audio input and transcribe to text | Medium |

### 3.2.6 Multi-Modal Task Extraction Service

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | System shall extract tasks from audio recordings (MP3, WAV, M4A) | High |
| FR-6.2 | System shall extract tasks from documents (PDF, DOCX) | High |
| FR-6.3 | System shall extract tasks from images (PNG, JPG) | High |
| FR-6.4 | System shall extract tasks from handwritten notes using OCR | Medium |
| FR-6.5 | System shall extract tasks from plain text files | High |
| FR-6.6 | System shall automatically detect input type and select appropriate processor | High |
| FR-6.7 | System shall validate extracted tasks using defined schema | High |
| FR-6.8 | System shall save extracted tasks to database | High |
| FR-6.9 | System shall support batch processing of multiple files | Medium |
| FR-6.10 | System shall translate non-English content to English | Medium |

### 3.2.7 Notebook Library Service

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.1 | System shall allow users to create notebooks | Medium |
| FR-7.2 | System shall allow users to upload documents to notebooks | Medium |
| FR-7.3 | System shall process and embed uploaded documents | Medium |
| FR-7.4 | System shall support chat with notebook content using RAG | Medium |
| FR-7.5 | System shall generate quizzes from notebook content | Low |
| FR-7.6 | System shall list user's notebooks | Medium |
| FR-7.7 | System shall delete documents from notebooks | Medium |

### 3.2.8 User Profile and Preferences

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.1 | System shall store user profile (name, role, team size) | Medium |
| FR-8.2 | System shall store user preferences (communication style, accepted/avoided recommendations) | Medium |
| FR-8.3 | System shall store user constraints (deadlines, PTO blocks) | Medium |
| FR-8.4 | System shall learn behavioral patterns from historical data | Medium |
| FR-8.5 | System shall calculate user's baseline burnout score after sufficient data | Medium |
| FR-8.6 | System shall identify user-specific stress triggers | Medium |

---

## 3.3 Non-Functional Requirements

### 3.3.1 Performance Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1.1 | API response time for simple queries | < 500ms |
| NFR-1.2 | Burnout analysis processing time | < 3 seconds |
| NFR-1.3 | Recommendation generation time | < 5 seconds |
| NFR-1.4 | AI companion response time | < 5 seconds |
| NFR-1.5 | Task extraction from text | < 3 seconds |
| NFR-1.6 | Task extraction from audio (5 min) | < 30 seconds |
| NFR-1.7 | Task extraction from document (10 pages) | < 60 seconds |
| NFR-1.8 | Concurrent user support | 100+ simultaneous users |

### 3.3.2 Security Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| NFR-2.1 | Authentication | JWT-based token authentication for all protected endpoints |
| NFR-2.2 | Authorization | Role-based access control; users access only their own data |
| NFR-2.3 | Data Encryption | HTTPS for all API communications |
| NFR-2.4 | Password Security | Passwords hashed using bcrypt with appropriate salt rounds |
| NFR-2.5 | Input Validation | All inputs validated and sanitized to prevent injection attacks |
| NFR-2.6 | Token Expiration | JWT tokens expire after configurable duration (default: 24 hours) |
| NFR-2.7 | Sensitive Data | Mental health data encrypted at rest and in transit |

### 3.3.3 Scalability Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| NFR-3.1 | Horizontal Scaling | System architecture supports horizontal scaling of API servers |
| NFR-3.2 | Database Scaling | PostgreSQL supports read replicas for increased query capacity |
| NFR-3.3 | Stateless Design | API services are stateless to enable load balancing |
| NFR-3.4 | Async Processing | Long-running tasks processed asynchronously |

### 3.3.4 Availability Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-4.1 | System Uptime | 99% availability |
| NFR-4.2 | Planned Maintenance | Maximum 4 hours/month during off-peak hours |
| NFR-4.3 | Error Recovery | Graceful degradation when external services unavailable |
| NFR-4.4 | Data Backup | Daily database backups with 30-day retention |

### 3.3.5 Usability Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| NFR-5.1 | Intuitive Interface | Users can complete primary tasks without documentation |
| NFR-5.2 | Response Clarity | AI responses are clear, actionable, and free of jargon |
| NFR-5.3 | Error Messages | User-friendly error messages with guidance for resolution |
| NFR-5.4 | Accessibility | UI complies with WCAG 2.1 AA guidelines |
| NFR-5.5 | Mobile Responsiveness | UI functions correctly on mobile devices |

### 3.3.6 Maintainability Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| NFR-6.1 | Modular Architecture | Services are loosely coupled and independently deployable |
| NFR-6.2 | Code Documentation | All public APIs documented with descriptions and examples |
| NFR-6.3 | Logging | Comprehensive logging for debugging and monitoring |
| NFR-6.4 | Configuration | Environment-based configuration (no hardcoded values) |

### 3.3.7 Reliability Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| NFR-7.1 | Data Integrity | Database transactions ensure data consistency |
| NFR-7.2 | Fault Tolerance | System handles individual component failures gracefully |
| NFR-7.3 | Validation | All extracted tasks validated before database insertion |
| NFR-7.4 | Idempotency | API operations are idempotent where appropriate |

---

## 3.4 Use Case Diagrams

### 3.4.1 Main System Use Case Diagram

> **Figure 3.1:** Main System Use Case Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SENTRY AI SYSTEM                                │
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐      │
│  │   Register &    │     │  Manage Tasks   │     │ Analyze Burnout │      │
│  │     Login       │     │  & Meetings     │     │                 │      │
│  └────────┬────────┘     └────────┬────────┘     └────────┬────────┘      │
│           │                       │                       │               │
│           │    ┌─────────────────┐│                       │               │
│           │    │  View Burnout   ││                       │               │
│  ┌────┐   │    │    Dashboard    │├───────────────────────┘               │
│  │    │   │    └────────┬────────┘│                                       │
│  │ U  │───┼─────────────┼─────────┼───────────────────────┐               │
│  │ S  │   │             │         │                       │               │
│  │ E  │   │    ┌────────┴────────┐│     ┌─────────────────┴─────┐        │
│  │ R  │   │    │      Get        ││     │   Chat with AI        │        │
│  │    │───┼────┤ Recommendations ├┼─────┤     Companion         │        │
│  └────┘   │    └────────┬────────┘│     └─────────────────┬─────┘        │
│           │             │         │                       │               │
│           │    ┌────────┴────────┐│     ┌─────────────────┴─────┐        │
│           │    │  Apply/Track    ││     │   Submit Diary        │        │
│           └────┤ Recommendations ├┼─────┤     Entry             │        │
│                └─────────────────┘│     └───────────────────────┘        │
│                                   │                                       │
│           ┌─────────────────┐     │     ┌─────────────────┐              │
│           │  Extract Tasks  │     │     │ Manage Notebook │              │
│           │   from Files    ├─────┘     │    Library      │              │
│           └─────────────────┘           └─────────────────┘              │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

                              ┌──────────┐
                              │ External │
                              │ Systems  │
                              └────┬─────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
              ┌─────┴─────┐ ┌─────┴─────┐ ┌─────┴─────┐
              │  Groq AI  │ │ Voyage AI │ │AssemblyAI │
              │    API    │ │Embeddings │ │  Audio    │
              └───────────┘ └───────────┘ └───────────┘
```

### 3.4.2 AI Companion Use Case Diagram

> **Figure 3.2:** AI Companion Use Case Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AI COMPANION SERVICE                      │
│                                                             │
│    ┌─────────────────┐                                      │
│    │  Send Text      │                                      │
│    │    Message      │──────────┐                           │
│    └─────────────────┘          │                           │
│                                 │                           │
│    ┌─────────────────┐          │    ┌─────────────────┐   │
│    │  Send Audio     │          ├───►│ Classify Intent │   │
│    │    Message      │──────────┘    └────────┬────────┘   │
│    └─────────────────┘                        │            │
│                                               │            │
│  ┌────┐                          ┌────────────┼────────────┤
│  │    │                          │            │            │
│  │ U  │    ┌─────────────────┐   │   ┌────────┴────────┐   │
│  │ S  │───►│ Get Emotional   │◄──┤   │  Emotional      │   │
│  │ E  │    │    Support      │   │   │   Support       │   │
│  │ R  │    └─────────────────┘   │   └─────────────────┘   │
│  │    │                          │                         │
│  │    │    ┌─────────────────┐   │   ┌─────────────────┐   │
│  │    │───►│ Query Task      │◄──┼───┤  Task Query     │   │
│  │    │    │   Statistics    │   │   └─────────────────┘   │
│  └────┘    └─────────────────┘   │                         │
│                                  │   ┌─────────────────┐   │
│            ┌─────────────────┐   ├───┤ Burnout Query   │   │
│            │ Query Burnout   │◄──┤   └─────────────────┘   │
│            │    Status       │   │                         │
│            └─────────────────┘   │   ┌─────────────────┐   │
│                                  ├───┤ Task Creation   │   │
│            ┌─────────────────┐   │   └─────────────────┘   │
│            │ Create Task via │◄──┤                         │
│            │ Natural Language│   │   ┌─────────────────┐   │
│            └─────────────────┘   └───┤ General Chat    │   │
│                                      └─────────────────┘   │
│            ┌─────────────────┐                             │
│            │ Submit Diary    │                             │
│            │    Entry        │                             │
│            └─────────────────┘                             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 3.4.3 Task Extraction Use Case Diagram

> **Figure 3.3:** Task Extraction Use Case Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  TASK EXTRACTION SERVICE                     │
│                                                             │
│            ┌─────────────────┐                              │
│            │  Upload Audio   │───┐                          │
│            │     File        │   │     ┌───────────────┐    │
│            └─────────────────┘   │     │   Transcribe  │    │
│                                  ├────►│     Audio     │    │
│            ┌─────────────────┐   │     └───────┬───────┘    │
│            │ Upload Document │───┤             │            │
│            │  (PDF, DOCX)    │   │             │            │
│  ┌────┐    └─────────────────┘   │     ┌───────▼───────┐    │
│  │    │                          │     │    Parse      │    │
│  │ U  │    ┌─────────────────┐   ├────►│   Document    │    │
│  │ S  │───►│  Upload Image   │───┤     └───────┬───────┘    │
│  │ E  │    │                 │   │             │            │
│  │ R  │    └─────────────────┘   │             │            │
│  │    │                          │     ┌───────▼───────┐    │
│  │    │    ┌─────────────────┐   │     │  OCR Process  │    │
│  │    │───►│Upload Handwritten───┼────►│  (if needed)  │    │
│  │    │    │     Notes       │   │     └───────┬───────┘    │
│  └────┘    └─────────────────┘   │             │            │
│                                  │             │            │
│            ┌─────────────────┐   │     ┌───────▼───────┐    │
│            │  Upload Text    │───┘     │ Extract Tasks │    │
│            │     File        │────────►│   via LLM     │    │
│            └─────────────────┘         └───────┬───────┘    │
│                                                │            │
│            ┌─────────────────┐         ┌───────▼───────┐    │
│            │ View Extraction │◄────────│   Validate    │    │
│            │    Results      │         │    Tasks      │    │
│            └─────────────────┘         └───────┬───────┘    │
│                                                │            │
│            ┌─────────────────┐         ┌───────▼───────┐    │
│            │  Batch Upload   │         │  Save to DB   │    │
│            │   Multiple Files│────────►│               │    │
│            └─────────────────┘         └───────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.4.4 Context Diagram

> **Figure 3.4:** System Context Diagram

```
                           ┌─────────────────┐
                           │    Groq AI      │
                           │   (LLM API)     │
                           └────────┬────────┘
                                    │
                                    ▼
┌─────────────┐            ┌───────────────────┐            ┌─────────────┐
│             │            │                   │            │             │
│    User     │◄──────────►│    SENTRY AI      │◄──────────►│  Voyage AI  │
│  (Mobile/   │            │     SYSTEM        │            │ (Embeddings)│
│    Web)     │            │                   │            │             │
│             │            │  ┌─────────────┐  │            └─────────────┘
└─────────────┘            │  │   Backend   │  │
                           │  │  Services   │  │            ┌─────────────┐
                           │  └─────────────┘  │            │             │
                           │                   │◄──────────►│ AssemblyAI  │
                           │  ┌─────────────┐  │            │   (Audio)   │
                           │  │     AI      │  │            │             │
                           │  │  Services   │  │            └─────────────┘
                           │  └─────────────┘  │
                           │                   │            ┌─────────────┐
                           │  ┌─────────────┐  │            │             │
                           │  │ PostgreSQL  │  │◄──────────►│  PGVector   │
                           │  │  Database   │  │            │(Vector Store│
                           │  └─────────────┘  │            │             │
                           │                   │            └─────────────┘
                           └───────────────────┘
```

---

## 3.5 Use Case Descriptions

### 3.5.1 UC-01: User Registration

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-01 |
| **Use Case Name** | User Registration |
| **Actor** | User |
| **Description** | New user creates an account in the system |
| **Preconditions** | User has valid email address |
| **Main Flow** | 1. User navigates to registration page<br>2. User enters email, password, and profile information<br>3. System validates input data<br>4. System creates user account<br>5. System sends verification email<br>6. User verifies email address<br>7. System activates account |
| **Alternative Flow** | 3a. If email already exists, display error message<br>3b. If password doesn't meet requirements, display requirements |
| **Postconditions** | User account created and activated |
| **Priority** | High |

### 3.5.2 UC-02: User Login

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-02 |
| **Use Case Name** | User Login |
| **Actor** | User |
| **Description** | Registered user authenticates to access the system |
| **Preconditions** | User has registered account |
| **Main Flow** | 1. User enters email and password<br>2. System validates credentials<br>3. System generates JWT token<br>4. System returns token to client<br>5. User is redirected to dashboard |
| **Alternative Flow** | 2a. If credentials invalid, display error message<br>2b. If account locked, display lockout message |
| **Postconditions** | User authenticated with valid JWT token |
| **Priority** | High |

### 3.5.3 UC-03: Create Task

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-03 |
| **Use Case Name** | Create Task |
| **Actor** | User |
| **Description** | User creates a new task in the system |
| **Preconditions** | User is authenticated |
| **Main Flow** | 1. User navigates to task creation form<br>2. User enters task details (title, description, priority, due date)<br>3. User optionally sets delegation status and estimated hours<br>4. User submits task<br>5. System validates task data<br>6. System saves task to database<br>7. System displays confirmation |
| **Alternative Flow** | 5a. If validation fails, display specific error messages |
| **Postconditions** | New task created and associated with user |
| **Priority** | High |

### 3.5.4 UC-04: Analyze Burnout

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-04 |
| **Use Case Name** | Analyze Burnout |
| **Actor** | User |
| **Description** | System analyzes user's current burnout level |
| **Preconditions** | User is authenticated; User has tasks/meetings in system |
| **Main Flow** | 1. User requests burnout analysis<br>2. System retrieves user's tasks and meetings<br>3. System retrieves user's qualitative data<br>4. System calculates workload metrics<br>5. System performs sentiment analysis<br>6. System combines scores (60% workload + 40% sentiment)<br>7. System classifies burnout level (GREEN/YELLOW/RED)<br>8. System identifies stress factors<br>9. System saves analysis to history<br>10. System displays results to user |
| **Alternative Flow** | 2a. If no data available, display message requesting data input |
| **Postconditions** | Burnout analysis completed and stored |
| **Priority** | High |

### 3.5.5 UC-05: Get Recommendations

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-05 |
| **Use Case Name** | Get Recommendations |
| **Actor** | User |
| **Description** | System generates personalized burnout recovery recommendations |
| **Preconditions** | User is authenticated; Burnout analysis completed |
| **Main Flow** | 1. User requests recommendations<br>2. System retrieves latest burnout analysis<br>3. System retrieves user profile and preferences<br>4. System retrieves current calendar events<br>5. System retrieves current task list<br>6. System queries vector database for relevant strategies (RAG)<br>7. System constructs LLM prompt with context<br>8. System generates event-specific recommendations<br>9. System displays recommendations with action steps |
| **Alternative Flow** | 6a. If no relevant strategies found, use general recommendations |
| **Postconditions** | Personalized recommendations displayed to user |
| **Priority** | High |

### 3.5.6 UC-06: Chat with AI Companion

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-06 |
| **Use Case Name** | Chat with AI Companion |
| **Actor** | User |
| **Description** | User interacts with AI companion for support and queries |
| **Preconditions** | User is authenticated |
| **Main Flow** | 1. User sends message to AI companion<br>2. System classifies message intent<br>3. Based on intent:<br>&nbsp;&nbsp;- Emotional: Save to qualitative data, respond empathetically<br>&nbsp;&nbsp;- Task query: Retrieve task statistics, respond with data<br>&nbsp;&nbsp;- Burnout query: Retrieve burnout status, respond with analysis<br>&nbsp;&nbsp;- Task creation: Extract task details, create task<br>&nbsp;&nbsp;- General: Generate helpful response<br>4. System performs sentiment analysis on message<br>5. System generates appropriate response<br>6. System displays response to user |
| **Alternative Flow** | 1a. If audio message, transcribe first then process |
| **Postconditions** | User receives appropriate response; emotional data saved if applicable |
| **Priority** | High |

### 3.5.7 UC-07: Extract Tasks from File

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-07 |
| **Use Case Name** | Extract Tasks from File |
| **Actor** | User |
| **Description** | System extracts tasks from uploaded file |
| **Preconditions** | User is authenticated |
| **Main Flow** | 1. User uploads file (audio/document/image/text)<br>2. System detects file type<br>3. System selects appropriate processor:<br>&nbsp;&nbsp;- Audio: Transcribe with AssemblyAI<br>&nbsp;&nbsp;- Document: Parse with Unstructured<br>&nbsp;&nbsp;- Image: Process with vision model<br>&nbsp;&nbsp;- Handwritten: OCR with Tesseract<br>&nbsp;&nbsp;- Text: Direct processing<br>4. System extracts text content<br>5. System sends content to LLM for task extraction<br>6. System validates extracted tasks<br>7. System saves valid tasks to database<br>8. System displays extraction results |
| **Alternative Flow** | 6a. If task validation fails, log warning and continue with valid tasks |
| **Postconditions** | Tasks extracted and saved to user's task list |
| **Priority** | High |

### 3.5.8 UC-08: Submit Diary Entry

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-08 |
| **Use Case Name** | Submit Diary Entry |
| **Actor** | User |
| **Description** | User submits emotional diary entry for analysis |
| **Preconditions** | User is authenticated |
| **Main Flow** | 1. User navigates to diary entry form<br>2. User writes diary entry content<br>3. User submits entry<br>4. System saves entry to qualitative_data table<br>5. System performs sentiment analysis<br>6. System extracts emotional themes<br>7. System generates supportive response<br>8. System displays response and analysis to user |
| **Alternative Flow** | None |
| **Postconditions** | Diary entry saved; sentiment analyzed; response provided |
| **Priority** | Medium |

### 3.5.9 UC-09: Apply Recommendation

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-09 |
| **Use Case Name** | Apply Recommendation |
| **Actor** | User |
| **Description** | User marks a recommendation as applied |
| **Preconditions** | User is authenticated; User has received recommendations |
| **Main Flow** | 1. User views recommendation<br>2. User takes action based on recommendation<br>3. User marks recommendation as applied<br>4. System records application timestamp<br>5. System optionally asks for feedback<br>6. System updates recommendation status |
| **Alternative Flow** | 3a. User can mark recommendation as skipped with reason |
| **Postconditions** | Recommendation status updated for tracking |
| **Priority** | Medium |

### 3.5.10 UC-10: View Burnout Dashboard

| Field | Description |
|-------|-------------|
| **Use Case ID** | UC-10 |
| **Use Case Name** | View Burnout Dashboard |
| **Actor** | User |
| **Description** | User views comprehensive burnout status dashboard |
| **Preconditions** | User is authenticated |
| **Main Flow** | 1. User navigates to dashboard<br>2. System retrieves latest burnout analysis<br>3. System retrieves burnout history<br>4. System retrieves task statistics<br>5. System retrieves active recommendations<br>6. System displays:<br>&nbsp;&nbsp;- Current burnout score and level<br>&nbsp;&nbsp;- Score trend graph<br>&nbsp;&nbsp;- Key stress factors<br>&nbsp;&nbsp;- Task summary<br>&nbsp;&nbsp;- Active recommendations |
| **Alternative Flow** | 2a. If no analysis exists, prompt user to run analysis |
| **Postconditions** | Dashboard displayed with current status |
| **Priority** | High |

---

## 3.6 User Stories

### 3.6.1 Authentication Stories

| ID | User Story | Priority |
|----|------------|----------|
| US-01 | As a new user, I want to register with my email so that I can access the system | High |
| US-02 | As a registered user, I want to log in securely so that I can access my data | High |
| US-03 | As a user, I want to reset my password via email so that I can recover my account | High |
| US-04 | As a user, I want to log in with Google/Facebook so that registration is faster | Medium |

### 3.6.2 Task Management Stories

| ID | User Story | Priority |
|----|------------|----------|
| US-05 | As a user, I want to create tasks so that I can track my work | High |
| US-06 | As a user, I want to set task priorities so that I can focus on important work | High |
| US-07 | As a user, I want to set due dates so that I don't miss deadlines | High |
| US-08 | As a user, I want to mark tasks as delegatable so that recommendations consider this | Medium |
| US-09 | As a user, I want to see overdue tasks so that I can address urgent items | High |

### 3.6.3 Burnout Analysis Stories

| ID | User Story | Priority |
|----|------------|----------|
| US-10 | As a user, I want to see my burnout score so that I understand my current state | High |
| US-11 | As a user, I want to see burnout trends so that I can track my progress | Medium |
| US-12 | As a user, I want to know my stress factors so that I can address root causes | High |
| US-13 | As a user, I want alerts when burnout is critical so that I can take immediate action | High |

### 3.6.4 Recommendation Stories

| ID | User Story | Priority |
|----|------------|----------|
| US-14 | As a user, I want personalized recommendations so that advice is relevant to me | High |
| US-15 | As a user, I want recommendations to reference my actual meetings so that I can act immediately | High |
| US-16 | As a user, I want to see action steps so that I know exactly what to do | High |
| US-17 | As a user, I want to set preferences so that I only receive acceptable recommendations | Medium |
| US-18 | As a user, I want to track applied recommendations so that I can see what works | Medium |

### 3.6.5 AI Companion Stories

| ID | User Story | Priority |
|----|------------|----------|
| US-19 | As a user, I want to chat with AI so that I can get support anytime | High |
| US-20 | As a user, I want to share my feelings so that I can receive emotional support | High |
| US-21 | As a user, I want to ask about my tasks so that I get quick summaries | High |
| US-22 | As a user, I want to create tasks by speaking so that entry is faster | Medium |
| US-23 | As a user, I want to send voice messages so that I can communicate hands-free | Medium |

### 3.6.6 Task Extraction Stories

| ID | User Story | Priority |
|----|------------|----------|
| US-24 | As a user, I want to extract tasks from meeting recordings so that I don't forget action items | High |
| US-25 | As a user, I want to extract tasks from documents so that I can capture written tasks | High |
| US-26 | As a user, I want to extract tasks from photos so that I can digitize handwritten notes | Medium |
| US-27 | As a user, I want batch upload so that I can process multiple files at once | Medium |

---

## 3.7 Summary

This chapter has presented a comprehensive analysis of the Sentry AI system requirements:

**System Analysis:**
- Identified limitations of current burnout management approaches
- Proposed an integrated AI-powered solution
- Confirmed technical, operational, and economic feasibility

**Functional Requirements:**
- 50+ detailed requirements across 8 service areas
- Prioritized by importance (High/Medium/Low)
- Traceable to specific system components

**Non-Functional Requirements:**
- Performance targets (response times, concurrency)
- Security requirements (authentication, encryption)
- Scalability, availability, usability, and maintainability specifications

**Use Cases:**
- 10 detailed use case descriptions
- 4 use case diagrams (Main System, AI Companion, Task Extraction, Context)
- 27 user stories organized by feature area

These requirements provide a clear specification for the system design and implementation phases that follow.

---

## Suggested Figures Summary

| Figure | Description | Type |
|--------|-------------|------|
| 3.1 | Main System Use Case Diagram | UML Use Case |
| 3.2 | AI Companion Use Case Diagram | UML Use Case |
| 3.3 | Task Extraction Use Case Diagram | UML Use Case |
| 3.4 | System Context Diagram | Context Diagram |
| 3.5 | Current vs Proposed System Comparison | Comparison Table |
