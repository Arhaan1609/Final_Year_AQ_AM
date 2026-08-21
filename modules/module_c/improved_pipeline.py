"""
improved_pipeline.py
====================
Complete fixed pipeline for RUL-to-knee prediction.
Run this instead of train_evaluate.py + train_dl.py + ensemble.py.

Fixes applied:
    1. No data leakage (scaler fitted on train only)
    2. Target (RUL_to_knee) is never scaled
    3. Log-transform on target to remove underprediction bias
    4. Proper sequence length (30) with correctly scaled sequences
    5. Upgraded BiLSTM architecture with Huber loss and BatchNorm
    6. ReduceLROnPlateau + longer patience early stopping
    7. Stacking ensemble (Ridge meta-learner over OOF predictions)
    8. Residual corrector to remove remaining systematic bias
"""

import pandas as pd
import numpy as np
import os
import warnings
import joblib
warnings.filterwarnings('ignore')

import xgboost as xgb
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    LSTM, GRU, Dense, Dropout, BatchNormalization,
    Bidirectional, Input, Conv1D, Concatenate
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# ---------------------------------------------
# CONFIG
# ---------------------------------------------
DATA_DIR       = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
FEATURE_PATH   = os.path.join(DATA_DIR, "labeled_features.csv")
SEQUENCE_LEN   = 30       # was buggy 5 or insufficient 20
RANDOM_SEED    = 42
LOG_TARGET     = True     # set False to disable log-transform
EPOCHS         = 200
BATCH_SIZE     = 64


# ---------------------------------------------
# SECTION 1: DATA PREPARATION
# ---------------------------------------------

EXCLUDE_COLS = [
    'chassis_no', 'date', 'timestamp', 'vehicle_no', 'city', 'oem', 'model',
    'source_file', 'cmcdts', 'start_gps', 'end_gps', 'createdAt', 'updatedAt',
    'rts', 'gdts', 'grts', 'vehicle_status', 'drive_mode', 'charge_inlet_mode', 'vmdl',
    'is_post_knee', 'knee_cycle',
    'RUL_to_knee'      # <- CRITICAL: exclude target from feature scaling
]


def prepare_tabular_data(df):
    """
    Chassis-level train/test split with correctly ordered scaling.
    Returns unscaled X (for stacking), scaled X, raw y, and feature names.
    """
    df_pre = df[df['is_post_knee'] == 0].copy()

    unique_chassis = df_pre['chassis_no'].unique().tolist()
    rng = np.random.default_rng(RANDOM_SEED)
    rng.shuffle(unique_chassis)

    split_idx    = int(len(unique_chassis) * 0.8)
    train_chassis = unique_chassis[:split_idx]
    test_chassis  = unique_chassis[split_idx:]

    train_df = df_pre[df_pre['chassis_no'].isin(train_chassis)]
    test_df  = df_pre[df_pre['chassis_no'].isin(test_chassis)]

    features = [c for c in train_df.columns if c not in EXCLUDE_COLS]

    X_train_raw = train_df[features].fillna(0).select_dtypes(include=[np.number])
    X_test_raw  = test_df[features].fillna(0).select_dtypes(include=[np.number])
    X_train_raw, X_test_raw = X_train_raw.align(X_test_raw, join='left', axis=1, fill_value=0)

    # Raw targets — never scaled
    y_train_raw = train_df['RUL_to_knee'].values.astype(np.float64)
    y_test_raw  = test_df['RUL_to_knee'].values.astype(np.float64)

    # Scale X on train statistics only
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_raw)
    X_test_scaled  = scaler.transform(X_test_raw)   # NO fit on test!

    joblib.dump(scaler, os.path.join(DATA_DIR, 'feature_scaler.pkl'))

    # Optional log-transform of target
    if LOG_TARGET:
        y_train = np.log1p(np.clip(y_train_raw, 0, None))
        y_test  = np.log1p(np.clip(y_test_raw,  0, None))
    else:
        y_train = y_train_raw
        y_test  = y_test_raw

    print(f"Tabular split -> Train: {len(X_train_raw)}, Test: {len(X_test_raw)}, "
          f"Features: {X_train_raw.shape[1]}")
    print(f"Target (raw)  -> Train: [{y_train_raw.min():.1f}, {y_train_raw.max():.1f}], "
          f"Test: [{y_test_raw.min():.1f}, {y_test_raw.max():.1f}]")

    return (X_train_scaled, X_test_scaled, y_train, y_test,
            y_train_raw, y_test_raw,
            X_train_raw.columns.tolist(), train_df, test_df)


