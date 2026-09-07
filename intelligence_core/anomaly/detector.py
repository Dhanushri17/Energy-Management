"""
Orchestrates anomaly detection: expected-vs-actual + any additional
signals (sensor status, inverter status, historical comparison).

This stays strictly at the "what is abnormal" level — never assigns
a root cause (spec section 9 — critical boundary).
"""

from intelligence_core.anomaly.scoring import (
    compute_deviation,
    classify_severity,
    anomaly_score,
)


def detect_anomaly(predicted: float | None, actual: float | None, measurement: dict) -> dict:
    """
    Args:
        predicted: model's expected power output
        actual: observed power output
        measurement: raw validated measurement dict (for supporting signals
                      like inverter_status, sensor_status)

    Returns:
        dict matching spec section 9's anomaly object.
    """
    deviation = compute_deviation(predicted, actual)
    severity = classify_severity(deviation["deviation_percent"])
    score = anomaly_score(deviation["deviation_percent"])

    detected = severity != "none"

    supporting_signals = []
    if detected:
        supporting_signals.append("power_deviation")

    # Report observed abnormal signals as evidence only — do NOT interpret
    # them as the cause. That's the AI Agent's job.
    if measurement.get("inverter_status") not in (None, "normal"):
        supporting_signals.append("inverter_status_abnormal")
    if measurement.get("sensor_status") not in (None, "normal"):
        supporting_signals.append("sensor_status_abnormal")

    anomaly_type = None
    if detected:
        if deviation["deviation_percent"] is not None and deviation["deviation_percent"] < 0:
            anomaly_type = "under_generation"
        elif deviation["deviation_percent"] is not None and deviation["deviation_percent"] > 0:
            anomaly_type = "over_generation"

    return {
        "detected": detected,
        "type": anomaly_type,
        "severity": severity,
        "score": score,
        "supporting_signals": supporting_signals,
        "deviation": deviation,
    }
