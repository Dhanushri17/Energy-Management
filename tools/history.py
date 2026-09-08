from typing import Any


def get_historical_generation(
    history_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Retrieve historical generation information
    for investigation.

    This tool provides historical comparison evidence.
    It does not diagnose the anomaly.
    """

    return {
        "component": "history",
        "status": history_data.get(
            "status",
            "unknown"
        ),
        "historical_average": history_data.get(
            "historical_average"
        ),
        "current_vs_historical": history_data.get(
            "current_vs_historical"
        ),
        "similar_anomalies": history_data.get(
            "similar_anomalies",
            0
        ),
        "available": True
    }