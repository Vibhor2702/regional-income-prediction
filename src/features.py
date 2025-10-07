"""
Feature Engineering Module for Regional Income Prediction.

This module handles:
1. Loading processed data from data ingestion
2. Handling missing values using median imputation
3. Creating derived features (ratios, log transforms, etc.)
4. Computing spatial lag features from neighboring regions
5. Normalizing numeric features with StandardScaler
6. Building and saving sklearn Pipeline for deployment

Usage:
    from src.features import FeatureEngineer
    fe = FeatureEngineer()
    X, y, pipeline = fe.prepare_features()
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
from typing import Tuple, List, Optional
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from src.config import (
    DATA_PROCESSED_DIR,
    MODELS_DIR,
    PROCESSED_DATA_FILE,
    TARGET_VARIABLE,
    IMPUTATION_STRATEGY,
    NUMERIC_FEATURES_TO_SCALE,
    RANDOM_SEED,
    FEATURE_PIPELINE_FILE,
    SPATIAL_LAG_K_NEIGHBORS
)
from src.logger import get_logger
from src.helpers import (
    load_dataframe,
    save_model,
    check_missing_values,
    create_derived_features,
    calculate_spatial_lag
)

logger = get_logger(__name__)


class FeatureEngineer:
    """
    Main class for feature engineering and preprocessing.
    
    Attributes:
        data: Raw merged DataFrame
        X: Feature matrix
        y: Target variable
        pipeline: Sklearn preprocessing pipeline
    """
    
    def __init__(self, data_path: Optional[Path] = None):
        """
        Initialize FeatureEngineer.
        
        Args:
            data_path: Path to processed data file (optional)
        """
        self.data_path = data_path or (DATA_PROCESSED_DIR / PROCESSED_DATA_FILE)
        self.data = None
        self.X = None
        self.y = None
        self.pipeline = None
        self.feature_names = []
    
    def load_data(self) -> pd.DataFrame:
        """
        Load processed data from parquet file.
        
        Returns:
            pd.DataFrame: Loaded dataset
        """
        logger.info(f"Loading data from {self.data_path}")
        self.data = load_dataframe(self.data_path)
        logger.info(f"Loaded {len(self.data)} records with {len(self.data.columns)} columns")
        return self.data
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Strategy:
        - Numeric columns: Median imputation
        - Categorical columns: Mode imputation or 'Unknown'
        - Very sparse columns (>50% missing): Drop or flag
        
        Args:
            df: Input DataFrame
        
        Returns:
            pd.DataFrame: DataFrame with missing values handled
        """
        logger.info("Handling missing values...")
        
        # Check missing values
        check_missing_values(df, threshold=0.5)
        
        df = df.copy()
        
        # Separate numeric and categorical columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Drop columns with excessive missing values (>80%)
        missing_props = df.isnull().sum() / len(df)
        cols_to_drop = missing_props[missing_props > 0.8].index.tolist()
        
        if cols_to_drop:
            logger.warning(f"Dropping {len(cols_to_drop)} columns with >80% missing values")
            df = df.drop(columns=cols_to_drop)
        
        # Impute numeric columns with median
        for col in numeric_cols:
            if col in df.columns and df[col].isnull().any():
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                logger.debug(f"Imputed {col} with median: {median_val:.2f}")
        
        # Impute categorical columns with mode or 'Unknown'
        for col in categorical_cols:
            if col in df.columns and df[col].isnull().any():
                if df[col].mode().empty:
                    df[col].fillna('Unknown', inplace=True)
                else:
                    mode_val = df[col].mode()[0]
                    df[col].fillna(mode_val, inplace=True)
                logger.debug(f"Imputed {col} with mode")
        
        logger.info(f"Missing value handling complete. Remaining nulls: {df.isnull().sum().sum()}")
        return df
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create derived features from existing columns.
        
        Features created:
        - Unemployment rate (unemployed / labor_force)
        - Poverty rate (poverty_count / total_population)
        - Education rate (college degree holders / population 25+)
        - Owner-occupied rate (owned homes / total households)
        - Wages ratio (wages / total income)
        - Dividends ratio (dividends / total income)
        - Log-transformed income variables
        - Population density (if area data available)
        
        Args:
            df: Input DataFrame
        
        Returns:
            pd.DataFrame: DataFrame with additional derived features
        """
        logger.info("Creating derived features...")
        
        df = df.copy()
        
        # Use helper function for standard derived features
        df = create_derived_features(df)
        
        # Additional domain-specific features
        
        # Tax filing rate (returns per capita)
        if 'num_returns' in df.columns and 'total_population' in df.columns:
            df['tax_filing_rate'] = df['num_returns'] / (df['total_population'] + 1)
        
        # Average household income
        if 'total_agi' in df.columns and 'total_households' in df.columns:
            df['avg_household_agi'] = df['total_agi'] / (df['total_households'] + 1)
        
        # Business income ratio
        if 'business_income' in df.columns and 'total_agi' in df.columns:
            df['business_income_ratio'] = df['business_income'] / (df['total_agi'] + 1)
        
        # Commute burden (long commuters as % of total)
        if 'long_commute_60plus_min' in df.columns and 'total_commuters' in df.columns:
            df['long_commute_rate'] = df['long_commute_60plus_min'] / (df['total_commuters'] + 1)
        
        # Housing affordability index
        if 'median_gross_rent' in df.columns and 'median_household_income' in df.columns:
            df['rent_burden'] = (df['median_gross_rent'] * 12) / (df['median_household_income'] + 1)
        
        # Age dependency ratio (simplified)
        if 'median_age' in df.columns:
            df['age_squared'] = df['median_age'] ** 2
        
        logger.info(f"Created derived features. Total columns: {len(df.columns)}")
        return df
    
    def add_spatial_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add spatial lag features using neighboring regions.
        
        Spatial autocorrelation can be important for income prediction
        as neighboring areas often have similar economic characteristics.
        
        Args:
            df: Input DataFrame with geographic information
        
        Returns:
            pd.DataFrame: DataFrame with spatial lag features
        """
        logger.info("Adding spatial lag features...")
        
        # Check if we have geometry data
        if 'geometry' not in df.columns:
            logger.warning("No geometry column found. Skipping spatial features.")
            return df
        
        try:
            # Convert to GeoDataFrame if not already
            if not isinstance(df, gpd.GeoDataFrame):
                gdf = gpd.GeoDataFrame(df, geometry='geometry')
            else:
                gdf = df.copy()
            
            # Remove rows with missing geometry
            gdf = gdf[gdf.geometry.notna()]
            
            if len(gdf) == 0:
                logger.warning("No valid geometries found. Skipping spatial features.")
                return df
            
            # Calculate spatial lag for key variables
            spatial_vars = ['avg_agi_per_return', 'median_household_income', 
                          'unemployment_rate', 'poverty_rate']
            
            for var in spatial_vars:
                if var in gdf.columns:
                    spatial_lag = calculate_spatial_lag(
                        gdf, var, k_neighbors=SPATIAL_LAG_K_NEIGHBORS
                    )
                    gdf[f'{var}_spatial_lag'] = spatial_lag
            
            logger.info(f"Added spatial lag features for {len(spatial_vars)} variables")
            return pd.DataFrame(gdf)
        
        except Exception as e:
            logger.warning(f"Failed to create spatial features: {e}")
            return df
    
    def build_preprocessing_pipeline(
        self,
        numeric_features: List[str]
    ) -> Pipeline:
        """
        Build sklearn preprocessing pipeline.
        
        Pipeline steps:
        1. SimpleImputer for missing values (median strategy)
        2. StandardScaler for normalization
        
        Args:
            numeric_features: List of numeric feature names
        
        Returns:
            Pipeline: Configured preprocessing pipeline
        """
        logger.info("Building preprocessing pipeline...")
        
        # Create numeric transformer
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy=IMPUTATION_STRATEGY)),
            ('scaler', StandardScaler())
        ])
        
        # Create column transformer
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features)
            ],
            remainder='passthrough'  # Keep other columns as-is
        )
        
        # Create full pipeline
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor)
        ])
        
        logger.info(f"Pipeline built with {len(numeric_features)} numeric features")
        return pipeline
    
    def prepare_features(
        self,
        include_spatial: bool = False
    ) -> Tuple[pd.DataFrame, pd.Series, Pipeline]:
        """
        Complete feature preparation pipeline.
        
        Steps:
        1. Load data
        2. Handle missing values
        3. Create derived features
        4. Add spatial features (optional)
        5. Separate features (X) and target (y)
        6. Build and fit preprocessing pipeline
        7. Save pipeline for deployment
        
        Args:
            include_spatial: Whether to include spatial lag features
        
        Returns:
            tuple: (X, y, pipeline)
                X: Feature matrix (DataFrame)
                y: Target variable (Series)
                pipeline: Fitted preprocessing pipeline
        """
        logger.info("=" * 60)
        logger.info("Starting Feature Engineering Pipeline")
        logger.info("=" * 60)
        
        # Step 1: Load data
        logger.info("\n[1/7] Loading data...")
        df = self.load_data()
        
        # Step 2: Handle missing values
        logger.info("\n[2/7] Handling missing values...")
        df = self.handle_missing_values(df)
        
        # Step 3: Create derived features
        logger.info("\n[3/7] Creating derived features...")
        df = self.create_features(df)
        
        # Step 4: Add spatial features (optional)
        if include_spatial:
            logger.info("\n[4/7] Adding spatial features...")
            df = self.add_spatial_features(df)
        else:
            logger.info("\n[4/7] Skipping spatial features")
        
        # Step 5: Separate features and target
        logger.info("\n[5/7] Separating features and target...")
        
        if TARGET_VARIABLE not in df.columns:
            raise ValueError(f"Target variable '{TARGET_VARIABLE}' not found in dataset")
        
        # Remove rows with missing target
        df = df[df[TARGET_VARIABLE].notna()]
        
        y = df[TARGET_VARIABLE]
        
        # Identify feature columns (exclude target and identifiers)
        exclude_cols = [
            TARGET_VARIABLE,
            'zipcode', 'fips', 'county_fips', 'state_fips',
            'county_name', 'geo_level', 'geometry', 'geo'
        ]
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Only keep numeric features for modeling
        X = df[feature_cols].select_dtypes(include=[np.number])
        
        self.feature_names = X.columns.tolist()
        
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Target shape: {y.shape}")
        logger.info(f"Number of features: {len(self.feature_names)}")
        
        # Step 6: Build preprocessing pipeline
        logger.info("\n[6/7] Building preprocessing pipeline...")
        pipeline = self.build_preprocessing_pipeline(self.feature_names)
        
        # Fit pipeline on training data
        pipeline.fit(X)
        
        # Transform features
        X_transformed = pipeline.transform(X)
        X = pd.DataFrame(X_transformed, columns=self.feature_names, index=X.index)
        
        # Step 7: Save pipeline
        logger.info("\n[7/7] Saving preprocessing pipeline...")
        pipeline_path = MODELS_DIR / FEATURE_PIPELINE_FILE
        save_model(pipeline, pipeline_path)
        
        self.X = X
        self.y = y
        self.pipeline = pipeline
        
        logger.info("=" * 60)
        logger.info("Feature Engineering Complete!")
        logger.info(f"Final feature matrix: {X.shape}")
        logger.info(f"Pipeline saved to: {pipeline_path}")
        logger.info("=" * 60)
        
        return X, y, pipeline
    
    def get_feature_names(self) -> List[str]:
        """
        Get list of feature names after preprocessing.
        
        Returns:
            list: Feature names
        """
        return self.feature_names


def main():
    """Main entry point for feature engineering."""
    engineer = FeatureEngineer()
    X, y, pipeline = engineer.prepare_features(include_spatial=False)
    
    # Display summary
    print("\n" + "=" * 60)
    print("Feature Engineering Summary")
    print("=" * 60)
    print(f"Number of samples: {len(X)}")
    print(f"Number of features: {len(X.columns)}")
    print(f"\nTarget variable statistics:")
    print(y.describe())
    print(f"\nFeature columns:")
    for i, col in enumerate(X.columns, 1):
        print(f"  {i:2d}. {col}")


if __name__ == "__main__":
    main()
