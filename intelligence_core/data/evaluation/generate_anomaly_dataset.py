"""
Generate a controlled anomaly-evaluation dataset.

The original synthetic dataset is never modified.

Anomalies are injected only into valid daytime samples by reducing
observed AC power while keeping environmental conditions unchanged.
"""

from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

SOURCE_FILE = BASE_DIR / "data" / "synthetic.csv"
OUTPUT_FILE = BASE_DIR / "data" / "evaluation" / "anomaly_test.csv"


def generate_dataset(
    anomaly_rate: float = 0.10,
    random_state: int = 42,
) -> pd.DataFrame:

    df = pd.read_csv(SOURCE_FILE)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Only use meaningful daytime generation conditions.
    eligible = df[
        (df["irradiance"] > 200)
        & (df["ac_power"] > 0.3)
    ].copy()

    rng = np.random.default_rng(random_state)

    # Start with every selected sample classified as normal.
    eligible["ground_truth_anomaly"] = False
    eligible["injection_factor"] = 1.0

    anomaly_count = int(len(eligible) * anomaly_rate)

    anomaly_indices = rng.choice(
        eligible.index,
        size=anomaly_count,
        replace=False,
    )

    # Different controlled fault severities.
    factors = rng.choice(
        [0.85, 0.70, 0.50, 0.20],
        size=anomaly_count,
        replace=True,
    )

    eligible.loc[anomaly_indices, "ac_power"] = (
        eligible.loc[anomaly_indices, "ac_power"].to_numpy()
        * factors
    )

    eligible.loc[anomaly_indices, "ground_truth_anomaly"] = True
    eligible.loc[anomaly_indices, "injection_factor"] = factors

    # Keep the dataset ordered chronologically.
    eligible = eligible.sort_values("timestamp").reset_index(drop=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    eligible.to_csv(OUTPUT_FILE, index=False)

    print("Anomaly evaluation dataset created.")
    print(f"Source samples          : {len(df)}")
    print(f"Eligible daytime samples: {len(eligible)}")
    print(f"Injected anomalies      : {anomaly_count}")
    print(f"Normal samples          : {len(eligible) - anomaly_count}")
    print(f"Anomaly rate            : {anomaly_rate:.1%}")
    print(f"Output                  : {OUTPUT_FILE}")

    return eligible


if __name__ == "__main__":
    generate_dataset()