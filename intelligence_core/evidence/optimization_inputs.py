"""
Optimization-ready state derived from Intelligence Core evidence.

IMPORTANT
---------
This module does not make operational decisions.

It only exposes deterministic quantitative state that a downstream
optimizer or AI Agent can use for reasoning.

Operational limits come from central configuration. They are never
invented inside this module.
"""

from __future__ import annotations

from typing import Any

from intelligence_core.config import (
    BATTERY_CONSTRAINTS,
    GRID_CONSTRAINTS,
    GENERATION_CONSTRAINTS,
)

from intelligence_core.evidence.constraints import (
    validate_operational_constraints,
)


def _to_float(value: Any) -> float | None:
    """Safely convert a value to float."""

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def build_optimization_inputs(
    measurement: dict,
    prediction: dict,
    energy_balance: dict,
    future_forecast: dict | None = None,
) -> dict:
    """
    Build optimization-ready operational state.

    Parameters
    ----------
    measurement:
        Current validated measurement.

    prediction:
        Current ML prediction result.

    energy_balance:
        Output from compute_energy_balance().

    future_forecast:
        Output from FutureForecaster.forecast().

    Returns
    -------
    dict
        Deterministic optimization input state.
    """

    # ========================================================
    # CURRENT GENERATION STATE
    # ========================================================

    actual_generation = _to_float(
        prediction.get("actual_power")
    )

    expected_generation = _to_float(
        prediction.get("predicted_power")
    )

    deviation_kw = _to_float(
        prediction.get("deviation_kw")
    )

    deviation_percent = _to_float(
        prediction.get("deviation_percent")
    )

    # ========================================================
    # CURRENT OPERATIONAL STATE
    # ========================================================

    load_power = _to_float(
        energy_balance.get("consumed")
    )

    battery_soc = _to_float(
        measurement.get("battery_soc")
    )

    battery_power = _to_float(
        energy_balance.get("stored")
    )

    grid_import = _to_float(
        energy_balance.get("imported")
    )

    grid_export = _to_float(
        energy_balance.get("exported")
    )

    balance_status = energy_balance.get(
        "balance_status"
    )

    imbalance = _to_float(
        energy_balance.get("imbalance")
    )

    # ========================================================
    # FUTURE GENERATION STATE
    # ========================================================

    if future_forecast is None:

        forecast_status = "unavailable"

        forecast_points = []

    else:

        forecast_status = future_forecast.get(
            "status",
            "unavailable",
        )

        forecast_points = (
            future_forecast.get(
                "forecast",
                [],
            )
            or []
        )

    future_generation = []

    for point in forecast_points:

        predicted_power = _to_float(
            point.get("predicted_power")
        )

        if predicted_power is None:
            continue

        future_generation.append(
            {
                "timestamp": point.get(
                    "timestamp"
                ),
                "predicted_power": (
                    predicted_power
                ),
                "prediction_ok": bool(
                    point.get(
                        "prediction_ok",
                        False,
                    )
                ),
                "model_version": point.get(
                    "model_version"
                ),
            }
        )

    # ========================================================
    # OPERATIONAL CONSTRAINT VALIDATION
    # ========================================================

    constraint_validation = validate_operational_constraints(
        battery_soc=battery_soc,
        battery_power=battery_power,
        grid_import=grid_import,
        grid_export=grid_export,
        actual_generation=actual_generation,
    )

    # ========================================================
    # CONFIGURED CONSTRAINT LIMITS
    # ========================================================

    battery_constraints = {
        "min_soc_percent": _to_float(
            BATTERY_CONSTRAINTS.get(
                "min_soc_percent"
            )
        ),
        "max_soc_percent": _to_float(
            BATTERY_CONSTRAINTS.get(
                "max_soc_percent"
            )
        ),
        "max_charge_power_kw": _to_float(
            BATTERY_CONSTRAINTS.get(
                "max_charge_power_kw"
            )
        ),
        "max_discharge_power_kw": _to_float(
            BATTERY_CONSTRAINTS.get(
                "max_discharge_power_kw"
            )
        ),
    }

    battery_constraints_available = all(
        value is not None
        for value in battery_constraints.values()
    )

    grid_constraints = {
        "max_import_power_kw": _to_float(
            GRID_CONSTRAINTS.get(
                "max_import_power_kw"
            )
        ),
        "max_export_power_kw": _to_float(
            GRID_CONSTRAINTS.get(
                "max_export_power_kw"
            )
        ),
    }

    grid_constraints_available = all(
        value is not None
        for value in grid_constraints.values()
    )

    generation_constraints = {
        "max_generation_power_kw": _to_float(
            GENERATION_CONSTRAINTS.get(
                "max_generation_power_kw"
            )
        ),
    }

    generation_constraints_available = all(
        value is not None
        for value in generation_constraints.values()
    )

    # ========================================================
    # FINAL OPTIMIZATION INPUTS
    # ========================================================

    return {

        "current_state": {

            "actual_generation": actual_generation,

            "expected_generation": (
                expected_generation
            ),

            "deviation_kw": deviation_kw,

            "deviation_percent": (
                deviation_percent
            ),

            "load_power": load_power,

            "battery_soc": battery_soc,

            "battery_power": battery_power,

            "grid_import": grid_import,

            "grid_export": grid_export,

            "balance_status": balance_status,

            "imbalance": imbalance,
        },

        "future_state": {

            "forecast_available": (
                forecast_status == "available"
            ),

            "forecast_status": forecast_status,

            "forecast_points": (
                future_generation
            ),

            "forecast_count": len(
                future_generation
            ),
        },

        "constraints": {

            "status": constraint_validation[
                "status"
            ],

            "violations": constraint_validation[
                "violations"
            ],

            "battery_constraints_available": (
                battery_constraints_available
            ),

            "battery": battery_constraints,

            "battery_validation": (
                constraint_validation[
                    "battery"
                ]
            ),

            "grid_constraints_available": (
                grid_constraints_available
            ),

            "grid": grid_constraints,

            "grid_validation": (
                constraint_validation[
                    "grid"
                ]
            ),

            "generation_constraints_available": (
                generation_constraints_available
            ),

            "generation": generation_constraints,

            "generation_validation": (
                constraint_validation[
                    "generation"
                ]
            ),
        },
    }