# Proposal

## Why

The trained model is a nowcast: its inputs include the current hour's actual radiation, so it can only say what the panel produces once the weather is known. The goal of the project is to plan ahead, that is, to know tomorrow's hourly Wh and daily total. Open-Meteo already publishes weather forecasts for free, so the open question is how much a model trained on past forecast errors improves on applying the physics formula straight to the raw forecast.

## What Changes

- Fetch, from the Open-Meteo historical-forecast API, the forecast values that were issued at the time (same 9 hourly variables as today), and from the forecast API the values for tomorrow.
- Train a day-ahead model on forecast-only features. The target is the residual `actual_wh - physics_wh(forecast)`, where `actual_wh` comes from the physics formula applied to ERA5 actual radiation and temperature. The final forecast is `physics_wh(forecast) + predicted residual`, clipped between 0 and the panel cap.
- Evaluate on a chronological hold-out (last 6 months) against the baseline "physics formula on the raw forecast", with hourly MAE/RMSE and daily-total Wh error. The change only counts as an improvement if the model beats the baseline on the hold-out.
- Produce evaluation charts (forecast vs actual, error by hour and by month, daily total scatter, model vs baseline) saved as PNG files, so the precision can be seen and not only read from numbers.
- Add a `predict` command that writes tomorrow's 24 hourly Wh values and daily total to `data/forecasts/forecast.json`.
- Out of scope: the scheduled job and the web API/page that serve `forecast.json` (a later change), uncertainty ranges, real EcoFlow readings as target, other locations. The existing nowcast stays untouched.

## Capabilities

### New Capabilities

- `forecast-data`: fetching and storing historical-forecast data (what the forecast said at the time) and tomorrow's forecast, aligned with the existing ERA5 actuals.
- `day-ahead-forecast`: forecast-only feature building, the residual model on top of the physics formula, training, and the `predict` command producing the 24-hour forecast file.
- `forecast-evaluation`: baseline comparison, hold-out metrics (hourly and daily) and the evaluation charts.

### Modified Capabilities

None. `solar-output-model` and `weather-data-fetch` keep their requirements; the new capabilities reuse the panel physics and the chronological split as they are.

## Impact

- New code under `src/wh_forecast/data/` (forecast client), `features/` (forecast features), `models/` (residual model, training, prediction), a new `evaluation/` package (metrics and charts), plus thin scripts in `scripts/`.
- New data files in `data/weather/` (historical forecast), `data/forecasts/` (forecast.json) and `data/reports/` (PNG charts), all git-ignored. A new model file in `data/models/`.
- No new dependencies: `matplotlib` is already installed and `httpx`, `xgboost` are in use.
- Risk to verify during design: the historical-forecast API returns forecasts with short lead time, so hold-out scores may look better than a true 24-hour-ahead forecast would.
