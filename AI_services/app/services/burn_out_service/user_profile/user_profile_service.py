"""
User Profile Service - Business Logic Layer
============================================

Service layer containing all business logic for:
- Creating and managing user profiles
- Learning from user behavior
- Building complete profile context for recommendations
- Updating behavioral patterns

Author: Sentry AI Team
Date: 2025
version: 1.0.0
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, List, Dict, Tuple
from datetime import datetime, date, timedelta, time
import json

# Import models and schemas
from .user_profile_models import (
    UserProfile, UserBehavioralProfile, UserConstraint,
    UserPreferences
)
from .user_profile_schemas import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    BehavioralProfileResponse, BehavioralProfileUpdate,
    ConstraintCreate, ConstraintUpdate, ConstraintResponse,
    PreferencesUpdate, PreferencesResponse,
    CompleteProfileForLLM, CompleteOnboarding
)


# ============================================================================
# USER PROFILE SERVICE
# ============================================================================

class UserProfileService:
    """
    Service for managing user profiles and learning from behavior.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize service with database session.
        
        Args:
            db_session: SQLAlchemy session
        """
        self.db = db_session
    
    # ========================================================================
    # PROFILE CRUD OPERATIONS
    # ========================================================================
    
    def create_user_profile(self, profile_data: UserProfileCreate) -> UserProfile:
        """
        Create a new user profile.
        
        Args:
            profile_data: Profile creation data
            
        Returns:
            Created UserProfile object
        """
        # Create user profile
        user = UserProfile(
            full_name=profile_data.full_name,
            email=profile_data.email,
            timezone=profile_data.timezone
        )
        
        # If onboarding data provided, populate it
        if profile_data.onboarding_data:
            self._populate_from_onboarding(user, profile_data.onboarding_data)
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Initialize related tables
        self._initialize_behavioral_profile(user.user_id)
        self._initialize_preferences(user.user_id)
        
        return user
    
    def _populate_from_onboarding(
        self, 
        user: UserProfile, 
        onboarding: CompleteOnboarding
    ):
        """Populate user profile from onboarding data"""
        user.job_role = onboarding.job_role.value
        user.seniority_level = onboarding.seniority_level.value
        user.job_title = onboarding.job_title
        user.department = onboarding.department
        user.team_name = onboarding.team_name
        user.team_size = onboarding.team_size
        user.direct_reports = onboarding.direct_reports
        user.work_arrangement = onboarding.work_arrangement.value
        user.communication_style = onboarding.communication_style.value
        user.biggest_challenge = onboarding.biggest_challenge
        user.things_tried_before = onboarding.things_tried_before
        user.has_flexible_schedule = onboarding.has_flexible_schedule
        
        # Infer capabilities
        user.can_delegate = onboarding.direct_reports > 0 or onboarding.team_size > 3
        
        # Mark onboarding complete
        user.onboarding_completed = True
        user.profile_complete = True
    
    def _initialize_behavioral_profile(self, user_id: int):
        """Initialize empty behavioral profile for new user"""
        behavioral = UserBehavioralProfile(
            user_id=user_id,
            total_recommendations_received=0,
            total_recommendations_accepted=0,
            total_recommendations_completed=0
        )
        self.db.add(behavioral)
        self.db.commit()
    
    def _initialize_preferences(self, user_id: int):
        """Initialize default preferences for new user"""
        preferences = UserPreferences(user_id=user_id)
        self.db.add(preferences)
        self.db.commit()
    
    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile by ID"""
        return self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()
    
    def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        """Get user profile by email"""
        return self.db.query(UserProfile).filter(
            UserProfile.email == email
        ).first()
    
    def update_user_profile(
        self, 
        user_id: int, 
        update_data: UserProfileUpdate
    ) -> Optional[UserProfile]:
        """
        Update user profile.
        
        Args:
            user_id: User ID
            update_data: Fields to update
            
        Returns:
            Updated profile or None if not found
        """
        user = self.get_user_profile(user_id)
        if not user:
            return None
        
        # Update only provided fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    # ========================================================================
    # BEHAVIORAL LEARNING
    # ========================================================================
    
    def learn_from_activity(
        self, 
        user_id: int, 
        days: int = 30
    ) -> BehavioralProfileResponse:
        """
        Analyze user activity and update behavioral profile.
        This should be called periodically (e.g., daily) to update patterns.
        
        Args:
            user_id: User ID
            days: Number of days to analyze (default 30)
            
        Returns:
            Updated behavioral profile
        """
        # Get user's activity from burnout analyses table
        # This assumes you have burnout_analyses table with daily snapshots
        
        behavioral = self.db.query(UserBehavioralProfile).filter(
            UserBehavioralProfile.user_id == user_id
        ).first()
        
        if not behavioral:
            return None
        
        # Calculate patterns from historical data
        patterns = self._calculate_work_patterns(user_id, days)
        
        # Update behavioral profile
        behavioral.avg_tasks_per_day = patterns.get('avg_tasks')
        behavioral.avg_work_hours_per_day = patterns.get('avg_hours')
        behavioral.avg_meetings_per_day = patterns.get('avg_meetings')
        behavioral.avg_completion_rate = patterns.get('completion_rate')
        
        # Calculate baseline (50th percentile when healthy)
        behavioral.baseline_burnout_score = patterns.get('baseline_score')
        behavioral.baseline_task_count = patterns.get('baseline_tasks')
        behavioral.baseline_work_hours = patterns.get('baseline_hours')
        
        # Peak productivity analysis
        behavioral.peak_productivity_hour = patterns.get('peak_hour')
        behavioral.most_productive_day = patterns.get('best_day')
        
        # Update timestamp
        behavioral.last_pattern_analysis = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(behavioral)
        
        return BehavioralProfileResponse.model_validate(behavioral)
    
    def _calculate_work_patterns(self, user_id: int, days: int) -> Dict:
        """
        Calculate work patterns from historical data using REAL behavioral learning.

        This now uses the behavioral_learning module to analyze actual
        burnout_analyses data instead of returning dummy values.
        """
        # Import the real behavioral learning function
        from Analysis_engine_layer import learn_behavioral_patterns

        # Use the REAL implementation
        patterns = learn_behavioral_patterns(
            db_session=self.db,
            user_id=user_id,
            days=days
        )

        return patterns
    
    def update_recommendation_effectiveness(
        self,
        user_id: int,
        accepted: bool,
        completed: bool,
        recommendation_type: str
    ):
        """
        Update behavioral profile based on recommendation interaction.
        
        Args:
            user_id: User ID
            accepted: Whether user accepted the recommendation
            completed: Whether user completed the action
            recommendation_type: Type of recommendation (for learning)
        """
        behavioral = self.db.query(UserBehavioralProfile).filter(
            UserBehavioralProfile.user_id == user_id
        ).first()
        
        if not behavioral:
            return
        
        # Update counters
        behavioral.total_recommendations_received += 1
        
        if accepted:
            behavioral.total_recommendations_accepted += 1
        
        if completed:
            behavioral.total_recommendations_completed += 1
        
        # Update follow-through rate
        if behavioral.total_recommendations_accepted > 0:
            behavioral.follows_through_rate = (
                behavioral.total_recommendations_completed / 
                behavioral.total_recommendations_accepted
            )
        
        # Update dismissal rate
        behavioral.dismissal_rate = 1.0 - (
            behavioral.total_recommendations_accepted / 
            behavioral.total_recommendations_received
        )
        
        # Learn preference: if accepted, add to preferred types
        if accepted and recommendation_type:
            if behavioral.preferred_recommendation_types is None:
                behavioral.preferred_recommendation_types = []
            
            if recommendation_type not in behavioral.preferred_recommendation_types:
                behavioral.preferred_recommendation_types.append(recommendation_type)
        
        # Learn avoidance: if dismissed multiple times, add to avoided
        if not accepted and recommendation_type:
            # Check how many times this type was dismissed
            # (This is simplified - you'd track this more precisely)
            if behavioral.avoided_recommendation_types is None:
                behavioral.avoided_recommendation_types = []
            
            # If dismissal rate for this type is high, add to avoided
            # (Simplified logic for demo)
            if behavioral.dismissal_rate > 0.7:
                if recommendation_type not in behavioral.avoided_recommendation_types:
                    behavioral.avoided_recommendation_types.append(recommendation_type)
        
        self.db.commit()
    
    def identify_stress_triggers(self, user_id: int) -> List[str]:
        """
        Identify patterns that precede burnout spikes.
        
        This analyzes historical data to find what consistently
        leads to increased burnout for this user.
        
        Returns:
            List of stress triggers
        """
        # TODO: Implement actual pattern analysis
        # This would analyze burnout_analyses to find:
        # - What conditions existed before burnout spikes?
        # - What patterns consistently predict burnout?
        
        # Placeholder implementation
        return [
            "back_to_back_meetings",
            "weekend_work",
            "late_night_sessions"
        ]
    
    # ========================================================================
    # CONSTRAINTS MANAGEMENT
    # ========================================================================
    
    def add_constraint(
        self, 
        user_id: int, 
        constraint_data: ConstraintCreate
    ) -> UserConstraint:
        """
        Add a new constraint for user.
        
        Args:
            user_id: User ID
            constraint_data: Constraint details
            
        Returns:
            Created constraint
        """
        constraint = UserConstraint(
            user_id=user_id,
            constraint_type=constraint_data.constraint_type.value,
            constraint_name=constraint_data.constraint_name,
            description=constraint_data.description,
            start_date=constraint_data.start_date,
            end_date=constraint_data.end_date,
            blocks_delegation=constraint_data.blocks_delegation,
            blocks_pto=constraint_data.blocks_pto,
            blocks_meeting_cancellation=constraint_data.blocks_meeting_cancellation,
            priority_level=constraint_data.priority_level.value
        )
        
        self.db.add(constraint)
        self.db.commit()
        self.db.refresh(constraint)
        
        return constraint
    
    def get_active_constraints(self, user_id: int) -> List[UserConstraint]:
        """
        Get all active constraints for user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active constraints
        """
        today = date.today()
        
        return self.db.query(UserConstraint).filter(
            and_(
                UserConstraint.user_id == user_id,
                UserConstraint.is_active == True,
                UserConstraint.end_date >= today
            )
        ).all()
    
    def resolve_constraint(self, constraint_id: int) -> bool:
        """
        Mark constraint as resolved.
        
        Args:
            constraint_id: Constraint ID
            
        Returns:
            True if successful
        """
        constraint = self.db.query(UserConstraint).filter(
            UserConstraint.id == constraint_id
        ).first()
        
        if constraint:
            constraint.is_active = False
            constraint.resolved_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    def auto_expire_constraints(self):
        """
        Automatically expire past constraints.
        Should be run daily as a cron job.
        """
        today = date.today()
        
        expired = self.db.query(UserConstraint).filter(
            and_(
                UserConstraint.is_active == True,
                UserConstraint.end_date < today
            )
        ).all()
        
        for constraint in expired:
            constraint.is_active = False
            constraint.resolved_at = datetime.utcnow()
        
        self.db.commit()
        return len(expired)
    
    # ========================================================================
    # PREFERENCES MANAGEMENT
    # ========================================================================
    
    def update_preferences(
        self, 
        user_id: int, 
        preferences_data: PreferencesUpdate
    ) -> Optional[UserPreferences]:
        """
        Update user preferences.
        
        Args:
            user_id: User ID
            preferences_data: Preferences to update
            
        Returns:
            Updated preferences
        """
        preferences = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
        
        if not preferences:
            return None
        
        # Update only provided fields
        update_dict = preferences_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(preferences, key):
                setattr(preferences, key, value)
        
        self.db.commit()
        self.db.refresh(preferences)
        
        return preferences
    
    def get_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Get user preferences"""
        return self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()
    
    def is_quiet_hours(self, user_id: int) -> bool:
        """
        Check if current time is in user's quiet hours.
        
        Args:
            user_id: User ID
            
        Returns:
            True if in quiet hours
        """
        preferences = self.get_preferences(user_id)
        
        if not preferences or not preferences.quiet_hours_enabled:
            return False
        
        # Get user's current time (considering timezone)
        user_profile = self.get_user_profile(user_id)
        # TODO: Convert to user's timezone
        current_time = datetime.utcnow().time()
        
        # Check if current time is in quiet hours
        if preferences.quiet_hours_start and preferences.quiet_hours_end:
            start = preferences.quiet_hours_start
            end = preferences.quiet_hours_end
            
            # Handle overnight quiet hours (e.g., 20:00 to 08:00)
            if start > end:
                return current_time >= start or current_time <= end
            else:
                return start <= current_time <= end
        
        return False
    
    # ========================================================================
    # COMPLETE PROFILE BUILDING (For LLM Context)
    # ========================================================================
    
    def get_complete_profile_for_llm(
        self, 
        user_id: int
    ) -> Optional[CompleteProfileForLLM]:
        """
        Build complete profile context for LLM recommendation generation.
        
        This combines:
        - User profile
        - Behavioral patterns
        - Active constraints
        - Effectiveness history
        
        Args:
            user_id: User ID
            
        Returns:
            Complete profile ready for LLM prompt
        """
        # Get all profile components
        user = self.get_user_profile(user_id)
        if not user:
            return None
        
        behavioral = user.behavioral_profile
        constraints = self.get_active_constraints(user_id)
        
        # Build complete profile
        complete_profile = CompleteProfileForLLM(
            user_id=user.user_id,
            full_name=user.full_name,
            job_role=user.job_role or "Unknown",
            seniority_level=user.seniority_level or "Unknown",
            team_size=user.team_size,
            direct_reports=user.direct_reports,
            can_delegate=user.can_delegate,
            avg_tasks_per_day=behavioral.avg_tasks_per_day if behavioral else None,
            avg_work_hours_per_day=behavioral.avg_work_hours_per_day if behavioral else None,
            avg_meetings_per_day=behavioral.avg_meetings_per_day if behavioral else None,
            baseline_burnout_score=behavioral.baseline_burnout_score if behavioral else None,
            communication_style=user.communication_style or "direct",
            preferred_recommendation_types=behavioral.preferred_recommendation_types if behavioral else None,
            avoided_recommendation_types=behavioral.avoided_recommendation_types if behavioral else None,
            active_constraints=[
                ConstraintResponse.model_validate(c) for c in constraints
            ]
        )
        
        return complete_profile
    
    def get_profile_summary(self, user_id: int) -> Dict:
        """
        Get a summary of user profile for dashboard display.
        
        Returns:
            Dictionary with profile summary
        """
        user = self.get_user_profile(user_id)
        if not user:
            return None
        
        behavioral = user.behavioral_profile
        constraints = self.get_active_constraints(user_id)
        
        return {
            'basic_info': {
                'name': user.full_name,
                'role': f"{user.seniority_level} {user.job_role}",
                'team': user.team_name,
                'team_size': user.team_size,
                'can_delegate': user.can_delegate
            },
            'work_patterns': {
                'avg_tasks_per_day': behavioral.avg_tasks_per_day if behavioral else None,
                'avg_work_hours': behavioral.avg_work_hours_per_day if behavioral else None,
                'avg_meetings': behavioral.avg_meetings_per_day if behavioral else None,
                'baseline_burnout': behavioral.baseline_burnout_score if behavioral else None,
                'peak_hour': behavioral.peak_productivity_hour if behavioral else None
            },
            'preferences': {
                'communication_style': user.communication_style,
                'preferred_types': behavioral.preferred_recommendation_types if behavioral else [],
                'avoided_types': behavioral.avoided_recommendation_types if behavioral else []
            },
            'effectiveness': {
                'total_received': behavioral.total_recommendations_received if behavioral else 0,
                'acceptance_rate': (
                    behavioral.total_recommendations_accepted / 
                    behavioral.total_recommendations_received 
                    if behavioral and behavioral.total_recommendations_received > 0 else 0
                ),
                'follow_through_rate': behavioral.follows_through_rate if behavioral else 0
            },
            'active_constraints': [
                {
                    'name': c.constraint_name,
                    'type': c.constraint_type,
                    'until': c.end_date,
                    'blocks_pto': c.blocks_pto
                }
                for c in constraints
            ]
        }


