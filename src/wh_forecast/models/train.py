"""Train and persist the hourly solar output model."""

import json
from pathlib import Path
from typing import Any

import pandas as pd

from wh_forecast.config import VIBORA_PARK_PANEL
from wh_forecast.features.solar_features import FEATURES, TARGET, build_dataset, time_split
from wh_forecast.models.panel import SolarPanel
from wh_forecast.models.xgb_model import SolarXGBModel

MODEL_FILENAME = "solar_xgb.joblib"


def train_solar_model(
    hourly_data_path: Path,
    model_save_dir: Path,
    panel: SolarPanel = VIBORA_PARK_PANEL,
    test_months: int = 6,
    params: dict[str, Any] | None = None,
    device: str | None = None,
) -> dict[str, Any]:
    """Train the model on an Open-Meteo hourly JSON file and save it.

    Business flow: load the hourly weather, derive the physics target and features,
    split chronologically, train, evaluate on the held-out months, save.

    Args:
        hourly_data_path: Open-Meteo hourly JSON file.
        model_save_dir: Directory where the model file is written.
        panel: Panel used to derive the output target.
        test_months: Trailing months held out as the test set.
        params: Optional XGBoost parameter overrides.
        device: "cuda" or "cpu"; detected automatically when omitted.

    Returns:
        Model path, train and test metrics, row counts and the device used.
    """
    with open(hourly_data_path, encoding="utf-8") as f:
        raw = json.load(f)

    weather = pd.DataFrame(raw["hourly"])
    weather["time"] = pd.to_datetime(weather["time"])
    weather = weather.set_index("time").sort_index()

    dataset = build_dataset(weather, panel)
    train_df, test_df = time_split(dataset, test_months=test_months)
    X_train, y_train = train_df[FEATURES].values, train_df[TARGET].values
    X_test, y_test = test_df[FEATURES].values, test_df[TARGET].values
    print(f"Train: {len(X_train):,} rows  Test: {len(X_test):,} rows")

    model = SolarXGBModel(params=params, device=device)
    train_metrics = model.train(X_train, y_train, X_val=X_test, y_val=y_test)
    test_metrics = model.evaluate(X_test, y_test)

    save_path = Path(model_save_dir) / MODEL_FILENAME
    model.save(save_path)
    print(f"\nTest metrics:  {test_metrics.to_dict()}")
    print(f"Model saved to: {save_path}")

    return {
        "model_path": str(save_path),
        "train_metrics": train_metrics.to_dict(),
        "test_metrics": test_metrics.to_dict(),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "device": model.device,
    }
