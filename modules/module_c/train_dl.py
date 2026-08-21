import pandas as pd
import numpy as np
import os
import joblib
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    LSTM, GRU, Dense, Conv1D, Dropout, Input,
    BatchNormalization, Bidirectional, Concatenate
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# -- Config ---------------------------------------------------------------
SEQUENCE_LEN = 30    # was buggy (5 in last run) or insufficient (20)
EPOCHS       = 200   # let ReduceLROnPlateau + EarlyStopping handle termination
BATCH_SIZE   = 64    # larger batches -> more stable RNN gradients
LOG_TARGET   = True  # log1p-transform target -> removes underprediction bias
# -------------------------------------------------------------------------

EXCLUDE_COLS = [
    'chassis_no', 'date', 'timestamp', 'vehicle_no', 'city', 'oem', 'model',
    'source_file', 'cmcdts', 'start_gps', 'end_gps', 'createdAt', 'updatedAt',
    'rts', 'gdts', 'grts', 'vehicle_status', 'drive_mode', 'charge_inlet_mode', 'vmdl',
    'is_post_knee', 'knee_cycle', 'RUL_to_knee'
]


def inv(y):
    """Inverse log1p."""
    return np.expm1(y) if LOG_TARGET else y


def create_sequences(train_df, test_df, features, sequence_length=SEQUENCE_LEN):
    """
    Build sliding-window sequences.
    FIX: StandardScaler fitted on TRAIN rows only, then applied to test rows.
    FIX: sequence_length=30 (not 5).
    """
    def _build(df, feat_matrix, scaler, fit):
        df = df.copy().reset_index(drop=True)
        data = df[features].fillna(0).values
        if fit:
            data = scaler.fit_transform(data)
        else:
            data = scaler.transform(data)
        df['_row'] = np.arange(len(df))

        X_seq, y_seq = [], []
        for chassis, group in df.sort_values(['chassis_no', 'charge_cycle_count']).groupby('chassis_no'):
            group = group[group['is_post_knee'] == 0]
            if len(group) <= sequence_length:
                continue
            idxs   = group['_row'].values
            feats  = data[idxs]
            target = group['RUL_to_knee'].values
            for i in range(len(group) - sequence_length):
                X_seq.append(feats[i:i + sequence_length])
                y_seq.append(target[i + sequence_length - 1])
        return np.array(X_seq, dtype=np.float32), np.array(y_seq, dtype=np.float32)

    print(f"Creating sequences of length {sequence_length}...")
    scaler = StandardScaler()
    X_tr, y_tr = _build(train_df, None, scaler, fit=True)
    X_te, y_te = _build(test_df,  None, scaler, fit=False)
    joblib.dump(scaler, 'seq_scaler.pkl')

    y_tr_raw = y_tr.copy()
    y_te_raw = y_te.copy()
    if LOG_TARGET:
        y_tr = np.log1p(np.clip(y_tr, 0, None))
        y_te = np.log1p(np.clip(y_te, 0, None))

    print(f"Sequences -> Train: {X_tr.shape}, Test: {X_te.shape}")
    return X_tr, y_tr, X_te, y_te, y_tr_raw, y_te_raw

def evaluate(y_true_raw, y_pred_log, model_name):
    """Evaluate in original (unlogged) cycle units and print accuracy bands."""
    y_pred = inv(y_pred_log)
    rmse   = np.sqrt(mean_squared_error(y_true_raw, y_pred))
    mae    = mean_absolute_error(y_true_raw, y_pred)
    r2     = r2_score(y_true_raw, y_pred)
    bias   = np.mean(y_pred - y_true_raw)

    pct    = np.abs(y_pred - y_true_raw) / (np.abs(y_true_raw) + 1e-6) * 100
    good   = np.mean(pct < 15) * 100
    poor   = np.mean(pct > 30) * 100

    print(f"{model_name:20s} | RMSE:{rmse:7.2f} | MAE:{mae:7.2f} | R²:{r2:.4f} | "
          f"Bias:{bias:+.1f} | <15%:{good:.0f}% >30%:{poor:.0f}%")
    return {"Model": model_name, "RMSE": rmse, "MAE": mae, "R2_Test": r2,
            "Bias": bias, "Pct_Good": good, "Pct_Poor": poor}

def get_callbacks():
    return [
        EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, min_delta=0.1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=7, min_lr=1e-5, verbose=0)
    ]


def train_bilstm(X_train, y_train, X_test, y_te_raw, input_shape):
    """Stacked Bidirectional LSTM with BatchNorm + Huber loss."""
    print(f"Training BiLSTM {input_shape}...")
    inp = Input(shape=input_shape)
    x   = Bidirectional(LSTM(64, return_sequences=True))(inp)
    x   = BatchNormalization()(x)
    x   = Dropout(0.2)(x)
    x   = Bidirectional(LSTM(32, return_sequences=False))(x)
    x   = BatchNormalization()(x)
    x   = Dropout(0.2)(x)
    x   = Dense(32, activation='relu')(x)
    x   = Dropout(0.1)(x)
    out = Dense(1)(x)
    model = Model(inp, out)
    model.compile(Adam(1e-3), tf.keras.losses.Huber(delta=10.0), metrics=['mae'])
    model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE,
              validation_split=0.1, callbacks=get_callbacks(), verbose=0)
    pred_log = model.predict(X_test, verbose=0).flatten()
    return evaluate(y_te_raw, pred_log, "BiLSTM"), model


