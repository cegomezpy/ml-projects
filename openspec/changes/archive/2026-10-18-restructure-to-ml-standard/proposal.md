# Proposal

## Why

The repo is organised as a generic FastAPI/DDD model-CRUD service (domain, application, presentation, infrastructure), but the project is now a single-purpose solar output forecaster that will be served as a small web app. The DDD layers are mostly unused by the solar code (it only borrows `Model`, `ModelType` and `IMLService`), the root folder is cluttered, and the name `ml-projects` no longer describes the project. A forecaster built on this layout would carry dead scaffolding and the DDD rules in `.claude/instructions.md` that contradict the chosen ML-standard layout.

## What Changes

- Rename the project to `wh-generation-forecast` (Python package `wh_forecast`) in `pyproject.toml`, README and any in-code names.
- **BREAKING**: remove the generic model-CRUD scaffolding: `main.py`, `src/domain`, `src/application`, `src/presentation`, `src/infrastructure/{repositories,persistence}`, `sklearn_service.py`, the generic model/prediction DTOs and routes, and the `models/` metadata handling.
- **BREAKING**: replace the DDD layout with an ML-standard package: `src/wh_forecast/{data,features,models,api}` plus `config.py`. Solar code is migrated without behavior change: `SolarPanel` and panel constants to `config.py`, `solar_feature_pipeline` to `features/`, XGBoost training and evaluation to `models/`, Open-Meteo clients and scrapers to `data/`.
- Training and fetch scripts keep working as thin entry points in `scripts/`.
- Move `notebooks/` content as-is; update imports.
- Declutter the root: keep `pyproject.toml`, `uv.lock`, `uv.toml`, `README.md`, `CLAUDE.md`, `.python-version`, `.gitignore`, `.gitattributes`, `.pre-commit-config.yaml`, `.env.example`; move `PRE_COMMIT_SETUP.md` into `docs/`; delete `DEVELOPMENT_GUIDELINES.md` and `.claude/instructions.md`.
- Move the surviving coding rules (type hints, docstring-documented flow, no numbered inline comments, domain-style naming where it helps) into `CLAUDE.md`.
- Drop the `fastapi`-based generic app dependencies that nothing uses until the thin `api/` returns in the forecast change; keep the `api/` package as an empty placeholder.
- Add tests that pin current behavior (panel output, feature building, chronological split) before moving code, plus a regression check that training on the saved hourly data reproduces the prior metrics.

Out of scope: any forecasting work (separate change `add-day-ahead-forecast`), the GitHub repo rename and the local folder rename, real EcoFlow data ingestion.

## Capabilities

### New Capabilities
- `solar-output-model`: baseline spec of today's behavior: derive physics-based hourly output from weather, build features, split chronologically, train and persist the XGBoost model, report test metrics.
- `weather-data-fetch`: baseline spec of today's behavior: fetch daily and hourly historical weather for a location from Open-Meteo's archive and save raw JSON.

### Modified Capabilities
<!-- None: openspec/specs/ is empty; these baseline specs describe existing behavior that must not change. -->

## Impact

- Code: everything under `src/`, plus `scripts/`, `main.py`, `notebooks/` imports, `pyproject.toml` (name, packages, description, dependencies, tool targets), `README.md`, `CLAUDE.md`, `.claude/instructions.md`, `DEVELOPMENT_GUIDELINES.md`, `PRE_COMMIT_SETUP.md`.
- Data and artifacts: `data/` and `data/models/solar_xgb.joblib` locations are kept; the saved model must still load or be reproducible with the new package path (joblib pickles reference module paths, so retraining is expected).
- Dependencies: remove unused FastAPI stack for now; others unchanged.
- No external API or user-facing behavior changes; the prior test metrics are the acceptance baseline.
