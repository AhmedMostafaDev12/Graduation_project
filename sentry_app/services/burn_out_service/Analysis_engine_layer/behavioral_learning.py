"""
Behavioral Learning System - Real Implementation
=================================================

This module contains the actual algorithms for learning user patterns
from historical burnout analysis data.

Integrates with:
- WorkloadAnalyzer (gets workload metrics)
- BurnoutEngine (gets historical burnout scores)
- User Profile (stores learned patterns)

Author: Sentry AI Team
Date: 2025
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass
import statistics
from collections import Counter


# ============================================================================
# DATA MODELS FOR ANALYSIS
# ============================================================================

@dataclass
class DailySnapshot:
    """Single day's worth of user data"""
    date: date
    total_active_tasks: int
    overdue_tasks: int
    work_hours: float
    meetings_count: int
    meeting_hours: float
    back_to_back_meetings: int
    completion_rate: float
    burnout_score: int
    burnout_level: str  # GREEN/YELLOW/RED


@dataclass
class WorkPatterns:
    """Calculated work patterns from historical data"""
    # Averages
    avg_tasks: float
    avg_hours: float
    avg_meetings: float
    avg_meeting_hours: float
    avg_completion_rate: float
    
    # Baselines (healthy normal - median when in GREEN)
    baseline_score: float
    baseline_tasks: float
    baseline_hours: float
    baseline_meetings: float
    
    # Peak productivity
    peak_hour: int  # 0-23
    best_day: str  # Monday-Friday
    worst_day: str
    
    # Patterns
    workload_trend: str  # "increasing", "stable", "decreasing"
    stress_triggers: List[str]


# ============================================================================
# BEHAVIORAL PATTERN ANALYZER
# ============================================================================

