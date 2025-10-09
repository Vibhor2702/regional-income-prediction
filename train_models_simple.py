"""
Simplified ML Model Training for Regional Income Prediction
Trains multiple models and saves the best one.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import DATA_PROCESSED_DIR, MODELS_DIR, RANDOM_SEED

print("="*70)
print("REGIONAL INCOME PREDICTION - MODEL TRAINING")
print("="*70)
print()

# ==============================================================================
# STEP 1: Load Data
# ==============================================================================
print("STEP 1: Loading Processed Data")
print("-" * 70)

data_file = DATA_PROCESSED_DIR / 'merged.parquet'
df = pd.read_parquet(data_file)
print(f"✓ Loaded {len(df):,} records from {data_file.name}")
print(f"  Features: {len(df.columns)}")
print()

# ==============================================================================
# STEP 2: Prepare Features
# ==============================================================================
print("STEP 2: Preparing Features")
print("-" * 70)

# Define target and features
target = 'avg_agi'
exclude_cols = ['zipcode', 'state', 'state_fips', target]
feature_cols = [col for col in df.columns if col not in exclude_cols]

X = df[feature_cols].copy()
y = df[target].copy()

print(f"Target variable: {target}")
print(f"Number of features: {len(feature_cols)}")
print(f"Feature list:")
for i, col in enumerate(feature_cols, 1):
    print(f"  {i:2d}. {col}")
print()

# Handle missing values
X = X.fillna(X.median())

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_SEED
)

print(f"✓ Train set: {len(X_train):,} samples")
print(f"✓ Test set:  {len(X_test):,} samples")
print()

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"✓ Features scaled using StandardScaler")
print()

# ==============================================================================
# STEP 3: Train Models
# ==============================================================================
print("STEP 3: Training Models")
print("-" * 70)

models = {}
results = []

# 1. Linear Regression
print("Training Linear Regression...")
lr = LinearRegression()
lr.fit(X_train_scaled, y_train)
y_pred_lr = lr.predict(X_test_scaled)
mae_lr = mean_absolute_error(y_test, y_pred_lr)
rmse_lr = np.sqrt(mean_squared_error(y_test, y_pred_lr))
r2_lr = r2_score(y_test, y_pred_lr)
models['linear_regression'] = lr
results.append(('Linear Regression', mae_lr, rmse_lr, r2_lr))
print(f"  MAE: ${mae_lr:,.2f}  |  RMSE: ${rmse_lr:,.2f}  |  R²: {r2_lr:.4f}")

# 2. Random Forest
print("Training Random Forest...")
rf = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_split=10,
    random_state=RANDOM_SEED,
    n_jobs=-1
)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
mae_rf = mean_absolute_error(y_test, y_pred_rf)
rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
r2_rf = r2_score(y_test, y_pred_rf)
models['random_forest'] = rf
results.append(('Random Forest', mae_rf, rmse_rf, r2_rf))
print(f"  MAE: ${mae_rf:,.2f}  |  RMSE: ${rmse_rf:,.2f}  |  R²: {r2_rf:.4f}")

# 3. XGBoost
print("Training XGBoost...")
xgb_model = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=RANDOM_SEED,
    n_jobs=-1,
    verbosity=0
)
xgb_model.fit(X_train, y_train)
y_pred_xgb = xgb_model.predict(X_test)
mae_xgb = mean_absolute_error(y_test, y_pred_xgb)
rmse_xgb = np.sqrt(mean_squared_error(y_test, y_pred_xgb))
r2_xgb = r2_score(y_test, y_pred_xgb)
models['xgboost'] = xgb_model
results.append(('XGBoost', mae_xgb, rmse_xgb, r2_xgb))
print(f"  MAE: ${mae_xgb:,.2f}  |  RMSE: ${rmse_xgb:,.2f}  |  R²: {r2_xgb:.4f}")

# 4. LightGBM
print("Training LightGBM...")
lgb_model = lgb.LGBMRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=RANDOM_SEED,
    n_jobs=-1,
    verbosity=-1
)
lgb_model.fit(X_train, y_train)
y_pred_lgb = lgb_model.predict(X_test)
mae_lgb = mean_absolute_error(y_test, y_pred_lgb)
rmse_lgb = np.sqrt(mean_squared_error(y_test, y_pred_lgb))
r2_lgb = r2_score(y_test, y_pred_lgb)
models['lightgbm'] = lgb_model
results.append(('LightGBM', mae_lgb, rmse_lgb, r2_lgb))
print(f"  MAE: ${mae_lgb:,.2f}  |  RMSE: ${rmse_lgb:,.2f}  |  R²: {r2_lgb:.4f}")

# 5. Stacked Ensemble (Research-Based Enhancement)
print("Training Stacked Ensemble (Research-Based)...")
estimators = [
    ('xgb', xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=RANDOM_SEED,
        n_jobs=-1,
        verbosity=0
    )),
    ('lgbm', lgb.LGBMRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=RANDOM_SEED,
        n_jobs=-1,
        verbosity=-1
    )),
    ('rf', RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        random_state=RANDOM_SEED,
        n_jobs=-1
    ))
]

meta_learner = Ridge(alpha=1.0, random_state=RANDOM_SEED)
stacked_model = StackingRegressor(
    estimators=estimators,
    final_estimator=meta_learner,
    cv=5,
    n_jobs=-1
)
stacked_model.fit(X_train, y_train)
y_pred_stacked = stacked_model.predict(X_test)
mae_stacked = mean_absolute_error(y_test, y_pred_stacked)
rmse_stacked = np.sqrt(mean_squared_error(y_test, y_pred_stacked))
r2_stacked = r2_score(y_test, y_pred_stacked)
models['stacked_ensemble'] = stacked_model
results.append(('Stacked Ensemble', mae_stacked, rmse_stacked, r2_stacked))
print(f"  MAE: ${mae_stacked:,.2f}  |  RMSE: ${rmse_stacked:,.2f}  |  R²: {r2_stacked:.4f}")
print(f"  (Combines XGBoost + LightGBM + Random Forest)")
print()

# ==============================================================================
# STEP 4: Model Comparison
# ==============================================================================
print("="*70)
print("MODEL COMPARISON")
print("="*70)
print()

# Create results dataframe
results_df = pd.DataFrame(results, columns=['Model', 'MAE', 'RMSE', 'R²'])
results_df = results_df.sort_values('R²', ascending=False)

print(f"{'Model':<20} {'MAE':>15} {'RMSE':>15} {'R²':>10}")
print("-" * 70)
for _, row in results_df.iterrows():
    print(f"{row['Model']:<20} ${row['MAE']:>14,.2f} ${row['RMSE']:>14,.2f} {row['R²']:>10.4f}")
print()

best_model_name = results_df.iloc[0]['Model']
best_r2 = results_df.iloc[0]['R²']
print(f"🏆 Best Model: {best_model_name} (R² = {best_r2:.4f})")
print()

# ==============================================================================
# STEP 5: Save Models
# ==============================================================================
print("STEP 5: Saving Models")
print("-" * 70)

MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Save best model
best_model_key = best_model_name.lower().replace(' ', '_')
best_model = models[best_model_key]

model_file = MODELS_DIR / 'best_model.pkl'
scaler_file = MODELS_DIR / 'scaler.pkl'
features_file = MODELS_DIR / 'feature_names.txt'

joblib.dump(best_model, model_file)
joblib.dump(scaler, scaler_file)
with open(features_file, 'w') as f:
    f.write('\n'.join(feature_cols))

print(f"✓ Saved best model:     {model_file.name}")
print(f"✓ Saved scaler:         {scaler_file.name}")
print(f"✓ Saved feature names:  {features_file.name}")
print()

# Save all models for comparison
for name, model in models.items():
    model_path = MODELS_DIR / f'{name}.pkl'
    joblib.dump(model, model_path)
    print(f"✓ Saved {name}: {model_path.name}")

print()

# ==============================================================================
# STEP 6: Feature Importance
# ==============================================================================
print("="*70)
print("FEATURE IMPORTANCE (Top 10)")
print("="*70)
print()

# Get feature importance from best model
if hasattr(best_model, 'feature_importances_'):
    importances = best_model.feature_importances_
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    print(f"{'Rank':<6} {'Feature':<30} {'Importance':<12}")
    print("-" * 70)
    for i, row in feature_importance.head(10).iterrows():
        print(f"{i+1:<6} {row['feature']:<30} {row['importance']:.6f}")
elif hasattr(best_model, 'coef_'):
    coefs = np.abs(best_model.coef_)
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': coefs
    }).sort_values('importance', ascending=False)
    
    print(f"{'Rank':<6} {'Feature':<30} {'Coefficient':<12}")
    print("-" * 70)
    for i, row in feature_importance.head(10).iterrows():
        print(f"{i+1:<6} {row['feature']:<30} {row['importance']:.6f}")

print()
print("="*70)
print("MODEL TRAINING COMPLETE!")
print("="*70)
print()
print("Next Steps:")
print("  1. Run: streamlit run app/streamlit_app.py  (Launch dashboard)")
print("  2. View predictions and model insights")
print("="*70)
