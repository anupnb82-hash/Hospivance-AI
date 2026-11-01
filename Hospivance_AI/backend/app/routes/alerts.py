"""Operational Alerts Routes for Hospivance AI."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from app.database.session import Session
from app.database.session import get_db
from app.services.alert_service import get_alerts, acknowledge_alert, create_simulated_alert

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


class SimulateAlertRequest(BaseModel):
    department: str = "Emergency Room"
    risk_level: str = "HIGH"
    metric_name: str = "Occupancy Rate"
    metric_value: float = 95.5
    threshold_value: float = 90.0
    title: Optional[str] = None
    message: Optional[str] = None


@router.get("")
def list_alerts(
    risk_level: Optional[str] = Query(None, description="Filter: ALL, HIGH, MODERATE, LOW"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledgment status"),
    db: Session = Depends(get_db)
):
    """Retrieves operational overcrowding alerts."""
    return get_alerts(db, risk_level=risk_level, acknowledged=acknowledged)


@router.post("/{alert_id}/ack")
def acknowledge_operational_alert(alert_id: int, db: Session = Depends(get_db)):
    """Acknowledges an active bottleneck alert."""
    result = acknowledge_alert(db, alert_id=alert_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found.")
    return {"status": "success", "alert": result}


@router.post("/simulate")
def trigger_simulated_surge_alert(payload: SimulateAlertRequest, db: Session = Depends(get_db)):
    """Triggers an operational alert for surge response simulation."""
    alert = create_simulated_alert(
        db,
        department=payload.department,
        risk_level=payload.risk_level,
        metric_name=payload.metric_name,
        metric_value=payload.metric_value,
        threshold_value=payload.threshold_value,
        title=payload.title,
        message=payload.message,
    )
    return {"status": "success", "alert": alert}
