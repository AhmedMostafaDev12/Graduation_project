"""
Burnout System Integration Service
===================================

This service orchestrates ALL components and eliminates redundancy:

1. WorkloadAnalyzer → Feeds metrics to BurnoutEngine
2. SentimentAnalyzer → Feeds sentiment to BurnoutEngine  
3. BurnoutEngine → Produces analysis (WITHOUT recommendations)
4. UserProfileService → Uses WorkloadAnalyzer output for learning
5. RecommendationEngine → Uses Profile + Guidebook + LLM (NEW)

CLEAN ARCHITECTURE - No Duplication!

Author: Sentry AI Team
Date: 2025
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime, date

# Import all components
from Analysis_engine_layer import (
    WorkloadAnalyzer,
    UserMetrics,
    SentimentAnalyzer,
    QualitativeData,
    BurnoutEngine,
    learn_behavioral_patterns
)
from .user_profile_service import UserProfileService
from .burnout_model import BurnoutAnalysis, store_burnout_analysis


# ============================================================================
# INTEGRATION SERVICE
# ============================================================================

class BurnoutSystemIntegration:
    """
    Master integration service that orchestrates all components.
    
    This is the SINGLE place where all components work together.
    Eliminates redundancy and creates clean data flow.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize all components.
        
        Args:
            db_session: SQLAlchemy session
        """
        self.db = db_session
        
        # Initialize analyzers
        self.workload_analyzer = WorkloadAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.burnout_engine = BurnoutEngine()
        
        # Initialize profile service
        self.profile_service = UserProfileService(db_session)
    
    # ========================================================================
    # MAIN ANALYSIS FLOW
    # ========================================================================
    
    def analyze_user_burnout(
        self,
        user_id: int,
        quantitative_metrics: UserMetrics,
        qualitative_data: QualitativeData,
        store_history: bool = True
    ) -> Dict:
        """
        Complete burnout analysis flow.
        
        This is the MAIN METHOD that runs everything:
        1. Workload analysis
        2. Sentiment analysis  
        3. Burnout fusion
        4. Profile context
        5. (Future: Generate recommendations)
        
        Args:
            user_id: User ID
            quantitative_metrics: Workload metrics
            qualitative_data: Text data
            store_history: Whether to store in database
            
        Returns:
            Complete analysis result with profile context
        """
        print(f"\n[ANALYSIS] Starting complete burnout analysis for user {user_id}...")

        # STEP 1: Workload Analysis
        print("  [STEP 1] Analyzing workload...")
        workload_result = self.workload_analyzer.calculate_score(quantitative_metrics)

        # STEP 2: Sentiment Analysis
        print("  [STEP 2] Analyzing sentiment...")
        sentiment_result = self.sentiment_analyzer.analyze(qualitative_data)

        # STEP 3: Get user profile context
        print("  [STEP 3] Loading user profile...")
        user_profile = self.profile_service.get_user_profile(user_id)
        complete_profile = self.profile_service.get_complete_profile_for_llm(user_id)

        # Get previous score for trend analysis
        previous_score = None
        days_in_level = 0
        if user_profile and user_profile.behavioral_profile:
            previous_score = self._get_previous_score(user_id)
            days_in_level = self._calculate_days_in_level(user_id)

        # STEP 4: Burnout Engine (Fusion - NO recommendations)
        print("  [STEP 4] Fusing scores...")
        burnout_result = self.burnout_engine.analyze(
            user_id=user_id,
            quantitative_metrics=quantitative_metrics,
            qualitative_data=qualitative_data,
            previous_score=previous_score,
            days_in_current_level=days_in_level
        )

        # NOTE: We IGNORE burnout_result.recommendations
        # Those are hardcoded and will be replaced by LLM-generated ones

        # STEP 5: Store history (for learning)
        if store_history:
            print("  [STEP 5] Storing analysis history...")
            self._store_analysis_history(
                user_id=user_id,
                metrics=quantitative_metrics,
                workload_result=workload_result,
                burnout_result=burnout_result
            )
        
        # STEP 6: Package complete result
        result = {
            'user_id': user_id,
            'analyzed_at': datetime.utcnow().isoformat(),
            
            # Burnout analysis
            'burnout': {
                'final_score': burnout_result.final_score,
                'level': burnout_result.level.value,
                'status_message': burnout_result.status_message,
                'components': burnout_result.components.to_dict(),
                'insights': burnout_result.insights.to_dict(),
                'trend': burnout_result.trend.to_dict(),
                'alert_triggers': burnout_result.alert_triggers.to_dict()
            },
            
            # User profile context (for recommendations)
            'user_profile': complete_profile.to_llm_context() if complete_profile else None,
            
            # Raw data (for reference)
            'workload_breakdown': workload_result.to_dict(),
            'sentiment_analysis': {
                'sentiment_score': sentiment_result.sentiment_score,
                'stress_indicators': sentiment_result.stress_indicators,
                'burnout_signals': sentiment_result.burnout_signals.model_dump()
            },
            
            # NOTE: Recommendations will be generated separately
            # by the new LLM-based recommendation engine
            'recommendations': None  # Placeholder for future
        }
        
        print("[SUCCESS] Analysis complete!")

        return result
    
    # ========================================================================
    # BEHAVIORAL LEARNING
    # ========================================================================
    
    def update_user_behavioral_profile(
        self,
        user_id: int,
        days: int = 30
    ) -> Dict:
        """
        Learn behavioral patterns from historical data.
        
        This uses the REAL behavioral learning system.
        It analyzes stored burnout analyses to learn patterns.
        
        Args:
            user_id: User ID
            days: Days to analyze
            
        Returns:
            Updated behavioral profile
        """
        print(f"\n[LEARNING] Learning behavioral patterns for user {user_id}...")

        # Use the real behavioral learning module
        patterns = learn_behavioral_patterns(
            db_session=self.db,
            user_id=user_id,
            days=days
        )

        # Update user's behavioral profile
        user = self.profile_service.get_user_profile(user_id)
        if user and user.behavioral_profile:
            behavioral = user.behavioral_profile

            # Update with learned patterns
            behavioral.avg_tasks_per_day = patterns.get('avg_tasks')
            behavioral.avg_work_hours_per_day = patterns.get('avg_hours')
            behavioral.avg_meetings_per_day = patterns.get('avg_meetings')
            behavioral.avg_meeting_hours_per_day = patterns.get('avg_meeting_hours')
            behavioral.avg_completion_rate = patterns.get('completion_rate')

            behavioral.baseline_burnout_score = patterns.get('baseline_score')
            behavioral.baseline_task_count = patterns.get('baseline_tasks')
            behavioral.baseline_work_hours = patterns.get('baseline_hours')
            behavioral.baseline_meeting_count = patterns.get('baseline_meetings')

            behavioral.peak_productivity_hour = patterns.get('peak_hour')
            behavioral.most_productive_day = patterns.get('best_day')
            behavioral.least_productive_day = patterns.get('worst_day')

            behavioral.stress_triggers = patterns.get('stress_triggers', [])
            behavioral.last_pattern_analysis = datetime.utcnow()

            self.db.commit()

            print("[SUCCESS] Behavioral profile updated!")
            
            return patterns
        
        return None
    
    # ========================================================================
    # COMPLETE FLOW (Analysis + Learning)
    # ========================================================================
    
    def complete_daily_flow(
        self,
        user_id: int,
        quantitative_metrics: UserMetrics,
        qualitative_data: QualitativeData
    ) -> Dict:
        """
        Complete daily flow: Analyze + Store + Learn.
        
        This is what runs daily for each user:
        1. Analyze current burnout
        2. Store results
        3. Update behavioral patterns (if enough data)
        4. Return complete result
        
        Args:
            user_id: User ID
            quantitative_metrics: Today's metrics
            qualitative_data: Today's text data
            
        Returns:
            Complete analysis with updated profile
        """
        print("="*80)
        print(f"COMPLETE DAILY FLOW - User {user_id}")
        print("="*80)
        
        # Run analysis
        result = self.analyze_user_burnout(
            user_id=user_id,
            quantitative_metrics=quantitative_metrics,
            qualitative_data=qualitative_data,
            store_history=True
        )
        
        # Check if we have enough history to learn patterns
        analysis_count = self._count_user_analyses(user_id)

        if analysis_count >= 7:  # Need at least 7 days
            print(f"\n[HISTORY] Sufficient history ({analysis_count} analyses) - updating patterns...")
            patterns = self.update_user_behavioral_profile(user_id, days=30)
            result['patterns_updated'] = True
            result['learned_patterns'] = patterns
        else:
            print(f"\n[HISTORY] Building history ({analysis_count}/7 analyses needed)...")
            result['patterns_updated'] = False

        print("\n" + "="*80)
        print("[SUCCESS] DAILY FLOW COMPLETE")
        print("="*80)
        
        return result
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _store_analysis_history(
        self,
        user_id: int,
        metrics: UserMetrics,
        workload_result,
        burnout_result
    ):
        """
        Store analysis results for historical learning.
        
        This creates records in burnout_analyses table that
        the behavioral learning system can analyze.
        """
        try:
            # Import model (already imported at top)
            # from burnout_model import BurnoutAnalysis
            
            # Create record
            analysis = BurnoutAnalysis(
                user_id=user_id,
                analyzed_at=datetime.utcnow(),
                final_score=burnout_result.final_score,
                level=burnout_result.level.value,
                
                # Store metrics for pattern learning
                metrics={
                    'total_active_tasks': metrics.total_active_tasks,
                    'overdue_tasks': metrics.overdue_tasks,
                    'work_hours_today': metrics.work_hours_today,
                    'work_hours_this_week': metrics.work_hours_this_week,
                    'meetings_today': metrics.meetings_today,
                    'total_meeting_hours_today': metrics.total_meeting_hours_today,
                    'back_to_back_meetings': metrics.back_to_back_meetings,
                    'completion_rate': metrics.completion_rate,
                },
                
                # Store component breakdown
                components=burnout_result.components.to_dict(),
                
                # Store insights
                insights=burnout_result.insights.to_dict()
            )
            
            self.db.add(analysis)
            self.db.commit()
            
        except ImportError:
            print("[WARNING] burnout_analyses table not found - skipping history storage")
    
    def _get_previous_score(self, user_id: int) -> Optional[int]:
        """Get user's previous burnout score"""
        try:
            # BurnoutAnalysis already imported at top
            
            result = self.db.query(BurnoutAnalysis).filter(
                BurnoutAnalysis.user_id == user_id
            ).order_by(
                BurnoutAnalysis.analyzed_at.desc()
            ).offset(1).first()  # Get second-most recent (skip today)
            
            return result.final_score if result else None
            
        except:
            return None
    
    def _calculate_days_in_level(self, user_id: int) -> int:
        """Calculate how many days user has been in current level"""
        try:
            # BurnoutAnalysis already imported at top
            
            # Get recent analyses
            recent = self.db.query(BurnoutAnalysis).filter(
                BurnoutAnalysis.user_id == user_id
            ).order_by(
                BurnoutAnalysis.analyzed_at.desc()
            ).limit(30).all()
            
            if not recent:
                return 0
            
            current_level = recent[0].level
            days = 0
            
            for analysis in recent:
                if analysis.level == current_level:
                    days += 1
                else:
                    break
            
            return days
            
        except:
            return 0
    
    def _count_user_analyses(self, user_id: int) -> int:
        """Count how many analyses exist for user"""
        try:
            # BurnoutAnalysis already imported at top
            from sqlalchemy import func
            
            count = self.db.query(func.count(BurnoutAnalysis.id)).filter(
                BurnoutAnalysis.user_id == user_id
            ).scalar()
            
            return count or 0
            
        except:
            return 0


