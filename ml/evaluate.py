"""
Evaluation helpers for ML models.

Provides small utilities that wrap sklearn evaluation. These functions avoid
side effects and are written to be explicit and easy to read.
"""
from typing import Any, Dict


def accuracy_score(model: Any, X, y) -> float:
    """Return a basic accuracy score using model.score when available.

    This function does not import heavy modules at top-level; it assumes the
    caller has prepared X and y in appropriate types (lists/numpy arrays).
    """
    try:
        return float(model.score(X, y))
    except Exception:
        return 0.0


def classification_report_dict(model: Any, X, y) -> Dict[str, float]:
    """Return a minimal dict with accuracy as the main metric.

    Kept intentionally small to avoid pulling pandas/scikit-learn text reports
    into programmatic code paths.
    """
    return {"accuracy": accuracy_score(model, X, y)}
