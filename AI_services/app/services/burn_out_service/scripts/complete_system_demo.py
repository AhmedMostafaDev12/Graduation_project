"""
Complete Burnout System Demo with Recommendations
==================================================

This script demonstrates the FULL end-to-end system:
1. User profile creation
2. Daily burnout analysis (complete_daily_flow)
3. Behavioral learning (after 7 days)
4. RAG-based personalized recommendations

Run this to see the complete integrated system.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Import burnout analysis components
from Analysis_engine_layer import UserMetrics, QualitativeData

# Import profile and integration
from user_profile.integration_services import BurnoutSystemIntegration
from user_profile.database_base import Base
from user_profile.service import UserProfileService
from user_profile.schemas import (
    UserProfileCreate, CompleteOnboarding,
    JobRole, SeniorityLevel, WorkArrangement, CommunicationStyle
)

# Import recommendation engine
from recommendations_RAG.recommendation_engine import generate_recommendations_from_analysis


def main():
    """Complete system demonstration with recommendations."""

    print("=" * 80)
    print("COMPLETE BURNOUT SYSTEM - WITH RECOMMENDATIONS")
    print("=" * 80)

    # Setup database
    print("\nSetting up database...")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("\nERROR: DATABASE_URL not found in .env file")
        print("Please add: DATABASE_URL=postgresql://user:pass@localhost:5432/sentry_burnout_db")
        print("Falling back to SQLite for demo purposes...")
        db_url = 'sqlite:///burnout_system_demo.db'

    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    print(f"Database ready! Using: {db_url.split('@')[1] if '@' in db_url else 'SQLite'}")

    # Create user profile
    print("\nCreating user profile...")
    profile_service = UserProfileService(session)
    existing_user = profile_service.get_user_by_email("demo@example.com")

    if not existing_user:
        onboarding = CompleteOnboarding(
            job_role=JobRole.SOFTWARE_ENGINEER,
            seniority_level=SeniorityLevel.SENIOR,
            job_title="Senior Backend Engineer",
            team_size=8,
            direct_reports=2,
            can_delegate=True,
            has_flexible_schedule=True,
            biggest_challenge="Too many meetings",
            peak_productivity_time="morning",
            things_tried_before=["time_blocking", "pomodoro"],
            communication_style=CommunicationStyle.DIRECT,
            department="Engineering",
            team_name="Platform Team",
            work_arrangement=WorkArrangement.HYBRID
        )

        profile_create = UserProfileCreate(
            full_name="Demo User",
            email="demo@example.com",
            timezone="America/New_York",
            onboarding_data=onboarding
        )

        user = profile_service.create_user_profile(profile_create)
        user_id = user.user_id
        print(f"Created user: {user.full_name} (ID: {user_id})")
    else:
        user_id = existing_user.user_id
        print(f"Using existing user: {existing_user.full_name} (ID: {user_id})")

    # Initialize integration service
    print("\nInitializing integration service...")
    integration = BurnoutSystemIntegration(session)

    # Simulate 6 days of work (building history)
    print("\n" + "=" * 80)
    print("SIMULATING DAYS 1-6 (Building History)")
    print("=" * 80)

    for day in range(1, 7):
        print(f"\n--- Day {day} ---")

        metrics = UserMetrics(
            total_active_tasks=8 + day,
            overdue_tasks=1 if day > 3 else 0,
            tasks_due_this_week=5 + day,
            completion_rate=0.75,
            work_hours_today=8.0 + (day * 0.5),
            work_hours_this_week=40 + (day * 2),
            meetings_today=3 + (day // 2),
            total_meeting_hours_today=2.0 + (day * 0.3),
            back_to_back_meetings=1 if day > 4 else 0,
            weekend_work_sessions=0,
            late_night_sessions=0 if day < 5 else 1,
            consecutive_work_days=day
        )

        qualitative = QualitativeData(
            meeting_transcripts=[f"Day {day} - Regular team sync"],
            task_notes=["Working on sprint tasks"],
            user_check_ins=[]
        )

        result = integration.complete_daily_flow(
            user_id=user_id,
            quantitative_metrics=metrics,
            qualitative_data=qualitative
        )

        print(f"Score: {result['burnout']['final_score']} ({result['burnout']['level']})")

    # Day 7: High stress + Learning + Recommendations
    print("\n" + "=" * 80)
    print("DAY 7 - HIGH STRESS + LEARNING + RECOMMENDATIONS")
    print("=" * 80)

    # High stress day
    metrics = UserMetrics(
        total_active_tasks=15,
        overdue_tasks=3,
        tasks_due_this_week=12,
        completion_rate=0.53,
        work_hours_today=10.5,
        work_hours_this_week=52,
        meetings_today=8,
        total_meeting_hours_today=5.0,
        back_to_back_meetings=4,
        weekend_work_sessions=1,
        late_night_sessions=2,
        consecutive_work_days=7
    )

    qualitative = QualitativeData(
        meeting_transcripts=["Team feeling overloaded with the new release"],
        task_notes=["Too many blockers", "Dependencies everywhere"],
        user_check_ins=["Feeling exhausted", "Working late again"]
    )

    print("\nRunning complete daily flow...")
    result = integration.complete_daily_flow(
        user_id=user_id,
        quantitative_metrics=metrics,
        qualitative_data=qualitative
    )

    print("\nBURNOUT ANALYSIS RESULTS:")
    print(f"   Burnout Score: {result['burnout']['final_score']}")
    print(f"   Level: {result['burnout']['level']}")
    print(f"   Status: {result['burnout']['status_message']}")
    print(f"   Patterns Updated: {result.get('patterns_updated', False)}")

    if result.get('learned_patterns'):
        patterns = result['learned_patterns']
        print("\nLEARNED PATTERNS:")
        print(f"   Average tasks/day: {patterns['avg_tasks']}")
        print(f"   Average work hours: {patterns['avg_hours']}")
        print(f"   Baseline burnout (healthy): {patterns['baseline_score']}")
        if patterns['stress_triggers']:
            print("\n   STRESS TRIGGERS IDENTIFIED:")
            for trigger in patterns['stress_triggers']:
                print(f"      - {trigger}")

    # Generate personalized recommendations
    print("\n" + "=" * 80)
    print("GENERATING PERSONALIZED RECOMMENDATIONS")
    print("=" * 80)

    try:
        print("\nCalling recommendation engine...")
        recommendations = generate_recommendations_from_analysis(result)

        print("\n" + "=" * 80)
        print("PERSONALIZED RECOMMENDATIONS")
        print("=" * 80)

        for i, rec in enumerate(recommendations.recommendations, 1):
            print(f"\n{i}. {rec.title} [{rec.priority}]")
            print(f"   Category: {rec.recommendation_type}")
            print(f"   Time to implement: ~{rec.estimated_time_minutes} minutes")
            print(f"\n   Why this helps you:")
            print(f"   {rec.description}")
            print(f"\n   Action Steps:")
            for j, step in enumerate(rec.action_steps, 1):
                print(f"      {j}. {step}")
            print(f"\n   Expected Impact: {rec.expected_impact}")
            if rec.evidence_source:
                print(f"   Evidence: {rec.evidence_source}")

        print(f"\n\nREASONING:")
        print(recommendations.reasoning)

        print("\n" + "=" * 80)
        print("SUCCESS! Complete system working end-to-end!")
        print("=" * 80)

    except Exception as e:
        print(f"\nERROR generating recommendations: {e}")
        print("\nMake sure:")
        print("   1. Vector database is populated (run populate_strategies.py)")
        print("   2. Ollama is running (ollama serve)")
        print("   3. Model is pulled (ollama pull llama3.1:8b)")
        import traceback
        traceback.print_exc()

    # Summary
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE!")
    print("=" * 80)

    print("\nWhat Just Happened:")
    print("   1. Created user profile with onboarding data")
    print("   2. Simulated 6 days of work (building history)")
    print("   3. On day 7, behavioral learning activated")
    print("   4. System learned user's personal patterns & baselines")
    print("   5. Generated burnout analysis with insights")
    print("   6. RAG retrieved relevant strategies from vector database")
    print("   7. LLM generated personalized recommendations")

    print("\nDatabase:")
    if '@' in db_url:
        print(f"   Main DB: {db_url.split('@')[1]}")
    else:
        print(f"   Location: {os.path.abspath('burnout_system_demo.db')}")

    vector_db = os.getenv("VECTOR_DB_URL")
    if vector_db:
        print(f"   Vector DB: {vector_db.split('@')[1] if '@' in vector_db else vector_db}")

    print("\nNext Steps:")
    print("   - Integrate with your frontend API")
    print("   - Add real task/calendar data sources")
    print("   - Deploy to production")

    session.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
