"""
07_prediction_system.py — Interactive terminal-based prediction system.

Module A — Loads best trained sklearn/XGBoost models to predict:
  - SOC  (State of Charge)
  - SOH  (State of Health — tabular, Extra Trees)
  - RUL  (Remaining Useful Life)
  - Mileage (Per-Charge Driving Range)

Module B — Loads BatteryIQ Engine (PyTorch + sklearn) to predict:
  - Thermal Safety  (Multi-Zone Random Forest, F1=0.997)
  - SOH Deep        (Hybrid 1D-CNN + LSTM, RMSE=5.29%)
  - Full Diagnosis  (Composite Health Score + BMS directive)
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import joblib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

warnings.filterwarnings("ignore")

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BASE_DIR)
import config as cfg
from utils import get_logger

logger = get_logger("07_prediction_system", cfg.LOGS_DIR)

# ── Module B — BatteryIQ Engine (CNN-LSTM + Multi-Zone RF)
_MODULE_B_DIR = os.path.join(_BASE_DIR, "..", "module_b")
_MODULE_B_DIR = os.path.abspath(_MODULE_B_DIR)
sys.path.insert(0, _MODULE_B_DIR)
_module_b_engine = None

def _load_module_b_engine():
    global _module_b_engine
    try:
        from src.models.engine import BatteryIQEngine
        _module_b_engine = BatteryIQEngine()
        return True
    except Exception as e:
        logger.warning(f"Module B engine not loaded: {e}")
        return False

# ── Module C — BA-BMS & Knee-Point Engine (XGBoost)
_MODULE_C_DIR = os.path.join(_BASE_DIR, "..", "module_c")
_MODULE_C_DIR = os.path.abspath(_MODULE_C_DIR)
sys.path.insert(0, _MODULE_C_DIR)
_module_c_engine = None

def _load_module_c_engine():
    global _module_c_engine
    try:
        from engine import BABMSEngine
        _module_c_engine = BABMSEngine()
        return _module_c_engine.is_loaded
    except Exception as e:
        logger.warning(f"Module C engine not loaded: {e}")
        return False

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
║      EV BATTERY INTELLIGENCE SYSTEM — TRI-PILLAR PREDICTION ENGINE   ║
║   Module A: Fleet Predictions  │  Module B: Thermal & SOH-Deep       ║
║   Module C: Driver Behavior (AI/BSI) & Knee-Point Prognostics        ║
╚══════════════════════════════════════════════════════════════════════╝{C['reset']}
"""

TASK_MENU = f"""
  {C['cyan']}── MODULE A — Fleet Predictions ─────────────────────────────{C['reset']}
    {C['green']}[1]{C['reset']} State of Charge (SOC)          — Current battery level %
    {C['green']}[2]{C['reset']} State of Health (SOH)          — Battery health % (tabular)
    {C['green']}[3]{C['reset']} Remaining Useful Life (RUL)    — Remaining charge cycles
    {C['green']}[4]{C['reset']} Mileage Prediction             — Km per full charge
    {C['yellow']}[5]{C['reset']} Run All Module A Predictions

  {C['magenta']}── MODULE B — Battery Health & Thermal ───────────────────────{C['reset']}
    {C['green']}[6]{C['reset']} Thermal Safety Check           — Multi-zone fault detection
    {C['green']}[7]{C['reset']} SOH Deep Analysis              — CNN-LSTM sequence estimation
    {C['green']}[8]{C['reset']} Full Vehicle Diagnosis         — Composite health + BMS directive
    {C['yellow']}[9]{C['reset']} Run All Module B Predictions

  {C['yellow']}── MODULE C — Driver Behavior & Knee Prognostics ─────────────{C['reset']}
    {C['green']}[10]{C['reset']} Driver Behavior & Stress (AI/BSI)— Aggressiveness & battery stress
    {C['green']}[11]{C['reset']} Knee-Point Prognostics (RUL)   — Cycles before accelerated fade
    {C['yellow']}[12]{C['reset']} Run All 11 Predictions (A + B + C)

    {C['red']}[0]{C['reset']} Exit
"""

