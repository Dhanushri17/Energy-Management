"""
Expected-vs-actual deviation math and severity classification.
Spec sections 7 and 9.
"""

from ..config import (
    SEVERITY_THRESHOLDS,
    MIN_MEANINGFUL_POWER_KW,
)


def compute_deviation(predicted: float | None, actual: float | None) -> dict:
    """
    Returns deviation_kw and deviation_percent, handling edge cases:
    predicted=0, actual missing, prediction missing, and — critically —
    both predicted AND actual near zero (e.g. nighttime), where a
    percentage is not meaningful even though it's mathematically
    computable (tiny absolute noise -> enormous %).

    A genuine fault (predicted meaningfully high, actual near zero, or
    vice versa) still produces a normal percentage — the floor only
    suppresses the case where NEITHER value carries real signal.
    """
    if predicted is None or actual is None:
        return {
            "deviation_kw": None,
            "deviation_percent": None,
            "reason": "predicted or actual value unavailable",
        }

    deviation_kw = round(actual - predicted, 3)

    if abs(predicted) < MIN_MEANINGFUL_POWER_KW and abs(actual) < MIN_MEANINGFUL_POWER_KW:
        return {
            "deviation_kw": deviation_kw,
            "deviation_percent": None,
            "reason": (
                f"both predicted and actual are below the meaningful power "
                f"floor ({MIN_MEANINGFUL_POWER_KW} kW) — percentage deviation "
                f"is not meaningful near zero output"
            ),
        }

    if predicted == 0:
        return {
            "deviation_kw": deviation_kw,
            "deviation_percent": None,
            "reason": "predicted value is zero — percentage undefined",
        }

    deviation_percent = round((actual - predicted) / predicted * 100, 2)
    return {
        "deviation_kw": deviation_kw,
        "deviation_percent": deviation_percent,
        "reason": None,
    }


def classify_severity(deviation_percent: float | None) -> str:
    """
    Maps |deviation%| to a severity bucket using SEVERITY_THRESHOLDS.
    Returns "none" if deviation is unavailable or below the lowest threshold.
    """
    if deviation_percent is None:
        return "none"

    magnitude = abs(deviation_percent)

    if magnitude >= SEVERITY_THRESHOLDS["critical"]:
        return "critical"
    if magnitude >= SEVERITY_THRESHOLDS["high"]:
        return "high"
    if magnitude >= SEVERITY_THRESHOLDS["medium"]:
        return "medium"
    if magnitude >= SEVERITY_THRESHOLDS["low"]:
        return "low"
    return "none"


def anomaly_score(deviation_percent: float | None) -> float:
    """
    Simple monotonic score in [0, 1] from deviation magnitude.
    Replace with a proper statistical/ML-based score once you have
    enough historical data (spec section 8 — you choose the algorithm).
    """
    if deviation_percent is None:
        return 0.0
    magnitude = abs(deviation_percent)
    # Saturate at 100% deviation -> score 1.0
    return round(min(magnitude / 100.0, 1.0), 3)
