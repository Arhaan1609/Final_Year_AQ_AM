# EV Battery Intelligence System
### Unified Final Year Project — ML & DL-Based Electric Vehicle Battery Analysis

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/sklearn-Module%20A-orange)](https://scikit-learn.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-Module%20B-red)](https://pytorch.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-green)](https://fastapi.tiangolo.com)

---

## 🗂️ Project Structure

```
Final_Year_Project_1/
│
├── run_all.py                       ← Single entry point (API + CLI launcher)
├── cli.py                           ← Shortcut to interactive CLI
├── requirements_unified.txt         ← All dependencies (both modules)
│
├── modules/                         ← All ML modules
│   ├── module_a/                    ← Module A: Fleet Prediction Pipeline
│   │   ├── config.py                   Central config (paths, features, hyperparams)
│   │   ├── utils.py                    Shared utilities
│   │   ├── 01_data_ingestion.py        Load raw Excel + JSON fleet data
│   │   ├── 02_preprocessing.py         Clean, clip outliers, merge datasets
│   │   ├── 03_feature_engineering.py   Build leak-free feature sets
│   │   ├── 04_model_training.py        Train 9 ML + 5 DL models per task
│   │   ├── 05_evaluation.py            RMSE/MAE/R² + SHAP + robustness tests
│   │   ├── 06_visualization.py         Generate all plots
│   │   ├── 07_prediction_system.py     Interactive CLI (9 prediction options)
│   │   ├── retrain_clean.py            Re-run pipeline steps 3-7 cleanly
│   │   └── diagnose_leakage.py         Leakage detection utility
│   │
│   └── module_b/                    ← Module B: Battery Health & Thermal Management
│       ├── src/
│       │   ├── core/                   schemas.py, preprocessor.py, exceptions.py
│       │   └── models/                 engine.py, soh_champion.py, thermal_champion.py
│       ├── weights/                    Pre-trained model weights (.pt, .joblib)
│       ├── data/                       Test splits, sample telemetry JSON
│       ├── config/settings.yaml        Thresholds and model config
│       └── tests/                      Automated test suite (pytest)
│
├── api/                             ← Unified REST API (FastAPI)
│   ├── main.py                         App with all 8 endpoints
│   ├── schemas.py                      Pydantic request/response models
│   └── routers/
│       ├── module_a.py                 SOC / SOH / RUL / Mileage endpoints
│       └── module_b.py                 Thermal / SOH-Deep / Diagnose endpoints
│
├── data/
│   ├── raw/                         ← Raw fleet data (930MB — Excel + JSON)
│   └── processed/                   ← Cleaned CSVs + feature sets (~480MB)
│
├── models/                          ← Trained model artifacts
│   ├── SOC_RandomForest.pkl            Best SOC model (R²=0.9973)
│   ├── SOH_ExtraTrees.pkl              Best SOH model (R²=0.9990)
│   ├── RUL_RandomForest.pkl            Best RUL model (R²=1.0000)
│   ├── Mileage_XGBoost.pkl             Best Mileage model (R²=0.9466)
│   ├── *_ANN_best.keras                Deep learning models (all 4 tasks)
│   └── scaler_*.pkl                    Feature scalers
│
├── results/
│   ├── plots/                       ← Training curves, scatter plots, SHAP charts
│   └── reports/                     ← model_comparison.csv, FINAL_REPORT.md
│
└── logs/                            ← Pipeline execution logs
```

---

## 🎯 Prediction Capabilities

### Module A — Fleet-Level EV Predictions
| Task | Target | Best Model | Performance |
|------|--------|-----------|-------------|
| **SOC** | State of Charge (%) | Random Forest | R² = 0.9973 |
| **SOH** | State of Health (%) | Extra Trees | R² = 0.9990 |
| **RUL** | Remaining Useful Life (cycles) | Random Forest | R² = 1.0000 |
| **Mileage** | Range per Charge (km) | XGBoost | R² = 0.9466 |

Trained on **930MB** of real Indian EV fleet telematics data (50M+ records).

### Module B — Battery Health & Thermal Management
| Task | Architecture | Performance |
|------|-------------|-------------|
| **SOH Deep** | Hybrid 1D-CNN + LSTM (PyTorch) | RMSE = 5.29% |
| **Thermal Safety** | Multi-Zone Random Forest (200 trees) | F1 = 0.997 |
| **Full Diagnosis** | Composite health score (SOH + Thermal) | — |

Trained on **53M records** from Euler HiLoad commercial EV fleet.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies (first time only)
pip install -r requirements_unified.txt

# 2. Run the full data pipeline (Module A — first time setup)
python modules/module_a/01_data_ingestion.py
python modules/module_a/02_preprocessing.py
python modules/module_a/retrain_clean.py    # Steps 3-7

# 3. Check all systems are ready
python run_all.py --check

# 4a. Start the Unified REST API
python run_all.py
# → API:  http://localhost:8000
# → Docs: http://localhost:8000/docs

# 4b. Or use the interactive CLI
python cli.py                # shortcut
python run_all.py --cli      # via launcher
```

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API info |
| `GET` | `/health` | System health + model status |
| `GET` | `/models/status` | Full model inventory |
| `POST` | `/predict/soc` | State of Charge prediction |
| `POST` | `/predict/soh` | State of Health (tabular) |
| `POST` | `/predict/rul` | Remaining Useful Life |
| `POST` | `/predict/mileage` | Mileage per charge |
| `POST` | `/predict/thermal` | Multi-zone thermal fault detection |
| `POST` | `/predict/soh-deep` | SOH deep estimation (CNN-LSTM) |
| `POST` | `/diagnose/vehicle` | Full dual-pillar vehicle diagnosis |
| `POST` | `/diagnose/batch` | Fleet batch diagnosis (up to 500) |

---

## 🔧 Module A Pipeline (Steps 1-7)

```bash
# Full pipeline from scratch
python modules/module_a/01_data_ingestion.py     # Load raw data → data/processed/
python modules/module_a/02_preprocessing.py      # Clean + merge
python modules/module_a/03_feature_engineering.py # Leak-free features
python modules/module_a/04_model_training.py     # Train 9ML + 5DL per task
python modules/module_a/05_evaluation.py         # Evaluate + SHAP
python modules/module_a/06_visualization.py      # Generate plots

# OR re-run steps 3-7 cleanly (wipes old models first)
python modules/module_a/retrain_clean.py
```

---

## 🔬 Module B Testing

```bash
# Run the official test suite
pytest modules/module_b/tests -v

# Run Module B benchmark validation
cd modules/module_b
python -m src.cli.main benchmark
```

---

## 📦 Dependencies

```bash
pip install -r requirements_unified.txt
```

Core: `scikit-learn`, `xgboost`, `tensorflow`, `torch`, `fastapi`, `pydantic`, `numpy`, `pandas`

---

## 👥 Contributors

| Module | Owner | Focus |
|--------|-------|-------|
| Module A (pipeline) | **You** | SOC / SOH / RUL / Mileage prediction + full data pipeline |
| Module B (BatteryIQ) | **Friend** | Thermal fault detection + SOH deep estimation |
| Unified API + CLI | **Integration** | REST API + extended CLI |
