"""Rule-based scam-risk scoring and scam-type classification."""

from __future__ import annotations

from typing import Any

from moneybuffer.scams.rules import detect_red_flags

TYPE_LABELS = {
    "romance_scam": "Romance scam",
    "pig_butchering_crypto": "Pig-butchering crypto investment scam",
    "fake_job_task": "Job or task scam",
    "app_impersonation": "Authorised push payment impersonation scam",
    "marketplace_scam": "Marketplace scam",
    "invoice_redirection": "Invoice redirection scam",
    "delivery_scam": "Delivery scam",
    "hmrc_tax_refund": "HMRC/tax refund scam",
    "bank_impersonation": "Bank impersonation scam",
    "investment_scam": "Investment scam",
}

TYPE_CATEGORY_WEIGHTS = {
    "romance_scam": {"romance_scam": 5, "secrecy": 1, "risky_payment_method": 1},
    "pig_butchering_crypto": {
        "pig_butchering_crypto": 5,
        "investment_scam": 2,
        "risky_payment_method": 1,
    },
    "fake_job_task": {
        "fake_job_task": 5,
        "risky_payment_method": 1,
        "off_platform_request": 1,
    },
    "app_impersonation": {
        "app_impersonation": 5,
        "bank_impersonation": 2,
        "impersonation": 1,
    },
    "marketplace_scam": {"marketplace_scam": 5, "off_platform_request": 2},
    "invoice_redirection": {"invoice_redirection": 5},
    "delivery_scam": {"delivery_scam": 5, "impersonation": 1, "suspicious_link": 1},
    "hmrc_tax_refund": {"hmrc_tax_refund": 5, "impersonation": 1, "suspicious_link": 1},
    "bank_impersonation": {"bank_impersonation": 5, "impersonation": 1},
    "investment_scam": {"investment_scam": 5, "risky_payment_method": 1},
}

PIG_BUTCHERING_LONG_CON_CUES = {
    "crypto opportunity",
    "trading platform",
    "mentor",
    "withdrawal fee",
    "tax to release funds",
}


def _risk_band(score: int) -> str:
    if score <= 20:
        return "Low"
    if score <= 45:
        return "Medium"
    if score <= 70:
        return "High"
    return "Severe"


def classify_scam_type(message: str) -> str:
    """Classify the most likely scam type using weighted red-flag categories."""

    message_lower = message.lower()
    flags = detect_red_flags(message)
    categories = {str(flag["category"]) for flag in flags}
    pig_butchering_matches = {
        str(match).lower()
        for flag in flags
        if flag["category"] == "pig_butchering_crypto"
        for match in flag["matches"]
    }
    has_long_con_crypto_cue = bool(
        pig_butchering_matches.intersection(PIG_BUTCHERING_LONG_CON_CUES)
    )
    scores: dict[str, int] = {}

    for scam_type, category_weights in TYPE_CATEGORY_WEIGHTS.items():
        if scam_type == "pig_butchering_crypto" and not has_long_con_crypto_cue:
            category_weights = {
                category: weight
                for category, weight in category_weights.items()
                if category != "pig_butchering_crypto"
            }
        scores[scam_type] = sum(
            weight
            for category, weight in category_weights.items()
            if category in categories
        )

    # Lightweight keyword nudges catch short messages that may only partially
    # match the red-flag groups.
    keyword_nudges = {
        "pig_butchering_crypto": (
            "crypto opportunity",
            "trading platform",
            "mentor",
            "withdrawal fee",
            "tax to release funds",
        ),
        "delivery_scam": ("royal mail", "dpd", "evri", "delivery", "parcel"),
        "hmrc_tax_refund": ("hmrc", "tax refund", "tax rebate"),
        "bank_impersonation": (
            "account will be closed",
            "online banking suspended",
            "verify your bank account",
        ),
        "marketplace_scam": ("ebay", "facebook marketplace", "gumtree", "vinted"),
        "fake_job_task": ("job", "task", "commission", "remote work", "recruiter"),
        "romance_scam": ("i love you", "travel", "my account is frozen"),
        "app_impersonation": ("safe account", "fraud team", "move your money"),
        "invoice_redirection": ("invoice", "new bank details", "changed account"),
    }
    for scam_type, keywords in keyword_nudges.items():
        if any(keyword in message_lower for keyword in keywords):
            scores[scam_type] += 1

    best_type, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score > 1:
        return TYPE_LABELS[best_type]

    return "Unclassified or low-risk message"


def _recommended_action(risk_band: str) -> str:
    if risk_band in {"High", "Severe"}:
        return (
            "Consider pausing before paying, clicking links, or sharing personal "
            "details. Verify using an official website or phone number, and "
            "consider reporting the message."
        )
    if risk_band == "Medium":
        return (
            "It may be sensible to pause and verify the request through a trusted "
            "official channel before taking action."
        )
    return (
        "No major scam indicators were detected, but consider verifying unexpected "
        "requests."
    )


def calculate_scam_risk_score(message: str) -> dict[str, Any]:
    """Calculate a 0-100 scam-risk score from transparent red-flag rules."""

    red_flags = detect_red_flags(message)
    raw_score = sum(int(flag["weight"]) for flag in red_flags)
    risk_score = min(100, raw_score)
    risk_band = _risk_band(risk_score)

    return {
        "risk_score": risk_score,
        "risk_band": risk_band,
        "scam_type": classify_scam_type(message),
        "red_flags": red_flags,
        "recommended_action": _recommended_action(risk_band),
    }
