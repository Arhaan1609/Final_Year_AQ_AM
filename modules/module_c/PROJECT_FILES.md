# EV Battery Degradation & BA-BMS Project Files

This document provides a map of the core files retained in the repository for pushing to Git. Redundant logs, JSON outputs, and intermediate pipeline models have been cleaned up to keep the repository streamlined.

## 核心 / Core Output Files
These files represent the final iterations of the Multi-Model, Multi-Target Ensemble Pipeline.

- **`run_final_pipeline.py`**
  - Contains the **final optimized deep learning pipeline** (CNN-BiLSTM variations with Attention and Quantile loss). This script successfully combines multiple metrics and layers to measure battery remaining useful life (`RUL_to_knee`).
  
- **`unified_ensemble.py`**
  - Contains the **final Meta-Ensemble implementation** combining both XGBoost (tabular) and LSTM/GRU Deep Learning models. 
  - *Note:* This is the file that integrates both models together (RUL & SOH tracking) preventing severe data loss and resolving earlier metric discrepancies.

- **`demo_ensemble.py`**
  - A professional terminal-based demonstration tool displaying performance metrics and generating comparative visual plots summarizing the ensemble's predictions.

## 辅助脚本 / Auxiliary Modules
These scripts handle specific parts of the project architecture such as data preprocessing and unified visualization.

- **`improved_pipeline.py` & `optimized_pipeline.py`**
  - Earlier successful iterations/optimizations of the pipeline leading up to the final model.
  
- **`knee_detection.py` & `knee_final.py`** & **`knee_advanced_pipeline.py`**
  - Scripts dedicated specifically to modeling and isolating the "Knee Point" in battery degradation curves.
  
- **`data_integrator.py` & `improved_data_processing.py`**
  - Unified data loading, preprocessing, and sequential feature engineering scripts that handle time-series formatting of the BMS logs.
  
- **`visualization_improved.py` & `final_viz.py` & `advanced_viz.py`**
  - Various Matplotlib & Seaborn utilities for rendering evaluation charts (such as R² plots, feature importance, and error distributions) directly into the `plots/` directory.

## 文档 / Project Documentation
- **`PROJECT_REPORT.md`** - Comprehensive technical analysis detailing the Behavior-Aware Battery Management System (BA-BMS) framework, insights, and findings.
- **`MODULE_ARCHITECTURE.md`** - Architectural breakdown of the backend processing logic.
- **`DATA_PREPROCESSING_PIPELINE.md` & `PREPROCESSING_BLUEPRINT.md`** - Explain the transformations applied to raw BMS telemetry to prepare it for deep learning.
- **`DATA_SPECIFICATIONS.md`** - Expected input feature lists and metadata schemas.

> **Important:** The `data/` and `plots/` directories, along with temporary log textual files and virtual environments, are excluded gracefully via `.gitignore` to prevent GitHub size limitations (`GH001`) from triggering.
