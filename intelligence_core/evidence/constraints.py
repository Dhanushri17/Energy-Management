"""
Deterministic operational constraint validation.

This module reports whether the current renewable-energy operating
state is within configured limits.

IMPORTANT
---------
This module does not make operational decisions or recommendations.
It only calculates constraint status, violations, and available
operating headroom for downstream optimization or AI-agent reasoning.
"""

from __future__ import annotations

from typing import Any

from intelligence_core.config import (
    BATTERY_CONSTRAINTS,
    GRID_CONSTRAINTS,
    GENERATION_CONSTRAINTS,
)


def _to_float(value: Any) -> float | None:
    """Safely convert a value to float."""

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_battery_constraints(
    battery_soc: Any,
    battery_power: Any,
) -> dict:
    """
    Validate current battery state against configured limits.

    Positive battery_power means charging.
    Negative battery_power means discharging.
    """

    soc = _to_float(battery_soc)
    power = _to_float(battery_power)

    min_soc = _to_float(
        BATTERY_CONSTRAINTS.get("min_soc_percent")
    )

    max_soc = _to_float(
        BATTERY_CONSTRAINTS.get("max_soc_percent")
    )

    max_charge = _to_float(
        BATTERY_CONSTRAINTS.get("max_charge_power_kw")
    )

    max_discharge = _to_float(
        BATTERY_CONSTRAINTS.get("max_discharge_power_kw")
    )

    violations = []
    headroom = {}

    # --------------------------------------------------------
    # SOC
    # --------------------------------------------------------

    if soc is None:
        soc_status = "unavailable"

    else:
        soc_status = "within_limits"

        if min_soc is not None and soc < min_soc:
            soc_status = "below_minimum"
            violations.append("battery_soc_below_minimum")

        if max_soc is not None and soc > max_soc:
            soc_status = "above_maximum"
            violations.append("battery_soc_above_maximum")

        if min_soc is not None:
            headroom["soc_above_minimum_percent"] = round(
                soc - min_soc,
                4,
            )

        if max_soc is not None:
            headroom["soc_below_maximum_percent"] = round(
                max_soc - soc,
                4,
            )

    # --------------------------------------------------------
    # Battery power
    # --------------------------------------------------------

    if power is None:
        power_status = "unavailable"

    elif power >= 0:

        if max_charge is None:
            power_status = "unavailable"

        elif power > max_charge:
            power_status = "charge_limit_exceeded"
            violations.append(
                "battery_charge_power_limit_exceeded"
            )

        else:
            power_status = "within_limits"

        if max_charge is not None:
            headroom["charge_power_headroom_kw"] = round(
                max_charge - power,
                4,
            )

    else:

        discharge_power = abs(power)

        if max_discharge is None:
            power_status = "unavailable"

        elif discharge_power > max_discharge:
            power_status = "discharge_limit_exceeded"
            violations.append(
                "battery_discharge_power_limit_exceeded"
            )

        else:
            power_status = "within_limits"

        if max_discharge is not None:
            headroom["discharge_power_headroom_kw"] = round(
                max_discharge - discharge_power,
                4,
            )

    # --------------------------------------------------------
    # Overall status
    # --------------------------------------------------------

    if soc_status == "unavailable" and power_status == "unavailable":
        status = "unavailable"

    elif violations:
        status = "violated"

    else:
        status = "within_limits"

    return {
        "status": status,
        "soc_status": soc_status,
        "power_status": power_status,
        "violations": violations,
        "headroom": headroom,
        "limits": {
            "min_soc_percent": min_soc,
            "max_soc_percent": max_soc,
            "max_charge_power_kw": max_charge,
            "max_discharge_power_kw": max_discharge,
        },
    }


def validate_grid_constraints(
    grid_import: Any,
    grid_export: Any,
) -> dict:
    """
    Validate grid import/export against configured limits.

    A None limit means that the corresponding operational limit
    is unavailable.
    """

    imported = _to_float(grid_import)
    exported = _to_float(grid_export)

    max_import = _to_float(
        GRID_CONSTRAINTS.get("max_import_power_kw")
    )

    max_export = _to_float(
        GRID_CONSTRAINTS.get("max_export_power_kw")
    )

    violations = []
    headroom = {}

    # --------------------------------------------------------
    # Grid import
    # --------------------------------------------------------

    if imported is not None and max_import is not None:

        if imported > max_import:
            violations.append(
                "grid_import_power_limit_exceeded"
            )

            headroom["import_power_headroom_kw"] = round(
                max_import - imported,
                4,
            )

        else:
            headroom["import_power_headroom_kw"] = round(
                max_import - imported,
                4,
            )

    # --------------------------------------------------------
    # Grid export
    # --------------------------------------------------------

    if exported is not None and max_export is not None:

        if exported > max_export:
            violations.append(
                "grid_export_power_limit_exceeded"
            )

            headroom["export_power_headroom_kw"] = round(
                max_export - exported,
                4,
            )

        else:
            headroom["export_power_headroom_kw"] = round(
                max_export - exported,
                4,
            )

    # --------------------------------------------------------
    # Overall status
    # --------------------------------------------------------

    limits_available = (
        max_import is not None
        or max_export is not None
    )

    if not limits_available:
        status = "unavailable"

    elif violations:
        status = "violated"

    else:
        status = "within_limits"

    return {
        "status": status,
        "violations": violations,
        "headroom": headroom,
        "limits": {
            "max_import_power_kw": max_import,
            "max_export_power_kw": max_export,
        },
    }


def validate_generation_constraints(
    actual_generation: Any,
) -> dict:
    """
    Validate current generation against configured capacity.
    """

    generation = _to_float(actual_generation)

    max_generation = _to_float(
        GENERATION_CONSTRAINTS.get(
            "max_generation_power_kw"
        )
    )

    violations = []
    headroom = {}

    if generation is None or max_generation is None:

        status = "unavailable"

    elif generation > max_generation:

        status = "violated"

        violations.append(
            "generation_capacity_exceeded"
        )

        headroom["generation_headroom_kw"] = round(
            max_generation - generation,
            4,
        )

    else:

        status = "within_limits"

        headroom["generation_headroom_kw"] = round(
            max_generation - generation,
            4,
        )

    return {
        "status": status,
        "violations": violations,
        "headroom": headroom,
        "limits": {
            "max_generation_power_kw": max_generation,
        },
    }


def validate_operational_constraints(
    battery_soc: Any,
    battery_power: Any,
    grid_import: Any,
    grid_export: Any,
    actual_generation: Any,
) -> dict:
    """
    Validate all configured operational constraints.
    """

    battery = validate_battery_constraints(
        battery_soc=battery_soc,
        battery_power=battery_power,
    )

    grid = validate_grid_constraints(
        grid_import=grid_import,
        grid_export=grid_export,
    )

    generation = validate_generation_constraints(
        actual_generation=actual_generation,
    )

    all_violations = (
        battery["violations"]
        + grid["violations"]
        + generation["violations"]
    )

    if all_violations:
        overall_status = "violated"

    elif all(
        result["status"] == "unavailable"
        for result in (
            battery,
            grid,
            generation,
        )
    ):
        overall_status = "unavailable"

    else:
        overall_status = "within_limits"

    return {
        "status": overall_status,
        "violations": all_violations,
        "battery": battery,
        "grid": grid,
        "generation": generation,
    }