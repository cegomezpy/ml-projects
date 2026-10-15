"""Regression metrics for model evaluation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RegressionMetrics:
    """Immutable regression scores.

    Attributes:
        r2_score: Coefficient of determination.
        mse: Mean squared error.
        rmse: Root mean squared error.
        mae: Mean absolute error.
    """

    r2_score: float
    mse: float
    rmse: float
    mae: float

    def __post_init__(self) -> None:
        if self.r2_score > 1.0:
            raise ValueError("R2 score cannot exceed 1.0")
        if any(v < 0 for v in (self.mse, self.rmse, self.mae)):
            raise ValueError("Error metrics cannot be negative")

    def to_dict(self) -> dict[str, float]:
        """Return the metrics rounded to four decimals."""
        return {
            "r2_score": round(self.r2_score, 4),
            "mse": round(self.mse, 4),
            "rmse": round(self.rmse, 4),
            "mae": round(self.mae, 4),
        }
