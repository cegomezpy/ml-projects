"""Characterization tests for SolarPanel output calculation."""

import pytest

from wh_forecast.config import VIBORA_PARK_PANEL
from wh_forecast.models.panel import SolarPanel


def test_zero_radiation_gives_zero_output() -> None:
    assert VIBORA_PARK_PANEL.output_watts(0.0, 25.0) == 0.0


def test_output_is_capped_at_hardware_limit() -> None:
    assert VIBORA_PARK_PANEL.output_watts(1200.0, 25.0) == 500.0


def test_output_follows_formula_below_cap() -> None:
    panel = VIBORA_PARK_PANEL
    expected = 100.0 * panel.area_m2 * panel.efficiency * panel.mppt_efficiency
    assert panel.output_watts(100.0, 25.0) == pytest.approx(expected)


def test_hot_panel_produces_less_than_reference_temperature() -> None:
    assert VIBORA_PARK_PANEL.output_watts(300.0, 45.0) < VIBORA_PARK_PANEL.output_watts(300.0, 25.0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"area_m2": 0.0},
        {"efficiency": 0.0},
        {"efficiency": 1.5},
        {"mppt_efficiency": 0.0},
        {"mppt_efficiency": 1.1},
        {"max_input_watts": 0.0},
    ],
)
def test_invalid_panel_specs_are_rejected(kwargs: dict) -> None:
    valid = {
        "area_m2": 2.0,
        "efficiency": 0.2,
        "temp_coefficient": -0.003,
        "max_input_watts": 500.0,
    }
    with pytest.raises(ValueError):
        SolarPanel(**{**valid, **kwargs})
