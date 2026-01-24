# Sentry AI - Graduation Project Presentation Script
## 45-50 Minutes | Team of 6

---

## SLIDE 1: Title Slide
**[Duration: 1 min]**

**Visuals:**
- Project logo
- Team names with roles
- University/Department info

**Speaker (Team Lead/Business):**

"Good morning/afternoon, distinguished professors and guests. We are honored to present **Sentry AI** - an AI-powered mobile application designed to combat occupational burnout while maximizing productivity.

Our team consists of six members: [Names] working on Flutter frontend and UI/UX design, [Name] on backend architecture, [Names] on AI services and machine learning, and [Name] on business strategy and impact analysis.

Over the past four months, we've built a comprehensive solution that bridges the gap between productivity tools and mental health applications. Let's begin."

---

## SLIDE 2-3: The Burnout Crisis
**[Duration: 3-4 min]**

**Visuals:**
- WHO statement graphic
- Burnout statistics chart (prevalence 2020 vs 2024)
- **[FIGURE NEEDED: Global burnout prevalence map or timeline]**

**Speaker (Business):**

"Before we discuss our solution, let's understand the problem we're solving.

**What is Burnout?**

In 2019, the World Health Organization officially recognized burnout as an 'occupational phenomenon' in the International Classification of Diseases. But what exactly is it?

Dr. Christina Maslach, the leading researcher in this field, defines burnout through three components:

1. **Emotional Exhaustion** - feeling drained and depleted
2. **Depersonalization** - developing cynical attitudes toward work
3. **Reduced Personal Accomplishment** - feeling ineffective

**[SLIDE TRANSITION: Statistics]**

The numbers are alarming:
- **77% of professionals** report experiencing burnout at their current job
- Healthcare workers show **58% burnout rates** - up from 42% in 2020
- Technology sector: **55%** - up from 38%
- The annual cost to the global economy exceeds **$300 billion** in lost productivity

**[Reference: Chapter 1, Figure 1.1 - Burnout Statistics]**

Even more concerning - these numbers have been *rising*, not falling, despite increased awareness. Traditional solutions aren't working."

---

## SLIDE 4-5: Current Solutions and Their Limitations
**[Duration: 3-4 min]**

**Visuals:**
- Split-screen showing productivity apps (ClickUp, Asana) vs mental health apps (Headspace, Calm)
- **[FIGURE: Gap diagram showing missing integration]**

**Speaker (Business):**

"When we surveyed the landscape of existing solutions, we found a critical disconnect.

**Category 1: Pure Productivity Tools**
Apps like ClickUp, Trello, and Asana are excellent at task management. They track deadlines, organize projects, and measure output.

**But here's the problem:** They measure *how much* you're doing, not *how you're feeling*. They can't tell when you're overwhelmed. In fact, they might *contribute* to burnout by encouraging endless productivity optimization.

**Category 2: Mental Health Applications**
On the other side, we have apps like Headspace, Calm, and BetterHelp. They offer meditation, therapy, and emotional support.

**But here's their limitation:** They exist in isolation from your actual work. They don't know *why* you're stressed. They can't see that you have 47 overdue tasks or 12 hours of meetings scheduled tomorrow. They provide generic advice when you need *personalized*, *context-aware* intervention.

**[SLIDE TRANSITION: What We Actually Need]**

What modern professionals need is a system that:
✓ Understands your actual workload
✓ Detects burnout patterns *before* they become critical
✓ Provides actionable, personalized strategies
✓ Integrates with your existing workflow

This is where AI becomes transformative."

---

## SLIDE 6: Hook Statement - Introducing Sentry AI
**[Duration: 2 min]**

**Visuals:**
- Bold statement with animated reveal
- App icon and key visual
- **[FIGURE: Venn diagram showing Productivity + Mental Health + AI]**

**Speaker (Team Lead):**

**[Pause for effect]**

"Imagine an assistant that knows you have 15 tasks due tomorrow, sees you've been working 12-hour days for two weeks straight, notices your meeting load has doubled, and *automatically* suggests which meetings to decline, which tasks to delegate, and when to take a mental health break.

Not generic advice. Not one-size-fits-all tips. **Personalized strategies based on your actual calendar, your role, your constraints.**

**[BOLD REVEAL]**

**This is Sentry AI.**

It's not *just* a productivity app. It's not *just* a mental health chatbot. It's the **first system that maximizes productivity while actively tracking and enhancing mental well-being**.

Think of it as having a personal wellness coach who has access to your calendar, understands your work context, and uses artificial intelligence to guide you toward sustainable productivity.

Now, let me hand it over to [AI Team Member] to explain how we built this."

---

## SLIDE 7-8: Proposed Solution - Sentry AI Features
**[Duration: 4-5 min]**

**Visuals:**
- Feature overview diagram (Chapter 5 architecture)
- **[FIGURE: Chapter 5 - Compact Architecture Diagram]**

**Speaker (AI Team - You):**

"Thank you. Let's talk about what makes Sentry AI unique.

Our system is built around **five core AI-powered features**, each addressing a specific aspect of burnout prevention:

**1. Burnout Analysis Engine**
This isn't a survey that asks 'how stressed are you?' Our system *calculates* burnout by analyzing two dimensions:

- **60% Workload Analysis**: We count your tasks, measure deadline pressure, track meeting density
- **40% Sentiment Analysis**: We analyze your chat messages with our AI companion to detect emotional patterns

The system learns *your* baseline. What's overwhelming for one person might be normal for another. We personalize the thresholds.

**[Reference: Chapter 5, Burnout Scoring Algorithm]**

**2. RAG-Powered Recommendations**
When we detect elevated burnout, we don't just show a number. We provide **grounded, research-backed strategies**.

We've embedded 50+ productivity research papers into a vector database. Using Retrieval-Augmented Generation, we retrieve relevant strategies and *personalize* them using your calendar events, your role, your constraints.

For example: We won't recommend 'delegate tasks' to someone whose profile says they can't delegate. We won't suggest 'decline meetings' if tomorrow's meeting is with your CEO.

**[Reference: Chapter 6, RAG Architecture]**

**3. Multi-Modal Task Extraction**
How many times have you attended a meeting and manually typed out action items afterward?

Our system extracts tasks from:
- Audio recordings (meeting recordings, voice notes)
- PDFs (email attachments, documents)
- Images (whiteboard photos)
- Videos (lecture recordings)

Using AssemblyAI for transcription and Groq's LLM for extraction, we turn unstructured data into structured to-do lists automatically.

**4. AI Companion**
This is your judgment-free space. Chat about your day, vent about a difficult project, or ask for advice.

Built using LangGraph for stateful conversations, the companion remembers context across sessions and can help you:
- Create tasks via natural language
- Get productivity coaching
- Receive emotional support
- Track your well-being trends over time

**5. Notebook Library**
For students and knowledge workers, we turn study materials into interactive knowledge bases.

Upload PDFs, lecture recordings, articles - then *chat* with your content. Generate flashcards, summaries, and quizzes automatically using RAG.

**[SLIDE TRANSITION]**

The key innovation here is **integration**. These features don't exist in isolation. The burnout analysis informs the recommendations. The AI companion can create tasks. The task extraction feeds into burnout calculation. Everything is connected."

