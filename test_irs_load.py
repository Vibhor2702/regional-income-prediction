"""
Quick test script to load and analyze IRS data.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import numpy as np
import pandas as pd
from src.config import DATA_RAW_IRS_DIR

def load_irs_data():
    """Load and process IRS data from CSV file."""
    print("Loading IRS data...")
    
    # Path to the main IRS data file
    irs_file = DATA_RAW_IRS_DIR / '15zpallagi.csv'
    
    if not irs_file.exists():
        print(f"ERROR: IRS data file not found at {irs_file}")
        return None
    
    # Read the CSV file
    print(f"Reading {irs_file.name}...")
    df = pd.read_csv(irs_file, low_memory=False)
    print(f"✓ Loaded {len(df):,} raw IRS records")
    
    # Filter out aggregate records (keep only ZIP code level data)
    print("Filtering ZIP code level data...")
    df = df[df['zipcode'] != '00000'].copy()
    print(f"✓ Kept {len(df):,} ZIP code records (removed state aggregates)")
    
    # Convert string zipcode to proper format
    df['zipcode'] = df['zipcode'].astype(str).str.zfill(5)
    
    # Extract key columns for ZIP-level data
    zip_columns = {
        'zipcode': 'zipcode',
        'STATEFIPS': 'state_fips',
        'STATE': 'state',
        'agi_stub': 'income_bracket',
        'N1': 'num_returns',
        'A00100': 'total_agi',
        'A00200': 'total_wages',
        'N00200': 'returns_with_wages',
        'A00600': 'dividends',
        'A00900': 'business_income',
        'A02650': 'total_income',
    }
    
    print("Extracting relevant columns...")
    df_zip = df[list(zip_columns.keys())].rename(columns=zip_columns).copy()
    
    # Aggregate by ZIP code (sum across income brackets)
    print("Aggregating data by ZIP code...")
    zip_agg = {
        'state_fips': 'first',
        'state': 'first',
        'num_returns': 'sum',
        'total_agi': 'sum',
        'total_wages': 'sum',
        'returns_with_wages': 'sum',
        'dividends': 'sum',
        'business_income': 'sum',
        'total_income': 'sum',
    }
    
    zip_data = df_zip.groupby('zipcode').agg(zip_agg).reset_index()
    
    # Calculate average AGI per return
    # Note: IRS data is in thousands of dollars, so multiply by 1000
    print("Calculating average AGI per return...")
    zip_data['avg_agi_per_return'] = (
        zip_data['total_agi'] * 1000 / zip_data['num_returns'].replace(0, np.nan)
    )
    
    # Remove rows with missing or invalid AGI
    print("Cleaning data...")
    initial_count = len(zip_data)
    zip_data = zip_data.dropna(subset=['avg_agi_per_return'])
    zip_data = zip_data[zip_data['avg_agi_per_return'] > 0]
    print(f"✓ Removed {initial_count - len(zip_data):,} rows with invalid AGI")
    
    print(f"\n{'='*60}")
    print(f"FINAL DATASET: {len(zip_data):,} ZIP codes with valid AGI data")
    print(f"{'='*60}\n")
    
    return zip_data


def show_statistics(df):
    """Display summary statistics."""
    if df is None:
        return
    
    print("SUMMARY STATISTICS")
    print("=" * 60)
    print(f"\nTotal ZIP codes: {len(df):,}")
    print(f"Total states: {df['state'].nunique()}")
    print(f"\nAverage AGI statistics:")
    print(f"  Mean:   ${df['avg_agi_per_return'].mean():,.2f}")
    print(f"  Median: ${df['avg_agi_per_return'].median():,.2f}")
    print(f"  Min:    ${df['avg_agi_per_return'].min():,.2f}")
    print(f"  Max:    ${df['avg_agi_per_return'].max():,.2f}")
    
    print(f"\nTop 10 highest income ZIP codes:")
    print(df.nlargest(10, 'avg_agi_per_return')[['zipcode', 'state', 'avg_agi_per_return', 'num_returns']])
    
    print(f"\nTop 10 states by number of ZIP codes:")
    state_counts = df['state'].value_counts().head(10)
    for state, count in state_counts.items():
        print(f"  {state}: {count:,} ZIP codes")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("IRS Data Loading Test")
    print("=" * 60 + "\n")
    
    # Load data
    df = load_irs_data()
    
    # Show statistics
    if df is not None:
        show_statistics(df)
        
        # Save to CSV for inspection
        output_file = DATA_RAW_IRS_DIR / "irs_processed_sample.csv"
        df.head(100).to_csv(output_file, index=False)
        print(f"\n✓ Saved first 100 rows to: {output_file}")
