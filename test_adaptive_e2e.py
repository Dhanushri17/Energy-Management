import json

from agent.agent import SolarDiagnosisAgent
from agent.input_schema import AgentInput


def run_adaptive_investigation():
    agent_input = AgentInput(
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
            "inverter": "abnormal",
            "inverter_fault_code": "INV_DC_FAULT",
            "weather": "unknown",
            "shading": "unknown",
            "historical_output": "unknown",
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

    agent = SolarDiagnosisAgent()

    agent.receive_input(agent_input)

    output = agent.run()

    return agent, output


def validate_adaptive_loop(agent, output):
    history_steps = [
        step.get("step")
        for step in agent.state.investigation_history
    ]

    rounds = [
        step
        for step in agent.state.investigation_history
        if step.get("step") == "investigation_round"
    ]

    return {
        "status_completed": output.status == "completed",

        "diagnosis_is_inverter": (
            output.diagnosis.get("root_cause")
            == "inverter_abnormality"
        ),

        "confidence_sufficient": output.confidence >= 0.50,

        "investigation_round_completed": (
            len(rounds) >= 1
        ),

        "hypotheses_generated": (
            len(agent.state.hypotheses) > 0
        ),

        "tools_executed": (
            len(agent.state.executed_tools) > 0
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
    agent, output = run_adaptive_investigation()

    checks = validate_adaptive_loop(
        agent,
        output,
    )

    passed = all(checks.values())

    results = {
        "test_suite": "adaptive_agent_e2e",
        "tests": {
            "full_adaptive_investigation": {
                "passed": passed,
                "output": serialize_output(
                    agent,
                    output,
                    checks,
                ),
            }
        },
        "status": "passed" if passed else "failed",
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