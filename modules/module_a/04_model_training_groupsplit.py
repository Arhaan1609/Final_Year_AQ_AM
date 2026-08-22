"""
04_model_training_groupsplit.py — Group-Aware Model Training for EV Battery State Estimation.
Uses GroupShuffleSplit on chassis_no / vehicle_no to ensure strict zero-leakage evaluation.
Saves retrained models to models/module_a_groupsplit/.
"""

import os
import sys
import time
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib

# sklearn
from sklearn.ensemble import (
    RandomForestRegressor, GradientBoostingRegressor,
    ExtraTreesRegressor
)
from sklearn.svm import LinearSVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

import xgboost as xgb

# Set up paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELS_DIR = os.path.join(BASE_DIR, "models", "module_a_groupsplit")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed", "module_a_fleet_telematics")

TASK_CONFIG = {
    "SOC":     {"file": "features_soc.csv",     "target": "soc",                "group": "chassis_no"},
    "SOH":     {"file": "features_soh.csv",     "target": "soh",                "group": "chassis_no"},
    "RUL":     {"file": "features_rul.csv",     "target": "rul_proxy",          "group": "chassis_no"},
    "Mileage": {"file": "features_mileage.csv", "target": "mileage_per_charge", "group": "vehicle_no"},
}

EXCLUDE_COLS_ALWAYS = [
    "vehicle_no", "chassis_no", "imei", "timestamp",
    "start_time", "end_time", "source_file", "gps", "start_gps", "end_gps",
    "_id", "oem_model", "oem", "model", "alert_type", "drive_mode",
    "vehicle_status", "city", "duration", "vehicle_no.1",
]

EXCLUDE_COLS_PER_TASK = {
    "SOC": [
        "rolling_soc_5", "rolling_soc_10", "rolling_soc_20",
        "rolling_soc_std_5", "rolling_soc_std_10",
        "charge_state_pct", "voltage_deviation",
    ],
    "SOH": [
        "soc", "charge_state_pct",
        "rolling_soc_5", "rolling_soc_10", "rolling_soc_20",
        "rolling_soc_std_5", "rolling_soc_std_10",
        "soh_lag1", "soh_change",
    ],
    "RUL": [
        "charge_cycle_count", "cycle_usage_ratio", "charge_frequency",
    ],
    "Mileage": [
        "soc_drain", "soc_at_start", "soc_at_end",
        "distance_per_soc_drop", "soc_drain_rate", "energy_per_soc",
    ],
}


def _wrap_imputer(estimator):
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
        ("model",   estimator),
    ])


def get_ml_models():
    rs = 42
    return {
        "RandomForest": _wrap_imputer(RandomForestRegressor(
            n_estimators=100, max_depth=15, min_samples_leaf=5,
            max_features="sqrt", max_samples=0.5, random_state=rs, n_jobs=-1
        )),
        "GradientBoosting": _wrap_imputer(GradientBoostingRegressor(
            n_estimators=50, learning_rate=0.1, max_depth=4,
            min_samples_leaf=5, subsample=0.8, random_state=rs
        )),
        "XGBoost": _wrap_imputer(xgb.XGBRegressor(
            n_estimators=100, learning_rate=0.1, max_depth=6,
            subsample=0.8, colsample_bytree=0.8, random_state=rs,
            n_jobs=-1, tree_method="hist"
        )),
        "ExtraTrees": _wrap_imputer(ExtraTreesRegressor(
            n_estimators=100, max_depth=15, min_samples_leaf=5,
            max_features="sqrt", max_samples=0.5, bootstrap=True,
            random_state=rs, n_jobs=-1
        )),
        "DecisionTree": _wrap_imputer(DecisionTreeRegressor(
            max_depth=10, min_samples_leaf=5, random_state=rs
        )),
        "KNN": _wrap_imputer(KNeighborsRegressor(
            n_neighbors=10, weights="distance", n_jobs=-1
        )),
        "Ridge": _wrap_imputer(Ridge(alpha=1.0)),
        "Lasso": _wrap_imputer(Lasso(alpha=0.01)),
        "SVR": _wrap_imputer(LinearSVR(C=1.0, max_iter=2000, random_state=rs, dual=False, loss="squared_epsilon_insensitive")),
    }


