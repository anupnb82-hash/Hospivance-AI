"""Forecast Service for Hospivance AI."""

from typing import Optional, Dict, Any
from ml.inference import predict_admissions


def get_forecast(horizon_days: int = 1, department: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves AI model forecasts for 24h (1d), 3d, or 7d horizons."""
    return predict_admissions(horizon_days=horizon_days, department_name=department)
