"""
04_model_training.py — Train all ML and DL models for SOC, SOH, RUL, Mileage prediction.

ML Models:  RandomForest, GradientBoosting, XGBoost, ExtraTrees, SVR,
            DecisionTree, KNN, Ridge, Lasso
DL Models:  ANN, LSTM, GRU, CNN-1D, CNN-LSTM Hybrid
"""

import os
import sys
import time
import warnings
import numpy as np
import pandas as pd
import joblib

warnings.filterwarnings("ignore")

# sklearn
from sklearn.ensemble import (
    RandomForestRegressor, GradientBoostingRegressor,
    ExtraTreesRegressor
)
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import (
    train_test_split, RandomizedSearchCV, TimeSeriesSplit
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

# XGBoost
import xgboost as xgb

# TensorFlow / Keras
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import (
    Dense, Dropout, LSTM, GRU, Conv1D, MaxPooling1D,
    Flatten, BatchNormalization, Input, Reshape
)
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
)
from tensorflow.keras.optimizers import Adam

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as cfg
from utils import (
    get_logger, print_header, print_step, print_success, print_warning,
    compute_metrics, load_csv, save_csv
)

logger = get_logger("04_model_training", cfg.LOGS_DIR)

# Silence TF logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
tf.get_logger().setLevel("ERROR")


# ─────────────────────────────────────────────
#  DATA LOADING & SPLITTING
# ─────────────────────────────────────────────
TASK_CONFIG = {
    "SOC":     {"file": "features_soc",     "target": "soc"},
    "SOH":     {"file": "features_soh",     "target": "soh"},
    "RUL":     {"file": "features_rul",     "target": "rul_proxy"},
    "Mileage": {"file": "features_mileage", "target": "mileage_per_charge"},
}

EXCLUDE_COLS_ALWAYS = [
    "vehicle_no", "chassis_no", "imei", "timestamp",
    "start_time", "end_time", "source_file", "gps", "start_gps", "end_gps",
    "_id", "oem_model", "oem", "model", "alert_type", "drive_mode",
    "vehicle_status", "city", "duration", "vehicle_no.1",
]

# Per-task columns that must NEVER be used as features (data leakage)
EXCLUDE_COLS_PER_TASK = {
    "SOC": [
        # Rolling SOC windows directly encode the target
        "rolling_soc_5", "rolling_soc_10", "rolling_soc_20",
        "rolling_soc_std_5", "rolling_soc_std_10",
        "charge_state_pct",   # may be same as soc
    ],
    "SOH": [
        # Current SOC is not a causal driver of long-term degradation
        "soc", "charge_state_pct",
        "rolling_soc_5", "rolling_soc_10", "rolling_soc_20",
        "rolling_soc_std_5", "rolling_soc_std_10",
        "soh_lag1", "soh_change",   # encode the target
    ],
    "RUL": [
        # rul_proxy = NOMINAL - charge_cycle_count  =>  r = -1.0
        "charge_cycle_count",
        "cycle_usage_ratio",   # = charge_cycle_count/NOMINAL, equally leaky
    ],
    "Mileage": [
        # All of these algebraically define mileage_per_charge
        "soc_drain",             # mileage = run_kms * (100/soc_drain)
        "soc_at_start", "soc_at_end",   # difference = soc_drain
        "distance_per_soc_drop",  # = run_kms/soc_drain = target/100
        "soc_drain_rate",         # = soc_drain/run_kms  (inverse)
        "energy_per_soc",         # = energy/soc_drain   (correlated)
    ],
}


def load_task_data(task: str):
    """Load and prepare (X, y) for a given task."""
    conf = TASK_CONFIG[task]
    path = cfg.PROCESSED_FILES[conf["file"]]
    target = conf["target"]

    if not os.path.exists(path):
        logger.warning(f"  Feature file not found for {task}: {path}")
        return None, None, None, None

    df = load_csv(path, logger)
    df = df.dropna(subset=[target])
    df = df.replace([np.inf, -np.inf], np.nan)

    # Build full exclusion list: global + per-task leaky columns + target
    task_exclude = EXCLUDE_COLS_PER_TASK.get(task, [])
    all_exclude  = set(EXCLUDE_COLS_ALWAYS + task_exclude + [target])
    drop_cols    = [c for c in df.columns if c in all_exclude]

    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    X = X.select_dtypes(include=np.number)
    # Robust NaN fill: use median per column, fallback to 0
    col_medians = X.median().fillna(0)
    X = X.fillna(col_medians).fillna(0)
    y = df[target].values

    if len(X) < 50:
        logger.warning(f"  {task}: insufficient data ({len(X)} rows)")
        return None, None, None, None

    logger.info(f"  {task}: {len(X):,} rows | Features ({X.shape[1]}): {list(X.columns)}")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=cfg.TRAIN_CONFIG["test_size"],
        random_state=cfg.TRAIN_CONFIG["random_state"]
    )
    logger.info(f"  {task}: X_train={X_train.shape}, X_test={X_test.shape}")
    return X_train, X_test, y_train, y_test


