"""Train the hourly solar output model from the saved Open-Meteo hourly data."""

from wh_forecast.config import LOCATION_NAME, MODELS_DIR, WEATHER_DIR
from wh_forecast.models.train import train_solar_model

if __name__ == "__main__":
    train_solar_model(
        hourly_data_path=WEATHER_DIR / f"{LOCATION_NAME}_hourly.json",
        model_save_dir=MODELS_DIR,
    )
