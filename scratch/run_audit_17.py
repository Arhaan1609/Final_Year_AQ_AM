import requests
import json
import numpy as np
import pandas as pd
import joblib
import os

API = "http://localhost:8000"

old_soh_model_path = os.path.abspath("models/module_a/soh/SOH_ExtraTrees.pkl")
old_model = joblib.load(old_soh_model_path) if os.path.exists(old_soh_model_path) else None

with open("frontend/public/data/fleet_vehicles.json", "r") as f:
    all_fleet = json.load(f)

fleet_by_id = {v["id"]: v for v in all_fleet}

selected_specs = [
    # 2 Original vehicles
    {"id": "DL1LAN0707", "chassis": "MAT486022RZD10219", "soh_0": 99.20, "cycles": 0, "voltage": 77.1, "temp": 40.0, "current": -16.5, "model_desc": "Tata Ace EV (Brand New)"},
    {"id": "GJ05CV6564", "chassis": "CN-GJ05CV6564",    "soh_0": 96.90, "cycles": 200, "voltage": 80.4, "temp": 29.4, "current": -1.5, "model_desc": "Euler HiLoad EV (Mid Life)"},
    
    # Low Baseline cohort (79% - 87% SOH)
    {"id": "DL1LAL8594", "chassis": "MD9EMHDL22H217002", "soh_0": 79.54, "cycles": 950, "voltage": 72.8, "temp": 38.5, "current": -24.0, "model_desc": "High-Cycle Logistics Fleet"},
    {"id": "DL1LAL8590", "chassis": "MD9EMHDL22H217018", "soh_0": 81.47, "cycles": 880, "voltage": 73.1, "temp": 37.2, "current": -22.5, "model_desc": "High-Cycle Delivery Van"},
    {"id": "DL1LAL8588", "chassis": "MD9EMHDL22J217074", "soh_0": 79.54, "cycles": 920, "voltage": 72.5, "temp": 39.0, "current": -25.0, "model_desc": "Heavy Route Fleet"},
    {"id": "DL1LAL8580", "chassis": "MAT486022RZD08112", "soh_0": 83.20, "cycles": 820, "voltage": 73.4, "temp": 36.5, "current": -20.0, "model_desc": "Urban Cargo Van"},
    {"id": "DL1LAL8575", "chassis": "MD9EMHDL22J217083", "soh_0": 87.20, "cycles": 650, "voltage": 74.2, "temp": 35.0, "current": -18.0, "model_desc": "Mid-Heavy Cargo"},

    # Mid Baseline cohort (89% - 94% SOH)
    {"id": "DL1LAK7280", "chassis": "MD9EMHDL23B217240", "soh_0": 89.87, "cycles": 520, "voltage": 75.0, "temp": 33.5, "current": -17.5, "model_desc": "Standard Commercial"},
    {"id": "DL1LAK7265", "chassis": "MD9EMHDL22H217011", "soh_0": 91.08, "cycles": 460, "voltage": 75.5, "temp": 32.8, "current": -16.0, "model_desc": "Fleet Delivery"},
    {"id": "DL1LAK7250", "chassis": "MD9EMHDL23D217211", "soh_0": 91.20, "cycles": 440, "voltage": 75.8, "temp": 32.0, "current": -15.5, "model_desc": "Regional Transit"},
    {"id": "DL1LAK7245", "chassis": "MD9EMHDL23E217001", "soh_0": 92.87, "cycles": 380, "voltage": 76.2, "temp": 31.5, "current": -15.0, "model_desc": "Suburban Fleet"},
    {"id": "DL1LAK7235", "chassis": "MAT486022RZD09412", "soh_0": 93.30, "cycles": 320, "voltage": 76.5, "temp": 31.0, "current": -14.5, "model_desc": "Metro Route Transit"},

    # High Baseline cohort (95% - 99.5% SOH)
    {"id": "DL1LAK7222", "chassis": "MD9EMHDL23C217305", "soh_0": 95.75, "cycles": 210, "voltage": 77.2, "temp": 30.2, "current": -14.0, "model_desc": "Light Duty EV"},
    {"id": "DL1LAK7216", "chassis": "MD9EMHDL23D217087", "soh_0": 96.37, "cycles": 180, "voltage": 77.6, "temp": 29.8, "current": -13.5, "model_desc": "Express Logistics"},
    {"id": "DL1LAK7207", "chassis": "MD9EMHDL23D217075", "soh_0": 96.77, "cycles": 150, "voltage": 77.8, "temp": 29.5, "current": -13.0, "model_desc": "City Shuttle"},
    {"id": "DL1LAK7203", "chassis": "MD9EMHDL23D217303", "soh_0": 97.84, "cycles": 90,  "voltage": 78.5, "temp": 28.5, "current": -12.0, "model_desc": "Short Haul Courier"},
    {"id": "DL1LAN0101", "chassis": "MD9EMHDL23D217132", "soh_0": 99.45, "cycles": 15,  "voltage": 79.2, "temp": 27.8, "current": -10.0, "model_desc": "New Commission Asset"},
]

