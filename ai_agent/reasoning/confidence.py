from typing import Any


def calculate_confidence(
    ranked_causes: list[dict[str, Any]]
) -> float:
    """
    Calculate calibrated confidence for the highest-ranked cause.

    Confidence considers:

    1. Strength of the top cause.
    2. Separation from competing causes.
    3. Whether competing causes have positive evidence.

    The result is intentionally conservative.
    A diagnosis should not automatically receive
    100% confidence from a single piece of evidence.
    """

    if not ranked_causes:
        return 0.0

    top_cause = ranked_causes[0]

    top_score = float(
        top_cause.get("score", 0.0)
    )

    # No positive evidence for the leading cause.
    if top_score <= 0:
        return 0.0

    # --------------------------------------------------
    # 1. Normalize top evidence strength
    # --------------------------------------------------

    top_strength = min(
        max(top_score, 0.0),
        1.0
    )

    # --------------------------------------------------
    # 2. Compare against the next strongest cause
    # --------------------------------------------------

    if len(ranked_causes) > 1:

        second_score = float(
            ranked_causes[1].get(
                "score",
                0.0
            )
        )

    else:

        second_score = 0.0

    separation = top_score - second_score

    # Convert separation into a 0-1 range.
    #
    # A separation of 2.0 means:
    # top cause = +1
    # competing cause = -1
    #
    # A separation of 0 means:
    # both causes have equal support.
    #
    separation_strength = min(
        max(separation / 2.0, 0.0),
        1.0
    )

    # --------------------------------------------------
    # 3. Check for competing positive hypotheses
    # --------------------------------------------------

    competing_positive_causes = 0

    for cause in ranked_causes[1:]:

        score = float(
            cause.get("score", 0.0)
        )

        if score > 0:
            competing_positive_causes += 1

    # Penalize confidence when multiple causes
    # have positive evidence.
    competition_penalty = min(
        competing_positive_causes * 0.10,
        0.30
    )

    # --------------------------------------------------
    # 4. Combine confidence components
    # --------------------------------------------------

    confidence = (
        0.60 * top_strength
        + 0.40 * separation_strength
        - competition_penalty
    )

    # --------------------------------------------------
    # 5. Keep confidence within safe bounds
    # --------------------------------------------------

    confidence = max(
        0.0,
        min(confidence, 0.95)
    )

    return round(
        confidence,
        2
    )