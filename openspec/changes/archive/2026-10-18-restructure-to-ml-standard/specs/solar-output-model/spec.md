# Spec Delta

## Purpose

Baseline of today's solar output model: derives hourly panel output from weather, trains a regression model on past hours and reports hold-out metrics. This change must preserve this behavior while the code is restructured.

## ADDED Requirements

### Requirement: Physics-derived hourly output target
The system SHALL compute the hourly output target in Wh for a configured solar panel from shortwave radiation and air temperature, applying temperature derating and MPPT efficiency, and clipping the result between 0 W and the panel's hardware input cap.

#### Scenario: Output is capped
- **WHEN** radiation is high enough that the computed power exceeds the configured input cap (500 W for the Vibora Park panel)
- **THEN** the target for that hour equals the cap

#### Scenario: No sunlight
- **WHEN** shortwave radiation is 0
- **THEN** the target for that hour is 0 Wh

#### Scenario: Invalid panel specification
- **WHEN** a panel is configured with a non-positive area, an efficiency outside (0, 1], an MPPT efficiency outside (0, 1], or a non-positive input cap
- **THEN** configuration is rejected with an error

### Requirement: Feature set for the output model
The system SHALL build, from an hourly weather table indexed by time, the weather variables, cyclical hour, month and day-of-year encodings, radiation lags of 1, 2, 3, 6, 12 and 24 hours, and rolling radiation means over 3, 6 and 24 hours, and SHALL drop rows with missing values.

#### Scenario: Dataset built from hourly weather
- **WHEN** an hourly weather table is passed to dataset building
- **THEN** the result contains all 24 feature columns and the target column, with no missing values

### Requirement: Chronological train/test split
The system SHALL split data by time, using the most recent configured number of months (default 6) as the test set and everything earlier as the training set, and SHALL NOT shuffle rows.

#### Scenario: Default split
- **WHEN** a dataset is split with the default setting
- **THEN** every test timestamp is later than every training timestamp, and the test set covers the last 6 months of the data

### Requirement: Train and persist the output model
The system SHALL train a gradient-boosted regression model on the training set, validating on the test set, evaluate it on the test set with R2, MSE, RMSE and MAE, and save the trained model to a configured directory.

#### Scenario: Training from a saved hourly file
- **WHEN** training is run on the saved hourly Open-Meteo JSON file
- **THEN** a model file is written to the configured directory and the run returns train metrics, test metrics, row counts and the model path

#### Scenario: Metrics unchanged by restructuring
- **WHEN** training is run on the same hourly file before and after the project restructuring
- **THEN** test R2, RMSE and MAE agree within a small tolerance (fixed random seed)

#### Scenario: Too few samples
- **WHEN** training is attempted with fewer samples than the minimum
- **THEN** training fails with an insufficient-data error

#### Scenario: Prediction before training
- **WHEN** a prediction is requested from a model that has not been trained
- **THEN** it fails with a model-not-trained error
