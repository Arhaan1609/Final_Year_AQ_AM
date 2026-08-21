"""
Knee-Aware Model Training
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import *
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
PLOTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "results", "plots"))
SEQ_LEN, EPOCHS, BATCH = 30, 100, 32


def add_knee(df):
    df = df.copy()
    df['total'] = df.groupby('chassis_no')['charge_cycle_count'].transform('max')
    df['post_knee'] = (df['charge_cycle_count'] >= df['knee_cycle']).astype(int)
    df['dist_knee'] = df['knee_cycle'] - df['charge_cycle_count']
    df['norm_dist'] = df['dist_knee'] / (df['total'] + 1)
    df['prox'] = np.exp(-np.abs(df['dist_knee']) / 20)
    df = df.drop(columns=['total'])
    return df


def make_seq(df, feats, seq_len):
    df = df.sort_values(['chassis_no', 'charge_cycle_count']).reset_index(drop=True)
    X, y = df[feats].values.astype(np.float32), df['RUL_to_knee'].values.astype(np.float32)
    post = df['is_post_knee'].values
    
    Xs, ys = [], []
    for chassis in df['chassis_no'].unique():
        mask = (df['chassis_no'] == chassis) & (post == 0)
        idxs = df[mask].index.tolist()
        if len(idxs) <= seq_len:
            continue
        for i in range(len(idxs) - seq_len):
            Xs.append(X[idxs[i]:[i+seq_len])
            ys.append(y[idxs[i+seq_len-1])
    return np.array(Xs, np.float32), np.array(ys, np.float32)


def build_model(shape):
    inp = Input(shape=shape)
    c3 = Conv1D(32, 3, padding='same', activation='relu')(inp)
    c5 = Conv1D(32, 5, padding='same', activation='relu')(inp)
    x = Concatenate()([c3, c5])
    x = BatchNormalization()(x)
    x = Dropout(0.1)(x)
    x = Bidirectional(LSTM(64, return_sequences=True))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    attn = MultiHeadAttention(4, 16)(x, x)
    x = Add()([x, attn])
    x = LayerNormalization()(x)
    x = GlobalAveragePooling1D()(x)
    x = Dense(32, activation='relu')(x)
    x = Dropout(0.2)(x)
    out = Dense(1)(x)
    m = Model(inp, out)
    m.compile(Adam(1e-3), tf.keras.losses.Huber(10.0), metrics=['mae'])
    return m


def main():
    print("="*50)
    print("KNEE TRAINING")
    print("="*50)
    
    df = pd.read_csv(f"{DATA_DIR}/labeled_features.csv")
    df = df[df['is_post_knee'] == 0].copy()
    df = add_knee(df)
    
    np.random.seed(42)
    chassis = df['chassis_no'].unique()
    np.random.shuffle(chassis)
    split = int(0.8 * len(chassis))
    train_df = df[df['chassis_no'].isin(chassis[:split])]
    test_df = df[df['chassis_no'].isin(chassis[split:])]
    
    print(f"Train: {len(train_df)}, Test: {len(test_df)}")
    
    excl = ['chassis_no', 'date', 'timestamp', 'vehicle_no', 'city', 'oem', 'model',
           'source_file', 'cmcdts', 'start_gps', 'end_gps', 'createdAt', 'updatedAt',
           'rts', 'gdts', 'grts', 'vehicle_status', 'drive_mode', 'charge_inlet_mode', 'vmdl',
           'is_post_knee', 'knee_cycle', 'RUL_to_knee']
    
    all_f = [c for c in df.columns if c not in excl and np.issubdtype(df[c].dtype, np.number)]
    no_knee = [c for c in all_f if c not in ['post_knee', 'dist_knee', 'norm_dist', 'prox']]
    
    print(f"With knee: {len(all_f)}, Without: {len(no_knee)}")
    results = []
    
    # WITHOUT
    print("\n[1] WITHOUT knee...")
    Xtr, ytr = make_seq(train_df, no_knee, SEQ_LEN)
    Xte, yte = make_seq(test_df, no_knee, SEQ_LEN)
    print(f"  Seq: {Xtr.shape}")
    yt_log = np.log1p(np.clip(ytr, 0, None))
    ye_log = np.log1p(np.clip(yte, 0, None))
    
    m1 = build_model((Xtr.shape[1], Xtr.shape[2]))
    m1.fit(Xtr, yt_log, epochs=EPOCHS, batch_size=BATCH, validation_split=0.1,
           callbacks=[EarlyStopping(patience=10, restore_best_weights=True)], verbose=0)
    p1 = np.expm1(m1.predict(Xte, verbose=0).flatten())
    r1 = np.sqrt(mean_squared_error(yte, p1))
    r2_1 = r2_score(yte, p1)
    g1 = np.mean(np.abs(p1 - yte) / (yte + 1e-6) * 100 < 15) * 100
    po1 = np.mean(np.abs(p1 - yte) / (yte + 1e-6) * 100 > 30) * 100
    print(f"  RMSE={r1:.2f}, R2={r2_1:.3f}")
    results.append(('Without', r1, r2_1, g1, po1, p1, yte))
    
    # WITH
    print("\n[2] WITH knee...")
    Xtr2, ytr2 = make_seq(train_df, all_f, SEQ_LEN)
    Xte2, yte2 = make_seq(test_df, all_f, SEQ_LEN)
    print(f"  Seq: {Xtr2.shape}")
    yt2_log = np.log1p(np.clip(ytr2, 0, None))
    ye2_log = np.log1p(np.clip(yte2, 0, None))
    
    m2 = build_model((Xtr2.shape[1], Xtr2.shape[2]))
    m2.fit(Xtr2, yt2_log, epochs=EPOCHS, batch_size=BATCH, validation_split=0.1,
           callbacks=[EarlyStopping(patience=10, restore_best_weights=True)], verbose=0)
    p2 = np.expm1(m2.predict(Xte2, verbose=0).flatten())
    r2 = np.sqrt(mean_squared_error(yte2, p2))
    r2_2 = r2_score(yte2, p2)
    g2 = np.mean(np.abs(p2 - yte2) / (yte2 + 1e-6) * 100 < 15) * 100
    po2 = np.mean(np.abs(p2 - yte2) / (yte2 + 1e-6) * 100 > 30) * 100
    print(f"  RMSE={r2:.2f}, R2={r2_2:.3f}")
    results.append(('With', r2, r2_2, g2, po2, p2, yte2))
    
    print("\n" + "="*50)
    print("RESULTS")
    print("="*50)
    for n, rm, r2_, g, po, _, _ in results:
        print(f"{n}: RMSE={rm:.2f}, R2={r2_:.3f}, <15%={g:.1f}%, >30%={po:.1f}%")
    
    # Plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    names = [r[0] for r in results]
    rms = [r[1] for r in results]
    r2s = [r[2] for r in results]
    gs = [r[3] for r in results]
    pos = [r[4] for r in results]
    cols = ['#e74c3c', '#27ae60']
    
    axes[0,0].bar(names, rms, color=cols)
    axes[0,0].set_title('RMSE')
    axes[0,1].bar(names, r2s, color=cols)
    axes[0,1].set_title('R2')
    axes[0,1].axhline(0, color='gray', ls='--')
    axes[1,0].bar(names, gs, color=cols)
    axes[1,0].set_title('<15% Error')
    axes[1,0].set_ylim(0, 40)
    axes[1,1].bar(names, pos, color=cols)
    axes[1,1].set_title('>30% Error')
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/knee_comparison.png")
    print(f"\nSaved: {PLOTS_DIR}/knee_comparison.png")
    
    # Dashboard
    fig = plt.figure(figsize=(14, 10))
    ax1 = fig.add_subplot(2, 3, 1)
    pct = np.abs(p2 - yte2) / (yte2 + 1e-6) * 100
    sz = [np.sum(pct < 5), np.sum((pct >= 5) & (pct < 15)), np.sum((pct >= 15) & (pct < 30)), np.sum(pct >= 30)]
    ax1.pie(sz, colors=['#27ae60', '#3498db', '#f39c12', '#e74c3c'], startangle=90)
    ax1.set_title('Accuracy')
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.scatter(yte2, p2, c=pct, cmap='RdYlGn_r', alpha=0.6)
    m = max(max(yte2), max(p2)) + 5
    ax2.plot([0, m], [0, m], 'k--')
    ax2.set_xlabel('Actual')
    ax2.set_ylabel('Predicted')
    ax2.set_title('Pred vs Actual')
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.axis('off')
    imp = f"Improvement:\nRMSE: {rms[0]-rms[1]:+.2f}\nR2: {r2s[1]-r2s[0]:+.3f}\n<15%: {gs[1]-gs[0]:+.1f}%\n>30%: {pos[0]-pos[1]:+.1f}%"
    ax3.text(0.5, 0.5, imp, transform=ax3.transAxes, fontsize=11, va='center', ha='center',
            bbox=dict(boxstyle='round', fc='#ecf0f1'))
    plt.tight_layout()
    plt.savefig(f"{PLOTS_DIR}/knee_dashboard.png")
    print(f"Saved: {PLOTS_DIR}/knee_dashboard.png")
    print("\nDone!")


if __name__ == "__main__":
    main()