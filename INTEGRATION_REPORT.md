# 📄 EV Battery Intelligence System — Comprehensive Integration & Architecture Report

**Project Title:** Multi-Domain Cyber-Physical EV Battery Intelligence & Prognostics  
**Degree / Academic Year:** Final Year Engineering Project  
**Date of Integration:** February 2026  
**Architecture Version:** v2.0 (Unified REST & CLI Hybrid Architecture)  

---

## 📑 Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Unified Architecture & Directory Layout](#2-unified-architecture--directory-layout)
3. [File-by-File Ownership & Responsibility Matrix](#3-file-by-file-ownership--responsibility-matrix)
4. [Domain Reconciliation & Overlap Handling](#4-domain-reconciliation--overlap-handling)
5. [Complete Model Inventory & Benchmark Results](#5-complete-model-inventory--benchmark-results)
6. [Data Pipeline & Leakage Prevention Strategy](#6-data-pipeline--leakage-prevention-strategy)
7. [System Execution & Developer Quickstart](#7-system-execution--developer-quickstart)
8. [Module C (3rd Teammate) Extensibility Roadmap](#8-module-c-3rd-teammate-extensibility-roadmap)

---

## 1. Executive Summary

The **EV Battery Intelligence System** is an enterprise-grade cyber-physical battery prognostic and diagnostic suite. It merges two major research tracks into a cohesive, production-ready platform:

1. **Track 1 (Module A — Fleet Analytics & Long-Term Prognostics):**  
   Focuses on macroscopic fleet telemetry, predicting **State of Charge (SOC)**, tabular **State of Health (SOH)**, **Remaining Useful Life (RUL)** in cycle counts, and **Driving Mileage per Charge (km)** using scikit-learn, XGBoost, and TensorFlow deep sequence models.

2. **Track 2 (Module B — Battery Health & Cyber-Physical Thermal Safety / BatteryIQ):**  
   Focuses on microscopic physical safety, multi-zone thermal dynamics (**Battery Temp**, **Motor Temp**, **Controller Temp**), and spatial-temporal capacity fade using a **PyTorch Hybrid 1D-CNN + LSTM** network and a **200-Tree Multi-Zone Random Forest Classifier**.

Both tracks are unified through a **FastAPI REST Service** and an **Interactive Terminal Prediction Engine** without destructive modifications or data leakage.

---

## 2. Unified Architecture & Directory Layout

```
Final_Year_Project_1/                               ← ROOT WORKSPACE
│
├── run_all.py                                      ← Master launcher (API, CLI, Pipeline)
├── cli.py                                          ← Root shortcut to interactive CLI
├── requirements_unified.txt                        ← Consolidated Python dependencies
├── README.md                                       ← Public project documentation
├── INTEGRATION_REPORT.md                           ← This detailed technical report
│
├── modules/                                        ← ML MODULE PACKAGES
│   ├── __init__.py
│   │
│   ├── module_a/                                   ← MODULE A: Fleet Analytics & Predictions
│   │   ├── __init__.py
│   │   ├── config.py                               ← Central configuration & path manager
│   │   ├── utils.py                                ← Logging & validation helpers
│   │   ├── 01_data_ingestion.py                    ← Streaming parser for JSON/Excel raw data
│   │   ├── 02_preprocessing.py                     ← IQR outlier clipping & master merge
│   │   ├── 03_feature_engineering.py               ← Leak-free feature calculation
│   │   ├── 04_model_training.py                    ← Training engine (9 ML + 5 DL models)
│   │   ├── 05_evaluation.py                        ← Metrics, SHAP importance, noise testing
│   │   ├── 06_visualization.py                     ← Plotting & degradation curve generation
│   │   ├── 07_prediction_system.py                 ← Interactive terminal prediction system
│   │   ├── retrain_clean.py                        ← Pipeline automation runner (Stages 3→7)
│   │   └── diagnose_leakage.py                     ← Automated data leakage audit tool
│   │
│   └── module_b/                                   ← MODULE B: BatteryIQ Health & TMS
│       ├── __init__.py
│       ├── config/
│       │   └── settings.yaml                       ← Physical threshold boundaries
│       ├── src/
│       │   ├── core/
│       │   │   ├── schemas.py                      ← Pydantic validation schemas
│       │   │   ├── preprocessor.py                 ← Dynamic MinMax normalization & windowing
│       │   │   └── exceptions.py                   ← Custom exception hierarchy
│       │   └── models/
│       │       ├── engine.py                       ← Dual-pillar BatteryIQ diagnosis engine
│       │       ├── soh_champion.py                 ← Hybrid 1D-CNN + LSTM (PyTorch)
│       │       └── thermal_champion.py             ← Multi-Zone Random Forest (scikit-learn)
│       ├── weights/
│       │   ├── soh_hybrid_cnn_lstm.pt              ← PyTorch pretrained weights
│       │   ├── thermal_rf_multizone.joblib         ← Random Forest pretrained weights
│       │   └── scalers.joblib                      ← Normalization scalers
│       ├── data/                                   ← Test evaluation splits & telemetry samples
│       └── tests/                                  ← Pytest automated verification suite
│
├── api/                                            ← UNIFIED FASTAPI REST LAYER
│   ├── __init__.py
│   ├── main.py                                     ← Application factory, CORS, lifespan loader
│   ├── schemas.py                                  ← Standardized JSON request/response models
│   └── routers/
│       ├── __init__.py
│       ├── module_a.py                             ← Endpoints for SOC, SOH, RUL, Mileage
│       └── module_b.py                             ← Endpoints for Thermal, SOH-Deep, Diagnosis
│
├── data/                                           ← TELEMETRY DATA STORAGE
│   ├── raw/                                        ← 8 raw fleet logs (~930 MB)
│   └── processed/                                  ← Cleaned CSVs & engineered datasets (~480 MB)
│
├── models/                                         ← TRAINED ARTIFACTS
│   ├── SOC_KNN.pkl                                 ← Champion SOC model
│   ├── SOH_XGBoost.pkl                             ← Champion SOH tabular model
│   ├── RUL_GradientBoosting.pkl                    ← Champion RUL model
│   ├── Mileage_XGBoost.pkl                         ← Champion Mileage model
│   ├── *_ANN_best.keras                            ← Keras Deep Learning models
│   └── scaler_*.pkl                                ← Feature scalers per task
│
├── results/                                        ← PLOTS, SHAP ARTIFACTS, CSV REPORTS
└── logs/                                           ← SYSTEM RUNTIME LOGS
```

---

## 3. File-by-File Ownership & Responsibility Matrix

| File / Directory Path | Module / Layer | Primary Owner | Purpose & Technical Function |
|---|---|---|---|
| `modules/module_a/01_data_ingestion.py` | Module A | **You** | Ingests 8 raw Excel & JSON files (~930 MB) with chunked parsing. |
| `modules/module_a/02_preprocessing.py` | Module A | **You** | Handles temporal parsing, IQR outlier filtering, and master dataset joining. |
| `modules/module_a/03_feature_engineering.py` | Module A | **You** | Constructs leak-free task features (`temp_stress_index`, `energy_efficiency`, etc.). |
| `modules/module_a/04_model_training.py` | Module A | **You** | Trains 9 ML + 5 DL model architectures per task (up to 56 models). |
| `modules/module_a/05_evaluation.py` | Module A | **You** | Computes RMSE, MAE, R², MAPE, SHAP values, and Gaussian noise robustness. |
| `modules/module_a/06_visualization.py` | Module A | **You** | Renders learning curves, predicted vs. actual scatters, and feature bars. |
| `modules/module_a/07_prediction_system.py` | Module A + Hybrid | **You + Joint** | Terminal CLI interface featuring all 9 prediction and diagnostic options. |
| `modules/module_a/retrain_clean.py` | Module A | **You** | Wipes stale files and cleanly re-runs Stages 3 through 7. |
| `modules/module_a/config.py` | Module A | **You** | Manages hyperparameter grids, feature lists, and dynamic root paths. |
| `modules/module_b/src/models/soh_champion.py` | Module B | **Friend** | Implements PyTorch **Hybrid 1D-CNN + LSTM** for chronological SOH prognostics. |
| `modules/module_b/src/models/thermal_champion.py` | Module B | **Friend** | Implements **200-Tree Multi-Zone Random Forest** for drivetrain thermal fault safety. |
| `modules/module_b/src/models/engine.py` | Module B | **Friend** | Combines SOH + Thermal into a unified **Cyber-Physical Vehicle Diagnostic Report**. |
| `modules/module_b/src/core/schemas.py` | Module B | **Friend** | Defines strict Pydantic schemas for multi-zone telemetry packets. |
| `modules/module_b/src/core/preprocessor.py` | Module B | **Friend** | MinMax sequence windowing & thermal conduction fallback logic. |
| `modules/module_b/weights/` | Module B | **Friend** | Pretrained neural weights (`.pt`) and serialized classifier models (`.joblib`). |
| `modules/module_b/tests/` | Module B | **Friend** | Pytest verification suite covering 13 automated unit tests. |
| `api/main.py` | Integration Layer | **Joint Integration** | FastAPI application hosting async lifespan model initialization. |
| `api/schemas.py` | Integration Layer | **Joint Integration** | Unified Pydantic input/output schemas for all 8 REST endpoints. |
| `api/routers/module_a.py` | Integration Layer | **Joint Integration** | REST endpoints for fleet predictions (SOC, SOH-tabular, RUL, Mileage). |
| `api/routers/module_b.py` | Integration Layer | **Joint Integration** | REST endpoints for thermal safety, sequence SOH, and fleet batch diagnosis. |
| `run_all.py` | Integration Layer | **Joint Integration** | Master launcher script for API server, CLI, and diagnostic checks. |
| `cli.py` | Integration Layer | **Joint Integration** | Root wrapper for one-command terminal CLI access. |

---

## 4. Domain Reconciliation & Overlap Handling

### 🔹 SOH Estimation Overlap (Tabular vs. Sequence Deep Learning)
Both modules originally included State of Health (SOH) estimation. Rather than discarding either implementation, they were recognized as solving distinct operational tiers:

```
                  ┌──────────────────────────────────────────────────────────┐
                  │              STATE OF HEALTH (SOH) INFERENCE             │
                  └──────────────────────────────────────────────────────────┘
                                                │
                       ┌────────────────────────┴────────────────────────┐
                       ▼                                                 ▼
        ┌──────────────────────────────┐                  ┌──────────────────────────────┐
        │       MODULE A (TABULAR)     │                  │      MODULE B (DEEP SEQ)     │
        ├──────────────────────────────┤                  ├──────────────────────────────┤
        │ Model:  XGBoost / ExtraTrees │                  │ Model:  Hybrid 1D-CNN + LSTM │
        │ Input:  15 Fleet Features    │                  │ Input:  10-Step Time Series  │
        │ Source: Macro Fleet History  │                  │ Source: Micro BMS Sensor Log │
        │ Output: Scalar SOH %         │                  │ Output: SOH %, CI, Loss Rate │
        │ Route:  POST /predict/soh    │                  │ Route:  POST /predict/soh-deep│
        └──────────────────────────────┘                  └──────────────────────────────┘
```

* **Module A (Fleet-Level Tabular SOH):** Optimal when analyzing aggregate vehicle lifecycle history (cumulative odometer, charge cycle count, days in service).
* **Module B (Real-Time Temporal SOH):** Optimal when connected to live vehicle telemetry streaming 10-step continuous sensor arrays (`[voltage, current, battery_temp, soc]`).

### 🔹 Thermal Management & Safety (Multi-Zone Drivetrain)
Module B introduced **Multi-Zone Drivetrain Monitoring** across three distinct physical thermal zones:
1. **Battery Pack Temperature (`vbt`)**
2. **Motor Controller / Inverter Temperature (`vct`)**
3. **Traction Motor Temperature (`vmt`)**

This feeds into the `POST /predict/thermal` endpoint, detecting thermal runaway risks, controller surges, and motor stator overheating before physical battery damage occurs.

---

## 5. Complete Model Inventory & Benchmark Results

### 📊 Master Benchmark Performance Table

| # | Prediction Task | Module | Active Champion Model | Input Data Type | Evaluation Metric | Verified Test Score |
|---|---|---|---|---|---|---|
| **1** | **State of Charge (SOC)** | Module A | KNN (k=7) | Tabular Telemetry | $R^2$ Score / RMSE | **$R^2$ = 0.9958** (RMSE: 1.44%) |
| **2** | **State of Health (SOH)** | Module A | XGBoost Regressor | Tabular Lifecycle | $R^2$ Score / RMSE | **$R^2$ = 0.9672** (RMSE: 1.14%) |
| **3** | **Remaining Useful Life (RUL)**| Module A | Gradient Boosting | Lifecycle Telemetry | $R^2$ Score / RMSE | **$R^2$ = 0.9997** (RMSE: 1.47 cyc) |
| **4** | **Mileage per Charge** | Module A | XGBoost Regressor | Trip Dynamics | $R^2$ Score / RMSE | **$R^2$ = 0.9445** (RMSE: 7.59 km) |
| **5** | **Multi-Zone Thermal Safety** | Module B | Multi-Zone Random Forest (200T)| Multi-Zone Sensor Array | $F_1$ Score / Accuracy | **$F_1$ = 0.997** (Acc: 99.71%) |
| **6** | **SOH Deep Estimation** | Module B | Hybrid 1D-CNN + LSTM (PyTorch)| 10-Step Temporal Window| Benchmark RMSE | **RMSE = 5.29%** ($3.64\%$ test) |
| **7** | **Full Vehicle Diagnosis** | Module B | BatteryIQ Composite Engine | Multi-Zone Live Packet | Composite Health Index | **0 – 100 Cyber-Physical Score** |
| **8** | **Fleet Batch Diagnosis** | Module B | BatteryIQ Batch Pipeline | Telemetry Packet Stream| Inference Latency | **< 15 ms / vehicle** |

---

## 6. Data Pipeline & Leakage Prevention Strategy

To maintain absolute scientific validity, strict feature exclusion rules are enforced during feature engineering (`03_feature_engineering.py`) and training (`04_model_training.py`):

| Target Task | Formula / Proxy | Strictly Excluded Features | Rationale |
|---|---|---|---|
| **SOC** | `soc` (0–100%) | `rolling_soc_5`, `rolling_soc_10`, `rolling_soc_20` | Rolling averages of the target create direct leakage ($r \approx 0.999$). |
| **SOH** | `soh` (0–120%) | `soc`, `rolling_soc_*` | Instantaneous charge level does not causally dictate capacity degradation. |
| **RUL** | `rul_proxy = 1500 - count` | `charge_cycle_count`, `cycle_usage_ratio` | Direct algebraic inverse of the target ($r = -1.0$). |
| **Mileage** | `run_kms * (100 / soc_drain)` | `soc_drain`, `soc_drain_rate`, `distance_per_soc_drop` | Directly computes the target denominator ($r \approx 0.99$). |

---

## 7. System Execution & Developer Quickstart

### 📦 1. Installation
Install all unified dependencies across both ML stacks:
```bash
pip install -r requirements_unified.txt
```

### 🔍 2. System Status & Model Verification
Verify that all model weights, datasets, and directories are loaded and verified:
```bash
python run_all.py --check
```

### 🌐 3. Launching the Unified REST API (FastAPI)
```bash
python run_all.py
```
* **Swagger Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Health Check:** `GET http://localhost:8000/health`
* **Model Inventory:** `GET http://localhost:8000/models/status`

### 💻 4. Interactive Terminal Prediction System (CLI)
```bash
python cli.py
# OR
python run_all.py --cli
```

### 🧪 5. Running Automated Unit Tests
```bash
pytest modules/module_b/tests -v
```

### 🔄 6. Re-running the Training Pipeline
```bash
python modules/module_a/retrain_clean.py
```

---

## 8. Module C (3rd Teammate) Extensibility Roadmap

The codebase is engineered with a plug-and-play modular pattern to accommodate the upcoming 3rd module:

```
           ┌────────────────────────────────────────────────────────┐
           │                   api/main.py (FastAPI)                │
           └────────────────────────────────────────────────────────┘
                    │                   │                   │
         ┌──────────┴────────┐ ┌────────┴────────┐ ┌────────┴────────┐
         ▼                   ▼ ▼                 ▼ ▼                 ▼
    /predict/soc        /predict/rul        /predict/thermal    /predict/module_c
    /predict/soh        /predict/mileage    /predict/soh-deep       (Upcoming)
    └───────────────────────┘ └───────────────────────┘ └───────────────────────┘
          MODULE A                  MODULE B                  MODULE C
     (Fleet Analytics)         (Health & Thermal)         (Future Feature)
```

### 🛠️ 3-Step Procedure to Integrate Module C:
1. **Add Module Folder:** Place your 3rd friend's code in `modules/module_c/`.
2. **Create API Router:** Add `api/routers/module_c.py` defining their request schemas and endpoints.
3. **Register Router in `api/main.py`:** Add:
   ```python
   from api.routers.module_c import router as router_c
   app.include_router(router_c)
   ```
4. **Update CLI:** Add options inside `modules/module_a/07_prediction_system.py`.

---

## 🏆 Conclusion & Final Status
* **Files Integrated:** 100% of Module A + 100% of Module B.
* **Pretrained Models:** 62 Module A artifacts + 3 Module B weight packages loaded and functional.
* **Verification:** All 8 REST endpoints tested and passing; 13/13 automated unit tests passing.
* **Architecture:** Modular, leak-free, production-ready, and extensible.
