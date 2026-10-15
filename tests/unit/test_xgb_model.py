"""Tests for the XGBoost solar output model."""

from pathlib import Path

import numpy as np
import pytest

from wh_forecast.models.exceptions import InsufficientDataError, ModelNotTrainedError
from wh_forecast.models.metrics import RegressionMetrics
from wh_forecast.models.xgb_model import SolarXGBModel

FAST_PARAMS = {"n_estimators": 50, "learning_rate": 0.3, "early_stopping_rounds": 5}


@pytest.fixture
def linear_data() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(0)
    X = rng.uniform(0, 1, size=(200, 3))
    y = 100 * X[:, 0] + 10 * X[:, 1]
    return X, y


def test_training_with_too_few_samples_fails() -> None:
    model = SolarXGBModel(device="cpu")

    with pytest.raises(InsufficientDataError):
        model.train(np.array([[1.0]]), np.array([1.0]))


def test_predicting_before_training_fails() -> None:
    model = SolarXGBModel(device="cpu")

    with pytest.raises(ModelNotTrainedError):
        model.predict(np.array([[1.0, 2.0, 3.0]]))


def test_saving_before_training_fails(tmp_path: Path) -> None:
    model = SolarXGBModel(device="cpu")

    with pytest.raises(ModelNotTrainedError):
        model.save(tmp_path / "model.joblib")


def test_mismatched_x_and_y_lengths_fail(linear_data: tuple[np.ndarray, np.ndarray]) -> None:
    X, y = linear_data

    with pytest.raises(ValueError):
        SolarXGBModel(FAST_PARAMS, device="cpu").train(X, y[:-1])


def test_trained_model_learns_a_simple_relationship(
    linear_data: tuple[np.ndarray, np.ndarray]
) -> None:
    X, y = linear_data
    model = SolarXGBModel(FAST_PARAMS, device="cpu")

    train_metrics = model.train(X[:150], y[:150], X_val=X[150:], y_val=y[150:])
    test_metrics = model.evaluate(X[150:], y[150:])

    assert isinstance(train_metrics, RegressionMetrics)
    assert test_metrics.r2_score > 0.9


def test_saved_model_predicts_identically_after_loading(
    linear_data: tuple[np.ndarray, np.ndarray], tmp_path: Path
) -> None:
    X, y = linear_data
    model = SolarXGBModel(FAST_PARAMS, device="cpu")
    model.train(X, y)
    path = tmp_path / "nested" / "model.joblib"

    model.save(path)
    loaded = SolarXGBModel.load(path, device="cpu")

    np.testing.assert_allclose(loaded.predict(X), model.predict(X))


def test_loading_a_missing_file_fails(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        SolarXGBModel.load(tmp_path / "missing.joblib", device="cpu")


def test_regression_metrics_reject_negative_errors() -> None:
    with pytest.raises(ValueError):
        RegressionMetrics(r2_score=0.9, mse=-1.0, rmse=1.0, mae=1.0)


def test_regression_metrics_to_dict_rounds_to_four_decimals() -> None:
    metrics = RegressionMetrics(r2_score=0.123456, mse=1.0, rmse=1.0, mae=1.0)

    assert metrics.to_dict()["r2_score"] == 0.1235
