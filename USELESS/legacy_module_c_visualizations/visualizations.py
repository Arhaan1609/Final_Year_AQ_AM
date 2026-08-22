import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.metrics import mean_squared_error, r2_score

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))


def load_data():
    """Load prediction data"""
    viz_data = joblib.load(os.path.join(DATA_DIR, 'viz_data.pkl'))
    metrics = pd.read_csv(os.path.join(DATA_DIR, 'final_metrics.csv'))
    return viz_data, metrics


def plot_accuracy_pie():
    """Create pie chart showing model accuracy breakdown"""
    viz_data, metrics = load_data()
    y_true = viz_data['y_true']
    pred = viz_data['pred_Ensemble']
    
    # Calculate percentage errors
    pct_error = np.abs(pred - y_true) / (y_true + 1e-6) * 100
    
    # Categorize predictions
    excellent = np.sum(pct_error < 5)   # <5% error
    good = np.sum((pct_error >= 5) & (pct_error < 15))  # 5-15%
    moderate = np.sum((pct_error >= 15) & (pct_error < 30))  # 15-30%
    poor = np.sum(pct_error >= 30)  # >30%
    
    total = len(y_true)
    
    labels = [
        f'Excellent (<5%)\n{excellent} ({100*excellent/total:.1f}%)',
        f'Good (5-15%)\n{good} ({100*good/total:.1f}%)',
        f'Moderate (15-30%)\n{moderate} ({100*moderate/total:.1f}%)',
        f'Poor (>30%)\n{poor} ({100*poor/total:.1f}%)'
    ]
    sizes = [excellent, good, moderate, poor]
    colors = ['#2ecc71', '#27ae60', '#f39c12', '#e74c3c']
    explode = (0.05, 0.02, 0, 0.1)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct='', startangle=90, pctdistance=0.75,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    
    # Add center circle for donut chart
    centre_circle = plt.Circle((0, 0), 0.50, fc='white')
    ax.add_artist(centre_circle)
    
    # Add center text
    ax.text(0, 0, f'Total\n{total}\nPredictions', 
          ha='center', va='center', fontsize=14, fontweight='bold')
    
    ax.set_title('Model Prediction Accuracy Distribution\n(Weighted Ensemble)', 
                 fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'viz_accuracy_pie.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: viz_accuracy_pie.png")


def plot_model_comparison():
    """Create bar chart comparing model metrics"""
    viz_data, metrics = load_data()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # RMSE comparison
    ax1 = axes[0, 0]
    models = metrics['Model'].values
    rmse = metrics['RMSE'].values
    colors = ['#3498db', '#9b59b6', '#1abc9c', '#e74c3c']
    bars = ax1.bar(models, rmse, color=colors, edgecolor='white', linewidth=2)
    ax1.set_ylabel('RMSE (cycles)')
    ax1.set_title('RMSE Comparison (Lower is Better)', fontweight='bold')
    ax1.set_ylim(0, max(rmse) * 1.2)
    for bar, val in zip(bars, rmse):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # R² comparison
    ax2 = axes[0, 1]
    r2_vals = metrics['R2'].values
    colors = ['#2ecc71' if v > 0 else '#e74c3c' for v in r2_vals]
    bars = ax2.bar(models, r2_vals, color=colors, edgecolor='white', linewidth=2)
    ax2.set_ylabel('R² Score')
    ax2.set_title('R² Comparison (Higher is Better)', fontweight='bold')
    ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    r2_min = min(r2_vals)
    r2_max = max(r2_vals) if max(r2_vals) > 0 else 0.6
    ax2.set_ylim(r2_min - 0.1, r2_max + 0.1)
    for bar, val in zip(bars, r2_vals):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.02 if val > 0 else val - 0.05,
                f'{val:.3f}', ha='center', va='bottom' if val > 0 else 'top', fontweight='bold')
    
    # MAE comparison
    ax3 = axes[1, 0]
    mae = metrics['MAE'].values
    bars = ax3.bar(models, mae, color=colors, edgecolor='white', linewidth=2)
    ax3.set_ylabel('MAE (cycles)')
    ax3.set_title('MAE Comparison (Lower is Better)', fontweight='bold')
    ax3.set_ylim(0, max(mae) * 1.2)
    for bar, val in zip(bars, mae):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{val:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # Accuracy percentages
    ax4 = axes[1, 1]
    x = np.arange(len(models))
    width = 0.35
    excellent = metrics['Pct_Excellent'].values if 'Pct_Excellent' in metrics.columns else [0]*len(models)
    good = metrics['Pct_Good'].values
    
    bars1 = ax4.bar(x - width/2, excellent, width, label='Excellent (<5%)', color='#2ecc71')
    bars2 = ax4.bar(x + width/2, good, width, label='Good (<15%)', color='#3498db')
    ax4.set_ylabel('Percentage (%)')
    ax4.set_title('Prediction Accuracy (Higher is Better)', fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(models, rotation=15)
    ax4.legend()
    ax4.set_ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'viz_model_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: viz_model_comparison.png")


def plot_error_distribution():
    """Create error distribution histograms"""
    viz_data, _ = load_data()
    y_true = viz_data['y_true']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    predictions = {
        'Huber': viz_data['pred_Huber'],
        'Quantile': viz_data['pred_Quantile'],
        'BiLSTM-Attn': viz_data['pred_BiLSTM'],
        'Ensemble': viz_data['pred_Ensemble']
    }
    
    for idx, (name, pred) in enumerate(predictions.items()):
        ax = axes[idx // 2, idx % 2]
        
        error = pred - y_true
        abs_error = np.abs(error)
        pct_error = abs_error / (y_true + 1e-6) * 100
        
        # Histogram
        n, bins, patches = ax.hist(pct_error, bins=30, edgecolor='white', alpha=0.7)
        
        # Color by error severity
        for i, patch in enumerate(patches):
            bin_val = (bins[i] + bins[i+1]) / 2
            if bin_val < 5:
                patch.set_facecolor('#2ecc71')
            elif bin_val < 15:
                patch.set_facecolor('#3498db')
            elif bin_val < 30:
                patch.set_facecolor('#f39c12')
            else:
                patch.set_facecolor('#e74c3c')
        
        ax.axvline(x=5, color='gray', linestyle='--', alpha=0.5, label='5% threshold')
        ax.axvline(x=15, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=30, color='gray', linestyle='--', alpha=0.5)
        
        rmse = np.sqrt(mean_squared_error(y_true, pred))
        r2 = r2_score(y_true, pred)
        
        ax.set_xlabel('Percentage Error (%)')
        ax.set_ylabel('Count')
        ax.set_title(f'{name}\nRMSE={rmse:.2f}, R²={r2:.3f}', fontweight='bold')
        ax.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'viz_error_distribution.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: viz_error_distribution.png")


def plot_feature_importance():
    """Plot feature importance based on correlation"""
    viz_data, _ = load_data()
    y_true = viz_data['y_true']
    feat_names = viz_data['feature_names']
    
    # Load data and calculate correlations
    df = pd.read_csv(os.path.join(DATA_DIR, 'labeled_features.csv'))
    df = df[df['is_post_knee'] == 0]
    
    features = sorted([
        c for c in df.columns
        if c not in ['chassis_no', 'date', 'timestamp', 'vehicle_no', 'city', 'oem', 'model',
                    'source_file', 'cmcdts', 'start_gps', 'end_gps', 'createdAt', 'updatedAt',
                    'rts', 'gdts', 'grts', 'vehicle_status', 'drive_mode', 'charge_inlet_mode', 'vmdl',
                    'is_post_knee', 'knee_cycle', 'RUL_to_knee', 'charge_cycle_count', 'cycle_age_ratio',
                    'oem_encoded', 'model_encoded']
        and np.issubdtype(df[c].dtype, np.number)
    ])
    
    # Calculate correlations
    correlations = []
    for feat in features:
        if feat in df.columns:
            corr = np.abs(df[feat].corr(df['RUL_to_knee']))
            if not np.isnan(corr):
                correlations.append((feat, corr))
    
    correlations.sort(key=lambda x: x[1], reverse=True)
    
    # Take top 15
    top_features = correlations[:15]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    feats = [f[0] for f in top_features]
    corrs = [f[1] for f in top_features]
    
    colors = plt.cm.RdYlGn(np.array(corrs) / max(corrs))
    
    bars = ax.barh(range(len(feats)), corrs, color=colors, edgecolor='white')
    ax.set_yticks(range(len(feats)))
    ax.set_yticklabels(feats)
    ax.invert_yaxis()
    ax.set_xlabel('Absolute Correlation with RUL')
    ax.set_title('Feature Importance (Correlation with Target)', fontweight='bold', fontsize=14)
    
    # Add value labels
    for bar, val in zip(bars, corrs):
        ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
               f'{val:.3f}', va='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'viz_feature_importance.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: viz_feature_importance.png")


def plot_predictions_vs_actual():
    """Create scatter plot of predictions vs actual"""
    viz_data, _ = load_data()
    y_true = viz_data['y_true']
    pred = viz_data['pred_Ensemble']
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Scatter
    scatter = ax.scatter(y_true, pred, c=np.abs(pred - y_true) / (y_true + 1e-6) * 100,
                       cmap='RdYlGn_r', alpha=0.6, s=50, edgecolor='white', linewidth=0.5)
    
    # Perfect prediction line
    max_val = max(max(y_true), max(pred)) + 10
    ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.5, label='Perfect Prediction')
    
    ax.set_xlabel('Actual RUL (cycles)')
    ax.set_ylabel('Predicted RUL (cycles)')
    ax.set_title('Predictions vs Actual\n(Color = % Error)', fontweight='bold', fontsize=14)
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Percentage Error (%)')
    
    # Add metrics
    rmse = np.sqrt(mean_squared_error(y_true, pred))
    r2 = r2_score(y_true, pred)
    ax.text(0.05, 0.95, f'RMSE: {rmse:.2f}\nR²: {r2:.3f}',
           transform=ax.transAxes, fontsize=12, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'viz_predictions_vs_actual.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: viz_predictions_vs_actual.png")


def plot_residuals():
    """Plot residuals analysis"""
    viz_data, _ = load_data()
    y_true = viz_data['y_true']
    pred = viz_data['pred_Ensemble']
    residuals = pred - y_true
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Residuals vs Predicted
    ax1 = axes[0]
    ax1.scatter(pred, residuals, alpha=0.5, c='#3498db', edgecolor='white', s=30)
    ax1.axhline(y=0, color='red', linestyle='--')
    ax1.set_xlabel('Predicted RUL')
    ax1.set_ylabel('Residual (Predicted - Actual)')
    ax1.set_title('Residuals vs Predictions', fontweight='bold')
    
    # Residuals distribution
    ax2 = axes[1]
    ax2.hist(residuals, bins=30, edgecolor='white', color='#3498db', alpha=0.7)
    ax2.axvline(x=0, color='red', linestyle='--')
    ax2.axvline(x=np.mean(residuals), color='green', linestyle='-', label=f'Mean: {np.mean(residuals):.2f}')
    ax2.set_xlabel('Residual')
    ax2.set_ylabel('Count')
    ax2.set_title('Residuals Distribution', fontweight='bold')
    ax2.legend()
    
    # Q-Q plot
    ax3 = axes[2]
    from scipy import stats
    stats.probplot(residuals, dist="norm", plot=ax3)
    ax3.set_title('Q-Q Plot of Residuals', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'viz_residuals.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: viz_residuals.png")


def plot_error_by_rul_range():
    """Plot error by RUL range"""
    viz_data, _ = load_data()
    y_true = viz_data['y_true']
    pred = viz_data['pred_Ensemble']
    
    # Calculate absolute percentage error
    abs_error = np.abs(pred - y_true)
    pct_error = abs_error / (y_true + 1e-6) * 100
    
    # Create RUL bins
    bins = [0, 10, 20, 30, 50, 80, 200]
    labels = ['0-10', '10-20', '20-30', '30-50', '50-80', '80+']
    rul_bins = pd.cut(y_true, bins=bins, labels=labels)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Calculate stats per bin
    bin_stats = []
    for label in labels:
        mask = rul_bins == label
        if np.sum(mask) > 0:
            bin_stats.append({
                'label': label,
                'mean_error': np.mean(pct_error[mask]),
                'median_error': np.median(pct_error[mask]),
                'count': np.sum(mask)
            })
    
    x = np.arange(len(bin_stats))
    mean_errors = [s['mean_error'] for s in bin_stats]
    median_errors = [s['median_error'] for s in bin_stats]
    counts = [s['count'] for s in bin_stats]
    
    width = 0.35
    ax.bar(x - width/2, mean_errors, width, label='Mean % Error', color='#3498db')
    ax.bar(x + width/2, median_errors, width, label='Median % Error', color='#2ecc71')
    
    ax.set_xlabel('RUL Range (cycles)')
    ax.set_ylabel('Percentage Error (%)')
    ax.set_title('Error by RUL Range', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{s['label']}\n(n={s['count']})" for s in bin_stats])
    ax.legend()
    ax.axhline(y=30, color='red', linestyle='--', alpha=0.5, label='30% threshold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'viz_error_by_rul.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: viz_error_by_rul.png")


def plot_summary_dashboard():
    """Create a summary dashboard"""
    viz_data, metrics = load_data()
    y_true = viz_data['y_true']
    pred = viz_data['pred_Ensemble']
    pct_error = np.abs(pred - y_true) / (y_true + 1e-6) * 100
    
    fig = plt.figure(figsize=(16, 12))
    
    # Title
    fig.suptitle('Battery RUL Prediction - Model Performance Dashboard', 
                fontsize=18, fontweight='bold', y=0.98)
    
    # 1. Pie chart (top-left)
    ax1 = fig.add_subplot(2, 3, 1)
    excellent = np.sum(pct_error < 5)
    good = np.sum((pct_error >= 5) & (pct_error < 15))
    moderate = np.sum((pct_error >= 15) & (pct_error < 30))
    poor = np.sum(pct_error >= 30)
    sizes = [excellent, good, moderate, poor]
    colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
    ax1.pie(sizes, colors=colors, startangle=90)
    ax1.set_title('Accuracy Distribution')
    
    # 2. RMSE comparison (top-middle)
    ax2 = fig.add_subplot(2, 3, 2)
    models = metrics['Model'].values
    rmse = metrics['RMSE'].values
    colors = ['#3498db', '#9b59b6', '#1abc9c', '#e74c3c']
    ax2.bar(models, rmse, color=colors)
    ax2.set_ylabel('RMSE')
    ax2.set_title('RMSE by Model')
    ax2.tick_params(axis='x', rotation=20)
    
    # 3. R² comparison (top-right)
    ax3 = fig.add_subplot(2, 3, 3)
    r2 = metrics['R2'].values
    colors = ['#2ecc71' if v > 0 else '#e74c3c' for v in r2]
    ax3.bar(models, r2, color=colors)
    ax3.set_ylabel('R²')
    ax3.set_title('R² by Model')
    ax3.tick_params(axis='x', rotation=20)
    ax3.axhline(y=0, color='gray', linestyle='--')
    
    # 4. Predictions vs Actual (bottom-left)
    ax4 = fig.add_subplot(2, 3, 4)
    scatter = ax4.scatter(y_true, pred, c=pct_error, cmap='RdYlGn_r', 
                        alpha=0.6, s=30, edgecolor='white', linewidth=0.3)
    max_val = max(max(y_true), max(pred)) + 10
    ax4.plot([0, max_val], [0, max_val], 'k--', alpha=0.5)
    ax4.set_xlabel('Actual RUL')
    ax4.set_ylabel('Predicted RUL')
    ax4.set_title('Predictions vs Actual')
    plt.colorbar(scatter, ax=ax4, label='% Error')
    
    # 5. Error distribution (bottom-middle)
    ax5 = fig.add_subplot(2, 3, 5)
    ax5.hist(pct_error, bins=30, edgecolor='white', alpha=0.7)
    ax5.axvline(x=5, color='green', linestyle='--', alpha=0.7)
    ax5.axvline(x=15, color='blue', linestyle='--', alpha=0.7)
    ax5.axvline(x=30, color='red', linestyle='--', alpha=0.7)
    ax5.set_xlabel('Percentage Error (%)')
    ax5.set_ylabel('Count')
    ax5.set_title('Error Distribution')
    
    # 6. Metrics summary (bottom-right)
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.axis('off')
    rmse = np.sqrt(mean_squared_error(y_true, pred))
    mae = np.mean(np.abs(pred - y_true))
    r2 = r2_score(y_true, pred)
    bias = np.mean(pred - y_true)
    
    text = f"""
    ╔═══════════════════════════════════╗
    ║      ENSEMBLE MODEL METRICS       ║
    ╠═══════════════════════════════════╣
    ║  RMSE:     {rmse:>8.2f} cycles       ║
    ║  MAE:      {mae:>8.2f} cycles       ║
    ║  R²:       {r2:>8.4f}              ║
    ║  Bias:     {bias:>+8.2f} cycles       ║
    ╠═══════════════════════════════════╣
    ║  Accuracy:                       ║
    ║    <5%   : {excellent:>5d} ({100*excellent/len(y_true):.1f}%)         ║
    ║    <15%  : {excellent+good:>5d} ({100*(excellent+good)/len(y_true):.1f}%)         ║
    ║    >30%  : {poor:>5d} ({100*poor/len(y_true):.1f}%)         ║
    ╚═══════════════════════════════════╝
    """
    ax6.text(0.5, 0.5, text, transform=ax6.transAxes, fontsize=11,
            family='monospace', va='center', ha='center',
            bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, 'viz_dashboard.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: viz_dashboard.png")


def main():
    print("="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70)
    
    # Check if data exists
    if not os.path.exists(os.path.join(DATA_DIR, 'viz_data.pkl')):
        print("ERROR: Run run_final_pipeline.py first to generate predictions!")
        return
    
    print("\n[1/8] Creating accuracy pie chart...")
    plot_accuracy_pie()
    
    print("[2/8] Creating model comparison chart...")
    plot_model_comparison()
    
    print("[3/8] Creating error distribution histograms...")
    plot_error_distribution()
    
    print("[4/8] Creating feature importance chart...")
    plot_feature_importance()
    
    print("[5/8] Creating predictions vs actual scatter...")
    plot_predictions_vs_actual()
    
    print("[6/8] Creating residuals analysis...")
    plot_residuals()
    
    print("[7/8] Creating error by RUL range chart...")
    plot_error_by_rul_range()
    
    print("[8/8] Creating summary dashboard...")
    plot_summary_dashboard()
    
    print("\n" + "="*70)
    print("ALL VISUALIZATIONS COMPLETE!")
    print("="*70)
    print(f"\nSaved to {DATA_DIR}:")
    print("  - viz_accuracy_pie.png")
    print("  - viz_model_comparison.png")
    print("  - viz_error_distribution.png")
    print("  - viz_feature_importance.png")
    print("  - viz_predictions_vs_actual.png")
    print("  - viz_residuals.png")
    print("  - viz_error_by_rul.png")
    print("  - viz_dashboard.png")


if __name__ == "__main__":
    main()