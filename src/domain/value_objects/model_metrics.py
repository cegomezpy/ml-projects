"""
Value Objects for model metrics.

Value objects are immutable and have no identity - they are defined solely by their attributes.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RegressionMetrics:
    """
    Metrics for regression models.

    Attributes:
        r2_score: Coefficient of determination (R² score)
        mse: Mean Squared Error
        rmse: Root Mean Squared Error
        mae: Mean Absolute Error
    """

    r2_score: float
    mse: float
    rmse: float
    mae: float

    def __post_init__(self):
        """Validate metrics values."""
        if self.r2_score > 1.0:
            raise ValueError("R² score cannot exceed 1.0")
        if any(v < 0 for v in [self.mse, self.rmse, self.mae]):
            raise ValueError("Error metrics cannot be negative")

    def to_dict(self) -> dict:
        """Convert metrics to dictionary."""
        return {
            "r2_score": round(self.r2_score, 4),
            "mse": round(self.mse, 4),
            "rmse": round(self.rmse, 4),
            "mae": round(self.mae, 4),
        }


@dataclass(frozen=True)
class ClassificationMetrics:
    """
    Metrics for classification models.

    Attributes:
        accuracy: Classification accuracy
        precision: Precision score
        recall: Recall score
        f1_score: F1 score
        confusion_matrix: Optional confusion matrix
    """

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: Optional[list[list[int]]] = None

    def __post_init__(self):
        """Validate metrics values."""
        metrics = [self.accuracy, self.precision, self.recall, self.f1_score]
        if any(m < 0 or m > 1 for m in metrics):
            raise ValueError("Classification metrics must be between 0 and 1")

    def to_dict(self) -> dict:
        """Convert metrics to dictionary."""
        result = {
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
        }
        if self.confusion_matrix:
            result["confusion_matrix"] = self.confusion_matrix
        return result