# ─────────────────────────────────────────────
#  ML MODEL DEFINITIONS
# ─────────────────────────────────────────────
def _wrap_imputer(estimator):
    """Wrap any sklearn estimator with a median imputer to handle NaNs."""
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model",   estimator),
    ])


def get_ml_models():
    return {
        "RandomForest": _wrap_imputer(RandomForestRegressor(
            n_estimators=200, random_state=cfg.TRAIN_CONFIG["random_state"],
            n_jobs=-1
        )),
        "GradientBoosting": _wrap_imputer(GradientBoostingRegressor(
            n_estimators=200, learning_rate=0.1, max_depth=5,
            random_state=cfg.TRAIN_CONFIG["random_state"]
        )),
        "XGBoost": _wrap_imputer(xgb.XGBRegressor(
            n_estimators=200, learning_rate=0.1, max_depth=5,
            subsample=0.8, n_jobs=-1,
            random_state=cfg.TRAIN_CONFIG["random_state"],
            verbosity=0
        )),
        "ExtraTrees": _wrap_imputer(ExtraTreesRegressor(
            n_estimators=200, random_state=cfg.TRAIN_CONFIG["random_state"],
            n_jobs=-1
        )),
        "SVR": _wrap_imputer(SVR(kernel="rbf", C=10, epsilon=0.1)),
        "DecisionTree": _wrap_imputer(DecisionTreeRegressor(
            max_depth=10, random_state=cfg.TRAIN_CONFIG["random_state"]
        )),
        "KNN": _wrap_imputer(KNeighborsRegressor(n_neighbors=7, n_jobs=-1)),
        "Ridge": _wrap_imputer(Ridge(alpha=1.0)),
        "Lasso": _wrap_imputer(Lasso(alpha=0.01, max_iter=5000)),
    }


def tune_model(model, param_grid: dict, X_train, y_train, task: str, model_name: str):
    """RandomizedSearchCV tuning."""
    print_step(f"  Tuning {model_name}...")
    cv = TimeSeriesSplit(n_splits=3) if len(X_train) > 500 else 3
    rs = RandomizedSearchCV(
        model, param_grid,
        n_iter=cfg.TRAIN_CONFIG["n_random_search_iter"],
        cv=cv, scoring="neg_root_mean_squared_error",
        random_state=cfg.TRAIN_CONFIG["random_state"],
        n_jobs=-1, verbose=0
    )
    rs.fit(X_train, y_train)
    logger.info(f"    Best params: {rs.best_params_}")
    return rs.best_estimator_


def train_ml_models(X_train, X_test, y_train, y_test, task: str) -> dict:
    """Train all ML models for a given task."""
    results = {}
    models  = get_ml_models()

    # Skip SVR for large datasets (slow)
    if len(X_train) > 50_000:
        models.pop("SVR", None)
        logger.info(f"  {task}: Skipping SVR (dataset too large)")

    for name, model in models.items():
        print_step(f"  Training {name} [{task}]...")
        t0 = time.time()
        model.fit(X_train, y_train)
        t_fit = time.time() - t0

        y_pred_train = model.predict(X_train)
        y_pred_test  = model.predict(X_test)

        train_metrics = compute_metrics(y_train, y_pred_train)
        test_metrics  = compute_metrics(y_test,  y_pred_test)

        results[name] = {
            "model":         model,
            "train_metrics": train_metrics,
            "test_metrics":  test_metrics,
            "train_time_s":  round(t_fit, 2),
            "y_pred":        y_pred_test,
            "y_true":        y_test,         # needed by error analysis in 05_evaluation.py
            "y_pred_train":  y_pred_train,   # needed by train vs test line chart
            "y_train":       y_train,        # needed by train vs test line chart
        }
        logger.info(
            f"    {name}: RMSE={test_metrics['RMSE']:.4f} "
            f"R²={test_metrics['R2']:.4f} time={t_fit:.1f}s"
        )

        # Save model
        model_path = os.path.join(cfg.MODELS_DIR, f"{task}_{name}.pkl")
        joblib.dump(model, model_path)

    return results


