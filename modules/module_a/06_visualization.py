"""
06_visualization.py — Generate all plots for EV Battery Analysis.

Plots:
  1. Correlation heatmap
  2. Feature importance (RF, XGB, SHAP)
  3. Actual vs Predicted (all models)
  4. Residual plots
  5. Time-series predictions
  6. Model comparison (bar + radar)
  7. DL training/validation loss curves
  8. SOC/SOH/RUL distribution plots
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from utils import get_logger, print_header, print_step, print_success, load_csv

logger = get_logger("06_visualization", cfg.LOGS_DIR)

# ── Global style
plt.rcParams.update({
    "figure.dpi":        150,
    "figure.facecolor":  "#0F1117",
    "axes.facecolor":    "#1A1D2E",
    "axes.edgecolor":    "#2D3250",
    "axes.labelcolor":   "#E0E0E0",
    "xtick.color":       "#9E9E9E",
    "ytick.color":       "#9E9E9E",
    "text.color":        "#E0E0E0",
    "grid.color":        "#2D3250",
    "grid.linestyle":    "--",
    "grid.alpha":        0.5,
    "font.family":       "DejaVu Sans",
    "font.size":         10,
    "axes.titlesize":    12,
    "axes.titleweight":  "bold",
    "legend.facecolor":  "#1A1D2E",
    "legend.edgecolor":  "#2D3250",
    "savefig.facecolor": "#0F1117",
    "savefig.bbox":      "tight",
    "savefig.pad_inches": 0.2,
})

PALETTE = ["#00D4FF", "#FF6B6B", "#4ECDC4", "#FFE66D", "#A78BFA",
           "#F97316", "#10B981", "#3B82F6", "#EC4899", "#84CC16",
           "#F59E0B", "#6366F1", "#14B8A6"]

TASK_COLORS = {
    "SOC": "#00D4FF", "SOH": "#10B981", "RUL": "#F97316", "Mileage": "#A78BFA"
}


def save_plot(fig, filename: str, subdir: str = ""):
    path = os.path.join(cfg.PLOTS_DIR, subdir, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    logger.info(f"  Plot saved: {os.path.basename(path)}")
    return path


# ─────────────────────────────────────────────
#  1. CORRELATION HEATMAP
# ─────────────────────────────────────────────
def plot_correlation_heatmap(df: pd.DataFrame, task: str, max_cols: int = 20):
    numeric = df.select_dtypes(include=np.number)

    # Drop all-null columns and low-variance
    numeric = numeric.dropna(axis=1, how="all")
    numeric = numeric.loc[:, numeric.std() > 0]

    if numeric.shape[1] > max_cols:
        # Keep cols most correlated with first numeric col (proxy target)
        corr_with_first = numeric.corrwith(numeric.iloc[:, 0]).abs().sort_values(ascending=False)
        numeric = numeric[corr_with_first.index[:max_cols]]

    corr = numeric.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))

    fig, ax = plt.subplots(figsize=(14, 11))
    sns.heatmap(
        corr, mask=mask, ax=ax,
        cmap=sns.diverging_palette(220, 10, as_cmap=True),
        center=0, vmin=-1, vmax=1,
        annot=corr.shape[0] <= 15,
        fmt=".2f" if corr.shape[0] <= 15 else "",
        linewidths=0.5, linecolor="#0F1117",
        cbar_kws={"shrink": 0.8, "label": "Pearson r"},
    )
    ax.set_title(f"Feature Correlation Heatmap — {task}", pad=15)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    return save_plot(fig, f"{task}_correlation_heatmap.png")


# ─────────────────────────────────────────────
#  2. FEATURE IMPORTANCE
# ─────────────────────────────────────────────
def _get_inner_model(model):
    """Unwrap sklearn Pipeline to get the actual estimator."""
    from sklearn.pipeline import Pipeline
    if isinstance(model, Pipeline):
        return model.steps[-1][1]
    return model


def plot_feature_importance(model, feature_names: list, task: str, model_name: str,
                            top_n: int = 20, subdir: str = "feature_importance"):
    inner = _get_inner_model(model)
    if not hasattr(inner, "feature_importances_"):
        return None

    importances = inner.feature_importances_
    idx = np.argsort(importances)[::-1][:top_n]

    fig, ax = plt.subplots(figsize=(10, 7))
    colors = [PALETTE[i % len(PALETTE)] for i in range(len(idx))]
    bars = ax.barh(
        [feature_names[i] for i in idx[::-1]],
        importances[idx[::-1]],
        color=colors, alpha=0.85, edgecolor="#0F1117"
    )

    # Add value labels
    for bar, val in zip(bars, importances[idx[::-1]]):
        ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height() / 2,
                f"{val:.4f}", va="center", fontsize=8, color="#E0E0E0")

    ax.set_xlabel("Feature Importance Score")
    ax.set_title(f"Feature Importance — {model_name} [{task}]", pad=12)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.4)
    return save_plot(fig, f"{task}_{model_name}_feature_importance.png", subdir=subdir)


# ─────────────────────────────────────────────
#  3. ACTUAL VS PREDICTED
# ─────────────────────────────────────────────
def plot_actual_vs_predicted(y_true, y_pred, task: str, model_name: str):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    color = TASK_COLORS.get(task, "#00D4FF")

    # ── Scatter plot
    ax = axes[0]
    ax.scatter(y_true, y_pred, alpha=0.4, s=15, color=color, edgecolors="none")
    lim_min = min(y_true.min(), y_pred.min())
    lim_max = max(y_true.max(), y_pred.max())
    ax.plot([lim_min, lim_max], [lim_min, lim_max], "w--", lw=1.5, label="Perfect")
    ax.set_xlabel("Actual")
    ax.set_ylabel("Predicted")
    ax.set_title(f"Actual vs Predicted — {model_name} [{task}]")
    ax.legend()

    from sklearn.metrics import r2_score, mean_squared_error
    r2   = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    ax.annotate(f"R² = {r2:.4f}\nRMSE = {rmse:.4f}",
                xy=(0.05, 0.90), xycoords="axes fraction",
                fontsize=10, color="#FFE66D",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#252840", alpha=0.8))

    # ── Residual distribution
    ax2 = axes[1]
    residuals = y_pred - y_true
    ax2.hist(residuals, bins=50, color=color, alpha=0.7, edgecolor="#0F1117")
    ax2.axvline(0, color="white", linestyle="--", lw=1.5)
    ax2.axvline(residuals.mean(), color="#FFE66D", linestyle="-.", lw=1.5, label=f"Mean={residuals.mean():.2f}")
    ax2.set_xlabel("Residuals (Predicted − Actual)")
    ax2.set_ylabel("Count")
    ax2.set_title(f"Residual Distribution — {model_name} [{task}]")
    ax2.legend()

    plt.tight_layout()
    return save_plot(fig, f"{task}_{model_name}_actual_vs_predicted.png", subdir="actual_vs_predicted")


# ─────────────────────────────────────────────
#  3b. TRAIN vs TEST LINE CHART (per model, overlapping)
# ─────────────────────────────────────────────
def plot_train_vs_test_line(
    y_train: np.ndarray,
    y_train_pred: np.ndarray,
    y_test: np.ndarray,
    y_test_pred: np.ndarray,
    task: str,
    model_name: str,
    max_points: int = 300,
    subdir: str = "line_graph",
):
    """
    Single overlapping line chart with all 4 lines:
      Train Actual     (solid, #3B82F6 blue)
      Train Predicted  (dashed, #00D4FF cyan)
      Test Actual      (solid, #F97316 orange)
      Test Predicted   (dashed, #FFE66D yellow)

    Layout: train samples on left (blue bg), test samples on right
    (orange bg), separated by a vertical dashed white line.
    This makes train/test performance directly comparable.
    """
    from sklearn.metrics import r2_score, mean_squared_error

    # Subsample each split evenly
    n_tr = min(max_points, len(y_train))
    n_ts = min(max_points, len(y_test))
    idx_tr = np.linspace(0, len(y_train) - 1, n_tr, dtype=int)
    idx_ts = np.linspace(0, len(y_test)  - 1, n_ts, dtype=int)

    yt_act  = y_train[idx_tr]
    yt_pred = y_train_pred[idx_tr]
    yv_act  = y_test[idx_ts]
    yv_pred = y_test_pred[idx_ts]

    # Build continuous x-axis: train [0, n_tr), test [n_tr, n_tr+n_ts)
    x_tr = np.arange(n_tr)
    x_ts = np.arange(n_tr, n_tr + n_ts)
    split_x = n_tr  # divider position

    # Metrics
    r2_tr   = r2_score(yt_act,  yt_pred)
    r2_ts   = r2_score(yv_act,  yv_pred)
    rmse_tr = np.sqrt(mean_squared_error(yt_act,  yt_pred))
    rmse_ts = np.sqrt(mean_squared_error(yv_act,  yv_pred))

    fig, ax = plt.subplots(figsize=(18, 6))
    fig.patch.set_facecolor("#0F1117")
    ax.set_facecolor("#0F1117")

    # ── Background shading
    ax.axvspan(0,       split_x,          alpha=0.07, color="#3B82F6", label="_nolegend_")  # train region
    ax.axvspan(split_x, split_x + n_ts,   alpha=0.07, color="#F97316", label="_nolegend_")  # test region

    # ── Train lines
    ax.plot(x_tr, yt_act,  color="#3B82F6", lw=1.8, alpha=0.95, label="Train Actual")
    ax.plot(x_tr, yt_pred, color="#00D4FF", lw=1.5, alpha=0.90,
            linestyle="--", label="Train Predicted")

    # ── Test lines
    ax.plot(x_ts, yv_act,  color="#F97316", lw=1.8, alpha=0.95, label="Test Actual")
    ax.plot(x_ts, yv_pred, color="#FFE66D", lw=1.5, alpha=0.90,
            linestyle="--", label="Test Predicted")

    # ── Divider line
    ax.axvline(split_x, color="white", lw=1.5, linestyle=":", alpha=0.7)
    ax.text(split_x - n_tr * 0.05,  ax.get_ylim()[1] if ax.get_ylim()[1] != 0 else 1,
            "TRAIN", fontsize=9, color="#3B82F6", ha="right", va="top",
            fontweight="bold", alpha=0.8)
    ax.text(split_x + n_ts * 0.02, ax.get_ylim()[1] if ax.get_ylim()[1] != 0 else 1,
            "TEST",  fontsize=9, color="#F97316", ha="left",  va="top",
            fontweight="bold", alpha=0.8)

    # ── Error bands
    ax.fill_between(x_tr, yt_act, yt_pred, alpha=0.10, color="#00D4FF")
    ax.fill_between(x_ts, yv_act, yv_pred, alpha=0.10, color="#FFE66D")

    # ── Metrics annotation boxes
    ax.annotate(
        f"TRAIN\nR\u00b2 = {r2_tr:.4f}\nRMSE = {rmse_tr:.4f}",
        xy=(n_tr * 0.5, 0.97), xycoords=("data", "axes fraction"),
        ha="center", va="top", fontsize=9, color="#00D4FF",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#1A1D2E", alpha=0.85,
                  edgecolor="#3B82F6", lw=1),
    )
    ax.annotate(
        f"TEST\nR\u00b2 = {r2_ts:.4f}\nRMSE = {rmse_ts:.4f}",
        xy=(split_x + n_ts * 0.5, 0.97), xycoords=("data", "axes fraction"),
        ha="center", va="top", fontsize=9, color="#FFE66D",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#1A1D2E", alpha=0.85,
                  edgecolor="#F97316", lw=1),
    )

    ax.set_xlabel("Sample Index  (left = train | right = test)", fontsize=10)
    ax.set_ylabel(task, fontsize=10)
    ax.set_title(
        f"Train vs Test Comparison  —  {model_name}  [{task}]",
        fontsize=12, fontweight="bold", color="white", pad=12
    )
    ax.legend(loc="upper right", fontsize=9, framealpha=0.85)
    ax.grid(True, alpha=0.25)
    ax.set_xlim(0, n_tr + n_ts)

    plt.tight_layout()
    return save_plot(fig, f"{task}_{model_name}_line.png", subdir=subdir)


# ─────────────────────────────────────────────
#  4. MODEL COMPARISON CHARTS
# ─────────────────────────────────────────────
def plot_model_comparison(comparison_df: pd.DataFrame, task: str, metric: str = "R2"):
    task_df = comparison_df[comparison_df["Task"] == task].copy()
    if task_df.empty:
        return None

    task_df = task_df.sort_values(metric, ascending=(metric == "RMSE"))
    models  = task_df["Model"].tolist()
    values  = task_df[metric].tolist()
    types   = task_df["Type"].tolist()

    colors = ["#00D4FF" if t == "ML" else "#F97316" for t in types]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(models, values, color=colors, alpha=0.85, edgecolor="#0F1117", width=0.6)

    # Labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{val:.4f}", ha="center", va="bottom", fontsize=9, color="#E0E0E0")

    ax.set_ylabel(metric)
    ax.set_title(f"{metric} Comparison — {task}", pad=12)
    plt.xticks(rotation=35, ha="right")

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#00D4FF", label="ML Models"),
        Patch(facecolor="#F97316", label="DL Models"),
    ]
    ax.legend(handles=legend_elements, loc="upper right")
    ax.grid(axis="y", alpha=0.4)

    return save_plot(fig, f"{task}_{metric}_comparison.png")


def plot_all_tasks_comparison(comparison_df: pd.DataFrame):
    """4-panel bar chart: best R² per task."""
    tasks = comparison_df["Task"].unique()
    n = len(tasks)
    if n == 0:
        return None

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()

    for i, task in enumerate(tasks):
        task_df = comparison_df[comparison_df["Task"] == task].sort_values("R2", ascending=True)
        ax = axes[i]
        colors = ["#00D4FF" if t == "ML" else "#F97316" for t in task_df["Type"]]
        ax.barh(task_df["Model"], task_df["R2"], color=colors, alpha=0.85, edgecolor="#0F1117")
        ax.set_title(f"{task} — R² Score", color=TASK_COLORS.get(task, "white"))
        ax.set_xlabel("R² Score")
        ax.axvline(0.9, color="#FFE66D", linestyle="--", lw=1, alpha=0.6, label="R²=0.9")
        ax.legend(fontsize=8)

    for j in range(i + 1, 4):
        axes[j].set_visible(False)

    plt.suptitle("Model Comparison Across All Prediction Tasks",
                 fontsize=14, fontweight="bold", color="white", y=1.01)
    plt.tight_layout()
    return save_plot(fig, "all_tasks_comparison.png")


# ─────────────────────────────────────────────
#  5. DL TRAINING LOSS CURVES
# ─────────────────────────────────────────────
def plot_training_history(history: dict, task: str, model_name: str):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    color1, color2 = "#00D4FF", "#FF6B6B"

    # Loss
    ax1 = axes[0]
    ax1.plot(history.get("loss", []),     color=color1, lw=1.8, label="Train Loss")
    ax1.plot(history.get("val_loss", []), color=color2, lw=1.8,
             linestyle="--", label="Val Loss")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("MSE Loss")
    ax1.set_title(f"Training Loss — {model_name} [{task}]")
    ax1.legend()

    # MAE
    ax2 = axes[1]
    ax2.plot(history.get("mae", []),     color=color1, lw=1.8, label="Train MAE")
    ax2.plot(history.get("val_mae", []), color=color2, lw=1.8,
             linestyle="--", label="Val MAE")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("MAE")
    ax2.set_title(f"Training MAE — {model_name} [{task}]")
    ax2.legend()

    plt.tight_layout()
    return save_plot(fig, f"{task}_{model_name}_loss_curves.png", subdir="loss_curves")


# ─────────────────────────────────────────────
#  6. DATA DISTRIBUTION PLOTS
# ─────────────────────────────────────────────
def plot_target_distributions(dfs: dict):
    """Plot distributions of SOC, SOH, RUL, Mileage targets."""
    targets = {
        "SOC":     ("features_soc",     "soc",              "#00D4FF"),
        "SOH":     ("features_soh",     "soh",              "#10B981"),
        "RUL":     ("features_rul",     "rul_proxy",        "#F97316"),
        "Mileage": ("features_mileage", "mileage_per_charge", "#A78BFA"),
    }

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for i, (task, (key, col, color)) in enumerate(targets.items()):
        ax = axes[i]
        path = cfg.PROCESSED_FILES.get(key, "")
        if not os.path.exists(path):
            ax.set_visible(False)
            continue

        df = pd.read_csv(path, usecols=[col] if col in pd.read_csv(path, nrows=0).columns else None,
                         low_memory=False)
        if col not in df.columns:
            ax.set_visible(False)
            continue

        data = df[col].dropna()
        ax.hist(data, bins=50, color=color, alpha=0.75, edgecolor="#0F1117")
        ax.axvline(data.mean(), color="white", linestyle="--", lw=1.5,
                   label=f"Mean: {data.mean():.2f}")
        ax.axvline(data.median(), color="#FFE66D", linestyle="-.", lw=1.5,
                   label=f"Median: {data.median():.2f}")
        ax.set_title(f"{task} Distribution (n={len(data):,})")
        ax.set_xlabel(col)
        ax.set_ylabel("Count")
        ax.legend(fontsize=8)

    plt.suptitle("Target Variable Distributions", fontsize=13, fontweight="bold",
                 color="white", y=1.01)
    plt.tight_layout()
    return save_plot(fig, "target_distributions.png")


# ─────────────────────────────────────────────
#  7. SHAP SUMMARY PLOT
# ─────────────────────────────────────────────
def plot_shap_importance(task: str, model_name: str):
    shap_path = os.path.join(cfg.REPORTS_DIR, f"{task}_{model_name}_shap.csv")
    if not os.path.exists(shap_path):
        return None

    shap_df = pd.read_csv(shap_path).head(20)
    fig, ax = plt.subplots(figsize=(10, 7))

    colors = [PALETTE[i % len(PALETTE)] for i in range(len(shap_df))]
    ax.barh(shap_df["feature"][::-1], shap_df["importance"][::-1],
            color=colors, alpha=0.85, edgecolor="#0F1117")
    ax.set_xlabel("Mean |SHAP Value|")
    ax.set_title(f"SHAP Feature Importance — {model_name} [{task}]", pad=12)

    return save_plot(fig, f"{task}_{model_name}_shap_importance.png", subdir="shap")


# ─────────────────────────────────────────────
#  8. RADAR CHART (Multi-metric comparison)
# ─────────────────────────────────────────────
def plot_radar_comparison(comparison_df: pd.DataFrame, task: str):
    """Radar chart comparing top-5 models on RMSE, MAE, R²."""
    task_df = comparison_df[comparison_df["Task"] == task].copy()
    if task_df.empty or len(task_df) < 2:
        return None

    top5 = task_df.sort_values("R2", ascending=False).head(5)

    # Normalize metrics to [0,1] for radar
    metrics = ["R2", "RMSE", "MAE"]
    data = top5[metrics].copy()

    # Invert RMSE and MAE so higher = better
    data["RMSE"] = 1 - (data["RMSE"] - data["RMSE"].min()) / (data["RMSE"].max() - data["RMSE"].min() + 1e-9)
    data["MAE"]  = 1 - (data["MAE"]  - data["MAE"].min())  / (data["MAE"].max()  - data["MAE"].min()  + 1e-9)
    data["R2"]   = (data["R2"]   - data["R2"].min())   / (data["R2"].max()   - data["R2"].min()   + 1e-9)

    N = len(metrics)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.set_facecolor("#1A1D2E")

    for i, (_, row) in enumerate(top5.iterrows()):
        vals = data.loc[row.name, metrics].tolist()
        vals += vals[:1]
        color = PALETTE[i % len(PALETTE)]
        ax.plot(angles, vals, "o-", color=color, lw=2, label=row["Model"])
        ax.fill(angles, vals, alpha=0.15, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, fontsize=11, color="white")
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], fontsize=7, color="#9E9E9E")
    ax.set_title(f"Model Radar — {task}", pad=20, fontsize=13)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=9)

    return save_plot(fig, f"{task}_radar_comparison.png")


# ─────────────────────────────────────────────
#  SUMMARY DASHBOARD
# ─────────────────────────────────────────────
def plot_summary_dashboard(comparison_df: pd.DataFrame):
    """Create a full-page summary heatmap of all models × tasks."""
    if comparison_df.empty:
        return None

    pivot = comparison_df.pivot_table(index="Model", columns="Task", values="R2", aggfunc="max")
    pivot = pivot.fillna(0)

    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto", vmin=0, vmax=1)

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=11)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=9)

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            color = "black" if val > 0.6 else "white"
            ax.text(j, i, f"{val:.3f}", ha="center", va="center",
                    fontsize=10, color=color, fontweight="bold")

    plt.colorbar(im, ax=ax, label="R² Score", shrink=0.8)
    ax.set_title("R² Score Summary — All Models × All Tasks",
                 fontsize=13, pad=15)
    plt.tight_layout()
    return save_plot(fig, "summary_dashboard.png")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def run_visualization(training_results: dict = None):
    print_header("STEP 6: VISUALIZATION")

    # ── Target distributions
    print_step("Plotting target distributions...")
    plot_target_distributions({})

    # ── Correlation heatmaps
    print_step("Plotting correlation heatmaps...")
    for task_key, feat_key in [
        ("SOC", "features_soc"), ("SOH", "features_soh"),
        ("RUL", "features_rul"), ("Mileage", "features_mileage"),
    ]:
        path = cfg.PROCESSED_FILES.get(feat_key)
        if path and os.path.exists(path):
            df = pd.read_csv(path, low_memory=False)
            plot_correlation_heatmap(df, task_key)

    if training_results:
        # ── Called from pipeline (in-memory results available)
        # Load comparison CSV if available
        # ── Load comparison CSV if available
        comp_path = os.path.join(cfg.REPORTS_DIR, "model_comparison.csv")
        if os.path.exists(comp_path):
            comp_df = pd.read_csv(comp_path)
        else:
            from evaluation import build_comparison_table
            comp_df = build_comparison_table(training_results)

        # ── Model comparison charts
        print_step("Plotting model comparison charts...")
        for task in ["SOC", "SOH", "RUL", "Mileage"]:
            for metric in ["R2", "RMSE"]:
                plot_model_comparison(comp_df, task, metric)
            plot_radar_comparison(comp_df, task)

        # ── All-task comparison
        plot_all_tasks_comparison(comp_df)

        # ── Summary dashboard
        plot_summary_dashboard(comp_df)

        # ── Per-model plots
        print_step("Plotting actual vs predicted, line charts, and feature importances...")
        for task, task_data in training_results.items():
            y_test_path = os.path.join(cfg.RESULTS_DIR, f"{task}_y_test.npy")
            y_train_path = os.path.join(cfg.RESULTS_DIR, f"{task}_X_test.npy")  # used only for existence check
            if not os.path.exists(y_test_path):
                continue
            y_test = np.load(y_test_path)

            for split in ["ml", "dl"]:
                for model_name, result in task_data.get(split, {}).items():
                    y_pred = result.get("y_pred")
                    y_true = result.get("y_true", y_test)
                    if y_pred is not None and len(y_pred) == len(y_true):
                        plot_actual_vs_predicted(y_true, y_pred, task, model_name)

                    # ── Train vs Test LINE CHART (requires y_train + y_train_pred)
                    y_train_pred = result.get("y_pred_train")
                    y_train_true = result.get("y_train")
                    if (
                        y_pred is not None
                        and y_train_pred is not None
                        and y_train_true is not None
                    ):
                        plot_train_vs_test_line(
                            np.asarray(y_train_true),
                            np.asarray(y_train_pred),
                            np.asarray(y_true),
                            np.asarray(y_pred),
                            task, model_name,
                        )

                    # DL loss curves
                    if split == "dl" and "history" in result:
                        plot_training_history(result["history"], task, model_name)

                    # Feature importance for tree models
                    if split == "ml":
                        feat_path = cfg.PROCESSED_FILES.get(f"features_{task.lower()}")
                        if feat_path and os.path.exists(feat_path):
                            df_feat = pd.read_csv(feat_path, nrows=0)
                            target_col = {"SOC": "soc", "SOH": "soh",
                                         "RUL": "rul_proxy", "Mileage": "mileage_per_charge"}.get(task)
                            feat_cols = [c for c in df_feat.columns
                                         if c not in ["vehicle_no", "chassis_no", "timestamp", target_col]]
                            model = result.get("model")
                            inner_m = _get_inner_model(model) if model else None
                            if inner_m and hasattr(inner_m, "feature_importances_"):
                                plot_feature_importance(model, feat_cols, task, model_name,
                                                        subdir="feature_importance")

        # ── SHAP plots
        print_step("Plotting SHAP importance...")
        for task in ["SOC", "SOH", "RUL", "Mileage"]:
            for model_name in ["RandomForest", "XGBoost"]:
                plot_shap_importance(task, model_name)

    else:
        # ── Standalone mode: no in-memory results, load from disk
        print_step("Standalone mode — loading saved models for line charts...")
        comp_path = os.path.join(cfg.REPORTS_DIR, "model_comparison.csv")
        if os.path.exists(comp_path):
            comp_df = pd.read_csv(comp_path)
            print_step("Plotting model comparison charts from saved CSV...")
            for task in ["SOC", "SOH", "RUL", "Mileage"]:
                for metric in ["R2", "RMSE"]:
                    plot_model_comparison(comp_df, task, metric)
                plot_radar_comparison(comp_df, task)
            plot_all_tasks_comparison(comp_df)
            plot_summary_dashboard(comp_df)
        else:
            print_warning("No model_comparison.csv found — run 05_evaluation.py first for comparison charts")

        # SHAP plots from saved CSVs
        print_step("Plotting SHAP importance from saved CSVs...")
        for task in ["SOC", "SOH", "RUL", "Mileage"]:
            for model_name in ["RandomForest", "XGBoost"]:
                plot_shap_importance(task, model_name)

        # Line charts from saved .pkl models
        standalone_line_charts()

    print_success(f"All plots saved to: {cfg.PLOTS_DIR}")


# ─────────────────────────────────────────────
#  STANDALONE LINE CHART GENERATOR
#  Works without training_results — loads .pkl models from disk
# ─────────────────────────────────────────────
def standalone_line_charts():
    """
    Regenerate train vs test line charts fully from disk:
      - Loads saved .pkl models from models/
      - Loads feature CSVs from processed_data/
      - Splits data using same 80/20 random_state=42 as training
      - Runs predictions on both splits
      - Saves charts to plots/line_graph/
    No training_results dict required.
    """
    import joblib
    from sklearn.model_selection import train_test_split

    print_step("Generating line charts from saved models (standalone)...")

    TASK_CONFIG = {
        "SOC":     {"feat_key": "features_soc",     "target": "soc"},
        "SOH":     {"feat_key": "features_soh",     "target": "soh"},
        "RUL":     {"feat_key": "features_rul",     "target": "rul_proxy"},
        "Mileage": {"feat_key": "features_mileage", "target": "mileage_per_charge"},
    }

    # Same exclusion list as 04_model_training.py
    GLOBAL_EXCL = [
        "vehicle_no", "chassis_no", "imei", "timestamp",
        "start_time", "end_time", "source_file", "gps", "start_gps", "end_gps",
        "_id", "oem_model", "oem", "model", "alert_type", "drive_mode",
        "vehicle_status", "city", "duration", "vehicle_no.1",
    ]
    TASK_EXCL = {
        "SOC":     ["rolling_soc_5","rolling_soc_10","rolling_soc_20",
                   "rolling_soc_std_5","rolling_soc_std_10","charge_state_pct"],
        "SOH":     ["soc","charge_state_pct","rolling_soc_5","rolling_soc_10",
                   "rolling_soc_20","rolling_soc_std_5","rolling_soc_std_10",
                   "soh_lag1","soh_change"],
        "RUL":     ["charge_cycle_count","cycle_usage_ratio"],
        "Mileage": ["soc_drain","soc_at_start","soc_at_end",
                   "distance_per_soc_drop","soc_drain_rate","energy_per_soc"],
    }

    ML_MODELS = [
        "RandomForest", "GradientBoosting", "XGBoost", "ExtraTrees",
        "DecisionTree", "KNN", "Ridge", "Lasso",
    ]

    charts_made = 0

    for task, conf in TASK_CONFIG.items():
        feat_path = cfg.PROCESSED_FILES.get(conf["feat_key"], "")
        target    = conf["target"]

        if not feat_path or not os.path.exists(feat_path):
            logger.warning(f"  {task}: feature CSV not found, skipping")
            continue

        # Load features
        df = pd.read_csv(feat_path, low_memory=False)
        df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=[target])

        excl = set(GLOBAL_EXCL + TASK_EXCL.get(task, []) + [target])
        feat_cols = [c for c in df.select_dtypes(include=np.number).columns
                     if c not in excl]

        X = df[feat_cols].fillna(df[feat_cols].median().fillna(0)).fillna(0).values
        y = df[target].values

        # Same split as training
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Load each saved ML model — track best by test R²
        best_r2       = -np.inf
        best_model_name  = None
        best_y_train      = None
        best_y_train_pred = None
        best_y_test       = None
        best_y_test_pred  = None

        for model_name in ML_MODELS:
            pkl_path = os.path.join(cfg.MODELS_DIR, f"{task}_{model_name}.pkl")
            if not os.path.exists(pkl_path):
                continue
            try:
                from sklearn.metrics import r2_score
                model        = joblib.load(pkl_path)
                y_train_pred = model.predict(X_train)
                y_test_pred  = model.predict(X_test)

                # Save line chart to main line_graph folder
                plot_train_vs_test_line(
                    y_train, y_train_pred,
                    y_test,  y_test_pred,
                    task, model_name,
                    subdir="line_graph",
                )
                charts_made += 1

                # Track best model by test R²
                test_r2 = r2_score(y_test, y_test_pred)
                if test_r2 > best_r2:
                    best_r2            = test_r2
                    best_model_name    = model_name
                    best_y_train       = y_train
                    best_y_train_pred  = y_train_pred
                    best_y_test        = y_test
                    best_y_test_pred   = y_test_pred

            except Exception as e:
                logger.warning(f"  Line chart failed [{task}/{model_name}]: {e}")

        # Save best model chart to line_graph_best/
        if best_model_name is not None:
            print_step(f"  Best for {task}: {best_model_name} (R²={best_r2:.4f})")
            plot_train_vs_test_line(
                best_y_train, best_y_train_pred,
                best_y_test,  best_y_test_pred,
                task, best_model_name,
                subdir="line_graph_best",
            )

    print_success(f"Line charts done: {charts_made} charts saved to plots/line_graph/")


if __name__ == "__main__":
    # Run standalone — loads comparison CSV + models from disk
    run_visualization()
