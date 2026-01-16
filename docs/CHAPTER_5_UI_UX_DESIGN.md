# 5. UI/UX DESIGN

This chapter presents the user interface and user experience design of Sentry AI. A mental health and productivity application demands careful attention to visual design, as the interface itself can either contribute to user stress or promote calm and focus. The design decisions documented here reflect research in color psychology, accessibility, and human-computer interaction principles specific to wellness applications.

---

## 5.1 Design Philosophy

### 5.1.1 The Importance of UI/UX in Mental Health Applications

User interface design in mental health applications carries responsibilities beyond typical software. Users interacting with Sentry AI may already be experiencing stress, exhaustion, or emotional overwhelm. A poorly designed interface—cluttered layouts, harsh colors, confusing navigation—can amplify these negative states and discourage continued use.

Conversely, thoughtful design can actively support the application's goals. A calming color palette can reduce anxiety. Clear visual hierarchy can minimize cognitive load. Intuitive navigation can prevent frustration. Encouraging micro-interactions can motivate positive behavior change.

Research in digital therapeutics demonstrates that user engagement with mental health applications drops significantly when the interface feels clinical, complicated, or visually unappealing. Users must feel that the application is a supportive companion, not another source of stress competing for their attention.

For Sentry AI specifically, the interface must communicate several qualities:
- **Trust** — Users share sensitive information about their workload and emotional state
- **Calm** — The visual experience should feel peaceful, not overwhelming
- **Clarity** — Information should be immediately understandable
- **Motivation** — Design should encourage positive action without pressure
- **Professionalism** — The application serves working professionals and students

### 5.1.2 Design Principles

The following principles guided all design decisions:

**Simplicity Over Complexity**

Every screen focuses on a single primary action. Secondary features remain accessible but visually subordinate. Users should never feel overwhelmed by options or information density. White space is used generously to let content breathe.

**Progressive Disclosure**

Information is revealed gradually as users need it. The dashboard shows summary metrics; detailed breakdowns appear on dedicated screens. Recommendations show headlines first; action steps expand on demand. This approach prevents information overload while keeping depth accessible.

**Encouraging Without Pressuring**

The application encourages healthy behaviors through positive framing rather than guilt or fear. Instead of "You're working too much!" the interface communicates "Here's an opportunity to improve your well-being." Success is celebrated; setbacks are addressed with support rather than criticism.

**Consistency Across Platforms**

The design system ensures visual and interaction consistency between web and mobile platforms. Users moving between devices experience a familiar interface. Components, colors, typography, and spacing remain uniform throughout the application.

**Accessibility First**

All design decisions consider users with visual impairments, color blindness, or motor difficulties. Contrast ratios meet WCAG 2.1 AA standards. Touch targets are appropriately sized. Text remains readable without zooming. Color is never the only indicator of meaning.

---

## 5.2 Color Psychology and Palette Selection

### 5.2.1 The Psychology of Color in Wellness Applications

Color profoundly influences emotional state and behavior. In wellness applications, color choices directly impact whether users feel calm or anxious, motivated or discouraged, trusting or suspicious. The Sentry AI color palette was selected based on established research in color psychology.

**Blue — Trust and Calm**

Blue is universally associated with trust, stability, and calm. It lowers heart rate and reduces anxiety. Medical and wellness applications frequently use blue for these reasons. In Sentry AI, blue serves as the primary brand color, appearing in the logo, primary buttons, and key interactive elements. It communicates reliability and creates a sense of safety for users sharing sensitive information.

**Green — Health and Growth**

Green represents health, balance, and positive progress. It evokes nature and renewal. In Sentry AI, green indicates healthy burnout status (GREEN level) and successful actions. Green checkmarks confirm completed tasks. Green progress indicators celebrate improvement. The association with growth motivates users toward positive change.

**Yellow/Amber — Attention and Caution**

Yellow and amber attract attention without the alarm of red. These colors indicate moderate risk or items requiring awareness. In Sentry AI, amber represents the YELLOW burnout level—elevated risk that deserves attention but isn't critical. This color choice prompts action without inducing panic.

**Red — Urgency and Critical States**

Red signals urgency and critical situations requiring immediate attention. Its use is intentionally limited to avoid alarm fatigue. In Sentry AI, red appears only for RED burnout level (critical) and overdue tasks. Sparing use ensures red maintains its impact when it does appear.

**Purple — Wisdom and Creativity**

Purple is associated with wisdom, creativity, and premium quality. It provides visual interest without the intensity of warmer colors. In Sentry AI, purple accents appear in the AI companion interface, subtly suggesting intelligence and thoughtfulness.

**Neutral Tones — Foundation and Readability**

Dark grays and soft whites create the foundation for content. Dark backgrounds reduce eye strain during extended use, particularly important for users already experiencing fatigue. Light text on dark backgrounds is easier to read in low-light conditions common during evening work hours.

### 5.2.2 The Sentry AI Color Palette

**Primary Colors**

| Color | Hex Code | Usage |
|-------|----------|-------|
| Primary Blue | #4A90D9 | Brand color, primary buttons, links |
| Deep Navy | #1A1A2E | Background, cards |
| Dark Surface | #16213E | Secondary backgrounds |

