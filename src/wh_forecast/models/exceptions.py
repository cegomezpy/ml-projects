"""Errors raised by the solar output model."""


class ModelError(Exception):
    """Base class for model errors."""


class ModelNotTrainedError(ModelError):
    """Raised when a model is used before it has been trained or loaded."""

    def __init__(self) -> None:
        super().__init__("Model has not been trained yet")


class InsufficientDataError(ModelError):
    """Raised when the training data has too few samples."""

    def __init__(self, required: int, provided: int) -> None:
        self.required = required
        self.provided = provided
        super().__init__(f"Insufficient data: need at least {required} samples, got {provided}")
