import pandas as pd
import pytest

from moneybuffer.resilience import calculate_resilience_score
from moneybuffer.stress_testing import (
    apply_bill_shock,
    apply_compound_scenario,
    apply_income_shock,
    apply_unexpected_expense,
    compare_baseline_vs_stress,
    months_until_savings_depleted,
    run_scenario,
    simulate_runway_over_time,
    summarise_compound_scenario,
)


def _household(**overrides: float | str) -> pd.DataFrame:
    data: dict[str, float | str] = {
        "household_id": "HH00001",
        "household_type": "Stable Household",
        "monthly_income": 4_000.0,
        "rent_or_mortgage": 900.0,
        "council_tax": 160.0,
        "energy_bill": 160.0,
        "water_bill": 40.0,
        "broadband_phone": 45.0,
        "groceries": 420.0,
        "transport": 180.0,
        "insurance": 90.0,
        "subscriptions": 40.0,
        "discretionary_spending": 250.0,
        "debt_repayments": 100.0,
        "savings_balance": 12_000.0,
        "overdraft_balance": 0.0,
        "credit_card_balance": 200.0,
    }
    data.update(overrides)
    return pd.DataFrame([data])


def test_income_drop_lowers_score() -> None:
    baseline = _household()
    stressed = apply_income_shock(baseline, pct_drop=0.40)

    baseline_score = calculate_resilience_score(baseline).loc[0, "resilience_score"]
    stressed_score = calculate_resilience_score(stressed).loc[0, "resilience_score"]

    assert stressed.loc[0, "monthly_income"] == 2_400
    assert stressed_score < baseline_score


def test_three_month_income_shock_reduces_savings_more_than_one_month() -> None:
    baseline = _household(savings_balance=2_000.0)

    one_month = apply_income_shock(baseline, pct_drop=0.50, duration_months=1)
    three_months = apply_income_shock(baseline, pct_drop=0.50, duration_months=3)

    assert (
        three_months.loc[0, "savings_balance"]
        < one_month.loc[
            0,
            "savings_balance",
        ]
    )


def test_income_shock_trajectory_recovers_after_duration() -> None:
    baseline = _household()
    stressed = apply_income_shock(baseline, pct_drop=0.50, duration_months=3)
    trajectory = simulate_runway_over_time(stressed.iloc[0], duration_months=5)

    assert trajectory.loc[0, "income"] == 2_000
    assert trajectory.loc[2, "income"] == 2_000
    assert trajectory.loc[3, "income"] == 4_000


def test_bill_increase_lowers_monthly_surplus() -> None:
    baseline = _household()
    stressed = apply_bill_shock(
        baseline,
        column="rent_or_mortgage",
        pct_increase=0.15,
    )

    baseline_surplus = calculate_resilience_score(baseline).loc[0, "monthly_surplus"]
    stressed_surplus = calculate_resilience_score(stressed).loc[0, "monthly_surplus"]

    assert stressed.loc[0, "rent_or_mortgage"] == 1_035
    assert stressed_surplus < baseline_surplus


def test_unexpected_expense_reduces_savings_and_runway() -> None:
    baseline = _household(savings_balance=1_500.0)
    stressed = apply_unexpected_expense(baseline, amount=500.0)

    baseline_runway = calculate_resilience_score(baseline).loc[
        0,
        "emergency_runway_months",
    ]
    stressed_runway = calculate_resilience_score(stressed).loc[
        0,
        "emergency_runway_months",
    ]

    assert stressed.loc[0, "savings_balance"] == 1_000
    assert stressed_runway < baseline_runway


def test_unexpected_expense_of_3000_is_supported() -> None:
    baseline = _household(savings_balance=5_000.0)
    stressed = apply_unexpected_expense(baseline, amount=3_000.0)

    assert stressed.loc[0, "savings_balance"] == 2_000


def test_run_scenario_dispatches_interest_rate_increase() -> None:
    baseline = _household()
    stressed = run_scenario(
        baseline,
        "interest_rate_payment_increase_amount",
        amount_increase=250,
        target="debt_repayments",
    )

    assert stressed.loc[0, "debt_repayments"] == 350


def test_comparison_output_contains_required_columns() -> None:
    baseline = _household()
    stressed = run_scenario(
        baseline,
        "energy_bill_increase_amount",
        amount_increase=100,
    )
    comparison = compare_baseline_vs_stress(baseline, stressed)

    required_columns = {
        "baseline_score",
        "stressed_score",
        "baseline_band",
        "stressed_band",
        "score_change",
        "baseline_monthly_surplus",
        "stressed_monthly_surplus",
        "baseline_runway_months",
        "stressed_runway_months",
    }

    assert required_columns.issubset(comparison.columns)
    assert (
        comparison.loc[0, "stressed_monthly_surplus"]
        < comparison.loc[
            0,
            "baseline_monthly_surplus",
        ]
    )


