"""
API Routers
===========

All FastAPI routers for the burnout detection system.
"""

from .burnout import router as burnout_router
from .workload import router as workload_router
from .recommendations import router as recommendations_router
from .profile import router as profile_router
from .integrations import router as integrations_router

__all__ = [
    'burnout_router',
    'workload_router',
    'recommendations_router',
    'profile_router',
    'integrations_router'
]
