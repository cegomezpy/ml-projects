# Spec Delta

## Purpose

Shows how precise the day-ahead forecast is by comparing it with a no-model baseline on held-out data, with numbers and charts.

## ADDED Requirements

### Requirement: Baseline comparison
The system SHALL compare the day-ahead model on the hold-out set against the baseline of applying the physics formula directly to the raw forecast, and SHALL report both under the same metrics.

#### Scenario: Both reported
- **WHEN** evaluation runs on the hold-out set
- **THEN** the result contains the metrics of the model and of the baseline, and states whether the model beat the baseline on each metric

### Requirement: Hourly and daily metrics
The system SHALL report hourly MAE and RMSE in Wh and, per day, the absolute error of the daily total in Wh (mean absolute daily error and its mean as a percentage of the mean actual daily total).

#### Scenario: Daily total error
- **WHEN** evaluation aggregates the hold-out hours by calendar day
- **THEN** the daily error is computed from the sum of 24 hourly forecasts against the sum of 24 actual hourly outputs, only for days with all 24 hours present

### Requirement: Evaluation charts
The system SHALL save PNG charts to the reports directory showing: forecast vs actual hourly output for a sample of days, forecast vs actual daily totals as a scatter with the identity line, hourly error by hour of day, daily error by month, and model vs baseline error side by side.

#### Scenario: Charts written
- **WHEN** the evaluation report is generated
- **THEN** one PNG per chart is written to the reports directory, each with titled axes including units, and the run reports their paths

#### Scenario: Empty hold-out
- **WHEN** the hold-out set has no complete days
- **THEN** report generation fails with an error instead of writing empty charts
