"""Synthetic Hospital Dataset Generator for Hospivance AI.

Generates realistic historical department-day time series data
with realistic day-of-week patterns, seasonal flu trends,
bed occupancy kinetics, and ambulance diversions.
Clearly marked as synthetic demo data.
"""

import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

DEPARTMENTS = [
    {"id": 1, "name": "Emergency Room", "beds": 80, "base_adm": 75, "adm_std": 14, "los_mean": 1.2},
    {"id": 2, "name": "Intensive Care Unit (ICU)", "beds": 30, "base_adm": 14, "adm_std": 3.5, "los_mean": 5.5},
    {"id": 3, "name": "General Ward", "beds": 150, "base_adm": 45, "adm_std": 8.0, "los_mean": 3.8},
    {"id": 4, "name": "Pediatrics", "beds": 45, "base_adm": 22, "adm_std": 5.0, "los_mean": 2.5},
    {"id": 5, "name": "Cardiology", "beds": 40, "base_adm": 18, "adm_std": 4.0, "los_mean": 3.2},
    {"id": 6, "name": "Surgery", "beds": 50, "base_adm": 20, "adm_std": 4.5, "los_mean": 3.0},
]


def is_us_holiday(dt: datetime) -> int:
    m, d = dt.month, dt.day
    if (m == 1 and d == 1) or (m == 7 and d == 4) or (m == 12 and d == 25):
        return 1
    if m == 11 and 22 <= d <= 28 and dt.weekday() == 3:  # Thanksgiving
        return 1
    if m == 5 and d >= 25 and dt.weekday() == 0:  # Memorial Day
        return 1
    if m == 9 and d <= 7 and dt.weekday() == 0:  # Labor Day
        return 1
    return 0


def generate_synthetic_hospital_data(
    num_days: int = 730,
    end_date: datetime = None,
    output_path: str = "data/hospital_daily.csv",
    seed: int = 42
) -> pd.DataFrame:
    """Generates synthetic daily data for all hospital departments."""
    np.random.seed(seed)
    if end_date is None:
        end_date = datetime.now()
    
    start_date = end_date - timedelta(days=num_days - 1)
    date_list = [start_date + timedelta(days=i) for i in range(num_days)]
    
    records = []
    dept_occupancy = {dept["name"]: int(dept["beds"] * 0.75) for dept in DEPARTMENTS}
    
    for dt in date_list:
        d_str = dt.strftime("%Y-%m-%d")
        dow = dt.weekday()  # 0=Monday, 6=Sunday
        is_wknd = 1 if dow >= 5 else 0
        holiday = is_us_holiday(dt)
        month = dt.month
        
        day_of_year = dt.timetuple().tm_yday
        flu_factor = max(0.0, np.sin((day_of_year + 15) * 2 * np.pi / 365.25))
        if month in [11, 12, 1, 2, 3]:
            flu_intensity = float(np.clip(0.4 + 0.6 * flu_factor + np.random.normal(0, 0.05), 0.0, 1.0))
        else:
            flu_intensity = float(np.clip(0.05 + 0.15 * flu_factor + np.random.normal(0, 0.03), 0.0, 0.4))
            
        temp_celsius = round(20 - 15 * np.cos(2 * np.pi * (month - 1) / 12) + np.random.normal(0, 3), 1)

        for dept in DEPARTMENTS:
            name = dept["name"]
            total_beds = dept["beds"]
            base_adm = dept["base_adm"]
            adm_std = dept["adm_std"]
            
            dow_multiplier = 1.0
            if name == "Emergency Room":
                dow_multiplier = 1.20 if is_wknd else 0.95
                flu_impact = flu_intensity * 25.0
            elif name == "Surgery":
                dow_multiplier = 0.25 if is_wknd else (1.25 if dow in [1, 2, 3] else 0.9)
                flu_impact = -flu_intensity * 3.0
            elif name == "Pediatrics":
                dow_multiplier = 1.1 if is_wknd else 0.98
                flu_impact = flu_intensity * 12.0
            elif name == "Cardiology":
                dow_multiplier = 0.85 if is_wknd else 1.05
                cold_impact = max(0, (10 - temp_celsius) * 0.4)
                flu_impact = flu_intensity * 4.0 + cold_impact
            elif name == "Intensive Care Unit (ICU)":
                dow_multiplier = 1.02 if is_wknd else 0.99
                flu_impact = flu_intensity * 6.0
            else:  # General Ward
                dow_multiplier = 0.88 if is_wknd else 1.04
                flu_impact = flu_intensity * 8.0

            if holiday:
                if name == "Surgery":
                    dow_multiplier *= 0.2
                elif name == "Emergency Room":
                    dow_multiplier *= 1.15

            expected_adm = (base_adm * dow_multiplier) + flu_impact
            admissions = int(max(1, np.random.normal(expected_adm, adm_std)))
            
            current_occ = dept_occupancy[name]
            los = dept["los_mean"]
            expected_discharges = current_occ / los
            discharge_dow_factor = 0.7 if is_wknd else 1.12
            discharges = int(max(0, np.random.normal(expected_discharges * discharge_dow_factor, adm_std * 0.6)))
            
            new_occ = max(5, min(total_beds, current_occ + admissions - discharges))
            dept_occupancy[name] = new_occ
            
            avail_beds = max(0, total_beds - new_occ)
            occ_rate = round((new_occ / total_beds) * 100.0, 1)
            
            if occ_rate >= 90.0:
                wait_time = round(np.random.uniform(65, 130), 1)
                diversions = int(np.random.poisson(3.5)) if name == "Emergency Room" else 0
            elif occ_rate >= 75.0:
                wait_time = round(np.random.uniform(35, 65), 1)
                diversions = int(np.random.poisson(0.8)) if name == "Emergency Room" else 0
            else:
                wait_time = round(np.random.uniform(15, 35), 1)
                diversions = 0

            base_staff = int(total_beds * 0.4)
            staff_on_duty = int(max(4, np.random.normal(base_staff * (0.85 if is_wknd else 1.0), 2.0)))

            records.append({
                "date": d_str,
                "department_id": dept["id"],
                "department": name,
                "total_beds": total_beds,
                "admissions_count": admissions,
                "discharges_count": discharges,
                "occupied_beds": new_occ,
                "available_beds": avail_beds,
                "occupancy_rate": occ_rate,
                "avg_wait_time_minutes": wait_time,
                "diverted_ambulances": diversions,
                "staff_on_duty": staff_on_duty,
                "day_of_week": dow,
                "is_weekend": is_wknd,
                "is_holiday": holiday,
                "month": month,
                "flu_season_intensity": round(flu_intensity, 3),
                "temperature_celsius": temp_celsius,
                "is_synthetic": True,
            })
            
    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} synthetic records across {len(DEPARTMENTS)} departments saved to {output_path}")
    return df


if __name__ == "__main__":
    generate_synthetic_hospital_data()
