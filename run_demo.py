import pandas as pd

from intelligence_core.interface import IntelligenceEngine


DATA_PATH = "intelligence_core/data/synthetic.csv"


def main():
    print("=" * 60)
    print("        RENEWABLE ENERGY INTELLIGENCE CORE")
    print("=" * 60)

    print("\n[1] Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    print(f"    Dataset loaded: {len(df)} rows")

    measurement = df.iloc[1000].to_dict()

    print("\n[2] Running IntelligenceEngine...")
    engine = IntelligenceEngine()

    result = engine.analyze(
        measurement,
        history_df=df,
    )

    print("\n[3] INTELLIGENCE RESULT")
    print("-" * 60)

    print(f"Plant ID           : {result.get('plant_id')}")
    print(f"Timestamp          : {result.get('timestamp')}")
    print("Pipeline Status    : SUCCESS")

    # ---------------------------------------------------------
    # PREDICTION
    # ---------------------------------------------------------
    prediction = result.get("prediction")

    if prediction:
        actual = measurement.get("ac_power")
        expected = prediction.get("predicted_power")

        print("\nPrediction")
        print(f"  Actual Power     : {actual:.3f}")
        print(f"  Expected Power   : {expected:.3f}")
        print(f"  Model Version    : {prediction.get('model_version')}")

        if expected is not None and actual is not None:
            print(f"  Deviation        : {actual - expected:.3f}")

    # ---------------------------------------------------------
    # ANOMALY DETECTION
    # ---------------------------------------------------------
    anomaly = result.get("anomaly")

    if anomaly:
        print("\nAnomaly Detection")
        print(f"  Detected         : {anomaly.get('detected')}")
        print(f"  Type             : {anomaly.get('type')}")
        print(f"  Severity         : {anomaly.get('severity')}")
        print(f"  Score            : {anomaly.get('score')}")

    # ---------------------------------------------------------
    # DATA QUALITY
    # ---------------------------------------------------------
    data_quality = result.get("data_quality") or {}

    print("\nData Quality")
    print(f"  Quality Score    : {data_quality.get('quality_score')}")
    print(f"  Missing Fields   : {data_quality.get('missing_fields', [])}")
    print(f"  Invalid Fields   : {data_quality.get('invalid_fields', [])}")

    quality_score = data_quality.get("quality_score")

    if quality_score is not None:
        if quality_score >= 0.8:
            quality_status = "GOOD"
        elif quality_score >= 0.5:
            quality_status = "WARNING"
        else:
            quality_status = "POOR"

        print(f"  Quality Status   : {quality_status}")

    # ---------------------------------------------------------
    # HISTORICAL EVIDENCE
    # ---------------------------------------------------------
    evidence = result.get("evidence") or {}

    historical = evidence.get("historical") or {}

    if historical:
        print("\nHistorical Evidence")
        print(f"  Comparison       : {historical.get('comparison')}")
        print(f"  Baseline Output  : {historical.get('baseline_output')}")
        print(f"  Historical Dev.  : {historical.get('deviation_percent')}%")
        print(f"  Match Count      : {historical.get('match_count')}")

    # ---------------------------------------------------------
    # ENERGY BALANCE
    # ---------------------------------------------------------
    energy = evidence.get("energy_balance") or {}

    if energy:
        print("\nEnergy Balance")
        print(f"  Generated        : {energy.get('generated')}")
        print(f"  Consumed         : {energy.get('consumed')}")
        print(f"  Imported         : {energy.get('imported')}")
        print(f"  Exported         : {energy.get('exported')}")
        print(f"  Stored           : {energy.get('stored')}")
        print(f"  Imbalance        : {energy.get('imbalance')}")
        print(f"  Status           : {energy.get('balance_status')}")

    # ---------------------------------------------------------
    # OPERATIONAL CONSTRAINTS
    # ---------------------------------------------------------
    optimization = evidence.get("optimization_inputs") or {}
    constraints = optimization.get("constraints") or {}

    if constraints:
        print("\nOperational Constraints")
        print(f"  Overall Status   : {constraints.get('status')}")
        print(f"  Violations       : {constraints.get('violations')}")

    # ---------------------------------------------------------
    # FUTURE FORECAST
    # ---------------------------------------------------------
    future = result.get("future_forecast") or {}

    if future:
        print("\nFuture Forecast")
        print(f"  Status           : {future.get('status')}")
        print(f"  Forecast Points  : {future.get('forecast_count')}")

        for point in future.get("forecast", []):
            predicted = point.get("predicted_power")

            if predicted is not None:
                print(
                    f"  {point.get('timestamp')} -> "
                    f"{predicted:.3f}"
                )
            else:
                print(
                    f"  {point.get('timestamp')} -> unavailable"
                )

    print("\n" + "=" * 60)
    print("                 DEMO COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()