"""Tests for the PDF report generator."""

from __future__ import annotations

from typing import Any

import pandas as pd
import pytest

from moneybuffer.reporting.pdf_report import FIXED_SUPPORT_LINKS, build_pdf_report

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scored_row(**overrides: Any) -> pd.Series:
    """Minimal scored household row sufficient for all report sections."""
    data: dict[str, Any] = {
        "household_id": "HH00001",
        "household_type": "Stable Household",
        "monthly_income": 4_000,
        "resilience_score": 72.5,
        "risk_band": "Watch",
        "emergency_runway_months": 4.8,
        "monthly_surplus": 420.0,
        "essential_spending_ratio": 0.50,
        "debt_service_ratio": 0.08,
        # sub-scores needed by explain_score
        "emergency_runway_score": 80.0,
        "essential_spending_score": 78.0,
        "debt_service_score": 86.0,
        "surplus_score": 75.0,
        "credit_dependency_score": 92.0,
        "credit_dependency_ratio": 0.04,
    }
    data.update(overrides)
    return pd.Series(data)


def _action_plan(**overrides: Any) -> dict[str, Any]:
    plan: dict[str, Any] = {
        "urgent_actions": [],
        "medium_term_actions": ["Review your budget monthly."],
        "positive_actions": ["Emergency savings cover several months."],
        "support_links": [],
        "disclaimer": "Educational tool only.",
    }
    plan.update(overrides)
    return plan


def _scam_result(risk_band: str = "High") -> dict[str, Any]:
    return {
        "risk_score": 68,
        "risk_band": risk_band,
        "scam_type": "Bank impersonation scam",
        "red_flags": [
            {"label": "Urgency language", "matches": ["urgent", "immediately"]},
            {"label": "Risky payment method", "matches": ["bank transfer"]},
        ],
        "recommended_action": "Verify through official channels before acting.",
    }


def _build(**kwargs: Any) -> bytes:
    """Convenience wrapper: build a PDF and return the bytes."""
    row = kwargs.pop("row", _scored_row())
    plan = kwargs.pop("plan", _action_plan())
    scam = kwargs.pop("scam", None)
    return build_pdf_report(row, plan, scam)


# ---------------------------------------------------------------------------
# Core output contract
# ---------------------------------------------------------------------------


def test_pdf_returns_bytes() -> None:
    result = _build()
    assert isinstance(result, bytes)


def test_pdf_is_not_empty() -> None:
    result = _build()
    assert len(result) > 500, f"PDF too small: {len(result)} bytes"


def test_pdf_starts_with_pdf_magic_bytes() -> None:
    result = _build()
    assert result[:5] == b"%PDF-", "File does not start with PDF magic bytes"


# ---------------------------------------------------------------------------
# Works without scam result
# ---------------------------------------------------------------------------


def test_pdf_without_scam_result_does_not_raise() -> None:
    result = build_pdf_report(_scored_row(), _action_plan(), scam_result=None)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_pdf_without_scam_result_is_valid_pdf() -> None:
    result = build_pdf_report(_scored_row(), _action_plan(), scam_result=None)
    assert result[:5] == b"%PDF-"


# ---------------------------------------------------------------------------
# Works with scam result
# ---------------------------------------------------------------------------


def test_pdf_with_scam_result_does_not_raise() -> None:
    result = build_pdf_report(_scored_row(), _action_plan(), scam_result=_scam_result())
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_pdf_with_scam_result_is_larger_than_without() -> None:
    without = build_pdf_report(_scored_row(), _action_plan(), scam_result=None)
    with_scam = build_pdf_report(
        _scored_row(), _action_plan(), scam_result=_scam_result()
    )
    assert len(with_scam) > len(without), (
        "PDF with scam section should be larger than PDF without"
    )


def test_pdf_with_severe_scam_risk() -> None:
    result = build_pdf_report(
        _scored_row(),
        _action_plan(),
        scam_result=_scam_result(risk_band="Severe"),
    )
    assert isinstance(result, bytes)
    assert result[:5] == b"%PDF-"


# ---------------------------------------------------------------------------
# Handles edge-case inputs without crashing
# ---------------------------------------------------------------------------


def test_pdf_with_urgent_actions() -> None:
    plan = _action_plan(
        urgent_actions=[
            "Consider contacting free debt advice support.",
            "You may want to contact creditors or providers early.",
        ]
    )
    result = build_pdf_report(_scored_row(), plan)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_pdf_with_critical_household() -> None:
    row = _scored_row(
        risk_band="Critical",
        resilience_score=22.0,
        emergency_runway_months=0.3,
        monthly_surplus=-180.0,
    )
    plan = _action_plan(
        urgent_actions=[
            "Consider reviewing essential bills.",
            "If struggling, consider free debt advice.",
        ]
    )
    result = build_pdf_report(row, plan, scam_result=_scam_result("Severe"))
    assert isinstance(result, bytes)
    assert result[:5] == b"%PDF-"


def test_pdf_with_missing_optional_fields() -> None:
    # Scored row without household_id — should omit that line gracefully.
    row = _scored_row()
    row = row.drop("household_id")
    result = build_pdf_report(row, _action_plan())
    assert isinstance(result, bytes)
    assert result[:5] == b"%PDF-"


def test_pdf_with_empty_action_plan() -> None:
    plan = _action_plan(urgent_actions=[], medium_term_actions=[], positive_actions=[])
    result = build_pdf_report(_scored_row(), plan)
    assert isinstance(result, bytes)


def test_pdf_with_negative_surplus() -> None:
    row = _scored_row(monthly_surplus=-350.0)
    result = build_pdf_report(row, _action_plan())
    assert isinstance(result, bytes)
    assert result[:5] == b"%PDF-"


def test_pdf_with_scam_result_missing_red_flags_key() -> None:
    # Minimal scam dict — should not crash on absent red_flags key.
    scam = {"risk_score": 50, "risk_band": "High", "scam_type": "Unknown"}
    result = build_pdf_report(_scored_row(), _action_plan(), scam_result=scam)
    assert isinstance(result, bytes)


# ---------------------------------------------------------------------------
# FIXED_SUPPORT_LINKS sanity
# ---------------------------------------------------------------------------


def test_fixed_support_links_contains_five_entries() -> None:
    assert len(FIXED_SUPPORT_LINKS) == 5


@pytest.mark.parametrize(
    "name",
    [
        "MoneyHelper",
        "StepChange Debt Charity",
        "Citizens Advice",
        "Action Fraud",
        "FCA ScamSmart",
    ],
)
def test_fixed_support_links_contains_expected_service(name: str) -> None:
    names = {entry[0] for entry in FIXED_SUPPORT_LINKS}
    assert name in names, f"Expected '{name}' in FIXED_SUPPORT_LINKS"
