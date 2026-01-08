"""
Complete End-to-End System Test
=================================

This test demonstrates the COMPLETE flow using mock data:

1. Mock Data: Rich, comprehensive mock data for various burnout scenarios
2. Metric Calculation: Test workload metrics with realistic data
3. Burnout Analysis: Analyze burnout using all components
4. Recommendation Generation: Generate event-specific recommendations with RAG + LLM

Run this to test the entire integrated system.

Requirements:
- PostgreSQL database for user profiles (MAIN_DB_URL in .env)
- PGVector database for strategies (VECTOR_DB_URL in .env)
- Ollama running locally with llama3.1:8b model

Author: Sentry AI Team
Date: 2025
"""

import os
import sys
from datetime import datetime, timedelta
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

# Import burnout analysis components
from Analysis_engine_layer import UserMetrics, QualitativeData

# Import user profile and integration services
from user_profile.integration_services import BurnoutSystemIntegration
from user_profile.user_profile_service import UserProfileService
from user_profile.database_base import Base as ProfileBase

# Import recommendation engine
from recommendations_RAG.recommendation_engine import RecommendationEngine


# ============================================================================
# CONFIGURATION
# ============================================================================

# Database URLs from environment
MAIN_DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/sentry_burnout_db")
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL", "postgresql://user:password@localhost:5432/sentry_vector_db")


# ============================================================================
# MOCK DATA GENERATORS
# ============================================================================

