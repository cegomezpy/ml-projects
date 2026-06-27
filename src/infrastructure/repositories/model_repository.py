"""
Implementation of IModelRepository using JSON file storage.

This is the CONCRETE implementation that the infrastructure layer provides.
It implements the interface defined by the domain layer.
"""

import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from domain.entities.model import Model
from domain.repositories.i_model_repository import IModelRepository
from domain.value_objects.model_type import ModelType
from domain.value_objects.model_metrics import RegressionMetrics, ClassificationMetrics


class JsonModelRepository(IModelRepository):
    """
    Repository that stores model metadata in a JSON file.

    This implementation is easily swappable - we could replace it with
    a database implementation without touching the domain or application layers.
    """

    def __init__(self, storage_path: str = "models/metadata.json"):
        """
        Initialize repository.

        Args:
            storage_path: Path to the JSON file for storing metadata
        """
        self._storage_path = Path(storage_path)
        self._ensure_storage_exists()

    def _ensure_storage_exists(self) -> None:
        """Create storage directory and file if they don't exist."""
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._storage_path.exists():
            self._storage_path.write_text(json.dumps({"models": {}}, indent=2))

    def _load_data(self) -> dict:
        """Load all data from JSON file."""
        try:
            return json.loads(self._storage_path.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return {"models": {}}

    def _save_data(self, data: dict) -> None:
        """Save all data to JSON file."""
        self._storage_path.write_text(json.dumps(data, indent=2))

    def _model_to_dict(self, model: Model) -> dict:
        """Convert model entity to storable dictionary."""
        data = {
            "model_id": model.model_id,
            "model_type": model.model_type.value,
            "name": model.name,
            "is_trained": model.is_trained,
            "created_at": model.created_at.isoformat(),
            "trained_at": model.trained_at.isoformat() if model.trained_at else None,
        }

        # Serialize metrics if present
        if model.metrics:
            data["metrics"] = model.metrics.to_dict()
            data["metrics_type"] = (
                "regression"
                if isinstance(model.metrics, RegressionMetrics)
                else "classification"
            )

        return data

    def _dict_to_model(self, data: dict) -> Model:
        """Convert stored dictionary back to model entity."""
        model = Model(
            model_type=ModelType(data["model_type"]),
            model_id=data["model_id"],
            name=data["name"],
        )

        # Restore timestamps
        model._created_at = datetime.fromisoformat(data["created_at"])
        if data.get("trained_at"):
            model._trained_at = datetime.fromisoformat(data["trained_at"])

        # Restore metrics if present
        if data.get("metrics"):
            metrics_data = data["metrics"]
            if data.get("metrics_type") == "regression":
                metrics = RegressionMetrics(
                    r2_score=metrics_data["r2_score"],
                    mse=metrics_data["mse"],
                    rmse=metrics_data["rmse"],
                    mae=metrics_data["mae"],
                )
            else:
                metrics = ClassificationMetrics(
                    accuracy=metrics_data["accuracy"],
                    precision=metrics_data["precision"],
                    recall=metrics_data["recall"],
                    f1_score=metrics_data["f1_score"],
                )
            model._metrics = metrics
            model._is_trained = True

        return model

    def save(self, model: Model) -> None:
        """
        Save model metadata to JSON file.

        Args:
            model: The model entity to save
        """
        data = self._load_data()
        data["models"][model.model_id] = self._model_to_dict(model)
        self._save_data(data)

    def find_by_id(self, model_id: str) -> Optional[Model]:
        """
        Find a model by its ID.

        Args:
            model_id: Unique identifier

        Returns:
            Model if found, None otherwise
        """
        data = self._load_data()
        model_data = data["models"].get(model_id)
        if model_data is None:
            return None
        return self._dict_to_model(model_data)

    def delete(self, model_id: str) -> bool:
        """
        Delete a model by ID.

        Args:
            model_id: Unique identifier

        Returns:
            True if deleted, False if not found
        """
        data = self._load_data()
        if model_id in data["models"]:
            del data["models"][model_id]
            self._save_data(data)

            # Also delete the model file if it exists
            model_file = Path(f"models/{model_id}.joblib")
            if model_file.exists():
                model_file.unlink()

            return True
        return False

    def list_all(self) -> list[Model]:
        """
        List all models.

        Returns:
            List of all models (may be empty)
        """
        data = self._load_data()
        return [self._dict_to_model(model_data) for model_data in data["models"].values()]

    def exists(self, model_id: str) -> bool:
        """
        Check if a model exists.

        Args:
            model_id: Unique identifier

        Returns:
            True if exists, False otherwise
        """
        data = self._load_data()
        return model_id in data["models"]
