"""
API Dependencies
================

Shared dependencies for FastAPI routers.
"""

from backend_services.app.database import get_db

__all__ = ['get_db']
