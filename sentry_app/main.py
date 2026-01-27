"""
Unified Sentry AI - Complete System
===================================
Run with: uvicorn sentry_app.main:app --reload
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# IMPORT ROUTERS
# ============================================================================

# Backend Service Routers
# Formerly: backend_services.app.routers
from sentry_app.routers import user, task
from sentry_app.routers.auth import app_auth, google_auth, apple_auth, facebook_auth
from sentry_app.routers.uploads import upload_files
from sentry_app.routers.integrations import (
    sync_task,
    google_tasks,
    google_classroom,
    trello_cards,
    zoom_meetings
)

# Burnout Service Routers
# Formerly: app.services.burn_out_service...
from sentry_app.services.burn_out_service.api.routers import (
    burnout_router,
    workload_router,
    recommendations_router,
    profile_router,
    integrations_router
)
from sentry_app.services.burn_out_service.api.routers.recommendation_applier import router as recommendation_applier_router

# Task Extraction Router
from sentry_app.services.task_extraction.task_extraction_api import router as task_extraction_router

# Notebook Library Router
from sentry_app.services.notebook_library.router import router as notebook_router

# AI Companion Router
from sentry_app.services.ai_companion.router import router as companion_router

# ============================================================================
# APP DEFINITION
# ============================================================================

app = FastAPI(
    title="Sentry AI - Unified System",
    description="Unified Sentry AI API",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

# Backend
app.include_router(user.router)
app.include_router(task.router)
app.include_router(app_auth.router)
app.include_router(google_auth.router)
app.include_router(apple_auth.router)
app.include_router(facebook_auth.router)
app.include_router(upload_files.router)
app.include_router(sync_task.router)
app.include_router(google_tasks.router)
app.include_router(google_classroom.router)
app.include_router(trello_cards.router)
app.include_router(zoom_meetings.router)

# Burnout
app.include_router(burnout_router)
app.include_router(workload_router)
app.include_router(recommendations_router)
app.include_router(recommendation_applier_router)
app.include_router(profile_router)
app.include_router(integrations_router)

# Services
app.include_router(task_extraction_router)
app.include_router(companion_router)
app.include_router(notebook_router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "service": "Sentry AI - Unified System",
        "status": "operational",
        "version": "2.1.0"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": os.popen("date -u +%Y-%m-%dT%H:%M:%SZ").read().strip(),
        "version": "2.1.0",
        "services": {}
    }
    
    # Check Database
    try:
        from sqlalchemy import create_engine, text
        from sentry_app.database import SQLCHEMY_DATABASE_URL
        
        db_url = SQLCHEMY_DATABASE_URL or os.getenv("DATABASE_URL")
        
        if db_url:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            health_status["services"]["database"] = "connected"
        else:
            health_status["services"]["database"] = "not configured"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)[:50]}"
        health_status["status"] = "degraded"

    # Check AI APIs
    health_status["services"]["groq_api"] = "configured" if os.getenv("GROQ_API_KEY") else "not configured"
    health_status["services"]["voyage_ai"] = "configured" if os.getenv("VOYAGE_API_KEY") else "not configured"

    # Service Status (Assumed operational if server is running)
    health_status["services"]["backend"] = "operational"
    health_status["services"]["burnout"] = "operational"
    health_status["services"]["companion"] = "operational"
    health_status["services"]["extraction"] = "operational"
    health_status["services"]["notebooks"] = "operational"
        
    return health_status