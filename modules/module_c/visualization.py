import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.linear_model import LinearRegression

def plot_degradation_and_knee(df, chassis_id, output_dir):
    print(f"Plotting degradation curve for {chassis_id}...")
    group = df[df['chassis_no'] == chassis_id].sort_values('charge_cycle_count')
    if group.empty: return

    cycles = group['charge_cycle_count'].values
    capacity = group['smoothed_capacity'].values
    knee_cycle = group['knee_cycle'].iloc[0]
    
    # Recalculate segments for visualization
    knee_idx = np.argmin(np.abs(cycles - knee_cycle))
    
    x1, y1 = cycles[:knee_idx+1].reshape(-1, 1), capacity[:knee_idx+1]
    x2, y2 = cycles[knee_idx:].reshape(-1, 1), capacity[knee_idx:]
    
    lr1 = LinearRegression().fit(x1, y1)
    lr2 = LinearRegression().fit(x2, y2)
    
    plt.figure(figsize=(12, 6))
    plt.plot(cycles, capacity, label='Smoothed Capacity', color='#2196F3', linewidth=2)
    
    # Plot segments
    plt.plot(x1, lr1.predict(x1), 'g--', linewidth=2, label='Segment 1: Slow')
    plt.plot(x2, lr2.predict(x2), 'm--', linewidth=2, label='Segment 2: Accelerated')
    
    plt.axvline(x=knee_cycle, color='red', linestyle='--', linewidth=2, label=f'Global Knee: {knee_cycle:.0f}')
    
    plt.title(f"Full-Curve Piecewise Analysis - {chassis_id}", fontsize=14, fontweight='bold')
    plt.xlabel("Charge Cycle Count", fontsize=12)
    plt.ylabel("Capacity (Normalized)", fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"degradation_{chassis_id}.png"), dpi=150)
    plt.close()

def plot_knee_derivatives(df, chassis_id, output_dir):
    print(f"Plotting knee detection derivatives for {chassis_id}...")
    group = df[df['chassis_no'] == chassis_id].sort_values('charge_cycle_count')
    if len(group) < 20: return

    cycles = group['charge_cycle_count'].values
    capacity = group['smoothed_capacity'].values
    
    f1 = np.gradient(capacity, cycles)
    f2 = np.gradient(f1, cycles)
    f2_smooth = pd.Series(f2).rolling(window=11, center=True).mean().fillna(0).values

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax1.plot(cycles, f1, color='green', label='1st Derivative (Rate)')
    ax1.set_ylabel("dC / dCycle")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(cycles, f2_smooth, color='purple', label='2nd Derivative (Smoothed)')
    ax2.axvline(x=group['knee_cycle'].iloc[0], color='red', linestyle='--', label='Detected Knee')
    ax2.set_ylabel("d²C / dCycle²")
    ax2.set_xlabel("Cycle Count")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(f"Knee Detection Analysis - {chassis_id}", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"knee_analysis_{chassis_id}.png"), dpi=150)
    plt.close()

def plot_model_comparison(metrics_df, output_dir):
    """Bar plot comparing RMSE and R² Test across all models."""
    print("Plotting model comparison (RMSE + R²)...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    
    # RMSE Bar Chart
    colors_rmse = sns.color_palette("coolwarm", len(metrics_df))
    bars1 = ax1.barh(metrics_df['Model'], metrics_df['RMSE'], color=colors_rmse)
    ax1.set_xlabel("RMSE (Lower is Better)", fontsize=12)
    ax1.set_title("Model RMSE Comparison", fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    for bar, val in zip(bars1, metrics_df['RMSE']):
        ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, f'{val:.2f}', va='center', fontsize=9)
    
    # R² Test Bar Chart
    if 'R2_Test' in metrics_df.columns:
        colors_r2 = sns.color_palette("viridis", len(metrics_df))
        bars2 = ax2.barh(metrics_df['Model'], metrics_df['R2_Test'], color=colors_r2)
        ax2.set_xlabel("R² Test (Higher is Better)", fontsize=12)
        ax2.set_title("Model R² Test Comparison", fontsize=14, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        for bar, val in zip(bars2, metrics_df['R2_Test']):
            ax2.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, f'{val:.4f}', va='center', fontsize=9)
    else:
        # Fallback: MAE chart
        bars2 = ax2.barh(metrics_df['Model'], metrics_df['MAE'], color='#FF9800')
        ax2.set_xlabel("MAE (Lower is Better)")
        ax2.set_title("Model MAE Comparison", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "model_comparison.png"), dpi=150)
    plt.close()

