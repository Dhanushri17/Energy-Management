from dataclasses import dataclass, field
from typing import Any


@dataclass
class InvestigationState:
    """
    Stores everything the AI Agent knows during
    a single solar-energy anomaly investigation.

    A fresh InvestigationState should be used for
    every independent investigation.
    """

    # ======================================================
    # INPUT FROM INTELLIGENCE CORE
    # ======================================================

    measurement: dict[str, Any] = field(default_factory=dict)

    prediction: dict[str, Any] = field(default_factory=dict)

    anomaly: dict[str, Any] = field(default_factory=dict)

    evidence: dict[str, Any] = field(default_factory=dict)

    verification_context: dict[str, Any] = field(
        default_factory=dict
    )

    # ======================================================
    # INVESTIGATION
    # ======================================================

    hypotheses: list[dict[str, Any]] = field(
        default_factory=list
    )

    selected_tools: list[str] = field(
        default_factory=list
    )

    executed_tools: list[str] = field(
        default_factory=list
    )

    pending_tools: list[str] = field(
        default_factory=list
    )

    failed_tools: dict[str, str] = field(
        default_factory=dict
    )

    investigation_round: int = 0

    max_investigation_rounds: int = 3

    investigation_history: list[dict[str, Any]] = field(
        default_factory=list
    )

    tool_results: dict[str, Any] = field(
        default_factory=dict
    )

    investigation_evidence: dict[str, Any] = field(
        default_factory=dict
    )

    # ======================================================
    # REASONING
    # ======================================================

    ranked_causes: list[dict[str, Any]] = field(
        default_factory=list
    )

    confidence: float = 0.0

    evidence_sufficient: bool = False

    # ======================================================
    # DECISION
    # ======================================================

    diagnosis: dict[str, Any] = field(
        default_factory=dict
    )

    recommendation: dict[str, Any] = field(
        default_factory=dict
    )

    # ======================================================
    # VERIFICATION / LEARNING
    # ======================================================

    verification: dict[str, Any] = field(
        default_factory=dict
    )

    feedback: dict[str, Any] = field(
        default_factory=dict
    )

    # ======================================================
    # RESET
    # ======================================================

    def reset_investigation(self) -> None:
        """
        Clear all investigation-specific state.

        This prevents information from a previous
        investigation from contaminating a new one.
        """

        self.measurement = {}

        self.prediction = {}

        self.anomaly = {}

        self.evidence = {}

        self.verification_context = {}

        self.hypotheses = []

        self.selected_tools = []

        self.executed_tools = []

        self.pending_tools = []

        self.failed_tools = {}

        self.investigation_round = 0

        self.investigation_history = []

        self.tool_results = {}

        self.investigation_evidence = {}

        self.ranked_causes = []

        self.confidence = 0.0

        self.evidence_sufficient = False

        self.diagnosis = {}

        self.recommendation = {}

        self.verification = {}

        self.feedback = {}

    # ======================================================
    # INVESTIGATION HISTORY
    # ======================================================

    def record_step(
        self,
        step: str,
        data: dict[str, Any] | None = None
    ) -> None:
        """
        Record one step of the investigation.
        """

        self.investigation_history.append(
            {
                "step": step,
                "data": data or {}
            }
        )