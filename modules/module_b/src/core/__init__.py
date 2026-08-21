"""
Core schemas, preprocessors, and exception classes for BatteryIQ.
"""

from .schemas import (
    VehicleTelemetryPacket,
    MultiZoneThermalInput,
    SOHSequenceInput,
    SOHPredictionOutput,
    ThermalSafetyOutput,
    VehicleDiagnosticReport,
    BatchDiagnosticRequest,
    BatchDiagnosticResponse,
)
from .preprocessor import BatteryDataPreprocessor
from .exceptions import (
    BatteryIQException,
    ModelNotLoadedException,
    InvalidTelemetryException,
    DataProcessingException,
)

__all__ = [
    "VehicleTelemetryPacket",
    "MultiZoneThermalInput",
    "SOHSequenceInput",
    "SOHPredictionOutput",
    "ThermalSafetyOutput",
    "VehicleDiagnosticReport",
    "BatchDiagnosticRequest",
    "BatchDiagnosticResponse",
    "BatteryDataPreprocessor",
    "BatteryIQException",
    "ModelNotLoadedException",
    "InvalidTelemetryException",
    "DataProcessingException",
]
