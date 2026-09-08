from typing import Any


def get_grid_status(
    grid_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Retrieve and normalize grid information
    for investigation.

    This tool provides grid and curtailment evidence.
    It does not diagnose the anomaly.
    """

    return {
        "component": "grid",
        "status": grid_data.get(
            "status",
            "unknown"
        ),
        "voltage": grid_data.get(
            "voltage"
        ),
        "frequency": grid_data.get(
            "frequency"
        ),
        "curtailment": grid_data.get(
            "curtailment",
            "unknown"
        ),
        "available": True
    }