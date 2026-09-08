"""
Central configuration for the Solar Intelligence Core.

Keep every magic number / path / threshold here so the rest of the
codebase never hardcodes values. This makes the module easy to tune
without hunting through files.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models" / "artifacts"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
MODEL_VERSION = "solar_power_v1"
MODEL_ARTIFACT_PATH = MODEL_DIR / f"{MODEL_VERSION}.pkl"

# Prediction target column
TARGET_COLUMN = "ac_power"

# Features used for prediction (adjust once you've explored the real dataset)
FEATURE_COLUMNS = [
    "irradiance",
    "panel_temperature",
    "hour",
    "day_of_year",
]

# ---------------------------------------------------------------------------
# Anomaly thresholds
# ---------------------------------------------------------------------------
# Deviation % thresholds that map a deviation to a severity bucket.
# Tune these once you've looked at real distribution of deviations.
SEVERITY_THRESHOLDS = {
    "low": 10.0,       # |deviation%| >= 10  -> low
    "medium": 25.0,    # |deviation%| >= 25  -> medium
    "high": 40.0,      # |deviation%| >= 40  -> high
    "critical": 60.0,  # |deviation%| >= 60  -> critical
}

# Below this power level (kW), percentage deviation is not meaningful —
# tiny absolute noise near zero (nighttime, dawn/dusk) produces enormous,
# spurious percentages. Only suppresses the check when BOTH predicted and
# actual are below the floor; a genuine fault (predicted high, actual near
# zero) is still caught normally. Tune relative to your plant's typical
# minimum daytime output.
MIN_MEANINGFUL_POWER_KW = 0.3

# Minimum data-quality score required to trust a prediction/anomaly result.
MIN_QUALITY_SCORE = 0.5
# ---------------------------------------------------------------------------
# Operational constraints
# ---------------------------------------------------------------------------
# Prototype/default limits used by the optimization layer.
#
# These values are configuration assumptions for the current software
# prototype. They must be replaced with plant-specific operating limits
# before deployment on a real renewable-energy system.

BATTERY_CONSTRAINTS = {
    "min_soc_percent": 5.0,
    "max_soc_percent": 100.0,
    "max_charge_power_kw": 4.0,
    "max_discharge_power_kw": 4.0,
}

GRID_CONSTRAINTS = {
    "max_import_power_kw": None,
    "max_export_power_kw": None,
}

GENERATION_CONSTRAINTS = {
    "max_generation_power_kw": 10.0,
}

# ---------------------------------------------------------------------------
# Required raw input fields (per the measurement contract)
# ---------------------------------------------------------------------------
REQUIRED_FIELDS = [
    "plant_id",
    "timestamp",
]

OPTIONAL_FIELDS = [
    "irradiance",
    "panel_temperature",
    "dc_voltage",
    "dc_current",
    "ac_power",
    "battery_soc",
    "battery_voltage",
    "battery_current",
    "battery_temperature",
    "load_power",
    "grid_status",
    "grid_voltage",
    "grid_frequency",
    "import_power",
    "export_power",
    "inverter_status",
    "inverter_fault_code",
    "sensor_status",
]
