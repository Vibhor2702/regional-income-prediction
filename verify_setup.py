"""
Project Setup Verification Script

Run this script to verify that your environment is correctly set up
and all dependencies are properly installed.

Usage:
    python verify_setup.py
"""

import sys
from pathlib import Path

print("=" * 70)
print("Regional Income Prediction - Setup Verification")
print("=" * 70)

# Check Python version
print("\n[1/8] Checking Python version...")
required_version = (3, 11)
current_version = sys.version_info[:2]

if current_version >= required_version:
    print(f"✓ Python {current_version[0]}.{current_version[1]} (meets requirement >= 3.11)")
else:
    print(f"✗ Python {current_version[0]}.{current_version[1]} (requires >= 3.11)")
    sys.exit(1)

# Check directory structure
print("\n[2/8] Checking directory structure...")
base_dir = Path(__file__).parent
required_dirs = [
    "app",
    "data_raw",
    "data_processed",
    "models",
    "notebooks",
    "reports",
    "src",
    "tests",
]

missing_dirs = []
for dir_name in required_dirs:
    dir_path = base_dir / dir_name
    if dir_path.exists():
        print(f"✓ {dir_name}/")
    else:
        print(f"✗ {dir_name}/ (missing)")
        missing_dirs.append(dir_name)

if missing_dirs:
    print(f"\n⚠ Missing directories: {', '.join(missing_dirs)}")
else:
    print("\n✓ All directories present")

# Check required files
print("\n[3/8] Checking required files...")
required_files = [
    "requirements.txt",
    "Dockerfile",
    "Makefile",
    ".env.example",
    "README.md",
    "src/config.py",
    "src/data_ingest.py",
    "src/features.py",
    "src/modeling.py",
    "src/interpret.py",
    "app/streamlit_app.py",
]

missing_files = []
for file_name in required_files:
    file_path = base_dir / file_name
    if file_path.exists():
        print(f"✓ {file_name}")
    else:
        print(f"✗ {file_name} (missing)")
        missing_files.append(file_name)

if missing_files:
    print(f"\n⚠ Missing files: {', '.join(missing_files)}")

# Check Python packages
print("\n[4/8] Checking Python packages...")
required_packages = [
    "pandas",
    "numpy",
    "scikit-learn",
    "xgboost",
    "lightgbm",
    "optuna",
    "shap",
    "streamlit",
    "plotly",
    "matplotlib",
    "seaborn",
]

missing_packages = []
for package in required_packages:
    try:
        __import__(package)
        print(f"✓ {package}")
    except ImportError:
        print(f"✗ {package} (not installed)")
        missing_packages.append(package)

if missing_packages:
    print(f"\n⚠ Missing packages: {', '.join(missing_packages)}")
    print("   Run: pip install -r requirements.txt")

# Check geospatial packages (optional but recommended)
print("\n[5/8] Checking geospatial packages (optional)...")
geo_packages = ["geopandas", "shapely", "fiona", "pyproj"]

missing_geo = []
for package in geo_packages:
    try:
        __import__(package)
        print(f"✓ {package}")
    except ImportError:
        print(f"⚠ {package} (optional, not installed)")
        missing_geo.append(package)

# Check environment configuration
print("\n[6/8] Checking environment configuration...")
env_file = base_dir / ".env"
env_example = base_dir / ".env.example"

if env_file.exists():
    print("✓ .env file exists")
    
    # Check for Census API key
    with open(env_file, 'r') as f:
        content = f.read()
        if "CENSUS_API_KEY=" in content:
            if "your_census_api_key_here" in content:
                print("⚠ Census API key not set (using placeholder)")
            else:
                print("✓ Census API key configured")
        else:
            print("✗ CENSUS_API_KEY not found in .env")
else:
    print("⚠ .env file not found")
    if env_example.exists():
        print("  Run: copy .env.example .env")
        print("  Then add your Census API key")

# Check src module imports
print("\n[7/8] Checking src module imports...")
try:
    sys.path.insert(0, str(base_dir / "src"))
    
    from src import config
    print("✓ src.config")
    
    from src import logger
    print("✓ src.logger")
    
    from src import helpers
    print("✓ src.helpers")
    
    print("✓ All src modules can be imported")
except Exception as e:
    print(f"✗ Error importing src modules: {e}")

# Summary
print("\n[8/8] Verification Summary")
print("=" * 70)

all_good = (
    not missing_dirs and
    not missing_files and
    not missing_packages
)

if all_good:
    print("✓ Setup verification PASSED")
    print("\nYour environment is ready!")
    print("\nNext steps:")
    print("  1. Configure .env with your Census API key")
    print("  2. Run: python src/data_ingest.py")
    print("  3. Run: python src/modeling.py")
    print("  4. Run: streamlit run app/streamlit_app.py")
    print("\nOr use Makefile:")
    print("  make prepare")
    print("  make train")
    print("  make dashboard")
else:
    print("⚠ Setup verification found issues")
    print("\nPlease address the items marked with ✗ or ⚠ above")
    
    if missing_packages:
        print("\nTo install missing packages:")
        print("  pip install -r requirements.txt")
    
    if not env_file.exists():
        print("\nTo create .env file:")
        print("  copy .env.example .env")
        print("  Edit .env and add your Census API key")

print("=" * 70)
print("\nFor detailed setup instructions, see QUICKSTART.md")
print("For full documentation, see README.md")
print("=" * 70)
