"""
User Profile Schemas - Pydantic Models
=======================================

Data validation and serialization schemas for user profiles.
Used for API requests/responses and data validation.

Author: Sentry AI Team
Date: 2025
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict
from datetime import datetime, time, date
from enum import Enum


# ============================================================================
# ENUMS FOR CHOICES
# ============================================================================

class JobRole(str, Enum):
    """Standard job roles"""
    SOFTWARE_ENGINEER = "Software Engineer"
    PRODUCT_MANAGER = "Product Manager"
    DESIGNER = "Designer"
    DATA_SCIENTIST = "Data Scientist"
    DEVOPS_ENGINEER = "DevOps Engineer"
    QA_ENGINEER = "QA Engineer"
    MARKETING = "Marketing"
    SALES = "Sales"
    CUSTOMER_SUCCESS = "Customer Success"
    HR = "Human Resources"
    FINANCE = "Finance"
    STUDENT = "Student"
    OTHER = "Other"


class SeniorityLevel(str, Enum):
    """Seniority levels"""
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"
    STAFF = "Staff"
    PRINCIPAL = "Principal"
    LEAD = "Lead"
    MANAGER = "Manager"
    DIRECTOR = "Director"
    VP = "VP"
    C_LEVEL = "C-Level"


class WorkArrangement(str, Enum):
    """Work arrangement types"""
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    OFFICE = "Office"


class CommunicationStyle(str, Enum):
    """Communication preferences"""
    DIRECT = "direct"
    EMPATHETIC = "empathetic"
    CASUAL = "casual"
    FORMAL = "formal"


class ActionStyle(str, Enum):
    """Preferred action types"""
    QUICK_WINS = "quick_wins"
    SYSTEMATIC = "systematic"
    COLLABORATIVE = "collaborative"


class NotificationFrequency(str, Enum):
    """Notification delivery preferences"""
    REALTIME = "realtime"
    BATCHED = "batched"
    DAILY_DIGEST = "daily_digest"
    WEEKLY_DIGEST = "weekly_digest"


class ConstraintType(str, Enum):
    """Types of user constraints"""
    DEADLINE = "deadline"
    PTO_RESTRICTED = "pto_restricted"
    ON_CALL = "on_call"
    CRITICAL_MEETING = "critical_meeting"
    PROJECT_LAUNCH = "project_launch"
    TEAM_UNDERSTAFFED = "team_understaffed"


class PriorityLevel(str, Enum):
    """Priority levels for constraints"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# ONBOARDING SCHEMAS
# ============================================================================

class OnboardingStep1(BaseModel):
    """First step of onboarding - Role & Seniority"""
    job_role: JobRole
    seniority_level: SeniorityLevel
    job_title: Optional[str] = None


class OnboardingStep2(BaseModel):
    """Second step - Team & Schedule"""
    team_size: int = Field(ge=0, le=1000, description="Team size")
    direct_reports: int = Field(ge=0, le=100, description="Direct reports")
    has_flexible_schedule: bool = True
    biggest_challenge: str = Field(min_length=1, max_length=500)


class OnboardingStep3(BaseModel):
    """Third step - Preferences & History"""
    peak_productivity_time: str = Field(description="morning, midday, afternoon, evening")
    things_tried_before: List[str] = Field(default_factory=list)
    communication_style: CommunicationStyle = CommunicationStyle.DIRECT
    
    @validator('peak_productivity_time')
    def validate_time_of_day(cls, v):
        valid_times = ['morning', 'midday', 'afternoon', 'evening', 'unknown']
        if v.lower() not in valid_times:
            raise ValueError(f"Must be one of: {valid_times}")
        return v.lower()


class CompleteOnboarding(BaseModel):
    """Complete onboarding data"""
    # From Step 1
    job_role: JobRole
    seniority_level: SeniorityLevel
    job_title: Optional[str] = None
    
    # From Step 2
    team_size: int = Field(ge=0)
    direct_reports: int = Field(ge=0)
    has_flexible_schedule: bool = True
    biggest_challenge: str
    
    # From Step 3
    peak_productivity_time: str
    things_tried_before: List[str] = Field(default_factory=list)
    communication_style: CommunicationStyle = CommunicationStyle.DIRECT
    
    # Additional optional
    department: Optional[str] = None
    team_name: Optional[str] = None
    work_arrangement: WorkArrangement = WorkArrangement.HYBRID
    timezone: str = "UTC"


