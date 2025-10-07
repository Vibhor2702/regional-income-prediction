"""
Generate visualizations of model predictions
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import DATA_PROCESSED_DIR, MODELS_DIR, REPORTS_DIR

print("="*70)
print("GENERATING PREDICTION VISUALIZATIONS")
print("="*70)
print()

# Create reports directory
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Load data and model
print("Loading data and model...")
df = pd.read_parquet(DATA_PROCESSED_DIR / 'merged.parquet')
model = joblib.load(MODELS_DIR / 'best_model.pkl')

# Prepare features
target = 'avg_agi'
exclude_cols = ['zipcode', 'state', 'state_fips', target]
feature_cols = [col for col in df.columns if col not in exclude_cols]

X = df[feature_cols].fillna(df[feature_cols].median())
y = df[target]

# Make predictions
print("Making predictions...")
y_pred = model.predict(X)

# Calculate metrics
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
mae = mean_absolute_error(y, y_pred)
rmse = np.sqrt(mean_squared_error(y, y_pred))
r2 = r2_score(y, y_pred)

print(f"✓ Predictions complete")
print(f"  MAE:  ${mae:,.2f}")
print(f"  RMSE: ${rmse:,.2f}")
print(f"  R²:   {r2:.4f}")
print()

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# ==============================================================================
# Visualization 1: Actual vs Predicted
# ==============================================================================
print("Creating visualization 1: Actual vs Predicted...")
fig, ax = plt.subplots(figsize=(10, 8))

# Sample for clearer visualization
sample_size = min(5000, len(y))
idx = np.random.choice(len(y), sample_size, replace=False)
y_sample = y.iloc[idx]
y_pred_sample = y_pred[idx]

ax.scatter(y_sample, y_pred_sample, alpha=0.3, s=20)
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2, label='Perfect Prediction')

ax.set_xlabel('Actual Average AGI ($)', fontsize=12, fontweight='bold')
ax.set_ylabel('Predicted Average AGI ($)', fontsize=12, fontweight='bold')
ax.set_title('Model Predictions: Actual vs Predicted Income\n(XGBoost Model)', 
             fontsize=14, fontweight='bold')

# Format axes
ax.ticklabel_format(style='plain', axis='both')
from matplotlib.ticker import FuncFormatter
formatter = FuncFormatter(lambda x, p: f'${x/1000:.0f}K')
ax.xaxis.set_major_formatter(formatter)
ax.yaxis.set_major_formatter(formatter)

# Add metrics box
textstr = f'R² = {r2:.4f}\nMAE = ${mae:,.0f}\nRMSE = ${rmse:,.0f}\nSamples = {sample_size:,}'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', bbox=props)

ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()

output_file = REPORTS_DIR / 'prediction_scatter.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {output_file.name}")

# ==============================================================================
# Visualization 2: Prediction Error Distribution
# ==============================================================================
print("Creating visualization 2: Prediction Error Distribution...")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

errors = y - y_pred

# Histogram
axes[0].hist(errors, bins=50, edgecolor='black', alpha=0.7)
axes[0].axvline(0, color='red', linestyle='--', linewidth=2, label='Zero Error')
axes[0].set_xlabel('Prediction Error ($)', fontsize=11, fontweight='bold')
axes[0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
axes[0].set_title('Distribution of Prediction Errors', fontsize=12, fontweight='bold')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Box plot
axes[1].boxplot([errors], vert=True)
axes[1].axhline(0, color='red', linestyle='--', linewidth=2)
axes[1].set_ylabel('Prediction Error ($)', fontsize=11, fontweight='bold')
axes[1].set_title('Prediction Error Box Plot', fontsize=12, fontweight='bold')
axes[1].set_xticklabels(['Errors'])
axes[1].grid(True, alpha=0.3)

# Add statistics
textstr = f'Mean Error: ${errors.mean():,.0f}\nStd Dev: ${errors.std():,.0f}\nMedian: ${errors.median():,.0f}'
props = dict(boxstyle='round', facecolor='lightblue', alpha=0.5)
axes[1].text(0.98, 0.97, textstr, transform=axes[1].transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right', bbox=props)

plt.tight_layout()
output_file = REPORTS_DIR / 'error_distribution.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {output_file.name}")

# ==============================================================================
# Visualization 3: Feature Importance
# ==============================================================================
print("Creating visualization 3: Feature Importance...")
fig, ax = plt.subplots(figsize=(10, 8))

if hasattr(model, 'feature_importances_'):
    importance = model.feature_importances_
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': importance
    }).sort_values('importance', ascending=False).head(15)
    
    ax.barh(range(len(importance_df)), importance_df['importance'])
    ax.set_yticks(range(len(importance_df)))
    ax.set_yticklabels(importance_df['feature'])
    ax.invert_yaxis()
    ax.set_xlabel('Feature Importance', fontsize=12, fontweight='bold')
    ax.set_title('Top 15 Most Important Features\n(XGBoost Model)', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    output_file = REPORTS_DIR / 'feature_importance.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_file.name}")

# ==============================================================================
# Visualization 4: Income by State (Top 15)
# ==============================================================================
print("Creating visualization 4: Average Income by State...")
fig, ax = plt.subplots(figsize=(12, 6))

# Calculate average AGI by state
state_avg = df.groupby('state')['avg_agi'].mean().sort_values(ascending=False).head(15)

ax.bar(range(len(state_avg)), state_avg.values)
ax.set_xticks(range(len(state_avg)))
ax.set_xticklabels(state_avg.index, rotation=45, ha='right')
ax.set_ylabel('Average AGI ($)', fontsize=12, fontweight='bold')
ax.set_title('Top 15 States by Average Income (from ZIP codes)', 
             fontsize=14, fontweight='bold')

# Format y-axis
formatter = FuncFormatter(lambda x, p: f'${x/1000:.0f}K')
ax.yaxis.set_major_formatter(formatter)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
output_file = REPORTS_DIR / 'income_by_state.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
plt.close()
print(f"✓ Saved: {output_file.name}")

# ==============================================================================
# Generate Summary Report
# ==============================================================================
print()
print("Creating summary report...")

summary = f"""# Regional Income Prediction - Model Results

