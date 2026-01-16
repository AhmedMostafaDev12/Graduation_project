"""
Task Database Integration
==========================

Integrates with your internal task management database to:
1. Retrieve user's assigned tasks
2. Calculate workload metrics automatically (total_tasks, overdue_tasks, etc.)
3. Provide actual task names for event-specific recommendations

This replaces manual metric entry with automatic calculation from your database.

Database Schema (assumed):
- tasks table with: id, title, user_id, status, priority, due_date, assigned_to, can_delegate, estimated_hours
- meetings table with: id, title, start_time, end_time, attendees, is_recurring, is_optional

Author: Sentry AI Team
Date: 2025
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os

# Import UserMetrics from workload analyzer
try:
    from Analysis_engine_layer import UserMetrics
except ImportError:
    # Fallback for when imported from unified system
    import sys
    from pathlib import Path
    burnout_service_path = Path(__file__).parent.parent
    if str(burnout_service_path) not in sys.path:
        sys.path.insert(0, str(burnout_service_path))
    from Analysis_engine_layer import UserMetrics

# Create local Base for model definitions
# Note: We use a shared session from the unified system, so even though
# models are defined separately, they query the same database
Base = declarative_base()


# ============================================================================
# DATABASE MODELS (YOUR BACKEND TEAM'S SCHEMA)
# ============================================================================

class Task(Base):
    """
    Task model - matches your backend team's task database schema.

    This table stores BOTH regular tasks AND meetings.
    Differentiated by task_type field:
    - 'task': Regular work task
    - 'meeting': Calendar meeting/event

    Adjust fields to match your actual database schema.
    """
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=False)
    task_type = Column(String(20), default='task')  # 'task' or 'meeting'

    # Common fields (for both tasks and meetings)
    status = Column(String(50))  # 'Todo', 'In Progress', 'Done', 'Blocked'
    priority = Column(String(20))  # 'Low', 'Medium', 'High', 'Critical'
    due_date = Column(DateTime, nullable=True)
    assigned_to = Column(String(100))
    can_delegate = Column(Boolean, default=True)
    estimated_hours = Column(Float, nullable=True)

    # Meeting-specific fields (only used when task_type='meeting')
    start_time = Column(DateTime, nullable=True)  # For meetings
    end_time = Column(DateTime, nullable=True)    # For meetings
    attendees = Column(Text, nullable=True)       # Comma-separated emails
    is_recurring = Column(Boolean, default=False)  # For recurring meetings
    is_optional = Column(Boolean, default=False)   # Can user decline?

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class QualitativeDataEntry(Base):
    """
    Qualitative data model - sentiment notes and user check-ins.
    This is where meeting transcripts, task notes, and user reflections are stored.
    """
    __tablename__ = 'qualitative_data'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    entry_type = Column(String(50))  # 'meeting_transcript', 'task_note', 'user_check_in'
    content = Column(Text, nullable=False)
    sentiment_score = Column(Float, nullable=True)  # If pre-calculated
    task_id = Column(Integer, nullable=True)  # Link to associated task if applicable
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# TASK DATABASE SERVICE
# ============================================================================

class TaskDatabaseService:
    """
    Service to interact with your internal task database.

    Features:
    - Retrieve user's tasks
    - Calculate workload metrics automatically
    - Provide task data for event-specific recommendations
    """

    def __init__(self, database_url: Optional[str] = None, session: Optional[Session] = None):
        """
        Initialize task database service.

        Args:
            database_url: Database URL (defaults to TASK_DB_URL from .env)
            session: Existing SQLAlchemy session to use (for unified system)
        """
        if session:
            # Use provided session (unified system)
            self.session = session
            self.engine = None
        else:
            # Create own session (standalone mode)
            self.database_url = database_url or os.getenv(
                "TASK_DB_URL",
                os.getenv("DATABASE_URL")  # Fallback to main database
            )
            self.engine = create_engine(self.database_url, echo=False)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()

    # ========================================================================
    # RETRIEVE TASKS
    # ========================================================================

    def get_user_tasks(
        self,
        user_id: int,
        include_completed: bool = False
    ) -> List[Dict]:
        """
        Retrieve all WORK TASKS for a user (not meetings).

        Args:
            user_id: User ID
            include_completed: Include completed tasks (default: False)

        Returns:
            List of task dictionaries
        """
        query = self.session.query(Task).filter(
            Task.user_id == user_id,
            Task.task_type == 'task'  # Only get tasks, not meetings
        )

        if not include_completed:
            query = query.filter(Task.status != 'Done')

        tasks = query.all()

        return [
            {
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else 'No deadline',
                'assigned_to': task.assigned_to,
                'can_delegate': task.can_delegate,
                'estimated_hours': task.estimated_hours or 0
            }
            for task in tasks
        ]

    def get_user_meetings(
        self,
        user_id: int,
        date: datetime = None
    ) -> List[Dict]:
        """
        Retrieve MEETINGS for a user on a specific date.
        Meetings are stored in the tasks table with task_type='meeting'.

        Args:
            user_id: User ID
            date: Date to retrieve meetings for (defaults to today)

        Returns:
            List of meeting dictionaries
        """
        if date is None:
            date = datetime.now()

        start_of_day = datetime.combine(date.date(), datetime.min.time())
        end_of_day = datetime.combine(date.date(), datetime.max.time())

        meetings = self.session.query(Task).filter(
            Task.user_id == user_id,
            Task.task_type == 'meeting',  # Only get meetings
            Task.start_time >= start_of_day,
            Task.start_time <= end_of_day
        ).order_by(Task.start_time).all()

        return [
            {
                'id': meeting.id,
                'title': meeting.title,
                'start_time': meeting.start_time.strftime('%I:%M %p') if meeting.start_time else 'N/A',
                'end_time': meeting.end_time.strftime('%I:%M %p') if meeting.end_time else 'N/A',
                'attendees': meeting.attendees.split(',') if meeting.attendees else [],
                'is_recurring': meeting.is_recurring,
                'is_optional': meeting.is_optional,
                'duration_minutes': int((meeting.end_time - meeting.start_time).total_seconds() / 60) if meeting.end_time and meeting.start_time else 0
            }
            for meeting in meetings
        ]

    def get_qualitative_data(
        self,
        user_id: int,
        date: datetime = None,
        days_back: int = 1
    ) -> Dict:
        """
        Retrieve qualitative data (sentiment notes, meeting transcripts, task notes).

        Args:
            user_id: User ID
            date: Date to retrieve data for (defaults to today)
            days_back: How many days back to retrieve (default: 1)

        Returns:
            Dictionary with categorized qualitative data
        """
        if date is None:
            date = datetime.now()

        cutoff_date = date - timedelta(days=days_back)

        entries = self.session.query(QualitativeDataEntry).filter(
            QualitativeDataEntry.user_id == user_id,
            QualitativeDataEntry.created_at >= cutoff_date
        ).all()

        # Categorize by entry type
        meeting_transcripts = [
            e.content for e in entries
            if e.entry_type == 'meeting_transcript'
        ]

        task_notes = [
            e.content for e in entries
            if e.entry_type == 'task_note'
        ]

        user_check_ins = [
            e.content for e in entries
            if e.entry_type == 'user_check_in'
        ]

        return {
            'meeting_transcripts': meeting_transcripts,
            'task_notes': task_notes,
            'user_check_ins': user_check_ins
        }

    # ========================================================================
    # CALCULATE METRICS AUTOMATICALLY
    # ========================================================================

    def calculate_workload_metrics(
        self,
        user_id: int,
        date: datetime = None
    ) -> UserMetrics:
        """
        Calculate ALL workload metrics automatically from the database.

        This replaces manual metric entry:
        - Retrieves tasks from database
        - Retrieves meetings from database
        - Calculates all metrics needed for burnout analysis

        Args:
            user_id: User ID
            date: Date to calculate metrics for (defaults to today)

        Returns:
            UserMetrics object ready for burnout analysis
        """
        if date is None:
            date = datetime.now()

        print(f"\n[CALCULATE] Calculating metrics for user {user_id} on {date.date()}...")

        # Get all active tasks
        tasks = self.get_user_tasks(user_id, include_completed=False)

        # Get today's meetings
        meetings = self.get_user_meetings(user_id, date)

        # Calculate task metrics
        total_active_tasks = len(tasks)

        overdue_tasks = len([
            t for t in tasks
            if t['due_date'] != 'No deadline' and
            datetime.strptime(t['due_date'], '%Y-%m-%d') < datetime.now()
        ])

        tasks_due_this_week = len([
            t for t in tasks
            if t['due_date'] != 'No deadline' and
            datetime.strptime(t['due_date'], '%Y-%m-%d') < datetime.now() + timedelta(days=7)
        ])

        # Calculate completion rate (completed tasks this week / total tasks this week)
        completed_this_week = self._get_completed_tasks_count(user_id, days=7)
        total_this_week = completed_this_week + total_active_tasks
        completion_rate = completed_this_week / total_this_week if total_this_week > 0 else 1.0

        # Calculate meeting metrics
        meetings_today = len(meetings)
        total_meeting_hours_today = sum(m['duration_minutes'] for m in meetings) / 60.0

        # Detect back-to-back meetings
        back_to_back_meetings = self._count_back_to_back_meetings(meetings)

        # Calculate work hours (estimated from tasks + meetings)
        estimated_task_hours = sum(t['estimated_hours'] for t in tasks) / 7  # Average per day
        work_hours_today = estimated_task_hours + total_meeting_hours_today

        # Get weekly metrics
        work_hours_this_week = self._calculate_weekly_work_hours(user_id)
        weekend_work_sessions = self._count_weekend_work(user_id, date)
        late_night_sessions = self._count_late_night_work(user_id, date)
        consecutive_work_days = self._count_consecutive_work_days(user_id, date)

        # Create UserMetrics object
        metrics = UserMetrics(
            total_active_tasks=total_active_tasks,
            overdue_tasks=overdue_tasks,
            tasks_due_this_week=tasks_due_this_week,
            completion_rate=completion_rate,
            work_hours_today=work_hours_today,
            work_hours_this_week=work_hours_this_week,
            meetings_today=meetings_today,
            total_meeting_hours_today=total_meeting_hours_today,
            back_to_back_meetings=back_to_back_meetings,
            weekend_work_sessions=weekend_work_sessions,
            late_night_sessions=late_night_sessions,
            consecutive_work_days=consecutive_work_days
        )

        print(f"[OK] Metrics calculated:")
        print(f"     - {total_active_tasks} active tasks ({overdue_tasks} overdue)")
        print(f"     - {meetings_today} meetings today ({total_meeting_hours_today:.1f} hours)")
        print(f"     - {back_to_back_meetings} back-to-back meetings")

        return metrics

    # ========================================================================
    # HELPER METHODS FOR METRIC CALCULATION
    # ========================================================================

    def _get_completed_tasks_count(self, user_id: int, days: int = 7) -> int:
        """Count tasks completed in the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)

        completed = self.session.query(Task).filter(
            Task.user_id == user_id,
            Task.status == 'Done',
            Task.updated_at >= cutoff_date
        ).count()

        return completed

    def _count_back_to_back_meetings(self, meetings: List[Dict]) -> int:
        """Count back-to-back meetings (less than 5 min gap)"""
        if len(meetings) < 2:
            return 0

        count = 0
        for i in range(len(meetings) - 1):
            # Parse times
            current_end = datetime.strptime(meetings[i]['end_time'], '%I:%M %p')
            next_start = datetime.strptime(meetings[i + 1]['start_time'], '%I:%M %p')

            # Calculate gap
            gap_minutes = (next_start - current_end).total_seconds() / 60

            if gap_minutes < 5:
                count += 1

        return count

    def _calculate_weekly_work_hours(self, user_id: int) -> float:
        """Calculate total work hours this week (from meetings in tasks table)"""
        # Get start of week (Monday)
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())

        # Get meetings from tasks table
        weekly_meetings = self.session.query(Task).filter(
            Task.user_id == user_id,
            Task.task_type == 'meeting',
            Task.start_time >= start_of_week
        ).all()

        total_hours = sum(
            (m.end_time - m.start_time).total_seconds() / 3600
            for m in weekly_meetings
            if m.end_time and m.start_time
        )

        # Add estimated task hours (rough estimate: 40 hours/week baseline)
        return total_hours + 40  # Adjust based on your team's typical hours

    def _count_weekend_work(self, user_id: int, date: datetime) -> int:
        """Count weekend work sessions in the last week"""
        last_weekend_start = date - timedelta(days=date.weekday() + 2)  # Last Saturday
        last_weekend_end = last_weekend_start + timedelta(days=2)  # Sunday end

        # Count meetings and task updates on weekend
        weekend_meetings = self.session.query(Task).filter(
            Task.user_id == user_id,
            Task.task_type == 'meeting',
            Task.start_time >= last_weekend_start,
            Task.start_time <= last_weekend_end
        ).count()

        weekend_tasks = self.session.query(Task).filter(
            Task.user_id == user_id,
            Task.task_type == 'task',
            Task.updated_at >= last_weekend_start,
            Task.updated_at <= last_weekend_end
        ).count()

        return weekend_meetings + weekend_tasks

    def _count_late_night_work(self, user_id: int, date: datetime) -> int:
        """Count late night work sessions (after 8 PM) in the last week"""
        week_start = date - timedelta(days=7)

        # Count late meetings
        late_meetings = self.session.query(Task).filter(
            Task.user_id == user_id,
            Task.task_type == 'meeting',
            Task.start_time >= week_start,
            Task.start_time <= date
        ).all()

        late_count = sum(
            1 for m in late_meetings
            if m.start_time and m.start_time.hour >= 20  # After 8 PM
        )

        return late_count

    def _count_consecutive_work_days(self, user_id: int, date: datetime) -> int:
        """Count consecutive work days (days with meetings or tasks updated)"""
        consecutive = 0
        current_date = date

        for _ in range(30):  # Check last 30 days max
            # Check if user had meetings or updated tasks on this day
            start_of_day = datetime.combine(current_date.date(), datetime.min.time())
            end_of_day = datetime.combine(current_date.date(), datetime.max.time())

            # Check for meetings
            had_meetings = self.session.query(Task).filter(
                Task.user_id == user_id,
                Task.task_type == 'meeting',
                Task.start_time >= start_of_day,
                Task.start_time <= end_of_day
            ).count() > 0

            # Check for task activity
            had_task_activity = self.session.query(Task).filter(
                Task.user_id == user_id,
                Task.task_type == 'task',
                Task.updated_at >= start_of_day,
                Task.updated_at <= end_of_day
            ).count() > 0

            if had_meetings or had_task_activity:
                consecutive += 1
                current_date -= timedelta(days=1)
            else:
                break  # No work on this day, streak ends

        return consecutive


