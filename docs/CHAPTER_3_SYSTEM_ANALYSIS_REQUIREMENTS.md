# 3. SYSTEM ANALYSIS AND REQUIREMENTS

This chapter presents an analysis of the current approaches to burnout management, identifies their limitations, and defines the requirements for the Sentry AI system. The analysis covers feasibility assessment, functional and non-functional requirements, and provides use case models to illustrate system interactions.

---

## 3.1 Current System Analysis

Burnout management today relies on fragmented, disconnected approaches that fail to address the problem comprehensively.

**Manual Self-Assessment** remains the most common approach, where individuals periodically complete burnout questionnaires such as the Maslach Burnout Inventory. However, these assessments provide only static snapshots without continuous monitoring. They require conscious effort from users who are already overwhelmed, leading to inconsistent tracking and late detection of burnout symptoms.

**Generic Wellness Applications** like Headspace and Calm have gained popularity for stress management. While these apps provide valuable meditation and relaxation content, they operate in complete isolation from the user's actual work life. They cannot see your calendar, don't know about your deadlines, and provide the same generic advice to everyone regardless of their specific situation. A recommendation to "take deep breaths" offers little help when you have three back-to-back meetings and an urgent deadline.

**Productivity Tools** such as Todoist, Asana, and Google Calendar help users organize their work but remain completely unaware of health implications. These tools will happily let you schedule 12 hours of meetings in a single day without any warning. They track tasks without considering whether the workload is sustainable, creating a disconnect between productivity management and well-being.

**Organizational Wellness Programs** typically consist of annual surveys and generic wellness initiatives. By the time an annual survey identifies burnout, employees have often been suffering for months. These programs are reactive rather than proactive, and their one-size-fits-all approach fails to address individual needs.

The fundamental problem with all these approaches is fragmentation. Burnout results from the interaction of multiple factors—workload, deadlines, meetings, emotional state, personal constraints—yet existing solutions analyze these factors in isolation or ignore them entirely.

---

## 3.2 Proposed System Analysis

Sentry AI addresses these limitations through an integrated, AI-powered approach that connects the dots between workload, emotional state, and personalized intervention.

**Automated Data Collection** eliminates the burden of manual tracking. The system integrates directly with task databases and calendar systems, automatically calculating metrics like meeting density, overdue tasks, and workload trends. Users don't need to fill out questionnaires or manually log their activities—the system understands their workload by observing their actual commitments.

**Multi-Dimensional Analysis** combines quantitative and qualitative signals. The system doesn't just count tasks; it analyzes emotional check-ins and diary entries to understand how users feel about their work. This combination provides a more accurate picture of burnout risk than either approach alone.

**Evidence-Based Recommendations** ensure that every suggestion is grounded in validated psychological research. The RAG architecture retrieves strategies from a curated guidebook rather than generating generic advice. When the system recommends time-blocking or meeting batching, it's drawing from proven techniques—not hallucinating plausible-sounding but unsupported suggestions.

**Event-Specific Guidance** transforms abstract advice into immediate action. Instead of telling users to "reduce meetings," Sentry AI identifies specific meetings that can be cancelled or shortened. Instead of suggesting "delegate some tasks," it identifies which tasks can be delegated and to whom. This specificity makes recommendations actionable rather than aspirational.

**Conversational Support** through the AI companion provides emotional support alongside practical recommendations. Users can share how they're feeling, ask questions about their workload, or create tasks through natural conversation. This human-like interaction makes the system more accessible and supportive.

---

## 3.3 Feasibility Study

### Technical Feasibility

The system leverages mature, well-documented technologies. Large Language Models are accessed through the Groq API, providing fast inference for text processing and recommendation generation. Vector similarity search uses PostgreSQL with the PGVector extension, a production-ready solution for semantic retrieval. Audio transcription relies on AssemblyAI, a commercial service with high accuracy. Document processing uses Unstructured.io, an open-source library for parsing various document formats. The FastAPI framework provides high-performance REST endpoints with automatic documentation.

