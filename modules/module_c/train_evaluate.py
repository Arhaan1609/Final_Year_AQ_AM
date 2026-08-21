import pandas as pd
import numpy as np
import os
import joblib
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# ── Config ───────────────────────────────────────────────────────────────
LOG_TARGET = True   # log1p-transform RUL_to_knee to fix underprediction bias
# ─────────────────────────────────────────────────────────────────────────

def prepare_data(df):
    """
    Chassis-level train/test split.
    FIX 1: StandardScaler is fit on TRAIN data only — no data leakage.
    FIX 2: RUL_to_knee is explicitly excluded from features (was being scaled before).
    FIX 3: Optional log1p transform on target to remove underprediction bias.
    """
    print("Preparing data...")
    df_pre = df[df['is_post_knee'] == 0].copy()

    unique_chassis = df_pre['chassis_no'].unique().tolist()
    np.random.seed(42)
    np.random.shuffle(unique_chassis)

    split_idx     = int(len(unique_chassis) * 0.8)
    train_chassis = unique_chassis[:split_idx]
    test_chassis  = unique_chassis[split_idx:]

    train_df = df_pre[df_pre['chassis_no'].isin(train_chassis)]
    test_df  = df_pre[df_pre['chassis_no'].isin(test_chassis)]

    # Exclude identifiers AND the target from the feature set
    exclude_cols = [
        'chassis_no', 'date', 'timestamp', 'vehicle_no', 'city', 'oem', 'model',
        'source_file', 'cmcdts', 'start_gps', 'end_gps', 'createdAt', 'updatedAt',
        'rts', 'gdts', 'grts', 'vehicle_status', 'drive_mode', 'charge_inlet_mode', 'vmdl',
        'is_post_knee', 'knee_cycle',
        'RUL_to_knee'   # ← CRITICAL: target must not be a feature
    ]

    features = [col for col in train_df.columns if col not in exclude_cols]

    X_train_raw = train_df[features].fillna(0).select_dtypes(include=[np.number])
    X_test_raw  = test_df[features].fillna(0).select_dtypes(include=[np.number])
    X_train_raw, X_test_raw = X_train_raw.align(X_test_raw, join='left', axis=1, fill_value=0)

    # Raw targets (in original cycle units)
    y_train_raw = train_df['RUL_to_knee'].values
    y_test_raw  = test_df['RUL_to_knee'].values

    # FIX 1: Scale X using ONLY train statistics
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_test  = scaler.transform(X_test_raw)          # transform only — no fit!
    joblib.dump(scaler, 'feature_scaler.pkl')

    # FIX 3: Log-transform target to reduce right-skew and underprediction bias
    if LOG_TARGET:
        y_train = np.log1p(np.clip(y_train_raw, 0, None))
        y_test  = np.log1p(np.clip(y_test_raw,  0, None))
    else:
        y_train, y_test = y_train_raw, y_test_raw

    print(f"Train: {len(X_train)}, Test: {len(X_test)}, Features: {X_train_raw.shape[1]}")
    print(f"Target range (raw) — Train: [{y_train_raw.min():.1f}, {y_train_raw.max():.1f}]  "
          f"Test: [{y_test_raw.min():.1f}, {y_test_raw.max():.1f}]")

    return X_train, X_test, y_train, y_test, y_train_raw, y_test_raw, X_train_raw.columns.tolist()

def inv(y):
    """Inverse of log1p transform applied to targets."""
    return np.expm1(y) if LOG_TARGET else y


def evaluate(y_train_true_raw, y_train_pred_log, y_test_true_raw, y_test_pred_log, model_name):
    """Evaluate always in original (unlogged) cycle units."""
    y_train_pred = inv(y_train_pred_log)
    y_test_pred  = inv(y_test_pred_log)

    rmse     = np.sqrt(mean_squared_error(y_test_true_raw, y_test_pred))
    mae      = mean_absolute_error(y_test_true_raw, y_test_pred)
    r2_train = r2_score(y_train_true_raw, y_train_pred)
    r2_test  = r2_score(y_test_true_raw,  y_test_pred)
    bias     = np.mean(y_test_pred - y_test_true_raw)

    pct_err  = np.abs(y_test_pred - y_test_true_raw) / (np.abs(y_test_true_raw) + 1e-6) * 100
    pct_good = np.mean(pct_err < 15) * 100
    pct_poor = np.mean(pct_err > 30) * 100

    print(f"{model_name:45s} | RMSE:{rmse:7.2f} | MAE:{mae:7.2f} | "
          f"R²tr:{r2_train:.3f} | R²te:{r2_test:.3f} | Bias:{bias:+6.1f} | "
          f"<15%:{pct_good:.0f}% >30%:{pct_poor:.0f}%")
    return {"Model": model_name, "RMSE": rmse, "MAE": mae,
            "R2_Train": r2_train, "R2_Test": r2_test,
            "Bias": bias, "Pct_Good": pct_good, "Pct_Poor": pct_poor}

