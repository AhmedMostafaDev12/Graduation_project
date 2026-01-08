"""
Burnout Analysis History Model
===============================

This model stores daily burnout analysis snapshots for:
1. Historical trend analysis
2. Behavioral pattern learning
3. Effectiveness tracking

Author: Sentry AI Team
Date: 2025
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from datetime import datetime

# Import shared base
from .database_base import Base


class BurnoutAnalysis(Base):
    """
    Stores complete burnout analysis results for each day.
    
    This table is the SOURCE OF TRUTH for:
    - Behavioral learning (calculates patterns from this data)
    - Trend analysis (tracks score changes over time)
    - Effectiveness tracking (measures if recommendations worked)
    """
    __tablename__ = "burnout_analyses"
    
    # ========== PRIMARY KEY ==========
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # ========== USER & TIMESTAMP ==========
    user_id = Column(Integer, ForeignKey('user_profiles.user_id'), nullable=False, index=True)
    analyzed_at = Column(DateTime, nullable=False, index=True, default=func.now())
    
    # ========== BURNOUT SCORES ==========
    final_score = Column(Integer, nullable=False)  # 0-100
    level = Column(String(10), nullable=False)  # GREEN, YELLOW, RED
    
    # ========== RAW METRICS (For pattern learning) ==========
    # Stored as JSON to be flexible
    metrics = Column(JSON, nullable=False)
    """
    Example metrics structure:
    {
        "total_active_tasks": 12,
        "overdue_tasks": 3,
        "work_hours_today": 9,
        "work_hours_this_week": 45,
        "meetings_today": 5,
        "total_meeting_hours_today": 3.5,
        "back_to_back_meetings": 2,
        "completion_rate": 0.75,
        "weekend_work_sessions": 0,
        "late_night_sessions": 1,
        "days_without_breaks": 5,
        "consecutive_work_days": 10
    }
    """
    
    # ========== COMPONENT BREAKDOWN ==========
    components = Column(JSON)
    """
    Example components structure:
    {
        "workload_score": 65,
        "task_score": 18,
        "time_score": 22,
        "meeting_score": 15,
        "pattern_score": 10,
        "sentiment_score": -0.45,
        "sentiment_adjustment": 8
    }
    """
    
    # ========== INSIGHTS ==========
    insights = Column(JSON)
    """
    Example insights structure:
    {
        "primary_issues": [
            "High task load",
            "Excessive work hours"
        ],
        "stress_indicators": [
            "overwhelmed",
            "tired"
        ],
        "burnout_signals": {
            "emotional_exhaustion": true,
            "overwhelm": true,
            "sleep_concerns": false
        }
    }
    """
    
    # ========== TREND DATA ==========
    previous_score = Column(Integer)  # Previous day's score
    score_change = Column(Integer)  # Change from previous day
    trend_direction = Column(String(20))  # "improving", "stable", "worsening"
    days_in_current_level = Column(Integer, default=0)  # Days in GREEN/YELLOW/RED
    
    # ========== METADATA ==========
    analysis_version = Column(String(20))  # Version of analysis algorithm used
    
    # ========== INDEXES FOR QUERIES ==========
    __table_args__ = (
        # For querying user's history
        Index('idx_user_date', 'user_id', 'analyzed_at'),
        # For finding patterns by level
        Index('idx_user_level', 'user_id', 'level'),
        # For trend analysis
        Index('idx_analyzed_at', 'analyzed_at'),
    )
    
    def __repr__(self):
        return f"<BurnoutAnalysis(user_id={self.user_id}, score={self.final_score}, level='{self.level}', date={self.analyzed_at})>"


def init_burnout_analysis_table(engine):
    """
    Initialize the burnout_analyses table.
    
    Usage:
        from sqlalchemy import create_engine
        engine = create_engine('postgresql://...')
        init_burnout_analysis_table(engine)
    """
    Base.metadata.create_all(engine)
    print("✅ burnout_analyses table created!")


# ============================================================================
# HELPER FUNCTIONS FOR QUERYING
# ============================================================================

def store_burnout_analysis(
    session,
    user_id: int,
    final_score: int,
    level: str,
    metrics: dict,
    components: dict = None,
    insights: dict = None,
    previous_score: int = None,
    days_in_current_level: int = 0,
    analysis_version: str = "1.0.0"
):
    """
    Store a burnout analysis result.
    
    Args:
        session: SQLAlchemy session
        user_id: User ID
        final_score: Burnout score (0-100)
        level: GREEN/YELLOW/RED
        metrics: Dictionary of raw metrics
        components: Score breakdown
        insights: Analysis insights
        previous_score: Previous day's score
        days_in_current_level: Days in current level
        analysis_version: Version of algorithm
    
    Returns:
        Created BurnoutAnalysis object
    """
    # Calculate change
    score_change = None
    trend_direction = None
    
    if previous_score is not None:
        score_change = final_score - previous_score
        if abs(score_change) <= 5:
            trend_direction = "stable"
        elif score_change > 5:
            trend_direction = "worsening"
        else:
            trend_direction = "improving"
    
    # Create record
    analysis = BurnoutAnalysis(
        user_id=user_id,
        analyzed_at=datetime.utcnow(),
        final_score=final_score,
        level=level,
        metrics=metrics,
        components=components or {},
        insights=insights or {},
        previous_score=previous_score,
        score_change=score_change,
        trend_direction=trend_direction,
        days_in_current_level=days_in_current_level,
        analysis_version=analysis_version
    )
    
    session.add(analysis)
    session.commit()
    session.refresh(analysis)
    
    return analysis


def get_user_history(session, user_id: int, days: int = 30):
    """
    Get user's burnout history for the last N days.
    
    Args:
        session: SQLAlchemy session
        user_id: User ID
        days: Number of days to retrieve
    
    Returns:
        List of BurnoutAnalysis objects
    """
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    return session.query(BurnoutAnalysis).filter(
        BurnoutAnalysis.user_id == user_id,
        BurnoutAnalysis.analyzed_at >= cutoff_date
    ).order_by(BurnoutAnalysis.analyzed_at.asc()).all()


def get_latest_analysis(session, user_id: int):
    """
    Get user's most recent burnout analysis.
    
    Args:
        session: SQLAlchemy session
        user_id: User ID
    
    Returns:
        Most recent BurnoutAnalysis object or None
    """
    return session.query(BurnoutAnalysis).filter(
        BurnoutAnalysis.user_id == user_id
    ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()


def get_analyses_by_level(session, user_id: int, level: str, days: int = 30):
    """
    Get all analyses where user was in a specific level.
    
    Args:
        session: SQLAlchemy session
        user_id: User ID
        level: GREEN, YELLOW, or RED
        days: Number of days to look back
    
    Returns:
        List of BurnoutAnalysis objects
    """
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    return session.query(BurnoutAnalysis).filter(
        BurnoutAnalysis.user_id == user_id,
        BurnoutAnalysis.level == level,
        BurnoutAnalysis.analyzed_at >= cutoff_date
    ).order_by(BurnoutAnalysis.analyzed_at.asc()).all()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example of using the burnout analysis history table.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    print("="*80)
    print("BURNOUT ANALYSIS HISTORY - EXAMPLE")
    print("="*80)
    
    # Setup database
    engine = create_engine('sqlite:///burnout_history.db', echo=False)
    init_burnout_analysis_table(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Example 1: Store an analysis
    print("\n📝 Storing burnout analysis...")
    
    analysis = store_burnout_analysis(
        session=session,
        user_id=1,
        final_score=65,
        level="YELLOW",
        metrics={
            "total_active_tasks": 12,
            "overdue_tasks": 3,
            "work_hours_today": 9,
            "meetings_today": 5,
            "completion_rate": 0.75
        },
        components={
            "workload_score": 60,
            "sentiment_adjustment": 5
        },
        insights={
            "primary_issues": ["High task load", "Many meetings"]
        },
        previous_score=58
    )
    
    print(f"✅ Stored analysis ID: {analysis.id}")
    print(f"   Score: {analysis.final_score}")
    print(f"   Level: {analysis.level}")
    print(f"   Change: {analysis.score_change:+d} ({analysis.trend_direction})")
    
    # Example 2: Retrieve history
    print("\n📊 Retrieving user history...")
    
    history = get_user_history(session, user_id=1, days=30)
    
    print(f"✅ Found {len(history)} analyses")
    for h in history:
        print(f"   {h.analyzed_at.date()}: Score {h.final_score} ({h.level})")
    
    # Example 3: Get latest
    print("\n📍 Getting latest analysis...")
    
    latest = get_latest_analysis(session, user_id=1)
    
    if latest:
        print(f"✅ Latest analysis:")
        print(f"   Date: {latest.analyzed_at}")
        print(f"   Score: {latest.final_score}")
        print(f"   Level: {latest.level}")
    
    print("\n" + "="*80)
    print("✅ Burnout Analysis History Table Working!")
    print("="*80)
    
    session.close()