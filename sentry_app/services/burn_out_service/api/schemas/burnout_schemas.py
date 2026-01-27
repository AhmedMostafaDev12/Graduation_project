"""
Burnout Analysis API Schemas
=============================

Pydantic models for burnout analysis endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class BurnoutComponentsResponse(BaseModel):
    """Burnout score component breakdown."""
    workload_score: float = Field(..., description="Workload component score")
    sentiment_adjustment: float = Field(..., description="Sentiment adjustment")
    temporal_adjustment: Optional[float] = Field(None, description="Temporal adjustment if applicable")
    workload_contribution: float = Field(..., description="Workload contribution percentage")
    sentiment_contribution: float = Field(..., description="Sentiment contribution percentage")


class BurnoutTrendInfo(BaseModel):
    """Trend information."""
    direction: str = Field(..., description="rising, stable, or lowering")
    change_percentage: float = Field(..., description="Percentage change")
    change_points: float = Field(..., description="Absolute change in points")
    days_at_current_level: int = Field(..., description="Days at current burnout level")


class AlertTrigger(BaseModel):
    """Alert trigger information."""
    category: str = Field(..., description="Alert category")
    severity: str = Field(..., description="Alert severity level")
    message: str = Field(..., description="Alert message")
    triggered: bool = Field(..., description="Whether alert is triggered")


class BurnoutAnalysisResponse(BaseModel):
    """Complete burnout analysis response."""
    user_id: int = Field(..., description="User ID")
    analyzed_at: str = Field(..., description="Analysis timestamp")

    # Core burnout info
    final_score: float = Field(..., description="Final burnout score (0-100)", ge=0, le=100)
    level: str = Field(..., description="Burnout level (LOW, MODERATE, HIGH, SEVERE, CRITICAL)")
    status_message: str = Field(..., description="Human-readable status message")

    # Component breakdown
    components: BurnoutComponentsResponse = Field(..., description="Score component breakdown")

    # Insights and trends
    insights: Dict[str, Any] = Field(..., description="Analysis insights")
    trend: Optional[BurnoutTrendInfo] = Field(None, description="Trend information")
    alert_triggers: List[AlertTrigger] = Field(default_factory=list, description="Alert triggers")


class TrendDataPoint(BaseModel):
    """Single trend data point."""
    date: str = Field(..., description="Date of analysis")
    score: float = Field(..., description="Burnout score", ge=0, le=100)
    level: str = Field(..., description="Burnout level")


class BurnoutTrendResponse(BaseModel):
    """Burnout trend over time."""
    user_id: int
    period: str = Field(..., description="Time period (7days, 30days, 90days)")

    # Trend data
    data_points: List[TrendDataPoint] = Field(..., description="Historical data points")

    # Trend analysis
    trend_direction: str = Field(..., description="rising, stable, or lowering")
    percentage_change: float = Field(..., description="Percentage change over period")
    current_score: float = Field(..., description="Current burnout score")
    previous_score: float = Field(..., description="Score at start of period")

    # Moving average
    moving_average: List[float] = Field(default_factory=list, description="7-day moving average")


class BurnoutBreakdownResponse(BaseModel):
    """Detailed component breakdown."""
    user_id: int
    analyzed_at: str

    # Component scores
    workload_score: float = Field(..., description="Raw workload score (0-100)")
    sentiment_score: float = Field(..., description="Sentiment adjustment (-20 to +20)")
    temporal_adjustment: Optional[float] = Field(None, description="Temporal adjustment")

    # Contribution percentages
    workload_contribution_percent: float = Field(..., description="Workload contribution %")
    sentiment_contribution_percent: float = Field(..., description="Sentiment contribution %")

    # Final score
    final_score: float = Field(..., description="Final burnout score")


class BurnoutInsightsResponse(BaseModel):
    """Primary issues and insights."""
    user_id: int
    analyzed_at: str

    # Primary contributors
    primary_contributors: List[str] = Field(..., description="Main burnout factors")

    # Key insights
    key_insights: List[str] = Field(..., description="Key analysis insights")

    # Risk factors
    risk_factors: List[str] = Field(..., description="Identified risk factors")

    # Alert triggers
    alert_triggers: List[AlertTrigger] = Field(..., description="Critical issues")


class StressIndicator(BaseModel):
    """Stress indicator from sentiment analysis."""
    indicator: str = Field(..., description="Stress indicator text")
    severity: str = Field(..., description="Severity level")


class BurnoutSignalsResponse(BaseModel):
    """Burnout warning signals."""
    user_id: int
    analyzed_at: str

    # Sentiment-based signals
    stress_indicators: List[StressIndicator] = Field(..., description="Stress indicators from text")
    burnout_signals: Dict[str, Any] = Field(..., description="Detected burnout signals")

    # Behavioral warnings
    work_pattern_anomalies: List[str] = Field(..., description="Anomalous work patterns")

    # Historical patterns
    historical_patterns: Optional[List[str]] = Field(None, description="Patterns from history")


class RecoveryAction(BaseModel):
    """Single recovery action."""
    title: str
    priority: str
    description: str
    action_steps: List[str]
    timeline: str = Field(..., description="When to do this (immediate, short-term, long-term)")
    expected_impact: str


class RecoveryPlanResponse(BaseModel):
    """Structured recovery plan."""
    user_id: int
    generated_at: str
    burnout_level: str

    # Categorized by timeline
    immediate_actions: List[RecoveryAction] = Field(..., description="Next 24-48 hours")
    short_term_goals: List[RecoveryAction] = Field(..., description="Next 1-2 weeks")
    long_term_strategies: List[RecoveryAction] = Field(..., description="Next month")

    # Progress tracking
    progress_metrics: List[str] = Field(..., description="Metrics to track progress")