def train_task_groupsplit(task: str):
    conf = TASK_CONFIG[task]
    fp = os.path.join(PROCESSED_DIR, conf["file"])
    target = conf["target"]
    group_col = conf["group"]

    print(f"\n{'='*70}\n  TRAINING TASK (GROUP-SPLIT): {task}\n{'='*70}")
    print(f"  Source: {fp}")
    print(f"  Target: {target} | Group Identifier: {group_col}")

    df = pd.read_csv(fp, low_memory=False)
    df = df.dropna(subset=[target, group_col])
    df = df.replace([np.inf, -np.inf], np.nan)

    task_exclude = EXCLUDE_COLS_PER_TASK.get(task, [])
    all_exclude = set(EXCLUDE_COLS_ALWAYS + task_exclude + [target])
    drop_cols = [c for c in df.columns if c in all_exclude]

    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    X = X.select_dtypes(include=np.number)
    col_medians = X.median().fillna(0)
    X = X.fillna(col_medians).fillna(0)
    y = df[target].values
    groups = df[group_col].values

    # Perform strict GroupShuffleSplit
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups=groups))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    train_groups = np.unique(groups[train_idx])
    test_groups = np.unique(groups[test_idx])

    print(f"  Dataset: {len(X):,} rows across {len(np.unique(groups))} unique {group_col}s")
    print(f"  Train:   {len(X_train):,} rows ({len(train_groups)} groups)")
    print(f"  Test:    {len(X_test):,} rows ({len(test_groups)} groups)")
    assert len(set(train_groups).intersection(set(test_groups))) == 0, "Group leakage detected!"
    print(f"  [OK] ZERO GROUP LEAKAGE: Test groups are 100% strictly held out.")

    task_model_dir = os.path.join(MODELS_DIR, task.lower())
    os.makedirs(task_model_dir, exist_ok=True)

    # Fit and save scaler
    scaler = StandardScaler()
    scaler.fit(X_train)
    joblib.dump(scaler, os.path.join(task_model_dir, f"scaler_{task.lower()}.pkl"))

    models = get_ml_models()
    results = {}
    best_name, best_r2, best_model = None, -999.0, None

    for name, model in models.items():
        t0 = time.time()
        # Fit model
        model.fit(X_train, y_train)
        elapsed = time.time() - t0

        # Predict on held-out test groups
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        results[name] = {"r2": r2, "mae": mae, "rmse": rmse, "time": elapsed}
        print(f"    {name:18s} | R² = {r2:7.4f} | MAE = {mae:7.3f} | RMSE = {rmse:7.3f} | Time = {elapsed:4.1f}s")

        # Save individual model
        model_path = os.path.join(task_model_dir, f"{task}_{name}.pkl")
        joblib.dump(model, model_path)

        if r2 > best_r2:
            best_r2 = r2
            best_name = name
            best_model = model

    # Save best model indicator
    with open(os.path.join(task_model_dir, f"{task}_best_model.txt"), "w") as f:
        f.write(f"Best Model: {best_name}\nR2: {best_r2:.4f}\n")

    print(f"  --> Champion Model ({task}): {best_name} (R² = {best_r2:.4f})")
    return results, best_name, best_r2


def main():
    print("=" * 75)
    print("  EV BATTERY INTELLIGENCE — GROUP-AWARE (ZERO LEAKAGE) RETRAINING")
    print("=" * 75)

    all_task_results = {}
    for task in ["SOC", "SOH", "RUL", "Mileage"]:
        res, best_name, best_r2 = train_task_groupsplit(task)
        all_task_results[task] = res

    print("\n" + "=" * 75)
    print("  ALL 4 TASKS RETRAINED WITH ZERO GROUP LEAKAGE")
    print(f"  Artifacts saved to: {MODELS_DIR}")
    print("=" * 75)


if __name__ == "__main__":
    main()
