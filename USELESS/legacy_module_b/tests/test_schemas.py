"""
Unit tests for Pydantic data schemas and boundary validation.
"""

import pytest
from pydantic import ValidationError
from src.core.schemas import (
    VehicleTelemetryPacket,
    MultiZoneThermalInput,
    SOHSequenceInput,
    SOHPredictionOutput,
    ThermalSafetyOutput,
    VehicleDiagnosticReport
)


def test_valid_telemetry_packet():
    """Verify that valid telemetry parses properly."""
    packet = VehicleTelemetryPacket(
        vehicle_id="GJ05CV6564",
        oem_model="Euler HiLoad",
        soc=85.5,
        voltage=78.2,
        current=-22.0,
        battery_temp=30.5,
        controller_temp=42.0,
        motor_temp=58.0,
        speed=35.0
    )
    assert packet.vehicle_id == "GJ05CV6564"
    assert packet.soc == 85.5
    assert packet.voltage == 78.2


def test_invalid_soc_boundary():
    """Verify that out-of-bound SoC (>100% or <0%) raises ValidationError."""
    with pytest.raises(ValidationError):
        VehicleTelemetryPacket(
            vehicle_id="FAIL-VEH",
            soc=125.0,  # Invalid
            voltage=72.0,
            battery_temp=30.0
        )

    with pytest.raises(ValidationError):
        VehicleTelemetryPacket(
            vehicle_id="FAIL-VEH",
            soc=-5.0,  # Invalid
            voltage=72.0,
            battery_temp=30.0
        )


def test_multizone_thermal_input():
    """Verify MultiZoneThermalInput vector construction."""
    mz = MultiZoneThermalInput(
        vbt=32.0,
        vct=45.0,
        vmt=62.0,
        vbv=74.0,
        vbc=-20.0,
        soc=70.0,
        speed=40.0
    )
    assert mz.vbt == 32.0
    assert mz.vmt == 62.0


def test_soh_sequence_input_validation():
    """Verify sequence validation requiring minimum length."""
    with pytest.raises(ValidationError):
        SOHSequenceInput(
            vehicle_id="FAIL-SEQ",
            sequence=[[72.0, -10.0, 30.0, 80.0]]  # Only 1 step, requires at least 5
        )
