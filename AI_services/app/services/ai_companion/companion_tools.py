"""
AI Companion Tools
==================

Tools that the companion agent can use to interact with the system:
1. Save emotional entries to qualitative_data
2. Get task statistics
3. Get burnout status and recommendations
4. Create tasks from natural language
5. Query user data
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

# Import shared services (replaces HTTP calls)
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared_services import (
    TaskService,
    BurnoutService,
    RecommendationService,
    ExtractionService,
    SentimentService
)

Base = declarative_base()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _trigger_burnout_analysis_background(user_id: int, db: Session):
    """
    Trigger burnout analysis in background (non-blocking).

    This is called after saving qualitative data to update the analysis
    so next time user asks, they get fresh recommendations.

    Uses threading to avoid blocking the response to the user.
    Now uses direct function call instead of HTTP.
    """
    import threading

    def _run_analysis():
        try:
            # Use shared service instead of HTTP call
            result = BurnoutService.analyze_auto(user_id, db, store_history=True)
            if result.get("status") != "failed":
                print(f"✅ Background burnout analysis completed for user {user_id}")
            else:
                print(f"⚠️ Background burnout analysis failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"⚠️ Background burnout analysis failed: {e}")

    # Run in background thread (non-blocking)
    thread = threading.Thread(target=_run_analysis, daemon=True)
    thread.start()


# ============================================================================
# DATABASE MODELS
# ============================================================================

class QualitativeData(Base):
    """Qualitative data model"""
    __tablename__ = "qualitative_data"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    entry_type = Column(String)  # 'diary_entry', 'feeling_check_in', 'conversation', 'task_note'
    content = Column(Text, nullable=False)
    sentiment_score = Column(Float)
    task_id = Column(Integer, nullable=True)  # Optional: link to specific task
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# TOOL 1: Save Emotional Entry
# ============================================================================

def save_emotional_entry(
    user_id: int,
    content: str,
    entry_type: str = "conversation",
    task_id: Optional[int] = None,
    db: Session = None
) -> Dict[str, Any]:
    """
    Save emotional entry to qualitative_data table.

    Used for:
    - Diary entries
    - Feeling check-ins
    - Emotional conversations
    - Mental health notes

    Also triggers burnout analysis in BACKGROUND so next time
    user asks for recommendations, they'll have updated data.

    Returns sentiment analysis and entry ID.
    """
    try:
        # Analyze sentiment using Ollama
        sentiment_result = analyze_sentiment_with_llm(content)

        # Save to database
        entry = QualitativeData(
            user_id=user_id,
            entry_type=entry_type,
            content=content,
            sentiment_score=sentiment_result.get("score", 0.0),
            task_id=task_id  # Optional: link to specific task
        )

        db.add(entry)
        db.commit()
        db.refresh(entry)

        # Trigger burnout analysis in BACKGROUND (non-blocking)
        # This updates the analysis so next query gets fresh recommendations
        _trigger_burnout_analysis_background(user_id, db)

        return {
            "success": True,
            "entry_id": entry.id,
            "sentiment": sentiment_result.get("label"),
            "score": sentiment_result.get("score"),
            "themes": sentiment_result.get("themes", [])
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def analyze_sentiment_with_llm(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment using the existing Sentiment Analyzer.

    Uses the production sentiment analyzer from burnout service
    with LangChain + Ollama (Llama 3.1 8B).

    Returns:
    - label: "positive", "neutral", "negative", "distressed"
    - score: -1.0 to 1.0
    - themes: List of emotional themes
    """
    try:
        # Import the existing sentiment analyzer from burnout service
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'burn_out_service'))

        from Analysis_engine_layer.sentiment_analyzer import SentimentAnalyzer, QualitativeData

        # Initialize analyzer
        analyzer = SentimentAnalyzer(model_name="llama3.1:8b")

        # Create qualitative data object with the text
        qual_data = QualitativeData(user_check_ins=[text])

        # Run analysis
        result = analyzer.analyze_qualitative_data(qual_data)

        # Extract sentiment label from score
        score = result.sentiment_score
        if score >= 0.5:
            label = "positive"
        elif score >= -0.2:
            label = "neutral"
        elif score >= -0.6:
            label = "negative"
        else:
            label = "distressed"

        # Extract themes from burnout signals
        themes = []
        if result.burnout_signals.emotional_exhaustion:
            themes.append("emotional_exhaustion")
        if result.burnout_signals.overwhelm:
            themes.append("overwhelm")
        if result.burnout_signals.sleep_concerns:
            themes.append("sleep_issues")
        if result.burnout_signals.negative_outlook:
            themes.append("negativity")
        if result.burnout_signals.health_concerns:
            themes.append("health_concerns")

        return {
            "label": label,
            "score": score,
            "themes": themes,
            "summary": result.summary
        }

    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        # Fallback to neutral if analyzer fails
        return {
            "label": "neutral",
            "score": 0.0,
            "themes": [],
            "summary": f"Analysis unavailable: {str(e)}"
        }


# ============================================================================
# TOOL 2: Get Task Statistics
# ============================================================================

