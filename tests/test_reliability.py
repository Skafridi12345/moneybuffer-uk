import math

import pandas as pd
import pytest

from moneybuffer.data_generation import generate_households, generate_scam_messages
from moneybuffer.data_generation.transactions import generate_transactions
from moneybuffer.recommendations import generate_combined_action_plan
from moneybuffer.resilience import calculate_resilience_score
from moneybuffer.resilience.score import SUB_SCORE_COLUMNS
from moneybuffer.scams import calculate_scam_risk_score
from moneybuffer.stress_testing import (
    apply_bill_shock,
    apply_income_shock,
    apply_unexpected_expense,
    compare_baseline_vs_stress,
    run_scenario,
)


def _household(**overrides: float | str) -> pd.DataFrame:
    data: dict[str, float | str] = {
        "household_id": "HH99999",
        "household_type": "Reliability Test Household",
        "monthly_income": 4_000.0,
        "rent_or_mortgage": 1_000.0,
        "council_tax": 180.0,
        "energy_bill": 180.0,
        "water_bill": 40.0,
        "broadband_phone": 45.0,
        "groceries": 450.0,
        "transport": 200.0,
        "insurance": 100.0,
        "subscriptions": 50.0,
        "discretionary_spending": 250.0,
        "debt_repayments": 150.0,
        "savings_balance": 6_000.0,
        "overdraft_balance": 0.0,
        "credit_card_balance": 300.0,
    }
    data.update(overrides)
    return pd.DataFrame([data])


def test_resilience_scores_and_subscores_are_clipped_for_extreme_inputs() -> None:
    households = pd.concat(
        [
            _household(
                monthly_income=1.0,
                debt_repayments=10_000.0,
                overdraft_balance=50_000.0,
                credit_card_balance=50_000.0,
                savings_balance=0.0,
            ),
            _household(
                monthly_income=20_000.0,
                rent_or_mortgage=0.0,
                council_tax=0.0,
                energy_bill=0.0,
                water_bill=0.0,
                broadband_phone=0.0,
                groceries=0.0,
                transport=0.0,
                insurance=0.0,
                debt_repayments=0.0,
                savings_balance=1_000_000.0,
            ),
        ],
        ignore_index=True,
    )

    scored = calculate_resilience_score(households)

    assert scored["resilience_score"].between(0, 100).all()
    for column in SUB_SCORE_COLUMNS:
        assert scored[column].between(0, 100).all()


def test_zero_income_and_zero_essential_spending_create_finite_metrics() -> None:
    scored = calculate_resilience_score(
        _household(
            monthly_income=0.0,
            rent_or_mortgage=0.0,
            council_tax=0.0,
            energy_bill=0.0,
            water_bill=0.0,
            broadband_phone=0.0,
            groceries=0.0,
            transport=0.0,
            insurance=0.0,
            savings_balance=1_000.0,
        )
    )

    numeric_values = scored.select_dtypes(include="number").iloc[0]
    assert all(math.isfinite(value) for value in numeric_values)


def test_synthetic_households_avoid_personal_data_fields() -> None:
    households = generate_households(n=20, seed=99)
    forbidden_columns = {
        "name",
        "first_name",
        "last_name",
        "email",
        "phone",
        "address",
        "postcode",
        "national_insurance_number",
    }

    assert forbidden_columns.isdisjoint(set(households.columns))
    assert households["household_id"].str.fullmatch(r"HH\d{5}").all()


def test_synthetic_scam_messages_are_labelled_demo_text() -> None:
    messages = generate_scam_messages()

    assert {"message_type", "is_scam", "message"}.issubset(messages.columns)
    assert messages["message"].str.len().gt(0).all()
    assert not messages["message"].str.contains("@").any()


def test_transactions_support_full_allowed_month_range() -> None:
    households = generate_households(n=3, seed=5)
    transactions = generate_transactions(households, months=12, seed=5)

    transaction_months = pd.to_datetime(transactions["date"]).dt.to_period("M")
    assert transaction_months.nunique() == 12


def test_scenario_engine_validates_mismatched_comparison_lengths() -> None:
    baseline = generate_households(n=2, seed=1)
    stressed = baseline.iloc[[0]].copy()

    with pytest.raises(ValueError, match="same row count"):
        compare_baseline_vs_stress(baseline, stressed)


def test_scenario_engine_validates_bad_inputs() -> None:
    household = _household()

    with pytest.raises(ValueError, match="between 0 and 1"):
        apply_income_shock(household, pct_drop=1.5)
    with pytest.raises(ValueError, match="Column not found"):
        apply_bill_shock(household, column="not_a_bill", amount_increase=10)
    with pytest.raises(ValueError, match="non-negative"):
        apply_unexpected_expense(household, amount=-1)
    with pytest.raises(ValueError, match="Unknown scenario_name"):
        run_scenario(household, "not_a_scenario")


def test_scam_risk_score_is_capped_and_empty_message_is_low_risk() -> None:
    severe_message = (
        "Urgent HMRC bank final warning. Use new bank details, pay this account "
        "instead by bank transfer, bitcoin or gift card at http://bit.ly/pay-now. "
        "This is a risk free investment with guaranteed returns."
    )

    severe_result = calculate_scam_risk_score(severe_message)
    empty_result = calculate_scam_risk_score("")

    assert severe_result["risk_score"] == 100
    assert severe_result["risk_band"] == "Severe"
    assert empty_result["risk_score"] == 0
    assert empty_result["risk_band"] == "Low"


def test_action_plan_public_wording_is_cautious_not_directive() -> None:
    row = pd.Series(
        {
            "risk_band": "Critical",
            "emergency_runway_months": 0.1,
            "debt_service_ratio": 0.4,
            "monthly_surplus": -100.0,
            "credit_dependency_ratio": 0.7,
        }
    )
    scam_result = {"risk_band": "Severe"}

    plan = generate_combined_action_plan(row, scam_result)
    public_text = " ".join(
        [
            *plan["urgent_actions"],
            *plan["medium_term_actions"],
            *plan["positive_actions"],
            str(plan["disclaimer"]),
        ]
    ).lower()

    assert "you should" not in public_text
    assert "you must" not in public_text
    assert "guaranteed" not in public_text
    assert "consider" in public_text or "you may want" in public_text
