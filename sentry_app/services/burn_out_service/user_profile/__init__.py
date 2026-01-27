"""
User Profile Management System
===============================

This module manages user profiles, preferences, constraints, and behavioral patterns.

Main components:
- models.py: Database models
- schemas.py: Pydantic schemas for validation
- service.py: Business logic for profile management
- integration_services.py: Main burnout analysis orchestrator
"""

# Import main classes for easy access
from .integration_services import BurnoutSystemIntegration

__all__ = [
    'BurnoutSystemIntegration',
]
