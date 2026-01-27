"""
Workload Analyzer - Rule-Based Burnout Score Calculator
========================================================

This module calculates workload-based burnout scores (0-100) from quantitative metrics.
The score is composed of four main components:
1. Task Overload Score (max 30 points)
2. Time Overload Score (max 30 points)
3. Meeting Overload Score (max 25 points)
4. Pattern Score (max 15 points)

Author: Sentry AI Team
Date: 2025
"""

from dataclasses import dataclass
from typing import Dict, Tuple
from datetime import datetime


@dataclass
class UserMetrics:
    """
    Data class holding all quantitative metrics for a user.
    These metrics are fetched from the database.
    """
    # Task metrics
    total_active_tasks: int = 0
    overdue_tasks: int = 0
    tasks_due_this_week: int = 0
    completion_rate: float = 1.0  # 0.0 to 1.0
    average_task_duration: float = 0.0  # hours
    
    # Time metrics
    work_hours_today: float = 0.0
    work_hours_this_week: float = 0.0
    weekend_work_sessions: int = 0  # last month
    late_night_sessions: int = 0  # after 10pm, last week
    consecutive_work_days: int = 0
    
    # Meeting metrics
    meetings_today: int = 0
    meetings_this_week: int = 0
    total_meeting_hours_today: float = 0.0
    back_to_back_meetings: int = 0
    average_meeting_duration: float = 0.0  # minutes
    
    # Pattern metrics
    days_without_breaks: int = 0  # last 14 days
    task_postponement_count: int = 0  # last week
    workload_trend: float = 0.0  # -1 to +1 (decreasing to increasing)


@dataclass
class WorkloadScoreBreakdown:
    """Detailed breakdown of workload score components"""
    task_score: int
    time_score: int
    meeting_score: int
    pattern_score: int
    total_score: int
    
    # Sub-components for detailed analysis
    task_details: Dict[str, int]
    time_details: Dict[str, int]
    meeting_details: Dict[str, int]
    pattern_details: Dict[str, int]
    
    # Insights
    primary_issues: list[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "task_score": self.task_score,
            "time_score": self.time_score,
            "meeting_score": self.meeting_score,
            "pattern_score": self.pattern_score,
            "total_score": self.total_score,
            "breakdown": {
                "tasks": self.task_details,
                "time": self.time_details,
                "meetings": self.meeting_details,
                "patterns": self.pattern_details
            },
            "primary_issues": self.primary_issues
        }


