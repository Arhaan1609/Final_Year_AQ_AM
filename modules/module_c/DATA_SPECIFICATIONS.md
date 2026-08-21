# EV Battery Data: Pipeline & Dataset Documentation

This document provides a technical overview of the precise data lifecycle and the **Top 4 datasets** utilized in this project for behavior-aware battery health modeling.

---

## 1. Data Preprocessing Pipeline

The preprocessing pipeline ensures that raw telemetry and charge cycle data are transformed into a stable, physically consistent, and model-ready format. This is achieved through a 4-step sequential process.

### Step 1: Remove SEI Noise
*   **What & Why**: The **first 30 charge cycles** are discarded unconditionally for each battery chassis. During this initial "formation phase," the **Solid Electrolyte Interphase (SEI)** layer stabilizes. This phase often shows artificially elevated and non-representative capacity readings that would bias downstream models if not removed.
*   **Result**: Stable, representative degradation data from cycle 31 onwards.

### Step 2: Savitzky-Golay Smoothing
*   **What & Why**: A **Savitzky-Golay filter** (Polynomial Order = 2, Window Length = 11) is applied to the capacity time series. This method uses local least-squares polynomial approximation to suppress high-frequency measurement noise while preserving genuine degradation trends and the critical inflection structure near the "knee point."
*   **Result**: A smoothed capacity signal with minimized sensor noise and preserved physical trends.

### Step 3: Enforce Monotonicity
*   **What & Why**: We apply a **cumulative minimum (cummin)** transformation to enforce that the discharge capacity is strictly **non-increasing** over the battery’s life. This step is crucial to prevent physically impossible "capacity recoveries" that often occur due to changes in ambient temperature or measurement drift.
*   **Result**: A monotonic, physically consistent capacity curve that respects thermodynamic laws.

### Step 4: Validate Consistency
*   **What & Why**: The final stage involves rigorous sanity checks for **missing values, outliers, and cycle indexing**. We ensure that any remaining gaps are filled using behavior-aware imputation and that the time-series indexing is perfectly sequential for LSTM/RNN training.
*   **Result**: A clean, validated, and model-ready dataset for reliable RUL and behavior analysis.

---

## 2. Dataset Description

The analysis is powered by the integration of the following **Top 4 datasets** extracted from the project's source files.

| Dataset | Role | Key Fields | Notes |
| :--- | :--- | :--- | :--- |
| **`charge_cycles_cleaned`** | Primary Training Source | cycle_index, capacity, voltage, current | Represents the core degradation signal for capacity fade analysis. |
| **`oem_battery_cleaned`** | Target Derivation | SOH (State of Health), Odometer, Voltage | Provides the ground-truth SOH labels and cumulative aging metrics. |
| **`device_telemetry_cleaned`** | Environmental Context | temperature, SoC, cell_voltage, imei | Captures high-frequency electrical stressors and cell-level balancing data. |
| **`trips_cleaned`** | Driving Behavior Source | trip_id, distance, speed, acceleration | Enables behavioral profiling (Aggressiveness Index) and operational patterns. |

**Data Volume**: The integrated dataset spans hundreds of unique vehicle IDs (Chassis) and thousands of telemetry records, providing the necessary scale for robust AI/ML evaluation.
