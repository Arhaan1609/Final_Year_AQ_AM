# BatteryIQ ML Model Integration Guide 🔌⚡
### Engineering Guide for In-Process Python ML Integration

This guide provides step-by-step instructions for importing and running the BatteryIQ champion models directly in any Python codebase, telematics gateway, or data pipeline.

---

## 🚀 1. Direct Python In-Process SDK Integration

You can import the unified diagnostic engine directly into your existing scripts:

```python
from src.models.engine import BatteryIQEngine
from src.core.schemas import VehicleTelemetryPacket

# 1. Initialize the Engine (loads Champion PyTorch & Random Forest weights)
engine = BatteryIQEngine(config_path="config/settings.yaml")

# 2. Define incoming telemetry record
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

# 3. Execute Dual-Pillar ML Diagnosis
report = engine.diagnose_packet(packet)

# 4. Access Predictions
print(f"Vehicle:        {report.vehicle_id}")
print(f"Health Score:   {report.overall_health_score}/100")
print(f"SOH Prediction: {report.soh_evaluation.estimated_soh_percent}% ({report.soh_evaluation.capacity_state})")
print(f"Thermal Safety: {report.thermal_evaluation.safety_status}")
print(f"Active Hotspot: {report.thermal_evaluation.hotspot_zone}")
print(f"Recommended BMS Action: {report.thermal_evaluation.recommended_bms_action}")
```

---

## 🧠 2. Direct Access to Individual Champion Models

### A. Champion 1: SOH Hybrid 1D-CNN + LSTM
```python
import numpy as np
from src.models.soh_champion import SOHModelWrapper

# Load model with pretrained PyTorch weights
soh_model = SOHModelWrapper(weights_path="weights/soh_hybrid_cnn_lstm.pt")

# Telemetry sequence: (Window_Length=10, Features=4: [voltage, current, battery_temp, soc])
sample_sequence = np.array([
    [78.0, -15.0, 28.0, 85.0],
    [77.5, -18.0, 28.5, 84.0],
    [77.0, -20.0, 29.0, 83.0],
    [76.5, -22.0, 29.5, 82.0],
    [76.0, -20.0, 30.0, 81.0],
    [75.5, -18.0, 30.2, 80.0],
    [75.0, -19.0, 30.5, 79.0],
    [74.5, -20.0, 30.8, 78.0],
    [74.0, -21.0, 31.0, 77.0],
    [73.5, -22.0, 31.2, 76.0]
], dtype=np.float32)

soh_result = soh_model.predict_soh(sample_sequence)
print(f"Predicted SOH: {soh_result.estimated_soh_percent}%")
print(f"95% CI: [{soh_result.confidence_interval['ci_95_lower']}%, {soh_result.confidence_interval['ci_95_upper']}%]")
```

### B. Champion 2: Multi-Zone Random Forest Classifier (200 Trees)
```python
import numpy as np
from src.models.thermal_champion import MultiZoneThermalRandomForest

# Load model with pretrained joblib weights
thermal_model = MultiZoneThermalRandomForest(weights_path="weights/thermal_rf_multizone.joblib")

# Feature vector: [vbt (battery), vct (controller), vmt (motor), vbv (voltage), vbc (current), soc, speed]
feature_vector = np.array([30.0, 70.0, 98.0, 72.0, -60.0, 60.0, 25.0], dtype=np.float32)

thermal_result = thermal_model.evaluate_vector(feature_vector)
print(f"Safety Status: {thermal_result.safety_status}")
print(f"Is Critical:   {thermal_result.is_critical}")
print(f"Fault Hotspot: {thermal_result.hotspot_zone}")
print(f"Threat:        {thermal_result.primary_thermal_threat}")
```

---

## 💻 3. Command Line Interface (CLI) Execution

```bash
# 1. Run official benchmark verification on test splits
python -m src.cli.main benchmark

# 2. Diagnose a sample telemetry file
python -m src.cli.main diagnose --file data/multizone_fleet_stream_sample.json

# 3. Diagnose single vehicle telemetry directly via CLI arguments
python -m src.cli.main diagnose --vehicle-id "GJ05CV6564" --soc 82.5 --voltage 78.4 --current -18.2 --battery-temp 28.5 --motor-temp 52.0
```
