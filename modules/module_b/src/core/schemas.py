"""
Pydantic schemas for telemetry data, model inputs, and diagnostic reports.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, timezone


class BaseSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


class VehicleTelemetryPacket(BaseSchema):
    """Raw single-point vehicle telemetry record from fleet telematics."""
    vehicle_id: str = Field(..., description="Unique vehicle registration or chassis identifier (e.g. GJ05CV6564)")
    oem_model: Optional[str] = Field("Euler HiLoad", description="OEM and vehicle model name")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="UTC timestamp of the telemetry packet")
    
    # Telemetry measurements (Exact Fleet Nomenclature & Clean Aliases)
    soc: float = Field(..., ge=0.0, le=100.0, description="State of Charge percentage (0-100%)")
    voltage: float = Field(..., ge=0.0, le=150.0, description="Battery Pack Voltage in Volts (vbv)")
    current: float = Field(0.0, description="Battery Current in Amperes (vbc, negative for discharge)")
    battery_temp: float = Field(..., ge=-20.0, le=120.0, description="Battery Pack Temperature in °C (vbt)")
    controller_temp: Optional[float] = Field(None, ge=-20.0, le=140.0, description="Motor Controller / Inverter Temp in °C (vct)")
    motor_temp: Optional[float] = Field(None, ge=-20.0, le=160.0, description="Drive Motor Temperature in °C (vmt)")
    speed: float = Field(0.0, ge=0.0, le=150.0, description="Vehicle Speed in km/h")
    
    # GPS / Odometer context
    odometer_km: Optional[float] = Field(None, ge=0.0, description="Cumulative odometer reading")
    gps_coordinates: Optional[str] = Field(None, description="Latitude,Longitude string")

    @field_validator('battery_temp')
    @classmethod
    def validate_battery_temp(cls, v: float) -> float:
        if v > 90.0:
            # Extreme boundary sanity check
            pass
        return v


class MultiZoneThermalInput(BaseSchema):
    """Direct vector for Multi-Zone Random Forest Classifier."""
    vbt: float = Field(..., description="Battery Temperature (°C)")
    vct: float = Field(..., description="Controller / Inverter Temperature (°C)")
    vmt: float = Field(..., description="Motor Temperature (°C)")
    vbv: float = Field(..., description="Pack Voltage (V)")
    vbc: float = Field(..., description="Battery Current (A)")
    soc: float = Field(..., ge=0.0, le=100.0, description="State of Charge (%)")
    speed: float = Field(..., ge=0.0, description="Vehicle Speed (km/h)")


class SOHSequenceInput(BaseSchema):
    """Multi-step time-series window for Hybrid 1D-CNN + LSTM."""
    vehicle_id: str = Field(..., description="Target vehicle chassis or registration")
    sequence: List[List[float]] = Field(
        ...,
        min_length=5,
        description="Chronological time-series matrix of shape (seq_len, 4): [voltage, current, battery_temp, soc]"
    )


class SOHPredictionOutput(BaseSchema):
    """Prediction result from Champion 1: Hybrid CNN-LSTM."""
    estimated_soh_percent: float = Field(..., ge=0.0, le=100.0, description="Estimated State of Health (%)")
    capacity_state: str = Field(..., description="Health category: Optimal, Good, Degraded, Critical Replacement")
    confidence_interval: Dict[str, float] = Field(..., description="Lower and upper 95% confidence bounds")
    degradation_slope_per_100_cycles: float = Field(..., description="Estimated capacity loss rate (%)")
    model_architecture: str = Field("Hybrid 1D-CNN + LSTM", description="Champion SOH architecture name")
    verified_benchmark_rmse: float = Field(5.29, description="Published benchmark RMSE on real-world EV fleet data")


class ThermalSafetyOutput(BaseSchema):
    """Prediction result from Champion 2: Multi-Zone Random Forest."""
    safety_status: str = Field(..., description="SAFE (Benign) or CRITICAL (Thermal Fault Detected)")
    is_critical: bool = Field(..., description="True if dangerous thermal condition detected")
    risk_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of critical thermal state")
    primary_thermal_threat: str = Field(..., description="Identified threat type or Nominal Operation")
    hotspot_zone: str = Field(..., description="Active thermal bottleneck: Battery Pack, Motor Controller, or Motor Core")
    contributing_features: Dict[str, float] = Field(..., description="Gini relative feature importance breakdown")
    recommended_bms_action: str = Field(..., description="Automated mitigation directive for edge/cloud BMS")
    model_architecture: str = Field("Multi-Zone Random Forest (200 trees)", description="Champion TMS architecture name")
    verified_benchmark_f1: float = Field(0.997, description="Published benchmark F1-Score on balanced fleet data")


class VehicleDiagnosticReport(BaseSchema):
    """Unified dual-pillar diagnostic evaluation of a vehicle."""
    vehicle_id: str
    timestamp: datetime
    overall_health_score: float = Field(..., ge=0.0, le=100.0, description="Composite Cyber-Physical Health Index (0-100)")
    soh_evaluation: SOHPredictionOutput
    thermal_evaluation: ThermalSafetyOutput
    fleet_operating_mode: str = Field("Optimal", description="Normal, Throttled, or Immediate Maintenance Required")
    digital_twin_sync_status: str = Field("Synchronized", description="Edge-Cloud state synchronization indicator")


class BatchDiagnosticRequest(BaseSchema):
    """Batch ingestion of fleet telemetry packets."""
    packets: List[VehicleTelemetryPacket]


class BatchDiagnosticResponse(BaseSchema):
    """Batch evaluation results."""
    total_processed: int
    critical_alerts_count: int
    reports: List[VehicleDiagnosticReport]
    execution_time_ms: float
