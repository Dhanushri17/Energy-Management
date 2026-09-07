"""
Energy balance calculations.

IMPORTANT:
An imbalance is EVIDENCE, not a diagnosis.
Never label it as a fault. Interpretation belongs to the AI Agent.

This module currently calculates an instantaneous POWER balance in kW.
It does not calculate accumulated energy in kWh.
"""


def _to_float(value):
    """Safely convert a measurement value to float."""
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _battery_power_kw(measurement: dict):
    """
    Calculate instantaneous battery power in kW.

    Convention:
        positive  -> battery charging
        negative  -> battery discharging

    Formula:
        P = V * I / 1000

    Assumption:
        battery_current is signed positive when charging.

    If the physical sensor uses the opposite convention, the sign
    must be inverted before relying on this calculation.
    """

    voltage = _to_float(
        measurement.get("battery_voltage")
    )

    current = _to_float(
        measurement.get("battery_current")
    )

    if voltage is None or current is None:
        return None

    return round(
        (voltage * current) / 1000.0,
        3,
    )


def compute_energy_balance(measurement: dict) -> dict:
    """
    Calculate the instantaneous power balance.

    Balance identity:

        generated + imported
        =
        consumed + exported + battery_charging + imbalance

    Battery convention:

        stored > 0  -> charging
        stored < 0  -> discharging

    Therefore, when the battery is discharging, its negative value
    correctly moves energy to the supply side of the equation.

    Example:

        generated = 7.0
        imported  = 0.0
        consumed  = 2.0
        exported  = 5.0
        stored    = 0.0

        7 + 0 = 2 + 5 + 0

        imbalance = 0

    Missing optional measurements are NOT silently treated as
    physically measured zero. If they are unavailable, the result
    records the assumption used for the residual calculation.
    """

    generated = _to_float(
        measurement.get("ac_power")
    )

    consumed = _to_float(
        measurement.get("load_power")
    )

    imported = _to_float(
        measurement.get("import_power")
    )

    exported = _to_float(
        measurement.get("export_power")
    )

    stored = _battery_power_kw(
        measurement
    )

    # ---------------------------------------------------------
    # Base result
    # ---------------------------------------------------------
    result = {
        "generated": generated,
        "consumed": consumed,
        "imported": imported,
        "exported": exported,
        "stored": stored,
        "imbalance": None,
        "balance_status": "insufficient_data",
        "skipped_fields": [],
        "assumptions": [],
    }

    # ---------------------------------------------------------
    # Track missing fields
    # ---------------------------------------------------------
    if generated is None:
        result["skipped_fields"].append(
            "ac_power"
        )

    if consumed is None:
        result["skipped_fields"].append(
            "load_power"
        )

    if imported is None:
        result["skipped_fields"].append(
            "import_power"
        )

    if exported is None:
        result["skipped_fields"].append(
            "export_power"
        )

    if stored is None:
        result["skipped_fields"].append(
            "battery_voltage/battery_current"
        )

    # ---------------------------------------------------------
    # We need generation and consumption as the minimum
    # foundation for calculating the residual.
    # ---------------------------------------------------------
    if generated is None or consumed is None:
        return result

    # ---------------------------------------------------------
    # Explicit handling of unavailable terms
    # ---------------------------------------------------------
    imported_value = imported

    if imported_value is None:
        imported_value = 0.0

        result["assumptions"].append(
            "import_power=0 because unavailable"
        )

    exported_value = exported

    if exported_value is None:
        exported_value = 0.0

        result["assumptions"].append(
            "export_power=0 because unavailable"
        )

    stored_value = stored

    if stored_value is None:
        stored_value = 0.0

        result["assumptions"].append(
            "battery_power=0 because unavailable"
        )

    # ---------------------------------------------------------
    # Power balance
    #
    # generated + imported
    # =
    # consumed + exported + stored + imbalance
    #
    # Rearranged:
    #
    # imbalance =
    # (generated + imported)
    # -
    # (consumed + exported + stored)
    # ---------------------------------------------------------
    supply = (
        generated
        + imported_value
    )

    demand = (
        consumed
        + exported_value
        + stored_value
    )

    imbalance = supply - demand

    result["imbalance"] = round(
        imbalance,
        3,
    )

    # ---------------------------------------------------------
    # Determine whether the calculated residual is effectively
    # balanced.
    #
    # 0.01 kW is used as a small numerical tolerance to avoid
    # treating floating-point rounding as a meaningful imbalance.
    # ---------------------------------------------------------
    BALANCE_TOLERANCE_KW = 0.01

    if abs(imbalance) <= BALANCE_TOLERANCE_KW:
        result["balance_status"] = "balanced"
    else:
        result["balance_status"] = "imbalanced"

    # ---------------------------------------------------------
    # Additional useful quantities
    # ---------------------------------------------------------
    result["supply_power"] = round(
        supply,
        3,
    )

    result["demand_power"] = round(
        demand,
        3,
    )

    return result