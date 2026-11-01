"""Resource Allocation Recommendations Routes for Hospivance AI."""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.forecast_service import get_forecast
from app.services.llm_service import get_recommendations

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


class RecommendationRequest(BaseModel):
    horizon_days: int = Field(1, description="Forecast horizon for recommendation generation: 1, 3, or 7")
    department: Optional[str] = Field(None, description="Optional department filter")


@router.post("")
def generate_resource_recommendations(payload: RecommendationRequest = RecommendationRequest()):
    """Generates AI-backed or clinical-rule resource allocation recommendations."""
    # Run forecast first
    forecast = get_forecast(horizon_days=payload.horizon_days, department=payload.department)
    # Generate recommendations from LLM (Gemini/OpenAI) or rule-based fallback
    briefing_and_recs = get_recommendations(forecast)

    return {
        "status": "success",
        "horizon_days": payload.horizon_days,
        "forecast_summary": forecast["summary"],
        "ai_engine": briefing_and_recs["source"],
        "model_used": briefing_and_recs.get("model", "Clinical Heuristic"),
        "executive_briefing": briefing_and_recs["executive_briefing"],
        "recommendations": briefing_and_recs["recommendations"],
        "action_items_count": briefing_and_recs["action_items_count"],
    }
