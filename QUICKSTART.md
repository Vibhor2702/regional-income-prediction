# 🚀 Quick Start Guide

## Regional Income Prediction Project

This guide will help you get started with the Regional Income Prediction system in just a few minutes.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.11 or higher installed
- [ ] Git installed (for version control)
- [ ] Census API key ([Get free key](https://api.census.gov/data/key_signup.html))
- [ ] 2GB+ free disk space
- [ ] Internet connection for data download

## Step-by-Step Setup

### 1. Installation (5 minutes)

```powershell
# Clone or navigate to project directory
cd regional-income-prediction

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration (2 minutes)

```powershell
# Copy environment template
copy .env.example .env

# Edit .env file and add your Census API key
notepad .env
```

Add your Census API key:
```
CENSUS_API_KEY=your_actual_api_key_here
```

### 3. Run the Pipeline (15-30 minutes)

#### Option A: Quick Demo (Recommended for first run)

```powershell
# Run data preparation
python src/data_ingest.py

# Train models (quick mode without hyperparameter tuning)
python src/modeling.py

# Generate interpretation reports
python src/interpret.py

# Launch dashboard
streamlit run app/streamlit_app.py
```

#### Option B: Using Makefile

```powershell
# Prepare data
make prepare

# Train models
make train

# Generate interpretations
make interpret

# Launch dashboard
make dashboard
```

### 4. Access Dashboard

Once the dashboard is running, open your browser to:
```
http://localhost:8501
```

## Project Workflow

```
┌─────────────────┐
│  Data Ingestion │  ← Download IRS & Census data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Feature Engineer │  ← Create derived features
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model Training  │  ← Train ML models
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Interpretation  │  ← SHAP & feature importance
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │  ← Interactive predictions
└─────────────────┘
```

## What Each Module Does

### 📥 Data Ingestion (`data_ingest.py`)
- Downloads IRS tax statistics (ZIP & County level)
- Fetches Census ACS demographic data via API
- Loads HUD ZIP-County crosswalk
- Merges datasets into single Parquet file
- **Output**: `data_processed/merged.parquet`

### 🔧 Feature Engineering (`features.py`)
- Handles missing values (median imputation)
- Creates 15+ derived features
- Normalizes numeric variables
- Builds sklearn preprocessing pipeline
- **Output**: `models/feature_pipeline.joblib`

### 🤖 Model Training (`modeling.py`)
- Trains 4 models: Linear, RandomForest, XGBoost, LightGBM
- Performs hyperparameter tuning with Optuna (optional)
- Evaluates with MAE, RMSE, R², MAPE
- Saves best model
- **Output**: `models/best_model.joblib`, `reports/model_results.json`

### 📊 Interpretation (`interpret.py`)
- Computes SHAP values for explainability
- Generates feature importance plots
- Creates dependence plots
- Calculates permutation importance
- **Output**: Multiple PNG files in `reports/feature_importance/`

### 🌐 Dashboard (`streamlit_app.py`)
- Single prediction form
- Batch CSV predictions
- What-if analysis with sliders
- Feature importance visualization
- Model performance metrics

## Common Commands

### Development

```powershell
# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Format code
black src/ app/ tests/

# Lint code
flake8 src/ app/ tests/
```

### Data Analysis

```powershell
# Open Jupyter notebook for EDA
jupyter notebook notebooks/01_exploratory_analysis.ipynb

# View processed data
python -c "import pandas as pd; df = pd.read_parquet('data_processed/merged.parquet'); print(df.head())"
```

### Docker Deployment

```powershell
# Build Docker image
docker build -t regional-income-prediction:latest .

# Run container
docker run -p 8501:8501 regional-income-prediction:latest

# Access at http://localhost:8501
```

## Troubleshooting

### Issue: Census API key error
**Solution**: Make sure you've:
1. Signed up for a free key at https://api.census.gov/data/key_signup.html
2. Added the key to your `.env` file
3. Restarted the script

### Issue: Import errors
**Solution**: Ensure you're in the virtual environment:
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: GDAL/GeoPandas installation fails
**Solution**: Install GDAL binaries first:
```powershell
# Download GDAL wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal
pip install path/to/GDAL-xxx.whl
pip install geopandas
```

### Issue: Out of memory
**Solution**: Reduce sample size in scripts:
- In `interpret.py`, reduce `sample_size` parameter
- In `modeling.py`, set `tune_hyperparameters=False`

## Next Steps

1. **Explore the Dashboard**: Try different input values and see predictions
2. **Review Feature Importance**: Check `reports/feature_importance/` for insights
3. **Customize Models**: Edit `src/config.py` to adjust hyperparameters
4. **Add Your Data**: Replace sample data with real IRS/Census downloads
5. **Deploy**: Use Docker or Streamlit Cloud for production

## File Locations

| What | Where |
|------|-------|
| Raw data | `data_raw/` |
| Processed data | `data_processed/merged.parquet` |
| Trained models | `models/best_model.joblib` |
| Feature pipeline | `models/feature_pipeline.joblib` |
| Reports | `reports/feature_importance/` |
| Logs | `logs/project.log` |

## Performance Benchmarks

On a typical laptop (8GB RAM, 4 cores):

| Task | Time |
|------|------|
| Data Ingestion | 2-5 min |
| Feature Engineering | 1-2 min |
| Model Training (no tuning) | 2-5 min |
| Model Training (with tuning) | 30-60 min |
| Interpretation | 3-10 min |
| Dashboard startup | 5-10 sec |

## Getting Help

1. **Documentation**: Read the full README.md
2. **Code Comments**: All functions have detailed docstrings
3. **Notebooks**: Check `notebooks/` for examples
4. **Tests**: Look at `tests/` for usage patterns
5. **Issues**: Create a GitHub issue for bugs

## Resources

- **IRS Data**: https://www.irs.gov/statistics/soi-tax-stats
- **Census API**: https://www.census.gov/data/developers/data-sets.html
- **SHAP Documentation**: https://shap.readthedocs.io/
- **Streamlit Docs**: https://docs.streamlit.io/

---

**Happy Predicting! 💰📊🚀**
