"""
Recommendation API Schemas
==========================

Pydantic models for recommendation endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class RecommendationItem(BaseModel):
    """Single recommendation."""
    recommendation_id: Optional[int] = Field(None, description="Unique recommendation ID")
    title: str = Field(..., description="Recommendation title")
    priority: str = Field(..., description="Priority level (HIGH, MEDIUM, LOW)")
    description: str = Field(..., description="Detailed description")
    action_steps: List[str] = Field(..., description="Actionable steps")
    expected_impact: str = Field(..., description="Expected impact description")

    # Optional event-specific info
    related_event: Optional[str] = Field(None, description="Related calendar event if applicable")
    related_task: Optional[str] = Field(None, description="Related task if applicable")


class RecommendationMetadata(BaseModel):
    """Recommendation generation metadata."""
    strategies_retrieved: int = Field(..., description="Number of strategies retrieved from vector DB")
    llm_model: str = Field(..., description="LLM model used")
    generation_time_seconds: Optional[float] = Field(None, description="Time taken to generate")


class RecommendationResponse(BaseModel):
    """Complete recommendation response."""
    user_id: int
    generated_at: str
    burnout_level: str = Field(..., description="User's current burnout level")

    # Recommendations
    recommendations: List[RecommendationItem] = Field(..., description="List of personalized recommendations")

    # Additional context
    reasoning: Optional[str] = Field(None, description="LLM reasoning for recommendations")
    metadata: Optional[RecommendationMetadata] = Field(None, description="Generation metadata")


# ============================================================================
# REQUEST MODELS
# ============================================================================

class RecommendationFeedbackRequest(BaseModel):
    """Request body for recommendation feedback."""
    user_id: int = Field(..., description="User ID")
    helpful: bool = Field(..., description="Was this recommendation helpful?")
    completed: bool = Field(False, description="Did user complete this recommendation?")
    impact_rating: Optional[int] = Field(None, ge=1, le=5, description="Impact rating 1-5")
    notes: Optional[str] = Field(None, description="Optional feedback notes")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "helpful": True,
                "completed": True,
                "impact_rating": 4,
                "notes": "This really helped reduce my stress"
            }
        }
