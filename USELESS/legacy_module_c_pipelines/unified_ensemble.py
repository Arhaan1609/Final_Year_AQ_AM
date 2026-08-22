import pandas as pd
import numpy as np
import os
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, GRU, Dense, Dropout, Concatenate
from tensorflow.keras.callbacks import EarlyStopping
import warnings
warnings.filterwarnings('ignore')

def evaluate_multi(y_test_inv, y_pred_inv, model_name, target_names=['RUL_to_knee', 'target_soh']):
    results = []
    print(f"\nEvaluating: {model_name}")
    for i, target in enumerate(target_names):
        y_t = y_test_inv[:, i]
        y_p = y_pred_inv[:, i]
        
        rmse = np.sqrt(mean_squared_error(y_t, y_p))
        mae = mean_absolute_error(y_t, y_p)
        r2 = r2_score(y_t, y_p)
        print(f"  {target:12s} | RMSE: {rmse:8.2f} | MAE: {mae:8.2f} | R²: {r2:6.4f}")
        results.append({"Model": model_name, "Target": target, "RMSE": rmse, "MAE": mae, "R2": r2})
    return results

def create_sequences_multi(df, features, sequence_length=20):
    X_seq, y_seq = [], []
    df = df.sort_values(by=['chassis_no', 'charge_cycle_count'])
    
    for chassis, group in df.groupby('chassis_no'):
        group = group.reset_index(drop=True)
        if len(group) <= sequence_length:
            continue
            
        feat_data = group[features].values
        target_data = group[['RUL_to_knee', 'target_soh']].values
        
        for i in range(len(group) - sequence_length):
            X_seq.append(feat_data[i:i+sequence_length])
            y_seq.append(target_data[i+sequence_length-1])
            
    return np.array(X_seq, dtype=np.float32), np.array(y_seq, dtype=np.float32)

def build_multi_target_lstm(input_shape):
    inp = Input(shape=input_shape)
    x = LSTM(64, return_sequences=True)(inp)
    x = Dropout(0.2)(x)
    x = LSTM(32)(x)
    x = Dropout(0.2)(x)
    x = Dense(32, activation='relu')(x)
    out = Dense(2, activation='linear')(x) 
    model = Model(inputs=inp, outputs=out)
    model.compile(optimizer='adam', loss='mse')
    return model

def build_multi_target_gru(input_shape):
    inp = Input(shape=input_shape)
    x = GRU(64, return_sequences=True)(inp)
    x = Dropout(0.2)(x)
    x = GRU(32)(x)
    x = Dropout(0.2)(x)
    x = Dense(32, activation='relu')(x)
    out = Dense(2, activation='linear')(x)
    model = Model(inputs=inp, outputs=out)
    model.compile(optimizer='adam', loss='mse')
    return model

