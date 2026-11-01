"""Prediction and Forecasting Routes for Hospivance AI."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.forecast_service import get_forecast

router = APIRouter(prefix="/api/predict", tags=["Predictions"])


class PredictRequest(BaseModel):
    horizon_days: int = Field(1, description="Forecast horizon: 1 (24 hours), 3 (3 days), or 7 (7 days)")
    department: Optional[str] = Field(None, description="Optional department filter, e.g. 'Emergency Room'")


@router.post("")
def predict_patient_admissions(payload: PredictRequest):
    """Executes AI admission forecasting pipeline for 24-hour, 3-day, or 7-day windows."""
    if payload.horizon_days not in [1, 3, 7]:
        raise HTTPException(
            status_code=400,
            detail="horizon_days must be either 1 (24 hours), 3 (3 days), or 7 (7 days)."
        )

    try:
        result = get_forecast(horizon_days=payload.horizon_days, department=payload.department)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failure: {str(e)}")
