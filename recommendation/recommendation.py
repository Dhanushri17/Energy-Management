from typing import Any


def generate_recommendation(
    diagnosis: dict[str, Any],
    confidence: float
) -> dict[str, Any]:
    """
    Generate an actionable recommendation based on
    the diagnosis and confidence produced by the Agent.

    The recommendation does not perform diagnosis.
    It translates the diagnosis into a suitable next action.
    """

    root_cause = diagnosis.get(
        "root_cause",
        "unknown"
    )

    # ==================================================
    # LOW CONFIDENCE / INSUFFICIENT EVIDENCE
    # ==================================================

    if (
        root_cause in ["unknown", "undetermined"]
        or confidence < 0.5
    ):
        return {
            "action": "collect_additional_evidence",
            "priority": "medium",
            "reason": (
                "The diagnosis does not have sufficient "
                "confidence for a corrective action."
            ),
            "recommended_steps": [
                "Collect additional system evidence.",
                "Monitor the anomaly over the next observation period.",
                "Re-evaluate the possible causes."
            ]
        }

    # ==================================================
    # INVERTER ABNORMALITY
    # ==================================================

    if root_cause == "inverter_abnormality":
        return {
            "action": "inspect_inverter",
            "priority": "high",
            "reason": (
                "The inverter is the most likely source "
                "of the observed generation anomaly."
            ),
            "recommended_steps": [
                "Inspect inverter status and fault codes.",
                "Check AC-side output.",
                "Check inverter temperature and operating condition.",
                "If the abnormal condition persists, schedule maintenance."
            ]
        }

    # ==================================================
    # PANEL OR SYSTEM FAULT
    # ==================================================

    if root_cause == "panel_or_system_fault":
        return {
            "action": "inspect_pv_system",
            "priority": "high",
            "reason": (
                "The evidence indicates a possible PV panel "
                "or system-level performance issue."
            ),
            "recommended_steps": [
                "Inspect PV panel condition.",
                "Check DC voltage and current.",
                "Inspect wiring and connections.",
                "Compare affected output with historical performance."
            ]
        }

    # ==================================================
    # SHADING
    # ==================================================

    if root_cause == "shading":
        return {
            "action": "inspect_for_shading",
            "priority": "medium",
            "reason": (
                "The evidence indicates that shading may be "
                "reducing solar generation."
            ),
            "recommended_steps": [
                "Inspect the PV array for temporary or permanent shading.",
                "Check nearby objects causing obstruction.",
                "Compare generation before and after the suspected shading period."
            ]
        }

    # ==================================================
    # ENVIRONMENTAL CONDITIONS
    # ==================================================

    if root_cause == "environmental_conditions":
        return {
            "action": "continue_monitoring",
            "priority": "low",
            "reason": (
                "Environmental conditions may explain the "
                "reduction in solar generation."
            ),
            "recommended_steps": [
                "Continue monitoring generation.",
                "Compare actual output with weather conditions.",
                "Re-evaluate system performance when environmental conditions normalize."
            ]
        }

    # ==================================================
    # BATTERY OR SYSTEM CONSTRAINT
    # ==================================================

    if root_cause == "battery_or_system_constraint":
        return {
            "action": "inspect_battery_and_energy_flow",
            "priority": "high",
            "reason": (
                "A battery or system constraint may be "
                "limiting usable solar energy."
            ),
            "recommended_steps": [
                "Check battery state of charge.",
                "Check battery charge and discharge status.",
                "Inspect charge controller or power-management constraints.",
                "Verify whether generation is being curtailed."
            ]
        }

    # ==================================================
    # GRID OR CURTAILMENT ISSUE
    # ==================================================

    if root_cause == "grid_or_curtailment_issue":
        return {
            "action": "inspect_grid_and_curtailment_status",
            "priority": "high",
            "reason": (
                "Grid conditions or curtailment may be "
                "limiting solar power output."
            ),
            "recommended_steps": [
                "Check grid availability and status.",
                "Inspect grid voltage and frequency.",
                "Check inverter grid-related warnings.",
                "Verify whether power curtailment is active."
            ]
        }

    # ==================================================
    # SENSOR OR DATA QUALITY ISSUE
    # ==================================================

    if root_cause == "sensor_or_data_quality_issue":
        return {
            "action": "inspect_sensors",
            "priority": "medium",
            "reason": (
                "Sensor or data-quality problems may be "
                "causing an incorrect representation of system performance."
            ),
            "recommended_steps": [
                "Check sensor connectivity.",
                "Inspect sensor readings for abnormal values.",
                "Check sensor calibration.",
                "Compare sensor readings with related measurements."
            ]
        }

    # ==================================================
    # UNKNOWN CAUSE
    # ==================================================

    return {
        "action": "continue_investigation",
        "priority": "medium",
        "reason": (
            "The diagnosed cause does not have a defined "
            "corrective action yet."
        ),
        "recommended_steps": [
            "Collect additional evidence.",
            "Continue monitoring the system.",
            "Re-evaluate the diagnosis."
        ]
    }