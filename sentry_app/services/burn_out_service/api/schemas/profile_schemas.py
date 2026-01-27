"""
User Profile API Schemas
=========================

Pydantic models for user profile endpoints.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional
from datetime import datetime


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class BehavioralProfileResponse(BaseModel):
    """Behavioral profile data."""
    # Averages
    avg_tasks_per_day: Optional[float] = None
    avg_work_hours_per_day: Optional[float] = None
    avg_meetings_per_day: Optional[float] = None
    avg_meeting_hours_per_day: Optional[float] = None
    avg_completion_rate: Optional[float] = None

    # Baselines
    baseline_burnout_score: Optional[float] = None
    baseline_task_count: Optional[int] = None
    baseline_work_hours: Optional[float] = None
    baseline_meeting_count: Optional[int] = None

    # Patterns
    peak_productivity_hour: Optional[int] = Field(None, description="Hour of day (0-23)")
    most_productive_day: Optional[str] = None
    least_productive_day: Optional[str] = None

    # Stress triggers
    stress_triggers: List[str] = Field(default_factory=list)

    # Last updated
    last_pattern_analysis: Optional[str] = None


class PreferencesResponse(BaseModel):
    """User preferences."""
    preferred_work_hours_start: Optional[str] = None
    preferred_work_hours_end: Optional[str] = None
    max_daily_meetings: Optional[int] = None
    focus_time_blocks_needed: Optional[int] = None
    communication_style: Optional[str] = None
    work_style: Optional[str] = None


class ConstraintsResponse(BaseModel):
    """User constraints."""
    has_caregiving_responsibilities: bool = False
    has_health_conditions: bool = False
    has_timezone_constraints: bool = False
    description: Optional[str] = None


class UserProfileResponse(BaseModel):
    """Complete user profile."""
    user_id: int
    full_name: str
    email: str
    job_role: Optional[str] = None
    seniority_level: Optional[str] = None
    department: Optional[str] = None
    timezone: str = Field(default="UTC")

    # Sub-profiles
    preferences: Optional[PreferencesResponse] = None
    constraints: Optional[ConstraintsResponse] = None
    behavioral_profile: Optional[BehavioralProfileResponse] = None

    # Metadata
    created_at: str
    updated_at: str


# ============================================================================
# REQUEST MODELS
# ============================================================================

class UpdatePreferencesRequest(BaseModel):
    """Update user preferences."""
    preferred_work_hours_start: Optional[str] = Field(None, pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    preferred_work_hours_end: Optional[str] = Field(None, pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    max_daily_meetings: Optional[int] = Field(None, ge=0, le=20)
    focus_time_blocks_needed: Optional[int] = Field(None, ge=0, le=8)
    communication_style: Optional[str] = Field(None, description="e.g., 'direct', 'collaborative'")
    work_style: Optional[str] = Field(None, description="e.g., 'independent', 'team-oriented'")


class UpdateConstraintsRequest(BaseModel):
    """Update user constraints."""
    has_caregiving_responsibilities: Optional[bool] = None
    has_health_conditions: Optional[bool] = None
    has_timezone_constraints: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=500)


class UpdateProfileRequest(BaseModel):
    """Update user profile."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    job_role: Optional[str] = Field(None, max_length=100)
    seniority_level: Optional[str] = Field(None, max_length=50, description="e.g., 'Junior', 'Mid', 'Senior', 'Staff'")
    department: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)

    # Sub-profiles
    preferences: Optional[UpdatePreferencesRequest] = None
    constraints: Optional[UpdateConstraintsRequest] = None


class LearnPatternsResponse(BaseModel):
    """Response from pattern learning."""
    user_id: int
    patterns_learned: Dict[str, Optional[float]] = Field(..., description="Learned behavioral patterns")
    days_analyzed: int = Field(..., description="Number of days analyzed")
    last_updated: str = Field(..., description="Timestamp of pattern update")
