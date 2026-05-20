"""Household stress-testing scenarios."""

from moneybuffer.stress_testing.bill_shocks import (
    apply_bill_shock,
    apply_unexpected_expense,
)
from moneybuffer.stress_testing.income_shocks import apply_income_shock
from moneybuffer.stress_testing.scenario_engine import (
    apply_compound_scenario,
    compare_baseline_vs_stress,
    months_until_savings_depleted,
    run_scenario,
    simulate_runway_over_time,
    summarise_compound_scenario,
)

__all__ = [
    "apply_bill_shock",
    "apply_compound_scenario",
    "apply_income_shock",
    "apply_unexpected_expense",
    "compare_baseline_vs_stress",
    "months_until_savings_depleted",
    "run_scenario",
    "simulate_runway_over_time",
    "summarise_compound_scenario",
]