class BehavioralPatternAnalyzer:
    """
    Analyzes historical user data to learn behavioral patterns.
    
    This is the REAL implementation that replaces the dummy function.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize analyzer with database session.
        
        Args:
            db_session: SQLAlchemy session for querying history
        """
        self.db = db_session
    
    def calculate_work_patterns(
        self, 
        user_id: int, 
        days: int = 30
    ) -> Dict:
        """
        Calculate comprehensive work patterns from historical data.
        
        This is the REAL implementation that analyzes actual burnout history.
        
        Args:
            user_id: User ID
            days: Number of days to analyze (default 30)
            
        Returns:
            Dictionary with all calculated patterns
        """
        # Get historical data
        snapshots = self._fetch_historical_data(user_id, days)
        
        if not snapshots:
            # No history yet - return None/defaults
            return self._get_default_patterns()
        
        # Calculate patterns
        patterns = WorkPatterns(
            avg_tasks=self._calculate_average(snapshots, 'total_active_tasks'),
            avg_hours=self._calculate_average(snapshots, 'work_hours'),
            avg_meetings=self._calculate_average(snapshots, 'meetings_count'),
            avg_meeting_hours=self._calculate_average(snapshots, 'meeting_hours'),
            avg_completion_rate=self._calculate_average(snapshots, 'completion_rate'),
            
            baseline_score=self._calculate_baseline_score(snapshots),
            baseline_tasks=self._calculate_baseline_metric(snapshots, 'total_active_tasks'),
            baseline_hours=self._calculate_baseline_metric(snapshots, 'work_hours'),
            baseline_meetings=self._calculate_baseline_metric(snapshots, 'meetings_count'),
            
            peak_hour=self._identify_peak_productivity_hour(user_id, days),
            best_day=self._identify_best_day(snapshots),
            worst_day=self._identify_worst_day(snapshots),
            
            workload_trend=self._calculate_trend(snapshots),
            stress_triggers=self._identify_stress_triggers(snapshots)
        )
        
        # Convert to dictionary
        return {
            'avg_tasks': patterns.avg_tasks,
            'avg_hours': patterns.avg_hours,
            'avg_meetings': patterns.avg_meetings,
            'avg_meeting_hours': patterns.avg_meeting_hours,
            'completion_rate': patterns.avg_completion_rate,
            'baseline_score': patterns.baseline_score,
            'baseline_tasks': patterns.baseline_tasks,
            'baseline_hours': patterns.baseline_hours,
            'baseline_meetings': patterns.baseline_meetings,
            'peak_hour': patterns.peak_hour,
            'best_day': patterns.best_day,
            'worst_day': patterns.worst_day,
            'workload_trend': patterns.workload_trend,
            'stress_triggers': patterns.stress_triggers
        }
    
    def _fetch_historical_data(
        self, 
        user_id: int, 
        days: int
    ) -> List[DailySnapshot]:
        """
        Fetch historical burnout analysis data.
        
        This queries the burnout_analyses table where daily snapshots are stored.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            List of daily snapshots
        """
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Query burnout_analyses table
        # NOTE: This assumes you have a burnout_analyses table
        # If you don't have this table yet, you'll need to create it
        # to store daily burnout analysis results
        
        try:
            # Import the model from the user_profile folder
            from sentry_app.services.burn_out_service.user_profile.burnout_model import BurnoutAnalysis

            results = self.db.query(BurnoutAnalysis).filter(
                and_(
                    BurnoutAnalysis.user_id == user_id,
                    BurnoutAnalysis.analyzed_at >= start_date,
                    BurnoutAnalysis.analyzed_at <= end_date
                )
            ).order_by(BurnoutAnalysis.analyzed_at).all()
            
            # Convert to DailySnapshot objects
            snapshots = []
            for result in results:
                snapshot = DailySnapshot(
                    date=result.analyzed_at.date() if isinstance(result.analyzed_at, datetime) else result.analyzed_at,
                    total_active_tasks=result.metrics.get('total_active_tasks', 0),
                    overdue_tasks=result.metrics.get('overdue_tasks', 0),
                    work_hours=result.metrics.get('work_hours_today', 0),
                    meetings_count=result.metrics.get('meetings_today', 0),
                    meeting_hours=result.metrics.get('total_meeting_hours_today', 0),
                    back_to_back_meetings=result.metrics.get('back_to_back_meetings', 0),
                    completion_rate=result.metrics.get('completion_rate', 0),
                    burnout_score=result.final_score,
                    burnout_level=result.level
                )
                snapshots.append(snapshot)
            
            return snapshots
            
        except ImportError:
            # Table doesn't exist yet - return empty
            print("⚠️  Warning: burnout_analyses table not found. Using dummy data.")
            return []
    
    def _calculate_average(
        self, 
        snapshots: List[DailySnapshot], 
        field: str
    ) -> float:
        """Calculate average of a field across all snapshots"""
        values = [getattr(s, field) for s in snapshots]
        return statistics.mean(values) if values else 0.0
    
    def _calculate_baseline_score(
        self, 
        snapshots: List[DailySnapshot]
    ) -> float:
        """
        Calculate baseline burnout score.
        
        Baseline = median score when user is in GREEN zone
        This represents their "healthy normal" state.
        """
        green_scores = [
            s.burnout_score 
            for s in snapshots 
            if s.burnout_level == 'GREEN'
        ]
        
        if green_scores:
            return statistics.median(green_scores)
        
        # If never in GREEN, use median of all scores
        all_scores = [s.burnout_score for s in snapshots]
        return statistics.median(all_scores) if all_scores else 0.0
    
    def _calculate_baseline_metric(
        self, 
        snapshots: List[DailySnapshot], 
        field: str
    ) -> float:
        """
        Calculate baseline for a specific metric.
        
        Baseline = median value when user is in GREEN zone
        """
        green_values = [
            getattr(s, field) 
            for s in snapshots 
            if s.burnout_level == 'GREEN'
        ]
        
        if green_values:
            return statistics.median(green_values)
        
        # If never in GREEN, use overall median
        all_values = [getattr(s, field) for s in snapshots]
        return statistics.median(all_values) if all_values else 0.0
    
    def _identify_peak_productivity_hour(
        self, 
        user_id: int, 
        days: int
    ) -> int:
        """
        Identify peak productivity hour.
        
        This would ideally analyze when user completes most tasks.
        For now, using a simplified approach.
        """
        # TODO: Implement real analysis of task completion times
        # This would require tracking when tasks are completed
        # For now, returning a reasonable default (10 AM)
        return 10
    
    def _identify_best_day(self, snapshots: List[DailySnapshot]) -> str:
        """
        Identify day of week with lowest burnout scores.
        """
        if not snapshots:
            return "Tuesday"
        
        # Group by day of week
        day_scores = {}
        for snapshot in snapshots:
            day = snapshot.date.strftime('%A')  # Monday, Tuesday, etc.
            if day not in day_scores:
                day_scores[day] = []
            day_scores[day].append(snapshot.burnout_score)
        
        # Find day with lowest average score
        day_averages = {
            day: statistics.mean(scores) 
            for day, scores in day_scores.items()
        }
        
        return min(day_averages, key=day_averages.get) if day_averages else "Tuesday"
    
    def _identify_worst_day(self, snapshots: List[DailySnapshot]) -> str:
        """
        Identify day of week with highest burnout scores.
        """
        if not snapshots:
            return "Friday"
        
        # Group by day of week
        day_scores = {}
        for snapshot in snapshots:
            day = snapshot.date.strftime('%A')
            if day not in day_scores:
                day_scores[day] = []
            day_scores[day].append(snapshot.burnout_score)
        
        # Find day with highest average score
        day_averages = {
            day: statistics.mean(scores) 
            for day, scores in day_scores.items()
        }
        
        return max(day_averages, key=day_averages.get) if day_averages else "Friday"
    
    def _calculate_trend(self, snapshots: List[DailySnapshot]) -> str:
        """
        Determine if workload is increasing, stable, or decreasing.
        
        Uses linear regression on burnout scores over time.
        """
        if len(snapshots) < 7:
            return "stable"
        
        # Get scores from first half and second half
        mid = len(snapshots) // 2
        first_half = [s.burnout_score for s in snapshots[:mid]]
        second_half = [s.burnout_score for s in snapshots[mid:]]
        
        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)
        
        change = avg_second - avg_first
        
        if change > 10:
            return "increasing"
        elif change < -10:
            return "decreasing"
        else:
            return "stable"
    
    def _identify_stress_triggers(
        self, 
        snapshots: List[DailySnapshot]
    ) -> List[str]:
        """
        Identify patterns that precede burnout spikes.
        
        Looks for conditions that consistently appear before score increases.
        """
        triggers = []
        
        # Analyze what precedes burnout spikes
        for i in range(1, len(snapshots)):
            current = snapshots[i]
            previous = snapshots[i-1]
            
            # Did burnout increase significantly?
            if current.burnout_score - previous.burnout_score >= 15:
                # What happened the day before?
                
                if previous.back_to_back_meetings >= 4:
                    triggers.append("back_to_back_meetings")
                
                if previous.work_hours >= 10:
                    triggers.append("long_work_hours")
                
                if previous.date.weekday() in [5, 6]:  # Weekend
                    triggers.append("weekend_work")
                
                if previous.meetings_count >= 8:
                    triggers.append("excessive_meetings")
                
                if previous.overdue_tasks >= 5:
                    triggers.append("high_overdue_tasks")
        
        # Return most common triggers
        if triggers:
            trigger_counts = Counter(triggers)
            return [t for t, count in trigger_counts.most_common(5)]
        
        return []
    
    def _get_default_patterns(self) -> Dict:
        """
        Return default patterns when no history exists yet.
        """
        return {
            'avg_tasks': None,
            'avg_hours': None,
            'avg_meetings': None,
            'avg_meeting_hours': None,
            'completion_rate': None,
            'baseline_score': None,
            'baseline_tasks': None,
            'baseline_hours': None,
            'baseline_meetings': None,
            'peak_hour': 10,  # Default to 10 AM
            'best_day': 'Tuesday',
            'worst_day': 'Friday',
            'workload_trend': 'stable',
            'stress_triggers': []
        }


