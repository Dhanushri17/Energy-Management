"""
Builds the final Evidence Package.

This is the contract consumed by the Backend and AI Agent.

Public output field names should remain stable.
"""

from __future__ import annotations

from .energy_balance import compute_energy_balance
from .historical import (
    compute_baseline,
    compare_to_baseline,
)
from .cause_indicators import (
    build_cause_indicators,
)
from .optimization_inputs import (
    build_optimization_inputs,
)


def build_evidence_package(
    plant_id,
    timestamp: str,
    measurement: dict,
    prediction: dict,
    anomaly: dict,
    validation_result,
    history_df=None,
    historical_result=None,
    future_forecast=None,
) -> dict:
    """
    Assemble the complete Intelligence Core output.

    Parameters
    ----------
    plant_id:
        Renewable plant identifier.

    timestamp:
        Timestamp of the current measurement.

    measurement:
        Validated raw measurement.

    prediction:
        Current ML prediction plus actual power
        and deviation information.

    anomaly:
        Result from anomaly detection.

    validation_result:
        Measurement validation result.

    history_df:
        Optional historical dataframe.

    historical_result:
        Optional result from comparable-condition
        historical intelligence.

    future_forecast:
        Optional offline future forecast.

    Returns
    -------
    dict
        Stable Intelligence Core evidence package.
    """

    # ========================================================
    # HISTORICAL EVIDENCE
    # ========================================================

    if historical_result is not None:

        historical_evidence = historical_result

    elif history_df is not None:

        baseline = compute_baseline(
            history_df
        )

        historical_comparison = compare_to_baseline(
            measurement.get("ac_power"),
            baseline,
        )

        historical_evidence = {
            "comparison": historical_comparison,
            "baseline_output": baseline.get(
                "mean"
            ),
            "actual_output": measurement.get(
                "ac_power"
            ),
            "deviation_kw": None,
            "deviation_percent": None,
            "match_count": 0,
            "matches": [],
        }

    else:

        historical_evidence = {
            "comparison": "insufficient_data",
            "baseline_output": None,
            "actual_output": measurement.get(
                "ac_power"
            ),
            "deviation_kw": None,
            "deviation_percent": None,
            "match_count": 0,
            "matches": [],
        }

    # ========================================================
    # ENERGY BALANCE
    # ========================================================

    energy_balance = compute_energy_balance(
        measurement
    )

    # ========================================================
    # CAUSE INDICATORS
    # ========================================================

    cause_indicators = build_cause_indicators(
        measurement=measurement,
        prediction=prediction,
        anomaly=anomaly,
    )

    # ========================================================
    # OPTIMIZATION INPUTS
    # ========================================================

    optimization_inputs = build_optimization_inputs(
        measurement=measurement,
        prediction=prediction,
        energy_balance=energy_balance,
        future_forecast=future_forecast,
    )

    # ========================================================
    # FINAL PACKAGE
    # ========================================================

    package = {

        "plant_id": plant_id,

        "timestamp": timestamp,

        # ----------------------------------------------------
        # Current ML prediction
        # ----------------------------------------------------

        "prediction": prediction,

        # ----------------------------------------------------
        # Current anomaly assessment
        # ----------------------------------------------------

        "anomaly": {
            "detected": anomaly["detected"],
            "type": anomaly["type"],
            "severity": anomaly["severity"],
            "score": anomaly["score"],
            "supporting_signals": (
                anomaly["supporting_signals"]
            ),
        },

        # ----------------------------------------------------
        # Evidence
        # ----------------------------------------------------

        "evidence": {

            "environment": {
                "irradiance": measurement.get(
                    "irradiance"
                ),
                "panel_temperature": measurement.get(
                    "panel_temperature"
                ),
                "status": (
                    "normal"
                    if measurement.get(
                        "irradiance"
                    ) is not None
                    else "unavailable"
                ),
            },

            "historical": {
                "comparison": historical_evidence.get(
                    "comparison"
                ),
                "baseline_output": (
                    historical_evidence.get(
                        "baseline_output"
                    )
                ),
                "actual_output": (
                    historical_evidence.get(
                        "actual_output"
                    )
                ),
                "deviation_kw": (
                    historical_evidence.get(
                        "deviation_kw"
                    )
                ),
                "deviation_percent": (
                    historical_evidence.get(
                        "deviation_percent"
                    )
                ),
                "match_count": (
                    historical_evidence.get(
                        "match_count",
                        0,
                    )
                ),
                "matches": (
                    historical_evidence.get(
                        "matches",
                        [],
                    )
                ),
            },

            "inverter": {
                "status": measurement.get(
                    "inverter_status"
                ),
                "fault_code": measurement.get(
                    "inverter_fault_code"
                ),
            },

            "battery": {
                "soc": measurement.get(
                    "battery_soc"
                ),
                "status": (
                    "normal"
                    if measurement.get(
                        "battery_soc"
                    ) is not None
                    else "unavailable"
                ),
            },

            "load": {
                "power": measurement.get(
                    "load_power"
                ),
                "status": (
                    "normal"
                    if measurement.get(
                        "load_power"
                    ) is not None
                    else "unavailable"
                ),
            },

            "grid": {
                "status": measurement.get(
                    "grid_status"
                ),
            },

            "energy_balance": energy_balance,

            "cause_indicators": cause_indicators,

            "optimization_inputs": optimization_inputs,

            # Reserved for deterministic calculations
            # added later.
            "relevant_calculations": {},
        },

        # ----------------------------------------------------
        # Data quality
        # ----------------------------------------------------

        "data_quality": {
            "missing_fields": (
                validation_result.missing_fields
            ),
            "invalid_fields": (
                validation_result.invalid_fields
            ),
            "quality_score": (
                validation_result.quality_score()
            ),
        },
    }

    return package


def insufficient_data_package(
    plant_id,
    timestamp: str,
    reason: str,
) -> dict:
    """
    Standard response when critical input data
    is insufficient for intelligence processing.
    """

    return {
        "plant_id": plant_id,

        "timestamp": timestamp,

        "status": "insufficient_data",

        "reason": reason,

        "prediction": None,

        "anomaly": None,

        "evidence": {},

        "data_quality": {
            "complete": False,
        },
    }