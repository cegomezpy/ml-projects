"""
FastAPI routes for machine learning model operations.

This is the PRESENTATION layer - it only handles HTTP concerns.
All business logic is delegated to use cases.
"""

from fastapi import APIRouter, HTTPException, Depends, status

from application.dto.requests import (
    TrainModelRequest,
    PredictRequest,
    GetModelRequest,
)
from application.dto.responses import (
    TrainModelResponse,
    PredictionResponse,
    ModelInfoResponse,
    ModelListResponse,
    MessageResponse,
    ErrorResponse,
)
from application.use_cases.train_model import TrainModelUseCase
from application.use_cases.predict import PredictUseCase
from application.use_cases.get_model import (
    GetModelUseCase,
    ListModelsUseCase,
    DeleteModelUseCase,
)
from domain.exceptions import (
    DomainException,
    ModelNotFoundError,
    ModelNotTrainedError,
    InsufficientDataError,
    InvalidModelTypeError,
)
from presentation.dependencies import (
    get_train_model_use_case,
    get_predict_use_case,
    get_get_model_use_case,
    get_list_models_use_case,
    get_delete_model_use_case,
)

# Create router for model endpoints
router = APIRouter(prefix="/api/models", tags=["models"])


# ============================================================================
# POST /api/models/train - Train a new model
# ============================================================================


@router.post(
    "/train",
    response_model=TrainModelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Train a new ML model",
    description="Train a new machine learning model with the provided data",
    responses={
        201: {"description": "Model trained successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request or insufficient data"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def train_model(
    request: TrainModelRequest,
    use_case: TrainModelUseCase = Depends(get_train_model_use_case),
):
    """
    Train a new machine learning model.

    This endpoint:
    1. Validates the request (Pydantic does this automatically)
    2. Calls the TrainModelUseCase
    3. Returns the trained model information with metrics
    4. Handles domain exceptions and converts them to HTTP errors
    """
    try:
        result = use_case.execute(
            model_type_str=request.model_type,
            X=request.X,
            y=request.y,
            model_name=request.model_name,
        )

        # Convert to response DTO
        return TrainModelResponse(
            model_id=result["model_id"],
            model_type=result["model_type"],
            model_name=result["name"],
            is_trained=result["is_trained"],
            trained_at=result["trained_at"],
            metrics=result["metrics"],
        )

    except InvalidModelTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InsufficientDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# POST /api/models/predict - Make predictions
# ============================================================================


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Make predictions",
    description="Use a trained model to make predictions on new data",
    responses={
        200: {"description": "Predictions made successfully"},
        400: {"model": ErrorResponse, "description": "Model not trained or invalid data"},
        404: {"model": ErrorResponse, "description": "Model not found"},
    },
)
async def predict(
    request: PredictRequest,
    use_case: PredictUseCase = Depends(get_predict_use_case),
):
    """
    Make predictions using a trained model.

    This endpoint:
    1. Validates the request
    2. Retrieves the trained model
    3. Makes predictions
    4. Returns the results
    """
    try:
        result = use_case.execute(model_id=request.model_id, X=request.X)
        return PredictionResponse(**result)

    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ModelNotTrainedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"Model file not found: {str(e)}"
        )
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# GET /api/models/{model_id} - Get model information
# ============================================================================


@router.get(
    "/{model_id}",
    response_model=ModelInfoResponse,
    summary="Get model information",
    description="Retrieve information about a specific model",
    responses={
        200: {"description": "Model information retrieved"},
        404: {"model": ErrorResponse, "description": "Model not found"},
    },
)
async def get_model(
    model_id: str,
    use_case: GetModelUseCase = Depends(get_get_model_use_case),
):
    """Get information about a specific model."""
    try:
        result = use_case.execute(model_id=model_id)
        return ModelInfoResponse(**result)

    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# GET /api/models - List all models
# ============================================================================


@router.get(
    "",
    response_model=ModelListResponse,
    summary="List all models",
    description="Get a list of all trained models",
    responses={200: {"description": "List of models"}},
)
async def list_models(
    use_case: ListModelsUseCase = Depends(get_list_models_use_case),
):
    """List all models."""
    try:
        result = use_case.execute()
        return ModelListResponse(
            models=[ModelInfoResponse(**model) for model in result["models"]],
            count=result["count"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# DELETE /api/models/{model_id} - Delete a model
# ============================================================================


@router.delete(
    "/{model_id}",
    response_model=MessageResponse,
    summary="Delete a model",
    description="Delete a model and its associated files",
    responses={
        200: {"description": "Model deleted successfully"},
        404: {"model": ErrorResponse, "description": "Model not found"},
    },
)
async def delete_model(
    model_id: str,
    use_case: DeleteModelUseCase = Depends(get_delete_model_use_case),
):
    """Delete a model."""
    try:
        result = use_case.execute(model_id=model_id)
        return MessageResponse(**result)

    except ModelNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
