"""
Workload & Data Submission Endpoints
=====================================

FastAPI router for submitting workload metrics and qualitative data.
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
from sentry_app.services.burn_out_service.api.schemas.workload_schemas import (
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
from sentry_app.services.burn_out_service.api.schemas.burnout_schemas import BurnoutAnalysisResponse

try:
    from sentry_app.services.burn_out_service.Analysis_engine_layer import UserMetrics, QualitativeData
except ImportError:
    # Fallback for when imported from unified system
    import sys
    from pathlib import Path
    burnout_service_path = Path(__file__).parent.parent.parent.parent
    if str(burnout_service_path) not in sys.path:
        sys.path.insert(0, str(burnout_service_path))
    from sentry_app.services.burn_out_service.Analysis_engine_layer import UserMetrics, QualitativeData

from sentry_app.services.burn_out_service.user_profile.integration_services import BurnoutSystemIntegration
from sentry_app.services.burn_out_service.user_profile.user_profile_service import UserProfileService

# Pre-import the task database integration to avoid runtime import errors
try:
    from sentry_app.services.burn_out_service.integrations.task_database_integration import get_complete_user_context
except ImportError as e:
    print(f"[WORKLOAD ROUTER] Failed to import get_complete_user_context: {e}")
    # Will try again inside the endpoint function
    get_complete_user_context = None

router = APIRouter(prefix="/api", tags=["Workload & Analysis"])


# ============================================================================
# DATA SUBMISSION ENDPOINTS
# ============================================================================

@router.post("/sentiment/submit")
async def submit_qualitative_data(
    request: QualitativeDataRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit qualitative data (meeting notes, task notes, check-ins).

    **Authentication Required**: Pass JWT token in Authorization header.

    This endpoint:
    1. Analyzes each text entry through the sentiment analyzer to get a score (-1 to +1)
    2. Saves each entry to the database with the sentiment_score and task_id

    Can be called by Slack integrations, meeting transcription services, etc.

    Returns:
        Confirmation of data receipt with sentiment scores
    """
    try:
        user_id = current_user.id
        # Import required modules
        from sentry_app.services.burn_out_service.integrations.task_database_integration import QualitativeDataEntry
        from sentry_app.services.burn_out_service.Analysis_engine_layer.sentiment_analyzer import SentimentAnalyzer, QualitativeData as SentimentQualData

        # Initialize sentiment analyzer
        print(f"[SENTIMENT SUBMIT] Initializing sentiment analyzer for user {user_id}")
        analyzer = SentimentAnalyzer()

        saved_entries = []
        sentiment_scores = []

        # Process meeting transcripts
        for transcript in request.meeting_transcripts:
            # Analyze sentiment
            qual_data = SentimentQualData(meeting_transcripts=[transcript])
            try:
                sentiment_result = analyzer.analyze(qual_data)
                score = sentiment_result.sentiment_score
            except Exception as e:
                print(f"[SENTIMENT SUBMIT] Warning: Sentiment analysis failed for meeting transcript: {e}")
                score = 0.0  # Neutral score if analysis fails

            # Save to database
            entry = QualitativeDataEntry(
                user_id=user_id,
                entry_type='meeting_transcript',
                content=transcript,
                sentiment_score=score,
                task_id=None
            )
            db.add(entry)
            saved_entries.append('meeting_transcript')
            sentiment_scores.append(score)
            print(f"[SENTIMENT SUBMIT] Meeting transcript analyzed: score={score:.2f}")

        # Process task notes
        for note in request.task_notes:
            # Analyze sentiment
            qual_data = SentimentQualData(task_notes=[note])
            try:
                sentiment_result = analyzer.analyze(qual_data)
                score = sentiment_result.sentiment_score
            except Exception as e:
                print(f"[SENTIMENT SUBMIT] Warning: Sentiment analysis failed for task note: {e}")
                score = 0.0

            # Save to database
            entry = QualitativeDataEntry(
                user_id=user_id,
                entry_type='task_note',
                content=note,
                sentiment_score=score,
                task_id=None  # TODO: Extract task_id from request if needed
            )
            db.add(entry)
            saved_entries.append('task_note')
            sentiment_scores.append(score)
            print(f"[SENTIMENT SUBMIT] Task note analyzed: score={score:.2f}")

        # Process user check-ins
        for check_in in request.user_check_ins:
            # Analyze sentiment
            qual_data = SentimentQualData(user_check_ins=[check_in])
            try:
                sentiment_result = analyzer.analyze(qual_data)
                score = sentiment_result.sentiment_score
            except Exception as e:
                print(f"[SENTIMENT SUBMIT] Warning: Sentiment analysis failed for check-in: {e}")
                score = 0.0

            # Save to database
            entry = QualitativeDataEntry(
                user_id=user_id,
                entry_type='user_check_in',
                content=check_in,
                sentiment_score=score,
                task_id=None
            )
            db.add(entry)
            saved_entries.append('user_check_in')
            sentiment_scores.append(score)
            print(f"[SENTIMENT SUBMIT] User check-in analyzed: score={score:.2f}")

        # Commit all entries to database
        db.commit()

        # Calculate average sentiment
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0

        print(f"[SENTIMENT SUBMIT] Saved {len(saved_entries)} qualitative entries for user {user_id} (avg sentiment: {avg_sentiment:.2f})")

        return {
            "status": "success",
            "message": f"Analyzed and saved {len(saved_entries)} qualitative data entries to database",
            "user_id": user_id,
            "received_at": datetime.utcnow().isoformat(),
            "data_summary": {
                "meeting_transcripts": len(request.meeting_transcripts),
                "task_notes": len(request.task_notes),
                "user_check_ins": len(request.user_check_ins),
                "total_entries_saved": len(saved_entries),
                "average_sentiment_score": round(avg_sentiment, 2)
            }
        }

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"\n[SENTIMENT SUBMIT ERROR] Full traceback:\n{error_traceback}")
        raise HTTPException(status_code=500, detail=f"Failed to submit qualitative data: {str(e)}")


