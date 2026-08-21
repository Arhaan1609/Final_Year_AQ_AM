import pandas as pd
import numpy as np
import os
import gc
from scipy.signal import savgol_filter
import warnings
warnings.filterwarnings('ignore')

def load_data(data_dir):
    print("Loading data...")
    charge_cycles = pd.read_csv(os.path.join(data_dir, "charge_cycles_clean.csv"), low_memory=False)
    oem_telemetry = pd.read_csv(os.path.join(data_dir, "oem_telemetry_clean.csv"), low_memory=False)
    trip_logs = pd.read_csv(os.path.join(data_dir, "trip_logs_merged.csv"), low_memory=False)
    gc.collect()
    return charge_cycles, oem_telemetry, trip_logs


def clean_and_impute(df, dataset_name):
    if dataset_name == "charge_cycles":
        df['start_odometer_no_charge'].fillna(df['odometer'], inplace=True)
        df['city'].fillna("Unknown", inplace=True)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
    elif dataset_name == "oem_telemetry":
        if 'range_km' in df.columns:
            df.drop(columns=['range_km'], inplace=True)
        if 'cc' in df.columns:
            df.drop(columns=['cc', 'cp', 'cv'], inplace=True, errors='ignore')
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values(by=['chassis_no', 'timestamp'], inplace=True)
        cols_to_ffill = ['battery_voltage', 'battery_current', 'motor_temp', 'battery_temp', 'cell_temp']
        for col in cols_to_ffill:
            if col in df.columns:
                df[col] = df.groupby('chassis_no')[col].fillna(method='ffill').fillna(method='bfill')
        df['date'] = df['timestamp'].dt.date
    elif dataset_name == "trip_logs":
        df.drop(columns=['new_vehicle_no'], inplace=True, errors='ignore')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
    return df


def smooth_signals(oem_telemetry):
    print("Smoothing telemetry signals...")
    
    def apply_smoothing(group):
        group = group.sort_values('timestamp')
        if len(group) > 11:
            try:
                group['battery_voltage_smooth'] = savgol_filter(group['battery_voltage'], window_length=11, polyorder=2)
                group['battery_temp_smooth'] = group['battery_temp'].rolling(window=5, min_periods=1, center=True).mean()
            except:
                group['battery_voltage_smooth'] = group['battery_voltage']
                group['battery_temp_smooth'] = group['battery_temp']
        else:
            group['battery_voltage_smooth'] = group['battery_voltage']
            group['battery_temp_smooth'] = group['battery_temp']
            
        group['d_soc'] = group['soc'].diff()
        group['d_v'] = group['battery_voltage_smooth'].diff()
        group['dQ_dV'] = np.where(np.abs(group['d_v']) > 0.01, group['d_soc'] / group['d_v'], 0)
        group['dQ_dV'] = group['dQ_dV'].clip(lower=-50, upper=50)
        return group

    oem_telemetry = oem_telemetry.groupby('chassis_no', group_keys=False).apply(apply_smoothing)
    return oem_telemetry


