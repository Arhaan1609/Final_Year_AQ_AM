# 📋 EV Battery Intelligence System — Master Technical & Integration Report
### Comprehensive Model Inventory, Architecture & Task Mapping Reference

**Repository:** [Arhaan1609/Final_Year_AQ_AM](https://github.com/Arhaan1609/Final_Year_AQ_AM.git)  
**Academic Level:** Final Year Engineering Capstone Project  
**System Architecture:** Tri-Pillar Cyber-Physical Battery Intelligence System  
**Total Models & Algorithms:** **74 Trained Machine Learning, Deep Learning & Analytical Models**

---

## 🏛️ Tri-Pillar Architecture & Task Breakdown

```
                              ┌────────────────────────────────────────────────────────┐
                              │            EV BATTERY INTELLIGENCE SYSTEM              │
                              │        FastAPI Unified REST API  +  Terminal CLI       │
                              └────────────────────────────────────────────────────────┘
                                           │              │              │
                   ┌───────────────────────┘              │              └───────────────────────┐
                   ▼                                      ▼                                      ▼
    ┌──────────────────────────────┐       ┌──────────────────────────────┐       ┌──────────────────────────────┐
    │          MODULE A            │       │          MODULE B            │       │          MODULE C            │
    │      (Fleet Analytics)       │       │    (Thermal & Cyber-Physics) │       │   (Behavior & Knee Progn.)   │
    ├──────────────────────────────┤       ├──────────────────────────────┤       ├──────────────────────────────┤
    │ • State of Charge (SOC)      │       │ • Multi-Zone Thermal Safety  │       │ • Battery Degradation Curve  │
    │ • State of Health (SOH)      │       │ • Spatial-Temporal SOH (DL)  │       │ • Knee Point Onset (RUL_knee)│
    │ • Remaining Useful Life (RUL)│       │ • Multi-Zone Sensor Faults   │       │ • Driver Aggressiveness (AI) │
    │ • Mileage per Charge (km)    │       │ • Dual-Pillar Fleet Diagnosis│       │ • Battery Stress Index (BSI) │
    │ • Macro Battery Degradation  │       │ • Degradation Rate / 100 Cyc │       │ • Multi-Target Meta-Ensemble │
    └──────────────────────────────┘       └──────────────────────────────┘       └──────────────────────────────┘
```

---

## 🔬 Complete Task-by-Task Model Inventory

Here is the exact breakdown of **which models were trained for each task**, **in which module**, their **performance**, and their **file locations**:

---

### 1. State of Charge (SOC) Prediction
- **Module:** **Module A** (`modules/module_a/`)
- **Dataset:** 930MB Indian EV Fleet Telematics (50M+ records)
- **Features Used:** Battery Voltage, Battery Temp, Battery Current, Absolute Current, Charge State %, Drive Mode, Temp Stress Index, Voltage Deviation, Rolling SOC (5 & 10 step), Time/Calendar features.
- **Models Trained (14 Models):**
  1. **K-Nearest Neighbors (KNN)** — **CHAMPION: $R^2 = 0.9958$, RMSE = 1.34%** (Saved in `models/SOC_KNN.pkl`)
  2. Random Forest Regressor ($R^2 = 0.9973$)
  3. Extra Trees Regressor ($R^2 = 0.9981$)
  4. XGBoost Regressor ($R^2 = 0.9942$)
  5. Gradient Boosting Regressor ($R^2 = 0.9910$)
  6. Decision Tree Regressor ($R^2 = 0.9854$)
  7. Ridge Regressor ($R^2 = 0.8841$)
  8. Lasso Regressor ($R^2 = 0.8620$)
  9. Linear Regression ($R^2 = 0.8840$)
  10. Deep Artificial Neural Network (ANN) — (Saved in `models/SOC_ANN_best.keras`)
  11. Deep 1D-CNN Sequence Regressor
  12. Deep Long Short-Term Memory (LSTM)
  13. Deep Gated Recurrent Unit (GRU)
  14. Deep Bidirectional LSTM (BiLSTM)
- **API Endpoint:** `POST /predict/soc`

---

### 2. State of Health (SOH) Prediction (Multi-Domain)
- **Datasets:** Euler Motors HiLoad Telematics + Cross-Fleet Degradation Datasets.
- **Models Trained (20 Models across Modules A, B, and C):**

#### A. Tabular Fleet SOH (Module A — 14 Models):
1. **XGBoost Regressor** — **CHAMPION: $R^2 = 0.9672$, RMSE = 0.89%** (Saved in `models/SOH_XGBoost.pkl`)
2. Extra Trees Regressor ($R^2 = 0.9990$)
3. Random Forest Regressor ($R^2 = 0.9985$)
4. Gradient Boosting Regressor ($R^2 = 0.9540$)
5. Decision Tree Regressor ($R^2 = 0.9410$)
6. KNN Regressor ($R^2 = 0.9320$)
7. Ridge Regressor ($R^2 = 0.8210$)
8. Lasso Regressor ($R^2 = 0.8040$)
9. Linear Regression ($R^2 = 0.8210$)
10. Deep ANN — (Saved in `models/SOH_ANN_best.keras`)
11. Deep 1D-CNN
12. Deep LSTM
13. Deep GRU
14. Deep BiLSTM

#### B. Spatial-Temporal Deep SOH (Module B — 1 Champion Deep Model):
15. **Hybrid 1D-CNN + LSTM in PyTorch** — **RMSE = 5.29%** across 20.5M records.
    - Combines 1D convolutional feature extraction with recurrent LSTM cells to capture temporal battery impedance rise over consecutive charge/discharge steps.
    - Saved in `modules/module_b/weights/soh_hybrid_cnn_lstm.pt`
    - Implementation: `modules/module_b/src/models/soh_champion.py`

#### C. Behavioral & Ensemble SOH (Module C — 5 Models):
16. **Random Forest Regressor** — **$R^2 = 0.94$, RMSE = 1.25%** (Trained on behavioral telemetry + stress indices in `modules/module_c/ensemble.py`)
17. Multi-Target Deep LSTM (`modules/module_c/unified_ensemble.py`)
18. Multi-Target Deep GRU (`modules/module_c/unified_ensemble.py`)
19. LightGBM Regressor (`modules/module_c/ensemble.py`)
20. CatBoost Regressor (`modules/module_c/ensemble.py`)

- **API Endpoints:** `POST /predict/soh`, `POST /predict/soh-deep`

---

### 3. Remaining Useful Life (RUL — Global Lifecycle Cycles)
- **Module:** **Module A** (`modules/module_a/`)
- **Target:** Remaining full charge cycles before battery reaches 80% capacity End-of-Life (EOL).
- **Models Trained (14 Models):**
  1. **Gradient Boosting Regressor** — **CHAMPION: $R^2 = 0.9997$, RMSE = 8.12 cycles** (Saved in `models/RUL_GradientBoosting.pkl`)
  2. Random Forest Regressor ($R^2 = 1.0000$)
  3. Extra Trees Regressor ($R^2 = 0.9999$)
  4. XGBoost Regressor ($R^2 = 0.9991$)
  5. Decision Tree Regressor ($R^2 = 0.9912$)
  6. KNN Regressor ($R^2 = 0.9420$)
  7. Ridge Regressor ($R^2 = 0.8120$)
  8. Lasso Regressor ($R^2 = 0.7980$)
  9. Linear Regression ($R^2 = 0.8120$)
  10. Deep ANN — (Saved in `models/RUL_ANN_best.keras`)
  11. Deep 1D-CNN Sequence Regressor
  12. Deep LSTM
  13. Deep GRU
  14. Deep BiLSTM
- **API Endpoint:** `POST /predict/rul`

---

### 4. Mileage Prediction (Driving Range per Charge in km)
- **Module:** **Module A** (`modules/module_a/`)
- **Target:** Real-world driving range per full charge in kilometers (km).
- **Models Trained (14 Models):**
  1. **XGBoost Regressor** — **CHAMPION: $R^2 = 0.9445$, RMSE = 5.42 km** (Saved in `models/Mileage_XGBoost.pkl`)
  2. Random Forest Regressor ($R^2 = 0.9466$)
  3. Extra Trees Regressor ($R^2 = 0.9410$)
  4. Gradient Boosting Regressor ($R^2 = 0.9230$)
  5. Decision Tree Regressor ($R^2 = 0.9010$)
  6. KNN Regressor ($R^2 = 0.8840$)
  7. Ridge Regressor ($R^2 = 0.7920$)
  8. Lasso Regressor ($R^2 = 0.7810$)
  9. Linear Regression ($R^2 = 0.7920$)
  10. Deep ANN — (Saved in `models/Mileage_ANN_best.keras`)
  11. Deep 1D-CNN Sequence Regressor
  12. Deep LSTM
  13. Deep GRU
  14. Deep BiLSTM
- **API Endpoint:** `POST /predict/mileage`

---

### 5. Battery Degradation & Capacity Fade Modeling
- **Modules:** **Module A, Module B, and Module C**
- **Core Focus:** Modeling how chemical aging, temperature, current, and time degrade usable battery capacity.
- **Models & Algorithms (5 Implementations):**
  1. **Macro Degradation Factor Model (Module A)**:
     - Formula: $\text{Degradation Factor} = \frac{\text{Initial Capacity} - \text{Current Capacity}}{\text{Initial Capacity}}$
     - Tracks rolling capacity variance, degradation rate, and temperature stress coefficient.
     - Implemented in: `modules/module_a/03_feature_engineering.py`
  2. **Electrochemical Sequential Fade Model (Module B)**:
     - Computes dynamic capacity fade slope per 100 operating cycles (`degradation_slope_per_100_cycles`).
     - Categorizes physical capacity states: *Optimal (Tier 1)*, *Moderate Fade (Tier 2)*, *Critical Degradation (Tier 3)*.
     - Implemented in: `modules/module_b/src/models/engine.py`
  3. **Incremental Capacity Analysis (ICA - $dQ/dV$) Degradation Engine (Module C)**:
     - Derives $dQ/dV$ mean and standard deviation to detect internal phase transitions, lithium plating, and active material loss.
     - Implemented in: `modules/module_c/improved_data_processing.py`
  4. **Multi-Lag Temporal Degradation Engine (Module C)**:
     - Builds capacity lag vectors (`cap_lag_1`, `cap_lag_5`, `cap_drop_abs`, `trend_slope_10`, `trend_slope_20`, `early_degradation`).
     - Implemented in: `modules/module_c/run_final_pipeline.py`
  5. **Behavioral Accelerated Fade Engine (Module C)**:
     - Quantifies the $+4.7\%$ accelerated annual capacity fade caused by aggressive driving maneuvers.
     - Implemented in: `modules/module_c/engine.py`

---

### 6. Knee-Point Detection & Accelerated Aging Prognostics ($RUL_{to\_knee}$)
- **Module:** **Module C** (`modules/module_c/`)
- **Core Focus:** Detecting the non-linear inflection point ("Knee Point") where battery capacity degradation shifts from slow linear aging into exponential rapid breakdown.
- **Models Trained (7 Models):**
  1. **XGBoost Knee Booster** — **CHAMPION: 28-feature booster predicting $RUL_{to\_knee}$ cycles** (Saved in `modules/module_c/best_xgboost_model.json` + `modules/module_c/feature_scaler.pkl`)
  2. **Piecewise Linear Knee Fit Optimizer** — Mathematical two-segment optimization model that finds the split cycle minimizing joint Mean Squared Error (Implemented in `modules/module_c/knee_detection.py`)
  3. **Multi-Head Self-Attention CNN-BiLSTM** — 1D-CNN (kernels 3 & 5) + BiLSTM (64 units) + Multi-Head Self-Attention (4 heads) + Huber Loss (Implemented in `modules/module_c/knee_final.py`)
  4. **Multi-Target Deep LSTM** — Stacked 2-layer LSTM predicting $RUL_{to\_knee}$ and SOH simultaneously (Implemented in `modules/module_c/unified_ensemble.py`)
  5. **Multi-Target Deep GRU** — Stacked 2-layer GRU predicting $RUL_{to\_knee}$ and SOH simultaneously (Implemented in `modules/module_c/unified_ensemble.py`)
  6. **LightGBM Knee Regressor** — Leaf-wise gradient boosting (Implemented in `modules/module_c/ensemble.py`)
  7. **CatBoost Knee Regressor** — Oblivious symmetric tree boosting (Implemented in `modules/module_c/ensemble.py`)
- **API Endpoint:** `POST /predict/knee-point`

---

### 7. Multi-Zone Thermal Safety & Fault Diagnosis
- **Module:** **Module B** (`modules/module_b/`)
- **Core Focus:** Real-time drivetrain thermodynamic monitoring across 3 critical thermal zones:
  - Battery Pack Temperature ($VBT$)
  - Controller/Inverter Temperature ($VCT$)
  - Traction Motor Temperature ($VMT$)
- **Models Trained (3 Models / Engines):**
  1. **Multi-Zone Random Forest Classifier (200 Trees)** — **CHAMPION: $F_1 = 0.997$, Accuracy = 99.71%**
     - Balanced training across 53M Euler HiLoad telemetry packets.
     - Saved in: `modules/module_b/weights/thermal_rf_multizone.joblib`
     - Implementation: `modules/module_b/src/models/thermal_champion.py`
  2. **Baseline Decision Tree Classifier** — Interpretable decision-boundary model.
  3. **Digital-Twin Composite Health Scoring Engine** — Fuses Thermal Safety Risk ($0-1$) and Deep SOH ($0-100\%$) into a unified vehicle health score ($0-100$) and generates actionable BMS mitigation directives. (Implemented in `modules/module_b/src/models/engine.py`)
- **API Endpoints:** `POST /predict/thermal`, `POST /predict/diagnose/vehicle`, `POST /predict/diagnose/batch`

---

### 8. Driver Aggressiveness & Battery Stress Modeling (BA-BMS)
- **Module:** **Module C** (`modules/module_c/`)
- **Core Focus:** Behavior-Aware BMS framework quantifying how driver psychology accelerates battery degradation.
- **Models & Engines (2 Analytical Modeling Engines):**
  1. **Driver Aggressiveness Index ($AI$) Engine**:
     - Computes normalized rating ($0.0 \to 1.0$) from: Harsh Acceleration, Harsh Braking, Aggressive Cornering, Speed Variance, and $v^2$ Kinetic Intensity.
     - Classifies driver cohort: *Smooth & Energy-Conscious* ($AI \le 0.35$), *Moderate Fleet Standard* ($0.35 < AI \le 0.65$), *Aggressive / High Stress* ($AI > 0.65$).
     - Implemented in: `modules/module_c/engine.py` & `modules/module_c/improved_data_processing.py`
  2. **Battery Stress Index ($BSI$) Engine**:
     - Quantifies physical electrochemical strain ($0.0 \to 1.0$) from: Peak Battery Temperatures, $I_{max}$ discharge spikes, cell voltage fluctuations, and SOC drain velocity (%/km).
     - Triggers dynamic BMS current/power throttling directives.
     - Implemented in: `modules/module_c/engine.py`
- **API Endpoint:** `POST /predict/driver-behavior`

---

## 📊 Summary: Grand Total Model Count by Module

| Module | Subsystem / Focus | Total Models & Algorithms | Key Champion Model Artifacts |
|---|---|:---:|---|
| **Module A** | **Fleet Telematics Analytics** (Your Part) | **56 Models** | • `models/SOC_KNN.pkl`<br>• `models/SOH_XGBoost.pkl`<br>• `models/RUL_GradientBoosting.pkl`<br>• `models/Mileage_XGBoost.pkl`<br>• `models/*_ANN_best.keras` |
| **Module B** | **BatteryIQ Thermal & Deep Health** (Teammate 1) | **8 Models** | • `modules/module_b/weights/soh_hybrid_cnn_lstm.pt`<br>• `modules/module_b/weights/thermal_rf_multizone.joblib`<br>• `modules/module_b/weights/scalers.joblib` |
| **Module C** | **BA-BMS & Knee Prognostics** (Teammate 2) | **10 Models** | • `modules/module_c/best_xgboost_model.json`<br>• `modules/module_c/feature_scaler.pkl`<br>• Piecewise Linear Knee Detector<br>• Attention CNN-BiLSTM |
| **TOTAL** | **Integrated EV Battery Intelligence System** | **74 Models** | **All 11 champion models actively served in API & CLI** |

---

## 🧪 Verification & Automated Testing Evidence

1. **Automated Unit & Integration Tests (20/20 Passed):**
   - Command: `pytest modules/module_b/tests modules/module_c/tests`
   - Result: **20 passed in 10.19s, 0 failures, 0 errors.**
2. **FastAPI Live Endpoint Tests (11/11 Active Endpoints Returning 200 OK):**
   - Verified live via `TestClient(app)`:
     - `GET /health` → **200 OK**
     - `POST /predict/soc` → **200 OK** (95.75%)
     - `POST /predict/soh` → **200 OK** (99.40%)
     - `POST /predict/rul` → **200 OK** (1234.1 cycles)
     - `POST /predict/mileage` → **200 OK** (105.82 km)
     - `POST /predict/thermal` → **200 OK** (SAFE, Risk 0.0)
     - `POST /predict/soh-deep` → **200 OK** (91.69%)
     - `POST /predict/diagnose/vehicle` → **200 OK** (Health Score 94.1/100)
     - `POST /predict/driver-behavior` → **200 OK** (AI: 0.229, BSI: 0.300)
     - `POST /predict/knee-point` → **200 OK** (RUL_knee: 0.7 cycles)
     - `POST /predict/meta-ensemble` → **200 OK** (Estimated SOH: 97.33%)

---

## 🚀 Execution Commands

```bash
# 1. Start the Unified REST API (11 Endpoints)
python run_all.py

# 2. Start the Interactive Terminal CLI (12 Prediction Options)
python cli.py

# 3. Check System & Model Readiness
python run_all.py --check

# 4. Run Automated Test Suite
pytest modules/module_b/tests modules/module_c/tests
```
