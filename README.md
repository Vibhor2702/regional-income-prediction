# 💰 Regional Income Prediction

A complete machine learning project that predicts average Adjusted Gross Income (AGI) for U.S. regions using IRS tax data and U.S. Census socio-economic indicators.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)

## 🎯 Project Overview

This project provides an end-to-end machine learning pipeline for predicting regional income levels, featuring:

- **Data Ingestion**: Automated collection from IRS SOI and Census API
- **Feature Engineering**: 30+ derived features with spatial analysis
- **Multiple ML Models**: Linear, Random Forest, XGBoost, LightGBM
- **Hyperparameter Tuning**: Optuna-based optimization
- **Model Interpretation**: SHAP values and permutation importance
- **Interactive Dashboard**: Streamlit web application
- **Production Ready**: Dockerized deployment

## 🧱 Tech Stack

| Category | Technologies |
|----------|-------------|
| **Language** | Python 3.11 |
| **Data Handling** | pandas, numpy, geopandas |
| **Visualization** | matplotlib, seaborn, plotly, folium |
| **ML Framework** | scikit-learn, xgboost, lightgbm, optuna, shap |
| **Dashboard** | streamlit, pydeck |
| **APIs** | requests, censusdata |
| **Deployment** | Docker, Conda |

## 📦 Data Sources

1. **IRS SOI Individual Income Tax Statistics**
   - ZIP and County level tax data
   - Target: Average AGI per return

2. **U.S. Census ACS 5-year Estimates**
   - Demographic and socio-economic indicators
   - Income, education, employment, housing data

3. **HUD ZIP-County Crosswalk**
   - Geographic mapping between ZIP codes and counties

