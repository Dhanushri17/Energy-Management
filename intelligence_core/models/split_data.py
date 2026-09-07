import pandas as pd
from pathlib import Path
import sys


# ============================================================
# SOLAR INTELLIGENCE CORE
# TIME-BASED TRAIN / TEST SPLIT
# ============================================================


# ------------------------------------------------------------
# 1. MAKE PROJECT MODULES AVAILABLE
# ------------------------------------------------------------

PROJECT_PACKAGE = Path(__file__).resolve().parents[1]

sys.path.append(str(PROJECT_PACKAGE))


# ------------------------------------------------------------
# 2. IMPORT FEATURE PIPELINE
# ------------------------------------------------------------

from features.feature_engineering import build_features


# ------------------------------------------------------------
# 3. BUILD TRAIN / TEST DATA
# ------------------------------------------------------------

def split_data(test_size: float = 0.20):
    """
    Split time-series data chronologically.

    The earlier observations are used for training.
    The later observations are used for testing.

    Args:
        test_size: Fraction of data reserved for testing.

    Returns:
        X_train
        X_test
        y_train
        y_test
    """

    # Get model-ready features and target
    X, y = build_features()

    # Calculate split position
    split_index = int(len(X) * (1 - test_size))

    # Chronological split
    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    return X_train, X_test, y_train, y_test


# ------------------------------------------------------------
# 4. TEST THE SPLIT
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("SOLAR TIME-SERIES TRAIN / TEST SPLIT")
    print("=" * 60)

    X_train, X_test, y_train, y_test = split_data()

    print("\nTRAINING DATA")
    print("-" * 60)

    print(f"X_train shape : {X_train.shape}")
    print(f"y_train shape : {y_train.shape}")

    print("\nTESTING DATA")
    print("-" * 60)

    print(f"X_test shape  : {X_test.shape}")
    print(f"y_test shape  : {y_test.shape}")

    print("\nFEATURES")
    print("-" * 60)

    print(list(X_train.columns))

    print("\nFIRST TRAINING TIMESTAMP")
    print("-" * 60)

    # Timestamp isn't inside X, so we report row positions instead.
    print(f"Training rows: 0 → {len(X_train) - 1}")

    print("\nTESTING STARTS AFTER TRAINING DATA")

    print("\n" + "=" * 60)
    print("TRAIN / TEST SPLIT COMPLETE")
    print("=" * 60)