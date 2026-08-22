# 📊 EV Battery Intelligence Platform — Comprehensive Evaluation Methodology & SOH Generalization Analysis

> **Academic & Defense Reference**: This document provides an exhaustive, transparent, and mathematically rigorous breakdown of the model evaluation paradigms, detailing the progression from **Row-Level Leaky Baselines** to **Zero-Leakage Group-Aware Generalization**, **History-Aware Feature Extraction**, **Calibrated-Baseline BMS Framing**, and **19-Fold Leave-One-Chassis-Out Cross Validation (LOGO-CV)**.

---

## 🔍 1. The Core Scientific Problem: Entity & Temporal Data Leakage

In battery telematics, high-frequency CAN frames stream from a finite fleet of commercial electric vehicles.

### ⚠️ A. Row-Level Random Split (Traditional / Leaky)
Standard machine learning pipelines frequently use:
```python
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```
* **Why it leaks**: Because an individual vehicle (e.g. `GJ05CV6564`) generates consecutive rows at $t_0, t_1, t_2, \dots$, random shuffling places rows from the **exact same physical battery pack** in both the training set and the test set.
* **The consequence**: The model memorizes that specific vehicle's unique manufacturing capacity baseline, internal impedance offset, and sensor bias. When evaluated on test rows from that same vehicle at $t+1$, the model outputs hyper-optimistic metrics ($R^2 \ge 0.98$, $\text{MAE} < 0.6\%$).

### 🛡️ B. Vehicle Group-Aware Split (Strict Zero-Leakage)
To measure true real-world generalization to **new, unseen vehicles**, datasets are partitioned using **Group-Aware Splitting**:
```python
gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
train_idx, test_idx = next(gss.split(X, y, groups=df["chassis_no"]))
```
* **Strict Guarantee**: 100% of rows belonging to test vehicles are completely held out ($\text{train\_chassis} \cap \text{test\_chassis} = \emptyset$). The model has **never seen any data** from those physical battery packs during training.

---

## 📈 2. Module A Task Evaluation Matrix (Zero-Leakage Baseline)

| Task & Target | Algorithm | Row-Split $R^2$ (Leaked) | Group-Split $R^2$ (Realistic) | Row-Split MAE | Group-Split MAE | Generalization Analysis |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **SOC** (%) | **Lasso (Champion)** | `0.9958` | **`0.9873`** | `0.42 %` | **`1.78 %`** | **Highly Generalizable**: Open-circuit voltage (OCV), current, and temperature physical relationships hold across unseen chassis. |
| **SOC** (%) | **XGBoost** | `0.9942` | **`0.9765`** | `0.58 %` | **`2.28 %`** | Non-linear tree splits capture temperature-dependent polarization curves. |
| **SOC** (%) | **RandomForest** | `0.9935` | **`0.9652`** | `0.65 %` | **`2.92 %`** | Tree ensemble maintains robust bounds on novel vehicles. |
| **SOH** (%) | **Ridge (Champion)** | `0.9842` | **`0.0667`** | `0.61 %` | **`4.83 %`** | **Asset-Specific Drift**: Without seeing a specific chassis's initial capacity baseline, macroscopic point prediction has an expected error of $\pm 4.8\%$. |
| **SOH** (%) | **ExtraTrees** | `0.9840` | **`-0.1026`** | `0.63 %` | **`6.34 %`** | Tree regressors predict the fleet mean ($\approx 92\%$) on unseen degraded packs ($83\%$), producing negative $R^2$ relative to test mean. |
| **SOH** (%) | **XGBoost** | `0.9815` | **`-0.4151`** | `0.72 %` | **`8.26 %`** | Overfits to individual chassis offsets under row-level splits. |
| **RUL** (Cycles) | **GradientBoosting** | `0.9912` | **`0.9971`** | `18.4 cyc` | **`2.66 cyc`** | **Consistent Aging Trajectories**: Cycle throughput degradation slopes follow consistent electrochemical trajectories across fleet charging sessions. |
| **RUL** (Cycles) | **XGBoost** | `0.9890` | **`0.9937`** | `21.2 cyc` | **`3.94 cyc`** | Gradient-boosted decision trees locate cycle degradation milestones reliably. |
| **Mileage** (km) | **XGBoost (Champion)** | `0.9445` | **`0.9526`** | `3.20 km` | **`3.52 km`** | **Superb Generalization**: Kinematic velocity profiles, stoppage frequency, and energy efficiency ($\text{kWh/km}$) generalize across 644 commercial trucks. |
| **Mileage** (km) | **RandomForest** | `0.9410` | **`0.9362`** | `3.45 km` | **`4.64 km`** | Tree ensembles capture payload and traffic density variations across Indian delivery routes. |

