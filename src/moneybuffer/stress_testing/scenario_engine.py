"""Scenario orchestration for MoneyBuffer UK household stress tests."""

from __future__ import annotations

from typing import Any

import pandas as pd

from moneybuffer.resilience import calculate_resilience_score
from moneybuffer.stress_testing.bill_shocks import (
    apply_bill_shock,
    apply_unexpected_expense,
)
from moneybuffer.stress_testing.income_shocks import apply_income_shock

COMPARISON_COLUMNS = [
    "baseline_score",
    "stressed_score",
    "baseline_band",
    "stressed_band",
    "score_change",
    "baseline_monthly_surplus",
    "stressed_monthly_surplus",
    "baseline_runway_months",
    "stressed_runway_months",
]


def _apply_interest_rate_payment_increase(
    df: pd.DataFrame,
    amount: float,
    target: str = "debt_repayments",
) -> pd.DataFrame:
    if target not in {"debt_repayments", "rent_or_mortgage"}:
        raise ValueError("target must be 'debt_repayments' or 'rent_or_mortgage'")
    return apply_bill_shock(df, column=target, amount_increase=amount)


def run_scenario(df: pd.DataFrame, scenario_name: str, **kwargs: Any) -> pd.DataFrame:
    """Apply a named stress scenario to a household dataframe."""

    if scenario_name == "income_drop_pct":
        return apply_income_shock(
            df,
            pct_drop=float(kwargs["pct_drop"]),
            duration_months=int(kwargs.get("duration_months", 1)),
        )

    if scenario_name == "rent_or_mortgage_increase_pct":
        return apply_bill_shock(
            df,
            column="rent_or_mortgage",
            pct_increase=float(kwargs["pct_increase"]),
        )

    if scenario_name == "energy_bill_increase_amount":
        return apply_bill_shock(
            df,
            column="energy_bill",
            amount_increase=float(kwargs["amount_increase"]),
        )

    if scenario_name == "unexpected_expense_amount":
        return apply_unexpected_expense(df, amount=float(kwargs["amount"]))

    if scenario_name == "interest_rate_payment_increase_amount":
        return _apply_interest_rate_payment_increase(
            df,
            amount=float(kwargs["amount_increase"]),
            target=str(kwargs.get("target", "debt_repayments")),
        )

    if scenario_name == "compound_scenario":
        return apply_compound_scenario(
            df,
            income_drop_pct=float(kwargs.get("income_drop_pct", 0.0)),
            duration_months=int(kwargs.get("duration_months", 1)),
            rent_or_mortgage_increase_pct=float(
                kwargs.get("rent_or_mortgage_increase_pct", 0.0)
            ),
            energy_bill_increase_amount=float(
                kwargs.get("energy_bill_increase_amount", 0.0)
            ),
            unexpected_expense_amount=float(
                kwargs.get("unexpected_expense_amount", 0.0)
            ),
            debt_payment_increase_amount=float(
                kwargs.get("debt_payment_increase_amount", 0.0)
            ),
        )

    raise ValueError(f"Unknown scenario_name: {scenario_name}")


def apply_compound_scenario(
    df: pd.DataFrame,
    income_drop_pct: float = 0.0,
    duration_months: int = 1,
    rent_or_mortgage_increase_pct: float = 0.0,
    energy_bill_increase_amount: float = 0.0,
    unexpected_expense_amount: float = 0.0,
    debt_payment_increase_amount: float = 0.0,
) -> pd.DataFrame:
    """Apply multiple adverse shocks at the same time and return scored rows."""

    if income_drop_pct < 0 or income_drop_pct > 1:
        raise ValueError("income_drop_pct must be between 0 and 1")
    if duration_months <= 0:
        raise ValueError("duration_months must be greater than 0")
    for name, value in {
        "rent_or_mortgage_increase_pct": rent_or_mortgage_increase_pct,
        "energy_bill_increase_amount": energy_bill_increase_amount,
        "unexpected_expense_amount": unexpected_expense_amount,
        "debt_payment_increase_amount": debt_payment_increase_amount,
    }.items():
        if value < 0:
            raise ValueError(f"{name} must be non-negative")

    stressed = df.copy()
    original_income = stressed["monthly_income"].astype(float)
    original_savings = stressed["savings_balance"].astype(float)

    if income_drop_pct > 0:
        stressed["monthly_income"] = original_income * (1 - income_drop_pct)
    if rent_or_mortgage_increase_pct > 0:
        stressed["rent_or_mortgage"] = stressed["rent_or_mortgage"] * (
            1 + rent_or_mortgage_increase_pct
        )
    if energy_bill_increase_amount > 0:
        stressed["energy_bill"] = stressed["energy_bill"] + energy_bill_increase_amount
    if debt_payment_increase_amount > 0:
        stressed["debt_repayments"] = (
            stressed["debt_repayments"] + debt_payment_increase_amount
        )
    if unexpected_expense_amount > 0:
        stressed["savings_balance"] = (
            stressed["savings_balance"] - unexpected_expense_amount
        ).clip(lower=0)
    trajectory_start_savings = stressed["savings_balance"].astype(float)

    if income_drop_pct > 0:
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
        stressed["savings_balance"] = (
            stressed["savings_balance"] - total_drawdown
        ).clip(lower=0)

    stressed["pre_shock_monthly_income"] = original_income
    stressed["pre_shock_savings_balance"] = original_savings
    stressed["trajectory_start_savings_balance"] = trajectory_start_savings
    stressed["shock_duration_months"] = duration_months

    return calculate_resilience_score(stressed)


