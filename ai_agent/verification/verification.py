from typing import Any


def verify_action(
    diagnosis: dict[str, Any],
    recommendation: dict[str, Any],
    before_measurement: dict[str, Any],
    after_measurement: dict[str, Any]
) -> dict[str, Any]:
    """
    Verify whether the recommended action appears
    to have improved the detected anomaly.

    The verification compares system measurements
    before and after the recommended action.
    """

    before_power = before_measurement.get(
        "actual_power"
    )

    after_power = after_measurement.get(
        "actual_power"
    )

    expected_power = before_measurement.get(
        "expected_power"
    )

    root_cause = diagnosis.get(
        "root_cause",
        "unknown"
    )

    action = recommendation.get(
        "action",
        "unknown"
    )

    # ==================================================
    # CHECK WHETHER REQUIRED DATA EXISTS
    # ==================================================

    if (
        before_power is None
        or after_power is None
    ):
        return {
            "status": "insufficient_data",
            "verified": False,
            "root_cause": root_cause,
            "action": action,
            "reason": (
                "Before-and-after power measurements "
                "are required for verification."
            )
        }

    # ==================================================
    # CALCULATE CHANGE
    # ==================================================

    power_change = after_power - before_power

    if before_power != 0:
        improvement_percent = (
            power_change / abs(before_power)
        ) * 100
    else:
        improvement_percent = 0.0

    # ==================================================
    # CHECK AGAINST EXPECTED POWER
    # ==================================================

    if expected_power is not None:
        before_deviation = (
            before_power - expected_power
        )

        after_deviation = (
            after_power - expected_power
        )

        deviation_improved = (
            abs(after_deviation)
            < abs(before_deviation)
        )

    else:
        before_deviation = None
        after_deviation = None
        deviation_improved = (
            after_power > before_power
        )

    # ==================================================
    # DETERMINE VERIFICATION RESULT
    # ==================================================

    if deviation_improved:

        status = "improved"
        verified = True

        reason = (
            "System performance improved after "
            "the recommended action."
        )

    else:

        status = "not_improved"
        verified = False

        reason = (
            "System performance did not improve "
            "after the recommended action. "
            "Further investigation is required."
        )

    # ==================================================
    # RETURN VERIFICATION RESULT
    # ==================================================

    return {
        "status": status,
        "verified": verified,
        "root_cause": root_cause,
        "action": action,
        "before_power": before_power,
        "after_power": after_power,
        "power_change": round(
            power_change,
            3
        ),
        "improvement_percent": round(
            improvement_percent,
            2
        ),
        "before_deviation": (
            round(before_deviation, 3)
            if before_deviation is not None
            else None
        ),
        "after_deviation": (
            round(after_deviation, 3)
            if after_deviation is not None
            else None
        ),
        "reason": reason
    }