TASK_MAP = {
    "1": "SOC", "2": "SOH", "3": "RUL", "4": "Mileage",
    "6": "Thermal", "7": "SOH_Deep", "8": "Diagnosis",
    "10": "Driver_Behavior", "11": "Knee_Prognostics"
}
TASK_KEYS  = {"SOC": "soc", "SOH": "soh", "RUL": "rul", "Mileage": "mileage"}
TASK_UNITS = {"SOC": "%", "SOH": "%", "RUL": "cycles", "Mileage": "km"}

MODULE_A_TASKS = ["SOC", "SOH", "RUL", "Mileage"]
MODULE_B_TASKS = ["Thermal", "SOH_Deep", "Diagnosis"]
MODULE_C_TASKS = ["Driver_Behavior", "Knee_Prognostics"]


# ─────────────────────────────────────────────
#  MODULE C INPUT COLLECTORS
# ─────────────────────────────────────────────
def collect_behavior_inputs() -> dict:
    print(f"\n  {C['yellow']}Enter driving & operational parameters for BA-BMS Analysis:{C['reset']}")
    return {
        "harsh_accel_count": ask_float("Harsh Acceleration count", default=3, low=0),
        "harsh_brake_count": ask_float("Harsh Braking count", default=2, low=0),
        "harsh_corner_count": ask_float("Aggressive Cornering count", default=1, low=0),
        "speed_variance": ask_float("Speed Variance (std dev in km/h)", default=8.5, low=0),
        "avg_speed": ask_float("Average Trip Speed (km/h)", default=38.0, low=0, high=150),
        "max_speed": ask_float("Peak Trip Speed (km/h)", default=68.0, low=0, high=200),
        "battery_temp_max": ask_float("Peak Battery Temp reached (°C)", default=36.0, low=-20, high=120),
        "max_discharge_current": ask_float("Peak Discharge Current (A)", default=35.0, low=0),
    }


def collect_knee_inputs() -> dict:
    print(f"\n  {C['yellow']}Enter telemetry & lifecycle data for Knee-Point Prognostics:{C['reset']}")
    return {
        "charge_cycle_count": ask_float("Cumulative Charge Cycle Count", default=200, low=0),
        "capacity": ask_float("Current Estimated Capacity (Ah)", default=94.0, low=0),
        "voltage": ask_float("Pack Voltage (V)", default=73.8, low=20, high=150),
        "battery_temp": ask_float("Battery Temperature (°C)", default=33.0, low=-20, high=120),
        "current": ask_float("Battery Current (A, negative=discharge)", default=-20.0),
        "soc": ask_float("Current SOC (%)", default=75.0, low=0, high=100),
        "speed": ask_float("Vehicle Speed (km/h)", default=36.0, low=0, high=150),
    }


# ─────────────────────────────────────────────
#  MODULE B INPUT COLLECTORS
# ─────────────────────────────────────────────
def collect_thermal_inputs() -> dict:
    print(f"\n  {C['magenta']}Enter multi-zone thermal data for Thermal Safety Check:{C['reset']}")
    return {
        "vbt": ask_float("Battery Pack Temperature (°C)", default=32.0, low=-20, high=120),
        "vct": ask_float("Controller/Inverter Temperature (°C)", default=44.0, low=-20, high=140),
        "vmt": ask_float("Motor Temperature (°C)", default=58.0, low=-20, high=160),
        "vbv": ask_float("Pack Voltage (V)", default=74.0, low=0, high=150),
        "vbc": ask_float("Battery Current (A, negative=discharge)", default=-24.0),
        "soc": ask_float("State of Charge (%)", default=78.5, low=0, high=100),
        "speed": ask_float("Vehicle Speed (km/h)", default=35.0, low=0, high=150),
    }


