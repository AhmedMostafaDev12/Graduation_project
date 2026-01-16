"""
Shared Services Layer
=====================

This module provides direct function call interfaces to replace inter-service HTTP calls.
Eliminates network latency and simplifies deployment to a single port.

All services (Backend, Burnout, AI Companion, Task Extraction, Notebook Library)
can now communicate via direct function calls instead of HTTP requests.

Author: Sentry AI Team
Date: 2025
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# TASK OPERATIONS (replaces Backend HTTP calls)
# ============================================================================

class TaskService:
    """Task management operations - replaces HTTP calls to Backend service."""

    @staticmethod
    def get_all_tasks(user_id: int, db: Session, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all tasks for a user.

        Replaces: GET /api/tasks/
        """
        from backend_services.app import models

        query = db.query(models.Task).filter(models.Task.user_id == user_id)

        if status:
            query = query.filter(models.Task.status == status)

        tasks = query.all()

        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "created_at": task.created_at.isoformat() if hasattr(task, 'created_at') else None,
                "tags": task.tags if hasattr(task, 'tags') else []
            }
            for task in tasks
        ]

    @staticmethod
    def create_task(user_id: int, task_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Create a new task.

        Replaces: POST /api/tasks/ and POST /api/tasks/service/create
        Used by: Burnout Service (recommendation applier), Task Extraction
        """
        from backend_services.app import models

        # Parse due_date if it's a string
        due_date = task_data.get("due_date")
        if isinstance(due_date, str):
            try:
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except:
                due_date = None

        # Parse start_time if it's a string
        start_time = task_data.get("start_time")
        if isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            except:
                start_time = None

        # Parse end_time if it's a string
        end_time = task_data.get("end_time")
        if isinstance(end_time, str):
            try:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except:
                end_time = None

        task = models.Task(
            user_id=user_id,
            title=task_data.get("title"),
            description=task_data.get("description", ""),
            task_type=task_data.get("task_type", "task"),
            status=task_data.get("status", "Todo"),
            priority=task_data.get("priority", "Medium"),
            category=task_data.get("category"),
            due_date=due_date,
            start_time=start_time,
            end_time=end_time,
            assigned_to=task_data.get("assigned_to"),
            can_delegate=task_data.get("can_delegate", True),
            estimated_hours=task_data.get("estimated_hours"),
            is_recurring=task_data.get("is_recurring", False),
            is_optional=task_data.get("is_optional", False)
            # Note: tags field doesn't exist in Task model, so we skip it
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "category": task.category,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "start_time": task.start_time.isoformat() if task.start_time else None,
            "end_time": task.end_time.isoformat() if task.end_time else None,
            "estimated_hours": task.estimated_hours,
            "assigned_to": task.assigned_to,
            "created_at": task.created_at.isoformat() if hasattr(task, 'created_at') else None,
            "tags": task.tags if hasattr(task, 'tags') else []
        }

    @staticmethod
    def update_task(task_id: int, task_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Update an existing task."""
        from backend_services.app import models

        task = db.query(models.Task).filter(models.Task.id == task_id).first()

        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Update fields
        for key, value in task_data.items():
            if hasattr(task, key):
                setattr(task, key, value)

        db.commit()
        db.refresh(task)

        return {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "updated": True
        }

    @staticmethod
    def delete_task(task_id: int, db: Session) -> Dict[str, Any]:
        """Delete a task."""
        from backend_services.app import models

        task = db.query(models.Task).filter(models.Task.id == task_id).first()

        if not task:
            raise ValueError(f"Task {task_id} not found")

        db.delete(task)
        db.commit()

        return {"id": task_id, "deleted": True}


# ============================================================================
# BURNOUT OPERATIONS (replaces Burnout Service HTTP calls)
# ============================================================================

class BurnoutService:
    """Burnout analysis operations - replaces HTTP calls to Burnout Service."""

    @staticmethod
    def analyze_auto(user_id: int, db: Session, store_history: bool = True) -> Dict[str, Any]:
        """
        Trigger automatic burnout analysis.

        Replaces: POST /api/burnout/analyze-auto/{user_id}
        Used by: AI Companion
        """
        try:
            from app.services.burn_out_service.Analysis_engine_layer.burnout_engine import BurnoutEngine

            engine = BurnoutEngine(db)
            result = engine.analyze_burnout(user_id, store_history=store_history)

            return result
        except Exception as e:
            logger.error(f"Burnout analysis error: {e}")
            return {
                "error": str(e),
                "user_id": user_id,
                "status": "failed"
            }

    @staticmethod
    def get_workload_breakdown(user_id: int, db: Session) -> Dict[str, Any]:
        """
        Get workload breakdown and task statistics.

        Replaces: GET /api/workload/breakdown/{user_id}
        Used by: AI Companion
        """
        try:
            from app.services.burn_out_service.Analysis_engine_layer.Workload_analyzer import WorkloadAnalyzer

            analyzer = WorkloadAnalyzer(db)
            breakdown = analyzer.get_workload_breakdown(user_id)

            return breakdown
        except Exception as e:
            logger.error(f"Workload breakdown error: {e}")
            return {
                "error": str(e),
                "user_id": user_id,
                "status": "failed"
            }

    @staticmethod
    def get_latest_analysis(user_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """
        Get latest burnout analysis for a user.

        Replaces: GET /api/burnout/analysis/{user_id}
        Used by: AI Companion
        """
        try:
            from app.services.burn_out_service.user_profile.burnout_model import BurnoutAnalysis

            analysis = db.query(BurnoutAnalysis).filter(
                BurnoutAnalysis.user_id == user_id
            ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()

            if not analysis:
                return None

            return {
                "user_id": user_id,
                "burnout_score": analysis.final_score,
                "level": analysis.level,
                "components": analysis.components,
                "insights": analysis.insights,
                "analyzed_at": analysis.analyzed_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Get latest analysis error: {e}")
            return None


# ============================================================================
# RECOMMENDATION OPERATIONS (replaces Burnout Service HTTP calls)
# ============================================================================

class RecommendationService:
    """Recommendation operations - replaces HTTP calls to Burnout Service."""

    @staticmethod
    def get_for_user(user_id: int, db: Session) -> Dict[str, Any]:
        """
        Get recommendations for a user.

        Replaces: GET /api/recommendations/{user_id}
        Used by: AI Companion
        """
        try:
            from app.services.burn_out_service.recommendations_RAG.recommendation_engine import RecommendationEngine
            from app.services.burn_out_service.user_profile.burnout_model import BurnoutAnalysis

            # Get latest analysis
            latest_analysis = db.query(BurnoutAnalysis).filter(
                BurnoutAnalysis.user_id == user_id
            ).order_by(BurnoutAnalysis.analyzed_at.desc()).first()

            if not latest_analysis:
                return {"error": "No burnout analysis found for this user"}

            # Generate recommendations
            engine = RecommendationEngine()
            analysis_result = {
                'user_id': user_id,
                'burnout': {
                    'final_score': latest_analysis.final_score,
                    'level': latest_analysis.level,
                    'components': latest_analysis.components
                }
            }

            recommendations = engine.generate_recommendations(
                burnout_analysis=analysis_result,
                user_profile_context="",
                calendar_events=None,
                task_list=[]
            )

            return recommendations
        except Exception as e:
            logger.error(f"Get recommendations error: {e}")
            return {
                "error": str(e),
                "user_id": user_id,
                "status": "failed"
            }


# ============================================================================
# EXTRACTION OPERATIONS (replaces Task Extraction HTTP calls)
# ============================================================================

class ExtractionService:
    """Task extraction operations - replaces HTTP calls to Task Extraction Service."""

    @staticmethod
    def extract_from_text(text: str, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """
        Extract tasks from text and save to database.

        Replaces: POST /api/tasks/extract/text
        Used by: AI Companion
        """
        try:
            from app.services.task_extraction.text_extractor import TaskExtractor

            extractor = TaskExtractor()
            tasks = extractor.extract_tasks(text)

            # Save tasks to database
            saved_tasks = []
            for task_data in tasks:
                saved_task = TaskService.create_task(user_id, task_data, db)
                saved_tasks.append(saved_task)

            return saved_tasks
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            return []

    @staticmethod
    def extract_from_file(file_path: str, user_id: int, db: Session) -> Dict[str, Any]:
        """
        Extract tasks from file (audio, document, image, etc.).

        Uses the unified task extractor.
        """
        try:
            from app.services.task_extraction.unified_task_extractor import UnifiedTaskExtractor

            extractor = UnifiedTaskExtractor(db)
            result = extractor.process_file(file_path, user_id)

            return result
        except Exception as e:
            logger.error(f"File extraction error: {e}")
            return {
                "error": str(e),
                "tasks_extracted": 0,
                "tasks": []
            }


# ============================================================================
# USER OPERATIONS (Backend service)
# ============================================================================

class UserService:
    """User management operations."""

    @staticmethod
    def get_user(user_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        from backend_services.app import models

        user = db.query(models.User).filter(models.User.id == user_id).first()

        if not user:
            return None

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username if hasattr(user, 'username') else None,
            "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') else None
        }

    @staticmethod
    def create_user(user_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Create a new user."""
        from backend_services.app import models

        user = models.User(
            email=user_data.get("email"),
            username=user_data.get("username"),
            password_hash=user_data.get("password_hash")  # Should be hashed!
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "created": True
        }


# ============================================================================
# SENTIMENT/QUALITATIVE DATA OPERATIONS (Burnout service)
# ============================================================================

class SentimentService:
    """Sentiment analysis and qualitative data operations."""

    @staticmethod
    def save_emotional_entry(
        user_id: int,
        content: str,
        entry_type: str,
        db: Session
    ) -> Dict[str, Any]:
        """Save emotional/diary entry to qualitative_data table."""
        try:
            from app.services.burn_out_service.user_profile.models import QualitativeData
            from app.services.burn_out_service.core.sentiment_analyzer import SentimentAnalyzer

            # Analyze sentiment
            analyzer = SentimentAnalyzer()
            sentiment_result = analyzer.analyze_text(content)

            # Save to database
            entry = QualitativeData(
                user_id=user_id,
                entry_type=entry_type,
                content=content,
                sentiment_score=sentiment_result.get("sentiment_score"),
                emotional_themes=sentiment_result.get("themes", []),
                submitted_at=datetime.utcnow()
            )

            db.add(entry)
            db.commit()
            db.refresh(entry)

            return {
                "entry_id": entry.id,
                "sentiment": sentiment_result.get("sentiment_label"),
                "sentiment_score": sentiment_result.get("sentiment_score"),
                "themes": sentiment_result.get("themes", []),
                "saved": True
            }
        except Exception as e:
            logger.error(f"Save emotional entry error: {e}")
            return {
                "error": str(e),
                "saved": False
            }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_task_context_for_companion(user_id: int, db: Session) -> Dict[str, Any]:
    """
    Get comprehensive task context for AI Companion.

    Combines task statistics, burnout status, and recent recommendations.
    """
    context = {
        "workload": BurnoutService.get_workload_breakdown(user_id, db),
        "burnout_analysis": BurnoutService.get_latest_analysis(user_id, db),
    }

    return context


def apply_recommendation_to_tasks(
    recommendation: Dict[str, Any],
    user_id: int,
    db: Session
) -> Dict[str, Any]:
    """
    Apply a recommendation by creating tasks from action steps.

    Used by recommendation applier.
    """
    action_steps = recommendation.get("action_steps", [])

    created_tasks = []
    for step in action_steps:
        task_data = {
            "title": step,
            "description": f"Action from recommendation: {recommendation.get('title', 'Untitled')}",
            "status": "Todo",
            "priority": recommendation.get("priority", "Medium"),
            "tags": ["burnout-prevention", "auto-generated"]
        }

        task = TaskService.create_task(user_id, task_data, db)
        created_tasks.append(task)

    return {
        "recommendation_id": recommendation.get("id"),
        "tasks_created": len(created_tasks),
        "task_ids": [t["id"] for t in created_tasks],
        "tasks": created_tasks
    }
