"""Project configuration: location, data paths and the solar panel installation."""

from pathlib import Path

from wh_forecast.models.panel import SolarPanel

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
WEATHER_DIR = DATA_DIR / "weather"
MODELS_DIR = DATA_DIR / "models"

LOCATION_NAME = "vibora_park"
LATITUDE = 23.08
LONGITUDE = -82.35
TIMEZONE = "America/Havana"

# Romma RM-620W-182R/132TB connected to EcoFlow Delta 2
VIBORA_PARK_PANEL = SolarPanel(
    area_m2=2.382 * 1.134,
    efficiency=620 / (1000 * 2.382 * 1.134),
    temp_coefficient=-0.003,
    max_input_watts=500.0,
    mppt_efficiency=0.95,
)
