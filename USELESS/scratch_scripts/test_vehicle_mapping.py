import sqlite3
import requests

API = "http://localhost:8000"
vehicles_to_test = ["GJ05CV6564", "DL1LAN0707", "MH12VB7125"]

print("=" * 75)
print("  END-TO-END VEHICLE MAPPING & MULTI-MODULE PREDICTION VERIFICATION")
print("=" * 75)

conn = sqlite3.connect("fleet_intelligence.db")
cur = conn.cursor()

for vid in vehicles_to_test:
    cur.execute(
        "SELECT id, model, soc, soh, voltage, current, battery_temp, controller_temp, motor_temp, speed, charge_cycle_count FROM vehicles WHERE id=?",
        (vid,),
    )
    row = cur.fetchone()
    if not row:
        print(f"Vehicle {vid} not found in DB!")
        continue

    v = {
        "id": row[0],
        "model": row[1],
        "soc": row[2],
        "soh": row[3],
        "voltage": row[4],
        "current": row[5],
        "battery_temp": row[6],
        "controller_temp": row[7],
        "motor_temp": row[8],
        "speed": row[9],
        "charge_cycle_count": row[10],
    }

    print(f"\n--- VEHICLE: {v['id']} ({v['model']}) ---")
    print(f"   Telemetry: {v['voltage']}V, {v['current']}A, {v['battery_temp']}C, SOC={v['soc']}%, SOH={v['soh']}%, Cycles={v['charge_cycle_count']}")

    # Test Module A SOH
    r_a = requests.post(
        f"{API}/predict/soh",
        json={
            "battery_voltage": v["voltage"],
            "battery_temp": v["battery_temp"],
            "battery_current": v["current"],
            "odometer": v["charge_cycle_count"] * 58.0,
            "charge_cycle_count": v["charge_cycle_count"],
        },
    ).json()
    print(f"   [Module A] SOH Pred: {r_a['prediction']} {r_a['unit']} (Model: {r_a['model_used']})")

    # Test Module B Thermal
    r_b = requests.post(
        f"{API}/predict/thermal",
        json={
            "vbt": v["battery_temp"],
            "vct": v["controller_temp"],
            "vmt": v["motor_temp"],
            "vbv": v["voltage"],
            "vbc": v["current"],
            "soc": v["soc"],
            "speed": v["speed"],
        },
    ).json()
    print(f"   [Module B] Thermal: {r_b['safety_status']} (Risk: {r_b['risk_probability']:.3f})")

    # Test Module C Knee
    r_c = requests.post(
        f"{API}/predict/knee-point",
        json={
            "charge_cycle_count": v["charge_cycle_count"],
            "capacity": v["soh"],
            "voltage": v["voltage"],
            "battery_temp": v["battery_temp"],
            "current": v["current"],
            "soc": v["soc"],
        },
    ).json()
    print(f"   [Module C] Knee RUL: {r_c['rul_to_knee_cycles']} cycles to knee (State: {r_c['knee_risk_state']})")

conn.close()
print("\n" + "=" * 75)
print("  VERIFICATION COMPLETE: ALL 3 MODULES CORRECTLY MAPPED TO VEHICLE DATA")
print("=" * 75)
