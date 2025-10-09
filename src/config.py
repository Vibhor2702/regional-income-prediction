"""
Configuration module for Regional Income Prediction project.

This module contains all project-wide constants, paths, and configuration settings.
Loads environment variables and provides centralized access to settings.
"""

import os
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
DATA_RAW_DIR = BASE_DIR / "data_raw"
DATA_RAW_IRS_DIR = DATA_RAW_DIR / "irs"
DATA_RAW_CENSUS_DIR = DATA_RAW_DIR / "census"
DATA_RAW_SHAPEFILES_DIR = DATA_RAW_DIR / "shapefiles"
DATA_PROCESSED_DIR = BASE_DIR / "data_processed"

# Model and report directories
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
FEATURE_IMPORTANCE_DIR = REPORTS_DIR / "feature_importance"

# ============================================================================
# API KEYS AND URLS
# ============================================================================

# Census API key (required for data collection)
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY", "")

# IRS Data URLs
IRS_ZIP_DATA_URL = os.getenv(
    "IRS_ZIP_DATA_URL",
    "https://www.irs.gov/pub/irs-soi/zipcode.zip"
)
IRS_COUNTY_DATA_URL = os.getenv(
    "IRS_COUNTY_DATA_URL",
    "https://www.irs.gov/pub/irs-soi/countydata.zip"
)

# HUD Crosswalk URL
HUD_ZIP_COUNTY_CROSSWALK_URL = os.getenv(
    "HUD_ZIP_COUNTY_CROSSWALK_URL",
    "https://www.huduser.gov/portal/datasets/usps_crosswalk.html"
)

# TIGER/Line Shapefiles
TIGER_SHAPEFILE_BASE_URL = os.getenv(
    "TIGER_SHAPEFILE_BASE_URL",
    "https://www2.census.gov/geo/tiger/TIGER2023"
)

# ============================================================================
# CENSUS ACS VARIABLES
# ============================================================================

# American Community Survey (ACS) 5-year estimates variable codes
# These are the predictor variables from U.S. Census data
ACS_VARIABLES: Dict[str, str] = {
    # Income variables
    "B19013_001E": "median_household_income",
    "B19301_001E": "per_capita_income",
    "B19025_001E": "aggregate_household_income",
    
    # Education variables
    "B15003_022E": "bachelors_degree",
    "B15003_023E": "masters_degree",
    "B15003_025E": "doctorate_degree",
    "B15003_001E": "total_population_25plus",
    
    # Employment variables
    "B23025_005E": "unemployed",
    "B23025_003E": "labor_force",
    "B23025_002E": "employed",
    
    # Population and household variables
    "B01003_001E": "total_population",
    "B11001_001E": "total_households",
    "B25010_001E": "avg_household_size",
    
    # Age variables
    "B01002_001E": "median_age",
    
    # Poverty variables
    "B17001_002E": "poverty_count",
    "B17001_001E": "poverty_denominator",
    
    # Housing variables
    "B25077_001E": "median_home_value",
    "B25064_001E": "median_gross_rent",
    "B25003_002E": "owner_occupied_housing",
    "B25003_003E": "renter_occupied_housing",
    
    # Commute variables
    "B08303_001E": "total_commuters",
    "B08303_013E": "long_commute_60plus_min",
}

# Census geography levels
CENSUS_GEO_LEVELS: List[str] = ["county", "zip code tabulation area"]

# ============================================================================
# MODEL CONFIGURATION
# ============================================================================

# Random seed for reproducibility
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))

# Train/test split ratio
TEST_SIZE = float(os.getenv("TEST_SIZE", "0.2"))

# Cross-validation folds
CV_FOLDS = int(os.getenv("CV_FOLDS", "5"))

# Optuna hyperparameter tuning configuration
N_TRIALS = int(os.getenv("N_TRIALS", "100"))
OPTUNA_TIMEOUT = int(os.getenv("OPTUNA_TIMEOUT", "3600"))  # seconds

# Model names
MODEL_NAMES: List[str] = [
    "LinearRegression",
    "RandomForest",
    "XGBoost",
    "LightGBM"
]

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

# Target variable from IRS data
TARGET_VARIABLE = "avg_agi"

# Columns to scale (numeric features)
NUMERIC_FEATURES_TO_SCALE: List[str] = [
    "median_household_income",
    "per_capita_income",
    "total_population",
    "total_households",
    "avg_household_size",
    "median_age",
    "unemployment_rate",
    "poverty_rate",
    "education_rate",
    "median_home_value",
    "median_gross_rent",
]

# Derived features to create
DERIVED_FEATURES: List[str] = [
    "wages_ratio",
    "dividends_ratio",
    "log_income",
    "pop_density",
    "owner_occupied_rate",
]

# Missing value imputation strategy
IMPUTATION_STRATEGY = "median"

# ============================================================================
# STREAMLIT CONFIGURATION
# ============================================================================

STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
STREAMLIT_SERVER_HEADLESS = os.getenv("STREAMLIT_SERVER_HEADLESS", "true").lower() == "true"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================================
# FILE FORMATS
# ============================================================================

PROCESSED_DATA_FILE = "merged.parquet"
BEST_MODEL_FILE = "best_model.joblib"
FEATURE_PIPELINE_FILE = "feature_pipeline.joblib"
SCALER_FILE = "scaler.joblib"

# ============================================================================
# GEOSPATIAL CONFIGURATION
# ============================================================================

# Coordinate reference systems
CRS_WGS84 = "EPSG:4326"  # Standard lat/lon
CRS_WEB_MERCATOR = "EPSG:3857"  # Web mapping

# Spatial lag configuration (for spatial autocorrelation features)
SPATIAL_LAG_K_NEIGHBORS = 5

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config() -> bool:
    """
    Validate that all required configuration is properly set.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    issues = []
    
    # Check Census API key
    if not CENSUS_API_KEY:
        issues.append("CENSUS_API_KEY not set in environment variables")
    
    # Check that directories exist
    for directory in [DATA_RAW_DIR, DATA_PROCESSED_DIR, MODELS_DIR, REPORTS_DIR]:
        if not directory.exists():
            issues.append(f"Directory does not exist: {directory}")
    
    if issues:
        print("Configuration validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    return True


if __name__ == "__main__":
    """Run configuration validation when executed directly."""
    print("Regional Income Prediction - Configuration")
    print("=" * 60)
    print(f"Base Directory: {BASE_DIR}")
    print(f"Random Seed: {RANDOM_SEED}")
    print(f"Census API Key Set: {'Yes' if CENSUS_API_KEY else 'No'}")
    print(f"Number of ACS Variables: {len(ACS_VARIABLES)}")
    print(f"Models to Train: {', '.join(MODEL_NAMES)}")
    print("=" * 60)
    
    if validate_config():
        print("✓ Configuration is valid")
    else:
        print("✗ Configuration validation failed")