---

## 🔬 3. Decomposing the SOH Signal: "Free" Baseline Variance vs True Model Skill

In Part 2, framing SOH prediction as a "calibrated baseline" task ($\widehat{\text{SOH}}_t = \text{SOH}_0 + \widehat{\Delta \text{SOH}}_t$) reported an absolute SOH $R^2 = 0.9998$. 

### A. The Trivial Zero-Fade Baseline Test
To determine how much of this $0.9998$ $R^2$ represents genuine machine learning intelligence vs trivial carried-forward variance, we evaluated a **Trivial Naive Baseline** that predicts **zero fade at all times** ($\widehat{\text{SOH}}_t = \text{SOH}_0$, with zero ML model):

| Method | Absolute SOH $R^2$ | Absolute SOH MAE | Delta-SOH $R^2$ (Model Skill) | Delta-SOH MAE | Gain over Naive $R^2$ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Naive (SOH_0, Zero Fade, No Model)** | **`0.999874`** | **`0.0243 %`** | **N/A (0 Skill)** | **`0.0243 %`** | **`0.000000 (Baseline)`** |
| **XGBoost Calibrated** | `0.999814` | `0.0486 %` | `-0.5882` | `0.0486 %` | **`-0.000060` (Worse)** |
| **Lasso Calibrated** | `0.999622` | `0.0900 %` | `-2.2204` | `0.0900 %` | **`-0.000252` (Worse)** |
| **Ridge Calibrated** | `0.999556` | `0.1005 %` | `-2.7880` | `0.1005 %` | **`-0.000318` (Worse)** |
| **ExtraTrees Calibrated** | `0.999248` | `0.1238 %` | `-5.4097` | `0.1238 %` | **`-0.000626` (Worse)** |
| **RandomForest Calibrated** | `0.999101` | `0.1313 %` | `-6.6703` | `0.1313 %` | **`-0.000774` (Worse)** |

### 💡 The Plain-Language Scientific Finding
> **The machine learning models improve absolute SOH $R^2$ over the naive zero-fade baseline by exactly $0.000000$ (in fact, every ML model increases error, reducing $R^2$ by $-0.00006$ to $-0.00077$).**  
> **100% of the $0.9998$ absolute SOH score is "free" variance explained entirely by the commissioning baseline $\text{SOH}_0$. When tasked with forecasting the actual degradation signal beyond baseline ($\Delta\text{SOH}$), all machine learning models achieve negative $R^2$.**

---

## 🧪 4. Root-Cause Diagnosis: Why Delta-SOH Prediction Fails

An in-depth statistical audit of the 370,666 SOH rows across all 19 unique chassis reveals two structural causes:

### 1. Near-Zero Degradation Spread (Noise-Dominated Target)
Across the held-out test split (70,286 rows):
* **Exact Zero-Fade Rows**: **$66.88\%$** of all rows have $\Delta\text{SOH} = 0.0000\%$.
* **Mean $\Delta\text{SOH}$**: $-0.0237\%$ (less than $1/40^{\text{th}}$ of one percent).
* **Standard Deviation**: $0.0874\%$.
* **Chassis Distribution**: 4 vehicles have identically zero fade throughout their logs, and 13 vehicles vary by less than $0.15\%$. 
* *Conclusion*: Over the limited operational window captured in this telematics dataset, physical electrochemical fade is negligible. The tiny fluctuations present are dominated by sensor quantization noise ($0.05\%$), which cannot be modeled deterministically.

### 2. Extreme Entity Sample-Size Limitation ($N = 19$ Chassis)
* The entire SOH telematics dataset comprises only **19 physical vehicles**.
* An 80/20 group split reserves only **4 test vehicles**, making single-split metrics highly susceptible to fold-selection anomalies.