All required technologies are either open-source or available through affordable API services with comprehensive documentation and active community support.

### Operational Feasibility

Users interact with the system through familiar interfaces—chat conversations, file uploads, and dashboard views. The system integrates with existing workflows rather than replacing them, allowing gradual adoption. Users can start with one feature (such as the AI companion) and expand usage over time. Minimal training is required since the interface follows established UX patterns.

### Economic Feasibility

Cloud deployment enables pay-per-use pricing, making the system cost-effective for organizations of any size. Open-source components minimize licensing costs. API costs for LLM inference and audio transcription scale with usage, avoiding large upfront investments. The potential return on investment through reduced burnout-related productivity loss and turnover justifies the operational costs.

---

## 3.4 Functional Requirements

This section describes what the system does, organized by major functional areas.

### User Authentication and Management

The system provides secure user registration and authentication. Users can create accounts using email and password, with support for OAuth providers (Google, Facebook, Apple) for convenient single sign-on. Authentication uses JWT tokens that securely identify users across all API requests. Password reset functionality allows account recovery via email. User sessions have configurable expiration periods to balance security with convenience.

### Task and Calendar Management

Users can create, view, update, and delete tasks with rich metadata including title, description, priority level, due date, and current status. The system distinguishes between regular tasks and calendar events (meetings), storing additional information for meetings such as start time, end time, attendees, and whether attendance is optional. Tasks can be marked as delegatable, enabling the recommendation engine to suggest delegation when appropriate. The system tracks task completion history and calculates statistics including total active tasks, overdue items, and tasks due within the current week.

### Burnout Analysis Service

The burnout analysis engine processes both quantitative and qualitative data to assess burnout risk. Quantitative analysis examines workload metrics including task counts, meeting hours, deadline density, and back-to-back meeting patterns. Qualitative analysis processes emotional check-ins, diary entries, and conversation sentiment to detect emotional exhaustion and stress indicators.

The system combines these analyses using a weighted formula (60% workload, 40% sentiment) to produce a final burnout score. This score is classified into three levels: GREEN indicates healthy status, YELLOW signals elevated risk requiring attention, and RED indicates critical burnout requiring immediate intervention. The system identifies primary contributing factors, tracks score trends over time, and generates alerts when burnout reaches dangerous levels.

### Recommendation Generation Service

The recommendation engine uses Retrieval-Augmented Generation to produce personalized, evidence-based guidance. When generating recommendations, the system first queries the vector database to retrieve relevant strategies from the curated guidebook based on the user's burnout profile and identified stress factors.

The retrieved strategies are combined with the user's context—their profile, preferences, constraints, current calendar events, and task list—to construct a prompt for the language model. The LLM then generates recommendations that reference specific events and tasks, transforming generic strategies into actionable guidance tailored to the user's situation.

Recommendations respect user preferences (accepted and avoided recommendation types) and constraints (such as upcoming deadlines or blocked periods). Each recommendation includes clear action steps, priority level, and expected outcomes.

### AI Companion Service

The AI companion provides a conversational interface for emotional support, information queries, and task management. When users send messages, the system classifies their intent into categories: emotional support, task queries, burnout queries, task creation, or general conversation.

For emotional content, the companion responds empathetically while saving the entry to the qualitative data table for sentiment analysis. For task queries, it retrieves statistics and provides summaries of the user's workload. For burnout queries, it explains the user's current status and contributing factors. For task creation requests, it extracts task details from natural language and creates entries in the database.

The companion also accepts audio messages, transcribing speech to text before processing. This multi-modal input support allows users to interact in whatever way is most convenient for their situation.

### Multi-Modal Task Extraction Service

The task extraction service processes diverse input formats to automatically populate the user's task database. Supported formats include audio recordings (meeting recordings, voice memos), documents (PDF reports, Word documents), images (screenshots, photos of whiteboards), handwritten notes (photographed notebooks, scanned pages), and plain text files.

