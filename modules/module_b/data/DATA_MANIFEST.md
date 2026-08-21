# Data Manifest & Lineage Specification: Module 3 Battery Health & Thermal Management

This document defines the complete data dictionary, provenance lineage, feature transformation pipelines, and validation splits for Module 3 (Battery Health & Thermal Management).

---

## 🏛️ 1. Raw Telemetry Sources (50M+ Records Fleet Audit)

The models in this product were developed and validated on **53,476,634 real-world EV telematics records** collected across four major Indian urban operating environments (Delhi NCR, Mumbai, Bengaluru, and Ahmedabad) from the commercial fleet of **Magenta Mobility**.

| File Name | Format | Record Count | Primary Vehicle / OEM | Primary Telemetry Fields Captured | Role in Product |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `tms_history_l2_oem.json` | JSON / JSONL | **20,575,204** | Euler HiLoad / HiLoad+ | `vbt`, `vct`, `vmt`, `vbv`, `vbc`, `soc`, `soh`, `od`, `csp` | Primary source for SOH temporal sequence modeling and multi-zone thermal dynamics. |
| `tms_history_l2_device.json` | JSON / JSONL | **32,514,567** | Multi-OEM (Tata, Bajaj, Mahindra, Switch) | `vbv`, `soc`, `od`, `csp`, `hai`, `hbi`, `hci` | Multi-OEM driving behavior and cross-chemistry baselines. |
| `charge_cycles_logs.json` | JSON / JSONL | **254,178** | Tata Ace EV | `ccc`, `cod`, `csoc`, `sds`, `sodcc` | Charge session capacity degradation ground truth. |
| `Alert Log 11_47_07.xlsx` | Excel (.xlsx) | **170,354** | Fleet (North / Delhi) | `Alert Type`, `SoC`, `Batt. Volt.`, `Batt. Temp.`, `Speed` | Supervised labels for critical vs. benign thermal faults. |
| `Alert Log 11_47_03.xlsx` | Excel (.xlsx) | **50,838** | Fleet (West / Mumbai) | `Alert Type`, `SoC`, `Batt. Volt.`, `Batt. Temp.`, `Speed` | Supervised labels for critical vs. benign thermal faults. |
| `Trip Report 11_25_15.xlsx`| Excel (.xlsx) | **48,038** | Mumbai Fleet | `Run kms`, `Start SoC`, `End SoC`, `Energy Utilized (kWh)` | Trip energy consumption & SoC drain profiling. |
| `Trip Report 11_25_21.xlsx`| Excel (.xlsx) | **17,467** | Ahmedabad Fleet | `Run kms`, `Start SoC`, `End SoC`, `Energy Utilized (kWh)` | Trip energy consumption & SoC drain profiling. |
| `Trip Report 11_25_29.xlsx`| Excel (.xlsx) | **47,123** | Bengaluru Fleet | `Run kms`, `Start SoC`, `End SoC`, `Energy Utilized (kWh)` | Trip energy consumption & SoC drain profiling. |

---

## 📦 2. Derived & Bundled Datasets in this Deliverable

All derived datasets used to train and verify the shipped models are bundled directly in the `data/` directory:

### 1. `thermal_alerts_balanced_50_50.csv` & `.parquet`
* **Rows:** **10,314 balanced records** ($5,157$ Critical / $5,157$ Benign).
* **Source:** Derived from the $221,190$ raw Alert Log records via Balanced Downsampling (Master Notebook V3.2 Cell 13).
* **Rationale:** Eliminates the $98/2$ class imbalance artifact, forcing the Random Forest to learn the explicit thermodynamic conditions of dangerous faults.
* **Feature Schema:**
  - `alert_type` (String): Specific alarm description (*Deep Discharge Warning, Low SoC, Battery Under Voltage, Harsh Acceleration, OverSpeed*).
  - `is_critical` (Integer: 0 or 1): Binary label ($1 = \text{Critical Hazard}, 0 = \text{Benign Event}$).
  - `vbt` (Float, °C): Battery pack temperature.
  - `vct` (Float, °C): Motor controller / inverter temperature.
  - `vmt` (Float, °C): Drive motor stator temperature.
  - `vbv` (Float, Volts): Pack operating voltage.
  - `vbc` (Float, Amperes): Pack current (negative = discharge).
  - `soc` (Float, %): State of Charge ($0.0 - 100.0\%$).
  - `speed` (Float, km/h): Vehicle ground speed.

