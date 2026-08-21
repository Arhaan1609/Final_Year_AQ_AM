"""
Data preprocessing, feature normalization, and temporal sequence windowing.
"""

import numpy as np
from typing import List, Tuple, Dict, Any
from .schemas import VehicleTelemetryPacket, MultiZoneThermalInput
from .exceptions import DataProcessingException, InvalidTelemetryException


class BatteryDataPreprocessor:
    """
    Production preprocessor implementing the exact scaling and feature extraction
    pipelines established in master notebooks V3 and V3.2.
    """
    
    # Feature order for SOH 1D-CNN + LSTM
    SOH_FEATURE_COLS = ["voltage", "current", "battery_temp", "soc"]
    
    # Feature order for Multi-Zone Random Forest
    THERMAL_FEATURE_COLS = ["vbt", "vct", "vmt", "vbv", "vbc", "soc", "speed"]
    
    # Normalization bounds (Derived from 20.5M Euler HiLoad telemetry statistics)
    SOH_SCALER_MIN = np.array([40.0, -120.0, -10.0, 0.0])
    SOH_SCALER_MAX = np.array([120.0, 100.0, 60.0, 100.0])

    def __init__(self, window_length: int = 10):
        self.window_length = window_length

    def normalize_soh_matrix(self, matrix: np.ndarray) -> np.ndarray:
        """
        MinMax normalization for SOH neural network input.
        matrix shape: (seq_len, 4) or (batch, seq_len, 4)
        """
        try:
            span = self.SOH_SCALER_MAX - self.SOH_SCALER_MIN
            span = np.where(span == 0, 1.0, span)
            normalized = (matrix - self.SOH_SCALER_MIN) / span
            return np.clip(normalized, 0.0, 1.0)
        except Exception as e:
            raise DataProcessingException(f"Failed to normalize SOH sequence: {str(e)}")

    def denormalize_soh(self, norm_soh: float) -> float:
        """Denormalize SOH percentage output to 0-100 range."""
        return float(np.clip(norm_soh * 100.0, 0.0, 100.0))

    def telemetry_to_thermal_vector(self, packet: VehicleTelemetryPacket) -> np.ndarray:
        """
        Convert high-level telemetry packet into Multi-Zone Random Forest feature vector.
        Vector layout: [vbt, vct, vmt, vbv, vbc, soc, speed]
        """
        try:
            # Multi-zone fallback: if motor/controller temp is missing, estimate based on thermal conduction
            vbt = float(packet.battery_temp)
            vct = float(packet.controller_temp) if packet.controller_temp is not None else vbt + 8.0
            vmt = float(packet.motor_temp) if packet.motor_temp is not None else vbt + 15.0
            vbv = float(packet.voltage)
            vbc = float(packet.current)
            soc = float(packet.soc)
            speed = float(packet.speed)

            vector = np.array([vbt, vct, vmt, vbv, vbc, soc, speed], dtype=np.float32)
            return vector.reshape(1, -1)
        except Exception as e:
            raise DataProcessingException(f"Error converting telemetry to thermal vector: {str(e)}")

    def direct_thermal_to_vector(self, inp: MultiZoneThermalInput) -> np.ndarray:
        """Convert MultiZoneThermalInput to (1, 7) numpy array."""
        vector = np.array([inp.vbt, inp.vct, inp.vmt, inp.vbv, inp.vbc, inp.soc, inp.speed], dtype=np.float32)
        return vector.reshape(1, -1)

    def packets_to_soh_sequence(self, packets: List[VehicleTelemetryPacket]) -> np.ndarray:
        """
        Convert chronologically ordered packets into shape (1, seq_len, 4).
        If packets < window_length, pad with the oldest packet.
        """
        if not packets:
            raise InvalidTelemetryException("Cannot construct SOH sequence from empty packet list.")

        raw_rows = []
        for p in packets:
            raw_rows.append([p.voltage, p.current, p.battery_temp, p.soc])

        raw_mat = np.array(raw_rows, dtype=np.float32)

        # Handle window length
        if len(raw_mat) < self.window_length:
            pad_count = self.window_length - len(raw_mat)
            padding = np.repeat(raw_mat[:1], pad_count, axis=0)
            raw_mat = np.vstack([padding, raw_mat])
        elif len(raw_mat) > self.window_length:
            raw_mat = raw_mat[-self.window_length:]

        normalized_mat = self.normalize_soh_matrix(raw_mat)
        return np.expand_dims(normalized_mat, axis=0)  # Shape: (1, window_length, 4)
