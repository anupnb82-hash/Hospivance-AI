"""Reporting and Export Routes for Hospivance AI."""

from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.database.session import Session
from app.database.models import func
from app.database.session import get_db
from app.database.models import AdmissionRecord, Alert, Department
from app.services.forecast_service import get_forecast
from app.services.llm_service import get_recommendations

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/export")
def export_operations_report(db: Session = Depends(get_db)):
    """Exports full hospital operational status and AI bottleneck report as JSON."""
    latest_date = db.query(func.max(AdmissionRecord.date)).scalar()
    latest_records = db.query(AdmissionRecord).filter(AdmissionRecord.date == latest_date).all() if latest_date else []

    total_beds = sum(r.total_beds for r in latest_records)
    total_occ = sum(r.occupied_beds for r in latest_records)
    total_avail = sum(r.available_beds for r in latest_records)
    rate = round((total_occ / total_beds) * 100.0, 1) if total_beds > 0 else 0

    forecast = get_forecast(horizon_days=1)
    recs = get_recommendations(forecast)
    recent_alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(10).all()

    report_payload = {
        "report_title": "Hospivance AI - Hospital Bottleneck & Operations Report",
        "generated_at": datetime.utcnow().isoformat(),
        "data_date": latest_date,
        "is_synthetic_demonstration": True,
        "hospital_capacity": {
            "total_beds": total_beds,
            "total_occupied_beds": total_occ,
            "total_available_beds": total_avail,
            "system_occupancy_rate": rate,
            "system_risk_level": "HIGH" if rate >= 90 else "MODERATE" if rate >= 75 else "LOW",
        },
        "department_census": [
            {
                "department": r.department,
                "total_beds": r.total_beds,
                "occupied_beds": r.occupied_beds,
                "available_beds": r.available_beds,
                "occupancy_rate": r.occupancy_rate,
                "wait_time_minutes": r.avg_wait_time_minutes,
                "diverted_ambulances": r.diverted_ambulances,
            }
            for r in latest_records
        ],
        "ai_forecast_24h": forecast["summary"],
        "ai_recommendations": recs["recommendations"],
        "active_alerts_count": len([a for a in recent_alerts if not a.acknowledged]),
    }

    return JSONResponse(
        content=report_payload,
        headers={"Content-Disposition": f"attachment; filename=hospivance_report_{latest_date}.json"}
    )