---

## SLIDE 9-11: UI/UX Design Journey
**[Duration: 4-5 min]**

**Visuals:**
- Before/after design iterations
- Color palette showcase
- **[FIGURES: Chapter 4 - Onboarding screens, Dashboard, Burnout score screen]**
- **[FIGURE: Chapter 4 - Wireframe complete flow]**

**Speaker (Frontend/UX Team):**

"Now let me talk about how we translated these features into a user experience that actually *reduces* stress instead of adding to it.

**Our Design Philosophy: Calm by Design**

We had a unique challenge: we're building an app for people who are already overwhelmed. The interface itself can't add cognitive load.

**Color Psychology**
We chose a **light blue** primary palette (#E8F4FC) for a reason:

- Blue is scientifically proven to lower heart rate and reduce anxiety
- Light tones create openness and hope - critical for burnout sufferers
- We avoided dark themes because our users primarily engage during work hours

**[Show color palette slide]**

For status indicators, we use intuitive traffic-light colors:
- Green: Healthy (0-40 burnout score)
- Yellow: Moderate (41-60)
- Red: Critical (61-100)

But notice - even our 'critical' red is *soft*, not alarming. We want to inform, not panic.

**[Reference: Chapter 4, Section 5.2 - Color Psychology]**

**Information Architecture**

We mapped out **30+ screens** across seven functional areas:
- Onboarding (3 screens)
- Authentication (6 screens)
- Home Dashboard
- Tasks (2 screens)
- Burnout Analysis (4 screens)
- AI Companion
- Notebook Library (4 screens)
- Integrations (2 screens)
- Profile & Settings (3 screens)

**[Show wireframe diagram - Chapter 4, Figure 5.27]**

The architecture follows a **hub-and-spoke model**. The home screen is your central point. Everything is 2-3 taps away. No deep hierarchies. No getting lost.

**Progressive Disclosure**
We show summary information first, details on demand. For example:
- Dashboard shows your burnout *score*
- Tap to see *factor breakdown*
- Tap again to see *workload metrics*
- Tap once more for *detailed recommendations*

This prevents information overload while keeping depth accessible.

**Glassmorphism Design**
We adopted a modern glassmorphism aesthetic - translucent cards with subtle blur effects. This creates visual depth and a premium feel while maintaining the calming atmosphere.

**[Show dashboard and burnout screens]**

**Why Design-First Mattered**

We spent the first month in Figma *before* writing a single line of Flutter code. This was crucial because:

1. **Faster Iteration**: Changing a color in Figma takes 30 seconds. In code? 30 minutes across multiple files.
2. **Team Alignment**: Everyone could *see* what we're building
3. **User Validation**: We could test flows before implementation
4. **Development Clarity**: Frontend team knew exactly what to build

Every screen, every button, every transition was designed first. This saved us weeks of rework."

---

## SLIDE 12-13: Frontend Implementation
**[Duration: 3-4 min]**

**Visuals:**
- Flutter logo and tech stack icons
- **[FIGURE: Chapter 4, Section 5.8 - Flutter Project Structure]**
- Code-to-design comparison screenshot

**Speaker (Frontend Team):**

"With designs finalized, we moved to implementation using Flutter.

**Technology Stack:**

**Flutter 3.24+** as our framework because:
- **Cross-platform**: One codebase → iOS + Android (50% time savings)
- **Native performance**: Compiles to ARM machine code, not JavaScript
- **Rich widgets**: Built-in components for our glassmorphism design
- **Hot reload**: See changes in <1 second during development

**Supporting technologies:**
- **Dart 3.0+**: Type-safe, modern language
- **Provider/Riverpod**: State management (when burnout score updates, UI automatically rebuilds)
- **Dio**: HTTP client with automatic JWT token refresh
- **Shared Preferences**: Local data caching

**Project Architecture**

**[Show folder structure - Chapter 4, Section 5.8.3]**

We organized the codebase by *feature*, not by type:

```
lib/
  ├── screens/        # Complete pages (onboarding, auth, home, tasks...)
  ├── providers/      # State managers (auth, burnout, tasks)
  ├── services/       # API communication
  ├── widgets/        # Reusable components (cards, buttons)
  └── models/         # Data structures
```

This matters because when you need to modify the burnout feature, everything related is in one folder - the screen, the state logic, the service calls. No hunting through scattered files.

**Figma-to-Flutter Translation**

Our design system in Figma directly mapped to Flutter code:

- Color constants: `Color(0xFFE8F4FC)` exactly matches Figma
- Typography scales: Figma text styles → Flutter TextTheme
- Component library: Figma components → Flutter widgets

We even extracted exact spacing values. A 24px padding in Figma = `EdgeInsets.all(24)` in Flutter.

**Key Implementation Patterns:**

1. **Responsive Layouts**: Using `MediaQuery` and `LayoutBuilder` to adapt to different screen sizes
2. **Smooth Animations**: `TweenAnimationBuilder` for the burnout score counter animation
3. **Glassmorphism**: `BackdropFilter` with semi-transparent containers
4. **Accessible Design**: Minimum 44x44 touch targets, WCAG contrast ratios

The result? 30+ screens, pixel-perfect to the designs, running smoothly at 60fps."

---

## SLIDE 14-15: System Architecture - High-Level Overview
**[Duration: 3-4 min]**

**Visuals:**
- **[FIGURE: Chapter 5 - System Architecture (3-tier diagram)]**
- **[FIGURE: Chapter 5 - ER Diagram]**

**Speaker (Backend Team):**

"Now let's zoom out and look at the complete system architecture.

**Three-Tier Architecture:**

We designed Sentry AI as a **distributed system** with clear separation of concerns:

**Tier 1: Mobile Client (Flutter)**
- Runs on user's phone
- Handles UI rendering and user interaction
- Caches data locally for offline access

**Tier 2: Application Layer (Two FastAPI Services)**

This is where it gets interesting. We split our backend into **two independent services**:

1. **Backend Services** (Port 8000):
   - Authentication (JWT + OAuth)
   - Task management
   - User profiles
   - Third-party integrations (Google Calendar, Trello)

2. **AI Services** (Port 8001):
   - Burnout analysis
   - RAG recommendations
   - Task extraction
   - AI Companion (LangGraph)
   - Notebook Library

**Why separate them?**
- Different scaling requirements (AI is more compute-intensive)
- Different deployment patterns (AI might need GPU instances)
- Easier to update one without affecting the other
- Better for team development (backend team vs AI team)

**Tier 3: Data Layer (PostgreSQL + PGVector)**

Here's our key architectural decision: **Shared Database Pattern**.

Both services connect to the *same* PostgreSQL database. This enables:
- **Zero data duplication**: Tasks created in Backend Services are immediately available to AI Services for burnout analysis
- **Simplified consistency**: No need for complex data synchronization
- **Vector + Relational**: PGVector extension lets us store both structured data (tasks, users) and vector embeddings (for RAG) in one place

**[Reference: Chapter 5, Section 6.3 - Database Schema]**

**Scalability Design:**

**[Show ER diagram]**

Our database has 12 core tables:
- **Users** (authentication, profiles)
- **Tasks** (with AI-enhanced fields like `can_delegate`, `estimated_hours`)
- **Burnout Analyses** (historical tracking)
- **Recommendations** (RAG-generated strategies)
- **Notebooks** + **Notebook Sources** (RAG knowledge bases)
- **Integrations** (OAuth tokens for Google/Trello)

We designed for horizontal scalability:
- Stateless services (can run multiple instances)
- Database connection pooling (async SQLAlchemy)
- API Gateway pattern ready (add NGINX for load balancing)

This architecture supports our current 100 users and scales to 100,000+ with infrastructure upgrades."

---

## SLIDE 16-18: Backend Services - Deep Dive
**[Duration: 4-5 min]**

**Visuals:**
- Tech stack logos (FastAPI, PostgreSQL, SQLAlchemy)
- **[FIGURE: Chapter 6 - Backend Services API endpoints]**
- OAuth flow diagram

**Speaker (Backend Team):**

"Let me explain why our backend is more sophisticated than a typical CRUD application.

**Why Such a Comprehensive Backend?**

You might wonder - why 50+ API endpoints for a mobile app? Three reasons:

1. **AI Integration Requirements**: AI services need rich context. We provide:
   - Detailed task metadata (priority, category, time estimates)
   - Calendar events with attendee information
   - User profile data (role, seniority, delegation capability)
   - Historical burnout scores

2. **Real-Time Synchronization**: We sync with external services:
   - Google Calendar (fetch events, create/update)
   - Trello (import tasks, sync status changes)
   - OAuth token management with automatic refresh

3. **Security and Validation**: Every request passes through:
   - JWT authentication
   - Pydantic schema validation
   - Role-based access control
   - Rate limiting

**Technology Stack:**

**FastAPI** as our framework:
- **Async by default**: Non-blocking I/O for database queries and external APIs
- **Automatic OpenAPI docs**: Interactive API documentation generated automatically
- **Type safety**: Pydantic validates every request/response
- **Performance**: 3x faster than Django, comparable to Node.js

**SQLAlchemy 2.0** for database ORM:
- **Async support**: `async/await` for all database operations
- **Type hints**: Full IDE autocomplete for queries
- **Migration management**: Alembic for schema versioning

**Key Backend Features:**

**1. Authentication System**

**[Show OAuth flow diagram]**

We support four authentication methods:
- Email/Password (bcrypt hashing)
- Google OAuth
- Apple Sign-In
- Facebook Login

All return the same JWT token structure:
- **Access token**: 15-minute expiry (security)
- **Refresh token**: 30-day expiry (convenience)

The mobile app automatically refreshes expired tokens using Dio interceptors - users never see "please log in again" errors.

**2. Task Management**

Our task model is *AI-enhanced*:

```python
class Task:
    title: str
    due_date: datetime
    priority: Literal["low", "medium", "high"]
    category: Literal["work", "personal", "study"]

    # AI-enhanced fields
    can_delegate: bool          # Can this task be delegated?
    estimated_hours: float      # Time required
    is_optional: bool          # Is it truly necessary?
    source: str                # "manual" | "google_calendar" | "ai_extracted"
```

Why? Because burnout analysis needs to know:
- Can you delegate this task? (if not, delegating won't help)
- How many hours of work do you have scheduled? (workload calculation)
- Which tasks are optional? (prioritization suggestions)

**3. Integration Service**

We maintain OAuth connections to external services:

**Google Calendar Integration:**
- Fetch upcoming events (next 7 days)
- Create calendar blocks for focus time
- Detect meeting overload (>4 hours/day triggers warning)

**Trello Integration:**
- Import boards as task categories
- Sync card status changes
- Extract due dates and priorities

**Token Management Challenge:**
OAuth tokens expire. Our solution:
- Store refresh tokens securely in database
- Proactively refresh before long operations (sync)
- Retry failed requests with new tokens
- Graceful degradation if refresh fails

**[Reference: Chapter 6, Section 7.7 - Integration Implementation]**

This backend serves as a **robust foundation** for AI services to build upon."

---

## SLIDE 19-21: AI Foundation - LLMs, RAG, and Context
**[Duration: 5-6 min]**

**Visuals:**
- **[FIGURE: Transformer architecture diagram (high-level)]**
- **[FIGURE: Chapter 2 - RAG system architecture]**
- Context window visualization
- Hallucination example

**Speaker (AI Team - You):**

"Before diving into our AI features, let's establish the foundation: *why* we use Large Language Models and *how* we make them reliable.

**AI in Mental Health: Literature Foundation**

Recent research shows promising results for AI-assisted mental health interventions:
- **Torous et al. (2023)**: AI chatbots show 23% reduction in depression scores
- **Fitzpatrick et al. (2017)**: Conversational agents effective for anxiety management
- **Bendig et al. (2019)**: Digital interventions comparable to in-person therapy for mild-moderate cases

**But** - these studies focus on *standalone* mental health apps. Our innovation is *integrating* AI with productivity data for context-aware intervention.

**[Reference: Chapter 2, Literature Review]**

**What are Large Language Models?**

**[Show simplified transformer diagram]**

At a very high level, LLMs like GPT, Llama, and Claude are:
- **Trained on trillions of words** from the internet
- **Predict the next word** based on context
- **Understand patterns** in language, reasoning, and knowledge

For example, given:
> "The user has 47 overdue tasks and worked 12-hour days this week. They should..."

The LLM predicts: "...consider delegating tasks, declining meetings, and taking a mental health day."

**The Context Window Problem**

LLMs have a **limited memory** called a context window. Llama 3.1 supports 128K tokens (~96,000 words).

Sounds like a lot? Consider what we need to fit:
- User's task list (100+ tasks)
- Calendar events (50+ meetings)
- Burnout history (months of data)
- Chat conversation history
- 50+ research papers for recommendations

**We quickly exceed 128K tokens.**

**The Hallucination Problem**

LLMs sometimes generate confident, plausible-sounding, but *completely false* information.

Example hallucination:
> **User**: "How do I reduce burnout?"
> **LLM**: "Studies show taking 15-minute breaks every hour reduces burnout by 60%."

Sounds great! Problem: **That statistic doesn't exist.** The LLM made it up.

For a mental health application, hallucinations are unacceptable. Users need *accurate, evidence-based* guidance.

**Enter RAG: Retrieval-Augmented Generation**

**[Show RAG architecture diagram - Chapter 2]**

RAG solves both problems:

**How RAG Works (4 Steps):**

1. **Indexing Phase (One-Time Setup)**:
   - We take 50+ productivity research papers
   - Split into chunks (500 words each)
   - Convert each chunk to a **vector embedding** (1024-dimensional array of numbers)
   - Store in PGVector database

2. **Retrieval Phase (During User Request)**:
   - User profile: "Senior engineer, can't delegate, manages team"
   - Convert to embedding
   - Find top 5 most similar research chunks (vector similarity search)
   - Takes <200ms with IVFFlat indexing

3. **Augmentation Phase**:
   - Take retrieved research chunks
   - Combine with user context (tasks, calendar, profile)
   - Build a targeted prompt

4. **Generation Phase**:
   - Send to LLM (Llama 3.1 70B via Groq)
   - LLM generates response *grounded in* the research
   - No hallucinations - it cites the sources we provided

**Example RAG Flow:**

```
User Context:
- Role: Senior Engineer
- Meetings: 6 hours tomorrow
- Can't delegate: True

Retrieved Research (Top 3):
1. "Managers who block 2-hour focus periods show 40% higher output" (Newport, 2016)
2. "Meeting load >4h/day correlates with burnout" (Leiter & Maslach, 2005)
3. "Senior engineers benefit from 'maker schedule' blocks" (Graham, 2009)

Generated Recommendation:
"Based on your role and meeting load, consider blocking two 2-hour focus periods
this week. Research shows senior engineers are 40% more productive with
uninterrupted blocks (Newport, 2016). Your current 6-hour meeting day exceeds
the 4-hour threshold associated with burnout risk (Leiter & Maslach, 2005).
Suggested action: Decline or reschedule 2 low-priority meetings."
```

**Our LLM Providers:**

We use **Groq** as our LLM inference provider:
- **Model**: Llama 3.1 70B (open-source, high-quality)
- **Speed**: 300 tokens/second (10x faster than OpenAI)
- **Cost**: $0.79 per 1M tokens (15x cheaper than GPT-4)
- **Reliability**: 99.9% uptime in our testing

For embeddings: **Voyage AI**
- **Model**: voyage-3
- **Quality**: State-of-the-art retrieval accuracy
- **Speed**: 500 embeddings/second

For transcription: **AssemblyAI**
- **Accuracy**: 95%+ on technical content
- **Speed**: Real-time transcription
- **Features**: Speaker diarization, punctuation, timestamps

This foundation enables our four AI services to provide accurate, fast, personalized assistance."

---

## SLIDE 22-25: AI Service #1 - Burnout Analysis Engine
**[Duration: 4-5 min]**

**Visuals:**
- **[FIGURE: Chapter 6 - Burnout scoring algorithm flowchart]**
- **[FIGURE: Example burnout dashboard screen]**
- Component weight diagram (60/40 split)

**Speaker (AI Team - You):**

"Now let's dive into our first AI service: **Burnout Detection**.

**Design Philosophy: Rule-Based, Not Black-Box**

We made a controversial decision: we use a **transparent, rule-based algorithm** instead of machine learning.

Why? Three reasons:

1. **Transparency**: Users can see *exactly* how their score is calculated
2. **Predictability**: Same inputs always produce same output (critical for mental health)
3. **Explainability**: We can point to specific factors (meetings, tasks, sentiment)

Machine learning would give us a number with no explanation. "Your burnout score is 73." *Why?* "The neural network said so." Not acceptable.

**The Scoring Algorithm**

**[Show scoring diagram]**

Our burnout score (0-100) combines two dimensions:

```
Burnout Score = (Workload Score × 0.6) + (Sentiment Score × 0.4)
```

**Why 60/40?** Research by Maslach & Leiter (2016) shows workload is the primary predictor of burnout, but emotional exhaustion is a critical moderator. The 60/40 split reflects this empirical finding.

**[Reference: Chapter 5, Burnout Scoring Formula]**

**1. Workload Score (60%)**

We calculate three sub-components:

```
Workload = (Task Overload × 0.5) + (Time Pressure × 0.3) + (Meeting Density × 0.2)
```

**Task Overload:**
- Count active tasks
- Compare to *user's personal baseline* (learned over 2 weeks)
- Formula: `(current_tasks / baseline_tasks) × 100`
- Example: 45 tasks vs 30 baseline = 150% → High overload

**Time Pressure:**
- Calculate upcoming deadlines (next 7 days)
- Weight by priority: High priority × 3, Medium × 2, Low × 1
- Example: 5 high-priority tasks due tomorrow = Extreme pressure

**Meeting Density:**
- Sum meeting hours per day
- Thresholds based on Leiter & Maslach (2005):
  - <2 hours: Healthy
  - 2-4 hours: Moderate
  - >4 hours: Critical

**2. Sentiment Score (40%)**

We analyze chat messages with the AI Companion:

- Extract emotion words using LIWC (Linguistic Inquiry and Word Count)
- Classify tone: Positive, Neutral, Negative
- Track trend over time (is it getting worse?)

Example sentiment indicators:
- "I'm exhausted" → Negative
- "Can't handle this anymore" → Very negative
- "Feeling good about today" → Positive

**Baseline Learning**

The system learns *your* normal over the first 2 weeks:
- Average task count
- Typical meeting load
- Baseline productivity

Then it calculates deviations:
- 1.2x baseline = Elevated (Score: 41-60)
- 1.5x baseline = Critical (Score: 61+)

**This is personalized.** 50 tasks might be normal for a project manager but overwhelming for a junior developer.

**Real-World Example:**

```
User: Ahmed (Senior Engineer)
Baseline (learned):
- Tasks: 30 active tasks
- Meetings: 2 hours/day
- Sentiment: Neutral-positive

Current Week:
- Tasks: 47 (1.57x baseline) → Task overload: 78/100
- Meetings: 6 hours tomorrow → Meeting density: 85/100
- Sentiment: "Feeling overwhelmed, can't sleep" → Sentiment: 70/100

Calculation:
Workload = (78×0.5) + (85×0.3) + (70×0.2) = 78.5
Sentiment = 70

Final Score = (78.5×0.6) + (70×0.4) = 75.1

Result: CRITICAL BURNOUT RISK
```

**[Show example burnout screen from Chapter 4]**

The app displays:
- Score: 75
- Level: Critical (red indicator)
- Top factors: Meeting overload (85), Task volume (78)
- Trend: ↑ 12% from last week

This triggers the recommendation engine, which we'll discuss next."

---

## SLIDE 26-28: AI Service #2 - RAG Recommendation Engine
**[Duration: 4-5 min]**

**Visuals:**
- **[FIGURE: Chapter 6 - RAG recommendation pipeline]**
- **[FIGURE: Example recommendation cards from app]**
- Vector similarity search visualization

**Speaker (AI Team - You):**

"When we detect burnout, we don't just show a number. We provide **actionable, personalized strategies** using RAG.

**The Recommendation Pipeline (5 Stages)**

**[Show RAG pipeline diagram]**

**Stage 1: Context Assembly**

We gather user context:
```python
context = {
    "burnout_score": 75,
    "top_factors": ["meeting_overload", "task_volume"],
    "user_profile": {
        "role": "Senior Engineer",
        "seniority": "Senior",
        "can_delegate": False,
        "manages_team": True
    },
    "calendar_next_week": [
        "6-hour meeting day tomorrow",
        "Presentation to executives Friday"
    ]
}
```

**Stage 2: Vector Retrieval**

We convert the context to an embedding and search our knowledge base:

```python
query_embedding = voyage_ai.embed(
    "Senior engineer with meeting overload, cannot delegate, manages team"
)

# Vector similarity search in PGVector
top_strategies = db.query(
    "SELECT * FROM research_strategies
     ORDER BY embedding <-> query_embedding
     LIMIT 10"
)
```

This retrieves research-backed strategies relevant to this specific situation.

**Stage 3: Relevance Filtering**

Not all strategies apply to everyone:

❌ **Skip**: "Delegate routine tasks to junior team members"
*Why?* User's profile says `can_delegate: False`

✓ **Keep**: "Block 2-hour focus periods for deep work"
*Why?* Applicable to senior engineers with meeting overload

❌ **Skip**: "Discuss workload reduction with your manager"
*Why?* User manages a team (they *are* the manager)

✓ **Keep**: "Decline low-priority meetings this week"
*Why?* Directly addresses meeting overload

This filtering happens via LLM reasoning:

```
You are a productivity advisor. Given the user's constraints,
filter these 10 strategies to only those that are:
1. Actionable given their role and constraints
2. Address their top burnout factors
3. Realistic for this week's calendar
```

**Stage 4: Personalization**

We don't give generic advice. We make it *specific*:

Generic strategy:
> "Take regular breaks to prevent burnout."

Personalized recommendation:
> "Your calendar shows 6 hours of meetings tomorrow. Block 10:30-10:45am
> and 3:00-3:15pm as 'Focus Breaks.' Research shows even 15-minute breaks
> reduce meeting fatigue by 35% (Microsoft, 2021). These slots fall between
> your morning standup and afternoon planning sessions."

Notice:
- Specific time slots (based on actual calendar)
- Quantified benefit (35% reduction)
- Research citation (Microsoft, 2021)
- Contextual placement (between existing meetings)

**Stage 5: Ranking and Presentation**

We rank recommendations by:
- **Relevance score** (vector similarity)
- **Urgency** (addresses critical factors first)
- **Feasibility** (easy to implement = higher priority)

Final output: **Top 5 personalized strategies**

**[Show recommendation cards from Chapter 4]**

Example recommendations for Ahmed:

1. ⭐⭐⭐⭐⭐ **Decline 2 Low-Priority Meetings This Week**
   - Tomorrow's 2pm sync is informational (you're optional)
   - Thursday's retrospective can be async
   - Saves 2 hours for deep work

2. ⭐⭐⭐⭐ **Block 2-Hour Focus Periods**
   - Friday 9am-11am (before executive presentation)
   - Prepare without interruption
   - Newport (2016): 40% productivity increase

3. ⭐⭐⭐ **Redistribute Tasks to Team**
   - You have 47 active tasks
   - 8 are routine code reviews
   - Suggestion: Rotate code review responsibility weekly

Users can:
- ✅ **Try Out** (apply to calendar immediately)
- 👎 **Not Helpful** (remove and request new recommendation)
- 📋 **Apply All** (batch accept all strategies)

**The Impact:**

Traditional advice: "You should take breaks."
→ Generic, hard to implement, no clear action

Our RAG recommendations: "Block 10:30-10:45am tomorrow as a focus break between your standup and planning session. Research shows this reduces meeting fatigue by 35%."
→ Specific, calendar-integrated, research-backed, one-click action

This is the power of RAG + context-aware AI."

---

## SLIDE 29-31: AI Service #3 - Multi-Modal Task Extraction
**[Duration: 3-4 min]**

**Visuals:**
- **[FIGURE: Chapter 6 - Task extraction pipeline]**
- Before/after example (audio → structured tasks)
- **[PLACEHOLDER: Demo screenshot of extraction preview]**

**Speaker (AI Team - You):**

"Our third AI service automates one of the most tedious parts of productivity: turning unstructured information into actionable tasks.

**The Problem:**

You attend a 1-hour meeting. Afterward, you spend 15 minutes typing out:
- Action items
- Deadlines
- Assigned responsibilities

Or you receive a PDF with project requirements and manually extract:
- Deliverables
- Due dates
- Dependencies

This is **busywork**. Let AI handle it.

**Multi-Modal Support:**

We extract tasks from four input types:

**1. Audio (Meetings, Voice Notes)**

Pipeline:
```
Audio File → AssemblyAI Transcription → LLM Task Extraction → Structured Output
```

Example:
> **Audio**: "Hey team, we need to finalize the Q4 budget by Friday. Sarah, can you compile the department expenses? And John, send me those vendor quotes by Wednesday."

Extracted tasks:
```json
[
  {
    "title": "Finalize Q4 budget",
    "due_date": "2024-11-15",
    "priority": "high",
    "assigned_to": "Team"
  },
  {
    "title": "Compile department expenses",
    "due_date": "2024-11-15",
    "assigned_to": "Sarah"
  },
  {
    "title": "Send vendor quotes",
    "due_date": "2024-11-13",
    "assigned_to": "John"
  }
]
```

**2. PDFs (Documents, Emails)**

We extract text and identify:
- Deliverables ("submit report," "review document")
- Deadlines ("by next Friday," "November 15th")
- Priorities (marked as "urgent" or "high priority")

**3. Images (Whiteboard Photos, Screenshots)**

OCR → Text extraction → Task parsing

Useful for:
- Brainstorming session whiteboards
- Screenshots of Slack messages
- Handwritten to-do lists

**4. Video (Lecture Recordings)**

Transcribe → Extract key points → Generate tasks

Example: 3-hour lecture → "Review chapter 5," "Complete assignment 3 by Monday"

**The LLM Extraction Prompt**

This is where prompt engineering matters:

```
You are a task extraction specialist. Given a transcript, extract ALL action items.

For each task, provide:
1. Title (concise, actionable verb phrase)
2. Due date (parse relative dates: "next Friday" → calculate actual date)
3. Priority (high/medium/low - infer from language like "urgent," "ASAP")
4. Category (work/personal/study - infer from context)
5. Assigned to (if mentioned)

Rules:
- If no deadline mentioned, return null (don't invent dates)
- If priority unclear, default to "medium"
- Only extract ACTIONABLE items (not informational statements)

Output format: JSON array of task objects
```

**Structured Output Validation**

We use Pydantic to validate LLM output:

```python
class ExtractedTask(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    due_date: Optional[datetime] = None
    priority: Literal["low", "medium", "high"] = "medium"
    category: Literal["work", "personal", "study"] = "work"
    assigned_to: Optional[str] = None
```

If the LLM generates invalid JSON or missing required fields, we reject it and retry.

**User Workflow:**

1. **Upload** audio file (or PDF/image)
2. **Wait** 5-30 seconds for processing (with progress indicator)
3. **Preview** extracted tasks
4. **Edit** any task (fix dates, adjust priority)
5. **Select** which tasks to add (checkboxes)
6. **Confirm** → Tasks added to your list

**[Show preview screen from Chapter 4]**

Critical: Users *always* review before confirming. We don't silently add tasks - that would break trust.

**Accuracy:**

Through prompt engineering iterations, we achieved:
- **98% extraction recall** (captures all mentioned tasks)
- **92% precision** (rarely invents non-existent tasks)
- **85% date parsing accuracy** (correctly interprets "next Friday," "two weeks from now")

This transforms hours of manual data entry into seconds of AI processing."

---

## SLIDE 32-34: AI Service #4 - AI Companion (LangGraph)
**[Duration: 3-4 min]**

**Visuals:**
- **[FIGURE: Chapter 6 - LangGraph state machine]**
- **[FIGURE: Chat interface from Chapter 4]**
- Conversation context example

**Speaker (AI Team - You):**

"Our fourth AI service is the **AI Companion** - a conversational assistant for emotional support and productivity coaching.

**Why Stateful Conversations Matter**

Traditional chatbots reset after every message:

> **User**: "I'm feeling overwhelmed."
> **Bot**: "I'm sorry to hear that. How can I help?"
> **User**: "What should I do about it?"
> **Bot**: "About what?"  ← Lost context

This is frustrating. Real conversations have *memory*.

**Enter LangGraph: Stateful AI Conversations**

LangGraph is a framework for building stateful, multi-turn conversations.

**[Show state machine diagram]**

Our companion has three conversational states:

**State 1: Greeting & Context Gathering**
- Welcomes user
- Asks about their day
- Detects emotional tone

**State 2: Problem Exploration**
- User describes challenges
- Companion asks clarifying questions
- Maintains conversation history

**State 3: Action Planning**
- Suggests specific actions
- Can create tasks via natural language
- Offers to check burnout score

**Conversation Context Persistence**

We store conversation history in the database:

```python
class ConversationHistory(BaseModel):
    user_id: int
    messages: List[Message]  # User + assistant messages
    current_state: str       # greeting | exploring | planning
    detected_issues: List[str]  # ["work_overload", "sleep_deprivation"]
    created_at: datetime
```

This enables:
- **Multi-session memory**: "Last week you mentioned difficulty sleeping. How's that going?"
- **Context-aware responses**: Knows user's current burnout score, upcoming deadlines
- **Personalization**: Remembers user preferences ("You prefer morning focus blocks")

**Example Conversation:**

> **User**: "I have a huge presentation Friday and I'm panicking."

> **Companion**: "I see you have a presentation to executives on Friday at 2pm. What's causing the panic - preparation time or presentation anxiety?"

> **User**: "I haven't started preparing and I have meetings all week."

> **Companion**: "Looking at your calendar, you have 6 hours of meetings tomorrow. Let me suggest a plan:
>
> 1. **Block Thursday 9am-12pm for prep** (I can add this to your calendar)
> 2. **Decline tomorrow's 2pm sync** (you're marked optional)
> 3. **Use the Pomodoro technique** during your prep block
>
> Would you like me to create these calendar blocks?"

