from typing import Any


def get_sensor_health(
    sensor_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Retrieve and normalize sensor health information.

    This tool provides data-quality evidence.
    It does not diagnose the anomaly.
    """

    return {
        "component": "sensor",
        "status": sensor_data.get(
            "status",
            "unknown"
        ),
        "missing_values": sensor_data.get(
            "missing_values",
            0
        ),
        "stale_data": sensor_data.get(
            "stale_data",
            False
        ),
        "out_of_range": sensor_data.get(
            "out_of_range",
            False
        ),
        "available": True
    }