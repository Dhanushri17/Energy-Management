"""
Controlled anomaly-detection evaluation.

This module evaluates the anomaly detector against independently
defined ground-truth labels.

Ground truth is NOT used by the production detector.
"""

from intelligence_core.anomaly.detector import detect_anomaly


def evaluate_cases(cases: list[dict]) -> list[dict]:
    """
    Evaluate anomaly detection on controlled test cases.

    Each case must contain:
        name
        predicted_power
        actual_power
        measurement
        ground_truth_anomaly
    """

    results = []

    for case in cases:
        prediction = case["predicted_power"]
        actual = case["actual_power"]
        measurement = case.get("measurement", {})

        result = detect_anomaly(
            predicted=prediction,
            actual=actual,
            measurement=measurement,
        )

        results.append({
            "name": case["name"],
            "ground_truth": case["ground_truth_anomaly"],
            "predicted": result["detected"],
            "severity": result["severity"],
            "score": result["score"],
            "deviation_percent": result["deviation"]["deviation_percent"],
        })

    return results