> **User**: "Yes please."

> **Companion**: "Done. I've blocked Thursday morning and sent a decline for tomorrow's meeting. You now have 3 focused hours for preparation. Want me to create task reminders too?"

Notice:
- **Calendar integration**: Companion accesses real calendar data
- **Proactive suggestions**: Identifies specific meetings to decline
- **Action execution**: Creates calendar blocks on user's behalf
- **Natural flow**: Feels like talking to a human assistant

**Safety and Boundaries**

We're not therapists. The companion:
✓ Provides productivity coaching
✓ Offers emotional support
✓ Suggests stress-reduction techniques

✗ Does NOT diagnose mental health conditions
✗ Does NOT replace professional therapy
✗ Escalates serious concerns ("I'm having suicidal thoughts" → directs to crisis hotline)

**Technical Implementation:**

- **LangGraph** for state management
- **Groq Llama 3.1** for language understanding
- **PGVector** for semantic search of past conversations
- **Context window**: 8,000 tokens (enough for 20-30 message exchanges)

The AI Companion transforms Sentry AI from a *tool* into a *partner* in burnout prevention."

---

## SLIDE 35-37: AI Service #5 - Notebook Library (RAG for Learning)
**[Duration: 3-4 min]**

**Visuals:**
- **[FIGURE: Chapter 6 - Notebook RAG architecture]**
- **[FIGURE: Chapter 4 - Notebook screens (library, chat, AI studio)]**
- Example flashcard generation

