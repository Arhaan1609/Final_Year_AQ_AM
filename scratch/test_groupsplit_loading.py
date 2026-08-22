import os, sys, joblib, numpy as np, pandas as pd

MODELS_DIR = os.path.abspath("models")

# 1. Test SOC from module_a_groupsplit/soc
soc_path = os.path.join(MODELS_DIR, "module_a_groupsplit", "soc", "SOC_Lasso.pkl")
print("Loading SOC model:", soc_path)
soc_model = joblib.load(soc_path)
print("  SOC Model type:", type(soc_model))
if hasattr(soc_model, "feature_names_in_"):
    print("  SOC features:", soc_model.feature_names_in_)

# 2. Test RUL from module_a_groupsplit/rul
rul_path = os.path.join(MODELS_DIR, "module_a_groupsplit", "rul", "RUL_GradientBoosting.pkl")
print("\nLoading RUL model:", rul_path)
rul_model = joblib.load(rul_path)
print("  RUL Model type:", type(rul_model))

# 3. Test Mileage from module_a_groupsplit/mileage
mil_path = os.path.join(MODELS_DIR, "module_a_groupsplit", "mileage", "Mileage_XGBoost.pkl")
print("\nLoading Mileage model:", mil_path)
mil_model = joblib.load(mil_path)
print("  Mileage Model type:", type(mil_model))

# 4. Test SOH from module_a_soh_calibrated
soh_path = os.path.join(MODELS_DIR, "module_a_soh_calibrated", "SOH_Calibrated_XGBoost.pkl")
print("\nLoading SOH Calibrated model:", soh_path)
soh_model = joblib.load(soh_path)
print("  SOH Model type:", type(soh_model))
if hasattr(soh_model, "feature_names_in_"):
    print("  SOH features count:", len(soh_model.feature_names_in_))

print("\n[SUCCESS] All 4 group-split / calibrated model artifacts loaded cleanly!")
