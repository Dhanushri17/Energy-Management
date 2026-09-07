class PredictionModel:
    """
    Prediction model interface.

    This class provides the prediction interface used by
    the Intelligence Core.

    The current implementation is a temporary baseline.
    It will later be replaced by the trained ML model
    without changing the Intelligence Core or Backend.
    """

    def predict(
        self,
        irradiance: float,
        temperature: float,
    ) -> float:
        """
        Predict solar power generation.

        Temporary baseline implementation.
        """

        predicted_power = irradiance * 4.2

        return round(predicted_power, 2)


# Create a single prediction model instance
prediction_model = PredictionModel()


def predict_power(
    irradiance: float,
    temperature: float,
) -> float:
    """
    Public prediction interface used by the Intelligence Core.
    """

    return prediction_model.predict(
        irradiance=irradiance,
        temperature=temperature,
    )