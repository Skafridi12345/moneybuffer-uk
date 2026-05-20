"""Trusted UK support resources for educational signposting."""

from __future__ import annotations

from typing import Any, NotRequired, TypedDict

import pandas as pd


class SupportLink(TypedDict):
    """A trusted UK support resource shown for educational signposting."""

    name: str
    url: str
    use_case: str
    reason: NotRequired[str]


SUPPORT_RESOURCES: tuple[SupportLink, ...] = (
    {
        "name": "MoneyHelper",
        "url": "https://www.moneyhelper.org.uk/",
        "use_case": "Budgeting, debt guidance, pensions, benefits, and money problems.",
    },
    {
        "name": "StepChange Debt Charity",
        "url": "https://www.stepchange.org/",
        "use_case": "Free debt advice.",
    },
    {
        "name": "Citizens Advice",
        "url": "https://www.citizensadvice.org.uk/",
        "use_case": "Debt, benefits, bills, and consumer rights.",
    },
    {
        "name": "National Debtline",
        "url": "https://www.nationaldebtline.org/",
        "use_case": "Free debt advice.",
    },
    {
        "name": "Action Fraud",
        "url": "https://www.actionfraud.police.uk/",
        "use_case": "Report fraud and cyber crime.",
    },
    {
        "name": "FCA ScamSmart",
        "url": "https://www.fca.org.uk/scamsmart",
        "use_case": "Investment and pension scam checks.",
    },
    {
        "name": "FCA Financial Services Register",
        "url": "https://register.fca.org.uk/",
        "use_case": "Check whether a firm or individual is authorised.",
    },
)

_RESOURCE_BY_NAME: dict[str, SupportLink] = {
    resource["name"]: resource for resource in SUPPORT_RESOURCES
}


def _row_value(row: pd.Series, key: str, default: Any = 0) -> Any:
    return row[key] if key in row else default


def _add_resource(
    resources: list[SupportLink],
    resource_name: str,
    reason: str,
) -> None:
    resource: SupportLink = {**_RESOURCE_BY_NAME[resource_name]}
    resource["reason"] = reason
    if resource["name"] not in {item["name"] for item in resources}:
        resources.append(resource)


def get_relevant_support_links(
    row: pd.Series,
    scam_result: dict[str, Any] | None = None,
) -> list[SupportLink]:
    """Return relevant UK support links based on household and scam-risk signals."""

    links: list[SupportLink] = []

    debt_service_ratio = float(_row_value(row, "debt_service_ratio", 0))
    monthly_surplus = float(_row_value(row, "monthly_surplus", 0))
    emergency_runway_months = float(_row_value(row, "emergency_runway_months", 0))
    essential_spending_ratio = float(_row_value(row, "essential_spending_ratio", 0))

    if debt_service_ratio > 0.30:
        reason = "Debt repayments appear high relative to monthly income."
        _add_resource(links, "StepChange Debt Charity", reason)
        _add_resource(links, "National Debtline", reason)

    if monthly_surplus < 0:
        reason = "Estimated monthly cashflow is negative in this scenario."
        _add_resource(links, "MoneyHelper", reason)
        _add_resource(links, "Citizens Advice", reason)
        _add_resource(links, "StepChange Debt Charity", reason)

    if emergency_runway_months < 1:
        reason = "Emergency savings appear to provide less than one month of runway."
        _add_resource(links, "MoneyHelper", reason)
        _add_resource(links, "Citizens Advice", reason)

    if essential_spending_ratio > 0.70:
        reason = "Essential costs appear to consume a high share of income."
        _add_resource(links, "MoneyHelper", reason)
        _add_resource(links, "Citizens Advice", reason)

    if not scam_result:
        return links

    scam_risk_band = str(scam_result.get("risk_band", "Low"))
    scam_type = str(scam_result.get("scam_type", "")).lower()

    if scam_risk_band in {"High", "Severe"}:
        _add_resource(
            links,
            "Action Fraud",
            "The scam checker found high or severe risk indicators.",
        )

    if any(term in scam_type for term in ("investment", "crypto", "pension")):
        reason = "The scam type suggests an investment, crypto, or pension scam risk."
        _add_resource(links, "FCA ScamSmart", reason)
        _add_resource(links, "FCA Financial Services Register", reason)

    if any(term in scam_type for term in ("invoice", "bank-detail", "bank detail")):
        reason = "The scam type suggests an invoice or bank-detail-change risk."
        _add_resource(links, "Action Fraud", reason)
        _add_resource(links, "FCA Financial Services Register", reason)

    return links