def plot_feature_importance(fi_df, output_dir):
    print("Plotting feature importance...")
    plt.figure(figsize=(10, 8))
    sns.barplot(x=fi_df['importance'], y=fi_df.index, palette='viridis')
    plt.title("XGBoost Feature Importance for RUL Prediction", fontsize=14, fontweight='bold')
    plt.xlabel("Importance Score")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "feature_importance.png"), dpi=150)
    plt.close()

def plot_predictions(pred_df, output_dir):
    """Scatter plot of actual vs predicted with y=x line."""
    print("Plotting actual vs predicted scatter...")
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Ensemble scatter
    axes[0].scatter(pred_df['y_true'], pred_df['ensemble_pred'], alpha=0.4, color='#E91E63', s=15, label='Weighted Ensemble')
    min_val = min(pred_df['y_true'].min(), pred_df['ensemble_pred'].min())
    max_val = max(pred_df['y_true'].max(), pred_df['ensemble_pred'].max())
    axes[0].plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=2, label='Perfect (y=x)')
    axes[0].set_title("Weighted Ensemble: Actual vs Predicted", fontsize=13, fontweight='bold')
    axes[0].set_xlabel("Actual RUL (Cycles)")
    axes[0].set_ylabel("Predicted RUL (Cycles)")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Multi-model scatter
    axes[1].scatter(pred_df['y_true'], pred_df['lstm_pred'], alpha=0.3, s=10, label='LSTM', color='#2196F3')
    if 'gru_pred' in pred_df.columns:
        axes[1].scatter(pred_df['y_true'], pred_df['gru_pred'], alpha=0.3, s=10, label='GRU', color='#4CAF50')
    axes[1].scatter(pred_df['y_true'], pred_df['xgb_pred'], alpha=0.3, s=10, label='XGBoost', color='#FF9800')
    axes[1].plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=2, label='Perfect (y=x)')
    axes[1].set_title("Individual Models: Actual vs Predicted", fontsize=13, fontweight='bold')
    axes[1].set_xlabel("Actual RUL (Cycles)")
    axes[1].set_ylabel("Predicted RUL (Cycles)")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "predictions_scatter.png"), dpi=150)
    plt.close()

def plot_behavior_analysis(df, output_dir):
    print("Plotting driving behavior analysis...")
    if 'avg_speed' not in df.columns or 'energy_utilized' not in df.columns:
        print("  Skipping behavior plot (columns not found)")
        return
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='avg_speed', y='energy_utilized', alpha=0.5)
    plt.title("Energy Consumption vs Average Speed")
    plt.xlabel("Average Speed (km/h)")
    plt.ylabel("Energy Utilized")
    plt.savefig(os.path.join(output_dir, "behavior_analysis.png"), dpi=150)
    plt.close()

def main():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results", "plots"))
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    # 1. Load data
    labeled_df = pd.read_csv(os.path.join(data_dir, "labeled_features.csv"))
    model_metrics = pd.read_csv(os.path.join(data_dir, "model_metrics.csv"))
    ensemble_metrics = pd.read_csv(os.path.join(data_dir, "ensemble_metrics.csv"))
    fi_df = pd.read_csv(os.path.join(data_dir, "feature_importance.csv"), index_col=0)
    pred_df = pd.read_csv(os.path.join(data_dir, "predictions.csv"))

    # Select a chassis for specific plots
    sample_chassis = labeled_df['chassis_no'].unique()[0]

    # 2. Run plots
    plot_degradation_and_knee(labeled_df, sample_chassis, output_dir)
    plot_knee_derivatives(labeled_df, sample_chassis, output_dir)
    
    # Merge all metrics for comparison
    combined_metrics = pd.concat([model_metrics, ensemble_metrics], ignore_index=True).drop_duplicates('Model')
    plot_model_comparison(combined_metrics, output_dir)
    
    plot_feature_importance(fi_df, output_dir)
    plot_predictions(pred_df, output_dir)
    plot_behavior_analysis(labeled_df, output_dir)

    print(f"All visualizations saved to {output_dir}")

if __name__ == "__main__":
    main()