def create_sequences(train_df, test_df, features, sequence_length=SEQUENCE_LEN):
    """
    Build sliding-window sequences with correct train-only scaling.
    Targets are log-transformed if LOG_TARGET=True.
    """
    def _build(df, scaler, fit):
        feat_matrix = df[features].fillna(0).values
        if fit:
            feat_matrix = scaler.fit_transform(feat_matrix)
        else:
            feat_matrix = scaler.transform(feat_matrix)

        df = df.copy()
        df['_row'] = np.arange(len(df))

        X_seq, y_seq = [], []
        for chassis, group in df.sort_values(['chassis_no', 'charge_cycle_count']).groupby('chassis_no'):
            group = group[group['is_post_knee'] == 0]
            if len(group) <= sequence_length:
                continue
            idxs   = group['_row'].values
            feats  = feat_matrix[idxs]
            target = group['RUL_to_knee'].values
            for i in range(len(group) - sequence_length):
                X_seq.append(feats[i:i + sequence_length])
                y_seq.append(target[i + sequence_length - 1])

        X = np.array(X_seq, dtype=np.float32)
        y = np.array(y_seq, dtype=np.float32)
        return X, y

    scaler   = StandardScaler()
    X_tr, y_tr = _build(train_df, scaler, fit=True)
    X_te, y_te = _build(test_df,  scaler, fit=False)

    y_tr_raw = y_tr.copy()
    y_te_raw = y_te.copy()

    if LOG_TARGET:
        y_tr = np.log1p(np.clip(y_tr, 0, None))
        y_te = np.log1p(np.clip(y_te, 0, None))

    print(f"Sequences -> Train: {X_tr.shape}, Test: {X_te.shape}")
    return X_tr, y_tr, X_te, y_te, y_tr_raw, y_te_raw, scaler


# ---------------------------------------------
# SECTION 2: EVALUATION
# ---------------------------------------------

def evaluate(y_true_raw, y_pred_raw, model_name):
    """Evaluate in ORIGINAL (unlogged) space."""
    rmse   = np.sqrt(mean_squared_error(y_true_raw, y_pred_raw))
    mae    = mean_absolute_error(y_true_raw, y_pred_raw)
    r2     = r2_score(y_true_raw, y_pred_raw)
    bias   = np.mean(y_pred_raw - y_true_raw)

    pct_errs = np.abs(y_pred_raw - y_true_raw) / (np.abs(y_true_raw) + 1e-6) * 100
    excellent = np.mean(pct_errs < 5)  * 100
    good      = np.mean(pct_errs < 15) * 100
    poor      = np.mean(pct_errs > 30) * 100

    print(f"\n{'-'*70}")
    print(f"  {model_name}")
    print(f"  RMSE={rmse:.2f}  MAE={mae:.2f}  R²={r2:.4f}  Bias={bias:+.2f}")
    print(f"  Accuracy: <5%={excellent:.1f}%  <15%={good:.1f}%  >30%={poor:.1f}%")
    print(f"{'-'*70}")

    return {"Model": model_name, "RMSE": rmse, "MAE": mae, "R2": r2,
            "Bias": bias, "Pct_Excellent": excellent, "Pct_Good": good, "Pct_Poor": poor}


def inverse(y_log):
    """Inverse log-transform."""
    return np.expm1(y_log) if LOG_TARGET else y_log


# ---------------------------------------------
# SECTION 3: TREE-BASED MODELS
# ---------------------------------------------