@router.post("/burnout/analyze-auto")
async def analyze_burnout_auto(
    current_user: User = Depends(get_current_user),
    store_history: bool = True,
    db: Session = Depends(get_db)
):
    """
    Trigger burnout analysis with AUTO-FETCH from database.

    **Authentication Required**: Pass JWT token in Authorization header.

    This endpoint automatically:
    1. Fetches tasks from the database
    2. Calculates workload metrics
    3. Retrieves qualitative data (sentiment notes)
    4. Runs complete burnout analysis
    5. Stores results in history

    No manual input required - all data fetched from database!

    Args:
        store_history: Whether to store analysis in history (default: True)

    Returns:
        Complete burnout analysis with all components
    """
    try:
        user_id = current_user.id
        # Import the auto-fetch function (use pre-imported if available)
        if get_complete_user_context is None:
            from sentry_app.services.burn_out_service.integrations.task_database_integration import get_complete_user_context as _get_context
            context_func = _get_context
        else:
            context_func = get_complete_user_context

        # Auto-fetch all data from database
        context = context_func(user_id=user_id, session=db)

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
        import traceback
        error_traceback = traceback.format_exc()
        print(f"\n[BURNOUT AUTO-ANALYZE ERROR] Full traceback:\n{error_traceback}")
        raise HTTPException(status_code=500, detail=f"Failed to auto-analyze burnout: {str(e)}")


@router.get("/workload/breakdown", response_model=WorkloadBreakdownResponse)
async def get_workload_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed workload breakdown for UI charts.

    **Authentication Required**: Pass JWT token in Authorization header.

    Returns:
        - Task load breakdown
        - Time breakdown
        - Meeting patterns
        - Work-life balance metrics
        - Comparison to baseline (if available)
    """
    try:
        user_id = current_user.id
        # Get latest analysis to extract metrics
        from sentry_app.services.burn_out_service.user_profile.burnout_model import BurnoutAnalysis

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
