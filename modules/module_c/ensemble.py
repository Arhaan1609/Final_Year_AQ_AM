import pandas as pd
import numpy as np
import os
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from sklearn.model_selection import train_test_split

def evaluate(y_train_true, y_train_pred, y_test_true, y_test_pred, model_name):
    rmse = np.sqrt(mean_squared_error(y_test_true, y_test_pred))
    mae = mean_absolute_error(y_test_true, y_test_pred)
    r2_train = r2_score(y_train_true, y_train_pred)
    r2_test = r2_score(y_test_true, y_test_pred)
    print(f"{model_name:40s} | RMSE: {rmse:8.2f} | MAE: {mae:8.2f} | R² Train: {r2_train:.4f} | R² Test: {r2_test:.4f}")
    return {"Model": model_name, "RMSE": rmse, "MAE": mae, "R2_Train": r2_train, "R2_Test": r2_test}

def create_sequences(df, features, sequence_length=20):
    X_seq, y_seq = [], []
    df = df.sort_values(by=['chassis_no', 'charge_cycle_count'])
    for chassis, group in df.groupby('chassis_no'):
        group = group[group['is_post_knee'] == 0]
        if len(group) <= sequence_length:
            continue
        feat_data = group[features].fillna(0).values
        target_data = group['RUL_to_knee'].values
        for i in range(len(group) - sequence_length):
            X_seq.append(feat_data[i:i+sequence_length])
            y_seq.append(target_data[i+sequence_length-1])
    return np.array(X_seq), np.array(y_seq)