The system automatically detects the input type and selects the appropriate processing pipeline. Audio files are transcribed using AssemblyAI. Documents are parsed using Unstructured.io to extract text, tables, and embedded images. Images and handwritten notes are processed using OCR (Tesseract) and vision models. All extracted text is then analyzed by the LLM to identify and structure task information.

Extracted tasks are validated against a defined schema ensuring required fields are present and values are within acceptable ranges. Valid tasks are saved to the database while validation failures are logged as warnings without stopping the overall process.

### Notebook Library Service

The notebook library allows users to create personal knowledge repositories. Users can create notebooks and upload documents which are processed, chunked, and embedded for semantic search. The chat feature enables users to ask questions about their uploaded content, with the system retrieving relevant passages to generate accurate, grounded responses. A quiz generation feature creates study materials from notebook content.

### User Profile and Preferences

The system maintains detailed user profiles to enable personalization. Basic profile information includes name, role, team size, and delegation capabilities. Preference settings allow users to specify their preferred communication style and indicate which recommendation types they accept or wish to avoid.

Constraint management tracks time-bound restrictions such as upcoming deadlines, blocked periods, or delegation limitations. The behavioral learning module analyzes historical data to establish user-specific baselines, identifying their normal workload patterns and personal stress triggers. This learned information improves the accuracy of burnout detection and the relevance of recommendations over time.

---

## 3.5 Non-Functional Requirements

Beyond functional capabilities, the system must meet quality standards for performance, security, scalability, and usability.

### Performance

Response time is critical for user experience. Simple API queries should return within 500 milliseconds. Burnout analysis, which involves database queries and score calculation, should complete within 3 seconds. Recommendation generation, requiring RAG retrieval and LLM inference, should complete within 5 seconds. AI companion responses should arrive within 5 seconds to maintain conversational flow.

Task extraction times vary by input type: text files process within 3 seconds, audio recordings (5 minutes) within 30 seconds, and documents (10 pages) within 60 seconds. The system should support at least 100 concurrent users without performance degradation.

### Security

All API endpoints require JWT authentication, ensuring only authorized users access the system. Role-based access control restricts users to their own data—no user can view another user's tasks, burnout analysis, or conversations. All communications use HTTPS encryption. Passwords are hashed using bcrypt with appropriate salt rounds before storage.

Input validation prevents injection attacks by sanitizing all user-provided data. JWT tokens expire after a configurable duration (default 24 hours) to limit exposure from compromised tokens. Mental health data receives additional protection with encryption at rest.

### Scalability

The architecture supports horizontal scaling to handle growing user bases. API services are stateless, allowing load balancers to distribute requests across multiple server instances. PostgreSQL supports read replicas for increased query capacity. Long-running operations (such as document processing) execute asynchronously to prevent blocking.

### Availability

The system targets 99% uptime availability. Planned maintenance windows are limited to 4 hours per month during off-peak hours. When external services (LLM API, transcription service) are temporarily unavailable, the system degrades gracefully rather than failing completely. Daily database backups with 30-day retention protect against data loss.

### Usability

The user interface follows established design patterns, enabling users to complete primary tasks without consulting documentation. AI-generated responses are clear, actionable, and free of technical jargon. Error messages explain what went wrong and suggest resolution steps. The interface is accessible according to WCAG 2.1 AA guidelines and functions correctly on mobile devices.

### Maintainability

The modular architecture keeps services loosely coupled and independently deployable. All public APIs include documentation with descriptions and examples. Comprehensive logging supports debugging and monitoring. Configuration uses environment variables rather than hardcoded values, enabling deployment across different environments without code changes.

---

## 3.6 Use Case Diagrams

The following diagrams illustrate the primary interactions between users and the system.

> **Figure 3.1: Main System Use Case Diagram**
>
> *This diagram should show the User actor connected to primary use cases: Register & Login, Manage Tasks, Analyze Burnout, View Dashboard, Get Recommendations, Chat with AI Companion, Extract Tasks from Files, and Submit Diary Entry. External system actors (Groq AI, Voyage AI, AssemblyAI) connect to relevant processing use cases.*

