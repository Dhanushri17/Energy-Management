from typing import Any

from .state import InvestigationState
from .input_schema import AgentInput
from .output_schema import AgentOutput

from reasoning.hypotheses import generate_hypotheses
from reasoning.evidence import evaluate_hypotheses
from reasoning.ranking import rank_causes
from reasoning.confidence import calculate_confidence

from agent.workflow import select_tools

from tools.inverter import get_inverter_status
from tools.weather import get_weather_data
from tools.battery import get_battery_status
from tools.grid import get_grid_status
from tools.sensor_health import get_sensor_health
from tools.history import get_historical_generation

from diagnosis.diagnosis import generate_diagnosis

from recommendation.recommendation import (
    generate_recommendation
)

from verification.verification import (
    verify_action
)

from feedback.feedback import (
    record_feedback
)


class SolarDiagnosisAgent:
    """
    Domain-specific solar-energy diagnosis and reasoning agent.

    The Agent:
    - receives evidence from the Intelligence Core
    - generates possible causes
    - selects investigation tools
    - gathers additional evidence
    - evaluates hypotheses
    - ranks possible causes
    - calculates confidence
    - decides whether more investigation is required
    - generates diagnosis
    - generates recommendation
    - verifies the outcome when after-measurement data exists
    - records a learning signal

    The Agent does NOT perform ML prediction.
    The Agent does NOT train models.
    The Agent does NOT use an LLM.
    """

    def __init__(self):
        self.state = InvestigationState()

    # ==========================================================
    # INPUT
    # ==========================================================

    def receive_input(
        self,
        agent_input: AgentInput
    ) -> None:
        """
        Receive a fresh evidence package from the
        Intelligence Core.

        Every run starts with a clean investigation state.
        """

        if not isinstance(agent_input, AgentInput):
            raise TypeError(
                "agent_input must be an AgentInput instance."
            )

        errors = agent_input.validate()

        if errors:
            raise ValueError(
                "Invalid AgentInput: "
                + " ".join(errors)
            )

        self.state.reset_investigation()

        self.state.measurement = dict(
            agent_input.measurement
        )

        self.state.prediction = dict(
            agent_input.prediction
        )

        self.state.anomaly = dict(
            agent_input.anomaly
        )

        self.state.evidence = dict(
            agent_input.evidence
        )

        self.state.verification_context = dict(
            agent_input.verification_context
        )

        self.state.record_step(
            "input_received",
            {
                "measurement_available": bool(
                    self.state.measurement
                ),
                "prediction_available": bool(
                    self.state.prediction
                ),
                "anomaly_available": bool(
                    self.state.anomaly
                ),
                "evidence_available": bool(
                    self.state.evidence
                ),
                "verification_context_available": bool(
                    self.state.verification_context
                ),
            }
        )

    # ==========================================================
    # TOOL EXECUTION
    # ==========================================================

    def _execute_tool(
        self,
        tool_name: str
    ) -> dict[str, Any]:
        """
        Execute one investigation tool.

        Tool failures are captured as structured results.
        A failed tool must never be interpreted as normal
        operating evidence.
        """

        try:

            if tool_name == "inverter":

                inverter_data = {
                    "status": self.state.evidence.get(
                        "inverter",
                        "unknown"
                    ),
                    "fault_code": self.state.evidence.get(
                        "inverter_fault_code"
                    ),
                    "temperature": self.state.evidence.get(
                        "inverter_temperature"
                    ),
                    "ac_output": self.state.measurement.get(
                        "actual_power"
                    ),
                }

                return get_inverter_status(
                    inverter_data
                )

            if tool_name == "weather":

                weather_data = {
                    "status": self.state.evidence.get(
                        "weather",
                        "unknown"
                    ),
                    "irradiance": self.state.measurement.get(
                        "irradiance"
                    ),
                    "temperature": self.state.measurement.get(
                        "panel_temperature"
                    ),
                    "cloud_cover": self.state.evidence.get(
                        "cloud_cover"
                    ),
                    "shading": self.state.evidence.get(
                        "shading",
                        "unknown"
                    ),
                }

                return get_weather_data(
                    weather_data
                )

            if tool_name == "battery":

                battery_data = {
                    "soc": self.state.measurement.get(
                        "battery_soc"
                    ),
                    "charge_status": self.state.evidence.get(
                        "battery_charge_status",
                        "unknown"
                    ),
                    "constraint": self.state.evidence.get(
                        "battery_constraint",
                        "unknown"
                    ),
                    "battery_temperature": self.state.evidence.get(
                        "battery_temperature"
                    ),
                }

                return get_battery_status(
                    battery_data
                )

            if tool_name == "grid":

                grid_data = {
                    "status": self.state.evidence.get(
                        "grid",
                        "unknown"
                    ),
                    "voltage": self.state.evidence.get(
                        "grid_voltage"
                    ),
                    "frequency": self.state.evidence.get(
                        "grid_frequency"
                    ),
                    "curtailment": self.state.evidence.get(
                        "curtailment",
                        "unknown"
                    ),
                }

                return get_grid_status(
                    grid_data
                )

            if tool_name == "sensor_health":

                sensor_data = {
                    "status": self.state.evidence.get(
                        "sensor",
                        "unknown"
                    ),
                    "missing_values": self.state.evidence.get(
                        "missing_values"
                    ),
                    "stale_data": self.state.evidence.get(
                        "stale_data"
                    ),
                    "out_of_range": self.state.evidence.get(
                        "out_of_range"
                    ),
                }

                return get_sensor_health(
                    sensor_data
                )

            if tool_name == "history":

                history_data = {
                    "status": self.state.evidence.get(
                        "historical_output",
                        "unknown"
                    ),
                    "historical_average": self.state.evidence.get(
                        "historical_average"
                    ),
                    "current_vs_historical": self.state.evidence.get(
                        "current_vs_historical"
                    ),
                    "similar_anomalies": self.state.evidence.get(
                        "similar_anomalies",
                        0
                    ),
                }

                return get_historical_generation(
                    history_data
                )

            raise ValueError(
                f"Unknown investigation tool: {tool_name}"
            )

        except Exception as exc:

            error_message = str(exc)

            self.state.failed_tools[
                tool_name
            ] = error_message

            self.state.record_step(
                "tool_failure",
                {
                    "tool": tool_name,
                    "error": error_message,
                    "round": self.state.investigation_round,
                }
            )

            return {
                "component": tool_name,
                "available": False,
                "status": "tool_error",
                "error": error_message,
            }

    # ==========================================================
    # BUILD INVESTIGATION EVIDENCE
    # ==========================================================

    def _build_investigation_evidence(
        self
    ) -> dict[str, Any]:
        """
        Convert successful tool results into normalized
        investigation evidence.

        Tool failures are represented as unknown and therefore
        cannot accidentally become supporting evidence.
        """

        investigation_evidence = dict(
            self.state.evidence
        )

        for tool_name, result in (
            self.state.tool_results.items()
        ):

            if not isinstance(result, dict):
                continue

            if result.get("available") is False:
                continue

            if result.get("status") == "tool_error":
                continue

            if tool_name == "inverter":

                status = result.get(
                    "status",
                    "unknown"
                )

                investigation_evidence[
                    "inverter"
                ] = status

                investigation_evidence[
                    "inverter_fault_code"
                ] = result.get(
                    "fault_code"
                )

                if result.get(
                    "temperature"
                ) is not None:

                    investigation_evidence[
                        "inverter_temperature"
                    ] = result.get(
                        "temperature"
                    )

            elif tool_name == "weather":

                investigation_evidence[
                    "weather"
                ] = result.get(
                    "status",
                    "unknown"
                )

                investigation_evidence[
                    "shading"
                ] = result.get(
                    "shading",
                    "unknown"
                )

                if result.get(
                    "cloud_cover"
                ) is not None:

                    investigation_evidence[
                        "cloud_cover"
                    ] = result.get(
                        "cloud_cover"
                    )

            elif tool_name == "battery":

                investigation_evidence[
                    "battery_constraint"
                ] = result.get(
                    "constraint",
                    "unknown"
                )

                investigation_evidence[
                    "battery_charge_status"
                ] = result.get(
                    "charge_status",
                    "unknown"
                )

            elif tool_name == "grid":

                investigation_evidence[
                    "grid"
                ] = result.get(
                    "status",
                    "unknown"
                )

                investigation_evidence[
                    "curtailment"
                ] = result.get(
                    "curtailment",
                    "unknown"
                )

            elif tool_name == "sensor_health":

                investigation_evidence[
                    "sensor"
                ] = result.get(
                    "status",
                    "unknown"
                )

                investigation_evidence[
                    "missing_values"
                ] = result.get(
                    "missing_values"
                )

                investigation_evidence[
                    "stale_data"
                ] = result.get(
                    "stale_data"
                )

                investigation_evidence[
                    "out_of_range"
                ] = result.get(
                    "out_of_range"
                )

            elif tool_name == "history":

                investigation_evidence[
                    "historical_output"
                ] = result.get(
                    "status",
                    "unknown"
                )

                if result.get(
                    "historical_average"
                ) is not None:

                    investigation_evidence[
                        "historical_average"
                    ] = result.get(
                        "historical_average"
                    )

                if result.get(
                    "current_vs_historical"
                ) is not None:

                    investigation_evidence[
                        "current_vs_historical"
                    ] = result.get(
                        "current_vs_historical"
                    )

        return investigation_evidence

    # ==========================================================
    # HYPOTHESIS EVALUATION
    # ==========================================================

    def _evaluate_hypotheses(
        self
    ) -> None:
        """
        Evaluate every hypothesis against all evidence
        collected so far.
        """

        self.state.hypotheses = evaluate_hypotheses(
            hypotheses=self.state.hypotheses,
            evidence=self.state.investigation_evidence
        )

        self.state.record_step(
            "hypothesis_evaluation",
            {
                "round": self.state.investigation_round,
                "evidence": dict(
                    self.state.investigation_evidence
                ),
                "hypotheses": self.state.hypotheses,
            }
        )

    # ==========================================================
    # EVIDENCE SUFFICIENCY
    # ==========================================================

    def _check_evidence_sufficiency(
        self
    ) -> bool:
        """
        Determine whether the current evidence is strong enough
        to make a diagnosis.

        A diagnosis requires:
        - a positive top cause
        - meaningful confidence
        - no unresolved stronger competing cause
        """

        if not self.state.ranked_causes:
            return False

        top_cause = self.state.ranked_causes[0]

        top_score = float(
            top_cause.get(
                "score",
                0.0
            )
        )

        if top_score <= 0:
            return False

        if self.state.confidence < 0.50:
            return False

        positive_causes = [
            cause
            for cause in self.state.ranked_causes
            if float(
                cause.get(
                    "score",
                    0.0
                )
            ) > 0
        ]

        if len(positive_causes) > 1:

            top_score = float(
                positive_causes[0].get(
                    "score",
                    0.0
                )
            )

            second_score = float(
                positive_causes[1].get(
                    "score",
                    0.0
                )
            )

            if (
                top_score - second_score
                < 0.20
            ):
                return False

        return True

    # ==========================================================
    # ADAPTIVE INVESTIGATION LOOP
    # ==========================================================

    def _run_investigation(
        self
    ) -> None:
        """
        Run the adaptive investigation loop.

        Each round:

        1. Select unused tools.
        2. Execute them.
        3. Collect evidence.
        4. Re-evaluate hypotheses.
        5. Re-rank causes.
        6. Recalculate confidence.
        7. Decide whether another round is required.

        The Agent does NOT stop simply because the current
        round's tools have finished executing.
        """

        while (
            self.state.investigation_round
            < self.state.max_investigation_rounds
        ):

            self.state.investigation_round += 1

            # --------------------------------------------------
            # SELECT NEW TOOLS
            # --------------------------------------------------

            next_tools = select_tools(
                self.state.hypotheses,
                executed_tools=self.state.executed_tools
            )

            self.state.pending_tools = list(
                next_tools
            )

            self.state.selected_tools = list(
                next_tools
            )

            # --------------------------------------------------
            # NO NEW TOOLS
            # --------------------------------------------------

            if not self.state.pending_tools:

                self.state.record_step(
                    "investigation_complete",
                    {
                        "reason": (
                            "no_new_tools_available"
                        ),
                        "round": (
                            self.state.investigation_round
                        ),
                        "confidence": (
                            self.state.confidence
                        ),
                    }
                )

                break

            # --------------------------------------------------
            # EXECUTE CURRENT ROUND
            # --------------------------------------------------

            current_tools = list(
                self.state.pending_tools
            )

            for tool_name in current_tools:

                if tool_name in (
                    self.state.executed_tools
                ):
                    continue

                result = self._execute_tool(
                    tool_name
                )

                self.state.tool_results[
                    tool_name
                ] = result

                self.state.executed_tools.append(
                    tool_name
                )

            # Current tools have now been consumed.
            self.state.pending_tools = []

            # --------------------------------------------------
            # BUILD EVIDENCE
            # --------------------------------------------------

            self.state.investigation_evidence = (
                self._build_investigation_evidence()
            )

            # --------------------------------------------------
            # EVALUATE HYPOTHESES
            # --------------------------------------------------

            self._evaluate_hypotheses()

            # --------------------------------------------------
            # RANK CAUSES
            # --------------------------------------------------

            self.state.ranked_causes = rank_causes(
                self.state.hypotheses
            )

            self.state.record_step(
                "cause_ranking",
                {
                    "round": (
                        self.state.investigation_round
                    ),
                    "ranked_causes": (
                        self.state.ranked_causes
                    ),
                }
            )

            # --------------------------------------------------
            # CALCULATE CONFIDENCE
            # --------------------------------------------------

            self.state.confidence = (
                calculate_confidence(
                    self.state.ranked_causes
                )
            )

            # --------------------------------------------------
            # CHECK SUFFICIENCY
            # --------------------------------------------------

            self.state.evidence_sufficient = (
                self._check_evidence_sufficiency()
            )

            self.state.record_step(
                "confidence_check",
                {
                    "round": (
                        self.state.investigation_round
                    ),
                    "confidence": (
                        self.state.confidence
                    ),
                    "evidence_sufficient": (
                        self.state.evidence_sufficient
                    ),
                    "failed_tools": dict(
                        self.state.failed_tools
                    ),
                }
            )

            # --------------------------------------------------
            # TRACE ROUND
            # --------------------------------------------------

            self.state.record_step(
                "investigation_round",
                {
                    "round": (
                        self.state.investigation_round
                    ),
                    "selected_tools": (
                        current_tools
                    ),
                    "executed_tools": list(
                        self.state.executed_tools
                    ),
                    "failed_tools": dict(
                        self.state.failed_tools
                    ),
                    "confidence": (
                        self.state.confidence
                    ),
                    "evidence_sufficient": (
                        self.state.evidence_sufficient
                    ),
                }
            )

            # --------------------------------------------------
            # STOP IF ENOUGH EVIDENCE
            # --------------------------------------------------

            if self.state.evidence_sufficient:

                self.state.record_step(
                    "investigation_complete",
                    {
                        "reason": (
                            "evidence_sufficient"
                        ),
                        "round": (
                            self.state.investigation_round
                        ),
                        "confidence": (
                            self.state.confidence
                        ),
                    }
                )

                break

            # --------------------------------------------------
            # OTHERWISE CONTINUE
            # --------------------------------------------------

            if (
                self.state.investigation_round
                >= self.state.max_investigation_rounds
            ):

                self.state.record_step(
                    "investigation_complete",
                    {
                        "reason": (
                            "max_rounds_reached"
                        ),
                        "round": (
                            self.state.investigation_round
                        ),
                        "confidence": (
                            self.state.confidence
                        ),
                    }
                )

                break

            # The next loop iteration will select unused tools.
            # This is the adaptive part of the Agent.

    # ==========================================================
    # NO ANOMALY
    # ==========================================================

    def _handle_no_anomaly(
        self
    ) -> None:
        """
        Handle a normal operating condition.
        """

        self.state.ranked_causes = []

        self.state.confidence = 1.0

        self.state.evidence_sufficient = True

        self.state.diagnosis = {
            "root_cause": "no_anomaly",
            "confidence": 1.0,
            "reasoning": (
                "The Intelligence Core did not detect "
                "a significant anomaly."
            ),
            "evidence": [],
        }

        self.state.recommendation = {
            "action": "continue_monitoring",
            "priority": "normal",
            "reason": (
                "System operation is within the "
                "expected range."
            ),
        }

        self.state.verification = {
            "status": "not_required",
            "reason": (
                "No corrective action was required."
            ),
        }

        self.state.feedback = {
            "status": "normal_operation",
            "signal": 0,
        }

    # ==========================================================
    # OUTPUT
    # ==========================================================

    def _build_output(
        self
    ) -> AgentOutput:
        """
        Build the final machine-readable Agent output.
        """

        if (
            self.state.evidence_sufficient
            and self.state.diagnosis.get(
                "root_cause"
            ) not in (
                None,
                "",
                "undetermined",
            )
        ):

            status = "completed"

        else:

            status = "insufficient_evidence"

        return AgentOutput(
            status=status,

            diagnosis=dict(
                self.state.diagnosis
            ),

            ranked_causes=list(
                self.state.ranked_causes
            ),

            confidence=float(
                self.state.confidence
            ),

            recommendation=dict(
                self.state.recommendation
            ),

            evidence=[
                {
                    "type": "intelligence_evidence",
                    "evidence": dict(
                        self.state.evidence
                    ),
                },
                {
                    "type": "investigation_evidence",
                    "evidence": dict(
                        self.state.investigation_evidence
                    ),
                },
                {
                    "type": "hypothesis_evaluation",
                    "hypotheses": list(
                        self.state.hypotheses
                    ),
                },
            ],

            investigation_summary=(
                "The Agent investigated the anomaly "
                "using hypothesis-driven tool selection, "
                "iterative evidence collection, "
                "hypothesis evaluation, cause ranking, "
                "confidence assessment, diagnosis, "
                "recommendation, verification, and "
                "feedback recording."
            ),

            verification=dict(
                self.state.verification
            ),

            feedback=dict(
                self.state.feedback
            ),

            tool_results=dict(
                self.state.tool_results
            ),

        )

    # ==========================================================
    # MAIN AGENT LOOP
    # ==========================================================

    def run(self) -> AgentOutput:
        """
        Execute the complete Agent workflow.
        """

        # --------------------------------------------------
        # INPUT SAFETY
        # --------------------------------------------------

        if not self.state.measurement and not (
            self.state.prediction
            or self.state.anomaly
            or self.state.evidence
        ):

            raise RuntimeError(
                "Agent cannot run before receiving input."
            )

        # --------------------------------------------------
        # STEP 1: UNDERSTAND ANOMALY
        # --------------------------------------------------

        anomaly_detected = bool(
            self.state.anomaly.get(
                "detected",
                False
            )
        )

        # --------------------------------------------------
        # STEP 2: NORMAL OPERATION
        # --------------------------------------------------

        if not anomaly_detected:

            self._handle_no_anomaly()

            self.state.record_step(
                "diagnosis",
                {
                    "diagnosis": (
                        self.state.diagnosis
                    )
                }
            )

            self.state.record_step(
                "recommendation",
                {
                    "recommendation": (
                        self.state.recommendation
                    )
                }
            )

            self.state.record_step(
                "verification",
                {
                    "verification": (
                        self.state.verification
                    )
                }
            )

            self.state.record_step(
                "feedback_learning",
                {
                    "feedback": (
                        self.state.feedback
                    )
                }
            )

            return self._build_output()

        # --------------------------------------------------
        # STEP 3: GENERATE HYPOTHESES
        # --------------------------------------------------

        self.state.hypotheses = (
            generate_hypotheses(
                self.state.anomaly
            )
        )

        self.state.record_step(
            "hypothesis_generation",
            {
                "hypotheses": (
                    self.state.hypotheses
                )
            }
        )

        # --------------------------------------------------
        # STEP 4: ADAPTIVE INVESTIGATION
        # --------------------------------------------------

        self._run_investigation()

        # --------------------------------------------------
        # STEP 5: DIAGNOSIS
        # --------------------------------------------------

        self.state.diagnosis = generate_diagnosis(
            ranked_causes=self.state.ranked_causes,
            confidence=self.state.confidence
        )

        # If evidence is insufficient, force an
        # explicit undetermined diagnosis.
        if not self.state.evidence_sufficient:

            self.state.diagnosis = {
                "root_cause": "undetermined",
                "confidence": 0.0,
                "reasoning": (
                    "Available evidence is insufficient "
                    "to determine a reliable root cause."
                ),
                "evidence": [],
            }

        self.state.record_step(
            "diagnosis",
            {
                "diagnosis": (
                    self.state.diagnosis
                )
            }
        )

        # --------------------------------------------------
        # STEP 6: RECOMMENDATION
        # --------------------------------------------------

        self.state.recommendation = (
            generate_recommendation(
                diagnosis=self.state.diagnosis,
                confidence=self.state.confidence
            )
        )

        if not self.state.evidence_sufficient:

            self.state.recommendation = {
                "action": (
                    "collect_additional_evidence"
                ),
                "priority": "medium",
                "reason": (
                    "The Agent does not have enough "
                    "evidence to recommend a specific "
                    "corrective action."
                ),
            }

        self.state.record_step(
            "recommendation",
            {
                "recommendation": (
                    self.state.recommendation
                )
            }
        )

        # --------------------------------------------------
        # STEP 7: VERIFICATION
        # --------------------------------------------------

        before_measurement = {
            "actual_power": (
                self.state.measurement.get(
                    "actual_power"
                )
            ),
            "expected_power": (
                self.state.prediction.get(
                    "expected_power"
                )
            ),
        }

        after_measurement = (
            self.state.verification_context.get(
                "after_measurement",
                {}
            )
        )

        self.state.verification = verify_action(
            diagnosis=self.state.diagnosis,
            recommendation=self.state.recommendation,
            before_measurement=before_measurement,
            after_measurement=after_measurement
        )

        self.state.record_step(
            "verification",
            {
                "verification": (
                    self.state.verification
                )
            }
        )

        # --------------------------------------------------
        # STEP 8: FEEDBACK / LEARNING
        # --------------------------------------------------

        self.state.feedback = record_feedback(
            diagnosis=self.state.diagnosis,
            recommendation=self.state.recommendation,
            verification=self.state.verification
        )

        self.state.record_step(
            "feedback_learning",
            {
                "feedback": (
                    self.state.feedback
                )
            }
        )

        # --------------------------------------------------
        # STEP 9: FINAL OUTPUT
        # --------------------------------------------------

        return self._build_output()