import os
import sys
import json
import sqlite3
import pandas as pd

print("=" * 70)
print("  DATA PROVENANCE & RAW-TO-PROCESSED DEEP AUDIT")
print("=" * 70)

# 1. RAW DATA AUDIT
print("\n[1] AUDITING RAW TELEMATICS DATA (data/raw/)...")
raw_files = [
    "data/raw/magenta-telematics-prod.charge_cycles_logs.json",
    "data/raw/tms_history_l2_device.json",
    "data/raw/tms_history_l2_oem.json"
]

for rf in raw_files:
    if os.path.exists(rf):
        size_mb = os.path.getsize(rf) / (1024*1024)
        print(f"\n  File: {rf} ({size_mb:.2f} MB)")
        try:
            # Read first 5 lines or first objects
            with open(rf, "r", encoding="utf-8", errors="ignore") as f:
                first_chars = f.read(2000)
                try:
                    data = json.loads(first_chars)
                    if isinstance(data, list) and len(data) > 0:
                        print(f"    Format: JSON Array of {type(data[0])}")
                        print(f"    Sample Keys: {list(data[0].keys())}")
                    elif isinstance(data, dict):
                        print(f"    Format: JSON Dict with keys: {list(data.keys())[:10]}")
                except Exception:
                    # Might be json lines
                    f.seek(0)
                    line1 = f.readline().strip()
                    try:
                        obj = json.loads(line1)
                        print(f"    Format: JSON Lines")
                        print(f"    Sample Keys ({len(obj)}): {list(obj.keys())}")
                        # Check for driver or user fields
                        driver_keys = [k for k in obj.keys() if any(w in k.lower() for w in ['driver', 'user', 'operator', 'name', 'pilot', 'chassis', 'vehicle'])]
                        print(f"    Identity/Vehicle Keys: {driver_keys}")
                    except Exception as je:
                        print(f"    Parse preview: {first_chars[:200]}")
        except Exception as e:
            print(f"    Error reading: {e}")

# 2. PROCESSED DATA AUDIT
print("\n" + "=" * 70)
print("[2] AUDITING PROCESSED DATASETS (data/processed/)...")
processed_files = [
    "data/processed/features_soc.csv",
    "data/processed/features_soh.csv",
    "data/processed/features_rul.csv",
    "data/processed/features_mileage.csv",
    "data/processed/master_dataset.csv",
    "data/processed/charge_cycles_clean.csv",
    "data/processed/oem_telemetry_clean.csv"
]

for pf in processed_files:
    if os.path.exists(pf):
        size_mb = os.path.getsize(pf) / (1024*1024)
        df_head = pd.read_csv(pf, nrows=5)
        print(f"\n  File: {pf} ({size_mb:.2f} MB)")
        print(f"    Columns ({len(df_head.columns)}): {list(df_head.columns)}")
        id_cols = [c for c in df_head.columns if any(w in c.lower() for w in ['vehicle', 'chassis', 'driver', 'user', 'id', 'model'])]
        print(f"    Identifier columns: {id_cols}")

# 3. DRIVER AND VEHICLE REGISTRY AUDIT (SQL DB & JSON)
print("\n" + "=" * 70)
print("[3] AUDITING FLEET DATABASE & FRONTEND DATA (fleet_intelligence.db & fleet_vehicles.json)...")
db_path = "fleet_intelligence.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    print(f"  SQLite Tables: {[t[0] for t in tables]}")
    for t in tables:
        tname = t[0]
        cur.execute(f"SELECT COUNT(*) FROM {tname}")
        cnt = cur.fetchone()[0]
        cur.execute(f"PRAGMA table_info({tname})")
        cols = [c[1] for c in cur.fetchall()]
        print(f"    Table '{tname}': {cnt} rows, Columns: {cols}")
        cur.execute(f"SELECT * FROM {tname} LIMIT 3")
        rows = cur.fetchall()
        for r in rows:
            print(f"      Sample Row: {r}")
    conn.close()

# 4. FRONTEND FLEET VEHICLES JSON
fv_json = "frontend/public/data/fleet_vehicles.json"
if os.path.exists(fv_json):
    with open(fv_json, "r") as f:
        f_data = json.load(f)
    print(f"\n  frontend/public/data/fleet_vehicles.json ({len(f_data)} vehicles loaded)")
    print(f"    Sample 5 Vehicles with Driver Mappings:")
    for v in f_data[:5]:
        print(f"      Vehicle ID: {v.get('id'):12s} | Model: {v.get('model'):20s} | Driver: {v.get('driver'):20s} | Fleet: {v.get('fleet')}")
