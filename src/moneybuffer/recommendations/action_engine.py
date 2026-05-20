"""Educational action-plan generation for MoneyBuffer UK."""

from __future__ import annotations

from typing import Any, TypedDict

import pandas as pd

from moneybuffer.recommendations.support_links import (
    SupportLink,
    get_relevant_support_links,
)


class ActionPlan(TypedDict):
    """Grouped educational action plan returned by the action engine."""

    urgent_actions: list[str]
    medium_term_actions: list[str]
    positive_actions: list[str]
    support_links: list[SupportLink]
    disclaimer: str


DISCLAIMER = (
    "MoneyBuffer UK is an educational tool only and does not provide regulated "
    "financial advice, debt advice, investment advice, credit broking, insurance "
    "advice, or personalised product recommendations."
)


def _value(row: pd.Series, key: str, default: Any = 0) -> Any:
    return row[key] if key in row else default


def generate_financial_actions(row: pd.Series) -> list[str]:
    """Generate cautious educational financial actions from a scored household row."""

    actions: list[str] = []
    risk_band = str(_value(row, "risk_band", ""))
    emergency_runway_months = float(_value(row, "emergency_runway_months", 0))
    debt_service_ratio = float(_value(row, "debt_service_ratio", 0))
    monthly_surplus = float(_value(row, "monthly_surplus", 0))
    credit_dependency_ratio = float(_value(row, "credit_dependency_ratio", 0))
    essential_spending_ratio = float(_value(row, "essential_spending_ratio", 0))

    if risk_band == "Critical":
        actions.extend(
            [
                (
                    "Consider reviewing essential bills to identify any immediate "
                    "pressure points."
                ),
                (
                    "You may want to contact creditors or providers early if payment "
                    "difficulty is likely."
                ),
                (
                    "If you are struggling, consider contacting free debt advice "
                    "support from a reputable UK charity or public service."
                ),
            ]
        )

    if emergency_runway_months < 1:
        actions.append(
            "Your emergency savings cover about "
            f"{emergency_runway_months:.1f} months of essential spending, leaving "
            "little buffer for an unexpected bill or income disruption. You may "
            "want to consider building an emergency buffer before increasing "
            "discretionary spending."
        )

    if debt_service_ratio > 0.30:
        actions.append(
            "Your debt repayments are approximately "
            f"{debt_service_ratio:.0%} of monthly income, which suggests debt "
            "commitments may be placing pressure on your household budget. It "
            "may be sensible to review high-interest debt commitments and free "
            "debt support options."
        )

    if monthly_surplus < 0:
        actions.append(
            "Your estimated monthly cashflow is negative by approximately "
            f"£{abs(monthly_surplus):,.0f}, meaning spending and commitments "
            "exceed income in this scenario. You may want to identify immediate "
            "spending reductions or support options."
        )

    if essential_spending_ratio > 0.70:
        actions.append(
            "Essential costs consume approximately "
            f"{essential_spending_ratio:.0%} of income, leaving limited "
            "flexibility. Consider reviewing core bills and checking whether "
            "support schemes or tariff changes may be available."
        )

    if credit_dependency_ratio > 0.5:
        actions.append(
            "Consider reviewing reliance on overdraft or credit card borrowing."
        )

    if not actions:
        actions.append(
            "Consider maintaining regular budget check-ins and reviewing your "
            "emergency buffer."
        )

    return actions


def generate_scam_actions(scam_result: dict[str, Any]) -> list[str]:
    """Generate cautious educational scam-risk actions."""

    scam_risk_band = str(scam_result.get("risk_band", "Low"))
    if scam_risk_band not in {"High", "Severe"}:
        return [
            (
                "It may be sensible to verify unexpected payment requests through "
                "official channels."
            )
        ]

    return [
        (
            "Consider pausing before sending money or sharing personal details "
            "until the request is verified."
        ),
        (
            "Verify the request through official channels, not links or numbers "
            "in the message."
        ),
        (
            "If payment has already been made, consider contacting your bank as "
            "soon as possible."
        ),
        "Consider reporting the suspicious message through official reporting routes.",
    ]


_CROSS_FEATURE_ALERT = (
    "This household is already financially vulnerable, and the message shows high "
    "scam-risk indicators. A mistaken payment could materially reduce the available "
    "safety buffer. Pause before sending money, verify through official channels, "
    "and contact your bank immediately if money has already been sent."
)


def generate_cross_feature_alert(
    row: pd.Series,
    scam_result: dict[str, Any] | None,
) -> str | None:
    """Return a combined alert when financial vulnerability meets high scam risk.

    Returns ``None`` when either condition is absent, so callers can show the
    alert only when both signals are present simultaneously.
    """
    financial_risk_band = str(_value(row, "risk_band", ""))
    scam_risk_band = str(scam_result.get("risk_band", "")) if scam_result else ""

    if financial_risk_band in {"Vulnerable", "Critical"} and scam_risk_band in {
        "High",
        "Severe",
    }:
        return _CROSS_FEATURE_ALERT

    return None


def generate_combined_action_plan(
    row: pd.Series,
    scam_result: dict[str, Any] | None = None,
) -> ActionPlan:
    """Create a grouped educational action plan from financial and scam-risk signals."""

    financial_actions = generate_financial_actions(row)
    scam_actions = generate_scam_actions(scam_result) if scam_result else []
    support_links = get_relevant_support_links(row, scam_result)

    urgent_actions: list[str] = []
    medium_term_actions: list[str] = []
    positive_actions: list[str] = []

    risk_band = str(_value(row, "risk_band", ""))
    monthly_surplus = float(_value(row, "monthly_surplus", 0))
    emergency_runway_months = float(_value(row, "emergency_runway_months", 0))
    scam_risk_band = str(scam_result.get("risk_band", "Low")) if scam_result else "Low"

    if risk_band == "Critical" or monthly_surplus < 0:
        urgent_actions.extend(
            action
            for action in financial_actions
            if "debt advice" in action
            or "immediate" in action
            or "contact creditors" in action
            or "support options" in action
        )

    if scam_risk_band in {"High", "Severe"}:
        urgent_actions.extend(scam_actions)

    medium_term_actions.extend(
        action
        for action in financial_actions
        if action not in urgent_actions
        and not action.startswith("Consider maintaining regular budget check-ins")
    )

    if not urgent_actions and risk_band in {"Stable", "Watch"}:
        positive_actions.append(
            "You may want to keep monitoring your budget and emergency savings "
            "over time."
        )

    if emergency_runway_months >= 3:
        positive_actions.append(
            "Your emergency savings appear to cover several months of essential "
            "spending."
        )

    if not positive_actions:
        positive_actions.append(
            "Small, regular reviews can help make financial pressure visible earlier."
        )

    return {
        "urgent_actions": urgent_actions,
        "medium_term_actions": medium_term_actions,
        "positive_actions": positive_actions,
        "support_links": support_links,
        "disclaimer": DISCLAIMER,
    }
