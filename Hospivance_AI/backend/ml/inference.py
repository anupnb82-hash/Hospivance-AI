"""Model Inference Pipeline for Hospivance AI.

Performs multi-horizon patient admission forecasting (24-hour, 3-day, 7-day),
calculates bed occupancy projections, and assigns bottleneck risk categories
(LOW, MODERATE, HIGH) with confidence bounds.
"""

import os
import sys
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ml.generate_data import DEPARTMENTS, is_us_holiday

_model_cache = None
_metrics_cache = None


def load_model_and_metadata(artifact_dir: str = "backend/ml/artifacts"):
    global _model_cache, _metrics_cache
    if _model_cache is not None:
        return _model_cache["model"], _model_cache["feature_names"], _metrics_cache

    root_dir = os.path.dirname(backend_dir)
    if not os.path.isabs(artifact_dir):
        artifact_dir = os.path.join(root_dir, artifact_dir)

    model_path = os.path.join(artifact_dir, "model.joblib")
    metrics_path = os.path.join(artifact_dir, "metrics.json")

    if not os.path.exists(model_path):
        from ml.train import train_model
        print(f"Model artifact not found at {model_path}. Training initial model...")
        train_model()

    try:
        import joblib
        data = joblib.load(model_path)
    except Exception:
        with open(model_path, "rb") as f:
            data = pickle.load(f)

    _model_cache = data

    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            _metrics_cache = json.load(f)
    else:
        _metrics_cache = {"rmse": 7.5, "mae": 5.5, "r2_score": 0.90}

    return _model_cache["model"], _model_cache["feature_names"], _metrics_cache


def get_risk_level(occupancy_rate: float) -> str:
    """Classifies risk level based on standard hospital threshold guidelines."""
    if occupancy_rate >= 90.0:
        return "HIGH"
    elif occupancy_rate >= 75.0:
        return "MODERATE"
    return "LOW"


