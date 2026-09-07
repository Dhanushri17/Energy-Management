"""
Runtime prediction wrapper. This is what `interface.py` calls.
"""

import pandas as pd

from ..config import FEATURE_COLUMNS, MODEL_VERSION
from .model_loader import load_model


class PredictionResult:
    def __init__(
        self,
        predicted_power: float | None,
        model_version: str,
        ok: bool,
        reason: str = "",
    ):
        self.predicted_power = predicted_power
        self.model_version = model_version
        self.ok = ok
        self.reason = reason

    def to_dict(self) -> dict:
        return {
            "predicted_power": self.predicted_power,
            "model_version": self.model_version,
        }


class Predictor:
    def __init__(self):
        self._model = None
        self._metadata = None

    def _ensure_loaded(self):
        if self._model is None:
            self._model, self._metadata = load_model()

    def predict(self, features: dict) -> PredictionResult:
        """
        Args:
            features: dict containing at least FEATURE_COLUMNS, already
                      engineered (see features/feature_engineering.py).
        """
        try:
            self._ensure_loaded()
        except Exception as e:
            return PredictionResult(
                None,
                MODEL_VERSION,
                ok=False,
                reason=str(e),
            )

        missing = [c for c in FEATURE_COLUMNS if features.get(c) is None]

        if missing:
            return PredictionResult(
                None,
                MODEL_VERSION,
                ok=False,
                reason=f"missing required features: {missing}",
            )

        row = pd.DataFrame(
            [{c: features[c] for c in FEATURE_COLUMNS}]
        )

        try:
            pred = float(self._model.predict(row)[0])
        except Exception as e:
            return PredictionResult(
                None,
                MODEL_VERSION,
                ok=False,
                reason=str(e),
            )

        return PredictionResult(
            pred,
            MODEL_VERSION,
            ok=True,
        )