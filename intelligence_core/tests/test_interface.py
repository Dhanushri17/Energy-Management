import pandas as pd

from intelligence_core.interface import (
    IntelligenceEngine,
    MockIntelligenceEngine,
)
from intelligence_core.inference import _build_future_conditions
from intelligence_core.models.predict import (
    PredictionResult,
    Predictor,
)
from intelligence_core.anomaly.detector import detect_anomaly
from intelligence_core.anomaly.scoring import compute_deviation


def test_spec_section_27_scenario():
    """
    Basic interface contract regression test.
    """

    measurement = {
        "plant_id": "PLANT-001",
        "timestamp": "2026-01-01T12:00:00",
        "irradiance": 800.0,
        "panel_temperature": 35.0,
        "ac_power": 7.0,
        "battery_soc": 50.0,
        "battery_voltage": 400.0,
        "battery_current": 0.0,
        "load_power": 2.0,
        "grid_status": "available",
        "grid_voltage": 230.0,
        "grid_frequency": 50.0,
        "import_power": 0.0,
        "export_power": 5.0,
        "inverter_status": "normal",
        "sensor_status": "normal",
    }

    engine = MockIntelligenceEngine()
    result = engine.analyze(measurement)

    assert isinstance(result, dict)

    assert "plant_id" in result
    assert "timestamp" in result
    assert "prediction" in result
    assert "anomaly" in result
    assert "evidence" in result
    assert "future_forecast" in result
    assert "data_quality" in result


def test_mock_engine_shape():
    """
    Verify that the mock engine follows the same public contract
    expected from the real Intelligence Engine.
    """

    measurement = {
        "plant_id": "PLANT-001",
        "timestamp": "2026-01-01T12:00:00",
        "irradiance": 800.0,
        "panel_temperature": 35.0,
        "ac_power": 7.0,
    }

    engine = MockIntelligenceEngine()
    result = engine.analyze(measurement)

    assert "plant_id" in result
    assert "timestamp" in result
    assert "prediction" in result
    assert "anomaly" in result
    assert "evidence" in result
    assert "future_forecast" in result
    assert "data_quality" in result

    prediction = result["prediction"]

    assert "predicted_power" in prediction
    assert "actual_power" in prediction
    assert "deviation_kw" in prediction
    assert "deviation_percent" in prediction
    assert "model_version" in prediction

    anomaly = result["anomaly"]

    assert "detected" in anomaly
    assert "score" in anomaly
    assert "severity" in anomaly
    assert "type" in anomaly
    assert "supporting_signals" in anomaly

    evidence = result["evidence"]

    assert "environment" in evidence
    assert "historical" in evidence
    assert "inverter" in evidence
    assert "battery" in evidence
    assert "load" in evidence
    assert "grid" in evidence
    assert "energy_balance" in evidence
    assert "cause_indicators" in evidence
    assert "optimization_inputs" in evidence
    assert "relevant_calculations" in evidence

    optimization = evidence["optimization_inputs"]

    assert "current_state" in optimization
    assert "future_state" in optimization
    assert "constraints" in optimization

    constraints = optimization["constraints"]

    assert "status" in constraints
    assert "violations" in constraints
    assert "battery_constraints_available" in constraints
    assert "grid_constraints_available" in constraints
    assert "generation_constraints_available" in constraints

    # Root-cause reasoning belongs to the AI Agent,
    # not the Intelligence Core.
    assert "root_cause" not in result
    assert "root_cause" not in evidence


def test_deviation_edge_cases():
    """
    Verify deviation calculations for normal and edge-case values.
    """

    deviation = compute_deviation(
        predicted=10.0,
        actual=8.0,
    )

    assert deviation["deviation_kw"] == -2.0
    assert deviation["deviation_percent"] == -20.0

    deviation = compute_deviation(
        predicted=10.0,
        actual=10.0,
    )

    assert deviation["deviation_kw"] == 0.0
    assert deviation["deviation_percent"] == 0.0

    deviation = compute_deviation(
        predicted=None,
        actual=10.0,
    )

    assert deviation["deviation_kw"] is None
    assert deviation["deviation_percent"] is None


def test_normal_case_no_anomaly():
    """
    A small deviation should not be classified as an anomaly.
    """

    anomaly = detect_anomaly(
        predicted=6.5,
        actual=6.4,
        measurement={},
    )

    assert anomaly["detected"] is False
    assert anomaly["severity"] == "none"


