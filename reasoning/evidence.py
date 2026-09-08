from typing import Any


def _result(
    assessment: str,
    score: float,
    evidence: str | None = None,
) -> dict[str, Any]:
    """
    Build a standard evidence-evaluation result.

    `assessment` is the legacy/current Agent contract.
    `status` is the newer normalized reasoning label.
    """

    status_map = {
        "supports": "supports",
        "contradicts": "contradicts",
        "neutral": "neutral",
        "unknown": "unknown",
    }

    return {
        "assessment": assessment,
        "status": status_map.get(assessment, "unknown"),
        "score": score,
        "evidence": [evidence] if evidence else [],
    }


def _get_value(
    evidence: dict[str, Any],
    *keys: str,
) -> Any:
    for key in keys:
        if key in evidence:
            return evidence[key]

    return None


def evaluate_evidence(
    hypothesis: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """
    Evaluate one hypothesis against available evidence.

    The current Agent passes the hypothesis as a string.
    """

    cause = hypothesis

    if cause == "inverter_abnormality":
        inverter = _get_value(
            evidence,
            "inverter",
            "inverter_status",
        )

        if inverter == "abnormal":
            return _result(
                "supports",
                1.0,
                "Inverter status is abnormal.",
            )

        if inverter == "normal":
            return _result(
                "contradicts",
                -0.8,
                "Inverter status is normal.",
            )

        return _result("unknown", 0.0)

    if cause == "panel_or_system_fault":
        historical = _get_value(
            evidence,
            "historical_output",
            "historical_status",
        )

        sensor = _get_value(
            evidence,
            "sensor",
            "sensor_status",
        )

        if historical == "abnormal":
            return _result(
                "supports",
                0.8,
                "Historical generation performance is abnormal.",
            )

        if historical == "normal":
            return _result(
                "contradicts",
                -0.5,
                "Historical generation performance is normal.",
            )

        if sensor == "abnormal":
            return _result(
                "supports",
                0.5,
                "Sensor health indicates a possible system-data problem.",
            )

        return _result("unknown", 0.0)

    if cause == "shading":
        shading = _get_value(
            evidence,
            "shading",
        )

        if shading == "present":
            return _result(
                "supports",
                0.8,
                "Shading is indicated by the available evidence.",
            )

        if shading == "absent":
            return _result(
                "contradicts",
                -0.8,
                "No shading is indicated by the available evidence.",
            )

        return _result("unknown", 0.0)

    if cause == "environmental_conditions":
        weather = _get_value(
            evidence,
            "weather",
            "environment",
            "environmental_conditions",
        )

        if weather == "abnormal":
            return _result(
                "supports",
                0.8,
                "Environmental conditions are abnormal.",
            )

        if weather == "normal":
            return _result(
                "contradicts",
                -0.8,
                "Environmental conditions are normal.",
            )

        return _result("unknown", 0.0)

    if cause == "battery_or_system_constraint":
        constraint = _get_value(
            evidence,
            "battery_constraint",
            "constraint",
        )

        if constraint in {
            "active",
            "present",
            "abnormal",
        }:
            return _result(
                "supports",
                0.8,
                "A battery or energy-management constraint is active.",
            )

        if constraint in {
            "none",
            "inactive",
            "normal",
        }:
            return _result(
                "contradicts",
                -0.6,
                "No battery or energy-management constraint is indicated.",
            )

        return _result("unknown", 0.0)

    if cause == "grid_or_curtailment_issue":
        grid = _get_value(
            evidence,
            "grid",
            "grid_status",
        )

        curtailment = _get_value(
            evidence,
            "curtailment",
        )

        if grid in {
            "abnormal",
            "fault",
            "unavailable",
        }:
            return _result(
                "supports",
                0.8,
                "Grid conditions are abnormal.",
            )

        if curtailment in {
            "active",
            "present",
        }:
            return _result(
                "supports",
                0.8,
                "Curtailment is active.",
            )

        if (
            grid in {"normal", "available"}
            and curtailment in {"inactive", "none", "normal"}
        ):
            return _result(
                "contradicts",
                -0.6,
                "Grid conditions are normal and curtailment is inactive.",
            )

        return _result("unknown", 0.0)

    if cause == "sensor_or_data_quality_issue":
        sensor = _get_value(
            evidence,
            "sensor",
            "sensor_status",
        )

        missing_values = _get_value(
            evidence,
            "missing_values",
        )

        stale_data = _get_value(
            evidence,
            "stale_data",
        )

        out_of_range = _get_value(
            evidence,
            "out_of_range",
        )

        if sensor == "abnormal":
            return _result(
                "supports",
                0.9,
                "Sensor health is abnormal.",
            )

        if missing_values is not None and missing_values > 0:
            return _result(
                "supports",
                0.9,
                "Missing sensor values are present.",
            )

        if stale_data is True:
            return _result(
                "supports",
                0.9,
                "Stale sensor data is present.",
            )

        if out_of_range is True:
            return _result(
                "supports",
                0.9,
                "Out-of-range sensor values are present.",
            )

        if sensor == "normal":
            return _result(
                "contradicts",
                -0.9,
                "Sensor health is normal.",
            )

        return _result("unknown", 0.0)

    return _result("unknown", 0.0)


def update_hypothesis(
    hypothesis: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """
    Update a hypothesis dictionary using current evidence.
    """

    cause = hypothesis.get("cause")

    if not cause:
        hypothesis["status"] = "unknown"
        hypothesis["score"] = 0.0
        hypothesis["evidence"] = []
        return hypothesis

    evaluation = evaluate_evidence(
        hypothesis=cause,
        evidence=evidence,
    )

    hypothesis["status"] = evaluation["assessment"]
    hypothesis["score"] = float(
        evaluation["score"]
    )

    existing_evidence = hypothesis.get(
        "evidence",
        [],
    )

    if not isinstance(existing_evidence, list):
        existing_evidence = []

    for item in evaluation["evidence"]:
        if item not in existing_evidence:
            existing_evidence.append(item)

    hypothesis["evidence"] = existing_evidence

    return hypothesis


def evaluate_hypotheses(
    hypotheses: list[dict[str, Any]],
    evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Evaluate all hypotheses against the current evidence.
    """

    return [
        update_hypothesis(
            hypothesis=hypothesis,
            evidence=evidence,
        )
        for hypothesis in hypotheses
    ]