**Speaker (AI Team Member):**

"Our final AI feature addresses a specific use case: students and knowledge workers managing large amounts of study material.

**The Problem:**

You're preparing for an exam. You have:
- 10 lecture PDFs (300 pages total)
- 5 hours of recorded lectures
- 20 research articles
- Handwritten notes

Traditional approach:
- Read everything
- Manually create flashcards
- Hope you remember the important parts

This takes **hours** and you might miss key concepts.

**Notebook Library: Your Personal Knowledge Assistant**

**[Show notebook architecture]**

**Step 1: Source Upload**

Users create a notebook and add sources:
- PDFs (lecture slides, textbooks)
- Audio (lecture recordings)
- Web links (articles, documentation)
- Images (diagrams, charts)
- Text snippets (copy-pasted notes)

**Step 2: Content Processing**

We extract and chunk the content:

```python
# For PDFs
text = extract_pdf_text(file)
chunks = split_into_chunks(text, chunk_size=500)  # 500 words each

# For audio
transcript = assemblyai.transcribe(audio_file)
chunks = split_into_chunks(transcript)

# For each chunk
embedding = voyage_ai.embed(chunk)
db.store(chunk_text, embedding, source_metadata)
```

Result: Searchable knowledge base of all your study materials.

**Step 3: Interactive Chat**

