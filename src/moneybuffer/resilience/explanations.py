"""Plain-English explanations for resilience scores."""

from __future__ import annotations

import math

import pandas as pd


def _number(row: pd.Series, key: str, default: float = 0.0) -> float:
    value = row.get(key, default)
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def _score_gap(row: pd.Series, score_key: str, fallback: float) -> float:
    sub_score = _number(row, score_key, fallback)
    return max(0.0, 100.0 - sub_score)


def explain_score(row: pd.Series) -> list[str]:
    """Return the top three score explanations using calculated values."""

    emergency_runway_months = _number(row, "emergency_runway_months")
    debt_service_ratio = _number(row, "debt_service_ratio")
    essential_spending_ratio = _number(row, "essential_spending_ratio")
    monthly_surplus = _number(row, "monthly_surplus")
    credit_dependency_ratio = _number(row, "credit_dependency_ratio")

    explanations: list[tuple[float, str]] = [
        (
            _score_gap(row, "emergency_runway_score", 0),
            "Your emergency savings cover about "
            f"{emergency_runway_months:.1f} months of essential spending. A lower "
            "buffer means an income disruption or large bill could affect your "
            "ability to keep up with essentials. Try the Income Drop or Unexpected "
            "Expense simulator to see the impact.",
        ),
        (
            _score_gap(row, "debt_service_score", 0),
            "Debt repayments are approximately "
            f"{debt_service_ratio:.0%} of monthly income. Higher debt commitments "
            "reduce flexibility if bills rise or income falls. Consider reviewing "
            "the Bill Shock Simulator to see how extra commitments affect the score.",
        ),
        (
            _score_gap(row, "essential_spending_score", 0),
            "Essential spending is approximately "
            f"{essential_spending_ratio:.0%} of income. This leaves less room to "
            "absorb unexpected costs. Try the Rent/mortgage increase or Energy "
            "bill increase simulator to explore pressure points.",
        ),
        (
            _score_gap(row, "surplus_score", 0),
            "Your estimated monthly surplus is "
            f"£{monthly_surplus:,.0f}. A negative or very small surplus means "
            "your savings may fall over time. It may be sensible to review the "
            "Action Plan for practical educational prompts.",
        ),
        (
            _score_gap(row, "credit_dependency_score", 0),
            "Overdraft and credit-card balances are approximately "
            f"{credit_dependency_ratio:.0%} of monthly income. Reliance on "
            "short-term credit can increase vulnerability if income falls. Try "
            "the Income Drop simulator to see how this could affect resilience.",
        ),
    ]

    return [
        explanation
        for _, explanation in sorted(
            explanations,
            key=lambda item: item[0],
            reverse=True,
        )[:3]
    ]


def _next_band_threshold(score: float) -> tuple[str, float] | None:
    if score < 35:
        return ("Vulnerable", 35)
    if score < 55:
        return ("Watch", 55)
    if score < 75:
        return ("Stable", 75)
    return None


def estimate_improvement_to_next_band(row: pd.Series) -> str:
    """Return an illustrative improvement statement for the next score band."""

    score = _number(row, "resilience_score")
    next_band = _next_band_threshold(score)
    monthly_surplus = _number(row, "monthly_surplus")
    essential_spending = _number(row, "essential_spending")
    emergency_runway_score = _number(row, "emergency_runway_score")

    if next_band is None:
        return (
            "Illustrative: this household is already in the highest band. "
            "Maintaining savings, positive cashflow, and manageable commitments "
            "could help preserve the score."
        )

    band_name, threshold = next_band
    score_gap = max(0.0, threshold - score)

    if monthly_surplus < 0:
        commitment_reduction = abs(monthly_surplus)
        return (
            "Illustrative: reducing monthly commitments or increasing income by "
            f"about £{commitment_reduction:,.0f} could remove the estimated "
            f"cashflow shortfall and may move the household closer to the "
            f"{band_name} band."
        )

    if essential_spending > 0 and emergency_runway_score < 100:
        runway_score_points = min(100 - emergency_runway_score, score_gap / 0.30)
        extra_runway_months = max(0.0, runway_score_points / 100 * 6)
        savings_increase = extra_runway_months * essential_spending
        return (
            "Illustrative: increasing savings by about "
            f"£{savings_increase:,.0f} could improve emergency runway and may "
            f"move the household closer to the {band_name} band."
        )

    commitment_reduction = max(50.0, score_gap * 25)
    return (
        "Illustrative: reducing monthly commitments by about "
        f"£{commitment_reduction:,.0f} could improve the score meaningfully and "
        f"may move the household closer to the {band_name} band."
    )