def test_near_zero_power_not_flagged_as_anomaly():
    """
    Regression test: nighttime/near-zero output should NOT be flagged
    as a critical anomaly just because tiny absolute noise produces a
    huge percentage deviation.

    But a genuine fault where predicted generation is high and actual
    generation is near zero must still be detected.
    """

    deviation = compute_deviation(
        predicted=0.01,
        actual=0.05,
    )

    assert deviation["deviation_percent"] is None

    anomaly = detect_anomaly(
        predicted=0.01,
        actual=0.05,
        measurement={},
    )

    assert anomaly["detected"] is False

    # Genuine fault:
    # predicted generation is high but actual generation is almost zero.
    anomaly = detect_anomaly(
        predicted=6.0,
        actual=0.02,
        measurement={},
    )

    assert anomaly["detected"] is True
    assert anomaly["severity"] in ("high", "critical")


def test_real_engine_returns_optimization_inputs():
    """
    End-to-end regression test for the real Intelligence Engine.

    Verifies that the Intelligence Core produces optimization-ready
    quantitative state without making operational decisions itself.
    """

    df = pd.read_csv(
        "intelligence_core/data/synthetic.csv"
    )

    engine = IntelligenceEngine()

    result = engine.analyze(
        df.iloc[1000].to_dict(),
        history_df=df,
    )

    optimization = result["evidence"]["optimization_inputs"]

    assert "current_state" in optimization
    assert "future_state" in optimization
    assert "constraints" in optimization

    constraints = optimization["constraints"]

    assert constraints["status"] == "within_limits"
    assert constraints["violations"] == []

    assert constraints["battery_constraints_available"] is True
    assert constraints["generation_constraints_available"] is True
    assert constraints["grid_constraints_available"] is False

    assert (
        constraints["battery_validation"]["status"]
        == "within_limits"
    )

    assert (
        constraints["generation_validation"]["status"]
        == "within_limits"
    )

    assert (
        constraints["grid_validation"]["status"]
        == "unavailable"
    )

    assert (
        optimization["future_state"]["forecast_available"]
        is True
    )


def test_prediction_failure_returns_insufficient_data(
    monkeypatch,
):
    """
    Regression test for model inference failure.

    A failed prediction must stop the normal inference pipeline
    and return the standard insufficient-data response.
    """

    def fake_predict(self, features):
        return PredictionResult(
            predicted_power=None,
            model_version="test_failure",
            ok=False,
            reason="simulated model failure",
        )

    monkeypatch.setattr(
        Predictor,
        "predict",
        fake_predict,
    )

    measurement = {
        "plant_id": "PLANT-001",
        "timestamp": "2026-01-01T12:00:00",
        "irradiance": 800.0,
        "panel_temperature": 35.0,
        "ac_power": 7.0,
    }

    engine = IntelligenceEngine()
    result = engine.analyze(measurement)

    # Verify the standard failure contract.
    assert result["status"] == "insufficient_data"

    assert (
        result["reason"]
        == "simulated model failure"
    )

    # A failed prediction must not produce a
    # normal prediction or anomaly result.
    assert result["prediction"] is None
    assert result["anomaly"] is None

    # Evidence generation must not continue after
    # model inference failure.
    assert result["evidence"] == {}

    # Data quality explicitly marks the package incomplete.
    assert result["data_quality"]["complete"] is False


def test_future_forecast_uses_newest_condition_first():
    """
    Regression test for future-condition ordering.

    The newest historical observation must be mapped to the
    nearest future timestamp.
    """

    history = pd.DataFrame(
        [
            {
                "timestamp": "2026-01-01 11:00:00",
                "irradiance": 500.0,
                "panel_temperature": 30.0,
            },
            {
                "timestamp": "2026-01-01 11:15:00",
                "irradiance": 600.0,
                "panel_temperature": 31.0,
            },
            {
                "timestamp": "2026-01-01 11:30:00",
                "irradiance": 700.0,
                "panel_temperature": 32.0,
            },
        ]
    )

    measurement = {
        "plant_id": "PLANT-001",
        "timestamp": "2026-01-01 11:45:00",
        "irradiance": 750.0,
        "panel_temperature": 33.0,
        "ac_power": 6.0,
    }

    conditions = _build_future_conditions(
        measurement=measurement,
        history_df=history,
        forecast_steps=3,
        interval_minutes=15,
    )

    assert len(conditions) == 3

    # Newest historical condition -> nearest future point.
    assert conditions[0]["irradiance"] == 700.0
    assert conditions[0]["panel_temperature"] == 32.0

    # Next-newest historical condition -> second future point.
    assert conditions[1]["irradiance"] == 600.0
    assert conditions[1]["panel_temperature"] == 31.0

    # Oldest historical condition -> third future point.
    assert conditions[2]["irradiance"] == 500.0
    assert conditions[2]["panel_temperature"] == 30.0

    # Verify future timestamps are correctly spaced.
    assert conditions[0]["timestamp"] == pd.Timestamp(
        "2026-01-01 12:00:00"
    )

    assert conditions[1]["timestamp"] == pd.Timestamp(
        "2026-01-01 12:15:00"
    )

    assert conditions[2]["timestamp"] == pd.Timestamp(
        "2026-01-01 12:30:00"
    )