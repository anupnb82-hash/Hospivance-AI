"""Bed Capacity Monitoring Routes for Hospivance AI."""

from fastapi import APIRouter, Depends
from app.database.session import Session
from app.database.models import func
from app.database.session import get_db
from app.database.models import AdmissionRecord, Department

router = APIRouter(prefix="/api/beds", tags=["Beds"])


@router.get("")
def get_bed_monitoring_data(db: Session = Depends(get_db)):
    """Returns department bed availability matrix and 14-day historical occupancy curves."""
    latest_date = db.query(func.max(AdmissionRecord.date)).scalar()
    if not latest_date:
        return {"status": "empty", "message": "No bed data available."}

    latest_records = (
        db.query(AdmissionRecord)
        .filter(AdmissionRecord.date == latest_date)
        .all()
    )

    # 14-day history dates
    dates_14d = [
        d[0]
        for d in db.query(AdmissionRecord.date)
        .distinct()
        .order_by(AdmissionRecord.date.desc())
        .limit(14)
        .all()
    ][::-1]

    # Department bed details
    dept_beds = []
    for r in latest_records:
        # Maintenance beds estimate (roughly 3-5% of total beds undergoing deep sanitization)
        maintenance_beds = max(1, int(r.total_beds * 0.04))
        operational_avail = max(0, r.available_beds - maintenance_beds)

        # Risk classification
        if r.occupancy_rate >= 90.0:
            risk = "HIGH"
        elif r.occupancy_rate >= 75.0:
            risk = "MODERATE"
        else:
            risk = "LOW"

        # Fetch 14-day historical occupancy curve for this department
        history = (
            db.query(AdmissionRecord.date, AdmissionRecord.occupancy_rate, AdmissionRecord.occupied_beds)
            .filter(AdmissionRecord.department_id == r.department_id, AdmissionRecord.date.in_(dates_14d))
            .order_by(AdmissionRecord.date.asc())
            .all()
        )
        curve = [
            {"date": h.date, "occupancy_rate": h.occupancy_rate, "occupied_beds": h.occupied_beds}
            for h in history
        ]

        # Target discharges to bring occupancy below 85% threshold
        target_discharges_to_safety = (
            max(0, r.occupied_beds - int(r.total_beds * 0.82))
            if r.occupancy_rate > 85.0
            else 0
        )

        dept_beds.append({
            "department_id": r.department_id,
            "department": r.department,
            "total_beds": r.total_beds,
            "occupied_beds": r.occupied_beds,
            "available_beds": r.available_beds,
            "maintenance_beds": maintenance_beds,
            "ready_for_admission": operational_avail,
            "occupancy_rate": r.occupancy_rate,
            "risk_level": risk,
            "target_discharges_needed": target_discharges_to_safety,
            "occupancy_history_14d": curve,
        })

    total_beds = sum(d["total_beds"] for d in dept_beds)
    total_occupied = sum(d["occupied_beds"] for d in dept_beds)
    total_available = sum(d["available_beds"] for d in dept_beds)
    overall_rate = round((total_occupied / total_beds) * 100.0, 1) if total_beds > 0 else 0

    return {
        "status": "success",
        "data_date": latest_date,
        "summary": {
            "total_hospital_beds": total_beds,
            "total_occupied": total_occupied,
            "total_available": total_available,
            "overall_occupancy_rate": overall_rate,
            "critical_departments_count": sum(1 for d in dept_beds if d["risk_level"] == "HIGH"),
        },
        "department_beds": dept_beds,
    }
