"""
Knee Visualization Script (No TensorFlow required)
==================================================
Tasks 1, 2, 6 - Knee visualizations only
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from sklearn.linear_model import LinearRegression

plt.style.use('seaborn-v0_8-whitegrid')

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
PLOTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results", "plots"))
os.makedirs(PLOTS_DIR, exist_ok=True)


def advanced_knee_visualization(vehicle_id):
    """Generate multi-panel knee analysis figure for a specific vehicle"""
    
    df = pd.read_csv(os.path.join(DATA_DIR, "labeled_features.csv"))
    vehicle_data = df[df['chassis_no'] == vehicle_id].copy()
    vehicle_data = vehicle_data.sort_values('charge_cycle_count')
    
    if len(vehicle_data) < 30:
        print(f"Not enough data for {vehicle_id}")
        return
    
    cycles = vehicle_data['charge_cycle_count'].values
    capacity = vehicle_data['smoothed_capacity'].values
    knee_cycle = vehicle_data['knee_cycle'].iloc[0]
    
    pre_mask = cycles <= knee_cycle
    post_mask = cycles >= knee_cycle
    
    lr_pre = LinearRegression()
    lr_post = LinearRegression()
    
    if pre_mask.sum() > 5:
        lr_pre.fit(cycles[pre_mask].reshape(-1, 1), capacity[pre_mask])
    if post_mask.sum() > 5:
        lr_post.fit(cycles[post_mask].reshape(-1, 1), capacity[post_mask])
    
    d1 = np.gradient(capacity, cycles)
    d2 = np.gradient(d1, cycles)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Advanced Knee Analysis - {vehicle_id}', fontsize=14, fontweight='bold')
    
    # 1. Degradation Curve
    ax1 = axes[0, 0]
    ax1.plot(cycles, capacity, 'b-', alpha=0.5, label='Raw', linewidth=1)
    ax1.plot(cycles, capacity, 'b.', alpha=0.3, markersize=3)
    ax1.axvline(x=knee_cycle, color='red', linestyle='--', linewidth=2, label=f'Knee @ {knee_cycle:.0f}')
    ax1.set_xlabel('Charge Cycle')
    ax1.set_ylabel('Smoothed Capacity')
    ax1.set_title('1. Degradation Curve', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Piecewise Fit
    ax2 = axes[0, 1]
    ax2.scatter(cycles, capacity, c='blue', alpha=0.5, s=20, label='Data')
    if pre_mask.sum() > 5:
        ax2.plot(cycles[pre_mask], lr_pre.predict(cycles[pre_mask].reshape(-1, 1)), 
                'g-', linewidth=2, label=f'Pre-knee (slope={lr_pre.coef_[0]:.6f})')
    if post_mask.sum() > 5:
        ax2.plot(cycles[post_mask], lr_post.predict(cycles[post_mask].reshape(-1, 1)), 
                'r-', linewidth=2, label=f'Post-knee (slope={lr_post.coef_[0]:.6f})')
    ax2.axvline(x=knee_cycle, color='orange', linestyle='--', linewidth=2)
    ax2.set_xlabel('Charge Cycle')
    ax2.set_ylabel('Capacity')
    ax2.set_title('2. Piecewise Linear Fit', fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 3. First Derivative
    ax3 = axes[1, 0]
    ax3.plot(cycles, d1, 'b-', linewidth=1, label='dC/dCycle')
    ax3.axvline(x=knee_cycle, color='red', linestyle='--', linewidth=2)
    ax3.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    slope_change_mask = (cycles > knee_cycle - 10) & (cycles < knee_cycle + 10)
    ax3.fill_between(cycles[slope_change_mask], d1[slope_change_mask], 
                    alpha=0.3, color='yellow', label='Slope change region')
    ax3.set_xlabel('Charge Cycle')
    ax3.set_ylabel('dCapacity/dCycle')
    ax3.set_title('3. First Derivative (Degradation Rate)', fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Second Derivative
    ax4 = axes[1, 1]
    ax4.plot(cycles, d2, 'purple', linewidth=1, label='d2C/dCycle2')
    ax4.axvline(x=knee_cycle, color='red', linestyle='--', linewidth=2)
    knee_idx = np.argmin(np.abs(cycles - knee_cycle))
    ax4.plot(cycles[knee_idx], d2[knee_idx], 'ro', markersize=10, 
            label=f'Peak curvature @ {cycles[knee_idx]:.0f}')
    ax4.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax4.set_xlabel('Charge Cycle')
    ax4.set_ylabel('d2Capacity/dCycle2')
    ax4.set_title('4. Second Derivative (Curvature)', fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f'knee_analysis_{vehicle_id}.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: knee_analysis_{vehicle_id}.png")


def knee_breakdown_analysis(vehicle_id):
    """Create pre vs post knee comparison figure"""
    
    df = pd.read_csv(os.path.join(DATA_DIR, "labeled_features.csv"))
    vehicle_data = df[df['chassis_no'] == vehicle_id].copy()
    vehicle_data = vehicle_data.sort_values('charge_cycle_count')
    
    if len(vehicle_data) < 30:
        return
    
    cycles = vehicle_data['charge_cycle_count'].values
    capacity = vehicle_data['smoothed_capacity'].values
    knee_cycle = vehicle_data['knee_cycle'].iloc[0]
    
    pre_mask = cycles <= knee_cycle
    post_mask = cycles >= knee_cycle
    
    pre_rate = np.mean(np.diff(capacity[pre_mask]) / np.diff(cycles[pre_mask])) if pre_mask.sum() > 1 else 0
    post_rate = np.mean(np.diff(capacity[post_mask]) / np.diff(cycles[post_mask])) if post_mask.sum() > 1 else 0
    
    pre_var = np.var(capacity[pre_mask]) if pre_mask.sum() > 0 else 0
    post_var = np.var(capacity[post_mask]) if post_mask.sum() > 0 else 0
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f'Knee Breakdown Analysis - {vehicle_id}', fontsize=14, fontweight='bold')
    
    # Degradation curves
    ax1 = axes[0]
    ax1.plot(cycles[pre_mask], capacity[pre_mask], 'g-', linewidth=2, 
            label=f'Slow Degradation (slope={pre_rate:.6f})')
    ax1.plot(cycles[post_mask], capacity[post_mask], 'r-', linewidth=2, 
            label=f'Accelerated Degradation (slope={post_rate:.6f})')
    ax1.axvline(x=knee_cycle, color='orange', linestyle='--', linewidth=2)
    ax1.fill_between(cycles, capacity, alpha=0.2, color='blue')
    ax1.set_xlabel('Charge Cycle')
    ax1.set_ylabel('Smoothed Capacity')
    ax1.set_title('Degradation Phases', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Statistics
    ax2 = axes[1]
    x = np.arange(2)
    width = 0.35
    vars_data = [pre_var * 1000, post_var * 1000]
    rates_data = [abs(pre_rate) * 1000, abs(post_rate) * 1000]
    
    bars1 = ax2.bar(x - width/2, vars_data, width, label='Variance (x1000)', color='#3498db')
    bars2 = ax2.bar(x + width/2, rates_data, width, label='|Rate| (x1000)', color='#e74c3c')
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(['Pre-Knee', 'Post-Knee'])
    ax2.set_ylabel('Value')
    ax2.set_title('Statistics Comparison', fontweight='bold')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f'knee_breakdown_{vehicle_id}.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: knee_breakdown_{vehicle_id}.png")


def main():
    print("="*70)
    print("KNEE VISUALIZATION (Task 1 & 2)")
    print("="*70)
    
    df = pd.read_csv(os.path.join(DATA_DIR, "labeled_features.csv"))
    available_vehicles = df['chassis_no'].unique()[:3]
    
    for vehicle_id in available_vehicles:
        vehicle_data = df[df['chassis_no'] == vehicle_id]
        if len(vehicle_data) > 30:
            advanced_knee_visualization(vehicle_id)
            knee_breakdown_analysis(vehicle_id)
    
    print("\nVisualizations saved to:", PLOTS_DIR)


if __name__ == "__main__":
    main()
