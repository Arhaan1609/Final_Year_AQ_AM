"""
07_prediction_system.py — Interactive terminal-based prediction system.

Loads best trained models and accepts user inputs to predict:
  - SOC  (State of Charge)
  - SOH  (State of Health)
  - RUL  (Remaining Useful Life)
  - Mileage (Per-Charge Driving Range)
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import joblib

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from utils import get_logger

logger = get_logger("07_prediction_system", cfg.LOGS_DIR)

# ── Color codes for terminal
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    C = {
        "cyan": Fore.CYAN, "green": Fore.GREEN, "yellow": Fore.YELLOW,
        "red": Fore.RED, "white": Fore.WHITE, "magenta": Fore.MAGENTA,
        "reset": Style.RESET_ALL, "bold": Style.BRIGHT,
    }
except ImportError:
    C = {k: "" for k in ["cyan", "green", "yellow", "red", "white", "magenta", "reset", "bold"]}


# ─────────────────────────────────────────────
#  BEST MODEL REGISTRY
# ─────────────────────────────────────────────
BEST_MODEL_PREFERENCE = [
    "RandomForest", "XGBoost", "GradientBoosting", "ExtraTrees",
    "Ridge", "KNN", "DecisionTree", "Lasso", "SVR"
]


def find_best_model(task: str):
    """Find the best pkl model for a given task."""
    # Check if a best_model.txt exists
    txt = os.path.join(cfg.MODELS_DIR, f"{task}_best_model.txt")
    if os.path.exists(txt):
        with open(txt) as f:
            line = f.readline().strip()
            best_name = line.replace("Best Model: ", "").strip()
        pkl = os.path.join(cfg.MODELS_DIR, f"{task}_{best_name}.pkl")
        if os.path.exists(pkl):
            return best_name, joblib.load(pkl)

    # Fallback: try preference list
    for name in BEST_MODEL_PREFERENCE:
        pkl = os.path.join(cfg.MODELS_DIR, f"{task}_{name}.pkl")
        if os.path.exists(pkl):
            return name, joblib.load(pkl)

    return None, None


def find_scaler(task_key: str):
    """Load scaler for a given task."""
    path = os.path.join(cfg.MODELS_DIR, f"scaler_{task_key}.pkl")
    if os.path.exists(path):
        return joblib.load(path)
    return None


# ─────────────────────────────────────────────
#  INPUT COLLECTION
# ─────────────────────────────────────────────
def ask_float(prompt: str, default: float = None, low: float = None, high: float = None) -> float:
    """Prompt user for a float value with optional default and range."""
    while True:
        hint = f" [default: {default}]" if default is not None else ""
        hint += f" ({low} – {high})" if low is not None else ""
        raw = input(f"  {C['cyan']}{prompt}{hint}: {C['reset']}").strip()
        if raw == "" and default is not None:
            return default
        try:
            val = float(raw)
            if low is not None and val < low:
                print(f"  {C['yellow']}⚠  Value below minimum ({low}), using {low}{C['reset']}")
                return low
            if high is not None and val > high:
                print(f"  {C['yellow']}⚠  Value above maximum ({high}), using {high}{C['reset']}")
                return high
            return val
        except ValueError:
            print(f"  {C['red']}Invalid number. Try again.{C['reset']}")


def collect_soc_inputs() -> dict:
    print(f"\n  {C['cyan']}Enter vehicle telemetry data for SOC prediction:{C['reset']}")
    return {
        "battery_voltage":   ask_float("Battery Voltage (V)", default=72.0, low=20, high=150),
        "battery_temp":      ask_float("Battery Temperature (°C)", default=30.0, low=-20, high=70),
        "battery_current":   ask_float("Battery Current (A, negative=discharge)", default=-10.0),
        "odometer":          ask_float("Odometer (km)", default=15000, low=0),
        "charge_state_pct":  ask_float("Charge State %", default=50, low=0, high=100),
        "drive_mode_encoded":ask_float("Drive Mode (0=Eco, 1=Normal, 2=Sport)", default=1, low=0, high=2),
        "hour":              ask_float("Hour of day (0-23)", default=10, low=0, high=23),
        "day_of_week":       ask_float("Day of week (0=Mon, 6=Sun)", default=2, low=0, high=6),
        "month":             ask_float("Month (1-12)", default=2, low=1, high=12),
        "is_weekend":        ask_float("Weekend? (0=No, 1=Yes)", default=0, low=0, high=1),
        "temp_stress_index": ask_float("Temp Stress Index (0–1)", default=0.2, low=0, high=1),
        "voltage_deviation":  ask_float("Voltage Deviation from 72V", default=0.0),
        "abs_current":       ask_float("Absolute Current (A)", default=10.0, low=0),
        "is_charging":       ask_float("Is Charging? (0=No, 1=Yes)", default=0, low=0, high=1),
        "rolling_soc_5":     ask_float("Rolling SOC 5-step avg (if known, else current approx)", default=60, low=0, high=100),
        "rolling_soc_10":    ask_float("Rolling SOC 10-step avg", default=60, low=0, high=100),
    }


def collect_soh_inputs() -> dict:
    print(f"\n  {C['cyan']}Enter battery health data for SOH prediction:{C['reset']}")
    return {
        "battery_voltage":    ask_float("Battery Voltage (V)", default=72.0, low=20, high=150),
        "battery_temp":       ask_float("Battery Temperature (°C)", default=30.0, low=-20, high=70),
        "battery_current":    ask_float("Battery Current (A)", default=-5.0),
        "odometer":           ask_float("Total Odometer (km)", default=25000, low=0),
        "soc":                ask_float("Current SOC %", default=70, low=0, high=100),
        "charge_cycle_count": ask_float("Total Charge Cycles", default=300, low=0),
        "mile_avg":           ask_float("Avg Miles per Day", default=80, low=0),
        "miles_per_charge":   ask_float("Miles per Charge", default=120, low=0),
        "days_in_service":    ask_float("Days in Service", default=400, low=1),
        "degradation_factor": ask_float("Degradation Factor (0–1, 0=new)", default=0.1, low=0, high=1),
        "temp_stress_index":  ask_float("Temp Stress Index (0–1)", default=0.2, low=0, high=1),
        "voltage_deviation":  ask_float("Voltage Deviation from 72V", default=0.0),
        "rolling_soc_5":      ask_float("Rolling SOC 5-step avg", default=65, low=0, high=100),
        "rolling_soc_10":     ask_float("Rolling SOC 10-step avg", default=65, low=0, high=100),
    }


def collect_rul_inputs() -> dict:
    print(f"\n  {C['cyan']}Enter battery lifecycle data for RUL prediction:{C['reset']}")
    return {
        "charge_cycle_count": ask_float("Total Charge Cycles so far", default=300, low=0),
        "odometer":           ask_float("Total Odometer (km)", default=25000, low=0),
        "soc_at_charge":      ask_float("SOC at Last Charge %", default=80, low=0, high=100),
        "mile_avg":           ask_float("Avg Miles per Day", default=80, low=0),
        "miles_per_charge":   ask_float("Miles per Charge", default=120, low=0),
        "days_in_service":    ask_float("Days in Service", default=400, low=1),
        "degradation_factor": ask_float("Degradation Factor (0–1)", default=0.1, low=0, high=1),
        "cycle_usage_ratio":  ask_float("Cycle Usage Ratio (Cycles / 1500)", default=0.2, low=0, high=1),
        "charge_frequency":   ask_float("Charge Frequency (charges/day)", default=0.75, low=0),
        "soh_mean":           ask_float("Avg SOH % (if known)", default=90, low=0, high=120),
    }


def collect_mileage_inputs() -> dict:
    print(f"\n  {C['cyan']}Enter trip data for Mileage prediction:{C['reset']}")
    return {
        "soc_at_start":         ask_float("SOC at Trip Start %", default=85, low=0, high=100),
        "soc_at_end":           ask_float("SOC at Trip End %", default=45, low=0, high=100),
        "soc_drain":            ask_float("SOC Drained %", default=40, low=0, high=100),
        "run_kms":              ask_float("Trip Distance (km)", default=60, low=0),
        "energy_utilized":      ask_float("Energy Used (kWh)", default=12.0, low=0),
        "avg_speed":            ask_float("Avg Speed (kmph)", default=35, low=0, high=200),
        "max_speed":            ask_float("Max Speed (kmph)", default=65, low=0, high=200),
        "trip_duration_hrs":    ask_float("Trip Duration (hours)", default=2.0, low=0),
        "stoppage_count":       ask_float("Stoppage Count", default=5, low=0),
        "soc_drain_rate":       ask_float("SOC Drain Rate (%/km)", default=0.7, low=0),
        "energy_efficiency":    ask_float("Energy Efficiency (kWh/km)", default=0.2, low=0),
        "distance_per_soc_drop":ask_float("Distance per SOC % drop (km/%)", default=1.5, low=0),
        "trip_intensity":       ask_float("Trip Intensity (speed × time)", default=70.0, low=0),
        "hour":                 ask_float("Hour of trip start (0-23)", default=9, low=0, high=23),
        "day_of_week":          ask_float("Day of week (0=Mon)", default=1, low=0, high=6),
        "is_weekend":           ask_float("Weekend? (0/1)", default=0, low=0, high=1),
    }


INPUT_COLLECTORS = {
    "SOC":     collect_soc_inputs,
    "SOH":     collect_soh_inputs,
    "RUL":     collect_rul_inputs,
    "Mileage": collect_mileage_inputs,
}


# ─────────────────────────────────────────────
#  PREDICTION ENGINE
# ─────────────────────────────────────────────
def make_prediction(task: str, model, scaler, input_dict: dict) -> tuple:
    """
    Prepare input, apply scaler, and predict.
    Returns (prediction_value, confidence_range)
    """
    X = pd.DataFrame([input_dict])
    X = X.select_dtypes(include=np.number)
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
    X_arr = X.values.astype(np.float32)

    # Apply scaler if available
    if scaler is not None:
        try:
            n_expected = scaler.n_features_in_
            if X_arr.shape[1] < n_expected:
                # Pad with zeros
                pad = np.zeros((1, n_expected - X_arr.shape[1]))
                X_arr = np.hstack([X_arr, pad])
            elif X_arr.shape[1] > n_expected:
                X_arr = X_arr[:, :n_expected]
            X_arr = scaler.transform(X_arr)
        except Exception:
            pass  # use raw if scaler fails

    try:
        pred = model.predict(X_arr).ravel()[0]
    except Exception as e:
        logger.warning(f"Prediction failed: {e}")
        pred = 0.0

    # Simple confidence range (±10% of prediction as heuristic)
    margin = abs(pred) * 0.10
    return pred, margin


def interpret_result(task: str, value: float) -> str:
    """Return a human-readable interpretation."""
    if task == "SOC":
        if value >= 80: return f"{C['green']} High charge — Good to go!{C['reset']}"
        if value >= 40: return f"{C['yellow']} Moderate charge — Plan a charge soon{C['reset']}"
        return f"{C['red']} Low charge — Charge immediately!{C['reset']}"

    elif task == "SOH":
        if value >= 90: return f"{C['green']}  Excellent battery health{C['reset']}"
        if value >= 75: return f"{C['yellow']} Good health — Monitor regularly{C['reset']}"
        if value >= 60: return f"{C['yellow']}  Degraded — Consider service{C['reset']}"
        return f"{C['red']} Poor health — Battery replacement recommended{C['reset']}"

    elif task == "RUL":
        cycles = max(0, value)
        days   = round(cycles / 0.75) if cycles > 0 else 0  # ~0.75 charges/day
        years  = round(days / 365, 1)
        return (f"{C['cyan']} Estimated {cycles:.0f} charge cycles remaining "
                f"(~{days} days / {years} yrs){C['reset']}")

    elif task == "Mileage":
        if value >= 150: return f"{C['green']} Excellent range — Long trips possible{C['reset']}"
        if value >= 80:  return f"{C['yellow']} Moderate range — City driving comfortable{C['reset']}"
        return f"{C['red']} Limited range — Short trips only{C['reset']}"

    return ""


# ─────────────────────────────────────────────
#  BANNER
# ─────────────────────────────────────────────
BANNER = f"""
{C['cyan']}╔══════════════════════════════════════════════════════════════════════╗
║      EV BATTERY INTELLIGENCE SYSTEM — PREDICTION ENGINE              ║
║     Final Year Project | ML & DL-Based EV Analysis                   ║
╚══════════════════════════════════════════════════════════════════════╝{C['reset']}
"""

TASK_MENU = f"""
  {C['cyan']}Select Prediction Task:{C['reset']}

    {C['green']}[1]{C['reset']} State of Charge (SOC)          — Current battery level %
    {C['green']}[2]{C['reset']} State of Health (SOH)          — Battery health %
    {C['green']}[3]{C['reset']} Remaining Useful Life (RUL)    — Remaining charge cycles
    {C['green']}[4]{C['reset']} Mileage Prediction             — Km per full charge
    {C['yellow']}[5]{C['reset']} Run All 4 Predictions
    {C['red']}[0]{C['reset']} Exit
