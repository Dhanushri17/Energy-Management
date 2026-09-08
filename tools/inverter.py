from typing import Any


def get_inverter_status(inverter_data: dict[str, Any]) -> dict[str, Any]:
    """
    Retrieve and normalize inverter information for investigation.

    This tool provides evidence to the reasoning engine.
    It does not diagnose the problem.
    """

    return {
        "component": "inverter",
        "status": inverter_data.get("status", "unknown"),
        "fault_code": inverter_data.get("fault_code"),
        "temperature": inverter_data.get("temperature"),
        "ac_output": inverter_data.get("ac_output"),
        "available": True
    }