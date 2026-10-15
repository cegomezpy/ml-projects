"""Solar panel value object with physical characteristics."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SolarPanel:
    """Immutable physical specs of a solar panel installation.

    Attributes:
        area_m2: Panel surface area in square metres.
        efficiency: STC efficiency as a decimal (e.g. 0.2295 for 22.95%).
        temp_coefficient: Power temp coefficient per °C (e.g. -0.003 for -0.30%/°C).
        max_input_watts: Hardware cap imposed by the charge controller / power station.
        mppt_efficiency: MPPT converter efficiency as a decimal (e.g. 0.95).
    """

    area_m2: float
    efficiency: float
    temp_coefficient: float
    max_input_watts: float
    mppt_efficiency: float = 0.95

    def __post_init__(self) -> None:
        if self.area_m2 <= 0:
            raise ValueError("Panel area must be positive")
        if not 0 < self.efficiency <= 1:
            raise ValueError("Efficiency must be between 0 and 1")
        if not 0 < self.mppt_efficiency <= 1:
            raise ValueError("MPPT efficiency must be between 0 and 1")
        if self.max_input_watts <= 0:
            raise ValueError("Max input watts must be positive")

    def output_watts(self, radiation_w_m2: float, temperature_c: float) -> float:
        """Compute instantaneous output power in watts.

        Applies temperature derating and clips to the hardware cap.
        """
        temp_factor = 1.0 + self.temp_coefficient * (temperature_c - 25.0)
        power = radiation_w_m2 * self.area_m2 * self.efficiency * temp_factor * self.mppt_efficiency
        return max(0.0, min(power, self.max_input_watts))
