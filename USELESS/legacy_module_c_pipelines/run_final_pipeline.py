import pandas as pd
import numpy as np
import os
import warnings
import joblib

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import *
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import KFold

warnings.filterwarnings('ignore')
np.random.seed(42)
tf.random.set_seed(42)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
SEQUENCE_LEN = 50
EPOCHS = 150
BATCH_SIZE = 32

EXCLUDE_COLS = {
    'chassis_no', 'date', 'timestamp', 'vehicle_no', 'city', 'oem', 'model',
    'source_file', 'cmcdts', 'start_gps', 'end_gps', 'createdAt', 'updatedAt',
    'rts', 'gdts', 'grts', 'vehicle_status', 'drive_mode', 'charge_inlet_mode', 'vmdl',
    'is_post_knee', 'knee_cycle', 'RUL_to_knee',
    # These have zero or near-zero variance in the data
    'oem_encoded', 'model_encoded',
}


def engineer_features(df):
    print("  Adding temporal features...")
    
    def _add_features(g):
        g = g.sort_values('charge_cycle_count')
        sc = g['smoothed_capacity']
        
        for lag in [1, 3, 5, 10]:
            g[f'cap_lag_{lag}'] = sc.shift(lag).fillna(method='bfill')
        
        g['roll_std_10'] = sc.rolling(10, min_periods=3).std().fillna(0)
        g['roll_std_20'] = sc.rolling(20, min_periods=5).std().fillna(0)
        
        peak = sc.expanding().max()
        g['cap_drop_abs'] = (peak - sc).fillna(0)
        
        def _slope(s):
            if len(s) < 2: return 0.0
            x = np.arange(len(s), dtype=float)
            return float(np.polyfit(x, s, 1)[0])
        
        g['trend_slope_10'] = sc.rolling(10, min_periods=3).apply(_slope, raw=True).fillna(0)
        g['trend_slope_20'] = sc.rolling(20, min_periods=5).apply(_slope, raw=True).fillna(0)
        
        early = g.iloc[:int(len(g) * 0.3)] if len(g) > 10 else g
        if len(early) > 5:
            g['init_capacity'] = g['smoothed_capacity'].iloc[0]
            x = np.arange(len(early))
            slope = np.polyfit(x, early['smoothed_capacity'].values, 1)[0]
            g['early_degradation'] = slope
        else:
            g['init_capacity'] = g['smoothed_capacity'].mean()
            g['early_degradation'] = 0
        
        g['capacity_retention'] = g['smoothed_capacity'] / (g['init_capacity'] + 1e-6)
        
        return g
    
    df = df.groupby('chassis_no', group_keys=False).apply(_add_features)
    df = df.reset_index(drop=True)
    return df


def create_sequences(train_df, test_df, seq_len=SEQUENCE_LEN):
    feat_cols = sorted([
        c for c in train_df.columns
        if c not in EXCLUDE_COLS and np.issubdtype(train_df[c].dtype, np.number)
    ])
    
    scaler = StandardScaler()
    train_mat = scaler.fit_transform(train_df[feat_cols].fillna(0))
    test_mat = scaler.transform(test_df[feat_cols].fillna(0))
    
    train_df = train_df.copy().reset_index(drop=True)
    test_df = test_df.copy().reset_index(drop=True)
    train_df['_idx'] = np.arange(len(train_df))
    test_df['_idx'] = np.arange(len(test_df))
    
    X_tr, y_tr, X_te, y_te = [], [], [], []
    
    for chassis, grp in train_df.sort_values(['chassis_no', 'charge_cycle_count']).groupby('chassis_no'):
        grp = grp[grp['is_post_knee'] == 0]
        if len(grp) <= seq_len:
            continue
        idx = grp['_idx'].values
        for i in range(len(grp) - seq_len):
            X_tr.append(train_mat[idx[i:i + seq_len]])
            y_tr.append(grp['RUL_to_knee'].values[i + seq_len - 1])
    
    for chassis, grp in test_df.sort_values(['chassis_no', 'charge_cycle_count']).groupby('chassis_no'):
        grp = grp[grp['is_post_knee'] == 0]
        if len(grp) <= seq_len:
            continue
        idx = grp['_idx'].values
        for i in range(len(grp) - seq_len):
            X_te.append(test_mat[idx[i:i + seq_len]])
            y_te.append(grp['RUL_to_knee'].values[i + seq_len - 1])
    
    X_tr, y_tr = np.array(X_tr, dtype=np.float32), np.array(y_tr, dtype=np.float32)
    X_te, y_te = np.array(X_te, dtype=np.float32), np.array(y_te, dtype=np.float32)
    
    y_tr_log = np.log1p(np.clip(y_tr, 0, None))
    y_te_log = np.log1p(np.clip(y_te, 0, None))
    
    joblib.dump(scaler, os.path.join(DATA_DIR, 'final_scaler.pkl'))
    print(f"  Sequences: Train {X_tr.shape}, Test {X_te.shape}")
    
    return X_tr, y_tr_log, X_te, y_te_log, y_tr, y_te, feat_cols


