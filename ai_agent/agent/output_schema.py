from dataclasses import dataclass, field
from typing import Any


VALID_STATUSES = {
    "completed",
    "insufficient_evidence",
}


@dataclass
class AgentOutput:
    """
    Final output produced by the Solar Diagnosis Agent.

    Status contract
    ---------------

    completed:
        1. Normal operation with no anomaly
           OR
        2. Anomaly investigated successfully
           with a determined root cause and
           sufficient confidence.

    insufficient_evidence:
        An anomaly exists, but the available
        evidence is not sufficient to support
        a reliable diagnosis.

    The output schema acts as the final safety
    boundary of the Agent.
    """

    status: str = "completed"
    agent_version: str = "solar-diagnosis-agent-v1"

    diagnosis: dict[str, Any] = field(default_factory=dict)
    ranked_causes: list[dict[str, Any]] = field(default_factory=list)

    confidence: float = 0.0

    recommendation: dict[str, Any] = field(default_factory=dict)

    evidence: list[dict[str, Any]] = field(default_factory=list)

    investigation_summary: str = ""

    verification: dict[str, Any] = field(default_factory=dict)

    feedback: dict[str, Any] = field(default_factory=dict)

    tool_results: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Enforce the final status contract immediately
        after AgentOutput is created.

        This prevents an inconsistent output such as:

            status = completed
            root_cause = undetermined
            confidence = 0.0

        from escaping the Agent.
        """

        self._normalize_confidence()

        if self.status not in VALID_STATUSES:
            self.status = "insufficient_evidence"

        self._enforce_status_contract()

    # =========================================================
    # STATUS CONTRACT
    # =========================================================

    def _enforce_status_contract(self) -> None:
        """
        Normalize the output so that status, diagnosis,
        confidence and recommendation remain consistent.
        """

        root_cause = self.diagnosis.get("root_cause")

        # -----------------------------------------------------
        # NORMAL OPERATION
        # -----------------------------------------------------

        if root_cause == "no_anomaly":

            self.status = "completed"
            self.confidence = 1.0

            return

        # -----------------------------------------------------
        # INSUFFICIENT EVIDENCE
        # -----------------------------------------------------

        if self.status == "insufficient_evidence":

            self._set_insufficient_evidence()

            return

        # -----------------------------------------------------
        # COMPLETED ANOMALY
        # -----------------------------------------------------

        if self.status == "completed":

            # A completed anomaly investigation must have
            # a real diagnosis and sufficient confidence.

            if (
                root_cause in (None, "", "undetermined")
                or self.confidence < 0.50
            ):
                self._set_insufficient_evidence()

    # =========================================================
    # INSUFFICIENT EVIDENCE NORMALIZATION
    # =========================================================

    def _set_insufficient_evidence(self) -> None:
        """
        Force a safe insufficient-evidence state.
        """

        self.status = "insufficient_evidence"

        self.confidence = 0.0

        self.diagnosis = {
            "root_cause": "undetermined",
            "reasoning": (
                "Available evidence is insufficient "
                "to determine a reliable root cause."
            ),
        }

        self.recommendation = {
            "action": "collect_additional_evidence",
            "reasoning": (
                "Additional evidence is required before "
                "a reliable diagnosis can be made."
            ),
        }

    # =========================================================
    # CONFIDENCE NORMALIZATION
    # =========================================================

    def _normalize_confidence(self) -> None:
        """
        Keep confidence within the valid range [0, 1].
        """

        try:
            self.confidence = float(self.confidence)
        except (TypeError, ValueError):
            self.confidence = 0.0

        self.confidence = max(
            0.0,
            min(1.0, self.confidence)
        )

    # =========================================================
    # VALIDATION
    # =========================================================

    def validate_status_contract(self) -> list[str]:
        """
        Validate the final output without modifying it.

        Returns:
            list[str]: validation errors.
            Empty list means the output is valid.
        """

        errors: list[str] = []

        root_cause = self.diagnosis.get("root_cause")

        # -----------------------------------------------------
        # STATUS VALIDATION
        # -----------------------------------------------------

        if self.status not in VALID_STATUSES:

            errors.append(
                f"Invalid status: {self.status}"
            )

            return errors

        # -----------------------------------------------------
        # NORMAL OPERATION
        # -----------------------------------------------------

        if root_cause == "no_anomaly":

            if self.status != "completed":

                errors.append(
                    "Normal operation must have "
                    "status='completed'."
                )

            if self.confidence != 1.0:

                errors.append(
                    "Normal operation must have "
                    "confidence=1.0."
                )

            return errors

        # -----------------------------------------------------
        # INSUFFICIENT EVIDENCE
        # -----------------------------------------------------

        if self.status == "insufficient_evidence":

            if root_cause != "undetermined":

                errors.append(
                    "Insufficient evidence must have "
                    "root_cause='undetermined'."
                )

            if self.confidence != 0.0:

                errors.append(
                    "Insufficient evidence must have "
                    "confidence=0.0."
                )

            action = self.recommendation.get("action")

            if action != "collect_additional_evidence":

                errors.append(
                    "Insufficient evidence must recommend "
                    "'collect_additional_evidence'."
                )

            return errors

        # -----------------------------------------------------
        # COMPLETED ANOMALY
        # -----------------------------------------------------

        if self.status == "completed":

            if root_cause in (
                None,
                "",
                "undetermined",
            ):

                errors.append(
                    "Completed anomaly investigation must "
                    "have a determined root cause."
                )

            if self.confidence < 0.50:

                errors.append(
                    "Completed anomaly investigation must "
                    "have confidence >= 0.50."
                )

        return errors

    # =========================================================
    # STRICT VALIDATION
    # =========================================================

    def ensure_valid_status_contract(self) -> None:
        """
        Raise ValueError if the output violates the
        status contract.
        """

        errors = self.validate_status_contract()

        if errors:

            raise ValueError(
                "Invalid AgentOutput status contract: "
                + " ".join(errors)
            )

    # =========================================================
    # SERIALIZATION
    # =========================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the Agent output into a JSON-compatible
        dictionary.
        """

        return {
            "status": self.status,
            "agent_version": self.agent_version,
            "diagnosis": self.diagnosis,
            "ranked_causes": self.ranked_causes,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
            "evidence": self.evidence,
            "investigation_summary": self.investigation_summary,
            "verification": self.verification,
            "feedback": self.feedback,
            "tool_results": self.tool_results,
        }

    # =========================================================
    # STATUS HELPERS
    # =========================================================

    def is_successful(self) -> bool:
        """
        True only when the Agent completed successfully.
        """

        return self.status == "completed"

    def is_insufficient_evidence(self) -> bool:
        """
        True when the Agent could not obtain enough
        evidence for a reliable diagnosis.
        """

        return self.status == "insufficient_evidence"