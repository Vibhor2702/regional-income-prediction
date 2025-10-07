# Instructions for Obtaining IRS Data

## Data Source
This project uses **IRS SOI Individual Income Tax Statistics - ZIP Code Data**.

## How to Get the Data

### Option 1: Download from IRS (Recommended)
1. Visit: https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-statistics-zip-code-data-soi
2. Download the ZIP code level data file (typically named `15zpallagi.csv` or similar)
3. Also download `field_definitions.csv` for variable descriptions
4. Place the CSV files in the `data_raw/irs/` directory

### Option 2: Alternative Sources
- **Kaggle**: Search for "IRS SOI ZIP Code Data" or "IRS Tax Statistics"
- **Data.gov**: May have archived versions of IRS statistics

## Expected Files
Place these files in `data_raw/irs/`:
- `15zpallagi.csv` - Main ZIP code level AGI data (~172 MB)
- `field_definitions.csv` - Variable descriptions
- Optional: Yearly data files (e.g., `14zpallagi.csv`, `13zpallagi.csv`, etc.)

## Data Structure
The main file (`15zpallagi.csv`) should contain:
- ZIP code level tax statistics
- Multiple income brackets (agi_stub: 1-6)
- Key variables:
  - `A00100`: Total AGI amount
  - `N1`: Number of returns
  - `A00200`: Wages and salaries
  - `STATEFIPS`: State FIPS code
  - And 100+ other tax-related variables

## After Downloading
1. Place files in `data_raw/irs/`
2. Run: `python test_irs_load.py` to verify the data loads correctly
3. Run: `python run_pipeline_simple.py` to process the data
4. Run: `python train_models_simple.py` to train models

## Data Privacy Note
This is **aggregated, anonymized data** published by the IRS. No individual taxpayer information is included.

## File Size Warning
The main data file is approximately **170-200 MB**. Make sure you have adequate storage space.

## Need Help?
If you can't find the data, open an issue on GitHub and we'll help you locate it!