# ============================================================================
# USER PROFILE SCHEMAS
# ============================================================================

class UserProfileCreate(BaseModel):
    """Schema for creating a new user profile"""
    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    timezone: str = "UTC"
    
    # Onboarding data
    onboarding_data: Optional[CompleteOnboarding] = None


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    timezone: Optional[str] = None
    job_title: Optional[str] = None
    team_name: Optional[str] = None
    team_size: Optional[int] = None
    direct_reports: Optional[int] = None
    work_arrangement: Optional[WorkArrangement] = None
    typical_work_hours_start: Optional[time] = None
    typical_work_hours_end: Optional[time] = None
    communication_style: Optional[CommunicationStyle] = None


class UserProfileResponse(BaseModel):
    """Response schema for user profile"""
    user_id: int
    full_name: str
    email: str
    timezone: str
    
    # Role info
    job_role: Optional[str]
    seniority_level: Optional[str]
    department: Optional[str]
    job_title: Optional[str]
    
    # Team info
    team_size: int
    direct_reports: int
    team_name: Optional[str]
    
    # Capabilities
    can_delegate: bool
    has_flexible_schedule: bool
    can_work_remotely: bool
    
    # Work arrangement
    work_arrangement: Optional[str]
    
    # Status
    profile_complete: bool
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


# ============================================================================
# BEHAVIORAL PROFILE SCHEMAS
# ============================================================================

class BehavioralProfileResponse(BaseModel):
    """Response schema for behavioral profile"""
    user_id: int
    
    # Work patterns
    avg_tasks_per_day: Optional[float]
    avg_work_hours_per_day: Optional[float]
    avg_meetings_per_day: Optional[float]
    avg_completion_rate: Optional[float]
    
    # Peak productivity
    peak_productivity_hour: Optional[int]
    most_productive_day: Optional[str]
    
    # Stress triggers
    stress_triggers: Optional[List[str]]
    
    # Response patterns
    typical_response_time: Optional[str]
    follows_through_rate: Optional[float]
    dismissal_rate: Optional[float]
    
    # Preferences
    preferred_recommendation_types: Optional[List[str]]
    avoided_recommendation_types: Optional[List[str]]
    
    # Baselines
    baseline_burnout_score: Optional[float]
    baseline_task_count: Optional[float]
    
    # Engagement
    total_recommendations_received: int
    total_recommendations_accepted: int
    total_recommendations_completed: int
    
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BehavioralProfileUpdate(BaseModel):
    """Schema for updating behavioral profile (system-generated)"""
    avg_tasks_per_day: Optional[float] = None
    avg_work_hours_per_day: Optional[float] = None
    avg_meetings_per_day: Optional[float] = None
    avg_completion_rate: Optional[float] = None
    peak_productivity_hour: Optional[int] = Field(None, ge=0, le=23)
    stress_triggers: Optional[List[str]] = None
    baseline_burnout_score: Optional[float] = None


# ============================================================================
# CONSTRAINT SCHEMAS
# ============================================================================

class ConstraintCreate(BaseModel):
    """Schema for creating a new constraint"""
    constraint_type: ConstraintType
    constraint_name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    blocks_delegation: bool = False
    blocks_pto: bool = False
    blocks_meeting_cancellation: bool = False
    priority_level: PriorityLevel = PriorityLevel.MEDIUM
    
    @validator('end_date')
    def end_after_start(cls, v, values):
        if 'start_date' in values and values['start_date'] and v:
            if v < values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v


class ConstraintUpdate(BaseModel):
    """Schema for updating a constraint"""
    constraint_name: Optional[str] = None
    description: Optional[str] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    priority_level: Optional[PriorityLevel] = None


class ConstraintResponse(BaseModel):
    """Response schema for constraint"""
    id: int
    user_id: int
    constraint_type: str
    constraint_name: str
    description: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    is_active: bool
    blocks_delegation: bool
    blocks_pto: bool
    blocks_meeting_cancellation: bool
    priority_level: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# PREFERENCES SCHEMAS
