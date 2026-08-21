"""
05_evaluation.py — Comprehensive model evaluation, SHAP explainability, 
                   overfitting detection, robustness testing, and comparison table.
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import joblib
import json
from pathlib import Path

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from utils import (
    get_logger, print_header, print_step, print_success, print_warning,
    compute_metrics, format_metrics_table, load_csv
)

logger = get_logger("05_evaluation", cfg.LOGS_DIR)

TASKS = ["SOC", "SOH", "RUL", "Mileage"]
ML_MODELS = [
    "RandomForest", "GradientBoosting", "XGBoost", "ExtraTrees",
    "SVR", "DecisionTree", "KNN", "Ridge", "Lasso"
]


# ─────────────────────────────────────────────
#  LOAD SAVED MODELS AND DATA
# ─────────────────────────────────────────────
def load_all_results(training_results: dict = None) -> dict:
    """
    If training_results dict is provided, use it directly.
    Otherwise try to load models from disk.
    """
    if training_results is not None:
        return training_results

    results = {}
    for task in TASKS:
        results[task] = {"ml": {}, "dl": {}}
        # Load test data
        y_test_path = os.path.join(cfg.RESULTS_DIR, f"{task}_y_test.npy")
        X_test_path = os.path.join(cfg.RESULTS_DIR, f"{task}_X_test.npy")
        if not os.path.exists(y_test_path):
            continue
        y_test = np.load(y_test_path)
        X_test = np.load(X_test_path)

        # Load ML models
        for model_name in ML_MODELS:
            pkl = os.path.join(cfg.MODELS_DIR, f"{task}_{model_name}.pkl")
            if os.path.exists(pkl):
                model = joblib.load(pkl)
                y_pred = model.predict(X_test)
                metrics = compute_metrics(y_test, y_pred)
                results[task]["ml"][model_name] = {
                    "test_metrics": metrics,
                    "y_pred": y_pred,
                    "model": model,
                }

    return results


# ─────────────────────────────────────────────
#  OVERFITTING DETECTION
# ─────────────────────────────────────────────
def detect_overfitting(train_metrics: dict, test_metrics: dict, threshold: float = 0.15) -> str:
    """
    Compare train vs test R². If gap > threshold, flag as overfitting.
    Returns: 'Overfitting' | 'Underfitting' | 'Good Fit'
    """
    train_r2 = train_metrics.get("R2", 0)
    test_r2  = test_metrics.get("R2", 0)
    gap = train_r2 - test_r2

    if train_r2 < 0.5:
        return "Underfitting"
    elif gap > threshold:
        return f"Overfitting (gap={gap:.3f})"
    else:
        return "Good Fit"


# ─────────────────────────────────────────────
#  ROBUSTNESS TESTING
# ─────────────────────────────────────────────
def robustness_test(model, X_test: np.ndarray, y_test: np.ndarray,
                    noise_levels: list = [0.01, 0.05, 0.1]) -> dict:
    """
    Add Gaussian noise at multiple levels and measure R² degradation.
    """
    base_metrics = compute_metrics(y_test, model.predict(X_test))
    base_r2 = base_metrics["R2"]
    robust = {"base_R2": base_r2}

    for noise in noise_levels:
        X_noisy = X_test + np.random.normal(0, noise * X_test.std(), X_test.shape)
        try:
            y_pred_noisy = model.predict(X_noisy)
            noisy_metrics = compute_metrics(y_test, y_pred_noisy)
            robust[f"R2_noise_{int(noise*100)}pct"] = noisy_metrics["R2"]
        except Exception:
            robust[f"R2_noise_{int(noise*100)}pct"] = np.nan

    return robust


# ─────────────────────────────────────────────
#  SHAP EXPLAINABILITY
# ─────────────────────────────────────────────
def compute_shap(model, X_test: np.ndarray, feature_names: list,
                 task: str, model_name: str, max_samples: int = 200):
    """Generate SHAP values and save mean importance."""
    try:
        import shap
        from sklearn.pipeline import Pipeline
        print_step(f"  Computing SHAP for {model_name} [{task}]...")

        X_sample = X_test[:max_samples]

        # Unwrap pipeline: get inner estimator and transform X through preceding steps
        if isinstance(model, Pipeline):
            inner = model.steps[-1][1]
            # Transform X through all steps EXCEPT the final estimator
            X_transformed = X_sample.copy()
            for step_name, step_transform in model.steps[:-1]:
                X_transformed = step_transform.transform(X_transformed)
            X_for_shap = X_transformed
        else:
            inner = model
            X_for_shap = X_sample

        # Choose SHAP explainer
        if hasattr(inner, "feature_importances_"):
            explainer = shap.TreeExplainer(inner)
        elif hasattr(inner, "predict"):
            explainer = shap.KernelExplainer(
                inner.predict, shap.sample(X_for_shap, min(50, len(X_for_shap)))
            )
        else:
            logger.warning(f"    SHAP: no suitable explainer for {model_name}")
            return None

        shap_values = explainer.shap_values(X_for_shap)
        if isinstance(shap_values, list):
            shap_values = shap_values[0]

        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        shap_df = pd.DataFrame({
            "feature": feature_names[:len(mean_abs_shap)],
            "importance": mean_abs_shap
        }).sort_values("importance", ascending=False)

        shap_path = os.path.join(cfg.REPORTS_DIR, f"{task}_{model_name}_shap.csv")
        shap_df.to_csv(shap_path, index=False)
        logger.info(f"    SHAP saved: {shap_path}")
        return shap_df

    except Exception as e:
        logger.warning(f"    SHAP failed for {model_name}: {e}")
        return None


# ─────────────────────────────────────────────
#  COMPARISON TABLE BUILDER
# ─────────────────────────────────────────────
def build_comparison_table(training_results: dict) -> pd.DataFrame:
    """Build a flat comparison DataFrame from training results."""
    rows = []
    for task, task_data in training_results.items():
        for split in ["ml", "dl"]:
            model_dict = task_data.get(split, {})
            for model_name, result in model_dict.items():
                tm = result.get("test_metrics", {})
                trm = result.get("train_metrics", {})
                fit_status = detect_overfitting(trm, tm)

                row = {
                    "Task":         task,
                    "Model":        model_name,
                    "Type":         "ML" if split == "ml" else "DL",
                    "RMSE":         tm.get("RMSE", np.nan),
                    "MAE":          tm.get("MAE",  np.nan),
                    "R2":           tm.get("R2",   np.nan),
                    "MAPE%":        tm.get("MAPE", np.nan),
                    "Train_RMSE":   trm.get("RMSE", np.nan),
                    "Train_R2":     trm.get("R2",   np.nan),
                    "FitStatus":    fit_status,
                    "TrainTime_s":  result.get("train_time_s", np.nan),
                }
                rows.append(row)

    df = pd.DataFrame(rows)
    return df


# ─────────────────────────────────────────────
#  BEST MODEL ANALYSIS
# ─────────────────────────────────────────────
def select_overall_best(comparison_df: pd.DataFrame) -> pd.DataFrame:
    """Select best model per task based on R² (test)."""
    if comparison_df.empty:
        return pd.DataFrame()
    best_rows = []
    for task in comparison_df["Task"].unique():
        task_df = comparison_df[comparison_df["Task"] == task].copy()
        task_df = task_df.sort_values("R2", ascending=False)
        if len(task_df) > 0:
            best = task_df.iloc[0].copy()
            best["Rank"] = 1
            best_rows.append(best)
    return pd.DataFrame(best_rows)[["Task", "Model", "Type", "RMSE", "MAE", "R2", "MAPE%", "FitStatus"]]


# ─────────────────────────────────────────────
#  ERROR ANALYSIS
# ─────────────────────────────────────────────
def error_analysis(y_true: np.ndarray, y_pred: np.ndarray, task: str, model_name: str) -> dict:
    """Compute error distribution stats."""
    errors = y_true - y_pred
    abs_errors = np.abs(errors)
    return {
        "task":         task,
        "model":        model_name,
        "mean_error":   round(errors.mean(), 4),
        "std_error":    round(errors.std(), 4),
        "max_error":    round(abs_errors.max(), 4),
        "p95_error":    round(np.percentile(abs_errors, 95), 4),
        "pct_within_5pct": round(
            (abs_errors <= 0.05 * np.abs(y_true + 1e-6)).mean() * 100, 2
        ),
    }


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def run_evaluation(training_results: dict = None):
    print_header("STEP 5: MODEL EVALUATION & ANALYSIS")

    results = load_all_results(training_results)

    # ── Build comparison dataframe
    print_step("Building comparison table...")
    comp_df = build_comparison_table(results)

    if comp_df.empty:
        print_warning("No results to evaluate — run model training first!")
        return {}

    # ── Save comparison table
    comp_path = os.path.join(cfg.REPORTS_DIR, "model_comparison.csv")
    comp_df.to_csv(comp_path, index=False)
    logger.info(f"Comparison table saved: {comp_path}")

    # ── Print beautiful comparison table
    print("\n" + "═" * 100)
    print("  📊 MODEL PERFORMANCE COMPARISON")
    print("═" * 100)
    print(comp_df.to_string(index=False))

    # ── Best per task
    best_df = select_overall_best(comp_df)
    if not best_df.empty:
        print("\n" + "═" * 80)
        print("  🏆 BEST MODEL PER TASK")
        print("═" * 80)
        print(best_df.to_string(index=False))
        best_path = os.path.join(cfg.REPORTS_DIR, "best_models.csv")
        best_df.to_csv(best_path, index=False)

    # ── SHAP + Error analysis for best ML models
    error_rows = []
    for task, task_data in results.items():
        ml_models = task_data.get("ml", {})
        if not ml_models:
            continue

        # Load feature data for SHAP
        feat_path = cfg.PROCESSED_FILES.get(f"features_{task.lower()}", "")
        feature_names = []
        X_shap = None

        if feat_path and os.path.exists(feat_path):
            df_feat = load_csv(feat_path, logger)
            target_col = {"SOC": "soc", "SOH": "soh", "RUL": "rul_proxy", "Mileage": "mileage_per_charge"}.get(task)
            df_feat = df_feat.dropna(subset=[target_col]) if target_col and target_col in df_feat.columns else df_feat

            # Use the SAME exclusion logic as load_task_data() in 04_model_training.py
            # to ensure SHAP feature names exactly match training features
            from config import PROCESSED_FILES as _PF  # noqa: F401
            _GLOBAL_EXCL = [
                "vehicle_no", "chassis_no", "imei", "timestamp",
                "start_time", "end_time", "source_file", "gps", "start_gps", "end_gps",
                "_id", "oem_model", "oem", "model", "alert_type", "drive_mode",
                "vehicle_status", "city", "duration", "vehicle_no.1",
            ]
            _TASK_EXCL = {
                "SOC":     ["rolling_soc_5","rolling_soc_10","rolling_soc_20",
                            "rolling_soc_std_5","rolling_soc_std_10","charge_state_pct",
                            "voltage_deviation"],   # sync with 04_model_training.py
                "SOH":     ["soc","charge_state_pct","rolling_soc_5","rolling_soc_10",
                            "rolling_soc_20","rolling_soc_std_5","rolling_soc_std_10",
                            "soh_lag1","soh_change"],
                "RUL":     ["charge_cycle_count","cycle_usage_ratio",
                            "charge_frequency"],     # sync with 04_model_training.py
                "Mileage": ["soc_drain","soc_at_start","soc_at_end",
                            "distance_per_soc_drop","soc_drain_rate","energy_per_soc"],
            }
            exclude_set = set(_GLOBAL_EXCL + _TASK_EXCL.get(task, []) + [target_col or ""])
            feat_cols = [c for c in df_feat.select_dtypes(include=np.number).columns
                         if c not in exclude_set]
            df_feat = df_feat[feat_cols].fillna(0)
            X_shap = df_feat.values[:200]   # use 200 rows max for speed
            feature_names = feat_cols

        # SHAP for top 2 ML models by R²
        sorted_ml = sorted(ml_models.items(), key=lambda x: x[1]["test_metrics"].get("R2", -999), reverse=True)
        for rank, (mname, mres) in enumerate(sorted_ml[:2]):
            if X_shap is not None and hasattr(mres.get("model"), "predict"):
                compute_shap(mres["model"], X_shap, feature_names, task, mname)

            # Error analysis
            if "y_pred" in mres:
                y_t = mres.get("y_true", np.array([]))
                y_p = mres["y_pred"]
                if len(y_t) == 0:
                    y_t_path = os.path.join(cfg.RESULTS_DIR, f"{task}_y_test.npy")
                    if os.path.exists(y_t_path):
                        y_t = np.load(y_t_path)
                if len(y_t) == len(y_p):
                    err = error_analysis(y_t, y_p, task, mname)
                    error_rows.append(err)

    # ── Save error analysis
    if error_rows:
        err_df = pd.DataFrame(error_rows)
        err_path = os.path.join(cfg.REPORTS_DIR, "error_analysis.csv")
        err_df.to_csv(err_path, index=False)
        logger.info(f"Error analysis saved: {err_path}")

    # ── Robustness summary
    print_step("Robustness testing...")
    robust_rows = []
    for task, task_data in results.items():
        ml_models = task_data.get("ml", {})
        X_test_path = os.path.join(cfg.RESULTS_DIR, f"{task}_X_test.npy")
        y_test_path = os.path.join(cfg.RESULTS_DIR, f"{task}_y_test.npy")

        if not os.path.exists(X_test_path):
            continue

        X_test = np.load(X_test_path)
        y_test = np.load(y_test_path)

        sorted_ml = sorted(ml_models.items(), key=lambda x: x[1]["test_metrics"].get("R2", -999), reverse=True)
        for mname, mres in sorted_ml[:1]:
            model = mres.get("model")
            if model is not None:
                rob = robustness_test(model, X_test, y_test)
                rob["task"]  = task
                rob["model"] = mname
                robust_rows.append(rob)

    if robust_rows:
        rob_df = pd.DataFrame(robust_rows)
        rob_path = os.path.join(cfg.REPORTS_DIR, "robustness_analysis.csv")
        rob_df.to_csv(rob_path, index=False)
        logger.info(f"Robustness analysis saved: {rob_path}")

    print_success("Evaluation complete!")
    return {
        "comparison": comp_df,
        "best":       best_df if not comp_df.empty else pd.DataFrame(),
    }


if __name__ == "__main__":
    run_evaluation()
