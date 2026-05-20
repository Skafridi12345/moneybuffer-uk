"""Feature engineering for household financial resilience scoring."""

from __future__ import annotations

import numpy as np
import pandas as pd

ESSENTIAL_SPENDING_FIELDS = [
    "rent_or_mortgage",
    "council_tax",
    "energy_bill",
    "water_bill",
    "broadband_phone",
    "groceries",
    "transport",
    "insurance",
]

REQUIRED_RESILIENCE_FIELDS = [
    "monthly_income",
    *ESSENTIAL_SPENDING_FIELDS,
    "subscriptions",
    "discretionary_spending",
    "debt_repayments",
    "savings_balance",
    "overdraft_balance",
    "credit_card_balance",
]


def _safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Return numerator / denominator without raising on zero income rows."""

    numerator_values = numerator.astype(float)
    denominator_values = denominator.astype(float)
    return pd.Series(
        np.divide(
            numerator_values,
            denominator_values,
            out=np.zeros(len(numerator_values), dtype=float),
            where=denominator_values.to_numpy() != 0,
        ),
        index=numerator.index,
    )


def _as_dataframe(data: pd.DataFrame | pd.Series) -> pd.DataFrame:
    if isinstance(data, pd.Series):
        return data.to_frame().T
    return data.copy()


def _validate_required_columns(df: pd.DataFrame) -> None:
    missing_columns = [
        column for column in REQUIRED_RESILIENCE_FIELDS if column not in df.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Missing required resilience fields: {missing}")


def calculate_resilience_features(df: pd.DataFrame | pd.Series) -> pd.DataFrame:
    """Calculate explainable household financial resilience features."""

    features = _as_dataframe(df)
    _validate_required_columns(features)

    features["essential_spending"] = features[ESSENTIAL_SPENDING_FIELDS].sum(axis=1)
    features["essential_spending_ratio"] = _safe_ratio(
        features["essential_spending"],
        features["monthly_income"],
    )
    features["debt_service_ratio"] = _safe_ratio(
        features["debt_repayments"],
        features["monthly_income"],
    )
    features["monthly_surplus"] = (
        features["monthly_income"]
        - features["essential_spending"]
        - features["subscriptions"]
        - features["discretionary_spending"]
        - features["debt_repayments"]
    )
    features["emergency_runway_months"] = _safe_ratio(
        features["savings_balance"],
        features["essential_spending"],
    )
    features["credit_dependency_ratio"] = _safe_ratio(
        (features["overdraft_balance"] + features["credit_card_balance"]).clip(lower=0),
        features["monthly_income"],
    )
    features["fixed_cost_burden"] = _safe_ratio(
        features["essential_spending"] + features["debt_repayments"],
        features["monthly_income"],
    )

    return features
