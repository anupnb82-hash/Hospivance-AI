"""Alert Service for Hospivance AI."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from app.database.session import Session
from app.database.models import Alert


def format_dt(dt: Any) -> Optional[str]:
    if not dt:
        return None
    return dt.isoformat() if hasattr(dt, "isoformat") else str(dt)


def get_alerts(
    db: Session,
    risk_level: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Fetches system alerts with optional filtering."""
    query = db.query(Alert)
    if risk_level and risk_level.upper() != "ALL":
        query = query.filter(Alert.risk_level == risk_level.upper())
    if acknowledged is not None:
        query = query.filter(Alert.acknowledged == (1 if acknowledged else 0))
        
    alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": a.id,
            "timestamp": format_dt(a.timestamp),
            "department": a.department,
            "risk_level": a.risk_level,
            "title": a.title,
            "message": a.message,
            "metric_name": a.metric_name,
            "metric_value": a.metric_value,
            "threshold_value": a.threshold_value,
            "acknowledged": bool(a.acknowledged),
            "acknowledged_at": format_dt(a.acknowledged_at),
        }
        for a in alerts
    ]


def acknowledge_alert(db: Session, alert_id: int) -> Optional[Dict[str, Any]]:
    """Marks an alert as acknowledged by the charge nurse / bed coordinator."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None
    now_str = datetime.utcnow().isoformat()
    alert.acknowledged = 1
    alert.acknowledged_at = now_str
    # Update directly in sqlite if needed
    if hasattr(db, "conn"):
        cur = db.conn.cursor()
        cur.execute("UPDATE alerts SET acknowledged = 1, acknowledged_at = ? WHERE id = ?", (now_str, alert_id))
    db.commit()
    return {
        "id": alert.id,
        "department": alert.department,
        "risk_level": alert.risk_level,
        "title": alert.title,
        "acknowledged": True,
        "acknowledged_at": now_str,
    }


def create_simulated_alert(
    db: Session,
    department: str = "Emergency Room",
    risk_level: str = "HIGH",
    metric_name: str = "Occupancy Rate",
    metric_value: float = 94.2,
    threshold_value: float = 90.0,
    title: Optional[str] = None,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    """Generates an immediate operational alert for simulation & drills."""
    if not title:
        title = f"{risk_level} Risk Surge in {department}"
    if not message:
        message = f"Immediate attention required: {metric_name} hit {metric_value}% (threshold {threshold_value}%). Bottleneck mitigation activated."

    now_str = datetime.utcnow().isoformat()
    alert = Alert(
        timestamp=now_str,
        department=department,
        risk_level=risk_level.upper(),
        title=title,
        message=message,
        metric_name=metric_name,
        metric_value=metric_value,
        threshold_value=threshold_value,
        acknowledged=0,
    )
    db.add(alert)
    db.commit()
    return {
        "id": alert.id,
        "timestamp": now_str,
        "department": alert.department,
        "risk_level": alert.risk_level,
        "title": alert.title,
        "message": alert.message,
        "metric_name": alert.metric_name,
        "metric_value": alert.metric_value,
        "threshold_value": alert.threshold_value,
        "acknowledged": False,
    }
