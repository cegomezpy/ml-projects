"""
Dependency injection configuration for FastAPI.

This module provides FastAPI Depends functions that wire up the application layers.
Following the Dependency Inversion Principle, we inject interfaces, not implementations.
"""

from functools import lru_cache

from domain.repositories.i_model_repository import IModelRepository
from domain.repositories.i_ml_service import IMLService
from infrastructure.repositories.model_repository import JsonModelRepository
from infrastructure.ml_models.sklearn_service import SklearnMLService
from application.use_cases.train_model import TrainModelUseCase
from application.use_cases.predict import PredictUseCase
from application.use_cases.get_model import (
    GetModelUseCase,
    ListModelsUseCase,
    DeleteModelUseCase,
)


# ============================================================================
# Infrastructure Layer Dependencies
# ============================================================================


@lru_cache()
def get_model_repository() -> IModelRepository:
    """
    Get model repository instance.

    Using lru_cache ensures this is a singleton.
    This could be easily swapped for a database implementation.
    """
    return JsonModelRepository()


@lru_cache()
def get_ml_service() -> IMLService:
    """
    Get ML service instance.

    Using lru_cache ensures this is a singleton.
    This could be easily swapped for PyTorch, TensorFlow, etc.
    """
    return SklearnMLService()


# ============================================================================
# Application Layer Dependencies (Use Cases)
# ============================================================================


def get_train_model_use_case(
    ml_service: IMLService = get_ml_service(),
    model_repository: IModelRepository = get_model_repository(),
) -> TrainModelUseCase:
    """Get TrainModel use case with injected dependencies."""
    return TrainModelUseCase(ml_service=ml_service, model_repository=model_repository)


def get_predict_use_case(
    ml_service: IMLService = get_ml_service(),
    model_repository: IModelRepository = get_model_repository(),
) -> PredictUseCase:
    """Get Predict use case with injected dependencies."""
    return PredictUseCase(ml_service=ml_service, model_repository=model_repository)


def get_get_model_use_case(
    model_repository: IModelRepository = get_model_repository(),
) -> GetModelUseCase:
    """Get GetModel use case with injected dependencies."""
    return GetModelUseCase(model_repository=model_repository)


def get_list_models_use_case(
    model_repository: IModelRepository = get_model_repository(),
) -> ListModelsUseCase:
    """Get ListModels use case with injected dependencies."""
    return ListModelsUseCase(model_repository=model_repository)


def get_delete_model_use_case(
    model_repository: IModelRepository = get_model_repository(),
) -> DeleteModelUseCase:
    """Get DeleteModel use case with injected dependencies."""
    return DeleteModelUseCase(model_repository=model_repository)
