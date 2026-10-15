"""Feature engineering and target derivation for solar output prediction."""

import numpy as np
import pandas as pd

from wh_forecast.models.panel import SolarPanel

FEATURES = [
    "shortwave_radiation",
    "direct_radiation",
    "diffuse_radiation",
    "cloud_cover",
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "surface_pressure",
    "sunshine_duration",
    "hour_sin",
    "hour_cos",
    "month_sin",
    "month_cos",
    "doy_sin",
    "doy_cos",
    "rad_lag1h",
    "rad_lag2h",
    "rad_lag3h",
    "rad_lag6h",
    "rad_lag12h",
    "rad_lag24h",
    "rad_roll3h",
    "rad_roll6h",
    "rad_roll24h",
]

TARGET = "output_wh"


def build_dataset(df: pd.DataFrame, panel: SolarPanel) -> pd.DataFrame:
    """Add physics-derived target and time/lag features to hourly weather DataFrame.

    Args:
        df: Hourly weather DataFrame indexed by datetime.
        panel: Solar panel specs used to compute the output target.

    Returns:
        DataFrame with all FEATURES columns and TARGET column, NaNs dropped.
    """
    out = df.copy()

    # Physics target
    out[TARGET] = [
        panel.output_watts(rad, temp)
        for rad, temp in zip(out["shortwave_radiation"], out["temperature_2m"])
    ]

    # Cyclical time encoding — avoids ordinality discontinuity at midnight / Jan
    out["hour_sin"] = np.sin(2 * np.pi * out.index.hour / 24)
    out["hour_cos"] = np.cos(2 * np.pi * out.index.hour / 24)
    out["month_sin"] = np.sin(2 * np.pi * out.index.month / 12)
    out["month_cos"] = np.cos(2 * np.pi * out.index.month / 12)
    out["doy_sin"] = np.sin(2 * np.pi * out.index.dayofyear / 365)
    out["doy_cos"] = np.cos(2 * np.pi * out.index.dayofyear / 365)

    # Radiation lags — recent sky memory
    for lag in [1, 2, 3, 6, 12, 24]:
        out[f"rad_lag{lag}h"] = out["shortwave_radiation"].shift(lag)

    # Rolling means — trend persistence
    out["rad_roll3h"] = out["shortwave_radiation"].rolling(3, min_periods=1).mean()
    out["rad_roll6h"] = out["shortwave_radiation"].rolling(6, min_periods=1).mean()
    out["rad_roll24h"] = out["shortwave_radiation"].rolling(24, min_periods=1).mean()

    return out.dropna()


def time_split(df: pd.DataFrame, test_months: int = 6) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split DataFrame into train/test on a time boundary.

    Always splits chronologically — never shuffles — to avoid future leakage.
    """
    split_date = df.index.max() - pd.DateOffset(months=test_months)
    return df[df.index <= split_date], df[df.index > split_date]
