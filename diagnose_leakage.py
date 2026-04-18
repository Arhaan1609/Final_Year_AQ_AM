import pandas as pd
import numpy as np
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROC = r'c:\Final_Year_Project_1\processed_data'

TASKS = [
    ('features_soc.csv',     'soc',               'SOC'),
    ('features_soh.csv',     'soh',               'SOH'),
    ('features_rul.csv',     'rul_proxy',         'RUL'),
    ('features_mileage.csv', 'mileage_per_charge','Mileage'),
]

EXCLUDE = ['vehicle_no','chassis_no','imei','timestamp','start_time','end_time',
           'source_file','gps','start_gps','end_gps','_id','oem_model','oem','model',
           'alert_type','drive_mode','vehicle_status','city','duration','vehicle_no.1']

print("=" * 65)
print("  DATA LEAKAGE & ACCURACY INVESTIGATION")
print("=" * 65)

for fname, target, task in TASKS:
    path = os.path.join(PROC, fname)
    if not os.path.exists(path):
        print(f"\n[SKIP] {fname} not found")
        continue

    df = pd.read_csv(path, low_memory=False, nrows=10000)
    df = df.replace([np.inf, -np.inf], np.nan)

    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    feature_cols = [c for c in num_cols
                    if c != target and c not in EXCLUDE]

    print(f"\n{'='*65}")
    print(f"  TASK: {task}  |  target={target}")
    print(f"  Rows: {len(df):,}  |  Features: {len(feature_cols)}")
    print(f"  All feature columns: {feature_cols}")

    if target not in df.columns:
        print(f"  [!] Target '{target}' not found in columns!")
        continue

    # Target stats
    t = df[target].dropna()
    print(f"\n  Target '{target}' stats:")
    print(f"    mean={t.mean():.3f}  std={t.std():.3f}  "
          f"min={t.min():.3f}  max={t.max():.3f}")
    print(f"    unique values: {t.nunique()}  |  range: {t.max()-t.min():.3f}")

    # Pearson correlations
    df_sub = df[feature_cols + [target]].dropna()
    if len(df_sub) < 10:
        print("  Too few rows for correlation")
        continue

    corrs = df_sub.corr()[target].drop(target).abs().sort_values(ascending=False)
    print(f"\n  TOP correlations with [{target}]:")
    for feat, val in corrs.head(12).items():
        flag = " <<< LEAKAGE?" if val > 0.99 else (" *** HIGH" if val > 0.9 else "")
        print(f"    {feat:<38} r={val:.4f}{flag}")

    # Check if any feature name contains the target name (common leakage pattern)
    print(f"\n  Features that CONTAIN the target name '{target}':")
    leaky = [f for f in feature_cols if target.lower().replace('_proxy','') in f.lower()]
    if leaky:
        for f in leaky:
            print(f"    *** {f}  <-- LIKELY LEAKAGE")
    else:
        print("    None")

    # Check for rolling/lag features of target
    print(f"\n  Rolling / lag features of target:")
    rolling = [f for f in feature_cols if 'rolling' in f.lower() or 'lag' in f.lower()]
    for f in rolling:
        r = abs(df_sub[f].corr(df_sub[target]))
        print(f"    {f:<38} r={r:.4f}")

print("\n" + "="*65)
print("  SUMMARY: Look for r > 0.99 or feature names matching target.")
print("  These cause near-perfect R2 scores.")
print("="*65)
