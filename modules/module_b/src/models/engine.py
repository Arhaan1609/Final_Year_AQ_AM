"""
Unified BatteryIQ Dual-Pillar Diagnostic Engine.
Coordinates Champion 1 (Hybrid CNN-LSTM) and Champion 2 (Multi-Zone Random Forest).
"""

import time
import os
import yaml
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np

from ..core.schemas import (
    VehicleTelemetryPacket,
    MultiZoneThermalInput,
    SOHSequenceInput,
    SOHPredictionOutput,
    ThermalSafetyOutput,
    VehicleDiagnosticReport,
    BatchDiagnosticRequest,
    BatchDiagnosticResponse,
)
from ..core.preprocessor import BatteryDataPreprocessor
from .soh_champion import SOHModelWrapper
from .thermal_champion import MultiZoneThermalRandomForest

# Absolute path to the module_b root (modules/module_b/) — works regardless of cwd
_MODULE3_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class BatteryIQEngine:
    """
    Main Production Engine for Battery Health & Thermal Management.
    """
    def __init__(self, config_path: Optional[str] = None):
        # Default config path resolves relative to module_b root
        if config_path is None:
            config_path = os.path.join(_MODULE3_ROOT, "config", "settings.yaml")
        self.config = self._load_config(config_path)
        self.preprocessor = BatteryDataPreprocessor(
            window_length=self.config.get("models", {}).get("soh", {}).get("input_window_length", 10)
        )
        
        # Paths from resolved config
        soh_weights = self.config.get("models", {}).get("soh", {}).get("weights_path", os.path.join(_MODULE3_ROOT, "weights", "soh_hybrid_cnn_lstm.pt"))
        thermal_weights = self.config.get("models", {}).get("thermal", {}).get("weights_path", os.path.join(_MODULE3_ROOT, "weights", "thermal_rf_multizone.joblib"))
        
        # Initialize Champion Models
        self.soh_model = SOHModelWrapper(weights_path=soh_weights)
        self.thermal_model = MultiZoneThermalRandomForest(weights_path=thermal_weights)

    def _load_config(self, path: Optional[str]) -> Dict[str, Any]:
        default_config = {
            "models": {
                "soh": {
                    "weights_path": os.path.join(_MODULE3_ROOT, "weights", "soh_hybrid_cnn_lstm.pt"),
                    "input_window_length": 10,
                },
                "thermal": {
                    "weights_path": os.path.join(_MODULE3_ROOT, "weights", "thermal_rf_multizone.joblib")
                }
            }
        }
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f) or {}
                # Resolve relative weight paths in config to module3 root
                for model_key in ["soh", "thermal"]:
                    wp = loaded.get("models", {}).get(model_key, {}).get("weights_path", "")
                    if wp and not os.path.isabs(wp):
                        loaded["models"][model_key]["weights_path"] = os.path.join(_MODULE3_ROOT, wp)
                return loaded
            except Exception:
                return default_config
        return default_config

    def diagnose_packet(self, packet: VehicleTelemetryPacket) -> VehicleDiagnosticReport:
        """
        Execute unified dual-pillar diagnosis on a single incoming vehicle telemetry packet.
        """
        # 1. Thermal Safety Evaluation
        thermal_vector = self.preprocessor.telemetry_to_thermal_vector(packet)
        thermal_eval = self.thermal_model.evaluate_vector(thermal_vector)

        # 2. SOH Estimation (Single packet expanded to sequence with temporal context)
        soh_seq = self.preprocessor.packets_to_soh_sequence([packet])
        soh_eval = self.soh_model.predict_soh(soh_seq)

        # 3. Overall Composite Health Index (0-100)
        # SOH contributes 65%, Thermal stability contributes 35%
        thermal_penalty = 35.0 if thermal_eval.is_critical else (thermal_eval.risk_probability * 15.0)
        overall_score = float(np.clip((soh_eval.estimated_soh_percent * 0.65) + (35.0 - thermal_penalty), 0.0, 100.0))

        # 4. Fleet Operating Mode
        if thermal_eval.is_critical:
            mode = "Immediate Maintenance / Active Throttling"
        elif overall_score < 75.0:
            mode = "Restricted Fast Charging"
        else:
            mode = "Optimal Autonomous Operation"

        return VehicleDiagnosticReport(
            vehicle_id=packet.vehicle_id,
            timestamp=packet.timestamp,
            overall_health_score=round(overall_score, 1),
            soh_evaluation=soh_eval,
            thermal_evaluation=thermal_eval,
            fleet_operating_mode=mode,
            digital_twin_sync_status="Synchronized (Edge-Cloud Twin Active)"
        )

    def predict_soh_sequence(self, input_seq: SOHSequenceInput) -> SOHPredictionOutput:
        """Direct SOH evaluation for chronological charge cycle sequences."""
        matrix = np.array(input_seq.sequence, dtype=np.float32)
        norm_matrix = self.preprocessor.normalize_soh_matrix(matrix)
        return self.soh_model.predict_soh(norm_matrix)

    def predict_thermal_vector(self, thermal_input: MultiZoneThermalInput) -> ThermalSafetyOutput:
        """Direct Thermal safety evaluation for multi-zone vectors."""
        vector = self.preprocessor.direct_thermal_to_vector(thermal_input)
        return self.thermal_model.evaluate_vector(vector)

    def diagnose_batch(self, request: BatchDiagnosticRequest) -> BatchDiagnosticResponse:
        """Batch diagnosis of multiple fleet packets with performance timing."""
        start_t = time.perf_counter()
        reports = []
        critical_count = 0

        for pkt in request.packets:
            rep = self.diagnose_packet(pkt)
            if rep.thermal_evaluation.is_critical:
                critical_count += 1
            reports.append(rep)

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return BatchDiagnosticResponse(
            total_processed=len(reports),
            critical_alerts_count=critical_count,
            reports=reports,
            execution_time_ms=round(elapsed_ms, 2)
        )
