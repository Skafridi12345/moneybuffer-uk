"""Risk-band assignment for MoneyBuffer UK resilience scores."""

from __future__ import annotations


def assign_risk_band(score: float) -> str:
    """Assign a plain-English risk band from a 0-100 resilience score."""

    if score >= 75:
        return "Stable"
    if score >= 55:
        return "Watch"
    if score >= 35:
        return "Vulnerable"
    return "Critical"
