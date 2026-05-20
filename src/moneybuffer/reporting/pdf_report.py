"""One-page educational PDF report generator for MoneyBuffer UK."""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from moneybuffer.resilience.explanations import explain_score

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------

_MARGIN = 15  # mm — applied to all four sides
_LINE = 5  # mm — standard line height
_BRAND = (31, 122, 92)  # #1f7a5c dark teal
_GREY = (90, 90, 90)
_AMBER_BG = (255, 243, 205)
_AMBER_BORDER = (200, 150, 0)

_DISCLAIMER = (
    "This is an educational prototype and does not provide regulated financial "
    "advice, debt advice, investment advice, or personalised product recommendations. "
    "Outputs are illustrative only. Always verify important information independently."
)

# Always included regardless of dynamic support-link triggers.
FIXED_SUPPORT_LINKS: tuple[tuple[str, str, str], ...] = (
    (
        "MoneyHelper",
        "moneyhelper.org.uk",
        "Budgeting, debt guidance, pensions and money problems.",
    ),
    (
        "StepChange Debt Charity",
        "stepchange.org",
        "Free debt advice.",
    ),
    (
        "Citizens Advice",
        "citizensadvice.org.uk",
        "Debt, benefits, bills and consumer rights.",
    ),
    (
        "Action Fraud",
        "actionfraud.police.uk",
        "Report fraud and cyber crime.",
    ),
    (
        "FCA ScamSmart",
        "fca.org.uk/scamsmart",
        "Investment and pension scam checks.",
    ),
)


# ---------------------------------------------------------------------------
# Internal rendering helpers
# ---------------------------------------------------------------------------


def _v(row: pd.Series, key: str, default: Any = "") -> Any:
    return row[key] if key in row.index else default


def _section_title(pdf: FPDF, title: str) -> None:
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*_BRAND)
    pdf.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(*_BRAND)
    pdf.set_line_width(0.4)
    y = pdf.get_y()
    pdf.line(_MARGIN, y, _MARGIN + 180, y)
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)


