"""
Anomaly detection evaluation metrics (spec section 18).

If you don't have labeled anomaly data yet, use `document_limitations()`
to record that explicitly rather than skipping evaluation silently.
"""

from sklearn.metrics import precision_score, recall_score, confusion_matrix


def evaluate_anomaly_detection(y_true, y_pred) -> dict:
    """
    Args:
        y_true: list/array of ground-truth booleans (1 = actual anomaly)
        y_pred: list/array of predicted booleans (1 = detected anomaly)
    """
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)

    return {
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "detection_rate": round(float(recall), 4),
    }


def document_limitations(note: str) -> dict:
    """Use this when you don't yet have labeled anomaly data to evaluate against."""
    return {
        "status": "no_labeled_data",
        "note": note,
    }
