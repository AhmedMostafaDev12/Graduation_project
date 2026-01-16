"""
Shared Authentication for AI Services
=====================================

Re-exports authentication from backend services for use in AI endpoints.
This allows AI services to authenticate users via JWT tokens without
duplicating authentication logic.
"""

import sys
import os
from pathlib import Path

# Add backend_services to path
backend_path = Path(__file__).parent.parent.parent.parent / "backend_services"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Import authentication from backend
from app.oauth2 import get_current_user, oauth2_scheme
from app.models import User

__all__ = ['get_current_user', 'oauth2_scheme', 'User']
