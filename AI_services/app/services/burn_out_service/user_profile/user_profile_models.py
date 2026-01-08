"""
User Profile System - SQLAlchemy Models
========================================

Database models for storing user profiles, behavioral patterns,
constraints, and preferences.

Author: Sentry AI Team
Date: 2025
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, Float, Time, Date,
    DateTime, Text, ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, time
from typing import Optional, List, Dict

# Import shared base
from .database_base import Base


# ============================================================================
# CORE USER PROFILE MODEL
# ============================================================================

class UserProfile(Base):
    """
    Core user profile containing static information collected during onboarding.
    This is the foundation - other profile tables reference this.
    """
    __tablename__ = "user_profiles"
    
    # ========== IDENTITY ==========
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # ========== DEMOGRAPHICS ==========
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    timezone = Column(String(50), default="UTC")  # e.g., "America/New_York"
    
    # ========== ROLE INFORMATION ==========
    job_role = Column(String(100), nullable=False)  # "Software Engineer", "Product Manager"
    seniority_level = Column(String(50), nullable=False)  # "Junior", "Mid", "Senior", "Staff"
    department = Column(String(100))  # "Engineering", "Sales", "Marketing"
    job_title = Column(String(200))  # Actual title (more specific)
    
    # ========== TEAM STRUCTURE ==========
    team_size = Column(Integer, default=0)  # Number of people on their team
    direct_reports = Column(Integer, default=0)  # Number of people they manage
    reports_to = Column(String(255))  # Manager's email (optional)
    team_name = Column(String(100))  # Team or squad name
    
    # ========== CAPABILITIES ==========
    can_delegate = Column(Boolean, default=False)
    has_flexible_schedule = Column(Boolean, default=True)
    can_work_remotely = Column(Boolean, default=True)
    has_calendar_access = Column(Boolean, default=False)  # Calendar connected?
    has_slack_access = Column(Boolean, default=False)  # Slack connected?
    
    # ========== WORK ARRANGEMENT ==========
    work_arrangement = Column(String(50))  # "Remote", "Hybrid", "Office"
    typical_work_hours_start = Column(Time, default=time(9, 0))  # 09:00
    typical_work_hours_end = Column(Time, default=time(17, 0))  # 17:00
    
    # ========== PREFERENCES (Collected during onboarding) ==========
    communication_style = Column(String(50), default="direct")  # "direct", "empathetic", "casual"
    notification_preference = Column(String(50), default="realtime")  # "immediate", "batched", "digest"
    action_style = Column(String(50), default="quick_wins")  # "quick_wins", "systematic", "collaborative"
    
    # ========== ONBOARDING CONTEXT ==========
    biggest_challenge = Column(String(200))  # What they said during onboarding
    things_tried_before = Column(JSON)  # List of strategies they've tried
    
    # ========== STATUS ==========
    profile_complete = Column(Boolean, default=False)
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # ========== RELATIONSHIPS ==========
    behavioral_profile = relationship("UserBehavioralProfile", back_populates="user", uselist=False)
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    constraints = relationship("UserConstraint", back_populates="user")
    
    # ========== INDEXES ==========
    __table_args__ = (
        Index('idx_user_role', 'job_role', 'seniority_level'),
        Index('idx_user_team', 'team_name'),
        Index('idx_user_email', 'email'),
    )
    
    def __repr__(self):
        return f"<UserProfile(id={self.user_id}, name='{self.full_name}', role='{self.job_role}')>"


# ============================================================================
# BEHAVIORAL PROFILE (LEARNED PATTERNS)
# ============================================================================

class UserBehavioralProfile(Base):
    """
    Behavioral patterns learned from user activity over time.
    Updated automatically by the system (no manual input).
    """
    __tablename__ = "user_behavioral_profiles"
    
    user_id = Column(Integer, ForeignKey('user_profiles.user_id'), primary_key=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # ========== WORK PATTERNS (30-day rolling averages) ==========
    avg_tasks_per_day = Column(Float)
    avg_work_hours_per_day = Column(Float)
    avg_meetings_per_day = Column(Float)
    avg_meeting_hours_per_day = Column(Float)
    avg_completion_rate = Column(Float)  # 0.0 to 1.0
    
    # ========== PEAK PRODUCTIVITY (Learned) ==========
    peak_productivity_hour = Column(Integer)  # 0-23 (hour of day)
    most_productive_day = Column(String(20))  # "Monday", "Tuesday", etc.
    least_productive_day = Column(String(20))
    
    # ========== STRESS TRIGGERS (Identified patterns) ==========
    stress_triggers = Column(JSON)  # ["back_to_back_meetings", "weekend_work"]
    
    # ========== RESPONSE PATTERNS ==========
    typical_response_time = Column(String(50))  # "immediate", "same_day", "delayed"
    follows_through_rate = Column(Float)  # 0.0 to 1.0
    dismissal_rate = Column(Float)  # 0.0 to 1.0
    
    # ========== PREFERENCE LEARNING ==========
    preferred_recommendation_types = Column(JSON)  # ["time_blocking", "async_communication"]
    avoided_recommendation_types = Column(JSON)  # ["delegation", "confrontation"]
    
    # ========== BEST TIME FOR ALERTS ==========
    best_notification_time = Column(Time)  # Learned from engagement
    worst_notification_time = Column(Time)  # When they ignore alerts
    
    # ========== BASELINE SCORES (Personal "normal") ==========
    baseline_burnout_score = Column(Float)  # Their typical score when healthy
    baseline_task_count = Column(Float)
    baseline_work_hours = Column(Float)
    baseline_meeting_count = Column(Float)
    
    # ========== RECOVERY PATTERNS ==========
    typical_recovery_time_days = Column(Integer)  # Days to go from RED to GREEN
    effective_recovery_methods = Column(JSON)  # What works for them
    
    # ========== ENGAGEMENT METRICS ==========
    total_recommendations_received = Column(Integer, default=0)
    total_recommendations_accepted = Column(Integer, default=0)
    total_recommendations_completed = Column(Integer, default=0)
    avg_time_to_action_minutes = Column(Integer)
    
    # ========== METADATA ==========
    last_pattern_analysis = Column(DateTime)
    
    # ========== RELATIONSHIPS ==========
    user = relationship("UserProfile", back_populates="behavioral_profile")
    
    def __repr__(self):
        return f"<BehavioralProfile(user_id={self.user_id}, baseline={self.baseline_burnout_score})>"


# ============================================================================
# USER CONSTRAINTS (TEMPORARY/ACTIVE)
# ============================================================================

class UserConstraint(Base):
    """
    Active constraints affecting the user (deadlines, PTO restrictions, etc.)
    These are temporary and affect what recommendations we can give.
    """
    __tablename__ = "user_constraints"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user_profiles.user_id'), nullable=False)
    
    # ========== CONSTRAINT DETAILS ==========
    constraint_type = Column(String(50), nullable=False)  # "deadline", "pto_restricted", "on_call"
    constraint_name = Column(String(255), nullable=False)  # "Q4 Product Launch"
    description = Column(Text)
    
    # ========== TIMING ==========
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True, index=True)
    
    # ========== IMPACT ON RECOMMENDATIONS ==========
    blocks_delegation = Column(Boolean, default=False)
    blocks_pto = Column(Boolean, default=False)
    blocks_meeting_cancellation = Column(Boolean, default=False)
    priority_level = Column(String(20), default="medium")  # "low", "medium", "high", "critical"
    
    # ========== METADATA ==========
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime)
    
    # ========== RELATIONSHIPS ==========
    user = relationship("UserProfile", back_populates="constraints")
    
    # ========== INDEXES ==========
    __table_args__ = (
        Index('idx_active_constraints', 'user_id', 'is_active', 'end_date'),
    )
    
    def __repr__(self):
        return f"<UserConstraint(id={self.id}, type='{self.constraint_type}', active={self.is_active})>"


# ============================================================================
# USER PREFERENCES & SETTINGS
# ============================================================================

class UserPreferences(Base):
    """
    User-controlled settings for notifications, privacy, and UI preferences.
    """
    __tablename__ = "user_preferences"
    
    user_id = Column(Integer, ForeignKey('user_profiles.user_id'), primary_key=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # ========== NOTIFICATION SETTINGS ==========
    enable_push_notifications = Column(Boolean, default=True)
    enable_email_notifications = Column(Boolean, default=True)
    enable_slack_notifications = Column(Boolean, default=False)
    notification_frequency = Column(String(50), default='realtime')  # "realtime", "batched", "digest"
    
    # ========== QUIET HOURS ==========
    quiet_hours_enabled = Column(Boolean, default=False)
    quiet_hours_start = Column(Time)  # e.g., 20:00
    quiet_hours_end = Column(Time)  # e.g., 08:00
    quiet_hours_days = Column(JSON)  # ["saturday", "sunday"]
    
    # ========== ALERT PREFERENCES ==========
    min_alert_severity = Column(String(20), default='medium')  # Only show medium+ alerts
    max_alerts_per_day = Column(Integer, default=5)
    alert_style = Column(String(50), default='balanced')  # "minimal", "balanced", "detailed"
    
    # ========== AUTO-ACTION PERMISSIONS ==========
    allow_auto_calendar_block = Column(Boolean, default=False)
    allow_auto_meeting_decline = Column(Boolean, default=False)
    allow_auto_task_reschedule = Column(Boolean, default=False)
    
    # ========== UI PREFERENCES ==========
    dashboard_layout = Column(String(50), default='default')
    theme = Column(String(20), default='light')  # "light", "dark", "auto"
    language = Column(String(10), default='en')
    
    # ========== PRIVACY SETTINGS ==========
    share_data_for_research = Column(Boolean, default=False)
    share_anonymized_patterns = Column(Boolean, default=True)
    allow_team_visibility = Column(Boolean, default=True)  # Can manager see burnout?
    
    # ========== RECOMMENDATION PREFERENCES ==========
    recommendation_detail_level = Column(String(20), default='medium')  # "brief", "medium", "detailed"
    show_research_citations = Column(Boolean, default=True)
    show_success_rates = Column(Boolean, default=True)
    
    # ========== RELATIONSHIPS ==========
    user = relationship("UserProfile", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id})>"


# ============================================================================
# HELPER FUNCTION FOR DATABASE INITIALIZATION
# ============================================================================

def init_database(engine):
    """
    Initialize database tables.
    
    Usage:
        from sqlalchemy import create_engine
        engine = create_engine('postgresql://user:pass@localhost/dbname')
        init_database(engine)
    """
    Base.metadata.create_all(engine)
    print("✅ User profile tables created successfully!")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example of how to use these models.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Create in-memory SQLite database for testing
    engine = create_engine('sqlite:///user_profiles.db', echo=True)
    init_database(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("\n" + "="*80)
    print("EXAMPLE: Creating a new user profile")
    print("="*80)
    
    # Create a new user profile
    user = UserProfile(
        full_name="Sarah Chen",
        email="sarah.chen@company.com",
        timezone="America/New_York",
        job_role="Software Engineer",
        seniority_level="Senior",
        department="Engineering",
        job_title="Senior Backend Engineer",
        team_size=8,
        direct_reports=2,
        team_name="Platform Team",
        can_delegate=True,
        work_arrangement="Hybrid",
        communication_style="direct",
        biggest_challenge="Too many meetings",
        things_tried_before=["time_blocking", "saying_no"],
        onboarding_completed=True,
        profile_complete=True
    )
    
    session.add(user)
    session.commit()
    
    print(f"\n✅ Created: {user}")
    print(f"   User ID: {user.user_id}")
    print(f"   Email: {user.email}")
    print(f"   Role: {user.seniority_level} {user.job_role}")
    print(f"   Team: {user.team_name} ({user.team_size} people)")
    print(f"   Can delegate: {user.can_delegate}")
    
    # Create behavioral profile
    behavioral = UserBehavioralProfile(
        user_id=user.user_id,
        avg_tasks_per_day=8.5,
        avg_work_hours_per_day=9.2,
        avg_meetings_per_day=4.5,
        avg_completion_rate=0.85,
        peak_productivity_hour=10,
        most_productive_day="Tuesday",
        baseline_burnout_score=42.0,
        follows_through_rate=0.78,
        preferred_recommendation_types=["time_blocking", "async_communication"],
        avoided_recommendation_types=["meditation"]
    )
    
    session.add(behavioral)
    session.commit()
    
    print(f"\n✅ Created behavioral profile:")
    print(f"   Avg tasks/day: {behavioral.avg_tasks_per_day}")
    print(f"   Baseline burnout: {behavioral.baseline_burnout_score}")
    print(f"   Preferred: {behavioral.preferred_recommendation_types}")
    
    # Create constraint
    constraint = UserConstraint(
        user_id=user.user_id,
        constraint_type="deadline",
        constraint_name="Q4 Product Launch",
        description="Major product launch for holiday season",
        start_date=datetime(2025, 11, 1).date(),
        end_date=datetime(2025, 12, 15).date(),
        blocks_pto=True,
        priority_level="critical"
    )
    
    session.add(constraint)
    session.commit()
    
    print(f"\n✅ Created constraint:")
    print(f"   Type: {constraint.constraint_type}")
    print(f"   Name: {constraint.constraint_name}")
    print(f"   Until: {constraint.end_date}")
    print(f"   Blocks PTO: {constraint.blocks_pto}")
    
    # Create preferences
    preferences = UserPreferences(
        user_id=user.user_id,
        enable_push_notifications=True,
        notification_frequency="realtime",
        quiet_hours_enabled=True,
        quiet_hours_start=time(20, 0),
        quiet_hours_end=time(8, 0),
        max_alerts_per_day=3,
        allow_team_visibility=True
    )
    
    session.add(preferences)
    session.commit()
    
    print(f"\n✅ Created preferences:")
    print(f"   Notifications: {preferences.notification_frequency}")
    print(f"   Quiet hours: {preferences.quiet_hours_start} - {preferences.quiet_hours_end}")
    print(f"   Max alerts/day: {preferences.max_alerts_per_day}")
    
    # Query the complete profile
    print("\n" + "="*80)
    print("QUERYING COMPLETE PROFILE")
    print("="*80)
    
    user_profile = session.query(UserProfile).filter_by(email="sarah.chen@company.com").first()
    
    print(f"\n📊 Complete Profile for {user_profile.full_name}:")
    print(f"\n   Basic Info:")
    print(f"   - Role: {user_profile.seniority_level} {user_profile.job_role}")
    print(f"   - Team: {user_profile.team_name}")
    print(f"   - Can delegate: {user_profile.can_delegate}")
    
    print(f"\n   Behavioral Patterns:")
    print(f"   - Avg work hours: {user_profile.behavioral_profile.avg_work_hours_per_day}/day")
    print(f"   - Baseline burnout: {user_profile.behavioral_profile.baseline_burnout_score}")
    print(f"   - Follow-through: {user_profile.behavioral_profile.follows_through_rate * 100}%")
    
    print(f"\n   Active Constraints: {len(user_profile.constraints)}")
    for c in user_profile.constraints:
        print(f"   - {c.constraint_name} (until {c.end_date})")
    
    print(f"\n   Notification Preferences:")
    print(f"   - Frequency: {user_profile.preferences.notification_frequency}")
    print(f"   - Quiet hours: {user_profile.preferences.quiet_hours_enabled}")
    
    print("\n" + "="*80)
    print("✅ User Profile Models Working Successfully!")
    print("="*80)
    
    session.close()