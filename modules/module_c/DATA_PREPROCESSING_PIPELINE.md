# Data Preprocessing Pipeline: Electrochemical Signal Conditioning

This document outlines the four-stage transformation pipeline used to convert raw battery telemetry into a physically consistent, model-ready dataset.

---

## 1. Phase One: Stabilization (SEI Noise Removal)

> [!IMPORTANT]
> **Constraint:** Discard the **first 30 charge cycles** per battery chassis.

### What & Why
During the initial life of a lithium-ion battery, a **Solid Electrolyte Interphase (SEI)** layer forms on the anode. This is a stabilization phase where:
- Measurements are erratic and non-representative of long-term health.
- Capacity may appear at artificially elevated levels due to initial chemistry settling.
- **Action:** These 30 cycles are unconditionally discarded to prevent biasing downstream degradation gradients.

### Result
Stable, linearizable data starting from cycle 31 onwards.

---

## 2. Phase Two: Signal Conditioning (Savitzky-Golay)

> [!TIP]
> **Configuration:** Polynomial Order = 3, Window Length = 21 cycles.

### What & Why
Raw battery sensor data (current/voltage integration) is susceptible to high-frequency measurement artifacts.
- **Method:** We apply a **Savitzky-Golay digital filter**. 
- **Benefit:** Unlike a simple moving average, it uses local polynomial regression to preserve the underlying "shape" of the degradation curve. It suppresses noise while maintaining the critical structural data near the "Knee Point."

### Result
A smooth, high-fidelity capacity signal with true physical trends preserved.

---

## 3. Phase Three: Physics Enforcement (Monotonicity)

> [!CAUTION]
> **Physical Law:** Capacity cannot spontaneously increase without external reconditioning.

### What & Why
Batteries are subject to irreversible entropy. In the real world, a battery's capacity can only **stay the same or decrease**.
- **Transform:** We apply a **Cumulative Minimum (`cummin`)** to the smoothed signal.
- **Impact:** This removes "false recovery" artifacts where sensor drift might otherwise suggest a battery is regaining health. It ensures the model respects the second law of thermodynamics.

### Result
A strictly non-increasing, physically realistic capacity curve.

---

## 4. Phase Four: Dataset Integrity (Final Validation)

> [!NOTE]
> **Checklist:** Missing Value Imputation, Cycle Indexing, Outlier Capping.

### What & Why
The final stage ensures the dataset is numerically robust for deep learning (LSTM/GRU).
- **Checks:**
  - **Continuity:** Verifying cycle counts are sequential and sorted.
  - **Imputation:** Filling residual NaNs from rolling window calculations with the original capacity proxy.
  - **Scaling:** Normalizing features to a [0, 1] range to ensure stable gradient descent in neural networks.

### Result
A clean, validated, and high-quality dataset ready for model training.
