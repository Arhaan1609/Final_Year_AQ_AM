import pandas as pd
import numpy as np
import os

def merge_datasets(knee_path, behavior_path, output_path):
    print("Loading datasets...")
    knee_df = pd.read_csv(knee_path)
    behavior_df = pd.read_csv(behavior_path)
    
    # Intelligent Rank-Based Mapping
    # Calculate average RUL per knee vehicle (higher is better)
    knee_health = knee_df.groupby('chassis_no')['RUL_to_knee'].mean().sort_values(ascending=False).index.tolist()
    
    # Calculate target_soh per behavior vehicle (higher is better)
    beh_health = behavior_df.groupby('vehicle_id')['target_soh'].mean().sort_values(ascending=False).index.tolist()
    
    print(f"Knee Unique Vehicles: {len(knee_health)}")
    print(f"Behavior Unique Vehicles: {len(beh_health)}")
    
    # Map by rank to preserve physical correlation (good drivers -> healthy batteries)
    v_map = {}
    for i, b_id in enumerate(beh_health):
        # Map to corresponding percentile in knee_health
        k_idx = int(i * len(knee_health) / len(beh_health))
        if k_idx >= len(knee_health):
            k_idx = len(knee_health) - 1
        v_map[b_id] = knee_health[k_idx]
        
    behavior_df['chassis_no'] = behavior_df['vehicle_id'].map(v_map)
    behavior_df.drop(columns=['vehicle_id'], inplace=True)
    
    # Drop cycle count from behavior if it exists to allow left merge on chassis
    if 'charge_cycle_count' in behavior_df.columns:
        behavior_df = behavior_df.drop(columns=['charge_cycle_count'])
        
    overlap = set(knee_df.columns).intersection(set(behavior_df.columns)) - {'chassis_no'}
    if overlap:
        behavior_df = behavior_df.drop(columns=list(overlap))
        
    # Merge only on chassis_no
    merged_df = pd.merge(knee_df, behavior_df, on='chassis_no', how='left')
    
    if merged_df['target_soh'].isna().sum() > 0:
        print("Imputing missing target_soh and behavior features...")
        merged_df = merged_df.sort_values(['chassis_no', 'charge_cycle_count'])
        for col in behavior_df.columns:
            if col != 'chassis_no':
                merged_df[col] = merged_df.groupby('chassis_no')[col].ffill().bfill()
        merged_df = merged_df.fillna(merged_df.median(numeric_only=True))

    merged_df = merged_df.dropna(subset=['RUL_to_knee', 'target_soh'])
    merged_df.to_csv(output_path, index=False)
    print(f"Unified dataset saved to {output_path}. Shape: {merged_df.shape}")

if __name__ == '__main__':
    merge_datasets(
        'data/labeled_features.csv', 
        'Final_Year_Project_1_akshat/Processed_Data/final_merged_dataset.csv', 
        'data/unified_battery_dataset.csv'
    )
