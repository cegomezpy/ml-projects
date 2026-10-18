# Spec Delta

## Purpose

Predicts tomorrow's hourly energy (Wh) and daily total for the configured panel from the weather forecast, by correcting the physics output of the raw forecast with a learned residual.

## ADDED Requirements

### Requirement: Forecast-only features
The system SHALL build model inputs only from forecast values and the calendar: the nine forecast variables, the physics output of the forecast for that hour, cyclical hour, month and day-of-year encodings, the forecast radiation of the previous and next hours, and the forecast radiation total of that day. It SHALL NOT use actual (ERA5) values or lags of actual values.

#### Scenario: Features at prediction time
- **WHEN** features are built from tomorrow's 24 forecast hours
- **THEN** every feature column is computed without any actual observation, and no row has missing values

### Requirement: Residual target
The system SHALL train on the residual between the actual output and the physics output of the forecast, where the actual output is the physics formula applied to ERA5 actual radiation and temperature and the forecast output is the same formula applied to the forecast radiation and temperature.

#### Scenario: Residual definition
- **WHEN** the training target is built for an hour
- **THEN** it equals actual output Wh minus forecast physics output Wh for that hour

### Requirement: Chronological training and persistence
The system SHALL split the aligned data chronologically, using the most recent 6 months as the hold-out set, train a gradient-boosted regressor on the earlier rows, and save the trained model to the models directory.

#### Scenario: Training run
- **WHEN** day-ahead training is run on the aligned data
- **THEN** a model file is written, and no hold-out timestamp is earlier than any training timestamp

#### Scenario: Too few samples
- **WHEN** training is attempted with fewer samples than the minimum
- **THEN** training fails with an insufficient-data error

### Requirement: Final forecast composition
The system SHALL compute each hour's forecast as the physics output of the forecast plus the predicted residual, clipped between 0 Wh and the panel's input cap, and SHALL return 0 Wh for hours with zero forecast radiation.

#### Scenario: Clipping
- **WHEN** the predicted residual would push an hour below 0 or above the cap
- **THEN** the forecast for that hour is 0 or the cap respectively

#### Scenario: Night hours
- **WHEN** the forecast shortwave radiation for an hour is 0
- **THEN** the forecast for that hour is 0 Wh

### Requirement: Predict command
The system SHALL provide a command that fetches tomorrow's forecast, applies the trained model and writes a forecast file containing the date, the 24 hourly Wh values, the daily total in Wh and the time the file was generated.

#### Scenario: Successful prediction
- **WHEN** the predict command runs with a trained model and a complete forecast
- **THEN** the forecast file holds 24 hourly values for tomorrow, their sum as the daily total, and a generation timestamp

#### Scenario: Model missing
- **WHEN** the predict command runs and no trained model file exists
- **THEN** it fails with a clear error and writes no forecast file
