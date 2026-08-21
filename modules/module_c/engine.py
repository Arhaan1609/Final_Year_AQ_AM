"""
modules/module_c/engine.py — Unified Behavior-Aware BMS (BA-BMS) & Knee-Point Prognostics Engine.

Core Capabilities:
  1. Driver Aggressiveness Index (AI) & Battery Stress Index (BSI) computation.
  2. Battery Degradation Knee-Point Prognostics (XGBoost Booster + StandardScaler).
  3. Behavioral impact mapping & mitigation directives.
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
import xgboost as xgb
from typing import Dict, Any, Optional, List, Tuple

_MODULE_C_ROOT = os.path.dirname(os.path.abspath(__file__))

KNEE_FEATURE_NAMES = [
    'charge_cycle_count', 'oem_encoded', 'model_encoded', 'capacity',
    'smoothed_capacity', 'delta_capacity', 'rolling_mean_capacity',
    'rolling_slope', 'degradation_rate', 'battery_voltage_smooth_mean',
    'battery_voltage_smooth_min', 'battery_voltage_smooth_max',
    'battery_voltage_smooth_std', 'battery_current_mean',
    'battery_current_min', 'battery_current_max',
    'battery_temp_smooth_mean', 'battery_temp_smooth_max',
    'dQ_dV_mean', 'dQ_dV_std', 'soc_min', 'soc_max', 'run_kms',
    'energy_utilized', 'avg_speed', 'max_speed', 'driving_intensity',
    'soc_drain'
]


class BABMSEngine:
    """
    Production Engine for Module C:
      - Driver Behavior Modeling (Aggressiveness Index & Battery Stress Index)
      - Knee-Point Remaining Useful Life Prognostics
    """
    def __init__(self, model_path: Optional[str] = None, scaler_path: Optional[str] = None):
        self.model_path = model_path or os.path.join(_MODULE_C_ROOT, "best_xgboost_model.json")
        self.scaler_path = scaler_path or os.path.join(_MODULE_C_ROOT, "feature_scaler.pkl")
        
        self.booster: Optional[xgb.Booster] = None
        self.scaler = None
        self.is_loaded = False

        self._load_artifacts()

    def _load_artifacts(self):
        """Load pretrained XGBoost booster and StandardScaler."""
        try:
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)

            if os.path.exists(self.model_path):
                self.booster = xgb.Booster()
                self.booster.load_model(self.model_path)

            if self.booster is not None and self.scaler is not None:
                self.is_loaded = True
        except Exception as e:
            print(f"  [WARNING] BABMSEngine failed to load artifacts: {e}")
            self.is_loaded = False

    # ─────────────────────────────────────────────────────────────
    #  1. DRIVER AGGRESSIVENESS & BATTERY STRESS (BA-BMS)
    # ─────────────────────────────────────────────────────────────
    def compute_behavior_indices(
        self,
        harsh_accel_count: float = 0.0,
        harsh_brake_count: float = 0.0,
        harsh_corner_count: float = 0.0,
        speed_variance: float = 5.0,
        avg_speed: float = 35.0,
        max_speed: float = 65.0,
        overspeed_count: float = 0.0,
        battery_temp_max: float = 35.0,
        max_discharge_current: float = 25.0,
        voltage_variance: float = 1.2,
        soc_drain_rate: float = 0.65,
    ) -> Dict[str, Any]:
        """
        Compute Driver Aggressiveness Index (AI) and Battery Stress Index (BSI).
        
        AI (0.0 to 1.0): Driver aggression ranking based on behavioral events.
        BSI (0.0 to 1.0): Cell-level physical strain caused by driving style.
        """
        # --- Aggressiveness Index (AI) ---
        # Weighted normalized components
        norm_accel = min(1.0, harsh_accel_count / 10.0)
        norm_brake = min(1.0, harsh_brake_count / 10.0)
        norm_corner = min(1.0, harsh_corner_count / 8.0)
        norm_speed_var = min(1.0, speed_variance / 25.0)
        norm_kinetic = min(1.0, (avg_speed ** 2) / (70.0 ** 2))
        norm_overspeed = min(1.0, overspeed_count / 5.0)

        ai_score = (
            0.25 * norm_accel +
            0.20 * norm_brake +
            0.15 * norm_corner +
            0.15 * norm_speed_var +
            0.15 * norm_kinetic +
            0.10 * norm_overspeed
        )
        ai_score = float(np.clip(round(ai_score, 4), 0.0, 1.0))

        # Classify driver profile
        if ai_score <= 0.35:
            driver_class = "Smooth & Energy-Conscious"
            soh_impact_desc = "Optimal driving style: preserves battery lifecycle (+4.7% SOH retention)."
            soh_penalty_pct = 0.0
        elif ai_score <= 0.65:
            driver_class = "Moderate Fleet Standard"
            soh_impact_desc = "Nominal fleet driving: expected baseline degradation."
            soh_penalty_pct = 1.8
        else:
            driver_class = "Aggressive / High Stress"
            soh_impact_desc = "Aggressive driving style: accelerated capacity loss (~4.7% faster SOH fade)."
            soh_penalty_pct = 4.7

        # --- Battery Stress Index (BSI) ---
        temp_strain = max(0.0, (battery_temp_max - 32.0) / 25.0)
        current_strain = min(1.0, abs(max_discharge_current) / 80.0)
        voltage_strain = min(1.0, voltage_variance / 5.0)
        drain_strain = min(1.0, soc_drain_rate / 1.5)

        bsi_score = (
            0.35 * temp_strain +
            0.30 * current_strain +
            0.20 * voltage_strain +
            0.15 * drain_strain
        )
        bsi_score = float(np.clip(round(bsi_score, 4), 0.0, 1.0))

        # Mitigation directive
        if bsi_score >= 0.70:
            directive = "CRITICAL STRESS: Immediate power throttling recommended to prevent cell thermal overshoot."
        elif bsi_score >= 0.40:
            directive = "ELEVATED STRESS: Limit consecutive fast charges and avoid sustained high-current discharges."
        else:
            directive = "NORMAL: Battery operates within optimal thermodynamic and electrical limits."

        return {
            "aggressiveness_index": ai_score,
            "battery_stress_index": bsi_score,
            "driver_classification": driver_class,
            "annual_soh_penalty_percent": soh_penalty_pct,
            "behavioral_impact_description": soh_impact_desc,
            "bms_recommended_directive": directive,
            "sub_scores": {
                "harsh_acceleration_component": round(norm_accel, 3),
                "harsh_braking_component": round(norm_brake, 3),
                "kinetic_intensity_component": round(norm_kinetic, 3),
                "thermal_strain_component": round(temp_strain, 3),
                "current_strain_component": round(current_strain, 3),
            }
        }

    # ─────────────────────────────────────────────────────────────
    #  2. KNEE-POINT PROGNOSTICS (XGBOOST BOOSTER)
    # ─────────────────────────────────────────────────────────────
    def predict_knee_point(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict Remaining Useful Life to the battery degradation Knee Point (RUL_to_knee).
        Uses pre-trained XGBoost model + StandardScaler on 28 features.
        """
        if not self.is_loaded:
            raise RuntimeError("Module C BABMSEngine models are not loaded.")

        # Build feature vector matching exact 28 feature schema
        raw_row = []
        for col in KNEE_FEATURE_NAMES:
            val = feature_dict.get(col, None)
            if val is None:
                # Intelligent fallbacks for missing derived features
                if col == 'charge_cycle_count': val = feature_dict.get('cycle_count', 150.0)
                elif col == 'capacity': val = feature_dict.get('capacity_ah', 95.0)
                elif col == 'smoothed_capacity': val = feature_dict.get('capacity_ah', 95.0)
                elif col == 'delta_capacity': val = -0.05
                elif col == 'rolling_mean_capacity': val = feature_dict.get('capacity_ah', 95.0)
                elif col == 'rolling_slope': val = -0.015
                elif col == 'degradation_rate': val = 0.02
                elif col == 'battery_voltage_smooth_mean': val = feature_dict.get('voltage', 74.0)
                elif col == 'battery_voltage_smooth_min': val = feature_dict.get('voltage', 74.0) - 2.0
                elif col == 'battery_voltage_smooth_max': val = feature_dict.get('voltage', 74.0) + 2.0
                elif col == 'battery_voltage_smooth_std': val = 1.2
                elif col == 'battery_current_mean': val = feature_dict.get('current', -18.0)
                elif col == 'battery_current_min': val = feature_dict.get('current', -18.0) - 10.0
                elif col == 'battery_current_max': val = 0.0
                elif col == 'battery_temp_smooth_mean': val = feature_dict.get('battery_temp', 32.0)
                elif col == 'battery_temp_smooth_max': val = feature_dict.get('battery_temp', 32.0) + 5.0
                elif col == 'dQ_dV_mean': val = 45.0
                elif col == 'dQ_dV_std': val = 8.0
                elif col == 'soc_min': val = feature_dict.get('soc', 80.0) - 30.0
                elif col == 'soc_max': val = feature_dict.get('soc', 80.0)
                elif col == 'run_kms': val = feature_dict.get('run_kms', 50.0)
                elif col == 'energy_utilized': val = feature_dict.get('energy_kwh', 8.5)
                elif col == 'avg_speed': val = feature_dict.get('speed', 35.0)
                elif col == 'max_speed': val = feature_dict.get('speed', 35.0) + 20.0
                elif col == 'driving_intensity': val = 42.0
                elif col == 'soc_drain': val = 35.0
                elif col in ('oem_encoded', 'model_encoded'): val = 0.0
                else: val = 0.0
            raw_row.append(float(val))

        X_raw = np.array([raw_row], dtype=np.float32)

        # Apply StandardScaler
        X_scaled = self.scaler.transform(X_raw)

        # XGBoost inference
        dmatrix = xgb.DMatrix(X_scaled)
        rul_pred = float(self.booster.predict(dmatrix)[0])
        rul_knee = max(0.0, round(rul_pred, 1))

        current_cycle = float(raw_row[0])
        estimated_knee_cycle = round(current_cycle + rul_knee, 1)

        # Risk state evaluation
        if rul_knee > 300:
            risk_state = "Pre-Knee Nominal (Linear Degradation Stage)"
            action = "Battery operates far prior to knee point. Standard charge/discharge cycles permitted."
        elif rul_knee > 100:
            risk_state = "Knee Proximity Warning (Transition Zone)"
            action = "Knee point approaching. Reduce fast-charging frequency and enforce cell balancing."
        else:
            risk_state = "Critical Knee Onset / Accelerated Aging"
            action = "Battery near/at accelerated aging knee. Capacity drop will compound rapidly. Service inspection required."

        return {
            "current_cycle_count": current_cycle,
            "rul_to_knee_cycles": rul_knee,
            "estimated_knee_cycle": estimated_knee_cycle,
            "knee_risk_state": risk_state,
            "recommended_action": action,
            "model_used": "XGBoost Knee Booster (28 features)",
        }
