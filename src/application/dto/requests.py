"""
Request DTOs using Pydantic for validation.

These are Data Transfer Objects that define the contract for incoming API requests.
Pydantic automatically validates the data and provides clear error messages.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Union


class TrainModelRequest(BaseModel):
    """
    Request to train a new machine learning model.

    Example:
        {
            "model_type": "linear_regression",
            "X": [[1], [2], [3], [4], [5]],
            "y": [2, 4, 6, 8, 10],
            "model_name": "my_first_model"
        }
    """

    model_type: str = Field(
        ...,
        description="Type of ML model to train",
        examples=["linear_regression", "logistic_regression"],
    )
    X: list[list[float]] = Field(
        ..., description="Training features (2D array)", min_length=2
    )
    y: Union[list[float], list[int]] = Field(
        ..., description="Training labels/targets", min_length=2
    )
    model_name: str | None = Field(
        None, description="Optional custom name for the model"
    )

    @field_validator("X")
    @classmethod
    def validate_X(cls, v: list[list[float]]) -> list[list[float]]:
        """Validate training features."""
        if not v:
            raise ValueError("X cannot be empty")
        if len(v) < 2:
            raise ValueError("Need at least 2 samples for training")

        # Check all rows have same length
        first_len = len(v[0])
        if not all(len(row) == first_len for row in v):
            raise ValueError("All feature rows must have the same length")

        return v

    @field_validator("y")
    @classmethod
    def validate_y(cls, v: Union[list[float], list[int]]) -> Union[list[float], list[int]]:
        """Validate training labels."""
        if not v:
            raise ValueError("y cannot be empty")
        if len(v) < 2:
            raise ValueError("Need at least 2 labels for training")
        return v

    def model_post_init(self, __context):
        """Validate that X and y have the same length."""
        if len(self.X) != len(self.y):
            raise ValueError(
                f"X and y must have the same length. Got X={len(self.X)}, y={len(self.y)}"
            )


class PredictRequest(BaseModel):
    """
    Request to make predictions using a trained model.

    Example:
        {
            "model_id": "reg_abc123def456",
            "X": [[6], [7], [8]]
        }
    """

    model_id: str = Field(..., description="ID of the trained model to use")
    X: list[list[float]] = Field(
        ..., description="Features to predict on (2D array)", min_length=1
    )

    @field_validator("X")
    @classmethod
    def validate_X(cls, v: list[list[float]]) -> list[list[float]]:
        """Validate prediction features."""
        if not v:
            raise ValueError("X cannot be empty")

        # Check all rows have same length
        first_len = len(v[0])
        if not all(len(row) == first_len for row in v):
            raise ValueError("All feature rows must have the same length")

        return v


class GetModelRequest(BaseModel):
    """Request to retrieve a model by ID."""

    model_id: str = Field(..., description="Unique identifier of the model")
