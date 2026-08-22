"""
api/routers/module_a.py — REST endpoints for Module A predictions.
Serves: SOC (Random Forest), SOH (Extra Trees), RUL (Random Forest), Mileage (XGBoost).
"""

import os
import sys
import logging
import numpy as np
import joblib
from fastapi import APIRouter, HTTPException

logger = logging.getLogger("api.module_a")

# Project root → modules/module_a/ so config.py resolves correctly
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_MODULE_A_DIR = os.path.join(_PROJECT_ROOT, "modules", "module_a")
sys.path.insert(0, _MODULE_A_DIR)

import config as cfg
from api.schemas import SOCRequest, SOHRequest, RULRequest, MileageRequest, PredictionResponse

router = APIRouter(prefix="/predict", tags=["Module A — Fleet Predictions"])

# ──────────────────────────────────────────────
#  Model Registry — loaded once at startup
# ──────────────────────────────────────────────
_MODELS: dict = {}
_BEST_MODEL_NAMES: dict = {}
_KNOWN_BASELINES: dict = {}

try:
    _features_soh_csv = os.path.join(_PROJECT_ROOT, "data", "processed", "module_a_fleet_telematics", "features_soh.csv")
    if os.path.exists(_features_soh_csv):
        import pandas as pd
        _df_b = pd.read_csv(_features_soh_csv, usecols=["chassis_no", "soh"])
        for ch, grp in _df_b.groupby("chassis_no"):
            _KNOWN_BASELINES[str(ch)] = float(grp["soh"].iloc[0])
    _fleet_json = os.path.join(_PROJECT_ROOT, "frontend", "public", "data", "fleet_vehicles.json")
    if os.path.exists(_fleet_json):
        import json
        with open(_fleet_json) as f:
            for v in json.load(f):
                if "chassis" in v: _KNOWN_BASELINES[str(v["chassis"])] = float(v.get("soh", 95.0))
                if "id" in v: _KNOWN_BASELINES[str(v["id"])] = float(v.get("soh", 95.0))
except Exception as e:
    print(f"  [WARNING] Could not preload baseline SOH lookup table: {e}")


def _patch_model_compatibility(model):
    if hasattr(model, "named_steps"):
        for _, step_obj in model.named_steps.items():
            if hasattr(step_obj, "missing_values") and not hasattr(step_obj, "_fill_dtype"):
                step_obj._fill_dtype = np.float64
    return model


def _load_best_model(task: str):
    """Load the best group-split / calibrated pkl model for a given task."""
    if task == "SOH":
        # Calibrated baseline models
        preference = ["XGBoost", "Ridge", "Lasso", "ExtraTrees", "RandomForest"]
        for name in preference:
            pkl = cfg.get_model_file_path(task, f"SOH_Calibrated_{name}.pkl")
            if os.path.exists(pkl):
                try:
                    model = joblib.load(pkl)
                    model = _patch_model_compatibility(model)
                    return f"Calibrated {name}", model
                except Exception:
                    continue
        return None, None

    # SOC, RUL, Mileage models
    txt = cfg.get_model_file_path(task, f"{task}_best_model.txt")
    model_name = None
    if os.path.exists(txt):
        with open(txt) as f:
            line = f.readline().strip()
            model_name = line.replace("Best Model: ", "").strip()

    # For SOC, prefer non-linear tree models over unscaled linear models
    if task == "SOC":
        preference = ["XGBoost", "GradientBoosting", "RandomForest", "ExtraTrees", "KNN"]
        candidates = preference
    elif task == "RUL":
        preference = ["GradientBoosting", "XGBoost", "RandomForest", "ExtraTrees"]
        candidates = [model_name] + preference if model_name else preference
    elif task == "Mileage":
        preference = ["XGBoost", "RandomForest", "GradientBoosting", "ExtraTrees"]
        candidates = [model_name] + preference if model_name else preference
    else:
        preference = ["XGBoost", "GradientBoosting", "RandomForest", "ExtraTrees", "Ridge", "Lasso"]
        candidates = [model_name] + preference if model_name else preference
    seen = set()
    deduped = []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            deduped.append(c)

    for name in deduped:
        pkl = cfg.get_model_file_path(task, f"{task}_{name}.pkl")
        if os.path.exists(pkl):
            try:
                model = joblib.load(pkl)
                model = _patch_model_compatibility(model)
                return f"Group-Split {name}", model
            except Exception:
                continue
    return None, None