# ============================================================================

class PreferencesUpdate(BaseModel):
    """Schema for updating user preferences"""
    # Notifications
    enable_push_notifications: Optional[bool] = None
    enable_email_notifications: Optional[bool] = None
    enable_slack_notifications: Optional[bool] = None
    notification_frequency: Optional[NotificationFrequency] = None
    
    # Quiet hours
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[time] = None
    quiet_hours_end: Optional[time] = None
    quiet_hours_days: Optional[List[str]] = None
    
    # Alerts
    min_alert_severity: Optional[str] = None
    max_alerts_per_day: Optional[int] = Field(None, ge=0, le=50)
    alert_style: Optional[str] = None
    
    # Auto-actions
    allow_auto_calendar_block: Optional[bool] = None
    allow_auto_meeting_decline: Optional[bool] = None
    allow_auto_task_reschedule: Optional[bool] = None
    
    # Privacy
    allow_team_visibility: Optional[bool] = None
    
    # Recommendations
    recommendation_detail_level: Optional[str] = None
    show_research_citations: Optional[bool] = None


class PreferencesResponse(BaseModel):
    """Response schema for preferences"""
    user_id: int
    
    # Notifications
    enable_push_notifications: bool
    enable_email_notifications: bool
    enable_slack_notifications: bool
    notification_frequency: str
    
    # Quiet hours
    quiet_hours_enabled: bool
    quiet_hours_start: Optional[time]
    quiet_hours_end: Optional[time]
    quiet_hours_days: Optional[List[str]]
    
    # Alerts
    min_alert_severity: str
    max_alerts_per_day: int
    alert_style: str
    
    # Auto-actions
    allow_auto_calendar_block: bool
    allow_auto_meeting_decline: bool
    allow_auto_task_reschedule: bool
    
    # Privacy
    allow_team_visibility: bool
    
    # Recommendations
    recommendation_detail_level: str
    show_research_citations: bool
    
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# COMPLETE PROFILE SCHEMA (For LLM Context)
# ============================================================================

class CompleteProfileForLLM(BaseModel):
    """
    Complete profile data formatted for LLM context.
    This is what gets passed to the recommendation engine.
    """
    # Basic info
    user_id: int
    full_name: str
    job_role: str
    seniority_level: str
    team_size: int
    direct_reports: int
    can_delegate: bool
    
    # Work patterns
    avg_tasks_per_day: Optional[float]
    avg_work_hours_per_day: Optional[float]
    avg_meetings_per_day: Optional[float]
    baseline_burnout_score: Optional[float]
    
    # Preferences
    communication_style: str
    preferred_recommendation_types: Optional[List[str]]
    avoided_recommendation_types: Optional[List[str]]
    
    # Current constraints
    active_constraints: List[ConstraintResponse]
    
    # Effectiveness data (added from recommendation history)
    top_effective_recommendations: Optional[List[Dict]] = None
    
    def to_llm_context(self) -> str:
        """
        Format profile as text for LLM prompt.
        """
        context = f"""
USER PROFILE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {self.full_name}
Role: {self.seniority_level} {self.job_role}
Team: {self.team_size} people, {self.direct_reports} direct reports
Can delegate: {self.can_delegate}

BEHAVIORAL PATTERNS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Typical workload: {self.avg_tasks_per_day or 'Unknown'} tasks, {self.avg_meetings_per_day or 'Unknown'} meetings
Work hours: {self.avg_work_hours_per_day or 'Unknown'} hours/day
Baseline burnout (healthy): {self.baseline_burnout_score or 'Unknown'}

PREFERENCES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Communication style: {self.communication_style}
Accepts: {', '.join(self.preferred_recommendation_types or ['Unknown'])}
Avoids: {', '.join(self.avoided_recommendation_types or ['None'])}

CURRENT CONSTRAINTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        if self.active_constraints:
            for c in self.active_constraints:
                context += f"• {c.constraint_name} ({c.constraint_type}) until {c.end_date}\n"
                if c.blocks_delegation:
                    context += "  - Cannot delegate during this time\n"
                if c.blocks_pto:
                    context += "  - Cannot take PTO during this time\n"
        else:
            context += "None\n"
        
        return context