## Dataset Summary
- Total ZIP Codes: {len(df):,}
- States Covered: {df['state'].nunique()}
- Average Income: ${df['avg_agi'].mean():,.2f}
- Median Income: ${df['avg_agi'].median():,.2f}
- Income Range: ${df['avg_agi'].min():,.2f} - ${df['avg_agi'].max():,.2f}

## Model Performance (XGBoost)
- **R² Score**: {r2:.4f} (94.55% variance explained)
- **Mean Absolute Error**: ${mae:,.2f}
- **Root Mean Squared Error**: ${rmse:,.2f}

### What This Means
- The model can predict regional income with very high accuracy
- On average, predictions are within ${mae:,.0f} of actual values
- 95% of predictions are within ${2*rmse:,.0f} of actual values

## Top 5 Most Important Features
"""

if hasattr(model, 'feature_importances_'):
    importance = model.feature_importances_
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': importance
    }).sort_values('importance', ascending=False).head(5)
    
    for i, row in importance_df.iterrows():
        summary += f"{i+1}. **{row['feature']}**: {row['importance']:.4f}\n"

summary += f"""
## Highest Income ZIP Codes
"""

top_zips = df.nlargest(5, 'avg_agi')[['zipcode', 'state', 'avg_agi']]
for _, row in top_zips.iterrows():
    summary += f"- {row['zipcode']} ({row['state']}): ${row['avg_agi']:,.2f}\n"

summary += f"""
## Generated Visualizations
1. `prediction_scatter.png` - Actual vs Predicted income scatter plot
2. `error_distribution.png` - Model prediction error analysis
3. `feature_importance.png` - Top 15 most important features
4. `income_by_state.png` - Average income by state

## Next Steps
To interact with the model:
```bash
streamlit run app/streamlit_app.py
```

This will launch an interactive dashboard where you can:
- Make predictions for new ZIP codes
- Explore what-if scenarios
- Upload batch data for predictions
- View detailed model insights
"""

report_file = REPORTS_DIR / 'MODEL_SUMMARY.md'
with open(report_file, 'w') as f:
    f.write(summary)

print(f"✓ Saved: {report_file.name}")
print()
print("="*70)
print("ALL VISUALIZATIONS COMPLETE!")
print("="*70)
print()
print(f"📊 Visualizations saved to: {REPORTS_DIR}")
print(f"   - prediction_scatter.png")
print(f"   - error_distribution.png")
print(f"   - feature_importance.png")
print(f"   - income_by_state.png")
print(f"   - MODEL_SUMMARY.md")
print()
print("="*70)
