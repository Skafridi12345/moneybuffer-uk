"""Transparent rule-based scam red-flag detection."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ScamRule:
    """A weighted text rule for scam-risk detection."""

    category: str
    label: str
    patterns: tuple[str, ...]
    weight: int


SCAM_RULES: tuple[ScamRule, ...] = (
    ScamRule(
        category="urgency",
        label="Urgency or pressure language",
        patterns=(
            "urgent",
            "immediately",
            "today only",
            "final warning",
            "account will be closed",
            "act now",
        ),
        weight=18,
    ),
    ScamRule(
        category="secrecy",
        label="Secrecy request",
        patterns=("do not tell anyone", "keep this private", "confidential"),
        weight=22,
    ),
    ScamRule(
        category="risky_payment_method",
        label="Risky payment method",
        patterns=(
            "bank transfer",
            "gift card",
            "crypto",
            "bitcoin",
            "friends and family",
        ),
        weight=24,
    ),
    ScamRule(
        category="off_platform_request",
        label="Off-platform request",
        patterns=(
            "pay outside ebay",
            "message me on whatsapp",
            "avoid platform fees",
            "friends and family",
        ),
        weight=24,
    ),
    ScamRule(
        category="impersonation",
        label="Organisation or authority impersonation cue",
        patterns=(
            "hmrc",
            "bank",
            "police",
            "delivery company",
            "royal mail",
            "dpd",
            "evri",
        ),
        weight=14,
    ),
    ScamRule(
        category="bank_impersonation",
        label="Bank impersonation cue",
        patterns=(
            "account will be closed",
            "verify your bank account",
            "bank account is locked",
            "suspicious bank activity",
            "online banking suspended",
        ),
        weight=24,
    ),
    ScamRule(
        category="hmrc_tax_refund",
        label="HMRC or tax refund cue",
        patterns=(
            "hmrc refund",
            "tax refund",
            "tax rebate",
            "claim your refund",
            "hmrc final warning",
        ),
        weight=24,
    ),
    ScamRule(
        category="delivery_scam",
        label="Delivery scam cue",
        patterns=(
            "royal mail",
            "dpd",
            "evri",
            "delivery fee",
            "parcel redelivery",
            "missed delivery",
        ),
        weight=22,
    ),
    ScamRule(
        category="marketplace_scam",
        label="Marketplace purchase scam cue",
        patterns=(
            "pay outside ebay",
            "avoid platform fees",
            "facebook marketplace",
            "gumtree",
            "vinted",
            "friends and family",
        ),
        weight=24,
    ),
    ScamRule(
        category="romance_scam",
        label="Romance or emotional manipulation cue",
        patterns=(
            "i need help urgently",
            "i cannot access my money",
            "send money for travel",
            "my account is frozen",
            "i love you but need help",
        ),
        weight=28,
    ),
    ScamRule(
        category="pig_butchering_crypto",
        label="Pig-butchering or long-con crypto cue",
        patterns=(
            "guaranteed returns",
            "crypto opportunity",
            "trading platform",
            "mentor",
            "withdrawal fee",
            "tax to release funds",
            "risk free",
        ),
        weight=30,
    ),
    ScamRule(
        category="fake_job_task",
        label="Fake recruitment or task scam cue",
        patterns=(
            "earn money from home",
            "simple task",
            "telegram job",
            "whatsapp recruiter",
            "pay a deposit",
            "unlock commission",
            "work only 30 minutes",
        ),
        weight=28,
    ),
    ScamRule(
        category="app_impersonation",
        label="Authorised push payment impersonation cue",
        patterns=(
            "safe account",
            "move your money",
            "fraud team",
            "your account is compromised",
            "new payee",
        ),
        weight=30,
    ),
    ScamRule(
        category="suspicious_link",
        label="Suspicious or shortened link",
        patterns=(
            r"\bbit\.ly\b",
            r"\btinyurl\.com\b",
            r"https?://[^\s]*(?:verify|secure|login|account|refund)[^\s]*",
            r"https?://(?:\d{1,3}\.){3}\d{1,3}[^\s]*",
        ),
        weight=22,
    ),
    ScamRule(
        category="investment_scam",
        label="Investment scam phrase",
        patterns=(
            "guaranteed returns",
            "double your money",
            "risk free investment",
            "crypto opportunity",
            "trading platform",
        ),
        weight=30,
    ),
    ScamRule(
        category="invoice_redirection",
        label="Invoice or bank-detail change",
        patterns=("new bank details", "changed account", "pay this account instead"),
        weight=46,
    ),
)


def _pattern_match(message: str, pattern: str) -> str | None:
    if pattern.startswith(("http", r"\b", r"https?")) or "\\" in pattern:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if match is None:
            return None
        return match.group(0)
    if pattern in message:
        return pattern
    return None


def detect_red_flags(message: str) -> list[dict[str, Any]]:
    """Detect transparent scam red flags in a message."""

    normalised_message = message.lower()
    red_flags: list[dict[str, Any]] = []

    for rule in SCAM_RULES:
        matched_patterns = [
            match
            for pattern in rule.patterns
            if (match := _pattern_match(normalised_message, pattern.lower()))
        ]
        if matched_patterns:
            red_flags.append(
                {
                    "category": rule.category,
                    "label": rule.label,
                    "matches": matched_patterns,
                    "weight": rule.weight,
                }
            )

    return red_flags
