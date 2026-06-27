"""
Domain exceptions for the ML projects application.

These exceptions represent business rule violations and domain errors.
They should be caught and handled at the presentation layer.
"""


class DomainException(Exception):
    """Base exception for all domain-level errors."""
    pass


class ModelNotTrainedError(DomainException):
    """Raised when attempting to use an untrained model for predictions."""

    def __init__(self, model_id: str):
        self.model_id = model_id
        super().__init__(f"Model '{model_id}' has not been trained yet")


class InsufficientDataError(DomainException):
    """Raised when training data is insufficient for the model."""

    def __init__(self, required: int, provided: int):
        self.required = required
        self.provided = provided
        super().__init__(
            f"Insufficient data: need at least {required} samples, got {provided}"
        )


class InvalidModelTypeError(DomainException):
    """Raised when an invalid or unsupported model type is requested."""

    def __init__(self, model_type: str):
        self.model_type = model_type
        super().__init__(f"Invalid model type: '{model_type}'")


class ModelNotFoundError(DomainException):
    """Raised when a requested model cannot be found."""

    def __init__(self, model_id: str):
        self.model_id = model_id
        super().__init__(f"Model not found: '{model_id}'")
