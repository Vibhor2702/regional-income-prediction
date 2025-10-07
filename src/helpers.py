"""
Helper utilities module.

Contains shared utility functions used across multiple modules in the project.
Includes functions for data validation, file I/O, geographic operations, etc.
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import joblib
from sklearn.neighbors import NearestNeighbors
from src.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# FILE I/O UTILITIES
# ============================================================================

def save_dataframe(
    df: pd.DataFrame,
    file_path: Path,
    file_format: str = "parquet"
) -> None:
    """
    Save DataFrame to disk in specified format.
    
    Args:
        df: DataFrame to save
        file_path: Destination file path
        file_format: Format to save ('parquet', 'csv', 'pickle')
    
    Raises:
        ValueError: If unsupported file format is specified
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if file_format == "parquet":
        df.to_parquet(file_path, index=False)
    elif file_format == "csv":
        df.to_csv(file_path, index=False)
    elif file_format == "pickle":
        df.to_pickle(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")
    
    logger.info(f"Saved DataFrame to {file_path} ({len(df)} rows)")


def load_dataframe(
    file_path: Path,
    file_format: Optional[str] = None
) -> pd.DataFrame:
    """
    Load DataFrame from disk, auto-detecting format from extension if not specified.
    
    Args:
        file_path: Source file path
        file_format: Format to load ('parquet', 'csv', 'pickle'). Auto-detected if None.
    
    Returns:
        pd.DataFrame: Loaded DataFrame
    
    Raises:
        ValueError: If unsupported file format or file doesn't exist
    """
    if not file_path.exists():
        raise ValueError(f"File not found: {file_path}")
    
    # Auto-detect format from extension
    if file_format is None:
        file_format = file_path.suffix.lower().replace(".", "")
    
    if file_format == "parquet":
        df = pd.read_parquet(file_path)
    elif file_format == "csv":
        df = pd.read_csv(file_path)
    elif file_format in ["pickle", "pkl"]:
        df = pd.read_pickle(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")
    
    logger.info(f"Loaded DataFrame from {file_path} ({len(df)} rows)")
    return df


def save_model(model: object, file_path: Path) -> None:
    """
    Save trained model to disk using joblib.
    
    Args:
        model: Trained model or pipeline object
        file_path: Destination file path
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, file_path)
    logger.info(f"Saved model to {file_path}")


def load_model(file_path: Path) -> object:
    """
    Load trained model from disk.
    
    Args:
        file_path: Source file path
    
    Returns:
        object: Loaded model or pipeline object
    
    Raises:
        ValueError: If file doesn't exist
    """
    if not file_path.exists():
        raise ValueError(f"Model file not found: {file_path}")
    
    model = joblib.load(file_path)
    logger.info(f"Loaded model from {file_path}")
    return model


# ============================================================================
# DATA VALIDATION UTILITIES
# ============================================================================

def check_missing_values(df: pd.DataFrame, threshold: float = 0.5) -> Dict[str, float]:
    """
    Check for missing values in DataFrame and report columns exceeding threshold.
    
    Args:
        df: Input DataFrame
        threshold: Maximum acceptable proportion of missing values (0-1)
    
    Returns:
        dict: Dictionary mapping column names to missing value proportions
              for columns exceeding the threshold
    """
    missing_props = df.isnull().sum() / len(df)
    problematic = missing_props[missing_props > threshold].to_dict()
    
    if problematic:
        logger.warning(
            f"Found {len(problematic)} columns with >{threshold*100}% missing values"
        )
        for col, prop in problematic.items():
            logger.warning(f"  - {col}: {prop*100:.1f}% missing")
    
    return problematic


def validate_dataframe_schema(
    df: pd.DataFrame,
    required_columns: List[str],
    raise_error: bool = True
) -> bool:
    """
    Validate that DataFrame contains all required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        raise_error: If True, raise ValueError on validation failure
    
    Returns:
        bool: True if valid, False otherwise
    
    Raises:
        ValueError: If validation fails and raise_error is True
    """
    missing_cols = set(required_columns) - set(df.columns)
    
    if missing_cols:
        error_msg = f"Missing required columns: {', '.join(missing_cols)}"
        if raise_error:
            raise ValueError(error_msg)
        else:
            logger.error(error_msg)
            return False
    
    return True


def detect_outliers_iqr(
    series: pd.Series,
    multiplier: float = 1.5
) -> Tuple[pd.Series, int]:
    """
    Detect outliers using the Interquartile Range (IQR) method.
    
    Args:
        series: Numeric series to analyze
        multiplier: IQR multiplier for outlier boundaries (typically 1.5)
    
    Returns:
        tuple: (Boolean mask of outliers, count of outliers)
    """
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    outliers = (series < lower_bound) | (series > upper_bound)
    outlier_count = outliers.sum()
    
    if outlier_count > 0:
        logger.info(
            f"Detected {outlier_count} outliers in '{series.name}' "
            f"({outlier_count/len(series)*100:.1f}%)"
        )
    
    return outliers, outlier_count


# ============================================================================
# GEOGRAPHIC UTILITIES
# ============================================================================

def calculate_spatial_lag(
    gdf: gpd.GeoDataFrame,
    value_column: str,
    k_neighbors: int = 5
) -> pd.Series:
    """
    Calculate spatial lag features using k-nearest neighbors.
    
    Spatial lag represents the average value of neighboring regions,
    useful for capturing spatial autocorrelation.
    
    Args:
        gdf: GeoDataFrame with geometry column
        value_column: Column to calculate spatial lag for
        k_neighbors: Number of nearest neighbors to consider
    
    Returns:
        pd.Series: Spatial lag values for each region
    """
    # Get centroids for distance calculations
    centroids = gdf.geometry.centroid
    coords = np.array([[point.x, point.y] for point in centroids])
    
    # Fit nearest neighbors
    nn = NearestNeighbors(n_neighbors=k_neighbors + 1, algorithm='ball_tree')
    nn.fit(coords)
    
    # Get neighbors (excluding self)
    distances, indices = nn.kneighbors(coords)
    
    # Calculate spatial lag as mean of neighbors
    values = gdf[value_column].values
    spatial_lags = []
    
    for idx_array in indices:
        # Skip first index (self)
        neighbor_values = values[idx_array[1:]]
        # Calculate mean, handling NaN values
        spatial_lag = np.nanmean(neighbor_values)
        spatial_lags.append(spatial_lag)
    
    logger.info(f"Calculated spatial lag for '{value_column}' using {k_neighbors} neighbors")
    return pd.Series(spatial_lags, index=gdf.index, name=f"{value_column}_spatial_lag")


def merge_geometries(
    df: pd.DataFrame,
    shapefile_path: Path,
    left_on: str,
    right_on: str
) -> gpd.GeoDataFrame:
    """
    Merge DataFrame with shapefile geometries.
    
    Args:
        df: Input DataFrame
        shapefile_path: Path to shapefile
        left_on: Column name in df for join
        right_on: Column name in shapefile for join
    
    Returns:
        gpd.GeoDataFrame: Merged GeoDataFrame with geometries
    """
    # Load shapefile
    gdf_shapes = gpd.read_file(shapefile_path)
    
    # Merge
    gdf = df.merge(
        gdf_shapes[[right_on, 'geometry']],
        left_on=left_on,
        right_on=right_on,
        how='left'
    )
    
    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    
    logger.info(f"Merged {len(gdf)} records with geometries from {shapefile_path}")
    return gdf


# ============================================================================
# FEATURE ENGINEERING UTILITIES
# ============================================================================

def create_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create derived features from existing columns.
    
    This function creates ratio, log-transformed, and computed features
    that are commonly useful for income prediction.
    
    Args:
        df: Input DataFrame
    
    Returns:
        pd.DataFrame: DataFrame with additional derived features
    """
    df = df.copy()
    
    # Income ratios (if wage and dividend data available)
    if 'total_wages' in df.columns and 'total_income' in df.columns:
        df['wages_ratio'] = df['total_wages'] / (df['total_income'] + 1)
    
    if 'dividends' in df.columns and 'total_income' in df.columns:
        df['dividends_ratio'] = df['dividends'] / (df['total_income'] + 1)
    
    # Log transformations for skewed income variables
    income_cols = [col for col in df.columns if 'income' in col.lower()]
    for col in income_cols:
        if df[col].dtype in [np.float64, np.int64] and (df[col] > 0).any():
            df[f'log_{col}'] = np.log1p(df[col])
    
    # Population density (if area is available)
    if 'total_population' in df.columns and 'area_sq_km' in df.columns:
        df['pop_density'] = df['total_population'] / (df['area_sq_km'] + 0.1)
    
    # Housing ownership rate
    if 'owner_occupied_housing' in df.columns and 'total_households' in df.columns:
        df['owner_occupied_rate'] = df['owner_occupied_housing'] / (df['total_households'] + 1)
    
    # Unemployment rate
    if 'unemployed' in df.columns and 'labor_force' in df.columns:
        df['unemployment_rate'] = df['unemployed'] / (df['labor_force'] + 1)
    
    # Poverty rate
    if 'poverty_count' in df.columns and 'poverty_denominator' in df.columns:
        df['poverty_rate'] = df['poverty_count'] / (df['poverty_denominator'] + 1)
    
    # Education rate (bachelor's degree or higher)
    if 'bachelors_degree' in df.columns and 'total_population_25plus' in df.columns:
        df['education_rate'] = (
            (df['bachelors_degree'] + df.get('masters_degree', 0) + df.get('doctorate_degree', 0))
            / (df['total_population_25plus'] + 1)
        )
    
    logger.info(f"Created {len(df.columns) - len(df.columns)} derived features")
    return df


def get_feature_importance_dict(
    model,
    feature_names: List[str]
) -> Dict[str, float]:
    """
    Extract feature importance from trained model.
    
    Works with models that have feature_importances_ attribute
    (RandomForest, XGBoost, LightGBM).
    
    Args:
        model: Trained model with feature_importances_ attribute
        feature_names: List of feature names
    
    Returns:
        dict: Dictionary mapping feature names to importance scores
    """
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        return dict(zip(feature_names, importances))
    else:
        logger.warning(f"Model {type(model).__name__} does not have feature importances")
        return {}


# ============================================================================
# METRICS UTILITIES
# ============================================================================

def calculate_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """
    Calculate comprehensive regression evaluation metrics.
    
    Args:
        y_true: True target values
        y_pred: Predicted target values
    
    Returns:
        dict: Dictionary of metric names and values
    """
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    # Additional metrics
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1))) * 100  # Mean Absolute Percentage Error
    
    metrics = {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2,
        'MAPE': mape
    }
    
    return metrics


if __name__ == "__main__":
    """Test helper functions."""
    print("Testing helper utilities...")
    
    # Test DataFrame validation
    test_df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': [4, 5, 6],
        'c': [7, np.nan, 9]
    })
    
    print(f"\n✓ Missing values check:")
    check_missing_values(test_df, threshold=0.2)
    
    print(f"\n✓ Schema validation:")
    validate_dataframe_schema(test_df, ['a', 'b', 'c'], raise_error=False)
    
    print(f"\n✓ All helper utilities loaded successfully")
