"""
Model type enumeration.
"""

from enum import Enum


class ModelType(str, Enum):
    """
    Supported machine learning model types.

    Inherits from str to make it JSON serializable.
    """

    # Regression Models
    LINEAR_REGRESSION = "linear_regression"
    POLYNOMIAL_REGRESSION = "polynomial_regression"
    RIDGE_REGRESSION = "ridge_regression"
    LASSO_REGRESSION = "lasso_regression"

    # Classification Models
    LOGISTIC_REGRESSION = "logistic_regression"
    DECISION_TREE_CLASSIFIER = "decision_tree_classifier"
    RANDOM_FOREST_CLASSIFIER = "random_forest_classifier"

    # Tree-based Models
    DECISION_TREE_REGRESSOR = "decision_tree_regressor"
    RANDOM_FOREST_REGRESSOR = "random_forest_regressor"

    def is_regression(self) -> bool:
        """Check if the model is a regression model."""
        return self in [
            ModelType.LINEAR_REGRESSION,
            ModelType.POLYNOMIAL_REGRESSION,
            ModelType.RIDGE_REGRESSION,
            ModelType.LASSO_REGRESSION,
            ModelType.DECISION_TREE_REGRESSOR,
            ModelType.RANDOM_FOREST_REGRESSOR,
        ]

    def is_classification(self) -> bool:
        """Check if the model is a classification model."""
        return self in [
            ModelType.LOGISTIC_REGRESSION,
            ModelType.DECISION_TREE_CLASSIFIER,
            ModelType.RANDOM_FOREST_CLASSIFIER,
        ]
