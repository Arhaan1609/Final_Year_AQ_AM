"""
modules/module_c/tests/test_c_engine.py — Unit & Integration Tests for Module C.
"""

import os
import sys
import pytest

_MOD_C_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_PROJECT_ROOT = os.path.abspath(os.path.join(_MOD_C_DIR, "..", ".."))

sys.path.insert(0, _MOD_C_DIR)
sys.path.insert(0, _PROJECT_ROOT)

from engine import BABMSEngine
from api.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def engine():
    eng = BABMSEngine()
    assert eng.is_loaded, "BABMSEngine failed to load pre-trained artifacts."
    return eng


def test_engine_load(engine):
    assert engine.is_loaded is True
    assert engine.booster is not None
    assert engine.scaler is not None


def test_driver_behavior_smooth(engine):
    res = engine.compute_behavior_indices(
        harsh_accel_count=0,
        harsh_brake_count=0,
        harsh_corner_count=0,
        speed_variance=3.0,
        avg_speed=30.0,
        max_speed=50.0,
        overspeed_count=0,
        battery_temp_max=30.0,
        max_discharge_current=15.0,
    )
    assert res["aggressiveness_index"] <= 0.35
    assert "Smooth" in res["driver_classification"]
    assert res["annual_soh_penalty_percent"] == 0.0


def test_driver_behavior_aggressive(engine):
    res = engine.compute_behavior_indices(
        harsh_accel_count=10,
        harsh_brake_count=10,
        harsh_corner_count=8,
        speed_variance=25.0,
        avg_speed=70.0,
        max_speed=110.0,
        overspeed_count=5,
        battery_temp_max=48.0,
        max_discharge_current=85.0,
    )
    assert res["aggressiveness_index"] > 0.65
    assert "Aggressive" in res["driver_classification"]
    assert res["annual_soh_penalty_percent"] > 3.0
    assert res["battery_stress_index"] > 0.60


def test_knee_prognostics(engine):
    res = engine.predict_knee_point({
        "charge_cycle_count": 150.0,
        "capacity": 96.0,
        "voltage": 74.0,
        "battery_temp": 31.0,
        "current": -15.0,
        "soc": 82.0,
        "speed": 35.0,
    })
    assert "rul_to_knee_cycles" in res
    assert res["rul_to_knee_cycles"] >= 0.0
    assert res["estimated_knee_cycle"] >= 150.0
    assert "knee_risk_state" in res


def test_api_driver_behavior_endpoint():
    with TestClient(app) as client:
        r = client.post("/predict/driver-behavior", json={
            "harsh_accel_count": 2,
            "harsh_brake_count": 1,
            "harsh_corner_count": 1,
            "speed_variance": 6.0,
            "avg_speed": 35.0,
            "max_speed": 60.0,
            "battery_temp_max": 33.0,
            "max_discharge_current": 25.0
        })
        assert r.status_code == 200
        data = r.json()
        assert "aggressiveness_index" in data
        assert "battery_stress_index" in data
        assert "driver_classification" in data


def test_api_knee_point_endpoint():
    with TestClient(app) as client:
        r = client.post("/predict/knee-point", json={
            "charge_cycle_count": 220.0,
            "capacity": 93.0,
            "voltage": 73.5,
            "battery_temp": 34.0,
            "current": -20.0,
            "soc": 76.0,
            "speed": 38.0
        })
        assert r.status_code == 200
        data = r.json()
        assert "rul_to_knee_cycles" in data
        assert "knee_risk_state" in data


def test_api_meta_ensemble_endpoint():
    with TestClient(app) as client:
        r = client.post("/predict/meta-ensemble", json={
            "vehicle_id": "TEST_EV_01",
            "charge_cycle_count": 180.0,
            "battery_voltage": 74.0,
            "battery_temp": 32.0,
            "battery_current": -18.0,
            "soc": 80.0,
            "harsh_accel_count": 2,
            "speed_variance": 5.0
        })
        assert r.status_code == 200
        data = r.json()
        assert data["vehicle_id"] == "TEST_EV_01"
        assert "estimated_soh" in data
        assert "rul_to_knee_cycles" in data
