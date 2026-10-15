"""Tests for the solar model training flow."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from wh_forecast.models.train import train_solar_model
from wh_forecast.models.xgb_model import SolarXGBModel

FAST_PARAMS = {"n_estimators": 20, "learning_rate": 0.3, "early_stopping_rounds": 5}


@pytest.fixture
def hourly_file(tmp_path: Path) -> Path:
    index = pd.date_range("2023-01-01", periods=24 * 400, freq="h")
    hour = index.hour.to_numpy()
    radiation = (np.clip(np.sin((hour - 6) / 12 * np.pi), 0, None) * 800).tolist()
    hourly = {
        "time": [t.isoformat() for t in index],
        "shortwave_radiation": radiation,
        "direct_radiation": radiation,
        "diffuse_radiation": [r * 0.3 for r in radiation],
        "cloud_cover": [30.0] * len(index),
        "temperature_2m": [28.0] * len(index),
        "relative_humidity_2m": [70.0] * len(index),
        "precipitation": [0.0] * len(index),
        "surface_pressure": [1012.0] * len(index),
        "sunshine_duration": [1800.0] * len(index),
    }
    path = tmp_path / "hourly.json"
    path.write_text(json.dumps({"hourly": hourly}), encoding="utf-8")
    return path


def test_training_saves_a_loadable_model_and_reports_metrics(
    hourly_file: Path, tmp_path: Path
) -> None:
    result = train_solar_model(hourly_file, tmp_path / "models", params=FAST_PARAMS, device="cpu")

    assert Path(result["model_path"]).exists()
    assert result["train_rows"] > result["test_rows"] > 0
    assert set(result["test_metrics"]) == {"r2_score", "mse", "rmse", "mae"}
    assert result["device"] == "cpu"
    SolarXGBModel.load(result["model_path"], device="cpu")


def test_test_set_is_the_last_months_of_the_data(hourly_file: Path, tmp_path: Path) -> None:
    result = train_solar_model(
        hourly_file, tmp_path / "models", test_months=2, params=FAST_PARAMS, device="cpu"
    )

    assert 24 * 55 < result["test_rows"] < 24 * 65
