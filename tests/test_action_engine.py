import pandas as pd

from moneybuffer.recommendations import (
    generate_combined_action_plan,
    generate_cross_feature_alert,
    generate_financial_actions,
    generate_scam_actions,
)


def _row(**overrides: float | str) -> pd.Series:
    data: dict[str, float | str] = {
        "risk_band": "Stable",
        "emergency_runway_months": 6.0,
        "debt_service_ratio": 0.05,
        "monthly_surplus": 500.0,
        "credit_dependency_ratio": 0.05,
        "essential_spending_ratio": 0.45,
    }
    data.update(overrides)
    return pd.Series(data)


def test_critical_band_produces_urgent_support_action() -> None:
    plan = generate_combined_action_plan(
        _row(
            risk_band="Critical",
            emergency_runway_months=0.2,
            monthly_surplus=-150.0,
        )
    )

    assert any("free debt advice" in action for action in plan["urgent_actions"])
    assert any("creditors or providers" in action for action in plan["urgent_actions"])


def test_high_scam_risk_produces_stop_and_verify_action() -> None:
    scam_result = {
        "risk_score": 82,
        "risk_band": "Severe",
        "scam_type": "Bank impersonation scam",
        "red_flags": [],
    }

    actions = generate_scam_actions(scam_result)
    plan = generate_combined_action_plan(_row(), scam_result)

    assert any("pausing before sending money" in action for action in actions)
    assert any("official channels" in action for action in plan["urgent_actions"])


def test_stable_household_gets_maintenance_positive_actions() -> None:
    plan = generate_combined_action_plan(_row())
    financial_actions = generate_financial_actions(_row())

    assert plan["urgent_actions"] == []
    assert any(
        "monitoring your budget" in action for action in plan["positive_actions"]
    )
    assert any("budget check-ins" in action for action in financial_actions)


def test_negative_monthly_surplus_produces_spending_support_action() -> None:
    row = _row(risk_band="Vulnerable", monthly_surplus=-50.0)

    financial_actions = generate_financial_actions(row)
    plan = generate_combined_action_plan(row)

    assert any("spending reductions" in action for action in financial_actions)
    assert any("support options" in action for action in plan["urgent_actions"])


def test_financial_actions_include_household_feature_values() -> None:
    row = _row(
        emergency_runway_months=0.7,
        debt_service_ratio=0.32,
        monthly_surplus=-250.0,
        essential_spending_ratio=0.74,
    )

    actions = generate_financial_actions(row)

    assert any("0.7 months" in action for action in actions)
    assert any("32% of monthly income" in action for action in actions)
    assert any("£250" in action for action in actions)
    assert any("74% of income" in action for action in actions)


def test_combined_plan_includes_support_links_key() -> None:
    plan = generate_combined_action_plan(_row())

    assert "support_links" in plan
    assert isinstance(plan["support_links"], list)


# ---------------------------------------------------------------------------
# Cross-feature alert tests
# ---------------------------------------------------------------------------


def _scam(risk_band: str) -> dict:
    return {
        "risk_score": 80,
        "risk_band": risk_band,
        "scam_type": "Bank impersonation scam",
    }


def test_vulnerable_plus_high_scam_risk_returns_alert() -> None:
    alert = generate_cross_feature_alert(_row(risk_band="Vulnerable"), _scam("High"))

    assert alert is not None
    assert isinstance(alert, str)
    assert len(alert) > 0


def test_vulnerable_plus_high_scam_alert_mentions_key_advice() -> None:
    alert = generate_cross_feature_alert(_row(risk_band="Vulnerable"), _scam("High"))

    assert alert is not None
    text = alert.lower()
    assert "vulnerable" in text or "safety buffer" in text or "pause" in text
    assert "verify" in text or "official" in text
    assert "bank" in text


def test_critical_plus_severe_scam_risk_returns_alert() -> None:
    alert = generate_cross_feature_alert(_row(risk_band="Critical"), _scam("Severe"))

    assert alert is not None
    assert isinstance(alert, str)


def test_stable_plus_high_scam_risk_returns_none() -> None:
    # Financial position is fine — no combined vulnerability alert warranted.
    alert = generate_cross_feature_alert(_row(risk_band="Stable"), _scam("High"))

    assert alert is None


def test_watch_plus_severe_scam_risk_returns_none() -> None:
    alert = generate_cross_feature_alert(_row(risk_band="Watch"), _scam("Severe"))

    assert alert is None


def test_vulnerable_plus_low_scam_risk_returns_none() -> None:
    alert = generate_cross_feature_alert(_row(risk_band="Vulnerable"), _scam("Low"))

    assert alert is None


def test_vulnerable_plus_medium_scam_risk_returns_none() -> None:
    alert = generate_cross_feature_alert(_row(risk_band="Vulnerable"), _scam("Medium"))

    assert alert is None


def test_no_scam_result_returns_none() -> None:
    alert = generate_cross_feature_alert(_row(risk_band="Critical"), None)

    assert alert is None


def test_cross_feature_alert_does_not_raise_on_missing_keys() -> None:
    # Minimal scam dict with only risk_band — should not crash.
    alert = generate_cross_feature_alert(
        _row(risk_band="Vulnerable"),
        {"risk_band": "Severe"},
    )
    assert isinstance(alert, str)