def train_tree_models(X_train, y_train, X_test, y_test_raw, y_train_raw):
    results = []

    # XGBoost (tuned)
    print("\n[1/3] Training XGBoost...")
    xgb_model = xgb.XGBRegressor(
        n_estimators=1000, max_depth=5, learning_rate=0.02,
        subsample=0.8, colsample_bytree=0.7,
        min_child_weight=5, reg_lambda=1.0, reg_alpha=0.1,
        random_state=RANDOM_SEED, n_jobs=-1,
        early_stopping_rounds=50,
        eval_metric='rmse'
    )
    split = int(len(X_train) * 0.9)
    xgb_model.fit(X_train[:split], y_train[:split],
                  eval_set=[(X_train[split:], y_train[split:])], verbose=False)
    xgb_pred_test  = inverse(xgb_model.predict(X_test))
    xgb_pred_train = inverse(xgb_model.predict(X_train))
    results.append(evaluate(y_test_raw,  xgb_pred_test,  "XGBoost (tuned)"))
    xgb_model.save_model(os.path.join(DATA_DIR, "xgb_improved.json"))

    # Random Forest (tuned)
    print("[2/3] Training Random Forest...")
    rf = RandomForestRegressor(
        n_estimators=300, max_depth=10, min_samples_leaf=5,
        max_features=0.6, random_state=RANDOM_SEED, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    rf_pred_test = inverse(rf.predict(X_test))
    results.append(evaluate(y_test_raw, rf_pred_test, "Random Forest (tuned)"))

    # Gradient Boosting (tuned)
    print("[3/3] Training Gradient Boosting...")
    gbm = GradientBoostingRegressor(
        n_estimators=500, max_depth=4, learning_rate=0.02,
        subsample=0.8, min_samples_leaf=5, random_state=RANDOM_SEED
    )
    gbm.fit(X_train, y_train)
    gbm_pred_test = inverse(gbm.predict(X_test))
    results.append(evaluate(y_test_raw, gbm_pred_test, "Gradient Boosting (tuned)"))

    return results, xgb_model, rf, gbm, xgb_pred_test, rf_pred_test, gbm_pred_test


# ---------------------------------------------
# SECTION 4: DEEP LEARNING MODELS
# ---------------------------------------------

def get_callbacks():
    return [
        EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, min_delta=0.1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=7, min_lr=1e-5, verbose=0)
    ]


def build_bilstm(input_shape):
    """Stacked Bidirectional LSTM."""
    inp = Input(shape=input_shape)
    x = Bidirectional(LSTM(64, return_sequences=True))(inp)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    x = Bidirectional(LSTM(32, return_sequences=False))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    x = Dense(32, activation='relu')(x)
    x = Dropout(0.1)(x)
    out = Dense(1)(x)
    m = Model(inp, out)
    m.compile(Adam(1e-3), tf.keras.losses.Huber(delta=10.0), metrics=['mae'])
    return m


def build_bigru(input_shape):
    """Stacked Bidirectional GRU."""
    inp = Input(shape=input_shape)
    x = Bidirectional(GRU(64, return_sequences=True))(inp)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    x = Bidirectional(GRU(32, return_sequences=False))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    x = Dense(32, activation='relu')(x)
    out = Dense(1)(x)
    m = Model(inp, out)
    m.compile(Adam(1e-3), tf.keras.losses.Huber(delta=10.0), metrics=['mae'])
    return m


def build_cnn_bilstm(input_shape):
    """Multi-scale CNN + Bidirectional LSTM."""
    inp = Input(shape=input_shape)
    c3  = Conv1D(32, 3, padding='same', activation='relu')(inp)
    c5  = Conv1D(32, 5, padding='same', activation='relu')(inp)
    x   = Concatenate()([c3, c5])
    x   = BatchNormalization()(x)
    x   = Dropout(0.1)(x)
    x   = Bidirectional(LSTM(64, return_sequences=False))(x)
    x   = BatchNormalization()(x)
    x   = Dropout(0.2)(x)
    x   = Dense(32, activation='relu')(x)
    out = Dense(1)(x)
    m = Model(inp, out)
    m.compile(Adam(1e-3), tf.keras.losses.Huber(delta=10.0), metrics=['mae'])
    return m


