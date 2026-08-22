import json

with open("frontend/public/data/fleet_vehicles.json") as f:
    fleet = json.load(f)

expected_keys = [
    "id", "chassis", "model", "fleet", "driver",
    "soc", "soh", "rul", "mileage",
    "battery_temp", "controller_temp", "motor_temp",
    "voltage", "current", "speed", "charge_cycle_count",
    "status", "lastPing"
]

print(f"Total vehicles: {len(fleet)}")
missing_counts = {k: 0 for k in expected_keys}
null_counts = {k: 0 for k in expected_keys}

for idx, v in enumerate(fleet):
    for k in expected_keys:
        if k not in v:
            missing_counts[k] += 1
        elif v[k] is None or v[k] == "":
            null_counts[k] += 1

print("\n--- Field Completeness across all 778 vehicles in fleet_vehicles.json ---")
for k in expected_keys:
    print(f"  Field: {k:20s} | Missing: {missing_counts[k]:4d} | Null/Empty: {null_counts[k]:4d}")
