"""
Feature engineering for renewable-energy ML models.

This module provides the shared feature transformation used by:

    Training
        ↓
    Runtime inference

The transformation logic must remain identical between
training and inference to avoid feature mismatch.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


# ============================================================
# MAKE PROJECT PACKAGE AVAILABLE
# ============================================================

PROJECT_PACKAGE = Path(__file__).resolve().parents[1]

sys.path.append(str(PROJECT_PACKAGE))


# ============================================================
# PROJECT IMPORTS
# ============================================================

from preprocessing.clean_data import clean_dataframe


# ============================================================
# DEFAULT DATASET
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "synthetic.csv"
)


# ============================================================
# ML SCHEMA
# ============================================================

FEATURE_COLUMNS = [
    "irradiance",
    "panel_temperature",
    "hour",
    "day_of_year",
]

TARGET_COLUMN = "ac_power"


# ============================================================
# TIMESTAMP TRANSFORMATION
# ============================================================

def convert_timestamp(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Convert timestamp column to pandas datetime.
    """

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    return df


# ============================================================
# TIME FEATURES
# ============================================================

def create_time_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create time-based features used by the ML model.
    """

    df = df.copy()

    df["hour"] = (
        df["timestamp"].dt.hour
    )

    df["day_of_year"] = (
        df["timestamp"].dt.dayofyear
    )

    return df


# ============================================================
# SHARED TRANSFORMATION PIPELINE
# ============================================================

def transform_dataframe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clean and transform an existing dataframe
    into ML-ready features.

    This function is shared by training and
    runtime inference.
    """

    df = clean_dataframe(df)

    df = convert_timestamp(df)

    df = create_time_features(df)

    return df


# ============================================================
# FEATURE / TARGET SELECTION
# ============================================================

def select_features(
    df: pd.DataFrame,
):
    """
    Select ML features and target.
    """

    X = df[FEATURE_COLUMNS]

    y = df[TARGET_COLUMN]

    return X, y


# ============================================================
# TRAINING FEATURE PIPELINE
# ============================================================

def build_features(
    data_path: str | Path | None = None,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Build training features from a dataset.

    Parameters
    ----------
    data_path:
        Optional path to the training dataset.

        If omitted, the default synthetic dataset
        is used.

    Returns
    -------
    X:
        ML feature dataframe.

    y:
        Target series.
    """

    dataset_path = (
        Path(data_path)
        if data_path is not None
        else DATA_FILE
    )

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Training dataset not found: {dataset_path}"
        )

    df = pd.read_csv(
        dataset_path
    )

    df = transform_dataframe(df)

    X, y = select_features(df)

    return X, y


# ============================================================
# RUNTIME FEATURE PIPELINE
# ============================================================

def build_features_from_dataframe(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transform an incoming measurement dataframe
    for runtime inference.
    """

    return transform_dataframe(df)


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    X, y = build_features()

    print("Features:")
    print(X.head())

    print(
        "\nFeature shape:",
        X.shape,
    )

    print("\nTarget:")
    print(y.head())

    print(
        "\nTarget shape:",
        y.shape,
    )