def load_all_module_a_models():
    """Load all 4 Module A models into the registry. Called at API startup."""
    for task in ["SOC", "SOH", "RUL", "Mileage"]:
        name, model = _load_best_model(task)
        if model:
            _MODELS[task] = model
            _BEST_MODEL_NAMES[task] = name
            print(f"  [OK] Module A {task} loaded: {name}")


def get_model_status() -> dict:
    return {task: task in _MODELS for task in ["SOC", "SOH", "RUL", "Mileage"]}


def get_model_names() -> dict:
    return dict(_BEST_MODEL_NAMES)


def _interpret(task: str, value: float) -> str:
    if task == "SOC":
        if value >= 80: return "High charge — Good to go!"
        if value >= 40: return "Moderate charge — Plan a charge soon."
        return "Low charge — Charge immediately!"
    elif task == "SOH":
        if value >= 90: return "Excellent battery health (Calibrated Baseline)."
        if value >= 75: return "Good health — Monitor regularly."
        if value >= 60: return "Degraded — Consider service."
        return "Poor health — Battery replacement recommended."
    elif task == "RUL":
        days = round(max(0, value) / 0.75)
        years = round(days / 365, 1)
        return f"~{max(0,int(value))} cycles remaining (~{days} days / {years} yrs)"
    elif task == "Mileage":
        if value >= 150: return "Excellent range — Long trips possible."
        if value >= 80:  return "Moderate range — City driving comfortable."
        return "Limited range — Short trips only."
    return ""


