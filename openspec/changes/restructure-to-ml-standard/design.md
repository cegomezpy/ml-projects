# Design

## Context

See proposal.md for motivation. Today `src/` holds four DDD layers. The solar code lives in `infrastructure/ml_models` (`solar_feature_pipeline.py`, `xgb_service.py`), `domain/value_objects/solar_panel.py`, `application/use_cases/train_solar_model.py`, `infrastructure/weather` and `infrastructure/scrapers`. It reuses only `Model`, `ModelType`, `IMLService`, `RegressionMetrics`, `PredictionResult` and two domain exceptions. `tests/` is empty, so no behavior is pinned yet. Scripts and notebooks import in mixed styles (`src.infrastructure...`, and `application...` with a `sys.path` hack). `data/models/solar_xgb.joblib` is a pickle bound to current module paths.

## Goals / Non-Goals

**Goals:**
- A single installable package `wh_forecast` with an ML-standard layout, usable from scripts, notebooks and, later, the API without `sys.path` hacks.
- No behavior change to the nowcast model, proven by tests and a metrics regression check.
- A clean root folder and project rules that match the new architecture.

**Non-Goals:**
- Any forecasting, new features or new endpoints.
- Preserving the generic model-CRUD API or the sklearn service.
- Renaming the GitHub repo or the local folder.

## Decisions

**Layout.**
```
src/wh_forecast/
  config.py        panel spec, location, paths
  data/            open_meteo.py (archive client), scrapers/
  features/        solar_features.py (FEATURES, build_dataset, time_split)
  models/          panel.py (SolarPanel), xgb_model.py, train.py
  api/             placeholder, filled by add-day-ahead-forecast
scripts/           fetch_*.py, train_solar_model.py (thin wrappers)
notebooks/ data/ models/ tests/ docs/ openspec/
```
Alternatives: keep DDD (rejected: dead weight, contradicts the chosen standard); flat `src/` without a package (rejected: brings back the `sys.path` hacks).

**Drop the `Model` / `IMLService` abstractions.** The XGBoost trainer becomes a plain class with typed methods: train, predict, save, load, evaluate. Metrics become a small frozen dataclass. The two exceptions the spec needs (insufficient data, not trained) stay as plain exceptions in `models/`. Alternative: keep the interface for a second algorithm; rejected under YAGNI, since the notebook's Random Forest comparison does not need a production abstraction.

**Move `SolarPanel` to `models/panel.py`, constants to `config.py`.** It stays a frozen dataclass with the same validation and formula.

**Tests before moves.** Characterization tests for panel output, feature building and the split are written first and stay green through the move (TDD). A regression check trains on `data/weather/vibora_park_hourly.json` and compares metrics with the values recorded before any change; the baseline numbers are recorded in `tasks.md` section 1.

**Package config.** `[tool.hatch.build.targets.wheel] packages = ["src/wh_forecast"]`, installed editable with `uv sync`; scripts import `wh_forecast`. `black` and `ruff` targets move to py313 to match `.python-version`.

**Dependencies.** Remove `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings` and `pytest-asyncio` while unused; they return with the API change. Keep `scrapy`, since the solar-panel spider moves to `data/scrapers`; it is unrelated to forecasting and is a candidate for removal later.

**Docs and rules.** `CLAUDE.md` keeps the workflow section and gains a short "Code conventions" section (type hints on public functions, flow described in docstrings, no numbered inline comments, no obvious comments). `.claude/instructions.md` and `DEVELOPMENT_GUIDELINES.md` are deleted. `PRE_COMMIT_SETUP.md` moves to `docs/`. The README is rewritten for the new project.

## Risks / Trade-offs

- [Saved joblib model breaks because module paths change] → retrain with the fixed seed and compare metrics; keep the old file until the comparison passes.
- [Metrics differ slightly because XGBoost GPU is non-deterministic] → compare with a tolerance and run on the same device before and after.
- [Large deletion removes something still needed] → delete only after a references scan shows no remaining imports; git history holds the old layout.
- [Notebooks break on new imports] → update import cells and run them top to bottom once.
- [Scraper is dead weight] → migrated unchanged now; removal decided separately.
