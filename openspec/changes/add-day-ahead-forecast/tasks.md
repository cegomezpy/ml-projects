# Tasks

Use test-driven development for every task (failing test first), and run verification before checking a task off.

## 1. Forecast data

- [ ] 1.1 Add `fetch_historical_forecast` (yearly chunks, nine variables, saves `vibora_park_forecast_hourly.json`) and `fetch_forecast` (next calendar day, 24 hours) to `data/open_meteo.py`, with mocked-HTTP tests for success, file saved, error without file written and incomplete tomorrow; verify the tests pass
- [ ] 1.2 Add `scripts/fetch_forecast_history.py`, run it for 2021-01-01 to the last actuals date, and verify the file exists with the nine variables and report per-year row coverage and gaps in a comment at the bottom of this file
- [ ] 1.3 Add the alignment function that joins forecast rows to ERA5 actuals by timestamp and drops hours missing from either, with tests for matching, missing hours and no actual columns reaching the inputs; verify they pass

## 2. Features, target and model

- [ ] 2.1 Create `features/forecast_features.py` with forecast-only features (nine variables, physics output of forecast, cyclical time, previous/next-hour radiation, daily radiation total) and the residual target builder; tests for no missing values, no actual columns used and residual = actual Wh - forecast Wh; verify they pass
- [ ] 2.2 Generalise the model wrapper to take feature names (nowcast behaviour unchanged) and verify the existing nowcast tests and the slow regression test still pass
- [ ] 2.3 Add the residual training flow (chronological 6-month hold-out, minimum samples, save `solar_residual.joblib`) and the forecast composition function (physics + residual, clip to [0, cap], zero at zero radiation); tests for clipping, night hours, too few samples and no hold-out leakage; verify they pass

## 3. Evaluation and charts

- [ ] 3.1 Add `evaluation/metrics.py` with hourly MAE/RMSE, daily-total error (complete days only) and the model vs baseline comparison; tests on small hand-computed examples; verify they pass
- [ ] 3.2 Add `evaluation/charts.py` writing the five PNGs to `data/reports/`, failing on an empty hold-out; tests that the files are written and that an empty hold-out raises; verify they pass and open the PNGs to check they read correctly
- [ ] 3.3 Add `scripts/train_forecast_model.py` (train, evaluate, charts), run it on the real data, and record hold-out metrics for model and baseline, the verdict on beating the baseline, and the residual-vs-direct-target experiment in a comment at the bottom of this file

## 4. Prediction and docs

- [ ] 4.1 Add the predict function and `scripts/predict_tomorrow.py` writing `data/forecasts/forecast.json` (date, 24 hourly Wh, daily total, generated-at); tests with a mocked forecast for success and for a missing model file; verify they pass and run the script once against the live API
- [ ] 4.2 Update README (day-ahead usage, how to read the charts, the lead-time caveat and the real result vs baseline) and the CLAUDE.md layout line; verify every documented command runs as written

## 5. Integration check

- [ ] 5.1 Run the full test suite, pre-commit hooks and mypy on `src/wh_forecast`, and verify all pass
- [ ] 5.2 Run `superpowers:requesting-code-review` and verify no blocking findings remain
