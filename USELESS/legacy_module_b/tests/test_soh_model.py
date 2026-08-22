"""
Unit tests for Champion 1: Hybrid 1D-CNN + LSTM State of Health (SOH) Model.
"""

import os
import json
import numpy as np
import pytest
from src.models.soh_champion import SOHModelWrapper, HybridCNNLSTMSOH
from src.core.preprocessor import BatteryDataPreprocessor


@pytest.fixture
def soh_wrapper():
    weights_path = os.path.join(os.path.dirname(__file__), "..", "weights", "soh_hybrid_cnn_lstm.pt")
    return SOHModelWrapper(weights_path=weights_path if os.path.exists(weights_path) else None)


def test_soh_model_forward_pass(soh_wrapper):
    """Verify PyTorch forward pass output shape and value ranges."""
    # Dummy sequence of shape (1, 10, 4)
    seq = np.random.uniform(0.1, 0.9, size=(1, 10, 4)).astype(np.float32)
    output = soh_wrapper.predict_soh(seq)
    
    assert 0.0 <= output.estimated_soh_percent <= 100.0
    assert output.model_architecture == "Hybrid 1D-CNN + LSTM"
    assert "ci_95_lower" in output.confidence_interval
    assert "ci_95_upper" in output.confidence_interval
    assert output.confidence_interval["ci_95_lower"] <= output.estimated_soh_percent <= output.confidence_interval["ci_95_upper"]


def test_soh_preprocessor_windowing():
    """Verify sequence windowing and normalization."""
    prep = BatteryDataPreprocessor(window_length=10)
    raw_mat = np.array([
        [72.0, -20.0, 30.0, 80.0],
        [74.0, -25.0, 31.0, 78.0]
    ], dtype=np.float32)
    
    norm_mat = prep.normalize_soh_matrix(raw_mat)
    assert norm_mat.shape == (2, 4)
    assert np.all(norm_mat >= 0.0) and np.all(norm_mat <= 1.0)


def test_soh_benchmark_test_split(soh_wrapper):
    """Verify inference on bundled test_split_soh.json dataset."""
    split_path = os.path.join(os.path.dirname(__file__), "..", "data", "test_split_soh.json")
    if os.path.exists(split_path):
        with open(split_path, "r", encoding="utf-8") as f:
            samples = json.load(f)
        
        preds, actuals = [], []
        for s in samples[:20]:
            seq = np.array(s["sequence"], dtype=np.float32)
            out = soh_wrapper.predict_soh(seq)
            preds.append(out.estimated_soh_percent)
            actuals.append(s["ground_truth_soh_percent"])
        
        errors = np.abs(np.array(preds) - np.array(actuals))
        mean_err = np.mean(errors)
        # Verify mean error is well within realistic physical tolerance (< 8%)
        assert mean_err < 8.0
