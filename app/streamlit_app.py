"""Streamlit MVP entrypoint for MoneyBuffer UK."""

from __future__ import annotations

# ruff: noqa: E402, I001

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from moneybuffer import __version__  # noqa: E402
from moneybuffer.data_generation.households import (  # noqa: E402
    generate_households,
)
from moneybuffer.data_generation.scam_messages import (  # noqa: E402
    generate_scam_messages,
)
from moneybuffer.recommendations.action_engine import (  # noqa: E402
    generate_combined_action_plan,
    generate_cross_feature_alert,
)
from moneybuffer.reporting.pdf_report import build_pdf_report  # noqa: E402
from moneybuffer.resilience.explanations import (  # noqa: E402
    estimate_improvement_to_next_band,
    explain_score,
)
from moneybuffer.resilience.features import (  # noqa: E402
    calculate_resilience_features,
)
from moneybuffer.resilience.score import (  # noqa: E402
    calculate_resilience_score,
)
from moneybuffer.scams.classifier import (  # noqa: E402
    calculate_scam_risk_score,
)
from moneybuffer.scams.explanations import explain_scam_risk  # noqa: E402
from moneybuffer.scams.ml_model import (  # noqa: E402
    predict_scam_ml,
    train_scam_classifier,
)
from moneybuffer.scams.rules import detect_red_flags  # noqa: E402
from moneybuffer.stress_testing.scenario_engine import (  # noqa: E402
    apply_compound_scenario,
    compare_baseline_vs_stress,
    months_until_savings_depleted,
    run_scenario,
    simulate_runway_over_time,
)
from moneybuffer.ui.theme import (  # noqa: E402
    action_cards_html,
    adjust_banner_html,
    band_comparison_html,
    brand_header,
    comparison_cards_html,
    cross_alert_html,
    driver_bars_html,
    explain_bullets_html,
    gauge_hero_html,
    hint_html,
    inject_brand_css,
    nav_bar_html,
    page_footer,
    red_flag_items_html,
    scam_badge,
    scam_risk_card_html,
    section_anchor,
    section_divider,
    section_header,
    support_link_card_html,
    warning_banner,
)
from moneybuffer.validation.input_validation import (  # noqa: E402
    FIELD_BOUNDS,
    validate_household_inputs,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DISCLAIMER_BODY = (
    "MoneyBuffer UK does not provide regulated financial advice, "
    "debt advice, investment advice, credit broking, insurance advice, "
    "or personalised product recommendations. It is not a lending tool "
    "and not a guaranteed scam detector."
)

HOUSEHOLD_TYPES = [
    "Stable Household",
    "Payday Pressure",
    "High Debt Burden",
    "Irregular Income Worker",
    "Low Savings Renter",
    "Mortgage Rate Shock Household",
]

EDITABLE_FIELDS = [
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
]

FIELD_LABELS = {
    "monthly_income": "Monthly income",
    "rent_or_mortgage": "Rent or mortgage",
    "council_tax": "Council tax",
    "energy_bill": "Energy bill",
    "water_bill": "Water bill",
    "broadband_phone": "Broadband and phone",
    "groceries": "Groceries",
    "transport": "Transport",
    "insurance": "Insurance",
    "subscriptions": "Subscriptions",
    "discretionary_spending": "Discretionary spending",
    "debt_repayments": "Debt repayments",
    "savings_balance": "Savings balance",
    "overdraft_balance": "Overdraft balance",
    "credit_card_balance": "Credit card balance",
}

# ---------------------------------------------------------------------------
# Page config — must be the first Streamlit call
# ---------------------------------------------------------------------------

# TODO: replace page_icon with a real .ico path once assets/ is populated
st.set_page_config(
    page_title="MoneyBuffer UK",
    page_icon="🛡️",
    layout="wide",
)

inject_brand_css()

# ---------------------------------------------------------------------------
# Logo image (optional — falls back gracefully if PNG not present)
# ---------------------------------------------------------------------------

_LOGO_PATH = PROJECT_ROOT / "assets" / "logo_moneybuffer.png"
# TODO: copy your logo PNG to assets/logo_moneybuffer.png
# The sidebar and header use an inline SVG fallback automatically.

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


@st.cache_data
def load_demo_households() -> pd.DataFrame:
    """Load one deterministic demo household for each archetype."""
    synthetic_dir = PROJECT_ROOT / "data" / "synthetic"
    households_path = synthetic_dir / "households.csv"
    scam_messages_path = synthetic_dir / "scam_messages.csv"

    synthetic_dir.mkdir(parents=True, exist_ok=True)
    if not households_path.exists():
        generate_households(n=120, seed=42).to_csv(households_path, index=False)
    if not scam_messages_path.exists():
        generate_scam_messages().to_csv(scam_messages_path, index=False)

    households = pd.read_csv(households_path)
    return (
        households.sort_values("household_id")
        .groupby("household_type", as_index=False)
        .first()
    )


@st.cache_resource
def load_scam_ml_model():
    """Train the optional experimental scam classifier once per session."""
    return train_scam_classifier()


def try_predict_scam_ml(
    message: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Return optional ML output without blocking the rule-based check."""
    try:
        return predict_scam_ml(message, load_scam_ml_model()), None
    except Exception as exc:  # pragma: no cover
        return None, str(exc)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def money(value: float) -> str:
    return f"GBP {value:,.0f}"


def percent(value: float) -> str:
    return f"{value:.0%}"


# ---------------------------------------------------------------------------
# Household input helpers
# ---------------------------------------------------------------------------


def selected_household_row(households: pd.DataFrame, household_type: str) -> pd.Series:
    return households.loc[households["household_type"] == household_type].iloc[0].copy()


_INPUT_GROUPS: list[tuple[str, list[str]]] = [
    ("Income", ["monthly_income"]),
    (
        "Housing & bills",
        [
            "rent_or_mortgage",
            "council_tax",
            "energy_bill",
            "water_bill",
            "broadband_phone",
        ],
    ),
    (
        "Living costs",
        [
            "groceries",
            "transport",
            "insurance",
            "subscriptions",
            "discretionary_spending",
        ],
    ),
    (
        "Debts & savings",
        [
            "debt_repayments",
            "savings_balance",
            "overdraft_balance",
            "credit_card_balance",
        ],
    ),
]


def editable_household(row: pd.Series, enabled: bool) -> pd.Series:
    """Return edited household row using inline grouped inputs."""
    if not enabled:
        return row

    edited = row.copy()
    with st.expander("✏️ Edit household inputs", expanded=True):
        for group_label, fields in _INPUT_GROUPS:
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;'
                f"color:#6B8A7F;text-transform:uppercase;"
                f'letter-spacing:.08em;margin:10px 0 6px">'
                f"{group_label}</div>",
                unsafe_allow_html=True,
            )
            cols = st.columns(len(fields))
            for i, field in enumerate(fields):
                _, field_max = FIELD_BOUNDS[field]
                with cols[i]:
                    edited[field] = st.number_input(
                        FIELD_LABELS[field],
                        min_value=0.0,
                        max_value=float(field_max),
                        value=min(float(row[field]), float(field_max)),
                        step=25.0,
                        format="%.2f",
                    )
    return edited


def row_to_frame(row: pd.Series) -> pd.DataFrame:
    return pd.DataFrame([row.to_dict()])


# ---------------------------------------------------------------------------
# Chart builders
# ---------------------------------------------------------------------------

_CHART_LAYOUT = dict(
    plot_bgcolor="white",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="'Plus Jakarta Sans', Inter, 'Segoe UI', sans-serif",
        size=12,
        color="#3D5A4E",
    ),
    margin={"l": 20, "r": 20, "t": 56, "b": 20},
    yaxis=dict(
        gridcolor="#F4F7F5",
        zeroline=False,
        showline=False,
    ),
    xaxis=dict(showline=False, showgrid=False),
)


def build_spending_chart(scored_row: pd.Series) -> go.Figure:
    categories = ["Income", "Essentials", "Debt", "Discretionary"]
    values = [
        scored_row["monthly_income"],
        scored_row["essential_spending"],
        scored_row["debt_repayments"],
        scored_row["discretionary_spending"] + scored_row["subscriptions"],
    ]
    fig = go.Figure(
        data=[
            go.Bar(
                x=categories,
                y=values,
                marker_color=[
                    "#00A87A",
                    "#0D2218",
                    "#9B2220",
                    "#F5A623",
                ],
                marker_line_width=0,
                hovertemplate="%{x}: GBP %{y:,.0f}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text="Monthly Income & Spending Snapshot",
            font=dict(size=14, color="#0D2218", weight=700),
        ),
        yaxis_title="GBP / month",
        xaxis_title=None,
        showlegend=False,
        **_CHART_LAYOUT,
    )
    return fig


def build_stress_chart(
    comparison: pd.Series,
    title: str = "Baseline vs Stressed Scenario",
) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(
        name="Baseline",
        x=["Resilience score", "Monthly surplus", "Runway months"],
        y=[
            comparison["baseline_score"],
            comparison["baseline_monthly_surplus"],
            comparison["baseline_runway_months"],
        ],
        marker_color="#00A87A",
        marker_line_width=0,
    )
    fig.add_bar(
        name="Stressed",
        x=["Resilience score", "Monthly surplus", "Runway months"],
        y=[
            comparison["stressed_score"],
            comparison["stressed_monthly_surplus"],
            comparison["stressed_runway_months"],
        ],
        marker_color="#9B2220",
        marker_line_width=0,
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#0D2218", weight=700)),
        barmode="group",
        yaxis_title="Value",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        **_CHART_LAYOUT,
    )
    return fig


def build_runway_chart(trajectory: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Scatter(
                x=trajectory["month"],
                y=trajectory["savings_balance"],
                mode="lines+markers",
                line={"color": "#00A87A", "width": 2.5},
                marker={"size": 6, "color": "#00A87A"},
                fill="tozeroy",
                fillcolor="rgba(0,168,122,0.07)",
                hovertemplate=("Month %{x}: GBP %{y:,.0f}<extra></extra>"),
            )
        ]
    )
    fig.update_layout(
        title=dict(
            text="Projected Savings Balance Over Time",
            font=dict(size=14, color="#0D2218", weight=700),
        ),
        xaxis_title="Month",
        yaxis_title="Savings balance (GBP)",
        **_CHART_LAYOUT,
    )
    return fig


# ---------------------------------------------------------------------------
# Scenario controls
# ---------------------------------------------------------------------------


def scenario_controls(
    household_df: pd.DataFrame,
) -> tuple[pd.DataFrame, str]:
    scenario = st.selectbox(
        "Scenario",
        [
            "Income drop",
            "Rent/mortgage increase",
            "Energy bill increase",
            "Unexpected expense",
            "Debt/mortgage payment increase",
            "Compound Scenario",
        ],
    )

    if scenario == "Income drop":
        pct_drop = st.selectbox(
            "Income drop", [20, 40, 100], format_func=lambda x: f"{x}%"
        )
        duration_months = st.selectbox(
            "Shock duration",
            [1, 3, 6, 12],
            format_func=(lambda x: f"{x} month" if x == 1 else f"{x} months"),
        )
        return (
            run_scenario(
                household_df,
                "income_drop_pct",
                pct_drop=pct_drop / 100,
                duration_months=duration_months,
            ),
            f"Income drop of {pct_drop}% for {duration_months} month(s)",
        )

    if scenario == "Rent/mortgage increase":
        pct_increase = st.selectbox(
            "Rent or mortgage increase",
            [5, 10, 15],
            format_func=lambda x: f"{x}%",
        )
        return (
            run_scenario(
                household_df,
                "rent_or_mortgage_increase_pct",
                pct_increase=pct_increase / 100,
            ),
            f"Rent or mortgage increase of {pct_increase}%",
        )

    if scenario == "Energy bill increase":
        amount = st.selectbox("Monthly energy bill increase", [50, 100, 150])
        return (
            run_scenario(
                household_df,
                "energy_bill_increase_amount",
                amount_increase=amount,
            ),
            f"Energy bill increase of {money(amount)}",
        )

    if scenario == "Unexpected expense":
        amount = st.selectbox(
            "One-off unexpected expense",
            [300, 500, 1000, 1500, 2000, 3000],
        )
        return (
            run_scenario(
                household_df,
                "unexpected_expense_amount",
                amount=amount,
            ),
            f"Unexpected expense of {money(amount)}",
        )

    if scenario == "Compound Scenario":
        st.caption(
            "Compound scenarios apply multiple shocks at once. "
            "Educational modelling only — not a forecast."
        )
        income_drop_pct = st.selectbox(
            "Income drop %",
            [0, 20, 40, 100],
            format_func=lambda x: f"{x}%",
        )
        rent_increase_pct = st.selectbox(
            "Rent/mortgage increase %",
            [0, 5, 10, 15],
            format_func=lambda x: f"{x}%",
        )
        energy_increase = st.selectbox("Energy bill increase", [0, 50, 100, 150])
        unexpected_expense = st.selectbox(
            "Unexpected expense",
            [0, 300, 500, 1000, 1500, 2000, 3000],
        )
        payment_increase = st.number_input(
            "Debt/mortgage payment increase",
            min_value=0.0,
            value=0.0,
            step=25.0,
        )
        stressed = apply_compound_scenario(
            household_df,
            income_drop_pct=income_drop_pct / 100,
            rent_or_mortgage_increase_pct=rent_increase_pct / 100,
            energy_bill_increase_amount=energy_increase,
            unexpected_expense_amount=unexpected_expense,
            debt_payment_increase_amount=payment_increase,
        )
        return (
            stressed,
            (
                f"Compound: income -{income_drop_pct}%, "
                f"rent +{rent_increase_pct}%, "
                f"energy +{money(energy_increase)}, "
                f"expense {money(unexpected_expense)}, "
                f"payments +{money(payment_increase)}"
            ),
        )

    # Debt / mortgage payment increase
    amount = st.number_input(
        "Payment increase amount", min_value=0.0, value=150.0, step=25.0
    )
    target_label = st.radio(
        "Apply increase to",
        ["Debt repayments", "Mortgage/rent payment"],
        horizontal=True,
    )
    target = "debt_repayments"
    if target_label == "Mortgage/rent payment":
        target = "rent_or_mortgage"

    return (
        run_scenario(
            household_df,
            "interest_rate_payment_increase_amount",
            amount_increase=amount,
            target=target,
        ),
        f"{target_label} increase of {money(amount)}",
    )


# ---------------------------------------------------------------------------
# Text report builder
# ---------------------------------------------------------------------------


def build_text_report(
    scored_row: pd.Series,
    action_plan: dict[str, Any],
    scam_result: dict[str, Any] | None,
) -> str:
    lines = [
        "MoneyBuffer UK educational prototype report",
        "",
        _DISCLAIMER_BODY,
        "",
        "Financial health snapshot",
        f"- Resilience score: {scored_row['resilience_score']:.1f}/100",
        f"- Risk band: {scored_row['risk_band']}",
        (f"- Emergency runway: {scored_row['emergency_runway_months']:.1f} months"),
        f"- Monthly surplus: {money(float(scored_row['monthly_surplus']))}",
        "",
        "Urgent actions",
        *[f"- {a}" for a in action_plan["urgent_actions"]],
        "",
        "Medium-term actions",
        *[f"- {a}" for a in action_plan["medium_term_actions"]],
        "",
        "Positive actions",
        *[f"- {a}" for a in action_plan["positive_actions"]],
    ]
    support_links = action_plan.get("support_links", [])
    if support_links:
        lines += ["", "Official support resources"] + [
            f"- {lnk['name']}: {lnk['url']} ({lnk['use_case']})"
            for lnk in support_links
        ]
    if scam_result:
        lines += [
            "",
            "Scam checker snapshot",
            f"- Risk score: {scam_result['risk_score']}/100",
            f"- Risk band: {scam_result['risk_band']}",
            f"- Scam type: {scam_result['scam_type']}",
            (f"- Recommended action: {scam_result['recommended_action']}"),
        ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

brand_header(__version__)

# ---------------------------------------------------------------------------
# Inline controls — household selector only (edit checkbox moved to section 1)
# ---------------------------------------------------------------------------

demo_households = load_demo_households()

selected_type = st.selectbox(
    "Demo household profile",
    HOUSEHOLD_TYPES,
)

base_row = selected_household_row(demo_households, selected_type)

# ---------------------------------------------------------------------------
# Sticky navigation bar
# ---------------------------------------------------------------------------

st.markdown(nav_bar_html(), unsafe_allow_html=True)

# ── Section 1: Financial Health Check ────────────────────────────────────

section_anchor("section-health")
if True:  # scope block
    section_header(
        "📊",
        "Financial Health Check",
        "Educational resilience snapshot for the selected household.",
    )

    # ── Hero gauge placeholder — filled after scores are computed ─────────
    hero_slot = st.empty()

    # ── Adjustment banner + edit checkbox ─────────────────────────────────
    st.markdown(adjust_banner_html(selected_type), unsafe_allow_html=True)
    edit_col, _ = st.columns([2, 5])
    with edit_col:
        manual_edit = st.checkbox("✏️ Edit my inputs", value=False)

    household_row = editable_household(base_row, manual_edit)
    household_df = row_to_frame(household_row)

    scored_df = calculate_resilience_score(
        calculate_resilience_features(household_df),
    )
    scored_row = scored_df.iloc[0]

    # ── Fill the hero slot now that scores are ready ───────────────────────
    hero_slot.markdown(gauge_hero_html(scored_row), unsafe_allow_html=True)

    # Input validation notices
    input_warnings = validate_household_inputs(scored_row)
    if input_warnings:
        notice_label = (
            f"⚠️ Input notices ({len(input_warnings)})"
            " — some values may affect result quality"
        )
        with st.expander(notice_label, expanded=False):
            for w in input_warnings:
                st.warning(w)

    # Score driver bars
    st.markdown(driver_bars_html(scored_row), unsafe_allow_html=True)

    # Score explanations
    section_header("📝", "Score drivers — detail")
    st.markdown(
        explain_bullets_html(explain_score(scored_row)),
        unsafe_allow_html=True,
    )

    # Improvement hint
    section_header("💡", "How to improve")
    st.markdown(
        hint_html(estimate_improvement_to_next_band(scored_row)),
        unsafe_allow_html=True,
    )

    # Spending breakdown chart
    section_header("💰", "Spending breakdown")
    st.plotly_chart(build_spending_chart(scored_row), width="stretch")

# ── Section 2: Bill Shock Simulator ──────────────────────────────────────

section_divider()
section_anchor("section-shock")
if True:  # scope block
    section_header(
        "⚡",
        "Bill Shock Simulator",
        "Apply a stress scenario and compare outcomes. "
        "Simplified educational modelling — not a forecast.",
    )

    stressed_df, scenario_label = scenario_controls(household_df)
    comparison = compare_baseline_vs_stress(household_df, stressed_df).iloc[0]

    st.markdown(
        f'<div style="font-size:13px;color:#6B8A7F;margin-bottom:1rem">'
        f"<strong style='color:#1A2E25'>Scenario:</strong> "
        f"{scenario_label}</div>",
        unsafe_allow_html=True,
    )

    # Comparison cards — before/after with delta arrow
    st.markdown(comparison_cards_html(comparison), unsafe_allow_html=True)
    st.markdown(
        band_comparison_html(
            str(comparison["baseline_band"]),
            str(comparison["stressed_band"]),
        ),
        unsafe_allow_html=True,
    )

    # Delta metrics
    shock_cols = st.columns(4)
    shock_cols[0].metric("Baseline score", f"{comparison['baseline_score']:.1f}")
    shock_cols[1].metric(
        "Stressed score",
        f"{comparison['stressed_score']:.1f}",
        delta=f"{comparison['score_change']:.1f}",
    )
    shock_cols[2].metric(
        "Surplus change",
        money(
            float(
                comparison["stressed_monthly_surplus"]
                - comparison["baseline_monthly_surplus"]
            )
        ),
    )
    runway_change = (
        comparison["stressed_runway_months"] - comparison["baseline_runway_months"]
    )
    shock_cols[3].metric("Runway change", f"{runway_change:.1f} mo")

    chart_title = "Baseline vs Stressed Scenario"
    if scenario_label.startswith("Compound"):
        chart_title = "Baseline vs Compound Scenario"
    st.plotly_chart(
        build_stress_chart(comparison, title=chart_title),
        width="stretch",
    )

    section_header("⏱️", "Savings runway projection")
    stressed_scored_row = calculate_resilience_score(
        calculate_resilience_features(stressed_df)
    ).iloc[0]
    trajectory = simulate_runway_over_time(stressed_scored_row, duration_months=12)
    depletion_month = months_until_savings_depleted(stressed_scored_row, max_months=12)

    if depletion_month is None:
        st.success("✅ Savings not depleted within 12 months in this scenario.")
    else:
        st.error(f"🔴 Savings depleted after {depletion_month} month(s).")

    st.plotly_chart(build_runway_chart(trajectory), width="stretch")

# ── Section 3: Scam Checker ───────────────────────────────────────────────

section_divider()
section_anchor("section-scam")
if True:  # scope block
    section_header(
        "🔍",
        "Scam Checker",
        "Rule-based scam-risk signals — not an LLM, results are not guaranteed.",
    )

    warning_banner(
        "This tool may flag legitimate messages and may miss real scams. "
        "Treat it as an early-warning prompt, not a guarantee."
    )

    scam_examples = generate_scam_messages()
    with st.expander("📋 Example messages — click to load"):
        for _, example in scam_examples.iterrows():
            label = "Scam example" if example["is_scam"] else "Legitimate comparison"
            st.markdown(f"**{example['message_type']}** — {label}")
            st.caption(str(example["message"]))

    message = st.text_area(
        "Paste a message or payment request to check",
        value=st.session_state.get(
            "scam_message",
            "Royal Mail final warning: pay a small delivery fee "
            "today only at http://bit.ly/parcel-check.",
        ),
        height=120,
    )
    st.session_state["scam_message"] = message

    if st.button("🔍 Check scam risk", type="primary"):
        st.session_state["scam_result"] = calculate_scam_risk_score(message)
        scam_ml_result, scam_ml_error = try_predict_scam_ml(message)
        st.session_state["scam_ml_result"] = scam_ml_result
        st.session_state["scam_ml_error"] = scam_ml_error

    scam_result = st.session_state.get("scam_result")
    if scam_result:
        scam_ml_result = st.session_state.get("scam_ml_result")
        scam_ml_error = st.session_state.get("scam_ml_error")

        # Premium visual risk card
        st.markdown(scam_risk_card_html(scam_result), unsafe_allow_html=True)

        scam_cols = st.columns(3)
        scam_cols[0].metric(
            "Scam-risk score",
            f"{scam_result['risk_score']} / 100",
        )
        scam_cols[1].metric("Scam type", scam_result["scam_type"])
        scam_cols[2].metric("Red flags", len(scam_result["red_flags"]))

        scam_badge(str(scam_result["risk_band"]))

        cross_text = generate_cross_feature_alert(scored_row, scam_result)
        if cross_text:
            st.markdown(cross_alert_html(cross_text), unsafe_allow_html=True)

        section_header("🚩", "Red flags detected")
        st.markdown(
            red_flag_items_html(detect_red_flags(message)),
            unsafe_allow_html=True,
        )

        section_header("💬", "Why this was flagged")
        explanations = explain_scam_risk(message)
        if explanations:
            st.markdown(
                explain_bullets_html(explanations),
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="font-size:13px;color:#6B8A7F;'
                'font-style:italic">'
                "No major rule-based scam indicators found.</div>",
                unsafe_allow_html=True,
            )

        section_header("✅", "Recommended action")
        st.markdown(
            hint_html(str(scam_result["recommended_action"])),
            unsafe_allow_html=True,
        )

        with st.expander("🧪 Experimental ML proof-of-concept"):
            st.caption(
                "This experimental classifier is trained on synthetic/"
                "demo data and should not be interpreted as real-world "
                "scam detection performance. The transparent red-flag "
                "rules above are the primary output."
            )
            if scam_ml_result:
                ml_cols = st.columns(3)
                ml_cols[0].metric(
                    "ML scam probability",
                    f"{float(scam_ml_result['scam_probability']):.0%}",
                )
                ml_cols[1].metric("ML label", str(scam_ml_result["label"]))
                ml_cols[2].metric(
                    "ML category",
                    str(scam_ml_result["scam_category"]),
                )
            else:
                st.info(
                    "The optional ML proof-of-concept is unavailable. "
                    "The rule-based output above is still active."
                )
                if scam_ml_error:
                    st.caption("Technical note: optional ML signal could not run.")

# ── Section 4: Action Plan ────────────────────────────────────────────────

section_divider()
section_anchor("section-actions")
if True:  # scope block
    section_header(
        "📋",
        "Action Plan",
        "Cautious educational prompts based on the financial snapshot and scam check.",
    )

    current_scam_result = st.session_state.get("scam_result")
    action_plan = generate_combined_action_plan(scored_row, current_scam_result)

    cross_text = generate_cross_feature_alert(scored_row, current_scam_result)
    if cross_text:
        st.markdown(cross_alert_html(cross_text), unsafe_allow_html=True)

    section_header("🔴", "Urgent actions")
    st.markdown(
        action_cards_html(
            action_plan["urgent_actions"],
            style="urgent",
            empty_message=("No urgent action prompts from the current inputs."),
        ),
        unsafe_allow_html=True,
    )

    section_header("📌", "Medium-term actions")
    st.markdown(
        action_cards_html(
            action_plan["medium_term_actions"],
            style="medium",
            empty_message=("No medium-term action prompts from the current inputs."),
        ),
        unsafe_allow_html=True,
    )

    section_header("✅", "Strengths to maintain")
    st.markdown(
        action_cards_html(
            action_plan["positive_actions"],
            style="positive",
            empty_message=("No positive action prompts from the current inputs."),
        ),
        unsafe_allow_html=True,
    )

    support_links = action_plan.get("support_links", [])
    section_header("🔗", "UK support resources")
    if support_links:
        st.caption(
            "UK support resources relevant to the signals above. "
            "Provided for educational signposting only."
        )
        cards_html = "".join(
            support_link_card_html(
                lnk["name"],
                lnk["url"],
                lnk["use_case"],
                lnk.get("reason", ""),
            )
            for lnk in support_links
        )
        st.markdown(cards_html, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="background:#F4F7F5;border:1px dashed #DDE8E3;'
            "border-radius:10px;padding:12px 15px;font-size:13px;"
            'color:#6B8A7F">'
            "ℹ️ No specific support links triggered by current "
            "signals.</div>",
            unsafe_allow_html=True,
        )

    st.caption(str(action_plan["disclaimer"]))

    st.divider()

    # Export buttons
    export_cols = st.columns(2)

    pdf_bytes = build_pdf_report(scored_row, action_plan, current_scam_result)
    export_cols[0].download_button(
        "⬇️ Download PDF report",
        data=pdf_bytes,
        file_name="moneybuffer_uk_educational_report.pdf",
        mime="application/pdf",
        type="primary",
    )

    report_txt = build_text_report(scored_row, action_plan, current_scam_result)
    export_cols[1].download_button(
        "⬇️ Download text report",
        data=report_txt,
        file_name="moneybuffer_uk_educational_report.txt",
        mime="text/plain",
    )

# ── Section 5: How to Use ─────────────────────────────────────────────────

section_divider()
section_anchor("section-guide")
if True:  # scope block
    # ── Hero description ─────────────────────────────────────────────────
    st.markdown(
        """
        <div style="background:linear-gradient(
            135deg,#0D2218 0%,#0F3526 60%,#163D2C 100%);
          border-radius:16px;padding:28px 32px;margin-bottom:1.5rem;
          position:relative;overflow:hidden">
          <div style="position:absolute;inset:0;
            background-image:radial-gradient(
              circle,rgba(0,168,122,0.055) 1px,transparent 1px);
            background-size:24px 24px;pointer-events:none"></div>
          <div style="position:relative">
            <div style="font-size:11px;font-weight:700;
              color:rgba(0,200,150,0.8);text-transform:uppercase;
              letter-spacing:0.1em;margin-bottom:10px">
              About this tool
            </div>
            <div style="font-size:22px;font-weight:700;color:#fff;
              letter-spacing:-0.02em;line-height:1.3;margin-bottom:12px">
              MoneyBuffer UK is a free educational tool<br>
              for UK household financial awareness.
            </div>
            <div style="font-size:13.5px;color:rgba(255,255,255,0.6);
              line-height:1.7;max-width:680px">
              It helps you understand how financially resilient a household
              is, explore what happens under bill shocks or income drops,
              and spot common warning signs in suspicious messages — all
              explained in plain English, with no jargon and no data
              stored.
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── What it IS / What it ISN'T ───────────────────────────────────────
    section_header("⚖️", "What it is — and what it isn't")

    col_is, col_isnot = st.columns(2)

    _IS_ITEMS = [
        (
            "🎓",
            "An educational tool",
            "Designed to prompt reflection about financial resilience "
            "and scam awareness — not to replace professional advice.",
        ),
        (
            "🔍",
            "A scenario explorer",
            "Model what happens if your rent rises, income drops, or an "
            "unexpected bill arrives — see the impact before it happens.",
        ),
        (
            "🛡️",
            "A scam-awareness checker",
            "Apply transparent rule-based checks to suspicious messages "
            "or payment requests and understand the warning signs.",
        ),
        (
            "📊",
            "Explainable and transparent",
            "Every score, red flag, and action prompt is explained in "
            "plain English. No black-box decisions.",
        ),
        (
            "🔒",
            "Privacy-safe",
            "Uses synthetic demo data by default. Nothing you enter is "
            "stored, sent anywhere, or used for any other purpose.",
        ),
    ]

    _ISNOT_ITEMS = [
        (
            "❌",
            "Not financial advice",
            "Outputs are illustrative only. Always consult a qualified, "
            "FCA-regulated adviser for personal financial decisions.",
        ),
        (
            "❌",
            "Not debt or credit advice",
            "It cannot recommend debt management plans, consolidation "
            "loans, or any credit products.",
        ),
        (
            "❌",
            "Not a guaranteed scam detector",
            "It may miss real scams and flag legitimate messages. "
            "Never rely on it as your only check.",
        ),
        (
            "❌",
            "Not a lending or decisioning tool",
            "Scores are for educational reflection only — not credit "
            "scoring, affordability assessment, or underwriting.",
        ),
        (
            "❌",
            "Not based on your real bank data",
            "Demo profiles are fictional. For your own numbers, use the "
            '"Manually edit inputs" toggle in the sidebar.',
        ),
    ]

    def _info_card(
        icon: str, title: str, body: str, bg: str, border: str, fg: str
    ) -> str:
        return (
            f'<div style="background:{bg};border:1px solid {border};'
            f"border-radius:12px;padding:14px 16px;margin-bottom:8px;"
            f'display:flex;gap:12px;align-items:flex-start">'
            f'<span style="font-size:18px;flex-shrink:0;'
            f'line-height:1.3">{icon}</span>'
            f"<div>"
            f'<div style="font-size:13px;font-weight:600;color:{fg};'
            f'margin-bottom:3px">{title}</div>'
            f'<div style="font-size:12.5px;color:#3D5A4E;line-height:1.55">'
            f"{body}</div>"
            f"</div></div>"
        )

    with col_is:
        st.markdown(
            '<div style="font-size:11px;font-weight:700;color:#0A6B4A;'
            "text-transform:uppercase;letter-spacing:0.09em;"
            'margin-bottom:10px">✅ It IS</div>',
            unsafe_allow_html=True,
        )
        for icon, title, body in _IS_ITEMS:
            st.markdown(
                _info_card(icon, title, body, "#F0FBF7", "#A7F3D0", "#0A6B4A"),
                unsafe_allow_html=True,
            )

    with col_isnot:
        st.markdown(
            '<div style="font-size:11px;font-weight:700;color:#9B2220;'
            "text-transform:uppercase;letter-spacing:0.09em;"
            'margin-bottom:10px">🚫 It IS NOT</div>',
            unsafe_allow_html=True,
        )
        for icon, title, body in _ISNOT_ITEMS:
            st.markdown(
                _info_card(icon, title, body, "#FFF5F5", "#FECACA", "#9B2220"),
                unsafe_allow_html=True,
            )

    # ── Step-by-step guide ───────────────────────────────────────────────
    section_header(
        "🗺️", "How to use MoneyBuffer UK", "A quick walkthrough of each section."
    )

    _STEPS = [
        (
            "1",
            "#00A87A",
            "Choose a household profile",
            "Sidebar — Demo household selector",
            "Pick one of the six fictional UK household archetypes from "
            "the sidebar dropdown: Stable Household, Payday Pressure, "
            "High Debt Burden, Irregular Income Worker, Low Savings "
            "Renter, or Mortgage Rate Shock. Each represents a realistic "
            "financial situation. To explore your own numbers, tick "
            '"Manually edit inputs" and adjust each field.',
            [
                "Stable Household — solid buffer, low debt",
                "Payday Pressure — income barely covers essentials",
                "High Debt Burden — large debt repayments eating income",
                "Irregular Income Worker — variable monthly earnings",
                "Low Savings Renter — renting with minimal emergency fund",
                "Mortgage Rate Shock — homeowner hit by rate rise",
            ],
        ),
        (
            "2",
            "#00A87A",
            "Check financial health",
            "Tab: Financial Health Check",
            "See a 0–100 resilience score for the selected household, "
            "an emergency runway (months of essential spending covered "
            "by savings), monthly surplus, and five score-driver bars. "
            "Green is healthy, amber is a watch signal, red needs "
            'attention. The "How to improve" card shows what change '
            "would move the household to the next band.",
            [
                "Score ≥ 75 = Stable · 55–74 = Watch · "
                "35–54 = Vulnerable · < 35 = Critical",
                "Emergency runway < 1 month is a key risk signal",
                "Debt service ratio > 20 % of income is a warning sign",
            ],
        ),
        (
            "3",
            "#F5A623",
            "Simulate a bill shock",
            "Tab: Bill Shock Simulator",
            "Apply a stress scenario — income drop, rent increase, "
            "energy bill spike, one-off expense, or a compound mix of "
            "several shocks at once. The before/after score cards and "
            "chart show how resilience, monthly surplus, and emergency "
            "runway change. The savings runway projection shows how many "
            "months before savings run out under the stressed scenario.",
            [
                "Income drop 20 % / 40 % / 100 % (e.g. job loss)",
                "Rent or mortgage increase 5 % / 10 % / 15 %",
                "Energy bill increase £50 / £100 / £150 per month",
                "Unexpected one-off expense £300 – £3,000",
                "Compound scenario: combine multiple shocks at once",
            ],
        ),
        (
            "4",
            "#9B2220",
            "Check a suspicious message",
            "Tab: Scam Checker",
            "Paste any message, payment request, or email text into the "
            'text box and click "Check scam risk". The tool applies '
            "eight transparent rule-based checks — urgency language, "
            "secrecy requests, suspicious links, risky payment methods, "
            "impersonation cues, and more — and returns a risk score "
            "with a plain-English explanation of each flag. "
            "Always treat the result as a prompt to pause and verify, "
            "never as a guarantee.",
            [
                "Low (0–20): fewer warning signs detected",
                "Medium (21–45): be cautious, verify independently",
                "High (46–70): significant red flags — do not act yet",
                "Severe (71–100): stop, do not pay or respond",
            ],
        ),
        (
            "5",
            "#7C3AED",
            "Review the action plan",
            "Tab: Action Plan",
            "Based on the financial health score and (optionally) the "
            "scam-risk result, the tool generates a set of cautious "
            "educational prompts grouped into urgent actions, "
            "medium-term actions, and positive strengths to maintain. "
            "UK support resource links (StepChange, MoneyHelper, Action "
            "Fraud, etc.) are shown where relevant. You can download a "
            "PDF or text summary for reference.",
            [
                "Urgent — address these signals first",
                "Medium-term — build resilience over weeks or months",
                "Strengths — what is already working well",
                "Support links — official UK organisations relevant "
                "to the signals detected",
            ],
        ),
    ]

    for step_num, color, title, location, desc, bullets in _STEPS:
        bullet_html = "".join(
            f'<div style="display:flex;gap:8px;align-items:flex-start;'
            f'padding:4px 0;font-size:12.5px;color:#3D5A4E;line-height:1.5">'
            f'<span style="color:{color};font-weight:700;flex-shrink:0">'
            f"›</span><span>{b}</span></div>"
            for b in bullets
        )
        st.markdown(
            f'<div style="background:#fff;border:1px solid #DDE8E3;'
            f"border-left:4px solid {color};border-radius:14px;"
            f"padding:20px 22px;margin-bottom:12px;"
            f'box-shadow:0 1px 4px rgba(0,0,0,0.05)">'
            f'<div style="display:flex;align-items:center;gap:12px;'
            f'margin-bottom:10px">'
            f'<div style="width:32px;height:32px;border-radius:50%;'
            f"background:{color};color:#fff;font-size:14px;font-weight:800;"
            f"display:flex;align-items:center;justify-content:center;"
            f'flex-shrink:0">{step_num}</div>'
            f"<div>"
            f'<div style="font-size:15px;font-weight:700;color:#0D2218;'
            f'letter-spacing:-0.01em">{title}</div>'
            f'<div style="font-size:11.5px;color:#6B8A7F;margin-top:1px">'
            f"{location}</div>"
            f"</div></div>"
            f'<div style="font-size:13px;color:#3D5A4E;line-height:1.65;'
            f'margin-bottom:12px">{desc}</div>'
            f'<div style="background:#F4F7F5;border-radius:8px;'
            f'padding:10px 14px">{bullet_html}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    # ── Score band reference ─────────────────────────────────────────────
    section_header("📐", "Score band reference")

    band_cols = st.columns(2)

    with band_cols[0]:
        st.markdown(
            '<div style="font-size:11px;font-weight:700;color:#6B8A7F;'
            "text-transform:uppercase;letter-spacing:0.09em;"
            'margin-bottom:10px">Financial resilience bands</div>'
            + "".join(
                f'<div style="background:{bg};border:1px solid {bg};'
                f"border-radius:10px;padding:10px 14px;margin-bottom:6px;"
                f"display:flex;justify-content:space-between;"
                f'align-items:center">'
                f'<span style="font-weight:600;color:{fg}">{band}</span>'
                f'<span style="font-size:12px;color:{fg};opacity:0.8">'
                f"{rng}</span></div>"
                for band, bg, fg, rng in [
                    ("Stable", "#E0F5EE", "#0A6B4A", "75 – 100"),
                    ("Watch", "#FFF3DC", "#8A5E00", "55 – 74"),
                    ("Vulnerable", "#FDECEA", "#9B2220", "35 – 54"),
                    ("Critical", "#FDECEA", "#7B1414", "0 – 34"),
                ]
            ),
            unsafe_allow_html=True,
        )

    with band_cols[1]:
        st.markdown(
            '<div style="font-size:11px;font-weight:700;color:#6B8A7F;'
            "text-transform:uppercase;letter-spacing:0.09em;"
            'margin-bottom:10px">Scam risk bands</div>'
            + "".join(
                f'<div style="background:{bg};border:1px solid {bg};'
                f"border-radius:10px;padding:10px 14px;margin-bottom:6px;"
                f"display:flex;justify-content:space-between;"
                f'align-items:center">'
                f'<span style="font-weight:600;color:{fg}">{band}</span>'
                f'<span style="font-size:12px;color:{fg};opacity:0.8">'
                f"{rng}</span></div>"
                for band, bg, fg, rng in [
                    ("Low", "#E0F5EE", "#0A6B4A", "0 – 20"),
                    ("Medium", "#FFF3DC", "#8A5E00", "21 – 45"),
                    ("High", "#FDECEA", "#9B2220", "46 – 70"),
                    ("Severe", "#FDECEA", "#7B1414", "71 – 100"),
                ]
            ),
            unsafe_allow_html=True,
        )

    # ── Full disclaimer ──────────────────────────────────────────────────
    section_header("📋", "Full disclaimer")
    st.markdown(
        '<div style="background:#F4F7F5;border:1px solid #DDE8E3;'
        "border-radius:12px;padding:18px 20px;font-size:12.5px;"
        'color:#3D5A4E;line-height:1.75">'
        "<strong style='color:#0D2218'>MoneyBuffer UK is an educational "
        "prototype only.</strong> It is not financial advice, not debt "
        "advice, not investment advice, not a lending tool, not a credit "
        "decisioning system, and not a guaranteed scam detector. "
        "Outputs should be treated as general educational information "
        "and prompts for reflection only.<br><br>"
        "Users should verify important information independently and "
        "contact qualified professionals, FCA-regulated firms, public "
        "services, or trusted support organisations where appropriate. "
        "The tool uses synthetic demo data by default and does not "
        "collect, store, or transmit any personal information."
        "</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

page_footer(__version__)
