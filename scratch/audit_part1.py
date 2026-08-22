import requests
import json
import numpy as np
import pandas as pd
import os

API = "http://localhost:8000"

with open("frontend/public/data/fleet_vehicles.json", "r") as f:
    all_fleet = json.load(f)

# Sort fleet vehicles by charge_cycle_count and odometer to pick 30 spanning the full gamut
fleet_sorted = sorted(all_fleet, key=lambda x: (x.get("charge_cycle_count", 0), x.get("odometer", 0)))
indices = np.linspace(0, len(fleet_sorted) - 1, 30, dtype=int)
sample_30 = [fleet_sorted[i] for i in indices]

# Also vary avg_speed and run_kms systematically across the 30 vehicles
speeds = np.linspace(18.0, 58.0, 30)
run_distances = np.linspace(15.0, 95.0, 30)

results = []

for idx, (v, spd, dist) in enumerate(zip(sample_30, speeds, run_distances)):
    cycles = float(v.get("charge_cycle_count", 0))
    odo = float(v.get("odometer", cycles * 58.0))
    voltage = float(v.get("voltage", 74.0))
    temp = float(v.get("battery_temp", 32.0))
    current = float(v.get("current", -18.0))
    soc = float(v.get("soc", 80.0))
    soh = float(v.get("soh", 95.0))
    chassis = v.get("chassis", v.get("id"))
    
    # 1. Query RUL
    rul_payload = {
        "odometer": odo,
        "charge_cycle_count": cycles,
        "battery_temp": temp,
        "soc_at_charge": soc,
        "days_in_service": max(1.0, cycles * 1.25),
        "mile_avg": 45.0,
        "miles_per_charge": max(35.0, min(130.0, 120.0 - (cycles * 0.045))),
    }
    rul_res = requests.post(f"{API}/predict/rul", json=rul_payload).json()
    rul_pred = rul_res.get("prediction", np.nan)
    rul_model = rul_res.get("model_used", "Unknown")

    # 2. Query Mileage
    mil_payload = {
        "avg_speed": round(spd, 1),
        "max_speed": round(spd + 16.0, 1),
        "run_kms": round(dist, 1),
        "trip_duration_hrs": round(dist / max(15.0, spd), 2),
        "stoppage_count": max(1.0, round(dist / 20.0)),
        "energy_efficiency": 0.88,
        "soc": soc,
        "energy_utilized": round(dist * 0.16, 2)
    }
    mil_res = requests.post(f"{API}/predict/mileage", json=mil_payload).json()
    mil_pred = mil_res.get("prediction", np.nan)
    mil_model = mil_res.get("model_used", "Unknown")

    results.append({
        "idx": idx + 1,
        "id": v.get("id"),
        "chassis": chassis,
        "cycles": cycles,
        "odometer": odo,
        "soc": soc,
        "soh": soh,
        "avg_speed": round(spd, 1),
        "run_kms": round(dist, 1),
        "rul_pred": rul_pred,
        "mil_pred": mil_pred,
        "rul_model": rul_model,
        "mil_model": mil_model
    })

df = pd.DataFrame(results)

out = []
out.append("=" * 125)
out.append("PART 1: 30-VEHICLE AUDIT FOR RUL & MILEAGE CONSTANT-COLLAPSE CHECK")
out.append("=" * 125)
header = f"{'#':2s} | {'Vehicle ID':10s} | {'Chassis No':18s} | {'Cycles':6s} | {'Odo(km)':7s} | {'Speed':5s} | {'Dist':5s} | {'SOC%':5s} | {'RUL (cyc)':9s} | {'Mileage (km)':12s}"
out.append(header)
out.append("-" * 125)
for _, r in df.iterrows():
    out.append(f"{int(r['idx']):2d} | {r['id']:10s} | {r['chassis']:18s} | {r['cycles']:6.0f} | {r['odometer']:7.0f} | {r['avg_speed']:5.1f} | {r['run_kms']:5.1f} | {r['soc']:5.1f} | {r['rul_pred']:9.0f} | {r['mil_pred']:12.1f}")

out.append("\n" + "=" * 125)
out.append("STATISTICAL SPREAD & VARIANCE ANALYSIS (30 VEHICLES)")
out.append("=" * 125)
out.append(f"INPUT Charge Cycles   : Min = {df['cycles'].min():.0f}, Max = {df['cycles'].max():.0f}, Range = {df['cycles'].max()-df['cycles'].min():.0f}, Mean = {df['cycles'].mean():.1f}, Std = {df['cycles'].std():.1f}")
out.append(f"INPUT Odometer (km)   : Min = {df['odometer'].min():.0f}, Max = {df['odometer'].max():.0f}, Range = {df['odometer'].max()-df['odometer'].min():.0f}, Mean = {df['odometer'].mean():.1f}, Std = {df['odometer'].std():.1f}")
out.append(f"INPUT Avg Speed (km/h): Min = {df['avg_speed'].min():.1f}, Max = {df['avg_speed'].max():.1f}, Range = {df['avg_speed'].max()-df['avg_speed'].min():.1f}, Mean = {df['avg_speed'].mean():.1f}, Std = {df['avg_speed'].std():.1f}")
out.append(f"INPUT Run Kms         : Min = {df['run_kms'].min():.1f}, Max = {df['run_kms'].max():.1f}, Range = {df['run_kms'].max()-df['run_kms'].min():.1f}, Mean = {df['run_kms'].mean():.1f}, Std = {df['run_kms'].std():.1f}")
out.append(f"INPUT SOC (%)         : Min = {df['soc'].min():.1f}%, Max = {df['soc'].max():.1f}%, Range = {df['soc'].max()-df['soc'].min():.1f}%, Mean = {df['soc'].mean():.1f}%, Std = {df['soc'].std():.1f}%")
out.append("-" * 125)
out.append(f"OUTPUT RUL (cycles)   : Min = {df['rul_pred'].min():.0f}, Max = {df['rul_pred'].max():.0f}, Range = {df['rul_pred'].max()-df['rul_pred'].min():.0f}, Mean = {df['rul_pred'].mean():.1f}, Std = {df['rul_pred'].std():.1f} | Model: {df['rul_model'].iloc[0]}")
out.append(f"OUTPUT Mileage (km)   : Min = {df['mil_pred'].min():.1f}, Max = {df['mil_pred'].max():.1f}, Range = {df['mil_pred'].max()-df['mil_pred'].min():.1f}, Mean = {df['mil_pred'].mean():.1f}, Std = {df['mil_pred'].std():.1f} | Model: {df['mil_model'].iloc[0]}")

# Check correlation between cycles and RUL
corr_rul_cycles = np.corrcoef(df['cycles'], df['rul_pred'])[0, 1]
corr_mil_soc = np.corrcoef(df['soc'], df['mil_pred'])[0, 1]
out.append("-" * 125)
out.append(f"Pearson Correlation (Cycles vs Predicted RUL)    : {corr_rul_cycles:.4f} (Expected strong negative)")
out.append(f"Pearson Correlation (SOC vs Predicted Mileage)   : {corr_mil_soc:.4f} (Expected strong positive)")
out.append("=" * 125)

with open("scratch/part1_rul_mileage_audit.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

print("Part 1 Audit finished and saved to scratch/part1_rul_mileage_audit.txt")