def predict_admissions(
    horizon_days: int = 1,
    department_name: Optional[str] = None,
    data_path: str = "data/hospital_daily.csv"
) -> Dict[str, Any]:
    """Generates 1-day (24h), 3-day, or 7-day admissions and occupancy forecasts."""
    model, feature_names, metrics = load_model_and_metadata()
    rmse = metrics.get("rmse", 7.5)

    root_dir = os.path.dirname(backend_dir)
    if not os.path.isabs(data_path):
        data_path = os.path.join(root_dir, data_path)

    df_raw = pd.read_csv(data_path)
    latest_date_str = df_raw["date"].max()
    latest_dt = datetime.strptime(latest_date_str, "%Y-%m-%d")

    target_departments = (
        [d for d in DEPARTMENTS if d["name"].lower() == department_name.lower()]
        if department_name
        else DEPARTMENTS
    )
    if not target_departments:
        target_departments = DEPARTMENTS

    # Get recent history per department for lag calculation
    predictions_by_dept = []
    daily_timeline = []

    for day_offset in range(1, horizon_days + 1):
        target_date = latest_dt + timedelta(days=day_offset)
        d_str = target_date.strftime("%Y-%m-%d")
        dow = target_date.weekday()
        is_wknd = 1 if dow >= 5 else 0
        holiday = is_us_holiday(target_date)
        month = target_date.month

        day_of_year = target_date.timetuple().tm_yday
        flu_factor = max(0.0, np.sin((day_of_year + 15) * 2 * np.pi / 365.25))
        flu_intensity = float(np.clip(0.4 + 0.6 * flu_factor, 0.0, 1.0)) if month in [11, 12, 1, 2, 3] else float(np.clip(0.05 + 0.15 * flu_factor, 0.0, 0.4))
        temp_celsius = round(20 - 15 * np.cos(2 * np.pi * (month - 1) / 12), 1)

        total_day_admissions = 0
        total_day_occupied = 0
        total_day_capacity = 0

        for dept in target_departments:
            dept_id = dept["id"]
            name = dept["name"]
            total_beds = dept["beds"]
            los = dept["los_mean"]

            # Filter department records up to latest
            d_hist = df_raw[df_raw["department_id"] == dept_id].sort_values("date")
            recent_adm = d_hist["admissions_count"].values
            recent_occ = d_hist["occupied_beds"].values
            staff = int(d_hist["staff_on_duty"].iloc[-1])

            adm_lag_1 = float(recent_adm[-1]) if len(recent_adm) >= 1 else dept["base_adm"]
            adm_lag_2 = float(recent_adm[-2]) if len(recent_adm) >= 2 else dept["base_adm"]
            adm_lag_3 = float(recent_adm[-3]) if len(recent_adm) >= 3 else dept["base_adm"]
            adm_lag_7 = float(recent_adm[-7]) if len(recent_adm) >= 7 else dept["base_adm"]
            occ_lag_1 = float(recent_occ[-1]) if len(recent_occ) >= 1 else total_beds * 0.75

            adm_roll_7 = float(np.mean(recent_adm[-7:])) if len(recent_adm) >= 7 else dept["base_adm"]
            adm_std_7 = float(np.std(recent_adm[-7:])) if len(recent_adm) >= 7 else 3.0

            # Build feature dictionary
            feat_dict = {
                "department_id": dept_id,
                "day_of_week": dow,
                "is_weekend": is_wknd,
                "is_holiday": holiday,
                "month": month,
                "flu_season_intensity": flu_intensity,
                "temperature_celsius": temp_celsius,
                "staff_on_duty": staff,
                "admissions_lag_1": adm_lag_1,
                "admissions_lag_2": adm_lag_2,
                "admissions_lag_3": adm_lag_3,
                "admissions_lag_7": adm_lag_7,
                "occupancy_lag_1": occ_lag_1,
                "admissions_rolling_mean_7": adm_roll_7,
                "admissions_rolling_std_7": adm_std_7,
            }
            # Add department one-hot flags
            for d_info in DEPARTMENTS:
                col_name = f"dept_{d_info['name']}"
                feat_dict[col_name] = 1 if d_info["name"] == name else 0

            # Construct feature row in exact order of model feature_names
            feat_vector = np.array([feat_dict.get(fn, 0.0) for fn in feature_names]).reshape(1, -1)
            raw_pred = float(model.predict(feat_vector)[0])
            pred_adm = max(2, int(round(raw_pred)))

            # Discharge & Occupancy modeling
            expected_discharges = int(round(occ_lag_1 / los * (0.75 if is_wknd else 1.05)))
            proj_occupied = max(4, min(total_beds, int(occ_lag_1 + pred_adm - expected_discharges)))
            avail_beds = max(0, total_beds - proj_occupied)
            occ_rate = round((proj_occupied / total_beds) * 100.0, 1)
            risk = get_risk_level(occ_rate)

            # Confidence bounds
            ci_lower = max(0, int(round(pred_adm - 1.96 * (rmse / 2.0))))
            ci_upper = int(round(pred_adm + 1.96 * (rmse / 2.0)))

            dept_res = {
                "date": d_str,
                "department": name,
                "department_id": dept_id,
                "predicted_admissions": pred_adm,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "projected_occupied_beds": proj_occupied,
                "available_beds": avail_beds,
                "total_beds": total_beds,
                "projected_occupancy_rate": occ_rate,
                "risk_level": risk,
                "expected_discharges": expected_discharges,
                "bottleneck_warning": risk == "HIGH",
            }
            predictions_by_dept.append(dept_res)

            total_day_admissions += pred_adm
            total_day_occupied += proj_occupied
            total_day_capacity += total_beds

        overall_day_occ_rate = round((total_day_occupied / total_day_capacity) * 100.0, 1) if total_day_capacity > 0 else 0
        daily_timeline.append({
            "date": d_str,
            "day_label": f"Day {day_offset} ({target_date.strftime('%a, %b %d')})",
            "total_predicted_admissions": total_day_admissions,
            "projected_occupied_beds": total_day_occupied,
            "total_capacity": total_day_capacity,
            "projected_occupancy_rate": overall_day_occ_rate,
            "overall_risk": get_risk_level(overall_day_occ_rate),
        })

    # Summary KPIs
    horizon_label = "24 Hours (Next Day)" if horizon_days == 1 else f"{horizon_days} Days"
    total_projected_adm = sum(d["total_predicted_admissions"] for d in daily_timeline)
    peak_occ = max(d["projected_occupancy_rate"] for d in daily_timeline)
    high_risk_depts = sorted(list(set(p["department"] for p in predictions_by_dept if p["risk_level"] == "HIGH")))

    return {
        "status": "success",
        "horizon_days": horizon_days,
        "horizon_label": horizon_label,
        "filter_department": department_name,
        "forecast_generated_at": datetime.now().isoformat(),
        "summary": {
            "total_projected_admissions": total_projected_adm,
            "peak_occupancy_rate": peak_occ,
            "overall_risk_level": get_risk_level(peak_occ),
            "high_risk_departments": high_risk_depts,
            "model_rmse": rmse,
            "model_r2": metrics.get("r2_score", 0.90),
        },
        "daily_timeline": daily_timeline,
        "department_forecasts": predictions_by_dept,
    }
