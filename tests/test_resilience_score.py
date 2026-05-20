import pandas as pd
import pytest

from moneybuffer.resilience import (
    assign_risk_band,
    calculate_resilience_features,
    calculate_resilience_score,
    estimate_improvement_to_next_band,
    explain_score,
)
from moneybuffer.resilience.score import (
    _CREDIT_DEPENDENCY_POINTS,
    _DEBT_SERVICE_POINTS,
    _ESSENTIAL_SPENDING_POINTS,
    _RUNWAY_POINTS,
    _SURPLUS_RATIO_POINTS,
    piecewise_score,
)


def _household(**overrides: float) -> pd.DataFrame:
    data: dict[str, float] = {
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
        "savings_balance": 18_000.0,
        "overdraft_balance": 0.0,
        "credit_card_balance": 200.0,
    }
    data.update(overrides)
    return pd.DataFrame([data])


def test_high_savings_household_scores_high() -> None:
    scored = calculate_resilience_score(_household())

    assert scored.loc[0, "resilience_score"] >= 75
    assert scored.loc[0, "risk_band"] == "Stable"


def test_negative_monthly_surplus_reduces_score() -> None:
    stable = calculate_resilience_score(_household())
    pressured = calculate_resilience_score(
        _household(
            monthly_income=2_500,
            rent_or_mortgage=1_100,
            discretionary_spending=650,
            debt_repayments=450,
            savings_balance=300,
        )
    )

    assert pressured.loc[0, "monthly_surplus"] < 0
    assert pressured.loc[0, "surplus_score"] == 0
    assert pressured.loc[0, "resilience_score"] < stable.loc[0, "resilience_score"]


def test_high_debt_service_reduces_score() -> None:
    low_debt = calculate_resilience_score(_household(debt_repayments=50))
    high_debt = calculate_resilience_score(_household(debt_repayments=1_400))

    assert high_debt.loc[0, "debt_service_ratio"] == 0.35
    assert (
        high_debt.loc[0, "debt_service_score"]
        < low_debt.loc[
            0,
            "debt_service_score",
        ]
    )
    assert high_debt.loc[0, "resilience_score"] < low_debt.loc[0, "resilience_score"]


def test_correct_risk_band_assignment() -> None:
    assert assign_risk_band(100) == "Stable"
    assert assign_risk_band(75) == "Stable"
    assert assign_risk_band(74) == "Watch"
    assert assign_risk_band(55) == "Watch"
    assert assign_risk_band(54) == "Vulnerable"
    assert assign_risk_band(35) == "Vulnerable"
    assert assign_risk_band(34) == "Critical"
    assert assign_risk_band(0) == "Critical"


def test_no_division_by_zero_crash_when_income_is_zero() -> None:
    scored = calculate_resilience_score(
        _household(
            monthly_income=0,
            savings_balance=0,
            overdraft_balance=100,
            credit_card_balance=500,
        )
    )

    assert len(scored) == 1
    assert scored.loc[0, "resilience_score"] >= 0
    assert scored.loc[0, "risk_band"] in {"Stable", "Watch", "Vulnerable", "Critical"}


def test_features_and_explanations_are_available() -> None:
    features = calculate_resilience_features(_household(savings_balance=1_000))
    scored = calculate_resilience_score(features)
    reasons = explain_score(scored.loc[0])

    assert "essential_spending" in features.columns
    assert len(reasons) == 3
    assert any("emergency savings cover about" in reason for reason in reasons)


def test_explanations_include_actual_numeric_values() -> None:
    scored = calculate_resilience_score(
        _household(
            savings_balance=1_000,
            debt_repayments=1_200,
            credit_card_balance=4_000,
        )
    )
    reasons = explain_score(scored.loc[0])
    combined = " ".join(reasons)

    assert "0.5 months" in combined
    assert "30% of monthly income" in combined


