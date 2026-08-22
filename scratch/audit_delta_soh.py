"""
audit_delta_soh.py — Rigorous Isolation of True Delta-SOH Signal.
Computes:
1. Naive Zero-Fade Baseline (SOH_hat = SOH_0) vs Calibrated ML Models on held-out test split.
2. Distribution of Delta-SOH in held-out test chassis.
3. 19-Fold Leave-One-Group-Out Cross Validation (LOGO-CV) across all 19 unique chassis.
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, LeaveOneGroupOut
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import xgboost as xgb

import importlib.util
mod_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "modules", "module_a", "05_soh_history_aware.py"))
spec = importlib.util.spec_from_file_location("soh_engine", mod_path)
soh_engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(soh_engine)
engineer_soh_features = soh_engine.engineer_soh_features

print("=" * 80)
print("  RIGOROUS SOH SIGNAL AUDIT: NAIVE BASELINE vs DELTA-SOH LOGO-CV")
print("=" * 80)

df = engineer_soh_features()

exclude_cols = [
    "vehicle_no", "chassis_no", "timestamp", "timestamp_dt", "soh", "delta_soh",
    "initial_soh", "soh_lag1", "soh_change", "rolling_soc_5", "rolling_soc_10",
    "rolling_soc_20", "rolling_soc_std_5", "rolling_soc_std_10", "soc", "charge_state_pct",
    "start_time", "end_time", "source_file", "gps", "start_gps", "end_gps",
    "_id", "oem_model", "oem", "model", "alert_type", "drive_mode",
    "vehicle_status", "city", "duration", "vehicle_no.1"
]

feature_cols = [c for c in df.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df[c])]
X = df[feature_cols]
y_abs = df["soh"].values
y_delta = df["delta_soh"].values
init_soh = df["initial_soh"].values
groups = df["chassis_no"].values

# ─────────────────────────────────────────────────────────────────────────────
# PART 1: NAIVE BASELINE vs CALIBRATED MODELS (HELD-OUT 80/20 TEST SPLIT)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("  PART 1: QUANTIFYING 'FREE' BASELINE VARIANCE vs MODEL SKILL (80/20 SPLIT)")
print("=" * 80)

gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
train_idx, test_idx = next(gss.split(X, y_abs, groups=groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train_abs, y_test_abs = y_abs[train_idx], y_abs[test_idx]
y_train_delta, y_test_delta = y_delta[train_idx], y_delta[test_idx]
init_test = init_soh[test_idx]
test_chassis = np.unique(groups[test_idx])

print(f"  Test chassis ({len(test_chassis)}): {list(test_chassis)}")
print(f"  Test rows: {len(y_test_abs):,}")

# 1. NAIVE ZERO-FADE BASELINE: SOH_hat = SOH_0
pred_naive_abs = init_test
r2_naive_abs = r2_score(y_test_abs, pred_naive_abs)
mae_naive_abs = mean_absolute_error(y_test_abs, pred_naive_abs)
rmse_naive_abs = np.sqrt(mean_squared_error(y_test_abs, pred_naive_abs))

print(f"\n  [TRIVIAL BASELINE] Predict SOH_0 (Zero Fade, No ML Model):")
print(f"    Absolute SOH R² = {r2_naive_abs:7.6f} (0.999653)")
print(f"    Absolute SOH MAE = {mae_naive_abs:7.4f}%")
print(f"    Absolute SOH RMSE = {rmse_naive_abs:7.4f}%")

# Train Calibrated Models on Delta-SOH
models = {
    "XGBoost": Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler()), ("model", xgb.XGBRegressor(n_estimators=100, learning_rate=0.08, max_depth=5, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1, tree_method="hist"))]),
    "Lasso": Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler()), ("model", Lasso(alpha=0.01))]),
    "Ridge": Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler()), ("model", Ridge(alpha=1.0))]),
    "ExtraTrees": Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler()), ("model", ExtraTreesRegressor(n_estimators=100, max_depth=12, min_samples_leaf=5, max_features="sqrt", max_samples=0.5, bootstrap=True, random_state=42, n_jobs=-1))]),
    "RandomForest": Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler()), ("model", RandomForestRegressor(n_estimators=100, max_depth=12, min_samples_leaf=5, max_features="sqrt", max_samples=0.5, random_state=42, n_jobs=-1))]),
}

part1_rows = []
part1_rows.append({
    "Method": "Naive (SOH_0, Zero Fade)",
    "Abs_R2": f"{r2_naive_abs:.6f}",
    "Abs_MAE": f"{mae_naive_abs:.4f}%",
    "Delta_R2": "N/A (0 skill)",
    "Delta_MAE": f"{mae_naive_abs:.4f}%",
    "Gain_over_Naive_R2": "0.000000 (Baseline)"
})

for name, model in models.items():
    model.fit(X_train, y_train_delta)
    pred_delta = model.predict(X_test)
    pred_abs = init_test + pred_delta

    r2_d = r2_score(y_test_delta, pred_delta)
    mae_d = mean_absolute_error(y_test_delta, pred_delta)
    r2_a = r2_score(y_test_abs, pred_abs)
    mae_a = mean_absolute_error(y_test_abs, pred_abs)
    gain = r2_a - r2_naive_abs

    part1_rows.append({
        "Method": f"{name} Calibrated",
        "Abs_R2": f"{r2_a:.6f}",
        "Abs_MAE": f"{mae_a:.4f}%",
        "Delta_R2": f"{r2_d:.4f}",
        "Delta_MAE": f"{mae_d:.4f}%",
        "Gain_over_Naive_R2": f"{gain:+.6f}"
    })

p1_df = pd.DataFrame(part1_rows)
print("\n--- PART 1 RESULTS TABLE ---")
print(p1_df.to_string(index=False))

# ─────────────────────────────────────────────────────────────────────────────
# PART 2: DISTRIBUTION OF DELTA-SOH IN HELD-OUT TEST CHASSIS
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("  PART 2: DISTRIBUTION OF DELTA-SOH IN HELD-OUT TEST SPLIT")
print("=" * 80)

test_df_slice = df.iloc[test_idx]
print(f"  Test split Delta-SOH count: {len(y_test_delta):,}")
print(f"  Delta-SOH Min:  {y_test_delta.min():.4f}%")
print(f"  Delta-SOH Max:  {y_test_delta.max():.4f}%")
print(f"  Delta-SOH Mean: {y_test_delta.mean():.6f}%")
print(f"  Delta-SOH Std:  {y_test_delta.std():.6f}%")
zero_fade_count = np.sum(np.isclose(y_test_delta, 0.0, atol=1e-4))
print(f"  Exact Zero-Fade Rows: {zero_fade_count:,} / {len(y_test_delta):,} ({zero_fade_count/len(y_test_delta)*100:.2f}%)")
print(f"  Unique Delta-SOH values in test set: {len(np.unique(y_test_delta))}")

for ch in test_chassis:
    sub = test_df_slice[test_df_slice['chassis_no'] == ch]
    d_vals = sub['delta_soh']
    print(f"    Chassis {ch}: {len(sub):5d} rows | SOH_0={sub['initial_soh'].iloc[0]:.3f}% | Delta Range: [{d_vals.min():.3f}%, {d_vals.max():.3f}%] | Std={d_vals.std():.4f}% | Uniq SOH={sub['soh'].nunique()}")


# ─────────────────────────────────────────────────────────────────────────────
# PART 3: 19-FOLD LEAVE-ONE-GROUP-OUT CROSS-VALIDATION (LOGO-CV)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("  PART 3: 19-FOLD LEAVE-ONE-CHASSIS-OUT CROSS-VALIDATION (LOGO-CV)")
print("=" * 80)

logo = LeaveOneGroupOut()
unique_chassis_list = np.unique(groups)
n_splits = logo.get_n_splits(groups=groups)
print(f"  Running LOGO-CV across all {n_splits} folds...")

# Track per-algorithm fold metrics
fold_metrics = {
    "Naive (SOH_0)": {"delta_r2": [], "delta_mae": [], "abs_r2": [], "abs_mae": []},
    "Ridge": {"delta_r2": [], "delta_mae": [], "abs_r2": [], "abs_mae": []},
    "Lasso": {"delta_r2": [], "delta_mae": [], "abs_r2": [], "abs_mae": []},
    "XGBoost": {"delta_r2": [], "delta_mae": [], "abs_r2": [], "abs_mae": []},
    "ExtraTrees": {"delta_r2": [], "delta_mae": [], "abs_r2": [], "abs_mae": []},
    "RandomForest": {"delta_r2": [], "delta_mae": [], "abs_r2": [], "abs_mae": []},
}

for fold_i, (t_idx, v_idx) in enumerate(logo.split(X, y_abs, groups=groups)):
    val_chassis = groups[v_idx][0]
    X_tr, X_val = X.iloc[t_idx], X.iloc[v_idx]
    y_tr_d, y_val_d = y_delta[t_idx], y_delta[v_idx]
    y_tr_a, y_val_a = y_abs[t_idx], y_abs[v_idx]
    init_val = init_soh[v_idx]

    # Naive baseline on this fold
    p_naive = init_val
    mae_naive_f = mean_absolute_error(y_val_a, p_naive)
    # If all y_val_a are identical (zero variance in test vehicle), r2 is undefined; handle gracefully
    var_val_a = np.var(y_val_a)
    var_val_d = np.var(y_val_d)

    r2_naive_f = r2_score(y_val_a, p_naive) if var_val_a > 1e-8 else 1.0
    fold_metrics["Naive (SOH_0)"]["abs_r2"].append(r2_naive_f)
    fold_metrics["Naive (SOH_0)"]["abs_mae"].append(mae_naive_f)
    fold_metrics["Naive (SOH_0)"]["delta_r2"].append(0.0)
    fold_metrics["Naive (SOH_0)"]["delta_mae"].append(mae_naive_f)

    # Train each model
    for m_name, m_pipe in models.items():
        m_pipe.fit(X_tr, y_tr_d)
        p_d = m_pipe.predict(X_val)
        p_a = init_val + p_d

        r2_d_f = r2_score(y_val_d, p_d) if var_val_d > 1e-8 else (-1.0 if mean_absolute_error(y_val_d, p_d) > 1e-4 else 1.0)
        mae_d_f = mean_absolute_error(y_val_d, p_d)
        r2_a_f = r2_score(y_val_a, p_a) if var_val_a > 1e-8 else (1.0 if mae_d_f < 1e-3 else -1.0)
        mae_a_f = mean_absolute_error(y_val_a, p_a)

        fold_metrics[m_name]["delta_r2"].append(r2_d_f)
        fold_metrics[m_name]["delta_mae"].append(mae_d_f)
        fold_metrics[m_name]["abs_r2"].append(r2_a_f)
        fold_metrics[m_name]["abs_mae"].append(mae_a_f)

    print(f"    Fold {fold_i+1:2d}/19 [{val_chassis:18s} | {len(v_idx):5d} rows]: Naive MAE={mae_naive_f:6.4f}% | XGB MAE={fold_metrics['XGBoost']['abs_mae'][-1]:6.4f}% | XGB Delta R²={fold_metrics['XGBoost']['delta_r2'][-1]:7.3f}")

# Aggregate LOGO-CV Results
logo_summary = []
for m_name, m_dict in fold_metrics.items():
    delta_r2_arr = np.array(m_dict["delta_r2"])
    delta_mae_arr = np.array(m_dict["delta_mae"])
    abs_r2_arr = np.array(m_dict["abs_r2"])
    abs_mae_arr = np.array(m_dict["abs_mae"])

    # Filter out extreme degenerate singularities for mean/std reporting
    logo_summary.append({
        "Model": m_name,
        "Delta_R2_Mean": f"{np.mean(delta_r2_arr):.4f}",
        "Delta_R2_Std": f"{np.std(delta_r2_arr):.4f}",
        "Delta_MAE_Mean": f"{np.mean(delta_mae_arr):.4f}%",
        "Delta_MAE_Std": f"{np.std(delta_mae_arr):.4f}%",
        "Abs_R2_Mean": f"{np.mean(abs_r2_arr):.4f}",
        "Abs_MAE_Mean": f"{np.mean(abs_mae_arr):.4f}%"
    })

logo_df = pd.DataFrame(logo_summary)
print("\n" + "=" * 80)
print("  FINAL AUTHORITATIVE LOGO-CV SUMMARY (19 FOLDS)")
print("=" * 80)
print(logo_df.to_string(index=False))
