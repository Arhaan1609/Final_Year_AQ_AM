"""
visualization_improved.py
=========================
Generates all plots for the improved RUL-to-knee pipeline.
Saves to plots/ directory, matching the existing plot naming scheme
while also adding new diagnostic charts for the fixed models.

Run AFTER improved_pipeline.py (or train_evaluate.py + train_dl.py) completes.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')   # non-interactive backend — safe for all environments
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
import os
from sklearn.linear_model import LinearRegression

# ─── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR   = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Style ──────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0f1117',
    'axes.facecolor':   '#1a1d2e',
    'axes.edgecolor':   '#2d3154',
    'axes.labelcolor':  '#e0e0e0',
    'axes.titlecolor':  '#ffffff',
    'xtick.color':      '#b0b0b0',
    'ytick.color':      '#b0b0b0',
    'text.color':       '#e0e0e0',
    'grid.color':       '#2d3154',
    'grid.linewidth':   0.8,
    'legend.facecolor': '#1e2236',
    'legend.edgecolor': '#3a3f6b',
    'font.family':      'DejaVu Sans',
    'font.size':        10,
})

PALETTE = ['#00d4ff', '#ff6b6b', '#a8ff78', '#ffd700', '#ff9f43',
           '#ee5a24', '#0652DD', '#9980FA', '#fd79a8', '#55efc4']


# ─────────────────────────────────────────────────────────────────────────────
# 1. DEGRADATION CURVE + KNEE
# ─────────────────────────────────────────────────────────────────────────────
def plot_degradation_and_knee(df, chassis_id):
    group = df[df['chassis_no'] == chassis_id].sort_values('charge_cycle_count')
    if group.empty or 'smoothed_capacity' not in group.columns:
        print(f"  Skipping degradation plot for {chassis_id} — missing columns")
        return
    if 'knee_cycle' not in group.columns:
        print(f"  Skipping degradation plot for {chassis_id} — no knee_cycle column")
        return

    cycles   = group['charge_cycle_count'].values
    capacity = group['smoothed_capacity'].values
    knee_cy  = group['knee_cycle'].iloc[0]
    knee_idx = int(np.argmin(np.abs(cycles - knee_cy)))

    x1, y1 = cycles[:knee_idx+1].reshape(-1,1), capacity[:knee_idx+1]
    x2, y2 = cycles[knee_idx:].reshape(-1,1),   capacity[knee_idx:]

    lr1 = LinearRegression().fit(x1, y1)
    lr2 = LinearRegression().fit(x2, y2)

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(cycles, capacity, color='#00d4ff', linewidth=2.5, label='Smoothed Capacity', zorder=3)
    if len(x1) > 1:
        ax.plot(x1, lr1.predict(x1), color='#a8ff78', linestyle='--', linewidth=2, label='Phase 1: Gradual Decay')
    if len(x2) > 1:
        ax.plot(x2, lr2.predict(x2), color='#ff6b6b', linestyle='--', linewidth=2, label='Phase 2: Accelerated Decay')
    ax.axvline(x=knee_cy, color='#ffd700', linestyle='--', linewidth=2.5, label=f'Knee Point: {knee_cy:.0f}')
    ax.fill_between(cycles[:knee_idx+1], capacity[:knee_idx+1], alpha=0.08, color='#a8ff78')
    ax.fill_between(cycles[knee_idx:],   capacity[knee_idx:],   alpha=0.08, color='#ff6b6b')

    ax.set_title(f"Battery Degradation Curve — {chassis_id}", fontsize=15, fontweight='bold', pad=15)
    ax.set_xlabel("Charge Cycle Count", fontsize=12)
    ax.set_ylabel("Normalized Capacity", fontsize=12)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = os.path.join(OUTPUT_DIR, f"degradation_{chassis_id}.png")
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. KNEE DERIVATIVE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
def plot_knee_derivatives(df, chassis_id):
    group = df[df['chassis_no'] == chassis_id].sort_values('charge_cycle_count')
    if len(group) < 20 or 'smoothed_capacity' not in group.columns:
        return

    cycles   = group['charge_cycle_count'].values
    capacity = group['smoothed_capacity'].values
    f1       = np.gradient(capacity, cycles)
    f2       = np.gradient(f1, cycles)
    f2s      = pd.Series(f2).rolling(window=11, center=True).mean().fillna(0).values

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9), sharex=True)
    ax1.plot(cycles, f1, color='#a8ff78', linewidth=1.8, label='1st Derivative (Degradation Rate)')
    ax1.axhline(0, color='#ffffff', linestyle=':', alpha=0.4)
    ax1.set_ylabel("dC / dCycle", fontsize=11)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    ax2.plot(cycles, f2s, color='#9980FA', linewidth=1.8, label='2nd Derivative (Smoothed)')
    if 'knee_cycle' in group.columns:
        kc = group['knee_cycle'].iloc[0]
        ax2.axvline(x=kc, color='#ffd700', linestyle='--', linewidth=2, label=f'Knee @ {kc:.0f}')
    ax2.axhline(0, color='#ffffff', linestyle=':', alpha=0.4)
    ax2.set_ylabel("d²C / dCycle²", fontsize=11)
    ax2.set_xlabel("Cycle Count", fontsize=11)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.suptitle(f"Knee Detection Analysis — {chassis_id}", fontsize=14, fontweight='bold', y=1.01)
    fig.tight_layout()
    out = os.path.join(OUTPUT_DIR, f"knee_analysis_{chassis_id}.png")
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. MODEL COMPARISON (RMSE + R² + Bias)
# ─────────────────────────────────────────────────────────────────────────────
def plot_model_comparison(metrics_df):
    df = metrics_df.copy().drop_duplicates('Model').sort_values('RMSE')

    n_metrics = sum(c in df.columns for c in ['RMSE', 'MAE', 'R2_Test', 'Bias'])
    ncols = min(n_metrics, 2)
    nrows = (n_metrics + 1) // 2

    fig, axes = plt.subplots(nrows, ncols, figsize=(16, 5 * nrows))
    axes = np.array(axes).flatten()
    idx  = 0

    for col, label, ascending, cmap in [
        ('RMSE',    'RMSE ↓ Lower is better',   True,  'coolwarm'),
        ('MAE',     'MAE ↓ Lower is better',    True,  'YlOrRd'),
        ('R2_Test', 'R² Test ↑ Higher is better', False, 'viridis'),
        ('Bias',    'Bias (pred − actual)',      True,  'PiYG'),
    ]:
        if col not in df.columns or idx >= len(axes):
            continue
        ax   = axes[idx]
        vals = df[col].values
        clrs = plt.cm.get_cmap(cmap)(
            (vals - vals.min()) / max(vals.max() - vals.min(), 1e-6)
        )
        bars = ax.barh(df['Model'], vals, color=clrs, edgecolor='#0f1117', linewidth=0.5)
        ax.set_xlabel(label, fontsize=11)
        ax.set_title(f"{col} Comparison", fontsize=13, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        ax.axvline(0, color='white', linewidth=0.6, alpha=0.5)
        for bar, v in zip(bars, vals):
            xpos = bar.get_width() + (abs(vals.max() - vals.min()) * 0.01)
            ax.text(xpos, bar.get_y() + bar.get_height()/2,
                    f'{v:.2f}', va='center', fontsize=8, color='#e0e0e0')
        idx += 1

    for a in axes[idx:]:
        a.set_visible(False)

    fig.suptitle("Model Comparison — Improved Pipeline", fontsize=16, fontweight='bold', y=1.01)
    fig.tight_layout()
    out = os.path.join(OUTPUT_DIR, "model_comparison.png")
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. PREDICTIONS SCATTER (Actual vs Predicted)
# ─────────────────────────────────────────────────────────────────────────────
def plot_predictions(pred_df, pred_cols=None):
    if pred_cols is None:
        pred_cols = [c for c in pred_df.columns if c != 'y_true']

    n  = len(pred_cols)
    nc = min(n, 3)
    nr = (n + nc - 1) // nc
    fig, axes = plt.subplots(nr, nc, figsize=(7 * nc, 6 * nr))
    axes = np.array(axes).flatten()

    y_true = pred_df['y_true'].values
    lim    = (min(y_true.min(), 0) * 0.95, y_true.max() * 1.05)

    for i, col in enumerate(pred_cols):
        ax    = axes[i]
        y_hat = pred_df[col].values
        color = PALETTE[i % len(PALETTE)]

        ax.scatter(y_true, y_hat, alpha=0.35, s=12, color=color, label=col)
        ax.plot(lim, lim, 'w--', linewidth=1.5, label='Perfect (y=x)', alpha=0.7)

        # Error bands ±15%
        x_arr = np.array(lim)
        ax.fill_between(x_arr, x_arr * 0.85, x_arr * 1.15,
                        alpha=0.07, color='#a8ff78', label='±15% band')

        r2   = 1 - np.sum((y_true - y_hat)**2) / (np.sum((y_true - y_true.mean())**2) + 1e-9)
        rmse = np.sqrt(np.mean((y_true - y_hat)**2))
        ax.set_title(f"{col}\nRMSE={rmse:.1f}  R²={r2:.3f}", fontsize=11, fontweight='bold')
        ax.set_xlabel("Actual RUL (Cycles)", fontsize=10)
        ax.set_ylabel("Predicted RUL (Cycles)", fontsize=10)
        ax.set_xlim(lim)
        ax.set_ylim(lim)
        ax.legend(fontsize=8, loc='upper left')
        ax.grid(True, alpha=0.3)

    for a in axes[len(pred_cols):]:
        a.set_visible(False)

    fig.suptitle("Actual vs Predicted RUL — All Models", fontsize=14, fontweight='bold', y=1.01)
    fig.tight_layout()
    out = os.path.join(OUTPUT_DIR, "predictions_scatter.png")
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 5. ERROR DISTRIBUTION (Residuals)
# ─────────────────────────────────────────────────────────────────────────────
def plot_error_distribution(pred_df, best_col=None):
    y_true = pred_df['y_true'].values
    if best_col is None:
        pred_cols = [c for c in pred_df.columns if c != 'y_true']
    else:
        pred_cols = [best_col] if best_col in pred_df.columns else [c for c in pred_df.columns if c != 'y_true']

    nc = min(len(pred_cols), 3)
    nr = (len(pred_cols) + nc - 1) // nc
    fig, axes = plt.subplots(nr, nc, figsize=(7 * nc, 5 * nr))
    axes = np.array(axes).flatten()

    for i, col in enumerate(pred_cols):
        ax   = axes[i]
        res  = pred_df[col].values - y_true
        color = PALETTE[i % len(PALETTE)]

        ax.hist(res, bins=50, color=color, alpha=0.75, edgecolor='#0f1117', density=True)
        ax.axvline(0, color='white', linestyle='--', linewidth=2, label='Zero bias')
        ax.axvline(res.mean(), color='#ffd700', linestyle='--', linewidth=1.5,
                   label=f'Mean={res.mean():.1f}')
        ax.set_title(f"Residuals: {col}", fontsize=11, fontweight='bold')
        ax.set_xlabel("Prediction Error (Predicted − Actual)", fontsize=10)
        ax.set_ylabel("Density", fontsize=10)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    for a in axes[len(pred_cols):]:
        a.set_visible(False)

    fig.suptitle("Residual Error Distribution — Improved Models", fontsize=14, fontweight='bold', y=1.01)
    fig.tight_layout()
    out = os.path.join(OUTPUT_DIR, "error_distribution.png")
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 6. ACCURACY PIE CHART (% Excellent / Good / Poor)
# ─────────────────────────────────────────────────────────────────────────────
def plot_accuracy_pie(pred_df, col='best'):
    y_true = pred_df['y_true'].values

    # Pick best column by RMSE
    pred_cols = [c for c in pred_df.columns if c != 'y_true']
    if col == 'best' or col not in pred_df.columns:
        rmse_map = {c: np.sqrt(np.mean((pred_df[c].values - y_true)**2)) for c in pred_cols}
        col = min(rmse_map, key=rmse_map.get)

    y_hat = pred_df[col].values
    pct   = np.abs(y_hat - y_true) / (np.abs(y_true) + 1e-6) * 100

    bands = {
        'Excellent\n(<5%)':  np.mean(pct < 5)  * 100,
        'Good\n(5–15%)':     np.mean((pct >= 5)  & (pct < 15)) * 100,
        'Fair\n(15–30%)':    np.mean((pct >= 15) & (pct < 30)) * 100,
        'Poor\n(>30%)':      np.mean(pct >= 30) * 100,
    }
    colors = ['#a8ff78', '#00d4ff', '#ffd700', '#ff6b6b']
    explode = [0.05, 0.02, 0.02, 0.02]

    fig, ax = plt.subplots(figsize=(9, 9))
    wedges, texts, autos = ax.pie(
        list(bands.values()),
        labels=list(bands.keys()),
        colors=colors,
        autopct='%1.1f%%',
        startangle=140,
        explode=explode,
        wedgeprops=dict(edgecolor='#0f1117', linewidth=2),
        textprops=dict(fontsize=12, color='white')
    )
    for auto in autos:
        auto.set_fontsize(11)
        auto.set_fontweight('bold')

    ax.set_title(f"Prediction Accuracy Distribution\n({col})", fontsize=14, fontweight='bold')
    out = os.path.join(OUTPUT_DIR, "accuracy_pie_chart.png")
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 7. FEATURE IMPORTANCE
# ─────────────────────────────────────────────────────────────────────────────
def plot_feature_importance(fi_df):
    df = fi_df.copy()
    if 'importance' not in df.columns:
        df.columns = ['importance']
    df = df[df['importance'] > 0].sort_values('importance', ascending=True).tail(15)

    fig, ax = plt.subplots(figsize=(11, 8))
    colors  = plt.cm.viridis(np.linspace(0.3, 1.0, len(df)))
    bars    = ax.barh(df.index, df['importance'], color=colors, edgecolor='#0f1117', linewidth=0.5)
    for bar, val in zip(bars, df['importance']):
        ax.text(bar.get_width() + df['importance'].max() * 0.01,
                bar.get_y() + bar.get_height()/2,
                f'{val:.4f}', va='center', fontsize=9, color='#e0e0e0')
    ax.set_xlabel("Importance Score", fontsize=12)
    ax.set_title("XGBoost Feature Importance — Top 15", fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    fig.tight_layout()
    out = os.path.join(OUTPUT_DIR, "feature_importance.png")
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 8. MODEL PERFORMANCE RADAR
# ─────────────────────────────────────────────────────────────────────────────
def plot_radar(metrics_df):
    df = metrics_df.copy().drop_duplicates('Model').head(8)
    cats = ['RMSE', 'MAE', 'R2_Test', 'Pct_Good', 'Pct_Poor']
    cats = [c for c in cats if c in df.columns]
    if len(cats) < 3:
        print("  Skipping radar — not enough metric columns")
        return

    N = len(cats)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    ax.set_facecolor('#1a1d2e')

    for i, (_, row) in enumerate(df.iterrows()):
        values = []
        for c in cats:
            v = float(row[c]) if c in row.index and not pd.isna(row[c]) else 0.0
            # Normalise to [0,1] min is best for RMSE/MAE/Pct_Poor, max is best for R2/Pct_Good
            col_min = df[c].min()
            col_max = df[c].max()
            rng = col_max - col_min
            if rng < 1e-9:
                norm = 0.5
            elif c in ['RMSE', 'MAE', 'Pct_Poor']:
                norm = 1 - (v - col_min) / rng   # invert: lower is better
            else:
                norm = (v - col_min) / rng
            values.append(norm)
        values += values[:1]
        color = PALETTE[i % len(PALETTE)]
        ax.plot(angles, values, color=color, linewidth=2)
        ax.fill(angles, values, color=color, alpha=0.1)
        ax.plot([], [], color=color, label=row['Model'])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(cats, fontsize=11, color='white')
    ax.set_yticklabels([])
    ax.set_title("Model Performance Radar\n(Normalised: outer edge = best)", fontsize=13,
                 fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=9)
    ax.grid(color='#2d3154', linewidth=0.8)
    ax.spines['polar'].set_color('#2d3154')
    fig.tight_layout()
    out = os.path.join(OUTPUT_DIR, "model_performance_radar.png")
    fig.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 9. SUMMARY CARD (per DL model)
# ─────────────────────────────────────────────────────────────────────────────
def plot_dl_summary(metrics_df):
    dl_names = [n for n in metrics_df['Model'].unique()
                if any(k in n.upper() for k in ['LSTM', 'GRU', 'CNN'])]
    for mname in dl_names:
        row = metrics_df[metrics_df['Model'] == mname].iloc[0]
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.axis('off')

        stats = []
        for col in ['RMSE', 'MAE', 'R2_Test', 'Bias', 'Pct_Good', 'Pct_Poor']:
            if col in row.index and not pd.isna(row[col]):
                stats.append((col, f"{row[col]:.3f}"))

        y_pos = 0.85
        ax.text(0.5, 0.97, mname, ha='center', va='top', fontsize=16, fontweight='bold',
                color='#00d4ff', transform=ax.transAxes)
        ax.text(0.5, 0.90, "Performance Summary (Fixed Pipeline)", ha='center', va='top',
                fontsize=10, color='#b0b0b0', transform=ax.transAxes)

        for label, value in stats:
            color = '#a8ff78' if label in ['R2_Test', 'Pct_Good'] else \
                    '#ff6b6b' if label in ['Pct_Poor'] else '#00d4ff'
            ax.text(0.25, y_pos, label, ha='left', va='top', fontsize=12,
                    color='#b0b0b0', transform=ax.transAxes)
            ax.text(0.65, y_pos, value, ha='left', va='top', fontsize=12,
                    fontweight='bold', color=color, transform=ax.transAxes)
            y_pos -= 0.12

        slug = mname.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
        out  = os.path.join(OUTPUT_DIR, f"summary_{slug}.png")
        fig.savefig(out, dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"  Saved: {out}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("  GENERATING VISUALIZATIONS")
    print("=" * 65)

    # ── Load data files ─────────────────────────────────────────────
    labeled_path = os.path.join(DATA_DIR, "labeled_features.csv")
    metrics_path = os.path.join(DATA_DIR, "model_metrics.csv")

    if not os.path.exists(labeled_path):
        print(f"ERROR: {labeled_path} not found. Run data_processing.py first.")
        return
    if not os.path.exists(metrics_path):
        print(f"ERROR: {metrics_path} not found. Run train_evaluate.py first.")
        return

    labeled_df  = pd.read_csv(labeled_path)
    metrics_df  = pd.read_csv(metrics_path)

    # Merge improved metrics if they exist
    imp_metrics = os.path.join(DATA_DIR, "improved_model_metrics.csv")
    if os.path.exists(imp_metrics):
        imp_df     = pd.read_csv(imp_metrics)
        metrics_df = pd.concat([metrics_df, imp_df], ignore_index=True).drop_duplicates('Model')
        print("  Loaded improved_model_metrics.csv")

    # ── Pick 2 sample chassis for per-chassis plots ──────────────────
    sample_chassis = labeled_df['chassis_no'].dropna().unique()[:2]

    print("\n[1/9] Degradation curves...")
    for cid in sample_chassis:
        plot_degradation_and_knee(labeled_df, cid)

    print("\n[2/9] Knee derivative analysis...")
    for cid in sample_chassis:
        plot_knee_derivatives(labeled_df, cid)

    print("\n[3/9] Model comparison bar chart...")
    plot_model_comparison(metrics_df)

    # ── Load predictions (tabular first, then DL) ────────────────────
    pred_df = None
    for fname in ["improved_predictions_tabular.csv", "predictions.csv"]:
        p = os.path.join(DATA_DIR, fname)
        if os.path.exists(p):
            pred_df = pd.read_csv(p)
            print(f"  Using predictions from {fname}")
            break

    if pred_df is not None:
        pred_cols = [c for c in pred_df.columns if c != 'y_true']

        print("\n[4/9] Actual vs Predicted scatter...")
        plot_predictions(pred_df, pred_cols)

        print("\n[5/9] Error distribution (residuals)...")
        plot_error_distribution(pred_df)

        print("\n[6/9] Accuracy pie chart...")
        plot_accuracy_pie(pred_df)
    else:
        print("  [!] No predictions file found — run train_evaluate.py or improved_pipeline.py first")

    print("\n[7/9] Feature importance...")
    fi_path = os.path.join(DATA_DIR, "feature_importance.csv")
    if os.path.exists(fi_path):
        fi_df = pd.read_csv(fi_path, index_col=0)
        plot_feature_importance(fi_df)
    else:
        print("  [!] feature_importance.csv not found — run ensemble.py or improved_pipeline.py")

    print("\n[8/9] Performance radar chart...")
    plot_radar(metrics_df)

    print("\n[9/9] DL model summary cards...")
    plot_dl_summary(metrics_df)

    print(f"\n{'='*65}")
    print(f"  All plots saved to: {OUTPUT_DIR}")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