def compare_baseline_vs_stress(
    baseline_df: pd.DataFrame,
    stressed_df: pd.DataFrame,
) -> pd.DataFrame:
    """Compare baseline and stressed resilience outputs."""

    if len(baseline_df) != len(stressed_df):
        raise ValueError("baseline_df and stressed_df must contain the same row count")

    baseline = calculate_resilience_score(baseline_df).reset_index(drop=True)
    stressed = calculate_resilience_score(stressed_df).reset_index(drop=True)

    comparison = pd.DataFrame(
        {
            "baseline_score": baseline["resilience_score"],
            "stressed_score": stressed["resilience_score"],
            "baseline_band": baseline["risk_band"],
            "stressed_band": stressed["risk_band"],
            "score_change": stressed["resilience_score"] - baseline["resilience_score"],
            "baseline_monthly_surplus": baseline["monthly_surplus"],
            "stressed_monthly_surplus": stressed["monthly_surplus"],
            "baseline_runway_months": baseline["emergency_runway_months"],
            "stressed_runway_months": stressed["emergency_runway_months"],
        }
    )

    id_columns = [
        column
        for column in ("household_id", "household_type")
        if column in baseline_df.columns
    ]
    if id_columns:
        identifiers = baseline_df[id_columns].reset_index(drop=True)
        comparison = pd.concat([identifiers, comparison], axis=1)

    return comparison


def summarise_compound_scenario(
    baseline_df: pd.DataFrame,
    stressed_df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise baseline versus compound stress outputs."""

    comparison = compare_baseline_vs_stress(baseline_df, stressed_df)
    output_columns = [
        "household_id",
        "baseline_score",
        "stressed_score",
        "score_change",
        "baseline_band",
        "stressed_band",
        "baseline_monthly_surplus",
        "stressed_monthly_surplus",
        "baseline_runway_months",
        "stressed_runway_months",
    ]
    available_columns = [
        column for column in output_columns if column in comparison.columns
    ]
    return comparison[available_columns]


def simulate_runway_over_time(
    row: pd.Series,
    duration_months: int = 12,
) -> pd.DataFrame:
    """Simulate simple month-by-month savings drawdown or accumulation."""

    if duration_months <= 0:
        raise ValueError("duration_months must be greater than 0")

    scored = calculate_resilience_score(pd.DataFrame([row.to_dict()])).iloc[0]
    savings_balance = float(
        scored.get(
            "trajectory_start_savings_balance",
            scored.get("pre_shock_savings_balance", scored["savings_balance"]),
        )
    )
    shock_duration_months = int(scored.get("shock_duration_months", duration_months))
    recovered_income = float(
        scored.get("pre_shock_monthly_income", scored["monthly_income"])
    )
    shocked_income = float(scored["monthly_income"])
    recurring_spending = (
        float(scored["essential_spending"])
        + float(scored["subscriptions"])
        + float(scored["discretionary_spending"])
        + float(scored["debt_repayments"])
    )
    records: list[dict[str, float | int | bool]] = []

    for month in range(1, duration_months + 1):
        income = shocked_income if month <= shock_duration_months else recovered_income
        monthly_surplus = income - recurring_spending
        savings_balance = max(0.0, savings_balance + monthly_surplus)
        is_depleted = savings_balance <= 0
        records.append(
            {
                "month": month,
                "income": income,
                "essential_spending": float(scored["essential_spending"]),
                "debt_repayments": float(scored["debt_repayments"]),
                "discretionary_spending": float(
                    scored["discretionary_spending"] + scored["subscriptions"]
                ),
                "monthly_surplus": monthly_surplus,
                "savings_balance": savings_balance,
                "is_depleted": is_depleted,
            }
        )

    return pd.DataFrame.from_records(records)


def months_until_savings_depleted(
    row: pd.Series,
    max_months: int = 24,
) -> int | None:
    """Return months until savings reach zero, or None within the horizon."""

    if max_months <= 0:
        raise ValueError("max_months must be greater than 0")

    trajectory = simulate_runway_over_time(row, duration_months=max_months)
    depleted = trajectory.loc[trajectory["is_depleted"]]
    if depleted.empty:
        return None
    return int(depleted.iloc[0]["month"])