> **Figure 3.2: AI Companion Use Case Diagram**
>
> *This diagram should show the User actor connected to: Send Text Message, Send Audio Message, Get Emotional Support, Query Task Statistics, Query Burnout Status, Create Task via Natural Language, and Submit Diary Entry. Internal use cases include Classify Intent, Perform Sentiment Analysis, and Generate Response.*

> **Figure 3.3: Task Extraction Use Case Diagram**
>
> *This diagram should show the User actor connected to upload use cases for different file types (Audio, Document, Image, Handwritten Notes, Text). Processing use cases include Transcribe Audio, Parse Document, OCR Processing, Extract Tasks via LLM, Validate Tasks, and Save to Database.*

> **Figure 3.4: System Context Diagram**
>
> *This diagram should show Sentry AI as the central system, with the User on one side and external services (Groq AI, Voyage AI, AssemblyAI, PostgreSQL/PGVector) on the other side, illustrating the system boundaries and external dependencies.*

---

## 3.7 Use Case Descriptions

### UC-01: User Registration and Login

A new user begins by creating an account with their email address and password. The system validates the input, creates the account, and sends a verification email. Once verified, the user can log in by providing credentials. The system validates these credentials and issues a JWT token that authenticates subsequent requests. Users can also authenticate through OAuth providers for faster access.

**Actors:** User
**Preconditions:** Valid email address for registration; existing account for login
**Postconditions:** User account created and verified; valid JWT token issued

### UC-02: Analyze Burnout

When a user requests burnout analysis, the system retrieves their tasks, meetings, and qualitative data from the database. The workload analyzer calculates metrics including task counts, meeting hours, deadline pressure, and back-to-back meeting patterns. The sentiment analyzer processes recent emotional check-ins and diary entries to assess emotional state.

The system combines these scores (60% workload, 40% sentiment) to produce a final burnout score, classifies it into GREEN/YELLOW/RED levels, and identifies the primary contributing factors. The analysis is saved to history for trend tracking, and results are displayed to the user.

**Actors:** User
**Preconditions:** User authenticated; tasks/meetings exist in system
**Postconditions:** Burnout analysis completed and stored; results displayed

### UC-03: Get Recommendations

Following burnout analysis, users can request personalized recommendations. The system retrieves the latest analysis along with the user's profile, preferences, and constraints. It queries the vector database using RAG to find relevant strategies from the curated guidebook based on identified stress factors.

The system constructs a prompt including the user's context, current calendar events, and task list. The LLM generates recommendations that reference specific events (e.g., "Cancel your 3:30 PM Team Sync") and tasks (e.g., "Delegate the Database Migration to Alex"). Each recommendation includes priority level and actionable steps.

**Actors:** User
**Preconditions:** User authenticated; burnout analysis completed
**Postconditions:** Personalized, event-specific recommendations displayed

### UC-04: Chat with AI Companion

Users send messages to the AI companion through text or audio input. For audio, the system first transcribes the speech to text. The companion classifies the message intent to determine the appropriate response type.

For emotional content, the companion saves the entry to qualitative data, performs sentiment analysis, and responds empathetically. For task queries, it retrieves statistics and summarizes the user's workload. For burnout queries, it explains current status and contributing factors. For task creation, it extracts details and creates the task. For general conversation, it provides helpful responses.

**Actors:** User
**Preconditions:** User authenticated
**Postconditions:** Appropriate response generated; emotional data saved if applicable

### UC-05: Extract Tasks from Files

Users upload files containing task information—meeting recordings, project documents, photos of whiteboards, or handwritten notes. The system detects the file type and routes it to the appropriate processor.

Audio files are transcribed using AssemblyAI. Documents are parsed using Unstructured.io to extract text and tables. Images are processed using vision models. Handwritten notes undergo OCR with Tesseract. The extracted text is sent to the LLM with instructions to identify and structure task information.