# ============================================================================
# INTEGRATION WITH RECOMMENDATION ENGINE
# ============================================================================

def get_complete_user_context(
    user_id: int,
    session: Session,
    date: datetime = None
) -> Dict:
    """
    Get complete user context for burnout analysis and recommendations:
    1. Calculate metrics from task database (automatic)
    2. Retrieve actual tasks for event-specific recommendations
    3. Retrieve actual meetings for event-specific recommendations
    4. Retrieve qualitative data (sentiment notes, meeting transcripts, task notes)

    This is what you'll call from your backend API.

    Args:
        user_id: User ID
        session: SQLAlchemy session
        date: Date to analyze (defaults to today)

    Returns:
        Dictionary with:
        - metrics: UserMetrics object (for burnout analysis)
        - tasks: List of actual tasks (for recommendations)
        - meetings: List of actual meetings (for recommendations)
        - qualitative_data: QualitativeData object (for sentiment analysis)
    """
    task_service = TaskDatabaseService(session=session)

    # Calculate metrics automatically from task database
    metrics = task_service.calculate_workload_metrics(user_id, date)

    # Get actual tasks and meetings for event-specific recommendations
    tasks = task_service.get_user_tasks(user_id)
    meetings = task_service.get_user_meetings(user_id, date)

    # Get qualitative data from database
    qualitative_dict = task_service.get_qualitative_data(user_id, date)

    # Import QualitativeData here to avoid circular imports
    from Analysis_engine_layer.sentiment_analyzer import QualitativeData

    qualitative_data = QualitativeData(
        meeting_transcripts=qualitative_dict['meeting_transcripts'],
        task_notes=qualitative_dict['task_notes'],
        user_check_ins=qualitative_dict['user_check_ins']
    )

    return {
        'metrics': metrics,              # Auto-calculated from database
        'tasks': tasks,                  # For event-specific recommendations
        'meetings': meetings,            # For event-specific recommendations
        'qualitative_data': qualitative_data  # For sentiment analysis
    }
# For usage examples, see: examples/complete_flow_example.py