class WorkloadAnalyzer:
    """
    Calculates workload-based burnout score using rule-based logic.
    
    The analyzer uses thresholds and scoring rules to evaluate:
    - Task overload (active tasks, overdue tasks, completion rate)
    - Time overload (daily/weekly hours, off-hours work)
    - Meeting overload (meeting count, duration, back-to-back)
    - Negative patterns (lack of breaks, consecutive work days, trends)
    
    Final score ranges from 0-100:
    - 0-35: GREEN (Healthy workload)
    - 36-65: YELLOW (Moderate risk)
    - 66-100: RED (High burnout risk)
    """
    
    # Score thresholds for each component
    MAX_TASK_SCORE = 30
    MAX_TIME_SCORE = 30
    MAX_MEETING_SCORE = 25
    MAX_PATTERN_SCORE = 15
    MAX_TOTAL_SCORE = 100
    
    def __init__(self):
        """Initialize the WorkloadAnalyzer"""
        pass
    
    def calculate_score(self, metrics: UserMetrics) -> WorkloadScoreBreakdown:
        """
        Calculate complete workload score from user metrics.
        
        Args:
            metrics: UserMetrics object containing all quantitative data
            
        Returns:
            WorkloadScoreBreakdown with detailed scoring information
        """
        # Calculate each component
        task_score, task_details = self._calculate_task_score(metrics)
        time_score, time_details = self._calculate_time_score(metrics)
        meeting_score, meeting_details = self._calculate_meeting_score(metrics)
        pattern_score, pattern_details = self._calculate_pattern_score(metrics)
        
        # Calculate total
        total_score = task_score + time_score + meeting_score + pattern_score
        
        # Cap at maximum
        total_score = min(total_score, self.MAX_TOTAL_SCORE)
        
        # Identify primary issues (components contributing most)
        primary_issues = self._identify_primary_issues(
            task_score, time_score, meeting_score, pattern_score
        )
        
        return WorkloadScoreBreakdown(
            task_score=task_score,
            time_score=time_score,
            meeting_score=meeting_score,
            pattern_score=pattern_score,
            total_score=total_score,
            task_details=task_details,
            time_details=time_details,
            meeting_details=meeting_details,
            pattern_details=pattern_details,
            primary_issues=primary_issues
        )
    
    def _calculate_task_score(self, metrics: UserMetrics) -> Tuple[int, Dict]:
        """
        Calculate task overload score (max 30 points).
        
        Components:
        - Active tasks (0-10 points)
        - Overdue tasks (0-12 points)
        - Completion rate (0-8 points)
        """
        score = 0
        details = {}
        
        # A. Active Tasks Component (0-10 points)
        active_tasks = metrics.total_active_tasks
        if active_tasks <= 5:
            active_score = 0
        elif active_tasks <= 8:
            active_score = 3
        elif active_tasks <= 12:
            active_score = 6
        else:
            active_score = 10
        
        score += active_score
        details['active_tasks'] = active_score
        
        # B. Overdue Tasks Component (0-12 points)
        overdue = metrics.overdue_tasks
        if overdue == 0:
            overdue_score = 0
        elif overdue == 1:
            overdue_score = 3
        elif overdue <= 3:
            overdue_score = 6
        elif overdue <= 5:
            overdue_score = 9
        else:
            overdue_score = 12
        
        score += overdue_score
        details['overdue_tasks'] = overdue_score
        
        # C. Completion Rate Component (0-8 points)
        completion = metrics.completion_rate
        if completion >= 0.8:
            completion_score = 0
        elif completion >= 0.6:
            completion_score = 3
        elif completion >= 0.4:
            completion_score = 5
        else:
            completion_score = 8
        
        score += completion_score
        details['completion_rate'] = completion_score
        
        # Cap at maximum
        score = min(score, self.MAX_TASK_SCORE)
        
        return score, details
    
    def _calculate_time_score(self, metrics: UserMetrics) -> Tuple[int, Dict]:
        """
        Calculate time overload score (max 30 points).
        
        Components:
        - Daily work hours (0-10 points)
        - Weekly work hours (0-10 points)
        - Weekend work (0-5 points)
        - Late night work (0-5 points)
        """
        score = 0
        details = {}
        
        # A. Daily Work Hours Component (0-10 points)
        daily_hours = metrics.work_hours_today
        if daily_hours <= 8:
            daily_score = 0
        elif daily_hours <= 10:
            daily_score = 4
        elif daily_hours <= 12:
            daily_score = 7
        else:
            daily_score = 10
        
        score += daily_score
        details['daily_hours'] = daily_score
        
        # B. Weekly Work Hours Component (0-10 points)
        weekly_hours = metrics.work_hours_this_week
        if weekly_hours <= 40:
            weekly_score = 0
        elif weekly_hours <= 50:
            weekly_score = 4
        elif weekly_hours <= 60:
            weekly_score = 7
        else:
            weekly_score = 10
        
        score += weekly_score
        details['weekly_hours'] = weekly_score
        
        # C. Weekend Work Component (0-5 points)
        weekend_sessions = metrics.weekend_work_sessions
        if weekend_sessions == 0:
            weekend_score = 0
        elif weekend_sessions <= 2:
            weekend_score = 2
        elif weekend_sessions <= 4:
            weekend_score = 4
        else:
            weekend_score = 5
        
        score += weekend_score
        details['weekend_work'] = weekend_score
        
        # D. Late Night Work Component (0-5 points)
        late_night = metrics.late_night_sessions
        if late_night == 0:
            late_night_score = 0
        elif late_night <= 2:
            late_night_score = 2
        elif late_night <= 4:
            late_night_score = 4
        else:
            late_night_score = 5
        
        score += late_night_score
        details['late_night_work'] = late_night_score
        
        # Cap at maximum
        score = min(score, self.MAX_TIME_SCORE)
        
        return score, details
    
    def _calculate_meeting_score(self, metrics: UserMetrics) -> Tuple[int, Dict]:
        """
        Calculate meeting overload score (max 25 points).
        
        Components:
        - Daily meeting count (0-10 points)
        - Meeting duration (0-8 points)
        - Back-to-back meetings (0-7 points)
        """
        score = 0
        details = {}
        
        # A. Daily Meeting Count (0-10 points)
        meeting_count = metrics.meetings_today
        if meeting_count <= 3:
            count_score = 0
        elif meeting_count <= 5:
            count_score = 4
        elif meeting_count <= 7:
            count_score = 7
        else:
            count_score = 10
        
        score += count_score
        details['meeting_count'] = count_score
        
        # B. Meeting Duration (0-8 points)
        meeting_hours = metrics.total_meeting_hours_today
        if meeting_hours <= 2:
            duration_score = 0
        elif meeting_hours <= 4:
            duration_score = 3
        elif meeting_hours <= 6:
            duration_score = 6
        else:
            duration_score = 8
        
        score += duration_score
        details['meeting_duration'] = duration_score
        
        # C. Back-to-Back Meetings (0-7 points)
        back_to_back = metrics.back_to_back_meetings
        if back_to_back == 0:
            b2b_score = 0
        elif back_to_back <= 2:
            b2b_score = 3
        elif back_to_back <= 4:
            b2b_score = 5
        else:
            b2b_score = 7
        
        score += b2b_score
        details['back_to_back'] = b2b_score
        
        # Cap at maximum
        score = min(score, self.MAX_MEETING_SCORE)
        
        return score, details
    
    def _calculate_pattern_score(self, metrics: UserMetrics) -> Tuple[int, Dict]:
        """
        Calculate pattern score (max 15 points).
        
        Components:
        - Days without breaks (0-7 points)
        - Consecutive work days (0-5 points)
        - Workload trend (0-3 points)
        """
        score = 0
        details = {}
        
        # A. Break Deficiency (0-7 points)
        no_breaks = metrics.days_without_breaks
        if no_breaks <= 2:
            breaks_score = 0
        elif no_breaks <= 5:
            breaks_score = 3
        elif no_breaks <= 10:
            breaks_score = 5
        else:
            breaks_score = 7
        
        score += breaks_score
        details['no_breaks'] = breaks_score
        
        # B. Consecutive Work Days (0-5 points)
        consecutive = metrics.consecutive_work_days
        if consecutive <= 5:
            consecutive_score = 0
        elif consecutive <= 10:
            consecutive_score = 2
        elif consecutive <= 15:
            consecutive_score = 4
        else:
            consecutive_score = 5
        
        score += consecutive_score
        details['consecutive_days'] = consecutive_score
        
        # C. Workload Trend (0-3 points)
        trend = metrics.workload_trend
        if trend < 0:
            trend_score = 0  # Improving
        elif trend <= 0.3:
            trend_score = 1  # Stable
        elif trend <= 0.7:
            trend_score = 2  # Increasing
        else:
            trend_score = 3  # Rapidly increasing
        
        score += trend_score
        details['workload_trend'] = trend_score
        
        # Cap at maximum
        score = min(score, self.MAX_PATTERN_SCORE)
        
        return score, details
    
    def _identify_primary_issues(
        self, 
        task_score: int, 
        time_score: int, 
        meeting_score: int, 
        pattern_score: int
    ) -> list[str]:
        """
        Identify the top contributing factors to workload.
        
        Returns list of primary issues in order of severity.
        """
        issues = []
        scores = [
            (task_score, "High task load", self.MAX_TASK_SCORE),
            (time_score, "Excessive work hours", self.MAX_TIME_SCORE),
            (meeting_score, "Meeting overload", self.MAX_MEETING_SCORE),
            (pattern_score, "Unhealthy work patterns", self.MAX_PATTERN_SCORE)
        ]
        
        # Calculate percentage of maximum for each component
        percentages = [
            (score / max_score if max_score > 0 else 0, label) 
            for score, label, max_score in scores
        ]
        
        # Sort by percentage (highest first)
        percentages.sort(reverse=True, key=lambda x: x[0])
        
        # Add issues that are above 40% of their maximum
        for percentage, label in percentages:
            if percentage >= 0.4:  # 40% threshold
                issues.append(f"{label} ({int(percentage * 100)}% of max)")
        
        return issues if issues else ["Workload within normal range"]
    
    def get_level(self, score: int) -> Tuple[str, str, str]:
        """
        Determine burnout risk level from score.
        
        Args:
            score: Workload score (0-100)
            
        Returns:
            Tuple of (level, status, color_hex)
        """
        if score < 35:
            return ("GREEN", "Healthy workload", "#4CAF50")
        elif score < 65:
            return ("YELLOW", "At risk - Monitor closely", "#FFC107")
        else:
            return ("RED", "High risk - Take action now", "#F44336")


