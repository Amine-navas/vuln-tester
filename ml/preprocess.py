"""
Preprocessing helpers for the ML pipeline.

Keep these helpers simple and readable. They avoid heavy dependencies so the
project remains easy to run in low-footprint environments.
"""
from typing import List, Dict, Any


def sanitize_row(row: Dict[str, Any]) -> Dict[str, float]:
    """Convert a DB row (mapping) into a numeric-only feature dict.

    Non-numeric values are coerced to 0.0. Caller decides which columns to keep.
    """
    out = {}
    for k, v in row.items():
        try:
            out[k] = float(v) if v is not None else 0.0
        except Exception:
            out[k] = 0.0
    return out


def aggregate_rows(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    """Aggregate a list of numeric rows into their column-wise means.

    This is intentionally simple: compute means and return a flat dict.
    """
    if not rows:
        return {}
    sums = {}
    counts = {}
    for r in rows:
        for k, v in sanitize_row(r).items():
            sums[k] = sums.get(k, 0.0) + v
            counts[k] = counts.get(k, 0) + 1
    return {k: (sums[k] / counts[k]) for k in sums}
