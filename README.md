# EV Battery Analysis & Prediction System

## 1. Project Overview
This project focuses on building an advanced machine learning pipeline to analyze and predict critical electrical vehicle (EV) battery parameters. By combining diverse data sources including OEM telemetry, device telemetry, trip records, and charge cycles, the system predicts the battery's real-time charge state, long-term degradation, lifespan, and estimated driving range.

The pipeline comprises end-to-end data ingestion, secure pre-processing, data leak prevention, robust feature engineering, and model training evaluated on both Classical Machine Learning and Deep Learning architectures.

---

## 2. Complete Context of the Tasks

The system addresses four primary analytical predictive tasks within EV Battery Management Systems (BMS). Because predicting battery parameters offline can easily suffer from "data leakage" (e.g., using algebraic properties of a target variable to predict the target), each task was heavily structured to learn from underlying causes rather than direct proxy mappings.

### A. State of Charge (SOC) Prediction
* **Objective:** Estimate the instantaneous battery charge in % available.
* **Context:** Predicting SOC helps handle imprecise or faulty SoC measurements from the BMS. The models are trained to map hardware signatures directly to SOC.
* **Constraint:** No rolling SOC data or charge states are passed to the model—doing so yields R² near 1.0 purely by leakage. Models strictly depend on causal hardware features.

### B. State of Health (SOH) Prediction
* **Objective:** Predict the overarching battery degradation over time, commonly denoted as a percentage (100% being brand new).
* **Context:** Estimates capacity fade securely decoupling from short-term SOC changes. SOH is critical for warranty analytics and predictive maintenance.

### C. Remaining Useful Life (RUL) Prediction
* **Objective:** Predict how many nominal charge cycles (or driving capacity equivalents) remain until the battery degrades below an acceptable threshold.
* **Context:** RUL helps fleet managers phase out deteriorating batteries efficiently. 

### D. Mileage per Charge
* **Objective:** Predict the realistic range an EV can achieve on a full charge based entirely on external mapping context and vehicle behavior.
* **Context:** Essential for dynamic route optimization. Excludes direct measurements like `soc_drain`, driving models strictly from environmental conditions and trip characteristics.

---

## 3. Feature Engineering Strategy

Feature engineering was executed iteratively using combinations of OEM Telemetry, alerting systems, and trip metrics. The fundamental driving ethos behind the pipeline was strict prevention of **Data Leakage**.

* **Trip-Based Features:** From granular point-to-point journey data, features capturing driver behavior and vehicle performance were mapped:
  * *Created:* `soc_drain_rate`, `energy_efficiency`, `trip_intensity` (avg speed × duration), `speed_ratio` (avg / max speed), and `distance_per_soc_drop`.
  * *Leakage Prevention:* For the Mileage task, values like `soc_drain` and `soc_drain_rate` were explicitly dropped to force the system to learn from energy profiles rather than simple math equations.
* **Telemetry & Hardware Features:** Derived directly from physical properties of the battery and circuit.
  * *Created:* `voltage_deviation` (difference from nominal 72V), `temp_stress_index` (normalized penalty for extreme temperature deviations from optimal 25°C), and `abs_current` (absolute magnitude).
* **Long-Term Degradation Signals:** Derived from aggregated charge records indicating the aging curve.
  * *Created:* `degradation_factor` (deviation from baseline/fleet average miles-per-charge), `charge_frequency` (usage rate over time), and rolling histories of mileage drops (e.g., `miles_per_charge_rolling_5`).

---

## 4. Models Trained

A broad spectrum of robust predictive models were trained, crossing both classical ensemble methods and sequence-based Deep Learning networks:

### Classical Machine Learning
* Random Forest Regressor
* Gradient Boosting Regressor
* eXtreme Gradient Boosting (XGBoost)
* Extra Trees Regressor
* Support Vector Regressor (SVR)
* K-Nearest Neighbors (KNN), Decision Trees, Lasso & Ridge Regressors.

### Deep Learning
* Feed Forward Artificial Neural Networks (ANN)
* Long Short-Term Memory Networks (LSTM)
* Gated Recurrent Units (GRU)
* 1D-Convolutional Neural Networks (CNN-1D)
* Hybrid CNN-LSTM Architecture 

> All model hyper-parameter tuning was tracked via Randomized Search Cross-Validation over multiple folds. DL models incorporated sequence batching, dropout regularization, and early stopping to mitigate overfitting. 

---

## 5. Best Models Achieved

Following evaluation against RMSE, MAE, R², and MAPE, tree-based ensemble methods successfully beat out Deep Learning algorithms across the board, providing robust, interpretable predictions on tabular subsets. 

| Task | Best Model Acquired | Error Profile (RMSE) | Mean Absolute Error (MAE) | R² Score | Fit Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SOC** | Random Forest | 1.1457 | 0.4177 | 0.9973 | Underfitting |
| **SOH** | Extra Trees | 0.2001 | 0.0147 | 0.9990 | Underfitting |
| **RUL** | Random Forest | 0.0455 | 0.0262 | 1.0000 | Underfitting |
| **Mileage** | XGBoost | 7.4424 | 3.7726 | 0.9466 | Underfitting |

### Detailed Model Performances per Task

