import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score

plt.style.use('seaborn-v0_8-whitegrid')
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))


def load_optimized_results():
    """Load results from optimized_pipeline"""
    metrics = pd.read_csv(os.path.join(DATA_DIR, "optimized_model_metrics.csv"))
    
    if os.path.exists(os.path.join(DATA_DIR, 'opt_config.pkl')):
        config = joblib.load(os.path.join(DATA_DIR, 'opt_config.pkl'))
        features = config.get('feat_cols', [])
    
    return metrics


def create_comprehensive_viz():
    """Create visualizations with optimized pipeline results"""
    metrics = load_optimized_results()
    
    # Load predictions data  
    pred_df = pd.read_csv(os.path.join(DATA_DIR, "optimized_predictions_dl.csv"))
    y_true = pred_df['y_true'].values
    pred_ensemble = pred_df['ensemble_pred'].values
    
    # Calculate errors
    pct_error = np.abs(pred_ensemble - y_true) / (np.abs(y_true) + 1e-6) * 100
    
    # 1. ACCURACY PIE CHART
    fig, ax = plt.subplots(figsize=(10, 8))
    
    excellent = np.sum(pct_error < 5)
    good = np.sum((pct_error >= 5) & (pct_error < 15))
    moderate = np.sum((pct_error >= 15) & (pct_error < 30))
    poor = np.sum(pct_error >= 30)
    
    total = len(y_true)
    sizes = [excellent, good, moderate, poor]
    colors = ['#27ae60', '#3498db', '#f39c12', '#e74c3c']
    labels = [
        f'Excellent (<5%)\n{excellent} samples ({100*excellent/total:.1f}%)',
        f'Good (5-15%)\n{good} samples ({100*good/total:.1f}%)', 
        f'Moderate (15-30%)\n{moderate} samples ({100*moderate/total:.1f}%)',
        f'Poor (>30%)\n{poor} samples ({100*poor/total:.1f}%)'
    ]
    
    wedges, texts = ax.pie(sizes, colors=colors, labels=labels, startangle=90,
                        labeldistance=1.1, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    
    # Center circle for donut
    centre = plt.Circle((0, 0), 0.5, fc='white')
    ax.add_artist(centre)
    ax.text(0, 0, f'Total\n{total}', ha='center', va='center', fontsize=14, fontweight='bold')
    
    ax.set_title('Model Prediction Accuracy Distribution\n(Optimized CNN-BiLSTM + Attention)', 
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'viz_accuracy_pie_v2.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: viz_accuracy_pie_v2.png")
    
    # 2. MODEL COMPARISON BAR CHART
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    models = metrics['Model'].values
    rmse = metrics['RMSE'].values
    mae = metrics['MAE'].values
    r2 = metrics['R2'].values
    good_pct = metrics['Pct_Good'].values
    poor_pct = metrics['Pct_Poor'].values
    
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(models)))
    
    # RMSE
    ax1 = axes[0, 0]
    bars = ax1.bar(range(len(models)), rmse, color=colors)
    ax1.set_xticks(range(len(models)))
    ax1.set_xticklabels(models, rotation=25, ha='right')
    ax1.set_ylabel('RMSE (cycles)')
    ax1.set_title('RMSE (Lower is Better)', fontweight='bold')
    for bar, val in zip(bars, rmse):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.2, f'{val:.2f}', 
                ha='center', fontsize=9)
    
    # R²
    ax2 = axes[0, 1]
    colors_r2 = ['#27ae60' if v > 0.5 else '#3498db' if v > 0 else '#f39c12' if v > -0.5 else '#e74c3c' for v in r2]
    bars = ax2.bar(range(len(models)), r2, color=colors_r2)
    ax2.set_xticks(range(len(models)))
    ax2.set_xticklabels(models, rotation=25, ha='right')
    ax2.set_ylabel('R² Score')
    ax2.set_title('R² (Higher is Better)', fontweight='bold')
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    for bar, val in zip(bars, r2):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.02, f'{val:.3f}', 
                ha='center', fontsize=9)
    
    # % Good predictions
    ax3 = axes[1, 0]
    bars = ax3.bar(range(len(models)), good_pct, color='#3498db')
    ax3.set_xticks(range(len(models)))
    ax3.set_xticklabels(models, rotation=25, ha='right')
    ax3.set_ylabel('Percentage (%)')
    ax3.set_title('Predictions <15% Error (Higher is Better)', fontweight='bold')
    ax3.set_ylim(0, 40)
    for bar, val in zip(bars, good_pct):
        ax3.text(bar.get_x() + bar.get_width()/2, val + 0.5, f'{val:.1f}%', 
                ha='center', fontsize=9)
    
    # % Poor predictions  
    ax4 = axes[1, 1]
    bars = ax4.bar(range(len(models)), poor_pct, color='#e74c3c')
    ax4.set_xticks(range(len(models)))
    ax4.set_xticklabels(models, rotation=25, ha='right')
    ax4.set_ylabel('Percentage (%)')
    ax4.set_title('Predictions >30% Error (Lower is Better)', fontweight='bold')
    ax4.set_ylim(0, 100)
    for bar, val in zip(bars, poor_pct):
        ax4.text(bar.get_x() + bar.get_width()/2, val + 1, f'{val:.1f}%', 
                ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'viz_model_comparison_v2.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: viz_model_comparison_v2.png")
    
    # 3. DASHBOARD
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('Battery RUL Prediction - Optimized Model Performance Dashboard', fontsize=16, fontweight='bold')
    
    # Get best model
    best_idx = metrics['RMSE'].idxmin()
    best_model = metrics.loc[best_idx]
    
    # 1. Pie chart
    ax1 = fig.add_subplot(2, 3, 1)
    ax1.pie(sizes, colors=colors, startangle=90)
    ax1.set_title('Accuracy Distribution')
    
    # 2. RMSE
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.bar(models, rmse, color=colors)
    ax2.set_ylabel('RMSE')
    ax2.set_title('RMSE Comparison')
    ax2.tick_params(axis='x', rotation=25)
    
    # 3. R²
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.bar(models, r2, color=colors_r2)
    ax3.set_ylabel('R²')
    ax3.set_title('R² Comparison')
    ax3.tick_params(axis='x', rotation=25)
    ax3.axhline(y=0, color='gray', linestyle='--')
    
    # 4. Scatter
    ax4 = fig.add_subplot(2, 3, 4)
    scatter = ax4.scatter(y_true, pred_ensemble, c=pct_error, cmap='RdYlGn_r', 
                       alpha=0.6, s=50, edgecolor='white', linewidth=0.5)
    max_val = max(max(y_true), max(pred_ensemble)) + 10
    ax4.plot([0, max_val], [0, max_val], 'k--', alpha=0.5)
    ax4.set_xlabel('Actual RUL')
    ax4.set_ylabel('Predicted RUL')
    ax4.set_title('Predictions vs Actual')
    cbar = plt.colorbar(scatter, ax=ax4)
    cbar.set_label('% Error')
    
    # 5. Error distribution
    ax5 = fig.add_subplot(2, 3, 5)
    ax5.hist(pct_error, bins=25, edgecolor='white', color='#3498db', alpha=0.7)
    ax5.axvline(x=5, color='green', linestyle='--', alpha=0.7, label='5%')
    ax5.axvline(x=15, color='blue', linestyle='--', alpha=0.7, label='15%')
    ax5.axvline(x=30, color='red', linestyle='--', alpha=0.7, label='30%')
    ax5.set_xlabel('% Error')
    ax5.set_ylabel('Count')
    ax5.set_title('Error Distribution')
    ax5.legend()
    
    # 6. Summary metrics
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.axis('off')
    rmse_val = np.sqrt(mean_squared_error(y_true, pred_ensemble))
    r2_val = r2_score(y_true, pred_ensemble)
    text = f"""
    ╔════════════════════════════════════╗
    ║     BEST MODEL METRICS        ║
    ║   {best_model['Model'][:20]:20s}       ║
    ╠═══════���════════════════════════════╣
    ║  RMSE:    {best_model['RMSE']:>8.2f} cycles        ║
    ║  MAE:     {best_model['MAE']:>8.2f} cycles        ║
    ║  R²:      {best_model['R2']:>8.4f}               ║
    ║  Bias:    {best_model['Bias']:>+8.2f} cycles        ║
    ╠════════════════════════════════════╣
    ║  Accuracy:                       ║
    ║    <15%:  {best_model['Pct_Good']:>6.1f}%              ║
    ║    >30%:  {best_model['Pct_Poor']:>6.1f}%              ║
    ╚════════════════════════════════════╝
    """
    ax6.text(0.5, 0.5, text, transform=ax6.transAxes, fontsize=10,
            family='monospace', va='center', ha='center',
            bbox=dict(boxstyle='round', facecolor='#ecf0f1', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'viz_dashboard_v2.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: viz_dashboard_v2.png")
    
    print("\nAll visualizations created with optimized pipeline results!")


if __name__ == "__main__":
    create_comprehensive_viz()