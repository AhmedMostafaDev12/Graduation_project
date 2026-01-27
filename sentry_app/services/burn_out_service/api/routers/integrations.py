"""
Integration & Health Endpoints
===============================

FastAPI router for external integrations and system health checks.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List
from datetime import datetime
import os

from sentry_app.services.burn_out_service.api.dependencies import get_db, MAIN_DB_URL, VECTOR_DB_URL

router = APIRouter(prefix="/api", tags=["Integrations & Health"])


# ============================================================================
# INTEGRATION ENDPOINTS (Webhooks for external systems)
# ============================================================================

@router.post("/integrations/tasks/sync")
async def sync_tasks_from_external(
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for task management system integrations.

    Receives task data from external systems (Jira, Asana, Trello, etc.)
    and converts it to UserMetrics format.

    Expected payload structure (example for Jira):
    ```json
    {
        "user_id": 123,
        "tasks": [
            {
                "id": "PROJ-123",
                "title": "...",
                "status": "In Progress",
                "priority": "High",
                "due_date": "2025-12-20",
                "assigned_to": "user@example.com"
            }
        ],
        "source": "jira",
        "synced_at": "2025-12-18T10:00:00Z"
    }
    ```

    Returns:
        Confirmation and extracted metrics summary
    """
    try:
        user_id = payload.get('user_id')
        tasks = payload.get('tasks', [])
        source = payload.get('source', 'unknown')

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        # Extract metrics from tasks
        total_active = len([t for t in tasks if t.get('status') not in ['Done', 'Closed']])
        overdue = len([t for t in tasks if t.get('status') == 'Overdue'])

        # This would trigger a background task to analyze the data
        # background_tasks.add_task(analyze_user_burnout_from_sync, user_id, metrics)

        return {
            "status": "success",
            "message": f"Tasks synced from {source}",
            "user_id": user_id,
            "synced_at": datetime.utcnow().isoformat(),
            "metrics_summary": {
                "total_tasks": len(tasks),
                "active_tasks": total_active,
                "overdue_tasks": overdue
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync tasks: {str(e)}")


@router.post("/integrations/calendar/sync")
async def sync_calendar_events(
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for calendar system integrations.

    Receives calendar events from Google Calendar, Outlook, etc.
    and extracts meeting metrics.

    Expected payload structure:
    ```json
    {
        "user_id": 123,
        "events": [
            {
                "id": "event-123",
                "title": "Sprint Planning",
                "start_time": "2025-12-18T09:00:00Z",
                "end_time": "2025-12-18T10:30:00Z",
                "attendees": ["..."],
                "is_recurring": true,
                "is_optional": false
            }
        ],
        "source": "google_calendar",
        "synced_at": "2025-12-18T10:00:00Z"
    }
    ```

    Returns:
        Confirmation and extracted meeting metrics
    """
    try:
        user_id = payload.get('user_id')
        events = payload.get('events', [])
        source = payload.get('source', 'unknown')

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        # Extract meeting metrics
        total_meetings = len(events)
        total_hours = sum([
            (datetime.fromisoformat(e['end_time'].replace('Z', '+00:00')) -
             datetime.fromisoformat(e['start_time'].replace('Z', '+00:00'))).total_seconds() / 3600
            for e in events
        ])

        # Detect back-to-back meetings
        sorted_events = sorted(events, key=lambda e: e['start_time'])
        back_to_back = 0
        for i in range(len(sorted_events) - 1):
            end_current = datetime.fromisoformat(sorted_events[i]['end_time'].replace('Z', '+00:00'))
            start_next = datetime.fromisoformat(sorted_events[i+1]['start_time'].replace('Z', '+00:00'))
            if (start_next - end_current).total_seconds() < 300:  # Less than 5 minutes gap
                back_to_back += 1

        return {
            "status": "success",
            "message": f"Calendar events synced from {source}",
            "user_id": user_id,
            "synced_at": datetime.utcnow().isoformat(),
            "metrics_summary": {
                "total_events": total_meetings,
                "total_meeting_hours": round(total_hours, 2),
                "back_to_back_meetings": back_to_back
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync calendar: {str(e)}")


@router.post("/integrations/slack/messages")
async def sync_slack_messages(
    payload: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for Slack message integration.

    Receives user messages/status updates for sentiment analysis.

    Expected payload structure:
    ```json
    {
        "user_id": 123,
        "messages": [
            {
                "text": "Feeling overwhelmed with the deadline",
                "timestamp": "2025-12-18T10:00:00Z",
                "channel": "general"
            }
        ],
        "source": "slack",
        "synced_at": "2025-12-18T10:00:00Z"
    }
    ```

    Returns:
        Confirmation of message receipt
    """
    try:
        user_id = payload.get('user_id')
        messages = payload.get('messages', [])

        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required")

        # Extract text for sentiment analysis
        message_texts = [m.get('text', '') for m in messages]

        return {
            "status": "success",
            "message": "Slack messages received for sentiment analysis",
            "user_id": user_id,
            "synced_at": datetime.utcnow().isoformat(),
            "data_summary": {
                "total_messages": len(messages),
                "text_entries": len(message_texts)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync Slack messages: {str(e)}")


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@router.get("/health/databases")
async def check_database_health(db: Session = Depends(get_db)):
    """
    Check database connectivity and health.

    Tests:
    - Main database connection
    - Vector database connection (if URL is configured)
    - Response times

    Returns:
        Status of all database connections
    """
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "databases": {}
    }

    # Check main database
    try:
        start_time = datetime.utcnow()
        db.execute(text("SELECT 1"))
        end_time = datetime.utcnow()
        response_time_ms = (end_time - start_time).total_seconds() * 1000

        health_status["databases"]["main_db"] = {
            "status": "healthy",
            "url": MAIN_DB_URL.split('@')[1] if '@' in MAIN_DB_URL else 'configured',
            "response_time_ms": round(response_time_ms, 2)
        }
    except Exception as e:
        health_status["databases"]["main_db"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Check vector database
    try:
        import psycopg
        start_time = datetime.utcnow()
        conn = psycopg.connect(VECTOR_DB_URL)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        end_time = datetime.utcnow()
        response_time_ms = (end_time - start_time).total_seconds() * 1000

        health_status["databases"]["vector_db"] = {
            "status": "healthy",
            "url": VECTOR_DB_URL.split('@')[1] if '@' in VECTOR_DB_URL else 'configured',
            "response_time_ms": round(response_time_ms, 2)
        }
    except Exception as e:
        health_status["databases"]["vector_db"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Determine overall status
    all_healthy = all(
        db_info.get('status') == 'healthy'
        for db_info in health_status["databases"].values()
    )

    health_status["overall_status"] = "healthy" if all_healthy else "degraded"

    return health_status


@router.get("/health/llm")
async def check_llm_health():
    """
    Check Ollama/LLM service availability and response time.

    Tests:
    - LLM service connectivity
    - Model availability
    - Response time for simple query

    Returns:
        LLM service status
    """
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "llm_service": {}
    }

    try:
        from langchain_ollama import ChatOllama
        import time

        # Test simple query
        start_time = time.time()
        llm = ChatOllama(model="llama3.1:8b", temperature=0)
        response = llm.invoke("Say 'OK' if you're working")
        end_time = time.time()

        response_time_sec = end_time - start_time

        health_status["llm_service"] = {
            "status": "healthy",
            "model": "llama3.1:8b",
            "service": "ollama",
            "response_time_seconds": round(response_time_sec, 2),
            "test_response": response.content if hasattr(response, 'content') else str(response)
        }

    except Exception as e:
        health_status["llm_service"] = {
            "status": "unhealthy",
            "error": str(e),
            "troubleshooting": [
                "Ensure Ollama is running: ollama serve",
                "Ensure model is downloaded: ollama pull llama3.1:8b",
                "Check Ollama is accessible on default port"
            ]
        }

    health_status["overall_status"] = health_status["llm_service"]["status"]

    return health_status


@router.get("/health")
async def check_overall_health(db: Session = Depends(get_db)):
    """
    Comprehensive health check of all system components.

    Returns:
        - Overall system status
        - Individual component statuses
        - Recommendations if issues detected
    """
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": "unknown",
        "components": {}
    }

    # Check database health
    db_health = await check_database_health(db)
    health_status["components"]["databases"] = db_health["databases"]

    # Check LLM health
    llm_health = await check_llm_health()
    health_status["components"]["llm"] = llm_health["llm_service"]

    # Determine overall status
    db_status = db_health.get("overall_status", "unhealthy")
    llm_status = llm_health.get("overall_status", "unhealthy")

    if db_status == "healthy" and llm_status == "healthy":
        health_status["overall_status"] = "healthy"
    elif db_status == "healthy" or llm_status == "healthy":
        health_status["overall_status"] = "degraded"
    else:
        health_status["overall_status"] = "unhealthy"

    # Add recommendations if needed
    if health_status["overall_status"] != "healthy":
        health_status["recommendations"] = []

        if db_status != "healthy":
            health_status["recommendations"].append("Check database connectivity and configuration")

        if llm_status != "healthy":
            health_status["recommendations"].append("Ensure Ollama is running and model is downloaded")

    return health_status