# ─────────────────────────────────────────────
#  DL MODEL DEFINITIONS
# ─────────────────────────────────────────────
def build_ann(input_dim: int) -> Sequential:
    model = Sequential([
        Dense(256, activation="relu", input_shape=(input_dim,)),
        BatchNormalization(),
        Dropout(cfg.DL_CONFIG["dropout_rate"]),
        Dense(128, activation="relu"),
        BatchNormalization(),
        Dropout(cfg.DL_CONFIG["dropout_rate"]),
        Dense(64, activation="relu"),
        Dense(1)
    ])
    model.compile(
        optimizer=Adam(cfg.DL_CONFIG["learning_rate"]),
        loss="mse", metrics=["mae"]
    )
    return model


def build_lstm(seq_len: int, n_features: int) -> Sequential:
    model = Sequential([
        LSTM(cfg.DL_CONFIG["lstm_units"][0], return_sequences=True,
             input_shape=(seq_len, n_features)),
        Dropout(cfg.DL_CONFIG["dropout_rate"]),
        LSTM(cfg.DL_CONFIG["lstm_units"][1]),
        Dropout(cfg.DL_CONFIG["dropout_rate"]),
        Dense(32, activation="relu"),
        Dense(1)
    ])
    model.compile(
        optimizer=Adam(cfg.DL_CONFIG["learning_rate"]),
        loss="mse", metrics=["mae"]
    )
    return model


def build_gru(seq_len: int, n_features: int) -> Sequential:
    model = Sequential([
        GRU(cfg.DL_CONFIG["gru_units"][0], return_sequences=True,
            input_shape=(seq_len, n_features)),
        Dropout(cfg.DL_CONFIG["dropout_rate"]),
        GRU(cfg.DL_CONFIG["gru_units"][1]),
        Dropout(cfg.DL_CONFIG["dropout_rate"]),
        Dense(32, activation="relu"),
        Dense(1)
    ])
    model.compile(
        optimizer=Adam(cfg.DL_CONFIG["learning_rate"]),
        loss="mse", metrics=["mae"]
    )
    return model


def build_cnn(seq_len: int, n_features: int) -> Sequential:
    model = Sequential([
        Conv1D(filters=64, kernel_size=3, activation="relu",
               input_shape=(seq_len, n_features), padding="same"),
        BatchNormalization(),
        Conv1D(filters=32, kernel_size=3, activation="relu", padding="same"),
        MaxPooling1D(pool_size=2),
        Dropout(cfg.DL_CONFIG["dropout_rate"]),
        Flatten(),
        Dense(64, activation="relu"),
        Dense(1)
    ])
    model.compile(
        optimizer=Adam(cfg.DL_CONFIG["learning_rate"]),
        loss="mse", metrics=["mae"]
    )
    return model


def build_cnn_lstm(seq_len: int, n_features: int) -> Sequential:
    model = Sequential([
        Conv1D(filters=64, kernel_size=3, activation="relu",
               input_shape=(seq_len, n_features), padding="same"),
        BatchNormalization(),
        MaxPooling1D(pool_size=2, padding="same"),
        LSTM(64, return_sequences=False),
        Dropout(cfg.DL_CONFIG["dropout_rate"]),
        Dense(32, activation="relu"),
        Dense(1)
    ])
    model.compile(
        optimizer=Adam(cfg.DL_CONFIG["learning_rate"]),
        loss="mse", metrics=["mae"]
    )
    return model


CALLBACKS = [
    EarlyStopping(monitor="val_loss", patience=cfg.DL_CONFIG["patience"],
                  restore_best_weights=True, verbose=0),
    ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=7, verbose=0),
]


def make_sequences(X: np.ndarray, y: np.ndarray, seq_len: int):
    """Create sliding-window sequences for LSTM/GRU/CNN."""
    Xs, ys = [], []
    for i in range(len(X) - seq_len):
        Xs.append(X[i:i + seq_len])
        ys.append(y[i + seq_len])
    return np.array(Xs), np.array(ys)


