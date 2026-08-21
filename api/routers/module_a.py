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


def _load_best_model(task: str):
    """Load the best pkl model for a given task using the best_model.txt pointer."""
    txt = os.path.join(cfg.MODELS_DIR, f"{task}_best_model.txt")
    model_name = None
    if os.path.exists(txt):
        with open(txt) as f:
            line = f.readline().strip()
            model_name = line.replace("Best Model: ", "").strip()

    preference = ["RandomForest", "XGBoost", "GradientBoosting", "ExtraTrees",
                  "Ridge", "KNN", "DecisionTree", "Lasso", "SVR"]
    candidates = [model_name] + preference if model_name else preference

    for name in candidates:
        pkl = os.path.join(cfg.MODELS_DIR, f"{task}_{name}.pkl")
        if os.path.exists(pkl):
            return name, joblib.load(pkl)
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
        row = {col: feature_dict.get(col, 0.0) for col in expected_cols}
        import pandas as pd
        X = pd.DataFrame([row])
    else:
        X = np.array([[feature_dict.get(k, 0.0) for k in feature_dict]], dtype=np.float64)
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    try:
        pred = float(model.predict(X).ravel()[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}")

    units = {"SOC": "%", "SOH": "%", "RUL": "cycles", "Mileage": "km"}
    return PredictionResponse(
        task=task,
        prediction=round(pred, 4),
        unit=units[task],
        model_used=_BEST_MODEL_NAMES.get(task, "Unknown"),
        interpretation=_interpret(task, pred),
        confidence_margin=round(abs(pred) * 0.10, 4),
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
