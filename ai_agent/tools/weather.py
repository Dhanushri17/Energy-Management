from typing import Any


def get_weather_data(
    weather_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Retrieve and normalize weather information
    for investigation.

    This tool provides environmental evidence.
    It does not diagnose the anomaly.
    """

    return {
        "component": "weather",
        "status": weather_data.get(
            "status",
            "unknown"
        ),
        "irradiance": weather_data.get(
            "irradiance"
        ),
        "temperature": weather_data.get(
            "temperature"
        ),
        "cloud_cover": weather_data.get(
            "cloud_cover"
        ),
        "shading": weather_data.get(
            "shading",
            "unknown"
        ),
        "available": True
    }