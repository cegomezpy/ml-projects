"""
Interface for Machine Learning operations.

This abstraction separates the domain from the actual ML library implementation.
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Union

from domain.entities.model import Model
from domain.value_objects.model_metrics import RegressionMetrics, ClassificationMetrics
from domain.value_objects.prediction_result import PredictionResult


class IMLService(ABC):
    """
    Interface for machine learning training and prediction operations.

    Implementations might use scikit-learn, PyTorch, TensorFlow, etc.
    The domain doesn't care about the implementation details.
    """

    @abstractmethod
    def train(
        self, model: Model, X: np.ndarray, y: np.ndarray
    ) -> Union[RegressionMetrics, ClassificationMetrics]:
        """
        Train a machine learning model.

        Args:
            model: The model entity to train
            X: Training features
            y: Training labels/targets

        Returns:
            Performance metrics after training

        Raises:
            InsufficientDataError: If data is insufficient
            ValueError: If data is invalid
        """
        pass

    @abstractmethod
    def predict(self, model: Model, X: np.ndarray) -> PredictionResult:
        """
        Make predictions using a trained model.

        Args:
            model: The trained model entity
            X: Features to predict on

        Returns:
            Prediction results

        Raises:
            ModelNotTrainedError: If model hasn't been trained
            ValueError: If input data is invalid
        """
        pass

    @abstractmethod
    def save_trained_model(self, model: Model, path: str) -> None:
        """
        Save the trained model's internal state to disk.

        Args:
            model: The trained model to save
            path: File path where to save the model

        Raises:
            ModelNotTrainedError: If model hasn't been trained
        """
        pass

    @abstractmethod
    def load_trained_model(self, model: Model, path: str) -> None:
        """
        Load a trained model's internal state from disk.

        Args:
            model: The model entity to load state into
            path: File path from where to load the model

        Raises:
            FileNotFoundError: If model file doesn't exist
        """
        pass
