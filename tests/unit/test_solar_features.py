"""Characterization tests for solar feature building and the chronological split."""

import numpy as np
import pandas as pd
import pytest

from wh_forecast.config import VIBORA_PARK_PANEL
from wh_forecast.features.solar_features import (
    FEATURES,
    TARGET,
    build_dataset,
    time_split,
)


@pytest.fixture
def hourly_weather() -> pd.DataFrame:
    index = pd.date_range("2023-01-01", periods=24 * 400, freq="h", name="time")
    hour = index.hour.to_numpy()
    radiation = np.clip(np.sin((hour - 6) / 12 * np.pi), 0, None) * 800
    return pd.DataFrame(
        {
            "shortwave_radiation": radiation,
            "direct_radiation": radiation * 0.7,
            "diffuse_radiation": radiation * 0.3,
            "cloud_cover": 30.0,
            "temperature_2m": 28.0,
            "relative_humidity_2m": 70.0,
            "precipitation": 0.0,
            "surface_pressure": 1012.0,
            "sunshine_duration": 1800.0,
        },
        index=index,
    )


def test_build_dataset_has_all_features_and_target_without_nans(
    hourly_weather: pd.DataFrame,
) -> None:
    dataset = build_dataset(hourly_weather, VIBORA_PARK_PANEL)

    assert len(FEATURES) == 24
    assert set(FEATURES + [TARGET]).issubset(dataset.columns)
    assert not dataset[FEATURES + [TARGET]].isna().any().any()


def test_build_dataset_drops_rows_lost_to_the_24h_lag(hourly_weather: pd.DataFrame) -> None:
    dataset = build_dataset(hourly_weather, VIBORA_PARK_PANEL)

    assert len(dataset) == len(hourly_weather) - 24


def test_target_is_capped_and_non_negative(hourly_weather: pd.DataFrame) -> None:
    dataset = build_dataset(hourly_weather, VIBORA_PARK_PANEL)

    assert dataset[TARGET].between(0.0, 500.0).all()


def test_time_split_is_chronological_with_six_month_test_set(hourly_weather: pd.DataFrame) -> None:
    dataset = build_dataset(hourly_weather, VIBORA_PARK_PANEL)

    train, test = time_split(dataset)

    assert train.index.max() < test.index.min()
    assert test.index.min() > dataset.index.max() - pd.DateOffset(months=6)
    assert len(train) + len(test) == len(dataset)
