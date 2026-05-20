"""End-to-end integration tests covering the full MoneyBuffer UK MVP pipeline.

Each test walks through every stage in sequence:
  generate → select → score → stress → compare → scam-check → action-plan

These tests complement the existing unit tests by exercising module
boundaries and ensuring outputs flow correctly between layers.
"""

from __future__ import annotations

import pandas as pd
import pytest

from moneybuffer.data_generation.households import generate_households
from moneybuffer.recommendations.action_engine import generate_combined_action_plan
from moneybuffer.resilience.score import calculate_resilience_score
from moneybuffer.scams.classifier import calculate_scam_risk_score
from moneybuffer.stress_testing.income_shocks import apply_income_shock
from moneybuffer.stress_testing.scenario_engine import (
    COMPARISON_COLUMNS,
    compare_baseline_vs_stress,
)

VALID_RESILIENCE_BANDS = {"Stable", "Watch", "Vulnerable", "Critical"}
VALID_SCAM_BANDS = {"Low", "Medium", "High", "Severe"}

# An obvious high-risk message hitting urgency, secrecy, risky payment, and
# a suspicious shortlink — expected to score Severe or High.
HIGH_RISK_MESSAGE = (
    "URGENT: Your Barclays account will be suspended today. "
    "Please transfer your funds immediately via bank transfer to a safe account. "
    "Do not tell anyone about this. Verify now: http://bit.ly/secure-barclays"
)

