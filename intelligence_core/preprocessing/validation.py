"""
Input validation for incoming measurements.

Per the spec, the module must distinguish between:
    - available    -> value present and plausible
    - missing      -> key not present / value is None
    - invalid      -> value present but out of physical range or wrong type
    - not_applicable -> field doesn't apply to this plant's hardware

Never invent or interpolate a value here. This layer only classifies.
"""

from dataclasses import dataclass, field
from enum import Enum


class FieldStatus(str, Enum):
    AVAILABLE = "available"
    MISSING = "missing"
    INVALID = "invalid"
    NOT_APPLICABLE = "not_applicable"


# Physically plausible ranges for numeric fields. Extend as you learn more
# about the real sensor hardware. Keep these conservative (reject only
# clear nonsense).
PLAUSIBLE_RANGES = {
    "irradiance": (0, 1500),          # W/m^2
    "panel_temperature": (-20, 100),  # deg C
    "dc_voltage": (0, 1000),          # V
    "dc_current": (0, 100),           # A
    "ac_power": (0, 1000),            # kW (adjust to plant size)
    "battery_soc": (0, 100),          # %
    "battery_voltage": (0, 100),      # V
    "battery_current": (-200, 200),   # A (signed: charge/discharge)
    "battery_temperature": (-20, 80), # deg C
    "load_power": (0, 1000),          # kW
    "grid_voltage": (0, 500),         # V
    "grid_frequency": (45, 65),       # Hz
    "import_power": (0, 1000),        # kW
    "export_power": (0, 1000),        # kW
}

# Categorical/status fields — checked for presence and type only, not range.
CATEGORICAL_FIELDS = ["grid_status", "inverter_status", "sensor_status"]

# Fields where `None` is a legitimate value (not a missing-data signal).
# inverter_fault_code = null means "no active fault" per the measurement
# contract's own example (spec section 4) — it is only MISSING if the key
# itself is absent from the payload.
NULLABLE_FIELDS = ["inverter_fault_code"]


@dataclass
class ValidationResult:
    status: dict = field(default_factory=dict)  # field_name -> FieldStatus
    invalid_reasons: dict = field(default_factory=dict)  # field_name -> str

    @property
    def missing_fields(self) -> list:
        return [f for f, s in self.status.items() if s == FieldStatus.MISSING]

    @property
    def invalid_fields(self) -> list:
        return [f for f, s in self.status.items() if s == FieldStatus.INVALID]

    def quality_score(self) -> float:
        """
        Very simple completeness/validity score in [0, 1].
        Replace with something more principled once you have real data
        (e.g. weight by field importance, penalize staleness, etc.)
        """
        if not self.status:
            return 0.0
        good = sum(
            1 for s in self.status.values() if s == FieldStatus.AVAILABLE
        )
        return round(good / len(self.status), 3)


def validate_measurement(measurement: dict) -> ValidationResult:
    """
    Classify every known field in a raw measurement dict.

    Args:
        measurement: raw dict as sent by the backend (see spec section 4).

    Returns:
        ValidationResult with per-field status and a quality score.
    """
    result = ValidationResult()

    # 1. Numeric fields with a known plausible range.
    for field_name, (lo, hi) in PLAUSIBLE_RANGES.items():
        if field_name not in measurement or measurement[field_name] is None:
            result.status[field_name] = FieldStatus.MISSING
            continue

        value = measurement[field_name]

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            result.status[field_name] = FieldStatus.INVALID
            result.invalid_reasons[field_name] = f"non-numeric value: {value!r}"
            continue

        if not (lo <= value <= hi):
            result.status[field_name] = FieldStatus.INVALID
            result.invalid_reasons[field_name] = (
                f"value {value} outside plausible range [{lo}, {hi}]"
            )
            continue

        result.status[field_name] = FieldStatus.AVAILABLE

    # 2. Categorical/status fields — presence and type only.
    for field_name in CATEGORICAL_FIELDS:
        if field_name not in measurement or measurement[field_name] is None:
            result.status[field_name] = FieldStatus.MISSING
            continue

        value = measurement[field_name]
        if not isinstance(value, str):
            result.status[field_name] = FieldStatus.INVALID
            result.invalid_reasons[field_name] = f"expected string, got: {value!r}"
            continue

        result.status[field_name] = FieldStatus.AVAILABLE

    # 3. Fields where None is a legitimate value by design (e.g. "no fault").
    #    Only flag MISSING when the key itself is absent from the payload.
    for field_name in NULLABLE_FIELDS:
        if field_name not in measurement:
            result.status[field_name] = FieldStatus.MISSING
            continue
        result.status[field_name] = FieldStatus.AVAILABLE

    return result