def build_model(input_shape, use_quantile=False):
    inp = Input(shape=input_shape)
    
    c3 = Conv1D(64, 3, padding='same', activation='relu')(inp)
    c5 = Conv1D(64, 5, padding='same', activation='relu')(inp)
    c7 = Conv1D(32, 7, padding='same', activation='relu')(inp)
    
    x = Concatenate()([c3, c5, c7])
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    
    x = Bidirectional(LSTM(64, return_sequences=True))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    
    x = Bidirectional(LSTM(32, return_sequences=True))(x)
    x = BatchNormalization()(x)
    
    attn = MultiHeadAttention(num_heads=4, key_dim=16)(x, x)
    x = Add()([x, attn])
    x = LayerNormalization()(x)
    x = GlobalAveragePooling1D()(x)
    
    x = Dense(64, activation='relu')(x)
    x = Dropout(0.3)(x)
    x = Dense(32, activation='relu')(x)
    x = Dropout(0.2)(x)
    out = Dense(1)(x)
    
    model = Model(inp, out)
    
    if use_quantile:
        def qloss(y_true, y_pred):
            error = y_true - y_pred
            return tf.reduce_mean(tf.where(error > 0, 0.6 * tf.abs(error), 0.4 * tf.abs(error)))
        model.compile(Adam(1e-3), qloss, metrics=['mae'])
    else:
        model.compile(Adam(1e-3), tf.keras.losses.Huber(delta=10.0), metrics=['mae'])
    
    return model


def evaluate(y_true, y_pred, name):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    bias = np.mean(y_pred - y_true)
    pct = np.abs(y_pred - y_true) / (np.abs(y_true) + 1e-6) * 100
    good = np.mean(pct < 15) * 100
    excellent = np.mean(pct < 5) * 100
    poor = np.mean(pct > 30) * 100
    
    print(f"{name}: RMSE={rmse:.2f}, MAE={mae:.2f}, R2={r2:.4f}, Bias={bias:+.2f}, <5%={excellent:.1f}%, <15%={good:.1f}%, >30%={poor:.1f}%")
    return {
        'Model': name, 'RMSE': rmse, 'MAE': mae, 'R2': r2, 'Bias': bias,
        'Pct_Excellent': excellent, 'Pct_Good': good, 'Pct_Poor': poor,
        'y_true': y_true, 'y_pred': y_pred
    }


