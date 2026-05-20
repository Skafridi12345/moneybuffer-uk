import pandas as pd

from moneybuffer.recommendations.support_links import (
    SupportLink,
    get_relevant_support_links,
)


def _row(**overrides: float | str) -> pd.Series:
    data: dict[str, float | str] = {
        "risk_band": "Stable",
        "emergency_runway_months": 6.0,
        "debt_service_ratio": 0.05,
        "monthly_surplus": 500.0,
        "credit_dependency_ratio": 0.05,
        "essential_spending_ratio": 0.45,
    }
    data.update(overrides)
    return pd.Series(data)


def _link_names(links: list[SupportLink]) -> set[str]:
    return {link["name"] for link in links}


def test_high_debt_burden_returns_debt_support_links() -> None:
    links = get_relevant_support_links(_row(debt_service_ratio=0.36))
    names = _link_names(links)

    assert "StepChange Debt Charity" in names or "National Debtline" in names


def test_high_scam_risk_returns_action_fraud() -> None:
    links = get_relevant_support_links(
        _row(),
        {"risk_band": "High", "scam_type": "Bank impersonation scam"},
    )

    assert "Action Fraud" in _link_names(links)


def test_investment_scam_returns_fca_resources() -> None:
    links = get_relevant_support_links(
        _row(),
        {"risk_band": "Severe", "scam_type": "Investment scam"},
    )
    names = _link_names(links)

    assert "FCA ScamSmart" in names
    assert "FCA Financial Services Register" in names


def test_invoice_redirection_returns_relevant_reporting_links() -> None:
    links = get_relevant_support_links(
        _row(),
        {"risk_band": "Severe", "scam_type": "Invoice redirection scam"},
    )
    names = _link_names(links)

    assert "Action Fraud" in names
    assert "FCA Financial Services Register" in names


def test_stable_household_gets_no_excessive_support_links() -> None:
    links = get_relevant_support_links(_row())

    assert links == []
