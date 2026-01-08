"""
API Schemas
===========

Pydantic models for request/response validation.
"""

from .burnout_schemas import *
from .workload_schemas import *
from .recommendation_schemas import *
from .profile_schemas import *

__all__ = [
    # Burnout schemas
    'BurnoutAnalysisResponse',
    'BurnoutTrendResponse',
    'BurnoutBreakdownResponse',
    'BurnoutInsightsResponse',
    'BurnoutSignalsResponse',
    'RecoveryPlanResponse',

    # Workload schemas
    'WorkloadMetricsRequest',
    'QualitativeDataRequest',
    'WorkloadBreakdownResponse',
    'AnalyzeRequest',

    # Recommendation schemas
    'RecommendationResponse',
    'RecommendationFeedbackRequest',

    # Profile schemas
    'UserProfileResponse',
    'UpdateProfileRequest',
]
