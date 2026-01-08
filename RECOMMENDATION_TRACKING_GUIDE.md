# Recommendation Tracking System - Implementation Guide

## Overview

The recommendation tracking system has been fully implemented with database persistence, application tracking, and effectiveness measurement.

## Database Schema

### Tables Created

1. **recommendations** - Stores all AI-generated recommendations
   - Links to user and burnout analysis
   - Stores title, priority, description, action steps, expected impact
   - Tracks generation metadata (LLM model, generation time, strategies retrieved)

2. **recommendation_applications** - Tracks when recommendations are applied
   - Records tasks created, calendar events, tasks modified
   - Tracks effectiveness rating and user feedback
   - Measures burnout score before/after with computed improvement
   - Status tracking: applied → in_progress → completed/cancelled

3. **recommendation_action_items** - Individual action step tracking
   - Links action steps to created tasks
   - Tracks completion status for each step
   - Maintains action order

4. **recommendation_feedback** - Detailed user feedback
   - Records whether recommendation was helpful
   - Identifies most/least helpful action steps
   - Free-form comments for improvement

## API Endpoints

### 1. Generate Recommendations (Enhanced)

**Endpoint:** `GET /api/recommendations/{user_id}`

**What's New:**
- Now saves recommendations to database automatically
- Returns recommendation IDs in response
- Links to the burnout analysis that triggered generation

**Response:**
```json
{
  "user_id": 1,
  "generated_at": "2025-01-15T10:30:00",
  "burnout_level": "MODERATE",
  "recommendations": [
    {
      "recommendation_id": 123,  // NEW: Database ID
      "title": "Reduce Meeting Overload",
      "priority": "HIGH",
      "description": "...",
      "action_steps": ["Step 1", "Step 2", "Step 3"],
      "expected_impact": "..."
    }
  ],
  "reasoning": "...",
  "metadata": {
    "strategies_retrieved": 5,
    "llm_model": "llama3.1:8b",
    "generation_time_seconds": 12.5
  }
}
```

### 2. Get Pending Recommendations

**Endpoint:** `GET /api/recommendations/{user_id}/pending`

**Purpose:** Get all unapplied recommendations for display in frontend

**Response:**
```json
{
  "user_id": 1,
  "pending_count": 3,
  "recommendations": [
    {
      "id": 123,
      "title": "Reduce Meeting Overload",
      "priority": "HIGH",
      "description": "...",
      "action_steps": ["Step 1", "Step 2"],
      "expected_impact": "...",
      "generated_at": "2025-01-15T10:30:00",
      "category": "meeting_overload"
    }
  ]
}
```

### 3. Get Recommendation History

**Endpoint:** `GET /api/recommendations/{user_id}/history?include_unapplied=true`

**Purpose:** View all recommendations with application status

**Response:**
```json
{
  "user_id": 1,
  "total_recommendations": 10,
  "recommendations": [
    {
      "id": 123,
      "title": "Reduce Meeting Overload",
      "priority": "HIGH",
      "applied": true,
      "generated_at": "2025-01-15T10:30:00",
      "application_data": {
        "applied_at": "2025-01-15T14:00:00",
        "tasks_created": 3,
        "status": "completed",
        "effectiveness_rating": 5,
        "burnout_score_before": 75,
        "burnout_score_after": 60,
        "completion_rate": 100
      }
    }
  ]
}
```

### 4. Apply Single Recommendation

**Endpoint:** `POST /api/recommendations/{user_id}/apply`

**Request Body:**
```json
{
  "user_id": 1,
  "recommendation_id": 123  // Database ID from GET pending/history
}
```

**Response:**
```json
{
  "success": true,
  "tasks_created": 3,
  "tasks_modified": 1,
  "calendar_events_created": 5,
  "actions_applied": ["Step 1", "Step 2", "Step 3"],
  "message": "Successfully applied recommendation: Reduce Meeting Overload. Created 3 tasks."
}
```

**What Happens:**
1. Fetches recommendation from database
2. Parses action steps into tasks with intelligent priority/due date detection
3. Creates tasks in backend via API
4. Creates action item records linking recommendation to tasks
5. Saves application record with burnout score before applying
6. Creates calendar events for focus time blocks

### 5. Apply All Recommendations

**Endpoint:** `POST /api/recommendations/{user_id}/apply-all`

**Purpose:** Apply all unapplied recommendations at once

**Response:**
```json
{
  "success": true,
  "recommendations_applied": 3,
  "total_tasks_created": 9,
  "total_tasks_modified": 2,
  "total_calendar_events_created": 15,
  "message": "Successfully applied 3 recommendations."
}
```

### 6. Submit Feedback

**Endpoint:** `POST /api/recommendations/{recommendation_id}/feedback`

