"""Income shock scenarios for household stress testing."""

from __future__ import annotations

import pandas as pd

ALLOWED_INCOME_DROP_PCTS = {0.20, 0.40, 1.00}


def apply_income_shock(
    df: pd.DataFrame,
    pct_drop: float,
    duration_months: int = 1,
) -> pd.DataFrame:
    """Reduce monthly income and model savings drawdown over the shock duration."""

    if pct_drop < 0 or pct_drop > 1:
        raise ValueError("pct_drop must be between 0 and 1")
    if duration_months <= 0:
        raise ValueError("duration_months must be greater than 0")

    stressed = df.copy()
    original_income = stressed["monthly_income"].astype(float)
    original_savings = stressed["savings_balance"].astype(float)
    stressed["monthly_income"] = original_income * (1 - pct_drop)

    recurring_spending = (
        stressed["rent_or_mortgage"]
        + stressed["council_tax"]
        + stressed["energy_bill"]
        + stressed["water_bill"]
        + stressed["broadband_phone"]
        + stressed["groceries"]
        + stressed["transport"]
        + stressed["insurance"]
        + stressed["subscriptions"]
        + stressed["discretionary_spending"]
        + stressed["debt_repayments"]
    )
    stressed_surplus = stressed["monthly_income"] - recurring_spending
    total_drawdown = (-stressed_surplus.clip(upper=0)) * duration_months
    stressed["savings_balance"] = (stressed["savings_balance"] - total_drawdown).clip(
        lower=0
    )
    stressed["pre_shock_monthly_income"] = original_income
    stressed["pre_shock_savings_balance"] = original_savings
    stressed["trajectory_start_savings_balance"] = original_savings
    stressed["shock_duration_months"] = duration_months
    return stressed
