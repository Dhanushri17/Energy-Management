"""
Loads a local model artifact for inference.

No downloading models at runtime — this only ever reads from disk
(spec section 19).
"""

import json
from pathlib import Path

import joblib

import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from config import MODEL_ARTIFACT_PATH


class ModelLoadError(Exception):
    pass


def load_model(path: Path = None):
    """
    Load the trained model artifact + its metadata.

    Raises:
        ModelLoadError if the artifact is missing or corrupt.
    """
    artifact_path = Path(path) if path else MODEL_ARTIFACT_PATH

    if not artifact_path.exists():
        raise ModelLoadError(
            f"No model artifact found at {artifact_path}. "
            "Run `python -m models.train --data <path>` first."
        )

    try:
        model = joblib.load(artifact_path)
    except Exception as e:
        raise ModelLoadError(f"Failed to load model artifact: {e}") from e

    metadata = {}
    metadata_path = artifact_path.with_suffix(".metadata.json")
    if metadata_path.exists():
        with open(metadata_path) as f:
            metadata = json.load(f)

    return model, metadata