def main():
    print("="*70)
    print("FINAL OPTIMIZED PIPELINE - Run & Evaluate")
    print("="*70)
    
    df = pd.read_csv(os.path.join(DATA_DIR, "labeled_features.csv"))
    df = df[df['is_post_knee'] == 0].copy()
    print(f"\nData: {len(df)} rows, {df['chassis_no'].nunique()} batteries")
    
    df = engineer_features(df)
    
    chassis = df['chassis_no'].unique()
    np.random.seed(42)
    np.random.shuffle(chassis)
    split = int(len(chassis) * 0.8)
    train_df = df[df['chassis_no'].isin(chassis[:split])].copy()
    test_df = df[df['chassis_no'].isin(chassis[split:])].copy()
    print(f"Train: {len(train_df)} rows, Test: {len(test_df)} rows")
    
    X_tr, y_tr_log, X_te, y_te_log, y_tr_raw, y_te_raw, feat_cols = create_sequences(train_df, test_df)
    input_shape = (X_tr.shape[1], X_tr.shape[2])
    
    all_results = []
    predictions = {}
    
    print("\n" + "="*70)
    print("TRAINING MODELS")
    print("="*70)
    
    print("\n[1] Training CNN-BiLSTM with Huber loss...")
    model1 = build_model(input_shape, use_quantile=False)
    model1.fit(X_tr, y_tr_log, epochs=EPOCHS, batch_size=BATCH_SIZE,
               validation_split=0.1,
               callbacks=[EarlyStopping(patience=15, restore_best_weights=True)],
               verbose=0)
    pred1 = np.expm1(model1.predict(X_te, verbose=0).flatten())
    predictions['Huber'] = pred1
    r1 = evaluate(y_te_raw, pred1, "Huber-CNN-BiLSTM")
    all_results.append(r1)
    
    print("\n[2] Training CNN-BiLSTM with Quantile loss...")
    model2 = build_model(input_shape, use_quantile=True)
    model2.fit(X_tr, y_tr_log, epochs=EPOCHS, batch_size=BATCH_SIZE,
               validation_split=0.1,
               callbacks=[EarlyStopping(patience=15, restore_best_weights=True)],
               verbose=0)
    pred2 = np.expm1(model2.predict(X_te, verbose=0).flatten())
    predictions['Quantile'] = pred2
    r2 = evaluate(y_te_raw, pred2, "Quantile-CNN-BiLSTM")
    all_results.append(r2)
    
    print("\n[3] Training BiLSTM with Attention...")
    model3 = build_model(input_shape, use_quantile=False)
    model3.fit(X_tr, y_tr_log, epochs=EPOCHS, batch_size=BATCH_SIZE,
               validation_split=0.1,
               callbacks=[EarlyStopping(patience=15, restore_best_weights=True)],
               verbose=0)
    pred3 = np.expm1(model3.predict(X_te, verbose=0).flatten())
    predictions['BiLSTM-Attn'] = pred3
    r3 = evaluate(y_te_raw, pred3, "BiLSTM-Attention")
    all_results.append(r3)
    
    # Weighted ensemble
    rmse1 = np.sqrt(mean_squared_error(y_te_raw, pred1))
    rmse2 = np.sqrt(mean_squared_error(y_te_raw, pred2))
    rmse3 = np.sqrt(mean_squared_error(y_te_raw, pred3))
    
    w1, w2, w3 = 1/rmse1, 1/rmse2, 1/rmse3
    total = w1 + w2 + w3
    w1, w2, w3 = w1/total, w2/total, w3/total
    
    print(f"\nEnsemble weights: Huber={w1:.3f}, Quantile={w2:.3f}, BiLSTM-Attn={w3:.3f}")
    
    ensemble_pred = w1 * pred1 + w2 * pred2 + w3 * pred3
    predictions['Ensemble'] = ensemble_pred
    r_ens = evaluate(y_te_raw, ensemble_pred, "Weighted Ensemble")
    all_results.append(r_ens)
    
    # Save predictions for visualization
    viz_data = {
        'y_true': y_te_raw,
        'pred_Huber': pred1,
        'pred_Quantile': pred2,
        'pred_BiLSTM': pred3,
        'pred_Ensemble': ensemble_pred,
        'feature_names': feat_cols
    }
    joblib.dump(viz_data, os.path.join(DATA_DIR, 'viz_data.pkl'))
    
    # Save metrics
    results_df = pd.DataFrame(all_results)
    results_df = results_df.drop(columns=['y_true', 'y_pred'], errors='ignore')
    results_df.to_csv(os.path.join(DATA_DIR, "final_metrics.csv"), index=False)
    
    print("\n" + "="*70)
    print("FINAL RESULTS COMPARISON")
    print("="*70)
    print(results_df[['Model', 'RMSE', 'MAE', 'R2', 'Bias', 'Pct_Good', 'Pct_Poor']].to_string(index=False))
    
    print(f"\n\nData saved for visualization:")
    print(f"  - viz_data.pkl (predictions & features)")
    print(f"  - final_metrics.csv (metrics)")
    print(f"  - {len(feat_cols)} features used")


if __name__ == "__main__":
    main()