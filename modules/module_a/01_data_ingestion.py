"""
01_data_ingestion.py — Load, validate, and merge all raw data sources.

Sources:
  Excel: Alert Logs (×2), Trip Reports (×3)
  JSON:  charge_cycles, oem_telemetry, device_telemetry
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from tqdm import tqdm

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from utils import (
    get_logger, print_header, print_step, print_success, print_warning,
    json_to_dataframe, flatten_mongo_record, parse_timestamp,
    replace_sentinels, save_csv, detect_schema, print_schema
)

logger = get_logger("01_data_ingestion", cfg.LOGS_DIR)


# ─────────────────────────────────────────────
#  EXCEL LOADERS
# ─────────────────────────────────────────────
def load_excel_safe(path: str, col_map: dict, name: str) -> pd.DataFrame:
    """Load an Excel file with renamed columns."""
    logger.info(f"Loading Excel: {os.path.basename(path)}")
    df = pd.read_excel(path, dtype=str)
    df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)
    df["source_file"] = os.path.basename(path)
    logger.info(f"  Loaded {len(df):,} rows × {df.shape[1]} cols")
    return df


def load_alert_logs() -> pd.DataFrame:
    print_step("Loading Alert Logs (Excel)...")
    frames = []
    for key in ["alert_log_1", "alert_log_2"]:
        path = cfg.EXCEL_FILES[key]
        df = load_excel_safe(path, cfg.ALERT_COL_MAP, key)
        frames.append(df)
    merged = pd.concat(frames, ignore_index=True)
    logger.info(f"Alert Logs merged: {len(merged):,} rows")
    return merged


def load_trip_logs() -> pd.DataFrame:
    print_step("Loading Trip Report Logs (Excel)...")
    frames = []
    for key in ["trip_log_1", "trip_log_2", "trip_log_3"]:
        path = cfg.EXCEL_FILES[key]
        df = load_excel_safe(path, cfg.TRIP_COL_MAP, key)
        frames.append(df)
    merged = pd.concat(frames, ignore_index=True)
    logger.info(f"Trip Logs merged: {len(merged):,} rows")
    return merged


# ─────────────────────────────────────────────
#  JSON LOADERS
# ─────────────────────────────────────────────
def load_charge_cycles() -> pd.DataFrame:
    print_step("Loading Charge Cycle Logs (JSON)...")
    path = cfg.JSON_FILES["charge_cycles"]
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = json_to_dataframe(data, logger)
    df.rename(columns={k: v for k, v in cfg.CHARGE_CYCLE_COL_MAP.items() if k in df.columns}, inplace=True)
    df.drop(columns=["_id", "__v", "isDeleted"], errors="ignore", inplace=True)
    logger.info(f"Charge Cycles: {len(df):,} rows")
    return df


def load_oem_telemetry() -> pd.DataFrame:
    print_step("Loading OEM Telemetry (JSON) — contains SOH...")
    path = cfg.JSON_FILES["oem_telemetry"]
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = json_to_dataframe(data, logger)
    df.rename(columns={k: v for k, v in cfg.OEM_COL_MAP.items() if k in df.columns}, inplace=True)
    df.drop(columns=["_id", "__v", "mv", "src", "nct"], errors="ignore", inplace=True)
    logger.info(f"OEM Telemetry: {len(df):,} rows")
    return df


def load_device_telemetry() -> pd.DataFrame:
    """
    Load the large (~557MB) device telemetry JSON in streaming fashion.
    Extracts key fields only to keep memory manageable.
    """
    print_step("Loading Device Telemetry (JSON ~557MB) — chunked...")
    path = cfg.JSON_FILES["device_telemetry"]
    file_size_mb = os.path.getsize(path) / (1024 ** 2)
    logger.info(f"  File size: {file_size_mb:.0f} MB")

    KEEP_KEYS = {
        "_id", "rn", "cn", "imei", "oem", "mdl", "dts",
        "soc", "od", "vbv", "vbc", "vbt", "vct", "vmt",
        "soh", "vs", "dm", "ig", "lt", "lng", "gdir",
        "csp", "cc", "cp", "cv", "dte",
    }

    logger.info("  Parsing JSON (this may take a few minutes)...")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    records = []
    for item in tqdm(raw, desc="  Parsing device records"):
        flat = flatten_mongo_record(item)
        slim = {k: v for k, v in flat.items() if k in KEEP_KEYS}
        records.append(slim)

    df = pd.DataFrame(records)
    df.rename(columns={k: v for k, v in cfg.OEM_COL_MAP.items() if k in df.columns}, inplace=True)
    df.drop(columns=["_id", "__v"], errors="ignore", inplace=True)
    logger.info(f"  Device Telemetry: {len(df):,} rows × {df.shape[1]} cols")
    return df


# ─────────────────────────────────────────────
#  DATA VALIDATION
# ─────────────────────────────────────────────
def validate_dataframe(df: pd.DataFrame, name: str):
    logger.info(f"\n  Validating: {name}")
    schema = detect_schema(df)
    print_schema(schema, title=name)
    high_null = [c for c, v in schema.items() if v["null_pct"] > 50]
    if high_null:
        print_warning(f"{name}: High null% columns: {high_null}")
    return schema


# ─────────────────────────────────────────────
#  VEHICLE ID STANDARDIZATION
# ─────────────────────────────────────────────
def standardize_vehicle_no(df: pd.DataFrame, col: str = "vehicle_no") -> pd.DataFrame:
    """Normalize registration numbers: uppercase, strip spaces."""
    if col in df.columns:
        df[col] = df[col].astype(str).str.upper().str.strip().str.replace(r"\s+", "", regex=True)
    return df


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def run_ingestion():
    print_header("STEP 1: DATA INGESTION")

    # Load all sources
    df_alert  = load_alert_logs()
    df_trip   = load_trip_logs()
    df_charge = load_charge_cycles()
    df_oem    = load_oem_telemetry()
    df_device = load_device_telemetry()

    # Standardize vehicle IDs
    for df, col in [
        (df_alert, "vehicle_no"), (df_trip, "vehicle_no"),
        (df_oem, "vehicle_no"),   (df_oem, "chassis_no"),
        (df_charge, "vehicle_no"), (df_charge, "chassis_no"),
        (df_device, "vehicle_no"), (df_device, "chassis_no"),
    ]:
        standardize_vehicle_no(df, col)

    # Replace sentinel missing values
    for df in [df_alert, df_trip, df_charge, df_oem, df_device]:
        replace_sentinels(df)

    # Validate schemas
    validate_dataframe(df_alert,  "Alert Logs")
    validate_dataframe(df_trip,   "Trip Reports")
    validate_dataframe(df_charge, "Charge Cycles")
    validate_dataframe(df_oem,    "OEM Telemetry")
    validate_dataframe(df_device, "Device Telemetry")

    # Save ingested (raw-merged) data
    print_step("Saving ingested datasets...")
    save_csv(df_alert,  cfg.PROCESSED_FILES["alert_merged"],     logger)
    save_csv(df_trip,   cfg.PROCESSED_FILES["trip_merged"],       logger)
    save_csv(df_charge, cfg.PROCESSED_FILES["charge_cycles"],     logger)
    save_csv(df_oem,    cfg.PROCESSED_FILES["oem_telemetry"],     logger)
    save_csv(df_device, cfg.PROCESSED_FILES["device_telemetry"],  logger)

    # Quick summary
    print_success(f"Ingestion complete!")
    for name, df in [
        ("Alert Logs",       df_alert),
        ("Trip Reports",     df_trip),
        ("Charge Cycles",    df_charge),
        ("OEM Telemetry",    df_oem),
        ("Device Telemetry", df_device),
    ]:
        logger.info(f"  {name:<20}: {len(df):>8,} rows | {df.shape[1]:>3} cols | "
                    f"Vehicles: {df.get('vehicle_no', df.get('chassis_no', pd.Series())).nunique()}")

    return {
        "alert":  df_alert,
        "trip":   df_trip,
        "charge": df_charge,
        "oem":    df_oem,
        "device": df_device,
    }


if __name__ == "__main__":
    run_ingestion()
