"""
Train models with research-based ensemble stacking.

This script implements the stacked ensemble approach from academic research:
- Combines XGBoost, LightGBM, and Random Forest as base learners
- Uses Ridge regression as meta-learner
- Expected 3-5% accuracy improvement over single models

Reference: Verme, P. (2025). "Predicting Poverty." World Bank Economic Review.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.features import FeatureEngineer
from src.modeling import ModelTrainer
from src.logger import get_logger

logger = get_logger(__name__)


def main():
    """Train models with ensemble stacking enabled."""
    print("=" * 80)
    print("RESEARCH-BASED MODEL TRAINING WITH ENSEMBLE STACKING")
    print("=" * 80)
    print()
    print("Enhancement: Stacked ensemble combining XGBoost + LightGBM + Random Forest")
    print("Expected improvement: +3-5% accuracy over single models")
    print("Reference: Verme, P. (2025). World Bank Economic Review")
    print()
    print("=" * 80)
    print()
    
    # Load features
    logger.info("Loading preprocessed features...")
    engineer = FeatureEngineer()
    X, y, pipeline = engineer.prepare_features()
    
    logger.info(f"Features loaded: {X.shape[0]} samples, {X.shape[1]} features")
    print()
    
    # Initialize trainer
    logger.info("Initializing model trainer...")
    trainer = ModelTrainer(X, y)
    
    # Split data
    trainer.split_data()
    print()
    
    # Train all models (including ensemble)
    logger.info("Training all models with ensemble stacking...")
    trainer.train_all_models(tune_hyperparameters=False, use_ensemble=True)
    print()
    
    # Select and save best model
    logger.info("Selecting best model...")
    best_name, best_model = trainer.select_best_model()
    print()
    
    # Save best model
    logger.info("Saving best model...")
    trainer.save_best_model()
    print()
    
    # Print comparison summary
    trainer.print_results_summary()
    
    # Additional ensemble analysis
    if 'StackedEnsemble' in trainer.results:
        ensemble_r2 = trainer.results['StackedEnsemble']['R2']
        xgb_r2 = trainer.results.get('XGBoost', {}).get('R2', 0)
        
        improvement = (ensemble_r2 - xgb_r2) * 100
        
        print()
        print("=" * 80)
        print("ENSEMBLE PERFORMANCE ANALYSIS")
        print("=" * 80)
        print(f"XGBoost R²:          {xgb_r2:.4f}")
        print(f"Ensemble R²:         {ensemble_r2:.4f}")
        print(f"Improvement:         {improvement:.2f} percentage points")
        print()
        
        if best_name == 'StackedEnsemble':
            print("✓ Stacked Ensemble selected as best model!")
            print("  Research-based enhancement successfully improved performance.")
        else:
            print(f"✓ {best_name} selected as best model.")
            print("  Ensemble provides alternative with different characteristics.")
        
        print("=" * 80)


if __name__ == "__main__":
    main()
