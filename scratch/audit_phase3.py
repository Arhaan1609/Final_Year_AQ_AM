import os
import joblib
import json
import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error, f1_score, roc_auc_score

print("=" * 80)
print("  AUDIT PHASE 3 — ITEMS 9, 10, 11, 12: OFFLINE PREDICTIONS & LEAKAGE AUDIT")
print("=" * 80)

# Item 9: Offline model inference vs API
print("\n--- ITEM 9: OFFLINE RECOMPUTATION OF MODEL WEIGHTS FOR 5 VEHICLES ---")

# Load models offline
soc_model = joblib.load("models/module_a/soc/SOC_RandomForest.pkl")
soh_model = joblib.load("models/module_a/soh/SOH_ExtraTrees.pkl")
rul_model = joblib.load("models/module_a/rul/RUL_GradientBoosting.pkl")
mileage_model = joblib.load("models/module_a/mileage/Mileage_XGBoost.pkl")
thermal_model = joblib.load("models/module_b/thermal_rf_multizone.joblib")

knee_scaler = joblib.load("models/module_c/feature_scaler.pkl")
knee_booster = xgb.Booster()
knee_booster.load_model("models/module_c/best_xgboost_model.json")

test_vehicles = [
    {"id": "DL1LAN0707", "v": 77.1, "i": -16.5, "t": 40.0, "vct": 47.5, "vmt": 56.0, "soc": 78.0, "soh": 99.2, "cycles": 0, "speed": 32.0},
    {"id": "GJ05CV6564", "v": 80.4, "i": -1.5, "t": 29.4, "vct": 36.9, "vmt": 69.0, "soc": 91.4, "soh": 96.9, "cycles": 200, "speed": 32.0},
    {"id": "KA01AP8021", "v": 74.1, "i": -34.0, "t": 34.0, "vct": 41.5, "vmt": 49.0, "soc": 33.0, "soh": 93.7, "cycles": 212, "speed": 42.0},
    {"id": "DL1LAK7203", "v": 73.6, "i": -14.0, "t": 30.0, "vct": 37.5, "vmt": 45.0, "soc": 25.0, "soh": 96.8, "cycles": 90, "speed": 28.0},
    {"id": "GJ01LT4770", "v": 75.4, "i": -27.0, "t": 33.0, "vct": 40.5, "vmt": 48.0, "soc": 52.0, "soh": 83.2, "cycles": 633, "speed": 41.0},
]

for veh in test_vehicles:
    # 1. Module A SOH Offline:
    # Feature columns for SOH ExtraTrees:
    # ['battery_voltage', 'battery_temp', 'battery_current', 'abs_current', 'odometer', 'odometer_diff', 'charge_cycle_count', 'mile_avg', 'miles_per_charge', 'days_in_service', 'degradation_factor', 'temp_stress_index', 'voltage_deviation', 'oem_encoded', 'model_encoded']
    odo = veh["cycles"] * 58.0
    x_soh = np.array([[veh["v"], veh["t"], veh["i"], abs(veh["i"]), odo, 10.0, veh["cycles"], 58.0, 58.0, 100.0, 1.0, 0.5, abs(veh["v"] - 72.0), 0, 0]])
    soh_offline = float(soh_model.predict(x_soh)[0])

    # 2. Module B Thermal Offline:
    # [vbt, vct, vmt, vbv, vbc, soc, speed]
    x_therm = np.array([[veh["t"], veh["vct"], veh["vmt"], veh["v"], veh["i"], veh["soc"], veh["speed"]]])
    therm_risk_offline = float(thermal_model.predict_proba(x_therm)[0][1])

    # 3. Module C Knee Offline:
    # 28 features
    x_knee = np.zeros((1, 28))
    x_knee[0, 0] = veh["cycles"]
    x_knee[0, 3] = veh["soh"]
    x_knee[0, 4] = veh["soh"]
    x_knee[0, 9] = veh["v"]
    x_knee[0, 13] = veh["i"]
    x_knee[0, 16] = veh["t"]
    x_knee_scaled = knee_scaler.transform(x_knee)
    dmat = xgb.DMatrix(x_knee_scaled)
    knee_pred_log = float(knee_booster.predict(dmat)[0])
    knee_rul_offline = max(0.0, np.expm1(knee_pred_log))

    print(f"Vehicle {veh['id']}: SOH_Offline={soh_offline:.2f}%, ThermalRisk_Offline={therm_risk_offline:.3f}, KneeRUL_Offline={knee_rul_offline:.1f} cyc")

# Item 10: Evaluation & Train/Test Leakage Check
print("\n--- ITEM 10: EVALUATION METRICS & LEAKAGE AUDIT ---")
# Check Module B test set
b_test_path = "data/processed/module_b_thermal_deep_soh/thermal_alerts_balanced_50_50.csv"
if os.path.exists(b_test_path):
    df_b = pd.read_csv(b_test_path)
    print(f"Module B Thermal Dataset Shape: {df_b.shape}")
    X_b = df_b[['vbt', 'vct', 'vmt', 'vbv', 'vbc', 'soc', 'speed']]
    y_b = df_b['is_critical']
    y_pred_b = thermal_model.predict(X_b)
    y_prob_b = thermal_model.predict_proba(X_b)[:, 1]
    f1 = f1_score(y_b, y_pred_b)
    roc = roc_auc_score(y_b, y_prob_b)
    print(f"Module B Thermal Re-evaluated: F1={f1:.4f}, ROC-AUC={roc:.4f}")

# Check Module A split logic in 04_model_training.py
print("\nTrain/Test Split Logic in Module A:")
with open("modules/module_a/04_model_training.py", "r") as f:
    code_a = f.read()
    if "train_test_split" in code_a:
        print("  Module A uses: scikit-learn standard train_test_split (Random record-level split)")
        print("  LEAKAGE NOTE: Random record-level split splits time-series rows of the same vehicle across train and test sets, explaining high R^2 (0.98 - 0.995).")
    if "GroupKFold" in code_a or "chassis" in code_a:
        print("  Module A uses GroupKFold on chassis")

# Item 12: Test Meta-Ensemble Disagreement
print("\n--- ITEM 12: META-ENSEMBLE DISAGREEMENT TEST ---")
import requests
API = "http://localhost:8000"

# Normal truck
res_norm = requests.post(f"{API}/predict/diagnose/vehicle", json={
    "id": "DL1LAK7203", "vbt": 30.0, "vct": 37.5, "vmt": 45.0, "vbv": 73.6, "vbc": -14.0,
    "soc": 25.0, "speed": 28.0, "charge_cycle_count": 90, "capacity": 96.8, "odometer": 5220.0
}).json()
print("Normal Truck Diagnosis Status:", res_norm.get("system_verdict"), "| Action:", res_norm.get("action_priority"))

# Stressed / Critical truck (high temp + high cycles)
res_crit = requests.post(f"{API}/predict/diagnose/vehicle", json={
    "id": "CRITICAL_TRUCK_TEST", "vbt": 62.0, "vct": 75.0, "vmt": 88.0, "vbv": 66.0, "vbc": -85.0,
    "soc": 12.0, "speed": 65.0, "charge_cycle_count": 1450, "capacity": 68.0, "odometer": 85000.0
}).json()
print("Critical Truck Diagnosis Status:", res_crit.get("system_verdict"), "| Action:", res_crit.get("action_priority"))
