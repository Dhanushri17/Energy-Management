from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


# ---------------------------------------------------------
# Similarity weights
# ---------------------------------------------------------
# For solar generation, irradiance has the strongest influence
# on comparable-condition matching.
IRRADIANCE_WEIGHT = 0.50
TEMPERATURE_WEIGHT = 0.30
TIME_WEIGHT = 0.20


def compute_baseline(
    history_df: pd.DataFrame,
    target_column: str = "ac_power",
) -> dict[str, Any]:
    """
    Compute a simple statistical baseline from historical data.
    """

    if history_df is None or history_df.empty:
        return {
            "mean": None,
            "median": None,
            "std": None,
            "n_samples": 0,
            "insufficient_data": True,
        }

    if target_column not in history_df.columns:
        return {
            "mean": None,
            "median": None,
            "std": None,
            "n_samples": 0,
            "insufficient_data": True,
        }

    values = pd.to_numeric(
        history_df[target_column],
        errors="coerce",
    ).dropna()

    if values.empty:
        return {
            "mean": None,
            "median": None,
            "std": None,
            "n_samples": 0,
            "insufficient_data": True,
        }

    return {
        "mean": float(values.mean()),
        "median": float(values.median()),
        "std": float(values.std()) if len(values) > 1 else 0.0,
        "n_samples": int(len(values)),
        "insufficient_data": False,
    }


def compare_to_baseline(
    current_value: float,
    baseline: dict[str, Any],
) -> dict[str, Any]:
    """
    Compare the current output against a historical baseline.
    """

    if current_value is None:
        return {
            "status": "insufficient_data",
            "z_score": None,
            "difference": None,
        }

    median = baseline.get("median")
    std = baseline.get("std")

    if median is None:
        return {
            "status": "insufficient_data",
            "z_score": None,
            "difference": None,
        }

    difference = float(current_value - median)

    if std is None or std == 0:
        return {
            "status": "normal" if difference == 0 else "unusual",
            "z_score": None,
            "difference": difference,
        }

    z_score = difference / std

    return {
        "status": "unusual" if abs(z_score) > 2 else "normal",
        "z_score": float(z_score),
        "difference": difference,
    }


def _time_difference_hours(
    hour_a: float,
    hour_b: float,
) -> float:
    """
    Calculate circular time-of-day difference.

    Example:
    23:00 and 01:00 are 2 hours apart,
    not 22 hours apart.
    """

    difference = abs(hour_a - hour_b)

    return min(
        difference,
        24.0 - difference,
    )


