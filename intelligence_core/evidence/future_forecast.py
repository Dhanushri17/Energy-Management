"""
Future generation forecasting.

Uses the existing trained solar power model to predict expected
generation for future timestamps based on forecasted environmental
conditions.

This module is intentionally separate from the single-measurement
Predictor so the existing runtime inference path remains stable.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from ..models.predict import Predictor


class FutureForecaster:
    """
    Generates future expected-generation forecasts using the
    existing trained ML model.
    """

    def __init__(self):
        self._predictor = Predictor()

    def forecast(
        self,
        future_conditions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Generate expected power for a sequence of future conditions.

        Each condition should contain:

            timestamp
            irradiance
            panel_temperature

        The remaining time-based features are generated automatically.
        """

        if not future_conditions:
            return {
                "status": "insufficient_data",
                "forecast": [],
                "forecast_count": 0,
            }

        rows = []

        for condition in future_conditions:

            timestamp = pd.to_datetime(
                condition.get("timestamp"),
                errors="coerce",
            )

            if pd.isna(timestamp):
                continue

            try:
                irradiance = float(
                    condition["irradiance"]
                )

                panel_temperature = float(
                    condition["panel_temperature"]
                )

            except (KeyError, TypeError, ValueError):
                continue

            rows.append(
                {
                    "timestamp": timestamp,
                    "irradiance": irradiance,
                    "panel_temperature": panel_temperature,
                }
            )

        if not rows:
            return {
                "status": "insufficient_data",
                "forecast": [],
                "forecast_count": 0,
            }

        forecast_df = pd.DataFrame(rows)

        # Create the same time-based features used during
        # model training.
        forecast_df["hour"] = (
            forecast_df["timestamp"].dt.hour
            + forecast_df["timestamp"].dt.minute / 60.0
        )

        forecast_df["day_of_year"] = (
            forecast_df["timestamp"].dt.dayofyear
        )

        forecast = []

        for _, row in forecast_df.iterrows():

            features = {
                "irradiance": float(
                    row["irradiance"]
                ),
                "panel_temperature": float(
                    row["panel_temperature"]
                ),
                "hour": float(
                    row["hour"]
                ),
                "day_of_year": int(
                    row["day_of_year"]
                ),
            }

            prediction = self._predictor.predict(
                features
            )

            forecast.append(
                {
                    "timestamp": row["timestamp"].isoformat(),
                    "irradiance": features["irradiance"],
                    "panel_temperature": features[
                        "panel_temperature"
                    ],
                    "predicted_power": prediction.predicted_power,
                    "model_version": prediction.model_version,
                    "prediction_ok": prediction.ok,
                    "reason": prediction.reason,
                }
            )

        successful_predictions = [
            item
            for item in forecast
            if item["prediction_ok"]
        ]

        return {
            "status": (
                "available"
                if successful_predictions
                else "prediction_failed"
            ),
            "forecast": forecast,
            "forecast_count": len(forecast),
        }