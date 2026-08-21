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
    """Input features for State of Health prediction (Module A — Extra Trees / XGBoost)."""
    battery_voltage: float = Field(..., ge=20, le=150)
    battery_temp: float = Field(..., ge=-20, le=70)
    battery_current: float = Field(...)
    abs_current: float = Field(18.0, ge=0)
    odometer: float = Field(12000.0, ge=0)
    odometer_diff: float = Field(0.0)
    charge_cycle_count: float = Field(200.0, ge=0)
    mile_avg: float = Field(88.0, ge=0)
    miles_per_charge: float = Field(95.0, ge=0)
    days_in_service: float = Field(180.0, ge=1)
    degradation_factor: float = Field(0.0, ge=-1, le=1)
    temp_stress_index: float = Field(0.0, ge=0, le=1)
    voltage_deviation: float = Field(0.0)
    oem_encoded: int = Field(0, ge=0)
    model_encoded: int = Field(0, ge=0)


class RULRequest(BaseSchema):
    """Input features for Remaining Useful Life prediction (Module A — Random Forest / GradientBoosting)."""
    odometer: float = Field(12000.0, ge=0)
    soc_at_charge: float = Field(85.0, ge=0, le=100)
    mile_avg: float = Field(88.0, ge=0)
    miles_per_charge: float = Field(95.0, ge=0)
    days_in_service: float = Field(180.0, ge=1)
    degradation_factor: float = Field(0.0, ge=-1, le=1)
    soh_mean: float = Field(85.0, ge=0, le=120)
    miles_per_charge_rolling_3: float = Field(92.0, ge=0)
    miles_per_charge_rolling_5: float = Field(90.0, ge=0)
    miles_per_charge_rolling_10: float = Field(88.0, ge=0)
    oem_encoded: int = Field(0, ge=0)
    model_encoded: int = Field(0, ge=0)


class MileageRequest(BaseSchema):
    """Input features for Mileage per Charge prediction (Module A — XGBoost)."""
    run_kms: float = Field(45.0, ge=0)
    avg_speed: float = Field(32.0, ge=0, le=200)
    max_speed: float = Field(55.0, ge=0, le=200)
    trip_duration_hrs: float = Field(1.5, ge=0)
    stoppage_count: int = Field(2, ge=0)
    energy_efficiency: float = Field(0.88, ge=0)
    trip_intensity: float = Field(1.2, ge=0)
    speed_ratio: float = Field(0.58, ge=0, le=1)
    stoppage_density: float = Field(0.05, ge=0)
    energy_utilized: float = Field(8.5, ge=0)
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
#  MODULE C — REQUEST SCHEMAS (BA-BMS & Knee)
# ──────────────────────────────────────────────

class DriverBehaviorRequest(BaseSchema):
    """Input parameters for Driver Aggressiveness Index (AI) and Battery Stress Index (BSI)."""
    harsh_accel_count: float = Field(0.0, ge=0, description="Count of harsh acceleration events in trip/window")
    harsh_brake_count: float = Field(0.0, ge=0, description="Count of harsh braking events")
    harsh_corner_count: float = Field(0.0, ge=0, description="Count of aggressive cornering maneuvers")
    speed_variance: float = Field(5.0, ge=0, description="Standard deviation of vehicle speed (km/h)")
    avg_speed: float = Field(35.0, ge=0, le=150, description="Average trip speed (km/h)")
    max_speed: float = Field(65.0, ge=0, le=200, description="Peak vehicle speed (km/h)")
    overspeed_count: float = Field(0.0, ge=0, description="Occurrences of exceeding speed limits")
    battery_temp_max: float = Field(35.0, ge=-20, le=120, description="Peak battery temperature reached (°C)")
    max_discharge_current: float = Field(25.0, description="Maximum discharge current peak in Amperes")
    voltage_variance: float = Field(1.2, ge=0, description="Cell voltage variance during acceleration")
    soc_drain_rate: float = Field(0.65, ge=0, description="SOC drain percentage per kilometer (%/km)")


class KneePredictionRequest(BaseSchema):
    """Telemetry and battery cycle input for Knee-Point RUL Prognostics."""
    charge_cycle_count: float = Field(..., ge=0, description="Cumulative battery full charge cycles")
    capacity: Optional[float] = Field(95.0, ge=0, description="Current estimated capacity (Ah)")
    voltage: Optional[float] = Field(74.0, ge=20, le=150, description="Battery pack voltage (V)")
    battery_temp: Optional[float] = Field(32.0, ge=-20, le=120, description="Battery temperature (°C)")
    current: Optional[float] = Field(-18.0, description="Battery current (A, negative=discharge)")
    soc: Optional[float] = Field(80.0, ge=0, le=100, description="Current State of Charge (%)")
    speed: Optional[float] = Field(35.0, ge=0, le=150, description="Vehicle speed (km/h)")
    run_kms: Optional[float] = Field(50.0, ge=0, description="Trip distance covered (km)")
    energy_kwh: Optional[float] = Field(8.5, ge=0, description="Energy consumed (kWh)")


class MetaEnsembleRequest(BaseSchema):
    """Multi-target input for simultaneous SOH and Knee RUL estimation."""
    vehicle_id: str = Field("GJ05CV6564", description="Vehicle registration identifier")
    charge_cycle_count: float = Field(..., ge=0)
    battery_voltage: float = Field(..., ge=20, le=150)
    battery_temp: float = Field(..., ge=-20, le=120)
    battery_current: float = Field(...)
    soc: float = Field(..., ge=0, le=100)
    harsh_accel_count: float = Field(0.0, ge=0)
    speed_variance: float = Field(5.0, ge=0)


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


class DriverBehaviorResponse(BaseSchema):
    """Response for Driver Aggressiveness Index (AI) and Battery Stress Index (BSI)."""
    aggressiveness_index: float
    battery_stress_index: float
    driver_classification: str
    annual_soh_penalty_percent: float
    behavioral_impact_description: str
    bms_recommended_directive: str
    sub_scores: Dict[str, float] = {}


class KneePredictionResponse(BaseSchema):
    """Response for Knee-Point Degradation Prognostics."""
    current_cycle_count: float
    rul_to_knee_cycles: float
    estimated_knee_cycle: float
    knee_risk_state: str
    recommended_action: str
    model_used: str


class MetaEnsembleResponse(BaseSchema):
    """Response for Multi-Target Meta-Ensemble estimation."""
    vehicle_id: str
    estimated_soh: float
    rul_to_knee_cycles: float
    driver_aggressiveness_index: float
    battery_stress_index: float
    health_status: str
    ensemble_architecture: str


class HealthStatusResponse(BaseSchema):
    """Response for system health status endpoint."""
    status: str = "ok"
    module_a_models: Dict[str, bool] = {}
    module_b_engine: bool = False
    module_c_engine: bool = False
    message: str = ""