def find_comparable_conditions(
    current_measurement: dict[str, Any],
    history_df: pd.DataFrame,
    irradiance_tolerance: float = 0.15,
    temperature_tolerance: float = 0.15,
    time_tolerance_hours: float = 2.0,
    max_matches: int = 10,
) -> dict[str, Any]:
    """
    Find historical observations that occurred under conditions
    comparable to the current measurement.

    Matching dimensions:
        - Irradiance
        - Panel temperature
        - Time of day

    Important:
        Only historical observations strictly before the current
        timestamp are considered. This prevents future-data leakage.

    Similarity weighting:
        Irradiance       = 50%
        Temperature      = 30%
        Time of day      = 20%
    """

    required_columns = {
        "irradiance",
        "panel_temperature",
        "ac_power",
        "timestamp",
    }

    # ---------------------------------------------------------
    # Validate history
    # ---------------------------------------------------------
    if history_df is None or history_df.empty:
        return {
            "comparison": "insufficient_historical_data",
            "match_count": 0,
            "baseline_output": None,
            "actual_output": current_measurement.get("ac_power"),
            "deviation_kw": None,
            "deviation_percent": None,
            "matches": [],
        }

    missing_columns = required_columns - set(history_df.columns)

    if missing_columns:
        return {
            "comparison": "insufficient_historical_data",
            "match_count": 0,
            "baseline_output": None,
            "actual_output": current_measurement.get("ac_power"),
            "deviation_kw": None,
            "deviation_percent": None,
            "matches": [],
        }

    # ---------------------------------------------------------
    # Current measurement values
    # ---------------------------------------------------------
    try:
        current_irradiance = float(
            current_measurement["irradiance"]
        )

        current_temperature = float(
            current_measurement["panel_temperature"]
        )

    except (KeyError, TypeError, ValueError):
        return {
            "comparison": "insufficient_current_conditions",
            "match_count": 0,
            "baseline_output": None,
            "actual_output": current_measurement.get("ac_power"),
            "deviation_kw": None,
            "deviation_percent": None,
            "matches": [],
        }

    current_timestamp = pd.to_datetime(
        current_measurement.get("timestamp"),
        errors="coerce",
    )

    if pd.isna(current_timestamp):
        return {
            "comparison": "insufficient_current_timestamp",
            "match_count": 0,
            "baseline_output": None,
            "actual_output": current_measurement.get("ac_power"),
            "deviation_kw": None,
            "deviation_percent": None,
            "matches": [],
        }

    current_hour = (
        current_timestamp.hour
        + current_timestamp.minute / 60.0
        + current_timestamp.second / 3600.0
    )

    # ---------------------------------------------------------
    # Prepare historical data
    # ---------------------------------------------------------
    df = history_df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    df["irradiance"] = pd.to_numeric(
        df["irradiance"],
        errors="coerce",
    )

    df["panel_temperature"] = pd.to_numeric(
        df["panel_temperature"],
        errors="coerce",
    )

    df["ac_power"] = pd.to_numeric(
        df["ac_power"],
        errors="coerce",
    )

    # Remove incomplete historical observations.
    df = df.dropna(
        subset=[
            "timestamp",
            "irradiance",
            "panel_temperature",
            "ac_power",
        ]
    )

    # ---------------------------------------------------------
    # Prevent future-data leakage
    # ---------------------------------------------------------
    df = df[
        df["timestamp"] < current_timestamp
    ].copy()

    if df.empty:
        return {
            "comparison": "no_comparable_conditions",
            "match_count": 0,
            "baseline_output": None,
            "actual_output": current_measurement.get("ac_power"),
            "deviation_kw": None,
            "deviation_percent": None,
            "matches": [],
        }

    # ---------------------------------------------------------
    # Find comparable observations
    # ---------------------------------------------------------
    matches = []

    for _, row in df.iterrows():

        historical_irradiance = float(
            row["irradiance"]
        )

        historical_temperature = float(
            row["panel_temperature"]
        )

        historical_timestamp = row["timestamp"]

        historical_hour = (
            historical_timestamp.hour
            + historical_timestamp.minute / 60.0
            + historical_timestamp.second / 3600.0
        )

        # ---------------------------------------------
        # Raw differences
        # ---------------------------------------------
        irradiance_difference = abs(
            historical_irradiance - current_irradiance
        )

        temperature_difference = abs(
            historical_temperature - current_temperature
        )

        time_difference_hours = _time_difference_hours(
            current_hour,
            historical_hour,
        )

        # ---------------------------------------------
        # Tolerance filtering
        # ---------------------------------------------
        irradiance_limit = max(
            abs(current_irradiance)
            * irradiance_tolerance,
            1e-9,
        )

        temperature_limit = max(
            abs(current_temperature)
            * temperature_tolerance,
            1e-9,
        )

        if irradiance_difference > irradiance_limit:
            continue

        if temperature_difference > temperature_limit:
            continue

        if time_difference_hours > time_tolerance_hours:
            continue

        # ---------------------------------------------
        # Normalize each distance
        # ---------------------------------------------
        irradiance_distance = min(
            irradiance_difference
            / irradiance_limit,
            1.0,
        )

        temperature_distance = min(
            temperature_difference
            / temperature_limit,
            1.0,
        )

        time_distance = min(
            time_difference_hours
            / time_tolerance_hours,
            1.0,
        )

        # ---------------------------------------------
        # Weighted condition distance
        # ---------------------------------------------
        condition_distance = (
            IRRADIANCE_WEIGHT
            * irradiance_distance
            + TEMPERATURE_WEIGHT
            * temperature_distance
            + TIME_WEIGHT
            * time_distance
        )

        # ---------------------------------------------
        # Convert distance into similarity score
        # ---------------------------------------------
        similarity_score = (
            1.0 - condition_distance
        ) * 100.0

        matches.append(
            {
                "timestamp": historical_timestamp,
                "irradiance": historical_irradiance,
                "panel_temperature": historical_temperature,
                "ac_power": float(row["ac_power"]),

                # Explainable matching evidence
                "irradiance_difference": float(
                    irradiance_difference
                ),
                "temperature_difference": float(
                    temperature_difference
                ),
                "time_difference_hours": float(
                    time_difference_hours
                ),

                # Overall matching metrics
                "condition_distance": float(
                    condition_distance
                ),
                "similarity_score": float(
                    similarity_score
                ),
            }
        )

    # ---------------------------------------------------------
    # No matches
    # ---------------------------------------------------------
    if not matches:
        return {
            "comparison": "no_comparable_conditions",
            "match_count": 0,
            "baseline_output": None,
            "actual_output": current_measurement.get("ac_power"),
            "deviation_kw": None,
            "deviation_percent": None,
            "matches": [],
        }

    # ---------------------------------------------------------
    # Rank by best similarity
    # ---------------------------------------------------------
    matches.sort(
        key=lambda item: item["condition_distance"]
    )

    matches = matches[:max_matches]

    # ---------------------------------------------------------
    # Historical baseline
    # ---------------------------------------------------------
    comparable_outputs = [
        match["ac_power"]
        for match in matches
    ]

    baseline_output = float(
        np.median(comparable_outputs)
    )

    # ---------------------------------------------------------
    # Determine actual output
    # ---------------------------------------------------------
    actual_output = current_measurement.get(
        "ac_power"
    )

    if actual_output is None:
        current_rows = history_df[
            pd.to_datetime(
                history_df["timestamp"],
                errors="coerce",
            )
            == current_timestamp
        ]

        if not current_rows.empty:
            actual_output = current_rows.iloc[0][
                "ac_power"
            ]

    try:
        actual_output = float(actual_output)
    except (TypeError, ValueError):
        actual_output = None

    # ---------------------------------------------------------
    # Historical deviation
    # ---------------------------------------------------------
    deviation_kw = None
    deviation_percent = None

    if actual_output is not None:
        deviation_kw = (
            actual_output
            - baseline_output
        )

        if abs(baseline_output) > 1e-9:
            deviation_percent = (
                deviation_kw
                / abs(baseline_output)
            ) * 100.0

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------
    return {
        "comparison": "available",
        "match_count": len(matches),
        "baseline_output": baseline_output,
        "actual_output": actual_output,
        "deviation_kw": (
            float(deviation_kw)
            if deviation_kw is not None
            else None
        ),
        "deviation_percent": (
            float(deviation_percent)
            if deviation_percent is not None
            else None
        ),
        "matches": matches,
    }