---

## 🏛️ 5. Authoritative 19-Fold Leave-One-Chassis-Out Cross Validation (LOGO-CV)

To establish statistically robust and defensible generalization metrics, we conducted full **19-Fold Leave-One-Group-Out Cross Validation (LOGO-CV)**, holding out one entire vehicle per fold across all 19 folds:

| Model / Strategy | Delta-SOH Mean $R^2$ | Delta-SOH Std $R^2$ | Delta-SOH Mean MAE | Delta-SOH Std MAE | Absolute SOH Mean MAE |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Trivial Naive Baseline ($\text{SOH}_0$)** | `0.0000` | `0.0000` | **`0.1279 %`** | `0.2852 %` | **`0.1279 %`** |
| **ExtraTrees** | **`-3.5887`** | `9.7222` | `0.1957 %` | `0.2817 %` | `0.1957 %` |
| **Lasso** | **`-3.8058`** | `7.1754` | `0.1903 %` | `0.2888 %` | `0.1903 %` |
| **XGBoost** | **`-4.7690`** | `14.5081` | `0.2237 %` | `0.4338 %` | `0.2237 %` |
| **Ridge** | **`-6.4739`** | `11.2149` | `0.2045 %` | `0.2850 %` | `0.2045 %` |
| **RandomForest** | **`-25.8383`** | `103.8053` | `0.2173 %` | `0.3102 %` | `0.2173 %` |

---

## 📝 6. Official Text for Research Paper (Results & Limitations Section)

> *"In evaluating State of Health (SOH) prognostics, we observed a critical distinction between absolute capacity estimation and true degradation forecasting. While calibrated-baseline formulations achieve an apparent absolute SOH $R^2 > 0.999$, statistical decomposition reveals that this variance is entirely explained by the static vehicle commissioning baseline ($\text{SOH}_0$). A naive baseline predicting zero degradation ($\widehat{\text{SOH}}_t = \text{SOH}_0$) achieves $R^2 = 0.99987$ and an $\text{MAE} = 0.024\%$ on held-out vehicles without training any model.*  
> 
> *Under rigorous 19-fold Leave-One-Chassis-Out Cross Validation (LOGO-CV), all predictive machine learning architectures (Ridge, Lasso, Random Forest, ExtraTrees, and XGBoost) failed to forecast the residual capacity fade ($\Delta\text{SOH}$), yielding negative cross-validation scores (best model: ExtraTrees $\text{LOGO-CV } R^2 = -3.59 \pm 9.72$, $\text{MAE} = 0.196\% \pm 0.282\%$). This negative result is fundamentally attributed to dataset characteristics: across the 19 commercial vehicles, $66.88\%$ of records exhibit zero measurable degradation ($\text{mean } \Delta\text{SOH} = -0.024\%$), meaning the target signal is dominated by sensor quantization noise over the observation timeframe. Consequently, macroscopic CAN telematics alone without multi-year accelerated aging cycles cannot reliably forecast SOH degradation deltas across unseen vehicles without periodic physical laboratory capacity recalibration."*

---

## 📋 7. Final Summary of Operational Prerequisites

| Module | Purpose | Cold-Start Requirement | Operating Mode |
| :--- | :--- | :--- | :--- |
| **Module A (SOC, RUL, Range)** | Primary state estimation | **Zero historical data (0 cycles)** | Instantaneous single-packet inference. Fully generalizable across fleets ($R^2 > 0.95 - 0.99$). |
| **Module A (SOH — Calibrated)** | Capacity fade tracking | **1 commissioning record ($\text{SOH}_0$)** | Relative delta tracking from vehicle delivery baseline. |
| **Module B (Thermal Hazard & CNN-LSTM)** | Multi-zone thermal hazard detection & sequence SOH | **10 consecutive sensor packets ($10\text{ s}$)** | Temporal sliding window over voltage, current, and pack temperatures. |
| **Module C (Knee Point & $dQ/dV$)** | Accelerated aging & knee-point prognostics | **$\ge 20$ full charge cycles** | Computes $dQ/dV$ differential capacity curves and driver stress indices. |
