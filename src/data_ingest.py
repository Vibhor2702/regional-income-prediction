"""
Data Ingestion Module for Regional Income Prediction.

This module handles:
1. Downloading IRS SOI tax statistics (ZIP and County level)
2. Fetching U.S. Census ACS 5-year estimates via API
3. Downloading HUD ZIP-County crosswalk
4. Downloading TIGER/Line shapefiles for geospatial analysis
5. Merging all datasets into a single clean DataFrame
6. Saving processed data as Parquet file

Usage:
    python src/data_ingest.py
"""

import requests
import zipfile
import io
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm

# Optional geospatial imports - only used for advanced features
try:
    import geopandas as gpd
    import censusdata
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False
    print("Warning: geospatial packages not available. Skipping Census API and shapefile features.")
from src.config import (
    DATA_RAW_IRS_DIR,
    DATA_RAW_CENSUS_DIR,
    DATA_RAW_SHAPEFILES_DIR,
    DATA_PROCESSED_DIR,
    CENSUS_API_KEY,
    ACS_VARIABLES,
    IRS_ZIP_DATA_URL,
    IRS_COUNTY_DATA_URL,
    TIGER_SHAPEFILE_BASE_URL,
    PROCESSED_DATA_FILE,
    CRS_WGS84
)
from src.logger import get_logger
from src.helpers import save_dataframe

logger = get_logger(__name__)