def train_dl_models(X_train, y_train, X_test, y_test_raw, y_train_raw):
    results = []
    preds   = {}
    input_shape = (X_train.shape[1], X_train.shape[2])

    for name, builder in [
        ("BiLSTM",      build_bilstm),
        ("BiGRU",       build_bigru),
        ("CNN-BiLSTM",  build_cnn_bilstm),
    ]:
        print(f"\n[DL] Training {name}...")
        model = builder(input_shape)
        model.fit(
            X_train, y_train,
            epochs=EPOCHS, batch_size=BATCH_SIZE,
            validation_split=0.1,
            callbacks=get_callbacks(),
            verbose=0
        )
        pred_log = model.predict(X_test, verbose=0).flatten()
        pred_raw = inverse(pred_log)
        results.append(evaluate(y_test_raw, pred_raw, name))
        preds[name] = pred_raw
        model.save(os.path.join(DATA_DIR, f"{name.lower().replace('-','_')}_model.keras"))

    return results, preds


# ---------------------------------------------
# SECTION 5: STACKING ENSEMBLE
# ---------------------------------------------

def _make_xgb_no_es():
    """XGBoost without early_stopping — safe for KFold splits."""
    return xgb.XGBRegressor(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.7,
        min_child_weight=5, reg_lambda=1.0, reg_alpha=0.1,
        random_state=RANDOM_SEED, n_jobs=-1
    )


def stacking_ensemble(
    X_train_tab, y_train_raw, X_test_tab,
    xgb_model, rf, gbm
):
    """
    Build OOF predictions from tabular models using time-ordered 5-fold CV.
    Train a Ridge meta-learner on OOF predictions.
    Returns test-set meta-predictions.
    """
    from sklearn.model_selection import KFold
    print("\n[Ensemble] Building stacking ensemble...")

    n = len(X_train_tab)
    kf = KFold(n_splits=5, shuffle=False)   # ordered split for time-series

    xgb_fresh = xgb.XGBRegressor(
        n_estimators=300, max_depth=5, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.7,
        random_state=RANDOM_SEED, n_jobs=-1
    )
    rf_fresh = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=RANDOM_SEED, n_jobs=-1)
    gbm_fresh = GradientBoostingRegressor(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=RANDOM_SEED)

    base_models = [
        ("XGBoost", xgb_fresh),
        ("RF",      rf_fresh),
        ("GBM",     gbm_fresh),
    ]

    oof  = np.zeros((n, len(base_models)))
    test_avg = np.zeros((len(X_test_tab), len(base_models)))

    y_train_log = np.log1p(np.clip(y_train_raw, 0, None)) if LOG_TARGET else y_train_raw

    for j, (name, model) in enumerate(base_models):
        fold_preds = []
        for fold_idx, (tr, val) in enumerate(kf.split(X_train_tab)):
            model.fit(X_train_tab[tr], y_train_log[tr])
            oof[val, j] = inverse(model.predict(X_train_tab[val]))
            fold_preds.append(inverse(model.predict(X_test_tab)))
        test_avg[:, j] = np.mean(fold_preds, axis=0)
        oof_rmse = np.sqrt(mean_squared_error(y_train_raw, oof[:, j]))
        print(f"  OOF RMSE [{name}]: {oof_rmse:.2f}")

    meta = Ridge(alpha=1.0)
    meta.fit(oof, y_train_raw)
    print(f"  Meta-learner weights: {dict(zip([n for n,_ in base_models], meta.coef_.round(3)))}")
    return meta.predict(test_avg), meta


# ---------------------------------------------
# SECTION 6: RESIDUAL CORRECTOR
# ---------------------------------------------

def residual_corrector(X_train, y_train_raw, y_pred_train, X_test, y_pred_test):
    """
    Train a GBM on training residuals to correct systematic prediction bias.
    """
    print("\n[Residual] Training residual corrector...")
    residuals_train = y_train_raw - y_pred_train

    corrector = GradientBoostingRegressor(
        n_estimators=200, max_depth=3, learning_rate=0.05, random_state=RANDOM_SEED
    )
    corrector.fit(X_train, residuals_train)
    correction = corrector.predict(X_test)
    y_corrected = y_pred_test + correction

    print(f"  Mean residual before: {np.mean(y_train_raw - y_pred_train):.2f}")
    print(f"  Mean correction applied: {np.mean(correction):.2f}")
    return y_corrected


# ---------------------------------------------
# MAIN
# ---------------------------------------------

