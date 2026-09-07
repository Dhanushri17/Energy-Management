"""
Tests for deterministic operational constraint validation.
"""

from intelligence_core.evidence.constraints import (
    validate_battery_constraints,
    validate_grid_constraints,
    validate_generation_constraints,
    validate_operational_constraints,
)


def test_battery_within_limits():
    result = validate_battery_constraints(
        battery_soc=50.0,
        battery_power=2.0,
    )

    assert result["status"] == "within_limits"
    assert result["violations"] == []
    assert result["soc_status"] == "within_limits"
    assert result["power_status"] == "within_limits"


def test_battery_soc_below_minimum():
    result = validate_battery_constraints(
        battery_soc=3.0,
        battery_power=0.0,
    )

    assert result["status"] == "violated"
    assert "battery_soc_below_minimum" in result["violations"]
    assert result["soc_status"] == "below_minimum"


def test_battery_charge_limit_exceeded():
    result = validate_battery_constraints(
        battery_soc=50.0,
        battery_power=5.0,
    )

    assert result["status"] == "violated"
    assert (
        "battery_charge_power_limit_exceeded"
        in result["violations"]
    )
    assert result["power_status"] == "charge_limit_exceeded"


def test_battery_discharge_limit_exceeded():
    result = validate_battery_constraints(
        battery_soc=50.0,
        battery_power=-5.0,
    )

    assert result["status"] == "violated"
    assert (
        "battery_discharge_power_limit_exceeded"
        in result["violations"]
    )
    assert result["power_status"] == "discharge_limit_exceeded"


def test_generation_within_limit():
    result = validate_generation_constraints(
        actual_generation=6.5,
    )

    assert result["status"] == "within_limits"
    assert result["violations"] == []
    assert result["headroom"]["generation_headroom_kw"] == 3.5


def test_generation_capacity_exceeded():
    result = validate_generation_constraints(
        actual_generation=11.0,
    )

    assert result["status"] == "violated"
    assert "generation_capacity_exceeded" in result["violations"]
    assert result["headroom"]["generation_headroom_kw"] == -1.0


def test_grid_constraints_unavailable():
    result = validate_grid_constraints(
        grid_import=2.0,
        grid_export=1.0,
    )

    assert result["status"] == "unavailable"
    assert result["violations"] == []


def test_multiple_constraint_violations():
    result = validate_operational_constraints(
        battery_soc=3.0,
        battery_power=5.0,
        grid_import=0.0,
        grid_export=0.0,
        actual_generation=11.0,
    )

    assert result["status"] == "violated"

    assert "battery_soc_below_minimum" in result["violations"]

    assert (
        "battery_charge_power_limit_exceeded"
        in result["violations"]
    )

    assert (
        "generation_capacity_exceeded"
        in result["violations"]
    )


def test_normal_operational_state():
    result = validate_operational_constraints(
        battery_soc=34.46,
        battery_power=4.0,
        grid_import=0.0,
        grid_export=0.06,
        actual_generation=6.43,
    )

    assert result["status"] == "within_limits"
    assert result["violations"] == []

    assert result["battery"]["status"] == "within_limits"
    assert result["generation"]["status"] == "within_limits"
    assert result["grid"]["status"] == "unavailable"