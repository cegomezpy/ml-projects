"""XGBoost regression model for hourly solar output, with GPU to CPU fallback."""

import subprocess  # nosec B404 - only used to query nvidia-smi
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from wh_forecast.models.exceptions import InsufficientDataError, ModelNotTrainedError
from wh_forecast.models.metrics import RegressionMetrics

MIN_SAMPLES = 2

# Tuned for hourly solar regression (~45k rows, 24 features)
DEFAULT_PARAMS: dict[str, Any] = {
    "n_estimators": 2000,
    "learning_rate": 0.05,
    "max_depth": 6,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 5,
    "tree_method": "hist",
    "early_stopping_rounds": 50,
    "random_state": 42,
}


def detect_device() -> str:
    """Return "cuda" when an NVIDIA GPU is visible, otherwise "cpu"."""
    try:
        result = subprocess.run(  # nosec B603 B607 - fixed arguments, no user input
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            print(f"GPU detected: {result.stdout.strip()} - using CUDA")
            return "cuda"
    except (OSError, subprocess.SubprocessError):
        pass
    print("No GPU detected - using CPU")
    return "cpu"


def _score(y_true: np.ndarray, y_pred: np.ndarray) -> RegressionMetrics:
    mse = mean_squared_error(y_true, y_pred)
    return RegressionMetrics(
        r2_score=r2_score(y_true, y_pred),
        mse=mse,
        rmse=float(np.sqrt(mse)),
        mae=mean_absolute_error(y_true, y_pred),
    )


class SolarXGBModel:
    """XGBoost regressor that predicts hourly solar output in Wh."""

    def __init__(self, params: dict[str, Any] | None = None, device: str | None = None) -> None:
        self._params = {**DEFAULT_PARAMS, **(params or {})}
        self.device = device or detect_device()
        self._regressor: xgb.XGBRegressor | None = None

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        X_val: np.ndarray | None = None,
        y_val: np.ndarray | None = None,
    ) -> RegressionMetrics:
        """Fit the model and return its scores on the training data.

        Without a validation set, the last 10% of the rows is held out for early stopping.

        Raises:
            InsufficientDataError: If fewer than MIN_SAMPLES rows are given.
            ValueError: If X and y have different lengths.
        """
        if len(X) < MIN_SAMPLES:
            raise InsufficientDataError(required=MIN_SAMPLES, provided=len(X))
        if len(X) != len(y):
            raise ValueError(f"X and y length mismatch: {len(X)} vs {len(y)}")

        if X_val is not None and y_val is not None:
            eval_set = [(X_val, y_val)]
        else:
            split = int(len(X) * 0.9)
            eval_set = [(X[split:], y[split:])]
            X, y = X[:split], y[:split]

        regressor = xgb.XGBRegressor(**self._params, device=self.device)
        regressor.fit(X, y, eval_set=eval_set, verbose=False)
        self._regressor = regressor
        return _score(y, regressor.predict(X))

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict output for each row of X.

        Raises:
            ModelNotTrainedError: If the model has not been trained or loaded.
        """
        predictions: np.ndarray = self._trained().predict(X)
        return predictions

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> RegressionMetrics:
        """Score the model's predictions for X against the true values y."""
        return _score(y, self.predict(X))

    def save(self, path: str | Path) -> None:
        """Persist the trained model, creating parent folders.

        Raises:
            ModelNotTrainedError: If the model has not been trained or loaded.
        """
        regressor = self._trained()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(regressor, path)

    @classmethod
    def load(cls, path: str | Path, device: str | None = None) -> "SolarXGBModel":
        """Load a model saved with save().

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not Path(path).exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        model = cls(device=device)
        model._regressor = joblib.load(path)
        return model

    def _trained(self) -> xgb.XGBRegressor:
        if self._regressor is None:
            raise ModelNotTrainedError()
        return self._regressor