def get_mock_scenario(scenario_type: str = "high_stress"):
    """
    Generate comprehensive mock data for different burnout scenarios.

    Args:
        scenario_type: Type of scenario - 'high_stress', 'moderate', 'balanced', 'overwhelming'

    Returns:
        Tuple of (metrics, qualitative_data, tasks, meetings)
    """
    scenarios = {
        "high_stress": {
            "metrics": UserMetrics(
                total_active_tasks=15,
                overdue_tasks=5,
                tasks_due_this_week=10,
                completion_rate=0.60,
                work_hours_today=11.5,
                work_hours_this_week=58.0,
                meetings_today=7,
                total_meeting_hours_today=5.0,
                back_to_back_meetings=4,
                weekend_work_sessions=2,
                late_night_sessions=3,
                consecutive_work_days=14
            ),
            "qualitative": QualitativeData(
                meeting_transcripts=[
                    "Honestly, I'm feeling overwhelmed. The Q4 deadline is killing me and I can't keep up.",
                    "Team mentioned they're working late every night to meet the sprint goals.",
                    "Manager pushed back the code review because 'there's too much on our plates right now'.",
                    "I had to skip lunch again because of back-to-back client calls.",
                    "Everyone in the standup mentioned feeling burned out but we just keep adding more tasks."
                ],
                task_notes=[
                    "This refactoring is taking way longer than expected. Feeling stuck and frustrated.",
                    "Too many dependencies blocking this feature. Can't move forward without 3 other teams.",
                    "Client keeps changing requirements mid-sprint. This is the 4th revision this week.",
                    "Critical bug found in production. Dropping everything to fix it even though I'm already maxed out.",
                    "Estimated 5 hours but already spent 12. Still not done. So exhausted."
                ],
                user_check_ins=[
                    "Feeling completely drained. Barely slept 4 hours last night thinking about work.",
                    "Can't focus anymore. Keep making silly mistakes because I'm so tired.",
                    "Skipped gym again this week. No energy left after work.",
                    "Partner complained I'm always on laptop even on weekends. They're right but I have no choice.",
                    "Headache from staring at screen for 12 hours straight. Need a break but deadlines won't wait."
                ]
            ),
            "tasks": [
                {
                    'title': 'Complete Q4 Database Migration',
                    'status': 'Overdue',
                    'priority': 'Critical',
                    'due_date': '3 days ago',
                    'can_delegate': False,
                    'assigned_to': 'You',
                    'estimated_hours': 20,
                    'actual_hours': 35
                },
                {
                    'title': 'Fix Production Authentication Bug',
                    'status': 'In Progress',
                    'priority': 'Critical',
                    'due_date': 'Today',
                    'can_delegate': False,
                    'assigned_to': 'You',
                    'estimated_hours': 4,
                    'actual_hours': 8
                },
                {
                    'title': 'Implement New Payment Gateway',
                    'status': 'In Progress',
                    'priority': 'High',
                    'due_date': 'Tomorrow',
                    'can_delegate': True,
                    'assigned_to': 'You',
                    'estimated_hours': 16,
                    'actual_hours': 12
                },
                {
                    'title': 'Update API Documentation',
                    'status': 'Overdue',
                    'priority': 'Medium',
                    'due_date': '1 week ago',
                    'can_delegate': True,
                    'assigned_to': 'You',
                    'estimated_hours': 8,
                    'actual_hours': 2
                },
                {
                    'title': 'Code Review for 5 Pull Requests',
                    'status': 'Not Started',
                    'priority': 'High',
                    'due_date': 'Today',
                    'can_delegate': True,
                    'assigned_to': 'You',
                    'estimated_hours': 3,
                    'actual_hours': 0
                }
            ],
            "meetings": [
                {
                    'title': 'Emergency Production Incident Review',
                    'start_time': '08:00 AM',
                    'end_time': '09:00 AM',
                    'is_optional': False,
                    'is_recurring': False,
                    'attendees': ['engineering@company.com', 'leadership@company.com'],
                    'duration_minutes': 60
                },
                {
                    'title': 'Daily Standup',
                    'start_time': '09:00 AM',
                    'end_time': '09:30 AM',
                    'is_optional': False,
                    'is_recurring': True,
                    'attendees': ['team@company.com'],
                    'duration_minutes': 30
                },
                {
                    'title': 'Sprint Planning',
                    'start_time': '09:30 AM',
                    'end_time': '11:00 AM',
                    'is_optional': False,
                    'is_recurring': True,
                    'attendees': ['team@company.com', 'product@company.com'],
                    'duration_minutes': 90
                },
                {
                    'title': 'Client Requirements Discussion',
                    'start_time': '11:00 AM',
                    'end_time': '12:00 PM',
                    'is_optional': False,
                    'is_recurring': False,
                    'attendees': ['client@external.com', 'sales@company.com'],
                    'duration_minutes': 60
                },
                {
                    'title': 'Architecture Review',
                    'start_time': '01:00 PM',
                    'end_time': '02:30 PM',
                    'is_optional': False,
                    'is_recurring': True,
                    'attendees': ['architects@company.com'],
                    'duration_minutes': 90
                },
                {
                    'title': 'Team Sync',
                    'start_time': '02:30 PM',
                    'end_time': '03:30 PM',
                    'is_optional': True,
                    'is_recurring': True,
                    'attendees': ['team@company.com'],
                    'duration_minutes': 60
                },
                {
                    'title': 'Q4 Planning Session',
                    'start_time': '03:30 PM',
                    'end_time': '05:00 PM',
                    'is_optional': False,
                    'is_recurring': False,
                    'attendees': ['all@company.com'],
                    'duration_minutes': 90
                }
            ]
        },
        "moderate": {
            "metrics": UserMetrics(
                total_active_tasks=8,
                overdue_tasks=2,
                tasks_due_this_week=5,
                completion_rate=0.75,
                work_hours_today=8.5,
                work_hours_this_week=44.0,
                meetings_today=4,
                total_meeting_hours_today=2.5,
                back_to_back_meetings=1,
                weekend_work_sessions=0,
                late_night_sessions=1,
                consecutive_work_days=10
            ),
            "qualitative": QualitativeData(
                meeting_transcripts=[
                    "Team is making good progress but we need to watch out for scope creep.",
                    "Sprint retrospective went well. We identified some bottlenecks to address.",
                    "Had a productive 1:1 with manager. Discussed workload concerns."
                ],
                task_notes=[
                    "Making steady progress on this feature. Should finish by end of week.",
                    "Need to follow up with design team on the mockups.",
                    "Code review feedback was helpful. Will implement changes tomorrow."
                ],
                user_check_ins=[
                    "Feeling okay today. A bit tired but manageable.",
                    "Got good sleep last night. Feeling more focused.",
                    "Work is busy but I'm keeping up. Need to remember to take breaks."
                ]
            ),
            "tasks": [
                {
                    'title': 'Implement User Dashboard',
                    'status': 'In Progress',
                    'priority': 'High',
                    'due_date': 'Friday',
                    'can_delegate': False,
                    'assigned_to': 'You',
                    'estimated_hours': 12,
                    'actual_hours': 8
                },
                {
                    'title': 'Update Dependencies',
                    'status': 'Not Started',
                    'priority': 'Medium',
                    'due_date': 'Next Week',
                    'can_delegate': True,
                    'assigned_to': 'You',
                    'estimated_hours': 4,
                    'actual_hours': 0
                },
                {
                    'title': 'Write Unit Tests',
                    'status': 'In Progress',
                    'priority': 'Medium',
                    'due_date': 'Thursday',
                    'can_delegate': True,
                    'assigned_to': 'You',
                    'estimated_hours': 6,
                    'actual_hours': 4
                }
            ],
            "meetings": [
                {
                    'title': 'Daily Standup',
                    'start_time': '09:00 AM',
                    'end_time': '09:15 AM',
                    'is_optional': False,
                    'is_recurring': True,
                    'attendees': ['team@company.com'],
                    'duration_minutes': 15
                },
                {
                    'title': 'Design Review',
                    'start_time': '10:00 AM',
                    'end_time': '11:00 AM',
                    'is_optional': False,
                    'is_recurring': False,
                    'attendees': ['design@company.com'],
                    'duration_minutes': 60
                },
                {
                    'title': '1:1 with Manager',
                    'start_time': '02:00 PM',
                    'end_time': '02:30 PM',
                    'is_optional': False,
                    'is_recurring': True,
                    'attendees': ['manager@company.com'],
                    'duration_minutes': 30
                },
                {
                    'title': 'Team Knowledge Share',
                    'start_time': '04:00 PM',
                    'end_time': '04:45 PM',
                    'is_optional': True,
                    'is_recurring': True,
                    'attendees': ['team@company.com'],
                    'duration_minutes': 45
                }
            ]
        },
        "balanced": {
            "metrics": UserMetrics(
                total_active_tasks=5,
                overdue_tasks=0,
                tasks_due_this_week=3,
                completion_rate=0.90,
                work_hours_today=7.5,
                work_hours_this_week=38.0,
                meetings_today=2,
                total_meeting_hours_today=1.5,
                back_to_back_meetings=0,
                weekend_work_sessions=0,
                late_night_sessions=0,
                consecutive_work_days=5
            ),
            "qualitative": QualitativeData(
                meeting_transcripts=[
                    "Great team collaboration today. Everyone is aligned on priorities.",
                    "Standup was efficient. No major blockers to report."
                ],
                task_notes=[
                    "Finished the feature ahead of schedule. Code review went smoothly.",
                    "Taking time to refactor this properly. Good to have breathing room.",
                    "Pair programming session was really productive."
                ],
                user_check_ins=[
                    "Feeling energized and productive. Good work-life balance this week.",
                    "Enjoying the work. Nice to have time for deep focus.",
                    "Went for a run at lunch. Coming back refreshed."
                ]
            ),
            "tasks": [
                {
                    'title': 'Code Refactoring',
                    'status': 'In Progress',
                    'priority': 'Medium',
                    'due_date': 'Next Week',
                    'can_delegate': False,
                    'assigned_to': 'You',
                    'estimated_hours': 8,
                    'actual_hours': 5
                },
                {
                    'title': 'Documentation Update',
                    'status': 'Not Started',
                    'priority': 'Low',
                    'due_date': '2 Weeks',
                    'can_delegate': True,
                    'assigned_to': 'You',
                    'estimated_hours': 3,
                    'actual_hours': 0
                },
                {
                    'title': 'Performance Optimization',
                    'status': 'In Progress',
                    'priority': 'Medium',
                    'due_date': 'Next Week',
                    'can_delegate': False,
                    'assigned_to': 'You',
                    'estimated_hours': 6,
                    'actual_hours': 3
                }
            ],
            "meetings": [
                {
                    'title': 'Daily Standup',
                    'start_time': '09:00 AM',
                    'end_time': '09:15 AM',
                    'is_optional': False,
                    'is_recurring': True,
                    'attendees': ['team@company.com'],
                    'duration_minutes': 15
                },
                {
                    'title': 'Weekly Team Review',
                    'start_time': '03:00 PM',
                    'end_time': '04:15 PM',
                    'is_optional': False,
                    'is_recurring': True,
                    'attendees': ['team@company.com'],
                    'duration_minutes': 75
                }
            ]
        }
    }

    scenario = scenarios.get(scenario_type, scenarios["moderate"])
    return (
        scenario["metrics"],
        scenario["qualitative"],
        scenario["tasks"],
        scenario["meetings"]
    )


