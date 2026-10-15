"""Fetch daily historical weather data for Vibora Park from Open-Meteo."""

from datetime import date

from wh_forecast.config import LATITUDE, LOCATION_NAME, LONGITUDE, TIMEZONE, WEATHER_DIR
from wh_forecast.data.open_meteo import fetch_historical

if __name__ == "__main__":
    fetch_historical(
        location_name=LOCATION_NAME,
        latitude=LATITUDE,
        longitude=LONGITUDE,
        start_date="2016-01-01",
        end_date=date.today().isoformat(),
        timezone=TIMEZONE,
        save_dir=WEATHER_DIR,
    )