4. **TIGER/Line Shapefiles**
   - Geographic boundaries for visualization

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Census API Key ([Get one here](https://api.census.gov/data/key_signup.html))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/regional-income-prediction.git
   cd regional-income-prediction
   ```

2. **Create and activate virtual environment**
   ```bash
   # Using conda (recommended)
   conda create -n income-pred python=3.11
   conda activate income-pred
   
   # Or using venv
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Unix/MacOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your Census API key
   ```

### Running the Pipeline

#### Option 1: Using Makefile (Recommended)

```bash
# Prepare data
make prepare

# Train models
make train

# Generate interpretation reports
make interpret

# Launch dashboard
make dashboard
```

#### Option 2: Manual Execution

```bash
# 1. Data ingestion
python src/data_ingest.py

# 2. Feature engineering
python src/features.py

# 3. Model training
python src/modeling.py

# 4. Model interpretation
python src/interpret.py

# 5. Launch dashboard
streamlit run app/streamlit_app.py
```

### Using Docker

```bash
# Build image
make docker-build

# Run container
make docker-run

# Access dashboard at http://localhost:8501
```

## 📁 Project Structure

```
regional-income-prediction/
├── app/
│   └── streamlit_app.py          # Interactive dashboard
├── data_raw/                      # Raw data (not in git)
│   ├── irs/                       # IRS tax data
│   ├── census/                    # Census ACS data
│   └── shapefiles/                # Geographic boundaries
├── data_processed/                # Processed data (not in git)
│   └── merged.parquet             # Final merged dataset
├── models/                        # Trained models (not in git)
│   ├── best_model.joblib          # Best performing model
│   └── feature_pipeline.joblib    # Preprocessing pipeline
├── notebooks/                     # Jupyter notebooks
│   └── 01_exploratory_analysis.ipynb
├── reports/                       # Generated reports
│   └── feature_importance/        # SHAP & importance plots
├── src/                           # Source code
│   ├── config.py                  # Configuration settings
│   ├── logger.py                  # Logging setup
│   ├── helpers.py                 # Utility functions
│   ├── data_ingest.py             # Data collection
│   ├── features.py                # Feature engineering
│   ├── modeling.py                # Model training
│   └── interpret.py               # Model interpretation
├── tests/                         # Unit tests
│   ├── test_data_ingest.py
│   ├── test_features.py
│   └── test_modeling.py
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── Dockerfile                     # Docker configuration
├── Makefile                       # Build automation
├── README.md                      # This file
└── requirements.txt               # Python dependencies
```

## 🧩 Pipeline Components

### 1. Data Ingestion (`data_ingest.py`)

Downloads and merges data from multiple sources:

```python
from src.data_ingest import DataIngester

ingester = DataIngester()
merged_data = ingester.run_full_pipeline()
```

**Key Features:**
- Automated IRS data download
- Census API integration
- HUD crosswalk processing
- TIGER/Line shapefile loading
- Data validation and cleaning

### 2. Feature Engineering (`features.py`)

Creates derived features and preprocessing pipeline:

```python
from src.features import FeatureEngineer

engineer = FeatureEngineer()
X, y, pipeline = engineer.prepare_features()
```

**Derived Features:**
- Unemployment rate
- Poverty rate
- Education rate (college+)
- Housing ownership rate
- Income ratios and log transforms
- Spatial lag features (optional)

### 3. Model Training (`modeling.py`)

Trains and evaluates multiple models:

```python
from src.modeling import ModelTrainer

trainer = ModelTrainer(X, y)
trainer.split_data()
trainer.train_all_models(tune_hyperparameters=True)
trainer.save_best_model()
```

**Models Implemented:**
- Linear Regression (baseline)
- Random Forest Regressor
- XGBoost Regressor
- LightGBM Regressor

**Evaluation Metrics:**
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² (Coefficient of Determination)
- MAPE (Mean Absolute Percentage Error)

### 4. Model Interpretation (`interpret.py`)

Generates feature importance visualizations:

```python
from src.interpret import ModelInterpreter

interpreter = ModelInterpreter()
interpreter.generate_all_reports()
```

**Outputs:**
- SHAP summary plots
- SHAP dependence plots
- Permutation importance
- Feature ranking

### 5. Dashboard (`streamlit_app.py`)

Interactive web application with:

- **Single Prediction**: Manual data entry form
- **Batch Predictions**: CSV upload
- **What-If Analysis**: Interactive sliders
- **Feature Importance**: Visual rankings
- **Geographic View**: Choropleth maps
- **Model Performance**: Metrics comparison

## 📊 Features

### Census ACS Variables Used

| Variable | Description |
|----------|-------------|
| `median_household_income` | Median household income |
| `per_capita_income` | Per capita income |
| `total_population` | Total population |
| `total_households` | Number of households |
| `avg_household_size` | Average household size |
| `median_age` | Median age of residents |
| `unemployment_rate` | Unemployment rate |
| `poverty_rate` | Poverty rate |
| `education_rate` | % with bachelor's degree or higher |
| `median_home_value` | Median home value |
| `median_gross_rent` | Median monthly rent |
| `owner_occupied_rate` | % owner-occupied housing |

### Model Performance Example

| Model | MAE | RMSE | R² | MAPE |
|-------|-----|------|----|----|
| **LightGBM** | $3,245 | $4,821 | 0.912 | 8.2% |
| XGBoost | $3,512 | $5,134 | 0.898 | 9.1% |
| Random Forest | $3,789 | $5,445 | 0.883 | 9.8% |
| Linear Regression | $5,234 | $7,892 | 0.743 | 14.5% |

*Note: Actual results will vary based on data quality and hyperparameter tuning.*

## 🧪 Testing

Run unit tests:

```bash
# Run all tests
make test

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## 📝 Development

### Code Style

This project follows PEP 8 style guidelines:

```bash
# Format code
black src/ app/ tests/

# Lint code
flake8 src/ app/ tests/
```

### Adding New Features

1. Create feature branch
2. Implement changes with docstrings
3. Add unit tests
4. Update documentation
5. Submit pull request

## 🐳 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Connect repository to [Streamlit Cloud](https://streamlit.io/cloud)
3. Configure secrets (Census API key)
4. Deploy

### Docker

```bash
# Build
docker build -t regional-income-prediction:latest .

# Run
docker run -p 8501:8501 \
  -v $(pwd)/data_processed:/app/data_processed \
  -v $(pwd)/models:/app/models \
  regional-income-prediction:latest
```

### Custom Server

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 📈 Model Interpretation

The project uses SHAP (SHapley Additive exPlanations) for model interpretation:

- **Global Importance**: Which features matter most overall
- **Local Explanations**: Why a specific prediction was made
- **Dependence Plots**: How feature values affect predictions
- **Interaction Effects**: How features work together

## 🔧 Configuration

Key settings in `src/config.py`:

```python
# Model parameters
RANDOM_SEED = 42
TEST_SIZE = 0.2
CV_FOLDS = 5

# Optuna tuning
N_TRIALS = 100
OPTUNA_TIMEOUT = 3600

# Feature engineering
IMPUTATION_STRATEGY = "median"
SPATIAL_LAG_K_NEIGHBORS = 5
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **IRS Statistics of Income Division** for tax data
- **U.S. Census Bureau** for demographic data
- **HUD** for geographic crosswalks
- **SHAP** team for interpretability tools

## 📧 Contact

For questions or feedback:
- Create an issue on GitHub
- Email: your.email@example.com

## 🗺️ Roadmap

- [ ] Add time series forecasting
- [ ] Implement deep learning models
- [ ] Add more geographic visualizations
- [ ] Create API endpoint for predictions
- [ ] Add automated data updates
- [ ] Expand to international data

---

**Built with ❤️ for transparent and explainable income prediction**
