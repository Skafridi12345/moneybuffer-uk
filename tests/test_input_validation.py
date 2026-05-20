"""Tests for household input validation."""

from __future__ import annotations

import pandas as pd
import pytest

from moneybuffer.validation.input_validation import (
    FIELD_BOUNDS,
    validate_household_inputs,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _household(**overrides: float) -> pd.Series:
    """Return a raw household Series with sensible defaults for a stable household."""
    data: dict[str, float] = {
        "monthly_income": 4_000,
        "rent_or_mortgage": 900,
        "council_tax": 160,
        "energy_bill": 160,
        "water_bill": 40,
        "broadband_phone": 45,
        "groceries": 420,
        "transport": 180,
        "insurance": 90,
        "subscriptions": 40,
        "discretionary_spending": 250,
        "debt_repayments": 100,
        "savings_balance": 18_000,
        "overdraft_balance": 0,
        "credit_card_balance": 200,
    }
    data.update(overrides)
    return pd.Series(data)


def _warnings(row: pd.Series) -> list[str]:
    return validate_household_inputs(row)


def _combined_text(row: pd.Series) -> str:
    return " ".join(_warnings(row)).lower()


# ---------------------------------------------------------------------------
# FIELD_BOUNDS sanity checks
# ---------------------------------------------------------------------------


def test_field_bounds_covers_all_editable_fields() -> None:
    expected = {
        "monthly_income",
        "rent_or_mortgage",
        "council_tax",
        "energy_bill",
        "water_bill",
        "broadband_phone",
        "groceries",
        "transport",
        "insurance",
        "subscriptions",
        "discretionary_spending",
        "debt_repayments",
        "savings_balance",
        "overdraft_balance",
        "credit_card_balance",
    }
    assert set(FIELD_BOUNDS.keys()) == expected


def test_field_bounds_min_is_zero_for_all_fields() -> None:
    for field, (lo, _) in FIELD_BOUNDS.items():
        assert lo == 0, f"Expected min=0 for {field}, got {lo}"


def test_field_bounds_max_is_positive_for_all_fields() -> None:
    for field, (_, hi) in FIELD_BOUNDS.items():
        assert hi > 0, f"Expected positive max for {field}, got {hi}"


# ---------------------------------------------------------------------------
# Warning: zero income
# ---------------------------------------------------------------------------


def test_zero_income_triggers_warning() -> None:
    row = _household(monthly_income=0)
    warnings = _warnings(row)
    assert any(w for w in warnings), "Expected at least one warning for zero income"
    assert any("zero" in w.lower() or "income" in w.lower() for w in warnings)


def test_zero_income_warning_mentions_ratios() -> None:
    text = _combined_text(_household(monthly_income=0))
    assert "ratio" in text, "Expected mention of ratios being affected by zero income"


def test_zero_income_does_not_raise() -> None:
    # Must not crash — warnings only, never exceptions
    result = validate_household_inputs(_household(monthly_income=0))
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Warning: essential spending exceeds income
# ---------------------------------------------------------------------------


def test_essentials_exceed_income_triggers_warning() -> None:
    # Rent alone (3500) exceeds income (2000)
    row = _household(monthly_income=2_000, rent_or_mortgage=3_500)
    text = _combined_text(row)
    assert "essential" in text or "exceed" in text, (
        "Expected a warning when essential spending exceeds income"
    )


def test_essentials_exceed_income_names_both_values() -> None:
    row = _household(monthly_income=1_000, rent_or_mortgage=2_000)
    text = _combined_text(row)
    # Warning should include both the essential figure and the income figure
    assert "1,000" in text or "2,000" in text


def test_essentials_exceed_income_not_triggered_when_income_zero() -> None:
    # When income is zero the 'essentials exceed income' check is suppressed
    # (the zero-income warning already covers it); avoid a misleading double warning.
    row = _household(monthly_income=0, rent_or_mortgage=3_500)
    texts = [w.lower() for w in _warnings(row)]
    # The zero-income warning fires but the essentials>income check should not
    # independently fire when income is exactly zero.
    assert not any("essential" in t and "exceed" in t for t in texts), (
        "Should not fire the essentials-exceed-income warning when income is zero"
    )


# ---------------------------------------------------------------------------
# Warning: high debt service ratio
# ---------------------------------------------------------------------------


def test_high_debt_service_ratio_triggers_warning() -> None:
    # debt_repayments / income = 1800 / 3000 = 60% > 40%
    row = _household(monthly_income=3_000, debt_repayments=1_800)
    text = _combined_text(row)
    assert "debt" in text and ("40%" in text or "threshold" in text), (
        "Expected a high-debt warning mentioning the 40% threshold"
    )


def test_high_debt_service_ratio_shows_percentage() -> None:
    row = _household(monthly_income=2_000, debt_repayments=1_000)
    text = _combined_text(row)
    assert "50%" in text, "Expected the actual ratio (50%) to appear in the warning"


def test_debt_below_threshold_does_not_trigger_warning() -> None:
    # 10% debt service ratio — well within acceptable range
    row = _household(monthly_income=4_000, debt_repayments=400)
    texts = [w.lower() for w in _warnings(row)]
    assert not any("40%" in t or "debt pressure" in t for t in texts)


# ---------------------------------------------------------------------------
# Warning: zero savings
# ---------------------------------------------------------------------------


def test_zero_savings_triggers_warning() -> None:
    row = _household(savings_balance=0)
    text = _combined_text(row)
    assert "savings" in text and "zero" in text, (
        "Expected a warning when savings_balance is zero"
    )


def test_zero_savings_mentions_emergency_runway() -> None:
    text = _combined_text(_household(savings_balance=0))
    assert "runway" in text or "buffer" in text or "emergency" in text


def test_nonzero_savings_does_not_trigger_savings_warning() -> None:
    row = _household(savings_balance=500)
    texts = [w.lower() for w in _warnings(row)]
    assert not any("savings balance is zero" in t for t in texts)


# ---------------------------------------------------------------------------
# Warning: negative monthly cashflow
# ---------------------------------------------------------------------------


def test_negative_surplus_triggers_warning() -> None:
    # income=2000, essentials=1995, discretionary=500 → surplus is negative
    # but essentials do not exceed income, so this is a standalone surplus warning
    row = _household(
        monthly_income=2_000,
        rent_or_mortgage=900,
        council_tax=160,
        energy_bill=160,
        water_bill=40,
        broadband_phone=45,
        groceries=420,
        transport=180,
        insurance=90,
        subscriptions=100,
        discretionary_spending=600,
        debt_repayments=0,
    )
    text = _combined_text(row)
    assert "negative" in text or "cashflow" in text or "exceed" in text


# ---------------------------------------------------------------------------
# Normal household produces no warnings
# ---------------------------------------------------------------------------


def test_normal_stable_household_produces_no_warnings() -> None:
    # Stable Household: strong income, modest essential costs, solid savings.
    # No threshold should fire.
    row = _household()
    assert _warnings(row) == [], (
        f"Expected no warnings for a healthy household, got: {_warnings(row)}"
    )


def test_warnings_returns_list_type() -> None:
    assert isinstance(validate_household_inputs(_household()), list)


# ---------------------------------------------------------------------------
# Works on scored rows (pre-computed derived features)
# ---------------------------------------------------------------------------


def test_validate_works_on_scored_row() -> None:
    """validate_household_inputs should accept a scored row without crashing."""
    from moneybuffer.resilience.score import calculate_resilience_score

    scored = calculate_resilience_score(pd.DataFrame([_household().to_dict()]))
    scored_row = scored.iloc[0]

    # Should not raise
    result = validate_household_inputs(scored_row)
    assert isinstance(result, list)


def test_validate_scored_row_uses_precomputed_surplus() -> None:
    """Pre-computed monthly_surplus in a scored row should drive the surplus warning."""
    from moneybuffer.resilience.score import calculate_resilience_score

    # Construct a row where the surplus will be negative after scoring
    row = _household(
        monthly_income=2_000,
        discretionary_spending=1_500,
        debt_repayments=800,
    )
    scored = calculate_resilience_score(pd.DataFrame([row.to_dict()]))
    scored_row = scored.iloc[0]

    assert float(scored_row["monthly_surplus"]) < 0
    text = " ".join(validate_household_inputs(scored_row)).lower()
    assert "negative" in text or "cashflow" in text or "exceed" in text


# ---------------------------------------------------------------------------
# Multiple warnings can fire simultaneously
# ---------------------------------------------------------------------------


def test_multiple_warnings_for_severely_distressed_household() -> None:
    row = _household(
        monthly_income=1_000,
        rent_or_mortgage=1_200,  # essentials > income
        debt_repayments=500,  # debt_service_ratio > 40%
        savings_balance=0,  # zero savings
    )
    warnings = _warnings(row)
    assert len(warnings) >= 2, (
        f"Expected multiple warnings for a severely distressed household, "
        f"got {len(warnings)}: {warnings}"
    )


@pytest.mark.parametrize(
    "field,extreme_value",
    [
        ("monthly_income", 0),
        ("savings_balance", 0),
        ("debt_repayments", 9_000),
    ],
)
def test_extreme_values_do_not_raise(field: str, extreme_value: float) -> None:
    """Validation must never raise an exception, only return warnings."""
    row = _household(**{field: extreme_value})
    result = validate_household_inputs(row)
    assert isinstance(result, list)
