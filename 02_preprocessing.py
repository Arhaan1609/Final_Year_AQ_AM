"""
02_preprocessing.py — Data Cleaning, Outlier Handling, and Standardization.

Reads ingested CSVs → cleans → outputs cleaned CSVs to processed_data/
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from utils import (
    get_logger, print_header, print_step, print_success, print_warning,
    replace_sentinels, remove_duplicates, clip_outliers_iqr,
    safe_numeric, parse_timestamp, extract_temporal_features,
    parse_gps, save_csv, load_csv
)

logger = get_logger("02_preprocessing", cfg.LOGS_DIR)


# ─────────────────────────────────────────────
#  NUMERIC COLUMN LISTS PER DATASET
# ─────────────────────────────────────────────
ALERT_NUMERIC = ["speed", "soc", "battery_voltage", "battery_temp", "aux_batt_voltage"]
TRIP_NUMERIC  = [
    "start_odometer", "end_odometer", "run_kms",
    "soc_at_start", "soc_at_end", "soc_drain",
    "stoppage_count", "energy_utilized", "avg_speed", "max_speed"
]
CHARGE_NUMERIC = [
    "charge_cycle_count", "odometer", "soc_at_charge",
    "first_service_days", "mile_avg", "miles_per_charge", "days_in_service",
    "start_odometer_charge_cycle", "start_odometer_charge_cycle_max",
    "start_odometer_no_charge"
]
OEM_NUMERIC = [
    "odometer", "soc", "soh", "charge_state_pct",
    "battery_voltage", "battery_current", "battery_temp",
    "cell_temp", "motor_temp", "range_km", "latitude", "longitude"
]
DEVICE_NUMERIC = [
    "odometer", "soc", "soh", "battery_voltage", "battery_current",
    "battery_temp", "cell_temp", "motor_temp", "charge_state_pct",
    "latitude", "longitude"
]


# ─────────────────────────────────────────────
#  ALERT LOG CLEANING
# ─────────────────────────────────────────────
def clean_alert_logs(df: pd.DataFrame) -> pd.DataFrame:
    print_step("Cleaning Alert Logs...")
    df = replace_sentinels(df)
    df = remove_duplicates(df, logger=logger)

    # Numeric conversion
    for col in ALERT_NUMERIC:
        if col in df.columns:
            df[col] = safe_numeric(df[col])

    # Timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = parse_timestamp(df["timestamp"], logger)
        df = extract_temporal_features(df, "timestamp")

    # GPS
    if "gps" in df.columns:
        df[["latitude", "longitude"]] = df["gps"].apply(
            lambda x: pd.Series(parse_gps(x))
        )

    # OEM/Model split
    if "oem_model" in df.columns:
        split = df["oem_model"].str.split(" ", n=1, expand=True)
        df["oem"]   = split[0].str.strip()
        df["model"] = split[1].str.strip() if 1 in split.columns else np.nan

    # Alert type encoding
    if "alert_type" in df.columns:
        df["alert_type_encoded"] = LabelEncoder().fit_transform(
            df["alert_type"].fillna("Unknown").astype(str)
        )

    # Outlier clipping
    df = clip_outliers_iqr(df, ALERT_NUMERIC, factor=cfg.TRAIN_CONFIG["outlier_iqr_factor"], logger=logger)

    # SoC range guard [0, 100]
    if "soc" in df.columns:
        df["soc"] = df["soc"].clip(0, 100)

    # Drop extreme invalids
    df = df[df["battery_voltage"].between(20, 150, inclusive="both") | df["battery_voltage"].isna()]

    logger.info(f"  Alert Logs cleaned: {len(df):,} rows")
    return df


# ─────────────────────────────────────────────
#  TRIP LOG CLEANING
# ─────────────────────────────────────────────
def parse_trip_duration(duration_str) -> float:
    """Parse '05h 32m 10s' -> hours (float)."""
    if pd.isna(duration_str):
        return np.nan
    s = str(duration_str)
    hrs = mins = secs = 0
    try:
        import re
        h = re.search(r"(\d+)\s*h", s)
        m = re.search(r"(\d+)\s*m", s)
        sec = re.search(r"(\d+)\s*s", s)
        if h: hrs  = int(h.group(1))
        if m: mins = int(m.group(1))
        if sec: secs = int(sec.group(1))
        return hrs + mins / 60 + secs / 3600
    except Exception:
        return np.nan


def clean_trip_logs(df: pd.DataFrame) -> pd.DataFrame:
    print_step("Cleaning Trip Logs...")
    df = replace_sentinels(df)
    df = remove_duplicates(df, logger=logger)

    # Numeric conversion
    for col in TRIP_NUMERIC:
        if col in df.columns:
            df[col] = safe_numeric(df[col])

    # Parse duration
    if "duration" in df.columns:
        df["trip_duration_hrs"] = df["duration"].apply(parse_trip_duration)

    # Timestamps
    for ts_col in ["start_time", "end_time"]:
        if ts_col in df.columns:
            df[ts_col] = parse_timestamp(df[ts_col], logger)

    # Use start_time as primary timestamp
    if "start_time" in df.columns:
        df = extract_temporal_features(df, "start_time")
        df.rename(columns={"start_time": "timestamp"}, inplace=True)

    # OEM/Model split
    if "oem_model" in df.columns:
        split = df["oem_model"].str.split(" ", n=1, expand=True)
        df["oem"]   = split[0].str.strip()
        df["model"] = split[1].str.strip() if 1 in split.columns else np.nan

    # Derived columns
    df["soc_drain"] = safe_numeric(df.get("soc_drain", np.nan))
    if "soc_at_start" in df.columns and "soc_at_end" in df.columns:
        df["soc_drain_calc"] = df["soc_at_start"] - df["soc_at_end"]

    # Outlier clipping
    df = clip_outliers_iqr(df, TRIP_NUMERIC, factor=cfg.TRAIN_CONFIG["outlier_iqr_factor"], logger=logger)

    # Physical validity guards
    if "run_kms" in df.columns:
        df = df[(df["run_kms"] >= 0) | df["run_kms"].isna()]
    if "soc_at_start" in df.columns:
        df["soc_at_start"] = df["soc_at_start"].clip(0, 100)
    if "soc_at_end" in df.columns:
        df["soc_at_end"] = df["soc_at_end"].clip(0, 100)

    # City encoding
    if "city" in df.columns:
        df["city_encoded"] = LabelEncoder().fit_transform(
            df["city"].fillna("Unknown").astype(str)
        )

    logger.info(f"  Trip Logs cleaned: {len(df):,} rows")
    return df


# ─────────────────────────────────────────────
#  CHARGE CYCLE CLEANING
# ─────────────────────────────────────────────
def clean_charge_cycles(df: pd.DataFrame) -> pd.DataFrame:
    print_step("Cleaning Charge Cycle Logs...")
    df = replace_sentinels(df)
    df = remove_duplicates(df, subset=["chassis_no", "timestamp"], logger=logger)

    # Numeric conversion
    for col in CHARGE_NUMERIC:
        if col in df.columns:
            df[col] = safe_numeric(df[col])

    # Timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = parse_timestamp(df["timestamp"], logger)

    # OEM encoding
    if "oem" in df.columns:
        df["oem_encoded"] = LabelEncoder().fit_transform(
            df["oem"].fillna("Unknown").astype(str)
        )
    if "model" in df.columns:
        df["model_encoded"] = LabelEncoder().fit_transform(
            df["model"].fillna("Unknown").astype(str)
        )

    # Outlier clipping
    df = clip_outliers_iqr(df, CHARGE_NUMERIC, factor=cfg.TRAIN_CONFIG["outlier_iqr_factor"], logger=logger)

    # Sanity guards
    if "soc_at_charge" in df.columns:
        df["soc_at_charge"] = df["soc_at_charge"].clip(0, 100)
    if "charge_cycle_count" in df.columns:
        df = df[df["charge_cycle_count"] >= 0]

    logger.info(f"  Charge Cycles cleaned: {len(df):,} rows")
    return df


# ─────────────────────────────────────────────
#  OEM TELEMETRY CLEANING
# ─────────────────────────────────────────────
def clean_oem_telemetry(df: pd.DataFrame) -> pd.DataFrame:
    print_step("Cleaning OEM Telemetry (SOH source)...")
    df = replace_sentinels(df)
    df = remove_duplicates(df, subset=["chassis_no", "timestamp"], logger=logger)

    # Numeric conversion
    for col in OEM_NUMERIC:
        if col in df.columns:
            df[col] = safe_numeric(df[col])

    # Timestamp
    if "timestamp" in df.columns:
        df["timestamp"] = parse_timestamp(df["timestamp"], logger)
        df = extract_temporal_features(df, "timestamp")

    # Encode categoricals
    for cat_col, encoded_col in [("oem", "oem_encoded"), ("model", "model_encoded"),
                                   ("drive_mode", "drive_mode_encoded"),
                                   ("vehicle_status", "vehicle_status_encoded")]:
        if cat_col in df.columns:
            df[encoded_col] = LabelEncoder().fit_transform(
                df[cat_col].fillna("Unknown").astype(str)
            )

    # Outlier clipping
    df = clip_outliers_iqr(df, OEM_NUMERIC, factor=cfg.TRAIN_CONFIG["outlier_iqr_factor"], logger=logger)

    # Guard physical limits
    if "soc" in df.columns:
        df["soc"] = df["soc"].clip(0, 100)
    if "soh" in df.columns:
        df = df[df["soh"].isna() | df["soh"].between(0, 120)]
        df["soh"] = df["soh"].clip(0, 120)
    if "battery_voltage" in df.columns:
        df = df[df["battery_voltage"].isna() | df["battery_voltage"].between(0, 200)]

    logger.info(f"  OEM Telemetry cleaned: {len(df):,} rows")
    return df


# ─────────────────────────────────────────────
#  DEVICE TELEMETRY CLEANING
# ─────────────────────────────────────────────
def clean_device_telemetry(df: pd.DataFrame) -> pd.DataFrame:
    print_step("Cleaning Device Telemetry...")
    df = replace_sentinels(df)
    df = remove_duplicates(df, subset=["chassis_no", "timestamp"], logger=logger)

    for col in DEVICE_NUMERIC:
        if col in df.columns:
            df[col] = safe_numeric(df[col])

    if "timestamp" in df.columns:
        df["timestamp"] = parse_timestamp(df["timestamp"], logger)
        df = extract_temporal_features(df, "timestamp")

    for cat_col, enc_col in [("oem", "oem_encoded"), ("model", "model_encoded"),
                               ("drive_mode", "drive_mode_encoded"),
                               ("vehicle_status", "vehicle_status_encoded")]:
        if cat_col in df.columns:
            df[enc_col] = LabelEncoder().fit_transform(
                df[cat_col].fillna("Unknown").astype(str)
            )

    df = clip_outliers_iqr(df, DEVICE_NUMERIC, factor=cfg.TRAIN_CONFIG["outlier_iqr_factor"], logger=logger)

    if "soc" in df.columns:
        df["soc"] = df["soc"].clip(0, 100)
    if "soh" in df.columns:
        df["soh"] = df["soh"].clip(0, 120)

    logger.info(f"  Device Telemetry cleaned: {len(df):,} rows")
    return df


# ─────────────────────────────────────────────
#  MASTER MERGE
# ─────────────────────────────────────────────
def build_master_dataset(df_oem: pd.DataFrame, df_charge: pd.DataFrame,
                          df_trip: pd.DataFrame, df_alert: pd.DataFrame) -> pd.DataFrame:
    """
    Build master dataset by merging OEM telemetry (SOH) with charge cycles → enrich with trips.
    OEM telemetry is the primary source (has SOH, SOC, voltage, temp).
    """
    print_step("Building master dataset...")

    # 1. OEM + charge cycles on chassis_no (nearest charge info per record)
    df_oem_sorted = df_oem.sort_values("timestamp")
    df_charge_sorted = df_charge.sort_values("timestamp")

    # Merge on chassis_no — take latest charge info per vehicle
    charge_agg = df_charge.groupby("chassis_no").agg(
        charge_cycle_count=("charge_cycle_count", "last"),
        odometer_charge=("odometer", "last"),
        mile_avg=("mile_avg", "mean"),
        miles_per_charge=("miles_per_charge", "mean"),
        days_in_service=("days_in_service", "last"),
        soc_at_charge=("soc_at_charge", "mean"),
    ).reset_index()

    master = pd.merge(df_oem_sorted, charge_agg, on="chassis_no", how="left")

    # 2. Enrich with trip aggregates on vehicle_no
    if "vehicle_no" in df_trip.columns:
        trip_agg = df_trip.groupby("vehicle_no").agg(
            avg_trip_distance=("run_kms", "mean"),
            total_trip_distance=("run_kms", "sum"),
            avg_energy_utilized=("energy_utilized", "mean"),
            avg_trip_speed=("avg_speed", "mean"),
            avg_soc_drain=("soc_drain", "mean"),
            trip_count=("run_kms", "count"),
        ).reset_index()

        master = pd.merge(master, trip_agg, on="vehicle_no", how="left")

    # 3. Enrich with alert counts per vehicle
    if "vehicle_no" in df_alert.columns and "alert_type" in df_alert.columns:
        alert_agg = df_alert.groupby("vehicle_no").agg(
            alert_count=("alert_type", "count"),
            avg_alert_soc=("soc", "mean"),
            avg_alert_speed=("speed", "mean"),
        ).reset_index()

        master = pd.merge(master, alert_agg, on="vehicle_no", how="left")

    logger.info(f"Master dataset: {len(master):,} rows × {master.shape[1]} cols")
    return master


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def run_preprocessing(data_dict: dict = None):
    print_header("STEP 2: DATA PREPROCESSING & CLEANING")

    # Load from disk if not passed in
    if data_dict is None:
        data_dict = {
            "alert":  pd.read_csv(cfg.PROCESSED_FILES["alert_merged"],     low_memory=False),
            "trip":   pd.read_csv(cfg.PROCESSED_FILES["trip_merged"],       low_memory=False),
            "charge": pd.read_csv(cfg.PROCESSED_FILES["charge_cycles"],     low_memory=False),
            "oem":    pd.read_csv(cfg.PROCESSED_FILES["oem_telemetry"],     low_memory=False),
            "device": pd.read_csv(cfg.PROCESSED_FILES["device_telemetry"], low_memory=False),
        }

    df_alert  = clean_alert_logs(data_dict["alert"])
    df_trip   = clean_trip_logs(data_dict["trip"])
    df_charge = clean_charge_cycles(data_dict["charge"])
    df_oem    = clean_oem_telemetry(data_dict["oem"])
    df_device = clean_device_telemetry(data_dict["device"])

    # Build master
    master = build_master_dataset(df_oem, df_charge, df_trip, df_alert)

    # Save all cleaned datasets
    print_step("Saving cleaned datasets...")
    save_csv(df_alert,  cfg.PROCESSED_FILES["alert_merged"],     logger)
    save_csv(df_trip,   cfg.PROCESSED_FILES["trip_merged"],       logger)
    save_csv(df_charge, cfg.PROCESSED_FILES["charge_cycles"],     logger)
    save_csv(df_oem,    cfg.PROCESSED_FILES["oem_telemetry"],     logger)
    save_csv(df_device, cfg.PROCESSED_FILES["device_telemetry"], logger)
    save_csv(master,    cfg.PROCESSED_FILES["master_dataset"],    logger)

    print_success("Preprocessing complete!")
    return {
        "alert":  df_alert,
        "trip":   df_trip,
        "charge": df_charge,
        "oem":    df_oem,
        "device": df_device,
        "master": master,
    }


if __name__ == "__main__":
    run_preprocessing()
