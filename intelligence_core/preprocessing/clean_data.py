"""
Cleaning and normalization for raw measurement data.

This module is intentionally simple to start. Fill in real logic once
you've explored the actual dataset in Phase 1.
"""

import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply baseline cleaning to a time-series dataframe of measurements.

    Steps (expand as needed once you've profiled the real data):
        1. Parse/align timestamps
        2. Drop exact duplicate rows
        3. Sort chronologically
        4. Leave missing values as NaN (do NOT fill with fabricated values —
           that decision belongs to feature engineering / evidence layer,
           and must be documented, not silently imputed).
    """
    df = df.copy()

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])
        df = df.sort_values("timestamp")

    df = df.drop_duplicates()

    return df.reset_index(drop=True)


def resample(df: pd.DataFrame, freq: str = "15min") -> pd.DataFrame:
    """
    Resample to a fixed frequency. Useful once you know the real sampling
    interval of the sensors (don't guess — confirm with the backend team).
    """
    if "timestamp" not in df.columns:
        raise ValueError("resample() requires a 'timestamp' column")

    return (
        df.set_index("timestamp")
        .resample(freq)
        .mean(numeric_only=True)
        .reset_index()
    )


def remove_outliers_iqr(df: pd.DataFrame, column: str, k: float = 1.5) -> pd.DataFrame:
    """
    Basic IQR-based outlier filter for a single column.
    Only use this after you understand whether extreme values are sensor
    noise vs. real physical events (e.g. a genuine power spike is not noise).
    """
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    mask = df[column].between(lower, upper) | df[column].isna()
    return df[mask].reset_index(drop=True)
