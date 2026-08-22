import pandas as pd
import numpy as np
import os

from scipy.signal import savgol_filter

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

def detect_knee_points(df):
    """
    Detect knee points for each battery chassis using a Piecewise Linear Fit.
    Fits two lines (slow degradation vs accelerated) and finds the split point 
    that minimizes the overall Mean Squared Error.
    """
    print("Detecting knee points (Piecewise Linear Fit)...")
    knee_points = []
    
    df = df.sort_values(by=['chassis_no', 'charge_cycle_count'])
    
    for chassis, group in df.groupby('chassis_no'):
        group = group.drop_duplicates(subset=['charge_cycle_count']).reset_index(drop=True)
        
        if len(group) < 40: # Need enough points for two segments
            continue
            
        cycles = group['charge_cycle_count'].values.reshape(-1, 1)
        capacity = group['smoothed_capacity'].values
        
        # Search range: Ignore first 20 and last 10 points
        best_split_idx = -1
        min_total_mse = float('inf')
        
        for i in range(20, len(group) - 10):
            # Segment 1: Start to i
            x1, y1 = cycles[:i+1], capacity[:i+1]
            # Segment 2: i to End
            x2, y2 = cycles[i:], capacity[i:]
            
            lr1 = LinearRegression().fit(x1, y1)
            lr2 = LinearRegression().fit(x2, y2)
            
            mse1 = mean_squared_error(y1, lr1.predict(x1))
            mse2 = mean_squared_error(y2, lr2.predict(x2))
            
            total_mse = (mse1 * len(y1) + mse2 * len(y2)) / len(group)
            
            if total_mse < min_total_mse:
                min_total_mse = total_mse
                best_split_idx = i
        
        if best_split_idx != -1:
            knee_cycle = cycles[best_split_idx][0]
            knee_points.append({
                'chassis_no': chassis,
                'knee_cycle': knee_cycle
            })
            
    return pd.DataFrame(knee_points)

def generate_labels(df, knee_df):
    """
    Merge knee points and create targets: RUL_to_knee and is_post_knee
    """
    print("Generating labels...")
    df = df.merge(knee_df, on='chassis_no', how='left')
    
    # We drop batteries where a knee point couldn't be detected (or just use them for testing)
    df = df.dropna(subset=['knee_cycle'])
    
    # Remaining useful life (cycles) before the knee point
    df['RUL_to_knee'] = df['knee_cycle'] - df['charge_cycle_count']
    
    # For prediction, we might not care about data long after the knee, or we predict negatives
    
    # Classification label
    df['is_post_knee'] = (df['charge_cycle_count'] >= df['knee_cycle']).astype(int)
    
    return df

def main():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    feature_path = os.path.join(data_dir, "processed_features.csv")
    
    if not os.path.exists(feature_path):
        print(f"Error: {feature_path} not found.")
        return
        
    df = pd.read_csv(feature_path)
    
    # Reverse scaling to calculate derivatives accurately?
    # Actually, capacity_proxy isn't scaled, only trip and telemetry features are
    # Wait, earlier I scaled everything except ['chassis_no', 'date', 'timestamp', 'charge_cycle_count']
    # If capacity_proxy was scaled, its shape is preserved, second derivative still finds the knee.
    
    knee_df = detect_knee_points(df)
    print(f"Detected knee points for {len(knee_df)} total batteries.")
    
    labeled_df = generate_labels(df, knee_df)
    
    out_path = os.path.join(data_dir, "labeled_features.csv")
    labeled_df.to_csv(out_path, index=False)
    print(f"Saved labeled dataset to {out_path} with shape {labeled_df.shape}")

if __name__ == "__main__":
    main()
