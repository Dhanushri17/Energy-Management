from typing import Any


def get_battery_status(
    battery_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Retrieve and normalize battery information
    for investigation.

    This tool provides battery/system evidence.
    It does not diagnose the anomaly.
    """

    return {
        "component": "battery",
        "soc": battery_data.get(
            "soc"
        ),
        "charge_status": battery_data.get(
            "charge_status",
            "unknown"
        ),
        "constraint": battery_data.get(
            "constraint",
            "unknown"
        ),
        "battery_temperature": battery_data.get(
            "battery_temperature"
        ),
        "available": True
    }