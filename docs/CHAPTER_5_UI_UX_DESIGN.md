# 5. UI/UX DESIGN

This chapter presents the user interface and user experience design of Sentry AI. The design reflects careful consideration of color psychology, visual hierarchy, and user-centered principles specifically tailored for a mental health and productivity application. A total of 30 screens were designed across seven functional areas, creating a cohesive and calming experience that supports users in managing their well-being.

---

## 5.1 Design Philosophy

### 5.1.1 The Importance of UI/UX in Mental Health Applications

User interface design in mental health applications carries responsibilities beyond typical software. Users interacting with Sentry AI may already be experiencing stress, exhaustion, or emotional overwhelm. A poorly designed interface—cluttered layouts, harsh colors, confusing navigation—can amplify these negative states and discourage continued use.

Conversely, thoughtful design actively supports the application's therapeutic goals. A calming color palette reduces anxiety. Clear visual hierarchy minimizes cognitive load. Intuitive navigation prevents frustration. Encouraging illustrations and friendly language motivate positive behavior change without creating pressure.

Research in digital therapeutics demonstrates that user engagement with mental health applications drops significantly when the interface feels clinical, complicated, or visually unappealing. Users must feel that the application is a supportive companion, not another source of stress competing for their attention.

For Sentry AI specifically, the interface communicates:
- **Trust** — Users share sensitive information about their workload and emotional state
- **Calm** — The visual experience feels peaceful, not overwhelming
- **Clarity** — Information is immediately understandable at a glance
- **Motivation** — Design encourages positive action without pressure
- **Warmth** — Friendly illustrations create an approachable, human feel

### 5.1.2 Design Principles

**Simplicity Over Complexity**

Every screen focuses on a single primary purpose. The home dashboard shows the day's plan at a glance. The burnout screen focuses on the score and its components. Secondary features remain accessible but visually subordinate. White space and soft backgrounds let content breathe.

**Progressive Disclosure**

Information is revealed gradually as users need it. The dashboard shows summary metrics; detailed breakdowns appear on dedicated screens. Recommendations show headlines first; action steps expand on demand. This approach prevents information overload while keeping depth accessible.

**Encouraging Without Pressuring**

The application uses friendly language and supportive illustrations. Instead of alarming warnings, the interface uses gentle color transitions (green to yellow to red) to indicate status. Success is celebrated; challenges are addressed with support rather than criticism. The AI companion asks "wanna say something?" rather than demanding input.

**Consistency Across Flows**

The design system ensures visual consistency throughout the application. Cards use the same rounded corners and gradient styles. Typography follows a clear hierarchy. The bottom navigation provides constant orientation. Users always know where they are and how to navigate.

---

## 5.2 Color Psychology and Palette Selection

### 5.2.1 The Psychology of Color in Wellness Applications

Color profoundly influences emotional state and behavior. The Sentry AI color palette was carefully selected based on established research in color psychology, prioritizing calming tones that reduce anxiety while maintaining visual interest and clarity.

**Light Blue — Calm and Serenity**