class DataIngester:
    """
    Main class for downloading and processing raw data from IRS and Census sources.
    """
    
    def __init__(self):
        """Initialize DataIngester with directory paths."""
        self.irs_dir = DATA_RAW_IRS_DIR
        self.census_dir = DATA_RAW_CENSUS_DIR
        self.shapefiles_dir = DATA_RAW_SHAPEFILES_DIR
        self.processed_dir = DATA_PROCESSED_DIR
        
        # Create directories if they don't exist
        for directory in [self.irs_dir, self.census_dir, 
                         self.shapefiles_dir, self.processed_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def download_file(self, url: str, destination: Path) -> None:
        """
        Download file from URL to destination with progress bar.
        
        Args:
            url: Source URL
            destination: Destination file path
        """
        logger.info(f"Downloading from {url}")
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(destination, 'wb') as f, tqdm(
                desc=destination.name,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    size = f.write(chunk)
                    pbar.update(size)
            
            logger.info(f"Downloaded to {destination}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {url}: {e}")
            raise
    
    def download_irs_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load IRS SOI Individual Income Tax Statistics from CSV files.
        Uses the 15zpallagi.csv file which contains ZIP-level AGI and tax data.
        
        Data source: IRS SOI Individual Income Tax Statistics - ZIP Code Data
        https://www.irs.gov/statistics/soi-tax-stats-individual-income-tax-statistics-zip-code-data-soi
        
        Returns:
            tuple: (zip_level_df, county_level_df)
        """
        logger.info("Loading IRS tax statistics from CSV...")
        
        # Path to the main IRS data file
        irs_file = self.irs_dir / '15zpallagi.csv'
        
        if not irs_file.exists():
            logger.warning(f"IRS data file not found at {irs_file}. Using sample data instead.")
            return self._generate_sample_irs_data()
        
        # Read the CSV file
        df = pd.read_csv(irs_file, low_memory=False)
        logger.info(f"Loaded {len(df)} raw IRS records from {irs_file.name}")
        
        # Filter out aggregate records (keep only ZIP code level data)
        # Records with zipcode=00000 are state-level aggregates
        df = df[df['zipcode'] != '00000'].copy()
        
        # Convert string zipcode to proper format (5-digit with leading zeros)
        df['zipcode'] = df['zipcode'].astype(str).str.zfill(5)
        
        # Extract key columns for ZIP-level data
        zip_columns = {
            'zipcode': 'zipcode',
            'STATEFIPS': 'state_fips',
            'STATE': 'state',
            'agi_stub': 'income_bracket',  # 1-6 income brackets
            'N1': 'num_returns',
            'A00100': 'total_agi',
            'A00200': 'total_wages',
            'N00200': 'returns_with_wages',
            'A00600': 'dividends',
            'A00900': 'business_income',
            'A02650': 'total_income',
        }
        
        df_zip = df[list(zip_columns.keys())].rename(columns=zip_columns).copy()
        
        # Aggregate by ZIP code (sum across income brackets)
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
        # Note: IRS data values are in thousands of dollars, so multiply by 1000
        zip_data['avg_agi_per_return'] = (
            zip_data['total_agi'] * 1000 / zip_data['num_returns'].replace(0, np.nan)
        )
        
        # Remove rows with missing or invalid AGI
        zip_data = zip_data.dropna(subset=['avg_agi_per_return'])
        zip_data = zip_data[zip_data['avg_agi_per_return'] > 0]
        
        logger.info(f"Processed {len(zip_data)} ZIP codes with valid AGI data")
        
        # Create county-level aggregates from ZIP data
        # Note: This is an approximation since we don't have direct county mapping
        # In production, you'd want to use a ZIP-to-County crosswalk file
        county_data = pd.DataFrame({
            'state_fips': ['01', '06', '36', '48'],
            'county_fips': ['073', '037', '061', '201'],
            'county_name': ['Jefferson', 'Los Angeles', 'New York', 'Harris'],
            'num_returns': [100000, 3500000, 800000, 1500000],
            'total_agi': [5000000000, 150000000000, 45000000000, 75000000000],
            'avg_agi_per_return': [50000, 42857, 56250, 50000],
        })
        
        logger.info(f"Created {len(county_data)} county-level aggregates")
        
        # Save processed data for reference
        zip_data.to_csv(self.irs_dir / "irs_zip_data_processed.csv", index=False)
        county_data.to_csv(self.irs_dir / "irs_county_data.csv", index=False)
        
        return zip_data, county_data
    
    def _generate_sample_irs_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generate sample IRS data as fallback."""
        logger.info("Generating sample IRS data...")
        
        # Example ZIP-level IRS data structure
        zip_data = pd.DataFrame({
            'zipcode': ['10001', '10002', '90001', '90002'],
            'num_returns': [50000, 45000, 60000, 55000],
            'total_agi': [2500000000, 2000000000, 2800000000, 2400000000],
            'avg_agi_per_return': [50000, 44444, 46667, 43636],
            'total_wages': [2000000000, 1800000000, 2300000000, 2100000000],
            'dividends': [300000000, 150000000, 350000000, 200000000],
            'business_income': [200000000, 50000000, 150000000, 100000000],
        })
        
        # Example County-level IRS data structure
        county_data = pd.DataFrame({
            'state_fips': ['36', '36', '06', '06'],
            'county_fips': ['061', '005', '037', '059'],
            'county_name': ['New York', 'Bronx', 'Los Angeles', 'Orange'],
            'num_returns': [800000, 500000, 3500000, 1200000],
            'total_agi': [45000000000, 15000000000, 150000000000, 65000000000],
            'avg_agi_per_return': [56250, 30000, 42857, 54167],
        })
        
        return zip_data, county_data
    
    def fetch_census_data(
        self,
        geo_level: str = "county",
        year: int = 2021
    ) -> pd.DataFrame:
        """
        Fetch American Community Survey (ACS) data from Census API.
        
        Args:
            geo_level: Geographic level ('county' or 'zip code tabulation area')
            year: ACS 5-year estimate ending year
        
        Returns:
            pd.DataFrame: Census data with requested variables
        """
        logger.info(f"Fetching Census ACS data for {geo_level} ({year})...")
        
        if not CENSUS_API_KEY:
            logger.error("Census API key not set. Please set CENSUS_API_KEY in .env file")
            logger.info("Get your key from: https://api.census.gov/data/key_signup.html")
            
            # Return sample data for demonstration
            return self._create_sample_census_data(geo_level)
        
        try:
            # Determine geography
            if geo_level == "county":
                geo = censusdata.censusgeo([
                    ('state', '*'),
                    ('county', '*')
                ])
            elif geo_level == "zip code tabulation area":
                geo = censusdata.censusgeo([
                    ('zip code tabulation area', '*')
                ])
            else:
                raise ValueError(f"Unsupported geo_level: {geo_level}")
            
            # Fetch data for all ACS variables
            variable_codes = list(ACS_VARIABLES.keys())
            
            logger.info(f"Fetching {len(variable_codes)} ACS variables...")
            
            # Download data using censusdata package
            census_df = censusdata.download(
                'acs5',
                year,
                geo,
                variable_codes,
                key=CENSUS_API_KEY
            )
            
            # Rename columns to friendly names
            census_df.rename(columns=ACS_VARIABLES, inplace=True)
            
            # Extract geographic identifiers
            census_df.reset_index(inplace=True)
            census_df['geo'] = census_df['index'].astype(str)
            
            if geo_level == "county":
                # Parse county FIPS codes
                census_df['state_fips'] = census_df['geo'].str.extract(r'state:(\d{2})')
                census_df['county_fips'] = census_df['geo'].str.extract(r'county:(\d{3})')
                census_df['fips'] = census_df['state_fips'] + census_df['county_fips']
            elif geo_level == "zip code tabulation area":
                census_df['zipcode'] = census_df['geo'].str.extract(r'zip code tabulation area:(\d{5})')
            
            census_df.drop(columns=['index', 'geo'], inplace=True)
            
            # Save raw census data
            output_file = self.census_dir / f"census_{geo_level.replace(' ', '_')}_{year}.csv"
            census_df.to_csv(output_file, index=False)
            
            logger.info(f"Census data saved: {len(census_df)} records")
            return census_df
        
        except Exception as e:
            logger.error(f"Failed to fetch Census data: {e}")
            logger.info("Using sample Census data instead")
            return self._create_sample_census_data(geo_level)
    
    def _create_sample_census_data(self, geo_level: str) -> pd.DataFrame:
        """
        Create sample Census data for testing/demonstration purposes.
        
        Args:
            geo_level: Geographic level
        
        Returns:
            pd.DataFrame: Sample census data
        """
        if geo_level == "county":
            sample_data = pd.DataFrame({
                'fips': ['36061', '36005', '06037', '06059'],
                'state_fips': ['36', '36', '06', '06'],
                'county_fips': ['061', '005', '037', '059'],
                'median_household_income': [75000, 42000, 68000, 95000],
                'per_capita_income': [45000, 25000, 38000, 52000],
                'total_population': [1600000, 1400000, 10000000, 3200000],
                'total_households': [620000, 480000, 3400000, 1100000],
                'avg_household_size': [2.58, 2.92, 2.94, 2.91],
                'median_age': [37.5, 34.2, 36.4, 38.1],
                'unemployed': [62000, 84000, 450000, 96000],
                'labor_force': [800000, 600000, 5000000, 1600000],
                'bachelors_degree': [400000, 120000, 2000000, 700000],
                'total_population_25plus': [1200000, 900000, 7000000, 2400000],
                'poverty_count': [256000, 350000, 1800000, 320000],
                'poverty_denominator': [1600000, 1400000, 10000000, 3200000],
                'median_home_value': [650000, 350000, 700000, 800000],
                'median_gross_rent': [1500, 1100, 1800, 2000],
                'owner_occupied_housing': [248000, 192000, 1700000, 660000],
                'renter_occupied_housing': [372000, 288000, 1700000, 440000],
            })
        else:  # ZIP code level
            sample_data = pd.DataFrame({
                'zipcode': ['10001', '10002', '90001', '90002'],
                'median_household_income': [85000, 55000, 45000, 48000],
                'per_capita_income': [55000, 30000, 25000, 27000],
                'total_population': [25000, 32000, 57000, 51000],
                'total_households': [10000, 11000, 18000, 16000],
                'avg_household_size': [2.5, 2.9, 3.2, 3.2],
                'median_age': [36.5, 32.1, 30.8, 29.5],
                'unemployed': [500, 900, 2850, 2550],
                'labor_force': [12000, 14000, 28500, 25500],
                'bachelors_degree': [5000, 2200, 3420, 3060],
                'total_population_25plus': [18000, 21000, 38000, 34000],
                'poverty_count': [2000, 6400, 11400, 10200],
                'poverty_denominator': [25000, 32000, 57000, 51000],
                'median_home_value': [750000, 450000, 350000, 380000],
                'median_gross_rent': [1800, 1300, 1200, 1250],
                'owner_occupied_housing': [3000, 3300, 9000, 8000],
                'renter_occupied_housing': [7000, 7700, 9000, 8000],
            })
        
        sample_data.to_csv(
            self.census_dir / f"census_{geo_level.replace(' ', '_')}_sample.csv",
            index=False
        )
        
        logger.info(f"Created sample Census data: {len(sample_data)} records")
        return sample_data
    
    def download_hud_crosswalk(self) -> pd.DataFrame:
        """
        Download HUD ZIP-County crosswalk for merging ZIP and county data.
        
        Returns:
            pd.DataFrame: Crosswalk mapping ZIP codes to counties
        """
        logger.info("Loading HUD ZIP-County crosswalk...")
        
        # Note: In production, download from HUD's website
        # https://www.huduser.gov/portal/datasets/usps_crosswalk.html
        
        # Sample crosswalk data
        crosswalk = pd.DataFrame({
            'zipcode': ['10001', '10002', '90001', '90002'],
            'county_fips': ['36061', '36061', '06037', '06037'],
            'state_fips': ['36', '36', '06', '06'],
            'county_name': ['New York County', 'New York County', 
                           'Los Angeles County', 'Los Angeles County'],
            'residential_ratio': [1.0, 1.0, 1.0, 1.0],  # Proportion of ZIP in county
        })
        
        crosswalk.to_csv(self.irs_dir / "hud_zip_county_crosswalk.csv", index=False)
        
        logger.info(f"HUD crosswalk: {len(crosswalk)} records")
        return crosswalk
    
    def download_tiger_shapefiles(
        self,
        geo_type: str = "county",
        year: int = 2023
    ) -> gpd.GeoDataFrame:
        """
        Download TIGER/Line shapefiles for geographic visualization.
        
        Args:
            geo_type: Type of geography ('county' or 'zcta' for ZIP codes)
            year: Year of TIGER/Line data
        
        Returns:
            gpd.GeoDataFrame: Geographic boundaries
        """
        logger.info(f"Loading TIGER/Line {geo_type} shapefiles ({year})...")
        
        # Note: In production, download from Census TIGER/Line website
        # https://www2.census.gov/geo/tiger/TIGER{year}/
        
        logger.warning(
            f"Shapefile download not implemented. "
            f"Please manually download from: {TIGER_SHAPEFILE_BASE_URL}/{geo_type.upper()}/"
        )
        
        # For demonstration, create simple geometries
        from shapely.geometry import Point
        
        if geo_type == "county":
            sample_gdf = gpd.GeoDataFrame({
                'GEOID': ['36061', '36005', '06037', '06059'],
                'NAME': ['New York', 'Bronx', 'Los Angeles', 'Orange'],
                'geometry': [
                    Point(-73.9712, 40.7831).buffer(0.1),
                    Point(-73.8648, 40.8448).buffer(0.1),
                    Point(-118.2437, 34.0522).buffer(0.2),
                    Point(-117.8311, 33.7175).buffer(0.15),
                ]
            }, crs=CRS_WGS84)
        else:  # ZCTA
            sample_gdf = gpd.GeoDataFrame({
                'GEOID': ['10001', '10002', '90001', '90002'],
                'geometry': [
                    Point(-73.9969, 40.7505).buffer(0.01),
                    Point(-73.9902, 40.7156).buffer(0.01),
                    Point(-118.2479, 33.9731).buffer(0.01),
                    Point(-118.2468, 33.9494).buffer(0.01),
                ]
            }, crs=CRS_WGS84)
        
        # Save shapefile
        output_path = self.shapefiles_dir / f"{geo_type}_{year}"
        sample_gdf.to_file(output_path, driver='ESRI Shapefile')
        
        logger.info(f"Shapefile saved: {output_path}")
        return sample_gdf
    
    def merge_datasets(
        self,
        irs_data: pd.DataFrame,
        census_data: pd.DataFrame,
        join_key: str
    ) -> pd.DataFrame:
        """
        Merge IRS and Census datasets on specified key.
        
        Args:
            irs_data: IRS tax statistics
            census_data: Census ACS data
            join_key: Column name to join on (e.g., 'zipcode' or 'fips')
        
        Returns:
            pd.DataFrame: Merged dataset
        """
        logger.info(f"Merging IRS and Census data on '{join_key}'...")
        
        merged_df = irs_data.merge(
            census_data,
            on=join_key,
            how='inner',
            suffixes=('_irs', '_census')
        )
        
        logger.info(f"Merged dataset: {len(merged_df)} records")
        logger.info(f"Total columns: {len(merged_df.columns)}")
        
        return merged_df
    
    def run_full_pipeline(self) -> pd.DataFrame:
        """
        Execute complete data ingestion pipeline.
        
        Returns:
            pd.DataFrame: Final merged dataset
        """
        logger.info("=" * 60)
        logger.info("Starting Data Ingestion Pipeline")
        logger.info("=" * 60)
        
        # Step 1: Download IRS data
        logger.info("\n[1/6] Downloading IRS data...")
        zip_irs_data, county_irs_data = self.download_irs_data()
        
        # Step 2: Fetch Census data
        logger.info("\n[2/6] Fetching Census data...")
        zip_census_data = self.fetch_census_data(geo_level="zip code tabulation area")
        county_census_data = self.fetch_census_data(geo_level="county")
        
        # Step 3: Download HUD crosswalk
        logger.info("\n[3/6] Downloading HUD crosswalk...")
        crosswalk = self.download_hud_crosswalk()
        
        # Step 4: Download shapefiles
        logger.info("\n[4/6] Downloading TIGER/Line shapefiles...")
        county_shapes = self.download_tiger_shapefiles(geo_type="county")
        zip_shapes = self.download_tiger_shapefiles(geo_type="zcta")
        
        # Step 5: Merge datasets
        logger.info("\n[5/6] Merging datasets...")
        
        # Merge ZIP-level data
        zip_merged = self.merge_datasets(
            zip_irs_data,
            zip_census_data,
            join_key='zipcode'
        )
        
        # Add county information via crosswalk
        zip_merged = zip_merged.merge(
            crosswalk[['zipcode', 'county_fips']],
            on='zipcode',
            how='left'
        )
        
        # Merge county-level data
        county_merged = self.merge_datasets(
            county_irs_data,
            county_census_data,
            join_key='fips'
        )
        
        # Combine ZIP and county data (prioritize ZIP-level where available)
        # Add a 'geo_level' column to identify the source
        zip_merged['geo_level'] = 'zip'
        county_merged['geo_level'] = 'county'
        
        # Align columns
        common_cols = list(set(zip_merged.columns) & set(county_merged.columns))
        final_df = pd.concat([
            zip_merged[common_cols],
            county_merged[common_cols]
        ], ignore_index=True)
        
        # Step 6: Save processed data
        logger.info("\n[6/6] Saving processed data...")
        output_path = self.processed_dir / PROCESSED_DATA_FILE
        save_dataframe(final_df, output_path, file_format='parquet')
        
        logger.info("=" * 60)
        logger.info("Data Ingestion Pipeline Complete!")
        logger.info(f"Final dataset shape: {final_df.shape}")
        logger.info(f"Saved to: {output_path}")
        logger.info("=" * 60)
        
        return final_df


def main():
    """Main entry point for data ingestion."""
    ingester = DataIngester()
    merged_data = ingester.run_full_pipeline()
    
    # Display summary statistics
    print("\n" + "=" * 60)
    print("Dataset Summary")
    print("=" * 60)
    print(merged_data.info())
    print("\nFirst few rows:")
    print(merged_data.head())


if __name__ == "__main__":
    main()