def test_negative_monthly_surplus_depletes_savings_over_time() -> None:
    household = _household(
        monthly_income=1_000.0,
        rent_or_mortgage=900.0,
        council_tax=100.0,
        energy_bill=100.0,
        water_bill=0.0,
        broadband_phone=0.0,
        groceries=0.0,
        transport=0.0,
        insurance=0.0,
        subscriptions=0.0,
        discretionary_spending=0.0,
        debt_repayments=0.0,
        savings_balance=250.0,
    )

    trajectory = simulate_runway_over_time(household.iloc[0], duration_months=4)

    assert trajectory.loc[0, "savings_balance"] == 150
    assert trajectory.loc[2, "savings_balance"] == 0
    assert trajectory.loc[2, "is_depleted"]


def test_positive_surplus_does_not_deplete_savings() -> None:
    trajectory = simulate_runway_over_time(_household().iloc[0], duration_months=12)

    assert not trajectory["is_depleted"].any()
    assert trajectory.loc[11, "savings_balance"] > trajectory.loc[0, "savings_balance"]


def test_months_until_savings_depleted_returns_expected_value() -> None:
    household = _household(
        monthly_income=1_000.0,
        rent_or_mortgage=900.0,
        council_tax=100.0,
        energy_bill=100.0,
        water_bill=0.0,
        broadband_phone=0.0,
        groceries=0.0,
        transport=0.0,
        insurance=0.0,
        subscriptions=0.0,
        discretionary_spending=0.0,
        debt_repayments=0.0,
        savings_balance=250.0,
    )

    assert months_until_savings_depleted(household.iloc[0], max_months=12) == 3


def test_compound_scenario_applies_more_than_one_shock() -> None:
    baseline = _household()
    stressed = apply_compound_scenario(
        baseline,
        income_drop_pct=0.20,
        rent_or_mortgage_increase_pct=0.10,
        energy_bill_increase_amount=100,
        debt_payment_increase_amount=50,
    )

    assert stressed.loc[0, "monthly_income"] == 3_200
    assert stressed.loc[0, "rent_or_mortgage"] == pytest.approx(990)
    assert stressed.loc[0, "energy_bill"] == 260
    assert stressed.loc[0, "debt_repayments"] == 150
    assert "resilience_score" in stressed.columns
    assert "risk_band" in stressed.columns


def test_compound_duration_reduces_savings_more_than_one_month() -> None:
    baseline = _household(savings_balance=2_500.0)

    one_month = apply_compound_scenario(
        baseline,
        income_drop_pct=0.50,
        duration_months=1,
        rent_or_mortgage_increase_pct=0.10,
    )
    three_months = apply_compound_scenario(
        baseline,
        income_drop_pct=0.50,
        duration_months=3,
        rent_or_mortgage_increase_pct=0.10,
    )

    assert three_months.loc[0, "savings_balance"] < one_month.loc[0, "savings_balance"]


def test_compound_trajectory_includes_unexpected_expense_before_drawdown() -> None:
    baseline = _household(savings_balance=5_000.0)
    stressed = apply_compound_scenario(
        baseline,
        income_drop_pct=0.50,
        duration_months=2,
        unexpected_expense_amount=3_000.0,
    )
    trajectory = simulate_runway_over_time(stressed.iloc[0], duration_months=1)

    assert trajectory.loc[0, "savings_balance"] < 2_000.0


def test_compound_scenario_score_is_lower_for_adverse_shocks() -> None:
    baseline = _household()
    stressed = apply_compound_scenario(
        baseline,
        income_drop_pct=0.40,
        rent_or_mortgage_increase_pct=0.15,
        energy_bill_increase_amount=150,
        unexpected_expense_amount=1000,
        debt_payment_increase_amount=250,
    )
    summary = summarise_compound_scenario(baseline, stressed)

    assert summary.loc[0, "stressed_score"] < summary.loc[0, "baseline_score"]
    assert summary.loc[0, "score_change"] < 0


def test_compound_unexpected_expense_reduces_savings() -> None:
    baseline = _household(savings_balance=5_000)
    stressed = apply_compound_scenario(
        baseline,
        unexpected_expense_amount=3_000,
    )

    assert stressed.loc[0, "savings_balance"] == 2_000
    assert (
        stressed.loc[0, "emergency_runway_months"]
        < calculate_resilience_score(baseline).loc[0, "emergency_runway_months"]
    )


def test_no_shock_compound_scenario_returns_similar_score_to_baseline() -> None:
    baseline = _household()
    stressed = apply_compound_scenario(baseline)
    summary = summarise_compound_scenario(baseline, stressed)

    assert summary.loc[0, "stressed_score"] == summary.loc[0, "baseline_score"]
    assert summary.loc[0, "stressed_band"] == summary.loc[0, "baseline_band"]
