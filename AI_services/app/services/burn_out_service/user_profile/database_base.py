"""
Shared Database Base
====================

Shared declarative base for all burnout service models.
This ensures all tables share the same metadata and can reference each other.

Author: Sentry AI Team
Date: 2025
"""

from sqlalchemy.ext.declarative import declarative_base

# Shared base for all models in the burnout service
Base = declarative_base()