# Example usage and testing
if __name__ == "__main__":
    """
    Example usage of WorkloadAnalyzer with different scenarios
    """
    analyzer = WorkloadAnalyzer()
    
    print("=" * 70)
    print("WORKLOAD ANALYZER - TEST SCENARIOS")
    print("=" * 70)
    
    # Scenario 1: Healthy User
    print("\n📗 SCENARIO 1: Healthy User")
    print("-" * 70)
    healthy_metrics = UserMetrics(
        total_active_tasks=5,
        overdue_tasks=0,
        completion_rate=0.9,
        work_hours_today=7,
        work_hours_this_week=35,
        meetings_today=2,
        total_meeting_hours_today=1.5,
        days_without_breaks=1
    )
    
    result = analyzer.calculate_score(healthy_metrics)
    level, status, color = analyzer.get_level(result.total_score)
    
    print(f"Total Score: {result.total_score}/100")
    print(f"Level: {level} - {status}")
    print(f"Breakdown:")
    print(f"  - Tasks: {result.task_score}/{analyzer.MAX_TASK_SCORE}")
    print(f"  - Time: {result.time_score}/{analyzer.MAX_TIME_SCORE}")
    print(f"  - Meetings: {result.meeting_score}/{analyzer.MAX_MEETING_SCORE}")
    print(f"  - Patterns: {result.pattern_score}/{analyzer.MAX_PATTERN_SCORE}")
    print(f"Primary Issues: {', '.join(result.primary_issues)}")
    
    # Scenario 2: Moderate Risk User
    print("\n📙 SCENARIO 2: Moderate Risk User")
    print("-" * 70)
    moderate_metrics = UserMetrics(
        total_active_tasks=10,
        overdue_tasks=2,
        completion_rate=0.65,
        work_hours_today=10,
        work_hours_this_week=48,
        weekend_work_sessions=2,
        meetings_today=5,
        total_meeting_hours_today=3.5,
        back_to_back_meetings=2,
        days_without_breaks=6
    )
    
    result = analyzer.calculate_score(moderate_metrics)
    level, status, color = analyzer.get_level(result.total_score)
    
    print(f"Total Score: {result.total_score}/100")
    print(f"Level: {level} - {status}")
    print(f"Breakdown:")
    print(f"  - Tasks: {result.task_score}/{analyzer.MAX_TASK_SCORE}")
    print(f"  - Time: {result.time_score}/{analyzer.MAX_TIME_SCORE}")
    print(f"  - Meetings: {result.meeting_score}/{analyzer.MAX_MEETING_SCORE}")
    print(f"  - Patterns: {result.pattern_score}/{analyzer.MAX_PATTERN_SCORE}")
    print(f"Primary Issues: {', '.join(result.primary_issues)}")
    
    # Scenario 3: High Risk User
    print("\n📕 SCENARIO 3: High Risk User (Burnout Danger)")
    print("-" * 70)
    high_risk_metrics = UserMetrics(
        total_active_tasks=15,
        overdue_tasks=6,
        completion_rate=0.35,
        work_hours_today=12,
        work_hours_this_week=65,
        weekend_work_sessions=5,
        late_night_sessions=6,
        meetings_today=8,
        total_meeting_hours_today=6.5,
        back_to_back_meetings=5,
        days_without_breaks=12,
        consecutive_work_days=18,
        workload_trend=0.8
    )
    
    result = analyzer.calculate_score(high_risk_metrics)
    level, status, color = analyzer.get_level(result.total_score)
    
    print(f"Total Score: {result.total_score}/100")
    print(f"Level: {level} - {status}")
    print(f"Breakdown:")
    print(f"  - Tasks: {result.task_score}/{analyzer.MAX_TASK_SCORE}")
    print(f"  - Time: {result.time_score}/{analyzer.MAX_TIME_SCORE}")
    print(f"  - Meetings: {result.meeting_score}/{analyzer.MAX_MEETING_SCORE}")
    print(f"  - Patterns: {result.pattern_score}/{analyzer.MAX_PATTERN_SCORE}")
    print(f"Primary Issues:")
    for issue in result.primary_issues:
        print(f"  ⚠️  {issue}")
    
    print("\n" + "=" * 70)
    print("Testing complete! ✅")
    print("=" * 70)