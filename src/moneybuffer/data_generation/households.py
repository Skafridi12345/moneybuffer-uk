"""Generate fictional UK-style household profiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

HOUSEHOLD_COLUMNS = [
    "household_id",
    "household_type",
    "monthly_income",
    "rent_or_mortgage",
    "council_tax",
    "energy_bill",
    "water_bill",
    "broadband_phone",
    "groceries",
    "transport",
    "insurance",
    "subscriptions",
    "discretionary_spending",
    "debt_repayments",
    "savings_balance",
    "overdraft_balance",
    "credit_card_balance",
    "employment_type",
    "dependants",
]


@dataclass(frozen=True)
class HouseholdArchetype:
    """Budget ranges for a fictional household archetype."""

    household_type: str
    monthly_income: tuple[int, int]
    rent_or_mortgage: tuple[int, int]
    council_tax: tuple[int, int]
    energy_bill: tuple[int, int]
    water_bill: tuple[int, int]
    broadband_phone: tuple[int, int]
    groceries: tuple[int, int]
    transport: tuple[int, int]
    insurance: tuple[int, int]
    subscriptions: tuple[int, int]
    discretionary_spending: tuple[int, int]
    debt_repayments: tuple[int, int]
    savings_balance: tuple[int, int]
    overdraft_balance: tuple[int, int]
    credit_card_balance: tuple[int, int]
    employment_types: tuple[str, ...]
    dependants: tuple[int, int]


ARCHETYPES: tuple[HouseholdArchetype, ...] = (
    HouseholdArchetype(
        household_type="Stable Household",
        monthly_income=(3300, 6200),
        rent_or_mortgage=(750, 1500),
        council_tax=(120, 230),
        energy_bill=(120, 240),
        water_bill=(28, 55),
        broadband_phone=(35, 75),
        groceries=(380, 720),
        transport=(140, 420),
        insurance=(55, 180),
        subscriptions=(15, 80),
        discretionary_spending=(220, 700),
        debt_repayments=(0, 220),
        savings_balance=(3500, 25000),
        overdraft_balance=(0, 0),
        credit_card_balance=(0, 1800),
        employment_types=("Full-time employee", "Dual-income household"),
        dependants=(0, 3),
    ),
    HouseholdArchetype(
        household_type="Payday Pressure",
        monthly_income=(1700, 3100),
        rent_or_mortgage=(650, 1200),
        council_tax=(95, 180),
        energy_bill=(110, 220),
        water_bill=(25, 50),
        broadband_phone=(30, 65),
        groceries=(300, 600),
        transport=(90, 260),
        insurance=(35, 125),
        subscriptions=(20, 100),
        discretionary_spending=(130, 380),
        debt_repayments=(120, 520),
        savings_balance=(0, 900),
        overdraft_balance=(0, 900),
        credit_card_balance=(500, 4500),
        employment_types=("Full-time employee", "Part-time employee"),
        dependants=(0, 3),
    ),
    HouseholdArchetype(
        household_type="High Debt Burden",
        monthly_income=(2300, 4700),
        rent_or_mortgage=(700, 1450),
        council_tax=(110, 220),
        energy_bill=(120, 250),
        water_bill=(28, 58),
        broadband_phone=(35, 75),
        groceries=(340, 700),
        transport=(120, 380),
        insurance=(55, 170),
        subscriptions=(25, 120),
        discretionary_spending=(120, 420),
        debt_repayments=(450, 1400),
        savings_balance=(0, 2500),
        overdraft_balance=(0, 1500),
        credit_card_balance=(3500, 18000),
        employment_types=("Full-time employee", "Self-employed"),
        dependants=(0, 4),
    ),
    HouseholdArchetype(
        household_type="Irregular Income Worker",
        monthly_income=(1400, 3900),
        rent_or_mortgage=(550, 1250),
        council_tax=(90, 190),
        energy_bill=(95, 220),
        water_bill=(22, 52),
        broadband_phone=(28, 65),
        groceries=(250, 580),
        transport=(80, 340),
        insurance=(35, 140),
        subscriptions=(10, 75),
        discretionary_spending=(90, 360),
        debt_repayments=(40, 360),
        savings_balance=(0, 4500),
        overdraft_balance=(0, 1300),
        credit_card_balance=(0, 5500),
        employment_types=("Gig economy worker", "Self-employed", "Zero-hours worker"),
        dependants=(0, 3),
    ),
    HouseholdArchetype(
        household_type="Low Savings Renter",
        monthly_income=(1500, 3200),
        rent_or_mortgage=(750, 1400),
        council_tax=(95, 190),
        energy_bill=(110, 240),
        water_bill=(24, 52),
        broadband_phone=(30, 70),
        groceries=(280, 620),
        transport=(70, 280),
        insurance=(30, 115),
        subscriptions=(10, 65),
        discretionary_spending=(80, 280),
        debt_repayments=(0, 280),
        savings_balance=(0, 600),
        overdraft_balance=(0, 800),
        credit_card_balance=(0, 3800),
        employment_types=("Full-time employee", "Part-time employee", "Student worker"),
        dependants=(0, 2),
    ),
    HouseholdArchetype(
        household_type="Mortgage Rate Shock Household",
        monthly_income=(3500, 7200),
        rent_or_mortgage=(1400, 2600),
        council_tax=(140, 280),
        energy_bill=(150, 310),
        water_bill=(32, 65),
        broadband_phone=(40, 85),
        groceries=(420, 850),
        transport=(160, 520),
        insurance=(80, 240),
        subscriptions=(25, 120),
        discretionary_spending=(180, 620),
        debt_repayments=(150, 650),
        savings_balance=(1200, 18000),
        overdraft_balance=(0, 700),
        credit_card_balance=(500, 8500),
        employment_types=("Full-time employee", "Dual-income household"),
        dependants=(1, 4),
    ),
)


def _random_money(
    rng: np.random.Generator,
    value_range: tuple[int, int],
    *,
    round_to: int = 5,
) -> int:
    value = int(rng.integers(value_range[0], value_range[1] + 1))
    return int(round(value / round_to) * round_to)


def _household_from_archetype(
    archetype: HouseholdArchetype,
    household_number: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    return {
        "household_id": f"HH{household_number:05d}",
        "household_type": archetype.household_type,
        "monthly_income": _random_money(rng, archetype.monthly_income, round_to=10),
        "rent_or_mortgage": _random_money(rng, archetype.rent_or_mortgage),
        "council_tax": _random_money(rng, archetype.council_tax),
        "energy_bill": _random_money(rng, archetype.energy_bill),
        "water_bill": _random_money(rng, archetype.water_bill),
        "broadband_phone": _random_money(rng, archetype.broadband_phone),
        "groceries": _random_money(rng, archetype.groceries),
        "transport": _random_money(rng, archetype.transport),
        "insurance": _random_money(rng, archetype.insurance),
        "subscriptions": _random_money(rng, archetype.subscriptions),
        "discretionary_spending": _random_money(
            rng,
            archetype.discretionary_spending,
        ),
        "debt_repayments": _random_money(rng, archetype.debt_repayments),
        "savings_balance": _random_money(rng, archetype.savings_balance, round_to=25),
        "overdraft_balance": _random_money(rng, archetype.overdraft_balance),
        "credit_card_balance": _random_money(
            rng,
            archetype.credit_card_balance,
            round_to=25,
        ),
        "employment_type": rng.choice(archetype.employment_types),
        "dependants": int(
            rng.integers(archetype.dependants[0], archetype.dependants[1] + 1)
        ),
    }


def generate_households(n: int = 100, seed: int = 42) -> pd.DataFrame:
    """Generate fictional UK-style household profiles.

    The data is synthetic and intended for demos, tests, and educational analysis.
    For ``n >= 6``, every required archetype is represented at least once.
    """

    if n <= 0:
        raise ValueError("n must be greater than 0")

    rng = np.random.default_rng(seed)
    archetypes: list[HouseholdArchetype]
    if n >= len(ARCHETYPES):
        archetypes = list(ARCHETYPES)
        remaining = n - len(ARCHETYPES)
        archetypes.extend(rng.choice(ARCHETYPES, size=remaining, replace=True).tolist())  # type: ignore[arg-type]
        rng.shuffle(archetypes)  # type: ignore[arg-type]
    else:
        archetypes = rng.choice(ARCHETYPES, size=n, replace=False).tolist()  # type: ignore[arg-type]

    records = [
        _household_from_archetype(archetype, index, rng)
        for index, archetype in enumerate(archetypes, start=1)
    ]
    return pd.DataFrame.from_records(records, columns=HOUSEHOLD_COLUMNS)
