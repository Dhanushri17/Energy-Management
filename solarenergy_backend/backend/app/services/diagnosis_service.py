from typing import Any

from agent.agent import SolarDiagnosisAgent
from agent.input_schema import AgentInput


def _build_agent_evidence(
    core_evidence: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert Intelligence Core evidence into the
    flattened evidence contract expected by the AI Agent.

    Only values with a clear semantic mapping are transferred.
    Missing Core evidence remains unknown rather than being guessed.
    """

    environment = core_evidence.get("environment") or {}
    historical = core_evidence.get("historical") or {}
    inverter = core_evidence.get("inverter") or {}
    battery = core_evidence.get("battery") or {}
    grid = core_evidence.get("grid") or {}

    cause_indicators = (
        core_evidence.get("cause_indicators") or {}
    )

    sensor_indicator = (
        cause_indicators.get("sensor") or {}
    )

    environmental_indicator = (
        cause_indicators.get("environmental") or {}
    )

    constraints = (
        core_evidence.get("optimization_inputs", {})
        .get("constraints", {})
    )

    battery_validation = (
        constraints.get("battery_validation") or {}
    )

    return {
        # Environmental evidence
        "weather": environment.get(
            "status",
            "unknown",
        ),
        "irradiance": environment.get(
            "irradiance"
        ),
        "temperature": environment.get(
            "panel_temperature"
        ),
        "irradiance_status": environmental_indicator.get(
            "irradiance_status",
            "unknown",
        ),
        "temperature_status": environmental_indicator.get(
            "temperature_status",
            "unknown",
        ),
        "shading": "unknown",

        # Inverter evidence
        "inverter": inverter.get(
            "status",
            "unknown",
        ),
        "inverter_fault_code": inverter.get(
            "fault_code"
        ),

        # Battery / system constraint evidence
        "battery_constraint": battery_validation.get(
            "status",
            "unknown",
        ),
        "battery_charge_status": "unknown",

        # Grid evidence
        "grid": grid.get(
            "status",
            "unknown",
        ),
        "curtailment": "unknown",

        # Sensor evidence
        "sensor": sensor_indicator.get(
            "status",
            "unknown",
        ),
        "missing_values": None,
        "stale_data": None,
        "out_of_range": None,

        # Historical evidence
        "historical_output": historical.get(
            "comparison",
            "unknown",
        ),
        "historical_average": historical.get(
            "baseline_output"
        ),
        "current_vs_historical": historical.get(
            "deviation_percent"
        ),
    }


def _build_agent_input(
    evidence_package: dict[str, Any],
) -> AgentInput:
    """
    Build the stable AgentInput contract from the
    Intelligence Core / Backend evidence package.

    The Backend currently provides measurement fields at
    the top level, so this adapter supports that structure
    and converts field names required by the Agent.
    """

    measurement = dict(
        evidence_package.get(
            "measurement",
            {},
        )
    )

    # Current Backend API provides measurement fields
    # at the top level of the evidence package.
    if not measurement:
        measurement = {
            "plant_id": evidence_package.get(
                "plant_id"
            ),
            "timestamp": evidence_package.get(
                "timestamp"
            ),
            "irradiance": evidence_package.get(
                "irradiance"
            ),
            "temperature": evidence_package.get(
                "temperature"
            ),
            "panel_temperature": evidence_package.get(
                "panel_temperature"
            ),
            "dc_voltage": evidence_package.get(
                "dc_voltage"
            ),
            "dc_current": evidence_package.get(
                "dc_current"
            ),
            "ac_power": evidence_package.get(
                "ac_power"
            ),
            "actual_power": evidence_package.get(
                "actual_power"
            ),
            "battery_soc": evidence_package.get(
                "battery_soc"
            ),
            "inverter_status": evidence_package.get(
                "inverter_status"
            ),
        }

    # Agent verification expects actual_power.
    if measurement.get("actual_power") is None:
        measurement["actual_power"] = (
            evidence_package.get("actual_power")
        )

    prediction = dict(
        evidence_package.get(
            "prediction",
            {},
        )
    )

    # Agent verification expects expected_power,
    # while Intelligence Core calls this predicted_power.
    if prediction.get("expected_power") is None:
        prediction["expected_power"] = prediction.get(
            "predicted_power"
        )

    return AgentInput(
        measurement=measurement,
        prediction=prediction,
        anomaly=evidence_package.get(
            "anomaly",
            {},
        ),
        evidence=_build_agent_evidence(
            evidence_package.get(
                "evidence",
                {},
            )
        ),
        verification_context=evidence_package.get(
            "verification_context",
            {},
        ),
    )


def run_diagnosis_engine(
    evidence_package: dict[str, Any],
) -> dict[str, Any]:
    """
    Backend adapter for the AI Diagnosis Agent.

    The Backend does not perform diagnosis, root-cause
    reasoning, confidence calculation, or recommendation
    generation.

    It converts the Intelligence Core / Backend evidence
    package into AgentInput, executes the Agent, and then
    converts AgentOutput into the contract expected by
    the existing Backend database/API layer.
    """

    # 1. Build Agent input
    agent_input = _build_agent_input(
        evidence_package
    )

    # 2. Create and execute Agent
    diagnosis_agent = SolarDiagnosisAgent()

    diagnosis_agent.receive_input(
        agent_input
    )

    agent_output = diagnosis_agent.run().to_dict()

    # 3. Extract Agent diagnosis
    diagnosis = (
        agent_output.get("diagnosis") or {}
    )

    recommendation = (
        agent_output.get("recommendation") or {}
    )

    root_cause = diagnosis.get(
        "root_cause",
        "undetermined",
    )

    reasoning = diagnosis.get(
        "reasoning",
        "Insufficient evidence for a reliable diagnosis.",
    )

    confidence = agent_output.get(
        "confidence",
        diagnosis.get(
            "confidence",
            0.0,
        ),
    )

    # 4. Extract Agent recommendation
    action = recommendation.get(
        "action",
        "collect_additional_evidence",
    )

    priority = recommendation.get(
        "priority",
        "medium",
    )

    reason = recommendation.get(
        "reason",
        "Additional evidence is required.",
    )

    recommended_steps = recommendation.get(
        "recommended_steps",
        [],
    )

    # 5. Convert structured recommendation into
    # a database-compatible text field.
    if recommended_steps:
        recommendation_text = (
            f"{reason} "
            f"Steps: {'; '.join(recommended_steps)}"
        )
    else:
        recommendation_text = reason

    # 6. Return Backend-compatible contract while
    # preserving the complete Agent output.
    return {
        "diagnosis": reasoning,
        "probable_cause": root_cause,
        "confidence": confidence,
        "recommendation": recommendation_text,
        "action": action,
        "priority": priority,

        # Preserve the complete Agent result so the
        # richer Agent output is not lost.
        "agent_output": agent_output,
    }