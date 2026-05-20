"""Explainable 0-100 financial resilience scoring using piecewise-linear curves."""

from __future__ import annotations

import numpy as np
import pandas as pd

from moneybuffer.resilience.bands import assign_risk_band
from moneybuffer.resilience.features import calculate_resilience_features

SUB_SCORE_COLUMNS = [
    "emergency_runway_score",
    "essential_spending_score",
    "debt_service_score",
    "surplus_score",
    "credit_dependency_score",
]

# ---------------------------------------------------------------------------
# Control-point tables
# Each table is a list of (x, y) pairs sorted by x ascending.
# Values outside the defined range clamp to the first or last y.
# ---------------------------------------------------------------------------

_RUNWAY_POINTS: list[tuple[float, float]] = [
    (0.0, 0.0),
    (1.0, 30.0),
    (3.0, 70.0),
    (6.0, 100.0),
]

_ESSENTIAL_SPENDING_POINTS: list[tuple[float, float]] = [
    (0.45, 100.0),
    (0.60, 75.0),
    (0.75, 40.0),
    (0.90, 0.0),
]

_DEBT_SERVICE_POINTS: list[tuple[float, float]] = [
    (0.10, 100.0),
    (0.20, 75.0),
    (0.30, 40.0),
    (0.50, 0.0),
]

# Surplus expressed as a ratio of monthly income (can be negative)
_SURPLUS_RATIO_POINTS: list[tuple[float, float]] = [
    (-0.10, 0.0),
    (0.00, 40.0),
    (0.10, 75.0),
    (0.20, 100.0),
]

# Credit-card + overdraft balances as a multiple of monthly income
_CREDIT_DEPENDENCY_POINTS: list[tuple[float, float]] = [
    (0.00, 100.0),
    (0.25, 70.0),
    (0.50, 40.0),
    (1.00, 0.0),
]


# ---------------------------------------------------------------------------
# Public piecewise-linear helper
# ---------------------------------------------------------------------------


def piecewise_score(value: float, points: list[tuple[float, float]]) -> float:
    """Map a scalar to a 0–100 score via piecewise-linear interpolation.

    `points` is a list of (x, y) pairs sorted by x ascending.  Values below
    the first x clamp to the first y; values above the last x clamp to the
    last y.  The result is always clipped to [0, 100].
    """
    if value <= points[0][0]:
        return float(np.clip(points[0][1], 0.0, 100.0))
    if value >= points[-1][0]:
        return float(np.clip(points[-1][1], 0.0, 100.0))
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        if x0 <= value <= x1:
            t = (value - x0) / (x1 - x0)
            return float(np.clip(y0 + t * (y1 - y0), 0.0, 100.0))
    return 0.0  # unreachable for well-formed points


def _apply_piecewise(series: pd.Series, points: list[tuple[float, float]]) -> pd.Series:
    """Apply piecewise_score element-wise to a pd.Series."""
    fn = np.vectorize(lambda v: piecewise_score(float(v), points))
    return pd.Series(fn(series.to_numpy(dtype=float)), index=series.index)


# ---------------------------------------------------------------------------
# Sub-score functions
# ---------------------------------------------------------------------------


def _runway_score(runway_months: pd.Series) -> pd.Series:
    # inf → natural clamp to 100 inside piecewise_score; -inf → 0
    return _apply_piecewise(runway_months, _RUNWAY_POINTS)


def _surplus_score(monthly_surplus: pd.Series, monthly_income: pd.Series) -> pd.Series:
    surplus_ratio = pd.Series(
        np.divide(
            monthly_surplus.astype(float),
            monthly_income.astype(float),
            out=np.zeros(len(monthly_surplus), dtype=float),
            where=monthly_income.to_numpy(dtype=float) != 0,
        ),
        index=monthly_surplus.index,
    )
    return _apply_piecewise(surplus_ratio, _SURPLUS_RATIO_POINTS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def calculate_resilience_score(df: pd.DataFrame | pd.Series) -> pd.DataFrame:
    """Calculate resilience features, sub-scores, final score, and risk band."""

    scored = calculate_resilience_features(df)

    scored["emergency_runway_score"] = _runway_score(scored["emergency_runway_months"])
    scored["essential_spending_score"] = _apply_piecewise(
        scored["essential_spending_ratio"], _ESSENTIAL_SPENDING_POINTS
    )
    scored["debt_service_score"] = _apply_piecewise(
        scored["debt_service_ratio"], _DEBT_SERVICE_POINTS
    )
    scored["surplus_score"] = _surplus_score(
        scored["monthly_surplus"], scored["monthly_income"]
    )
    scored["credit_dependency_score"] = _apply_piecewise(
        scored["credit_dependency_ratio"], _CREDIT_DEPENDENCY_POINTS
    )

    scored["resilience_score"] = (
        (
            0.30 * scored["emergency_runway_score"]
            + 0.20 * scored["essential_spending_score"]
            + 0.20 * scored["debt_service_score"]
            + 0.20 * scored["surplus_score"]
            + 0.10 * scored["credit_dependency_score"]
        )
        .clip(lower=0, upper=100)
        .round(1)
    )
    scored["risk_band"] = scored["resilience_score"].apply(assign_risk_band)

    return scored
