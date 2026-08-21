# MODULE 3: BATTERY HEALTH & THERMAL MANAGEMENT 🔋⚡
### Cyber-Physical Battery State of Health (SOH) & Multi-Zone Thermal Fault Management System (TMS)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Hybrid%20CNN--LSTM-EE4C2C.svg)](https://pytorch.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-Multi--Zone%20RF-F7931E.svg)](https://scikit-learn.org/)

---

## 🌟 Executive Overview

**Module 3: Battery Health & Thermal Management** is the core battery intelligence package trained and validated on **53,476,634 real-world telematics records** from commercial EV fleets.

The package contains the **2 Proven Champion Machine Learning Models**:

1. 🧠 **Domain 1: Battery State of Health (SOH) Estimation**
   * **Champion Architecture:** **Hybrid 1D-CNN + LSTM Neural Network**
   * **Performance:** **$5.29\%$ Benchmark RMSE** ($3.64\%$ test error) on chronological Euler HiLoad fleet data.
   * **Mechanism:** 1D-CNN extracts spatial curve features, while 2-layer LSTM captures chemical capacity fade across charge cycles.

2. 🔥 **Domain 2: Thermal Management & Fault Safety (TMS)**
   * **Champion Architecture:** **Multi-Zone Random Forest Classifier (200 Trees)**
   * **Performance:** **$0.997$ F1-Score ($99.71\%$ Accuracy)** on the 50/50 balanced fleet alert dataset.
   * **Mechanism:** Concurrently monitors **Battery Temp (`vbt`)**, **Controller Temp (`vct`)**, and **Motor Temp (`vmt`)** to identify cross-zone drivetrain overheating before battery pack thermal runaway.

---

## 📁 Package Layout

```
MODULE_3_BATTERY_HEALTH_AND_THERMAL_MANAGEMENT/
├── README.md                             # Package overview & quickstart
├── INTEGRATION_GUIDE.md                  # Python in-process SDK integration handbook
├── ARCHITECTURE.md                       # Deep technical dive on Cyber-Physical System & Math
├── requirements.txt                      # Core ML dependencies (torch, scikit-learn, etc.)
├── prepare_artifacts.py                  # Reproducible dataset & weight builder
├── config/
│   └── settings.yaml                     # Model thresholds and feature definitions
├── data/                                 # 📦 BUNDLED DATASETS & MANIFESTS
│   ├── DATA_MANIFEST.md                  # Detailed data dictionary & transformation lineage
│   ├── raw_source_audit.json             # Audit of 8 raw fleet files (50M+ records)
│   ├── thermal_alerts_balanced_50_50.csv # 50/50 Balanced Alert Dataset (10,314 rows)
│   ├── thermal_alerts_balanced_50_50.parquet # Fast Parquet format of the balanced dataset
│   ├── soh_timeseries_euler_processed.parquet # Processed Euler HiLoad SOH time-series
│   ├── soh_timeseries_euler_sample.json  # Sample JSON sequence for SOH demonstration
│   ├── multizone_fleet_stream_sample.json# Multi-zone streaming telemetry packets
│   ├── test_split_soh.json               # SOH test evaluation split
│   └── test_split_thermal.json           # Thermal test evaluation split (2,063 samples)
├── weights/                              # 🧠 SERIALIZED CHAMPION WEIGHTS
│   ├── soh_hybrid_cnn_lstm.pt            # Pretrained PyTorch weights for Champion 1
│   ├── thermal_rf_multizone.joblib       # Pretrained Random Forest model for Champion 2
│   └── scalers.joblib                    # Normalization bounds
├── notebooks/                            # 📓 ORIGINAL MASTER JUPYTER NOTEBOOKS
│   ├── Battery_Health_TMS_Replication_3_2.ipynb # V3.2 Master Thermal Notebook
│   ├── Battery_Health_TMS_Replication_3.ipynb   # V3 Master SOH Notebook
│   ├── Battery_Health_TMS_Replication_2.ipynb   # V2 Scale-Up Notebook
│   └── Battery_Health_TMS_Replication.ipynb     # V1 Baseline Notebook
├── src/                                  # ⚙️ MODULAR PYTHON SOURCE CODE
│   ├── core/                             # Schemas, preprocessor, and exceptions
│   ├── models/                           # SOH champion, Thermal champion, and unified engine
│   └── cli/                              # Command-line interface tool
└── tests/                                # 🧪 AUTOMATED TEST SUITE
    ├── test_schemas.py                   # Pydantic schema validation tests
    ├── test_soh_model.py                 # SOH model inference & metric tests
    ├── test_thermal_model.py             # Thermal fault detection on 50/50 test set
    └── test_engine.py                    # Unified in-process engine tests
```

---

## 🚀 Quickstart: Python Integration

```python
from src.models.engine import BatteryIQEngine
from src.core.schemas import VehicleTelemetryPacket

# Initialize the engine
engine = BatteryIQEngine(config_path="config/settings.yaml")

# Run inference on a vehicle telemetry packet
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
print(f"SOH: {report.soh_evaluation.estimated_soh_percent}%")
print(f"Thermal Status: {report.thermal_evaluation.safety_status}")
```

---

## 💻 CLI Usage

```bash
# 1. Run benchmark validation on official test splits
python -m src.cli.main benchmark

# 2. Batch diagnose a telemetry file
python -m src.cli.main diagnose --file data/multizone_fleet_stream_sample.json
```

---

## 🧪 Running Automated Tests

```bash
pytest tests -v
```
