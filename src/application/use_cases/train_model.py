"""
Use case for training a machine learning model.

This orchestrates the domain objects to fulfill the business requirement of training a model.
Following the Single Responsibility Principle - this class has ONE job: train models.
"""

import numpy as np
from typing import Union

from domain.entities.model import Model
from domain.exceptions import InvalidModelTypeError
from domain.repositories.i_model_repository import IModelRepository
from domain.repositories.i_ml_service import IMLService
from domain.value_objects.model_type import ModelType
from domain.value_objects.model_metrics import RegressionMetrics, ClassificationMetrics


class TrainModelUseCase:
    """
    Use case for training a machine learning model.

    This follows:
    - Single Responsibility: Only trains models
    - Dependency Inversion: Depends on abstractions (interfaces), not implementations
    - Open/Closed: Can add new model types without modifying this class
    """

    def __init__(
        self, ml_service: IMLService, model_repository: IModelRepository
    ):
        """
        Initialize use case with dependencies.

        Args:
            ml_service: Service for ML operations (training, prediction)
            model_repository: Repository for model persistence
        """
        self._ml_service = ml_service
        self._model_repository = model_repository

    def execute(
        self,
        model_type_str: str,
        X: list[list[float]],
        y: Union[list[float], list[int]],
        model_name: str | None = None,
    ) -> dict:
        """
        Execute the training use case.

        Business flow:
        1. Validate model type
        2. Create model entity
        3. Convert data to numpy arrays
        4. Train using ML service
        5. Mark model as trained with metrics
        6. Persist model
        7. Return result

        Args:
            model_type_str: String representation of model type
            X: Training features
            y: Training targets
            model_name: Optional custom name

        Returns:
            Dictionary with model information and metrics

        Raises:
            InvalidModelTypeError: If model type is not supported
            InsufficientDataError: If data is insufficient
            ValueError: If data is invalid
        """
        try:
            model_type = ModelType(model_type_str)
        except ValueError:
            valid_types = [t.value for t in ModelType]
            raise InvalidModelTypeError(
                f"{model_type_str}. Valid types: {', '.join(valid_types)}"
            )

        model = Model(model_type=model_type, name=model_name)

        X_array = np.array(X, dtype=np.float64)
        y_array = np.array(y, dtype=np.float64 if model_type.is_regression() else np.int32)

        metrics = self._ml_service.train(model=model, X=X_array, y=y_array)

        model.mark_as_trained(metrics)

        self._model_repository.save(model)

        model_path = f"models/{model.model_id}.joblib"
        self._ml_service.save_trained_model(model, model_path)

        return model.to_dict()

    def _validate_data_compatibility(
        self,
        model_type: ModelType,
        X: np.ndarray,
        y: np.ndarray,
    ) -> None:
        """
        Validate that data is compatible with the model type.

        Args:
            model_type: The type of model
            X: Feature array
            y: Target array

        Raises:
            ValueError: If data is incompatible
        """
        if model_type.is_classification():
            unique_values = np.unique(y)
            if len(unique_values) < 2:
                raise ValueError(
                    "Classification requires at least 2 different classes in y"
                )
