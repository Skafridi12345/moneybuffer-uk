"""Household input validation for MoneyBuffer UK.

Provides sensible field bounds and a function that returns plain-English
warning strings for inputs that may produce misleading outputs.  Warnings
are advisory only — callers should display them but not block execution.
"""

from __future__ import annotations

import pandas as pd

# ---------------------------------------------------------------------------
# Field bounds — (min, max) in whole GBP per month unless noted.
# Savings and credit balances are totals, not monthly flows.
# ---------------------------------------------------------------------------

FIELD_BOUNDS: dict[str, tuple[int, int]] = {
    "monthly_income": (0, 20_000),
    "rent_or_mortgage": (0, 10_000),
    "council_tax": (0, 1_000),
    "energy_bill": (0, 1_000),
    "water_bill": (0, 500),
    "broadband_phone": (0, 500),
    "groceries": (0, 3_000),
    "transport": (0, 2_000),
    "insurance": (0, 2_000),
    "subscriptions": (0, 1_000),
    "discretionary_spending": (0, 5_000),
    "debt_repayments": (0, 10_000),
    "savings_balance": (0, 250_000),
    "overdraft_balance": (0, 10_000),
    "credit_card_balance": (0, 50_000),
}

_ESSENTIAL_FIELDS = (
    "rent_or_mortgage",
    "council_tax",
    "energy_bill",
    "water_bill",
    "broadband_phone",
    "groceries",
    "transport",
    "insurance",
)


def _get(row: pd.Series, key: str, default: float = 0.0) -> float:
    """Return a float from a Series, falling back to *default* if absent."""
    return float(row[key]) if key in row.index else default


def validate_household_inputs(row: pd.Series) -> list[str]:
    """Return a list of plain-English warnings for inputs that may mislead.

    Works on both raw household rows and scored rows (which already carry
    derived features such as ``essential_spending`` and ``monthly_surplus``).
    Pre-computed values are preferred where available so warnings stay
    consistent with the metrics shown in the app.

    Returns an empty list when no concerns are identified.
    """
    warnings: list[str] = []

    income = _get(row, "monthly_income")
    savings = _get(row, "savings_balance")
    debt_repayments = _get(row, "debt_repayments")

    # Use pre-computed derived values when present (scored row), otherwise
    # compute inline so the validation module has no scoring dependency.
    if "essential_spending" in row.index:
        essential_spending = _get(row, "essential_spending")
    else:
        essential_spending = sum(_get(row, f) for f in _ESSENTIAL_FIELDS)

    if "monthly_surplus" in row.index:
        monthly_surplus = _get(row, "monthly_surplus")
    else:
        subs = _get(row, "subscriptions")
        discr = _get(row, "discretionary_spending")
        monthly_surplus = income - essential_spending - subs - discr - debt_repayments

    if "debt_service_ratio" in row.index and income > 0:
        debt_service_ratio = _get(row, "debt_service_ratio")
    else:
        debt_service_ratio = debt_repayments / income if income > 0 else 0.0

    # --- Warning checks ---

    if income == 0:
        warnings.append(
            "Monthly income is zero. Ratio-based metrics such as the debt service "
            "ratio and essential spending ratio will not be meaningful."
        )

    if income > 0 and essential_spending > income:
        warnings.append(
            f"Essential spending (GBP {essential_spending:,.0f}) exceeds monthly "
            f"income (GBP {income:,.0f}). This implies a deficit on essential costs "
            "alone, before discretionary spending or debt repayments are counted."
        )

    if income > 0 and debt_service_ratio > 0.40:
        warnings.append(
            f"Debt repayments are approximately {debt_service_ratio:.0%} of monthly "
            "income. This is above the 40% threshold commonly used to indicate "
            "significant debt pressure."
        )

    if savings == 0:
        warnings.append(
            "Savings balance is zero. Emergency runway is zero, leaving no buffer "
            "for an unexpected bill or income disruption."
        )

    if monthly_surplus < 0:
        warnings.append(
            f"Current inputs imply a negative monthly cashflow of approximately "
            f"GBP {abs(monthly_surplus):,.0f}. Total spending and commitments "
            "exceed income in this scenario."
        )

    return warnings