def extract_cycle_features(charge_cycles):
    print("Extracting physical features from charge cycles...")
    
    charge_cycles.drop_duplicates(subset=['chassis_no', 'charge_cycle_count'], keep='last', inplace=True)
    charge_cycles.sort_values(by=['chassis_no', 'charge_cycle_count'], inplace=True)
    
    # Filter early cycles
    print("  Filtering early-cycle noise (first 30 cycles per chassis)...")
    charge_cycles = charge_cycles.groupby('chassis_no', group_keys=False).apply(
        lambda g: g.iloc[30:] if len(g) > 35 else (g.iloc[10:] if len(g) > 15 else g)
    ).reset_index(drop=True)
    
    # Define capacity proxy
    max_miles = charge_cycles.groupby('chassis_no')['miles_per_charge'].transform('max')
    max_miles = max_miles.replace(0, 1)
    charge_cycles['capacity'] = charge_cycles['miles_per_charge'] / max_miles
    
    def eng_features(group):
        group = group.sort_values('charge_cycle_count')
        
        if len(group) > 21:
            try:
                group['smoothed_capacity'] = savgol_filter(group['capacity'], window_length=21, polyorder=3)
            except:
                group['smoothed_capacity'] = group['capacity'].rolling(window=10, min_periods=1, center=True).mean()
        elif len(group) > 5:
            group['smoothed_capacity'] = group['capacity'].rolling(window=5, min_periods=1, center=True).mean()
        else:
            group['smoothed_capacity'] = group['capacity']
            
        group['smoothed_capacity'].fillna(group['capacity'], inplace=True)
        group['smoothed_capacity'] = group['smoothed_capacity'].cummin()
        
        # Core degradation features
        group['delta_capacity'] = group['smoothed_capacity'].diff().fillna(0)
        group['rolling_mean_capacity'] = group['smoothed_capacity'].rolling(window=10, min_periods=1).mean()
        group['rolling_slope'] = group['delta_capacity'].rolling(window=10, min_periods=1).mean()
        group['degradation_rate'] = group['smoothed_capacity'].pct_change().replace([np.inf, -np.inf], np.nan).fillna(0)
        group['delta2_capacity'] = group['delta_capacity'].diff().fillna(0)
        group['ema_capacity'] = group['smoothed_capacity'].ewm(span=10, adjust=False).mean()
        group['capacity_variance_10'] = group['smoothed_capacity'].rolling(10, min_periods=2).std().fillna(0)
        
        max_cy = group['charge_cycle_count'].max()
        group['cycle_age_ratio'] = group['charge_cycle_count'] / (max_cy + 1)
        
        def _slope(s):
            if len(s) < 2: return 0.0
            x = np.arange(len(s), dtype=float)
            return float(np.polyfit(x, s, 1)[0])
        group['slope_20'] = group['smoothed_capacity'].rolling(20, min_periods=5).apply(_slope, raw=True).fillna(0)
        
        # NEW: Advanced features
        group['capacity_percentile'] = group['smoothed_capacity'].rank(pct=True)
        group['delta3_capacity'] = group['delta2_capacity'].diff().fillna(0)
        initial = group['smoothed_capacity'].iloc[0]
        group['half_life_ratio'] = group['smoothed_capacity'] / (initial + 1e-6)
        
        capacity_jump = group['smoothed_capacity'].diff()
        group['is_sudden_drop'] = (capacity_jump < -2 * capacity_jump.std()).astype(int) if capacity_jump.std() > 0 else 0
        
        group['log_cycle'] = np.log1p(group['charge_cycle_count'])
        
        # Local regime features
        group['local_mean_10'] = group['smoothed_capacity'].rolling(10, center=True).mean()
        group['local_std_10'] = group['smoothed_capacity'].rolling(10, center=True).std()
        group['local_cv'] = group['local_std_10'] / (group['local_mean_10'] + 1e-6)
        
        # Cumulative degradation
        group['cum_degradation'] = initial - group['smoothed_capacity']
        
        # Time-weighted features
        group['tw_degradation'] = group['degradation_rate'].ewm(span=5).mean()
        group['tw_delta'] = group['delta_capacity'].ewm(span=5).mean()
        
        group.dropna(subset=['smoothed_capacity', 'degradation_rate'], inplace=True)
        
        return group
        
    charge_cycles = charge_cycles.groupby('chassis_no', group_keys=False).apply(eng_features)
    
    # Drop irrelevant usage features
    cols_to_drop = ['odometer', 'miles_per_charge', 'start_odometer_charge_cycle', 
                    'start_odometer_charge_cycle_max', 'start_odometer_no_charge', 'first_service_days',
                    'mile_avg', 'days_in_service', 'soc_at_charge']
    charge_cycles.drop(columns=[c for c in cols_to_drop if c in charge_cycles.columns], inplace=True, errors='ignore')
    
    return charge_cycles


def extract_telemetry_features(oem_telemetry):
    print("Extracting telemetry features...")
    daily_stats = oem_telemetry.groupby(['chassis_no', 'date']).agg({
        'battery_voltage_smooth': ['mean', 'min', 'max', 'std'],
        'battery_current': ['mean', 'min', 'max'],
        'battery_temp_smooth': ['mean', 'max'],
        'dQ_dV': ['mean', 'std'],
        'soc': ['min', 'max']
    }).reset_index()
    daily_stats.columns = ['_'.join(col).strip('_') for col in daily_stats.columns.values]
    return daily_stats