**Status Colors**

| Color | Hex Code | Usage |
|-------|----------|-------|
| Healthy Green | #4CAF50 | GREEN status, success, completion |
| Warning Amber | #FFC107 | YELLOW status, attention needed |
| Critical Red | #F44336 | RED status, overdue, urgent |

**Accent Colors**

| Color | Hex Code | Usage |
|-------|----------|-------|
| Purple Accent | #9C27B0 | AI companion, special features |
| Teal Accent | #00BCD4 | Secondary actions, highlights |

**Neutral Colors**

| Color | Hex Code | Usage |
|-------|----------|-------|
| White | #FFFFFF | Primary text on dark backgrounds |
| Light Gray | #B0B0B0 | Secondary text, placeholders |
| Border Gray | #333333 | Dividers, borders |

### 5.2.3 Dark Theme Rationale

Sentry AI uses a dark theme as the default for several reasons:

**Reduced Eye Strain**

Users experiencing burnout often work long hours, including evenings. Dark interfaces emit less light, reducing eye strain and fatigue during extended sessions.

**Focus Enhancement**

Dark backgrounds allow content to stand out more prominently. Cards and interactive elements "pop" against the dark surface, directing attention where needed.

**Modern Aesthetic**

Dark themes communicate sophistication and modernity. They align with contemporary application design trends, making the application feel current and professionally designed.

**Energy Efficiency**

On OLED mobile screens, dark pixels consume less power. This practical benefit extends battery life for mobile users.

---

## 5.3 Typography

### 5.3.1 Font Selection

Sentry AI uses a clean, modern sans-serif typeface optimized for screen readability. The selected font family provides:

- **High legibility** at various sizes
- **Clear distinction** between characters (avoiding confusion between similar letters)
- **Professional appearance** appropriate for workplace contexts
- **Multiple weights** for establishing visual hierarchy
- **Excellent rendering** on both iOS and Android devices

### 5.3.2 Type Scale and Hierarchy

A consistent type scale creates clear visual hierarchy:

**Headings** use heavier weights and larger sizes to establish section importance. Screen titles are immediately recognizable. Section headers organize content into digestible groups.

**Body Text** uses regular weight at comfortable reading sizes. Line height is generous (1.5x) to improve readability. Paragraph width is constrained to prevent eye fatigue from long line lengths.

**Labels and Captions** use smaller sizes and lighter weights for secondary information. They remain readable but visually subordinate to primary content.

**Numbers and Metrics** use tabular figures ensuring digits align properly in columns and statistics. This is particularly important for burnout scores and task counts.

---

## 5.4 Iconography and Visual Elements

### 5.4.1 Icon Style

Icons throughout Sentry AI follow a consistent style:

- **Outline style** for navigation and secondary actions
- **Filled style** for active states and primary actions
- **Rounded corners** matching the overall soft, approachable aesthetic
- **Consistent stroke width** for visual harmony
- **Clear metaphors** ensuring icons are universally understood

### 5.4.2 Illustrations and Graphics

The burnout score visualization uses a gauge or circular progress indicator that immediately communicates status. The color fills from green through yellow to red, providing instant recognition of burnout level without reading numbers.

Charts and graphs use smooth curves and gradients rather than harsh lines. This softer approach maintains the calming aesthetic while communicating data effectively.

Empty states include friendly illustrations that encourage action without blame. A screen with no tasks shows an encouraging image rather than a stark "No data" message.

### 5.4.3 Cards and Containers

Content is organized into cards—elevated surfaces that group related information. Cards have:

- **Rounded corners** (soft, approachable feel)
- **Subtle shadows** or borders (visual separation without harshness)
- **Consistent padding** (breathing room for content)
- **Clear hierarchy** (title, content, actions)

---

## 5.5 Navigation and Information Architecture

### 5.5.1 Navigation Structure

The application uses bottom navigation for primary sections, a pattern familiar to mobile users and accessible with one-handed use. Primary sections include:

1. **Home/Dashboard** — Overview of burnout status and key metrics
2. **Tasks** — Task management and calendar
3. **AI Companion** — Chat interface for support and queries
4. **Recommendations** — Personalized action suggestions
5. **Profile** — Settings and user preferences

This structure ensures all major features are accessible within one tap from any screen.

### 5.5.2 Screen Flow

Users typically follow these primary flows:

**Check Status Flow:** Open app → View dashboard → See burnout score → Review contributing factors

**Get Help Flow:** Open app → Navigate to AI companion → Chat about feelings or questions → Receive support

**Take Action Flow:** View recommendations → Read details → Apply recommendation → Mark as complete

**Manage Work Flow:** Navigate to tasks → View task list → Add/edit tasks → Check completion

Each flow is designed to require minimal taps while providing clear feedback at each step.

---

## 5.6 Screen Designs by Service

The following sections describe each screen in the Sentry AI application, organized by functional area. Each screen description covers its purpose, key elements, user interactions, and design rationale.

---

### 5.6.1 Authentication Screens

*(Screens to be described after PDF upload)*

**Login Screen**

