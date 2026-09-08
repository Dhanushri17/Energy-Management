from typing import Any


def generate_hypotheses(anomaly: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Generate possible causes for a solar-energy anomaly.

    The function generates hypotheses only.
    It does not decide the root cause.
    """

    if not anomaly.get("detected", False):
        return []

    return [
        {
            "cause": "inverter_abnormality",
            "status": "uninvestigated",
            "score": 0.0,
            "evidence": []
        },
        {
            "cause": "panel_or_system_fault",
            "status": "uninvestigated",
            "score": 0.0,
            "evidence": []
        },
        {
            "cause": "shading",
            "status": "uninvestigated",
            "score": 0.0,
            "evidence": []
        },
        {
            "cause": "environmental_conditions",
            "status": "uninvestigated",
            "score": 0.0,
            "evidence": []
        },
        {
            "cause": "battery_or_system_constraint",
            "status": "uninvestigated",
            "score": 0.0,
            "evidence": []
        },
        {
            "cause": "grid_or_curtailment_issue",
            "status": "uninvestigated",
            "score": 0.0,
            "evidence": []
        },
        {
            "cause": "sensor_or_data_quality_issue",
            "status": "uninvestigated",
            "score": 0.0,
            "evidence": []
        }
    ]