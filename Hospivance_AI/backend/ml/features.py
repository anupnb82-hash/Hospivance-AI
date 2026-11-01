"""Feature Engineering Pipeline for Hospivance AI.

Builds chronological lag features, rolling statistics, calendar indicators,
and department encodings without lookahead bias / data leakage.
"""

from typing import Tuple, List
import pandas as pd
import numpy as np


def create_feature_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Creates lag and rolling window features per department chronologically."""
    df_sorted = df.sort_values(by=["department_id", "date"]).copy()
    grouped = df_sorted.groupby("department_id")
    
    df_sorted["admissions_lag_1"] = grouped["admissions_count"].shift(1)
    df_sorted["admissions_lag_2"] = grouped["admissions_count"].shift(2)
    df_sorted["admissions_lag_3"] = grouped["admissions_count"].shift(3)
    df_sorted["admissions_lag_7"] = grouped["admissions_count"].shift(7)
    df_sorted["occupancy_lag_1"] = grouped["occupied_beds"].shift(1)
    
    df_sorted["admissions_rolling_mean_7"] = (
        grouped["admissions_count"]
        .shift(1)
        .rolling(window=7, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )
    df_sorted["admissions_rolling_std_7"] = (
        grouped["admissions_count"]
        .shift(1)
        .rolling(window=7, min_periods=1)
        .std()
        .fillna(0.0)
        .reset_index(level=0, drop=True)
    )
    
    df_clean = df_sorted.dropna().copy()
    
    dept_dummies = pd.get_dummies(df_clean["department"], prefix="dept", drop_first=False)
    for col in dept_dummies.columns:
        dept_dummies[col] = dept_dummies[col].astype(int)
        
    df_final = pd.concat([df_clean, dept_dummies], axis=1)
    return df_final


def chronological_train_test_split(
    df: pd.DataFrame,
    test_ratio: float = 0.20
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Splits data strictly by date to prevent future lookahead leakage."""
    unique_dates = sorted(df["date"].unique())
    split_idx = int(len(unique_dates) * (1.0 - test_ratio))
    split_date = unique_dates[split_idx]
    
    train_df = df[df["date"] < split_date].copy()
    test_df = df[df["date"] >= split_date].copy()
    
    print(f"Chronological split at date {split_date}:")
    print(f"  Training set:   {train_df['date'].min()} to {train_df['date'].max()} ({len(train_df)} rows)")
    print(f"  Validation set: {test_df['date'].min()} to {test_df['date'].max()} ({len(test_df)} rows)")
    return train_df, test_df


def get_feature_matrix_and_target(
    df: pd.DataFrame,
    target_col: str = "admissions_count"
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Extracts X, y arrays and feature names."""
    base_feats = [
        "department_id",
        "day_of_week",
        "is_weekend",
        "is_holiday",
        "month",
        "flu_season_intensity",
        "temperature_celsius",
        "staff_on_duty",
        "admissions_lag_1",
        "admissions_lag_2",
        "admissions_lag_3",
        "admissions_lag_7",
        "occupancy_lag_1",
        "admissions_rolling_mean_7",
        "admissions_rolling_std_7",
    ]
    dept_feats = sorted([c for c in df.columns if c.startswith("dept_")])
    all_features = base_feats + dept_feats
    
    X = df[all_features].values.astype(np.float64)
    y = df[target_col].values.astype(np.float64)
    return X, y, all_features
