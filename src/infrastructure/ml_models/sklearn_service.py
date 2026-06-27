"""
Implementation of IMLService using scikit-learn.

This is the actual ML implementation. Following the Dependency Inversion Principle,
this can be swapped for PyTorch, TensorFlow, or any other ML library.
"""

import joblib
import numpy as np
from pathlib import Path
from typing import Union, Any
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)

from domain.entities.model import Model
from domain.exceptions import InsufficientDataError, ModelNotTrainedError
from domain.repositories.i_ml_service import IMLService
from domain.value_objects.model_metrics import RegressionMetrics, ClassificationMetrics
from domain.value_objects.model_type import ModelType
from domain.value_objects.prediction_result import PredictionResult


class SklearnMLService(IMLService):
    """
    ML service implementation using scikit-learn.

    Follows Open/Closed Principle - easy to add new model types
    by extending the model factory.
    """

    # Minimum samples required for training
    MIN_SAMPLES = 2

    def __init__(self):
        """Initialize service with model storage."""
        # Internal storage for trained sklearn models (in memory)
        self._trained_models: dict[str, Any] = {}

    def _create_sklearn_model(self, model_type: ModelType) -> Any:
        """
        Factory method to create sklearn model instances.

        This follows the Factory Pattern and makes it easy to add new models.

        Args:
            model_type: The type of model to create

        Returns:
            Sklearn model instance

        Raises:
            ValueError: If model type is not yet implemented
        """
        model_map = {
            ModelType.LINEAR_REGRESSION: LinearRegression(),
            ModelType.RIDGE_REGRESSION: Ridge(),
            ModelType.LASSO_REGRESSION: Lasso(),
            ModelType.LOGISTIC_REGRESSION: LogisticRegression(max_iter=1000),
            ModelType.DECISION_TREE_REGRESSOR: DecisionTreeRegressor(),
            ModelType.DECISION_TREE_CLASSIFIER: DecisionTreeClassifier(),
            ModelType.RANDOM_FOREST_REGRESSOR: RandomForestRegressor(n_estimators=100),
            ModelType.RANDOM_FOREST_CLASSIFIER: RandomForestClassifier(n_estimators=100),
        }

        sklearn_model = model_map.get(model_type)
        if sklearn_model is None:
            raise ValueError(f"Model type '{model_type.value}' not yet implemented")

        return sklearn_model

    def train(
        self, model: Model, X: np.ndarray, y: np.ndarray
    ) -> Union[RegressionMetrics, ClassificationMetrics]:
        """
        Train a machine learning model.

        Args:
            model: The model entity
            X: Training features
            y: Training targets

        Returns:
            Performance metrics

        Raises:
            InsufficientDataError: If not enough data
            ValueError: If data is invalid
        """
        # Validate data
        if len(X) < self.MIN_SAMPLES:
            raise InsufficientDataError(
                required=self.MIN_SAMPLES, provided=len(X)
            )

        if len(X) != len(y):
            raise ValueError(f"X and y must have same length. Got X={len(X)}, y={len(y)}")

        # Create sklearn model
        sklearn_model = self._create_sklearn_model(model.model_type)

        # Train the model
        sklearn_model.fit(X, y)

        # Store trained model in memory
        self._trained_models[model.model_id] = sklearn_model

        # Calculate metrics
        y_pred = sklearn_model.predict(X)

        if model.model_type.is_regression():
            metrics = self._calculate_regression_metrics(y, y_pred)
        else:
            metrics = self._calculate_classification_metrics(y, y_pred)

        return metrics

    def predict(self, model: Model, X: np.ndarray) -> PredictionResult:
        """
        Make predictions using a trained model.

        Args:
            model: The trained model entity
            X: Features to predict on

        Returns:
            Prediction results

        Raises:
            ModelNotTrainedError: If model not in memory
            ValueError: If input is invalid
        """
        # Ensure model is loaded in memory
        if model.model_id not in self._trained_models:
            raise ModelNotTrainedError(model.model_id)

        sklearn_model = self._trained_models[model.model_id]

        # Make predictions
        predictions = sklearn_model.predict(X)

        # Convert to appropriate type
        if model.model_type.is_regression():
            pred_list = predictions.tolist()
        else:
            pred_list = predictions.astype(int).tolist()

        return PredictionResult(predictions=pred_list, model_id=model.model_id)

    def save_trained_model(self, model: Model, path: str) -> None:
        """
        Save trained model to disk using joblib.

        Args:
            model: The model entity
            path: File path to save to

        Raises:
            ModelNotTrainedError: If model not in memory
        """
        if model.model_id not in self._trained_models:
            raise ModelNotTrainedError(model.model_id)

        sklearn_model = self._trained_models[model.model_id]

        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        # Save using joblib
        joblib.dump(sklearn_model, path)

    def load_trained_model(self, model: Model, path: str) -> None:
        """
        Load trained model from disk.

        Args:
            model: The model entity
            path: File path to load from

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not Path(path).exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        # Load using joblib
        sklearn_model = joblib.load(path)

        # Store in memory
        self._trained_models[model.model_id] = sklearn_model

    def _calculate_regression_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> RegressionMetrics:
        """Calculate regression performance metrics."""
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        return RegressionMetrics(r2_score=r2, mse=mse, rmse=rmse, mae=mae)

    def _calculate_classification_metrics(
        self, y_true: np.ndarray, y_pred: np.ndarray
    ) -> ClassificationMetrics:
        """Calculate classification performance metrics."""
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

        return ClassificationMetrics(
            accuracy=accuracy, precision=precision, recall=recall, f1_score=f1
        )
