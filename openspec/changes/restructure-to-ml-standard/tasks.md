# Tasks

Use test-driven development for every task (failing test first), and run verification before checking a task off.

## 1. Baseline before touching code

- [x] 1.1 Run `scripts/train_solar_model.py` on `data/weather/vibora_park_hourly.json`, record test R2/RMSE/MAE, row counts and device in a comment block at the bottom of this file, and verify the numbers are written down
- [x] 1.2 Add characterization tests in `tests/unit/` against the current code for `SolarPanel.output_watts` (cap, zero radiation, temperature derating, invalid specs), `build_dataset` (24 features plus target, no NaNs) and `time_split` (chronological, last 6 months), and verify `uv run pytest` passes on the old layout

## 2. New package skeleton and config

- [x] 2.1 Create `src/wh_forecast/{data,features,models,api}` with `__init__.py` files and `config.py` holding location, paths and the Vibora Park panel constants, point hatch `packages` to `src/wh_forecast`, and verify `uv sync` followed by `uv run python -c "import wh_forecast"` succeeds
- [x] 2.2 Rename the project to `wh-generation-forecast` in `pyproject.toml` (name, description, black/ruff target py313), and verify `uv sync` succeeds

## 3. Migrate solar code

- [x] 3.1 Move `SolarPanel` to `wh_forecast/models/panel.py`, repoint its tests, and verify the panel tests pass
- [x] 3.2 Move the feature pipeline to `wh_forecast/features/solar_features.py`, repoint its tests, and verify the feature and split tests pass
- [x] 3.3 Port the XGBoost trainer to `wh_forecast/models/xgb_model.py` without `Model`/`IMLService`, with metrics as a frozen dataclass and plain `InsufficientDataError` / `ModelNotTrainedError`; add tests for too-few-samples and predict-before-train, and verify they pass
- [x] 3.4 Port the training flow to `wh_forecast/models/train.py` and the thin `scripts/train_solar_model.py`, and verify the script runs end to end
- [x] 3.5 Compare the migrated training metrics with the baseline in 1.1 (same seed, same device, small tolerance), and verify they agree
- [x] 3.6 Move the Open-Meteo client to `wh_forecast/data/open_meteo.py` and the scrapers to `wh_forecast/data/scrapers/`, update `scripts/fetch_*.py`, add tests for fetch success, saved file name and error without file written using a mocked HTTP client, and verify they pass
- [x] 3.7 Update imports in `notebooks/` and verify both notebooks run top to bottom

## 4. Remove the old architecture

- [x] 4.1 Scan for remaining references to `domain`, `application`, `presentation`, `infrastructure`, `main`, `sklearn_service` and `src.`, and verify the scan is clean outside the files about to be deleted
- [x] 4.2 Delete `main.py`, `src/domain`, `src/application`, `src/presentation`, `src/infrastructure`, the empty `src/__init__.py` and generic model-CRUD files, and verify `uv run pytest` and both scripts still pass
- [x] 4.3 Remove unused dependencies (`fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `pytest-asyncio`) and verify `uv sync` and `uv run pytest` pass

## 5. Declutter root and docs

- [x] 5.1 Delete `DEVELOPMENT_GUIDELINES.md` and `.claude/instructions.md`, add a short "Code conventions" section to `CLAUDE.md` (type hints on public functions, flow in docstrings, no numbered inline comments, no obvious comments), remove the `@.claude/instructions.md` import line, and verify `CLAUDE.md` has no dangling reference
- [x] 5.2 Move `PRE_COMMIT_SETUP.md` to `docs/` and rewrite `README.md` for the new project (purpose, layout, setup with `uv`, how to fetch data and train), and verify the documented commands run as written
- [ ] 5.3 Verify the root contains only config files, `README.md`, `CLAUDE.md` and the folders `src`, `scripts`, `notebooks`, `data`, `models`, `tests`, `docs`, `openspec`

## 6. Integration check

- [x] 6.1 Run the full test suite, pre-commit hooks and mypy on `src/wh_forecast`, and verify all pass
- [ ] 6.2 Run `/opsx:verify` if enabled and `superpowers:requesting-code-review`, and verify no blocking findings remain

<!-- Baseline (task 1.1, old layout, 2026-10-15, device cuda: NVIDIA RTX 3050 Laptop GPU)
train_rows=45168 test_rows=4344
test: r2_score=1.0 mse=0.6309 rmse=0.7943 mae=0.4264
-->