def main():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    feature_path = os.path.join(data_dir, "labeled_features.csv")
    df = pd.read_csv(feature_path)

    # Time-based split
    df_pre = df[df['is_post_knee'] == 0].copy()
    # Strict battery-level split (randomized to prevent life span bias)
    unique_chassis = df_pre['chassis_no'].unique().tolist()
    np.random.seed(42)
    np.random.shuffle(unique_chassis)
    
    split_idx = int(len(unique_chassis) * 0.8)
    train_chassis = unique_chassis[:split_idx]
    test_chassis = unique_chassis[split_idx:]
    
    train_df = df_pre[df_pre['chassis_no'].isin(train_chassis)]
    test_df = df_pre[df_pre['chassis_no'].isin(test_chassis)]
    
    exclude_cols = ['chassis_no', 'date', 'timestamp', 'vehicle_no', 'city', 'oem', 'model', 
                    'source_file', 'cmcdts', 'start_gps', 'end_gps', 'createdAt', 'updatedAt',
                    'rts', 'gdts', 'grts', 'vehicle_status', 'drive_mode', 'charge_inlet_mode', 'vmdl',
                    'is_post_knee', 'knee_cycle', 'RUL_to_knee']
    num_features = [col for col in train_df.columns if col not in exclude_cols]

    train_pre = train_df[train_df['is_post_knee'] == 0]
    test_pre = test_df[test_df['is_post_knee'] == 0]
    X_train = train_pre[num_features].fillna(0).select_dtypes(include=[np.number])
    y_train = train_pre['RUL_to_knee']
    X_test = test_pre[num_features].fillna(0).select_dtypes(include=[np.number])
    y_test = test_pre['RUL_to_knee']
    num_features = X_train.columns.tolist()
    X_train, X_test = X_train.align(X_test, join='left', axis=1, fill_value=0)

    # Retrain XGBoost with tuned hyperparams
    print("Training XGBoost for ensemble...")
    xgb_model = xgb.XGBRegressor(n_estimators=500, max_depth=6, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1)
    xgb_model.fit(X_train, y_train)
    y_pred_xgb_test = xgb_model.predict(X_test)
    y_pred_xgb_train = xgb_model.predict(X_train)

    # Create sequences for LSTM and GRU (sequence_length = 20)
    print("Creating sequences for DL ensemble...")
    X_train_seq, y_train_seq = create_sequences(train_df, num_features, 20)
    X_test_seq, y_test_seq = create_sequences(test_df, num_features, 20)
    X_train_seq = np.asarray(X_train_seq).astype(np.float32)
    X_test_seq = np.asarray(X_test_seq).astype(np.float32)
    y_train_seq = np.asarray(y_train_seq).astype(np.float32)
    y_test_seq = np.asarray(y_test_seq).astype(np.float32)

    # Load or retrain LSTM
    lstm_path = os.path.join(data_dir, "best_lstm_model.h5")
    if os.path.exists(lstm_path):
        lstm_model = tf.keras.models.load_model(lstm_path, compile=False)
    else:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        from tensorflow.keras.callbacks import EarlyStopping
        lstm_model = Sequential([
            LSTM(64, input_shape=(X_train_seq.shape[1], X_train_seq.shape[2])),
            Dropout(0.3), Dense(32, activation='relu'), Dense(1)
        ])
        lstm_model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        lstm_model.fit(X_train_seq, y_train_seq, epochs=50, batch_size=32, validation_split=0.1, callbacks=[early_stop], verbose=0)

    # Load or retrain GRU
    gru_path = os.path.join(data_dir, "best_gru_model.h5")
    if os.path.exists(gru_path):
        gru_model = tf.keras.models.load_model(gru_path, compile=False)
    else:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import GRU, Dense, Dropout
        from tensorflow.keras.callbacks import EarlyStopping
        gru_model = Sequential([
            GRU(64, input_shape=(X_train_seq.shape[1], X_train_seq.shape[2])),
            Dropout(0.3), Dense(32, activation='relu'), Dense(1)
        ])
        gru_model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        gru_model.fit(X_train_seq, y_train_seq, epochs=50, batch_size=32, validation_split=0.1, callbacks=[early_stop], verbose=0)

    # Build XGBoost predictions matching the sequence test indices
    test_df_pre = test_df[test_df['is_post_knee'] == 0].sort_values(by=['chassis_no', 'charge_cycle_count'])
    xgb_preds_for_ensemble = []
    for chassis, group in test_df_pre.groupby('chassis_no'):
        group_reset = group.reset_index(drop=True)
        group_feats = group_reset[num_features].fillna(0)
        if len(group_reset) <= 20:
            continue
        for i in range(len(group_reset) - 20):
            row = group_feats.iloc[i+20-1:i+20]
            xgb_preds_for_ensemble.append(xgb_model.predict(row)[0])

    xgb_preds_for_ensemble = np.array(xgb_preds_for_ensemble)
    
    # Align lengths
    min_len = min(len(xgb_preds_for_ensemble), len(X_test_seq))
    xgb_preds_aligned = xgb_preds_for_ensemble[:min_len]
    X_test_seq_aligned = X_test_seq[:min_len]
    y_test_aligned = y_test_seq[:min_len]

    # Similarly build XGB train preds for R² computation
    train_df_pre = train_df[train_df['is_post_knee'] == 0].sort_values(by=['chassis_no', 'charge_cycle_count'])
    xgb_preds_train = []
    for chassis, group in train_df_pre.groupby('chassis_no'):
        group_reset = group.reset_index(drop=True)
        group_feats = group_reset[num_features].fillna(0)
        if len(group_reset) <= 20:
            continue
        for i in range(len(group_reset) - 20):
            row = group_feats.iloc[i+20-1:i+20]
            xgb_preds_train.append(xgb_model.predict(row)[0])
    xgb_preds_train = np.array(xgb_preds_train)
    min_len_train = min(len(xgb_preds_train), len(X_train_seq))
    xgb_preds_train = xgb_preds_train[:min_len_train]
    X_train_seq_aligned = X_train_seq[:min_len_train]
    y_train_aligned = y_train_seq[:min_len_train]

    # DL predictions
    lstm_preds_test = lstm_model.predict(X_test_seq_aligned, verbose=0).flatten()
    lstm_preds_train = lstm_model.predict(X_train_seq_aligned, verbose=0).flatten()
    gru_preds_test = gru_model.predict(X_test_seq_aligned, verbose=0).flatten()
    gru_preds_train = gru_model.predict(X_train_seq_aligned, verbose=0).flatten()

    # ===== WEIGHTED ENSEMBLE: 0.5*LSTM + 0.3*GRU + 0.2*XGBoost =====
    ensemble_preds_test = 0.5 * lstm_preds_test + 0.3 * gru_preds_test + 0.2 * xgb_preds_aligned
    ensemble_preds_train = 0.5 * lstm_preds_train + 0.3 * gru_preds_train + 0.2 * xgb_preds_train

    results = []
    results.append(evaluate(y_train_aligned, xgb_preds_train, y_test_aligned, xgb_preds_aligned, "XGBoost (Ensemble Context)"))
    results.append(evaluate(y_train_aligned, lstm_preds_train, y_test_aligned, lstm_preds_test, "LSTM (Ensemble Context)"))
    results.append(evaluate(y_train_aligned, gru_preds_train, y_test_aligned, gru_preds_test, "GRU (Ensemble Context)"))
    results.append(evaluate(y_train_aligned, ensemble_preds_train, y_test_aligned, ensemble_preds_test, "Weighted Ensemble (0.5L+0.3G+0.2X)"))

    print("\n" + "="*90)
    print("ENSEMBLE RESULTS")
    print("="*90)
    print(pd.DataFrame(results).to_string(index=False))

    # Feature Importance
    print("\nTop 15 XGBoost Feature Importances:")
    fi = pd.Series(xgb_model.feature_importances_, index=num_features).sort_values(ascending=False).head(15)
    print(fi.to_string())
    fi.to_csv(os.path.join(data_dir, "feature_importance.csv"), header=['importance'])

    # Save ensemble results
    pd.DataFrame(results).to_csv(os.path.join(data_dir, "ensemble_metrics.csv"), index=False)
    
    # Save predictions for plotting
    pred_df = pd.DataFrame({
        'y_true': y_test_aligned,
        'xgb_pred': xgb_preds_aligned,
        'lstm_pred': lstm_preds_test,
        'gru_pred': gru_preds_test,
        'ensemble_pred': ensemble_preds_test
    })
    pred_df.to_csv(os.path.join(data_dir, "predictions.csv"), index=False)
    print(f"\nSaved predictions and feature importance to data folder.")

if __name__ == "__main__":
    main()
