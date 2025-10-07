"""
Unit tests for data ingestion module.

Tests data collection, validation, and merging functionality.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_ingest import DataIngester
from src.config import DATA_RAW_DIR, DATA_PROCESSED_DIR


class TestDataIngester:
    """Test suite for DataIngester class."""
    
    @pytest.fixture
    def ingester(self):
        """Create DataIngester instance."""
        return DataIngester()
    
    def test_init(self, ingester):
        """Test DataIngester initialization."""
        assert ingester.irs_dir.exists()
        assert ingester.census_dir.exists()
        assert ingester.shapefiles_dir.exists()
    
    def test_download_irs_data(self, ingester):
        """Test IRS data download."""
        zip_data, county_data = ingester.download_irs_data()
        
        assert isinstance(zip_data, pd.DataFrame)
        assert isinstance(county_data, pd.DataFrame)
        assert len(zip_data) > 0
        assert len(county_data) > 0
        assert 'zipcode' in zip_data.columns or 'avg_agi_per_return' in zip_data.columns
    
    def test_fetch_census_data(self, ingester):
        """Test Census data fetching."""
        census_data = ingester.fetch_census_data(geo_level="county")
        
        assert isinstance(census_data, pd.DataFrame)
        assert len(census_data) > 0
        # Should have some demographic variables
        assert any(col in census_data.columns for col in [
            'median_household_income', 'total_population', 'fips'
        ])
    
    def test_download_hud_crosswalk(self, ingester):
        """Test HUD crosswalk download."""
        crosswalk = ingester.download_hud_crosswalk()
        
        assert isinstance(crosswalk, pd.DataFrame)
        assert len(crosswalk) > 0
        assert 'zipcode' in crosswalk.columns
        assert 'county_fips' in crosswalk.columns
    
    def test_merge_datasets(self, ingester):
        """Test dataset merging."""
        # Create sample data
        irs_data = pd.DataFrame({
            'zipcode': ['10001', '10002'],
            'avg_agi': [50000, 45000]
        })
        
        census_data = pd.DataFrame({
            'zipcode': ['10001', '10002'],
            'median_income': [60000, 55000]
        })
        
        merged = ingester.merge_datasets(irs_data, census_data, 'zipcode')
        
        assert isinstance(merged, pd.DataFrame)
        assert len(merged) > 0
        assert 'avg_agi' in merged.columns
        assert 'median_income' in merged.columns


def test_data_validation():
    """Test data validation functions."""
    # Create test dataframe
    df = pd.DataFrame({
        'col1': [1, 2, 3, np.nan],
        'col2': [4, 5, 6, 7],
        'col3': [np.nan, np.nan, np.nan, np.nan]
    })
    
    # Check missing values
    missing = df.isnull().sum()
    assert missing['col1'] == 1
    assert missing['col2'] == 0
    assert missing['col3'] == 4


def test_file_structure():
    """Test that required directories exist."""
    assert DATA_RAW_DIR.exists()
    assert DATA_PROCESSED_DIR.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
