"""Synthetic scam and legitimate messages for demos and tests."""

from __future__ import annotations

import pandas as pd

SCAM_MESSAGE_TEMPLATES: dict[str, list[str]] = {
    "romance scam": [
        "I love you but need help. My account is frozen and I need help urgently.",
        "I cannot access my money. Please send money for travel so we can meet.",
        "My account is frozen after my trip. I love you but need help today.",
        "Please keep this private, I need help urgently with a bank transfer.",
        "I cannot access my money while overseas. Send money for travel documents.",
        "I love you but need help with hospital bills before I can travel.",
        "My account is frozen and I cannot pay the hotel. Please help urgently.",
        "Send money for travel and I promise I will repay you when I arrive.",
        "I need help urgently, do not tell anyone, my card has stopped working.",
        "I cannot access my money and need a transfer before my flight.",
    ],
    "pig-butchering crypto investment scam": [
        (
            "My mentor found a crypto opportunity with guaranteed returns on a "
            "trading platform."
        ),
        "This trading platform is risk free. Pay the withdrawal fee to release funds.",
        "Your crypto profit is ready but there is tax to release funds today.",
        "My mentor says this crypto opportunity can double your money safely.",
        "The trading platform needs a small withdrawal fee before you can cash out.",
        "Guaranteed returns are available if you add bitcoin before midnight.",
        "Risk free crypto opportunity from my mentor, start with a bank transfer.",
        "Pay the tax to release funds from the trading platform account.",
        "Your investment balance is high but the withdrawal fee must be paid first.",
        "Join my mentor's trading platform for guaranteed returns this week.",
    ],
    "fake recruitment or task scam": [
        "Earn money from home with a simple task. Pay a deposit to unlock commission.",
        "WhatsApp recruiter here. Work only 30 minutes and unlock commission today.",
        "Telegram job available. Complete a simple task after you pay a deposit.",
        "Earn money from home, no interview, send crypto to unlock commission.",
        "Simple task role: pay a deposit and start earning commission immediately.",
        "WhatsApp recruiter: work only 30 minutes per day for high commission.",
        "Telegram job offer, pay a small training deposit to activate your account.",
        "Unlock commission by completing simple task orders from home.",
        "Earn money from home today only after a refundable deposit.",
        "Remote task job: deposit required before you can withdraw commission.",
    ],
    "authorised push payment impersonation scam": [
        "This is the fraud team. Your account is compromised, move your money now.",
        "Your bank fraud team says transfer funds to a safe account immediately.",
        "A new payee has been added. Move your money to a safe account.",
        "Your account is compromised. The fraud team needs you to act now.",
        "Move your money to a safe account while we block suspicious activity.",
        "Fraud team alert: set up this new payee and transfer your balance.",
        "Your account is compromised, do not tell anyone, move your money today.",
        "Safe account created. Transfer funds immediately to protect them.",
        "Bank fraud team: new payee verification needed to secure your savings.",
        "Move your money now because your online banking has been compromised.",
    ],
    "marketplace purchase scam": [
        "Pay outside eBay by friends and family to avoid platform fees.",
        "Facebook Marketplace buyer: message me on WhatsApp and pay a deposit.",
        "This Gumtree item is yours if you pay outside the platform today.",
        "Avoid platform fees and send friends and family payment now.",
        "Vinted purchase: message me on WhatsApp for bank transfer details.",
        "Pay outside eBay and I will arrange delivery after the transfer.",
        "Marketplace deal today only, deposit by friends and family please.",
        "I can reduce the price if you avoid platform fees and transfer direct.",
        "Message me on WhatsApp before paying for the Facebook Marketplace item.",
        "Pay by bank transfer outside the app to secure this listing.",
    ],
    "invoice redirection scam": [
        "We have new bank details for your invoice. Pay this account instead.",
        "Our account has changed. Please use the new bank details for payment.",
        "Changed account notice: pay this account instead for the attached invoice.",
        "Please ignore old invoice details and pay this new bank account.",
        "Supplier bank details changed today, update the payee before payment.",
        "New bank details for this invoice are confirmed below.",
        "Due to audit changes, pay this account instead for the balance.",
        "Our payment account changed. Please send the invoice payment today.",
        "Use these new bank details for all outstanding invoices.",
        "The invoice should now be paid to this changed account immediately.",
    ],
    "delivery scam": [
        "Royal Mail final warning: pay a delivery fee at http://bit.ly/parcel.",
        "DPD missed delivery. Pay redelivery fee today only using this link.",
        "Evri parcel redelivery requires a small payment immediately.",
        "Delivery company notice: your parcel is held until you pay this fee.",
        "Royal Mail parcel redelivery failed, confirm address at tinyurl link.",
        "DPD final warning, pay delivery fee now to avoid return.",
        "Evri delivery fee unpaid, act now to release your parcel.",
        "Missed delivery: pay a small customs fee through this secure link.",
        "Your parcel is delayed. Pay redelivery fee at http://bit.ly/check.",
        "Royal Mail needs payment today only for parcel redelivery.",
    ],
    "HMRC/tax refund scam": [
        "HMRC refund pending. Claim your refund immediately at this link.",
        "Tax refund available today only, confirm bank details for HMRC.",
        "HMRC final warning: claim your refund before your account is closed.",
        "Tax rebate approved. Use this secure refund link immediately.",
        "HMRC refund check: act now to receive your tax rebate.",
        "Your tax refund is waiting. Confirm details at http://bit.ly/hmrc.",
        "HMRC says you are due a refund. Keep this private and claim today.",
        "Final warning from HMRC: tax refund expires today only.",
        "Claim your refund now by verifying your bank account for HMRC.",
        "HMRC tax rebate requires immediate confirmation through this link.",
    ],
    "bank impersonation scam": [
        "URGENT: Your bank account will be closed. Act now to verify details.",
        "Bank alert: suspicious activity means your online banking is suspended.",
        "Verify your bank account immediately using this secure login link.",
        "Your bank account is locked. Confirm your details today only.",
        "Final warning: account will be closed unless you act now.",
        "Bank security check: urgent verification required at this link.",
        "Suspicious bank activity detected, confirm passcodes immediately.",
        "Online banking suspended. Verify your account to avoid closure.",
        "Your bank needs confirmation before a new payee can be blocked.",
        "Account will be closed today unless you confirm your bank details.",
    ],
}