# ============================================================================
# INTEGRATION FUNCTION
# ============================================================================

def learn_behavioral_patterns(
    db_session: Session,
    user_id: int,
    days: int = 30
) -> Dict:
    """
    Main entry point for behavioral learning.
    
    This replaces the dummy _calculate_work_patterns function
    in user_profile_service.py
    
    Usage:
        from behavioral_learning import learn_behavioral_patterns
        
        patterns = learn_behavioral_patterns(session, user_id, days=30)
        
        # Update user's behavioral profile with patterns
        behavioral.avg_tasks_per_day = patterns['avg_tasks']
        behavioral.baseline_burnout_score = patterns['baseline_score']
        # ... etc
    
    Args:
        db_session: SQLAlchemy session
        user_id: User ID
        days: Number of days to analyze
        
    Returns:
        Dictionary with all calculated patterns
    """
    analyzer = BehavioralPatternAnalyzer(db_session)
    return analyzer.calculate_work_patterns(user_id, days)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example of how to use the behavioral learning system.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    print("="*80)
    print("BEHAVIORAL LEARNING SYSTEM - REAL IMPLEMENTATION")
    print("="*80)
    
    # Setup
    engine = create_engine('sqlite:///demo.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Analyze user patterns
    print("\n📊 Analyzing user behavioral patterns...")
    
    patterns = learn_behavioral_patterns(
        db_session=session,
        user_id=1,
        days=30
    )
    
    print(f"\n✅ Patterns calculated:")
    print(f"   Average tasks/day: {patterns['avg_tasks']}")
    print(f"   Average work hours: {patterns['avg_hours']}")
    print(f"   Average meetings: {patterns['avg_meetings']}")
    print(f"   Baseline burnout: {patterns['baseline_score']}")
    print(f"   Peak productivity: {patterns['peak_hour']}:00")
    print(f"   Best day: {patterns['best_day']}")
    print(f"   Workload trend: {patterns['workload_trend']}")
    
    if patterns['stress_triggers']:
        print(f"\n⚠️  Stress triggers identified:")
        for trigger in patterns['stress_triggers']:
            print(f"      • {trigger}")
    
    print("\n" + "="*80)
    print("✅ Behavioral Learning System Ready!")
    print("="*80)
    
    session.close()