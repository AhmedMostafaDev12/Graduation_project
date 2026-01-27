"""
Recommendations Endpoints
=========================

FastAPI router for AI-generated personalized recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import time
import sys
from pathlib import Path

# Add backend_services to path for authentication
backend_path = Path(__file__).parent.parent.parent.parent.parent.parent / "backend_services"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from sentry_app.oauth2 import get_current_user
from sentry_app.models import User

from sentry_app.services.burn_out_service.api.dependencies import get_db
from sentry_app.services.burn_out_service.api.schemas.recommendation_schemas import (
    RecommendationResponse,
    RecommendationItem,
    RecommendationMetadata,
    RecommendationFeedbackRequest
)

from sentry_app.services.burn_out_service.recommendations_RAG.recommendation_engine import RecommendationEngine
from sentry_app.services.burn_out_service.user_profile.burnout_model import BurnoutAnalysis
from sentry_app.services.burn_out_service.user_profile.integration_services import BurnoutSystemIntegration
from sentry_app.services.burn_out_service.user_profile.recommendation_models import (
    Recommendation,
    RecommendationApplication,
    RecommendationActionItem,
    RecommendationFeedback
)

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


# ============================================================================
# RECOMMENDATIONS ENDPOINTS
# ============================================================================

@router.post("/generate", response_model=RecommendationResponse)
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    include_events: bool = Query(True, description="Include calendar-specific recommendations"),
    db: Session = Depends(get_db)
):
    """
    Get AI-generated personalized recommendations for the authenticated user.

    **Authentication Required**: Pass JWT token in Authorization header.

    This endpoint:
    1. Retrieves user's latest burnout analysis
    2. Fetches user profile context
    3. Retrieves evidence-based strategies from vector database (RAG)
    4. Generates personalized recommendations using LLM
    5. (Optional) Includes calendar-specific recommendations

    Parameters:
        - include_events: Whether to include calendar-specific recs

    Returns:
        - List of personalized recommendations with:
          - Title, priority, description
          - Actionable steps
          - Expected impact
        - LLM reasoning
        - Generation metadata
    """
    try:
        user_id = current_user.id
        start_time = time.time()

        # Get latest burnout analysis
        latest_analysis = db.query(BurnoutAnalysis).filter(
            BurnoutAnalysis.user_id == user_id
        ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()

        if not latest_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"No burnout analysis found for user {user_id}. Please run analysis first."
            )

        # Build analysis result dict
        integration = BurnoutSystemIntegration(db)
        from sentry_app.services.burn_out_service.user_profile.user_profile_service import UserProfileService

        profile_service = UserProfileService(db)
        complete_profile = profile_service.get_complete_profile_for_llm(user_id)

        analysis_result = {
            'user_id': user_id,
            'analyzed_at': latest_analysis.analyzed_at.isoformat(),
            'burnout': {
                'final_score': latest_analysis.final_score,
                'level': latest_analysis.level,
                'components': latest_analysis.components,
                'insights': latest_analysis.insights
            },
            'user_profile': complete_profile.to_llm_context() if complete_profile else None,
            'workload_breakdown': {},  # Would come from latest metrics
            'sentiment_analysis': {}   # Would come from latest analysis
        }

        # Initialize recommendation engine
        recommendation_engine = RecommendationEngine()

        # Get calendar events and tasks if requested
        calendar_events = [] if include_events else None

        # Retrieve user's tasks from database (already formatted as dicts)
        from sentry_app.services.burn_out_service.integrations.task_database_integration import TaskDatabaseService
        task_integration = TaskDatabaseService(session=db)
        task_list = task_integration.get_user_tasks(user_id, include_completed=False)

        # Generate recommendations
        recommendations = recommendation_engine.generate_recommendations(
            burnout_analysis=analysis_result,
            user_profile_context=analysis_result.get('user_profile', ''),
            calendar_events=calendar_events,
            task_list=task_list
        )

        end_time = time.time()
        generation_time = end_time - start_time

        # Save recommendations to database and convert to response format
        recommendation_items = []

        if hasattr(recommendations, 'recommendations'):
            for rec in recommendations.recommendations:
                # Extract recommendation data
                if isinstance(rec, dict):
                    title = rec.get('title', 'Untitled')
                    priority = rec.get('priority', 'MEDIUM')
                    description = rec.get('description', '')
                    action_steps = rec.get('action_steps', [])
                    expected_impact = rec.get('expected_impact', '')
                    category = rec.get('category')
                    burnout_component = rec.get('burnout_component')
                    related_event = rec.get('related_event')
                    related_task = rec.get('related_task')
                else:
                    title = getattr(rec, 'title', 'Untitled')
                    priority = getattr(rec, 'priority', 'MEDIUM')
                    description = getattr(rec, 'description', '')
                    action_steps = getattr(rec, 'action_steps', [])
                    expected_impact = getattr(rec, 'expected_impact', '')
                    category = getattr(rec, 'category', None)
                    burnout_component = getattr(rec, 'burnout_component', None)
                    related_event = getattr(rec, 'related_event', None)
                    related_task = getattr(rec, 'related_task', None)

                # Normalize priority to allowed values (HIGH, MEDIUM, LOW)
                priority_normalized = priority.upper() if priority else 'MEDIUM'
                if priority_normalized == 'CRITICAL':
                    priority_normalized = 'HIGH'
                elif priority_normalized not in ('HIGH', 'MEDIUM', 'LOW'):
                    priority_normalized = 'MEDIUM'

                # Save recommendation to database
                db_recommendation = Recommendation(
                    user_id=user_id,
                    burnout_analysis_id=latest_analysis.id,
                    title=title,
                    priority=priority_normalized,
                    description=description,
                    action_steps=action_steps,
                    expected_impact=expected_impact,
                    generated_at=datetime.utcnow(),
                    generated_by='RAG+LLM',
                    llm_model='llama3.1:8b',
                    strategies_retrieved=getattr(recommendations, 'strategies_count', 0),
                    generation_time_seconds=generation_time,
                    category=category,
                    burnout_component=burnout_component
                )

                db.add(db_recommendation)
                db.flush()  # Get the ID without committing

                # Add to response items
                recommendation_items.append(RecommendationItem(
                    recommendation_id=db_recommendation.id,
                    title=title,
                    priority=priority_normalized,
                    description=description,
                    action_steps=action_steps,
                    expected_impact=expected_impact,
                    related_event=related_event,
                    related_task=related_task
                ))

        # Commit all recommendations
        db.commit()

        # Build metadata
        metadata = RecommendationMetadata(
            strategies_retrieved=getattr(recommendations, 'strategies_count', 0),
            llm_model="llama3.1:8b",
            generation_time_seconds=round(generation_time, 2)
        )

        return RecommendationResponse(
            user_id=user_id,
            generated_at=datetime.utcnow().isoformat(),
            burnout_level=latest_analysis.level,
            recommendations=recommendation_items,
            reasoning=getattr(recommendations, 'reasoning', None),
            metadata=metadata
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")


@router.get("/history")
async def get_recommendation_history(
    current_user: User = Depends(get_current_user),
    include_unapplied: bool = Query(True, description="Include unapplied recommendations"),
    db: Session = Depends(get_db)
):
    """
    Get recommendation history for the authenticated user.

    **Authentication Required**: Pass JWT token in Authorization header.

    Returns all recommendations generated for the user, along with
    their application status and effectiveness data.

    Parameters:
        - include_unapplied: Whether to include recommendations that haven't been applied

    Returns:
        List of recommendations with application details
    """
    try:
        user_id = current_user.id
        query = db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        )

        if not include_unapplied:
            query = query.join(RecommendationApplication)

        recommendations = query.order_by(Recommendation.generated_at.desc()).all()

        result = []
        for rec in recommendations:
            # Get application data if exists
            application = db.query(RecommendationApplication).filter(
                RecommendationApplication.recommendation_id == rec.id
            ).first()

            rec_data = {
                "id": rec.id,
                "title": rec.title,
                "priority": rec.priority,
                "description": rec.description,
                "action_steps": rec.action_steps,
                "expected_impact": rec.expected_impact,
                "generated_at": rec.generated_at.isoformat(),
                "category": rec.category,
                "applied": application is not None,
                "application_data": None
            }

            if application:
                rec_data["application_data"] = {
                    "applied_at": application.applied_at.isoformat(),
                    "tasks_created": application.tasks_created,
                    "status": application.status,
                    "effectiveness_rating": application.effectiveness_rating,
                    "burnout_score_before": application.burnout_score_before,
                    "burnout_score_after": application.burnout_score_after,
                    "completion_rate": application.completion_rate
                }

            result.append(rec_data)

        return {
            "user_id": user_id,
            "total_recommendations": len(result),
            "recommendations": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation history: {str(e)}")


@router.get("/pending")
async def get_pending_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all unapplied recommendations for the authenticated user.

    **Authentication Required**: Pass JWT token in Authorization header.

    Returns recommendations that have been generated but not yet applied.

    Returns:
        List of unapplied recommendations
    """
    try:
        user_id = current_user.id
        # Query recommendations with no application record
        pending_recommendations = db.query(Recommendation).filter(
            Recommendation.user_id == user_id
        ).outerjoin(
            RecommendationApplication,
            RecommendationApplication.recommendation_id == Recommendation.id
        ).filter(
            RecommendationApplication.id == None
        ).order_by(Recommendation.generated_at.desc()).all()

        result = [
            {
                "id": rec.id,
                "title": rec.title,
                "priority": rec.priority,
                "description": rec.description,
                "action_steps": rec.action_steps,
                "expected_impact": rec.expected_impact,
                "generated_at": rec.generated_at.isoformat(),
                "category": rec.category
            }
            for rec in pending_recommendations
        ]

        return {
            "user_id": user_id,
            "pending_count": len(result),
            "recommendations": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending recommendations: {str(e)}")


@router.post("/{recommendation_id}/feedback")
async def submit_recommendation_feedback(
    recommendation_id: int,
    request: RecommendationFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback on a recommendation's effectiveness.

    **Authentication Required**: Pass JWT token in Authorization header.

    This helps improve future recommendations by learning which
    suggestions are most helpful for users.

    Parameters:
        - recommendation_id: Unique recommendation identifier
        - request: Feedback data (helpful, completed, impact rating, notes)

    Returns:
        Confirmation of feedback receipt
    """
    try:
        user_id = current_user.id
        # Verify recommendation exists and belongs to user
        recommendation = db.query(Recommendation).filter(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == user_id
        ).first()

        if not recommendation:
            raise HTTPException(
                status_code=404,
                detail=f"Recommendation {recommendation_id} not found for user {user_id}"
            )

        # Create feedback record
        feedback = RecommendationFeedback(
            recommendation_id=recommendation_id,
            user_id=user_id,
            helpful=request.helpful,
            comments=request.notes,
            submitted_at=datetime.utcnow()
        )

        db.add(feedback)

        # Update application record if exists
        application = db.query(RecommendationApplication).filter(
            RecommendationApplication.recommendation_id == recommendation_id
        ).first()

        if application:
            application.effectiveness_rating = request.impact_rating
            application.user_feedback = request.notes
            application.feedback_submitted_at = datetime.utcnow()

            if request.completed:
                application.status = 'completed'
                application.completed_at = datetime.utcnow()

        db.commit()

        return {
            "status": "success",
            "message": "Feedback received and will be used to improve recommendations",
            "recommendation_id": recommendation_id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")
