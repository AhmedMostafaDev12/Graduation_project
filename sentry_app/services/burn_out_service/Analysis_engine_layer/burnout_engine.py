"""
Burnout Engine - Fusion Layer for Complete Burnout Analysis
============================================================

This module combines outputs from:
1. WorkloadAnalyzer (rule-based quantitative analysis)
2. SentimentAnalyzer (LLM-based qualitative analysis)

To produce a comprehensive burnout assessment with:
- Final burnout score (0-100)
- Risk level (GREEN/YELLOW/RED)
- Component breakdowns
- Insights and recommendations
- Historical trends
- Complete data for Alert Detection Layer

Author: Sentry AI Team
Date: 2025
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import json

# Import from our other modules
from .Workload_analyzer import WorkloadAnalyzer, UserMetrics, WorkloadScoreBreakdown
from .sentiment_analyzer import SentimentAnalyzer, QualitativeData, SentimentAnalysisResult


# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class BurnoutLevel(str, Enum):
    """Burnout risk levels"""
    GREEN = "GREEN"    # 0-34: Healthy
    YELLOW = "YELLOW"  # 35-64: At Risk
    RED = "RED"        # 65-100: High Risk


class AlertPriority(str, Enum):
    """Alert priority levels for detection layer"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================================
# DATA MODELS FOR OUTPUT
# ============================================================================

