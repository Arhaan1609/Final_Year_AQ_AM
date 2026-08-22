import requests
import json

API = "http://localhost:8000"

vehicles = {
    "DL1LAN0707": {
        "id": "DL1LAN0707",
        "chassis": "MAT486022RZD10218",
        "model": "Tata Ace EV 14.2 kWh",
        "voltage": 77.1,
        "current": -16.5,
        "battery_temp": 40.0,
        "controller_temp": 42.0,
        "motor_temp": 48.0,
        "soc": 78.0,
        "odometer": 0,
        "charge_cycle_count": 0,
        "capacity": 99.2,
        "speed": 0.0,
    },
    "GJ05CV6564": {
        "id": "GJ05CV6564",
        "chassis": "MD9EMHDL23D217075",
        "model": "Euler HiLoad EV 12.4 kWh",
        "voltage": 80.4,
        "current": -1.5,
        "battery_temp": 29.4,
        "controller_temp": 36.9,
        "motor_temp": 69.0,
        "soc": 91.4,
        "odometer": 11600.0,
        "charge_cycle_count": 200,
        "capacity": 96.9,
        "speed": 32.0,
    },
}

for vid, v in vehicles.items():
    print("=" * 78)
    print(f"VEHICLE: {vid} ({v['model']})")
    print("=" * 78)

    # 1. SOC
    soc_res = requests.post(f"{API}/predict/soc", json={
        "battery_voltage": v["voltage"],
        "battery_temp": v["battery_temp"],
        "battery_current": v["current"],
        "odometer": v["odometer"]
    }).json()
    print(f"  [Tab: State Estimation] SOC Prediction:     {soc_res.get('prediction'):.2f}% (Model: {soc_res.get('model_used')})")

    # 2. SOH
    soh_res = requests.post(f"{API}/predict/soh", json={
        "battery_voltage": v["voltage"],
        "battery_temp": v["battery_temp"],
        "battery_current": v["current"],
        "charge_cycle_count": v["charge_cycle_count"],
        "odometer": v["odometer"]
    }).json()
    print(f"  [Tab: State Estimation] SOH Prediction:     {soh_res.get('prediction'):.2f}% (Model: {soh_res.get('model_used')})")

    # 3. RUL
    rul_res = requests.post(f"{API}/predict/rul", json={
        "odometer": v["odometer"],
        "charge_cycle_count": v["charge_cycle_count"],
        "days_in_service": max(1, int(v["charge_cycle_count"] * 1.4))
    }).json()
    print(f"  [Tab: State Estimation] RUL Prediction:     {rul_res.get('prediction'):.0f} cycles (Model: {rul_res.get('model_used')})")

    # 4. Mileage
    mil_res = requests.post(f"{API}/predict/mileage", json={
        "avg_speed": v["speed"] or 30.0,
        "max_speed": (v["speed"] or 30.0) + 20.0,
        "run_kms": 45.0,
        "trip_duration_hrs": 1.5,
        "stoppage_count": 3,
        "energy_efficiency": 0.88
    }).json()
    print(f"  [Tab: State Estimation] Mileage Prediction: {mil_res.get('prediction'):.1f} km (Model: {mil_res.get('model_used')})")

    # 5. Thermal
    th_res = requests.post(f"{API}/predict/thermal", json={
        "vbt": v["battery_temp"],
        "vct": v["controller_temp"],
        "vmt": v["motor_temp"],
        "vbv": v["voltage"],
        "vbc": v["current"],
        "soc": v["soc"],
        "speed": v["speed"]
    }).json()
    print(f"  [Tab: Thermal Safety]   Safety Status:      {th_res.get('safety_status')} (Risk: {th_res.get('risk_probability'):.3f})")

    # 6. Knee Point
    knee_res = requests.post(f"{API}/predict/knee-point", json={
        "charge_cycle_count": v["charge_cycle_count"],
        "capacity": v["capacity"],
        "voltage": v["voltage"],
        "battery_temp": v["battery_temp"],
        "current": v["current"],
        "soc": v["soc"],
        "speed": v["speed"],
        "run_kms": 45.0,
        "energy_kwh": 7.2
    }).json()
    print(f"  [Tab: Knee Prognostics] Knee Risk State:    {knee_res.get('knee_risk_state')} | RUL to Knee: {knee_res.get('rul_to_knee_cycles'):.1f} cyc | Estimated Knee: {knee_res.get('estimated_knee_cycle'):.0f} cyc")

    # 7. Driver Behavior
    dr_res = requests.post(f"{API}/predict/driver-behavior", json={
        "harsh_accel_count": 1.0,
        "harsh_brake_count": 1.0,
        "harsh_corner_count": 0.0,
        "speed_variance": 4.5,
        "avg_speed": v["speed"] or 30.0,
        "max_speed": (v["speed"] or 30.0) + 20.0,
        "overspeed_count": 0.0,
        "battery_temp_max": v["battery_temp"],
        "max_discharge_current": abs(v["current"]),
        "voltage_variance": 1.2,
        "soc_drain_rate": 0.65
    }).json()
    print(f"  [Tab: Driver Profile]   Driver Class:       {dr_res.get('driver_classification')} | Aggressiveness: {dr_res.get('aggressiveness_index'):.2f} | Battery Stress: {dr_res.get('battery_stress_index'):.2f}")
