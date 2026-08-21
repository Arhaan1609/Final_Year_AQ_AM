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
├── run_all.py                       ← Master entry point (API + CLI launcher for all 3 modules)
├── cli.py                           ← Master CLI shortcut (12 prediction options)
├── requirements_unified.txt         ← Unified dependencies (Modules A + B + C)
├── INTEGRATION_REPORT.md            ← Master Technical & Integration Report (Detailed 74-Model Inventory)
│
├── modules/                         ← All Machine Learning Modules
│   ├── module_a/                    ← Module A: Fleet Prediction Pipeline (56 Models)
│   │   ├── config.py                   Central config (paths, features, hyperparams)
│   │   ├── utils.py                    Shared utilities & loggers
│   │   ├── 01_data_ingestion.py        Load raw Excel + JSON fleet data
│   │   ├── 02_preprocessing.py         Clean, clip outliers, merge datasets
│   │   ├── 03_feature_engineering.py   Build leak-free feature sets & degradation factors
│   │   ├── 04_model_training.py        Train 9 ML + 5 DL models per task (56 models total)
│   │   ├── 05_evaluation.py            RMSE/MAE/R² + SHAP + robustness tests
│   │   ├── 06_visualization.py         Generate all plots
│   │   ├── 07_prediction_system.py     Interactive CLI (12 prediction options)
│   │   └── retrain_clean.py            Re-run pipeline steps 3-7 cleanly
│   │
│   ├── module_b/                    ← Module B: Cyber-Physical Health & Thermal Management (8 Models)
│   │   ├── src/
│   │   │   ├── core/                   schemas.py, preprocessor.py, exceptions.py
│   │   │   └── models/                 engine.py, soh_champion.py, thermal_champion.py
│   │   ├── weights/                    Pre-trained model weights (.pt, .joblib)
│   │   ├── data/                       Test splits, sample telemetry JSON
│   │   ├── config/settings.yaml        Thermal thresholds and model config
│   │   └── tests/                      Automated pytest test suite (13 tests)
│   │
│   └── module_c/                    ← Module C: Behavior-Aware BMS & Knee Prognostics (10 Models)
│       ├── engine.py                   BABMSEngine wrapper (AI, BSI, Knee Booster)
│       ├── best_xgboost_model.json     Pre-trained Knee-Point XGBoost Booster (28 features)
│       ├── feature_scaler.pkl          Pre-trained 28-feature StandardScaler
│       ├── knee_detection.py           Piecewise linear fit knee detector
│       ├── knee_final.py               Multi-Head Attention CNN-BiLSTM knee model
│       ├── unified_ensemble.py         Multi-target meta-ensemble training (LSTM + GRU)
│       ├── demo_ensemble.py            Visual performance demonstration tool
│       ├── data_integrator.py          Cross-vehicle rank mapping synthesizer
│       ├── improved_data_processing.py Behavioral index feature engineering (AI & BSI)
│       └── tests/                      Automated pytest test suite (7 tests)
│
├── api/                             ← Unified REST API (FastAPI)
│   ├── main.py                         FastAPI app registering all 11 endpoints
│   ├── schemas.py                      Unified Pydantic request/response models
│   └── routers/
│       ├── module_a.py                 SOC / SOH / RUL / Mileage endpoints
│       ├── module_b.py                 Thermal / SOH-Deep / Diagnose endpoints
│       └── module_c.py                 Driver Behavior / Knee-Point / Meta-Ensemble
│
├── data/
│   ├── raw/                         ← Raw fleet data (930MB — Excel + JSON)
│   └── processed/                   ← Cleaned CSVs + feature sets (~480MB)
│
├── models/                          ← Module A trained model artifacts (62 model files)
│   ├── SOC_KNN.pkl                     Best SOC model (R²=0.9958)
│   ├── SOH_XGBoost.pkl                 Best SOH model (R²=0.9672)
│   ├── RUL_GradientBoosting.pkl        Best RUL model (R²=0.9997)
│   ├── Mileage_XGBoost.pkl             Best Mileage model (R²=0.9445)
│   ├── *_ANN_best.keras                Deep learning Keras models
│   └── scaler_*.pkl                    Feature scalers
│
├── results/                         ← Plots, comparison tables, evaluation reports
└── logs/                            ← System execution logs
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
