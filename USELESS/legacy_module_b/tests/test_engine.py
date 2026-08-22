"""
Unit tests for unified BatteryIQEngine (In-Process Python SDK).
"""

import os
import pytest
from src.models.engine import BatteryIQEngine
from src.core.schemas import VehicleTelemetryPacket


@pytest.fixture
def engine():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "settings.yaml")
    return BatteryIQEngine(config_path=config_path)


def test_engine_diagnose_nominal_packet(engine):
    """Verify unified in-process diagnostic inference on nominal packet."""
    packet = VehicleTelemetryPacket(
        vehicle_id="GJ05CV6564",
        oem_model="Euler HiLoad",
        soc=82.5,
        voltage=78.4,
        current=-18.2,
        battery_temp=28.5,
        controller_temp=38.2,
        motor_temp=52.0,
        speed=34.0
    )
    report = engine.diagnose_packet(packet)
    assert report.vehicle_id == "GJ05CV6564"
    assert report.soh_evaluation.estimated_soh_percent > 0.0
    assert report.thermal_evaluation.safety_status == "SAFE (Benign)"
    assert not report.thermal_evaluation.is_critical


def test_engine_diagnose_critical_motor_packet(engine):
    """Verify unified diagnostic on critical motor overheating packet."""
    packet = VehicleTelemetryPacket(
        vehicle_id="CRIT-001",
        oem_model="Euler HiLoad",
        soc=60.0,
        voltage=72.0,
        current=-50.0,
        battery_temp=30.0,   # Safe battery
        controller_temp=70.0,
        motor_temp=98.0,     # Critical motor
        speed=25.0
    )
    report = engine.diagnose_packet(packet)
    assert report.thermal_evaluation.hotspot_zone == "Traction Motor Core"
