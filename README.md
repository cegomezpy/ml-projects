# Wh Generation Forecast

Predicts how much energy (Wh) a solar panel produces each hour, using weather data from [Open-Meteo](https://open-meteo.com/). The goal is a **day-ahead forecast**: tomorrow's 24 hourly Wh values and daily total for a Romma RM-620W panel feeding an EcoFlow Delta 2, so you can plan when the battery will charge.

The project is in progress. Today it trains and evaluates an hourly output model on past weather. The day-ahead forecast and the web app are the next steps (see [Roadmap](#roadmap)).

## The setup being modelled

| | |
|---|---|
| Location | Vibora Park, Havana (23.08 N, -82.35 W, America/Havana) |
| Panel | Romma RM-620W-182R/132TB, 2.382 x 1.134 m, about 22.95 % efficiency |
| Temperature coefficient | -0.30 % per degree C |
| Power station | EcoFlow Delta 2, MPPT efficiency 95 %, input capped at 500 W |

## How it works

```
Open-Meteo archive (ERA5) --> hourly weather JSON --> features --> XGBoost --> solar_xgb.joblib
                                       |
                                       +--> target: physics model of the panel (Wh)
```

1. **Data.** Hourly weather since 2021: radiation (total, direct, diffuse), cloud cover, temperature, humidity, precipitation, pressure and sunshine duration.
2. **Target.** Hourly output computed with a physics model: `P = radiation x area x efficiency x (1 + coef x (T - 25)) x MPPT`, clipped between 0 W and the 500 W cap. Real EcoFlow readings are not used yet.
3. **Features.** The weather variables, cyclical hour / month / day-of-year encodings, radiation lags (1 to 24 h) and rolling means (3, 6 and 24 h): 24 in total.
4. **Training.** XGBoost regression (GPU when an NVIDIA GPU is available, CPU otherwise). The split is chronological: the last 6 months are the test set and nothing is shuffled.

### Current results and limits

On the saved data (45,168 training hours, 4,344 test hours) the model scores R2 1.0, RMSE 0.79 Wh and MAE 0.43 Wh. Read these numbers with care:

- The model **learns the physics formula**, so near-perfect scores are expected. It does not yet reflect your real panel (shading, dust, angle, battery behaviour).
- It is a **nowcast**: its inputs include the current hour's actual radiation, which is unknown for future hours. It tells you the output *given* the weather, not tomorrow's output.

Both are addressed in the roadmap.

## Getting started

Requires Python 3.13 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra dev                              # install dependencies
uv run pytest                                    # run the tests

uv run python scripts/fetch_vibora_park_hourly.py  # download hourly weather (2021 to today)
uv run python scripts/fetch_vibora_park_data.py    # download daily weather (2016 to today)
uv run python scripts/train_solar_model.py         # train and save the model
```

Data lands in `data/weather/` and the trained model in `data/models/solar_xgb.joblib`. Both folders are git-ignored, so run the fetch script first on a fresh clone. Training takes about 2 minutes on a laptop GPU.

Optional: `uv run python -m wh_forecast.data.scrapers.run` scrapes solar panel listings from Revolico into `data/solar_panels_raw.json`. It is independent of the forecast.

## Project layout

```
src/wh_forecast/
  config.py        location, data paths and the panel installation
  data/            Open-Meteo client, scrapers
  features/        feature building and the chronological split
  models/          panel physics, XGBoost model, metrics, training flow
  api/             reserved for the web API
scripts/           entry points: fetch data, train
notebooks/         01_weather_eda, 02_solar_prediction (exploration)
tests/             pytest unit tests
data/              weather data and trained models (git-ignored)
docs/              extra documentation
openspec/          specs and change proposals
```

Notebooks only read from `data/`; they do not import the package.

## Roadmap

1. **Restructure** (this change): ML-standard layout, package `wh_forecast`, tests around the existing model.
2. **Day-ahead forecast**: train on what Open-Meteo's forecast said at the time (historical-forecast API) against the actual output, so the model learns typical forecast errors. At prediction time it uses tomorrow's forecast and returns 24 hourly Wh values plus the daily total. It must beat the baseline of applying the physics formula directly to the raw forecast.
3. **Web app**: a daily scheduled job writes `forecast.json`, and a thin API / page serves it.
4. **Later**: real EcoFlow readings as ground truth, uncertainty ranges.

## Development

The project uses [OpenSpec](https://github.com/Fission-AI/OpenSpec) for specs and planning, and Superpowers skills (test-driven development, verification, code review) while implementing. See [CLAUDE.md](CLAUDE.md) for the workflow and code conventions, and [docs/PRE_COMMIT_SETUP.md](docs/PRE_COMMIT_SETUP.md) for the pre-commit hooks.