def _kv(pdf: FPDF, label: str, value: str) -> None:
    """Render a bold label followed by a value that wraps if needed."""
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*_GREY)
    pdf.cell(62, _LINE, label, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, _LINE, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _bullet(pdf: FPDF, text: str) -> None:
    """Render a wrapped bullet point indented from the left margin."""
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(_MARGIN + 4)
    pdf.multi_cell(0, _LINE, f"-  {text}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)


def _subsection(pdf: FPDF, title: str) -> None:
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*_GREY)
    pdf.cell(0, 5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(1)


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------


def _render_header(pdf: FPDF) -> None:
    pdf.set_fill_color(*_BRAND)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(
        0,
        14,
        "MoneyBuffer UK  --  Educational Financial Resilience Summary",
        align="C",
        fill=True,
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)


def _render_date(pdf: FPDF) -> None:
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*_GREY)
    pdf.cell(
        0,
        5,
        f"Generated: {date.today().strftime('%d %B %Y')}",
        align="R",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)


def _render_disclaimer(pdf: FPDF) -> None:
    pdf.set_fill_color(*_AMBER_BG)
    pdf.set_draw_color(*_AMBER_BORDER)
    pdf.set_line_width(0.5)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(90, 60, 0)
    pdf.multi_cell(
        0,
        5,
        f"Educational notice:  {_DISCLAIMER}",
        border=1,
        fill=True,
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)
    pdf.ln(2)


def _render_household_summary(pdf: FPDF, row: pd.Series) -> None:
    _section_title(pdf, "Household Summary")

    household_type = str(_v(row, "household_type", "Not specified"))
    household_id = str(_v(row, "household_id", ""))
    score = float(_v(row, "resilience_score", 0))
    risk_band = str(_v(row, "risk_band", "Unknown"))
    runway = float(_v(row, "emergency_runway_months", 0))
    surplus = float(_v(row, "monthly_surplus", 0))
    ess_ratio = float(_v(row, "essential_spending_ratio", 0))
    dsr = float(_v(row, "debt_service_ratio", 0))

    if household_id:
        _kv(pdf, "Household ID:", household_id)
    _kv(pdf, "Household type:", household_type)
    _kv(pdf, "Resilience score:", f"{score:.1f} / 100")
    _kv(pdf, "Risk band:", risk_band)
    _kv(pdf, "Emergency runway:", f"{runway:.1f} months")
    surplus_sign = "" if surplus >= 0 else "-"
    _kv(pdf, "Monthly surplus:", f"GBP {surplus_sign}{abs(surplus):,.0f}")
    _kv(pdf, "Essential spending ratio:", f"{ess_ratio:.0%}")
    _kv(pdf, "Debt service ratio:", f"{dsr:.0%}")


def _render_explanations(pdf: FPDF, row: pd.Series) -> None:
    _section_title(pdf, "Key Score Drivers")
    for explanation in explain_score(row):
        _bullet(pdf, explanation)


def _render_scam_summary(pdf: FPDF, scam_result: dict[str, Any]) -> None:
    _section_title(pdf, "Scam-Risk Summary")
    _kv(pdf, "Risk score:", f"{scam_result.get('risk_score', 0)} / 100")
    _kv(pdf, "Risk band:", str(scam_result.get("risk_band", "Unknown")))
    _kv(pdf, "Scam type:", str(scam_result.get("scam_type", "Not classified")))

    red_flags = list(scam_result.get("red_flags", []))
    if red_flags:
        _subsection(pdf, "Red flags detected:")
        for flag in red_flags[:6]:
            label = str(flag.get("label", "Unknown flag"))
            matches = list(flag.get("matches", []))
            suffix = f": {', '.join(str(m) for m in matches[:3])}" if matches else ""
            _bullet(pdf, f"{label}{suffix}")

    action = str(scam_result.get("recommended_action", ""))
    if action:
        _kv(pdf, "Recommended action:", action)


def _render_action_plan(pdf: FPDF, action_plan: dict[str, Any]) -> None:
    _section_title(pdf, "Action Plan")

    urgent = list(action_plan.get("urgent_actions", []))
    medium = list(action_plan.get("medium_term_actions", []))
    positive = list(action_plan.get("positive_actions", []))

    if urgent:
        _subsection(pdf, "Urgent actions")
        for action in urgent:
            _bullet(pdf, action)

    if medium:
        _subsection(pdf, "Medium-term actions")
        for action in medium:
            _bullet(pdf, action)

    if positive:
        _subsection(pdf, "Positive actions")
        for action in positive:
            _bullet(pdf, action)

    if not urgent and not medium and not positive:
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(
            0,
            _LINE,
            "No action prompts were generated from the current inputs.",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )


def _render_support_links(pdf: FPDF) -> None:
    _section_title(pdf, "UK Support Resources")
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*_GREY)
    pdf.cell(
        0,
        4,
        "Provided for educational signposting only.",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    for name, url, use_case in FIXED_SUPPORT_LINKS:
        _kv(pdf, f"{name}:", f"{url}  --  {use_case}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_pdf_report(
    scored_row: pd.Series,
    action_plan: dict[str, Any],
    scam_result: dict[str, Any] | None = None,
) -> bytes:
    """Generate a one-page educational PDF summary. Returns raw PDF bytes.

    The report covers the household resilience snapshot, top score drivers,
    an optional scam-risk summary, the action plan, and fixed UK support links.
    No user-sensitive data beyond the figures entered into the app is included.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=_MARGIN)
    pdf.set_margins(_MARGIN, _MARGIN, _MARGIN)
    pdf.add_page()

    _render_header(pdf)
    _render_date(pdf)
    _render_disclaimer(pdf)
    _render_household_summary(pdf, scored_row)
    _render_explanations(pdf, scored_row)
    if scam_result:
        _render_scam_summary(pdf, scam_result)
    _render_action_plan(pdf, action_plan)
    _render_support_links(pdf)

    return bytes(pdf.output())