def collect_soh_deep_inputs() -> list:
    print(f"\n  {C['magenta']}Enter chronological telemetry sequence for SOH Deep Analysis:{C['reset']}")
    print(f"  {C['cyan']}Each step = [voltage, current, battery_temp, soc] (enter 10 steps){C['reset']}")
    steps = []
    defaults = [
        [78.0, -15.0, 28.0, 85.0], [77.5, -18.0, 28.5, 84.0],
        [77.0, -20.0, 29.0, 83.0], [76.5, -22.0, 29.5, 82.0],
        [76.0, -20.0, 30.0, 81.0], [75.5, -18.0, 30.2, 80.0],
        [75.0, -19.0, 30.5, 79.0], [74.5, -20.0, 30.8, 78.0],
        [74.0, -21.0, 31.0, 77.0], [73.5, -22.0, 31.2, 76.0],
    ]
    use_defaults = input(
        f"  {C['cyan']}Use demo sequence? (y=yes, n=enter manually) [y]: {C['reset']}"
    ).strip().lower()
    if use_defaults in ("", "y", "yes"):
        print(f"  {C['green']}Using demo 10-step Euler HiLoad sequence.{C['reset']}")
        return defaults
    for i in range(10):
        print(f"  Step {i+1}/10:")
        v   = ask_float("  Voltage (V)", default=defaults[i][0], low=0, high=150)
        c   = ask_float("  Current (A)", default=defaults[i][1])
        bt  = ask_float("  Battery Temp (°C)", default=defaults[i][2], low=-20, high=70)
        soc = ask_float("  SOC (%)", default=defaults[i][3], low=0, high=100)
        steps.append([v, c, bt, soc])
    return steps


def collect_diagnosis_inputs() -> dict:
    print(f"\n  {C['magenta']}Enter vehicle data for Full Dual-Pillar Diagnosis:{C['reset']}")
    return {
        "vehicle_id": input(f"  {C['cyan']}Vehicle ID (e.g. GJ05CV6564): {C['reset']}").strip() or "GJ05CV6564",
        "soc": ask_float("SOC (%)", default=78.5, low=0, high=100),
        "voltage": ask_float("Pack Voltage (V)", default=74.0, low=0, high=150),
        "current": ask_float("Battery Current (A, negative=discharge)", default=-24.0),
        "battery_temp": ask_float("Battery Temp (°C)", default=32.0, low=-20, high=120),
        "controller_temp": ask_float("Controller Temp (°C, press Enter to estimate)", default=40.0, low=-20, high=140),
        "motor_temp": ask_float("Motor Temp (°C, press Enter to estimate)", default=55.0, low=-20, high=160),
        "speed": ask_float("Speed (km/h)", default=35.0, low=0, high=150),
    }


