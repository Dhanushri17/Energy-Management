from typing import Any


def record_feedback(
    diagnosis: dict[str, Any],
    recommendation: dict[str, Any],
    verification: dict[str, Any]
) -> dict[str, Any]:
    """
    Record structured feedback from the verification stage.

    This module does not retrain the ML model.
    It creates a learning record that can later be used
    to improve reasoning rules, cause scores, and decisions.
    """

    root_cause = diagnosis.get(
        "root_cause",
        "unknown"
    )

    diagnosis_confidence = diagnosis.get(
        "confidence",
        0.0
    )

    action = recommendation.get(
        "action",
        "unknown"
    )

    verification_status = verification.get(
        "status",
        "insufficient_data"
    )

    verified = verification.get(
        "verified",
        False
    )

    if verification_status == "improved" and verified:

        outcome = "supported"
        learning_signal = 1.0

        message = (
            "The verification result supports the "
            "diagnosis and recommended action."
        )

    elif verification_status == "not_improved":

        outcome = "not_supported"
        learning_signal = -1.0

        message = (
            "The verification result does not support "
            "the diagnosis or recommended action. "
            "Further investigation is required."
        )

    else:

        outcome = "insufficient_data"
        learning_signal = 0.0

        message = (
            "There is insufficient verification data "
            "to determine whether the diagnosis and "
            "recommended action were successful."
        )

    return {
        "status": "learning_recorded",
        "outcome": outcome,
        "diagnosis": root_cause,
        "diagnosis_confidence": diagnosis_confidence,
        "action": action,
        "verification_status": verification_status,
        "verified": verified,
        "learning_signal": learning_signal,
        "message": message
    }