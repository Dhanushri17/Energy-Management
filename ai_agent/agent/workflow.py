from typing import Any


# ---------------------------------------------------------------------------
# Investigation planning
# ---------------------------------------------------------------------------

# Maps each possible cause to the tool(s) that can provide useful evidence
# about that cause.
CAUSE_TOOLS: dict[str, list[str]] = {
    "inverter_abnormality": [
        "inverter",
    ],
    "panel_or_system_fault": [
        "history",
        "sensor_health",
    ],
    "shading": [
        "weather",
    ],
    "environmental_conditions": [
        "weather",
    ],
    "battery_or_system_constraint": [
        "battery",
        "history",
    ],
    "grid_or_curtailment_issue": [
        "grid",
    ],
    "sensor_or_data_quality_issue": [
        "sensor_health",
    ],
}


# When two causes are equally plausible, this determines which investigation
# is preferred first.
TOOL_PRIORITY: dict[str, int] = {
    "inverter": 100,
    "weather": 90,
    "battery": 80,
    "grid": 80,
    "sensor_health": 70,
    "history": 60,
}


# Maximum number of new tools the planner selects in one investigation round.
MAX_TOOLS_PER_ROUND = 2


def _is_unknown_hypothesis(hypothesis: dict[str, Any]) -> bool:
    """
    Returns True when the hypothesis has not received meaningful evidence yet.
    """

    status = hypothesis.get("status", "uninvestigated")

    return status in {
        "uninvestigated",
        "neutral",
        "unknown",
    }


def _hypothesis_needs_more_investigation(
    hypothesis: dict[str, Any],
) -> bool:
    """
    Determines whether a hypothesis still needs investigation.

    A hypothesis that has already been strongly contradicted does not need
    another investigation unless no stronger explanation exists.
    """

    status = hypothesis.get("status", "uninvestigated")
    score = float(hypothesis.get("score", 0.0))

    if status in {"supports", "uninvestigated", "neutral", "unknown"}:
        return True

    if status == "contradicts":
        # Strongly negative hypotheses are not worth spending investigation
        # resources on.
        return score > -0.4

    return True


def _hypothesis_priority(
    hypothesis: dict[str, Any],
) -> float:
    """
    Calculates how valuable it is to investigate a hypothesis next.

    The score is intentionally simple and interpretable.

    Higher priority means:
      - the hypothesis is plausible,
      - evidence is missing/weak,
      - and it may explain the anomaly.
    """

    score = float(hypothesis.get("score", 0.0))
    status = hypothesis.get("status", "uninvestigated")
    evidence = hypothesis.get("evidence", [])

    # Plausibility:
    # Positive scores increase priority.
    # Negative scores decrease priority.
    plausibility = max(0.0, score)

    # Unknown hypotheses deserve investigation because we do not know
    # enough about them yet.
    uncertainty_bonus = 0.5 if _is_unknown_hypothesis(hypothesis) else 0.0

    # A supported hypothesis can still need confirmation.
    support_bonus = 0.25 if status == "supports" else 0.0

    # If evidence already exists, reduce the need for additional investigation.
    evidence_penalty = min(len(evidence) * 0.15, 0.45)

    priority = (
        plausibility
        + uncertainty_bonus
        + support_bonus
        - evidence_penalty
    )

    return round(priority, 4)


def _select_tools_for_hypotheses(
    hypotheses: list[dict[str, Any]],
    executed_tools: set[str],
) -> list[str]:
    """
    Selects the most useful unexecuted tools based on the current hypothesis
    state.

    This is the core adaptive planning logic.
    """

    candidate_tools: dict[str, float] = {}

    for hypothesis in hypotheses:
        if not _hypothesis_needs_more_investigation(hypothesis):
            continue

        cause = hypothesis.get("cause")

        if not cause:
            continue

        hypothesis_priority = _hypothesis_priority(hypothesis)

        for tool in CAUSE_TOOLS.get(cause, []):
            if tool in executed_tools:
                continue

            tool_priority = TOOL_PRIORITY.get(tool, 0)

            combined_priority = (
                hypothesis_priority * 100
                + tool_priority
            )

            # If multiple hypotheses need the same tool, keep the strongest
            # reason for selecting that tool.
            candidate_tools[tool] = max(
                candidate_tools.get(tool, float("-inf")),
                combined_priority,
            )

    ranked_tools = sorted(
        candidate_tools,
        key=lambda tool: candidate_tools[tool],
        reverse=True,
    )

    return ranked_tools[:MAX_TOOLS_PER_ROUND]


def select_tools(
    hypotheses: list[dict[str, Any]],
    executed_tools: list[str] | None = None,
) -> list[str]:
    """
    Select the next investigation tools.

    The planner does NOT blindly execute every available tool.

    Instead it considers:
      1. Current hypothesis scores
      2. Whether hypotheses have evidence
      3. Whether hypotheses are supported/neutral/contradicted
      4. Which tools can investigate those hypotheses
      5. Which tools have already been executed

    Returns a small set of tools for the next investigation round.
    """

    executed = set(executed_tools or [])

    return _select_tools_for_hypotheses(
        hypotheses=hypotheses,
        executed_tools=executed,
    )


def choose_additional_tools(
    hypotheses: list[dict[str, Any]],
    executed_tools: list[str] | None = None,
) -> list[str]:
    """
    Select additional tools when another investigation round is necessary.

    This intentionally uses the same adaptive planner rather than returning
    a fixed list.
    """

    return select_tools(
        hypotheses=hypotheses,
        executed_tools=executed_tools,
    )


def investigation_complete(
    evidence_sufficient: bool,
    pending_tools: list[str],
    investigation_round: int,
    max_rounds: int,
) -> bool:
    """
    Determines whether the investigation should stop.

    Investigation stops when:
      - evidence is sufficient, OR
      - there are no useful tools left, OR
      - the maximum investigation depth has been reached.
    """

    if evidence_sufficient:
        return True

    if not pending_tools:
        return True

    if investigation_round >= max_rounds:
        return True

    return False