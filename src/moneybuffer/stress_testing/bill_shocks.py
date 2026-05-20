"""Bill and one-off expense shock scenarios."""

from __future__ import annotations

import pandas as pd

ALLOWED_RENT_OR_MORTGAGE_INCREASE_PCTS = {0.05, 0.10, 0.15}
ALLOWED_ENERGY_BILL_INCREASE_AMOUNTS = {50.0, 100.0, 150.0}
ALLOWED_UNEXPECTED_EXPENSE_AMOUNTS = {300.0, 500.0, 1000.0, 1500.0, 2000.0, 3000.0}


def apply_bill_shock(
    df: pd.DataFrame,
    column: str,
    pct_increase: float | None = None,
    amount_increase: float | None = None,
) -> pd.DataFrame:
    """Increase a recurring household bill by percentage, amount, or both."""

    if column not in df.columns:
        raise ValueError(f"Column not found in household dataframe: {column}")
    if pct_increase is None and amount_increase is None:
        raise ValueError("Provide pct_increase, amount_increase, or both")
    if pct_increase is not None and pct_increase < 0:
        raise ValueError("pct_increase must be non-negative")
    if amount_increase is not None and amount_increase < 0:
        raise ValueError("amount_increase must be non-negative")

    stressed = df.copy()
    if pct_increase is not None:
        stressed[column] = stressed[column] * (1 + pct_increase)
    if amount_increase is not None:
        stressed[column] = stressed[column] + amount_increase
    return stressed


def apply_unexpected_expense(df: pd.DataFrame, amount: float) -> pd.DataFrame:
    """Apply a one-off expense by reducing available savings."""

    if amount < 0:
        raise ValueError("amount must be non-negative")

    stressed = df.copy()
    stressed["savings_balance"] = (stressed["savings_balance"] - amount).clip(lower=0)
    return stressed
