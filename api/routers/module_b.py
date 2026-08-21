"""
api/routers/module_b.py — REST endpoints for Module B (BatteryIQ Engine).
Serves: Thermal fault detection, SOH deep estimation (CNN-LSTM), Full vehicle diagnosis, Batch diagnosis.
"""

import os
import sys
from fastapi import APIRouter, HTTPException

# Add modules/module_b/ to sys.path so its internal `src` package resolves correctly
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_MODULE_B_DIR = os.path.join(_PROJECT_ROOT, "modules", "module_b")
sys.path.insert(0, _MODULE_B_DIR)

from src.models.engine import BatteryIQEngine
from src.core.schemas import (
    VehicleTelemetryPacket,
    MultiZoneThermalInput,
    SOHSequenceInput,
    BatchDiagnosticRequest,
)
from api.schemas import ThermalRequest, SOHDeepRequest, VehicleDiagnosisRequest, BatchDiagnosisRequest

router = APIRouter(prefix="/predict", tags=["Module B — Battery Health & Thermal"])

# ──────────────────────────────────────────────
#  Engine — loaded once at API startup
# ──────────────────────────────────────────────
_engine: BatteryIQEngine = None


def load_module_b_engine():
    """Initialize the BatteryIQ Engine with pre-trained weights. Called at API startup."""
    global _engine
    try:
        _engine = BatteryIQEngine()
        return True
    except Exception as e:
        print(f"  [WARNING] Module B engine failed to load: {e}")
        return False


def get_engine_status() -> bool:
    return _engine is not None


def _require_engine():
    if _engine is None:
        raise HTTPException(
            status_code=503,
            detail="Module B engine not loaded. Check modules/module_b/weights/ directory."
        )


# ──────────────────────────────────────────────
#  ENDPOINTS
# ──────────────────────────────────────────────

@router.post("/thermal", summary="Multi-Zone Thermal Fault Detection")
def predict_thermal(req: ThermalRequest):
    """
    Run Multi-Zone Random Forest classifier on [vbt, vct, vmt, vbv, vbc, soc, speed].
    Returns thermal safety status, risk probability, hotspot zone, and BMS action directive.
    Champion performance: F1 = 0.997 (99.71% accuracy) on 50/50 balanced fleet data.
    """
    _require_engine()
    thermal_input = MultiZoneThermalInput(
        vbt=req.vbt, vct=req.vct, vmt=req.vmt,
        vbv=req.vbv, vbc=req.vbc, soc=req.soc, speed=req.speed
    )
    result = _engine.predict_thermal_vector(thermal_input)
    return result.model_dump()


@router.post("/soh-deep", summary="SOH Deep Estimation (Hybrid CNN-LSTM)")
def predict_soh_deep(req: SOHDeepRequest):
    """
    Run Hybrid 1D-CNN + LSTM on a chronological telemetry sequence.
    Input: list of [voltage, current, battery_temp, soc] readings (min 5, ideal 10).
    Returns SOH %, health category, 95% confidence interval, and degradation slope.
    Champion performance: RMSE 5.29% on 20.5M Euler HiLoad records.
    """
    _require_engine()
    if len(req.sequence) < 5:
        raise HTTPException(status_code=422, detail="Sequence must have at least 5 time steps.")
    for step in req.sequence:
        if len(step) != 4:
            raise HTTPException(
                status_code=422,
                detail="Each sequence step must have exactly 4 values: [voltage, current, battery_temp, soc]"
            )

    seq_input = SOHSequenceInput(vehicle_id=req.vehicle_id, sequence=req.sequence)
    result = _engine.predict_soh_sequence(seq_input)
    return result.model_dump()


@router.post("/diagnose/vehicle", summary="Full Vehicle Dual-Pillar Diagnosis")
def diagnose_vehicle(req: VehicleDiagnosisRequest):
    """
    Run complete BatteryIQ dual-pillar diagnosis on a single telemetry packet.
    Returns: Composite Health Score (0-100), SOH evaluation, Thermal safety report,
    Fleet operating mode, and Digital twin sync status.
    """
    _require_engine()
    packet = VehicleTelemetryPacket(
        vehicle_id=req.vehicle_id,
        oem_model=req.oem_model or "EV",
        soc=req.soc,
        voltage=req.voltage,
        current=req.current,
        battery_temp=req.battery_temp,
        controller_temp=req.controller_temp,
        motor_temp=req.motor_temp,
        speed=req.speed,
        odometer_km=req.odometer_km,
    )
    report = _engine.diagnose_packet(packet)
    return report.model_dump()


@router.post("/diagnose/batch", summary="Fleet Batch Diagnosis")
def diagnose_batch(req: BatchDiagnosisRequest):
    """
    Run dual-pillar diagnosis on a batch of fleet telemetry packets.
    Returns all individual diagnostic reports plus critical alert count and execution time.
    """
    _require_engine()
    if not req.packets:
        raise HTTPException(status_code=422, detail="packets list cannot be empty.")
    if len(req.packets) > 500:
        raise HTTPException(status_code=422, detail="Batch size limit is 500 packets per request.")

    packets_m3 = [
        VehicleTelemetryPacket(
            vehicle_id=p.vehicle_id,
            oem_model=p.oem_model or "EV",
            soc=p.soc,
            voltage=p.voltage,
            current=p.current,
            battery_temp=p.battery_temp,
            controller_temp=p.controller_temp,
            motor_temp=p.motor_temp,
            speed=p.speed,
            odometer_km=p.odometer_km,
        )
        for p in req.packets
    ]

    batch_req = BatchDiagnosticRequest(packets=packets_m3)
    response = _engine.diagnose_batch(batch_req)
    return response.model_dump()