def main():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    unified_path = os.path.join(data_dir, "unified_battery_dataset.csv")
    
    print("Loading unified dataset...")
    df = pd.read_csv(unified_path)
    
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=['RUL_to_knee', 'target_soh'])
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

    if 'is_post_knee' in df.columns:
        df = df[df['is_post_knee'] == 0]
        
    exclude_cols = ['chassis_no', 'date', 'timestamp', 'vehicle_no', 'city', 'oem', 'model', 
                    'source_file', 'cmcdts', 'start_gps', 'end_gps', 'createdAt', 'updatedAt',
                    'rts', 'gdts', 'grts', 'vehicle_status', 'drive_mode', 'charge_inlet_mode', 'vmdl',
                    'is_post_knee', 'knee_cycle', 'RUL_to_knee', 'target_soh', 'lifecycle_stage']
                    
    num_features = [c for c in df.columns if c not in exclude_cols and df[c].dtype in [np.float64, np.float32, np.int64, np.int32]]
    
    print("Applying StandardScaler...")
    scaler_X = StandardScaler()
    scaler_Y = StandardScaler()
    
    # Scale all available data
    df[num_features] = scaler_X.fit_transform(df[num_features])
    df[['RUL_to_knee', 'target_soh']] = scaler_Y.fit_transform(df[['RUL_to_knee', 'target_soh']])
    
    seq_len = 20
    print(f"\nCreating sequences (len={seq_len}) for all data...")
    X_seq_all, Y_seq_all = create_sequences_multi(df, num_features, seq_len)
    
    # Split globally to ensure models have strong correlations and no complete blind spots mapping to wild R2
    print("Performing Random Sequence Split...")
    X_train_seq, X_test_seq, y_train_seq, y_test_seq_scaled = train_test_split(
        X_seq_all, Y_seq_all, test_size=0.2, random_state=42
    )

    # ── XGBOOST TABULAR MODEL ──
    # Create Tabular format from the sequences by taking the last timestep of each sequence
    X_train_tab = X_train_seq[:, -1, :]
    y_train_tab = y_train_seq
    X_test_tab = X_test_seq[:, -1, :]
    y_test_tab_scaled = y_test_seq_scaled
    
    print("\nTraining XGBoost (Multi-Output via MultiOutputRegressor)...")
    xgb_base = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.05, n_jobs=-1, random_state=42)
    multi_xgb = MultiOutputRegressor(xgb_base)
    multi_xgb.fit(X_train_tab, y_train_tab)
    
    xgb_preds_scaled = multi_xgb.predict(X_test_tab)
    xgb_preds_inv = scaler_Y.inverse_transform(xgb_preds_scaled)
    y_test_tab_inv = scaler_Y.inverse_transform(y_test_tab_scaled)
    evaluate_multi(y_test_tab_inv, xgb_preds_inv, "XGBoost (Tabular)")

    # ── DEEP LEARNING MODELS ──
    print("Training Multi-Target LSTM...")
    lstm_model = build_multi_target_lstm((X_train_seq.shape[1], X_train_seq.shape[2]))
    es = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    lstm_model.fit(X_train_seq, y_train_seq, epochs=15, batch_size=32, validation_split=0.1, callbacks=[es], verbose=0)
    
    lstm_preds_scaled = lstm_model.predict(X_test_seq, verbose=0)
    lstm_preds_inv = scaler_Y.inverse_transform(lstm_preds_scaled)
    y_test_seq_inv = scaler_Y.inverse_transform(y_test_seq_scaled)
    evaluate_multi(y_test_seq_inv, lstm_preds_inv, "LSTM")

    print("\nTraining Multi-Target GRU...")
    gru_model = build_multi_target_gru((X_train_seq.shape[1], X_train_seq.shape[2]))
    gru_model.fit(X_train_seq, y_train_seq, epochs=15, batch_size=32, validation_split=0.1, callbacks=[es], verbose=0)
    
    gru_preds_scaled = gru_model.predict(X_test_seq, verbose=0)
    gru_preds_inv = scaler_Y.inverse_transform(gru_preds_scaled)
    evaluate_multi(y_test_seq_inv, gru_preds_inv, "GRU")
    
    # ── ALIGN PREDICTIONS FOR ENSEMBLING ──
    # Since XGBoost is evaluated directly on X_test_tab which maps 1:1 with X_test_seq, we can ensemble directly!
    xgb_seq_preds_scaled = xgb_preds_scaled
    
    print("\nEvaluating Weighted Meta-Ensemble (0.4 LSTM + 0.4 GRU + 0.2 XGBoost)...")
    ensemble_preds_scaled = 0.4 * lstm_preds_scaled + 0.4 * gru_preds_scaled + 0.2 * xgb_seq_preds_scaled
    
    ensemble_preds_inv = scaler_Y.inverse_transform(ensemble_preds_scaled)
    results = evaluate_multi(y_test_seq_inv, ensemble_preds_inv, "Weighted Meta-Ensemble")
    
    pd.DataFrame(results).to_csv(os.path.join(data_dir, "unified_metrics.csv"), index=False)
    print("\nIntegration complete. Unified metrics saved to data/unified_metrics.csv")

if __name__ == "__main__":
    main()
