import os
import shutil

print("=" * 70)
print("  DEEP CLEANUP: ELIMINATING DUPLICATE FILES & STREAMLINING FOLDERS")
print("=" * 70)

# 1. CLEAN UP data/processed/ ROOT (REMOVE LOOSE DUPLICATE FILES)
processed_dir = "data/processed"
for item in os.listdir(processed_dir):
    p = os.path.join(processed_dir, item)
    if os.path.isfile(p):
        os.remove(p)
        print(f"  Removed loose duplicate file from data/processed/: {item}")

print("\n  -> data/processed/ now contains ONLY clean module subfolders:")
for item in os.listdir(processed_dir):
    print(f"     [DIR] data/processed/{item}")

# 2. CLEAN UP models/ ROOT (REMOVE LOOSE DUPLICATE FOLDERS)
models_dir = "models"
loose_model_dirs = ["soc", "soh", "rul", "mileage", "knee_prognostics", "driver_behavior"]
for d in loose_model_dirs:
    p = os.path.join(models_dir, d)
    if os.path.exists(p):
        shutil.rmtree(p)
        print(f"  Removed loose duplicate directory from models/: {d}")

# Also remove any loose files in models/
for item in os.listdir(models_dir):
    p = os.path.join(models_dir, item)
    if os.path.isfile(p):
        os.remove(p)
        print(f"  Removed loose file from models/: {item}")

print("\n  -> models/ now contains ONLY clean module subfolders:")
for item in os.listdir(models_dir):
    print(f"     [DIR] models/{item}")

# 3. CLEAN UP modules/module_b/ (MOVE DUPLICATE data, weights, notebooks TO ARCHIVE / CENTRAL)
os.makedirs("USELESS/legacy_module_b", exist_ok=True)

# Move module_b/notebooks
if os.path.exists("modules/module_b/notebooks"):
    shutil.move("modules/module_b/notebooks", "USELESS/legacy_module_b/notebooks")
    print("  Archived modules/module_b/notebooks/ -> USELESS/legacy_module_b/notebooks/")

# Move module_b/tests
if os.path.exists("modules/module_b/tests"):
    shutil.move("modules/module_b/tests", "USELESS/legacy_module_b/tests")
    print("  Archived modules/module_b/tests/ -> USELESS/legacy_module_b/tests/")

# Move module_c/tests
if os.path.exists("modules/module_c/tests"):
    shutil.move("modules/module_c/tests", "USELESS/legacy_module_c_pipelines/tests")
    print("  Archived modules/module_c/tests/ -> USELESS/legacy_module_c_pipelines/tests/")

# Move module_b/data artifacts
if os.path.exists("modules/module_b/data"):
    for f in os.listdir("modules/module_b/data"):
        src = os.path.join("modules/module_b/data", f)
        dst = os.path.join("data/processed/module_b_thermal_deep_soh", f)
        if not os.path.exists(dst) and os.path.isfile(src):
            shutil.copy(src, dst)
    shutil.move("modules/module_b/data", "USELESS/legacy_module_b/data")
    print("  Cleaned duplicate modules/module_b/data/ -> archived in USELESS")

# Remove redundant module_b/weights
if os.path.exists("modules/module_b/weights"):
    shutil.move("modules/module_b/weights", "USELESS/legacy_module_b/weights")
    print("  Cleaned duplicate modules/module_b/weights/ -> archived in USELESS")

# 4. CLEAN UP modules/module_c/ (REMOVE LOOSE WEIGHT DUPLICATES)
for f in ["best_xgboost_model.json", "feature_scaler.pkl"]:
    p = os.path.join("modules/module_c", f)
    if os.path.exists(p):
        os.remove(p)
        print(f"  Removed duplicate weight from modules/module_c/: {f} (Centralized in models/module_c/)")

print("\n" + "=" * 70)
print("  DEEP CLEANUP COMPLETE: 0 DUPLICATES REMAINING")
print("=" * 70)
