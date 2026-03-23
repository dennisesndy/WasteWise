"""
General utility functions.
"""

import numpy as np


def calculate_cv(series) -> float:
    """Calculate coefficient of variation."""
    mean = series.mean()
    if mean > 0:
        return series.std() / mean * 100
    return 0.0


def get_waste_class(waste_pct: float) -> str:
    """Determine CSS class based on waste percentage."""
    if waste_pct > 30:
        return "danger"
    elif waste_pct > 15:
        return "warning"
    return "safe"


def safe_mean(arr) -> float:
    """Calculate mean, handling empty arrays."""
    if arr is None or len(arr) == 0:
        return 0.0
    return float(np.mean(arr))
