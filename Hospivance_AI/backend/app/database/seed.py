"""Database Seeder for Hospivance AI."""

import os
import uuid
from datetime import datetime, timedelta
import pandas as pd
from app.database.session import Session
from app.database.models import Department, AdmissionRecord, Alert, Encounter
from ml.generate_data import DEPARTMENTS, generate_synthetic_hospital_data


def seed_database_if_empty(db: Session, csv_path: str = "data/hospital_daily.csv"):
    """Seeds departments, historical records, alerts, and FHIR encounters if empty."""
    dept_count = db.query(Department).count()
    if dept_count == 0:
        print("Seeding departments table...")
        for d in DEPARTMENTS:
            db.add(Department(
                id=d["id"],
                name=d["name"],
                total_beds=d["beds"],
                target_occupancy_pct=80.0,
                critical_occupancy_pct=90.0,
            ))
        db.commit()

    record_count = db.query(AdmissionRecord).count()
    if record_count == 0:
        if not os.path.exists(csv_path):
            print(f"Generating synthetic dataset at {csv_path}...")
            generate_synthetic_hospital_data(output_path=csv_path)

        print(f"Seeding historical admission records from {csv_path}...")
        df = pd.read_csv(csv_path)
        records = []
        for _, row in df.iterrows():
            records.append(AdmissionRecord(
                date=str(row["date"]),
                department_id=int(row["department_id"]),
                department=str(row["department"]),
                total_beds=int(row["total_beds"]),
                admissions_count=int(row["admissions_count"]),
                discharges_count=int(row["discharges_count"]),
                occupied_beds=int(row["occupied_beds"]),
                available_beds=int(row["available_beds"]),
                occupancy_rate=float(row["occupancy_rate"]),
                avg_wait_time_minutes=float(row["avg_wait_time_minutes"]),
                diverted_ambulances=int(row["diverted_ambulances"]),
                staff_on_duty=int(row["staff_on_duty"]),
                day_of_week=int(row["day_of_week"]),
                is_weekend=int(row["is_weekend"]),
                is_holiday=int(row["is_holiday"]),
                month=int(row["month"]),
                flu_season_intensity=float(row["flu_season_intensity"]),
                temperature_celsius=float(row["temperature_celsius"]),
                is_synthetic=True,
            ))
        db.bulk_save_objects(records)
        db.commit()
        print(f"Seeded {len(records)} admission records.")

    alert_count = db.query(Alert).count()
    if alert_count == 0:
        print("Seeding initial active operational alerts...")
        now = datetime.utcnow()
        sample_alerts = [
            Alert(
                timestamp=now - timedelta(minutes=18),
                department="Intensive Care Unit (ICU)",
                risk_level="HIGH",
                title="Critical ICU Bed Saturation Impending",
                message="ICU occupancy reached 96.7% (29/30 beds occupied). Projected 24h demand exceeds capacity by 3 beds. Immediate step-down review needed.",
                metric_name="Occupancy Rate",
                metric_value=96.7,
                threshold_value=90.0,
                acknowledged=False,
            ),
            Alert(
                timestamp=now - timedelta(minutes=42),
                department="Emergency Room",
                risk_level="HIGH",
                title="Severe ER Boarding & Wait Time Surge",
                message="ER average wait time escalated to 84.5 minutes. Ambulance diversion protocol on standby if general ward transfers are not expedited.",
                metric_name="Wait Time",
                metric_value=84.5,
                threshold_value=60.0,
                acknowledged=False,
            ),
            Alert(
                timestamp=now - timedelta(hours=1, minutes=15),
                department="General Ward",
                risk_level="MODERATE",
                title="General Ward Capacity Nearing Threshold",
                message="Occupancy is currently at 88.0% (132/150 beds). Afternoon elective surgical admissions may trigger high-risk surge.",
                metric_name="Occupancy Rate",
                metric_value=88.0,
                threshold_value=85.0,
                acknowledged=False,
            ),
            Alert(
                timestamp=now - timedelta(hours=2, minutes=30),
                department="Pediatrics",
                risk_level="LOW",
                title="Pediatrics Morning Discharge Complete",
                message="12 morning pediatric discharges cleared. Department operating smoothly at 64.4% occupancy.",
                metric_name="Occupancy Rate",
                metric_value=64.4,
                threshold_value=75.0,
                acknowledged=True,
                acknowledged_at=now - timedelta(hours=2),
            ),
        ]
        db.add_all(sample_alerts)
        db.commit()

    encounter_count = db.query(Encounter).count()
    if encounter_count == 0:
        print("Seeding synthetic FHIR encounters...")
        now = datetime.utcnow()
        sample_reasons = [
            ("Emergency Room", "Acute chest pain evaluation", 2),
            ("Emergency Room", "Severe respiratory distress", 1),
            ("Intensive Care Unit (ICU)", "Septic shock hemodynamics", 1),
            ("General Ward", "Post-operative orthopedic recovery", 3),
            ("Pediatrics", "Acute pediatric wheezing / RSV", 2),
            ("Cardiology", "Decompensated heart failure", 2),
            ("Surgery", "Laparoscopic cholecystectomy", 3),
        ]
        encs = []
        for i, (dept_name, reason, acuity) in enumerate(sample_reasons):
            encs.append(Encounter(
                encounter_id=f"ENC-{uuid.uuid4().hex[:8].upper()}",
                patient_pseudonym=f"SYNTH-PT-{1000 + i}",
                department=dept_name,
                status="in-progress" if i < 5 else "finished",
                admit_date=now - timedelta(hours=2 * (i + 1)),
                discharge_date=now - timedelta(hours=1) if i >= 5 else None,
                acuity_level=acuity,
                reason_for_visit=reason,
                is_synthetic=True,
            ))
        db.add_all(encs)
        db.commit()
        print(f"Seeded {len(encs)} synthetic FHIR encounters.")
