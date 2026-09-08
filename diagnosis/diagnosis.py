from typing import Any


def generate_diagnosis(
    ranked_causes: list[dict[str, Any]],
    confidence: float
) -> dict[str, Any]:
    """
    Generate a structured diagnosis from the ranked causes.

    The diagnosis is based on:
    - highest-ranked cause
    - supporting evidence
    - calculated confidence

    This function does not generate hypotheses.
    It only interprets the results of the investigation.
    """

    # No causes available
    if not ranked_causes:
        return {
            "root_cause": "unknown",
            "confidence": 0.0,
            "reasoning": (
                "No possible causes were identified "
                "during the investigation."
            )
        }

    # Get the highest-ranked cause
    top_cause = ranked_causes[0]

    cause = top_cause.get(
        "cause",
        "unknown"
    )

    score = top_cause.get(
        "score",
        0.0
    )

    evidence = top_cause.get(
        "evidence",
        []
    )

    # If the highest-ranked cause has no
    # meaningful supporting evidence
    if score <= 0:
        return {
            "root_cause": "undetermined",
            "confidence": 0.0,
            "reasoning": (
                "The available evidence does not provide "
                "sufficient support for a specific root cause."
            )
        }

    # Build reasoning from the evidence
    if evidence:

        evidence_text = " ".join(
            str(item)
            for item in evidence
        )

        reasoning = (
            f"The most likely cause is {cause}. "
            f"This is supported by the following evidence: "
            f"{evidence_text}"
        )

    else:

        reasoning = (
            f"The most likely cause is {cause}, "
            f"based on the current evidence ranking."
        )

    return {
        "root_cause": cause,
        "confidence": confidence,
        "reasoning": reasoning
    }