def _run_module_b_task(task: str):
    """Execute a Module B task using the loaded BatteryIQ engine."""
    if _module_b_engine is None:
        print(f"  {C['red']}✘  Module B engine not loaded. Check module3/weights/ directory.{C['reset']}")
        return

    from src.core.schemas import VehicleTelemetryPacket, MultiZoneThermalInput, SOHSequenceInput

    print(f"\n  {'═'*65}")
    print(f"  {C['bold']}{C['magenta']}MODULE B — {task}{C['reset']}")
    print(f"  {'═'*65}")

    if task == "Thermal":
        inputs = collect_thermal_inputs()
        thermal_input = MultiZoneThermalInput(**inputs)
        result = _module_b_engine.predict_thermal_vector(thermal_input)
        print(f"\n  {'─'*65}")
        print(f"  {C['bold']} Thermal Safety Result:{C['reset']}")
        print(f"  {'─'*65}")
        status_color = C['red'] if result.is_critical else C['green']
        print(f"  Status:        {status_color}{result.safety_status}{C['reset']}")
        print(f"  Risk Prob:     {C['yellow']}{result.risk_probability*100:.1f}%{C['reset']}")
        print(f"  Threat:        {result.primary_thermal_threat}")
        print(f"  Hotspot Zone:  {result.hotspot_zone}")
        print(f"  BMS Action:    {C['cyan']}{result.recommended_bms_action}{C['reset']}")
        print(f"  Model:         {C['magenta']}{result.model_architecture}{C['reset']}")
        print(f"  {'─'*65}")

    elif task == "SOH_Deep":
        sequence = collect_soh_deep_inputs()
        vid = input(f"  {C['cyan']}Vehicle ID [DEMO]: {C['reset']}").strip() or "DEMO"
        seq_input = SOHSequenceInput(vehicle_id=vid, sequence=sequence)
        result = _module_b_engine.predict_soh_sequence(seq_input)
        print(f"\n  {'─'*65}")
        print(f"  {C['bold']} SOH Deep Result (CNN-LSTM):{C['reset']}")
        print(f"  {'─'*65}")
        soh_color = C['green'] if result.estimated_soh_percent >= 80 else (C['yellow'] if result.estimated_soh_percent >= 65 else C['red'])
        print(f"  Estimated SOH: {soh_color}{result.estimated_soh_percent}%{C['reset']}")
        print(f"  Category:      {result.capacity_state}")
        print(f"  95% CI:        [{result.confidence_interval['ci_95_lower']}% — {result.confidence_interval['ci_95_upper']}%]")
        print(f"  Degradation:   {result.degradation_slope_per_100_cycles}% per 100 cycles")
        print(f"  Model:         {C['magenta']}{result.model_architecture} | RMSE={result.verified_benchmark_rmse}%{C['reset']}")
        print(f"  {'─'*65}")

    elif task == "Diagnosis":
        inputs = collect_diagnosis_inputs()
        packet = VehicleTelemetryPacket(
            vehicle_id=inputs["vehicle_id"],
            soc=inputs["soc"],
            voltage=inputs["voltage"],
            current=inputs["current"],
            battery_temp=inputs["battery_temp"],
            controller_temp=inputs.get("controller_temp"),
            motor_temp=inputs.get("motor_temp"),
            speed=inputs["speed"],
        )
        report = _module_b_engine.diagnose_packet(packet)
        print(f"\n  {'─'*65}")
        print(f"  {C['bold']} Full Diagnostic Report: {report.vehicle_id}{C['reset']}")
        print(f"  {'─'*65}")
        score = report.overall_health_score
        score_color = C['green'] if score >= 80 else (C['yellow'] if score >= 60 else C['red'])
        print(f"  Health Score:  {score_color}{score}/100{C['reset']}")
        print(f"  Fleet Mode:    {C['cyan']}{report.fleet_operating_mode}{C['reset']}")
        print(f"  Twin Status:   {report.digital_twin_sync_status}")
        print(f"\n  {C['bold']}[SOH Engine]{C['reset']}")
        print(f"    SOH:         {report.soh_evaluation.estimated_soh_percent}%  ({report.soh_evaluation.capacity_state})")
        print(f"    95% CI:      [{report.soh_evaluation.confidence_interval['ci_95_lower']}% — {report.soh_evaluation.confidence_interval['ci_95_upper']}%]")
        print(f"\n  {C['bold']}[Thermal Engine]{C['reset']}")
        t = report.thermal_evaluation
        thermal_color = C['red'] if t.is_critical else C['green']
        print(f"    Status:      {thermal_color}{t.safety_status}{C['reset']}")
        print(f"    Risk Prob:   {t.risk_probability*100:.1f}%")
        print(f"    Hotspot:     {t.hotspot_zone}")
        print(f"    Action:      {C['cyan']}{t.recommended_bms_action}{C['reset']}")
        print(f"  {'─'*65}")


# ─────────────────────────────────────────────
#  MODULE C TASK RUNNER
# ─────────────────────────────────────────────
def _run_module_c_task(task: str):
    if _module_c_engine is None or not _module_c_engine.is_loaded:
        print(f"\n  {C['red']}✘ Module C BABMSEngine is not loaded. Check modules/module_c/.{C['reset']}")
        return

    print(f"\n  {'═'*65}")
    print(f"  {C['bold']}{C['yellow']}MODULE C — {task.replace('_', ' ').upper()}{C['reset']}")
    print(f"  {'═'*65}")

    if task == "Driver_Behavior":
        inputs = collect_behavior_inputs()
        res = _module_c_engine.compute_behavior_indices(**inputs)
        print(f"\n  {'─'*65}")
        print(f"  {C['bold']} BA-BMS Driver Behavior & Stress Profile:{C['reset']}")
        print(f"  {'─'*65}")
        ai = res["aggressiveness_index"]
        ai_color = C['green'] if ai <= 0.35 else (C['yellow'] if ai <= 0.65 else C['red'])
        print(f"  Aggressiveness Index (AI): {ai_color}{ai}  [{res['driver_classification']}]{C['reset']}")
        
        bsi = res["battery_stress_index"]
        bsi_color = C['green'] if bsi <= 0.40 else (C['yellow'] if bsi <= 0.70 else C['red'])
        print(f"  Battery Stress Index (BSI): {bsi_color}{bsi}{C['reset']}")
        print(f"  SOH Impact:                {C['yellow']}{res['behavioral_impact_description']}{C['reset']}")
        print(f"  BMS Directive:             {C['cyan']}{res['bms_recommended_directive']}{C['reset']}")
        print(f"  {'─'*65}")

    elif task == "Knee_Prognostics":
        inputs = collect_knee_inputs()
        res = _module_c_engine.predict_knee_point(inputs)
        print(f"\n  {'─'*65}")
        print(f"  {C['bold']} Battery Degradation Knee-Point Prognostics:{C['reset']}")
        print(f"  {'─'*65}")
        rul_knee = res["rul_to_knee_cycles"]
        knee_color = C['green'] if rul_knee > 200 else (C['yellow'] if rul_knee > 50 else C['red'])
        print(f"  Current Cycle Count:       {res['current_cycle_count']}")
        print(f"  RUL to Knee Point:         {knee_color}{rul_knee} charge cycles{C['reset']}")
        print(f"  Estimated Knee Cycle:      {res['estimated_knee_cycle']}")
        print(f"  Risk State:                {knee_color}{res['knee_risk_state']}{C['reset']}")
        print(f"  Recommended Action:        {C['cyan']}{res['recommended_action']}{C['reset']}")
        print(f"  Model Used:                {C['magenta']}{res['model_used']}{C['reset']}")
        print(f"  {'─'*65}")


# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────
def run_prediction_system():
    print(BANNER)

    # Load Module A models
    print(f"  {C['cyan']}[Module A] Loading fleet prediction models...{C['reset']}")
    models  = {}
    scalers = {}
    for task in ["SOC", "SOH", "RUL", "Mileage"]:
        name, model = find_best_model(task)
        if model:
            models[task]  = {"name": name, "model": model}
            scalers[task] = find_scaler(TASK_KEYS[task])
            print(f"  {C['green']}  ✔  {task}: {name}{C['reset']}")
        else:
            print(f"  {C['red']}  ✘  {task}: No model found — run retrain_clean.py first{C['reset']}")

    # Load Module B engine
    print(f"  {C['magenta']}[Module B] Loading BatteryIQ engine (CNN-LSTM + Thermal RF)...{C['reset']}")
    b_ok = _load_module_b_engine()
    icon_b = "✔" if b_ok else "✘"
    color_b = C['green'] if b_ok else C['red']
    print(f"  {color_b}  {icon_b}  BatteryIQ Engine (SOH-Deep + Thermal Fault Detection){C['reset']}")

    # Load Module C engine
    print(f"  {C['yellow']}[Module C] Loading BA-BMS & Knee-Point Prognostics engine...{C['reset']}")
    c_ok = _load_module_c_engine()
    icon_c = "✔" if c_ok else "✘"
    color_c = C['green'] if c_ok else C['red']
    print(f"  {color_c}  {icon_c}  BA-BMS Engine (Behavior AI/BSI + Knee Prognostics){C['reset']}")

    if not models and not b_ok and not c_ok:
        print(f"\n  {C['red']}No models available. Run retrain_clean.py and check module weights.{C['reset']}\n")
        return

    while True:
        print(TASK_MENU)
        choice = input(f"  {C['cyan']}Your choice: {C['reset']}").strip()

        if choice == "0":
            print(f"\n  {C['green']}Thank you for using the EV Battery Intelligence System!{C['reset']}\n")
            break

        tasks_to_run = []
        if choice == "5":
            tasks_to_run = list(MODULE_A_TASKS)
        elif choice == "9":
            tasks_to_run = list(MODULE_B_TASKS)
        elif choice == "12":
            tasks_to_run = MODULE_A_TASKS + MODULE_B_TASKS + MODULE_C_TASKS
        elif choice in TASK_MAP:
            tasks_to_run = [TASK_MAP[choice]]
        else:
            print(f"  {C['red']}Invalid choice. Enter 0-12.{C['reset']}")
            continue

        for task in tasks_to_run:
            # ── Module C tasks
            if task in MODULE_C_TASKS:
                _run_module_c_task(task)
                continue

            # ── Module B tasks
            if task in MODULE_B_TASKS:
                _run_module_b_task(task)
                continue

            # ── Module A tasks
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
