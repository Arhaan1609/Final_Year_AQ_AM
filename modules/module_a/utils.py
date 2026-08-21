"""
utils.py — Shared utilities for EV Battery Analysis System
"""

import os
import re
import sys
import json
import logging
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm
from colorama import Fore, Style, init

warnings.filterwarnings("ignore")
init(autoreset=True)

# ─────────────────────────────────────────────
#  LOGGER
# ─────────────────────────────────────────────
def get_logger(name: str, log_dir: str = "logs") -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    # File handler
    fh = logging.FileHandler(os.path.join(log_dir, f"{name}.log"), encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger


def print_header(title: str):
    width = 70
    print(f"\n{Fore.CYAN}{'═' * width}")
    print(f"{Fore.CYAN}  {title}")
    print(f"{Fore.CYAN}{'═' * width}{Style.RESET_ALL}\n")


def print_step(msg: str):
    print(f"{Fore.GREEN}  ▶  {msg}{Style.RESET_ALL}")


def print_success(msg: str):
    print(f"{Fore.GREEN}  ✔  {msg}{Style.RESET_ALL}")


def print_warning(msg: str):
    print(f"{Fore.YELLOW}  ⚠  {msg}{Style.RESET_ALL}")


def print_error(msg: str):
    print(f"{Fore.RED}  ✘  {msg}{Style.RESET_ALL}")


# ─────────────────────────────────────────────
#  JSON LOADER (memory-safe for large files)
# ─────────────────────────────────────────────
def load_json_file(path: str, logger=None) -> list:
    """Load JSON array file. Handles MongoDB-style $date/$oid fields."""
    log = logger or get_logger("utils")
    file_size_mb = os.path.getsize(path) / (1024 ** 2)
    log.info(f"Loading JSON: {os.path.basename(path)} ({file_size_mb:.1f} MB)")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    log.info(f"  Loaded {len(data):,} records")
    return data


def flatten_mongo_record(record: dict) -> dict:
    """Convert MongoDB-style nested fields to flat Python types."""
    flat = {}
    for k, v in record.items():
        if isinstance(v, dict):
            if "$oid" in v:
                flat[k] = v["$oid"]
            elif "$date" in v:
                flat[k] = pd.to_datetime(v["$date"], utc=True)
            else:
                flat[k] = str(v)
        else:
            flat[k] = v
    return flat


def json_to_dataframe(data: list, logger=None) -> pd.DataFrame:
    """Convert list of MongoDB-style dicts to normalized DataFrame."""
    log = logger or get_logger("utils")
    flat_records = [flatten_mongo_record(r) for r in tqdm(data, desc="  Flattening records")]
    df = pd.DataFrame(flat_records)
    log.info(f"  DataFrame: {df.shape[0]:,} rows × {df.shape[1]} cols")
    return df


# ─────────────────────────────────────────────
#  TIMESTAMP PARSING
# ─────────────────────────────────────────────
TIMESTAMP_PATTERNS = [
    "%d-%b-%Y, %H:%M:%S",
    "%d-%b-%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%Y-%m-%dT%H:%M:%S",
]


def parse_timestamp(ts_series: pd.Series, logger=None) -> pd.Series:
    """Try multiple timestamp formats and return a normalized datetime series."""
    log = logger or get_logger("utils")

    if pd.api.types.is_datetime64_any_dtype(ts_series):
        return pd.to_datetime(ts_series, utc=True).dt.tz_localize(None)

    for fmt in TIMESTAMP_PATTERNS:
        try:
            parsed = pd.to_datetime(ts_series, format=fmt, errors="coerce")
            null_pct = parsed.isna().mean()
            if null_pct < 0.3:
                log.info(f"  Parsed timestamps with format: {fmt} (null: {null_pct:.1%})")
                return parsed
        except Exception:
            continue

    # fallback: let pandas infer (pandas 2.0+ compatible)
    parsed = pd.to_datetime(ts_series, errors="coerce", utc=True)
    parsed = parsed.dt.tz_localize(None)
    log.warning(f"  Timestamp parsed via inference (null: {parsed.isna().mean():.1%})")
    return parsed


def extract_temporal_features(df: pd.DataFrame, ts_col: str = "timestamp") -> pd.DataFrame:
    """Create time-based features from a timestamp column."""
    df = df.copy()
    ts = pd.to_datetime(df[ts_col], errors="coerce")
    df["hour"]        = ts.dt.hour
    df["day_of_week"] = ts.dt.dayofweek    # 0=Mon
    df["month"]       = ts.dt.month
    df["is_weekend"]  = (df["day_of_week"] >= 5).astype(int)
    df["is_peak"]     = df["hour"].apply(lambda h: 1 if (8 <= h <= 10 or 17 <= h <= 20) else 0)
    return df


# ─────────────────────────────────────────────
#  SCHEMA DETECTION
# ─────────────────────────────────────────────
def detect_schema(df: pd.DataFrame) -> dict:
    """Auto-detect column types and nullity."""
    schema = {}
    for col in df.columns:
        schema[col] = {
            "dtype": str(df[col].dtype),
            "null_pct": round(df[col].isna().mean() * 100, 2),
            "n_unique": df[col].nunique(),
            "sample": df[col].dropna().iloc[:3].tolist() if len(df[col].dropna()) > 0 else [],
        }
    return schema


def print_schema(schema: dict, title="Schema"):
    print(f"\n  {Fore.CYAN}[{title}]{Style.RESET_ALL}")
    print(f"  {'Column':<35} {'Type':<15} {'Null%':>6} {'Unique':>8}")
    print(f"  {'-'*65}")
    for col, info in schema.items():
        print(f"  {col:<35} {info['dtype']:<15} {info['null_pct']:>5.1f}% {info['n_unique']:>8,}")


# ─────────────────────────────────────────────
#  DATA CLEANING HELPERS
# ─────────────────────────────────────────────
MISSING_SENTINELS = ["-", "N/A", "n/a", "NA", "nan", "null", "None", "", " "]


def replace_sentinels(df: pd.DataFrame) -> pd.DataFrame:
    """Replace common missing-value strings with NaN."""
    return df.replace(MISSING_SENTINELS, np.nan)


def remove_duplicates(df: pd.DataFrame, subset=None, logger=None) -> pd.DataFrame:
    log = logger or get_logger("utils")
    before = len(df)
    df = df.drop_duplicates(subset=subset)
    after = len(df)
    log.info(f"  Removed {before - after:,} duplicate rows (kept {after:,})")
    return df


def clip_outliers_iqr(df: pd.DataFrame, cols: list, factor: float = 1.5, logger=None) -> pd.DataFrame:
    """Cap outliers at [Q1 - factor*IQR, Q3 + factor*IQR]."""
    log = logger or get_logger("utils")
    df = df.copy()
    for col in cols:
        if col not in df.columns:
            continue
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - factor * iqr, q3 + factor * iqr
        n_out = ((df[col] < lo) | (df[col] > hi)).sum()
        df[col] = df[col].clip(lower=lo, upper=hi)
        if n_out > 0:
            log.debug(f"    Clipped {n_out} outliers in '{col}' [{lo:.2f}, {hi:.2f}]")
    return df


def safe_numeric(series: pd.Series) -> pd.Series:
    """Coerce to numeric, turning errors to NaN."""
    return pd.to_numeric(series, errors="coerce")


# ─────────────────────────────────────────────
#  GPS PARSING
# ─────────────────────────────────────────────
def parse_gps(gps_str) -> tuple:
    """Extract (lat, lon) from 'lat,lon' string."""
    if pd.isna(gps_str) or gps_str in MISSING_SENTINELS:
        return np.nan, np.nan
    try:
        parts = str(gps_str).strip().split(",")
        if len(parts) == 2:
            return float(parts[0]), float(parts[1])
    except Exception:
        pass
    return np.nan, np.nan


# ─────────────────────────────────────────────
#  SAVE/LOAD HELPERS
# ─────────────────────────────────────────────
def save_csv(df: pd.DataFrame, path: str, logger=None):
    log = logger or get_logger("utils")
    df.to_csv(path, index=False)
    size_mb = os.path.getsize(path) / (1024 ** 2)
    log.info(f"  Saved {os.path.basename(path)} ({df.shape[0]:,} rows, {size_mb:.1f} MB)")


def load_csv(path: str, logger=None) -> pd.DataFrame:
    log = logger or get_logger("utils")
    df = pd.read_csv(path, low_memory=False)
    log.info(f"  Loaded {os.path.basename(path)}: {df.shape[0]:,} rows × {df.shape[1]} cols")
    return df


# ─────────────────────────────────────────────
#  EVALUATION HELPERS
# ─────────────────────────────────────────────
def compute_metrics(y_true, y_pred) -> dict:
    """Return RMSE, MAE, R², MAPE."""
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    mse  = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae  = mean_absolute_error(y_true, y_pred)
    r2   = r2_score(y_true, y_pred)

    # MAPE — avoid division by zero
    mask = y_true != 0
    mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100 if mask.any() else np.nan

    return {"RMSE": round(rmse, 4), "MAE": round(mae, 4), "R2": round(r2, 4), "MAPE": round(mape, 2)}


def format_metrics_table(results: dict) -> str:
    """Format results dict → pretty table string."""
    from tabulate import tabulate
    rows = []
    for model_name, targets in results.items():
        for target, metrics in targets.items():
            rows.append([
                model_name, target,
                metrics.get("RMSE", "-"),
                metrics.get("MAE", "-"),
                metrics.get("R2", "-"),
                metrics.get("MAPE", "-"),
                metrics.get("train_time_s", "-"),
            ])
    headers = ["Model", "Target", "RMSE", "MAE", "R²", "MAPE%", "Time(s)"]
    return tabulate(rows, headers=headers, tablefmt="fancy_grid", floatfmt=".4f")
