"""
Use cases for retrieving model information.
"""

from domain.exceptions import ModelNotFoundError
from domain.repositories.i_model_repository import IModelRepository


class GetModelUseCase:
    """Use case for retrieving a single model by ID."""

    def __init__(self, model_repository: IModelRepository):
        self._model_repository = model_repository

    def execute(self, model_id: str) -> dict:
        """
        Get model information by ID.

        Args:
            model_id: Unique identifier of the model

        Returns:
            Dictionary with model information

        Raises:
            ModelNotFoundError: If model doesn't exist
        """
        model = self._model_repository.find_by_id(model_id)
        if model is None:
            raise ModelNotFoundError(model_id)

        return model.to_dict()


class ListModelsUseCase:
    """Use case for listing all models."""

    def __init__(self, model_repository: IModelRepository):
        self._model_repository = model_repository

    def execute(self) -> dict:
        """
        List all models.

        Returns:
            Dictionary with list of models and count
        """
        models = self._model_repository.list_all()
        return {
            "models": [model.to_dict() for model in models],
            "count": len(models),
        }


class DeleteModelUseCase:
    """Use case for deleting a model."""

    def __init__(self, model_repository: IModelRepository):
        self._model_repository = model_repository

    def execute(self, model_id: str) -> dict:
        """
        Delete a model by ID.

        Args:
            model_id: Unique identifier of the model

        Returns:
            Dictionary with success message

        Raises:
            ModelNotFoundError: If model doesn't exist
        """
        deleted = self._model_repository.delete(model_id)
        if not deleted:
            raise ModelNotFoundError(model_id)

        return {"message": f"Model '{model_id}' deleted successfully", "success": True}