# ============================================================================
# ARCHITECTURE EXPLANATION
# ============================================================================

"""
CLEAN ARCHITECTURE - NO REDUNDANCY:

┌─────────────────────────────────────────────────────────────┐
│                    DAILY USER ACTIVITY                       │
│  • Tasks completed                                           │
│  • Work hours                                                │
│  • Meetings attended                                         │
│  • Text data (notes, messages)                              │
└──────────────────┬──────────────────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────────────────┐
│            BURNOUT SYSTEM INTEGRATION                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1️⃣  WORKLOAD ANALYZER (Quantitative)                       │
│     • Calculates workload score (0-100)                      │
│     • Breaks down: tasks, time, meetings, patterns           │
│     └─→ Used by: Burnout Engine + Profile Learning          │
│                                                               │
│  2️⃣  SENTIMENT ANALYZER (Qualitative)                       │
│     • Analyzes text for burnout signals                      │
│     • Calculates sentiment adjustment (-20 to +20)           │
│     └─→ Used by: Burnout Engine                             │
│                                                               │
│  3️⃣  BURNOUT ENGINE (Fusion)                                │
│     • Fuses workload + sentiment                             │
│     • Produces: score, level, insights, trends               │
│     • ❌ NO longer generates recommendations                 │
│     └─→ Analysis stored in database                         │
│                                                               │
│  4️⃣  USER PROFILE SERVICE (Context)                         │
│     • Stores user info, preferences, constraints             │
│     • Learns patterns from stored analyses                   │
│     • Builds LLM context                                     │
│     └─→ Uses: Behavioral Learning module                    │
│                                                               │
│  5️⃣  BEHAVIORAL LEARNING (Pattern Detection)                │
│     • Analyzes historical workload data                      │
│     • Calculates baselines and patterns                      │
│     • Identifies stress triggers                             │
│     └─→ Updates: User Behavioral Profile                    │
│                                                               │
│  6️⃣  [FUTURE] RECOMMENDATION ENGINE                         │
│     • Uses: Profile + Guidebook + LLM                        │
│     • Generates: Personalized recommendations                │
│     • NOT in Burnout Engine anymore!                         │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────────────────┐
│                    OUTPUT                                     │
├──────────────────────────────────────────────────────────────┤
│  • Burnout analysis (score, level, insights)                 │
│  • Alert triggers (for alert detection layer)                │
│  • User profile context (for recommendations)                │
│  • Historical patterns (for learning)                        │
└──────────────────────────────────────────────────────────────┘


KEY DIFFERENCES FROM OLD ARCHITECTURE:

❌ OLD (Redundant):
  • Burnout Engine had hardcoded recommendations
  • WorkloadAnalyzer used multiple times
  • Profile service had dummy learning function
  • Duplication everywhere

✅ NEW (Clean):
  • Burnout Engine = Analysis ONLY (no recommendations)
  • WorkloadAnalyzer used once, output shared
  • Profile service uses real behavioral learning
  • Single integration point
  • Recommendations will be in separate engine (LLM-based)


DATA FLOW:

Day 1:
  User Activity → Analyze → Store → (Not enough history yet)

Day 7:
  User Activity → Analyze → Store → Learn Patterns → Update Profile

Day 30:
  User Activity → Analyze (uses personal baseline) → Store → 
  Learn Patterns → Update Profile → Generate Recommendations (future)


WHAT GETS STORED:

burnout_analyses table:
  • Daily snapshot of all metrics
  • Burnout scores and levels
  • Component breakdowns
  • Used by behavioral learning

user_behavioral_profiles table:
  • Learned patterns (updated weekly)
  • Baselines and averages
  • Stress triggers
  • Used by recommendation engine


NO MORE DUPLICATION! 🎉
"""