def train_bigru(X_train, y_train, X_test, y_te_raw, input_shape):
    """Stacked Bidirectional GRU with BatchNorm + Huber loss."""
    print(f"Training BiGRU {input_shape}...")
    inp = Input(shape=input_shape)
    x   = Bidirectional(GRU(64, return_sequences=True))(inp)
    x   = BatchNormalization()(x)
    x   = Dropout(0.2)(x)
    x   = Bidirectional(GRU(32, return_sequences=False))(x)
    x   = BatchNormalization()(x)
    x   = Dropout(0.2)(x)
    x   = Dense(32, activation='relu')(x)
    out = Dense(1)(x)
    model = Model(inp, out)
    model.compile(Adam(1e-3), tf.keras.losses.Huber(delta=10.0), metrics=['mae'])
    model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE,
              validation_split=0.1, callbacks=get_callbacks(), verbose=0)
    pred_log = model.predict(X_test, verbose=0).flatten()
    return evaluate(y_te_raw, pred_log, "BiGRU"), model


def train_cnn_bilstm(X_train, y_train, X_test, y_te_raw, input_shape):
    """Multi-scale CNN (3+5 kernel) + Bidirectional LSTM + Huber loss."""
    print(f"Training CNN-BiLSTM {input_shape}...")
    inp = Input(shape=input_shape)
    c3  = Conv1D(32, kernel_size=3, padding='same', activation='relu')(inp)
    c5  = Conv1D(32, kernel_size=5, padding='same', activation='relu')(inp)
    x   = Concatenate()([c3, c5])
    x   = BatchNormalization()(x)
    x   = Dropout(0.1)(x)
    x   = Bidirectional(LSTM(64, return_sequences=False))(x)
    x   = BatchNormalization()(x)
    x   = Dropout(0.2)(x)
    x   = Dense(32, activation='relu')(x)
    out = Dense(1)(x)
    model = Model(inp, out)
    model.compile(Adam(1e-3), tf.keras.losses.Huber(delta=10.0), metrics=['mae'])
    model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE,
              validation_split=0.1, callbacks=get_callbacks(), verbose=0)
    pred_log = model.predict(X_test, verbose=0).flatten()
    return evaluate(y_te_raw, pred_log, "CNN-BiLSTM"), model

def main():
    data_dir     = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    feature_path = os.path.join(data_dir, "labeled_features.csv")

    if not os.path.exists(feature_path):
        print(f"Error: {feature_path} not found.")
        return

    df     = pd.read_csv(feature_path)
    df_pre = df[df['is_post_knee'] == 0].copy()

    # Chassis-level split (same seed as train_evaluate.py)
    unique_chassis = df_pre['chassis_no'].unique().tolist()
    np.random.seed(42)
    np.random.shuffle(unique_chassis)
    split_idx     = int(len(unique_chassis) * 0.8)
    train_chassis = unique_chassis[:split_idx]
    test_chassis  = unique_chassis[split_idx:]
    train_df = df_pre[df_pre['chassis_no'].isin(train_chassis)]
    test_df  = df_pre[df_pre['chassis_no'].isin(test_chassis)]

    features = [c for c in train_df.columns
                if c not in EXCLUDE_COLS
                and np.issubdtype(train_df[c].dtype, np.number)]

    # Build sequences (with correct scaling)
    X_tr, y_tr, X_te, y_te, y_tr_raw, y_te_raw = create_sequences(
        train_df, test_df, features, SEQUENCE_LEN
    )
    input_shape = (X_tr.shape[1], X_tr.shape[2])

    results = []

    # BiLSTM
    res, lstm_model = train_bilstm(X_tr, y_tr, X_te, y_te_raw, input_shape)
    results.append(res)
    lstm_model.save(os.path.join(data_dir, "best_bilstm_model.keras"))
    print("  Saved BiLSTM")

    # BiGRU
    res, gru_model = train_bigru(X_tr, y_tr, X_te, y_te_raw, input_shape)
    results.append(res)
    gru_model.save(os.path.join(data_dir, "best_bigru_model.keras"))
    print("  Saved BiGRU")

    # CNN-BiLSTM
    res, cnn_model = train_cnn_bilstm(X_tr, y_tr, X_te, y_te_raw, input_shape)
    results.append(res)
    cnn_model.save(os.path.join(data_dir, "best_cnn_bilstm_model.keras"))
    print("  Saved CNN-BiLSTM")

    # Merge with ML metrics
    metrics_path = os.path.join(data_dir, "model_metrics.csv")
    new_df = pd.DataFrame(results)
    if os.path.exists(metrics_path):
        existing = pd.read_csv(metrics_path)
        final    = pd.concat([existing, new_df], ignore_index=True)
    else:
        final = new_df
    final.to_csv(metrics_path, index=False)

    print("\n" + "="*100)
    print("ALL MODEL COMPARISON  (metrics in original RUL cycle units)")
    print("="*100)
    print(final.to_string(index=False))

if __name__ == "__main__":
    main()
