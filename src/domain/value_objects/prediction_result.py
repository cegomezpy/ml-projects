"""
Value object for prediction results.
"""

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class PredictionResult:
    """
    Immutable result of a model prediction.

    Attributes:
        predictions: The predicted values (can be numeric or categorical)
        model_id: ID of the model that made the prediction
    """

    predictions: Union[list[float], list[int], list[str]]
    model_id: str

    def __post_init__(self):
        """Validate prediction result."""
        if not self.predictions:
            raise ValueError("Predictions cannot be empty")
        if not self.model_id:
            raise ValueError("Model ID is required")

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "predictions": self.predictions,
            "model_id": self.model_id,
            "count": len(self.predictions),
        }

    def __len__(self) -> int:
        """Return number of predictions."""
        return len(self.predictions)
