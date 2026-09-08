import json

import agent.agent as agent_module

from agent.agent import SolarDiagnosisAgent
from agent.input_schema import AgentInput


def build_agent_input(after_power):
    return AgentInput(
        measurement={
            "plant_id": "PLANT_01",
            "irradiance": 850,
            "panel_temperature": 32,
            "actual_power": 5.4,
            "battery_soc": 78,
        },
        prediction={
            "expected_power": 9.2
        },
        anomaly={
            "detected": True,
            "severity": "high",
            "deviation_percent": -41.3,
        },
        evidence={
            "weather": "unknown",
            "shading": "unknown",
            "historical_output": "unknown",
            "inverter": "unknown",
            "inverter_fault_code": None,
            "battery_constraint": "unknown",
            "battery_charge_status": "unknown",
            "grid": "unknown",
            "curtailment": "unknown",
            "sensor": "unknown",
            "missing_values": None,
            "stale_data": None,
            "out_of_range": None,
        },
        verification_context={
            "after_measurement": {
                "actual_power": after_power,
            }
        },
    )


def run_verification_scenario(after_power):
    agent = SolarDiagnosisAgent()

    agent_input = build_agent_input(after_power=after_power)
    agent.receive_input(agent_input)

    original_select_tools = agent_module.select_tools
    round_number = {"value": 0}

    def controlled_select_tools(hypotheses, executed_tools=None):
        round_number["value"] += 1

        if round_number["value"] == 1:
            return ["weather"]

        if round_number["value"] == 2:
            return ["inverter"]

        return original_select_tools(
            hypotheses,
            executed_tools=executed_tools,
        )

    agent_module.select_tools = controlled_select_tools

    original_execute_tool = agent._execute_tool

    def controlled_execute_tool(tool_name):
        if tool_name == "weather":
            agent.state.evidence["weather"] = "normal"

        elif tool_name == "inverter":
            agent.state.evidence["inverter"] = "abnormal"
            agent.state.evidence["inverter_fault_code"] = "INV_DC_FAULT"

        return original_execute_tool(tool_name)

    agent._execute_tool = controlled_execute_tool

    try:
        output = agent.run()
    finally:
        agent_module.select_tools = original_select_tools

    return agent, output


def validate_success_scenario(agent, output):
    verification = output.verification
    feedback = output.feedback

    history_steps = [
        step.get("step")
        for step in agent.state.investigation_history
    ]

    return {
        "status_completed": output.status == "completed",
        "diagnosis_is_inverter": (
            output.diagnosis.get("root_cause")
            == "inverter_abnormality"
        ),
        "recommendation_is_inspect_inverter": (
            output.recommendation.get("action")
            == "inspect_inverter"
        ),
        "verification_improved": (
            verification.get("status") == "improved"
        ),
        "verification_true": (
            verification.get("verified") is True
        ),
        "before_power_correct": (
            verification.get("before_power") == 5.4
        ),
        "after_power_correct": (
            verification.get("after_power") == 8.7
        ),
        "power_change_correct": (
            verification.get("power_change") == 3.3
        ),
        "after_closer_to_expected": (
            abs(verification.get("after_deviation"))
            < abs(verification.get("before_deviation"))
        ),
        "feedback_supported": (
            feedback.get("outcome") == "supported"
        ),
        "learning_signal_positive": (
            feedback.get("learning_signal") == 1.0
        ),
        "feedback_verified": (
            feedback.get("verified") is True
        ),
        "verification_recorded": (
            "verification" in history_steps
        ),
        "feedback_recorded": (
            "feedback_learning" in history_steps
        ),
    }


def validate_failure_scenario(agent, output):
    verification = output.verification
    feedback = output.feedback

    history_steps = [
        step.get("step")
        for step in agent.state.investigation_history
    ]

    return {
        "status_completed": output.status == "completed",
        "diagnosis_is_inverter": (
            output.diagnosis.get("root_cause")
            == "inverter_abnormality"
        ),
        "recommendation_is_inspect_inverter": (
            output.recommendation.get("action")
            == "inspect_inverter"
        ),
        "verification_not_improved": (
            verification.get("status") == "not_improved"
        ),
        "verification_false": (
            verification.get("verified") is False
        ),
        "before_power_correct": (
            verification.get("before_power") == 5.4
        ),
        "after_power_correct": (
            verification.get("after_power") == 4.8
        ),
        "power_change_correct": (
            verification.get("power_change") == -0.6
        ),
        "after_farther_from_expected": (
            abs(verification.get("after_deviation"))
            > abs(verification.get("before_deviation"))
        ),
        "feedback_not_supported": (
            feedback.get("outcome") == "not_supported"
        ),
        "learning_signal_negative": (
            feedback.get("learning_signal") == -1.0
        ),
        "feedback_verified": (
            feedback.get("verified") is False
        ),
        "verification_recorded": (
            "verification" in history_steps
        ),
        "feedback_recorded": (
            "feedback_learning" in history_steps
        ),
    }


def serialize_output(agent, output, checks):
    return {
        "status": output.status,
        "confidence": output.confidence,
        "diagnosis": output.diagnosis,
        "recommendation": output.recommendation,
        "verification": output.verification,
        "feedback": output.feedback,
        "executed_tools": agent.state.executed_tools,
        "investigation_rounds": agent.state.investigation_round,
        "checks": checks,
    }


def main():
    success_agent, success_output = run_verification_scenario(
        after_power=8.7
    )

    success_checks = validate_success_scenario(
        success_agent,
        success_output,
    )

    failure_agent, failure_output = run_verification_scenario(
        after_power=4.8
    )

    failure_checks = validate_failure_scenario(
        failure_agent,
        failure_output,
    )

    success_passed = all(success_checks.values())
    failure_passed = all(failure_checks.values())
    overall_passed = success_passed and failure_passed

    results = {
        "test_suite": "real_verification_flow",
        "tests": {
            "successful_intervention": {
                "passed": success_passed,
                "output": serialize_output(
                    success_agent,
                    success_output,
                    success_checks,
                ),
            },
            "failed_intervention": {
                "passed": failure_passed,
                "output": serialize_output(
                    failure_agent,
                    failure_output,
                    failure_checks,
                ),
            },
        },
        "status": "passed" if overall_passed else "failed",
    }

    print(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