Below is the exhaustive list of classical Machine Learning models evaluated for each specific prediction task, alongside their respective R² and RMSE results, sorted by descending performance.

**1. State of Charge (SOC) - 8 Models Trained:**
* **RandomForest:** R² = 0.9973 | RMSE = 1.1457
* **ExtraTrees:** R² = 0.9970 | RMSE = 1.2064
* **GradientBoosting:** R² = 0.9969 | RMSE = 1.2231
* **KNN:** R² = 0.9964 | RMSE = 1.3215
* **XGBoost:** R² = 0.9952 | RMSE = 1.5281
* **DecisionTree:** R² = 0.9915 | RMSE = 2.0442
* **Ridge:** R² = 0.9603 | RMSE = 4.4132
* **Lasso:** R² = 0.9602 | RMSE = 4.4143

**2. State of Health (SOH) - 8 Models Trained:**
* **ExtraTrees:** R² = 0.9990 | RMSE = 0.2001
* **RandomForest:** R² = 0.9981 | RMSE = 0.2733
* **GradientBoosting:** R² = 0.9823 | RMSE = 0.8356
* **XGBoost:** R² = 0.9725 | RMSE = 1.0417
* **KNN:** R² = 0.9671 | RMSE = 1.1389
* **DecisionTree:** R² = 0.9614 | RMSE = 1.2339
* **Ridge:** R² = 0.3313 | RMSE = 5.1365
* **Lasso:** R² = 0.3313 | RMSE = 5.1365

**3. Remaining Useful Life (RUL) - 9 Models Trained:**
* **RandomForest:** R² = 1.0000 | RMSE = 0.0455
* **ExtraTrees:** R² = 1.0000 | RMSE = 0.0466
* **Lasso:** R² = 1.0000 | RMSE = 0.0710
* **DecisionTree:** R² = 1.0000 | RMSE = 0.1033
* **Ridge:** R² = 1.0000 | RMSE = 0.1068
* **GradientBoosting:** R² = 1.0000 | RMSE = 0.1617
* **XGBoost:** R² = 1.0000 | RMSE = 0.4800
* **SVR:** R² = 0.9991 | RMSE = 2.4434
* **KNN:** R² = 0.9950 | RMSE = 5.9283

**4. Mileage per Charge - 9 Models Trained:**
* **XGBoost:** R² = 0.9466 | RMSE = 7.4424
* **GradientBoosting:** R² = 0.9455 | RMSE = 7.5154
* **RandomForest:** R² = 0.9447 | RMSE = 7.5695
* **ExtraTrees:** R² = 0.9445 | RMSE = 7.5825
* **DecisionTree:** R² = 0.9193 | RMSE = 9.1437
* **SVR:** R² = 0.8598 | RMSE = 12.0571
* **KNN:** R² = 0.8236 | RMSE = 13.5222
* **Ridge:** R² = 0.7453 | RMSE = 16.2499
* **Lasso:** R² = 0.7452 | RMSE = 16.2521

---

## 6. Feature Importance & Selected Features

Based on post-hoc SHAP Value evaluations (Shapley Additive exPlanations), the following variables strictly guided the top-performing algorithms:

### ⚡ State of Charge (SOC)
* **Features Selected:** `battery_voltage`, `battery_temp`, `battery_current`, `abs_current`, `is_charging`, `odometer_diff`, `voltage_deviation`, `temp_stress_index`, temporal flags (e.g., `hour`, `is_weekend`), and identifiers. 
* **Top Important Features (by SHAP):**
  1. `battery_voltage` (Dominant indicator of capacity)
  2. `voltage_deviation`
  3. `odometer`
  4. `abs_current`
  5. `battery_current`

### 🔋 State of Health (SOH)
* **Features Selected:** `battery_voltage`, `battery_temp`, `odometer`, `odometer_diff`, `charge_cycle_count`, `mile_avg`, `miles_per_charge`, `days_in_service`, `degradation_factor`, and `temp_stress_index`.
* **Top Important Features (by SHAP):**
  1. `odometer` (Consistent correlation with battery fade)
  2. `abs_current`
  3. `battery_temp`
  4. `battery_current`
  5. `battery_voltage`

### ⏳ Remaining Useful Life (RUL)
* **Features Selected:** `odometer`, `soc_at_charge`, `mile_avg`, `miles_per_charge`, `days_in_service`, `degradation_factor`, `charge_frequency`, `soh_mean`, and temporal rolling variants of `miles_per_charge`.
* **Top Important Features (by SHAP):**
  1. `charge_frequency` (Primary predictor of rapid life loss)
  2. `miles_per_charge_rolling_3`
  3. `degradation_factor`
  4. `miles_per_charge_rolling_5`

### 🛣️ Mileage per Charge
* **Features Selected:** `run_kms`, `avg_speed`, `max_speed`, `trip_duration_hrs`, `stoppage_count`, `energy_efficiency`, `trip_intensity`, `speed_ratio`, `stoppage_density`, `energy_utilized`, demographic variables (`city_encoded`).
* **Top Important Features (by SHAP):**
  1. `energy_efficiency` (Critical for calculating viable distance limit)
  2. `run_kms`
  3. `city_encoded`
  4. `energy_utilized`
  5. `max_speed`
