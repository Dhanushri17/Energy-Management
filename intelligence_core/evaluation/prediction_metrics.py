"""
Prediction evaluation metrics (spec section 18).
"""

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def evaluate_predictions(y_true, y_pred) -> dict:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = r2_score(y_true, y_pred)

    # MAPE — only meaningful where y_true != 0
    nonzero_mask = y_true != 0
    if nonzero_mask.any():
        mape = float(
            np.mean(
                np.abs(
                    (y_true[nonzero_mask] - y_pred[nonzero_mask])
                    / y_true[nonzero_mask]
                )
            )
            * 100
        )
    else:
        mape = None

    return {
        "mae": round(float(mae), 4),
        "rmse": round(rmse, 4),
        "mape_percent": round(mape, 2) if mape is not None else None,
        "r2": round(float(r2), 4),
        "n_samples": int(len(y_true)),
    }
