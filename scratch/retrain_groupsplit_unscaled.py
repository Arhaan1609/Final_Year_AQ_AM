import os, sys, time, joblib, numpy as np, pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from xgboost import XGBRegressor

BASE_DIR = os.path.abspath(".")
MODELS_DIR = os.path.join(BASE_DIR, "models", "module_a_groupsplit")

print("=" * 80)
print("TRAINING GROUP-SPLIT MODELS DIRECTLY ON RAW PHYSICAL UNITS")
print("=" * 80)

# 1. RUL Model on Raw Data
print("\n--- 1. Training RUL Model (Raw Physical Units) ---")
df_charge_p = os.path.join(BASE_DIR, "data", "processed", "charge_cycles.csv")
if not os.path.exists(df_charge_p):
    df_charge_p = os.path.join(BASE_DIR, "data", "processed", "module_a_fleet_telematics", "master_dataset.csv")

df_master = pd.read_csv(os.path.join(BASE_DIR, "data", "processed", "module_a_fleet_telematics", "master_dataset.csv"), low_memory=False)

# Build raw RUL dataset from charge cycles / master
# Target: RUL = max(0, 1500 - cycles) or derived proxy
df_rul_raw = df_master.dropna(subset=["odometer", "chassis_no"]).copy()
# compute cycles from odometer if charge_cycle_count is missing
df_rul_raw["charge_cycles"] = df_rul_raw["charge_cycle_count"].fillna(df_rul_raw["odometer"] / 58.0)
df_rul_raw["rul_proxy"] = np.clip(1500.0 - df_rul_raw["charge_cycles"], 0.0, 1500.0)
df_rul_raw["days_in_service"] = df_rul_raw["days_in_service"].fillna(df_rul_raw["charge_cycles"] * 1.25)
df_rul_raw["miles_per_charge"] = df_rul_raw["miles_per_charge"].fillna(np.clip(120.0 - df_rul_raw["charge_cycles"] * 0.045, 35.0, 130.0))
df_rul_raw["degradation_factor"] = np.clip(df_rul_raw["charge_cycles"] / 1400.0, 0.0, 1.0)
df_rul_raw["soh_mean"] = df_rul_raw["soh"].fillna(95.0)

rul_features = ["odometer", "charge_cycles", "days_in_service", "miles_per_charge", "degradation_factor", "soh_mean", "oem_encoded", "model_encoded"]
X_rul = df_rul_raw[rul_features].copy()
y_rul = df_rul_raw["rul_proxy"].values
groups_rul = df_rul_raw["chassis_no"].values

gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
train_idx, test_idx = next(gss.split(X_rul, y_rul, groups=groups_rul))

X_train_r, X_test_r = X_rul.iloc[train_idx], X_rul.iloc[test_idx]
y_train_r, y_test_r = y_rul[train_idx], y_rul[test_idx]

rul_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42))
])
rul_pipeline.fit(X_train_r, y_train_r)
y_pred_r = rul_pipeline.predict(X_test_r)
r2_r = r2_score(y_test_r, y_pred_r)
mae_r = mean_absolute_error(y_test_r, y_pred_r)
print(f"  RUL Group-Split Test R2: {r2_r:.4f} | MAE: {mae_r:.2f} cycles")
os.makedirs(os.path.join(MODELS_DIR, "rul"), exist_ok=True)
joblib.dump(rul_pipeline, os.path.join(MODELS_DIR, "rul", "RUL_GradientBoosting.pkl"))

# 2. Mileage Model on Raw Data
print("\n--- 2. Training Mileage Model (Raw Physical Units) ---")
df_trip_raw = df_master.dropna(subset=["avg_trip_speed", "avg_trip_distance", "vehicle_no"]).copy()
df_trip_raw["run_kms"] = df_trip_raw["avg_trip_distance"].fillna(45.0)
df_trip_raw["avg_speed"] = df_trip_raw["avg_trip_speed"].fillna(32.0)
df_trip_raw["max_speed"] = df_trip_raw["avg_speed"] + 15.0
df_trip_raw["trip_duration_hrs"] = df_trip_raw["run_kms"] / df_trip_raw["avg_speed"].replace(0, 30.0)
df_trip_raw["stoppage_count"] = 3.0
df_trip_raw["energy_utilized"] = df_trip_raw["avg_energy_utilized"].fillna(df_trip_raw["run_kms"] * 0.16)
df_trip_raw["energy_efficiency"] = df_trip_raw["energy_utilized"] / df_trip_raw["run_kms"].replace(0, 1.0)
df_trip_raw["trip_intensity"] = df_trip_raw["avg_speed"] * df_trip_raw["trip_duration_hrs"]
df_trip_raw["speed_ratio"] = df_trip_raw["avg_speed"] / df_trip_raw["max_speed"]
df_trip_raw["stoppage_density"] = df_trip_raw["stoppage_count"] / df_trip_raw["trip_duration_hrs"]

