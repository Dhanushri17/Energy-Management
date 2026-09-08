import json

import agent.agent as agent_module

from agent.agent import SolarDiagnosisAgent
from agent.input_schema import AgentInput


def build_agent_input():
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
            "deviation_percent": -41.3
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
        }
    )


def run_multi_round_investigation():
    agent = SolarDiagnosisAgent()

    agent_input = build_agent_input()

    agent.receive_input(agent_input)

    original_select_tools = agent_module.select_tools

    round_number = {
        "value": 0
    }

    def controlled_select_tools(
        hypotheses,
        executed_tools=None
    ):
        round_number["value"] += 1

        if round_number["value"] == 1:
            return ["weather"]

        if round_number["value"] == 2:
            return ["inverter"]

        return original_select_tools(
            hypotheses,
            executed_tools=executed_tools
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


def validate_multi_round(agent, output):
    rounds = [
        step
        for step in agent.state.investigation_history
        if step.get("step") == "investigation_round"
    ]

    history_steps = [
        step.get("step")
        for step in agent.state.investigation_history
    ]

    first_round_data = (
        rounds[0].get("data", {})
        if len(rounds) >= 1
        else {}
    )

    second_round_data = (
        rounds[1].get("data", {})
        if len(rounds) >= 2
        else {}
    )

    first_round_tools = first_round_data.get(
        "selected_tools",
        []
    )

    second_round_tools = second_round_data.get(
        "selected_tools",
        []
    )

    first_round_sufficient = first_round_data.get(
        "evidence_sufficient"
    )

    second_round_sufficient = second_round_data.get(
        "evidence_sufficient"
    )

    return {
        "status_completed": (
            output.status == "completed"
        ),

        "diagnosis_is_inverter": (
            output.diagnosis.get("root_cause")
            == "inverter_abnormality"
        ),

        "confidence_sufficient": (
            output.confidence >= 0.50
        ),

        "multiple_rounds_completed": (
            len(rounds) >= 2
        ),

        "round_1_used_weather": (
            "weather" in first_round_tools
        ),

        "round_2_used_inverter": (
            "inverter" in second_round_tools
        ),

        "round_1_was_insufficient": (
            first_round_sufficient is False
        ),

        "round_2_was_sufficient": (
            second_round_sufficient is True
        ),

        "hypotheses_generated": (
            len(agent.state.hypotheses) > 0
        ),

        "weather_tool_executed": (
            "weather" in agent.state.executed_tools
        ),

        "inverter_tool_executed": (
            "inverter" in agent.state.executed_tools
        ),

        "tools_executed": (
            len(agent.state.executed_tools) >= 2
        ),

        "investigation_history_recorded": (
            len(agent.state.investigation_history) > 0
        ),

        "cause_ranking_recorded": (
            "cause_ranking" in history_steps
        ),

        "confidence_check_recorded": (
            "confidence_check" in history_steps
        ),

        "diagnosis_recorded": (
            "diagnosis" in history_steps
        ),

        "recommendation_recorded": (
            "recommendation" in history_steps
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
        "ranked_causes": output.ranked_causes,
        "verification": output.verification,
        "feedback": output.feedback,
        "executed_tools": agent.state.executed_tools,
        "failed_tools": agent.state.failed_tools,
        "investigation_rounds": agent.state.investigation_round,
        "investigation_history": (
            agent.state.investigation_history
        ),
        "checks": checks,
    }


def main():
    agent, output = run_multi_round_investigation()

    checks = validate_multi_round(
        agent,
        output,
    )

    passed = all(checks.values())

    results = {
        "test_suite": "multi_round_adaptive_agent",
        "tests": {
            "true_multi_round_investigation": {
                "passed": passed,
                "output": serialize_output(
                    agent,
                    output,
                    checks,
                ),
            }
        },
        "status": (
            "passed"
            if passed
            else "failed"
        ),
    }

    print(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
