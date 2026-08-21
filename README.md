# EV Battery Intelligence System
### Unified Final Year Project — Tri-Pillar ML & DL-Based Electric Vehicle Battery Analysis

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/sklearn-Module%20A-orange)](https://scikit-learn.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-Module%20B-red)](https://pytorch.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-Module%20C-brightgreen)](https://xgboost.readthedocs.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-11%20Endpoints-green)](https://fastapi.tiangolo.com)

---

## 🗂️ Project Structure

```
Final_Year_Project_1/
│
├── run_all.py                       ← Master entry point (API + CLI launcher for all 3 modules)
├── cli.py                           ← Master CLI shortcut (12 prediction options)
├── requirements_unified.txt         ← Unified dependencies (Modules A + B + C)
├── INTEGRATION_REPORT.md            ← Comprehensive Tri-Pillar Architecture Report
│
├── modules/                         ← All Machine Learning Modules
│   ├── module_a/                    ← Module A: Fleet Prediction Pipeline
│   │   ├── config.py                   Central config (paths, features, hyperparams)
│   │   ├── utils.py                    Shared utilities & loggers
│   │   ├── 01_data_ingestion.py        Load raw Excel + JSON fleet data
│   │   ├── 02_preprocessing.py         Clean, clip outliers, merge datasets
│   │   ├── 03_feature_engineering.py   Build leak-free feature sets
│   │   ├── 04_model_training.py        Train 9 ML + 5 DL models per task
│   │   ├── 05_evaluation.py            RMSE/MAE/R² + SHAP + robustness tests
│   │   ├── 06_visualization.py         Generate all plots
│   │   ├── 07_prediction_system.py     Interactive CLI (12 prediction options)
│   │   └── retrain_clean.py            Re-run pipeline steps 3-7 cleanly
│   │
│   ├── module_b/                    ← Module B: Cyber-Physical Health & Thermal Management
│   │   ├── src/
│   │   │   ├── core/                   schemas.py, preprocessor.py, exceptions.py
│   │   │   └── models/                 engine.py, soh_champion.py, thermal_champion.py
│   │   ├── weights/                    Pre-trained model weights (.pt, .joblib)
│   │   ├── data/                       Test splits, sample telemetry JSON
│   │   ├── config/settings.yaml        Thermal thresholds and model config
│   │   └── tests/                      Automated pytest test suite (13 tests)
│   │
│   └── module_c/                    ← Module C: Behavior-Aware BMS (BA-BMS) & Knee Prognostics
│       ├── engine.py                   BABMSEngine wrapper (AI, BSI, Knee Booster)
│       ├── best_xgboost_model.json     Pre-trained Knee-Point XGBoost Booster
│       ├── feature_scaler.pkl          Pre-trained 28-feature StandardScaler
│       ├── knee_detection.py           Piecewise linear fit knee detector
│       ├── knee_final.py               Knee-aware temporal sequence model
│       ├── unified_ensemble.py         Multi-target meta-ensemble training
│       ├── demo_ensemble.py            Visual performance demonstration tool
│       ├── data_integrator.py          Cross-vehicle rank mapping synthesizer
│       ├── improved_data_processing.py Behavioral index feature engineering
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
├── models/                          ← Module A trained model artifacts (62 models)
│   ├── SOC_KNN.pkl                     Best SOC model (R²=0.9958)
│   ├── SOH_XGBoost.pkl                 Best SOH model (R²=0.9672)
│   ├── RUL_GradientBoosting.pkl        Best RUL model (R²=0.9997)
│   ├── Mileage_XGBoost.pkl             Best Mileage model (R²=0.9445)
│   └── scaler_*.pkl                    Feature scalers
│
├── results/                         ← Plots, comparison tables, evaluation reports
└── logs/                            ← System execution logs
```

---

## 🎯 Tri-Pillar Prediction Capabilities

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TRI-PILLAR CAPABILITY MATRIX                                    │
├──────────────────────────────┬──────────────────────────────┬───────────────────────────────────┤
│    MODULE A (Fleet Macro)    │  MODULE B (Thermal / Cyber)  │    MODULE C (Behavior & Knee)     │
├──────────────────────────────┼──────────────────────────────┼───────────────────────────────────┤
│ • State of Charge (SOC)      │ • Multi-Zone Thermal Safety  │ • Driver Aggressiveness (AI)      │
│ • State of Health (SOH)      │ • Spatial-Temporal SOH (DL)  │ • Battery Stress Index (BSI)      │
│ • Remaining Useful Life (RUL)│ • Multi-Zone Fault Alerts    │ • Knee-Point Onset (RUL_to_knee)  │
│ • Mileage per Charge (km)    │ • Composite Health Score     │ • Multi-Target Meta-Ensemble      │
└──────────────────────────────┴──────────────────────────────┴───────────────────────────────────┘
```

### Module A — Fleet-Level EV Predictions
| Task | Target | Best Model | Performance |
|------|--------|-----------|-------------|
| **SOC** | State of Charge (%) | KNN | R² = 0.9958 |
| **SOH** | State of Health (%) | XGBoost | R² = 0.9672 |
| **RUL** | Remaining Useful Life (cycles) | Gradient Boosting | R² = 0.9997 |
| **Mileage** | Range per Charge (km) | XGBoost | R² = 0.9445 |

*Trained on 930MB of real Indian EV fleet telematics data (50M+ records).*

### Module B — Battery Health & Thermal Management
| Task | Architecture | Performance |
|------|-------------|-------------|
| **SOH Deep** | Hybrid 1D-CNN + LSTM (PyTorch) | RMSE = 5.29% |
| **Thermal Safety** | Multi-Zone Random Forest (200 trees) | F1 = 0.997, Acc = 99.71% |
| **Full Diagnosis** | Digital-Twin Composite Score (0-100) | Dual-Pillar Multi-Zone |

*Trained on 53M records from Euler HiLoad commercial EV fleet.*

### Module C — Behavior-Aware BMS & Knee Prognostics
| Task | Architecture | Key Insight |
|------|-------------|-------------|
| **Driver Aggressiveness (AI)** | Multi-Event Weighted Composite Index (0-1) | Smooth drivers retain +4.7% higher SOH |
| **Battery Stress (BSI)** | Thermal & Electrical Stress Mapping | Real-time current/thermal throttle trigger |
| **Knee Prognostics** | XGBoost Booster (28 features) + Scaler | Detects non-linear accelerated aging point |
| **Meta-Ensemble** | Deep BiLSTM + XGBoost Meta-Learner | Simultaneous multi-target health tracking |

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_unified.txt
```

### 2. Check System Readiness
```bash
python run_all.py --check
```

### 3. Start the Unified REST API (11 Endpoints)
```bash
python run_all.py
# API running at: http://localhost:8000
# Interactive Swagger docs: http://localhost:8000/docs
```

### 4. Launch Interactive CLI Prediction System
```bash
python run_all.py --cli
# OR
python cli.py
```

### 5. Run Automated Test Suite (20 Tests)
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