# Base range per charge target [km]
df_trip_raw["mileage_per_charge"] = np.clip(135.0 - (df_trip_raw["avg_speed"] - 25.0)*0.8 - (df_trip_raw["energy_efficiency"] - 0.15)*120.0, 40.0, 160.0)

mil_features = ["run_kms", "avg_speed", "max_speed", "trip_duration_hrs", "stoppage_count", "energy_efficiency", "trip_intensity", "speed_ratio", "stoppage_density", "energy_utilized", "hour", "day_of_week", "month", "is_weekend", "is_peak", "oem_encoded", "model_encoded"]
X_mil = df_trip_raw[mil_features].copy()
y_mil = df_trip_raw["mileage_per_charge"].values
groups_mil = df_trip_raw["vehicle_no"].values

train_idx_m, test_idx_m = next(gss.split(X_mil, y_mil, groups=groups_mil))
X_train_m, X_test_m = X_mil.iloc[train_idx_m], X_mil.iloc[test_idx_m]
y_train_m, y_test_m = y_mil[train_idx_m], y_mil[test_idx_m]

mil_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42))
])
mil_pipeline.fit(X_train_m, y_train_m)
y_pred_m = mil_pipeline.predict(X_test_m)
r2_m = r2_score(y_test_m, y_pred_m)
mae_m = mean_absolute_error(y_test_m, y_pred_m)
print(f"  Mileage Group-Split Test R2: {r2_m:.4f} | MAE: {mae_m:.2f} km")
os.makedirs(os.path.join(MODELS_DIR, "mileage"), exist_ok=True)
joblib.dump(mil_pipeline, os.path.join(MODELS_DIR, "mileage", "Mileage_XGBoost.pkl"))

# 3. SOC Model on Raw Data
print("\n--- 3. Training SOC Model (Raw Physical Units) ---")
df_soc_raw = df_master.dropna(subset=["battery_voltage", "battery_temp", "battery_current", "soc", "chassis_no"]).copy()
df_soc_raw["abs_current"] = np.abs(df_soc_raw["battery_current"])
df_soc_raw["is_charging"] = (df_soc_raw["battery_current"] > 0).astype(int)
df_soc_raw["voltage_deviation"] = df_soc_raw["battery_voltage"] - 72.0
df_soc_raw["temp_stress_index"] = np.clip((df_soc_raw["battery_temp"] - 25.0)/30.0, 0.0, 1.0)
df_soc_raw["odometer_diff"] = 0.0

soc_features = ["battery_voltage", "battery_temp", "battery_current", "abs_current", "is_charging", "odometer", "odometer_diff", "temp_stress_index", "voltage_deviation", "drive_mode_encoded", "hour", "day_of_week", "month", "is_weekend", "is_peak", "oem_encoded", "model_encoded"]
X_soc = df_soc_raw[soc_features].copy()
y_soc = df_soc_raw["soc"].values
groups_soc = df_soc_raw["chassis_no"].values

train_idx_s, test_idx_s = next(gss.split(X_soc, y_soc, groups=groups_soc))
X_train_s, X_test_s = X_soc.iloc[train_idx_s], X_soc.iloc[test_idx_s]
y_train_s, y_test_s = y_soc[train_idx_s], y_soc[test_idx_s]

soc_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("model", XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42))
])
soc_pipeline.fit(X_train_s, y_train_s)
y_pred_s = soc_pipeline.predict(X_test_s)
r2_s = r2_score(y_test_s, y_pred_s)
mae_s = mean_absolute_error(y_test_s, y_pred_s)
print(f"  SOC Group-Split Test R2: {r2_s:.4f} | MAE: {mae_s:.2f} %")
os.makedirs(os.path.join(MODELS_DIR, "soc"), exist_ok=True)
joblib.dump(soc_pipeline, os.path.join(MODELS_DIR, "soc", "SOC_XGBoost.pkl"))

print("\n[SUCCESS] Retrained clean unscaled group-split models for SOC, RUL, and Mileage!")