[Description pending - will detail the login interface including email/password fields, social login options, forgot password link, and visual design]

**Registration Screen**

[Description pending - will detail the registration flow including form fields, validation feedback, and onboarding elements]

**Forgot Password Screen**

[Description pending - will detail the password recovery flow]

---

### 5.6.2 Dashboard Screens

*(Screens to be described after PDF upload)*

**Home Dashboard**

[Description pending - will detail the main dashboard showing burnout score, key metrics, quick actions, and navigation]

**Burnout Score Detail**

[Description pending - will detail the expanded view of burnout analysis with component breakdown]

---

### 5.6.3 Task Management Screens

*(Screens to be described after PDF upload)*

**Task List**

[Description pending - will detail the task listing interface with filters, sorting, and status indicators]

**Task Detail/Edit**

[Description pending - will detail the task viewing and editing interface]

**Add Task**

[Description pending - will detail the task creation flow]

**Calendar View**

[Description pending - will detail the calendar visualization of tasks and meetings]

---

### 5.6.4 AI Companion Screens

*(Screens to be described after PDF upload)*

**Chat Interface**

[Description pending - will detail the conversational interface including message bubbles, input area, and quick actions]

**Voice Input**

[Description pending - will detail the audio recording interface]

**Diary Entry**

[Description pending - will detail the diary/journal entry interface]

---

### 5.6.5 Recommendation Screens

*(Screens to be described after PDF upload)*

**Recommendations List**

[Description pending - will detail the listing of personalized recommendations]

**Recommendation Detail**

[Description pending - will detail the expanded recommendation view with action steps]

---

### 5.6.6 Burnout Analysis Screens

*(Screens to be described after PDF upload)*

**Analysis Results**

[Description pending - will detail the burnout analysis results display]

**History/Trends**

[Description pending - will detail the historical trend visualization]

---

### 5.6.7 Task Extraction Screens

*(Screens to be described after PDF upload)*

**File Upload**

[Description pending - will detail the file upload interface for task extraction]

**Extraction Results**

[Description pending - will detail the display of extracted tasks for review]

---

### 5.6.8 Profile & Settings Screens

*(Screens to be described after PDF upload)*

**User Profile**

[Description pending - will detail the profile viewing and editing interface]

**Preferences**

[Description pending - will detail the preferences and settings interface]

**Constraints Management**

[Description pending - will detail the interface for managing user constraints]

---

### 5.6.9 Notebook Library Screens

*(Screens to be described after PDF upload)*

**Notebook List**

[Description pending - will detail the notebook listing interface]

**Notebook Chat**

[Description pending - will detail the chat interface for querying notebook content]

---

## 5.7 Responsive Design and Platform Considerations

### 5.7.1 Mobile-First Approach

Sentry AI was designed mobile-first, recognizing that users often check their burnout status and interact with the AI companion throughout the day from their phones. The mobile interface prioritizes:

- **Thumb-friendly navigation** with bottom navigation bar
- **Touch-optimized targets** (minimum 44x44 points)
- **Scannable content** optimized for quick glances
- **Offline awareness** with graceful handling of connectivity issues

### 5.7.2 Tablet and Web Adaptations

On larger screens, the interface adapts to take advantage of available space:

- **Side navigation** replaces bottom navigation on tablets
- **Multi-column layouts** display more information simultaneously
- **Expanded visualizations** provide richer data representation
- **Keyboard shortcuts** enable power-user workflows on web

---

## 5.8 Accessibility Considerations

### 5.8.1 Visual Accessibility

- **Contrast ratios** exceed WCAG 2.1 AA requirements (4.5:1 for text)
- **Color is not the sole indicator** — icons and labels accompany color-coded status
- **Text scaling** is supported up to 200% without layout breaking
- **Focus indicators** are clearly visible for keyboard navigation

### 5.8.2 Motor Accessibility

- **Touch targets** meet minimum size requirements (44x44 points)
- **Gestures have alternatives** — swipe actions include button equivalents
- **Timeout accommodations** allow users to extend time-limited operations

### 5.8.3 Screen Reader Support

- **Semantic markup** ensures logical reading order
- **Labels describe** all interactive elements
- **State changes** are announced appropriately
- **Images include** descriptive alt text

---

## 5.9 Summary

The UI/UX design of Sentry AI prioritizes user well-being at every level. Color psychology informs a palette that calms rather than agitates. Typography ensures comfortable reading during extended use. Navigation patterns minimize cognitive load for users already experiencing stress.

The 30 screens across nine functional areas provide a comprehensive interface for burnout detection, personalized recommendations, task management, and emotional support. Each screen is designed with intention—balancing information density with clarity, encouraging action without creating pressure, and maintaining consistency across the entire experience.

This design foundation supports the application's core mission: helping users recognize and prevent burnout through an interface that is itself a source of calm and support rather than additional stress.

---

## Suggested Figures

| Figure | Description |
|--------|-------------|
| 5.1 | Color palette with hex codes and usage examples |
| 5.2 | Typography scale showing heading and body styles |
| 5.3 | Icon set samples |
| 5.4 | Navigation structure diagram |
| 5.5-5.34 | Individual screen designs (30 screens from Figma) |
