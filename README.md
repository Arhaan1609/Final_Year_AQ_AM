# EV Battery Intelligence System
### Unified Final Year Project — Tri-Pillar ML & DL-Based Electric Vehicle Battery Analysis

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/sklearn-Module%20A-orange)](https://scikit-learn.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-Module%20B-red)](https://pytorch.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-Module%20C-brightgreen)](https://xgboost.readthedocs.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-11%20Endpoints-green)](https://fastapi.tiangolo.com)
[![Models](https://img.shields.io/badge/Trained%20Models-74%20Total-purple)](file:///c:/Final_Year_Project_1/INTEGRATION_REPORT.md)

---

## 🗂️ Project Structure & Module Overview

```
Final_Year_Project_1/
│
├── run_all.py                       ← Master Launcher (API, CLI, Check, Retrain)
├── retrain_all.py                   ← Autonomous Master Retraining Pipeline (All 3 Modules)
├── cli.py                           ← Interactive Terminal Prediction CLI
├── requirements.txt                 ← Consolidated Dependencies
├── README.md                        ← Project Overview & Quickstart
│
├── docs/                            ← [CONSOLIDATED] ALL DOCUMENTATION
│   ├── INTEGRATION_REPORT.md        ← Master 74-Model Report & Architecture Reference
│   ├── architecture.md              ← High-Level System Architecture
│   ├── module_a/                    ← Module A Pipeline Documentation
│   ├── module_b/                    ← Module B Documentation (ARCHITECTURE, INTEGRATION_GUIDE, etc.)
│   └── module_c/                    ← Module C Documentation (DATA_SPECIFICATIONS, PROJECT_REPORT, etc.)
│
├── models/                          ← [STRUCTURED] 8 TASK-SPECIFIC SUBFOLDERS
│   ├── soc/                         ← SOC Models (SOC_KNN.pkl, SOC_ANN_best.keras, scaler_soc.pkl)
│   ├── soh/                         ← Tabular SOH Models (SOH_XGBoost.pkl, SOH_ANN_best.keras, scaler_soh.pkl)
│   ├── rul/                         ← Global RUL Models (RUL_GradientBoosting.pkl, RUL_ANN_best.keras, scaler_rul.pkl)
│   ├── mileage/                     ← Mileage Models (Mileage_XGBoost.pkl, Mileage_ANN_best.keras, scaler_mileage.pkl)
│   ├── thermal/                     ← Multi-Zone Thermal Safety RF & Scalers (thermal_rf_multizone.joblib)
│   ├── soh_deep/                    ← Spatial-Temporal SOH Hybrid CNN-LSTM (soh_hybrid_cnn_lstm.pt)
│   ├── knee_prognostics/            ← Knee-Point XGBoost Booster (best_xgboost_model.json, feature_scaler.pkl)
│   └── driver_behavior/             ← Behavioral parameters, metadata, rule configurations
│
├── data/                            ← [UNIFIED] ALL FLEET DATA
│   ├── raw/                         ← Raw Excel & JSON Telematics files
│   ├── processed/                   ← Cleaned CSV feature tables & feature matrices
│   └── splits/                      ← Train/Test benchmark splits and manifests
│
├── modules/                         ← [CLEAN PYTHON CODE ONLY]
│   ├── module_a/                    ← Fleet Analytics Code (01 to 07, config.py, utils.py)
│   ├── module_b/                    ← BatteryIQ Core Engine (src/, config/, tests/)
│   └── module_c/                    ← BA-BMS & Knee Detection (engine.py, knee_detection.py, tests/)
│
├── api/                             ← Unified REST API Layer (FastAPI)
│   ├── main.py                         FastAPI app registering all 11 endpoints
│   ├── schemas.py                      Unified Pydantic request/response models
│   └── routers/                        Routers for Module A, Module B, and Module C
│
├── results/                         ← Plots & Comparison Reports (plots/, reports/)
└── logs/                            ← System Execution Logs
```

---

## 🎯 Complete Task-to-Model Mapping (74 Models Total)

| Task / Domain | Owning Module | Models Trained & Evaluated | Champion Model Deployed | Benchmark Performance |
|---|---|---|---|---|
| **1. State of Charge (SOC)** | **Module A** | 9 ML Models (KNN, RF, XGB, ExtraTrees, GB, DT, Ridge, Lasso, LR) + 5 Deep Learning Models (ANN, CNN-1D, LSTM, GRU, BiLSTM) | **KNN Regressor** | $R^2 = 0.9958$<br>RMSE = 1.34% |
| **2. State of Health (SOH)** | **Modules A, B, C** | • **Module A (Tabular)**: 9 ML + 5 DL models<br>• **Module B (Sequential Deep)**: Hybrid 1D-CNN + LSTM in PyTorch<br>• **Module C (Behavioral)**: Random Forest ($R^2=0.94$), Multi-Target LSTM, Multi-Target GRU, LightGBM, CatBoost | **XGBoost (Tabular)** & **PyTorch CNN-LSTM (Deep)** | $R^2 = 0.9672$<br>RMSE = 5.29% |
| **3. Remaining Useful Life (RUL)** | **Module A** | 9 ML Models (GB, RF, XGB, ExtraTrees, DT, Ridge, Lasso, LR, KNN) + 5 Deep Learning Models (ANN, CNN-1D, LSTM, GRU, BiLSTM) | **Gradient Boosting** | $R^2 = 0.9997$<br>RMSE = 8.12 cycles |
| **4. Mileage per Charge (km)** | **Module A** | 9 ML Models (XGB, RF, ExtraTrees, GB, DT, Ridge, Lasso, LR, KNN) + 5 Deep Learning Models (ANN, CNN-1D, LSTM, GRU, BiLSTM) | **XGBoost Regressor** | $R^2 = 0.9445$<br>RMSE = 5.42 km |
| **5. Battery Degradation & Capacity Fade** | **Modules A, B, C** | • Macro Degradation Factor Model (Module A)<br>• Electrochemical Sequential Fade Model (Module B)<br>• Incremental Capacity ($dQ/dV$) Engine (Module C)<br>• Multi-Lag Temporal Degradation Engine (Module C)<br>• Behavioral Accelerated Fade Engine (Module C) | **Dynamic Degradation Engines** | Tracks capacity loss slope & aging state |
| **6. Knee-Point Degradation ($RUL_{to\_knee}$)** | **Module C** | • Pre-trained 28-feature XGBoost Booster<br>• Piecewise Linear Joint MSE Optimizer<br>• Multi-Head Attention CNN-BiLSTM<br>• Multi-Target Deep LSTM & GRU<br>• LightGBM & CatBoost | **XGBoost Booster** & **Piecewise Detector** | Predicts cycles before non-linear rapid aging |
| **7. Multi-Zone Thermal Safety** | **Module B** | • Multi-Zone Random Forest (200 Trees)<br>• Baseline Decision Tree Classifier<br>• Digital Twin Vehicle Health Scoring Engine | **Multi-Zone RF (200T)** | $F_1 = 0.997$<br>Accuracy = 99.71% |
| **8. Driver Behavior & Stress (AI / BSI)** | **Module C** | • Driver Aggressiveness Index ($AI$) Normalization Engine<br>• Battery Stress Index ($BSI$) Electrochemical Strain Engine | **BA-BMS Engine** | Normalizes driving aggression ($0.0 \to 1.0$) |

---

## 🚀 Quick Start

### 1. Check System & Model Readiness
```bash
python run_all.py --check
```

### 2. Start the Unified REST API (11 Endpoints)
```bash
python run_all.py
# API running at: http://localhost:8000
# Interactive Swagger docs: http://localhost:8000/docs
```

### 3. Launch Interactive Terminal CLI (12 Prediction Options)
```bash
python run_all.py --cli
# OR
python cli.py
```

### 4. Run Automated Test Suite (20 Tests)
```bash
pytest modules/module_b/tests modules/module_c/tests
```

---

## 🌐 API Endpoint Reference

| Module | Method | Endpoint | Description |
|--------|--------|----------|-------------|
| **System** | `GET` | `/health` | Live health of all 3 modules & model weights |
| **System** | `GET` | `/models/status` | Complete model inventory & benchmark metrics |
| **Module A** | `POST` | `/predict/soc` | State of Charge prediction (%) |
| **Module A** | `POST` | `/predict/soh` | Tabular State of Health prediction (%) |
| **Module A** | `POST` | `/predict/rul` | Remaining Useful Life prediction (cycles) |
| **Module A** | `POST` | `/predict/mileage` | Per-charge driving range prediction (km) |
| **Module B** | `POST` | `/predict/thermal` | Multi-Zone Thermal Safety classification |
| **Module B** | `POST` | `/predict/soh-deep` | PyTorch CNN-LSTM sequential SOH (%) |
| **Module B** | `POST` | `/predict/diagnose/vehicle` | Full composite health diagnosis (0-100) |
| **Module B** | `POST` | `/predict/diagnose/batch` | Fleet-wide batch vehicle diagnostics |
| **Module C** | `POST` | `/predict/driver-behavior` | Driver Aggressiveness Index (AI) & Battery Stress (BSI) |
| **Module C** | `POST` | `/predict/knee-point` | Knee-Point Remaining Useful Life ($RUL_{to\_knee}$) |
| **Module C** | `POST` | `/predict/meta-ensemble` | Multi-Target simultaneous SOH and Knee prediction |
