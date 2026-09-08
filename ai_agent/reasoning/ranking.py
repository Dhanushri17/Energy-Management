from typing import Any


def rank_causes(
    hypotheses: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Rank possible causes based on their evidence scores.

    Higher scores indicate stronger support.
    Lower scores indicate stronger contradiction.
    """

    ranked = sorted(
        hypotheses,
        key=lambda hypothesis: hypothesis.get("score", 0.0),
        reverse=True
    )

    return ranked