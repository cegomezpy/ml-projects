"""
Use case for making predictions with a trained model.
"""

import numpy as np

from domain.exceptions import ModelNotFoundError
from domain.repositories.i_model_repository import IModelRepository
from domain.repositories.i_ml_service import IMLService
from domain.value_objects.prediction_result import PredictionResult


class PredictUseCase:
    """
    Use case for making predictions with a trained model.

    Follows Single Responsibility Principle - only handles prediction logic.
    """

    def __init__(
        self, ml_service: IMLService, model_repository: IModelRepository
    ):
        """
        Initialize use case with dependencies.

        Args:
            ml_service: Service for ML operations
            model_repository: Repository for model persistence
        """
        self._ml_service = ml_service
        self._model_repository = model_repository

    def execute(self, model_id: str, X: list[list[float]]) -> dict:
        """
        Execute the prediction use case.

        Business flow:
        1. Retrieve model from repository
        2. Ensure model exists and is trained
        3. Load trained model weights
        4. Convert input data
        5. Make predictions
        6. Return results

        Args:
            model_id: ID of the model to use
            X: Features to predict on

        Returns:
            Dictionary with predictions

        Raises:
            ModelNotFoundError: If model doesn't exist
            ModelNotTrainedError: If model hasn't been trained
            ValueError: If input data is invalid
        """
        model = self._model_repository.find_by_id(model_id)
        if model is None:
            raise ModelNotFoundError(model_id)

        model.ensure_trained()

        model_path = f"models/{model.model_id}.joblib"
        self._ml_service.load_trained_model(model, model_path)

        X_array = np.array(X, dtype=np.float64)

        prediction_result = self._ml_service.predict(model=model, X=X_array)

        return prediction_result.to_dict()
