"""
Run the Intelligent Core against the controlled anomaly
evaluation dataset and calculate detection metrics.
"""

from pathlib import Path

import pandas as pd

from intelligence_core.interface import IntelligenceEngine
from intelligence_core.evaluation.anomaly_metrics import (
    evaluate_anomaly_detection,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "intelligence_core"
    / "data"
    / "evaluation"
    / "anomaly_test.csv"
)


def run_evaluation():
    """Run the complete Intelligent Core on the evaluation dataset."""

    df = pd.read_csv(DATA_FILE)

    engine = IntelligenceEngine()

    y_true = []
    y_pred = []

    print("=" * 60)
    print("INTELLIGENT CORE - ANOMALY EVALUATION")
    print("=" * 60)
    print(f"Evaluation samples: {len(df)}")
    print()

    for index, row in df.iterrows():

        # Convert the dataset row into a production-style measurement.
        measurement = row.to_dict()

        # These columns exist ONLY for evaluation.
        measurement.pop("ground_truth_anomaly", None)
        measurement.pop("injection_factor", None)

        result = engine.analyze(measurement)

        actual_anomaly = bool(row["ground_truth_anomaly"])
        detected_anomaly = bool(result["anomaly"]["detected"])

        y_true.append(actual_anomaly)
        y_pred.append(detected_anomaly)

        if (index + 1) % 100 == 0:
            print(f"Processed: {index + 1}/{len(df)}")

    metrics = evaluate_anomaly_detection(
        y_true,
        y_pred,
    )

    print()
    print("=" * 60)
    print("ANOMALY DETECTION RESULTS")
    print("=" * 60)

    print(f"Total samples      : {len(df)}")
    print(f"Actual anomalies   : {sum(y_true)}")
    print(f"Detected anomalies : {sum(y_pred)}")

    print()
    print(f"True Positives     : {metrics['true_positives']}")
    print(f"False Positives    : {metrics['false_positives']}")
    print(f"True Negatives     : {metrics['true_negatives']}")
    print(f"False Negatives    : {metrics['false_negatives']}")

    print()
    print(f"Precision          : {metrics['precision']}")
    print(f"Recall             : {metrics['recall']}")
    print(f"Detection Rate     : {metrics['detection_rate']}")

    print("=" * 60)

    return metrics


if __name__ == "__main__":
    run_evaluation()