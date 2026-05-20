from pathlib import Path

import pandas as pd
import pytest

from moneybuffer.data_generation import (
    generate_households,
    generate_transactions,
    save_synthetic_data,
)
from moneybuffer.data_generation.households import HOUSEHOLD_COLUMNS
from moneybuffer.data_generation.transactions import TRANSACTION_COLUMNS

REQUIRED_ARCHETYPES = {
    "Stable Household",
    "Payday Pressure",
    "High Debt Burden",
    "Irregular Income Worker",
    "Low Savings Renter",
    "Mortgage Rate Shock Household",
}


def test_generate_households_has_required_schema_and_archetypes() -> None:
    households = generate_households(n=60, seed=7)

    assert list(households.columns) == HOUSEHOLD_COLUMNS
    assert len(households) == 60
    assert REQUIRED_ARCHETYPES.issubset(set(households["household_type"]))
    assert households["household_id"].is_unique
    assert (households["monthly_income"] > 0).all()
    assert (households["dependants"] >= 0).all()


def test_generate_households_is_reproducible() -> None:
    first = generate_households(n=12, seed=123)
    second = generate_households(n=12, seed=123)

    pd.testing.assert_frame_equal(first, second)


def test_generate_transactions_has_required_schema_and_months() -> None:
    households = generate_households(n=8, seed=10)
    transactions = generate_transactions(households, months=6, seed=20)

    assert list(transactions.columns) == TRANSACTION_COLUMNS
    assert set(transactions["household_id"]) == set(households["household_id"])
    assert set(transactions["direction"]) == {"income", "expense"}
    assert (transactions["amount"] > 0).all()
    assert transactions["transaction_id"].is_unique

    transaction_dates = pd.to_datetime(transactions["date"])
    month_count_by_household = (
        transactions.assign(month=transaction_dates.dt.to_period("M"))
        .groupby("household_id")["month"]
        .nunique()
    )
    assert (month_count_by_household == 6).all()


def test_generate_transactions_validates_month_range() -> None:
    households = generate_households(n=2, seed=1)

    with pytest.raises(ValueError, match="months must be between 6 and 12"):
        generate_transactions(households, months=5)


def test_save_synthetic_data_writes_csv_files(tmp_path: Path) -> None:
    save_synthetic_data(str(tmp_path))

    households_path = tmp_path / "households.csv"
    transactions_path = tmp_path / "transactions.csv"

    assert households_path.exists()
    assert transactions_path.exists()
    assert not pd.read_csv(households_path).empty
    assert not pd.read_csv(transactions_path).empty
