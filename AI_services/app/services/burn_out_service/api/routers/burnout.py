"""
Burnout Analysis Endpoints
===========================

FastAPI router for burnout analysis and insights.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from api.dependencies import get_db
from api.schemas.burnout_schemas import (
    BurnoutAnalysisResponse,
    BurnoutTrendResponse,
    BurnoutBreakdownResponse,
    BurnoutInsightsResponse,
    BurnoutSignalsResponse,
    RecoveryPlanResponse,
    TrendDataPoint,
    AlertTrigger,
    RecoveryAction,
    BurnoutComponentsResponse,
    BurnoutTrendInfo,
    StressIndicator
)

from user_profile.integration_services import BurnoutSystemIntegration
from user_profile.burnout_model import BurnoutAnalysis

router = APIRouter(prefix="/api/burnout", tags=["Burnout Analysis"])


# ============================================================================
# BURNOUT ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/analysis/{user_id}", response_model=BurnoutAnalysisResponse)
async def get_burnout_analysis(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get the latest burnout analysis for a user.

    Returns:
        - Current burnout score (0-100)
        - Burnout level (LOW, MODERATE, HIGH, SEVERE, CRITICAL)
        - Component breakdown
        - Insights and trends
        - Alert triggers
    """
    try:
        # Get latest analysis from database
        latest_analysis = db.query(BurnoutAnalysis).filter(
            BurnoutAnalysis.user_id == user_id
        ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()

        if not latest_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"No burnout analysis found for user {user_id}"
            )

        # Convert to response model
        components = BurnoutComponentsResponse(**latest_analysis.components)

        trend_info = None
        if latest_analysis.insights.get('trend'):
            trend_data = latest_analysis.insights['trend']
            trend_info = BurnoutTrendInfo(
                direction=trend_data.get('direction', 'stable'),
                change_percentage=trend_data.get('change_percentage', 0.0),
                change_points=trend_data.get('change_points', 0.0),
                days_at_current_level=trend_data.get('days_at_current_level', 0)
            )

        # Get alert triggers
        alert_triggers = []
        if 'alert_triggers' in latest_analysis.insights:
            for alert in latest_analysis.insights['alert_triggers']:
                alert_triggers.append(AlertTrigger(**alert))

        return BurnoutAnalysisResponse(
            user_id=user_id,
            analyzed_at=latest_analysis.analyzed_at.isoformat(),
            final_score=latest_analysis.final_score,
            level=latest_analysis.level,
            status_message=latest_analysis.insights.get('status_message', ''),
            components=components,
            insights=latest_analysis.insights,
            trend=trend_info,
            alert_triggers=alert_triggers
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get burnout analysis: {str(e)}")


@router.get("/trend/{user_id}", response_model=BurnoutTrendResponse)
async def get_burnout_trend(
    user_id: int,
    period: str = Query("30days", regex="^(7days|30days|90days)$"),
    db: Session = Depends(get_db)
):
    """
    Get burnout score trend over time.

    Parameters:
        - period: Time period (7days, 30days, 90days)

    Returns:
        - Historical data points
        - Trend direction (rising/stable/lowering)
        - Percentage change
        - Moving average
    """
    try:
        # Calculate date range
        period_days = {"7days": 7, "30days": 30, "90days": 90}[period]
        start_date = datetime.utcnow() - timedelta(days=period_days)

        # Get historical analyses
        analyses = db.query(BurnoutAnalysis).filter(
            BurnoutAnalysis.user_id == user_id,
            BurnoutAnalysis.analyzed_at >= start_date
        ).order_by(BurnoutAnalysis.analyzed_at.asc()).all()

        if not analyses:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for user {user_id}"
            )

        # Build data points
        data_points = [
            TrendDataPoint(
                date=a.analyzed_at.strftime("%Y-%m-%d"),
                score=a.final_score,
                level=a.level
            )
            for a in analyses
        ]

        # Calculate trend
        current_score = analyses[-1].final_score
        previous_score = analyses[0].final_score
        percentage_change = ((current_score - previous_score) / previous_score * 100) if previous_score > 0 else 0

        if percentage_change > 5:
            trend_direction = "rising"
        elif percentage_change < -5:
            trend_direction = "lowering"
        else:
            trend_direction = "stable"

        # Calculate 7-day moving average
        scores = [a.final_score for a in analyses]
        moving_avg = []
        window = min(7, len(scores))
        for i in range(len(scores)):
            start_idx = max(0, i - window + 1)
            avg = sum(scores[start_idx:i+1]) / (i - start_idx + 1)
            moving_avg.append(round(avg, 2))

        return BurnoutTrendResponse(
            user_id=user_id,
            period=period,
            data_points=data_points,
            trend_direction=trend_direction,
            percentage_change=round(percentage_change, 2),
            current_score=current_score,
            previous_score=previous_score,
            moving_average=moving_avg
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trend data: {str(e)}")


@router.get("/breakdown/{user_id}", response_model=BurnoutBreakdownResponse)
async def get_burnout_breakdown(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed component breakdown of burnout score.

    Returns:
        - Workload score
        - Sentiment adjustment
        - Temporal adjustment
        - Contribution percentages
    """
    try:
        latest_analysis = db.query(BurnoutAnalysis).filter(
            BurnoutAnalysis.user_id == user_id
        ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()

        if not latest_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"No burnout analysis found for user {user_id}"
            )

        components = latest_analysis.components

        return BurnoutBreakdownResponse(
            user_id=user_id,
            analyzed_at=latest_analysis.analyzed_at.isoformat(),
            workload_score=components.get('workload_score', 0),
            sentiment_score=components.get('sentiment_adjustment', 0),
            temporal_adjustment=components.get('temporal_adjustment'),
            workload_contribution_percent=components.get('workload_contribution', 0),
            sentiment_contribution_percent=components.get('sentiment_contribution', 0),
            final_score=latest_analysis.final_score
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get breakdown: {str(e)}")


@router.get("/insights/{user_id}", response_model=BurnoutInsightsResponse)
async def get_burnout_insights(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get primary issues and insights about burnout.

    Returns:
        - Primary contributors
        - Key insights
        - Risk factors
        - Alert triggers
    """
    try:
        latest_analysis = db.query(BurnoutAnalysis).filter(
            BurnoutAnalysis.user_id == user_id
        ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()

        if not latest_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"No burnout analysis found for user {user_id}"
            )

        insights_data = latest_analysis.insights

        # Extract primary contributors
        primary_contributors = insights_data.get('primary_contributors', [])

        # Extract key insights
        key_insights = insights_data.get('key_insights', [])

        # Extract risk factors
        risk_factors = insights_data.get('risk_factors', [])

        # Extract alert triggers
        alert_triggers = []
        if 'alert_triggers' in insights_data:
            for alert in insights_data['alert_triggers']:
                alert_triggers.append(AlertTrigger(**alert))

        return BurnoutInsightsResponse(
            user_id=user_id,
            analyzed_at=latest_analysis.analyzed_at.isoformat(),
            primary_contributors=primary_contributors,
            key_insights=key_insights,
            risk_factors=risk_factors,
            alert_triggers=alert_triggers
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")


@router.get("/signals/{user_id}", response_model=BurnoutSignalsResponse)
async def get_burnout_signals(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get burnout warning signals and patterns.

    Returns:
        - Stress indicators from sentiment analysis
        - Detected burnout signals
        - Work pattern anomalies
        - Historical patterns
    """
    try:
        latest_analysis = db.query(BurnoutAnalysis).filter(
            BurnoutAnalysis.user_id == user_id
        ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()

        if not latest_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"No burnout analysis found for user {user_id}"
            )

        insights_data = latest_analysis.insights

        # Extract stress indicators
        stress_indicators = []
        if 'stress_indicators' in insights_data:
            for indicator in insights_data['stress_indicators']:
                if isinstance(indicator, dict):
                    stress_indicators.append(StressIndicator(**indicator))
                else:
                    stress_indicators.append(StressIndicator(indicator=str(indicator), severity="medium"))

        # Extract burnout signals
        burnout_signals = insights_data.get('burnout_signals', {})

        # Identify work pattern anomalies
        work_pattern_anomalies = []
        metrics = latest_analysis.metrics

        if metrics.get('work_hours_today', 0) > 10:
            work_pattern_anomalies.append(f"Extended work hours: {metrics['work_hours_today']:.1f} hours today")

        if metrics.get('back_to_back_meetings', 0) >= 3:
            work_pattern_anomalies.append(f"Excessive back-to-back meetings: {metrics['back_to_back_meetings']}")

        if metrics.get('weekend_work_sessions', 0) > 0:
            work_pattern_anomalies.append(f"Weekend work detected: {metrics['weekend_work_sessions']} sessions")

        if metrics.get('late_night_sessions', 0) > 0:
            work_pattern_anomalies.append(f"Late night work: {metrics['late_night_sessions']} sessions")

        # Get historical patterns (if available)
        historical_patterns = insights_data.get('historical_patterns', [])

        return BurnoutSignalsResponse(
            user_id=user_id,
            analyzed_at=latest_analysis.analyzed_at.isoformat(),
            stress_indicators=stress_indicators,
            burnout_signals=burnout_signals,
            work_pattern_anomalies=work_pattern_anomalies,
            historical_patterns=historical_patterns if historical_patterns else None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get signals: {str(e)}")


@router.get("/recovery-plan/{user_id}", response_model=RecoveryPlanResponse)
async def get_recovery_plan(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get structured recovery plan based on burnout level.

    Returns:
        - Immediate actions (24-48 hours)
        - Short-term goals (1-2 weeks)
        - Long-term strategies (1 month)
        - Progress tracking metrics
    """
    try:
        latest_analysis = db.query(BurnoutAnalysis).filter(
            BurnoutAnalysis.user_id == user_id
        ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()

        if not latest_analysis:
            raise HTTPException(
                status_code=404,
                detail=f"No burnout analysis found for user {user_id}"
            )

        # Generate recovery plan based on burnout level
        burnout_level = latest_analysis.level

        # This is a placeholder - in production, this would come from the recommendation engine
        # or be stored with the analysis
        immediate_actions = [
            RecoveryAction(
                title="Take a Break",
                priority="HIGH",
                description="Step away from work for at least 30 minutes",
                action_steps=["Close all work applications", "Go for a short walk", "Do breathing exercises"],
                timeline="immediate",
                expected_impact="Reduce immediate stress levels"
            )
        ]

        short_term_goals = [
            RecoveryAction(
                title="Review Workload",
                priority="MEDIUM",
                description="Assess current task load and prioritize",
                action_steps=["List all active tasks", "Identify tasks that can be delegated", "Discuss priorities with manager"],
                timeline="short-term",
                expected_impact="Better workload management"
            )
        ]

        long_term_strategies = [
            RecoveryAction(
                title="Establish Boundaries",
                priority="MEDIUM",
                description="Set clear work-life boundaries",
                action_steps=["Define working hours", "Turn off notifications after hours", "Schedule regular breaks"],
                timeline="long-term",
                expected_impact="Sustainable work habits"
            )
        ]

        progress_metrics = [
            "Daily burnout score",
            "Work hours per day",
            "Number of breaks taken",
            "Sleep quality",
            "Meeting load"
        ]

        return RecoveryPlanResponse(
            user_id=user_id,
            generated_at=datetime.utcnow().isoformat(),
            burnout_level=burnout_level,
            immediate_actions=immediate_actions,
            short_term_goals=short_term_goals,
            long_term_strategies=long_term_strategies,
            progress_metrics=progress_metrics
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recovery plan: {str(e)}")


@router.get("/history/{user_id}")
async def get_burnout_history(
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get historical burnout analysis records.

    Parameters:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - limit: Maximum number of records
        - offset: Pagination offset

    Returns:
        List of historical analyses
    """
    try:
        query = db.query(BurnoutAnalysis).filter(BurnoutAnalysis.user_id == user_id)

        if start_date:
            query = query.filter(BurnoutAnalysis.analyzed_at >= datetime.fromisoformat(start_date))

        if end_date:
            query = query.filter(BurnoutAnalysis.analyzed_at <= datetime.fromisoformat(end_date))

        total_count = query.count()

        analyses = query.order_by(
            BurnoutAnalysis.analyzed_at.desc()
        ).limit(limit).offset(offset).all()

        return {
            "user_id": user_id,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "analyses": [
                {
                    "analyzed_at": a.analyzed_at.isoformat(),
                    "final_score": a.final_score,
                    "level": a.level,
                    "components": a.components,
                    "metrics": a.metrics,
                    "insights": a.insights
                }
                for a in analyses
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")
