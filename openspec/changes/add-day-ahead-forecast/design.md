# Design

## Context

See proposal.md for motivation. Today `wh_forecast.data.open_meteo` fetches ERA5 archive data (`fetch_hourly`), `features.solar_features` builds nowcast features (including same-hour actual radiation and lags of actuals), `models.panel.SolarPanel.output_watts` is the physics formula, `models.xgb_model.SolarXGBModel` is a regressor wrapper and `models.train` is the training flow. `config.py` holds the location, paths (resolved from the project root) and the panel. The hourly actuals file covers 2021-01-01 to 2026-08-26 (49,536 rows). Both forecast endpoints were checked to respond for this location: `historical-forecast-api.open-meteo.com/v1/forecast` (past forecasts, by date range) and `api.open-meteo.com/v1/forecast` (next days).

## Goals / Non-Goals

**Goals:**
- A day-ahead forecast whose value over the raw-forecast physics baseline is measured and visible.
- Reuse the panel physics, split and model wrapper; no changes to the nowcast.

**Non-Goals:**
- Serving (scheduled job, API, page), uncertainty ranges, real EcoFlow data, other locations.

## Decisions

**Residual target over direct target.** The model predicts `actual_wh - physics_wh(forecast)` and the final value is `physics_wh(forecast) + residual`, clipped to [0, cap]. The formula already carries most of the signal, so the model only learns the forecast's systematic error, and the baseline is exactly the "residual = 0" case, which makes the comparison direct. Alternative: predict `actual_wh` directly (kept as a cheap experiment in the evaluation, not as the shipped path).

**Target uses ERA5 actuals.** Actual Wh is the physics formula on ERA5 radiation and temperature. This corrects forecast errors but not panel-specific effects (shade, dust, angle); real EcoFlow data is a later change.

**Features from forecast only.** Nine forecast variables, physics output of the forecast, cyclical hour/month/day-of-year, forecast radiation of the previous and next hour, and the forecast radiation total for the day. Lags of actuals are excluded because tomorrow's actuals do not exist. Training and prediction share one feature function in `features/forecast_features.py`; it takes a forecast table and returns the feature frame (the target is added separately in training).

**New data files, same client module.** Add `fetch_historical_forecast` and `fetch_forecast` to `data/open_meteo.py` next to the archive functions, reusing the nine `HOURLY_VARIABLES`. The history is saved as `vibora_park_forecast_hourly.json` in `data/weather/`. Alternative: a separate module (rejected, same client and error handling).

**Reuse the model wrapper.** The residual regressor reuses `SolarXGBModel` (train, predict, save, load) with a different feature list and target, saved as `solar_residual.joblib`. If the wrapper hard-codes the 24 nowcast features, parameterise it by feature names instead of copying it. Persistence stays joblib for now; switching to XGBoost's JSON format is a separable follow-up.

**Chronological hold-out.** Last 6 months, using the existing `time_split`. Metrics in `evaluation/metrics.py` (hourly MAE/RMSE, daily-total absolute error, model vs baseline). Daily metrics only count days with all 24 hours.

**Charts with matplotlib, static PNG.** `evaluation/charts.py` writes five PNGs to `data/reports/`: sample days of forecast vs actual, daily total scatter, error by hour of day, daily error by month, model vs baseline bars. Static files fit the offline workflow and a later page can embed them. Alternative: notebook only (rejected, not reproducible from a command).

**Entry points.** `scripts/fetch_forecast_history.py`, `scripts/train_forecast_model.py` (trains, evaluates, writes charts) and `scripts/predict_tomorrow.py` (writes `data/forecasts/forecast.json`), each a thin wrapper over package functions.

## Risks / Trade-offs

- [Historical forecasts have short lead time, so hold-out scores look better than a real 24-hour-ahead forecast] → state it in the report and README; optionally log live next-day forecasts and the later actuals to measure real lead time.
- [Model does not beat the baseline] → report it as the result; the shipped forecast then uses the better of the two and the README says so, rather than hiding the comparison.
- [Residual is near zero at night and noisy near sunrise/sunset] → clip to [0, cap] and force 0 for zero forecast radiation.
- [Historical-forecast data may have gaps or changed model versions over time] → drop incomplete hours, check coverage per year in the data task, note the model-version change as a limitation.
- [Open-Meteo rate limits on long ranges] → fetch in yearly chunks.
