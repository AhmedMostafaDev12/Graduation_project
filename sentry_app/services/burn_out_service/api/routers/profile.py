"""
User Profile Endpoints
======================

FastAPI router for managing user profiles, preferences, and constraints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import sys
from pathlib import Path

# Add backend_services to path for authentication
backend_path = Path(__file__).parent.parent.parent.parent.parent.parent / "backend_services"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from sentry_app.oauth2 import get_current_user
from sentry_app.models import User

from sentry_app.services.burn_out_service.api.dependencies import get_db
from sentry_app.services.burn_out_service.api.schemas.profile_schemas import (
    UserProfileResponse,
    UpdateProfileRequest,
    LearnPatternsResponse,
    BehavioralProfileResponse,
    PreferencesResponse,
    ConstraintsResponse
)

from sentry_app.services.burn_out_service.user_profile.user_profile_service import UserProfileService
from sentry_app.services.burn_out_service.user_profile.integration_services import BurnoutSystemIntegration

router = APIRouter(prefix="/api/profile", tags=["User Profile"])


# ============================================================================
# PROFILE ENDPOINTS
# ============================================================================
# NOTE: Profile creation happens automatically during signup in backend_services/app/routers/user.py
# This API only provides GET (retrieve) and PUT (update for onboarding) endpoints

@router.get("", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete user profile including preferences and constraints.

    **Authentication Required**: Pass JWT token in Authorization header.

    Returns:
        - User information (name, email, role, department, timezone)
        - Work preferences
        - Constraints (caregiving, health, timezone)
        - Behavioral profile (learned patterns if available)
    """
    try:
        user_id = current_user.id
        profile_service = UserProfileService(db)
        user_profile = profile_service.get_user_profile(user_id)

        if not user_profile:
            raise HTTPException(
                status_code=404,
                detail=f"User profile not found for user {user_id}"
            )

        # Build preferences response
        preferences = None
        if user_profile.preferences:
            pref = user_profile.preferences
            preferences = PreferencesResponse(
                preferred_work_hours_start=pref.preferred_work_hours_start.strftime("%H:%M") if pref.preferred_work_hours_start else None,
                preferred_work_hours_end=pref.preferred_work_hours_end.strftime("%H:%M") if pref.preferred_work_hours_end else None,
                max_daily_meetings=pref.max_daily_meetings,
                focus_time_blocks_needed=pref.focus_time_blocks_needed,
                communication_style=pref.communication_style,
                work_style=pref.work_style
            )

        # Build constraints response
        constraints = None
        if user_profile.constraints:
            const = user_profile.constraints
            constraints = ConstraintsResponse(
                has_caregiving_responsibilities=const.has_caregiving_responsibilities,
                has_health_conditions=const.has_health_conditions,
                has_timezone_constraints=const.has_timezone_constraints,
                description=const.description
            )

        # Build behavioral profile response
        behavioral_profile = None
        if user_profile.behavioral_profile:
            behav = user_profile.behavioral_profile
            behavioral_profile = BehavioralProfileResponse(
                avg_tasks_per_day=behav.avg_tasks_per_day,
                avg_work_hours_per_day=behav.avg_work_hours_per_day,
                avg_meetings_per_day=behav.avg_meetings_per_day,
                avg_meeting_hours_per_day=behav.avg_meeting_hours_per_day,
                avg_completion_rate=behav.avg_completion_rate,
                baseline_burnout_score=behav.baseline_burnout_score,
                baseline_task_count=behav.baseline_task_count,
                baseline_work_hours=behav.baseline_work_hours,
                baseline_meeting_count=behav.baseline_meeting_count,
                peak_productivity_hour=behav.peak_productivity_hour,
                most_productive_day=behav.most_productive_day,
                least_productive_day=behav.least_productive_day,
                stress_triggers=behav.stress_triggers or [],
                last_pattern_analysis=behav.last_pattern_analysis.isoformat() if behav.last_pattern_analysis else None
            )

        return UserProfileResponse(
            user_id=user_profile.user_id,
            full_name=user_profile.full_name,
            email=user_profile.email,
            job_role=user_profile.job_role,
            seniority_level=user_profile.seniority_level,
            department=user_profile.department,
            timezone=user_profile.timezone,
            preferences=preferences,
            constraints=constraints,
            behavioral_profile=behavioral_profile,
            created_at=user_profile.created_at.isoformat(),
            updated_at=user_profile.updated_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")


@router.put("")
async def update_user_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile, preferences, or constraints.

    **Authentication Required**: Pass JWT token in Authorization header.

    Allows partial updates - only provided fields will be updated.

    Returns:
        Updated profile confirmation
    """
    try:
        user_id = current_user.id
        profile_service = UserProfileService(db)
        user_profile = profile_service.get_user_profile(user_id)

        if not user_profile:
            raise HTTPException(
                status_code=404,
                detail=f"User profile not found for user {user_id}"
            )

        # Update basic profile fields
        if request.full_name:
            user_profile.full_name = request.full_name
        if request.email:
            user_profile.email = request.email
        if request.job_role:
            user_profile.job_role = request.job_role
        if request.seniority_level:
            user_profile.seniority_level = request.seniority_level
        if request.department:
            user_profile.department = request.department
        if request.timezone:
            user_profile.timezone = request.timezone

        # Update preferences
        if request.preferences and user_profile.preferences:
            pref_update = request.preferences
            if pref_update.preferred_work_hours_start:
                from datetime import time as dt_time
                hour, minute = map(int, pref_update.preferred_work_hours_start.split(':'))
                user_profile.preferences.preferred_work_hours_start = dt_time(hour, minute)

            if pref_update.preferred_work_hours_end:
                from datetime import time as dt_time
                hour, minute = map(int, pref_update.preferred_work_hours_end.split(':'))
                user_profile.preferences.preferred_work_hours_end = dt_time(hour, minute)

            if pref_update.max_daily_meetings is not None:
                user_profile.preferences.max_daily_meetings = pref_update.max_daily_meetings

            if pref_update.focus_time_blocks_needed is not None:
                user_profile.preferences.focus_time_blocks_needed = pref_update.focus_time_blocks_needed

            if pref_update.communication_style:
                user_profile.preferences.communication_style = pref_update.communication_style

            if pref_update.work_style:
                user_profile.preferences.work_style = pref_update.work_style

        # Update constraints
        if request.constraints and user_profile.constraints:
            const_update = request.constraints
            if const_update.has_caregiving_responsibilities is not None:
                user_profile.constraints.has_caregiving_responsibilities = const_update.has_caregiving_responsibilities

            if const_update.has_health_conditions is not None:
                user_profile.constraints.has_health_conditions = const_update.has_health_conditions

            if const_update.has_timezone_constraints is not None:
                user_profile.constraints.has_timezone_constraints = const_update.has_timezone_constraints

            if const_update.description:
                user_profile.constraints.description = const_update.description

        user_profile.updated_at = datetime.utcnow()
        db.commit()

        return {
            "status": "success",
            "message": "User profile updated successfully",
            "user_id": user_id,
            "updated_at": user_profile.updated_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


@router.post("/learn-patterns", response_model=LearnPatternsResponse)
async def learn_behavioral_patterns(
    current_user: User = Depends(get_current_user),
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Trigger behavioral pattern learning for the authenticated user.

    **Authentication Required**: Pass JWT token in Authorization header.

    Analyzes historical burnout data to identify:
    - Average workload patterns
    - Baseline metrics
    - Peak productivity times
    - Stress triggers

    Parameters:
        - days: Number of days to analyze (default: 30)

    Returns:
        - Learned behavioral patterns
        - Number of days analyzed
        - Last updated timestamp
    """
    try:
        user_id = current_user.id
        # Check if user has enough historical data
        from sentry_app.services.burn_out_service.user_profile.burnout_model import BurnoutAnalysis

        analysis_count = db.query(BurnoutAnalysis).filter(
            BurnoutAnalysis.user_id == user_id
        ).count()

        if analysis_count < 7:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient historical data. Need at least 7 analyses, found {analysis_count}"
            )

        # Run pattern learning
        integration = BurnoutSystemIntegration(db)
        patterns = integration.update_user_behavioral_profile(user_id, days=days)

        if not patterns:
            raise HTTPException(
                status_code=404,
                detail=f"User profile not found for user {user_id}"
            )

        return LearnPatternsResponse(
            user_id=user_id,
            patterns_learned=patterns,
            days_analyzed=days,
            last_updated=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to learn patterns: {str(e)}")