"""

TASK_MAP = {"1": "SOC", "2": "SOH", "3": "RUL", "4": "Mileage"}
TASK_KEYS = {"SOC": "soc", "SOH": "soh", "RUL": "rul", "Mileage": "mileage"}
TASK_UNITS = {"SOC": "%", "SOH": "%", "RUL": "cycles", "Mileage": "km"}


# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────
def run_prediction_system():
    print(BANNER)

    # Pre-load models
    print(f"  {C['cyan']}Loading trained models...{C['reset']}")
    models  = {}
    scalers = {}
    for task in ["SOC", "SOH", "RUL", "Mileage"]:
        name, model = find_best_model(task)
        if model:
            models[task]  = {"name": name, "model": model}
            scalers[task] = find_scaler(TASK_KEYS[task])
            print(f"  {C['green']}✔  {task}: {name}{C['reset']}")
        else:
            print(f"  {C['red']}✘  {task}: No model found — run main_pipeline.py first{C['reset']}")

    if not models:
        print(f"\n  {C['red']}No trained models available. Run main_pipeline.py first.{C['reset']}\n")
        return

    while True:
        print(TASK_MENU)
        choice = input(f"  {C['cyan']}Your choice: {C['reset']}").strip()

        if choice == "0":
            print(f"\n  {C['green']}Thank you for using the EV Battery Intelligence System!{C['reset']}\n")
            break

        tasks_to_run = []
        if choice == "5":
            tasks_to_run = list(TASK_MAP.values())
        elif choice in TASK_MAP:
            tasks_to_run = [TASK_MAP[choice]]
        else:
            print(f"  {C['red']}Invalid choice. Enter 0-5.{C['reset']}")
            continue

        for task in tasks_to_run:
            if task not in models:
                print(f"\n  {C['yellow']}⚠  No model loaded for {task}. Skipping.{C['reset']}")
                continue

            print(f"\n  {'═'*65}")
            print(f"  {C['bold']}{C['cyan']}PREDICTION: {task}{C['reset']}")
            print(f"  {'═'*65}")

            collector = INPUT_COLLECTORS[task]
            input_data = collector()

            pred, margin = make_prediction(
                task, models[task]["model"], scalers.get(task), input_data
            )

            unit = TASK_UNITS[task]
            interpretation = interpret_result(task, pred)

            print(f"\n  {'─'*65}")
            print(f"  {C['bold']} Prediction Result:{C['reset']}")
            print(f"  {'─'*65}")
            print(f"  {C['bold']}  {task}:{C['reset']}"
                  f"  {C['green']}{pred:.2f} {unit}{C['reset']}"
                  f"  {C['yellow']}(±{margin:.2f} {unit}){C['reset']}")
            print(f"  {interpretation}")
            print(f"  Model used: {C['magenta']}{models[task]['name']}{C['reset']}")
            print(f"  {'─'*65}")

        again = input(f"\n  {C['cyan']}Make another prediction? (y/n): {C['reset']}").strip().lower()
        if again not in ("y", "yes"):
            print(f"\n  {C['green']}Thank you for using the EV Battery Intelligence System!{C['reset']}\n")
            break


if __name__ == "__main__":
    run_prediction_system()