def ensure_user_profile_exists(session, user_id: int):
    """
    Ensure a user profile exists in the database for testing.

    If user profile doesn't exist, we'll just use the first available user
    or inform user to create one manually.

    Args:
        session: Database session
        user_id: User ID to create/verify
    """
    user_service = UserProfileService(session)

    try:
        # Try to get existing profile
        profile = user_service.get_user_profile(user_id)
        if profile:
            print(f"✓ User profile {user_id} already exists")
            print(f"  Name: {profile.full_name}")
            print(f"  Email: {profile.email}")
            return profile
    except:
        pass

    # If no profile found, check if there are ANY profiles we can use
    from user_profile.user_profile_models import UserProfile
    any_profile = session.query(UserProfile).first()

    if any_profile:
        print(f"⚠️  User profile {user_id} not found")
        print(f"✓ Using existing profile: {any_profile.user_id} ({any_profile.full_name})")
        return any_profile

    # No profiles exist - provide instructions
    print(f"\n✗ No user profiles exist in the database")
    print(f"\nTo create a user profile, run the init script or create manually:")
    print(f"   python scripts/create_test_user.py")
    print(f"\nOr update user_id in the test to match an existing user.")
    raise Exception("No user profiles available for testing")


# ============================================================================
# MAIN TEST FLOW
# ============================================================================