Extracted tasks are validated against the schema. Valid tasks are saved to the user's task database with appropriate metadata. The system displays results showing how many tasks were extracted and saved.

**Actors:** User
**Preconditions:** User authenticated; valid file uploaded
**Postconditions:** Tasks extracted, validated, and saved to database

### UC-06: Submit Diary Entry

Users write diary entries describing their emotional state, work experiences, or personal reflections. Upon submission, the system saves the entry to the qualitative_data table with appropriate metadata. Sentiment analysis processes the content to extract emotional indicators and themes.

The AI companion generates a supportive response acknowledging the user's feelings and offering appropriate guidance. The entry contributes to future burnout analyses through the qualitative scoring component.

**Actors:** User
**Preconditions:** User authenticated
**Postconditions:** Entry saved; sentiment analyzed; supportive response provided

### UC-07: View Burnout Dashboard

Users access the dashboard to see their comprehensive burnout status. The system retrieves the latest burnout analysis, historical scores for trend visualization, current task statistics, and active recommendations.

The dashboard displays the current burnout score with level indicator (GREEN/YELLOW/RED), a trend graph showing score changes over time, key stress factors contributing to the current score, a summary of tasks (total, overdue, due this week), and prioritized recommendations awaiting action.

**Actors:** User
**Preconditions:** User authenticated
**Postconditions:** Dashboard displayed with current status and trends

---

## 3.8 User Stories

The following user stories capture requirements from the user's perspective.

### Authentication
- As a new user, I want to register with my email so that I can access the system and track my burnout.
- As a returning user, I want to log in quickly so that I can check my status without friction.
- As a busy professional, I want to use Google sign-in so that I don't need to remember another password.

### Task Management
- As a user, I want to create tasks with priorities and deadlines so that the system understands my workload.
- As a team lead, I want to mark tasks as delegatable so that recommendations can suggest delegation.
- As someone with a busy schedule, I want to see which tasks are overdue so that I can prioritize urgent items.

### Burnout Analysis
- As a user concerned about my well-being, I want to see my burnout score so that I understand my current state.
- As someone trying to improve, I want to see my burnout trends so that I know if I'm getting better or worse.
- As a proactive person, I want alerts when my burnout reaches critical levels so that I can take immediate action.

### Recommendations
- As a user, I want recommendations tailored to my situation so that advice is actually relevant to me.
- As someone with a packed calendar, I want recommendations that reference specific meetings so that I know exactly what to cancel or shorten.
- As a person with constraints, I want the system to respect my deadlines so that it doesn't suggest impossible actions.

### AI Companion
- As someone feeling overwhelmed, I want to share my feelings with the AI so that I feel heard and supported.
- As a busy person, I want to ask "how many tasks do I have" and get an instant answer.
- As someone in a meeting, I want to create tasks by voice so that I can capture action items hands-free.

### Task Extraction
- As someone who attends many meetings, I want to upload recordings and have tasks extracted automatically.
- As a student, I want to photograph my handwritten notes and have tasks digitized.
- As a professional, I want to process multiple files at once so that I can batch my task entry.

---

## 3.9 Summary

This chapter has analyzed the limitations of current burnout management approaches and defined comprehensive requirements for Sentry AI.

Current systems fail due to fragmentation—wellness apps don't see workloads, productivity tools ignore health, and organizational programs react too late. Sentry AI addresses these gaps through integrated, automated, personalized, and evidence-based intervention.

The feasibility study confirms that required technologies are mature and available, the system integrates with existing workflows, and costs scale reasonably with usage.

Functional requirements span seven service areas: authentication, task management, burnout analysis, recommendations, AI companion, task extraction, and user profiles. Non-functional requirements define quality standards for performance, security, scalability, availability, usability, and maintainability.

Use case diagrams and descriptions model the primary system interactions, while user stories capture requirements from the end-user perspective.

These requirements provide the foundation for system design in the following chapter.
