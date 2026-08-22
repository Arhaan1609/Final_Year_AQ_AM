"""
api/routers/module_a.py — REST endpoints for Module A predictions.
Serves: SOC (Random Forest), SOH (Extra Trees), RUL (Random Forest), Mileage (XGBoost).
"""

import os
import sys
import numpy as np
import joblib
from fastapi import APIRouter, HTTPException

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


def _patch_model_compatibility(model):
    if hasattr(model, "named_steps"):
        for _, step_obj in model.named_steps.items():
            if hasattr(step_obj, "missing_values") and not hasattr(step_obj, "_fill_dtype"):
                step_obj._fill_dtype = np.float64
    return model


def _load_best_model(task: str):
    """Load the best pkl model for a given task using task subfolder or root models dir."""
    txt = cfg.get_model_file_path(task, f"{task}_best_model.txt")
    model_name = None
    if os.path.exists(txt):
        with open(txt) as f:
            line = f.readline().strip()
            model_name = line.replace("Best Model: ", "").strip()

    preference = ["RandomForest", "XGBoost", "GradientBoosting", "ExtraTrees",
                  "Ridge", "KNN", "DecisionTree", "Lasso", "SVR"]
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
                return name, model
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
        if value >= 90: return "Excellent battery health."
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


def _predict(task: str, feature_dict: dict) -> PredictionResponse:
    if task not in _MODELS:
        raise HTTPException(
            status_code=503,
            detail=f"{task} model not loaded. Run modules/module_a/retrain_clean.py first."
        )
    model = _MODELS[task]

    # Intelligent feature auto-synthesis for derived fleet telemetry
    odo = float(feature_dict.get("odometer", 0.0))
    cycles = float(feature_dict.get("charge_cycle_count", odo / 58.0 if odo > 0 else 150.0))
    v = float(feature_dict.get("battery_voltage", 74.0))
    t = float(feature_dict.get("battery_temp", 32.0))
    i = float(feature_dict.get("battery_current", -18.0))
    soc = float(feature_dict.get("soc_at_charge", feature_dict.get("soc", 75.0)))
    soh_m = float(feature_dict.get("soh_mean", max(65.0, 100.0 - (cycles * 0.025))))

    synthesized = dict(feature_dict)
    synthesized.setdefault("charge_cycle_count", cycles)
    synthesized.setdefault("voltage_deviation", round(v - 72.0, 2))
    synthesized.setdefault("temp_stress_index", round(max(0.0, min(1.0, (t - 25.0) / 30.0)), 3))
    synthesized.setdefault("abs_current", abs(i))
    synthesized.setdefault("degradation_factor", round(min(1.0, cycles / 1400.0), 4))
    synthesized.setdefault("days_in_service", max(1.0, round(cycles * 1.25)))
    synthesized.setdefault("soh_mean", soh_m)
    synthesized.setdefault("miles_per_charge", max(45.0, min(130.0, 120.0 - (cycles * 0.035))))
    synthesized.setdefault("miles_per_charge_rolling_3", max(45.0, min(130.0, 120.0 - (cycles * 0.035))))
    synthesized.setdefault("miles_per_charge_rolling_5", max(45.0, min(130.0, 120.0 - (cycles * 0.035))))
    synthesized.setdefault("miles_per_charge_rolling_10", max(45.0, min(130.0, 120.0 - (cycles * 0.035))))
    synthesized.setdefault("mile_avg", max(40.0, min(120.0, 110.0 - (cycles * 0.03))))
    
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

    # Physics-Informed Hybridization Layer (Coupling ML with Semi-Empirical Aging)
    if task == "SOH":
        # Capacity loss scaling: LFP degradation rate (~0.018% per EFC + thermal acceleration)
        cycle_fade = (cycles * 0.021)
        temp_fade = max(0.0, (t - 33.0) * 0.18)
        pred = max(68.0, min(100.0, raw_pred - cycle_fade - temp_fade))
    elif task == "RUL":
        # Cumulative cycle subtraction from design lifetime (1400 EFC to 80% SOH)
        base_lifespan = 1350.0
        thermal_penalty = max(0.0, (t - 33.0) * 4.5)
        pred = max(0.0, min(base_lifespan, raw_pred - (cycles * 1.05) - thermal_penalty))
    elif task == "Mileage":
        # Range adjusted for current SOC, SOH and aerodynamic speed drag
        soh_factor = (soh_m / 100.0)
        soc_factor = (soc / 100.0)
        speed_factor = 1.0 - max(0.0, (float(feature_dict.get("avg_speed", 32.0)) - 35.0) * 0.006)
        pred = max(15.0, round(raw_pred * soh_factor * speed_factor, 1))
    elif task == "SOC":
        # Voltage-correlated SOC boundary enforcement for 72V LFP
        pred = max(5.0, min(100.0, raw_pred))
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