results = []

for s in selected_specs:
    payload = {
        "battery_voltage": s["voltage"],
        "battery_temp": s["temp"],
        "battery_current": s["current"],
        "charge_cycle_count": s["cycles"],
        "odometer": s["cycles"] * 58.0,
        "initial_soh": s["soh_0"],
        "soh": s["soh_0"],
        "chassis_no": s["chassis"],
        "vehicle_id": s["id"]
    }
    
    # 1. Query live API (Calibrated Delta-SOH model)
    res = requests.post(f"{API}/predict/soh", json=payload).json()
    reconstructed_soh = res.get("prediction", 0.0)
    
    # Calculate predicted delta_soh
    pred_delta = reconstructed_soh - s["soh_0"]
    
    # 2. Predict with OLD Row-Split model
    if old_model:
        cols = list(old_model.named_steps["imputer"].feature_names_in_)
        d_old = {
            "battery_voltage": s["voltage"], "battery_temp": s["temp"],
            "battery_current": s["current"], "abs_current": abs(s["current"]),
            "odometer": s["cycles"] * 58.0, "odometer_diff": 0.0,
            "charge_cycle_count": s["cycles"], "mile_avg": 45.0,
            "miles_per_charge": 115.0, "days_in_service": max(1, s["cycles"] * 1.25),
            "degradation_factor": min(1.0, s["cycles"] / 1400.0),
            "temp_stress_index": max(0.0, (s["temp"] - 25.0) / 30.0),
            "voltage_deviation": s["voltage"] - 72.0,
            "oem_encoded": 0, "model_encoded": 0
        }
        df_old = pd.DataFrame([{c: d_old.get(c, 0.0) for c in cols}])
        old_pred = float(old_model.predict(df_old)[0])
    else:
        old_pred = 90.0

    results.append({
        "vehicle_id": s["id"],
        "chassis_no": s["chassis"],
        "cycles": s["cycles"],
        "soh_0": s["soh_0"],
        "pred_delta": pred_delta,
        "reconstructed_soh": reconstructed_soh,
        "old_rowsplit_soh": old_pred,
        "model_used": res.get("model_used", "Calibrated XGBoost")
    })

df_res = pd.DataFrame(results)

out = []
out.append("=" * 110)
out.append("17-VEHICLE SPOT-CHECK: CALIBRATED BASELINE MODEL VS OLD ROW-SPLIT MODEL")
out.append("=" * 110)
header = f"{'Vehicle ID':12s} | {'Chassis No':18s} | {'Cycles':6s} | {'SOH_0 (Base)':12s} | {'Pred d_SOH':10s} | {'New SOH':8s} | {'Old SOH':8s} | {'Model Used':18s}"
out.append(header)
out.append("-" * 110)
for _, r in df_res.iterrows():
    out.append(f"{r['vehicle_id']:12s} | {r['chassis_no']:18s} | {r['cycles']:6.0f} | {r['soh_0']:10.2f}%  | {r['pred_delta']:+8.2f}% | {r['reconstructed_soh']:7.2f}% | {r['old_rowsplit_soh']:7.2f}% | {r['model_used']:18s}")

out.append("\n" + "=" * 110)
out.append("SPREAD & VARIANCE ANALYSIS")
out.append("=" * 110)
out.append(f"Commissioning Baseline SOH_0 : Min = {df_res['soh_0'].min():.2f}%, Max = {df_res['soh_0'].max():.2f}%, Range = {df_res['soh_0'].max() - df_res['soh_0'].min():.2f}%, Std = {df_res['soh_0'].std():.2f}%")
out.append(f"Predicted Delta (d_SOH)      : Min = {df_res['pred_delta'].min():+.2f}%, Max = {df_res['pred_delta'].max():+.2f}%, Range = {df_res['pred_delta'].max() - df_res['pred_delta'].min():.2f}%, Std = {df_res['pred_delta'].std():.2f}%")
out.append(f"NEW Reconstructed SOH        : Min = {df_res['reconstructed_soh'].min():.2f}%, Max = {df_res['reconstructed_soh'].max():.2f}%, Range = {df_res['reconstructed_soh'].max() - df_res['reconstructed_soh'].min():.2f}%, Std = {df_res['reconstructed_soh'].std():.2f}%")
out.append(f"OLD Row-Split Model SOH      : Min = {df_res['old_rowsplit_soh'].min():.2f}%, Max = {df_res['old_rowsplit_soh'].max():.2f}%, Range = {df_res['old_rowsplit_soh'].max() - df_res['old_rowsplit_soh'].min():.2f}%, Std = {df_res['old_rowsplit_soh'].std():.2f}%")
out.append("=" * 110)

with open("scratch/audit_17_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

print("Audit written to scratch/audit_17_results.txt successfully!")
