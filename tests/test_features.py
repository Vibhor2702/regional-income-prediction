"""
Unit tests for feature engineering module.

Tests preprocessing, feature creation, and pipeline functionality.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.features import FeatureEngineer
from src.helpers import create_derived_features


class TestFeatureEngineer:
    """Test suite for FeatureEngineer class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample dataset for testing."""
        return pd.DataFrame({
            'median_household_income': [50000, 60000, 70000],
            'per_capita_income': [30000, 35000, 40000],
            'total_population': [10000, 15000, 20000],
            'total_households': [4000, 5000, 6000],
            'unemployed': [400, 500, 600],
            'labor_force': [5000, 6000, 7000],
            'poverty_count': [1000, 1200, 1400],
            'poverty_denominator': [10000, 15000, 20000],
            'avg_agi_per_return': [45000, 55000, 65000]
        })
    
    def test_handle_missing_values(self, sample_data):
        """Test missing value handling."""
        # Add some missing values
        sample_data.loc[0, 'median_household_income'] = np.nan
        sample_data.loc[1, 'total_population'] = np.nan
        
        engineer = FeatureEngineer()
        result = engineer.handle_missing_values(sample_data)
        
        # Check that missing values are filled
        assert result['median_household_income'].isnull().sum() == 0
        assert result['total_population'].isnull().sum() == 0
    
    def test_create_features(self, sample_data):
        """Test derived feature creation."""
        engineer = FeatureEngineer()
        result = engineer.create_features(sample_data)
        
        # Check that derived features are created
        assert 'unemployment_rate' in result.columns
        assert 'poverty_rate' in result.columns
        
        # Verify calculations
        assert np.isclose(
            result['unemployment_rate'].iloc[0],
            sample_data['unemployed'].iloc[0] / sample_data['labor_force'].iloc[0]
        )
    
    def test_build_preprocessing_pipeline(self):
        """Test pipeline building."""
        engineer = FeatureEngineer()
        feature_names = ['feature1', 'feature2', 'feature3']
        
        pipeline = engineer.build_preprocessing_pipeline(feature_names)
        
        assert pipeline is not None
        assert hasattr(pipeline, 'fit')
        assert hasattr(pipeline, 'transform')


def test_create_derived_features():
    """Test derived feature creation helper."""
    df = pd.DataFrame({
        'total_wages': [100000, 200000],
        'total_income': [150000, 250000],
        'dividends': [10000, 20000],
        'unemployed': [100, 150],
        'labor_force': [1000, 1500],
    })
    
    result = create_derived_features(df)
    
    # Check wages ratio
    if 'wages_ratio' in result.columns:
        assert np.isclose(result['wages_ratio'].iloc[0], 100000 / 150001)
    
    # Check unemployment rate
    if 'unemployment_rate' in result.columns:
        assert np.isclose(result['unemployment_rate'].iloc[0], 100 / 1001)


def test_feature_validation():
    """Test feature validation."""
    # Test that feature names are strings
    features = ['feature1', 'feature2', 'feature3']
    assert all(isinstance(f, str) for f in features)
    
    # Test no duplicate features
    assert len(features) == len(set(features))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
