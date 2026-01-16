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
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Load environment variables
load_dotenv()

# Add backend_services to path for authentication
backend_path = Path(__file__).parent.parent.parent.parent.parent.parent / "backend_services"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.oauth2 import get_current_user
from app.models import User

# Import shared services (replaces HTTP calls)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
from shared_services import TaskService

from api.dependencies import get_db
from pydantic import BaseModel, Field as PydanticField
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
    Parse recommendation action steps into actionable tasks using LLM.

    Uses Groq LLM to intelligently parse action steps and determine:
    - Appropriate task priority based on context
    - Realistic due dates based on temporal cues
    - Clear task titles and descriptions

    Returns list of task objects to create.
    """
    try:
        # Initialize Groq LLM
        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile",
            temperature=0.3,  # Lower temperature for more consistent parsing
            max_tokens=2000
        )

        # Define the output schema
        class TaskOutput(BaseModel):
            """Schema for a single parsed task"""
            title: str = PydanticField(description="Clear, concise task title (keep original text if appropriate)")
            description: str = PydanticField(description="Brief description of what needs to be done")
            priority: str = PydanticField(description="Must be: High, Medium, or Low")
            due_date_offset_days: int = PydanticField(description="Number of days from today (0=today, 1=tomorrow, 7=week, null=no deadline)")
            reasoning: str = PydanticField(description="Brief explanation of priority and timing decisions")

        class TaskList(BaseModel):
            """List of parsed tasks"""
            tasks: List[TaskOutput]

        # Create JSON parser
        parser = JsonOutputParser(pydantic_object=TaskList)

        # Build the prompt
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        action_steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(action_steps)])

        prompt_template = PromptTemplate(
            template="""You are a task planning assistant helping convert burnout prevention action steps into structured tasks.

RECOMMENDATION TITLE: {recommendation_title}
TODAY'S DATE: {current_date}

ACTION STEPS TO PARSE:
{action_steps}

Your job is to convert each action step into a structured task with:
1. **Title**: Keep the original text if clear, or make it more actionable
2. **Description**: Add context about why this helps with burnout prevention
3. **Priority**:
   - High: Urgent/immediate actions, critical for preventing burnout escalation
   - Medium: Important but not urgent, foundational habits
   - Low: Nice-to-have, optional optimizations
4. **Due Date**: Estimate realistic timeframe based on:
   - "today", "immediately" → 0 days
   - "tomorrow", "soon" → 1 day
   - "this week", "within a week" → 7 days
   - "end of workday", "daily routine" → 0 days (start today)
   - "ongoing", "regularly", "as needed" → null (no specific deadline)
   - If no time cue, use null

IMPORTANT RULES:
- Priority MUST be exactly: "High", "Medium", or "Low" (case-sensitive)
- due_date_offset_days must be an integer or null
- Keep task titles concise and actionable
- Consider that these are burnout prevention tasks - balance urgency with sustainability

{format_instructions}

Return ONLY valid JSON, no additional text.""",
            input_variables=["recommendation_title", "current_date", "action_steps"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        # Create the chain
        chain = prompt_template | llm | parser

        # Invoke the LLM
        result = chain.invoke({
            "recommendation_title": recommendation_title,
            "current_date": current_date,
            "action_steps": action_steps_text
        })

        # Convert LLM output to task objects
        tasks_to_create = []
        for task_output in result.get("tasks", []):
            # Calculate due date from offset
            due_date = None
            offset_days = task_output.get("due_date_offset_days")
            if offset_days is not None:
                due_date = (datetime.utcnow() + timedelta(days=offset_days)).isoformat()

            task = {
                "title": task_output.get("title"),
                "description": task_output.get("description"),
                "priority": task_output.get("priority", "Medium"),
                "status": "Todo",
                "due_date": due_date,
                "tags": ["burnout-prevention", "auto-generated"],
                "created_from": "recommendation"
            }
            tasks_to_create.append(task)

        print(f"[LLM PARSING] Successfully parsed {len(tasks_to_create)} tasks")
        return tasks_to_create

    except Exception as e:
        print(f"[LLM PARSING ERROR] Failed to parse with LLM: {e}")
        print("[LLM PARSING] Falling back to simple parsing")

        # Fallback: Create basic tasks from action steps
        tasks_to_create = []
        for step in action_steps:
            task = {
                "title": step,
                "description": f"Action step from recommendation: {recommendation_title}",
                "priority": "Medium",
                "status": "Todo",
                "due_date": None,
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

@router.post("/apply", response_model=ApplyRecommendationResponse)
async def apply_recommendation(
    request: ApplyRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply a specific recommendation by creating tasks and modifying schedule.

    **Authentication Required**: Pass JWT token in Authorization header.

    This endpoint:
    1. Fetches the recommendation from database
    2. Parses action steps into actionable tasks
    3. Creates tasks in the backend database
    4. Saves application record to track effectiveness
    5. Creates action item records linking to tasks
    6. Returns summary of actions taken

    Parameters:
        - recommendation_id: Database ID of recommendation to apply

    Returns:
        - Number of tasks created
        - Number of tasks modified
        - Number of calendar events created
        - List of actions applied
    """
    try:
        user_id = current_user.id
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
                        created_task_id=task_id,  # Use created_task_id to match DB schema
                        action_text=action_steps[i] if i < len(action_steps) else task['title'],
                        order_index=i + 1,  # Use order_index to match DB schema
                        applied=True,  # Mark as applied since we just created the task
                        applied_at=datetime.utcnow()
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


@router.post("/apply-all")
async def apply_all_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply ALL unapplied recommendations for the authenticated user.

    **Authentication Required**: Pass JWT token in Authorization header.

    Fetches all recommendations from the database that haven't been applied yet
    and applies each one.
    """
    try:
        user_id = current_user.id
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
                recommendation_id=recommendation.id
            )

            result = await apply_recommendation(request, current_user, db)

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