def test_negative_surplus_produces_clear_explanation() -> None:
    scored = calculate_resilience_score(
        _household(
            monthly_income=2_200,
            rent_or_mortgage=1_100,
            discretionary_spending=650,
            debt_repayments=500,
            savings_balance=300,
        )
    )
    reasons = explain_score(scored.loc[0])
    combined = " ".join(reasons)

    assert "estimated monthly surplus" in combined
    assert "negative or very small surplus" in combined


def test_low_emergency_runway_suggests_relevant_simulator() -> None:
    scored = calculate_resilience_score(_household(savings_balance=250))
    reasons = explain_score(scored.loc[0])
    combined = " ".join(reasons)

    assert "Income Drop" in combined
    assert "Unexpected Expense simulator" in combined


def test_improvement_line_returns_string_and_does_not_crash() -> None:
    scored = calculate_resilience_score(_household(savings_balance=250))

    improvement = estimate_improvement_to_next_band(scored.loc[0])

    assert isinstance(improvement, str)
    assert "Illustrative:" in improvement


# ---------------------------------------------------------------------------
# piecewise_score unit tests
# ---------------------------------------------------------------------------


def test_piecewise_score_at_runway_control_points() -> None:
    assert piecewise_score(0.0, _RUNWAY_POINTS) == 0.0
    assert piecewise_score(1.0, _RUNWAY_POINTS) == 30.0
    assert piecewise_score(3.0, _RUNWAY_POINTS) == 70.0
    assert piecewise_score(6.0, _RUNWAY_POINTS) == 100.0


def test_piecewise_score_clamps_below_first_point() -> None:
    assert piecewise_score(-5.0, _RUNWAY_POINTS) == 0.0


def test_piecewise_score_clamps_above_last_point() -> None:
    assert piecewise_score(100.0, _RUNWAY_POINTS) == 100.0


def test_piecewise_score_clips_output_to_0_100() -> None:
    # A pathological points list whose y-values exceed 100 — output must clamp.
    weird: list[tuple[float, float]] = [(0.0, 120.0), (1.0, -10.0)]
    assert piecewise_score(-1.0, weird) == 100.0
    assert piecewise_score(2.0, weird) == 0.0


def test_piecewise_score_interpolates_between_points() -> None:
    # Midpoint between (1, 30) and (3, 70) should be 50.
    assert piecewise_score(2.0, _RUNWAY_POINTS) == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# Monotonicity tests
# ---------------------------------------------------------------------------


def test_runway_score_is_monotonically_non_decreasing() -> None:
    values = [0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 9.0, 24.0]
    scores = [piecewise_score(v, _RUNWAY_POINTS) for v in values]
    for i in range(len(scores) - 1):
        assert scores[i] <= scores[i + 1], (
            f"Runway score not non-decreasing between {values[i]} and {values[i + 1]}: "
            f"{scores[i]:.2f} > {scores[i + 1]:.2f}"
        )


def test_essential_spending_score_is_monotonically_non_increasing() -> None:
    values = [0.30, 0.45, 0.52, 0.60, 0.68, 0.75, 0.83, 0.90, 1.10]
    scores = [piecewise_score(v, _ESSENTIAL_SPENDING_POINTS) for v in values]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1], (
            f"Essential spending score not non-increasing between {values[i]} and "
            f"{values[i + 1]}: {scores[i]:.2f} < {scores[i + 1]:.2f}"
        )


def test_debt_service_score_is_monotonically_non_increasing() -> None:
    values = [0.0, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.70]
    scores = [piecewise_score(v, _DEBT_SERVICE_POINTS) for v in values]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1], (
            f"Debt service score not non-increasing between {values[i]} and "
            f"{values[i + 1]}: {scores[i]:.2f} < {scores[i + 1]:.2f}"
        )


