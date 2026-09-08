"""
Public interface — this is the ONLY thing the Backend should import
(spec section 21).

Keep this class's method signature stable; everything underneath it
is free to change.
"""

import pandas as pd

from .inference import run_pipeline


class IntelligenceEngine:
    """
    Public Intelligence Core interface.

    The Backend calls:

        engine = IntelligenceEngine()
        evidence_package = engine.analyze(measurement)

    Input:
        Single measurement dict.

    Output:
        Complete Intelligence Core evidence package.
    """

    def analyze(
        self,
        measurement: dict,
        history_df: pd.DataFrame = None,
    ) -> dict:
        """
        Args:
            measurement:
                Single raw measurement dict from the Backend.

            history_df:
                Optional historical dataframe supplied by the
                Backend/DB layer.

        Returns:
            Complete Intelligence Core output package.
        """

        return run_pipeline(
            measurement,
            history_df=history_df,
        )


class MockIntelligenceEngine:
    """
    Drop-in mock for Backend development.

    IMPORTANT
    ---------
    This mock does not perform real ML or intelligence.

    Its purpose is to provide the same public response shape as
    IntelligenceEngine so the Backend can be developed independently.
    """

    def analyze(
        self,
        measurement: dict,
        history_df: pd.DataFrame = None,
    ) -> dict:

        actual_power = measurement.get(
            "ac_power",
            5.4,
        )

        return {
            "plant_id": measurement.get(
                "plant_id"
            ),

            "timestamp": measurement.get(
                "timestamp"
            ),

            # ==================================================
            # Prediction
            # ==================================================

            "prediction": {
                "predicted_power": 9.2,
                "actual_power": actual_power,
                "deviation_kw": -3.8,
                "deviation_percent": -41.3,
                "model_version": "mock_v0",
            },

            # ==================================================
            # Anomaly
            # ==================================================

            "anomaly": {
                "detected": True,
                "type": "under_generation",
                "severity": "high",
                "score": 0.91,
                "supporting_signals": [
                    "power_deviation",
                ],
            },

            # ==================================================
            # Evidence
            # ==================================================

            "evidence": {

                "environment": {
                    "irradiance": 820,
                    "panel_temperature": 42.1,
                    "status": "normal",
                },

                "historical": {
                    "comparison": "normal",
                    "baseline_output": 8.9,
                    "actual_output": actual_power,
                    "deviation_kw": -3.5,
                    "deviation_percent": -39.33,
                    "match_count": 10,
                    "matches": [],
                },

                "inverter": {
                    "status": "abnormal",
                    "fault_code": None,
                },

                "battery": {
                    "soc": 78,
                    "status": "normal",
                },

                "load": {
                    "power": 2.1,
                    "status": "normal",
                },

                "grid": {
                    "status": "available",
                },

                "energy_balance": {
                    "generated": actual_power,
                    "consumed": 2.1,
                    "imported": 0.0,
                    "exported": 0.0,
                    "stored": 2.0,
                    "imbalance": 1.3,
                    "balance_status": "balanced",
                    "supply_power": actual_power,
                    "demand_power": (
                        2.1 + 2.0 + 1.3
                    ),
                },

                # ==================================================
                # Cause indicators
                # ==================================================

                "cause_indicators": {
                    "power_deviation": {
                        "status": "abnormal",
                        "predicted_power": 9.2,
                        "actual_power": actual_power,
                        "deviation_percent": -41.3,
                    },

                    "environmental": {
                        "irradiance": 820,
                        "panel_temperature": 42.1,
                        "status": "available",
                    },

                    "inverter": {
                        "status": "abnormal",
                        "fault_code": None,
                        "indicator": "abnormal",
                    },

                    "sensor": {
                        "status": "normal",
                        "indicator": "normal",
                    },

                    "grid": {
                        "status": "available",
                        "indicator": "normal",
                    },
                },

                # ==================================================
                # Optimization inputs
                # ==================================================

                "optimization_inputs": {
                    "current_state": {
                        "actual_generation": actual_power,
                        "expected_generation": 9.2,
                        "deviation_kw": -3.8,
                        "deviation_percent": -41.3,
                        "load_power": 2.1,
                        "battery_soc": 78.0,
                        "battery_power": 2.0,
                        "grid_import": 0.0,
                        "grid_export": 0.0,
                        "balance_status": "balanced",
                        "imbalance": 1.3,
                    },

                    "future_state": {
                        "forecast_available": True,
                        "forecast_status": "available",
                        "forecast_points": [
                            {
                                "timestamp": "2026-09-01T10:45:00",
                                "predicted_power": 6.8,
                                "prediction_ok": True,
                                "model_version": "mock_v0",
                            },
                            {
                                "timestamp": "2026-09-01T11:00:00",
                                "predicted_power": 7.2,
                                "prediction_ok": True,
                                "model_version": "mock_v0",
                            },
                        ],
                        "forecast_count": 2,
                    },

                    "constraints": {
                        "status": "within_limits",
                        "violations": [],

                        "battery_constraints_available": True,

                        "battery": {
                            "min_soc_percent": 5.0,
                            "max_soc_percent": 100.0,
                            "max_charge_power_kw": 4.0,
                            "max_discharge_power_kw": 4.0,
                        },

                        "battery_validation": {
                            "status": "within_limits",
                            "violations": [],
                        },

                        "grid_constraints_available": False,

                        "grid": {
                            "max_import_power_kw": None,
                            "max_export_power_kw": None,
                        },

                        "grid_validation": {
                            "status": "unavailable",
                            "violations": [],
                        },

                        "generation_constraints_available": True,

                        "generation": {
                            "max_generation_power_kw": 10.0,
                        },

                        "generation_validation": {
                            "status": "within_limits",
                            "violations": [],
                        },
                    },
                },

                "relevant_calculations": {},
            },

            # ==================================================
            # Future forecast
            # ==================================================

            "future_forecast": {
                "status": "available",
                "forecast": [
                    {
                        "timestamp": "2026-09-01T10:45:00",
                        "irradiance": 750.0,
                        "panel_temperature": 43.0,
                        "predicted_power": 6.8,
                        "model_version": "mock_v0",
                        "prediction_ok": True,
                    },
                    {
                        "timestamp": "2026-09-01T11:00:00",
                        "irradiance": 780.0,
                        "panel_temperature": 43.5,
                        "predicted_power": 7.2,
                        "model_version": "mock_v0",
                        "prediction_ok": True,
                    },
                ],
            },

            # ==================================================
            # Data quality
            # ==================================================

            "data_quality": {
                "missing_fields": [],
                "invalid_fields": [],
                "quality_score": 0.96,
            },
        }