def train_dl_models(X_train, X_test, y_train, y_test, task: str) -> dict:
    """Train all DL models for a given task."""
    results = {}
    seq_len = cfg.DL_CONFIG["sequence_length"]
    n_feat  = X_train.shape[1]

    # ── ANN (tabular, no sequence)
    for name, build_fn, use_seq in [
        ("ANN",       lambda: build_ann(n_feat),                  False),
        ("LSTM",      lambda: build_lstm(seq_len, n_feat),        True),
        ("GRU",       lambda: build_gru(seq_len, n_feat),         True),
        ("CNN",       lambda: build_cnn(seq_len, n_feat),         True),
        ("CNN_LSTM",  lambda: build_cnn_lstm(seq_len, n_feat),    True),
    ]:
        print_step(f"  Training {name} [{task}]...")
        t0 = time.time()

        if use_seq:
            Xtr_s, ytr_s = make_sequences(X_train.values if hasattr(X_train, "values") else X_train, y_train, seq_len)
            Xts_s, yts_s = make_sequences(X_test.values if hasattr(X_test, "values") else X_test, y_test, seq_len)
            if len(Xtr_s) < 20:
                logger.warning(f"    {name}: too few sequences, skipping")
                continue
            X_tr_in, y_tr_in = Xtr_s, ytr_s
            X_ts_in, y_ts_in = Xts_s, yts_s
        else:
            X_tr_in = X_train.values if hasattr(X_train, "values") else X_train
            y_tr_in = y_train
            X_ts_in = X_test.values if hasattr(X_test, "values") else X_test
            y_ts_in = y_test

        model = build_fn()

        # Model checkpoint
        ckpt_path = os.path.join(cfg.MODELS_DIR, f"{task}_{name}_best.keras")
        callbacks = CALLBACKS + [
            ModelCheckpoint(ckpt_path, save_best_only=True, verbose=0)
        ]

        history = model.fit(
            X_tr_in, y_tr_in,
            validation_split=cfg.DL_CONFIG["validation_split"],
            epochs=cfg.DL_CONFIG["epochs"],
            batch_size=cfg.DL_CONFIG["batch_size"],
            callbacks=callbacks,
            verbose=0
        )

        t_fit = time.time() - t0
        y_pred_train = model.predict(X_tr_in, verbose=0).ravel()
        y_pred_test  = model.predict(X_ts_in, verbose=0).ravel()

        train_metrics = compute_metrics(y_tr_in, y_pred_train)
        test_metrics  = compute_metrics(y_ts_in, y_pred_test)

        results[name] = {
            "model":         model,
            "train_metrics": train_metrics,
            "test_metrics":  test_metrics,
            "train_time_s":  round(t_fit, 2),
            "y_pred":        y_pred_test,
            "y_true":        y_ts_in,
            "y_pred_train":  y_pred_train,   # needed by train vs test line chart
            "y_train":       y_tr_in,        # needed by train vs test line chart
            "history":       history.history,
        }
        logger.info(
            f"    {name}: RMSE={test_metrics['RMSE']:.4f} "
            f"R²={test_metrics['R2']:.4f} time={t_fit:.1f}s"
        )

    return results


# ─────────────────────────────────────────────
#  BEST MODEL SELECTION
# ─────────────────────────────────────────────
def select_best_model(ml_results: dict, dl_results: dict) -> tuple:
    """Select best model by R² on test set."""
    all_results = {**ml_results, **dl_results}
    if not all_results:
        logger.warning("  select_best_model: no results to compare, returning None")
        return "None", {}
    best_name = max(all_results, key=lambda k: all_results[k]["test_metrics"].get("R2", -999))
    best = all_results[best_name]
    return best_name, best


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def run_training(feature_dict: dict = None):
    print_header("STEP 4: MODEL TRAINING")

    all_results = {}

    for task in TASK_CONFIG.keys():
        print(f"\n{'─'*60}")
        print(f"  Training models for: {task}")
        print(f"{'─'*60}")

        # Load data
        X_train, X_test, y_train, y_test = load_task_data(task)
        if X_train is None:
            print_warning(f"Skipping {task}: no data available")
            continue

        # Save test data for evaluation
        np.save(os.path.join(cfg.RESULTS_DIR, f"{task}_y_test.npy"), y_test)
        np.save(os.path.join(cfg.RESULTS_DIR, f"{task}_X_test.npy"), X_test if not hasattr(X_test, 'values') else X_test.values)

        # Train ML models
        ml_results = train_ml_models(X_train, X_test, y_train, y_test, task)

        # Train DL models
        dl_results = train_dl_models(X_train, X_test, y_train, y_test, task)

        # Select best
        best_name, best = select_best_model(ml_results, dl_results)
        print_success(f"Best model for {task}: {best_name} "
                      f"(R²={best['test_metrics']['R2']:.4f}, "
                      f"RMSE={best['test_metrics']['RMSE']:.4f})")

        # Save best model info
        best_info_path = os.path.join(cfg.MODELS_DIR, f"{task}_best_model.txt")
        with open(best_info_path, "w") as f:
            f.write(f"Best Model: {best_name}\n")
            f.write(f"Test Metrics: {best['test_metrics']}\n")
            f.write(f"Train Time: {best['train_time_s']}s\n")

        all_results[task] = {
            "ml": ml_results,
            "dl": dl_results,
            "best_name": best_name,
            "best": best,
        }

    print_success("All model training complete!")
    return all_results


if __name__ == "__main__":
    run_training()