LEGITIMATE_MESSAGES = [
    "Dinner tonight at 7? I can bank transfer my share afterwards.",
    "Reminder: your dental appointment is on Tuesday at 10:30.",
    "Your parcel is out for delivery. No action is required.",
    "Thanks for your payment. Your invoice receipt is attached.",
    "Can you send me the train times for tomorrow?",
    "Your GP appointment reminder: please arrive 10 minutes early.",
    "The school trip form is due next Friday.",
    "I paid for lunch, you can transfer your half when convenient.",
    "Your electricity direct debit confirmation is available online.",
    "Council tax bill is ready to view in your local account.",
    "Your broadband appointment is booked for Monday morning.",
    "The plumber confirmed the repair quote for next week.",
    "Family dinner is booked for Saturday, no deposit needed.",
    "Your payslip is available in the employee portal.",
    "The library book you requested is ready to collect.",
    "Your prescription is ready at the pharmacy.",
    "Can you pick up groceries on the way home?",
    "The football club subscription renews next month.",
    "Your cinema tickets are attached to this email.",
    "Thanks for confirming the meeting agenda.",
    "The car insurance renewal document is available to review.",
    "Your savings account statement is ready in online banking.",
    "The charity receipt for your donation is attached.",
    "Reminder: rent is due on the first of the month as usual.",
    "Your package was delivered to your safe place.",
    "Can you transfer GBP 20 for the birthday gift when you get a moment?",
    "The restaurant deposit has been paid from my card.",
    "Your appointment has been moved to Thursday at 2pm.",
    "The energy meter reading reminder is due this weekend.",
    "Please find the agenda for tomorrow's team meeting.",
]


def _build_scam_records() -> list[dict[str, str | bool]]:
    records: list[dict[str, str | bool]] = []
    for message_type, messages in SCAM_MESSAGE_TEMPLATES.items():
        records.extend(
            {
                "message_type": message_type,
                "is_scam": True,
                "message": message,
            }
            for message in messages
        )
    return records


SYNTHETIC_SCAM_MESSAGES = [
    *_build_scam_records(),
    *[
        {
            "message_type": "legitimate",
            "is_scam": False,
            "message": message,
        }
        for message in LEGITIMATE_MESSAGES
    ],
]


def generate_scam_messages() -> pd.DataFrame:
    """Return labelled synthetic scam and legitimate messages."""

    return pd.DataFrame(SYNTHETIC_SCAM_MESSAGES)
