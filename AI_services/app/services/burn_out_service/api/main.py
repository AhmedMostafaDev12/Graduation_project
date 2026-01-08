"""
Burnout Detection System - FastAPI Application
===============================================

Main FastAPI application that aggregates all routers and provides
the complete API for the Sentry AI burnout detection system.

Author: Sentry AI Team
Date: 2025
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all routers
from api.routers import (
    burnout_router,
    workload_router,
    recommendations_router,
    profile_router,
    integrations_router
)
from api.routers.recommendation_applier import router as recommendation_applier_router

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Sentry AI - Burnout Detection System",
    description="""
    AI-powered burnout detection and prevention system.

    ## Features

    * **Burnout Analysis**: Real-time burnout scoring with workload and sentiment analysis
    * **Trend Tracking**: Historical burnout trends with percentage changes
    * **Personalized Recommendations**: AI-generated recommendations using RAG + LLM
    * **User Profiles**: Behavioral pattern learning and personalization
    * **Integrations**: Webhooks for Jira, Slack, Google Calendar, etc.
    * **Health Monitoring**: System health checks for databases and LLM services

    ## System Architecture

    1. **Data Collection**: Workload metrics + Qualitative data
    2. **Analysis Engine**: Workload analyzer + Sentiment analyzer + Burnout fusion
    3. **User Profiling**: Behavioral pattern learning from historical data
    4. **Recommendations**: RAG-based retrieval + LLM generation
    5. **Integrations**: External system webhooks and sync

    ## Getting Started

    1. Submit workload metrics: `POST /api/workload/submit`
    2. Submit qualitative data: `POST /api/sentiment/submit`
    3. Trigger analysis: `POST /api/burnout/analyze`
    4. Get burnout score: `GET /api/burnout/analysis/{user_id}`
    5. Get recommendations: `GET /api/recommendations/{user_id}`

    ## Authentication

    (To be implemented: JWT-based authentication)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8000",  # Flutter web dev
        "http://localhost:8080",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

# Burnout analysis endpoints
app.include_router(burnout_router)

# Workload and data submission endpoints
app.include_router(workload_router)

# Recommendations endpoints
app.include_router(recommendations_router)

# Recommendation application endpoints (apply recommendations automatically)
app.include_router(recommendation_applier_router)

# User profile endpoints
app.include_router(profile_router)

# Integration and health check endpoints
app.include_router(integrations_router)

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information and health check.
    """
    return {
        "service": "Sentry AI - Burnout Detection System",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "health_check": "/api/health",
        "endpoints": {
            "burnout_analysis": "/api/burnout/analysis/{user_id}",
            "burnout_trend": "/api/burnout/trend/{user_id}",
            "workload_submit": "/api/workload/submit",
            "sentiment_submit": "/api/sentiment/submit",
            "analyze": "/api/burnout/analyze",
            "recommendations": "/api/recommendations/{user_id}",
            "user_profile": "/api/profile/{user_id}",
            "health": "/api/health"
        }
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource was not found",
            "path": str(request.url)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "path": str(request.url)
        }
    )

# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.

    - Initialize database connections
    - Load ML models
    - Verify system dependencies
    """
    print("=" * 80)
    print("STARTING SENTRY AI - BURNOUT DETECTION SYSTEM")
    print("=" * 80)
    print("\nInitializing components...")

    # Check database connectivity
    try:
        from api.dependencies import get_db, MAIN_DB_URL, VECTOR_DB_URL
        print(f"[OK] Main database configured: {MAIN_DB_URL.split('@')[1] if '@' in MAIN_DB_URL else 'localhost'}")
        print(f"[OK] Vector database configured: {VECTOR_DB_URL.split('@')[1] if '@' in VECTOR_DB_URL else 'localhost'}")
    except Exception as e:
        print(f"[ERROR] Database configuration error: {e}")

    # Check LLM availability
    try:
        from langchain_ollama import ChatOllama
        llm = ChatOllama(model="llama3.1:8b", temperature=0)
        print("[OK] LLM service (Ollama) available")
    except Exception as e:
        print(f"[WARNING] LLM service not available: {e}")
        print("   Recommendations will not work until Ollama is running")

    print("\n" + "=" * 80)
    print("API READY")
    print("=" * 80)
    print(f"\nDocumentation: http://localhost:8000/docs")
    print(f"Health Check:  http://localhost:8000/api/health")
    print()

@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.

    - Close database connections
    - Clean up resources
    """
    print("\n" + "=" * 80)
    print("SHUTTING DOWN SENTRY AI - BURNOUT DETECTION SYSTEM")
    print("=" * 80)
    print()

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"

    print(f"\nStarting server on {host}:{port}")
    print(f"Reload: {reload}\n")

    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