# A routine, verifiable message with no scam indicators.
LOW_RISK_MESSAGE = (
    "Reminder from Highfield Dental: your appointment is on Tuesday at 10:30am. "
    "Please call 01234 567890 if you need to reschedule."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _select_household(df: pd.DataFrame, household_type: str) -> pd.DataFrame:
    """Return the first household matching the given type as a single-row DataFrame."""
    matches = df[df["household_type"] == household_type]
    assert not matches.empty, f"No household of type '{household_type}' in dataset"
    return matches.iloc[[0]].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Test 1 — Financially vulnerable household under income shock + scam risk
# ---------------------------------------------------------------------------


def test_full_pipeline_vulnerable_household_with_scam() -> None:
    """Full pipeline: Low Savings Renter, 40 % income drop, high-risk scam message."""

    # --- Step 1: Generate synthetic households ---
    households = generate_households(n=30, seed=42)

    assert isinstance(households, pd.DataFrame)
    assert len(households) >= 6, "Expected at least one of every archetype"
    assert "household_type" in households.columns

    # --- Step 2: Select one household ---
    baseline_df = _select_household(households, "Low Savings Renter")
    assert len(baseline_df) == 1

    # --- Step 3 & 4: Calculate resilience features and score ---
    scored = calculate_resilience_score(baseline_df)

    assert "resilience_score" in scored.columns
    assert "risk_band" in scored.columns

    resilience_score = float(scored.loc[0, "resilience_score"])
    risk_band = str(scored.loc[0, "risk_band"])

    assert 0.0 <= resilience_score <= 100.0, (
        f"resilience_score {resilience_score} outside [0, 100]"
    )
    assert risk_band in VALID_RESILIENCE_BANDS, f"Unexpected risk_band: {risk_band!r}"

    # Derived features required by later stages should be present
    for feature in (
        "essential_spending",
        "essential_spending_ratio",
        "debt_service_ratio",
        "monthly_surplus",
        "emergency_runway_months",
        "credit_dependency_ratio",
    ):
        assert feature in scored.columns, f"Missing feature column: {feature}"

    # --- Step 5: Assign risk band (already in scored; verify it is valid) ---
    assert risk_band in VALID_RESILIENCE_BANDS

    # --- Step 6: Run income shock scenario (40 % drop) ---
    stressed_df = apply_income_shock(baseline_df, pct_drop=0.40)

    assert len(stressed_df) == 1
    stressed_income = float(stressed_df.loc[0, "monthly_income"])
    baseline_income = float(baseline_df.loc[0, "monthly_income"])
    assert stressed_income == pytest.approx(baseline_income * 0.60, rel=1e-6)

    # --- Step 7: Compare baseline vs stressed results ---
    comparison = compare_baseline_vs_stress(baseline_df, stressed_df)

    assert isinstance(comparison, pd.DataFrame)
    assert len(comparison) == 1

    for col in COMPARISON_COLUMNS:
        assert col in comparison.columns, f"Missing comparison column: {col!r}"

    baseline_score = float(comparison.loc[0, "baseline_score"])
    stressed_score = float(comparison.loc[0, "stressed_score"])
    baseline_band = str(comparison.loc[0, "baseline_band"])
    stressed_band = str(comparison.loc[0, "stressed_band"])
    score_change = float(comparison.loc[0, "score_change"])

    assert 0.0 <= baseline_score <= 100.0
    assert 0.0 <= stressed_score <= 100.0
    assert baseline_band in VALID_RESILIENCE_BANDS
    assert stressed_band in VALID_RESILIENCE_BANDS

    # A 40 % income drop must never improve the resilience score.
    assert stressed_score <= baseline_score, (
        f"stressed_score ({stressed_score}) should not exceed "
        f"baseline_score ({baseline_score}) after an adverse income shock"
    )
    assert score_change <= 0.0, (
        f"score_change ({score_change}) should be non-positive for an adverse shock"
    )

    # --- Step 8: Run scam-risk checker on an obvious scam message ---
    scam_result = calculate_scam_risk_score(HIGH_RISK_MESSAGE)

    assert isinstance(scam_result, dict)
    expected_scam_keys = (
        "risk_score",
        "risk_band",
        "scam_type",
        "red_flags",
        "recommended_action",
    )
    for key in expected_scam_keys:
        assert key in scam_result, f"Missing key in scam_result: {key!r}"

    scam_risk_score = int(scam_result["risk_score"])
    scam_risk_band = str(scam_result["risk_band"])

    assert 0 <= scam_risk_score <= 100
    assert scam_risk_band in VALID_SCAM_BANDS
    assert scam_risk_band in {"High", "Severe"}, (
        f"Expected High or Severe scam band for an obvious scam, got {scam_risk_band!r}"
    )
    assert isinstance(scam_result["red_flags"], list)
    assert len(scam_result["red_flags"]) > 0, "Expected at least one red flag detected"

    # --- Step 9: Generate combined action plan ---
    scored_row = calculate_resilience_score(baseline_df).loc[0]
    action_plan = generate_combined_action_plan(scored_row, scam_result=scam_result)

    # --- Step 10: Assert all expected outputs exist and are sensible ---
    assert isinstance(action_plan, dict)
    for key in (
        "urgent_actions",
        "medium_term_actions",
        "positive_actions",
        "disclaimer",
    ):  # noqa: E501
        assert key in action_plan, f"Missing key in action_plan: {key!r}"

    assert isinstance(action_plan["urgent_actions"], list)
    assert isinstance(action_plan["medium_term_actions"], list)
    assert isinstance(action_plan["positive_actions"], list)
    assert isinstance(action_plan["disclaimer"], str)
    assert len(action_plan["disclaimer"]) > 0

    # With a High/Severe scam signal, urgent actions must include stop-and-verify
    # language so the user is warned before taking any financial action.
    urgent_text = " ".join(action_plan["urgent_actions"]).lower()
    assert scam_risk_band in {"High", "Severe"}
    assert len(action_plan["urgent_actions"]) > 0, (
        "Expected at least one urgent action when scam risk is High or Severe"
    )
    assert any(
        phrase in urgent_text
        for phrase in ("pause", "verify", "stop", "do not", "before sending")
    ), (
        f"Expected a stop-and-verify instruction in urgent_actions for a "
        f"{scam_risk_band} scam risk, got: {action_plan['urgent_actions']}"
    )


# ---------------------------------------------------------------------------
# Test 2 — Financially stable household with a low-risk message
# ---------------------------------------------------------------------------


def test_full_pipeline_stable_household_with_low_risk_message() -> None:
    """Full pipeline: Stable Household, no income shock, low-risk legitimate message."""

    # --- Step 1: Generate synthetic households ---
    households = generate_households(n=30, seed=42)

    assert isinstance(households, pd.DataFrame)
    assert len(households) >= 6

    # --- Step 2: Select a stable household ---
    baseline_df = _select_household(households, "Stable Household")
    assert len(baseline_df) == 1

    # --- Steps 3 & 4: Calculate resilience score ---
    scored = calculate_resilience_score(baseline_df)

    resilience_score = float(scored.loc[0, "resilience_score"])
    risk_band = str(scored.loc[0, "risk_band"])

    assert 0.0 <= resilience_score <= 100.0
    assert risk_band in VALID_RESILIENCE_BANDS
    assert risk_band != "Critical", (
        f"Stable Household should not be in Critical band, got {risk_band!r}"
    )

    # --- Step 5: Band is already assigned; confirm it is not the worst band ---
    assert risk_band in {"Stable", "Watch", "Vulnerable"}

    # --- Step 6 & 7: Apply a mild 20 % income shock and compare ---
    stressed_df = apply_income_shock(baseline_df, pct_drop=0.20)
    comparison = compare_baseline_vs_stress(baseline_df, stressed_df)

    baseline_score = float(comparison.loc[0, "baseline_score"])
    stressed_score = float(comparison.loc[0, "stressed_score"])

    assert 0.0 <= baseline_score <= 100.0
    assert 0.0 <= stressed_score <= 100.0
    # Adverse shock must not improve the score even for a strong household.
    assert stressed_score <= baseline_score

    # --- Step 8: Run scam checker on a legitimate message ---
    scam_result = calculate_scam_risk_score(LOW_RISK_MESSAGE)

    scam_risk_band = str(scam_result["risk_band"])

    assert scam_risk_band in VALID_SCAM_BANDS
    assert scam_risk_band in {"Low", "Medium"}, (
        f"Expected Low or Medium scam band for a legitimate message, "
        f"got {scam_risk_band!r}"
    )

    # --- Step 9: Generate combined action plan ---
    scored_row = scored.loc[0]
    action_plan = generate_combined_action_plan(scored_row, scam_result=scam_result)

    # --- Step 10: Verify outputs ---
    for key in (
        "urgent_actions",
        "medium_term_actions",
        "positive_actions",
        "disclaimer",
    ):  # noqa: E501
        assert key in action_plan, f"Missing key in action_plan: {key!r}"

    # A stable household with a low-risk message should have positive actions.
    assert len(action_plan["positive_actions"]) > 0, (
        "Expected positive actions for a stable household with no scam risk"
    )

    # No stop-and-verify urgency should be injected for a low-risk message.
    urgent_text = " ".join(action_plan["urgent_actions"]).lower()
    scam_stop_phrases = ("pause before sending", "verify the request through official")
    assert not any(phrase in urgent_text for phrase in scam_stop_phrases), (
        "Scam stop-and-verify actions should not appear for a Low/Medium scam risk"
    )

    assert isinstance(action_plan["disclaimer"], str)
    assert "educational" in action_plan["disclaimer"].lower()