def extract_trip_features(trip_logs, chassis_mapping):
    print("Extracting trip log features...")
    trip_logs = trip_logs.merge(chassis_mapping, on='vehicle_no', how='left')
    trip_logs.dropna(subset=['chassis_no'], inplace=True)
    
    trip_logs['run_kms'] = pd.to_numeric(trip_logs['run_kms'], errors='coerce').fillna(0)
    trip_logs['trip_duration_hrs'] = pd.to_numeric(trip_logs['trip_duration_hrs'], errors='coerce').fillna(0)
    
    trip_logs['driving_intensity'] = np.where(trip_logs['trip_duration_hrs'] > 0, 
                                            trip_logs['run_kms'] / trip_logs['trip_duration_hrs'], 0)
    
    daily_trips = trip_logs.groupby(['chassis_no', 'date']).agg({
        'run_kms': 'sum',
        'energy_utilized': 'sum',
        'avg_speed': 'mean',
        'max_speed': 'max',
        'driving_intensity': 'mean',
        'soc_drain': 'sum'
    }).reset_index()
    return daily_trips


def merge_features_properly(cc, oem_daily, trip_daily):
    """
    CRITICAL FIX: Merge by chassis_no and forward-fill from ANY date.
    Previous approach failed because charge_cycle dates don't match 
    telemetry/trip dates.
    """
    print("Merging datasets (FIXED: forward-fill by chassis_no)...")
    
    # Convert all dates
    cc['date'] = pd.to_datetime(cc['timestamp']).dt.date
    oem_daily['date'] = pd.to_datetime(oem_daily['date']).apply(
        lambda d: d.date() if hasattr(d, 'date') else d
    ) if hasattr(oem_daily['date'], 'iloc') else pd.to_datetime(oem_daily['date']).dt.date
    trip_daily['date'] = pd.to_datetime(trip_daily['date']).apply(
        lambda d: d.date() if hasattr(d, 'date') else d
    ) if hasattr(trip_daily['date'], 'iloc') else pd.to_datetime(trip_daily['date']).dt.date
    
    # Merge only on chassis_no, forward-fill by date
    merged = cc.copy()
    
    # Add telemetry features
    merged = merged.merge(oem_daily, on=['chassis_no'], how='left', suffixes=('', '_telem'))
    # Use the latest available telemetry for this chassis
    for col in oem_daily.columns:
        if col not in ['chassis_no', 'date']:
            telem_col = col + '_telem' if col in merged.columns else col
            if telem_col in merged.columns:
                merged[telem_col] = merged.groupby('chassis_no')[telem_col].ffill()
                merged[telem_col] = merged[telem_col].fillna(0)
            elif col in merged.columns:
                merged[col] = merged.groupby('chassis_no')[col].ffill()
                merged[col] = merged[col].fillna(0)
    
    # Add trip features
    merged = merged.merge(trip_daily, on=['chassis_no'], how='left', suffixes=('', '_trip'))
    for col in trip_daily.columns:
        if col not in ['chassis_no', 'date']:
            trip_col = col + '_trip' if col in merged.columns else col
            if trip_col in merged.columns:
                merged[trip_col] = merged.groupby('chassis_no')[trip_col].ffill()
                merged[trip_col] = merged[trip_col].fillna(0)
            elif col in merged.columns:
                merged[col] = merged.groupby('chassis_no')[col].ffill()
                merged[col] = merged[col].fillna(0)
    
    # Fill any remaining NaNs with 0
    numeric_cols = merged.select_dtypes(include=[np.number]).columns
    merged[numeric_cols] = merged[numeric_cols].fillna(0)
    
    print(f"Merged shape: {merged.shape}")
    
    # Report fill rates
    for col in ['battery_voltage_smooth_mean', 'battery_current_mean', 'run_kms']:
        if col in merged.columns:
            non_zero = (merged[col] != 0).mean() * 100
            print(f"  {col} non-zero: {non_zero:.1f}%")
    
    return merged


def main():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    cc, oem, trips = load_data(data_dir)
    
    chassis_mapping = cc[['vehicle_no', 'chassis_no']].drop_duplicates()
    
    cc = clean_and_impute(cc, "charge_cycles")
    oem = clean_and_impute(oem, "oem_telemetry")
    trips = clean_and_impute(trips, "trip_logs")
    
    oem = smooth_signals(oem)
    gc.collect()
    
    cc = extract_cycle_features(cc)
    gc.collect()
    
    oem_daily = extract_telemetry_features(oem)
    del oem
    gc.collect()
    
    trip_daily = extract_trip_features(trips, chassis_mapping)
    del trips
    gc.collect()
    
    merged_data = merge_features_properly(cc, oem_daily, trip_daily)
    del cc, oem_daily, trip_daily
    gc.collect()
    
    print("Data processing complete.")
    print(f"Merged dataset shape: {merged_data.shape}")
    
    # Save processed dataset
    out_path = os.path.join(data_dir, "processed_features_v2.csv")
    merged_data.to_csv(out_path, index=False)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