**Request Body:**
```json
{
  "user_id": 1,
  "helpful": true,
  "completed": true,
  "impact_rating": 5,  // 1-5 stars
  "notes": "This really helped reduce my stress!"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback received and will be used to improve recommendations",
  "recommendation_id": 123
}
```

**What Happens:**
1. Creates feedback record
2. Updates application record with effectiveness rating
3. Marks recommendation as completed if `completed: true`

## Frontend Implementation Guide

### Displaying Recommendations

```javascript
// 1. Fetch pending recommendations
const response = await fetch(`/api/recommendations/${userId}/pending`);
const data = await response.json();

// Display each recommendation with "Apply" button
data.recommendations.forEach(rec => {
  displayRecommendation({
    id: rec.id,
    title: rec.title,
    priority: rec.priority,
    actionSteps: rec.action_steps,
    onApply: () => applyRecommendation(userId, rec.id)
  });
});
```

### Applying Recommendations

```javascript
// Single recommendation
async function applyRecommendation(userId, recommendationId) {
  const response = await fetch(`/api/recommendations/${userId}/apply`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      recommendation_id: recommendationId
    })
  });

  const result = await response.json();

  if (result.success) {
    showNotification(`Created ${result.tasks_created} tasks!`);
    refreshRecommendations(); // Reload pending list
  }
}

// Apply all
async function applyAllRecommendations(userId) {
  const response = await fetch(`/api/recommendations/${userId}/apply-all`, {
    method: 'POST'
  });

  const result = await response.json();

  if (result.success) {
    showNotification(`Applied ${result.recommendations_applied} recommendations, created ${result.total_tasks_created} tasks!`);
    refreshRecommendations();
  }
}
```

### Showing Recommendation History

```javascript
// Fetch history
const response = await fetch(`/api/recommendations/${userId}/history`);
const data = await response.json();

// Display with status
data.recommendations.forEach(rec => {
  displayHistoryItem({
    title: rec.title,
    generatedAt: rec.generated_at,
    applied: rec.applied,
    tasksCreated: rec.application_data?.tasks_created,
    effectiveness: rec.application_data?.effectiveness_rating,
    burnoutImprovement: rec.application_data?.burnout_score_before - rec.application_data?.burnout_score_after
  });
});
```

### Submitting Feedback

```javascript
async function submitFeedback(recommendationId, userId, rating, notes) {
  const response = await fetch(`/api/recommendations/${recommendationId}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      helpful: rating >= 3,
      completed: true,
      impact_rating: rating,
      notes: notes
    })
  });

  const result = await response.json();

  if (result.status === 'success') {
    showNotification('Thank you for your feedback!');
  }
}
```

## Task Parsing Intelligence

The system automatically parses action steps into tasks with smart detection:

### Priority Detection
- **High:** "urgent", "immediately", "critical"
- **Medium:** Default
- **Low:** "consider", "optional", "eventually"

### Due Date Detection
- **Today:** "today"
- **Tomorrow:** "tomorrow"
- **This Week:** "this week"

### Example
Action step: "Urgently block 2 hours of focus time today"
→ Creates task with:
- Priority: High
- Due date: Today
- Title: "Urgently block 2 hours of focus time today"
- Tags: ["burnout-prevention", "auto-generated"]

## Analytics Views (Database)

Two SQL views are created for analytics:

1. **recommendation_effectiveness** - Global effectiveness metrics
2. **user_recommendation_history** - Per-user history

These can be queried for dashboards and insights.

## Migration Required

Before using these features, run:

```bash
psql -U your_user -d your_database -f recommendation_tracking_migration.sql
```

## Summary of Changes

### Files Modified:
1. `AI_services/app/services/burn_out_service/api/routers/recommendations.py`
   - Now saves recommendations to database
   - Added `/history` and `/pending` endpoints
   - Enhanced feedback endpoint to save to database

2. `AI_services/app/services/burn_out_service/api/routers/recommendation_applier.py`
   - Changed from index-based to ID-based recommendation selection
   - Saves application records when applying
   - Creates action item records linking to tasks
   - Tracks burnout score before applying

### Files Created:
1. `AI_services/app/services/burn_out_service/user_profile/recommendation_models.py`
   - SQLAlchemy models for all 4 tables

2. `recommendation_tracking_migration.sql`
   - Complete database schema with indexes and views

## Benefits

✅ **Persistence:** Recommendations are saved and can be retrieved later
✅ **Tracking:** Full audit trail of what was applied and when
✅ **Effectiveness:** Measure burnout improvement from recommendations
✅ **Learning:** Feedback data to improve future recommendations
✅ **Integration:** Action items linked to actual tasks in task database
✅ **Analytics:** Built-in views for effectiveness analysis
