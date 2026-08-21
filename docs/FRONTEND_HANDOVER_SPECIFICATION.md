# 🔋 EV Battery Intelligence Platform — Complete Master Architecture & Frontend Handover Specification

---

## 📑 Table of Contents
1. [Executive Summary & Project Mission](#1-executive-summary--project-mission)
2. [Dataset Engineering & Telematics Architecture](#2-dataset-engineering--telematics-architecture)
3. [End-to-End Methodology: How the System Was Built](#3-end-to-end-methodology-how-the-system-was-built)
4. [The 3 Core Pillars (Modules)](#4-the-3-core-pillars-modules)
   - [Module A: Macro Fleet State Estimation (56 Models)](#module-a-macro-fleet-state-estimation-56-models)
   - [Module B: BatteryIQ Cyber-Physical & Thermal Safety (8 Models)](#module-b-batteryiq-cyber-physical--thermal-safety-8-models)
   - [Module C: Behavior-Aware BMS & Knee Prognostics (10 Models)](#module-c-behavior-aware-bms--knee-prognostics-10-models)
5. [74-Model Benchmark & Quantifiable Results](#5-74-model-benchmark--quantifiable-results)
6. [Backend Serving & Production Architecture](#6-backend-serving--production-architecture)
7. [Complete REST API Specification (11 Endpoints)](#7-complete-rest-api-specification-11-endpoints)
8. [Frontend UI/UX Design System & Component Architecture](#8-frontend-uiux-design-system--component-architecture)
9. [Verification, Retraining & Operation Guide](#9-verification-retraining--operation-guide)

---

## 1. Executive Summary & Project Mission

### 💡 The Problem
Commercial Electric Vehicle (EV) fleets—especially light commercial delivery vehicles and three-wheelers operating in extreme ambient temperatures—experience non-linear battery degradation, thermal stress, and unpredictable range depletion. Standard vehicle Battery Management Systems (BMS) rely on rudimentary lookup tables and simple coulomb counting. They fail to:
- Dynamically forecast **Remaining Useful Life (RUL)** under varying driving intensity.
- Detect **multi-zone thermal safety hazards** across battery, motor, and controller power electronics.
- Capture the electrochemical **"Knee Point"**—the critical tipping point where linear battery aging transitions into rapid, irreversible capacity loss.
- Quantify how **driver aggression** penalizes battery longevity.

### 🚀 The Solution
This project establishes a production-grade, tri-pillar artificial intelligence platform fusing **74 Machine Learning and Deep Learning models**. It processes high-frequency real-world fleet CAN-bus telematics and delivers real-time state estimation, thermal fault classification, driver aggressiveness profiling, and non-linear degradation prognostics via a unified **FastAPI REST backend**.

---

## 2. Dataset Engineering & Telematics Architecture

The platform is trained and validated on **930+ MB of commercial electric fleet telematics** collected from operational OEM vehicles (Euler Motors HiLoad commercial EVs):

### 📥 1. Raw Telematics Ingestion
1. **Excel Logs (350+ MB):**
   - `Alert Log12-FEB-2026_11_47_03.xlsx` & `07.xlsx`: High-frequency fault telemetry, thermal alarms, voltage sag warnings, and BMS isolation alerts.
   - `Trip Report Log12-FEB-2026_11_25_15.xlsx`, `21.xlsx`, `29.xlsx`: Route-level trip records, cumulative energy consumed ($kWh$), odometer readings, trip durations, and start/stop timestamps.
2. **Sequential JSON Packets (580+ MB):**
   - High-rate sub-second CAN-bus packets containing synchronized continuous sensor readings across operating chassis.

### 🔬 2. Sensor Channels & Telemetry Features
| Feature Channel | Sensor Metric / Unit | Description & Role in Models |
|---|---|---|
| `battery_voltage` / `vbv` | Volts ($V$) | Pack voltage, cell sag, open-circuit voltage ($OCV$) recovery |
| `battery_current` / `vbc` | Amperes ($A$) | Continuous current draw, peak discharge, regenerative braking |
| `battery_temp` / `vbt` | Celsius ($^\circ C$) | Pack core temperature, thermal gradient calculation |
| `controller_temp` / `vct`| Celsius ($^\circ C$) | Inverter and motor controller heat accumulation |
| `motor_temp` / `vmt` | Celsius ($^\circ C$) | Powertrain thermal stress and overload tracking |
| `odometer` | Kilometers ($km$) | Cumulative asset mileage |
| `charge_cycle_count` | Equivalent Full Cycles ($EFC$) | Battery aging reference index |
| `speed` / `avg_speed` | $km/h$ | Vehicle speed profile and dynamics |
| `harsh_accel_count` | Event count | High-current discharge spikes from rapid acceleration |
| `harsh_brake_count` | Event count | High-current regenerative charging spikes |

---

## 3. End-to-End Methodology: How the System Was Built

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA & MODEL PIPELINE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  [1. Raw Ingestion]   Load 930MB Excel & JSON CAN-bus telemetry             │
│          │                                                                  │
│          ▼                                                                  │
│  [2. Preprocessing]   Dynamic Outlier Clipping + Timestamp Alignment        │
│          │            (voltages [40V-90V], temps [-10°C to 100°C])          │
│          ▼                                                                  │
│  [3. Feature Eng]     Leak-free Scaling + Incremental Capacity (dQ/dV)      │
│          │            + 10-step sliding sequential tensors                  │
│          ▼                                                                  │
│  [4. Model Training]  74 Models Trained (sklearn, XGBoost, PyTorch, Keras)  │
│          │                                                                  │
│          ▼                                                                  │
│  [5. API Serving]     FastAPI Lifespan Registry (11 Endpoints at :8000)     │
│          │                                                                  │
│          ▼                                                                  │
│  [6. Frontend App]    Next.js / React / Vite Dashboard with Live Telemetry   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 🔹 Stage 1: Data Cleaning & Preprocessing
- **Outlier Rejection:** Replaced corrupted physical sensor readings (e.g. negative speeds, temperatures $>110^\circ C$) with bounded physical limits.
- **Leak-Free Transformation:** All `StandardScaler` objects fit exclusively on training splits and saved independently per task.

### 🔹 Stage 2: Feature Engineering & Signal Processing
- **Electrochemical Metrics:** Incremental capacity gradient ($dQ/dV$), temperature rise rate ($dT/dt$), internal resistance proxy ($R_{int} \approx \Delta V / \Delta I$).
- **Behavioral Indices:** Kinetic Energy Intensity ($v^2$), acceleration variance, speed standard deviation.
- **Deep Tensors:** 10-timestep sliding matrices `[voltage, current, temperature, soc]` for sequential deep networks.

---

## 4. The 3 Core Pillars (Modules)

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                       TRI-PILLAR SYSTEM ARCHITECTURE                          │
├───────────────────────┬───────────────────────┬───────────────────────────────┤
│  MODULE A             │  MODULE B             │  MODULE C                     │
│  Fleet Macro Telematics│  BatteryIQ Cyber-Phys │  Behavior-Aware BMS (BA-BMS)  │
├───────────────────────┼───────────────────────┼───────────────────────────────┤
│ • State of Charge     │ • Multi-Zone Thermal  │ • Driver Aggressiveness (AI)  │
│ • State of Health     │ • Deep SOH CNN-LSTM   │ • Battery Stress Index (BSI)  │
│ • Remaining Useful Life│ • Thermal Risk Safety │ • Knee-Point Prognostics      │
│ • Driving Range (km)  │ • Digital Twin 0-100  │ • Meta-Ensemble Fusion        │
│ [56 ML/DL Models]     │ [8 Models/Weights]    │ [10 Models/Algorithms]        │
└───────────────────────┴───────────────────────┴───────────────────────────────┘
```

### 🔹 Module A: Macro Fleet State Estimation (56 Models)
- **Engineered by:** Fleet Data Analytics Team
- **Storage:** `models/soc/`, `models/soh/`, `models/rul/`, `models/mileage/`
- **Scope:** 14 models per task (9 Machine Learning + 5 Deep Learning Neural Networks):
  - **SOC Champion:** K-Nearest Neighbors ($R^2=0.9958$, RMSE=1.34%)
  - **SOH Tabular Champion:** XGBoost Regressor ($R^2=0.9672$, RMSE=0.82%)
  - **RUL Champion:** Gradient Boosting Regressor ($R^2=0.9997$, RMSE=8.12 cycles)
  - **Mileage Champion:** XGBoost Regressor ($R^2=0.9445$, RMSE=5.42 km)

### 🔹 Module B: BatteryIQ Cyber-Physical & Thermal Safety (8 Models)
- **Engineered by:** BatteryIQ Cyber-Physical Safety Team
- **Storage:** `models/thermal/`, `models/soh_deep/`
- **Scope:**
  - **Multi-Zone Thermal Champion:** 200-Tree Random Forest ($F_1=0.997$, 99.71% accuracy) monitoring 3 critical thermal zones (Battery, Inverter Controller, Motor).
  - **Sequential Deep SOH Champion:** PyTorch Spatial-Temporal 1D-CNN + LSTM Network (RMSE=5.29%).
  - **Digital Twin Health Engine:** Fuses thermal risk, SOH, and cell balance into a single composite score ($0 \to 100$).

### 🔹 Module C: Behavior-Aware BMS & Knee Prognostics (10 Models)
- **Engineered by:** Degradation & Prognostics Team
- **Storage:** `models/knee_prognostics/`, `models/driver_behavior/`
- **Scope:**
  - **Driver Aggressiveness Index ($AI \in [0, 1]$):**
    $$AI = 0.25 \cdot Accel + 0.20 \cdot Brake + 0.15 \cdot Corner + 0.15 \cdot \sigma_{spd} + 0.15 \cdot v^2 + 0.10 \cdot Overspeed$$
  - **Battery Stress Index ($BSI \in [0, 1]$):**
    $$BSI = 0.35 \cdot \Delta T_{grad} + 0.30 \cdot I_{peak} + 0.20 \cdot \sigma_{V} + 0.15 \cdot \frac{dSOC}{dt}$$
  - **Knee-Point Degradation Prognostics ($RUL_{to\_knee}$):** 28-feature pre-trained XGBoost Booster forecasting remaining cycles before non-linear rapid aging.
  - **Piecewise Linear Knee Detector:** Mathematical optimizer minimizing combined MSE across pre-knee and post-knee slopes.

---

## 5. 74-Model Benchmark & Quantifiable Results

| Task / Domain | Owning Module | Models Evaluated | Champion Model | Accuracy / $R^2$ | RMSE / Error |
|---|---|---|---|---|---|
| **State of Charge (SOC %)** | Module A | 9 ML + 5 DL | **KNN Regressor** | **0.9958** | **1.34 %** |
| **State of Health (SOH % Tabular)** | Module A | 9 ML + 5 DL | **XGBoost** | **0.9672** | **0.82 %** |
| **Remaining Useful Life (RUL Cycles)**| Module A | 9 ML + 5 DL | **Gradient Boosting** | **0.9997** | **8.12 cycles**|
| **Driving Mileage (km / charge)** | Module A | 9 ML + 5 DL | **XGBoost** | **0.9445** | **5.42 km** |
| **Multi-Zone Thermal Safety** | Module B | 200-Tree RF + DT | **Random Forest** | **99.71 % Acc**| **$F_1 = 0.997$** |
| **Sequential Deep SOH (%)** | Module B | PyTorch Hybrid | **1D-CNN + LSTM** | **Deep Tensor** | **5.29 %** |
| **Degradation Knee Point ($RUL_{knee}$)**| Module C | XGBoost + Ensembles| **XGBoost Booster** | **28-Feature** | **Piecewise Opt**|
| **Driver Behavior ($AI$ & $BSI$)** | Module C | Normalized Indices | **BA-BMS Engine** | **Deterministic**| **$0.0 \to 1.0$** |

---

## 6. Backend Serving & Production Architecture

### 🗂️ Clean Folder Structure on Disk
```
Final_Year_Project_1/
├── run_all.py                       # Master Launcher (API / CLI / Audit)
├── retrain_all.py                   # Master Retraining Pipeline (All 3 Modules)
├── cli.py                           # 12-Option Interactive Terminal CLI
├── requirements.txt                 # Unified Dependencies
├── README.md                        # Master Overview
│
├── docs/                            # 📚 Consolidated Documentation
│   ├── FRONTEND_HANDOVER_SPECIFICATION.md
│   ├── INTEGRATION_REPORT.md
│   ├── architecture.md
│   ├── module_a/
│   ├── module_b/
│   └── module_c/
│
├── models/                          # 🧠 8 Task-Specific Model Subfolders
│   ├── soc/                         # SOC Models (.pkl, .keras, scaler)
│   ├── soh/                         # Tabular SOH Models (.pkl, .keras, scaler)
│   ├── rul/                         # Global RUL Models (.pkl, .keras, scaler)
│   ├── mileage/                     # Mileage Models (.pkl, .keras, scaler)
│   ├── thermal/                     # Multi-Zone Thermal RF & Scalers (.joblib)
│   ├── soh_deep/                    # Spatial-Temporal SOH Hybrid CNN-LSTM (.pt)
│   ├── knee_prognostics/            # Knee-Point XGBoost Booster (.json, .pkl)
│   └── driver_behavior/             # Behavioral Parameters & Rules (.json)
│
├── data/                            # 📊 raw/ (930MB), processed/ (480MB), splits/
├── modules/                         # ⚙️ Clean Python Code (module_a, module_b, module_c)
├── api/                             # 🌐 FastAPI App (main.py, schemas.py, routers/)
├── results/                         # 📈 Plots & Evaluation Reports
└── logs/                            # 📝 System Execution Logs
```

---

## 7. Complete REST API Specification (11 Endpoints)

Base URL: `http://localhost:8000` | Interactive Docs: `http://localhost:8000/docs`

### 1️⃣ System Health Check
- **Route:** `GET /health`
- **Response `200 OK`:**
```json
{
  "status": "ok",
  "modules": {
    "module_a_fleet": { "SOC": true, "SOH": true, "RUL": true, "Mileage": true },
    "module_b_battery_iq": true,
    "module_c_babms": true
  },
  "timestamp": "2026-08-21T14:00:00"
}
```

---

### 2️⃣ Module A — State of Charge (SOC) Prediction
- **Route:** `POST /predict/soc`
- **Request Body:**
```json
{
  "battery_voltage": 74.0,
  "battery_temp": 32.0,
  "battery_current": -20.0,
  "abs_current": 20.0,
  "is_charging": 0,
  "odometer": 12500.0,
  "odometer_diff": 5.2,
  "voltage_deviation": 2.0,
  "temp_stress_index": 0.28,
  "drive_mode_encoded": 1,
  "hour": 14,
  "day_of_week": 3,
  "month": 2,
  "is_weekend": 0,
  "is_peak": 1,
  "oem_encoded": 0,
  "model_encoded": 0
}
```
- **Response `200 OK`:**
```json
{
  "task": "SOC",
  "model_used": "KNN",
  "prediction": 95.75,
  "unit": "%"
}
```

---

### 3️⃣ Module A — State of Health (SOH Tabular) Prediction
- **Route:** `POST /predict/soh`
- **Request Body:**
```json
{
  "battery_voltage": 74.0,
  "battery_temp": 30.0,
  "battery_current": -15.0,
  "abs_current": 15.0,
  "odometer": 15000.0,
  "odometer_diff": 10.0,
  "charge_cycle_count": 250.0,
  "mile_avg": 75.0,
  "miles_per_charge": 110.0,
  "days_in_service": 300.0,
  "degradation_factor": 0.05,
  "temp_stress_index": 0.2,
  "voltage_deviation": 2.0,
  "oem_encoded": 0,
  "model_encoded": 0
}
```
- **Response `200 OK`:**
```json
{
  "task": "SOH",
  "model_used": "XGBoost",
  "prediction": 99.40,
  "unit": "%"
}
```

---

### 4️⃣ Module A — Remaining Useful Life (RUL) Prediction
- **Route:** `POST /predict/rul`
- **Request Body:**
```json
{
  "odometer": 15000.0,
  "soc_at_charge": 85.0,
  "mile_avg": 75.0,
  "miles_per_charge": 110.0,
  "days_in_service": 300.0,
  "degradation_factor": 0.05,
  "soh_mean": 92.0,
  "miles_per_charge_rolling_3": 112.0,
  "miles_per_charge_rolling_5": 110.0,
  "miles_per_charge_rolling_10": 108.0,
  "oem_encoded": 0,
  "model_encoded": 0
}
```
- **Response `200 OK`:**
```json
{
  "task": "RUL",
  "model_used": "GradientBoosting",
  "prediction": 1234.12,
  "unit": "cycles"
}
```

---

### 5️⃣ Module A — Driving Mileage per Charge (km) Prediction
- **Route:** `POST /predict/mileage`
- **Request Body:**
```json
{
  "run_kms": 45.0,
  "avg_speed": 32.0,
  "max_speed": 55.0,
  "trip_duration_hrs": 1.4,
  "stoppage_count": 3,
  "energy_efficiency": 0.18,
  "trip_intensity": 44.8,
  "speed_ratio": 0.58,
  "stoppage_density": 2.14,
  "energy_utilized": 8.1,
  "hour": 11,
  "day_of_week": 2,
  "month": 2,
  "is_weekend": 0,
  "is_peak": 0,
  "oem_encoded": 0,
  "city_encoded": 0
}
```
- **Response `200 OK`:**
```json
{
  "task": "Mileage",
  "model_used": "XGBoost",
  "prediction": 105.82,
  "unit": "km"
}
```

---

### 6️⃣ Module B — Multi-Zone Thermal Safety Assessment
- **Route:** `POST /predict/thermal`
- **Request Body:**
```json
{
  "vbt": 35.0,
  "vct": 42.0,
  "vmt": 55.0,
  "vbv": 74.0,
  "vbc": -20.0,
  "soc": 80.0,
  "speed": 30.0
}
```
- **Response `200 OK`:**
```json
{
  "safety_status": "SAFE",
  "risk_probability": 0.0,
  "severity": "NORMAL",
  "active_alert": "No active thermal hazards detected.",
  "recommended_action": "System operating within optimal thermal parameters."
}
```

---

### 7️⃣ Module B — Deep Sequential SOH (Hybrid CNN-LSTM)
- **Route:** `POST /predict/soh-deep`
- **Request Body:**
```json
{
  "vehicle_id": "GJ05CV6564",
  "sequence": [
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
  ]
}
```
- **Response `200 OK`:**
```json
{
  "vehicle_id": "GJ05CV6564",
  "estimated_soh_percent": 91.69,
  "capacity_state": "Optimal (Tier 1)",
  "confidence_score": 0.947,
  "requires_balancing": false
}
```

---

### 8️⃣ Module B — Comprehensive Digital Twin Vehicle Diagnosis
- **Route:** `POST /predict/diagnose/vehicle`
- **Request Body:**
```json
{
  "vehicle_id": "GJ05CV6564",
  "oem_model": "Euler HiLoad",
  "soc": 82.0,
  "voltage": 76.0,
  "current": -18.0,
  "battery_temp": 30.0,
  "controller_temp": 40.0,
  "motor_temp": 52.0,
  "speed": 35.0
}
```
- **Response `200 OK`:**
```json
{
  "vehicle_id": "GJ05CV6564",
  "overall_health_score": 94.1,
  "thermal_status": {
    "safety_status": "SAFE",
    "risk_probability": 0.0,
    "severity": "NORMAL"
  },
  "soh_status": {
    "estimated_soh_percent": 94.1,
    "capacity_state": "Optimal (Tier 1)"
  },
  "critical_alert": false,
  "action_items": [
    "Battery pack operating at nominal thermal equilibrium.",
    "Cell balance acceptable across sub-modules."
  ]
}
```

---

### 9️⃣ Module C — Driver Behavior & Battery Stress Index ($AI$ & $BSI$)
- **Route:** `POST /predict/driver-behavior`
- **Request Body:**
```json
{
  "harsh_accel_count": 3,
  "harsh_brake_count": 2,
  "harsh_corner_count": 1,
  "speed_variance": 8.5,
  "avg_speed": 38.0,
  "max_speed": 68.0,
  "battery_temp_max": 36.0,
  "max_discharge_current": 35.0
}
```
- **Response `200 OK`:**
```json
{
  "aggressiveness_index": 0.229,
  "battery_stress_index": 0.3003,
  "driver_classification": "Smooth & Energy-Conscious",
  "estimated_annual_soh_penalty_pct": 0.8,
  "recommendations": [
    "Driver style maintains optimal electrochemical battery longevity.",
    "Current discharge peaks within safe C-rate boundaries."
  ]
}
```

---

### 🔟 Module C — Degradation Knee-Point Prognostics ($RUL_{to\_knee}$)
- **Route:** `POST /predict/knee-point`
- **Request Body:**
```json
{
  "charge_cycle_count": 200.0,
  "capacity": 94.0,
  "voltage": 73.8,
  "battery_temp": 33.0,
  "current": -20.0,
  "soc": 75.0,
  "speed": 36.0
}
```
- **Response `200 OK`:**
```json
{
  "rul_to_knee_cycles": 142.5,
  "is_post_knee": false,
  "knee_risk_state": "Pre-Knee Safe Degradation",
  "aging_rate_slope": -0.018,
  "bms_directive": "Maintain standard charging protocol (CC-CV standard rate)."
}
```

---

### 1️⃣1️⃣ Module C — Meta-Ensemble Holistics (A + B + C Unified)
- **Route:** `POST /predict/meta-ensemble`
- **Request Body:**
```json
{
  "vehicle_id": "GJ05CV6564",
  "charge_cycle_count": 200.0,
  "battery_voltage": 73.8,
  "battery_temp": 33.0,
  "battery_current": -20.0,
  "soc": 75.0,
  "harsh_accel_count": 3,
  "speed_variance": 8.5
}
```
- **Response `200 OK`:**
```json
{
  "vehicle_id": "GJ05CV6564",
  "estimated_soh": 97.33,
  "rul_to_knee_cycles": 142.5,
  "driver_aggressiveness_index": 0.24,
  "battery_stress_index": 0.31,
  "unified_health_grade": "Grade A (Optimal)",
  "executive_summary": "Vehicle exhibiting healthy degradation curve; driver aggressiveness within benchmark tolerance."
}
```

---

## 8. Frontend UI/UX Design System & Component Architecture

### 🎨 Design Tokens & Aesthetic Principles
- **Theme:** High-end Dark Glassmorphism (`#0A0D14` background, `#111622` cards, `#1E293B` borders).
- **Accents:** Neon Emerald (`#10B981` for Safe/Optimal), Electric Cyan (`#06B6D4` for Telematics), Amber (`#F59E0B` for Warning/Stress), Crimson (`#EF4444` for Critical Overheat).
- **Typography:** Inter / Outfit from Google Fonts with high legibility for telemetry values.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      EV BATTERY INTELLIGENCE DASHBOARD                      │
├─────────────────┬───────────────────────────────────────────────────────────┤
│  ⚡ State Est.  │ [Real-Time Gauges: SOC 95.8%, SOH 99.4%, RUL 1234c, 106km]│
│  🌡️ Thermal     │ [3-Zone Thermal Map: Pack 35°C, Controller 42°C, Motor 55°C]│
│  🏎️ Driver AI   │ [Driver Aggressiveness Dial: 0.23 | Stress: 0.30 (Smooth)]│
│  📉 Knee Curve  │ [Interactive Capacity Fade Chart + RUL to Knee Countdown] │
│  🧬 Digital Twin│ [Overall Health Score: 94.1/100 | Actionable Diagnostics] │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

### 🧩 Recommended 6 Core Dashboard Tabs
1. **Fleet Health Overview:** Top KPIs, online vehicle picker, system health banner.
2. **State Estimation Hub (Module A):** Interactive sliders for Voltage, Current, Temperature, and Odometer with real-time KPI cards.
3. **Cyber-Physical Thermal Safety (Module B):** Multi-zone heat gauge, hazard alert badge, and safety recommendation ticker.
4. **Driver Profiling & Stress Radar (Module C):** Driver Aggressiveness ($AI$) and Battery Stress ($BSI$) dials, driver cohort tag, and annual SOH loss penalty estimator.
5. **Degradation & Knee Prognostics (Module C):** Live $SOH$ vs. $Cycles$ line graph showing piecewise knee intersection and $RUL_{to\_knee}$ countdown.
6. **Meta-Ensemble Vehicle Report:** Executive summary combining all 3 modules with a downloadable / printable PDF summary.

---

## 9. Verification, Retraining & Operation Guide

```bash
# 1. System Readiness Check (Audits all 8 model directories)
python run_all.py --check

# 2. Launch FastAPI REST Backend (Port 8000)
python run_all.py

# 3. Interactive Terminal CLI (12 Prediction Options)
python cli.py

# 4. Autonomous Master Retraining (Retrains all 3 modules on new data)
python retrain_all.py

# 5. Run Automated Test Suite (20 Tests across Module B & C)
pytest modules/module_b/tests modules/module_c/tests
```
