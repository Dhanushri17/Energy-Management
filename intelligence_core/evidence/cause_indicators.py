"""
Cause indicators for renewable-energy anomalies.

This module converts observed measurements and anomaly information
into objective evidence signals.

IMPORTANT:
This module does NOT assign root causes.
It only reports observable indicators.

The AI Agent is responsible for reasoning over these indicators.
"""


def build_cause_indicators(
    measurement: dict,
    prediction: dict,
    anomaly: dict,
) -> dict:
    """
    Build objective cause indicators from the current measurement.

    Returns:
        Dictionary containing observable indicators only.
    """

    deviation_percent = prediction.get("deviation_percent")
    actual_power = prediction.get("actual_power")
    predicted_power = prediction.get("predicted_power")

    # ---------------------------------------------------------
    # Power deviation
    # ---------------------------------------------------------

    power_deviation = {
        "status": "normal",
        "predicted_power": predicted_power,
        "actual_power": actual_power,
        "deviation_percent": deviation_percent,
    }

    if anomaly.get("detected"):
        power_deviation["status"] = "abnormal"

    # ---------------------------------------------------------
    # Environmental indicators
    # ---------------------------------------------------------

    irradiance = measurement.get("irradiance")
    panel_temperature = measurement.get("panel_temperature")

    environmental = {
        "irradiance": irradiance,
        "panel_temperature": panel_temperature,
        "irradiance_status": (
            "available"
            if irradiance is not None
            else "unavailable"
        ),
        "temperature_status": (
            "available"
            if panel_temperature is not None
            else "unavailable"
        ),
    }

    # ---------------------------------------------------------
    # Inverter indicators
    # ---------------------------------------------------------

    inverter_status = measurement.get("inverter_status")
    inverter_fault_code = measurement.get("inverter_fault_code")

    inverter = {
        "status": inverter_status,
        "fault_code": inverter_fault_code,
        "indicator": (
            "abnormal"
            if inverter_status not in (None, "normal")
            else "normal"
        ),
    }

    # ---------------------------------------------------------
    # Sensor indicators
    # ---------------------------------------------------------

    sensor_status = measurement.get("sensor_status")

    sensor = {
        "status": sensor_status,
        "indicator": (
            "abnormal"
            if sensor_status not in (None, "normal")
            else "normal"
        ),
    }

    # ---------------------------------------------------------
    # Grid indicators
    # ---------------------------------------------------------

    grid_status = measurement.get("grid_status")

    grid = {
        "status": grid_status,
        "indicator": (
            "abnormal"
            if grid_status not in (None, "available")
            else "normal"
        ),
        "grid_voltage": measurement.get("grid_voltage"),
        "grid_frequency": measurement.get("grid_frequency"),
    }

    return {
        "power_deviation": power_deviation,
        "environmental": environmental,
        "inverter": inverter,
        "sensor": sensor,
        "grid": grid,
    }