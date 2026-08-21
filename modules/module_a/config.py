"""
config.py — Central configuration for EV Battery Analysis System (Module A)

NOTE: This file lives at modules/module_a/config.py.
      BASE_DIR resolves to the project root (Final_Year_Project_1/).
"""

import os

# ─────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────
# BASE_DIR = project root (Final_Year_Project_1/)
# This file lives 2 levels deep: modules/module_a/config.py
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

RAW_DATA_DIR   = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR  = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR     = os.path.join(BASE_DIR, "models")
RESULTS_DIR    = os.path.join(BASE_DIR, "results")
PLOTS_DIR      = os.path.join(RESULTS_DIR, "plots")
REPORTS_DIR    = os.path.join(RESULTS_DIR, "reports")
LOGS_DIR       = os.path.join(BASE_DIR, "logs")

# Create all output directories
for d in [PROCESSED_DIR, MODELS_DIR, RESULTS_DIR, PLOTS_DIR, REPORTS_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# ─────────────────────────────────────────────
#  RAW DATA FILES
# ─────────────────────────────────────────────
EXCEL_FILES = {
    "alert_log_1":  os.path.join(RAW_DATA_DIR, "Alert Log12-FEB-2026_11_47_03.xlsx"),
    "alert_log_2":  os.path.join(RAW_DATA_DIR, "Alert Log12-FEB-2026_11_47_07.xlsx"),
    "trip_log_1":   os.path.join(RAW_DATA_DIR, "Trip Report Log12-FEB-2026_11_25_15.xlsx"),
    "trip_log_2":   os.path.join(RAW_DATA_DIR, "Trip Report Log12-FEB-2026_11_25_21.xlsx"),
    "trip_log_3":   os.path.join(RAW_DATA_DIR, "Trip Report Log12-FEB-2026_11_25_29.xlsx"),
}

JSON_FILES = {
    "charge_cycles": os.path.join(RAW_DATA_DIR, "magenta-telematics-prod.charge_cycles_logs.json"),
    "oem_telemetry": os.path.join(RAW_DATA_DIR, "tms_history_l2_oem.json"),
    "device_telemetry": os.path.join(RAW_DATA_DIR, "tms_history_l2_device.json"),
}

# ─────────────────────────────────────────────
#  PROCESSED DATA OUTPUT FILES
# ─────────────────────────────────────────────
PROCESSED_FILES = {
    "alert_merged":     os.path.join(PROCESSED_DIR, "alert_logs_merged.csv"),
    "trip_merged":      os.path.join(PROCESSED_DIR, "trip_logs_merged.csv"),
    "charge_cycles":    os.path.join(PROCESSED_DIR, "charge_cycles_clean.csv"),
    "oem_telemetry":    os.path.join(PROCESSED_DIR, "oem_telemetry_clean.csv"),
    "device_telemetry": os.path.join(PROCESSED_DIR, "device_telemetry_clean.csv"),
    "master_dataset":   os.path.join(PROCESSED_DIR, "master_dataset.csv"),
    "features_soc":     os.path.join(PROCESSED_DIR, "features_soc.csv"),
    "features_soh":     os.path.join(PROCESSED_DIR, "features_soh.csv"),
    "features_rul":     os.path.join(PROCESSED_DIR, "features_rul.csv"),
    "features_mileage": os.path.join(PROCESSED_DIR, "features_mileage.csv"),
}

# ─────────────────────────────────────────────
#  TARGET VARIABLES
# ─────────────────────────────────────────────
TARGETS = {
    "SOC":     "soc",
    "SOH":     "soh",
    "RUL":     "rul_proxy",
    "Mileage": "mileage_per_charge",
}

# ─────────────────────────────────────────────
#  FEATURE GROUPS (input to models)
# ─────────────────────────────────────────────
# NOTE: These lists are for reference only. 04_model_training.py determines
# the actual feature columns used via EXCLUDE_COLS_PER_TASK (line ~82).
# The definitive leak-free feature sets are documented in 03_feature_engineering.py.

SOC_FEATURES = [
    # Hardware sensors (physically causal, no leakage)
    "battery_voltage", "battery_temp", "battery_current",
    "abs_current", "is_charging", "odometer", "odometer_diff",
    # Derived from voltage/current only
    "voltage_deviation", "temp_stress_index",
    # Context
    "drive_mode_encoded", "hour", "day_of_week", "month",
    "is_weekend", "is_peak", "oem_encoded", "model_encoded",
]

SOH_FEATURES = [
    # Hardware + long-term wear signals (soc removed — not causal of degradation)
    "battery_voltage", "battery_temp", "battery_current", "abs_current",
    "odometer", "odometer_diff",
    # Charge history (charge_cycle_count is valid here — NOT the target)
    "charge_cycle_count", "mile_avg", "miles_per_charge",
    "days_in_service", "degradation_factor",
    "temp_stress_index", "voltage_deviation",
    "oem_encoded", "model_encoded",
]

RUL_FEATURES = [
    # Indirect degradation signals ONLY
    # charge_cycle_count EXCLUDED (rul_proxy = 1500 - count => r=-1.0)
    "odometer", "soc_at_charge", "mile_avg", "miles_per_charge",
    "days_in_service", "degradation_factor", "charge_frequency",
    "soh_mean",
    "miles_per_charge_rolling_3", "miles_per_charge_rolling_5",
    "miles_per_charge_rolling_10",
    "oem_encoded", "model_encoded",
]

MILEAGE_FEATURES = [
    # Driving behaviour features only
    # soc_drain / distance_per_soc_drop / soc_drain_rate EXCLUDED (define target algebraically)
    "run_kms", "avg_speed", "max_speed", "trip_duration_hrs", "stoppage_count",
    "energy_efficiency", "trip_intensity", "speed_ratio", "stoppage_density",
    "energy_utilized",
    "hour", "day_of_week", "month", "is_weekend", "is_peak",
    "oem_encoded", "city_encoded",
]

# ─────────────────────────────────────────────
#  ML MODEL HYPERPARAMETER GRIDS
# ─────────────────────────────────────────────
RF_PARAM_GRID = {
    "n_estimators": [100, 200, 300],
    "max_depth": [None, 10, 20],
    "min_samples_split": [2, 5],
    "max_features": ["sqrt", "log2"],
}

XGB_PARAM_GRID = {
    "n_estimators": [100, 200, 300],
    "learning_rate": [0.05, 0.1, 0.2],
    "max_depth": [3, 5, 7],
    "subsample": [0.8, 1.0],
}

GBM_PARAM_GRID = {
    "n_estimators": [100, 200],
    "learning_rate": [0.05, 0.1],
    "max_depth": [3, 5],
}

SVR_PARAM_GRID = {
    "C": [0.1, 1, 10],
    "epsilon": [0.01, 0.1],
    "kernel": ["rbf", "linear"],
}

# ─────────────────────────────────────────────
#  DEEP LEARNING CONFIG
# ─────────────────────────────────────────────
DL_CONFIG = {
    "epochs": 100,
    "batch_size": 64,
    "patience": 15,          # early stopping
    "validation_split": 0.2,
    "lstm_units": [128, 64],
    "gru_units": [128, 64],
    "ann_layers": [256, 128, 64],
    "cnn_filters": [64, 32],
    "cnn_kernel": 3,
    "dropout_rate": 0.2,
    "learning_rate": 0.001,
    "sequence_length": 10,   # for LSTM/GRU/CNN
}

# ─────────────────────────────────────────────
#  TRAINING CONFIG
# ─────────────────────────────────────────────
TRAIN_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "cv_folds": 5,
    "n_random_search_iter": 20,
    "outlier_iqr_factor": 1.5,
    "rolling_windows": [5, 10, 20],
    "nominal_battery_cycles": 1500,   # typical EV battery cycle life
    "nominal_battery_years": 8,
}

