"""Generate synthetic monthly household transactions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from moneybuffer.data_generation.households import generate_households

TRANSACTION_COLUMNS = [
    "transaction_id",
    "household_id",
    "date",
    "category",
    "merchant",
    "amount",
    "direction",
    "is_essential",
    "is_debt_payment",
    "is_discretionary",
]

EXPENSE_CATEGORIES: dict[str, dict[str, Any]] = {
    "rent_or_mortgage": {
        "category": "Housing",
        "merchants": (
            "Housing Association",
            "High Street Bank Mortgage",
            "Lettings Co",
        ),
        "is_essential": True,
        "is_debt_payment": False,
        "is_discretionary": False,
    },
    "council_tax": {
        "category": "Council Tax",
        "merchants": ("Local Council",),
        "is_essential": True,
        "is_debt_payment": False,
        "is_discretionary": False,
    },
    "energy_bill": {
        "category": "Energy",
        "merchants": ("Octopus Energy", "British Gas", "OVO Energy", "E.ON Next"),
        "is_essential": True,
        "is_debt_payment": False,
        "is_discretionary": False,
    },
    "water_bill": {
        "category": "Water",
        "merchants": ("Thames Water", "United Utilities", "Severn Trent Water"),
        "is_essential": True,
        "is_debt_payment": False,
        "is_discretionary": False,
    },
    "broadband_phone": {
        "category": "Broadband and Phone",
        "merchants": ("BT", "Sky", "Virgin Media", "Three"),
        "is_essential": True,
        "is_debt_payment": False,
        "is_discretionary": False,
    },
    "groceries": {
        "category": "Groceries",
        "merchants": ("Tesco", "Sainsbury's", "Asda", "Aldi", "Morrisons"),
        "is_essential": True,
        "is_debt_payment": False,
        "is_discretionary": False,
    },
    "transport": {
        "category": "Transport",
        "merchants": ("TfL", "National Rail", "Shell", "Stagecoach", "Uber"),
        "is_essential": True,
        "is_debt_payment": False,
        "is_discretionary": False,
    },
    "insurance": {
        "category": "Insurance",
        "merchants": ("Aviva", "Direct Line", "Admiral", "LV="),
        "is_essential": True,
        "is_debt_payment": False,
        "is_discretionary": False,
    },
    "subscriptions": {
        "category": "Subscriptions",
        "merchants": ("Netflix", "Spotify", "Amazon Prime", "Now TV"),
        "is_essential": False,
        "is_debt_payment": False,
        "is_discretionary": True,
    },
    "discretionary_spending": {
        "category": "Discretionary Spending",
        "merchants": ("Costa", "Deliveroo", "Boots", "Currys", "Local Pub"),
        "is_essential": False,
        "is_debt_payment": False,
        "is_discretionary": True,
    },
    "debt_repayments": {
        "category": "Debt Repayment",
        "merchants": (
            "Credit Card Provider",
            "Personal Loan Provider",
            "BNPL Provider",
        ),
        "is_essential": True,
        "is_debt_payment": True,
        "is_discretionary": False,
    },
}

INCOME_MERCHANTS = {
    "Full-time employee": ("Employer Payroll",),
    "Part-time employee": ("Employer Payroll",),
    "Dual-income household": ("Employer Payroll", "Second Employer Payroll"),
    "Self-employed": ("Client Payment", "Marketplace Payout"),
    "Gig economy worker": ("Platform Payout", "Delivery App Payout"),
    "Zero-hours worker": ("Shift Payroll",),
    "Student worker": ("Employer Payroll", "Student Finance"),
}


def _month_starts(months: int) -> pd.DatetimeIndex:
    end_month = pd.Timestamp("2025-12-01")
    return pd.date_range(end=end_month, periods=months, freq="MS")


def _date_in_month(month_start: pd.Timestamp, rng: np.random.Generator) -> pd.Timestamp:
    days_in_month = month_start.days_in_month
    return month_start + pd.Timedelta(days=int(rng.integers(0, days_in_month)))


def _jitter_amount(
    amount: float,
    rng: np.random.Generator,
    *,
    variation: float,
    minimum: float = 0.0,
) -> float:
    if amount <= 0:
        return 0.0
    multiplier = rng.normal(loc=1.0, scale=variation)
    return round(max(minimum, amount * multiplier), 2)


def _income_amount(
    monthly_income: float,
    employment_type: str,
    rng: np.random.Generator,
) -> float:
    irregular_types = {"Gig economy worker", "Self-employed", "Zero-hours worker"}
    variation = 0.22 if employment_type in irregular_types else 0.04
    return _jitter_amount(monthly_income, rng, variation=variation, minimum=100.0)


def _build_transaction(
    transaction_number: int,
    household_id: str,
    date: pd.Timestamp,
    category: str,
    merchant: str,
    amount: float,
    direction: str,
    *,
    is_essential: bool,
    is_debt_payment: bool,
    is_discretionary: bool,
) -> dict[str, Any]:
    return {
        "transaction_id": f"TX{transaction_number:08d}",
        "household_id": household_id,
        "date": date.date().isoformat(),
        "category": category,
        "merchant": merchant,
        "amount": amount,
        "direction": direction,
        "is_essential": is_essential,
        "is_debt_payment": is_debt_payment,
        "is_discretionary": is_discretionary,
    }


def generate_transactions(
    households: pd.DataFrame,
    months: int = 6,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate 6 to 12 months of synthetic monthly transactions per household."""

    if months < 6 or months > 12:
        raise ValueError("months must be between 6 and 12")
    if households.empty:
        return pd.DataFrame(columns=TRANSACTION_COLUMNS)

    rng = np.random.default_rng(seed)
    records: list[dict[str, Any]] = []
    transaction_number = 1

    for household in households.to_dict(orient="records"):
        household_id = str(household["household_id"])
        employment_type = str(household["employment_type"])
        income_merchants = INCOME_MERCHANTS.get(employment_type, ("Income",))

        for month_start in _month_starts(months):
            income = _income_amount(
                float(household["monthly_income"]),
                employment_type,
                rng,
            )
            records.append(
                _build_transaction(
                    transaction_number,
                    household_id,
                    _date_in_month(month_start, rng),
                    "Income",
                    str(rng.choice(income_merchants)),
                    income,
                    "income",
                    is_essential=False,
                    is_debt_payment=False,
                    is_discretionary=False,
                )
            )
            transaction_number += 1

            for budget_field, metadata in EXPENSE_CATEGORIES.items():
                budget_amount = float(household[budget_field])
                if budget_amount <= 0:
                    continue

                variation = 0.12
                if budget_field in {"rent_or_mortgage", "council_tax"}:
                    variation = 0.01
                elif budget_field in {
                    "groceries",
                    "transport",
                    "discretionary_spending",
                }:
                    variation = 0.18

                amount = _jitter_amount(
                    budget_amount,
                    rng,
                    variation=variation,
                    minimum=1.0,
                )
                records.append(
                    _build_transaction(
                        transaction_number,
                        household_id,
                        _date_in_month(month_start, rng),
                        str(metadata["category"]),
                        str(rng.choice(metadata["merchants"])),
                        amount,
                        "expense",
                        is_essential=bool(metadata["is_essential"]),
                        is_debt_payment=bool(metadata["is_debt_payment"]),
                        is_discretionary=bool(metadata["is_discretionary"]),
                    )
                )
                transaction_number += 1

    return pd.DataFrame.from_records(records, columns=TRANSACTION_COLUMNS)


def save_synthetic_data(output_dir: str = "data/synthetic") -> None:
    """Generate and save household and transaction datasets as CSV files."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    households = generate_households()
    transactions = generate_transactions(households)

    households.to_csv(output_path / "households.csv", index=False)
    transactions.to_csv(output_path / "transactions.csv", index=False)
