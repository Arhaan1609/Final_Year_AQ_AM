import os
import sys
import time
from datetime import datetime
import joblib

print("=" * 80)
print("INDEPENDENT MODEL LOADING & WEIGHT ARTIFACT AUDIT (MODULES A, B, C)")
print("=" * 80)

# --- 1. MODULE B AUDIT ---
print("\n[MODULE B: BatteryIQ Engine Audit]")
sys.path.insert(0, os.path.abspath("modules/module_b"))
from src.models.engine import BatteryIQEngine

eng_b = BatteryIQEngine()
print(f"  Thermal Model is_loaded : {eng_b.thermal_model.is_loaded}")
print(f"  Thermal Model Type      : {type(eng_b.thermal_model.model)}")
print(f"  Thermal Weights Path    : {eng_b.thermal_model.weights_path}")
if eng_b.thermal_model.weights_path and os.path.exists(eng_b.thermal_model.weights_path):
    mtime = os.path.getmtime(eng_b.thermal_model.weights_path)
    size = os.path.getsize(eng_b.thermal_model.weights_path)
    print(f"  Thermal Artifact Size   : {size:,} bytes")
    print(f"  Thermal Last Modified   : {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    # Inspect loaded sklearn object directly
    loaded_rf = eng_b.thermal_model.model
    print(f"  Number of RF Trees      : {len(loaded_rf.estimators_)}")
    print(f"  Feature Importances     : {[round(x, 4) for x in loaded_rf.feature_importances_]}")
else:
    print("  [ERROR] Thermal weights file NOT found on disk!")

print(f"\n  SOH Model is_loaded     : {eng_b.soh_model.is_loaded}")
print(f"  SOH Model Wrapper Type  : {type(eng_b.soh_model)}")
print(f"  SOH Weights Path        : {eng_b.soh_model.weights_path}")
if eng_b.soh_model.weights_path and os.path.exists(eng_b.soh_model.weights_path):
    mtime_s = os.path.getmtime(eng_b.soh_model.weights_path)
    size_s = os.path.getsize(eng_b.soh_model.weights_path)
    print(f"  SOH Artifact Size       : {size_s:,} bytes")
    print(f"  SOH Last Modified       : {datetime.fromtimestamp(mtime_s).strftime('%Y-%m-%d %H:%M:%S')}")
else:
    print("  [ERROR] SOH weights file NOT found on disk!")

# --- 2. MODULE C AUDIT ---
print("\n[MODULE C: BA-BMS & Knee Prognostics Engine Audit]")
sys.path.insert(0, os.path.abspath("modules/module_c"))
from engine import BABMSEngine

eng_c = BABMSEngine()
print(f"  Knee Engine is_loaded   : {eng_c.is_loaded}")
print(f"  Knee Booster Type       : {type(eng_c.booster)}")
print(f"  Knee Scaler Type        : {type(eng_c.scaler)}")
print(f"  Model Path              : {eng_c.model_path}")
print(f"  Scaler Path             : {eng_c.scaler_path}")
if os.path.exists(eng_c.model_path):
    mtime_c = os.path.getmtime(eng_c.model_path)
    size_c = os.path.getsize(eng_c.model_path)
    print(f"  Knee Model Size         : {size_c:,} bytes")
    print(f"  Knee Model Last Modified: {datetime.fromtimestamp(mtime_c).strftime('%Y-%m-%d %H:%M:%S')}")
if os.path.exists(eng_c.scaler_path):
    mtime_sc = os.path.getmtime(eng_c.scaler_path)
    size_sc = os.path.getsize(eng_c.scaler_path)
    print(f"  Knee Scaler Size        : {size_sc:,} bytes")
    print(f"  Knee Scaler Last Modified: {datetime.fromtimestamp(mtime_sc).strftime('%Y-%m-%d %H:%M:%S')}")

# --- 3. MODULE A AUDIT ---
print("\n[MODULE A: Group-Split & Calibrated Models Audit]")
for task, path in [
    ("SOC", "models/module_a_groupsplit/soc/SOC_XGBoost.pkl"),
    ("SOH", "models/module_a_soh_calibrated/soh_calibrated_delta_xgboost.pkl"),
    ("RUL", "models/module_a_groupsplit/rul/RUL_GradientBoosting.pkl"),
    ("Mileage", "models/module_a_groupsplit/mileage/Mileage_XGBoost.pkl"),
]:
    if os.path.exists(path):
        mtime_a = os.path.getmtime(path)
        size_a = os.path.getsize(path)
        print(f"  {task:8s}: Exists = True | Size = {size_a:,} bytes | Modified = {datetime.fromtimestamp(mtime_a).strftime('%Y-%m-%d %H:%M:%S')} | Path = {path}")
    else:
        print(f"  {task:8s}: Exists = FALSE | Path = {path}")

print("\n" + "=" * 80)
print("ENGINE & ARTIFACT AUDIT COMPLETE")
print("=" * 80)
