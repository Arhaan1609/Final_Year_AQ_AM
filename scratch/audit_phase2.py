import os
import hashlib
import joblib
import pandas as pd
import numpy as np
import pyarrow.parquet as pq

print("=" * 80)
print("  AUDIT PHASE 2 — ITEMS 5, 6, 7, 8: FEATURE MAPPING & SCALERS")
print("=" * 80)

# Item 7: Scaler Hashes & Inspection
print("\n--- ITEM 7: SCALER & MODEL WEIGHT HASHES ---")
scaler_files = [
    "models/module_a/soc/scaler_soc.pkl",
    "models/module_a/soh/scaler_soh.pkl",
    "models/module_a/rul/scaler_rul.pkl",
    "models/module_a/mileage/scaler_mileage.pkl",
    "models/module_b/scalers.joblib",
    "models/module_c/feature_scaler.pkl",
]

for sf in scaler_files:
    if os.path.exists(sf):
        with open(sf, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        mtime = os.path.getmtime(sf)
        size = os.path.getsize(sf)
        obj = joblib.load(sf)
        obj_type = type(obj).__name__
        n_features = getattr(obj, "n_features_in_", "N/A")
        print(f"{sf:45s} | SHA256: {h[:12]}... | Type: {obj_type:15s} | InFeatures: {str(n_features):4s} | Size: {size:6d}B")
    else:
        print(f"{sf:45s} | MISSING!")

# Item 8: Module B Time Series Tensor Chronological Order Check
print("\n--- ITEM 8: MODULE B (10, 4) TIME SERIES TENSOR CHRONOLOGICAL AUDIT ---")
parquet_path = "data/processed/module_b_thermal_deep_soh/soh_timeseries_euler_processed.parquet"
if os.path.exists(parquet_path):
    df_seq = pd.read_parquet(parquet_path)
    print(f"Parquet Columns: {df_seq.columns.tolist()}")
    print(f"Parquet Shape:   {df_seq.shape}")
    print(f"Sample records:\n{df_seq.head(3)}")
else:
    print(f"Parquet file {parquet_path} not found!")

# Item 5: Trace GJ05CV6564 in oem_telemetry_clean.csv
print("\n--- ITEM 5: TRACING RAW CAN TELEMETRY FOR GJ05CV6564 ---")
oem_clean = "data/processed/module_c_knee_and_behavior/oem_telemetry_clean.csv"
if os.path.exists(oem_clean):
    df_oem = pd.read_csv(oem_clean, nrows=100000)
    gj_rows = df_oem[df_oem["vehicle_no"].astype(str).str.contains("GJ05CV6564", na=False)]
    if len(gj_rows) == 0 and "chassis_no" in df_oem.columns:
        gj_rows = df_oem[df_oem["chassis_no"].astype(str).str.contains("GJ05CV6564", na=False)]
    print(f"Found {len(gj_rows)} rows for GJ05CV6564 in first 100k rows.")
    if len(gj_rows) > 0:
        sample_row = gj_rows.iloc[0]
        print(f"Raw CAN row:\n  Voltage: {sample_row.get('battery_voltage')}V\n  Current: {sample_row.get('battery_current')}A\n  Temp: {sample_row.get('battery_temp')}C\n  SOC: {sample_row.get('soc')}%\n  SOH: {sample_row.get('soh')}%")
