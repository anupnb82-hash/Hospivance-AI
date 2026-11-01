"""Dashboard Routes for Hospivance AI."""

from fastapi import APIRouter, Depends
from app.database.session import Session
from app.database.models import func
from app.database.session import get_db
from app.database.models import AdmissionRecord, Department, Alert
from app.services.forecast_service import get_forecast

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Provides high-level KPIs, 7-day trend, and department risk status."""
    # Find latest date in admission records
    latest_date = db.query(func.max(AdmissionRecord.date)).scalar()
    if not latest_date:
        return {"status": "empty", "message": "No admission records found."}

    # Fetch latest day records for all departments
    latest_records = (
        db.query(AdmissionRecord)
        .filter(AdmissionRecord.date == latest_date)
        .all()
    )

    total_beds = sum(r.total_beds for r in latest_records)
    total_occupied = sum(r.occupied_beds for r in latest_records)
    total_available = sum(r.available_beds for r in latest_records)
    overall_rate = round((total_occupied / total_beds) * 100.0, 1) if total_beds > 0 else 0

    er_rec = next((r for r in latest_records if "Emergency" in r.department), None)
    avg_wait = er_rec.avg_wait_time_minutes if er_rec else 42.0

    # Risk level determination
    if overall_rate >= 90.0:
        overall_risk = "HIGH"
    elif overall_rate >= 75.0:
        overall_risk = "MODERATE"
    else:
        overall_risk = "LOW"

    # Active alerts count
    high_risk_alerts = db.query(Alert).filter(Alert.risk_level == "HIGH", Alert.acknowledged == False).count()

    # Model forecast for next 24h
    forecast_24h = get_forecast(horizon_days=1)
    projected_adm_24h = forecast_24h["summary"]["total_projected_admissions"]

    # 7-day historical admission trend
    # Get last 7 distinct dates
    distinct_dates = [
        d[0]
        for d in db.query(AdmissionRecord.date)
        .distinct()
        .order_by(AdmissionRecord.date.desc())
        .limit(7)
        .all()
    ][::-1]

    trend_7d = []
    for d_str in distinct_dates:
        day_records = db.query(AdmissionRecord).filter(AdmissionRecord.date == d_str).all()
        adm_sum = sum(r.admissions_count for r in day_records)
        occ_sum = sum(r.occupied_beds for r in day_records)
        rate = round((occ_sum / total_beds) * 100.0, 1) if total_beds > 0 else 0
        trend_7d.append({
            "date": d_str,
            "admissions": adm_sum,
            "occupied_beds": occ_sum,
            "occupancy_rate": rate,
            "type": "actual",
        })

    # Add forecast to trend
    trend_7d.append({
        "date": forecast_24h["daily_timeline"][0]["date"],
        "admissions": projected_adm_24h,
        "occupied_beds": forecast_24h["daily_timeline"][0]["projected_occupied_beds"],
        "occupancy_rate": forecast_24h["daily_timeline"][0]["projected_occupancy_rate"],
        "type": "forecast",
    })

    # Department status grid
    departments_status = []
    for r in latest_records:
        if r.occupancy_rate >= 90.0:
            dept_risk = "HIGH"
        elif r.occupancy_rate >= 75.0:
            dept_risk = "MODERATE"
        else:
            dept_risk = "LOW"

        departments_status.append({
            "department_id": r.department_id,
            "name": r.department,
            "total_beds": r.total_beds,
            "occupied_beds": r.occupied_beds,
            "available_beds": r.available_beds,
            "occupancy_rate": r.occupancy_rate,
            "risk_level": dept_risk,
            "avg_wait_time": r.avg_wait_time_minutes,
            "diverted_ambulances": r.diverted_ambulances,
            "staff_on_duty": r.staff_on_duty,
        })

    # Sort departments: HIGH risk first, then descending occupancy
    departments_status.sort(key=lambda d: (0 if d["risk_level"] == "HIGH" else 1 if d["risk_level"] == "MODERATE" else 2, -d["occupancy_rate"]))

    return {
        "status": "success",
        "data_date": latest_date,
        "is_synthetic_data": True,
        "kpis": {
            "total_beds": total_beds,
            "total_occupied_beds": total_occupied,
            "total_available_beds": total_available,
            "overall_occupancy_rate": overall_rate,
            "overall_risk_level": overall_risk,
            "projected_24h_admissions": projected_adm_24h,
            "active_high_risk_alerts": high_risk_alerts,
            "er_avg_wait_minutes": avg_wait,
        },
        "trend_7day": trend_7d,
        "departments": departments_status,
        "model_performance": {
            "rmse": forecast_24h["summary"]["model_rmse"],
            "r2_score": forecast_24h["summary"]["model_r2"],
        }
    }