def main():
    print("=" * 70)
    print("  IMPROVED RUL-TO-KNEE PREDICTION PIPELINE")
    print(f"  LOG_TARGET={LOG_TARGET}, SEQUENCE_LEN={SEQUENCE_LEN}")
    print("=" * 70)

    if not os.path.exists(FEATURE_PATH):
        print(f"ERROR: {FEATURE_PATH} not found. Run data_processing.py first.")
        return

    df = pd.read_csv(FEATURE_PATH)
    print(f"\nLoaded dataset: {df.shape}")
    print(f"RUL_to_knee stats: min={df['RUL_to_knee'].min():.1f}, "
          f"max={df['RUL_to_knee'].max():.1f}, "
          f"mean={df['RUL_to_knee'].mean():.1f}, "
          f"median={df['RUL_to_knee'].median():.1f}")

    # -- Tabular data ------------------------------
    (X_train_tab, X_test_tab,
     y_train_log, y_test_log,
     y_train_raw, y_test_raw,
     feature_names, train_df, test_df) = prepare_tabular_data(df)

    # -- Sequence data -----------------------------
    seq_features = [c for c in train_df.columns if c not in EXCLUDE_COLS
                    and np.issubdtype(train_df[c].dtype, np.number)]
    (X_tr_seq, y_tr_seq, X_te_seq, y_te_seq,
     y_tr_seq_raw, y_te_seq_raw, seq_scaler) = create_sequences(
        train_df, test_df, seq_features, SEQUENCE_LEN
    )

    all_results = []

    # -- Tree models -------------------------------
    print("\n" + "=" * 70)
    print("TREE-BASED MODELS")
    print("=" * 70)
    tree_results, xgb_m, rf_m, gbm_m, xgb_preds, rf_preds, gbm_preds = \
        train_tree_models(X_train_tab, y_train_log, X_test_tab, y_test_raw, y_train_raw)
    all_results.extend(tree_results)

    # -- Deep learning models ----------------------
    print("\n" + "=" * 70)
    print("DEEP LEARNING MODELS")
    print("=" * 70)
    dl_results, dl_preds = train_dl_models(X_tr_seq, y_tr_seq, X_te_seq, y_te_seq_raw, y_tr_seq_raw)
    all_results.extend(dl_results)

    # -- Stacking ensemble -------------------------
    print("\n" + "=" * 70)
    print("STACKING ENSEMBLE")
    print("=" * 70)
    stack_preds, meta_model = stacking_ensemble(
        X_train_tab, y_train_raw, X_test_tab, xgb_m, rf_m, gbm_m
    )
    all_results.append(evaluate(y_test_raw, stack_preds, "Stacking Ensemble (Ridge meta)"))

    # -- Residual corrector on best model ----------
    best_xgb_train = inverse(xgb_m.predict(X_train_tab))
    corrected_xgb  = residual_corrector(
        X_train_tab, y_train_raw, best_xgb_train, X_test_tab, xgb_preds
    )
    all_results.append(evaluate(y_test_raw, corrected_xgb, "XGBoost + Residual Corrector"))

    # -- Final summary -----------------------------
    print("\n" + "=" * 70)
    print("FINAL COMPARISON TABLE")
    print("=" * 70)
    res_df = pd.DataFrame(all_results).sort_values('RMSE')
    print(res_df.to_string(index=False))

    res_df.to_csv(os.path.join(DATA_DIR, "improved_model_metrics.csv"), index=False)
    print(f"\nMetrics saved -> data/improved_model_metrics.csv")

    # Save predictions for visualization
    # (tabular test indices are aligned)
    pred_save = pd.DataFrame({
        'y_true':          y_test_raw,
        'xgb_pred':        xgb_preds,
        'rf_pred':         rf_preds,
        'gbm_pred':        gbm_preds,
        'stack_pred':      stack_preds,
        'corrected_pred':  corrected_xgb,
    })
    # DL preds may have different length (sequence-based split), save separately
    dl_pred_save = pd.DataFrame({'y_true': y_te_seq_raw, **dl_preds})
    pred_save.to_csv(os.path.join(DATA_DIR, "improved_predictions_tabular.csv"), index=False)
    dl_pred_save.to_csv(os.path.join(DATA_DIR, "improved_predictions_dl.csv"), index=False)
    print("Predictions saved.")


if __name__ == "__main__":
    main()