def test_surplus_ratio_score_is_monotonically_non_decreasing() -> None:
    values = [-0.20, -0.10, -0.05, 0.00, 0.05, 0.10, 0.15, 0.20, 0.40]
    scores = [piecewise_score(v, _SURPLUS_RATIO_POINTS) for v in values]
    for i in range(len(scores) - 1):
        assert scores[i] <= scores[i + 1], (
            f"Surplus score not non-decreasing between "
            f"{values[i]} and {values[i + 1]}: "
            f"{scores[i]:.2f} > {scores[i + 1]:.2f}"
        )


def test_credit_dependency_score_is_monotonically_non_increasing() -> None:
    values = [0.0, 0.10, 0.25, 0.38, 0.50, 0.75, 1.00, 1.50]
    scores = [piecewise_score(v, _CREDIT_DEPENDENCY_POINTS) for v in values]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1], (
            f"Credit dependency score not non-increasing between {values[i]} and "
            f"{values[i + 1]}: {scores[i]:.2f} < {scores[i + 1]:.2f}"
        )


# ---------------------------------------------------------------------------
# Continuity at key thresholds (no cliff edges)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("threshold", [1.0, 3.0, 6.0])
def test_no_cliff_at_runway_threshold(threshold: float) -> None:
    delta = 0.01
    score_before = piecewise_score(threshold - delta, _RUNWAY_POINTS)
    score_after = piecewise_score(threshold + delta, _RUNWAY_POINTS)
    assert abs(score_after - score_before) < 2.0, (
        f"Cliff of {abs(score_after - score_before):.2f} points at runway={threshold}"
    )


@pytest.mark.parametrize("threshold", [0.10, 0.20, 0.30, 0.50])
def test_no_cliff_at_debt_service_threshold(threshold: float) -> None:
    # Use a very small delta: a continuous function must change by < 1 point
    # across a 0.002-wide interval regardless of the local slope.
    delta = 0.001
    score_before = piecewise_score(threshold - delta, _DEBT_SERVICE_POINTS)
    score_after = piecewise_score(threshold + delta, _DEBT_SERVICE_POINTS)
    assert abs(score_after - score_before) < 1.0, (
        f"Cliff of {abs(score_after - score_before):.2f} points at DSR={threshold}"
    )


# ---------------------------------------------------------------------------
# End-to-end scoring behaviour
# ---------------------------------------------------------------------------


def test_high_runway_increases_resilience_score() -> None:
    low = calculate_resilience_score(_household(savings_balance=500))
    high = calculate_resilience_score(_household(savings_balance=30_000))
    assert high.loc[0, "resilience_score"] > low.loc[0, "resilience_score"]


def test_high_debt_reduces_resilience_score() -> None:
    low_debt = calculate_resilience_score(_household(debt_repayments=50))
    high_debt = calculate_resilience_score(_household(debt_repayments=1_600))
    assert high_debt.loc[0, "resilience_score"] < low_debt.loc[0, "resilience_score"]


def test_zero_income_does_not_crash_and_score_is_valid() -> None:
    scored = calculate_resilience_score(_household(monthly_income=0))
    score = scored.loc[0, "resilience_score"]
    assert 0.0 <= score <= 100.0
    assert scored.loc[0, "risk_band"] in {"Stable", "Watch", "Vulnerable", "Critical"}


def test_all_sub_scores_clipped_between_0_and_100() -> None:
    from moneybuffer.resilience.score import SUB_SCORE_COLUMNS

    extreme_household = _household(
        monthly_income=0,
        savings_balance=0,
        debt_repayments=5_000,
        discretionary_spending=5_000,
    )
    scored = calculate_resilience_score(extreme_household)
    for col in SUB_SCORE_COLUMNS:
        val = scored.loc[0, col]
        assert 0.0 <= val <= 100.0, f"{col} = {val} is outside [0, 100]"


def test_resilience_score_itself_clipped_between_0_and_100() -> None:
    extreme = _household(
        monthly_income=500,
        debt_repayments=2_000,
        savings_balance=0,
        discretionary_spending=1_000,
    )
    scored = calculate_resilience_score(extreme)
    assert 0.0 <= scored.loc[0, "resilience_score"] <= 100.0
