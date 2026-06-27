"""
Repository interface for Model persistence.

This is an abstraction (interface) that follows the Dependency Inversion Principle.
The domain layer defines WHAT operations are needed, not HOW they are implemented.
"""

from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.model import Model


class IModelRepository(ABC):
    """
    Interface for model persistence operations.

    This abstraction allows the domain layer to be independent of
    infrastructure concerns (database, file system, etc.).
    """

    @abstractmethod
    def save(self, model: Model) -> None:
        """
        Persist a model.

        Args:
            model: The model entity to save

        Raises:
            Exception: Implementation-specific errors
        """
        pass

    @abstractmethod
    def find_by_id(self, model_id: str) -> Optional[Model]:
        """
        Retrieve a model by its ID.

        Args:
            model_id: Unique identifier of the model

        Returns:
            The model if found, None otherwise
        """
        pass

    @abstractmethod
    def delete(self, model_id: str) -> bool:
        """
        Delete a model by its ID.

        Args:
            model_id: Unique identifier of the model

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def list_all(self) -> list[Model]:
        """
        List all persisted models.

        Returns:
            List of all models (may be empty)
        """
        pass

    @abstractmethod
    def exists(self, model_id: str) -> bool:
        """
        Check if a model exists.

        Args:
            model_id: Unique identifier of the model

        Returns:
            True if exists, False otherwise
        """
        pass
