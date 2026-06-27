"""
Model entity - represents a machine learning model in the domain.

This is an Entity (has identity) and an Aggregate Root in DDD.
"""

from datetime import datetime
from typing import Optional, Union
from uuid import uuid4

from domain.exceptions import ModelNotTrainedError
from domain.value_objects.model_metrics import RegressionMetrics, ClassificationMetrics
from domain.value_objects.model_type import ModelType


class Model:
    """
    Represents a machine learning model.

    This is an Entity with identity (model_id) and lifecycle.
    It enforces business rules and maintains invariants.
    """

    def __init__(
        self,
        model_type: ModelType,
        model_id: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Initialize a new model.

        Args:
            model_type: Type of the machine learning model
            model_id: Unique identifier (generated if not provided)
            name: Optional human-readable name for the model
        """
        self._model_id = model_id or self._generate_model_id(model_type)
        self._model_type = model_type
        self._name = name or f"{model_type.value}_{self._model_id[:8]}"
        self._is_trained = False
        self._trained_at: Optional[datetime] = None
        self._metrics: Optional[Union[RegressionMetrics, ClassificationMetrics]] = None
        self._created_at = datetime.now()

    @staticmethod
    def _generate_model_id(model_type: ModelType) -> str:
        """Generate a unique model ID."""
        prefix = "reg" if model_type.is_regression() else "clf"
        return f"{prefix}_{uuid4().hex[:12]}"

    # Properties (read-only access to private attributes)
    @property
    def model_id(self) -> str:
        """Get the model's unique identifier."""
        return self._model_id

    @property
    def model_type(self) -> ModelType:
        """Get the model type."""
        return self._model_type

    @property
    def name(self) -> str:
        """Get the model name."""
        return self._name

    @property
    def is_trained(self) -> bool:
        """Check if the model has been trained."""
        return self._is_trained

    @property
    def trained_at(self) -> Optional[datetime]:
        """Get when the model was trained."""
        return self._trained_at

    @property
    def metrics(self) -> Optional[Union[RegressionMetrics, ClassificationMetrics]]:
        """Get the model's performance metrics."""
        return self._metrics

    @property
    def created_at(self) -> datetime:
        """Get when the model was created."""
        return self._created_at

    # Business methods
    def mark_as_trained(
        self, metrics: Union[RegressionMetrics, ClassificationMetrics]
    ) -> None:
        """
        Mark the model as trained with performance metrics.

        This enforces the business rule that a model must have metrics after training.

        Args:
            metrics: Performance metrics from training

        Raises:
            ValueError: If metrics type doesn't match model type
        """
        # Validate metrics match model type
        if self._model_type.is_regression() and not isinstance(
            metrics, RegressionMetrics
        ):
            raise ValueError(
                f"Regression model requires RegressionMetrics, got {type(metrics)}"
            )
        if self._model_type.is_classification() and not isinstance(
            metrics, ClassificationMetrics
        ):
            raise ValueError(
                f"Classification model requires ClassificationMetrics, got {type(metrics)}"
            )

        self._is_trained = True
        self._trained_at = datetime.now()
        self._metrics = metrics

    def ensure_trained(self) -> None:
        """
        Ensure the model is trained before use.

        Raises:
            ModelNotTrainedError: If the model hasn't been trained yet
        """
        if not self._is_trained:
            raise ModelNotTrainedError(self._model_id)

    def to_dict(self) -> dict:
        """Convert model to dictionary representation."""
        return {
            "model_id": self._model_id,
            "model_type": self._model_type.value,
            "name": self._name,
            "is_trained": self._is_trained,
            "trained_at": self._trained_at.isoformat() if self._trained_at else None,
            "metrics": self._metrics.to_dict() if self._metrics else None,
            "created_at": self._created_at.isoformat(),
        }

    def __eq__(self, other: object) -> bool:
        """Two models are equal if they have the same ID."""
        if not isinstance(other, Model):
            return False
        return self._model_id == other._model_id

    def __hash__(self) -> int:
        """Hash based on model ID."""
        return hash(self._model_id)

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "trained" if self._is_trained else "untrained"
        return f"Model(id={self._model_id}, type={self._model_type.value}, status={status})"