Users ask questions, get answers grounded in their sources:

> **User**: "What are the three components of burnout according to Maslach?"

> **Notebook** (RAG retrieval):
> "Based on your uploaded lecture PDF 'Organizational Psychology - Week 3':
>
> Maslach identifies three components:
> 1. **Emotional Exhaustion** - feeling drained of emotional resources
> 2. **Depersonalization** - cynical attitudes toward work
> 3. **Reduced Personal Accomplishment** - feeling ineffective
>
> Source: Lecture 3, slide 12"

Notice the **source citation**. Users can verify the answer.

**Step 4: AI Studio - Generate Study Materials**

This is where it gets powerful. We auto-generate:

**Flashcards:**
```
Q: What are Maslach's three burnout components?
A: 1) Emotional exhaustion 2) Depersonalization 3) Reduced personal accomplishment
```

**Summaries:**
- Chapter summaries (1-page overviews)
- Key concept lists
- Timeline of events (for history courses)

**Quizzes:**
- Multiple choice questions
- True/false statements
- Short answer prompts

All generated using RAG:
1. Retrieve key concepts from notebook
2. LLM generates questions/summaries
3. Validate against source material (no hallucinations)

**Example: Generate Flashcards**

User selects: "Generate flashcards from Chapter 5"

System:
1. Retrieves all chunks from Chapter 5
2. Identifies key concepts (definitions, formulas, important facts)
3. Generates Q&A pairs
4. Creates 20 flashcards in 15 seconds

