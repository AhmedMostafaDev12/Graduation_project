"""
Recommendation Tracking Models
==============================

SQLAlchemy models for tracking AI-generated recommendations,
their applications, and user feedback.
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Recommendation(Base):
    """
    Stores all AI-generated recommendations for users.

    Each recommendation is linked to a specific burnout analysis
    and contains action steps that can be applied automatically.
    """
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    burnout_analysis_id = Column(Integer, ForeignKey('burnout_analyses.id', ondelete='SET NULL'), nullable=True)

    # Recommendation content
    title = Column(String(255), nullable=False)
    priority = Column(String(50))  # HIGH, MEDIUM, LOW
    description = Column(Text)
    action_steps = Column(JSONB)  # Array of action steps
    expected_impact = Column(Text)

    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(String(100), default='RAG+LLM')
    llm_model = Column(String(100))
    strategies_retrieved = Column(Integer)
    generation_time_seconds = Column(Float)

    # Categorization
    category = Column(String(100))
    burnout_component = Column(String(50))

    # Relationships
    applications = relationship("RecommendationApplication", back_populates="recommendation", cascade="all, delete-orphan")
    action_items = relationship("RecommendationActionItem", back_populates="recommendation", cascade="all, delete-orphan")
    feedback = relationship("RecommendationFeedback", back_populates="recommendation", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("priority IN ('HIGH', 'MEDIUM', 'LOW')", name='valid_priority'),
    )


class RecommendationApplication(Base):
    """
    Tracks when recommendations are applied and their outcomes.

    Records the impact of applying recommendations including
    tasks created, completion rates, and burnout score changes.
    """
    __tablename__ = "recommendation_applications"

    id = Column(Integer, primary_key=True)
    recommendation_id = Column(Integer, ForeignKey('recommendations.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Application details
    applied_at = Column(DateTime, default=datetime.utcnow)
    applied_by = Column(String(100))  # 'user' or 'auto'

    # What was created/modified
    tasks_created = Column(Integer, default=0)
    task_ids = Column(JSONB)  # Array of created task IDs
    calendar_events_created = Column(Integer, default=0)
    tasks_modified = Column(Integer, default=0)

    # Effectiveness tracking
    status = Column(String(50), default='applied')  # applied, in_progress, completed, cancelled
    completion_rate = Column(Float)  # 0-100
    completed_at = Column(DateTime)
    time_to_complete_days = Column(Integer)

    # User feedback
    effectiveness_rating = Column(Integer)  # 1-5 stars
    user_feedback = Column(Text)
    feedback_submitted_at = Column(DateTime)

    # Impact measurement
    burnout_score_before = Column(Integer)
    burnout_score_after = Column(Integer)
    # burnout_improvement is a GENERATED column in PostgreSQL, not defined here

    # Relationships
    recommendation = relationship("Recommendation", back_populates="applications")

    __table_args__ = (
        CheckConstraint("status IN ('applied', 'in_progress', 'completed', 'cancelled')", name='valid_status'),
        CheckConstraint("effectiveness_rating IS NULL OR (effectiveness_rating >= 1 AND effectiveness_rating <= 5)", name='valid_rating'),
    )


class RecommendationActionItem(Base):
    """
    Tracks individual action steps from recommendations.

    Links action steps to actual tasks when they are created,
    allowing fine-grained tracking of recommendation completion.
    """
    __tablename__ = "recommendation_action_items"

    id = Column(Integer, primary_key=True)
    recommendation_id = Column(Integer, ForeignKey('recommendations.id', ondelete='CASCADE'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True)

    # Action details
    action_text = Column(Text, nullable=False)
    action_order = Column(Integer)  # 1st, 2nd, 3rd action step

    # Completion tracking
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    recommendation = relationship("Recommendation", back_populates="action_items")


class RecommendationFeedback(Base):
    """
    Additional detailed feedback on recommendations.

    Captures user feedback to improve future recommendations
    and measure effectiveness of different strategies.
    """
    __tablename__ = "recommendation_feedback"

    id = Column(Integer, primary_key=True)
    recommendation_id = Column(Integer, ForeignKey('recommendations.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    # Feedback details
    helpful = Column(Boolean)
    reason = Column(String(255))

    # Which action steps were most helpful
    most_helpful_action_step = Column(Integer)
    least_helpful_action_step = Column(Integer)

    # Free-form feedback
    comments = Column(Text)

    # Metadata
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    recommendation = relationship("Recommendation", back_populates="feedback")
