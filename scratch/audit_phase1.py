import sqlite3
import json
import os

print("=" * 80)
print("  AUDIT PHASE 1 — ITEMS 3 & 4: DB VS JSON VS FRONTEND")
print("=" * 80)

# Check timestamps
db_path = "fleet_intelligence.db"
json_path = "frontend/public/data/fleet_vehicles.json"
script_path = "scripts/export_all_vehicles.py"

print(f"DB mtime:     {os.path.getmtime(db_path)} ({os.path.getsize(db_path)} bytes)")
print(f"JSON mtime:   {os.path.getmtime(json_path)} ({os.path.getsize(json_path)} bytes)")
print(f"Script mtime: {os.path.getmtime(script_path)} ({os.path.getsize(script_path)} bytes)")

# Load JSON
with open(json_path, "r", encoding="utf-8") as f:
    json_data = json.load(f)

json_map = {v["id"]: v for v in json_data}
print(f"\nTotal records in JSON: {len(json_data)}")

# Load DB
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT count(*) FROM vehicles")
total_db = cur.fetchone()[0]
print(f"Total records in DB:   {total_db}")

cur.execute("SELECT id, model, fleet, soc, soh, rul, mileage, battery_temp, controller_temp, motor_temp, voltage, current, speed, charge_cycle_count, status FROM vehicles")
db_rows = cur.fetchall()
db_map = {row[0]: row for row in db_rows}
conn.close()

# Check 5 specific vehicles
test_vids = ["DL1LAN0707", "GJ05CV6564", "KA01AP8021", "DL1LAK7203", "GJ01LT4770"]

fields = ["id", "model", "fleet", "soc", "soh", "rul", "mileage", "battery_temp", "controller_temp", "motor_temp", "voltage", "current", "speed", "charge_cycle_count", "status"]

for vid in test_vids:
    print(f"\n--- AUDIT VEHICLE: {vid} ---")
    db_row = db_map.get(vid)
    json_entry = json_map.get(vid)

    if not db_row or not json_entry:
        print(f"  [ERROR] Not found in DB or JSON! (DB: {bool(db_row)}, JSON: {bool(json_entry)})")
        continue

    print(f"{'Field':20s} | {'DB Value':25s} | {'JSON Value':25s} | {'Match?':7s}")
    print("-" * 80)
    for i, col in enumerate(fields):
        db_val = db_row[i]
        json_val = json_entry.get(col)
        match = (db_val == json_val) or (isinstance(db_val, float) and abs(db_val - float(json_val or 0)) < 1e-4)
        print(f"{col:20s} | {str(db_val):25s} | {str(json_val):25s} | {str(match):7s}")
