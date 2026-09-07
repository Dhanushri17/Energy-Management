"""
Train the solar power forecasting model.

Training is an offline/development operation.

Pipeline:

Historical Data
    ↓
Cleaning + Feature Engineering
    ↓
Time-based Train/Test Split
    ↓
Random Forest Training
    ↓
Evaluation
    ↓
Model Artifact + Metadata
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import joblib
from sklearn.ensemble import RandomForestRegressor


# ============================================================
# MAKE PROJECT PACKAGE AVAILABLE
# ============================================================

PROJECT_PACKAGE = Path(__file__).resolve().parents[1]

sys.path.append(str(PROJECT_PACKAGE))


# ============================================================
# PROJECT IMPORTS
# ============================================================

from config import (
    FEATURE_COLUMNS,
    MODEL_ARTIFACT_PATH,
    MODEL_VERSION,
    TARGET_COLUMN,
)

from evaluation.prediction_metrics import evaluate_predictions

from features.feature_engineering import build_features


# ============================================================
# TRAIN MODEL
# ============================================================

def train(data_path: str, model_out: str | None = None) -> dict:

    print("=" * 60)
    print("SOLAR ML MODEL TRAINING")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. BUILD FEATURES
    # --------------------------------------------------------

    print("\n[1/6] Loading and preparing data...")

    X, y = build_features(data_path)

    print(f"Total samples : {len(X)}")
    print(f"Features      : {list(X.columns)}")
    print(f"Target        : {TARGET_COLUMN}")


    # --------------------------------------------------------
    # 2. VALIDATE FEATURES
    # --------------------------------------------------------

    print("\n[2/6] Validating features...")

    missing_features = [
        column
        for column in FEATURE_COLUMNS
        if column not in X.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    X = X[FEATURE_COLUMNS]

    # Remove rows where ML inputs or target are missing
    valid_mask = X.notna().all(axis=1) & y.notna()

    X = X.loc[valid_mask].reset_index(drop=True)
    y = y.loc[valid_mask].reset_index(drop=True)

    print(f"Valid samples : {len(X)}")


    # --------------------------------------------------------
    # 3. TIME-BASED TRAIN / TEST SPLIT
    # --------------------------------------------------------

    print("\n[3/6] Splitting data chronologically...")

    split_index = int(len(X) * 0.80)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    print(f"Training samples : {len(X_train)}")
    print(f"Testing samples  : {len(X_test)}")


    # --------------------------------------------------------
    # 4. TRAIN RANDOM FOREST
    # --------------------------------------------------------

    print("\n[4/6] Training Random Forest...")

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    print("Model training complete.")


    # --------------------------------------------------------
    # 5. EVALUATE MODEL
    # --------------------------------------------------------

    print("\n[5/6] Evaluating model...")

    y_pred = model.predict(X_test)

    metrics = evaluate_predictions(
        y_test.to_numpy(),
        y_pred
    )

    print("\nMODEL PERFORMANCE")
    print("-" * 60)
    print(json.dumps(metrics, indent=2))


    # --------------------------------------------------------
    # 6. SAVE MODEL + METADATA
    # --------------------------------------------------------

    print("\n[6/6] Saving model...")

    artifact_path = (
        Path(model_out)
        if model_out
        else MODEL_ARTIFACT_PATH
    )

    artifact_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save trained model
    joblib.dump(model, artifact_path)

    # Save model metadata
    metadata = {
        "model_version": MODEL_VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "model_type": "RandomForestRegressor",
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "n_train_samples": len(X_train),
        "n_test_samples": len(X_test),
        "metrics": metrics,
    }

    metadata_path = artifact_path.with_suffix(
        ".metadata.json"
    )

    with open(metadata_path, "w", encoding="utf-8") as file:
        json.dump(
            metadata,
            file,
            indent=2
        )

    print(f"\nModel saved to:")
    print(artifact_path)

    print(f"\nMetadata saved to:")
    print(metadata_path)

    print("\n" + "=" * 60)
    print("MODEL TRAINING COMPLETE")
    print("=" * 60)

    return metadata


# ============================================================
# COMMAND LINE ENTRY POINT
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Train solar power forecasting model."
    )

    parser.add_argument(
        "--data",
        required=True,
        help="Path to historical CSV dataset."
    )

    parser.add_argument(
        "--out",
        required=False,
        help="Optional output path for trained model."
    )

    args = parser.parse_args()

    train(
        data_path=args.data,
        model_out=args.out
    )