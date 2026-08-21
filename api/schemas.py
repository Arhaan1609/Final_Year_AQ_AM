"""
api/schemas.py — Unified Pydantic request/response models for the EV Battery Intelligence API.

Covers Module A (SOC, SOH-tabular, RUL, Mileage) and Module B (Thermal, SOH-deep, Full Diagnosis).
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


# ──────────────────────────────────────────────
#  MODULE A — REQUEST SCHEMAS
# ──────────────────────────────────────────────

class SOCRequest(BaseSchema):
    """Input features for State of Charge prediction (Module A — Random Forest)."""
    battery_voltage: float = Field(..., ge=20, le=150, description="Battery voltage (V)")
    battery_temp: float = Field(..., ge=-20, le=70, description="Battery temperature (°C)")
    battery_current: float = Field(..., description="Battery current (A, negative=discharge)")
    abs_current: float = Field(..., ge=0, description="Absolute current magnitude (A)")
    is_charging: int = Field(0, ge=0, le=1, description="1 if charging, 0 if discharging")
    odometer: float = Field(..., ge=0, description="Cumulative odometer (km)")
    odometer_diff: float = Field(0.0, description="Recent trip distance (km)")
    voltage_deviation: float = Field(0.0, description="Deviation from 72V nominal")
    temp_stress_index: float = Field(0.0, ge=0, le=1, description="Temp stress (0-1)")
    drive_mode_encoded: int = Field(1, ge=0, le=2, description="0=Eco, 1=Normal, 2=Sport")
    hour: int = Field(10, ge=0, le=23)
    day_of_week: int = Field(2, ge=0, le=6)
    month: int = Field(6, ge=1, le=12)
    is_weekend: int = Field(0, ge=0, le=1)
    is_peak: int = Field(0, ge=0, le=1)
    oem_encoded: int = Field(0, ge=0)
    model_encoded: int = Field(0, ge=0)


class SOHRequest(BaseSchema):
    """Input features for State of Health prediction (Module A — Extra Trees)."""
    battery_voltage: float = Field(..., ge=20, le=150)
    battery_temp: float = Field(..., ge=-20, le=70)
    battery_current: float = Field(...)
    abs_current: float = Field(..., ge=0)
    odometer: float = Field(..., ge=0)
    odometer_diff: float = Field(0.0)
    charge_cycle_count: float = Field(..., ge=0)
    mile_avg: float = Field(..., ge=0)
    miles_per_charge: float = Field(..., ge=0)
    days_in_service: float = Field(..., ge=1)
    degradation_factor: float = Field(0.0, ge=-1, le=1)
    temp_stress_index: float = Field(0.0, ge=0, le=1)
    voltage_deviation: float = Field(0.0)
    oem_encoded: int = Field(0, ge=0)
    model_encoded: int = Field(0, ge=0)


class RULRequest(BaseSchema):
    """Input features for Remaining Useful Life prediction (Module A — Random Forest)."""
    odometer: float = Field(..., ge=0)
    soc_at_charge: float = Field(..., ge=0, le=100)
    mile_avg: float = Field(..., ge=0)
    miles_per_charge: float = Field(..., ge=0)
    days_in_service: float = Field(..., ge=1)
    degradation_factor: float = Field(0.0, ge=-1, le=1)
    soh_mean: float = Field(85.0, ge=0, le=120)
    miles_per_charge_rolling_3: float = Field(..., ge=0)
    miles_per_charge_rolling_5: float = Field(..., ge=0)
    miles_per_charge_rolling_10: float = Field(..., ge=0)
    oem_encoded: int = Field(0, ge=0)
    model_encoded: int = Field(0, ge=0)


class MileageRequest(BaseSchema):
    """Input features for Mileage per Charge prediction (Module A — XGBoost)."""
    run_kms: float = Field(..., ge=0)
    avg_speed: float = Field(..., ge=0, le=200)
    max_speed: float = Field(..., ge=0, le=200)
    trip_duration_hrs: float = Field(..., ge=0)
    stoppage_count: int = Field(0, ge=0)
    energy_efficiency: float = Field(..., ge=0)
    trip_intensity: float = Field(..., ge=0)
    speed_ratio: float = Field(..., ge=0, le=1)
    stoppage_density: float = Field(0.0, ge=0)
    energy_utilized: float = Field(..., ge=0)
    hour: int = Field(10, ge=0, le=23)
    day_of_week: int = Field(2, ge=0, le=6)
    month: int = Field(6, ge=1, le=12)
    is_weekend: int = Field(0, ge=0, le=1)
    is_peak: int = Field(0, ge=0, le=1)
    oem_encoded: int = Field(0, ge=0)
    city_encoded: int = Field(0, ge=0)


# ──────────────────────────────────────────────
#  MODULE B — REQUEST SCHEMAS
# ──────────────────────────────────────────────

class ThermalRequest(BaseSchema):
    """Input for Multi-Zone Thermal Fault Detection (Module B — RF Classifier)."""
    vbt: float = Field(..., ge=-20, le=120, description="Battery Pack Temperature (°C)")
    vct: float = Field(..., ge=-20, le=140, description="Controller/Inverter Temperature (°C)")
    vmt: float = Field(..., ge=-20, le=160, description="Motor Temperature (°C)")
    vbv: float = Field(..., ge=0, le=150, description="Pack Voltage (V)")
    vbc: float = Field(..., description="Battery Current (A)")
    soc: float = Field(..., ge=0, le=100, description="State of Charge (%)")
    speed: float = Field(0.0, ge=0, le=150, description="Vehicle Speed (km/h)")


class SOHDeepRequest(BaseSchema):
    """Sequence input for CNN-LSTM SOH Estimator (Module B)."""
    vehicle_id: str = Field("UNKNOWN", description="Vehicle registration / chassis ID")
    sequence: List[List[float]] = Field(
        ...,
        description="Chronological matrix shape (seq_len≥5, 4): [voltage, current, battery_temp, soc]"
    )


class VehicleDiagnosisRequest(BaseSchema):
    """Single telemetry packet for full dual-pillar diagnosis (Module B)."""
    vehicle_id: str = Field(..., description="Unique vehicle ID")
    oem_model: Optional[str] = Field("EV", description="OEM and model name")
    soc: float = Field(..., ge=0, le=100)
    voltage: float = Field(..., ge=0, le=150)
    current: float = Field(0.0)
    battery_temp: float = Field(..., ge=-20, le=120)
    controller_temp: Optional[float] = Field(None, ge=-20, le=140)
    motor_temp: Optional[float] = Field(None, ge=-20, le=160)
    speed: float = Field(0.0, ge=0, le=150)
    odometer_km: Optional[float] = Field(None, ge=0)


class BatchDiagnosisRequest(BaseSchema):
    """Batch of vehicle telemetry packets for fleet diagnosis (Module B)."""
    packets: List[VehicleDiagnosisRequest]


# ──────────────────────────────────────────────
#  UNIFIED RESPONSE SCHEMAS
# ──────────────────────────────────────────────

class PredictionResponse(BaseSchema):
    """Standard response for Module A single-value predictions."""
    task: str
    prediction: float
    unit: str
    model_used: str
    interpretation: str
    confidence_margin: Optional[float] = None


class HealthStatusResponse(BaseSchema):
    """Response for Module B health status endpoints."""
    status: str = "ok"
    module_a_models: Dict[str, bool] = {}
    module_b_engine: bool = False
    message: str = ""
