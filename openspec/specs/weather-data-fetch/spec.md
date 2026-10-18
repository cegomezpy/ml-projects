# weather-data-fetch Specification

## Purpose
Baseline of today's weather ingestion: retrieves historical daily and hourly weather for a location from Open-Meteo's archive service and stores it locally as raw JSON. This change must preserve this behavior.

## Requirements

### Requirement: Fetch hourly historical weather
The system SHALL fetch hourly temperature, humidity, precipitation, cloud cover, total/direct/diffuse shortwave radiation, sunshine duration and surface pressure for a latitude/longitude and date range, and SHALL save the raw response as `<location_name>_hourly.json` in the configured directory.

#### Scenario: Successful hourly fetch
- **WHEN** a valid location and date range are requested
- **THEN** the raw response is saved under the configured directory and returned, and the number of saved hourly records is reported

#### Scenario: Service error
- **WHEN** the service returns a non-success status or the network request fails
- **THEN** the error is raised to the caller and no file is written

### Requirement: Fetch daily historical weather
The system SHALL fetch daily temperature, precipitation, cloud cover, wind, humidity, radiation, sunshine and pressure aggregates for a location and date range, and SHALL save the raw response as `<location_name>_raw.json`.

#### Scenario: Successful daily fetch
- **WHEN** a valid location and date range are requested
- **THEN** the raw daily response is saved and returned
