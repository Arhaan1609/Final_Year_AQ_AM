"""
Unit tests for Champion 2: Multi-Zone Random Forest Thermal Safety Classifier.
"""

import os
import json
import numpy as np
import pytest
from src.models.thermal_champion import MultiZoneThermalRandomForest
from src.core.schemas import MultiZoneThermalInput


@pytest.fixture
def thermal_model():
    weights_path = os.path.join(os.path.dirname(__file__), "..", "weights", "thermal_rf_multizone.joblib")
    return MultiZoneThermalRandomForest(weights_path=weights_path if os.path.exists(weights_path) else None)


def test_thermal_safe_vector(thermal_model):
    """Verify that nominal operating conditions evaluate to SAFE."""
    # [vbt, vct, vmt, vbv, vbc, soc, speed]
    safe_vec = np.array([28.0, 36.0, 48.0, 78.0, -15.0, 85.0, 30.0], dtype=np.float32)
    output = thermal_model.evaluate_vector(safe_vec)
    
    assert not output.is_critical
    assert "SAFE" in output.safety_status
    assert output.risk_probability < 0.50
    assert output.hotspot_zone == "All Zones Nominal"


def test_thermal_critical_motor_overheat(thermal_model):
    """Verify that a hot motor is flagged even if the battery pack is cool."""
    # Battery is 30°C (cool), but motor is 98°C (overheating)
    crit_motor_vec = np.array([30.0, 70.0, 98.0, 72.0, -60.0, 60.0, 25.0], dtype=np.float32)
    output = thermal_model.evaluate_vector(crit_motor_vec)
    
    assert output.hotspot_zone == "Traction Motor Core"
    assert "Motor" in output.primary_thermal_threat


def test_thermal_critical_deep_discharge(thermal_model):
    """Verify that low SoC combined with under-voltage is flagged."""
    crit_discharge_vec = np.array([45.0, 55.0, 60.0, 44.0, -40.0, 4.0, 15.0], dtype=np.float32)
    output = thermal_model.evaluate_vector(crit_discharge_vec)
    
    assert output.is_critical
    assert "Deep Discharge" in output.primary_thermal_threat or "Thermal" in output.primary_thermal_threat


def test_thermal_benchmark_test_split(thermal_model):
    """Verify accuracy on the 2,063 test samples from test_split_thermal.json."""
    split_path = os.path.join(os.path.dirname(__file__), "..", "data", "test_split_thermal.json")
    if os.path.exists(split_path):
        with open(split_path, "r", encoding="utf-8") as f:
            test_data = json.load(f)

        X_mat = []
        y_true = []
        for sample in test_data:
            feat = sample["features"]
            X_mat.append([feat["vbt"], feat["vct"], feat["vmt"], feat["vbv"], feat["vbc"], feat["soc"], feat["speed"]])
            y_true.append(sample["ground_truth_is_critical"])

        X_mat = np.array(X_mat, dtype=np.float32)
        y_true = np.array(y_true, dtype=int)
        
        preds = thermal_model.model.predict(X_mat)
        accuracy = float(np.mean(preds == y_true) * 100.0)
        # Verify accuracy matches >98% benchmark
        assert accuracy >= 98.0
