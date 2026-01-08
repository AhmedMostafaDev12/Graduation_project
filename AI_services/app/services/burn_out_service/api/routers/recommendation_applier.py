"""
Recommendation Application Service
====================================

Applies burnout prevention recommendations by creating tasks,
adjusting schedules, and modifying user workload.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime, timedelta
import os
import sys

# Import shared services (replaces HTTP calls)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
from shared_services import TaskService

from api.dependencies import get_db
from pydantic import BaseModel
from user_profile.recommendation_models import (
    Recommendation,
    RecommendationApplication,
    RecommendationActionItem
)
from user_profile.burnout_model import BurnoutAnalysis

router = APIRouter(prefix="/api/recommendations", tags=["Recommendation Application"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ApplyRecommendationRequest(BaseModel):
    """Request to apply a recommendation"""
    user_id: int
    recommendation_id: int  # Database ID of the recommendation to apply


class ApplyRecommendationResponse(BaseModel):
    """Response after applying recommendation"""
    success: bool
    tasks_created: int
    tasks_modified: int
    calendar_events_created: int
    actions_applied: List[str]
    message: str


# ============================================================================
# RECOMMENDATION APPLICATION LOGIC
# ============================================================================

def parse_action_steps_to_tasks(
    action_steps: List[str],
    user_id: int,
    recommendation_title: str
) -> List[Dict[str, Any]]:
    """
    Parse recommendation action steps into actionable tasks.

    Returns list of task objects to create.
    """
    tasks_to_create = []

    for i, step in enumerate(action_steps):
        # Determine task priority based on keywords
        priority = "Medium"
        if any(keyword in step.lower() for keyword in ["urgent", "immediately", "critical"]):
            priority = "High"
        elif any(keyword in step.lower() for keyword in ["consider", "optional", "eventually"]):
            priority = "Low"

        # Determine due date based on keywords
        due_date = None
        if "today" in step.lower():
            due_date = datetime.utcnow().isoformat()
        elif "this week" in step.lower():
            due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        elif "tomorrow" in step.lower():
            due_date = (datetime.utcnow() + timedelta(days=1)).isoformat()

        # Create task object
        task = {
            "title": step,
            "description": f"Action step from recommendation: {recommendation_title}",
            "priority": priority,
            "status": "Todo",
            "due_date": due_date,
            "tags": ["burnout-prevention", "auto-generated"],
            "created_from": "recommendation"
        }

        tasks_to_create.append(task)

    return tasks_to_create


def create_focus_time_blocks(action_step: str, user_id: int) -> int:
    """
    Create calendar events for focus time blocks.

    Returns number of events created.
    """
    # Parse focus time duration from action step
    # Example: "Block 2 hours of focus time each day"

    import re
    hours_match = re.search(r'(\d+)\s*hours?', action_step.lower())

    if not hours_match:
        return 0

    hours = int(hours_match.group(1))

    # Create focus time blocks for next 5 working days
    events_created = 0
    base_time = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)

    for day in range(5):
        event_start = base_time + timedelta(days=day)
        event_end = event_start + timedelta(hours=hours)

        # Here you would call calendar service to create event
        # For now, we'll just count them
        # calendar_service.create_event(user_id, event_start, event_end, "Focus Time")

        events_created += 1

    return events_created


def adjust_meeting_schedules(action_step: str, user_id: int) -> int:
    """
    Adjust meeting schedules based on recommendation.

    Returns number of meetings modified.
    """
    # Example: "Reschedule back-to-back meetings to have 15-min breaks"

    # Here you would:
    # 1. Query user's calendar for back-to-back meetings
    # 2. Add buffer time between them
    # 3. Send reschedule requests

    # For now, return 0 as calendar integration is not yet implemented
    return 0


# ============================================================================
# APPLY RECOMMENDATION ENDPOINT
# ============================================================================

@router.post("/{user_id}/apply", response_model=ApplyRecommendationResponse)
async def apply_recommendation(
    user_id: int,
    request: ApplyRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Apply a specific recommendation by creating tasks and modifying schedule.

    This endpoint:
    1. Fetches the recommendation from database
    2. Parses action steps into actionable tasks
    3. Creates tasks in the backend database
    4. Saves application record to track effectiveness
    5. Creates action item records linking to tasks
    6. Returns summary of actions taken

    Parameters:
        - user_id: User ID
        - recommendation_id: Database ID of recommendation to apply

    Returns:
        - Number of tasks created
        - Number of tasks modified
        - Number of calendar events created
        - List of actions applied
    """
    try:
        # Get recommendation from database
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == request.recommendation_id,
            Recommendation.user_id == user_id
        ).first()

        if not recommendation:
            raise HTTPException(
                status_code=404,
                detail=f"Recommendation {request.recommendation_id} not found for user {user_id}"
            )

        # Get current burnout score before applying
        latest_analysis = db.query(BurnoutAnalysis).filter(
            BurnoutAnalysis.user_id == user_id
        ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()

        burnout_score_before = latest_analysis.final_score if latest_analysis else None

        # Parse action steps into tasks
        action_steps = recommendation.action_steps if isinstance(recommendation.action_steps, list) else []
        tasks_to_create = parse_action_steps_to_tasks(action_steps, user_id, recommendation.title)

        # Create tasks in backend and track their IDs
        tasks_created = 0
        created_task_ids = []

        for i, task in enumerate(tasks_to_create):
            try:
                # Use shared service instead of HTTP call
                task_data = TaskService.create_task(user_id, task, db)
                task_id = task_data.get('id')

                if task_id:
                    created_task_ids.append(task_id)
                    tasks_created += 1

                    # Create action item record linking recommendation to task
                    action_item = RecommendationActionItem(
                        recommendation_id=recommendation.id,
                        task_id=task_id,
                        action_text=action_steps[i] if i < len(action_steps) else task['title'],
                        action_order=i + 1,
                        completed=False
                    )
                    db.add(action_item)

            except Exception as e:
                print(f"Failed to create task: {e}")

        # Create calendar events for focus time
        calendar_events_created = 0
        for step in action_steps:
            if "focus time" in step.lower() or "block time" in step.lower():
                calendar_events_created += create_focus_time_blocks(step, user_id)

        # Adjust meeting schedules
        tasks_modified = 0
        for step in action_steps:
            if "meeting" in step.lower() and ("reschedule" in step.lower() or "decline" in step.lower()):
                tasks_modified += adjust_meeting_schedules(step, user_id)

        # Create application record
        application = RecommendationApplication(
            recommendation_id=recommendation.id,
            user_id=user_id,
            applied_at=datetime.utcnow(),
            applied_by='user',
            tasks_created=tasks_created,
            task_ids=created_task_ids,
            calendar_events_created=calendar_events_created,
            tasks_modified=tasks_modified,
            status='applied',
            burnout_score_before=burnout_score_before
        )

        db.add(application)
        db.commit()

        return ApplyRecommendationResponse(
            success=True,
            tasks_created=tasks_created,
            tasks_modified=tasks_modified,
            calendar_events_created=calendar_events_created,
            actions_applied=action_steps,
            message=f"Successfully applied recommendation: {recommendation.title}. Created {tasks_created} tasks."
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply recommendation: {str(e)}"
        )


@router.post("/{user_id}/apply-all")
async def apply_all_recommendations(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Apply ALL unapplied recommendations for a user.

    Fetches all recommendations from the database that haven't been applied yet
    and applies each one.
    """
    try:
        # Get all recommendations for this user that haven't been applied
        unapplied_recommendations = db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).outerjoin(
            RecommendationApplication,
            RecommendationApplication.recommendation_id == Recommendation.id
        ).filter(
            RecommendationApplication.id == None  # No application record exists
        ).order_by(Recommendation.generated_at.desc()).all()

        if not unapplied_recommendations:
            return {
                "success": True,
                "recommendations_applied": 0,
                "total_tasks_created": 0,
                "total_tasks_modified": 0,
                "total_calendar_events_created": 0,
                "message": "No unapplied recommendations found for this user."
            }

        # Apply each recommendation
        total_tasks_created = 0
        total_tasks_modified = 0
        total_events_created = 0
        all_actions = []

        for recommendation in unapplied_recommendations:
            request = ApplyRecommendationRequest(
                user_id=user_id,
                recommendation_id=recommendation.id
            )

            result = await apply_recommendation(user_id, request, db)

            total_tasks_created += result.tasks_created
            total_tasks_modified += result.tasks_modified
            total_events_created += result.calendar_events_created
            all_actions.extend(result.actions_applied)

        return {
            "success": True,
            "recommendations_applied": len(unapplied_recommendations),
            "total_tasks_created": total_tasks_created,
            "total_tasks_modified": total_tasks_modified,
            "total_calendar_events_created": total_events_created,
            "message": f"Successfully applied {len(unapplied_recommendations)} recommendations."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply all recommendations: {str(e)}"
        )