def _safe_float(val, default: float) -> float:
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _safe_int(val, default: int) -> int:
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def _predict(task: str, feature_dict: dict) -> PredictionResponse:
    if task not in _MODELS:
        raise HTTPException(
            status_code=503,
            detail=f"{task} model not loaded. Run modules/module_a/04_model_training_groupsplit.py first."
        )
    model = _MODELS[task]

    # Intelligent feature auto-synthesis for derived fleet telemetry
    odo = _safe_float(feature_dict.get("odometer"), 0.0)
    passed_cycles = _safe_float(feature_dict.get("charge_cycle_count"), 0.0)
    if odo > 0 and passed_cycles == 0:
        cycles = round(odo / 58.0, 1)
    elif passed_cycles > 0:
        cycles = passed_cycles
    else:
        cycles = 0.0

    v = _safe_float(feature_dict.get("battery_voltage"), 74.0)
    t = _safe_float(feature_dict.get("battery_temp"), 32.0)
    i = _safe_float(feature_dict.get("battery_current"), -18.0)
    soc = _safe_float(feature_dict.get("soc_at_charge", feature_dict.get("soc")), 75.0)
    
    # 1. Resolve authentic per-vehicle commissioning baseline (SOH_0)
    chassis = str(feature_dict.get("chassis_no") or feature_dict.get("chassis") or feature_dict.get("vehicle_id") or feature_dict.get("id") or "")
    if feature_dict.get("initial_soh") is not None and float(feature_dict["initial_soh"]) > 0:
        init_soh = float(feature_dict["initial_soh"])
    elif feature_dict.get("soh") is not None and float(feature_dict["soh"]) > 0:
        init_soh = float(feature_dict["soh"])
    elif chassis and chassis in _KNOWN_BASELINES:
        init_soh = float(_KNOWN_BASELINES[chassis])
    else:
        init_soh = 95.0 # Nominal fleet mean baseline
        logger.warning(f"[DATA SENTINEL WARNING] Task={task}: Missing vehicle chassis / baseline SOH in request; defaulted to 95.0% fleet mean.")

    if feature_dict.get("battery_voltage") is None and task in ["SOC", "SOH"]:
        logger.warning(f"[DATA SENTINEL WARNING] Task={task}: Missing 'battery_voltage' in request; defaulted to 74.0V.")

    synthesized = dict(feature_dict)
    synthesized["battery_voltage"] = v
    synthesized["battery_temp"] = t
    synthesized["battery_current"] = i
    synthesized["charge_cycle_count"] = cycles
    synthesized["charge_cycles"] = cycles
    synthesized["cycle_count"] = cycles
    synthesized["odometer"] = odo
    synthesized["soc_at_charge"] = soc
    synthesized["soc"] = soc
    synthesized["soh"] = init_soh
    synthesized["abs_current"] = abs(i) if synthesized.get("abs_current") is None else float(synthesized["abs_current"])
    synthesized["voltage_deviation"] = float(feature_dict.get("voltage_deviation", round(v - 72.0, 2)))
    synthesized["temp_stress_index"] = float(feature_dict.get("temp_stress_index", round(max(0.0, min(1.0, (t - 25.0) / 30.0)), 3)))
    synthesized["degradation_factor"] = float(feature_dict.get("degradation_factor", round(min(1.0, cycles / 1400.0), 4)))
    synthesized["days_in_service"] = float(feature_dict.get("days_in_service", max(1.0, round(cycles * 1.25))))
    synthesized["soh_mean"] = float(feature_dict.get("soh_mean", init_soh))
    synthesized["mile_avg"] = float(feature_dict.get("mile_avg", 45.0))
    mpc = float(feature_dict.get("miles_per_charge", max(35.0, min(130.0, 120.0 - (cycles * 0.045)))))
    synthesized["miles_per_charge"] = mpc
    synthesized["miles_per_charge_rolling_3"] = float(feature_dict.get("miles_per_charge_rolling_3", mpc))
    synthesized["miles_per_charge_rolling_5"] = float(feature_dict.get("miles_per_charge_rolling_5", mpc))
    synthesized["miles_per_charge_rolling_10"] = float(feature_dict.get("miles_per_charge_rolling_10", mpc))
    
    # History and Calibrated Delta features
    synthesized.setdefault("v_roll_mean_5", v)
    synthesized.setdefault("v_roll_std_5", 0.05)
    synthesized.setdefault("v_roll_slope_5", 0.0)
    synthesized.setdefault("v_roll_mean_10", v)
    synthesized.setdefault("v_roll_std_10", 0.08)
    synthesized.setdefault("v_roll_slope_10", 0.0)
    synthesized.setdefault("v_roll_mean_20", v)
    synthesized.setdefault("v_roll_std_20", 0.12)
    synthesized.setdefault("v_roll_slope_20", 0.0)
    synthesized.setdefault("i_roll_mean_5", i)
    synthesized.setdefault("i_roll_std_5", 0.5)
    synthesized.setdefault("i_roll_slope_5", 0.0)
    synthesized.setdefault("i_roll_mean_10", i)
    synthesized.setdefault("i_roll_std_10", 0.8)
    synthesized.setdefault("i_roll_slope_10", 0.0)
    synthesized.setdefault("i_roll_mean_20", i)
    synthesized.setdefault("i_roll_std_20", 1.2)
    synthesized.setdefault("i_roll_slope_20", 0.0)
    synthesized.setdefault("t_roll_mean_5", t)
    synthesized.setdefault("t_roll_std_5", 0.2)
    synthesized.setdefault("t_roll_mean_10", t)
    synthesized.setdefault("t_roll_std_10", 0.3)
    synthesized.setdefault("t_roll_mean_20", t)
    synthesized.setdefault("t_roll_std_20", 0.5)
    synthesized.setdefault("v_cycle_slope_20", -0.005)
    synthesized.setdefault("charge_acceptance_rate", 0.05)
    synthesized.setdefault("cycles_since_start", max(0.0, cycles))

    # Trip and Mission Dynamics
    run_kms = _safe_float(feature_dict.get("run_kms"), 45.0)
    avg_spd = _safe_float(feature_dict.get("avg_speed"), 32.0)
    max_spd = _safe_float(feature_dict.get("max_speed"), max(avg_spd + 15.0, 55.0))
    dur_hrs = _safe_float(feature_dict.get("trip_duration_hrs"), max(0.5, run_kms / max(15.0, avg_spd)))
    stops = _safe_float(feature_dict.get("stoppage_count"), 3.0)
    energy_kwh = _safe_float(feature_dict.get("energy_utilized"), max(1.0, run_kms * 0.16))

    synthesized.setdefault("run_kms", run_kms)
    synthesized.setdefault("avg_speed", avg_spd)
    synthesized.setdefault("max_speed", max_spd)
    synthesized.setdefault("trip_duration_hrs", round(dur_hrs, 2))
    synthesized.setdefault("stoppage_count", stops)
    synthesized.setdefault("energy_utilized", energy_kwh)
    synthesized.setdefault("energy_efficiency", round(energy_kwh / max(1.0, run_kms), 4))
    synthesized.setdefault("trip_intensity", round(avg_spd * dur_hrs, 2))
    synthesized.setdefault("speed_ratio", round(avg_spd / max(1.0, max_spd), 4))
    synthesized.setdefault("stoppage_density", round(stops / max(0.1, dur_hrs), 2))
    synthesized.setdefault("is_charging", 1 if i > 0 else _safe_int(feature_dict.get("is_charging"), 0))
    synthesized.setdefault("drive_mode_encoded", _safe_int(feature_dict.get("drive_mode_encoded"), 1))
    synthesized.setdefault("odometer_diff", _safe_float(feature_dict.get("odometer_diff"), 0.0))
    synthesized.setdefault("hour", _safe_int(feature_dict.get("hour"), 10))
    synthesized.setdefault("day_of_week", _safe_int(feature_dict.get("day_of_week"), 2))
    synthesized.setdefault("month", _safe_int(feature_dict.get("month"), 6))
    synthesized.setdefault("is_weekend", _safe_int(feature_dict.get("is_weekend"), 0))
    synthesized.setdefault("is_peak", _safe_int(feature_dict.get("is_peak"), 0))
    synthesized.setdefault("oem_encoded", _safe_int(feature_dict.get("oem_encoded"), 0))
    synthesized.setdefault("model_encoded", _safe_int(feature_dict.get("model_encoded"), 0))
    synthesized.setdefault("city_encoded", _safe_int(feature_dict.get("city_encoded"), 0))

    # Extract expected feature names from model if available
    expected_cols = None
    if hasattr(model, "feature_names_in_"):
        expected_cols = list(model.feature_names_in_)
    elif hasattr(model, "named_steps"):
        for step in model.named_steps.values():
            if hasattr(step, "feature_names_in_"):
                expected_cols = list(step.feature_names_in_)
                break

    if expected_cols:
        row = {col: synthesized.get(col, 0.0) for col in expected_cols}
        import pandas as pd
        X = pd.DataFrame([row])
    else:
        X = np.array([[synthesized.get(k, 0.0) for k in synthesized]], dtype=np.float64)
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    try:
        raw_pred = float(model.predict(X).ravel()[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}")

    # Process task outputs
    if task == "SOH":
        # Calibrated baseline delta-SOH reconstruction: SOH = SOH_0 + delta_SOH
        pred = float(np.clip(init_soh + raw_pred, 50.0, 100.0))
    elif task == "RUL":
        pred = float(np.clip(raw_pred, 0.0, 2000.0))
    elif task == "Mileage":
        # Driving range per charge based on vehicle trip efficiency, current SOC and SOH health
        soc_factor = min(1.0, max(0.1, soc / 100.0))
        soh_factor = min(1.0, max(0.5, init_soh / 100.0))
        pred = float(max(10.0, round(raw_pred * soc_factor * soh_factor, 1)))
    elif task == "SOC":
        pred = float(np.clip(raw_pred, 0.0, 100.0))
    else:
        pred = raw_pred

    units = {"SOC": "%", "SOH": "%", "RUL": "cycles", "Mileage": "km"}
    return PredictionResponse(
        task=task,
        prediction=round(pred, 2),
        unit=units[task],
        model_used=_BEST_MODEL_NAMES.get(task, "Unknown"),
        interpretation=_interpret(task, pred),
        confidence_margin=round(abs(pred) * 0.05, 2),
    )


# ──────────────────────────────────────────────
#  ENDPOINTS
# ──────────────────────────────────────────────

@router.post("/soc", response_model=PredictionResponse, summary="State of Charge Prediction")
def predict_soc(req: SOCRequest):
    """Predict current battery State of Charge (%) using the champion Random Forest model."""
    return _predict("SOC", req.model_dump())


@router.post("/soh", response_model=PredictionResponse, summary="State of Health Prediction (Tabular)")
def predict_soh(req: SOHRequest):
    """Predict battery State of Health (%) using the champion Extra Trees model."""
    return _predict("SOH", req.model_dump())


@router.post("/rul", response_model=PredictionResponse, summary="Remaining Useful Life Prediction")
def predict_rul(req: RULRequest):
    """Predict remaining charge cycles before battery end-of-life (Random Forest)."""
    return _predict("RUL", req.model_dump())


@router.post("/mileage", response_model=PredictionResponse, summary="Mileage per Charge Prediction")
def predict_mileage(req: MileageRequest):
    """Predict range (km) achievable on a full charge using champion XGBoost model."""
    return _predict("Mileage", req.model_dump())
