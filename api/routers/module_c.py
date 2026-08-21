"""
api/routers/module_c.py — REST endpoints for Module C (BA-BMS & Knee-Point Prognostics).

Serves:
  - Driver Aggressiveness Index (AI) & Battery Stress Index (BSI)
  - Battery Degradation Knee-Point RUL Prognostics (XGBoost Booster)
  - Multi-Target Meta-Ensemble estimation
"""

import os
import sys
from fastapi import APIRouter, HTTPException

# Add modules/module_c/ to sys.path so engine.py resolves cleanly
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_MODULE_C_DIR = os.path.join(_PROJECT_ROOT, "modules", "module_c")
sys.path.insert(0, _MODULE_C_DIR)

from engine import BABMSEngine
from api.schemas import (
    DriverBehaviorRequest,
    DriverBehaviorResponse,
    KneePredictionRequest,
    KneePredictionResponse,
    MetaEnsembleRequest,
    MetaEnsembleResponse,
)

router = APIRouter(prefix="/predict", tags=["Module C — Behavior & Knee Prognostics"])

# ──────────────────────────────────────────────
#  Engine instance — loaded once at API startup
# ──────────────────────────────────────────────
_engine: BABMSEngine = None


def load_module_c_engine():
    """Initialize the BABMSEngine with pre-trained XGBoost weights and scaler."""
    global _engine
    try:
        _engine = BABMSEngine()
        return _engine.is_loaded
    except Exception as e:
        print(f"  [WARNING] Module C engine failed to load: {e}")
        return False


def get_engine_status() -> bool:
    return _engine is not None and _engine.is_loaded


def _require_engine():
    if _engine is None or not _engine.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Module C engine not loaded. Check modules/module_c/best_xgboost_model.json."
        )


# ──────────────────────────────────────────────
#  ENDPOINTS
# ──────────────────────────────────────────────

@router.post("/driver-behavior", response_model=DriverBehaviorResponse, summary="Driver Aggressiveness (AI) & Battery Stress (BSI)")
def predict_driver_behavior(req: DriverBehaviorRequest):
    """
    Compute Driver Aggressiveness Index (AI) and Battery Stress Index (BSI) based on driving events.
    Returns composite score (0-1), driver classification, annual SOH penalty, and BMS directive.
    """
    _require_engine()
    res = _engine.compute_behavior_indices(
        harsh_accel_count=req.harsh_accel_count,
        harsh_brake_count=req.harsh_brake_count,
        harsh_corner_count=req.harsh_corner_count,
        speed_variance=req.speed_variance,
        avg_speed=req.avg_speed,
        max_speed=req.max_speed,
        overspeed_count=req.overspeed_count,
        battery_temp_max=req.battery_temp_max,
        max_discharge_current=req.max_discharge_current,
        voltage_variance=req.voltage_variance,
        soc_drain_rate=req.soc_drain_rate,
    )
    return res


@router.post("/knee-point", response_model=KneePredictionResponse, summary="Battery Degradation Knee-Point Prognostics")
def predict_knee_point(req: KneePredictionRequest):
    """
    Predict Remaining Useful Life to the battery degradation Knee Point (RUL_to_knee).
    Uses 28-feature StandardScaler and pre-trained XGBoost Booster model.
    """
    _require_engine()
    res = _engine.predict_knee_point(req.model_dump())
    return res


@router.post("/meta-ensemble", response_model=MetaEnsembleResponse, summary="Multi-Target Meta-Ensemble Estimation")
def predict_meta_ensemble(req: MetaEnsembleRequest):
    """
    Simultaneously project multi-target SOH and Knee RUL by combining behavioral
    features and temporal cycle progression.
    """
    _require_engine()
    
    # 1. Behavior indices
    beh = _engine.compute_behavior_indices(
        harsh_accel_count=req.harsh_accel_count,
        speed_variance=req.speed_variance,
        battery_temp_max=req.battery_temp,
        max_discharge_current=abs(req.battery_current),
    )

    # 2. Knee prognostics
    knee = _engine.predict_knee_point({
        'charge_cycle_count': req.charge_cycle_count,
        'voltage': req.battery_voltage,
        'battery_temp': req.battery_temp,
        'current': req.battery_current,
        'soc': req.soc,
    })

    # 3. Estimated SOH incorporating behavioral degradation
    base_soh = max(0.0, min(100.0, 100.0 - (req.charge_cycle_count / 1500.0) * 20.0))
    beh_adjusted_soh = round(max(0.0, base_soh - beh["annual_soh_penalty_percent"]), 2)

    status_str = "Optimal" if beh_adjusted_soh >= 85 and knee["rul_to_knee_cycles"] > 150 else "Monitor / High Wear"

    return {
        "vehicle_id": req.vehicle_id,
        "estimated_soh": beh_adjusted_soh,
        "rul_to_knee_cycles": knee["rul_to_knee_cycles"],
        "driver_aggressiveness_index": beh["aggressiveness_index"],
        "battery_stress_index": beh["battery_stress_index"],
        "health_status": status_str,
        "ensemble_architecture": "Meta-Ensemble (XGBoost + BA-BMS Dynamic Engine)",
    }