def train_all_models(X_train, X_test, y_train, y_test, y_train_raw, y_test_raw):
    """
    X_train/X_test : StandardScaler-scaled numpy arrays
    y_train/y_test : log1p-transformed targets (if LOG_TARGET=True)
    y_train_raw/y_test_raw : original cycle-count targets (for metric display)
    """
    results = []
    print("\nTraining models...")

    # 1. Ridge Regression
    lr = Ridge(alpha=1.0)
    lr.fit(X_train, y_train)
    results.append(evaluate(y_train_raw, lr.predict(X_train), y_test_raw, lr.predict(X_test), "Ridge Regression (L2)"))

    # 2. Polynomial Regression (degree 2, top 10 features by index)
    poly = make_pipeline(PolynomialFeatures(degree=2, include_bias=False), Ridge(alpha=1.0))
    poly.fit(X_train[:, :10], y_train)
    results.append(evaluate(y_train_raw, poly.predict(X_train[:, :10]),
                            y_test_raw,  poly.predict(X_test[:, :10]),  "Polynomial Regression (Deg 2)"))

    # 3. Decision Tree
    dt = DecisionTreeRegressor(max_depth=6, min_samples_leaf=10, random_state=42)
    dt.fit(X_train, y_train)
    results.append(evaluate(y_train_raw, dt.predict(X_train), y_test_raw, dt.predict(X_test), "Decision Tree"))

    # 4. Random Forest (tuned)
    rf = RandomForestRegressor(
        n_estimators=300, max_depth=10, min_samples_leaf=5,
        max_features=0.6, random_state=42, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    results.append(evaluate(y_train_raw, rf.predict(X_train), y_test_raw, rf.predict(X_test), "Random Forest"))

    # 5. Gradient Boosting (tuned)
    gbm = GradientBoostingRegressor(
        n_estimators=500, max_depth=4, learning_rate=0.02,
        subsample=0.8, min_samples_leaf=5, random_state=42
    )
    gbm.fit(X_train, y_train)
    results.append(evaluate(y_train_raw, gbm.predict(X_train), y_test_raw, gbm.predict(X_test), "Gradient Boosting (GBM)"))

    # 6. XGBoost (tuned — early stopping on 10% hold-out)
    split = int(len(X_train) * 0.9)
    xgb_model = xgb.XGBRegressor(
        n_estimators=1000, max_depth=5, learning_rate=0.02,
        subsample=0.8, colsample_bytree=0.7,
        min_child_weight=5, reg_lambda=1.0, reg_alpha=0.1,
        random_state=42, n_jobs=-1,
        early_stopping_rounds=50, eval_metric='rmse'
    )
    xgb_model.fit(
        X_train[:split], y_train[:split],
        eval_set=[(X_train[split:], y_train[split:])],
        verbose=False
    )
    results.append(evaluate(y_train_raw, xgb_model.predict(X_train), y_test_raw, xgb_model.predict(X_test), "XGBoost"))
    xgb_model.save_model("best_xgboost_model.json")

    # 7. SVR (already scaled X, works correctly now)
    svr = SVR(kernel='rbf', C=10, epsilon=0.5)
    svr.fit(X_train, y_train)
    results.append(evaluate(y_train_raw, svr.predict(X_train), y_test_raw, svr.predict(X_test), "SVR"))

    return results

def main():
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    feature_path = os.path.join(data_dir, "labeled_features.csv")

    if not os.path.exists(feature_path):
        print(f"Error: {feature_path} not found.")
        return

    df = pd.read_csv(feature_path)

    # prepare_data now returns both log-transformed and raw targets
    (X_train, X_test,
     y_train, y_test,
     y_train_raw, y_test_raw, features) = prepare_data(df)

    results = train_all_models(X_train, X_test, y_train, y_test, y_train_raw, y_test_raw)

    res_df = pd.DataFrame(results)
    print("\n" + "="*100)
    print("FINAL MODEL COMPARISON  (metrics in original RUL cycle units)")
    print("="*100)
    print(res_df.to_string(index=False))

    res_df.to_csv(os.path.join(data_dir, "model_metrics.csv"), index=False)
    print(f"\nMetrics saved to data/model_metrics.csv")

if __name__ == "__main__":
    main()