**[Show flashcard example from Chapter 4]**

Users can:
- Edit generated flashcards
- Export to Anki or Quizlet
- Practice with spaced repetition

**Real-World Use Case:**

Medical student scenario:
- Upload 500 pages of anatomy textbook
- Upload 10 hours of lecture recordings
- Ask: "Explain the cardiovascular system"
- Get: Summary with diagrams from uploaded sources
- Generate: 50 flashcards on cardiovascular concepts
- Study: Using generated quiz questions

Time saved: **20+ hours** of manual note-taking and flashcard creation.

**Why This Matters for Burnout:**

Students face burnout too. Notebook Library:
- Reduces study preparation time
- Improves retention (spaced repetition)
- Lowers anxiety (comprehensive coverage)
- Enables efficient exam prep

By reducing academic stress, we prevent student burnout."

---

## SLIDE 38-39: Integration and Data Flow
**[Duration: 3-4 min]**

**Visuals:**
- **[FIGURE: Chapter 6 - Flutter-Server Integration Sequence Diagram]**
- **[FIGURE: Complete system integration diagram]**
- Data flow animation

**Speaker (Backend + AI Team):**

"Let's step back and see how all these components work together.

**The Integration Story: User Login to Burnout Detection**

**[Show sequence diagram from Chapter 6, Section 7.15]**

