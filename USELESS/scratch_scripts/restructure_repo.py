import os
import shutil

print("=" * 70)
print("  RESTRUCTURING & ORGANIZING REPOSITORY")
print("=" * 70)

# 1. CREATE USELESS DIRECTORIES
useless_dirs = [
    "USELESS/legacy_module_c_visualizations",
    "USELESS/legacy_module_c_pipelines",
    "USELESS/scratch_scripts",
    "USELESS/stitch_exports",
    "USELESS/mcp_server_artifacts"
]

for d in useless_dirs:
    os.makedirs(d, exist_ok=True)
print("  [1] Created USELESS archive directories.")

# 2. MOVE LEGACY MODULE C FILES TO USELESS
legacy_c_viz = [
    "modules/module_c/advanced_viz.py",
    "modules/module_c/final_viz.py",
    "modules/module_c/visualization.py",
    "modules/module_c/visualization_improved.py",
    "modules/module_c/visualizations.py",
    "modules/module_c/knee_visualization.py",
    "modules/module_c/show_results.py"
]

for f in legacy_c_viz:
    if os.path.exists(f):
        shutil.move(f, os.path.join("USELESS/legacy_module_c_visualizations", os.path.basename(f)))
        print(f"    Archived: {f}")

legacy_c_pipes = [
    "modules/module_c/demo_ensemble.py",
    "modules/module_c/ensemble.py",
    "modules/module_c/improved_pipeline.py",
    "modules/module_c/knee_advanced_pipeline.py",
    "modules/module_c/optimized_pipeline.py",
    "modules/module_c/run_final_pipeline.py",
    "modules/module_c/train_dl.py",
    "modules/module_c/train_evaluate.py",
    "modules/module_c/unified_ensemble.py",
    "modules/module_c/data_integrator.py",
    "modules/module_c/knee_detection.py",
    "modules/module_c/knee_final.py"
]

for f in legacy_c_pipes:
    if os.path.exists(f):
        shutil.move(f, os.path.join("USELESS/legacy_module_c_pipelines", os.path.basename(f)))
        print(f"    Archived: {f}")

# Move stitch_exports and mcp-server
if os.path.exists("stitch_exports"):
    for f in os.listdir("stitch_exports"):
        src = os.path.join("stitch_exports", f)
        dst = os.path.join("USELESS/stitch_exports", f)
        if not os.path.exists(dst):
            shutil.move(src, dst)
    shutil.rmtree("stitch_exports", ignore_errors=True)
    print("    Archived: stitch_exports/")

if os.path.exists("mcp-server"):
    for f in os.listdir("mcp-server"):
        src = os.path.join("mcp-server", f)
        dst = os.path.join("USELESS/mcp_server_artifacts", f)
        if not os.path.exists(dst):
            shutil.move(src, dst)
    shutil.rmtree("mcp-server", ignore_errors=True)
    print("    Archived: mcp-server/")

# Move scratch scripts
if os.path.exists("scratch"):
    for f in os.listdir("scratch"):
        src = os.path.join("scratch", f)
        dst = os.path.join("USELESS/scratch_scripts", f)
        if not os.path.exists(dst):
            shutil.copy(src, dst)
    print("    Archived: scratch/")

# 3. ORGANIZE DATA DIRECTORY BY MODULE
data_subdirs = [
    "data/processed/module_a_fleet_telematics",
    "data/processed/module_b_thermal_deep_soh",
    "data/processed/module_c_knee_and_behavior"
]

for d in data_subdirs:
    os.makedirs(d, exist_ok=True)

# Copy/Move Module A datasets
mod_a_data = [
    "features_soc.csv", "features_soh.csv", "features_rul.csv",
    "features_mileage.csv", "master_dataset.csv"
]
for f in mod_a_data:
    src = os.path.join("data/processed", f)
    dst = os.path.join("data/processed/module_a_fleet_telematics", f)
    if os.path.exists(src):
        shutil.copy(src, dst)

# Copy/Move Module B datasets
mod_b_data = [
    "thermal_alerts_balanced_50_50.csv", "thermal_alerts_balanced_50_50.parquet",
    "soh_timeseries_euler_processed.parquet"
]
for f in mod_b_data:
    src = os.path.join("data/processed", f)
    dst = os.path.join("data/processed/module_b_thermal_deep_soh", f)
    if os.path.exists(src):
        shutil.copy(src, dst)

# Copy/Move Module C datasets
mod_c_data = [
    "features_knee_prognostics.csv", "charge_cycles_clean.csv", "oem_telemetry_clean.csv",
    "device_telemetry_clean.csv", "trip_logs_merged.csv", "alert_logs_merged.csv"
]
for f in mod_c_data:
    src = os.path.join("data/processed", f)
    dst = os.path.join("data/processed/module_c_knee_and_behavior", f)
    if os.path.exists(src):
        shutil.copy(src, dst)

print("  [2] Organized data/processed/ into module_a, module_b, module_c subdirectories.")

# 4. ORGANIZE MODELS DIRECTORY BY MODULE
model_subdirs = [
    "models/module_a",
    "models/module_b",
    "models/module_c"
]
for d in model_subdirs:
    os.makedirs(d, exist_ok=True)

# Module A models
for task in ["soc", "soh", "rul", "mileage"]:
    src_dir = os.path.join("models", task)
    dst_dir = os.path.join("models/module_a", task)
    if os.path.exists(src_dir) and not os.path.exists(dst_dir):
        shutil.copytree(src_dir, dst_dir)

# Module B weights
if os.path.exists("modules/module_b/weights"):
    for f in os.listdir("modules/module_b/weights"):
        src = os.path.join("modules/module_b/weights", f)
        dst = os.path.join("models/module_b", f)
        if os.path.isfile(src):
            shutil.copy(src, dst)

# Module C weights
if os.path.exists("modules/module_c/best_xgboost_model.json"):
    shutil.copy("modules/module_c/best_xgboost_model.json", "models/module_c/best_xgboost_model.json")
if os.path.exists("modules/module_c/feature_scaler.pkl"):
    shutil.copy("modules/module_c/feature_scaler.pkl", "models/module_c/feature_scaler.pkl")
if os.path.exists("models/knee_prognostics/best_xgboost_model.json"):
    shutil.copy("models/knee_prognostics/best_xgboost_model.json", "models/module_c/best_xgboost_model.json")
if os.path.exists("models/knee_prognostics/feature_scaler.pkl"):
    shutil.copy("models/knee_prognostics/feature_scaler.pkl", "models/module_c/feature_scaler.pkl")
if os.path.exists("models/driver_behavior/behavior_rules.json"):
    shutil.copy("models/driver_behavior/behavior_rules.json", "models/module_c/behavior_rules.json")

print("  [3] Organized models/ into models/module_a, models/module_b, models/module_c.")
print("\n" + "=" * 70)
print("  RESTRUCTURING COMPLETED SUCCESSFULLY")
print("=" * 70)
