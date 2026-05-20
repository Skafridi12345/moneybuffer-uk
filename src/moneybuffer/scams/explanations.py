"""Human-readable explanations for scam-risk outputs."""

from __future__ import annotations

from moneybuffer.scams.rules import detect_red_flags

EXPLANATION_TEMPLATES = {
    "urgency": "The message uses urgency or pressure language.",
    "secrecy": "The message asks you to keep the request secret.",
    "risky_payment_method": (
        "The message asks for a risky or hard-to-reverse payment method."
    ),
    "off_platform_request": (
        "The message asks you to move payment or messaging off-platform."
    ),
    "impersonation": (
        "The message references an organisation or authority often impersonated "
        "by scammers."
    ),
    "bank_impersonation": "The message contains bank impersonation cues.",
    "hmrc_tax_refund": "The message contains HMRC or tax-refund scam cues.",
    "delivery_scam": "The message contains delivery or parcel scam cues.",
    "marketplace_scam": "The message contains marketplace purchase scam cues.",
    "romance_scam": "The message contains romance or emotional manipulation cues.",
    "pig_butchering_crypto": (
        "The message contains long-con crypto or pig-butchering scam cues."
    ),
    "fake_job_task": "The message contains fake recruitment or task scam cues.",
    "app_impersonation": (
        "The message contains authorised push payment impersonation cues."
    ),
    "suspicious_link": "The message contains a shortened or suspicious-looking link.",
    "investment_scam": (
        "The message uses investment-scam language such as guaranteed returns."
    ),
    "invoice_redirection": (
        "The message asks for new bank details or a changed payment account."
    ),
}


def explain_scam_risk(message: str) -> list[str]:
    """Explain the scam-risk red flags found in a message."""

    flags = sorted(
        detect_red_flags(message),
        key=lambda flag: int(flag["weight"]),
        reverse=True,
    )
    return [
        EXPLANATION_TEMPLATES.get(str(flag["category"]), str(flag["label"]))
        for flag in flags
    ]
