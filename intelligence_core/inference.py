"""
Internal orchestration: measurement -> evidence package.

interface.py wraps this in the class the Backend actually calls.

The pipeline is designed to operate offline using local data
and the locally stored ML model.
"""

import pandas as pd

from .config import REQUIRED_FIELDS
from .preprocessing.validation import validate_measurement
from .features.feature_engineering import build_features_from_dataframe
from .models.predict import Predictor
from .anomaly.detector import detect_anomaly
from .evidence.generator import (
    build_evidence_package,
    insufficient_data_package,
)
from .evidence.historical import find_comparable_conditions
from .evidence.future_forecast import FutureForecaster


_predictor = Predictor()
_future_forecaster = FutureForecaster()


def _build_future_conditions(
    measurement: dict,
    history_df: pd.DataFrame = None,
    forecast_steps: int = 4,
    interval_minutes: int = 15,
) -> list[dict]:
    """
    Build future environmental conditions locally.

    The current implementation uses recent historical measurements
    as the source of future environmental conditions.

    The newest available historical observation is mapped to the
    nearest future timestamp, then progressively older observations
    are used for later forecast points.

    This keeps the Intelligence Core completely offline.

    If sufficient historical data is unavailable, an empty list
    is returned and future forecasting is marked unavailable.
    """

    if history_df is None or history_df.empty:
        return []

    required_columns = {
        "timestamp",
        "irradiance",
        "panel_temperature",
    }

    if not required_columns.issubset(history_df.columns):
        return []

    current_timestamp = pd.to_datetime(
        measurement.get("timestamp"),
        errors="coerce",
    )

    if pd.isna(current_timestamp):
        return []

    history = history_df.copy()

    history["timestamp"] = pd.to_datetime(
        history["timestamp"],
        errors="coerce",
    )

    history["irradiance"] = pd.to_numeric(
        history["irradiance"],
        errors="coerce",
    )

    history["panel_temperature"] = pd.to_numeric(
        history["panel_temperature"],
        errors="coerce",
    )

    history = history.dropna(
        subset=[
            "timestamp",
            "irradiance",
            "panel_temperature",
        ]
    )

    # Only use observations before the current measurement.
    # This prevents future-data leakage.
    history = history[
        history["timestamp"] < current_timestamp
    ].copy()

    if history.empty:
        return []

    # ---------------------------------------------------------
    # Use the most recent historical environmental conditions
    # as an offline baseline for future conditions.
    # ---------------------------------------------------------
    history = history.sort_values("timestamp")

    recent = history.tail(forecast_steps)

    if recent.empty:
        return []

    future_conditions = []

    last_timestamp = current_timestamp

    # IMPORTANT:
    # recent is chronological oldest -> newest.
    # For forecasting, the nearest future point should use
    # the newest historical observation first.
    recent_rows = (
        recent
        .sort_values("timestamp", ascending=False)
        .to_dict("records")
    )

    for index in range(forecast_steps):

        source_row = recent_rows[
            index % len(recent_rows)
        ]

        future_timestamp = (
            last_timestamp
            + pd.Timedelta(
                minutes=interval_minutes * (index + 1)
            )
        )

        future_conditions.append(
            {
                "timestamp": future_timestamp,
                "irradiance": float(
                    source_row["irradiance"]
                ),
                "panel_temperature": float(
                    source_row["panel_temperature"]
                ),
            }
        )

    return future_conditions


def run_pipeline(
    measurement: dict,
    history_df: pd.DataFrame = None,
) -> dict:
    """
    Full Intelligence Core pipeline for a single measurement.

    Pipeline:

        validate
            ->
        feature engineering
            ->
        current ML prediction
            ->
        historical comparison
            ->
        anomaly detection
            ->
        future forecast
            ->
        evidence package
    """

    plant_id = measurement.get("plant_id")
    timestamp = measurement.get("timestamp")

    # ---------------------------------------------------------
    # Required-field validation
    # ---------------------------------------------------------
    for field_name in REQUIRED_FIELDS:

        if measurement.get(field_name) is None:

            return insufficient_data_package(
                plant_id,
                timestamp,
                reason=(
                    f"missing required field: "
                    f"{field_name}"
                ),
            )

    # ---------------------------------------------------------
    # Measurement validation
    # ---------------------------------------------------------
    validation_result = validate_measurement(
        measurement
    )

    if validation_result.quality_score() == 0.0:

        return insufficient_data_package(
            plant_id,
            timestamp,
            reason=(
                "no usable measurement fields available"
            ),
        )

    # ---------------------------------------------------------
    # Current prediction
    # ---------------------------------------------------------
    df = pd.DataFrame([measurement])

    df = build_features_from_dataframe(df)

    features = df.iloc[0].to_dict()

    prediction_result = _predictor.predict(
        features
    )

    # ---------------------------------------------------------
    # Prediction failure handling
    # ---------------------------------------------------------
    #
    # The Predictor contract can report an unsuccessful
    # inference through ok=False. Never pass a failed
    # prediction into anomaly detection.
    #
    if not prediction_result.ok:

        reason = (
            getattr(
                prediction_result,
                "reason",
                None,
            )
            or "model inference failed"
        )

        return insufficient_data_package(
            plant_id,
            timestamp,
            reason=reason,
        )

    prediction_dict = prediction_result.to_dict()

    actual_power = measurement.get(
        "ac_power"
    )

    prediction_dict["actual_power"] = actual_power

    # ---------------------------------------------------------
    # Historical comparable-condition intelligence
    # ---------------------------------------------------------
    historical_result = find_comparable_conditions(
        current_measurement=measurement,
        history_df=history_df,
    )

    # ---------------------------------------------------------
    # Current anomaly detection
    # ---------------------------------------------------------
    anomaly = detect_anomaly(
        prediction_result.predicted_power,
        actual_power,
        measurement,
    )

    prediction_dict["deviation_kw"] = (
        anomaly["deviation"]["deviation_kw"]
    )

    prediction_dict["deviation_percent"] = (
        anomaly["deviation"]["deviation_percent"]
    )

    # ---------------------------------------------------------
    # Future forecasting
    # ---------------------------------------------------------
    future_conditions = _build_future_conditions(
        measurement=measurement,
        history_df=history_df,
        forecast_steps=4,
        interval_minutes=15,
    )

    future_forecast = _future_forecaster.forecast(
        future_conditions
    )

    # ---------------------------------------------------------
    # Build final evidence package
    # ---------------------------------------------------------
    package = build_evidence_package(
        plant_id=plant_id,
        timestamp=timestamp,
        measurement=measurement,
        prediction=prediction_dict,
        anomaly=anomaly,
        validation_result=validation_result,
        history_df=history_df,
        historical_result=historical_result,
        future_forecast=future_forecast,
    )

    # ---------------------------------------------------------
    # Add future forecast to evidence package
    # ---------------------------------------------------------
    package["future_forecast"] = future_forecast

    return package