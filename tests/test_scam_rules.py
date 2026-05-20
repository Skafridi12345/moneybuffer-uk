from moneybuffer.data_generation.scam_messages import generate_scam_messages
from moneybuffer.scams import (
    calculate_scam_risk_score,
    classify_scam_type,
    detect_red_flags,
    explain_scam_risk,
)


def test_urgent_bank_transfer_message_scores_high() -> None:
    message = (
        "Urgent: your bank account will be closed. Act now and send a bank "
        "transfer immediately."
    )

    result = calculate_scam_risk_score(message)

    assert result["risk_band"] in {"High", "Severe"}
    assert result["risk_score"] >= 46
    assert result["scam_type"] == "Bank impersonation scam"


def test_normal_appointment_reminder_scores_low() -> None:
    result = calculate_scam_risk_score(
        "Reminder: your GP appointment is tomorrow at 9:15."
    )

    assert result["risk_score"] == 0
    assert result["risk_band"] == "Low"
    assert result["red_flags"] == []


def test_crypto_guaranteed_return_identifies_investment_scam() -> None:
    message = "Send bitcoin for guaranteed returns and double your money."

    result = calculate_scam_risk_score(message)

    assert result["scam_type"] == "Investment scam"
    assert result["risk_band"] in {"High", "Severe"}
    assert any(flag["category"] == "investment_scam" for flag in result["red_flags"])


def test_delivery_link_scam_identifies_delivery_scam() -> None:
    message = "DPD final warning: pay delivery fee at http://bit.ly/dpd-fee today only."

    result = calculate_scam_risk_score(message)

    assert result["scam_type"] == "Delivery scam"
    assert any(flag["category"] == "suspicious_link" for flag in result["red_flags"])


def test_new_bank_details_identifies_invoice_redirection_risk() -> None:
    message = (
        "Please use our new bank details. The account changed, pay this account "
        "instead."
    )

    result = calculate_scam_risk_score(message)

    assert result["scam_type"] == "Invoice redirection scam"
    assert result["risk_band"] in {"High", "Severe"}
    assert result["risk_score"] >= 46
    assert any(
        flag["category"] == "invoice_redirection" for flag in result["red_flags"]
    )


def test_romance_scam_text_classified_as_romance() -> None:
    message = (
        "I love you but need help. My account is frozen and I need help urgently "
        "with travel."
    )

    result = calculate_scam_risk_score(message)

    assert result["scam_type"] == "Romance scam"
    assert any(flag["category"] == "romance_scam" for flag in result["red_flags"])


def test_pig_butchering_text_classified_as_crypto_investment() -> None:
    message = (
        "My mentor found a crypto opportunity on a trading platform. There are "
        "guaranteed returns, but you must pay a withdrawal fee first."
    )

    result = calculate_scam_risk_score(message)

    assert result["scam_type"] == "Pig-butchering crypto investment scam"
    assert any(
        flag["category"] == "pig_butchering_crypto" for flag in result["red_flags"]
    )


def test_fake_job_text_classified_as_job_task_scam() -> None:
    message = (
        "WhatsApp recruiter here. Earn money from home with a simple task, pay a "
        "deposit, then unlock commission."
    )

    result = calculate_scam_risk_score(message)

    assert result["scam_type"] == "Job or task scam"
    assert any(flag["category"] == "fake_job_task" for flag in result["red_flags"])


def test_legitimate_family_dinner_bank_transfer_not_severe() -> None:
    result = calculate_scam_risk_score(
        "Family dinner is at 7. I can bank transfer my share afterwards."
    )

    assert result["risk_band"] != "Severe"
    assert result["risk_score"] < 71


def test_synthetic_messages_cover_expanded_typologies() -> None:
    messages = generate_scam_messages()
    scam_counts = messages.loc[messages["is_scam"]].groupby("message_type").size()
    legitimate_count = int((~messages["is_scam"]).sum())

    expected_types = {
        "romance scam",
        "pig-butchering crypto investment scam",
        "fake recruitment or task scam",
        "authorised push payment impersonation scam",
        "marketplace purchase scam",
        "invoice redirection scam",
        "delivery scam",
        "HMRC/tax refund scam",
        "bank impersonation scam",
    }

    assert expected_types.issubset(set(scam_counts.index))
    assert scam_counts.loc[list(expected_types)].min() >= 10
    assert legitimate_count >= 30


def test_explanations_and_synthetic_messages_are_available() -> None:
    explanations = explain_scam_risk(
        "Keep this private and pay by gift card immediately."
    )
    messages = generate_scam_messages()

    assert len(explanations) >= 2
    assert {"message_type", "is_scam", "message"}.issubset(messages.columns)
    assert messages["is_scam"].any()
    assert (~messages["is_scam"]).any()


def test_detect_red_flags_returns_structured_flags() -> None:
    flags = detect_red_flags("HMRC final warning: claim at http://tinyurl.com/refund")

    assert flags
    assert {"category", "label", "matches", "weight"}.issubset(flags[0])


def test_detect_red_flags_displays_actual_regex_match() -> None:
    flags = detect_red_flags("Pay redelivery fee at http://bit.ly/parcel-check today.")
    link_flag = next(flag for flag in flags if flag["category"] == "suspicious_link")

    assert "bit.ly" in " ".join(link_flag["matches"])
    assert r"\bbit\.ly\b" not in link_flag["matches"]


def test_classify_scam_type_returns_low_risk_fallback() -> None:
    assert (
        classify_scam_type("Lunch is at 12:30.") == "Unclassified or low-risk message"
    )
