"""
Workload & Data Submission Endpoints
=====================================

FastAPI router for submitting workload metrics and qualitative data.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from api.dependencies import get_db
from api.schemas.workload_schemas import (
    WorkloadMetricsRequest,
    QualitativeDataRequest,
    AnalyzeRequest,
    WorkloadBreakdownResponse,
    TaskBreakdown,
    TimeBreakdown,
    MeetingPatterns,
    WorkLifeBalance,
    BaselineComparison
)
from api.schemas.burnout_schemas import BurnoutAnalysisResponse

from Analysis_engine_layer import UserMetrics, QualitativeData
from user_profile.integration_services import BurnoutSystemIntegration
from user_profile.user_profile_service import UserProfileService

router = APIRouter(prefix="/api", tags=["Workload & Analysis"])


# ============================================================================
# DATA SUBMISSION ENDPOINTS
# ============================================================================

@router.post("/workload/submit")
async def submit_workload_metrics(
    request: WorkloadMetricsRequest,
    db: Session = Depends(get_db)
):
    """
    Submit daily workload metrics from task management system.

    This endpoint receives workload data and stores it for analysis.
    Typically called by integrations (Jira, Asana, etc.) or scheduled jobs.

    Returns:
        Confirmation of data receipt
    """
    try:
        # Convert request to UserMetrics
        metrics = UserMetrics(
            total_active_tasks=request.total_active_tasks,
            overdue_tasks=request.overdue_tasks,
            tasks_due_this_week=request.tasks_due_this_week,
            completion_rate=request.completion_rate,
            work_hours_today=request.work_hours_today,
            work_hours_this_week=request.work_hours_this_week,
            meetings_today=request.meetings_today,
            total_meeting_hours_today=request.total_meeting_hours_today,
            back_to_back_meetings=request.back_to_back_meetings,
            weekend_work_sessions=request.weekend_work_sessions,
            late_night_sessions=request.late_night_sessions,
            consecutive_work_days=request.consecutive_work_days
        )

        # Here you could store raw metrics in a table for historical reference
        # For now, we'll just acknowledge receipt

        return {
            "status": "success",
            "message": "Workload metrics received",
            "user_id": request.user_id,
            "received_at": datetime.utcnow().isoformat(),
            "metrics_summary": {
                "total_tasks": metrics.total_active_tasks,
                "work_hours_today": metrics.work_hours_today,
                "meetings_today": metrics.meetings_today
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit workload metrics: {str(e)}")


@router.post("/sentiment/submit")
async def submit_qualitative_data(
    request: QualitativeDataRequest,
    db: Session = Depends(get_db)
):
    """
    Submit qualitative data (meeting notes, task notes, check-ins).

    This endpoint receives text data for sentiment analysis.
    Can be called by Slack integrations, meeting transcription services, etc.

    Returns:
        Confirmation of data receipt
    """
    try:
        # Convert request to QualitativeData
        qualitative_data = QualitativeData(
            meeting_transcripts=request.meeting_transcripts,
            task_notes=request.task_notes,
            user_check_ins=request.user_check_ins
        )

        # Here you could store raw qualitative data in a table for reference

        return {
            "status": "success",
            "message": "Qualitative data received",
            "user_id": request.user_id,
            "received_at": datetime.utcnow().isoformat(),
            "data_summary": {
                "meeting_transcripts": len(qualitative_data.meeting_transcripts),
                "task_notes": len(qualitative_data.task_notes),
                "user_check_ins": len(qualitative_data.user_check_ins),
                "total_text_entries": len(qualitative_data.meeting_transcripts) +
                                     len(qualitative_data.task_notes) +
                                     len(qualitative_data.user_check_ins)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit qualitative data: {str(e)}")


@router.post("/burnout/analyze")
async def analyze_burnout(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Trigger a complete burnout analysis.

    This is the main endpoint that runs the full analysis pipeline:
    1. Workload analysis
    2. Sentiment analysis
    3. Burnout score fusion
    4. Profile context integration
    5. Historical data storage

    Returns:
        Complete burnout analysis with all components
    """
    try:
        # Convert request data to internal models
        metrics = UserMetrics(
            total_active_tasks=request.quantitative_metrics.total_active_tasks,
            overdue_tasks=request.quantitative_metrics.overdue_tasks,
            tasks_due_this_week=request.quantitative_metrics.tasks_due_this_week,
            completion_rate=request.quantitative_metrics.completion_rate,
            work_hours_today=request.quantitative_metrics.work_hours_today,
            work_hours_this_week=request.quantitative_metrics.work_hours_this_week,
            meetings_today=request.quantitative_metrics.meetings_today,
            total_meeting_hours_today=request.quantitative_metrics.total_meeting_hours_today,
            back_to_back_meetings=request.quantitative_metrics.back_to_back_meetings,
            weekend_work_sessions=request.quantitative_metrics.weekend_work_sessions,
            late_night_sessions=request.quantitative_metrics.late_night_sessions,
            consecutive_work_days=request.quantitative_metrics.consecutive_work_days
        )

        qualitative_data = QualitativeData(
            meeting_transcripts=request.qualitative_data.meeting_transcripts,
            task_notes=request.qualitative_data.task_notes,
            user_check_ins=request.qualitative_data.user_check_ins
        )

        # Initialize integration service
        integration = BurnoutSystemIntegration(db)

        # Run complete analysis
        analysis_result = integration.analyze_user_burnout(
            user_id=request.user_id,
            quantitative_metrics=metrics,
            qualitative_data=qualitative_data,
            store_history=request.store_history
        )

        # Return the analysis result
        # The structure already matches what we need
        return {
            "status": "success",
            "message": "Burnout analysis completed",
            "analysis": analysis_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze burnout: {str(e)}")


@router.post("/burnout/analyze-auto/{user_id}")
async def analyze_burnout_auto(
    user_id: int,
    store_history: bool = True,
    db: Session = Depends(get_db)
):
    """
    Trigger burnout analysis with AUTO-FETCH from database.

    This endpoint automatically:
    1. Fetches tasks from the database
    2. Calculates workload metrics
    3. Retrieves qualitative data (sentiment notes)
    4. Runs complete burnout analysis
    5. Stores results in history

    No manual input required - all data fetched from database!

    Args:
        user_id: User ID to analyze
        store_history: Whether to store analysis in history (default: True)

    Returns:
        Complete burnout analysis with all components
    """
    try:
        # Import the auto-fetch function
        from integrations.task_database_integration import get_complete_user_context

        # Auto-fetch all data from database
        context = get_complete_user_context(user_id=user_id, session=db)

        # Initialize integration service
        integration = BurnoutSystemIntegration(db)

        # Run complete analysis with auto-fetched data
        analysis_result = integration.analyze_user_burnout(
            user_id=user_id,
            quantitative_metrics=context['metrics'],        # Auto-calculated
            qualitative_data=context['qualitative_data'],   # Auto-fetched
            store_history=store_history
        )

        # Return the analysis result with metadata
        return {
            "status": "success",
            "message": "Burnout analysis completed (auto-fetch mode)",
            "data_source": "database",
            "tasks_analyzed": len(context['tasks']),
            "meetings_analyzed": len(context['meetings']),
            "analysis": analysis_result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to auto-analyze burnout: {str(e)}")


@router.get("/workload/breakdown/{user_id}", response_model=WorkloadBreakdownResponse)
async def get_workload_breakdown(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed workload breakdown for UI charts.

    Returns:
        - Task load breakdown
        - Time breakdown
        - Meeting patterns
        - Work-life balance metrics
        - Comparison to baseline (if available)
    """
    try:
        # Get latest analysis to extract metrics
        from user_profile.burnout_model import BurnoutAnalysis

        latest_analysis = db.query(BurnoutAnalysis).filter(
            BurnoutAnalysis.user_id == user_id
        ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()

        if not latest_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"No analysis found for user {user_id}"
            )

        metrics = latest_analysis.metrics

        # Build task breakdown
        task_breakdown = TaskBreakdown(
            active_tasks=metrics.get('total_active_tasks', 0),
            overdue_tasks=metrics.get('overdue_tasks', 0),
            tasks_due_this_week=metrics.get('tasks_due_this_week', 0),
            completion_rate=metrics.get('completion_rate', 0.0)
        )

        # Build time breakdown
        work_hours = metrics.get('work_hours_today', 0)
        meeting_hours = metrics.get('total_meeting_hours_today', 0)
        focus_time = max(0, work_hours - meeting_hours)

        time_breakdown = TimeBreakdown(
            work_hours_today=work_hours,
            work_hours_this_week=metrics.get('work_hours_this_week', 0),
            meeting_hours_today=meeting_hours,
            estimated_focus_time=focus_time
        )

        # Build meeting patterns
        meeting_patterns = MeetingPatterns(
            total_meetings=metrics.get('meetings_today', 0),
            back_to_back_meetings=metrics.get('back_to_back_meetings', 0),
            optional_meetings=None,  # Would need calendar integration data
            required_meetings=None,
            average_meeting_duration=None
        )

        # Build work-life balance metrics
        weekend_sessions = metrics.get('weekend_work_sessions', 0)
        late_night = metrics.get('late_night_sessions', 0)
        consecutive_days = metrics.get('consecutive_work_days', 0)

        # Calculate balance score (0-100, higher is better)
        balance_score = 100
        if weekend_sessions > 0:
            balance_score -= (weekend_sessions * 10)
        if late_night > 0:
            balance_score -= (late_night * 15)
        if consecutive_days > 5:
            balance_score -= ((consecutive_days - 5) * 5)
        balance_score = max(0, balance_score)

        work_life_balance = WorkLifeBalance(
            weekend_work_sessions=weekend_sessions,
            late_night_sessions=late_night,
            consecutive_work_days=consecutive_days,
            work_life_balance_score=balance_score
        )

        # Get baseline comparison if user has behavioral profile
        baseline_comparison = None
        profile_service = UserProfileService(db)
        user_profile = profile_service.get_user_profile(user_id)

        if user_profile and user_profile.behavioral_profile:
            behavioral = user_profile.behavioral_profile

            baseline_tasks = behavioral.baseline_task_count or behavioral.avg_tasks_per_day
            baseline_hours = behavioral.baseline_work_hours or behavioral.avg_work_hours_per_day
            baseline_meetings = behavioral.baseline_meeting_count or behavioral.avg_meetings_per_day

            current_vs_baseline_tasks = None
            if baseline_tasks:
                current_vs_baseline_tasks = ((metrics.get('total_active_tasks', 0) - baseline_tasks) / baseline_tasks * 100)

            current_vs_baseline_hours = None
            if baseline_hours:
                current_vs_baseline_hours = ((work_hours - baseline_hours) / baseline_hours * 100)

            current_vs_baseline_meetings = None
            if baseline_meetings:
                current_vs_baseline_meetings = ((metrics.get('meetings_today', 0) - baseline_meetings) / baseline_meetings * 100)

            baseline_comparison = BaselineComparison(
                current_vs_baseline_tasks=current_vs_baseline_tasks,
                current_vs_baseline_hours=current_vs_baseline_hours,
                current_vs_baseline_meetings=current_vs_baseline_meetings
            )

        return WorkloadBreakdownResponse(
            user_id=user_id,
            analyzed_at=latest_analysis.analyzed_at.isoformat(),
            task_breakdown=task_breakdown,
            time_breakdown=time_breakdown,
            meeting_patterns=meeting_patterns,
            work_life_balance=work_life_balance,
            baseline_comparison=baseline_comparison
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workload breakdown: {str(e)}")
