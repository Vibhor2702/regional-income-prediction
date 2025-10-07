"""
Model Interpretation Module for Regional Income Prediction.

This module handles:
1. Loading trained model and test data
2. Computing SHAP values for feature importance
3. Generating global feature importance plots
4. Creating SHAP summary plots (beeswarm)
5. Generating SHAP dependence plots for top features
6. Computing permutation importance
7. Saving all visualizations to reports directory

Usage:
    python src/interpret.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Optional, Tuple
import shap
from sklearn.inspection import permutation_importance
from src.config import (
    MODELS_DIR,
    FEATURE_IMPORTANCE_DIR,
    BEST_MODEL_FILE,
    RANDOM_SEED
)
from src.logger import get_logger
from src.helpers import load_model
from src.features import FeatureEngineer

logger = get_logger(__name__)

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.figsize'] = (10, 6)


class ModelInterpreter:
    """
    Main class for model interpretation and feature importance analysis.
    
    Attributes:
        model: Trained model
        X_test: Test features
        y_test: Test target
        feature_names: List of feature names
        shap_values: SHAP values for test set
        explainer: SHAP explainer object
    """
    
    def __init__(
        self,
        model=None,
        X_test: Optional[pd.DataFrame] = None,
        y_test: Optional[pd.Series] = None
    ):
        """
        Initialize ModelInterpreter.
        
        Args:
            model: Trained model (if None, load from disk)
            X_test: Test features (if None, prepare from scratch)
            y_test: Test target (if None, prepare from scratch)
        """
        self.model = model
        self.X_test = X_test
        self.y_test = y_test
        self.feature_names = None
        self.shap_values = None
        self.explainer = None
        
        # Create output directory
        FEATURE_IMPORTANCE_DIR.mkdir(parents=True, exist_ok=True)
    
    def load_model_and_data(self) -> None:
        """Load trained model and prepare test data."""
        logger.info("Loading model and preparing data...")
        
        # Load model if not provided
        if self.model is None:
            model_path = MODELS_DIR / BEST_MODEL_FILE
            self.model = load_model(model_path)
            logger.info(f"Loaded model from {model_path}")
        
        # Prepare features if not provided
        if self.X_test is None or self.y_test is None:
            logger.info("Preparing features...")
            engineer = FeatureEngineer()
            X, y, _ = engineer.prepare_features()
            
            # Use last 20% as test set
            split_idx = int(len(X) * 0.8)
            self.X_test = X.iloc[split_idx:]
            self.y_test = y.iloc[split_idx:]
            
            logger.info(f"Test set: {len(self.X_test)} samples")
        
        self.feature_names = self.X_test.columns.tolist()
    
    def compute_shap_values(self, sample_size: Optional[int] = 100) -> np.ndarray:
        """
        Compute SHAP values for model predictions.
        
        Uses TreeExplainer for tree-based models (faster)
        or KernelExplainer for other models.
        
        Args:
            sample_size: Number of samples to use for SHAP computation
                        (use smaller value for faster computation)
        
        Returns:
            np.ndarray: SHAP values
        """
        logger.info("Computing SHAP values...")
        
        # Sample data if necessary (SHAP can be slow on large datasets)
        if len(self.X_test) > sample_size:
            logger.info(f"Sampling {sample_size} instances for SHAP analysis")
            sample_indices = np.random.RandomState(RANDOM_SEED).choice(
                len(self.X_test),
                size=sample_size,
                replace=False
            )
            X_sample = self.X_test.iloc[sample_indices]
        else:
            X_sample = self.X_test
        
        # Determine appropriate explainer based on model type
        model_type = type(self.model).__name__
        
        try:
            if 'XGB' in model_type or 'LightGBM' in model_type or 'RandomForest' in model_type:
                # Use TreeExplainer for tree-based models
                logger.info(f"Using TreeExplainer for {model_type}")
                self.explainer = shap.TreeExplainer(self.model)
                self.shap_values = self.explainer.shap_values(X_sample)
            else:
                # Use KernelExplainer for other models
                logger.info(f"Using KernelExplainer for {model_type}")
                
                # Use smaller background dataset for kernel explainer
                background = shap.sample(self.X_test, min(50, len(self.X_test)))
                self.explainer = shap.KernelExplainer(
                    self.model.predict,
                    background
                )
                self.shap_values = self.explainer.shap_values(X_sample)
        
        except Exception as e:
            logger.warning(f"SHAP computation failed with {model_type}: {e}")
            logger.info("Falling back to permutation importance only")
            self.shap_values = None
            return None
        
        logger.info(f"SHAP values computed. Shape: {self.shap_values.shape}")
        return self.shap_values
    
    def plot_shap_summary(self, save_path: Optional[Path] = None) -> None:
        """
        Create SHAP summary plot (beeswarm plot).
        
        This plot shows the distribution of SHAP values for each feature,
        helping identify which features are most important and how they
        impact predictions.
        
        Args:
            save_path: Path to save plot (optional)
        """
        if self.shap_values is None:
            logger.warning("SHAP values not computed. Skipping summary plot.")
            return
        
        logger.info("Generating SHAP summary plot...")
        
        plt.figure(figsize=(12, 8))
        shap.summary_plot(
            self.shap_values,
            self.X_test if len(self.X_test) <= 100 else self.X_test.iloc[:100],
            feature_names=self.feature_names,
            show=False
        )
        plt.tight_layout()
        
        if save_path is None:
            save_path = FEATURE_IMPORTANCE_DIR / "shap_summary.png"
        
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
        
        logger.info(f"SHAP summary plot saved to {save_path}")
    
    def plot_shap_bar(self, save_path: Optional[Path] = None, top_n: int = 20) -> None:
        """
        Create SHAP bar plot showing mean absolute SHAP values.
        
        Args:
            save_path: Path to save plot (optional)
            top_n: Number of top features to display
        """
        if self.shap_values is None:
            logger.warning("SHAP values not computed. Skipping bar plot.")
            return
        
        logger.info("Generating SHAP bar plot...")
        
        plt.figure(figsize=(10, 8))
        shap.summary_plot(
            self.shap_values,
            self.X_test if len(self.X_test) <= 100 else self.X_test.iloc[:100],
            feature_names=self.feature_names,
            plot_type="bar",
            max_display=top_n,
            show=False
        )
        plt.tight_layout()
        
        if save_path is None:
            save_path = FEATURE_IMPORTANCE_DIR / "shap_bar.png"
        
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
        
        logger.info(f"SHAP bar plot saved to {save_path}")
    
    def plot_shap_dependence(
        self,
        feature_names: List[str],
        save_dir: Optional[Path] = None
    ) -> None:
        """
        Create SHAP dependence plots for specified features.
        
        Dependence plots show how a single feature affects predictions
        across its entire range of values.
        
        Args:
            feature_names: List of feature names to plot
            save_dir: Directory to save plots (optional)
        """
        if self.shap_values is None:
            logger.warning("SHAP values not computed. Skipping dependence plots.")
            return
        
        logger.info(f"Generating SHAP dependence plots for {len(feature_names)} features...")
        
        if save_dir is None:
            save_dir = FEATURE_IMPORTANCE_DIR / "dependence"
        save_dir.mkdir(parents=True, exist_ok=True)
        
        X_sample = self.X_test if len(self.X_test) <= 100 else self.X_test.iloc[:100]
        
        for feature in feature_names:
            if feature not in self.feature_names:
                logger.warning(f"Feature '{feature}' not found. Skipping.")
                continue
            
            try:
                plt.figure(figsize=(10, 6))
                shap.dependence_plot(
                    feature,
                    self.shap_values,
                    X_sample,
                    feature_names=self.feature_names,
                    show=False
                )
                plt.tight_layout()
                
                save_path = save_dir / f"dependence_{feature}.png"
                plt.savefig(save_path, bbox_inches='tight')
                plt.close()
                
                logger.debug(f"Saved dependence plot for {feature}")
            
            except Exception as e:
                logger.warning(f"Failed to create dependence plot for {feature}: {e}")
    
    def compute_permutation_importance(
        self,
        n_repeats: int = 10,
        save_path: Optional[Path] = None
    ) -> pd.DataFrame:
        """
        Compute permutation importance for features.
        
        Permutation importance measures the decrease in model performance
        when a feature's values are randomly shuffled.
        
        Args:
            n_repeats: Number of times to permute each feature
            save_path: Path to save results (optional)
        
        Returns:
            pd.DataFrame: Feature importance scores
        """
        logger.info("Computing permutation importance...")
        
        result = permutation_importance(
            self.model,
            self.X_test,
            self.y_test,
            n_repeats=n_repeats,
            random_state=RANDOM_SEED,
            n_jobs=-1
        )
        
        # Create DataFrame with results
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance_mean': result.importances_mean,
            'importance_std': result.importances_std
        }).sort_values('importance_mean', ascending=False)
        
        if save_path is None:
            save_path = FEATURE_IMPORTANCE_DIR / "permutation_importance.csv"
        
        importance_df.to_csv(save_path, index=False)
        logger.info(f"Permutation importance saved to {save_path}")
        
        return importance_df
    
    def plot_permutation_importance(
        self,
        importance_df: pd.DataFrame,
        save_path: Optional[Path] = None,
        top_n: int = 20
    ) -> None:
        """
        Plot permutation importance with error bars.
        
        Args:
            importance_df: DataFrame with importance scores
            save_path: Path to save plot (optional)
            top_n: Number of top features to display
        """
        logger.info("Plotting permutation importance...")
        
        # Select top N features
        top_features = importance_df.head(top_n)
        
        plt.figure(figsize=(10, 8))
        plt.barh(
            range(len(top_features)),
            top_features['importance_mean'],
            xerr=top_features['importance_std'],
            color='steelblue',
            edgecolor='black',
            alpha=0.7
        )
        plt.yticks(range(len(top_features)), top_features['feature'])
        plt.xlabel('Permutation Importance (decrease in R²)')
        plt.ylabel('Feature')
        plt.title(f'Top {top_n} Features by Permutation Importance')
        plt.gca().invert_yaxis()
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        if save_path is None:
            save_path = FEATURE_IMPORTANCE_DIR / "permutation_importance_plot.png"
        
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Permutation importance plot saved to {save_path}")
    
    def get_top_features(self, n: int = 10) -> List[str]:
        """
        Get top N most important features based on mean absolute SHAP values.
        
        Args:
            n: Number of top features to return
        
        Returns:
            list: Top N feature names
        """
        if self.shap_values is None:
            logger.warning("SHAP values not computed. Cannot determine top features.")
            return []
        
        # Calculate mean absolute SHAP values
        mean_abs_shap = np.abs(self.shap_values).mean(axis=0)
        
        # Get indices of top N features
        top_indices = np.argsort(mean_abs_shap)[-n:][::-1]
        
        top_features = [self.feature_names[i] for i in top_indices]
        
        logger.info(f"Top {n} features: {', '.join(top_features)}")
        return top_features
    
    def generate_all_reports(self) -> None:
        """Generate all interpretation reports and visualizations."""
        logger.info("=" * 60)
        logger.info("Generating Model Interpretation Reports")
        logger.info("=" * 60)
        
        # Load model and data
        logger.info("\n[1/6] Loading model and data...")
        self.load_model_and_data()
        
        # Compute SHAP values
        logger.info("\n[2/6] Computing SHAP values...")
        self.compute_shap_values(sample_size=100)
        
        # Generate SHAP plots
        if self.shap_values is not None:
            logger.info("\n[3/6] Generating SHAP summary plot...")
            self.plot_shap_summary()
            
            logger.info("\n[4/6] Generating SHAP bar plot...")
            self.plot_shap_bar(top_n=20)
            
            logger.info("\n[5/6] Generating SHAP dependence plots...")
            top_features = self.get_top_features(n=5)
            self.plot_shap_dependence(top_features)
        else:
            logger.warning("Skipping SHAP plots (SHAP values not available)")
        
        # Compute and plot permutation importance
        logger.info("\n[6/6] Computing permutation importance...")
        importance_df = self.compute_permutation_importance(n_repeats=10)
        self.plot_permutation_importance(importance_df, top_n=20)
        
        logger.info("=" * 60)
        logger.info("Model Interpretation Complete!")
        logger.info(f"Reports saved to: {FEATURE_IMPORTANCE_DIR}")
        logger.info("=" * 60)


def main():
    """Main entry point for model interpretation."""
    interpreter = ModelInterpreter()
    interpreter.generate_all_reports()
    
    # Print top features
    if interpreter.shap_values is not None:
        print("\n" + "=" * 60)
        print("TOP 10 MOST IMPORTANT FEATURES")
        print("=" * 60)
        top_features = interpreter.get_top_features(n=10)
        for i, feature in enumerate(top_features, 1):
            print(f"{i:2d}. {feature}")
        print("=" * 60)


if __name__ == "__main__":
    main()
