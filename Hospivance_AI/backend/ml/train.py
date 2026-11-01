"""Model Training Pipeline for Hospivance AI.

Trains an admission forecasting model using a chronological train/test split.
Evaluates MAE, RMSE, R2 score, and MAPE without data leakage.
Saves model artifact and metrics to disk.
"""

import os
import sys
import json
import pickle
from datetime import datetime
from typing import Dict, Any
import numpy as np
import pandas as pd

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from ml.features import (
    create_feature_pipeline,
    chronological_train_test_split,
    get_feature_matrix_and_target,
)
from ml.models import FallbackRandomForest

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0
    mask = y_true > 0
    mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)
    return {
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "r2_score": round(r2, 4),
        "mape": round(mape, 2),
    }


def train_model(
    data_path: str = "data/hospital_daily.csv",
    artifact_dir: str = "backend/ml/artifacts",
) -> Dict[str, Any]:
    root_dir = os.path.dirname(backend_dir)
    if not os.path.isabs(data_path):
        data_path = os.path.join(root_dir, data_path)
    if not os.path.isabs(artifact_dir):
        artifact_dir = os.path.join(root_dir, artifact_dir)

    if not os.path.exists(data_path):
        from ml.generate_data import generate_synthetic_hospital_data
        print(f"Data file {data_path} not found. Generating synthetic data...")
        generate_synthetic_hospital_data(output_path=data_path)

    df_raw = pd.read_csv(data_path)
    print(f"Loaded {len(df_raw)} records from {data_path}")

    df_features = create_feature_pipeline(df_raw)
    train_df, test_df = chronological_train_test_split(df_features, test_ratio=0.20)
    
    X_train, y_train, feature_names = get_feature_matrix_and_target(train_df)
    X_test, y_test, _ = get_feature_matrix_and_target(test_df)

    print(f"Training on {len(X_train)} samples across {len(feature_names)} features...")

    if SKLEARN_AVAILABLE:
        print("Using scikit-learn RandomForestRegressor...")
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=12,
            min_samples_split=6,
            random_state=42,
            n_jobs=-1
        )
    else:
        print("Scikit-learn not in environment. Using high-performance ensemble...")
        model = FallbackRandomForest(n_estimators=25, max_depth=7, min_samples_split=8)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics = calculate_metrics(y_test, y_pred)
    
    metrics.update({
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "split_date": str(test_df["date"].min()),
        "trained_at": datetime.now().isoformat(),
        "algorithm": "RandomForestRegressor" if SKLEARN_AVAILABLE else "RandomForestEnsemble",
        "data_split": "Chronological (No Data Leakage)",
    })

    if hasattr(model, "feature_importances_") and model.feature_importances_ is not None:
        importances = dict(zip(feature_names, [round(float(v), 4) for v in model.feature_importances_]))
        metrics["feature_importances"] = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True)[:10])

    print("\n--- Model Evaluation Scorecard ---")
    print(f"  MAE:       {metrics['mae']} patients")
    print(f"  RMSE:      {metrics['rmse']} patients")
    print(f"  R² Score:  {metrics['r2_score']}")
    print(f"  MAPE:      {metrics['mape']}%")
    print("----------------------------------\n")

    os.makedirs(artifact_dir, exist_ok=True)
    model_path = os.path.join(artifact_dir, "model.joblib")
    metrics_path = os.path.join(artifact_dir, "metrics.json")

    try:
        import joblib
        joblib.dump({"model": model, "feature_names": feature_names}, model_path)
    except Exception:
        with open(model_path, "wb") as f:
            pickle.dump({"model": model, "feature_names": feature_names}, f)

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Artifacts saved to {model_path} and {metrics_path}")
    return metrics


if __name__ == "__main__":
    train_model()
