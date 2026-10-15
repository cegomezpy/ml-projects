"""Regression check: training on the saved hourly data reproduces the pre-restructure metrics."""

from pathlib import Path

import pytest

from wh_forecast.config import LOCATION_NAME, WEATHER_DIR
from wh_forecast.models.train import train_solar_model

HOURLY_FILE = WEATHER_DIR / f"{LOCATION_NAME}_hourly.json"

# Recorded before the restructure (openspec change restructure-to-ml-standard, task 1.1)
BASELINE = {"rmse": 0.7943, "mae": 0.4264}
BASELINE_ROWS = {"train_rows": 45168, "test_rows": 4344}
TOLERANCE = 0.05


@pytest.mark.slow
@pytest.mark.skipif(not HOURLY_FILE.exists(), reason="saved hourly weather data not available")
def test_training_reproduces_baseline_metrics(tmp_path: Path) -> None:
    result = train_solar_model(HOURLY_FILE, tmp_path)

    assert result["test_metrics"]["r2_score"] > 0.999
    assert result["test_metrics"]["rmse"] == pytest.approx(BASELINE["rmse"], abs=TOLERANCE)
    assert result["test_metrics"]["mae"] == pytest.approx(BASELINE["mae"], abs=TOLERANCE)
    assert result["train_rows"] == BASELINE_ROWS["train_rows"]
    assert result["test_rows"] == BASELINE_ROWS["test_rows"]
