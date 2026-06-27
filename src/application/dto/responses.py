"""
Response DTOs using Pydantic.

These define the structure of API responses.
"""

from pydantic import BaseModel, Field
from typing import Union, Optional
from datetime import datetime


class MetricsResponse(BaseModel):
    """Response containing model performance metrics."""

    r2_score: Optional[float] = Field(None, description="R² score for regression")
    mse: Optional[float] = Field(None, description="Mean Squared Error")
    rmse: Optional[float] = Field(None, description="Root Mean Squared Error")
    mae: Optional[float] = Field(None, description="Mean Absolute Error")
    accuracy: Optional[float] = Field(None, description="Accuracy for classification")
    precision: Optional[float] = Field(None, description="Precision for classification")
    recall: Optional[float] = Field(None, description="Recall for classification")
    f1_score: Optional[float] = Field(None, description="F1 score for classification")

    class Config:
        json_schema_extra = {
            "example": {
                "r2_score": 0.9523,
                "mse": 0.0234,
                "rmse": 0.1530,
                "mae": 0.1205,
            }
        }


class TrainModelResponse(BaseModel):
    """Response after training a model."""

    model_id: str = Field(..., description="Unique identifier of the trained model")
    model_type: str = Field(..., description="Type of the model")
    model_name: str = Field(..., description="Name of the model")
    is_trained: bool = Field(..., description="Whether the model is trained")
    trained_at: str = Field(..., description="Timestamp when model was trained")
    metrics: MetricsResponse = Field(..., description="Performance metrics")
    message: str = Field(default="Model trained successfully")

    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "reg_abc123def456",
                "model_type": "linear_regression",
                "model_name": "my_first_model",
                "is_trained": True,
                "trained_at": "2024-01-15T10:30:00",
                "metrics": {
                    "r2_score": 0.9523,
                    "mse": 0.0234,
                    "rmse": 0.1530,
                    "mae": 0.1205,
                },
                "message": "Model trained successfully",
            }
        }


class PredictionResponse(BaseModel):
    """Response containing predictions."""

    model_id: str = Field(..., description="ID of the model used")
    predictions: Union[list[float], list[int], list[str]] = Field(
        ..., description="Predicted values"
    )
    count: int = Field(..., description="Number of predictions")

    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "reg_abc123def456",
                "predictions": [12.0, 14.0, 16.0],
                "count": 3,
            }
        }


class ModelInfoResponse(BaseModel):
    """Response with model information."""

    model_id: str
    model_type: str
    model_name: str
    is_trained: bool
    created_at: str
    trained_at: Optional[str] = None
    metrics: Optional[MetricsResponse] = None

    class Config:
        json_schema_extra = {
            "example": {
                "model_id": "reg_abc123def456",
                "model_type": "linear_regression",
                "model_name": "my_first_model",
                "is_trained": True,
                "created_at": "2024-01-15T10:25:00",
                "trained_at": "2024-01-15T10:30:00",
                "metrics": {"r2_score": 0.9523, "mse": 0.0234},
            }
        }


class ModelListResponse(BaseModel):
    """Response with list of models."""

    models: list[ModelInfoResponse] = Field(..., description="List of models")
    count: int = Field(..., description="Total number of models")


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Whether operation succeeded")

    class Config:
        json_schema_extra = {
            "example": {"message": "Model deleted successfully", "success": True}
        }


class ErrorResponse(BaseModel):
    """Error response."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Model not found",
                "detail": "Model 'reg_xyz789' does not exist",
            }
        }
