"""
Simplified ML Pipeline for Regional Income Prediction
Uses real IRS data and synthetic Census features for demonstration.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import DATA_RAW_IRS_DIR, DATA_PROCESSED_DIR, RANDOM_SEED

print("="*70)
print("REGIONAL INCOME PREDICTION - SIMPLIFIED PIPELINE")
print("="*70)
print()

# ==============================================================================
# STEP 1: Load IRS Data
# ==============================================================================
print("STEP 1: Loading IRS Tax Data")
print("-" * 70)

irs_file = DATA_RAW_IRS_DIR / '15zpallagi.csv'
print(f"Reading {irs_file.name}...")

df = pd.read_csv(irs_file, low_memory=False)
print(f"✓ Loaded {len(df):,} raw records")

# Filter and process
df = df[df['zipcode'] != '00000'].copy()
df['zipcode'] = df['zipcode'].astype(str).str.zfill(5)

# Select relevant columns
columns = {
    'zipcode': 'zipcode',
    'STATEFIPS': 'state_fips',
    'STATE': 'state',
    'N1': 'num_returns',
    'A00100': 'total_agi',
    'A00200': 'total_wages',
    'N00200': 'returns_with_wages',
    'A00600': 'dividends',
    'A00900': 'business_income',
}

df_clean = df[list(columns.keys())].rename(columns=columns).copy()

# Aggregate by ZIP
agg_dict = {col: 'sum' if col not in ['state_fips', 'state'] else 'first' 
            for col in df_clean.columns if col != 'zipcode'}

df_irs = df_clean.groupby('zipcode').agg(agg_dict).reset_index()

# Calculate target variable (average AGI per return)
# IRS data is in thousands, so multiply by 1000
df_irs['avg_agi'] = df_irs['total_agi'] * 1000 / df_irs['num_returns'].replace(0, np.nan)

# Remove invalid records
df_irs = df_irs.dropna(subset=['avg_agi'])
df_irs = df_irs[df_irs['avg_agi'] > 0]

print(f"✓ Processed {len(df_irs):,} ZIP codes")
print(f"  Average AGI range: ${df_irs['avg_agi'].min():,.0f} - ${df_irs['avg_agi'].max():,.0f}")
print()

# ==============================================================================
# STEP 2: Generate Synthetic Census Features
# ==============================================================================
print("STEP 2: Generating Synthetic Census Features")
print("-" * 70)

np.random.seed(RANDOM_SEED)

# Create realistic synthetic features based on income correlations
n = len(df_irs)

# Income-based feature generation (higher income areas tend to have different demographics)
income_normalized = (df_irs['avg_agi'] - df_irs['avg_agi'].min()) / (df_irs['avg_agi'].max() - df_irs['avg_agi'].min())

df_irs['population'] = np.random.randint(1000, 50000, n)
df_irs['median_age'] = np.clip(30 + income_normalized * 20 + np.random.normal(0, 5, n), 20, 80)
df_irs['pct_white'] = np.clip(50 + income_normalized * 30 + np.random.normal(0, 15, n), 0, 100)
df_irs['pct_black'] = np.clip(15 - income_normalized * 10 + np.random.normal(0, 10, n), 0, 100)
df_irs['pct_asian'] = np.clip(5 + income_normalized * 20 + np.random.normal(0, 8, n), 0, 100)
df_irs['pct_hispanic'] = np.clip(20 - income_normalized * 10 + np.random.normal(0, 12, n), 0, 100)

# Socioeconomic features (correlated with income)
df_irs['median_household_income'] = np.clip(40000 + income_normalized * 100000 + np.random.normal(0, 15000, n), 20000, 300000)
df_irs['pct_bachelors_degree'] = np.clip(15 + income_normalized * 50 + np.random.normal(0, 10, n), 0, 100)
df_irs['pct_unemployed'] = np.clip(8 - income_normalized * 5 + np.random.normal(0, 2, n), 0, 25)
df_irs['pct_poverty'] = np.clip(15 - income_normalized * 12 + np.random.normal(0, 5, n), 0, 50)
df_irs['pct_food_stamps'] = np.clip(10 - income_normalized * 8 + np.random.normal(0, 3, n), 0, 40)

# Housing features
df_irs['median_home_value'] = np.clip(150000 + income_normalized * 500000 + np.random.normal(0, 80000, n), 50000, 2000000)
df_irs['pct_owner_occupied'] = np.clip(50 + income_normalized * 30 + np.random.normal(0, 15, n), 0, 100)

print(f"✓ Generated 13 synthetic Census features")
print(f"  Features: demographics, education, employment, housing")
print()

# ==============================================================================
# STEP 3: Feature Engineering
# ==============================================================================
print("STEP 3: Feature Engineering")
print("-" * 70)

# Create derived features
df_irs['unemployment_rate'] = df_irs['pct_unemployed'] / 100
df_irs['poverty_rate'] = df_irs['pct_poverty'] / 100
df_irs['education_rate'] = df_irs['pct_bachelors_degree'] / 100
df_irs['log_population'] = np.log1p(df_irs['population'])
df_irs['log_median_income'] = np.log1p(df_irs['median_household_income'])
df_irs['log_home_value'] = np.log1p(df_irs['median_home_value'])
df_irs['income_to_home_value'] = df_irs['median_household_income'] / df_irs['median_home_value'].replace(0, np.nan)

print(f"✓ Created 7 derived features")
print()

# ==============================================================================
# STEP 4: Save Processed Data
# ==============================================================================
print("STEP 4: Saving Processed Data")
print("-" * 70)

DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
output_file = DATA_PROCESSED_DIR / 'merged.parquet'

df_irs.to_parquet(output_file, index=False)
print(f"✓ Saved {len(df_irs):,} records to {output_file.name}")
print(f"  File size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
print()

# ==============================================================================
# STEP 5: Data Summary
# ==============================================================================
print("="*70)
print("PIPELINE COMPLETE - DATA SUMMARY")
print("="*70)
print()
print(f"Total Records: {len(df_irs):,}")
print(f"Total Features: {len(df_irs.columns)}")
print(f"States Covered: {df_irs['state'].nunique()}")
print()
print("Target Variable (avg_agi):")
print(f"  Mean:   ${df_irs['avg_agi'].mean():,.2f}")
print(f"  Median: ${df_irs['avg_agi'].median():,.2f}")
print(f"  Std:    ${df_irs['avg_agi'].std():,.2f}")
print(f"  Min:    ${df_irs['avg_agi'].min():,.2f}")
print(f"  Max:    ${df_irs['avg_agi'].max():,.2f}")
print()
print("Top 5 Features (by correlation with avg_agi):")
numeric_cols = df_irs.select_dtypes(include=[np.number]).columns
correlations = df_irs[numeric_cols].corr()['avg_agi'].abs().sort_values(ascending=False)
for i, (feature, corr) in enumerate(correlations[1:6].items(), 1):
    print(f"  {i}. {feature:30s} {corr:.3f}")
print()
print("="*70)
print("Next Steps:")
print("  1. Run: python src/modeling.py         (Train ML models)")
print("  2. Run: python src/interpret.py        (Generate SHAP analysis)")
print("  3. Run: streamlit run app/streamlit_app.py  (Launch dashboard)")
print("="*70)
