# Spec Delta

## Purpose

Provides the forecast inputs for day-ahead prediction: what the weather forecast said in the past, for training and evaluation, and what it says for tomorrow, for prediction.

## ADDED Requirements

### Requirement: Historical forecast download
The system SHALL download, from the Open-Meteo historical-forecast API, the hourly forecast values that were issued at the time for the nine hourly weather variables already used by the project (temperature, relative humidity, precipitation, cloud cover, shortwave/direct/diffuse radiation, sunshine duration, surface pressure) for the configured location and a given date range, and SHALL save them as JSON in the weather data directory.

#### Scenario: Historical forecast saved
- **WHEN** a historical-forecast download succeeds for a date range
- **THEN** a JSON file with one hourly record per hour of the range and all nine variables is written, and the number of records is reported

#### Scenario: Download fails
- **WHEN** the API returns an error status or the network request fails
- **THEN** the error is raised and no file is written

### Requirement: Tomorrow's forecast download
The system SHALL fetch, from the Open-Meteo forecast API, the same nine hourly variables for the next calendar day in the location's timezone, as 24 hourly records.

#### Scenario: Next-day forecast
- **WHEN** the next-day forecast is requested
- **THEN** it returns 24 hourly records dated tomorrow in America/Havana with all nine variables

#### Scenario: Incomplete forecast
- **WHEN** the API returns fewer than 24 hours or missing values for tomorrow
- **THEN** the request fails with an error that names the missing hours instead of predicting from partial data

### Requirement: Forecast and actuals aligned by hour
The system SHALL join historical-forecast rows to the ERA5 actual rows by timestamp, keep only hours present in both, and SHALL NOT use actual weather values as model inputs.

#### Scenario: Alignment
- **WHEN** forecast and actual tables are joined
- **THEN** each row carries the forecast variables as inputs and the actual radiation and temperature separately for computing the target, and hours missing from either table are dropped