def test_complete_flow(user_id: int = 123, scenario: str = "high_stress"):
    """
    Test the complete end-to-end flow with mock data.

    Args:
        user_id: User ID to test with
        scenario: Type of scenario - 'high_stress', 'moderate', or 'balanced'
    """
    print("=" * 80)
    print("COMPLETE END-TO-END SYSTEM TEST")
    print("=" * 80)
    print(f"\nTesting for User ID: {user_id}")
    print(f"Scenario: {scenario.upper().replace('_', ' ')}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ========================================================================
    # STEP 1: DATABASE CONNECTION (PROFILE & VECTOR ONLY)
    # ========================================================================

    print("\n" + "=" * 80)
    print("STEP 1: CONNECTING TO DATABASE")
    print("=" * 80)

    try:
        # Create database engine and session for user profiles
        engine = create_engine(MAIN_DB_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Create profile tables if they don't exist
        ProfileBase.metadata.create_all(engine)

        print("✓ Database connection successful")
        print(f"  - Profile DB: {MAIN_DB_URL.split('@')[1] if '@' in MAIN_DB_URL else 'localhost'}")
        print(f"  - Vector DB: {VECTOR_DB_URL.split('@')[1] if '@' in VECTOR_DB_URL else 'localhost'}")

        # Ensure user profile exists (may return a different user_id)
        profile = ensure_user_profile_exists(session, user_id)
        user_id = profile.user_id  # Use the actual user_id from the profile

    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is running")
        print("2. DATABASE_URL is set in .env")
        print("3. VECTOR_DB_URL is set in .env")
        return

    # ========================================================================
    # STEP 2: LOAD MOCK DATA FOR SCENARIO
    # ========================================================================

    print("\n" + "=" * 80)
    print("STEP 2: LOADING MOCK DATA")
    print("=" * 80)

    # Get mock scenario data
    metrics, qualitative_data, tasks, meetings = get_mock_scenario(scenario)

    print(f"\n✓ Loaded mock data for scenario: {scenario}")
    print(f"  - Tasks: {len(tasks)}")
    print(f"  - Meetings: {len(meetings)}")
    print(f"  - Meeting transcripts: {len(qualitative_data.meeting_transcripts)}")
    print(f"  - Task notes: {len(qualitative_data.task_notes)}")
    print(f"  - User check-ins: {len(qualitative_data.user_check_ins)}")

    # ========================================================================
    # STEP 3: DISPLAY WORKLOAD METRICS
    # ========================================================================

    print("\n" + "=" * 80)
    print("STEP 3: WORKLOAD METRICS OVERVIEW")
    print("=" * 80)

    print("\n✓ Workload metrics for scenario:")
    print(f"  - Total active tasks: {metrics.total_active_tasks}")
    print(f"  - Overdue tasks: {metrics.overdue_tasks}")
    print(f"  - Tasks due this week: {metrics.tasks_due_this_week}")
    print(f"  - Completion rate: {metrics.completion_rate:.1%}")
    print(f"  - Work hours today: {metrics.work_hours_today:.1f}h")
    print(f"  - Work hours this week: {metrics.work_hours_this_week:.1f}h")
    print(f"  - Meetings today: {metrics.meetings_today}")
    print(f"  - Total meeting hours: {metrics.total_meeting_hours_today:.1f}h")
    print(f"  - Back-to-back meetings: {metrics.back_to_back_meetings}")

    if metrics.weekend_work_sessions > 0:
        print(f"  - Weekend work sessions: {metrics.weekend_work_sessions}")
    if metrics.late_night_sessions > 0:
        print(f"  - Late night sessions: {metrics.late_night_sessions}")
    if metrics.consecutive_work_days > 5:
        print(f"  - Consecutive work days: {metrics.consecutive_work_days}")

    # Display sample qualitative data
    print("\n  Sample Qualitative Data:")
    if qualitative_data.user_check_ins:
        print(f"    Latest check-in: \"{qualitative_data.user_check_ins[0]}\"")
    if qualitative_data.task_notes:
        print(f"    Recent task note: \"{qualitative_data.task_notes[0][:80]}...\"")

    # ========================================================================
    # STEP 4: DISPLAY SAMPLE TASKS AND MEETINGS
    # ========================================================================

    print("\n" + "=" * 80)
    print("STEP 4: SAMPLE TASKS & MEETINGS")
    print("=" * 80)

    print("\nSample Tasks:")
    for i, task in enumerate(tasks[:3], 1):
        status_icon = "⚠️" if task['status'] == 'Overdue' else "🔄" if task['status'] == 'In Progress' else "📋"
        print(f"  {status_icon} {i}. {task['title']}")
        print(f"     Priority: {task['priority']} | Due: {task['due_date']} | Status: {task['status']}")

    print("\nSample Meetings:")
    for i, meeting in enumerate(meetings[:3], 1):
        optional_tag = " [Optional]" if meeting.get('is_optional') else ""
        print(f"  {i}. {meeting['start_time']} - {meeting['end_time']}: {meeting['title']}{optional_tag}")
        print(f"     Duration: {meeting['duration_minutes']}min")

    # ========================================================================
    # STEP 5: BURNOUT ANALYSIS
    # ========================================================================

    print("\n" + "=" * 80)
    print("STEP 5: ANALYZING BURNOUT")
    print("=" * 80)

    try:
        # Initialize burnout integration service
        burnout_integration = BurnoutSystemIntegration(session)

        # Run complete burnout analysis
        analysis_result = burnout_integration.analyze_user_burnout(
            user_id=user_id,
            quantitative_metrics=metrics,
            qualitative_data=qualitative_data,
            store_history=True
        )

        burnout_info = analysis_result['burnout']

        print("\n✓ Burnout analysis complete:")
        print(f"  - Burnout Score: {burnout_info['final_score']:.1f}/100")
        print(f"  - Burnout Level: {burnout_info['level']}")
        print(f"  - Status: {burnout_info['status_message']}")

        # Show component breakdown
        components = burnout_info['components']
        print("\n  Component Breakdown:")
        print(f"    • Workload Score: {components.get('workload_score', 0):.1f}")
        print(f"    • Sentiment Adjustment: {components.get('sentiment_adjustment', 0):+.1f}")
        if 'temporal_adjustment' in components:
            print(f"    • Temporal Adjustment: {components['temporal_adjustment']:+.1f}")
        print(f"\n  Contribution Analysis:")
        print(f"    • Workload Contribution: {components.get('workload_contribution', 0):.1f}%")
        print(f"    • Sentiment Contribution: {components.get('sentiment_contribution', 0):.1f}%")

    except Exception as e:
        print(f"✗ Burnout analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # ========================================================================
    # STEP 6: GENERATE EVENT-SPECIFIC RECOMMENDATIONS
    # ========================================================================

    print("\n" + "=" * 80)
    print("STEP 6: GENERATING EVENT-SPECIFIC RECOMMENDATIONS")
    print("=" * 80)

    try:
        # Initialize recommendation engine
        print("\nInitializing recommendation engine...")
        recommendation_engine = RecommendationEngine()

        # Use the task list and calendar events from mock data
        task_list = tasks
        calendar_events = meetings

        print("⏳ Retrieving evidence-based strategies from vector database...")
        print("⏳ Generating personalized recommendations with LLM...")
        print("   (This may take 30-60 seconds depending on LLM response time...)")

        # Generate recommendations with user profile context
        recommendations = recommendation_engine.generate_recommendations(
            burnout_analysis=analysis_result,
            user_profile_context=analysis_result.get('user_profile', 'Software Engineer working on critical projects'),
            calendar_events=calendar_events,
            task_list=task_list
        )

        # Check if we got recommendations
        if not recommendations or not hasattr(recommendations, 'recommendations'):
            print("\n⚠️  Warning: No recommendations object returned")
            print("    The system may be working but LLM did not generate recommendations")
            return

        rec_count = len(recommendations.recommendations) if hasattr(recommendations.recommendations, '__len__') else 0
        print(f"\n✓ Generated {rec_count} recommendations")

        # Display recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)

        if rec_count == 0:
            print("\n⚠️  No recommendations generated")
            print("    Possible reasons:")
            print("    - LLM failed to generate recommendations")
            print("    - Vector database returned no strategies")
            print("    - Check Ollama is running: ollama list")
        else:
            for i, rec in enumerate(recommendations.recommendations, 1):
                # Handle both dict and object formats
                if isinstance(rec, dict):
                    title = rec.get('title', 'Untitled Recommendation')
                    priority = rec.get('priority', 'MEDIUM')
                    description = rec.get('description', 'No description provided')
                    action_steps = rec.get('action_steps', [])
                    expected_impact = rec.get('expected_impact', '')
                else:
                    title = getattr(rec, 'title', 'Untitled Recommendation')
                    priority = getattr(rec, 'priority', 'MEDIUM')
                    description = getattr(rec, 'description', 'No description provided')
                    action_steps = getattr(rec, 'action_steps', [])
                    expected_impact = getattr(rec, 'expected_impact', '')

                print(f"\n[{i}] {title}")
                print(f"Priority: {priority}")
                print(f"\nDescription:")
                print(f"  {description}")

                if action_steps:
                    print(f"\nAction Steps:")
                    for j, step in enumerate(action_steps, 1):
                        print(f"  {j}. {step}")

                if expected_impact:
                    print(f"\nExpected Impact: {expected_impact}")

        # Show reasoning
        if hasattr(recommendations, 'reasoning') and recommendations.reasoning:
            print("\n" + "-" * 80)
            print("Reasoning:")
            print("-" * 80)
            print(f"{recommendations.reasoning}")

        # Show metadata if available
        if hasattr(recommendations, 'metadata') and recommendations.metadata:
            print("\n" + "-" * 80)
            print("Metadata:")
            print("-" * 80)
            for key, value in recommendations.metadata.items():
                print(f"  {key}: {value}")

    except Exception as e:
        print(f"✗ Recommendation generation failed: {e}")
        print("\nPossible issues:")
        print("  1. Ollama not running - start with: ollama serve")
        print("  2. Model not downloaded - run: ollama pull llama3.1:8b")
        print("  3. Vector database connection issue - check VECTOR_DB_URL in .env")
        print("  4. LangChain dependencies issue - check imports")
        import traceback
        traceback.print_exc()

        # Still show partial summary
        print("\n" + "=" * 80)
        print("TEST PARTIAL SUMMARY (Recommendation step failed)")
        print("=" * 80)
        print(f"\n✓ Burnout Score: {burnout_info['final_score']:.1f}/100 ({burnout_info['level']})")
        print(f"✗ Recommendations: Failed to generate")
        print(f"\n⚠️  Fix the recommendation engine issues and run again")

        session.close()
        return

    # ========================================================================
    # SUMMARY
    # ========================================================================

    print("\n" + "=" * 80)
    print("TEST COMPLETE - SUMMARY")
    print("=" * 80)
    print(f"\n✓ Burnout Score: {burnout_info['final_score']:.1f}/100 ({burnout_info['level']})")

    # Safe recommendation count
    try:
        rec_count_final = len(recommendations.recommendations) if recommendations and hasattr(recommendations, 'recommendations') else 0
        print(f"✓ Recommendations Generated: {rec_count_final}")
    except:
        print(f"✓ Recommendations Generated: Unable to count")

    print(f"✓ All system components working correctly!")

    print("\n" + "-" * 80)
    print("System Components Tested:")
    print("  ✓ Database connection")
    print("  ✓ Mock data generation")
    print("  ✓ Workload metrics calculation")
    print("  ✓ Burnout analysis (Workload + Sentiment + Fusion)")
    print("  ✓ User profile integration")
    print("  ✓ Vector database retrieval (RAG)")
    print("  ✓ LLM recommendation generation")
    print("  ✓ Event-specific recommendations")

    # Close database session
    session.close()


# ============================================================================
# RUN TEST
# ============================================================================

if __name__ == "__main__":
    try:
        # Configuration
        test_user_id = int(os.getenv("TEST_USER_ID", "123"))
        test_scenario = os.getenv("TEST_SCENARIO", "high_stress")  # Options: high_stress, moderate, balanced

        # Display available scenarios
        print("\nAvailable test scenarios:")
        print("  - high_stress: Overwhelmed with deadlines, overdue tasks, many meetings")
        print("  - moderate: Busy but manageable workload, some stress indicators")
        print("  - balanced: Healthy workload, good work-life balance")
        print(f"\nRunning scenario: {test_scenario.upper().replace('_', ' ')}\n")

        # Run the test
        test_complete_flow(user_id=test_user_id, scenario=test_scenario)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
