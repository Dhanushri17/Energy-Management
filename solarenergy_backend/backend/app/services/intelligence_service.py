import pandas as pd

from intelligence_core.interface import IntelligenceEngine


intelligence_engine = IntelligenceEngine()


def _map_measurement_to_core(measurement_data: dict) -> dict:
    """
    Convert the Backend measurement contract into the
    Intelligence Core measurement contract.
    """

    core_measurement = dict(measurement_data)

    if "panel_temperature" not in core_measurement:
        core_measurement["panel_temperature"] = core_measurement.get(
            "temperature"
        )

    return core_measurement


def _map_history_to_core(
    historical_data: list[dict] | None,
) -> pd.DataFrame | None:
    """
    Convert Backend historical records into the DataFrame
    expected by the Intelligence Core.
    """

    if not historical_data:
        return None

    history_df = pd.DataFrame(historical_data)

    if (
        "panel_temperature" not in history_df.columns
        and "temperature" in history_df.columns
    ):
        history_df["panel_temperature"] = history_df["temperature"]

    return history_df


def _map_core_output_to_backend(
    core_result: dict,
) -> dict:
    """
    Convert the Intelligence Core output into the response
    structure currently expected by the Backend.
    """

    prediction = core_result.get("prediction") or {}

    backend_result = dict(core_result)

    backend_result["predicted_power"] = prediction.get(
        "predicted_power"
    )
    backend_result["actual_power"] = prediction.get(
        "actual_power"
    )
    backend_result["deviation_percent"] = prediction.get(
        "deviation_percent"
    )

    backend_result["severity"] = (
        (core_result.get("anomaly") or {}).get("severity")
    )

    backend_result["historical_comparison"] = (
        (core_result.get("evidence") or {}).get("historical")
    )

    backend_result["quantitative_analysis"] = {
        "prediction_accuracy_percent": (
            100
            - abs(prediction.get("deviation_percent", 0))
            if prediction.get("deviation_percent") is not None
            else None
        )
    }

    return backend_result


def run_intelligence_engine(
    measurement_data: dict,
    historical_data: list[dict] | None = None,
) -> dict:
    """
    Run the Intelligence Core through its stable public interface.

    Backend owns database access.
    This adapter translates Backend input/output contracts.
    """

    core_measurement = _map_measurement_to_core(
        measurement_data
    )

    history_df = _map_history_to_core(
        historical_data
    )

    core_result = intelligence_engine.analyze(
        measurement=core_measurement,
        history_df=history_df,
    )

    return _map_core_output_to_backend(
        core_result
    )