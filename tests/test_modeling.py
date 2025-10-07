"""
Unit tests for modeling module.

Tests model training, evaluation, and prediction functionality.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modeling import ModelTrainer
from src.helpers import calculate_regression_metrics


class TestModelTrainer:
    """Test suite for ModelTrainer class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample dataset for testing."""
        np.random.seed(42)
        n_samples = 100
        n_features = 10
        
        X = pd.DataFrame(
            np.random.randn(n_samples, n_features),
            columns=[f'feature_{i}' for i in range(n_features)]
        )
        
        # Create target with some relationship to features
        y = pd.Series(
            X['feature_0'] * 2 + X['feature_1'] * 1.5 + np.random.randn(n_samples) * 0.5,
            name='target'
        )
        
        return X, y
    
    @pytest.fixture
    def trainer(self, sample_data):
        """Create ModelTrainer instance."""
        X, y = sample_data
        return ModelTrainer(X, y)
    
    def test_split_data(self, trainer):
        """Test train/test split."""
        trainer.split_data(test_size=0.2)
        
        assert trainer.X_train is not None
        assert trainer.X_test is not None
        assert trainer.y_train is not None
        assert trainer.y_test is not None
        
        # Check sizes
        total_size = len(trainer.X)
        assert len(trainer.X_train) == int(total_size * 0.8)
        assert len(trainer.X_test) == int(total_size * 0.2)
    
    def test_train_linear_regression(self, trainer):
        """Test Linear Regression training."""
        trainer.split_data()
        model = trainer.train_linear_regression()
        
        assert model is not None
        assert hasattr(model, 'coef_')
        assert hasattr(model, 'intercept_')
        
        # Test prediction
        y_pred = model.predict(trainer.X_test)
        assert len(y_pred) == len(trainer.y_test)
    
    def test_train_random_forest(self, trainer):
        """Test Random Forest training."""
        trainer.split_data()
        model = trainer.train_random_forest()
        
        assert model is not None
        assert hasattr(model, 'feature_importances_')
        
        # Test prediction
        y_pred = model.predict(trainer.X_test)
        assert len(y_pred) == len(trainer.y_test)
    
    def test_evaluate_model(self, trainer):
        """Test model evaluation."""
        trainer.split_data()
        trainer.train_linear_regression()
        
        metrics = trainer.evaluate_model('LinearRegression')
        
        assert 'MAE' in metrics
        assert 'RMSE' in metrics
        assert 'R2' in metrics
        assert 'MAPE' in metrics
        
        # Check that metrics are reasonable
        assert metrics['MAE'] >= 0
        assert metrics['RMSE'] >= 0
        assert -1 <= metrics['R2'] <= 1
    
    def test_select_best_model(self, trainer):
        """Test best model selection."""
        trainer.split_data()
        trainer.train_linear_regression()
        trainer.evaluate_model('LinearRegression')
        
        trainer.train_random_forest({'n_estimators': 10})
        trainer.evaluate_model('RandomForest')
        
        best_name, best_model = trainer.select_best_model()
        
        assert best_name in ['LinearRegression', 'RandomForest']
        assert best_model is not None


def test_calculate_regression_metrics():
    """Test regression metrics calculation."""
    y_true = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y_pred = np.array([1.1, 2.2, 2.9, 4.1, 4.8])
    
    metrics = calculate_regression_metrics(y_true, y_pred)
    
    assert 'MAE' in metrics
    assert 'RMSE' in metrics
    assert 'R2' in metrics
    
    # MAE should be small for close predictions
    assert metrics['MAE'] < 0.5
    
    # R2 should be close to 1 for good fit
    assert metrics['R2'] > 0.9


def test_prediction_validity():
    """Test that predictions are valid numbers."""
    from sklearn.linear_model import LinearRegression
    
    X = np.random.randn(100, 5)
    y = np.random.randn(100)
    
    model = LinearRegression()
    model.fit(X, y)
    
    predictions = model.predict(X)
    
    # Check no NaN or infinite values
    assert not np.isnan(predictions).any()
    assert not np.isinf(predictions).any()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
