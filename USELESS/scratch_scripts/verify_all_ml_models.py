import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import requests

print("=" * 60)
print("  BATTERY INTELLIGENCE PLATFORM: FULL SCIENTIFIC AUDIT")
print("=" * 60)

# ─── 1. AUDIT MODULE A MODELS ───
print("\n[1] AUDITING MODULE A (Fleet State Estimation Models)...")
mod_a_dir = "models"
# Check models directory structure
for root, dirs, files in os.walk("models"):
    pkls = [f for f in files if f.endswith(".pkl")]
    if pkls:
        print(f"  Directory: {root} -> {len(pkls)} PKL models")
        for f in pkls[:3]:
            try:
                m = joblib.load(os.path.join(root, f))
                cols = getattr(m, "feature_names_in_", None)
                print(f"    - {f}: {type(m).__name__} (cols={len(cols) if cols is not None else 'raw'})")
            except Exception as e:
                print(f"    - {f}: Load error ({e})")

# ─── 2. AUDIT MODULE B ENGINE ───
print("\n[2] AUDITING MODULE B (Multi-Zone Thermal & SOH Deep Engine)...")
sys.path.insert(0, "modules/module_b")
try:
    from src.models.engine import BatteryIQEngine
    from src.core.schemas import MultiZoneThermalInput, SOHSequenceInput, VehicleTelemetryPacket
    engine_b = BatteryIQEngine()
    print("  [PASS] BatteryIQEngine instantiated successfully.")
    
    # Test Thermal Classifier
    t_in = MultiZoneThermalInput(
        vbt=35.0, vct=42.0, vmt=55.0,
        vbv=74.0, vbc=-18.0, soc=80.0, speed=32.0
    )
    t_res = engine_b.predict_thermal_vector(t_in)
    print(f"  [PASS] Multi-Zone Thermal Output: {t_res.safety_status} (Risk: {t_res.risk_probability:.3f})")

    # Test CNN-LSTM Sequence
    seq = [[75.0, -18.0, 32.0, 80.0] for _ in range(10)]
    s_in = SOHSequenceInput(vehicle_id="GJ05CV6564", sequence=seq)
    s_res = engine_b.predict_soh_sequence(s_in)
    print(f"  [PASS] SOH Deep Sequence Output: {s_res.estimated_soh_percent:.2f}% ({s_res.capacity_state})")

    # Test Full Vehicle Packet
    pkt = VehicleTelemetryPacket(
        vehicle_id="GJ05CV6564", oem_model="Euler HiLoad",
        soc=78.0, voltage=74.5, current=-16.0,
        battery_temp=33.0, controller_temp=40.0, motor_temp=50.0,
        speed=35.0, odometer_km=14500.0
    )
    diag = engine_b.diagnose_packet(pkt)
    print(f"  [PASS] Dual-Pillar Diagnosis Output: Score={diag.overall_health_score}/100, Tier={diag.fleet_operating_mode}")
except Exception as e:
    print(f"  [FAIL] Module B Failed: {e}")

# ─── 3. AUDIT MODULE C ENGINE ───
print("\n[3] AUDITING MODULE C (BA-BMS & Knee-Point Engine)...")
sys.path.insert(0, "modules/module_c")
try:
    from engine import BABMSEngine
    engine_c = BABMSEngine()
    print(f"  [PASS] BABMSEngine loaded (is_loaded={engine_c.is_loaded})")
    
    # Test Driver Behavior
    beh = engine_c.compute_behavior_indices(
        harsh_accel_count=3, harsh_brake_count=2, harsh_corner_count=1,
        speed_variance=12.0, avg_speed=35.0, max_speed=65.0,
        battery_temp_max=38.0, max_discharge_current=45.0
    )
    print(f"  [PASS] Driver Behavior Output: AI={beh['aggressiveness_index']}, BSI={beh['battery_stress_index']}, Class={beh['driver_classification']}")

    # Test Knee Prognostics
    knee = engine_c.predict_knee_point({
        "charge_cycle_count": 250,
        "capacity": 94.0,
        "voltage": 74.0,
        "battery_temp": 32.0,
        "current": -18.0,
        "soc": 80.0
    })
    print(f"  [PASS] Knee Prognostics Output: RUL_to_knee={knee['rul_to_knee_cycles']} cycles, KneeState='{knee['knee_risk_state']}'")
except Exception as e:
    print(f"  [FAIL] Module C Failed: {e}")

# ─── 4. TEST LIVE API REST ENDPOINTS ───
print("\n[4] AUDITING LIVE FASTAPI REST ENDPOINTS (http://localhost:8000)...")
API = "http://localhost:8000"

endpoints = [
    ("/health", "GET", None),
    ("/predict/soc", "POST", {"battery_voltage": 74.0, "battery_temp": 32.0, "battery_current": -18.0, "odometer": 12500, "charge_cycle_count": 215}),
    ("/predict/soh", "POST", {"battery_voltage": 74.0, "battery_temp": 32.0, "battery_current": -18.0, "odometer": 12500, "charge_cycle_count": 215}),
    ("/predict/rul", "POST", {"odometer": 12500, "charge_cycle_count": 215, "battery_temp": 32.0, "soc_at_charge": 85.0}),
    ("/predict/mileage", "POST", {"run_kms": 45, "avg_speed": 32, "max_speed": 55, "odometer": 12500, "battery_voltage": 74.0, "battery_temp": 32.0}),
    ("/predict/thermal", "POST", {"vbt": 33.0, "vct": 41.0, "vmt": 52.0, "vbv": 74.0, "vbc": -18.0, "soc": 80.0, "speed": 34.0}),
    ("/predict/soh-deep", "POST", {"vehicle_id": "GJ05CV6564", "sequence": [[74.0, -18.0, 32.0, 80.0] for _ in range(10)]}),
    ("/predict/driver-behavior", "POST", {"harsh_accel_count": 2, "harsh_brake_count": 1, "harsh_corner_count": 1, "speed_variance": 8.0, "avg_speed": 35.0, "max_speed": 60.0, "battery_temp_max": 35.0, "max_discharge_current": 35.0}),
    ("/predict/knee-point", "POST", {"charge_cycle_count": 215, "capacity": 94.0, "voltage": 74.0, "battery_temp": 32.0, "current": -18.0, "soc": 80.0}),
    ("/predict/meta-ensemble", "POST", {"vehicle_id": "GJ05CV6564", "charge_cycle_count": 215, "battery_voltage": 74.0, "battery_temp": 32.0, "battery_current": -18.0, "soc": 80.0, "harsh_accel_count": 2, "speed_variance": 8.0}),
    ("/predict/diagnose/vehicle", "POST", {"vehicle_id": "GJ05CV6564", "oem_model": "Euler HiLoad", "soc": 80.0, "voltage": 74.0, "current": -18.0, "battery_temp": 32.0, "controller_temp": 40.0, "motor_temp": 50.0, "speed": 34.0, "odometer_km": 12500.0}),
]

for path, method, payload in endpoints:
    url = f"{API}{path}"
    try:
        if method == "GET":
            r = requests.get(url, timeout=5)
        else:
            r = requests.post(url, json=payload, timeout=5)
        
        if r.status_code == 200:
            print(f"  [PASS] {method} {path:28s} -> 200 OK | Sample: {json.dumps(r.json())[:60]}...")
        else:
            print(f"  [FAIL] {method} {path:28s} -> {r.status_code} ERROR: {r.text}")
    except Exception as e:
        print(f"  [FAIL] {method} {path:28s} -> Connection Error: {e}")

print("\n" + "=" * 60)
print("  AUDIT COMPLETED")
print("=" * 60)
