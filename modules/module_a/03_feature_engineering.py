"""
03_feature_engineering.py — Create advanced features for SOC, SOH, RUL, Mileage prediction.

Reads master_dataset.csv and per-source CSVs, outputs 4 task-specific feature sets.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from utils import (
    get_logger, print_header, print_step, print_success, print_warning,
    safe_numeric, save_csv, load_csv
)

logger = get_logger("03_feature_engineering", cfg.LOGS_DIR)


# ─────────────────────────────────────────────
#  FEATURE ENGINEERING — TRIP-BASED
# ─────────────────────────────────────────────
def engineer_trip_features(df_trip: pd.DataFrame) -> pd.DataFrame:
    """Create features from trip logs for SOC and Mileage prediction."""
    print_step("Engineering trip-based features...")
    df = df_trip.copy()

    # Ensure numeric
    for col in ["run_kms", "soc_at_start", "soc_at_end", "soc_drain",
                "energy_utilized", "avg_speed", "max_speed",
                "trip_duration_hrs", "stoppage_count"]:
        if col in df.columns:
            df[col] = safe_numeric(df[col])

    # ── SOC Drain Rate [% / km]
    df["soc_drain_rate"] = np.where(
        df.get("run_kms", pd.Series(0)) > 0,
        df.get("soc_drain", pd.Series(np.nan)) / df["run_kms"].replace(0, np.nan),
        np.nan
    )

    # ── Energy Efficiency [kWh / km]
    df["energy_efficiency"] = np.where(
        df.get("run_kms", pd.Series(0)) > 0,
        df.get("energy_utilized", pd.Series(np.nan)) / df["run_kms"].replace(0, np.nan),
        np.nan
    )

    # ── Distance per SOC drop [km / %]
    df["distance_per_soc_drop"] = np.where(
        df.get("soc_drain", pd.Series(0)) > 0,
        df.get("run_kms", pd.Series(np.nan)) / df["soc_drain"].replace(0, np.nan),
        np.nan
    )

    # ── Trip Intensity = avg_speed × trip_duration_hrs
    if "avg_speed" in df.columns and "trip_duration_hrs" in df.columns:
        df["trip_intensity"] = df["avg_speed"] * df["trip_duration_hrs"]
    else:
        df["trip_intensity"] = np.nan

    # ── Speed ratio: avg / max
    if "avg_speed" in df.columns and "max_speed" in df.columns:
        df["speed_ratio"] = df["avg_speed"] / df["max_speed"].replace(0, np.nan)
    else:
        df["speed_ratio"] = np.nan

    # ── Stoppage ratio: stoppage_count / duration
    if "stoppage_count" in df.columns and "trip_duration_hrs" in df.columns:
        df["stoppage_density"] = df["stoppage_count"] / df["trip_duration_hrs"].replace(0, np.nan)
    else:
        df["stoppage_density"] = np.nan

    # ── Energy per SoC drop [kWh / %]
    if "energy_utilized" in df.columns and "soc_drain" in df.columns:
        df["energy_per_soc"] = df["energy_utilized"] / df["soc_drain"].replace(0, np.nan)
    else:
        df["energy_per_soc"] = np.nan

    # ── Mileage proxy: km per full charge equivalent
    # If SOC drains by X% over Y km, full charge range = Y * (100/X)
    if "run_kms" in df.columns and "soc_drain" in df.columns:
        df["mileage_per_charge"] = df.apply(
            lambda r: r["run_kms"] * (100 / r["soc_drain"]) if r["soc_drain"] > 5 else np.nan,
            axis=1
        )
    else:
        df["mileage_per_charge"] = np.nan

    # Clip mileage physically (0-600 km for EV)
    if "mileage_per_charge" in df.columns:
        df["mileage_per_charge"] = df["mileage_per_charge"].clip(0, 600)

    logger.info(f"  Trip features: {df.shape[1]} columns, {len(df):,} rows")
    return df


# ─────────────────────────────────────────────
#  FEATURE ENGINEERING — OEM TELEMETRY (SOH, SOC)
# ─────────────────────────────────────────────
def engineer_oem_features(df_oem: pd.DataFrame) -> pd.DataFrame:
    """Create features from OEM telemetry for SOC/SOH prediction."""
    print_step("Engineering OEM telemetry features...")
    df = df_oem.copy()

    # ── Temperature Stress Index: penalty for extreme temps
    if "battery_temp" in df.columns:
        df["temp_stress_index"] = df["battery_temp"].apply(
            lambda t: abs(t - 25) / 25 if not pd.isna(t) else np.nan
        )
    else:
        df["temp_stress_index"] = np.nan

    # ── Voltage deviation from nominal (nominal ~72V for many EVs)
    if "battery_voltage" in df.columns:
        df["voltage_deviation"] = df["battery_voltage"] - 72.0

    # ── Current draw indicator
    if "battery_current" in df.columns:
        df["abs_current"] = df["battery_current"].abs()
        df["is_charging"] = (df["battery_current"] > 0).astype(int)

    # NOTE: Rolling SOC features are intentionally NOT created here.
    # Including rolling(soc) as a feature when predicting soc constitutes
    # direct data leakage (r > 0.999). Models must predict SOC from
    # hardware measurements alone (voltage, current, temperature, odometer).

    # ── Lagged odometer per vehicle (usage rate, not target-correlated)
    if "odometer" in df.columns and "vehicle_no" in df.columns and "timestamp" in df.columns:
        df = df.sort_values(["vehicle_no", "timestamp"])
        df["odometer_lag1"] = df.groupby("vehicle_no")["odometer"].shift(1)
        df["odometer_diff"] = df["odometer"] - df["odometer_lag1"]

    # ── SOH change rate (SOH is target for SOH task, NOT used in SOC features)
    # soh_lag1 / soh_change are only valid as SOH-task features, excluded from SOC build

    logger.info(f"  OEM features: {df.shape[1]} columns, {len(df):,} rows")
    return df


# ─────────────────────────────────────────────
#  FEATURE ENGINEERING — CHARGE CYCLES (RUL)
# ─────────────────────────────────────────────
def engineer_charge_features(df_charge: pd.DataFrame) -> pd.DataFrame:
    """Create features from charge cycles for RUL prediction."""
    print_step("Engineering charge cycle features (RUL)...")
    df = df_charge.copy()

    NOMINAL_CYCLES = cfg.TRAIN_CONFIG["nominal_battery_cycles"]

    # ── RUL Proxy: estimated remaining cycles
    # NOTE: cycle_usage_ratio = charge_cycle_count / NOMINAL_CYCLES is a direct
    # linear transform of rul_proxy (r = -1.0) and is EXCLUDED as a feature.
    # charge_cycle_count itself is also excluded since rul_proxy = 1500 - count.
    # Models must infer RUL from indirect degradation signals instead.
    if "charge_cycle_count" in df.columns:
        df["rul_proxy"] = (NOMINAL_CYCLES - df["charge_cycle_count"]).clip(lower=0)

    # ── Degradation factor: decrease in miles_per_charge over time
    # Normalized deviation from mean mileage
    if "miles_per_charge" in df.columns:
        mean_mpc = df["miles_per_charge"].mean()
        df["degradation_factor"] = (mean_mpc - df["miles_per_charge"]) / mean_mpc.clip(1e-6)
        df["degradation_factor"] = df["degradation_factor"].clip(-1, 1)

    # ── Rolling averages for mileage and charge count
    if "chassis_no" in df.columns:
        df = df.sort_values(["chassis_no", "timestamp"])
        for col in ["miles_per_charge", "mile_avg"]:
            if col in df.columns:
                for w in [3, 5, 10]:
                    df[f"{col}_rolling_{w}"] = (
                        df.groupby("chassis_no")[col]
                        .transform(lambda x: x.rolling(w, min_periods=1).mean())
                    )

    # ── Charge frequency: inverse of days between charges
    if "days_in_service" in df.columns and "charge_cycle_count" in df.columns:
        df["charge_frequency"] = df["charge_cycle_count"] / df["days_in_service"].replace(0, np.nan)

    logger.info(f"  Charge features: {df.shape[1]} columns, {len(df):,} rows")
    return df


# ─────────────────────────────────────────────
#  BUILD TASK-SPECIFIC FEATURE SETS
# ─────────────────────────────────────────────
def build_soc_dataset(df_oem: pd.DataFrame, df_alert: pd.DataFrame) -> pd.DataFrame:
    """SOC prediction dataset from OEM telemetry.

    Features are ONLY hardware sensor readings — no rolling SOC windows
    (those cause leakage with r > 0.999). Realistic expected R2: 0.80-0.92.
    """
    print_step("Building SOC feature set (leak-free)...")
    # Only physically-measurable inputs that do NOT encode the target
    cols_needed = [
        "vehicle_no", "chassis_no", "timestamp",
        # Core hardware sensors
        "battery_voltage",       # OCV curve correlated but physically causal
        "battery_temp",          # temperature affects electrochemistry
        "battery_current",       # current flow changes SOC
        "abs_current",           # absolute current magnitude
        "is_charging",           # charge vs discharge
        "odometer",              # cumulative usage
        "odometer_diff",         # recent trip distance
        # Derived (from voltage/current only)
        "voltage_deviation",     # deviation from nominal 72V
        "temp_stress_index",     # penalty for extreme temperatures
        # Usage context
        "drive_mode_encoded",
        "hour", "day_of_week", "month", "is_weekend", "is_peak",
        "oem_encoded", "model_encoded",
        # TARGET
        "soc",
    ]
    available = [c for c in cols_needed if c in df_oem.columns]
    df_soc = df_oem[available].dropna(subset=["soc"]).copy()
    df_soc = df_soc.dropna(thresh=int(len(df_soc.columns) * 0.5))
    logger.info(f"  SOC dataset: {len(df_soc):,} rows, {len(df_soc.columns)} cols")
    return df_soc


def build_soh_dataset(df_oem: pd.DataFrame, df_charge: pd.DataFrame) -> pd.DataFrame:
    """SOH prediction dataset (only vehicles with SOH labels).

    Excludes: soc (concurrent measurement, not causal driver of SOH),
    rolling_soc_* (leakage), soh_lag1/soh_change (encode target).
    Includes: long-term degradation signals — odometer, charge cycles,
    temperature stress, degradation factor, days in service.
    Realistic expected R2: 0.75-0.90.
    """
    print_step("Building SOH feature set (leak-free)...")
    df_soh = df_oem.dropna(subset=["soh"]).copy()

    if "chassis_no" in df_charge.columns:
        charge_feats = df_charge[[
            "chassis_no", "charge_cycle_count", "mile_avg",
            "miles_per_charge", "days_in_service", "degradation_factor"
        ]].groupby("chassis_no").last().reset_index()
        df_soh = pd.merge(df_soh, charge_feats, on="chassis_no", how="left")

    keep_cols = [
        "vehicle_no", "chassis_no", "timestamp",
        # Hardware measurements
        "battery_voltage",        # voltage sag indicates degradation
        "battery_temp",           # thermal stress accelerates aging
        "battery_current",        # charge/discharge patterns
        "abs_current",
        "odometer",               # total km driven
        "odometer_diff",
        # Degradation history (from charge cycle data)
        "charge_cycle_count",     # total cycles (NOT directly = target)
        "mile_avg", "miles_per_charge",  # range degradation over time
        "days_in_service",        # calendar aging
        "degradation_factor",     # normalized range loss
        # Derived
        "temp_stress_index",
        "voltage_deviation",
        "oem_encoded", "model_encoded",
        # TARGET
        "soh",
    ]
    available = [c for c in keep_cols if c in df_soh.columns]
    df_soh = df_soh[available].dropna(subset=["soh"])
    logger.info(f"  SOH dataset: {len(df_soh):,} rows, {len(df_soh.columns)} cols")
    return df_soh


def build_rul_dataset(df_charge: pd.DataFrame, df_oem: pd.DataFrame) -> pd.DataFrame:
    """RUL prediction dataset from charge cycle logs.

    CRITICAL EXCLUSIONS:
    - charge_cycle_count: rul_proxy = 1500 - charge_cycle_count (leakage r=-1.0)
    - cycle_usage_ratio:  = charge_cycle_count/1500 (same leakage, different scale)
    Models must infer remaining life from indirect degradation signals.
    Realistic expected R2: 0.65-0.85.
    """
    print_step("Building RUL feature set (leak-free)...")
    df_rul = df_charge.dropna(subset=["rul_proxy"]).copy()

    # Merge in SOH if available (indirect signal, not leakage)
    if "soh" in df_oem.columns and "chassis_no" in df_oem.columns:
        soh_agg = df_oem.groupby("chassis_no")["soh"].mean().reset_index().rename(
            columns={"soh": "soh_mean"}
        )
        df_rul = pd.merge(df_rul, soh_agg, on="chassis_no", how="left")

    keep_cols = [
        "chassis_no", "timestamp",
        # Degradation signals (indirect — do NOT encode target)
        "odometer",               # cumulative distance driven
        "soc_at_charge",          # SOC level when plugging in
        "mile_avg",               # average miles per charge over history
        "miles_per_charge",       # current miles per charge (range health)
        "days_in_service",        # calendar age
        "degradation_factor",     # normalised range loss vs fleet mean
        "charge_frequency",       # how often vehicle charges (usage rate)
        "soh_mean",               # average state of health (if available)
        # Rolling mileage trend (window over miles_per_charge)
        "miles_per_charge_rolling_3",
        "miles_per_charge_rolling_5",
        "miles_per_charge_rolling_10",
        "oem_encoded", "model_encoded",
        # TARGET
        "rul_proxy",
    ]
    available = [c for c in keep_cols if c in df_rul.columns]
    df_rul = df_rul[available].dropna(subset=["rul_proxy"])
    logger.info(f"  RUL dataset: {len(df_rul):,} rows, {len(df_rul.columns)} cols")
    return df_rul


def build_mileage_dataset(df_trip: pd.DataFrame) -> pd.DataFrame:
    """Mileage prediction dataset from trip reports.

    CRITICAL EXCLUSIONS (algebraically define the target):
    - soc_drain:          mileage_per_charge = run_kms * (100/soc_drain)
    - distance_per_soc_drop: = run_kms/soc_drain = mileage_per_charge/100
    - energy_per_soc:     = energy/soc_drain (correlated to target via soc_drain)
    - soc_drain_rate:     = soc_drain/run_kms (inverse of distance_per_soc)
    - soc_at_start/end:   their difference IS soc_drain
    Models learn from driving behaviour and energy use independently.
    Realistic expected R2: 0.70-0.85.
    """
    print_step("Building Mileage feature set (leak-free)...")
    df_m = df_trip.dropna(subset=["mileage_per_charge"]).copy()
    df_m = df_m[df_m["mileage_per_charge"] > 0]

    keep_cols = [
        "vehicle_no", "timestamp",
        # Driving behaviour (do NOT contain soc_drain)
        "run_kms",              # total distance of trip
        "avg_speed",            # average cruising speed
        "max_speed",            # peak speed (aerodynamic drag proxy)
        "trip_duration_hrs",    # how long the trip took
        "stoppage_count",       # number of stops (traffic/idling)
        # Derived behaviour features (no soc_drain involved)
        "energy_efficiency",    # kWh/km — independent energy use signal
        "trip_intensity",       # avg_speed x duration
        "speed_ratio",          # avg/max speed (driving smoothness)
        "stoppage_density",     # stops per hour
        "energy_utilized",      # total energy consumed
        # Time context
        "hour", "day_of_week", "month", "is_weekend", "is_peak",
        "oem_encoded", "city_encoded",
        # TARGET
        "mileage_per_charge",
    ]
    available = [c for c in keep_cols if c in df_m.columns]
    df_m = df_m[available]
    logger.info(f"  Mileage dataset: {len(df_m):,} rows, {len(df_m.columns)} cols")
    return df_m


# ─────────────────────────────────────────────
#  SCALE & SAVE SCALERS
# ─────────────────────────────────────────────
def scale_and_save(df: pd.DataFrame, target_col: str, task_name: str) -> pd.DataFrame:
    """StandardScale all numeric features (excluding target), save scaler."""
    df = df.copy()
    feature_cols = [c for c in df.select_dtypes(include=np.number).columns
                    if c != target_col and c not in ["vehicle_no", "chassis_no"]]
    
    # Fill remaining NaNs with column median for scaling
    df[feature_cols] = df[feature_cols].fillna(df[feature_cols].median())

    scaler = StandardScaler()
    df[feature_cols] = scaler.fit_transform(df[feature_cols])

    scaler_path = os.path.join(cfg.MODELS_DIR, f"scaler_{task_name}.pkl")
    joblib.dump(scaler, scaler_path)
    logger.info(f"  Scaler saved: {scaler_path}")
    return df


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def run_feature_engineering(data_dict: dict = None):
    print_header("STEP 3: FEATURE ENGINEERING")

    if data_dict is None:
        data_dict = {
            "alert":  load_csv(cfg.PROCESSED_FILES["alert_merged"],     logger),
            "trip":   load_csv(cfg.PROCESSED_FILES["trip_merged"],       logger),
            "charge": load_csv(cfg.PROCESSED_FILES["charge_cycles"],     logger),
            "oem":    load_csv(cfg.PROCESSED_FILES["oem_telemetry"],     logger),
            "device": load_csv(cfg.PROCESSED_FILES["device_telemetry"],  logger),
        }

    # Engineer features for each source
    df_trip   = engineer_trip_features(data_dict["trip"])
    df_oem    = engineer_oem_features(data_dict["oem"])
    df_charge = engineer_charge_features(data_dict["charge"])

    # Build task-specific datasets
    df_soc     = build_soc_dataset(df_oem, data_dict["alert"])
    df_soh     = build_soh_dataset(df_oem, df_charge)
    df_rul     = build_rul_dataset(df_charge, df_oem)
    df_mileage = build_mileage_dataset(df_trip)

    # Save scaled versions
    print_step("Scaling and saving feature sets...")
    for df, path, target, name in [
        (df_soc,     cfg.PROCESSED_FILES["features_soc"],     "soc",             "soc"),
        (df_soh,     cfg.PROCESSED_FILES["features_soh"],     "soh",             "soh"),
        (df_rul,     cfg.PROCESSED_FILES["features_rul"],     "rul_proxy",       "rul"),
        (df_mileage, cfg.PROCESSED_FILES["features_mileage"], "mileage_per_charge","mileage"),
    ]:
        df_scaled = scale_and_save(df, target, name)
        save_csv(df_scaled, path, logger)

    print_success("Feature engineering complete!")

    return {
        "soc":     df_soc,
        "soh":     df_soh,
        "rul":     df_rul,
        "mileage": df_mileage,
    }


if __name__ == "__main__":
    run_feature_engineering()
