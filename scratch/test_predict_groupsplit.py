import os, sys, joblib, numpy as np, pandas as pd

MODELS_DIR = os.path.abspath("models")

# Load models
soc_model = joblib.load(os.path.join(MODELS_DIR, "module_a_groupsplit", "soc", "SOC_Lasso.pkl"))
rul_model = joblib.load(os.path.join(MODELS_DIR, "module_a_groupsplit", "rul", "RUL_GradientBoosting.pkl"))
mil_model = joblib.load(os.path.join(MODELS_DIR, "module_a_groupsplit", "mileage", "Mileage_XGBoost.pkl"))
soh_model = joblib.load(os.path.join(MODELS_DIR, "module_a_soh_calibrated", "SOH_Calibrated_XGBoost.pkl"))

vehicles = {
    "DL1LAN0707": {
        "battery_voltage": 77.1, "battery_temp": 40.0, "battery_current": -16.5,
        "soc": 78.0, "odometer": 0.0, "charge_cycle_count": 0.0, "speed": 32.0, "soh": 99.2
    },
    "GJ05CV6564": {
        "battery_voltage": 80.4, "battery_temp": 29.4, "battery_current": -1.5,
        "soc": 91.4, "odometer": 11600.0, "charge_cycle_count": 200.0, "speed": 32.0, "soh": 96.9
    }
}

def predict_soc(v):
    cols = list(soc_model.feature_names_in_)
    d = {
        "battery_voltage": v["battery_voltage"], "battery_temp": v["battery_temp"],
        "battery_current": v["battery_current"], "abs_current": abs(v["battery_current"]),
        "is_charging": 1 if v["battery_current"] > 0 else 0, "odometer": v["odometer"],
        "odometer_diff": 0.0, "temp_stress_index": max(0.0, (v["battery_temp"] - 25.0)/30.0),
        "drive_mode_encoded": 1, "hour": 10, "day_of_week": 2, "month": 6,
        "is_weekend": 0, "is_peak": 0, "oem_encoded": 0, "model_encoded": 0
    }
    df = pd.DataFrame([{c: d.get(c, 0.0) for c in cols}])
    return float(soc_model.predict(df)[0])

def predict_rul(v):
    cols = list(rul_model.feature_names_in_)
    cycles = max(1.0, v["charge_cycle_count"] if v["charge_cycle_count"] > 0 else v["odometer"]/58.0)
    d = {
        "odometer": v["odometer"], "charge_cycle_count": cycles,
        "days_in_service": max(1.0, cycles * 1.25), "degradation_factor": min(1.0, cycles / 1400.0),
        "miles_per_charge": max(35.0, 120.0 - cycles*0.045), "temp_stress_index": 0.25,
        "voltage_deviation": round(v["battery_voltage"] - 72.0, 2), "abs_current": abs(v["battery_current"])
    }
    df = pd.DataFrame([{c: d.get(c, 0.0) for c in cols}])
    return float(rul_model.predict(df)[0])

def predict_mileage(v):
    cols = list(mil_model.feature_names_in_)
    d = {
        "avg_speed": v.get("speed", 30.0), "max_speed": v.get("speed", 30.0) + 15.0,
        "run_kms": 45.0, "trip_duration_hrs": 1.5, "stoppage_count": 3.0,
        "energy_utilized": 7.2, "energy_efficiency": 0.16, "trip_intensity": 45.0,
        "speed_ratio": 0.67, "stoppage_density": 2.0, "hour": 10, "day_of_week": 2,
        "month": 6, "is_weekend": 0, "is_peak": 0, "oem_encoded": 0, "model_encoded": 0
    }
    df = pd.DataFrame([{c: d.get(c, 0.0) for c in cols}])
    return float(mil_model.predict(df)[0])

def predict_soh(v):
    cols = list(soh_model.feature_names_in_)
    v_val = v["battery_voltage"]
    i_val = v["battery_current"]
    t_val = v["battery_temp"]
    cycles = v["charge_cycle_count"]
    d = {
        "battery_voltage": v_val, "battery_temp": t_val, "battery_current": i_val,
        "abs_current": abs(i_val), "odometer": v["odometer"], "odometer_diff": 0.0,
        "charge_cycle_count": cycles, "mile_avg": 45.0, "miles_per_charge": 115.0,
        "days_in_service": max(1.0, cycles*1.25), "degradation_factor": min(1.0, cycles/1400.0),
        "temp_stress_index": max(0.0, (t_val-25.0)/30.0), "voltage_deviation": v_val - 72.0,
        "oem_encoded": 0, "model_encoded": 0,
        "v_roll_mean_5": v_val, "v_roll_std_5": 0.05, "v_roll_slope_5": 0.0,
        "v_roll_mean_10": v_val, "v_roll_std_10": 0.08, "v_roll_slope_10": 0.0,
        "v_roll_mean_20": v_val, "v_roll_std_20": 0.12, "v_roll_slope_20": 0.0,
        "i_roll_mean_5": i_val, "i_roll_std_5": 0.5, "i_roll_slope_5": 0.0,
        "i_roll_mean_10": i_val, "i_roll_std_10": 0.8, "i_roll_slope_10": 0.0,
        "i_roll_mean_20": i_val, "i_roll_std_20": 1.2, "i_roll_slope_20": 0.0,
        "t_roll_mean_5": t_val, "t_roll_std_5": 0.2,
        "t_roll_mean_10": t_val, "t_roll_std_10": 0.3,
        "t_roll_mean_20": t_val, "t_roll_std_20": 0.5,
        "v_cycle_slope_20": -0.005, "charge_acceptance_rate": 0.05, "cycles_since_start": max(0.0, cycles)
    }
    df = pd.DataFrame([{c: d.get(c, 0.0) for c in cols}])
    delta_pred = float(soh_model.predict(df)[0])
    init_soh = v.get("initial_soh", v.get("soh", 99.2))
    abs_soh = np.clip(init_soh + delta_pred, 50.0, 100.0)
    return abs_soh, delta_pred

for vid, v in vehicles.items():
    print(f"\n--- {vid} Group-Split Model Predictions ---")
    print(f"  SOC Prediction:     {predict_soc(v):.2f}%")
    print(f"  RUL Prediction:     {predict_rul(v):.0f} cycles")
    print(f"  Mileage Prediction: {predict_mileage(v):.1f} km")
    abs_s, del_s = predict_soh(v)
    print(f"  SOH Prediction:     {abs_s:.2f}% (Delta: {del_s:+.4f}%, Baseline: {v['soh']}%)")
