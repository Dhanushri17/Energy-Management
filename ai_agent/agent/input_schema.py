from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentInput:
    """
    Stable input contract for the AI Diagnosis Agent.

    The Intelligence Core provides the current system state,
    prediction results, anomaly information, and supporting evidence.

    The Agent does not collect raw sensor data directly.
    It receives a structured evidence package and investigates it.
    """

    measurement: dict[str, Any] = field(
        default_factory=dict
    )

    prediction: dict[str, Any] = field(
        default_factory=dict
    )

    anomaly: dict[str, Any] = field(
        default_factory=dict
    )

    evidence: dict[str, Any] = field(
        default_factory=dict
    )

    # Optional context used when verification is available.
    #
    # During the initial investigation this can remain empty.
    # After an action is performed, the system can provide
    # post-action measurements here.
    verification_context: dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> list[str]:
        """
        Validate the minimum structure required by the Agent.

        Returns:
            A list of validation errors.
            An empty list means the input is structurally valid.
        """

        errors: list[str] = []

        if not isinstance(self.measurement, dict):
            errors.append(
                "measurement must be a dictionary."
            )

        if not isinstance(self.prediction, dict):
            errors.append(
                "prediction must be a dictionary."
            )

        if not isinstance(self.anomaly, dict):
            errors.append(
                "anomaly must be a dictionary."
            )

        if not isinstance(self.evidence, dict):
            errors.append(
                "evidence must be a dictionary."
            )

        if not isinstance(self.verification_context, dict):
            errors.append(
                "verification_context must be a dictionary."
            )

        return errors

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any]
    ) -> "AgentInput":
        """
        Create AgentInput from a dictionary.

        This is the interface that will be useful during
        Intelligence Core → Agent integration.
        """

        if not isinstance(data, dict):
            raise TypeError(
                "AgentInput data must be a dictionary."
            )

        input_data = cls(
            measurement=data.get(
                "measurement",
                {}
            ),
            prediction=data.get(
                "prediction",
                {}
            ),
            anomaly=data.get(
                "anomaly",
                {}
            ),
            evidence=data.get(
                "evidence",
                {}
            ),
            verification_context=data.get(
                "verification_context",
                {}
            )
        )

        errors = input_data.validate()

        if errors:
            raise ValueError(
                "Invalid AgentInput: "
                + " ".join(errors)
            )

        return input_data

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the input contract into a plain dictionary.

        Useful for API communication, logging, testing,
        and future backend integration.
        """

        return {
            "measurement": self.measurement,
            "prediction": self.prediction,
            "anomaly": self.anomaly,
            "evidence": self.evidence,
            "verification_context": (
                self.verification_context
            )
        }