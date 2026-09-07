from backend.app.ml.intelligence_core import IntelligenceCore


# Create the Intelligence Core instance
intelligence_core = IntelligenceCore()


def run_intelligence_engine(
    measurement_data: dict,
    historical_data: list[dict] | None = None,
) -> dict:
    """
    Backend adapter for the Intelligence Core.

    The backend does not perform prediction, anomaly detection,
    quantitative analysis, or historical analysis.

    It only passes current and historical measurement data
    to the Intelligence Core.
    """

    return intelligence_core.analyze(
        measurement_data=measurement_data,
        historical_data=historical_data,
    )