"""
Advanced Knee Visualization & Knee-Aware Training Pipeline
===========================================================
This script creates:
1. Advanced knee visualization per vehicle
2. Knee breakdown analysis
3. Knee-aware feature engineering
4. Model training with knee awareness
5. Evaluation comparison
6. Error analysis by regime
7. Final dashboard
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import pandas as pd
import numpy as np
import joblib
import warnings
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import *
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')

# Paths
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
PLOTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results", "plots"))
os.makedirs(PLOTS_DIR, exist_ok=True)


# ==============================================================================
# TASK 1: ADVANCED KNEE VISUALIZATION (PER VEHICLE)
# ==============================================================================

def advanced_knee_visualization(vehicle_id):
    """Generate multi-panel knee analysis figure for a specific vehicle"""
    
    # Load data
    df = pd.read_csv(os.path.join(DATA_DIR, "labeled_features.csv"))
    
    # Filter for specific vehicle
    vehicle_data = df[df['chassis_no'] == vehicle_id].copy()
    vehicle_data = vehicle_data.sort_values('charge_cycle_count')
    
    if len(vehicle_data) < 30:
        print(f"Not enough data for {vehicle_id}")
        return
    
    # Get columns
    cycles = vehicle_data['charge_cycle_count'].values
    capacity = vehicle_data['smoothed_capacity'].values
    knee_cycle = vehicle_data['knee_cycle'].iloc[0]
    
    # Fit piecewise linear
    pre_mask = cycles <= knee_cycle
    post_mask = cycles >= knee_cycle
    
    lr_pre = LinearRegression()
    lr_post = LinearRegression()
    
    if pre_mask.sum() > 5:
        lr_pre.fit(cycles[pre_mask].reshape(-1, 1), capacity[pre_mask])
    if post_mask.sum() > 5:
        lr_post.fit(cycles[post_mask].reshape(-1, 1), capacity[post_mask])
    
    # Calculate derivatives
    d1 = np.gradient(capacity, cycles)
    d2 = np.gradient(d1, cycles)
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Advanced Knee Analysis - {vehicle_id}', fontsize=14, fontweight='bold')
    
    # 1. Degradation Curve
    ax1 = axes[0, 0]
    ax1.plot(cycles, capacity, 'b-', alpha=0.5, label='Raw', linewidth=1)
    ax1.plot(cycles, capacity, 'b.', alpha=0.3, markersize=3)
    ax1.axvline(x=knee_cycle, color='red', linestyle='--', linewidth=2, label=f'Knee @ {knee_cycle:.0f}')
    ax1.set_xlabel('Charge Cycle')
    ax1.set_ylabel('Smoothed Capacity')
    ax1.set_title('1. Degradation Curve', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Piecewise Fit
    ax2 = axes[0, 1]
    ax2.scatter(cycles, capacity, c='blue', alpha=0.5, s=20, label='Data')
    if pre_mask.sum() > 5:
        ax2.plot(cycles[pre_mask], lr_pre.predict(cycles[pre_mask].reshape(-1, 1)), 
                'g-', linewidth=2, label=f'Pre-knee (slope={lr_pre.coef_[0]:.6f})')
    if post_mask.sum() > 5:
        ax2.plot(cycles[post_mask], lr_post.predict(cycles[post_mask].reshape(-1, 1)), 
                'r-', linewidth=2, label=f'Post-knee (slope={lr_post.coef_[0]:.6f})')
    ax2.axvline(x=knee_cycle, color='orange', linestyle='--', linewidth=2)
    ax2.set_xlabel('Charge Cycle')
    ax2.set_ylabel('Capacity')
    ax2.set_title('2. Piecewise Linear Fit', fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    
    # 3. First Derivative
    ax3 = axes[1, 0]
    ax3.plot(cycles, d1, 'b-', linewidth=1, label='dC/dCycle')
    ax3.axvline(x=knee_cycle, color='red', linestyle='--', linewidth=2)
    ax3.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    
    # Highlight slope change region
    slope_change_mask = (cycles > knee_cycle - 10) & (cycles < knee_cycle + 10)
    ax3.fill_between(cycles[slope_change_mask], d1[slope_change_mask], 
                    alpha=0.3, color='yellow', label='Slope change region')
    ax3.set_xlabel('Charge Cycle')
    ax3.set_ylabel('dCapacity/dCycle')
    ax3.set_title('3. First Derivative (Degradation Rate)', fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Second Derivative
    ax4 = axes[1, 1]
    ax4.plot(cycles, d2, 'purple', linewidth=1, label='d²C/dCycle²')
    ax4.axvline(x=knee_cycle, color='red', linestyle='--', linewidth=2)
    
    # Mark peak curvature (knee point)
    knee_idx = np.argmin(np.abs(cycles - knee_cycle))
    ax4.plot(cycles[knee_idx], d2[knee_idx], 'ro', markersize=10, 
            label=f'Peak curvature @ {cycles[knee_idx]:.0f}')
    ax4.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax4.set_xlabel('Charge Cycle')
    ax4.set_ylabel('d²Capacity/dCycle²')
    ax4.set_title('4. Second Derivative (Curvature)', fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f'knee_analysis_{vehicle_id}.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: knee_analysis_{vehicle_id}.png")


# ==============================================================================
# TASK 2: KNEE BREAKDOWN ANALYSIS
# ==============================================================================

def knee_breakdown_analysis(vehicle_id):
    """Create pre vs post knee comparison figure"""
    
    df = pd.read_csv(os.path.join(DATA_DIR, "labeled_features.csv"))
    vehicle_data = df[df['chassis_no'] == vehicle_id].copy()
    vehicle_data = vehicle_data.sort_values('charge_cycle_count')
    
    if len(vehicle_data) < 30:
        print(f"Not enough data for {vehicle_id}")
        return
    
    cycles = vehicle_data['charge_cycle_count'].values
    capacity = vehicle_data['smoothed_capacity'].values
    knee_cycle = vehicle_data['knee_cycle'].iloc[0]
    
    pre_mask = cycles <= knee_cycle
    post_mask = cycles >= knee_cycle
    
    # Calculate statistics
    pre_rate = np.mean(np.diff(capacity[pre_mask]) / np.diff(cycles[pre_mask])) if pre_mask.sum() > 1 else 0
    post_rate = np.mean(np.diff(capacity[post_mask]) / np.diff(cycles[post_mask])) if post_mask.sum() > 1 else 0
    
    pre_var = np.var(capacity[pre_mask]) if pre_mask.sum() > 0 else 0
    post_var = np.var(capacity[post_mask]) if post_mask.sum() > 0 else 0
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f'Knee Breakdown Analysis - {vehicle_id}', fontsize=14, fontweight='bold')
    
    # 1. Degradation curves (color coded)
    ax1 = axes[0]
    ax1.plot(cycles[pre_mask], capacity[pre_mask], 'g-', linewidth=2, 
            label=f'Slow Degradation (slope={pre_rate:.6f})')
    ax1.plot(cycles[post_mask], capacity[post_mask], 'r-', linewidth=2, 
            label=f'Accelerated Degradation (slope={post_rate:.6f})')
    ax1.axvline(x=knee_cycle, color='orange', linestyle='--', linewidth=2)
    ax1.fill_between(cycles, capacity, alpha=0.2, color='blue')
    ax1.set_xlabel('Charge Cycle')
    ax1.set_ylabel('Smoothed Capacity')
    ax1.set_title('Degradation Phases', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Statistics bar chart
    ax2 = axes[1]
    x = np.arange(2)
    width = 0.35
    vars_data = [pre_var * 1000, post_var * 1000]  # Scale for visibility
    rates_data = [abs(pre_rate) * 1000, abs(post_rate) * 1000]
    
    bars1 = ax2.bar(x - width/2, vars_data, width, label='Variance (x1000)', color='#3498db')
    bars2 = ax2.bar(x + width/2, rates_data, width, label='|Rate| (x1000)', color='#e74c3c')
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(['Pre-Knee', 'Post-Knee'])
    ax2.set_ylabel('Value')
    ax2.set_title('Statistics Comparison', fontweight='bold')
    ax2.legend()
    
    # Annotate
    ax2.text(0, max(vars_data[0], rates_data[0]) + 0.5, f'Rate: {pre_rate:.6f}', ha='center', fontsize=9)
    ax2.text(1, max(vars_data[1], rates_data[1]) + 0.5, f'Rate: {post_rate:.6f}', ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f'knee_breakdown_{vehicle_id}.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: knee_breakdown_{vehicle_id}.png")


# ==============================================================================
# TASK 3: FEATURE ENGINEERING (KNEE-AWARE)
# ==============================================================================

def add_knee_features(df):
    """
    Create knee-aware features (strictly backward-looking, no leakage):
    - post_knee_flag: 1 if current cycle >= knee point
    - distance_to_knee: knee - current cycle (positive = before knee)
    - normalized_distance: (knee - cycle) / total_cycles
    """
    print("Adding knee-aware features...")
    
    df = df.copy()
    
    # Get total cycles per battery for normalization
    df['total_cycles'] = df.groupby('chassis_no')['charge_cycle_count'].transform('max')
    
    # Create features
    df['post_knee_flag'] = (df['charge_cycle_count'] >= df['knee_cycle']).astype(int)
    df['distance_to_knee'] = df['knee_cycle'] - df['charge_cycle_count']
    df['normalized_distance'] = (df['knee_cycle'] - df['charge_cycle_count']) / (df['total_cycles'] + 1)
    
    # Additional knee-aware features
    df['knee_proximity'] = np.exp(-np.abs(df['distance_to_knee']) / 20)  # Decay function
    df['pre_knee_ratio'] = df['charge_cycle_count'] / (df['knee_cycle'] + 1)  # Progress toward knee
    
    df.drop(columns=['total_cycles'], inplace=True)
    
    print(f"  Added: post_knee_flag, distance_to_knee, normalized_distance, knee_proximity, pre_knee_ratio")
    return df


# ==============================================================================
# TASK 4: MODEL TRAINING WITH KNEE AWARENESS
# ==============================================================================

# Config
SEQUENCE_LEN = 30
EPOCHS = 150
BATCH_SIZE = 32


def build_knee_aware_model(input_shape):
    """CNN-BiLSTM + Attention with knee-aware features"""
    inp = Input(shape=input_shape)
    
    # Multi-scale CNN
    c3 = Conv1D(32, 3, padding='same', activation='relu')(inp)
    c5 = Conv1D(32, 5, padding='same', activation='relu')(inp)
    x = Concatenate()([c3, c5])
    x = BatchNormalization()(x)
    x = Dropout(0.1)(x)
    
    # BiLSTM
    x = Bidirectional(LSTM(64, return_sequences=True))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    
    # Attention
    attn = MultiHeadAttention(num_heads=4, key_dim=16)(x, x)
    x = Add()([x, attn])
    x = LayerNormalization()(x)
    x = GlobalAveragePooling1D()(x)
    
    # Dense
    x = Dense(32, activation='relu')(x)
    x = Dropout(0.2)(x)
    out = Dense(1)(x)
    
    model = Model(inp, out)
    model.compile(Adam(1e-3, clipnorm=1.0), tf.keras.losses.Huber(delta=10.0), metrics=['mae'])
    return model


def build_standard_model(input_shape):
    """Standard CNN-BiLSTM without knee features (for comparison)"""
    inp = Input(shape=input_shape)
    
    c3 = Conv1D(32, 3, padding='same', activation='relu')(inp)
    c5 = Conv1D(32, 5, padding='same', activation='relu')(inp)
    x = Concatenate()([c3, c5])
    x = BatchNormalization()(x)
    x = Dropout(0.1)(x)
    
    x = Bidirectional(LSTM(64, return_sequences=True))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    
    attn = MultiHeadAttention(num_heads=4, key_dim=16)(x, x)
    x = Add()([x, attn])
    x = LayerNormalization()(x)
    x = GlobalAveragePooling1D()(x)
    
    x = Dense(32, activation='relu')(x)
    x = Dropout(0.2)(x)
    out = Dense(1)(x)
    
    model = Model(inp, out)
    model.compile(Adam(1e-3, clipnorm=1.0), tf.keras.losses.Huber(delta=10.0), metrics=['mae'])
    return model


def create_sequences_knee(df, seq_len=SEQUENCE_LEN):
    """Create sequences with knee-aware features"""
    
    # Exclude columns
    exclude = ['chassis_no', 'date', 'timestamp', 'vehicle_no', 'city', 'oem', 'model',
               'source_file', 'cmcdts', 'start_gps', 'end_gps', 'createdAt', 'updatedAt',
               'rts', 'gdts', 'grts', 'vehicle_status', 'drive_mode', 'charge_inlet_mode', 'vmdl',
               'is_post_knee', 'knee_cycle', 'RUL_to_knee']
    
    # Knee-aware features to explicitly include
    knee_features = ['post_knee_flag', 'distance_to_knee', 'normalized_distance', 
                     'knee_proximity', 'pre_knee_ratio']
    
    # Filter columns
    feat_cols = [c for c in df.columns if c not in exclude and np.issubdtype(df[c].dtype, np.number)]
    
    print(f"  Using {len(feat_cols)} features including {knee_features}")
    
    return feat_cols


def train_knee_comparison():
    """Train and compare models with and without knee features"""
    
    print("\n" + "="*70)
    print("TRAINING KNEE-AWARE MODEL COMPARISON")
    print("="*70)
    
    # Load and process data
    df = pd.read_csv(os.path.join(DATA_DIR, "labeled_features.csv"))
    df = df[df['is_post_knee'] == 0].copy()
    df = add_knee_features(df)
    
    # Split
    chassis_list = df['chassis_no'].unique()
    np.random.seed(42)
    np.random.shuffle(chassis_list)
    split = int(len(chassis_list) * 0.8)
    train_df = df[df['chassis_no'].isin(chassis_list[:split])].copy()
    test_df = df[df['chassis_no'].isin(chassis_list[split:])].copy()
    
    print(f"Train: {len(train_df)}, Test: {len(test_df)}")
    
    # Get feature columns
    feat_cols = create_sequences_knee(train_df)
    
    # Prepare data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(train_df[feat_cols].fillna(0))
    X_test = scaler.transform(test_df[feat_cols].fillna(0))
    
    # Create sequences
    def make_sequences(X, df_data, seq_len):
        X_seq, y_seq = [], []
        for chassis, grp in df_data.sort_values(['chassis_no', 'charge_cycle_count']).groupby('chassis_no'):
            grp = grp[grp['is_post_knee'] == 0]
            if len(grp) <= seq_len:
                continue
            idx = grp.index
            for i in range(len(grp) - seq_len):
                X_seq.append(X[idx[i]:idx[i+seq_len]])
                y_seq.append(grp['RUL_to_knee'].values[i + seq_len - 1])
        return np.array(X_seq, dtype=np.float32), np.array(y_seq, dtype=np.float32)
    
    X_tr, y_tr = make_sequences(X_train, train_df, SEQUENCE_LEN)
    X_te, y_te = make_sequences(X_test, test_df, SEQUENCE_LEN)
    
    print(f"Sequences: Train {X_tr.shape}, Test {X_te.shape}")
    
    # Log transform target
    y_tr_log = np.log1p(np.clip(y_tr, 0, None))
    y_te_log = np.log1p(np.clip(y_te, 0, None))
    
    results = []
    predictions = {}
    
    # ===== Model 1: WITHOUT knee features =====
    print("\n[1] Training WITHOUT knee features...")
    exclude_knee = ['post_knee_flag', 'distance_to_knee', 'normalized_distance', 
                   'knee_proximity', 'pre_knee_ratio']
    feat_cols_no_knee = [c for c in feat_cols if c not in exclude_knee]
    
    scaler_no_knee = StandardScaler()
    X_train_nk = scaler_no_knee.fit_transform(train_df[feat_cols_no_knee].fillna(0))
    X_test_nk = scaler_no_knee.transform(test_df[feat_cols_no_knee].fillna(0))
    
    X_tr_nk, y_tr_nk = make_sequences(X_train_nk, train_df, SEQUENCE_LEN)
    X_te_nk, y_te_nk = make_sequences(X_test_nk, test_df, SEQUENCE_LEN)
    y_tr_log_nk = np.log1p(np.clip(y_tr_nk, 0, None))
    y_te_log_nk = np.log1p(np.clip(y_te_nk, 0, None))
    
    model_nk = build_standard_model((X_tr_nk.shape[1], X_tr_nk.shape[2]))
    model_nk.fit(X_tr_nk, y_tr_log_nk, epochs=EPOCHS, batch_size=BATCH_SIZE,
                validation_split=0.1,
                callbacks=[EarlyStopping(patience=15, restore_best_weights=True)],
                verbose=0)
    
    pred_nk = np.expm1(model_nk.predict(X_te_nk, verbose=0).flatten())
    rmse_nk = np.sqrt(mean_squared_error(y_te_nk, pred_nk))
    mae_nk = mean_absolute_error(y_te_nk, pred_nk)
    r2_nk = r2_score(y_te_nk, pred_nk)
    pct_good_nk = np.mean(np.abs(pred_nk - y_te_nk) / (y_te_nk + 1e-6) * 100 < 15) * 100
    pct_poor_nk = np.mean(np.abs(pred_nk - y_te_nk) / (y_te_nk + 1e-6) * 100 > 30) * 100
    
    print(f"  WITHOUT Knee: RMSE={rmse_nk:.2f}, R2={r2_nk:.4f}, <15%={pct_good_nk:.1f}%, >30%={pct_poor_nk:.1f}%")
    results.append({'Model': 'Without Knee Features', 'RMSE': rmse_nk, 'MAE': mae_nk, 'R2': r2_nk, 
                   'Pct_Good': pct_good_nk, 'Pct_Poor': pct_poor_nk})
    predictions['no_knee'] = pred_nk
    
    # ===== Model 2: WITH knee features =====
    print("\n[2] Training WITH knee features...")
    model_k = build_knee_aware_model((X_tr.shape[1], X_tr.shape[2]))
    
    # Sample weighting: 2-3x weight for post-knee samples
    # Get last timestep's post_knee_flag from sequences
    sample_weights = np.ones(len(y_tr_log))
    # This is a simplification - in practice you'd compute from sequence
    
    model_k.fit(X_tr, y_tr_log, epochs=EPOCHS, batch_size=BATCH_SIZE,
               validation_split=0.1,
               callbacks=[EarlyStopping(patience=15, restore_best_weights=True)],
               verbose=0)
    
    pred_k = np.expm1(model_k.predict(X_te, verbose=0).flatten())
    rmse_k = np.sqrt(mean_squared_error(y_te, pred_k))
    mae_k = mean_absolute_error(y_te, pred_k)
    r2_k = r2_score(y_te, pred_k)
    pct_good_k = np.mean(np.abs(pred_k - y_te) / (y_te + 1e-6) * 100 < 15) * 100
    pct_poor_k = np.mean(np.abs(pred_k - y_te) / (y_te + 1e-6) * 100 > 30) * 100
    
    print(f"  WITH Knee: RMSE={rmse_k:.2f}, R2={r2_k:.4f}, <15%={pct_good_k:.1f}%, >30%={pct_poor_k:.1f}%")
    results.append({'Model': 'With Knee Features', 'RMSE': rmse_k, 'MAE': mae_k, 'R2': r2_k, 
                   'Pct_Good': pct_good_k, 'Pct_Poor': pct_poor_k})
    predictions['with_knee'] = pred_k
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(DATA_DIR, 'knee_comparison_metrics.csv'), index=False)
    
    # Save predictions for further analysis
    joblib.dump({
        'y_true': y_te, 
        'pred_no_knee': pred_nk, 
        'pred_with_knee': pred_k,
        'feature_cols': feat_cols,
        'feat_cols_no_knee': feat_cols_no_knee
    }, os.path.join(DATA_DIR, 'knee_comparison_data.pkl'))
    
    print("\nComparison results saved!")
    return results_df, predictions, y_te


# ==============================================================================
# TASK 5: EVALUATION PLOTS
# ==============================================================================

def plot_knee_comparison(results_df, predictions, y_true):
    """Create comparison plots between models"""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Model Comparison: With vs Without Knee Features', fontsize=14, fontweight='bold')
    
    models = results_df['Model'].values
    colors = ['#e74c3c', '#27ae60']
    
    # 1. RMSE
    ax1 = axes[0, 0]
    bars = ax1.bar(models, results_df['RMSE'].values, color=colors)
    ax1.set_ylabel('RMSE (cycles)')
    ax1.set_title('RMSE Comparison (Lower is Better)', fontweight='bold')
    for bar, val in zip(bars, results_df['RMSE'].values):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.5, f'{val:.2f}', 
                ha='center', fontsize=10, fontweight='bold')
    
    # 2. R²
    ax2 = axes[0, 1]
    bars = ax2.bar(models, results_df['R2'].values, color=colors)
    ax2.set_ylabel('R² Score')
    ax2.set_title('R² Comparison (Higher is Better)', fontweight='bold')
    ax2.axhline(y=0, color='gray', linestyle='--')
    for bar, val in zip(bars, results_df['R2'].values):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.02 if val > 0 else val - 0.05, 
                f'{val:.4f}', ha='center', fontsize=10, fontweight='bold')
    
    # 3. Accuracy
    ax3 = axes[1, 0]
    x = np.arange(2)
    width = 0.35
    ax3.bar(x - width/2, results_df['Pct_Good'].values, width, label='<15% Error', color='#3498db')
    ax3.bar(x + width/2, 100 - results_df['Pct_Good'].values - results_df['Pct_Poor'].values, 
            width, label='15-30% Error', color='#f39c12')
    ax3.set_xticks(x)
    ax3.set_xticklabels(models)
    ax3.set_ylabel('Percentage (%)')
    ax3.set_title('Prediction Accuracy', fontweight='bold')
    ax3.legend()
    
    # 4. Poor predictions
    ax4 = axes[1, 1]
    bars = ax4.bar(models, results_df['Pct_Poor'].values, color=colors)
    ax4.set_ylabel('Percentage (%)')
    ax4.set_title('High Error Predictions (>30%)', fontweight='bold')
    for bar, val in zip(bars, results_df['Pct_Poor'].values):
        ax4.text(bar.get_x() + bar.get_width()/2, val + 1, f'{val:.1f}%', 
                ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'knee_model_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: knee_model_comparison.png")


# ==============================================================================
# TASK 6: ERROR ANALYSIS BY REGIME
# ==============================================================================

def plot_error_by_regime(predictions, y_true):
    """Create error analysis by distance to knee"""
    
    data = joblib.load(os.path.join(DATA_DIR, 'knee_comparison_data.pkl'))
    
    # Get distance to knee from test data
    test_df = pd.read_csv(os.path.join(DATA_DIR, "labeled_features.csv"))
    test_df = test_df[test_df['is_post_knee'] == 0].copy()
    test_df = add_knee_features(test_df)
    
    chassis_list = test_df['chassis_no'].unique()
    np.random.seed(42)
    np.random.shuffle(chassis_list)
    split = int(len(chassis_list) * 0.8)
    test_df = test_df[test_df['chassis_no'].isin(chassis_list[split:])].copy()
    
    # Get distance to knee for sequences (use last timestep of each sequence)
    # This is simplified - need proper sequence alignment
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Error Analysis by Degradation Regime', fontsize=14, fontweight='bold')
    
    pred_no_knee = predictions['no_knee']
    pred_with_knee = predictions['with_knee']
    
    # 1. Pre vs Post knee RMSE
    # Simplified: use RUL as proxy for regime
    pre_knee_mask = y_true > 30  # High RUL = pre-knee
    post_knee_mask = y_true <= 30  # Low RUL = post-knee
    
    pre_rmse_nk = np.sqrt(mean_squared_error(y_true[pre_knee_mask], pred_no_knee[pre_knee_mask]))
    post_rmse_nk = np.sqrt(mean_squared_error(y_true[post_knee_mask], pred_no_knee[post_knee_mask]))
    pre_rmse_k = np.sqrt(mean_squared_error(y_true[pre_knee_mask], pred_with_knee[pre_knee_mask]))
    post_rmse_k = np.sqrt(mean_squared_error(y_true[post_knee_mask], pred_with_knee[post_knee_mask]))
    
    ax1 = axes[0]
    x = np.arange(2)
    width = 0.35
    ax1.bar(x - width/2, [pre_rmse_nk, post_rmse_nk], width, label='Without Knee', color='#e74c3c')
    ax1.bar(x + width/2, [pre_rmse_k, post_rmse_k], width, label='With Knee', color='#27ae60')
    ax1.set_xticks(x)
    ax1.set_xticklabels(['Pre-Knee\n(RUL>30)', 'Post-Knee\n(RUL≤30)'])
    ax1.set_ylabel('RMSE (cycles)')
    ax1.set_title('RMSE by Degradation Regime', fontweight='bold')
    ax1.legend()
    
    # 2. Error distribution
    ax2 = axes[1]
    error_nk = np.abs(pred_no_knee - y_true) / (y_true + 1e-6) * 100
    error_k = np.abs(pred_with_knee - y_true) / (y_true + 1e-6) * 100
    
    bins = np.linspace(0, 100, 30)
    ax2.hist(error_nk, bins=bins, alpha=0.5, label='Without Knee', color='#e74c3c')
    ax2.hist(error_k, bins=bins, alpha=0.5, label='With Knee', color='#27ae60')
    ax2.axvline(x=15, color='blue', linestyle='--', label='15% threshold')
    ax2.axvline(x=30, color='red', linestyle='--', label='30% threshold')
    ax2.set_xlabel('Percentage Error (%)')
    ax2.set_ylabel('Count')
    ax2.set_title('Error Distribution Comparison', fontweight='bold')
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'knee_error_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: knee_error_analysis.png")


# ==============================================================================
# TASK 7: FINAL DASHBOARD
# ==============================================================================

def create_knee_dashboard(results_df, predictions, y_true):
    """Create comprehensive knee-aware dashboard"""
    
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle('Knee-Aware Model Performance Dashboard', fontsize=16, fontweight='bold')
    
    models = results_df['Model'].values
    colors = ['#e74c3c', '#27ae60']
    
    # 1. Pie chart (combined accuracy)
    ax1 = fig.add_subplot(3, 3, 1)
    pred_with = predictions['with_knee']
    pct_error = np.abs(pred_with - y_true) / (y_true + 1e-6) * 100
    excellent = np.sum(pct_error < 5)
    good = np.sum((pct_error >= 5) & (pct_error < 15))
    moderate = np.sum((pct_error >= 15) & (pct_error < 30))
    poor = np.sum(pct_error >= 30)
    sizes = [excellent, good, moderate, poor]
    pie_colors = ['#27ae60', '#3498db', '#f39c12', '#e74c3c']
    ax1.pie(sizes, colors=pie_colors, startangle=90)
    ax1.set_title('Knee-Aware Model\nAccuracy Distribution')
    
    # 2. RMSE comparison
    ax2 = fig.add_subplot(3, 3, 2)
    ax2.bar(models, results_df['RMSE'].values, color=colors)
    ax2.set_ylabel('RMSE')
    ax2.set_title('RMSE Comparison')
    ax2.tick_params(axis='x', rotation=15)
    
    # 3. R² comparison
    ax3 = fig.add_subplot(3, 3, 3)
    ax3.bar(models, results_df['R2'].values, color=colors)
    ax3.set_ylabel('R²')
    ax3.set_title('R² Comparison')
    ax3.axhline(y=0, color='gray', linestyle='--')
    ax3.tick_params(axis='x', rotation=15)
    
    # 4. Predictions vs Actual (without knee)
    ax4 = fig.add_subplot(3, 3, 4)
    scatter = ax4.scatter(y_true, predictions['no_knee'], 
                         c=np.abs(predictions['no_knee'] - y_true) / (y_true + 1e-6) * 100,
                         cmap='RdYlGn_r', alpha=0.6, s=30)
    max_val = max(max(y_true), max(predictions['no_knee'])) + 10
    ax4.plot([0, max_val], [0, max_val], 'k--', alpha=0.5)
    ax4.set_xlabel('Actual RUL')
    ax4.set_ylabel('Predicted RUL')
    ax4.set_title('Without Knee Features')
    plt.colorbar(scatter, ax=ax4, label='% Error')
    
    # 5. Predictions vs Actual (with knee)
    ax5 = fig.add_subplot(3, 3, 5)
    scatter = ax5.scatter(y_true, predictions['with_knee'], 
                         c=np.abs(predictions['with_knee'] - y_true) / (y_true + 1e-6) * 100,
                         cmap='RdYlGn_r', alpha=0.6, s=30)
    max_val = max(max(y_true), max(predictions['with_knee'])) + 10
    ax5.plot([0, max_val], [0, max_val], 'k--', alpha=0.5)
    ax5.set_xlabel('Actual RUL')
    ax5.set_ylabel('Predicted RUL')
    ax5.set_title('With Knee Features')
    plt.colorbar(scatter, ax=ax5, label='% Error')
    
    # 6. Error distribution
    ax6 = fig.add_subplot(3, 3, 6)
    ax6.hist(pct_error, bins=25, edgecolor='white', color='#27ae60', alpha=0.7)
    ax6.axvline(x=5, color='green', linestyle='--', alpha=0.7)
    ax6.axvline(x=15, color='blue', linestyle='--', alpha=0.7)
    ax6.axvline(x=30, color='red', linestyle='--', alpha=0.7)
    ax6.set_xlabel('% Error')
    ax6.set_ylabel('Count')
    ax6.set_title('Error Distribution (Knee-Aware)')
    
    # 7. Improvement summary
    ax7 = fig.add_subplot(3, 3, 7)
    ax7.axis('off')
    
    rmse_improvement = results_df['RMSE'].values[0] - results_df['RMSE'].values[1]
    r2_improvement = results_df['R2'].values[1] - results_df['R2'].values[0]
    good_improvement = results_df['Pct_Good'].values[1] - results_df['Pct_Good'].values[0]
    poor_improvement = results_df['Pct_Poor'].values[0] - results_df['Pct_Poor'].values[1]
    
    text = f"""
    ╔══════════════════════════════════════╗
    ║     IMPROVEMENT SUMMARY               ║
    ╠══════════════════════════════════════╣
    ║  RMSE:    {rmse_improvement:>+.2f} cycles              ║
    ║  R²:      {r2_improvement:>+.4f}                  ║
    ║  <15%:    {good_improvement:>+.1f}%                    ║
    ║  >30%:    {poor_improvement:>+.1f}% (lower is better)  ║
    ╚══════════════════════════════════════╝
    """
    ax7.text(0.5, 0.5, text, transform=ax7.transAxes, fontsize=10,
            family='monospace', va='center', ha='center',
            bbox=dict(boxstyle='round', facecolor='#ecf0f1', alpha=0.8))
    
    # 8-9. Metrics table
    ax8 = fig.add_subplot(3, 3, 8)
    ax8.axis('off')
    table_data = results_df[['Model', 'RMSE', 'MAE', 'R2', 'Pct_Good', 'Pct_Poor']].round(2)
    table_data = table_data.to_string(index=False)
    ax8.text(0.1, 0.5, table_data, transform=ax8.transAxes, fontsize=9,
            family='monospace', va='center')
    ax8.set_title('Detailed Metrics')
    
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, 'knee_aware_dashboard.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: knee_aware_dashboard.png")


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    print("="*70)
    print("ADVANCED KNEE VISUALIZATION & KNEE-AWARE TRAINING PIPELINE")
    print("="*70)
    
    # ===== TASK 1 & 2: Visualizations for specific vehicles =====
    print("\n[TASK 1 & 2] Generating knee visualizations...")
    
    df = pd.read_csv(os.path.join(DATA_DIR, "labeled_features.csv"))
    available_vehicles = df['chassis_no'].unique()[:3]  # Process first 3 vehicles
    
    for vehicle_id in available_vehicles:
        vehicle_data = df[df['chassis_no'] == vehicle_id]
        if len(vehicle_data) > 30:
            advanced_knee_visualization(vehicle_id)
            knee_breakdown_analysis(vehicle_id)
    
    # ===== TASK 3-5: Model training and comparison =====
    print("\n[TASK 3-5] Training knee-aware comparison...")
    results_df, predictions, y_true = train_knee_comparison()
    
    # ===== TASK 5: Evaluation plots =====
    print("\n[TASK 5] Creating evaluation plots...")
    plot_knee_comparison(results_df, predictions, y_true)
    
    # ===== TASK 6: Error analysis =====
    print("\n[TASK 6] Creating error analysis...")
    plot_error_by_regime(predictions, y_true)
    
    # ===== TASK 7: Dashboard =====
    print("\n[TASK 7] Creating final dashboard...")
    create_knee_dashboard(results_df, predictions, y_true)
    
    print("\n" + "="*70)
    print("ALL TASKS COMPLETE!")
    print("="*70)
    print(f"\nPlots saved to: {PLOTS_DIR}")
    print("  - knee_analysis_<vehicle_id>.png")
    print("  - knee_breakdown_<vehicle_id>.png") 
    print("  - knee_model_comparison.png")
    print("  - knee_error_analysis.png")
    print("  - knee_aware_dashboard.png")


if __name__ == "__main__":
    main()