### 2. `soh_timeseries_euler_processed.parquet` & `soh_timeseries_euler_sample.json`
* **Rows:** Chronological time-series sequences of Euler HiLoad commercial delivery vehicles tracked across charge cycles.
* **Source:** Extracted from `tms_history_l2_oem.json` with OEM isolation.
* **Feature Schema:**
  - `vehicle_id` (String): Unique chassis identifier.
  - `cycle_index` (Integer): Chronological charge/discharge cycle index ($0 - 400$).
  - `voltage` (Float, Volts): Pack voltage.
  - `current` (Float, Amps): Pack current.
  - `battery_temp` (Float, °C): Battery temperature.
  - `soc` (Float, %): State of Charge.
  - `soh_ground_truth` (Float, %): Verified Remaining Capacity percentage.

### 3. `multizone_fleet_stream_sample.json`
* **Purpose:** Multi-zone streaming packets for live API testing, simulating nominal cruising, motor overheating on steep inclines, and cell voltage collapse.

### 4. `test_split_soh.json` & `test_split_thermal.json`
* **Purpose:** Standalone test evaluation splits matching the exact test folds used in V3/V3.2 to verify **$5.29\%$ SOH RMSE** and **$0.997$ Thermal F1-Score**.

---

## 📐 3. Feature Dictionary & Engineering Formulas

### Feature Dictionary

| Key | Full Name | Units | Nominal Safe Range | Critical Threshold |
| :--- | :--- | :--- | :--- | :--- |
| `vbt` | Battery Pack Temperature | °C | $20.0 - 40.0\,^\circ\text{C}$ | $\ge 48.0\,^\circ\text{C}$ (Thermal runaway boundary) |
| `vct` | Motor Controller / Inverter Temp | °C | $30.0 - 60.0\,^\circ\text{C}$ | $\ge 68.0\,^\circ\text{C}$ (Power electronics thermal surge) |
| `vmt` | Traction Motor Stator Temp | °C | $40.0 - 75.0\,^\circ\text{C}$ | $\ge 85.0\,^\circ\text{C}$ (Motor winding insulation hazard) |
| `vbv` | Battery Pack Voltage | Volts (V) | $52.0 - 84.0\,\text{V}$ | $< 45.0\,\text{V}$ (Cell under-voltage collapse) |
| `vbc` | Battery Current | Amperes (A) | $-60.0\,\text{A} \text{ to } +40.0\,\text{A}$ | $< -90.0\,\text{A}$ (Excessive discharge surge) |
| `soc` | State of Charge | % | $20.0 - 95.0\%$ | $< 10.0\%$ (Deep discharge risk) |
| `speed` | Vehicle Speed | km/h | $0.0 - 65.0\,\text{km/h}$ | $> 70.0\,\text{km/h}$ (Over-speed condition) |
| `soh` | State of Health | % | $80.0 - 100.0\%$ | $< 70.0\%$ (EOL Replacement criteria) |

---

## ⚙️ 4. Normalization & Preprocessing Logic

### SOH Normalization Pipeline
The Hybrid 1D-CNN + LSTM requires input matrices of shape $(\text{Batch}, \text{Seq\_Len}=10, 4)$ where features $[V, I, T, \text{SoC}]$ are normalized via domain-specific empirical bounds:

$$\tilde{X} = \frac{X - X_{\min}}{X_{\max} - X_{\min}}$$

Where:
* $X_{\min} = [40.0\,\text{V}, -120.0\,\text{A}, -10.0\,^\circ\text{C}, 0.0\%]$
* $X_{\max} = [120.0\,\text{V}, 100.0\,\text{A}, 60.0\,^\circ\text{C}, 100.0\%]$

### Multi-Zone Thermal Pipeline
When motor or controller temperatures are absent on legacy telematics units, the preprocessor utilizes dynamic thermal conduction heuristics:
* $T_{\text{controller, estimated}} = T_{\text{battery}} + 8.0\,^\circ\text{C}$
* $T_{\text{motor, estimated}} = T_{\text{battery}} + 15.0\,^\circ\text{C}$

This guarantees backwards compatibility across single-sensor and multi-sensor EV fleets.
