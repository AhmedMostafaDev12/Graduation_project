"""
API Dependencies
================

FastAPI dependencies for request handling.
"""

from .database import get_db, MAIN_DB_URL, VECTOR_DB_URL

__all__ = ['get_db', 'MAIN_DB_URL', 'VECTOR_DB_URL']