Let me walk through what happens when Ahmed opens the app:

**1. Authentication (Backend Services)**

```
Flutter App → POST /auth/login {email, password}
           ← {access_token, refresh_token, user_data}
```

JWT tokens stored locally. All future requests include: `Authorization: Bearer <token>`

**2. Data Synchronization (Backend Services)**

```
Flutter App → GET /integrations/sync
Backend → Google Calendar API (fetch events)
Backend → Trello API (fetch tasks)
Backend → Database (store tasks, events)
           ← {synced: true, new_tasks: 12, new_events: 8}
```

Ahmed's tasks and calendar are now up-to-date.

**3. Burnout Analysis Trigger (AI Services)**

```
Flutter App → POST /burnout/analyze
AI Service → Database (fetch Ahmed's tasks, calendar, chat history)
AI Service → Calculate workload score (78.5)
AI Service → Calculate sentiment score (70)
AI Service → Compute final score (75.1)
AI Service → Database (store analysis)
           ← {score: 75, level: "critical", factors: [...]}
```

**4. Recommendation Generation (AI Services)**

```
Flutter App → GET /recommendations/generate
AI Service → Database (fetch burnout analysis)
AI Service → Vector search (find relevant strategies)
AI Service → Groq LLM (personalize recommendations)
AI Service → Database (store recommendations)
           ← {recommendations: [5 personalized strategies]}
```

**5. Display in UI (Flutter)**

```
BurnoutProvider updates state → UI rebuilds
Dashboard shows: Score 75, Critical level, Top 5 recommendations
```

**Key Integration Patterns:**

**Shared Database:**
- Backend writes tasks → AI reads for burnout analysis
- AI writes recommendations → Backend serves to Flutter
- Zero data duplication, zero sync delays

**JWT Token Flow:**
- Access token expires after 15 minutes
- Dio interceptor detects 401 error
- Automatically refreshes using refresh token
- Retries original request
- User never sees "please log in" error

**Async Communication:**
- All API calls are non-blocking (async/await)
- UI shows loading states
- Background operations don't freeze the app

**[Show complete integration diagram]**

**Data Flow Example: Create Task via Voice**

```
User speaks → Flutter records audio

1. Flutter → AI Service: POST /extract/audio
2. AI Service → AssemblyAI: Transcribe
3. AssemblyAI → AI Service: Transcript
4. AI Service → Groq LLM: Extract tasks
5. AI Service → Flutter: Preview tasks
6. User confirms selection
7. Flutter → Backend: POST /tasks (batch create)
8. Backend → Database: Insert tasks
9. Backend → Flutter: Created task IDs
10. Flutter → UI: Update task list

Next burnout analysis will include these new tasks automatically.
```

This seamless integration creates a **unified experience** across productivity and mental health."

---

## SLIDE 40-42: Conclusion and Impact
**[Duration: 4-5 min]**

**Visuals:**
- Project summary infographic
- Impact metrics
- **[PLACEHOLDER: Business Model Canvas]**
- Future roadmap

**Speaker (Business Team):**

"Let me bring us back to the big picture.

**What We've Built:**

In four months, our team of six has delivered:

**Technical Achievements:**
- ✅ **90+ API endpoints** across Backend and AI Services
- ✅ **30+ mobile screens** with production-ready UI/UX
- ✅ **12 database tables** supporting relational + vector data
- ✅ **5 AI-powered features** using LLMs, RAG, and NLP
- ✅ **~15,000 lines of code** (Flutter + Python)
- ✅ **Integration with 5 external services** (Google, AssemblyAI, Groq, Voyage, Trello)

**Innovation Highlights:**

1. **First System** to combine productivity tracking with AI-driven burnout detection
2. **Transparent Algorithms**: Rule-based scoring users can understand
3. **Context-Aware AI**: Recommendations grounded in real calendar data
4. **Multi-Modal Intelligence**: Extract tasks from audio, PDFs, images, video
5. **Stateful Companion**: LangGraph-powered conversational AI with memory

**The Impact:**

**Individual Level:**
- **Early Detection**: Identify burnout *before* it becomes severe
- **Personalized Intervention**: Strategies tailored to role, constraints, schedule
- **Time Savings**: Automate task extraction, study material generation
- **Sustainable Productivity**: Maximize output without sacrificing well-being

**Organizational Level:**
- **Reduce Turnover**: Prevent burnout-driven resignations (avg. cost: $15,000 per employee)
- **Improve Performance**: Healthy employees are 31% more productive
- **Lower Healthcare Costs**: Burnout-related illness costs $4,400 per employee annually
- **Data-Driven Management**: Aggregate team burnout trends (anonymized)

**Societal Level:**
- **Scalable Mental Health Support**: AI enables 24/7 availability
- **Evidence-Based Interventions**: Grounded in research, not generic advice
- **Preventive Care**: Address burnout before it requires clinical intervention
- **Democratized Access**: Mobile-first design reaches users without desktop computers

**Business Model:**

**[Show Business Model Canvas placeholder]**

**Freemium Model:**

**Free Tier:**
- Burnout analysis (1x per week)
- Basic task management
- AI Companion (10 messages/day)
- 1 notebook with 5 sources

**Premium Tier ($9.99/month):**
- Unlimited burnout analysis
- Advanced recommendations
- Unlimited AI Companion
- Unlimited notebooks
- Integration with Google Calendar, Trello
- Team features (for managers)

**Enterprise Tier (Custom pricing):**
- Team burnout dashboards
- Admin controls
- SSO integration
- Dedicated support
- Custom branding

**Target Market:**
- **Primary**: Knowledge workers (developers, designers, consultants) aged 25-45
- **Secondary**: Students (university, graduate school)
- **Enterprise**: HR departments, employee wellness programs

**Market Size:**
- **TAM**: 1 billion knowledge workers globally
- **SAM**: 100 million tech-savvy professionals in developed markets
- **SOM**: 1 million users in first 3 years (1% of SAM)

**Revenue Projection:**
- Year 1: 10,000 users (50% conversion to premium) → $600K revenue
- Year 2: 100,000 users (40% conversion) → $4.8M revenue
- Year 3: 1,000,000 users (30% conversion) → $36M revenue

**Competitive Advantage:**

We're not competing with:
- **Productivity apps** (we have mental health features they lack)
- **Mental health apps** (we have productivity features they lack)

We're creating a **new category**: AI-powered sustainable productivity.

**Challenges and Limitations:**

We're transparent about what we haven't solved:

**Technical:**
- Rule-based scoring may miss complex patterns (future: ML models)
- Limited integrations (future: Outlook, Slack, Asana)
- Local deployment only (future: cloud infrastructure)

