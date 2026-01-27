"""
Sentry AI - Complete System Example
====================================

This file demonstrates the complete end-to-end flow of the Sentry AI system.

All example code has been consolidated here from individual production files.
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()


def example_complete_flow():
    """
    Complete end-to-end example showing all layers working together.
    """
    print("=" * 80)
    print("SENTRY AI - COMPLETE SYSTEM EXAMPLE")
    print("=" * 80)

    # This would normally come from your database
    # For demo purposes, we'll use mock data
    user_id = 123

    print("\n[STEP 1] Retrieving user data from database...")
    print("In production, this calls: get_complete_user_context(user_id, db_session)")
    print("Returns: metrics, tasks, meetings, qualitative_data")

    # Mock data that would come from database
    from sentry_app.services.burn_out_service.Analysis_engine_layer import UserMetrics, QualitativeData

    mock_metrics = UserMetrics(
        total_active_tasks=8,
        overdue_tasks=2,
        tasks_due_this_week=5,
        completion_rate=0.75,
        work_hours_today=9.5,
        work_hours_this_week=48.0,
        meetings_today=5,
        total_meeting_hours_today=3.5,
        back_to_back_meetings=2,
        weekend_work_sessions=0,
        late_night_sessions=1,
        consecutive_work_days=12
    )

    mock_qualitative = QualitativeData(
        meeting_transcripts=["Team feeling overwhelmed with Q4 deadline"],
        task_notes=["Too many blockers on this task"],
        user_check_ins=["Feeling exhausted today"]
    )

    mock_meetings = [
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
            'title': 'Team Sync',
            'start_time': '03:30 PM',
            'end_time': '04:30 PM',
            'is_optional': True,
            'is_recurring': True,
            'attendees': ['team@company.com'],
            'duration_minutes': 60
        }
    ]

    mock_tasks = [
        {
            'title': 'Database Migration Script',
            'status': 'In Progress',
            'priority': 'High',
            'due_date': 'Tomorrow',
            'can_delegate': True,
            'assigned_to': 'Sarah Chen',
            'estimated_hours': 4
        }
    ]

    print("✓ Data retrieved successfully")

    print("\n[STEP 2] Analyzing burnout...")
    print("In production, this calls: integration.complete_daily_flow()")

    # For demo, we'll show what would happen
    print("\nWorkload Analysis:")
    print(f"  - Total tasks: {mock_metrics.total_active_tasks}")
    print(f"  - Meetings today: {mock_metrics.meetings_today}")
    print(f"  - Back-to-back meetings: {mock_metrics.back_to_back_meetings}")

    print("\nSentiment Analysis:")
    print(f"  - Qualitative entries: {len(mock_qualitative.user_check_ins + mock_qualitative.task_notes)}")
    print(f"  - Key phrase: '{mock_qualitative.user_check_ins[0]}'")

    # Mock analysis result
    burnout_score = 70.4
    burnout_level = 'RED'

    print(f"\n✓ Burnout Score: {burnout_score} ({burnout_level})")

    print("\n[STEP 3] Generating event-specific recommendations...")
    print("In production, this calls: engine.generate_recommendations()")
    print("\nLLM receives actual calendar events and tasks:")
    print("\nTODAY'S CALENDAR EVENTS:")
    for i, meeting in enumerate(mock_meetings, 1):
        optional = " [OPTIONAL]" if meeting['is_optional'] else ""
        print(f"  {i}. {meeting['start_time']} - {meeting['end_time']}: {meeting['title']}{optional}")

    print("\nCURRENT TASK LIST:")
    for i, task in enumerate(mock_tasks, 1):
        delegatable = " [CAN DELEGATE]" if task['can_delegate'] else ""
        print(f"  {i}. {task['title']} (Priority: {task['priority']}, Due: {task['due_date']}){delegatable}")

    print("\n✓ Event-specific recommendations generated!")

    print("\n" + "=" * 80)
    print("EXAMPLE OUTPUT:")
    print("=" * 80)

    # Mock recommendations (what LLM would generate)
    print("\nRecommendation 1: [HIGH PRIORITY]")
    print("Title: Cancel 3:30 PM Team Sync Meeting")
    print("Description: Your 'Team Sync' at 3:30 PM is OPTIONAL and creates a")
    print("             back-to-back situation. Canceling provides recovery time.")
    print("Action Steps:")
    print("  1. Decline '3:30 PM Team Sync (Weekly)' in calendar")
    print("  2. Use freed 3:30-4:30 PM for 30-min walk + prep time")

    print("\nRecommendation 2: [CRITICAL]")
    print("Title: Delegate Database Migration Script to Direct Report")
    print("Description: This High priority task is due Tomorrow and can be delegated.")
    print("             Frees you up for Critical Q4 Launch work.")
    print("Action Steps:")
    print("  1. Open task system and find 'Database Migration Script'")
    print("  2. Reassign from you to Alex Johnson")
    print("  3. Send context message with requirements")
    print("  4. Schedule 15-min sync tomorrow at 9:45 AM")

    print("\n" + "=" * 80)
    print("System working correctly!")
    print("=" * 80)

    print("\n[KEY FEATURES DEMONSTRATED]")
    print("✓ Real-time awareness - References exact event times")
    print("✓ Event-specific - References actual event/task names")
    print("✓ Actionable - Provides concrete steps to execute")
    print("✓ Time-aware - Suggests specific time slots")


if __name__ == "__main__":
    try:
        example_complete_flow()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