def get_task_statistics(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Get comprehensive task statistics for the user.

    Uses the shared service instead of HTTP call.

    Returns:
    - Total tasks
    - Overdue tasks
    - Tasks due this week
    - Completion rate
    - Work hours breakdown
    """
    try:
        # Use shared service instead of HTTP call
        data = BurnoutService.get_workload_breakdown(user_id, db)

        if data.get('status') == 'failed':
            return {
                "success": False,
                "error": data.get('error', 'Workload breakdown failed')
            }

        task_breakdown = data.get('task_breakdown', {})
        time_breakdown = data.get('time_breakdown', {})

        return {
            "success": True,
            "total_tasks": task_breakdown.get('active_tasks', 0),
            "overdue_tasks": task_breakdown.get('overdue_tasks', 0),
            "due_this_week": task_breakdown.get('tasks_due_this_week', 0),
            "completion_rate": task_breakdown.get('completion_rate', 0),
            "work_hours_today": time_breakdown.get('work_hours_today', 0),
            "work_hours_week": time_breakdown.get('work_hours_this_week', 0),
            "meeting_hours_today": time_breakdown.get('meeting_hours_today', 0)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# TOOL 3: Get Burnout Status
# ============================================================================

def get_burnout_status(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Get current burnout status and analysis.

    Gets EXISTING analysis from database (no computation latency).
    The analysis is updated in background when qualitative data is saved.
    Now uses shared service instead of HTTP call.

    Returns:
    - Burnout score (0-100)
    - Burnout level (GREEN/YELLOW/RED)
    - Component breakdown
    - Warning signals
    - Recovery actions
    """
    try:
        # Use shared service instead of HTTP call
        data = BurnoutService.get_latest_analysis(user_id, db)

        if data is None:
            return {
                "success": False,
                "error": "No burnout analysis found. Please use the app for a while to generate analysis."
            }

        return {
            "success": True,
            "burnout_score": data.get("burnout_score", 0),
            "burnout_level": data.get("level", "UNKNOWN"),
            "component_breakdown": data.get("components", {}),
            "analyzed_at": data.get("analyzed_at", ""),
            "insights": data.get("insights", {})
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# TOOL 4: Get Recent Recommendations
# ============================================================================

def get_recent_recommendations(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Get recent burnout prevention recommendations.

    Returns personalized recommendations from RAG system based on
    latest burnout analysis (already computed in background).
    Now uses shared service instead of HTTP call.
    """
    try:
        # Use shared service instead of HTTP call
        data = RecommendationService.get_for_user(user_id, db)

        if data.get("error"):
            return {
                "success": False,
                "error": data.get("error", "Failed to get recommendations")
            }

        # Extract recommendations list
        recommendations_list = data.get("recommendations", [])

        # Convert to simple dict format for LLM
        simplified_recs = []
        for rec in recommendations_list:
            if isinstance(rec, dict):
                simplified_recs.append({
                    "title": rec.get("title", ""),
                    "priority": rec.get("priority", "MEDIUM"),
                    "description": rec.get("description", ""),
                    "action_steps": rec.get("action_steps", []),
                    "expected_impact": rec.get("expected_impact", "")
                })

        return {
            "success": True,
            "recommendations": simplified_recs,
            "count": len(simplified_recs),
            "burnout_level": data.get("burnout_level", "UNKNOWN"),
            "generated_at": data.get("generated_at", ""),
            "reasoning": data.get("reasoning", "")
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# TOOL 5: Create Task from Natural Language
# ============================================================================

def create_task_from_text(
    user_id: int,
    task_description: str,
    db: Session
) -> Dict[str, Any]:
    """
    Create a task from natural language description.

    Uses text extraction service to parse task details from user message.
    Now uses shared service instead of HTTP call.

    Examples:
    - "Finish the report by Friday"
    - "Schedule meeting with team tomorrow at 2pm"
    - "Buy groceries this weekend"
    """
    try:
        # Use shared service instead of HTTP call
        tasks = ExtractionService.extract_from_text(task_description, user_id, db)

        return {
            "success": True,
            "tasks_created": len(tasks),
            "tasks": tasks
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# TOOL 6: Get Task Summary
# ============================================================================

def get_task_summary(user_id: int, db: Session, limit: int = 5) -> Dict[str, Any]:
    """
    Get a summary of recent and upcoming tasks.
    Now uses shared service instead of HTTP call.

    Returns:
    - Next N upcoming tasks
    - Recently completed tasks
    - High priority tasks
    """
    try:
        # Use shared service instead of HTTP call
        tasks = TaskService.get_all_tasks(user_id, db)

        from datetime import datetime

        # Categorize tasks
        upcoming = []
        recent_completed = []
        high_priority = []

        now = datetime.utcnow()

        for task in tasks:
            # High priority
            if task.get('priority') in ['High', 'HIGH', 'URGENT', 'CRITICAL']:
                high_priority.append(task)

            # Recently completed
            if task.get('status') == 'Completed':
                recent_completed.append(task)

            # Upcoming (has due date in future, not completed)
            due_date_str = task.get('due_date')
            if due_date_str and task.get('status') != 'Completed':
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    if due_date > now:
                        upcoming.append((due_date, task))
                except:
                    pass

        # Sort upcoming by due date
        upcoming.sort(key=lambda x: x[0])
        upcoming_tasks = [t[1] for t in upcoming[:limit]]

        # Sort recent completed by update time
        recent_completed.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        recent_completed = recent_completed[:limit]

        return {
            "success": True,
            "upcoming_tasks": upcoming_tasks,
            "recent_completed": recent_completed,
            "high_priority_tasks": high_priority[:limit]
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