@dataclass
class BurnoutComponents:
    """
    Detailed breakdown of burnout score components.
    This helps users understand what's contributing to their score.
    """
    # Workload components (from WorkloadAnalyzer)
    workload_score: int
    task_score: int
    time_score: int
    meeting_score: int
    pattern_score: int
    
    # Sentiment components (from SentimentAnalyzer)
    sentiment_score: float
    sentiment_adjustment: int
    
    # Contribution percentages
    workload_contribution: float  # 0-100
    sentiment_contribution: float  # 0-100
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class BurnoutInsights:
    """
    Actionable insights about burnout factors.
    These feed directly into the Alert Detection layer.
    """
    primary_issues: List[str]  # Top 3-5 issues (e.g., "High meeting load")
    stress_indicators: List[str]  # From sentiment analysis
    burnout_signals: Dict[str, bool]  # Specific signals detected
    key_concerns: List[str]  # Human-readable concerns
    confidence_level: int  # 0-100 (how confident we are)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class BurnoutRecommendations:
    """
    Actionable recommendations for the user.
    Alert Detection layer uses these to generate specific alerts.
    """
    immediate_actions: List[str]  # Actions to take now
    preventive_measures: List[str]  # Long-term improvements
    recovery_suggestions: List[str]  # If already burned out
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class BurnoutTrend:
    """
    Historical trend information.
    Alert Detection layer uses this to detect worsening/improving patterns.
    """
    current_score: int
    previous_score: Optional[int]
    score_change: Optional[int]  # Positive = worse, negative = better
    trend_direction: str  # "improving", "stable", "worsening", "unknown"
    days_in_current_level: int  # How long in GREEN/YELLOW/RED
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class AlertTriggers:
    """
    Specific triggers for the Alert Detection layer.
    This tells the detection layer WHAT to alert about.
    """
    # Threshold-based triggers
    high_burnout_score: bool  # Score >= 65
    moderate_burnout_score: bool  # Score 35-64
    workload_overload: bool  # Workload score > 60
    negative_sentiment: bool  # Sentiment < -0.5
    
    # Pattern-based triggers
    score_spike: bool  # Score increased > 15 points
    prolonged_yellow: bool  # In YELLOW for > 7 days
    prolonged_red: bool  # In RED for > 3 days
    
    # Signal-based triggers
    emotional_exhaustion: bool
    overwhelm: bool
    sleep_concerns: bool
    health_concerns: bool
    
    # Urgency level
    alert_priority: AlertPriority
    requires_immediate_action: bool
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class BurnoutAnalysisResult:
    """
    Complete burnout analysis result.
    This is the main output that feeds into the Alert Detection Layer.
    """
    # Core results
    final_score: int  # 0-100
    level: BurnoutLevel  # GREEN/YELLOW/RED
    status_message: str  # User-friendly message
    color: str  # Hex color for UI
    
    # Detailed breakdowns
    components: BurnoutComponents
    insights: BurnoutInsights
    recommendations: BurnoutRecommendations
    trend: BurnoutTrend
    
    # Alert triggers (for next layer)
    alert_triggers: AlertTriggers
    
    # Metadata
    analyzed_at: datetime
    user_id: int
    analysis_version: str  # For tracking algorithm changes
    
    def to_dict(self) -> Dict:
        """
        Convert to dictionary for JSON serialization.
        This is the format that goes to the Alert Detection Layer.
        """
        return {
            "final_score": self.final_score,
            "level": self.level.value,
            "status_message": self.status_message,
            "color": self.color,
            "components": self.components.to_dict(),
            "insights": self.insights.to_dict(),
            "recommendations": self.recommendations.to_dict(),
            "trend": self.trend.to_dict(),
            "alert_triggers": self.alert_triggers.to_dict(),
            "analyzed_at": self.analyzed_at.isoformat(),
            "user_id": self.user_id,
            "analysis_version": self.analysis_version
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


# ============================================================================
# BURNOUT ENGINE
# ============================================================================

class BurnoutEngine:
    """
    Fusion engine that combines workload and sentiment analysis
    into comprehensive burnout assessment.
    
    Responsibilities:
    1. Fuse quantitative (workload) + qualitative (sentiment) scores
    2. Generate insights and recommendations
    3. Track historical trends
    4. Determine alert triggers
    5. Output structured data for Alert Detection Layer
    """
    
    VERSION = "1.0.0"
    
    # Score thresholds
    GREEN_THRESHOLD = 35
    YELLOW_THRESHOLD = 65
    
    def __init__(self):
        """Initialize the Burnout Engine"""
        self.workload_analyzer = WorkloadAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def analyze(
        self,
        user_id: int,
        quantitative_metrics: UserMetrics,
        qualitative_data: QualitativeData,
        previous_score: Optional[int] = None,
        days_in_current_level: int = 0
    ) -> BurnoutAnalysisResult:
        """
        Perform complete burnout analysis.
        
        Args:
            user_id: User identifier
            quantitative_metrics: Workload metrics
            qualitative_data: Text data for sentiment analysis
            previous_score: Previous burnout score (for trend analysis)
            days_in_current_level: Days spent in current level
            
        Returns:
            Complete BurnoutAnalysisResult ready for Alert Detection Layer
        """
        # Step 1: Workload Analysis
        workload_result = self.workload_analyzer.calculate_score(quantitative_metrics)
        
        # Step 2: Sentiment Analysis
        sentiment_result = self.sentiment_analyzer.analyze(qualitative_data)
        
        # Step 3: Fusion - Calculate final score
        final_score = self._calculate_final_score(
            workload_result.total_score,
            sentiment_result.sentiment_adjustment
        )
        
        # Step 4: Determine level and status
        level, status_message, color = self._determine_level(final_score)
        
        # Step 5: Create components breakdown
        components = self._create_components(workload_result, sentiment_result, final_score)
        
        # Step 6: Generate insights
        insights = self._generate_insights(workload_result, sentiment_result)
        
        # Step 7: Generate recommendations
        recommendations = self._generate_recommendations(
            level, 
            workload_result, 
            sentiment_result
        )
        
        # Step 8: Calculate trend
        trend = self._calculate_trend(
            final_score, 
            previous_score, 
            level,
            days_in_current_level
        )
        
        # Step 9: Determine alert triggers
        alert_triggers = self._determine_alert_triggers(
            final_score,
            level,
            workload_result,
            sentiment_result,
            trend
        )
        
        # Step 10: Create final result
        result = BurnoutAnalysisResult(
            final_score=final_score,
            level=level,
            status_message=status_message,
            color=color,
            components=components,
            insights=insights,
            recommendations=recommendations,
            trend=trend,
            alert_triggers=alert_triggers,
            analyzed_at=datetime.utcnow(),
            user_id=user_id,
            analysis_version=self.VERSION
        )
        
        return result
    
    def _calculate_final_score(
        self, 
        workload_score: int, 
        sentiment_adjustment: int
    ) -> int:
        """
        Fuse workload score and sentiment adjustment.
        
        Formula: Final = Workload + Sentiment Adjustment
        Clamped to [0, 100]
        """
        final = workload_score + sentiment_adjustment
        return max(0, min(100, final))
    
    def _determine_level(self, score: int) -> Tuple[BurnoutLevel, str, str]:
        """
        Determine burnout level from score.
        
        Returns:
            Tuple of (level, status_message, color_hex)
        """
        if score < self.GREEN_THRESHOLD:
            return (
                BurnoutLevel.GREEN,
                "Healthy workload - Keep up the good work!",
                "#4CAF50"
            )
        elif score < self.YELLOW_THRESHOLD:
            return (
                BurnoutLevel.YELLOW,
                "Moderate risk - Monitor and take preventive action",
                "#FFC107"
            )
        else:
            return (
                BurnoutLevel.RED,
                "High risk - Immediate action needed",
                "#F44336"
            )
    
    def _create_components(
        self,
        workload_result: WorkloadScoreBreakdown,
        sentiment_result: SentimentAnalysisResult,
        final_score: int
    ) -> BurnoutComponents:
        """Create detailed components breakdown"""
        
        # Calculate contribution percentages
        workload_contribution = (workload_result.total_score / final_score * 100) if final_score > 0 else 0
        sentiment_contribution = (abs(sentiment_result.sentiment_adjustment) / final_score * 100) if final_score > 0 else 0
        
        return BurnoutComponents(
            workload_score=workload_result.total_score,
            task_score=workload_result.task_score,
            time_score=workload_result.time_score,
            meeting_score=workload_result.meeting_score,
            pattern_score=workload_result.pattern_score,
            sentiment_score=sentiment_result.sentiment_score,
            sentiment_adjustment=sentiment_result.sentiment_adjustment,
            workload_contribution=round(workload_contribution, 1),
            sentiment_contribution=round(sentiment_contribution, 1)
        )
    
    def _generate_insights(
        self,
        workload_result: WorkloadScoreBreakdown,
        sentiment_result: SentimentAnalysisResult
    ) -> BurnoutInsights:
        """Generate actionable insights"""
        
        # Combine primary issues from both analyzers
        primary_issues = workload_result.primary_issues.copy()
        
        # Add sentiment-based issues
        if sentiment_result.sentiment_score < -0.5:
            primary_issues.insert(0, "Negative emotional state detected")
        
        if sentiment_result.burnout_signals.emotional_exhaustion:
            primary_issues.append("Signs of emotional exhaustion")
        
        return BurnoutInsights(
            primary_issues=primary_issues[:5],  # Top 5
            stress_indicators=sentiment_result.stress_indicators,
            burnout_signals=sentiment_result.burnout_signals.dict(),
            key_concerns=sentiment_result.key_concerns,
            confidence_level=sentiment_result.confidence
        )
    
    def _generate_recommendations(
        self,
        level: BurnoutLevel,
        workload_result: WorkloadScoreBreakdown,
        sentiment_result: SentimentAnalysisResult
    ) -> BurnoutRecommendations:
        """Generate personalized recommendations"""
        
        immediate = []
        preventive = []
        recovery = []
        
        # Level-based recommendations
        if level == BurnoutLevel.RED:
            immediate.append("Cancel non-essential meetings this week")
            immediate.append("Delegate or postpone 3-5 low-priority tasks")
            immediate.append("Block recovery time in your calendar today")
            
            recovery.append("Take a mental health day if possible")
            recovery.append("Speak with your manager about workload")
            recovery.append("Consider professional counseling if stress persists")
        
        elif level == BurnoutLevel.YELLOW:
            immediate.append("Review and reprioritize your task list")
            immediate.append("Schedule breaks between meetings")
            
            preventive.append("Set boundaries for work hours")
            preventive.append("Practice stress management techniques")
        
        else:  # GREEN
            preventive.append("Maintain current healthy work patterns")
            preventive.append("Continue taking regular breaks")
        
        # Workload-specific recommendations
        if workload_result.meeting_score > 15:
            immediate.append("Decline optional meetings this week")
            preventive.append("Batch meetings into specific days")
        
        if workload_result.time_score > 20:
            immediate.append("Stop working after 6 PM today")
            preventive.append("Use time-blocking for focused work")
        
        if workload_result.task_score > 20:
            immediate.append("Move non-urgent tasks to next week")
            preventive.append("Learn to say no to new commitments")
        
        # Sentiment-specific recommendations
        if sentiment_result.burnout_signals.sleep_concerns:
            immediate.append("Prioritize 7-8 hours of sleep tonight")
            recovery.append("Establish a consistent sleep schedule")
        
        if sentiment_result.burnout_signals.emotional_exhaustion:
            immediate.append("Take a 15-minute mindfulness break")
            recovery.append("Engage in activities you enjoy outside work")
        
        if sentiment_result.sentiment_score < -0.6:
            immediate.append("Talk to someone you trust about how you're feeling")
            recovery.append("Consider speaking with a mental health professional")
        
        return BurnoutRecommendations(
            immediate_actions=immediate[:5],  # Top 5
            preventive_measures=preventive[:5],
            recovery_suggestions=recovery[:5]
        )
    
    def _calculate_trend(
        self,
        current_score: int,
        previous_score: Optional[int],
        current_level: BurnoutLevel,
        days_in_level: int
    ) -> BurnoutTrend:
        """Calculate trend information"""
        
        if previous_score is None:
            return BurnoutTrend(
                current_score=current_score,
                previous_score=None,
                score_change=None,
                trend_direction="unknown",
                days_in_current_level=days_in_level
            )
        
        change = current_score - previous_score
        
        # Determine trend direction
        if abs(change) <= 5:
            direction = "stable"
        elif change > 5:
            direction = "worsening"
        else:
            direction = "improving"
        
        return BurnoutTrend(
            current_score=current_score,
            previous_score=previous_score,
            score_change=change,
            trend_direction=direction,
            days_in_current_level=days_in_level
        )
    
    def _determine_alert_triggers(
        self,
        final_score: int,
        level: BurnoutLevel,
        workload_result: WorkloadScoreBreakdown,
        sentiment_result: SentimentAnalysisResult,
        trend: BurnoutTrend
    ) -> AlertTriggers:
        """
        Determine what alerts should be triggered.
        This is THE KEY OUTPUT for the Alert Detection Layer.
        """
        
        # Threshold-based triggers
        high_burnout = final_score >= 65
        moderate_burnout = 35 <= final_score < 65
        workload_overload = workload_result.total_score > 60
        negative_sentiment = sentiment_result.sentiment_score < -0.5
        
        # Pattern-based triggers
        score_spike = (trend.score_change or 0) > 15
        prolonged_yellow = level == BurnoutLevel.YELLOW and trend.days_in_current_level > 7
        prolonged_red = level == BurnoutLevel.RED and trend.days_in_current_level > 3
        
        # Signal-based triggers
        signals = sentiment_result.burnout_signals
        
        # Determine priority
        if high_burnout or prolonged_red or score_spike:
            priority = AlertPriority.CRITICAL
            requires_action = True
        elif moderate_burnout or prolonged_yellow or negative_sentiment:
            priority = AlertPriority.HIGH
            requires_action = True
        elif workload_overload:
            priority = AlertPriority.MEDIUM
            requires_action = False
        else:
            priority = AlertPriority.LOW
            requires_action = False
        
        return AlertTriggers(
            high_burnout_score=high_burnout,
            moderate_burnout_score=moderate_burnout,
            workload_overload=workload_overload,
            negative_sentiment=negative_sentiment,
            score_spike=score_spike,
            prolonged_yellow=prolonged_yellow,
            prolonged_red=prolonged_red,
            emotional_exhaustion=signals.emotional_exhaustion,
            overwhelm=signals.overwhelm,
            sleep_concerns=signals.sleep_concerns,
            health_concerns=signals.health_concerns,
            alert_priority=priority,
            requires_immediate_action=requires_action
        )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Example usage showing complete flow from metrics to alert-ready output.
    """
    
    print("=" * 80)
    print("BURNOUT ENGINE - COMPLETE ANALYSIS FLOW")
    print("=" * 80)
    
    # Initialize engine
    engine = BurnoutEngine()
    
    # ========================================================================
    # SCENARIO 1: Healthy User
    # ========================================================================
    print("\n" + "=" * 80)
    print("📗 SCENARIO 1: Healthy User")
    print("=" * 80)
    
    healthy_quantitative = UserMetrics(
        total_active_tasks=5,
        overdue_tasks=0,
        completion_rate=0.9,
        work_hours_today=7,
        work_hours_this_week=35,
        meetings_today=2,
        total_meeting_hours_today=1.5
    )
    
    healthy_qualitative = QualitativeData(
        meeting_transcripts=["Great meeting today!"],
        task_notes=["Finished ahead of schedule"],
        user_check_ins=["Feeling good"]
    )
    
    print("\n🔄 Running complete analysis...")
    result = engine.analyze(
        user_id=1,
        quantitative_metrics=healthy_quantitative,
        qualitative_data=healthy_qualitative,
        previous_score=None,
        days_in_current_level=0
    )
    
    print(f"\n📊 RESULTS:")
    print(f"  Final Score: {result.final_score}/100")
    print(f"  Level: {result.level.value} - {result.status_message}")
    print(f"\n  Components:")
    print(f"    - Workload: {result.components.workload_score} ({result.components.workload_contribution:.1f}%)")
    print(f"    - Sentiment Adj: {result.components.sentiment_adjustment:+d} ({result.components.sentiment_contribution:.1f}%)")
    print(f"\n  Alert Triggers:")
    print(f"    - Priority: {result.alert_triggers.alert_priority.value}")
    print(f"    - Requires Action: {result.alert_triggers.requires_immediate_action}")
    print(f"\n  Recommendations:")
    for rec in result.recommendations.immediate_actions[:3]:
        print(f"    ✓ {rec}")
    
    # ========================================================================
    # SCENARIO 2: High Risk User
    # ========================================================================
    print("\n" + "=" * 80)
    print("📕 SCENARIO 2: High Risk User (Should Trigger CRITICAL Alerts)")
    print("=" * 80)
    
    high_risk_quantitative = UserMetrics(
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
    
    high_risk_qualitative = QualitativeData(
        meeting_transcripts=[
            "Another exhausting meeting",
            "Team is completely overloaded"
        ],
        task_notes=[
            "Can't keep up anymore",
            "Feeling burned out",
            "Too much work, not enough time"
        ],
        user_check_ins=[
            "Feeling exhausted all the time",
            "Can't sleep, thinking about work",
            "Questioning if this is worth it"
        ]
    )
    
    print("\n🔄 Running complete analysis...")
    result = engine.analyze(
        user_id=2,
        quantitative_metrics=high_risk_quantitative,
        qualitative_data=high_risk_qualitative,
        previous_score=65,  # Was already in RED
        days_in_current_level=5  # Been in RED for 5 days
    )
    
    print(f"\n📊 RESULTS:")
    print(f"  Final Score: {result.final_score}/100 🚨")
    print(f"  Level: {result.level.value} - {result.status_message}")
    print(f"  Trend: {result.trend.trend_direction} (change: {result.trend.score_change:+d})")
    print(f"\n  Components Breakdown:")
    print(f"    - Workload: {result.components.workload_score}")
    print(f"      • Tasks: {result.components.task_score}")
    print(f"      • Time: {result.components.time_score}")
    print(f"      • Meetings: {result.components.meeting_score}")
    print(f"      • Patterns: {result.components.pattern_score}")
    print(f"    - Sentiment: {result.components.sentiment_score:.2f}")
    print(f"    - Adjustment: {result.components.sentiment_adjustment:+d}")
    print(f"\n  🚨 ALERT TRIGGERS (for Alert Detection Layer):")
    print(f"    - High Burnout Score: {result.alert_triggers.high_burnout_score}")
    print(f"    - Prolonged RED: {result.alert_triggers.prolonged_red}")
    print(f"    - Negative Sentiment: {result.alert_triggers.negative_sentiment}")
    print(f"    - Emotional Exhaustion: {result.alert_triggers.emotional_exhaustion}")
    print(f"    - Overwhelm: {result.alert_triggers.overwhelm}")
    print(f"    - Sleep Concerns: {result.alert_triggers.sleep_concerns}")
    print(f"    - PRIORITY: {result.alert_triggers.alert_priority.value}")
    print(f"    - REQUIRES IMMEDIATE ACTION: {result.alert_triggers.requires_immediate_action}")
    print(f"\n  Primary Issues:")
    for issue in result.insights.primary_issues:
        print(f"    ⚠️  {issue}")
    print(f"\n  🎯 IMMEDIATE ACTIONS:")
    for action in result.recommendations.immediate_actions:
        print(f"    🔴 {action}")
    print(f"\n  🔧 Recovery Suggestions:")
    for suggestion in result.recommendations.recovery_suggestions:
        print(f"    💊 {suggestion}")
    
    # ========================================================================
    # Show JSON output for Alert Detection Layer
    # ========================================================================
    print("\n" + "=" * 80)
    print("📤 OUTPUT FOR ALERT DETECTION LAYER (JSON)")
    print("=" * 80)
    print("\nThis is the exact structure that goes to the Alert Detection Layer:")
    print(result.to_json())
    
    print("\n" + "=" * 80)
    print("✅ Burnout Engine Complete!")
    print("=" * 80)
    print("\nThe output is now ready to be consumed by the Alert Detection Layer.")
    print("Alert Detection will use 'alert_triggers' to decide what alerts to show.")