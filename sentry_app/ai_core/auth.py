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

# Import authentication from backend
from sentry_app.oauth2 import get_current_user, oauth2_scheme
from sentry_app.models import User

__all__ = ['get_current_user', 'oauth2_scheme', 'User']
