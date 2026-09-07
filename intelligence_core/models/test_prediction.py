from intelligence_core.models.predict import Predictor


def main():
    predictor = Predictor()

    features = {
        "irradiance": 650.0,
        "panel_temperature": 30.0,
        "hour": 12,
        "day_of_year": 150,
    }

    result = predictor.predict(features)

    print("\n=== RUNTIME PREDICTION TEST ===")
    print("Prediction successful:", result.ok)
    print("Predicted power:", result.predicted_power)
    print("Model version:", result.model_version)

    if not result.ok:
        print("Reason:", result.reason)


if __name__ == "__main__":
    main()