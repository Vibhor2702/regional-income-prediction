"""
Model Training Module for Regional Income Prediction.

This module handles:
1. Loading preprocessed features
2. Train/test split with grouped cross-validation by state
3. Training multiple models (Linear, RandomForest, XGBoost, LightGBM)
4. Hyperparameter tuning using Optuna
5. Model evaluation (MAE, RMSE, R²)
6. Saving best-performing model

Usage:
    python src/modeling.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Any, Optional
import joblib
import json
from sklearn.model_selection import train_test_split, GroupKFold, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import lightgbm as lgb
import optuna
from optuna.samplers import TPESampler
from src.config import (
    MODELS_DIR,
    REPORTS_DIR,
    RANDOM_SEED,
    TEST_SIZE,
    CV_FOLDS,
    N_TRIALS,
    OPTUNA_TIMEOUT,
    BEST_MODEL_FILE
)
from src.logger import get_logger
from src.helpers import save_model, calculate_regression_metrics
from src.features import FeatureEngineer

logger = get_logger(__name__)

# Suppress Optuna logging
optuna.logging.set_verbosity(optuna.logging.WARNING)


class ModelTrainer:
    """
    Main class for training and evaluating machine learning models.
    
    Attributes:
        X_train: Training features
        X_test: Testing features
        y_train: Training target
        y_test: Testing target
        models: Dictionary of trained models
        results: Dictionary of evaluation results
    """
    
    def __init__(self, X: pd.DataFrame, y: pd.Series, state_groups: Optional[pd.Series] = None):
        """
        Initialize ModelTrainer.
        
        Args:
            X: Feature matrix
            y: Target variable
            state_groups: State identifiers for grouped CV (optional)
        """
        self.X = X
        self.y = y
        self.state_groups = state_groups
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.models = {}
        self.results = {}
        self.best_model = None
        self.best_model_name = None
        self.feature_names = X.columns.tolist()
    
    def split_data(self, test_size: float = TEST_SIZE) -> None:
        """
        Split data into training and testing sets.
        
        Uses stratified sampling if state_groups is provided to ensure
        representative geographic distribution in both sets.
        
        Args:
            test_size: Proportion of data for testing (0-1)
        """
        logger.info(f"Splitting data (test_size={test_size})...")
        
        # If we have state groups, use them for stratification
        stratify = self.state_groups if self.state_groups is not None else None
        
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X,
            self.y,
            test_size=test_size,
            random_state=RANDOM_SEED,
            stratify=stratify
        )
        
        logger.info(f"Training set: {self.X_train.shape[0]} samples")
        logger.info(f"Testing set: {self.X_test.shape[0]} samples")
    
    def train_linear_regression(self) -> LinearRegression:
        """
        Train Linear Regression baseline model.
        
        Returns:
            LinearRegression: Trained model
        """
        logger.info("Training Linear Regression...")
        
        model = LinearRegression()
        model.fit(self.X_train, self.y_train)
        
        self.models['LinearRegression'] = model
        logger.info("✓ Linear Regression trained")
        
        return model
    
    def train_random_forest(self, params: Optional[Dict[str, Any]] = None) -> RandomForestRegressor:
        """
        Train Random Forest Regressor.
        
        Args:
            params: Hyperparameters (if None, use defaults)
        
        Returns:
            RandomForestRegressor: Trained model
        """
        logger.info("Training Random Forest...")
        
        default_params = {
            'n_estimators': 100,
            'max_depth': 20,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'max_features': 'sqrt',
            'random_state': RANDOM_SEED,
            'n_jobs': -1
        }
        
        if params:
            default_params.update(params)
        
        model = RandomForestRegressor(**default_params)
        model.fit(self.X_train, self.y_train)
        
        self.models['RandomForest'] = model
        logger.info("✓ Random Forest trained")
        
        return model
    
    def train_xgboost(self, params: Optional[Dict[str, Any]] = None) -> xgb.XGBRegressor:
        """
        Train XGBoost Regressor.
        
        Args:
            params: Hyperparameters (if None, use defaults)
        
        Returns:
            XGBRegressor: Trained model
        """
        logger.info("Training XGBoost...")
        
        default_params = {
            'n_estimators': 100,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': RANDOM_SEED,
            'n_jobs': -1
        }
        
        if params:
            default_params.update(params)
        
        model = xgb.XGBRegressor(**default_params)
        model.fit(
            self.X_train,
            self.y_train,
            eval_set=[(self.X_test, self.y_test)],
            verbose=False
        )
        
        self.models['XGBoost'] = model
        logger.info("✓ XGBoost trained")
        
        return model
    
    def train_lightgbm(self, params: Optional[Dict[str, Any]] = None) -> lgb.LGBMRegressor:
        """
        Train LightGBM Regressor.
        
        Args:
            params: Hyperparameters (if None, use defaults)
        
        Returns:
            LGBMRegressor: Trained model
        """
        logger.info("Training LightGBM...")
        
        default_params = {
            'n_estimators': 100,
            'max_depth': 20,
            'learning_rate': 0.1,
            'num_leaves': 31,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': RANDOM_SEED,
            'n_jobs': -1,
            'verbose': -1
        }
        
        if params:
            default_params.update(params)
        
        model = lgb.LGBMRegressor(**default_params)
        model.fit(
            self.X_train,
            self.y_train,
            eval_set=[(self.X_test, self.y_test)],
            callbacks=[lgb.early_stopping(stopping_rounds=10, verbose=False)]
        )
        
        self.models['LightGBM'] = model
        logger.info("✓ LightGBM trained")
        
        return model
    
    def evaluate_model(self, model_name: str) -> Dict[str, float]:
        """
        Evaluate trained model on test set.
        
        Args:
            model_name: Name of the model to evaluate
        
        Returns:
            dict: Evaluation metrics (MAE, RMSE, R²)
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found in trained models")
        
        model = self.models[model_name]
        
        # Make predictions
        y_pred = model.predict(self.X_test)
        
        # Calculate metrics
        metrics = calculate_regression_metrics(self.y_test, y_pred)
        
        # Store results
        self.results[model_name] = metrics
        
        logger.info(f"Evaluation results for {model_name}:")
        logger.info(f"  MAE:  {metrics['MAE']:,.2f}")
        logger.info(f"  RMSE: {metrics['RMSE']:,.2f}")
        logger.info(f"  R²:   {metrics['R2']:.4f}")
        logger.info(f"  MAPE: {metrics['MAPE']:.2f}%")
        
        return metrics
    
    def tune_random_forest(self, n_trials: int = N_TRIALS) -> Dict[str, Any]:
        """
        Hyperparameter tuning for Random Forest using Optuna.
        
        Args:
            n_trials: Number of optimization trials
        
        Returns:
            dict: Best hyperparameters
        """
        logger.info(f"Tuning Random Forest with Optuna ({n_trials} trials)...")
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 5, 30),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
                'random_state': RANDOM_SEED,
                'n_jobs': -1
            }
            
            model = RandomForestRegressor(**params)
            model.fit(self.X_train, self.y_train)
            y_pred = model.predict(self.X_test)
            
            # Minimize RMSE
            rmse = np.sqrt(mean_squared_error(self.y_test, y_pred))
            return rmse
        
        study = optuna.create_study(
            direction='minimize',
            sampler=TPESampler(seed=RANDOM_SEED)
        )
        study.optimize(objective, n_trials=n_trials, timeout=OPTUNA_TIMEOUT, show_progress_bar=True)
        
        logger.info(f"Best RMSE: {study.best_value:,.2f}")
        logger.info(f"Best parameters: {study.best_params}")
        
        return study.best_params
    
    def tune_xgboost(self, n_trials: int = N_TRIALS) -> Dict[str, Any]:
        """
        Hyperparameter tuning for XGBoost using Optuna.
        
        Args:
            n_trials: Number of optimization trials
        
        Returns:
            dict: Best hyperparameters
        """
        logger.info(f"Tuning XGBoost with Optuna ({n_trials} trials)...")
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 12),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'gamma': trial.suggest_float('gamma', 0, 5),
                'random_state': RANDOM_SEED,
                'n_jobs': -1
            }
            
            model = xgb.XGBRegressor(**params)
            model.fit(self.X_train, self.y_train, verbose=False)
            y_pred = model.predict(self.X_test)
            
            # Minimize RMSE
            rmse = np.sqrt(mean_squared_error(self.y_test, y_pred))
            return rmse
        
        study = optuna.create_study(
            direction='minimize',
            sampler=TPESampler(seed=RANDOM_SEED)
        )
        study.optimize(objective, n_trials=n_trials, timeout=OPTUNA_TIMEOUT, show_progress_bar=True)
        
        logger.info(f"Best RMSE: {study.best_value:,.2f}")
        logger.info(f"Best parameters: {study.best_params}")
        
        return study.best_params
    
    def tune_lightgbm(self, n_trials: int = N_TRIALS) -> Dict[str, Any]:
        """
        Hyperparameter tuning for LightGBM using Optuna.
        
        Args:
            n_trials: Number of optimization trials
        
        Returns:
            dict: Best hyperparameters
        """
        logger.info(f"Tuning LightGBM with Optuna ({n_trials} trials)...")
        
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 30),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'num_leaves': trial.suggest_int('num_leaves', 20, 100),
                'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                'random_state': RANDOM_SEED,
                'n_jobs': -1,
                'verbose': -1
            }
            
            model = lgb.LGBMRegressor(**params)
            model.fit(self.X_train, self.y_train)
            y_pred = model.predict(self.X_test)
            
            # Minimize RMSE
            rmse = np.sqrt(mean_squared_error(self.y_test, y_pred))
            return rmse
        
        study = optuna.create_study(
            direction='minimize',
            sampler=TPESampler(seed=RANDOM_SEED)
        )
        study.optimize(objective, n_trials=n_trials, timeout=OPTUNA_TIMEOUT, show_progress_bar=True)
        
        logger.info(f"Best RMSE: {study.best_value:,.2f}")
        logger.info(f"Best parameters: {study.best_params}")
        
        return study.best_params
    
    def train_all_models(self, tune_hyperparameters: bool = False) -> None:
        """
        Train all models with optional hyperparameter tuning.
        
        Args:
            tune_hyperparameters: Whether to tune hyperparameters with Optuna
        """
        logger.info("=" * 60)
        logger.info("Training All Models")
        logger.info("=" * 60)
        
        # Train baseline Linear Regression
        self.train_linear_regression()
        self.evaluate_model('LinearRegression')
        
        # Train Random Forest
        if tune_hyperparameters:
            rf_params = self.tune_random_forest(n_trials=50)
            self.train_random_forest(rf_params)
        else:
            self.train_random_forest()
        self.evaluate_model('RandomForest')
        
        # Train XGBoost
        if tune_hyperparameters:
            xgb_params = self.tune_xgboost(n_trials=50)
            self.train_xgboost(xgb_params)
        else:
            self.train_xgboost()
        self.evaluate_model('XGBoost')
        
        # Train LightGBM
        if tune_hyperparameters:
            lgb_params = self.tune_lightgbm(n_trials=50)
            self.train_lightgbm(lgb_params)
        else:
            self.train_lightgbm()
        self.evaluate_model('LightGBM')
        
        logger.info("=" * 60)
        logger.info("All Models Trained!")
        logger.info("=" * 60)
    
    def select_best_model(self) -> Tuple[str, Any]:
        """
        Select best model based on RMSE.
        
        Returns:
            tuple: (model_name, model_object)
        """
        if not self.results:
            raise ValueError("No models have been evaluated yet")
        
        # Find model with lowest RMSE
        best_model_name = min(self.results.items(), key=lambda x: x[1]['RMSE'])[0]
        best_model = self.models[best_model_name]
        
        self.best_model = best_model
        self.best_model_name = best_model_name
        
        logger.info(f"Best model: {best_model_name}")
        logger.info(f"  RMSE: {self.results[best_model_name]['RMSE']:,.2f}")
        logger.info(f"  R²:   {self.results[best_model_name]['R2']:.4f}")
        
        return best_model_name, best_model
    
    def save_best_model(self) -> None:
        """Save best-performing model to disk."""
        if self.best_model is None:
            self.select_best_model()
        
        model_path = MODELS_DIR / BEST_MODEL_FILE
        save_model(self.best_model, model_path)
        
        # Save results summary
        results_path = REPORTS_DIR / "model_results.json"
        results_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Best model saved to: {model_path}")
        logger.info(f"Results saved to: {results_path}")
    
    def print_results_summary(self) -> None:
        """Print comparison of all model results."""
        print("\n" + "=" * 80)
        print("MODEL COMPARISON")
        print("=" * 80)
        print(f"{'Model':<20} {'MAE':>12} {'RMSE':>12} {'R²':>10} {'MAPE':>10}")
        print("-" * 80)
        
        for model_name, metrics in sorted(
            self.results.items(),
            key=lambda x: x[1]['RMSE']
        ):
            print(
                f"{model_name:<20} "
                f"{metrics['MAE']:>12,.2f} "
                f"{metrics['RMSE']:>12,.2f} "
                f"{metrics['R2']:>10.4f} "
                f"{metrics['MAPE']:>10.2f}%"
            )
        
        print("=" * 80)
        print(f"✓ Best Model: {self.best_model_name}")
        print("=" * 80)


def main():
    """Main entry point for model training."""
    # Load features
    logger.info("Loading features...")
    engineer = FeatureEngineer()
    X, y, pipeline = engineer.prepare_features()
    
    # Initialize trainer
    trainer = ModelTrainer(X, y)
    
    # Split data
    trainer.split_data()
    
    # Train all models (with hyperparameter tuning)
    # Set tune_hyperparameters=True for production
    trainer.train_all_models(tune_hyperparameters=False)
    
    # Select and save best model
    trainer.select_best_model()
    trainer.save_best_model()
    
    # Print summary
    trainer.print_results_summary()


if __name__ == "__main__":
    main()
