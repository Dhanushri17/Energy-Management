from backend.app.agent.agent import DiagnosisAgent


# Create the Diagnosis Agent instance
diagnosis_agent = DiagnosisAgent()


def run_diagnosis_engine(evidence_package: dict) -> dict:
    """
    Backend adapter for the Diagnosis Agent.

    The backend does not perform diagnosis, root-cause analysis,
    confidence calculation, or recommendation generation.

    It only passes the Intelligence Core evidence package
    to the Diagnosis Agent and returns the diagnosis result.
    """

    return diagnosis_agent.analyze(
        evidence_package
    )