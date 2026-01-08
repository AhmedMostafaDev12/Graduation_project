"""
Workload & Data Submission API Schemas
======================================

Pydantic models for workload and qualitative data submission.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


# ============================================================================
# REQUEST MODELS
# ============================================================================

class WorkloadMetricsRequest(BaseModel):
    """Request body for submitting workload metrics."""
    user_id: int = Field(..., description="User ID")

    # Task metrics
    total_active_tasks: int = Field(..., ge=0, description="Total active tasks")
    overdue_tasks: int = Field(0, ge=0, description="Number of overdue tasks")
    tasks_due_this_week: int = Field(0, ge=0, description="Tasks due this week")
    completion_rate: float = Field(..., ge=0.0, le=1.0, description="Task completion rate")

    # Time metrics
    work_hours_today: float = Field(..., ge=0, description="Work hours today")
    work_hours_this_week: float = Field(..., ge=0, description="Work hours this week")

    # Meeting metrics
    meetings_today: int = Field(0, ge=0, description="Number of meetings today")
    total_meeting_hours_today: float = Field(0, ge=0, description="Total meeting hours today")
    back_to_back_meetings: int = Field(0, ge=0, description="Number of back-to-back meetings")

    # Pattern indicators
    weekend_work_sessions: int = Field(0, ge=0, description="Weekend work sessions")
    late_night_sessions: int = Field(0, ge=0, description="Late night work sessions")
    consecutive_work_days: int = Field(0, ge=0, description="Consecutive work days")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "total_active_tasks": 15,
                "overdue_tasks": 5,
                "tasks_due_this_week": 10,
                "completion_rate": 0.75,
                "work_hours_today": 9.5,
                "work_hours_this_week": 48.0,
                "meetings_today": 6,
                "total_meeting_hours_today": 4.0,
                "back_to_back_meetings": 3,
                "weekend_work_sessions": 1,
                "late_night_sessions": 2,
                "consecutive_work_days": 12
            }
        }


class QualitativeDataRequest(BaseModel):
    """Request body for submitting qualitative data."""
    user_id: int = Field(..., description="User ID")

    meeting_transcripts: List[str] = Field(default_factory=list, description="Meeting transcripts or notes")
    task_notes: List[str] = Field(default_factory=list, description="Task notes and comments")
    user_check_ins: List[str] = Field(default_factory=list, description="User check-in messages")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "meeting_transcripts": [
                    "Feeling overwhelmed with the Q4 deadline",
                    "Team mentioned working late to meet sprint goals"
                ],
                "task_notes": [
                    "This refactoring is taking longer than expected",
                    "Blocked by dependencies from other teams"
                ],
                "user_check_ins": [
                    "Feeling tired today, worked late last night",
                    "Need to take a break soon"
                ]
            }
        }


class AnalyzeRequest(BaseModel):
    """Request body for triggering complete burnout analysis."""
    user_id: int = Field(..., description="User ID")
    quantitative_metrics: WorkloadMetricsRequest = Field(..., description="Workload metrics")
    qualitative_data: QualitativeDataRequest = Field(..., description="Qualitative data")
    store_history: bool = Field(True, description="Whether to store analysis in history")


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class TaskBreakdown(BaseModel):
    """Task load breakdown."""
    active_tasks: int
    overdue_tasks: int
    tasks_due_this_week: int
    completion_rate: float


class TimeBreakdown(BaseModel):
    """Time breakdown."""
    work_hours_today: float
    work_hours_this_week: float
    meeting_hours_today: float
    estimated_focus_time: float = Field(..., description="Estimated deep focus time")


class MeetingPatterns(BaseModel):
    """Meeting patterns analysis."""
    total_meetings: int
    back_to_back_meetings: int
    optional_meetings: Optional[int] = None
    required_meetings: Optional[int] = None
    average_meeting_duration: Optional[float] = None


class WorkLifeBalance(BaseModel):
    """Work-life balance metrics."""
    weekend_work_sessions: int
    late_night_sessions: int
    consecutive_work_days: int
    work_life_balance_score: float = Field(..., description="0-100, higher is better")


class BaselineComparison(BaseModel):
    """Comparison to personal baseline."""
    current_vs_baseline_tasks: Optional[float] = Field(None, description="% difference from baseline")
    current_vs_baseline_hours: Optional[float] = Field(None, description="% difference from baseline")
    current_vs_baseline_meetings: Optional[float] = Field(None, description="% difference from baseline")


class WorkloadBreakdownResponse(BaseModel):
    """Detailed workload breakdown for UI charts."""
    user_id: int
    analyzed_at: str

    # Breakdowns
    task_breakdown: TaskBreakdown
    time_breakdown: TimeBreakdown
    meeting_patterns: MeetingPatterns
    work_life_balance: WorkLifeBalance

    # Baseline comparison (if available)
    baseline_comparison: Optional[BaselineComparison] = None