**Validation:**
- No longitudinal user studies (future: clinical trials)
- Small test user base (10 users) (future: 1000+ beta users)

**Ethical:**
- Privacy concerns (storing sensitive work data)
- AI bias (recommendations may favor certain work styles)
- Over-reliance risk (users may defer to AI instead of self-awareness)

We've designed with these in mind (data encryption, bias testing, transparency), but acknowledge they require ongoing attention."

---

## SLIDE 43: Future Roadmap
**[Duration: 2 min]**

**Visuals:**
- Timeline showing next 12 months
- Feature preview mockups

**Speaker (Team Lead):**

"Looking ahead, our roadmap includes:

**Q1 2025: Foundation**
- ☑️ Deploy to cloud (AWS/Google Cloud)
- ☑️ Add 1000 beta users
- ☑️ Implement analytics dashboard (user retention, feature usage)

**Q2 2025: Expansion**
- ☑️ Machine learning burnout prediction model
- ☑️ Microsoft Outlook integration
- ☑️ Slack integration (detect burnout from chat patterns)
- ☑️ iOS App Store launch

**Q3 2025: Enterprise**
- ☑️ Team dashboard for managers
- ☑️ Aggregate (anonymized) burnout trends
- ☑️ Workload redistribution suggestions
- ☑️ HR integration (BambooHR, Workday)

**Q4 2025: Advanced Features**
- ☑️ Wearable integration (Apple Watch, Fitbit)
- ☑️ Sleep quality correlation
- ☑️ Heart rate variability analysis
- ☑️ Reinforcement learning for recommendation optimization

**Long-Term Vision:**

We envision Sentry AI as the **operating system for sustainable productivity** - a platform that:
- Prevents burnout before it starts
- Optimizes team performance while protecting mental health
- Makes evidence-based wellness accessible to everyone
- Redefines what 'productive' means (output *and* well-being)

**Call to Action:**

We're ready to:
1. **Deploy** the production system
2. **Recruit** beta users for validation studies
3. **Secure** seed funding ($500K) for cloud infrastructure and team expansion
4. **Partner** with organizations interested in employee wellness

This is just the beginning."

---

## SLIDE 44: Team Contributions
**[Duration: 1 min]**

**Visuals:**
- Team photo
- Contribution breakdown chart

**Speaker (Team Lead):**

"Before we conclude, I want to acknowledge our team's incredible work:

**UI/UX + Frontend (2 members):**
- Designed 30+ screens in Figma
- Implemented glassmorphism UI in Flutter
- Created responsive, accessible mobile experience

**Backend (1 member):**
- Built 50+ RESTful API endpoints
- Designed scalable database schema
- Implemented OAuth authentication

**AI Services (2 members):**
- Developed 4 AI-powered features
- Implemented RAG recommendation system
- Built multi-modal task extraction
- Created stateful AI companion

**Business + Strategy (1 member):**
- Validated market need
- Designed business model
- Analyzed competitive landscape
- Projected financial viability

Over **1,200 hours** of collective effort. Dozens of iterations. Countless debugging sessions. This is the result of true collaboration."

---

## SLIDE 45: Q&A
**[Duration: 5-10 min]**

**Visuals:**
- "Questions?" slide
- Team contact information

**Speaker (Team Lead):**

"Thank you for your attention. We're now happy to answer any questions about:
- Technical architecture
- AI implementation
- UI/UX design decisions
- Business model
- Future plans

Our team is here to provide detailed answers from our respective domains."

---

## APPENDIX: Anticipated Questions and Answers

**Q: Why rule-based burnout scoring instead of machine learning?**
**A (AI Team):** Transparency and trust. Users need to understand *why* their score is 75. "The neural network says so" isn't acceptable for mental health. We chose interpretability over marginal accuracy gains. That said, our future roadmap includes ML for pattern detection while maintaining explainability through SHAP values.

**Q: How do you ensure AI doesn't hallucinate harmful advice?**
**A (AI Team):** Three safeguards: (1) RAG grounds responses in research papers, not general knowledge, (2) We validate all recommendations against user constraints, (3) We don't diagnose conditions - only suggest productivity strategies. For emotional support, the companion directs serious concerns to professional resources.

**Q: What about data privacy? You're storing sensitive work information.**
**A (Backend):** All data encrypted at rest (AES-256) and in transit (TLS). JWT tokens expire after 15 minutes. We're GDPR-compliant with user data deletion on request. For enterprise, we offer on-premise deployment where data never leaves the organization's infrastructure.

**Q: How accurate is the task extraction?**
**A (AI Team):** Current metrics: 98% recall (captures all mentioned tasks), 92% precision (rarely invents tasks), 85% date parsing accuracy. We achieved this through iterative prompt engineering and structured output validation. Users always preview before confirming, so errors are caught.

**Q: What's your user acquisition strategy?**
**A (Business):** Phase 1: University students (captive audience, high burnout rates). Phase 2: Tech workers via Product Hunt, HackerNews. Phase 3: Enterprise partnerships with HR departments. We'll offer free tier indefinitely - conversion to premium happens when users see value.

**Q: How will you handle scalability with cloud costs?**
**A (Backend + AI):** We've architected for horizontal scaling (stateless services). Initial deployment: 2 backend instances, 1 AI instance, managed PostgreSQL. At 10,000 users: ~$500/month cloud costs. At 100,000 users: ~$3,000/month. LLM costs are our biggest variable - we chose Groq specifically for 15x cost savings vs OpenAI.

---

**Total Duration: ~45-47 minutes**
**Reserve: 3-5 minutes for Q&A**

---

## Figure Reference Checklist

**Figures to Include:**

- [x] Chapter 1, Figure 1.1 - Burnout Statistics
- [x] Chapter 2 - RAG System Architecture
- [x] Chapter 4, Section 5.2 - Color Palette
- [x] Chapter 4 - Onboarding Screens (3 screens)
- [x] Chapter 4 - Dashboard
- [x] Chapter 4 - Burnout Score Screen
- [x] Chapter 4, Figure 5.27 - Complete Wireframe
- [x] Chapter 4, Section 5.8.3 - Flutter Project Structure
- [x] Chapter 5 - System Architecture (3-tier)
- [x] Chapter 5 - ER Diagram
- [x] Chapter 5 - Compact Architecture Diagram
- [x] Chapter 6 - Burnout Scoring Algorithm Flowchart
- [x] Chapter 6 - RAG Recommendation Pipeline
- [x] Chapter 6 - Task Extraction Pipeline
- [x] Chapter 6 - LangGraph State Machine
- [x] Chapter 6 - Notebook RAG Architecture
- [x] Chapter 6, Section 7.15 - Flutter-Server Integration Sequence Diagram

**Placeholders Needed:**

- [ ] Global burnout prevalence map/timeline
- [ ] Gap diagram (productivity vs mental health apps)
- [ ] Venn diagram (Productivity + Mental Health + AI)
- [ ] Business Model Canvas
- [ ] Future roadmap timeline
- [ ] Team photo/contribution chart

---

**Good luck with your presentation! You've built something remarkable. 🚀**