Light blue serves as the dominant background color throughout the application. Blue is universally associated with calm, trust, and stability. It lowers heart rate and reduces anxiety. The soft, light blue (#E8F4FC) creates a serene atmosphere that feels like a clear sky—open, peaceful, and refreshing. This choice directly supports users who may be experiencing stress.

**Teal/Cyan Gradients — Energy and Freshness**

Cards and interactive elements use teal-to-cyan gradients (#4ECDC4 to #44A8B3). These colors combine the calming properties of blue with the vitality of green, creating a sense of balanced energy. The gradients add visual depth and modern appeal while maintaining the overall calming aesthetic.

**White and Light Tones — Clarity and Space**

White cards and light backgrounds create visual breathing room. In a mental health application, avoiding visual clutter is essential. The generous use of light tones ensures content stands out clearly without overwhelming the user.

**Status Colors — Intuitive Communication**

The burnout gauge uses an intuitive traffic-light metaphor:
- **Green** — Healthy, low burnout risk
- **Yellow** — Moderate, attention needed
- **Red** — Critical, immediate action required

This familiar color coding communicates status instantly without requiring users to read numbers or labels.

**Accent Colors — Visual Interest**

Purple and pink gradients appear in recommendation cards, adding warmth and visual variety. These colors are associated with creativity and care, appropriate for sections offering personalized guidance.

### 5.2.2 The Sentry AI Color Palette

**Primary Colors**

| Color | Usage |
|-------|-------|
| Light Blue (#E8F4FC) | Primary background throughout the app |
| Teal (#4ECDC4) | Card backgrounds, interactive elements |
| Cyan (#44A8B3) | Gradient endpoints, accents |
| Deep Blue (#1E88E5) | Primary buttons, links |

**Status Colors**

| Color | Usage |
|-------|-------|
| Green (#4CAF50) | Healthy status, success, completion |
| Yellow/Amber (#FFC107) | Moderate status, attention needed |
| Red (#F44336) | Critical status, urgent items |

**Accent Colors**

| Color | Usage |
|-------|-------|
| Purple gradient | Recommendation cards |
| Pink/Coral | Secondary highlights |
| White (#FFFFFF) | Cards, input fields |

### 5.2.3 Light Theme Rationale

Unlike many productivity apps that use dark themes, Sentry AI uses a light, airy color scheme for important psychological reasons:

**Openness and Hope**

Light colors create a sense of openness and possibility. For users experiencing burnout—which often involves feelings of being trapped or overwhelmed—a bright, open interface subconsciously communicates that relief is possible.

**Daytime Optimization**

Users primarily interact with the app during work hours when light themes are more comfortable and match ambient lighting conditions.

**Approachability**

Light interfaces feel friendlier and less technical. The soft blue background resembles a calm sky, creating an inviting atmosphere rather than a clinical tool.

**Illustration Integration**

The friendly character illustrations integrate seamlessly with the light background, creating a cohesive, storybook-like quality that makes the app feel personal and supportive.

---

## 5.3 Visual Elements and Illustrations

### 5.3.1 Character Illustrations

A distinctive feature of Sentry AI's design is the consistent use of friendly character illustrations throughout the application. These illustrations serve multiple purposes:

**Humanizing the Experience**

The illustrated characters—depicting people working, thinking, and interacting with technology—make the app feel personal rather than clinical. Users see relatable representations of themselves.

**Emotional Communication**

Illustrations communicate emotional states that support the app's messaging. The onboarding illustration shows a person overwhelmed with papers and devices, validating the user's feelings. Later illustrations show calm, organized scenarios, suggesting the positive outcomes the app enables.

**Visual Storytelling**

Each major section uses illustrations that tell a story:
- Onboarding: Overwhelmed person → AI assistant helping → Organized, peaceful work
- Login: Person at desk with security elements, suggesting safe, protected access
- AI Companion: Friendly robot offering to help

**Consistent Style**

All illustrations share a consistent style:
- Flat design with subtle gradients
- Blue-dominant color scheme matching the app palette
- Friendly, rounded character designs
- Modern, professional aesthetic

### 5.3.2 The AI Companion Character

The AI companion is represented by a distinctive robot character with:
- Rounded, friendly form (not angular or threatening)
- Teal/cyan coloring matching the app palette
- Headphones suggesting it's ready to listen
- Expressive posture (waving, gesturing helpfully)

This character appears on the home screen with the prompt "wanna say something?" creating an inviting entry point for emotional support. The friendly design encourages users to share their feelings without judgment.

### 5.3.3 Iconography

Icons throughout the app follow a consistent style:
- Rounded, soft appearance
- Consistent stroke weight
- Clear metaphors (calendar for schedule, chart for analytics)
- Matching the overall friendly aesthetic

The bottom navigation uses filled icons for the active state and outlined icons for inactive states, providing clear visual feedback.

---

## 5.4 Navigation and Information Architecture

### 5.4.1 App Flow Structure

The application follows a hub-and-spoke model with the Home screen as the central navigation point. The wireframe diagrams reveal the complete flow architecture:

**Flow 1: Onboarding + Login**
Onboarding screens → Email Verification → Login/Signup → Profile Setup Questions → Home

**Flow 2: Main Application**
Home connects to all major sections:
- Tasks (My Tasks → Upload Tasks)
- Profile (Settings → Personal Data → Contact Info)
- Burnout (Score → Details → Recommendations)
- AI Companion (Chat interface)
- Notebook Library (Create → Chat → AI Studio)
- Integrations (Connected services)

### 5.4.2 Bottom Navigation

The primary navigation uses a bottom tab bar with five sections:

1. **Integrations** (link icon) — Third-party service connections
2. **Analytics** (chart icon) — Burnout analysis and trends
3. **Home** (house icon) — Central dashboard
4. **Calendar** (calendar icon) — Task and schedule view
5. **Notebook** (book icon) — Notebook library

The home icon is centrally positioned and slightly elevated, emphasizing its role as the primary hub. This pattern is familiar to mobile users and enables one-handed navigation.

### 5.4.3 Screen Flow Principles

**Minimal Depth**

Most features are accessible within 2-3 taps from the home screen. Users can check their burnout score, view recommendations, or chat with the AI companion without navigating through complex hierarchies.

**Clear Back Navigation**

All secondary screens include a back arrow in the top-left corner, following platform conventions. Users always have a clear escape route.

**Contextual Actions**

Actions appear where users need them. The "Add a source" button appears directly in the notebook library. The "Apply All" button appears at the top of recommendations. Users don't need to hunt for functionality.

---

## 5.5 Screen Designs by Service

The following sections describe each screen in detail, organized by functional area.

---

### 5.5.1 Onboarding Screens

The onboarding flow introduces users to Sentry AI's value proposition through three illustrated screens that can be swiped or skipped.

---

#### Figure 5.1: Onboarding Screen 1 — "Take it easy"

![Onboarding - Take it easy](../images/login_signup_onboarding/01_onboarding_take_it_easy.png)

**Purpose:** Validate the user's experience with burnout and introduce the app's promise.

**Visual Elements:**
- Large, bold headline "Take it easy" in dark blue
- Subheadline "no more confusion, destruction or burnout" in gray
- Central illustration showing a person overwhelmed with papers, laptop, calendar, and documents flying around them
- The character appears stressed but not defeated, suggesting the situation is manageable
- Pagination dots (4 total) indicating position in the onboarding flow
- "skip" button allowing users to bypass onboarding

**Design Rationale:** The illustration validates what users are feeling—acknowledging the chaos of modern work life. The reassuring headline immediately positions the app as a solution rather than another obligation.

---

#### Figure 5.2: Onboarding Screen 2 — "Auto scheduling with AI"

![Onboarding - Auto scheduling](../images/login_signup_onboarding/02_onboarding_auto_scheduling.png)

**Purpose:** Introduce the AI-powered task management capability.

**Visual Elements:**
- Headline "Auto scheduling with AI" highlighting the intelligent automation
- Subheadline "no conflicts, overload or missing deadlines"
- Illustration showing a relaxed person sitting with a laptop, accompanied by a "MY GOALS" checklist with items being checked off
- Calm home environment with plants, suggesting work-life balance
- Same pagination and skip button pattern

**Design Rationale:** This screen shifts from problem (overwhelm) to solution (AI assistance). The relaxed posture and checked items suggest the outcome users can expect.

---

#### Figure 5.3: Onboarding Screen 3 — "Speak with your assistant"

![Onboarding - Speak with assistant](../images/login_signup_onboarding/03_onboarding_speak_assistant.png)

**Purpose:** Introduce the AI companion feature for emotional support and task management.

**Visual Elements:**
- Headline "Speak with your assistant"
- Subheadline "assign tasks, life coaching and mood tracking"
- Illustration showing the friendly robot character with a speech bubble saying "Hi! How can I help you?"
- User figure sitting comfortably in a chair, appearing relaxed
- Chat bubble icons suggesting conversation

**Design Rationale:** This screen introduces the AI companion character that users will interact with throughout the app. The speech bubble and conversational posture emphasize that this is a dialogue, not a one-way tool.

---

### 5.5.2 Authentication Screens

---

#### Figure 5.4: Sign Up Screen

![Sign Up](../images/login_signup_onboarding/04_signup.png)

**Purpose:** Allow new users to create an account.

**Visual Elements:**
- Clean, minimal form design on light gradient background
- "Create An Account" header
- Input fields for: Name, Email, Phone Number (with +20 country code), Password, Confirm Password
- Prominent "Sign up" button in teal/cyan
- "Already have an account? Log in" link
- Divider with "OR" and "Login with" label
- Social authentication buttons: Apple, Google, GitHub
- Each social button clearly labeled with provider name

**Design Rationale:** The form is intentionally simple with generous spacing. Social login options reduce friction for users who prefer not to create new credentials. The light background maintains the calming aesthetic.

---

#### Figure 5.5: Login Screen

![Login](../images/login_signup_onboarding/05_login.png)

**Purpose:** Authenticate returning users.

**Visual Elements:**
- Welcoming illustration showing a person at a desk with security-related icons (lock, shield, password field)
- "Welcome Back!" headline creating a friendly, personal greeting
- "Login to your Account" subheadline
- Email and Password input fields with subtle borders
- Password field includes visibility toggle (eye icon)
- "Forgot Password?" link positioned near password field
- "Log in" button in teal/cyan
- "Don't have an account? Sign up" link

**Design Rationale:** The security-themed illustration reassures users that their sensitive mental health data is protected. The welcoming language makes returning feel like coming back to a supportive space.

---

#### Figure 5.6: Forgot Password Screen

![Forgot Password](../images/login_signup_onboarding/06_forgot_password.png)

**Purpose:** Initiate password recovery.

**Visual Elements:**
- "Forgot password" header with back arrow
- Illustration showing a person with a mobile device displaying a user profile
- Instructional text: "Please Enter Your Email Address To Receive a Verification Code"
- Email address input field
- "Try another way" link offering alternative recovery
- "send" button

**Design Rationale:** The illustration shows the verification process visually, reducing anxiety about the recovery flow. Clear instructions set expectations.

---

#### Figure 5.7: Create New Password Screen

![Create New Password](../images/login_signup_onboarding/07_create_new_password.png)

**Purpose:** Allow users to set a new password after verification.

**Visual Elements:**
- "Create New Password" header
- Illustration showing a person with a large smartphone displaying a profile, suggesting account security
- Helpful text: "Your New password must differ from the old one"
- Password and Confirm Password input fields
- "Save" button

**Design Rationale:** Clear guidance prevents users from reusing compromised passwords. The illustration maintains visual continuity with the forgot password screen.

---

#### Figure 5.8: Email Verification Screen

![Email Verification](../images/login_signup_onboarding/08_email_verification.png)

**Purpose:** Verify user's email address during registration.

**Visual Elements:**
- "Verify Your Email" header with back arrow
- Illustration showing a person with a megaphone emerging from a device, representing notification/communication
- Instructional text: "Please Enter The 4 Digit Code Sent To Your Email"
- Four separate input boxes for the verification code (improving usability over a single text field)
- "Resend code" link for users who didn't receive the email
- "Verify" button

**Design Rationale:** Separate digit boxes make code entry easier and reduce errors. The resend option addresses common email delivery issues.

---

### 5.5.3 Profile Setup Screen

---

#### Figure 5.9: Profile Questions Screen

![Profile Questions](../images/login_signup_onboarding/09_profile_questions.png)

**Purpose:** Gather information to personalize the user experience and enable accurate burnout analysis.

**Visual Elements:**
- Tab navigation: "Personal data", "Contact info", "Questions" (Questions tab active)
- Sentry AI logo and tagline: "Help us tailor your experience by telling us a bit about yourself"
- Form fields with dropdown selections:
  - Job role: "Select your role"
  - Seniority level: "Select your level"
  - Can you delegate tasks to others?: Toggle (No/Yes)
  - Do you manage a team?: Toggle (No/Yes)
  - What is your biggest work challenge?: "select challenge"
- "Edit" button in top right for later modifications

**Design Rationale:** These questions directly feed into the burnout analysis engine. Knowing if a user can delegate tasks or manages a team affects which recommendations are appropriate. The toggle switches make binary choices quick and easy.

---

### 5.5.4 Home Dashboard

---

#### Figure 5.10: Home Screen

![Home Dashboard](../images/10_home_dashboard.png)

**Purpose:** Provide an at-a-glance overview of the user's day and quick access to all features.

**Visual Elements:**

*Header Section:*
- Personalized greeting: "Hello Ahmed" with user avatar
- Friendly illustration of person working at desk with laptop

*Calendar Strip:*
- Horizontal date selector showing week view (Sat 1 - Thu 6)
- Current date (Tue 4) highlighted with filled circle
- Month indicator (October)

*Today's Plan Section:*
- Three task cards with gradient backgrounds:
  - "Lecture 9:00 AM" marked as "urgent" (coral/orange gradient)
  - "Meeting 11:00 AM" (teal gradient)
  - "ML Task 1:00 PM" (teal gradient)

*Status Cards:*
- "Burnout Score" card showing status as "Exhausted" with a progress bar indicator (red level)
- "wanna say something?" card with AI companion robot, inviting conversation

*Bottom Navigation:*
- Five icons: Integrations, Analytics, Home (active), Calendar, Notebook

**Design Rationale:** The dashboard follows a "glanceable" design philosophy. Users can immediately see: who they are (greeting), what day it is (calendar), what they need to do (tasks), how they're feeling (burnout score), and how to get help (AI companion). The burnout score card creates urgency without panic through its color and friendly language.

---

### 5.5.5 Burnout Analysis Screens

---

#### Figure 5.11: Burnout Score Screen

![Burnout Score](../images/burnout_recommendations/11_burnout_score.png)

**Purpose:** Display comprehensive burnout analysis with trends and contributing factors.

**Visual Elements:**

*Score Header:*
- Large "60" burnout score with upward trend arrow
- "increasing" label and "moderate" status badge
- Visual gauge showing score position
- "15% up" indicator with colorful gauge graphic
- "check details" link for more information

*Trend Chart:*
- Line graph showing burnout score over time
- Time period toggles: Week, Month, Year
- Date indicator: "24 October 2025"
- Y-axis scale from 0-80
- Notable spike visible around day 15

*Factor Cards:*
- "Workload" card showing "80% impact" with small gauge
- "sentiment" card showing "30% positivity" with gauge

*Primary Issues Section:*
- List of identified issues:
  - "Over Tasks" (with icon)
  - "lack of team collaboration" (with icon)

**Design Rationale:** The score is prominently displayed as the key metric. The trend chart helps users understand patterns over time. Factor breakdown shows what's contributing to burnout, while primary issues provide actionable insights.

---

#### Figure 5.12: Burnout Details Screen (Scrolled)

![Burnout Details](../images/burnout_recommendations/12_burnout_details.png)

**Purpose:** Show complete burnout analysis with recommendations preview.

**Visual Elements:**

*Primary Issues (continued):*
- "Over Tasks"
- "lack of team collaboration"
- "successive no break holidays"

*AI Recommendations Preview:*
- Two recommendation cards:
  - "Cancel Meeting" — brief description about reducing burnout
  - "Cancel M..." (truncated, showing more available)

*Burnout Signals Section:*
- Visual indicators for detected signals:
  - "Over Tasks" (red indicator)
  - "lack of team collaboration" (yellow)
  - "successive no break holidays" (yellow)

*Recovery Plan Section:*
- Progress indicator: "Target: reduce burnout by 10%"
- Progress bar showing "progress: 50%, completed 5/10 steps"
- "View plan details" link

**Design Rationale:** This screen provides depth for users who want to understand their situation fully. The recovery plan progress creates motivation by showing incremental achievement.

---

#### Figure 5.13: Workload Breakdown Screen

![Workload Breakdown](../images/burnout_recommendations/13_workload_breakdown.png)

**Purpose:** Detailed analysis of workload components and their impact on burnout.

**Visual Elements:**

*Workload Breakdown Section:*
- Horizontal bar chart comparing metrics to baseline:
  - Tasks: 80% (significantly over baseline ~30%)
  - Time spent: 70%
  - Meetings: 50%
  - Baseline deviations: 30%

*Burnout Factors Donut Chart:*
- Circular chart showing factor distribution
- Color-coded segments for different factors
- Legend identifying each factor

*High Impact Metrics Section:*
- Ranked list with change indicators:
  - "Meeting overload" (+30% in red, indicating significant increase)
  - "lack of team collaboration" (+18%)
  - "successive no break holidays"

**Design Rationale:** This analytical screen is for users who want data-driven insights. The comparison to baseline helps users understand what "too much" means for them personally. High impact metrics prioritize what to address first.

---

#### Figure 5.14: AI Recommendations Screen

![AI Recommendations](../images/burnout_recommendations/14_ai_recommendations.png)

**Purpose:** Display personalized, actionable recommendations generated by the AI.

**Visual Elements:**

*Header:*
- "AI Recommendations" title with back arrow
- Bulk action buttons: "Apply All" and "Discard All"

*Recommendation Cards:*
Each card features:
- Gradient background (purple/pink/teal variations)
- Title (e.g., "Cancel Meeting")
- Star rating (relevance/impact indicator)
- "highly recommended" badge
- Brief description of the recommendation and expected benefit
- Two action buttons: "Try Out" and "cancel"

*Visible Recommendations:*
- "Cancel Meeting" — addresses non-urgent meetings
- "Take rest" — recovery recommendation
- Additional cards visible below (scrollable)

**Design Rationale:** The card-based design makes each recommendation feel like a discrete, manageable action. Star ratings help users prioritize. The "Try Out" language is less committal than "Apply," reducing resistance to trying new behaviors. Bulk actions enable quick adoption for users who trust the AI.

---

### 5.5.6 Task Management Screens

---

#### Figure 5.15: My Tasks Screen

![My Tasks](../images/tasks/15_my_tasks.png)

**Purpose:** Central task management with productivity overview.

**Visual Elements:**

*Header:*
- "My Tasks" title with user avatar
- Weekly progress card: "Your Weekly progress" showing "50% productivity" with trend graph

*Statistics Cards:*
- "Today's Tasks: 7" in teal card
- "calendar view" card with calendar icon for alternate view

*Calendar Strip:*
- Same week view pattern as home screen
- Current date highlighted

*Task List:*
- Individual task cards with color-coded priority bars:
  - "Lecture" — 9:00 AM, "pattern recognition lecture"
    - Tags: "University", "urgent" (red tag)
    - Orange accent bar indicating high priority
  - "Meeting" — 11:00 AM, "Online Meeting for pipeline"
    - Tags: "personal", "urgent"
    - Green accent bar

*Add Task Button:*
- Floating action button (+) for creating new tasks

*Bottom Navigation:*
- Category filters visible: "personal", "urgent"

**Design Rationale:** The productivity percentage provides motivation. Color-coded priority bars enable quick visual scanning. Tags allow flexible categorization. The floating add button follows Material Design conventions for primary actions.

---

#### Figure 5.16: Upload Tasks Screen

![Upload Tasks](../images/tasks/16_upload_tasks.png)

**Purpose:** Allow users to add tasks manually or extract them from files using AI.

**Visual Elements:**

*Header:*
- "Upload Tasks" with back arrow

*Two Expandable Sections:*

**Add Tasks manually (expanded):**
- Form fields:
  - Task name: text input
  - Subject: text input
  - Deadline: date picker
  - Priority: radio buttons (High, Medium, Low)
- "ADD" button

**Extract Tasks via AI (expanded):**
- File type options: "Audio", "DOCS", "video"
- Loading indicator showing processing status
- Results preview:
  - "1. example of task one extracted from files." ✓
  - "2. example of task two extracted from files." ✓
  - "3. example of task three extracted from files." ✓
- Selection indicator: "2 tasks are selected"
- "ADD" button to confirm extracted tasks

**Design Rationale:** Two clear paths accommodate different user preferences. Manual entry for quick additions; AI extraction for processing meeting recordings or documents. The preview with checkboxes lets users verify and select which extracted tasks to keep.

---

### 5.5.7 Integration Screens

---

#### Figure 5.17: Integrations Screen

![Integrations](../images/integrations/17_integrations.png)

**Purpose:** Manage connections to third-party services for automatic data synchronization.

**Visual Elements:**

*Header:*
- "Integration" title with back arrow

*Connected Services Summary:*
- Visual indicators: "4 Connected", "1 paused", "1 Need setup"
- "Last synced: 2 minutes ago"
- "sync all" button

*Services List:*

**Google Tasks:**
- Status: "connected" (green badge)
- Info: "3 events today", "Last synced: 2 minutes Ago"
- Google Tasks icon

**Google Class Room:**
- Status: "not connected" (red badge)
- "Need permission" notice with required permissions:
  - View your Google Classroom courses
  - Manage assignments and grades
  - Manage assignments and grades
- "Connect" button

**Design Rationale:** Clear status indicators show what's working and what needs attention. The permissions list sets transparent expectations before users connect services.

---

#### Figure 5.18: Integrations Screen (Continued)

![Integrations Continued](../images/integrations/18_integrations_continued.png)

**Purpose:** Additional service integrations including Zoom and university portals.

**Visual Elements:**

**Google Class Room (continued):**
- Same details as previous screen

**Zoom Meetings:**
- Status: "attention" (yellow badge)
- Message: "Connection error Failed to refresh token. Please re-authenticate"
- "re authenticate" button

**University Portal:**
- Status: "configured" (green badge)
- Description: "Connected to student information system. Syncs courses, grades, and announcements"
- "configurations" button

**Design Rationale:** Different status states (connected, not connected, attention, configured) are clearly distinguished. Error states include actionable resolution steps (re-authenticate). The university portal integration shows the system's extensibility to educational contexts.

---

### 5.5.8 Notebook Library Screens

---

#### Figure 5.19: Notebook Library — Create New

![Notebook Create](../images/notebookLibrary/19_notebook_create.png)

**Purpose:** Entry point for creating new notebooks from various source types.

**Visual Elements:**

*Header:*
- "Notebook Library" title with back arrow
- Tab options: "Create New" (active), "Most recent"

*Welcome Section:*
- Illustration of stacked documents
- "Let's get started" message
- "Create your new notebook" instruction

*Upload Options:*
- "Upload your files here" label
- Six source type buttons:
  - PDF (teal)
  - Images (teal)
  - Audio (gradient)
  - Website (gradient)
  - YouTube (gradient)
  - Copied text (gradient)

**Design Rationale:** The variety of source options demonstrates the system's flexibility. Users can create notebooks from documents, recordings, web content, or even copied text. Visual differentiation between options uses subtle gradient variations.

---

#### Figure 5.20: Notebook Content — Library View

![Notebook Library](../images/notebookLibrary/20_notebook_library.png)

**Purpose:** Display uploaded sources within a notebook.

**Visual Elements:**

*Header:*
- Notebook name: "AI_generated_notebook name"
- Edit icon for renaming

*Library Section:*
- List of uploaded sources with type indicators:
  - "The uploaded image_1 name" (image icon)
  - "The uploaded image_1 name" (image icon)
  - "The uploaded pdf name" (PDF icon)
  - "The uploaded URL page name" (link icon)
  - "The uploaded copied Text" (text icon)

*Add More:*
- "+ Add a source" button

*Bottom Navigation:*
- Three tabs: "Library" (active), "Chat", "AI studio"

**Design Rationale:** The source list shows what content has been added to the notebook. Type icons help users identify sources quickly. The three-tab navigation separates content management (Library), interaction (Chat), and generation (AI studio).

---

#### Figure 5.21: Notebook — Chat Interface

![Notebook Chat](../images/notebookLibrary/21_notebook_chat.png)

**Purpose:** Allow users to ask questions about their notebook content using RAG.

**Visual Elements:**

*Header:*
- Notebook name
- "Based on 2 sources uploaded" indicator

*Content Summary:*
- Title: "Decoding Machine Learning: Foundations, Types and Deep Networks"
- AI-generated summary: Comprehensive overview of the IBM source, explaining ML as artificial intelligence focused on learning from training data, contrasting with older rule-based approaches, describing the operational process of transforming raw data into numerical representations, and categorizing ML methods into three paradigms.

*Chat Input:*
- Text field: "Ask me anything..."
- Send button
- Microphone button for voice input

*Bottom Navigation:*
- "Chat" tab active

**Design Rationale:** The summary gives users immediate value from their uploaded content. The chat interface enables natural language queries. Voice input accommodates hands-free use.

---

#### Figure 5.22: Notebook — AI Studio

![Notebook AI Studio](../images/notebookLibrary/22_notebook_ai_studio.png)

**Purpose:** Generate study materials and extract tasks from notebook content.

**Visual Elements:**

*Header:*
- Notebook name

*Generate with AI Studio Section:*
- Four generation options, each with edit icon:
  - "Audio Overview" — Generate audio summary
  - "Extract Tasks" — Pull tasks from content
  - "Flashcards" — Create study flashcards
  - "Quiz" — Generate quiz questions

*Generated Media Section:*
- Previously generated items:
  - "Machine Learning Quiz"
  - "Machine Learning Flashcards"

*Bottom Navigation:*
- "AI studio" tab active

**Design Rationale:** The AI studio transforms passive content into active learning materials. The options address different learning styles (audio, visual flashcards, interactive quizzes). Previously generated items are saved for reuse.

---

### 5.5.9 AI Companion Screen

---

#### Figure 5.23: AI Companion Chat

![AI Companion Chat](../images/wire_frames/23_ai_companion_chat.png)

**Purpose:** Provide conversational interface for emotional support, task management, and queries.

**Visual Elements:**

*Header:*
- "AI companion" title with back arrow
- Robot avatar with greeting: "Hi, Ahmed! How is your day?"
- Subtext: "speak with your companion"

*Chat Interface:*
- Message bubbles:
  - User messages (right-aligned, teal background)
  - Assistant responses (left-aligned, light gray background)
- Conversation flow with alternating messages

*Quick Action Chips:*
- Pre-defined prompts at bottom:
  - "life advice from your day"
  - "Add tasks via assistant"
  - "your diary or moment"

*Input Area:*
- Text input: "Ask me anything..."
- Microphone button for voice input

**Design Rationale:** The friendly robot character creates a welcoming atmosphere. Quick action chips help users who aren't sure what to say. The chat bubble pattern is familiar from messaging apps. Voice input enables hands-free interaction.

---

### 5.5.10 Profile & Settings Screens

---

#### Figure 5.24: Profile Settings Screen

![Profile Settings](../images/profile/24_profile_settings.png)

**Purpose:** Central hub for account management and app settings.

**Visual Elements:**

*Header:*
- Back arrow
- Profile picture placeholder
- User name: "Ahmed Mohamed"
- Decorative wave gradient in brand colors

*Settings Options:*
- "My Account" — Account details and management
- "Notifications" — Toggle switch (currently ON)
- "Change password" — Security settings
- "Languages" — Current selection: "English"
- "Terms and Privacy Policy" — Legal documents

*Logout:*
- "Logout" button with icon (red text indicating destructive action)

**Design Rationale:** Clean, scannable list of settings. Toggle switches for binary options. Language selection shown inline. Logout is separated and colored to prevent accidental taps.

---

#### Figure 5.25: Profile — Personal Data Tab

![Profile Personal Data](../images/profile/25_profile_personal_data.png)

**Purpose:** View and edit personal information.

**Visual Elements:**

*Header:*
- "Profile" title
- "Edit" button
- Tab navigation: "Personal data" (active), "Contact info", "Questions"

*Sentry AI Branding:*
- Logo and tagline: "Help us tailor your experience by telling us a bit about yourself"

*Form Fields:*
- Name: "Alexander Oxlade Chamberlain"
- Email: "Alex_Oxain@gmail.com"
- Birth date: "2004-05-09"
- Email: "Alex_Oxain@gmail.com" (displayed twice, likely for confirmation)

**Design Rationale:** The three-tab structure organizes different types of profile information. Edit mode is clearly indicated. Pre-filled data shows users what's stored.

---

#### Figure 5.26: Profile — Contact Info Tab

![Profile Contact Info](../images/profile/26_profile_contact_info.png)

**Purpose:** Manage contact and location information.

**Visual Elements:**

*Same header and tab structure*

*Form Fields:*
- Country: "Egypt"
- City: "Cairo"
- Address: "Almazah, Heliopolis, Cairo"
- Mobile Number: "01234567899"

**Design Rationale:** Separating contact info from personal data keeps forms manageable. Location information could be used for timezone-aware scheduling or local recommendations.

---

### 5.5.11 Wireframes Overview

The wireframe diagrams show the complete application architecture and user flows.

---

#### Figure 5.27: Complete App Flow Diagram

![Wireframe Complete](../images/wire_frames/27_wireframe_complete.png)

**Purpose:** Show the complete application architecture and navigation structure.

**Visual Elements:**
- Central "Home" screen connecting to all major sections
- Flow 1: Onboarding + Login sequence (left side)
- Flow 2: Main app sections radiating from Home
- Color-coded groupings for different functional areas
- Connecting lines showing navigation paths

**Design Rationale:** This bird's-eye view demonstrates the hub-and-spoke navigation model. Users can see that Home is the central point and all features are accessible within a few taps.

---

#### Figure 5.28: Onboarding + Login Flow

![Wireframe Onboarding](../images/wire_frames/28_wireframe_onboarding.png)

**Purpose:** Detail the first-time user experience flow.

**Visual Elements:**
- Sequence of onboarding screens
- Login and signup branches
- Email verification step
- Profile setup screens
- Path to Home screen

**Design Rationale:** The flow shows how new users are guided from first launch to productive use, ensuring no user gets lost during initial setup.

---

#### Figure 5.29: Tasks and Profile Flow

![Wireframe Tasks Profile](../images/wire_frames/29_wireframe_tasks_profile.png)

**Purpose:** Detail the task management and profile management flows.

**Visual Elements:**
- Tasks section: My Tasks → Upload Tasks
- Profile section: Settings → Personal Data → Contact Info → Questions
- Home screen as navigation hub
- Connecting paths between related screens

**Design Rationale:** Shows how task and profile management are organized as separate but accessible flows from the home screen.

---

#### Figure 5.30: Notebook Library Flow

![Wireframe Notebook](../images/wire_frames/30_wireframe_notebook.png)

**Purpose:** Detail the notebook library feature flow.

**Visual Elements:**
- Create notebook entry point
- Library view with sources
- Chat interface for queries
- AI Studio for content generation
- Tab-based navigation within notebooks

**Design Rationale:** The notebook flow demonstrates how users progress from creating notebooks to interacting with and generating content from them.

---

#### Figure 5.31: Burnout and Integrations Flow

![Wireframe Burnout](../images/wire_frames/31_wireframe_burnout.png)

**Purpose:** Detail the burnout analysis and integrations flows.

**Visual Elements:**
- Burnout section: Score → Details → Workload → Recommendations
- Integrations section: Service list → Configuration
- Home screen connections
- AI Recommendations as destination from burnout flow

**Design Rationale:** Shows how users navigate from high-level burnout score to detailed analysis and actionable recommendations.

---

## 5.6 Responsive Design Considerations

### 5.6.1 Mobile-First Approach

Sentry AI was designed mobile-first, recognizing that users often check their burnout status throughout the day from their phones. The mobile interface prioritizes:

- **Thumb-friendly navigation** with bottom tab bar
- **Touch-optimized targets** (minimum 44x44 points)
- **Scannable content** optimized for quick glances
- **One-handed operation** for common tasks

### 5.6.2 Component Consistency

Design components maintain consistency across all screens:
- Card corner radius remains constant
- Button styles are uniform
- Spacing follows a consistent grid
- Typography scale is applied systematically

---

## 5.7 Accessibility Considerations

### 5.7.1 Visual Accessibility

- **Contrast ratios** meet WCAG 2.1 AA requirements
- **Color is not the sole indicator** — text labels accompany color-coded status
- **Text remains readable** at various sizes
- **Focus states** are clearly visible

### 5.7.2 Interaction Accessibility

- **Touch targets** meet minimum size requirements
- **Clear labels** on all interactive elements
- **Logical reading order** for screen readers
- **Alternative text** for illustrations

---

## 5.8 Summary

The UI/UX design of Sentry AI reflects a deep understanding of the psychological needs of users experiencing burnout. The light blue color palette creates calm. Friendly illustrations humanize the experience. Clear navigation prevents frustration. Progressive disclosure manages cognitive load.

The 30+ screens across seven functional areas create a comprehensive interface for:
- Onboarding and authentication (9 screens)
- Task management (2 screens)
- Burnout analysis and recommendations (4 screens)
- AI companion interaction (1 screen)
- Notebook library (4 screens)
- Integrations (2 screens)
- Profile and settings (3 screens)
- Wireframes and flow documentation (5 screens)

Every design decision—from the color of a button to the wording of a prompt—was made with the user's well-being in mind. The result is an interface that doesn't just display information about burnout; it actively contributes to the user's sense of calm, control, and hope.
