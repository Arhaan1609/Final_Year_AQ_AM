import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def main():
    print("="*80)
    print("   UNIFIED BA-BMS ENSEMBLE FRAMEWORK: FACULTY DEMONSTRATION MODULE   ")
    print("="*80 + "\n")
    
    metrics_path = r"data/unified_metrics.csv"
    if not os.path.exists(metrics_path):
        print(f"[ERROR] Could not find {metrics_path}. Please run 'python unified_ensemble.py' first.")
        return
        
    df = pd.read_csv(metrics_path)
    
    print("[INFO] Loading Ensemble Meta-Learner Evaluation Metrics...\n")
    
    # Print RUL metrics
    rul_df = df[df['Target'] == 'RUL_to_knee']
    print("--- 1. BATTERY STRUCTURAL HEALTH (RUL to Knee Prediction) ---")
    print(rul_df[['Model', 'RMSE', 'MAE', 'R2']].to_string(index=False))
    print("\n")
    
    # Print SOH metrics
    soh_df = df[df['Target'] == 'target_soh']
    print("--- 2. BEHAVIOR-AWARE HEALTH (Target SOH Prediction) ---")
    print(soh_df[['Model', 'RMSE', 'MAE', 'R2']].to_string(index=False))
    print("\n")
    
    print("[INFO] Generating Visualizations...")
    
    # Create plot directory
    os.makedirs('plots', exist_ok=True)
    
    # Plot comparisons
    plt.style.use('dark_background') # Looks great for presentations
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # RUL Plot
    models = rul_df['Model'].tolist()
    rmse_rul = rul_df['RMSE'].tolist()
    
    colors = ['#FF6F00' if 'Ensemble' in m else '#0277BD' for m in models]
    
    ax1.barh(models, rmse_rul, color=colors)
    ax1.set_title('Knee Prediction Error (Lower is Better)')
    ax1.set_xlabel('Root Mean Squared Error (RMSE)')
    ax1.invert_yaxis()
    
    # SOH Plot
    rmse_soh = soh_df['RMSE'].tolist()
    ax2.barh(models, rmse_soh, color=colors)
    ax2.set_title('Behavioral SOH Prediction Error (Lower is Better)')
    ax2.set_xlabel('Root Mean Squared Error (RMSE)')
    ax2.invert_yaxis()
    
    plt.suptitle("BA-BMS Meta-Ensemble Performance Comparison", fontsize=16)
    plt.tight_layout()
    
    plot_file = os.path.abspath('plots/ensemble_faculty_demo.png')
    plt.savefig(plot_file, dpi=300)
    print(f"[SUCCESS] Plot saved to: {plot_file}")
    
    # Automatically open the plot on Windows
    try:
        os.startfile(plot_file)
        print("\n[DISPLAY] Image opened in your default viewer. Enjoy your presentation!")
    except Exception as e:
        print(f"\n[DISPLAY] You can view the plot manually at: {plot_file}")
        
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
