# Preprocessing Action Log: Visual Blueprint

This document summarizes the exact operations performed by the current preprocessing pipeline (`src/data_processor.py` and `src/data_merger.py`). Use these steps as the "Blocks" for your technical diagram.

---

### Step 1: Multi-Source Ingestion
*   **Action**: Raw scripts read from three disparate formats: **Excel** (Alerts/Trips), **JSON** (OEM/Device), and **JSON-Stream** (Telemetry).
*   **Key Logic**: Streaming large telemetry files to prevent memory overflow.
*   **Visual Element**: Multiple arrows (Data sources) pointing into a "Unified Ingestion Engine."

### Step 2: Semantic Standardization
*   **Action**: Converting heterogeneous column names into a unified **Snake_Case** naming convention.
*   **Key Logic**: Mapping internal codes (e.g., `vbv`, `csp`) to human-readable terms (`battery_voltage`, `speed`).
*   **Visual Element**: A "Transformer" block that maps cryptic labels to readable ones.

### Step 3: Global Identity Normalization
*   **Action**: Cleaning the `vehicle_id` and `chassis_no` strings across all five datasets.
*   **Key Logic**: Trimming whitespace, forcing uppercase, and removing special characters to ensure perfect "joins" later.
*   **Visual Element**: A filtering funnel that standardizes ID formats.

### Step 4: Time-Series Temporal Alignment
*   **Action**: Converting various date formats (ISO-8601 and Custom Excel strings) into **Pandas Datetime** objects.
*   **Key Logic**: Aligning high-frequency telemetry timestamps with low-frequency trip/charge records.
*   **Visual Element**: A "Clock" icon representing the synchronization of different data frequencies.

### Step 5: Integrity Filtering & Cleaning
*   **Action**: Removing "Noise" records and invalid targets.
*   **Key Logic**: 
    1.  Dropping rows with missing `vehicle_id`.
    2.  Filtering SOH to realistic ranges (0% < SOH ≤ 100%).
    3.  Converting duration strings (DD:HH:MM:SS) into numeric minutes.
*   **Visual Element**: A "Scrubbing/Cleaning" icon indicating the removal of bad data.

### Step 6: Categorical Grouping & Synthesis
*   **Action**: Aggregating granular telemetry into vehicle-level features for ML.
*   **Key Logic**: Computing **Mean**, **Std**, and **Max** values per vehicle to create the "Vehicle Fingerprint."
*   **Visual Element**: A "Grouping" block that collapses hundreds of rows into a single summary vector.

### Step 7: Leakage-Free Dataset Generation
*   **Action**: Splitting and merging into final exports: `final_merged_dataset.csv` and `dl_timeseries_dataset.csv`.
*   **Key Logic**: Preparing the target SOH from the OEM data while maintaining a strict "Blacklist" of leaky features.
*   **Visual Element**: Two output paths (ML Path and DL Path) leading to the final data files.
