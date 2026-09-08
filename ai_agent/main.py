import json

from agent.agent import SolarDiagnosisAgent
from agent.input_schema import AgentInput


def run_agent(agent_input: AgentInput):
    agent = SolarDiagnosisAgent()
    agent.receive_input(agent_input)
    return agent.run()


def test_normal_operation():
    agent_input = AgentInput(
        measurement={
            "plant_id": "PLANT_01",
            "irradiance": 850,
            "panel_temperature": 32,
            "actual_power": 9.1,
            "battery_soc": 78,
        },
        prediction={
            "expected_power": 9.2
        },
        anomaly={
            "detected": False,
            "severity": "none",
            "deviation_percent": -1.09
        },
        evidence={
            "weather": "normal",
            "shading": "absent",
            "historical_output": "normal",
            "inverter": "normal",
            "inverter_fault_code": None,
            "battery_constraint": "none",
            "battery_charge_status": "normal",
            "grid": "normal",
            "curtailment": "inactive",
            "sensor": "normal",
            "missing_values": 0,
            "stale_data": False,
            "out_of_range": False
        }
    )

    return run_agent(agent_input)


def test_successful_diagnosis():
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
            "weather": "normal",
            "shading": "absent",
            "historical_output": "normal",
            "inverter": "abnormal",
            "inverter_fault_code": "INV_001",
            "battery_constraint": "none",
            "battery_charge_status": "normal",
            "grid": "normal",
            "curtailment": "inactive",
            "sensor": "normal",
            "missing_values": 0,
            "stale_data": False,
            "out_of_range": False
        }
    )

    return run_agent(agent_input)


def test_insufficient_evidence():
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
            "out_of_range": None
        }
    )

    return run_agent(agent_input)


def validate_normal_operation(output):
    return (
        output.status == "completed"
        and output.diagnosis.get("root_cause") == "no_anomaly"
        and output.confidence == 1.0
        and not output.validate_status_contract()
    )


def validate_successful_diagnosis(output):
    return (
        output.status == "completed"
        and output.diagnosis.get("root_cause")
        not in (
            None,
            "",
            "undetermined",
            "no_anomaly",
        )
        and output.confidence >= 0.50
        and not output.validate_status_contract()
    )


def validate_insufficient_evidence(output):
    return (
        output.status == "insufficient_evidence"
        and output.diagnosis.get("root_cause") == "undetermined"
        and output.confidence == 0.0
        and output.recommendation.get("action")
        == "collect_additional_evidence"
        and not output.validate_status_contract()
    )


def serialize_output(output):
    return {
        "status": output.status,
        "confidence": output.confidence,
        "diagnosis": output.diagnosis,
        "recommendation": output.recommendation,
        "ranked_causes": output.ranked_causes,
        "verification": output.verification,
        "feedback": output.feedback,
        "status_contract_errors": output.validate_status_contract(),
    }


def main():
    normal_output = test_normal_operation()
    diagnosed_output = test_successful_diagnosis()
    insufficient_output = test_insufficient_evidence()

    results = {
        "test_suite": "hardening_4_output_status_contract",
        "tests": {
            "normal_operation": {
                "passed": validate_normal_operation(normal_output),
                "output": serialize_output(normal_output),
            },
            "successful_diagnosis": {
                "passed": validate_successful_diagnosis(diagnosed_output),
                "output": serialize_output(diagnosed_output),
            },
            "insufficient_evidence": {
                "passed": validate_insufficient_evidence(
                    insufficient_output
                ),
                "output": serialize_output(insufficient_output),
            },
        },
    }

    all_passed = all(
        test_result["passed"]
        for test_result in results["tests"].values()
    )

    results["status"] = "passed" if all_passed else "failed"

    print(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()