"""Department Overcrowding Routes for Hospivance AI."""

from fastapi import APIRouter, Depends, Query
from app.database.session import Session
from app.database.models import func
from typing import Optional
from app.database.session import get_db
from app.database.models import AdmissionRecord

router = APIRouter(prefix="/api/departments", tags=["Departments"])


@router.get("")
def get_department_series(
    department_id: Optional[int] = Query(None, description="Optional department filter"),
    days: int = Query(30, ge=7, le=90, description="History window in days"),
    db: Session = Depends(get_db)
):
    """Provides 30-day historical time series and overcrowding metrics by department."""
    # Get recent dates
    recent_dates = [
        d[0]
        for d in db.query(AdmissionRecord.date)
        .distinct()
        .order_by(AdmissionRecord.date.desc())
        .limit(days)
        .all()
    ][::-1]

    query = db.query(AdmissionRecord).filter(AdmissionRecord.date.in_(recent_dates))
    if department_id is not None:
        query = query.filter(AdmissionRecord.department_id == department_id)

    records = query.order_by(AdmissionRecord.date.asc()).all()

    # Group by department
    departments_dict = {}
    for r in records:
        if r.department not in departments_dict:
            departments_dict[r.department] = {
                "department_id": r.department_id,
                "name": r.department,
                "total_beds": r.total_beds,
                "series": [],
            }
        departments_dict[r.department]["series"].append({
            "date": r.date,
            "admissions": r.admissions_count,
            "discharges": r.discharges_count,
            "occupied_beds": r.occupied_beds,
            "available_beds": r.available_beds,
            "occupancy_rate": r.occupancy_rate,
            "wait_time": r.avg_wait_time_minutes,
            "diverted_ambulances": r.diverted_ambulances,
            "staff_on_duty": r.staff_on_duty,
        })

    # Calculate department bottleneck statistics
    dept_summaries = []
    for name, data in departments_dict.items():
        series = data["series"]
        avg_occ = round(sum(s["occupancy_rate"] for s in series) / len(series), 1) if series else 0
        peak_occ = max(s["occupancy_rate"] for s in series) if series else 0
        high_risk_days = sum(1 for s in series if s["occupancy_rate"] >= 90.0)
        avg_wait = round(sum(s["wait_time"] for s in series) / len(series), 1) if series else 0
        total_adm = sum(s["admissions"] for s in series)
        total_disch = sum(s["discharges"] for s in series)

        dept_summaries.append({
            "department_id": data["department_id"],
            "name": name,
            "total_beds": data["total_beds"],
            "average_occupancy_rate": avg_occ,
            "peak_occupancy_rate": peak_occ,
            "high_risk_days_count": high_risk_days,
            "overcrowding_frequency_pct": round((high_risk_days / len(series)) * 100.0, 1) if series else 0,
            "average_wait_time": avg_wait,
            "total_admissions": total_adm,
            "total_discharges": total_disch,
            "net_flow": total_adm - total_disch,
            "series": series,
        })

    return {
        "status": "success",
        "window_days": days,
        "departments_count": len(dept_summaries),
        "departments": dept_summaries,
    }
