"""
API Dependencies
================

Shared dependencies for FastAPI routers.
"""

from sentry_app.database import get_db

__all__ = ['get_db']