# ─────────────────────────────────────────────
#  COLUMN MAPPING (raw → standard)
# ─────────────────────────────────────────────
ALERT_COL_MAP = {
    "Vehicle No.":          "vehicle_no",
    "New Vehicle No.":      "new_vehicle_no",
    "OEM & Model":          "oem_model",
    "Date & Time":          "timestamp",
    "Alert Type":           "alert_type",
    "Speed (kmph)":         "speed",
    "SoC (% )":             "soc",
    "Batt. Volt. (V)":      "battery_voltage",
    "Batt. Temp.(°c)":      "battery_temp",
    "GPS":                  "gps",
    "Aux. Batt. Under Volt. (V)": "aux_batt_voltage",
}

TRIP_COL_MAP = {
    "Vehicle number":         "vehicle_no",
    "Vehicle No.":            "vehicle_no",
    "New Vehicle No.":        "new_vehicle_no",
    "OEM & Model":            "oem_model",
    "City":                   "city",
    "Start Time":             "start_time",
    "End Time":               "end_time",
    "Duration":               "duration",
    "Start Odometer (kms)":   "start_odometer",
    "End Odometer (kms)":     "end_odometer",
    "Run kms (kms)":          "run_kms",
    "Start SoC ( % )":        "soc_at_start",
    "End SoC ( % )":          "soc_at_end",
    "SoC Drain( % )":         "soc_drain",
    "Stoppage Count":         "stoppage_count",
    "Energy Utilized (Kwh)":  "energy_utilized",
    "Avg. Speed (kmph)":      "avg_speed",
    "Max. Speed (kmph)":      "max_speed",
    "Start GPS":              "start_gps",
    "End GPS":                "end_gps",
}

OEM_COL_MAP = {
    "rn":   "vehicle_no",
    "cn":   "chassis_no",
    "oem":  "oem",
    "mdl":  "model",
    "od":   "odometer",
    "soc":  "soc",
    "soh":  "soh",
    "dte":  "range_km",
    "csp":  "charge_state_pct",
    "vbv":  "battery_voltage",
    "vbc":  "battery_current",
    "vbt":  "battery_temp",
    "vct":  "cell_temp",
    "vmt":  "motor_temp",
    "cim":  "charge_inlet_mode",
    "dm":   "drive_mode",
    "vs":   "vehicle_status",
    "lt":   "latitude",
    "lng":  "longitude",
    "dts":  "timestamp",
}

CHARGE_CYCLE_COL_MAP = {
    "cn":      "chassis_no",
    "dts":     "timestamp",
    "ccc":     "charge_cycle_count",
    "cod":     "odometer",
    "csoc":    "soc_at_charge",
    "fsdm":    "first_service_days",
    "mdl":     "model",
    "mileAvg": "mile_avg",
    "mpc":     "miles_per_charge",
    "oem":     "oem",
    "rn":      "vehicle_no",
    "sds":     "days_in_service",
    "sodcc":   "start_odometer_charge_cycle",
    "sodcmc":  "start_odometer_charge_cycle_max",
    "sodnmc":  "start_odometer_no_charge",
}

DEVICE_COL_MAP = {
    "rn":   "vehicle_no",
    "cn":   "chassis_no",
    "imei": "imei",
    "oem":  "oem",
    "dts":  "timestamp",
    "soc":  "soc",
}
