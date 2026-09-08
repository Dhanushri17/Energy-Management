import json

from reasoning.hypotheses import generate_hypotheses
from reasoning.evidence import evaluate_hypotheses
from reasoning.ranking import rank_causes
from agent.workflow import select_tools


def main():
    anomaly = {
        "detected": True,
        "severity": "high",
        "deviation_percent": -41.3,
    }

    hypotheses = generate_hypotheses(anomaly)

    initial_tools = select_tools(
        hypotheses=hypotheses,
        executed_tools=[],
    )

    round_1_evidence = {
        "weather": "normal",
        "shading": "absent",
        "historical_output": "normal",
        "battery_constraint": "none",
        "grid": "normal",
        "curtailment": "inactive",
        "sensor": "normal",
    }

    hypotheses_after_round_1 = evaluate_hypotheses(
        hypotheses=hypotheses,
        evidence=round_1_evidence,
    )

    ranked_after_round_1 = rank_causes(
        hypotheses_after_round_1
    )

    executed_after_round_1 = [
        "weather",
        "history",
        "battery",
        "grid",
        "sensor_health",
    ]

    second_tools = select_tools(
        hypotheses=hypotheses_after_round_1,
        executed_tools=executed_after_round_1,
    )

    result = {
        "test_suite": "adaptive_reasoning",
        "initial_state": {
            "hypothesis_count": len(hypotheses),
            "selected_tools": initial_tools,
        },
        "round_1": {
            "evidence": round_1_evidence,
            "ranked_causes": ranked_after_round_1,
            "executed_tools": executed_after_round_1,
            "selected_next_tools": second_tools,
        },
    }

    result["checks"] = {
        "hypotheses_generated": len(hypotheses) > 0,

        "initial_tools_selected": (
            len(initial_tools) > 0
        ),

        "hypotheses_updated": any(
            hypothesis["status"] != "uninvestigated"
            for hypothesis in hypotheses_after_round_1
        ),

        "causes_ranked": (
            len(ranked_after_round_1) > 0
        ),

        "unresolved_hypothesis_exists": any(
            hypothesis["status"]
            in {
                "supports",
                "unknown",
                "neutral",
                "uninvestigated",
            }
            for hypothesis in hypotheses_after_round_1
        ),

        "next_tools_selected": (
            len(second_tools) > 0
        ),

        "no_duplicate_tool_selection": not any(
            tool in executed_after_round_1
            for tool in second_tools
        ),
    }

    result["status"] = (
        "passed"
        if all(result["checks"].values())
        else "failed"
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()