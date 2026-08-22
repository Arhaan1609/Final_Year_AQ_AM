import json
import requests
import numpy as np

with open("frontend/public/data/fleet_vehicles.json") as f:
    fleet = json.load(f)

print(f"Loaded {len(fleet)} vehicles from fleet_vehicles.json")

thermal_results = []
rul_results = []

for v in fleet:
    vid = v["id"]
    cyc = float(v.get("charge_cycle_count", 0))
    odo = float(v.get("odometer", cyc * 58.0))
    bt = float(v.get("battery_temp", 30.0))
    ct = float(v.get("controller_temp", bt + 7.5))
    mt = float(v.get("motor_temp", bt + 16.0))
    volt = float(v.get("voltage", 74.0))
    curr = float(v.get("current", -15.0))
    soc = float(v.get("soc", 75.0))
    spd = float(v.get("speed", 30.0))
    
    # 1. Thermal
    r_th = requests.post("http://127.0.0.1:8000/predict/thermal", json={
        "vbt": bt, "vct": ct, "vmt": mt, "vbv": volt, "vbc": curr, "soc": soc, "speed": spd
    }).json()
    
    # 2. RUL
    r_rul = requests.post("http://127.0.0.1:8000/predict/rul", json={
        "odometer": odo, "charge_cycle_count": cyc, "battery_temp": bt, "soc_at_charge": soc
    }).json()
    
    p_th = r_th.get("risk_probability", 0.0)
    st_th = r_th.get("safety_status", "Unknown")
    p_rul = r_rul.get("prediction", 0.0)
    
    thermal_results.append((vid, bt, ct, mt, p_th, st_th))
    rul_results.append((vid, cyc, odo, p_rul))

probs = [t[4] for t in thermal_results]
statuses = [t[5] for t in thermal_results]
ruls = [r[3] for r in rul_results]
cycles = [r[1] for r in rul_results]

print("\n=== THERMAL RISK STATS (778 Vehicles) ===")
print(f"Min Prob = {min(probs):.4f}, Max Prob = {max(probs):.4f}, Mean = {np.mean(probs):.4f}, Std = {np.std(probs):.4f}")
status_counts = {}
for s in statuses:
    status_counts[s] = status_counts.get(s, 0) + 1
print(f"Status breakdown: {status_counts}")

elevated_thermal = [t for t in thermal_results if t[4] > 0.05 or "CRITICAL" in t[5] or "WARNING" in t[5]]
print(f"\nTotal vehicles with elevated thermal risk (>0.05): {len(elevated_thermal)}")
for et in elevated_thermal[:15]:
    print(f"  {et[0]}: Pack={et[1]}C, Inverter={et[2]}C, Motor={et[3]}C -> Risk={et[4]:.3f}, Status={et[5]}")

print("\n=== RUL STATS (778 Vehicles) ===")
print(f"Min RUL = {min(ruls):.1f}, Max RUL = {max(ruls):.1f}, Mean = {np.mean(ruls):.1f}, Std = {np.std(ruls):.1f}")
print(f"Cycles: Min = {min(cycles):.0f}, Max = {max(cycles):.0f}, Mean = {np.mean(cycles):.1f}, Std = {np.std(cycles):.1f}")
print(f"Pearson Corr(Cycles, RUL): {np.corrcoef(cycles, ruls)[0,1]:.4f}")
