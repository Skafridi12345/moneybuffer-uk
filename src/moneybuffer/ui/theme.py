"""MoneyBuffer UK — brand CSS injection and HTML component helpers.

Design system adapted from the MoneyBuffer UK HTML prototype.
Colour tokens, typography, card/badge/gauge/driver-bar components.
"""

from __future__ import annotations

import math
from textwrap import dedent
from typing import Any

import streamlit as st

# ---------------------------------------------------------------------------
# Google Fonts URL (interpolated into CSS to keep source lines short)
# ---------------------------------------------------------------------------

_GF = (
    "https://fonts.googleapis.com/css2"
    "?family=Plus+Jakarta+Sans:wght@300;400;500;600;700"
    "&display=swap"
)

# ---------------------------------------------------------------------------
# Inline SVG logo
# ---------------------------------------------------------------------------


def logo_svg(w: int = 40, h: int = 40) -> str:
    """Return the MoneyBuffer UK shield/wallet/coin SVG logo as HTML."""
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 40 40" fill="none"'
        ' xmlns="http://www.w3.org/2000/svg">'
        '<circle cx="20" cy="20" r="17.5" fill="none" stroke="#F5A623"'
        ' stroke-width="3" stroke-linecap="round"'
        ' stroke-dasharray="82 28" stroke-dashoffset="19"/>'
        '<circle cx="20" cy="20" r="17.5" fill="none" stroke="#00C896"'
        ' stroke-width="3" stroke-linecap="round"'
        ' stroke-dasharray="36 74" stroke-dashoffset="-63"/>'
        '<path d="M20 7L30.5 11V19.5C30.5 27 20 32.5 20 32.5'
        'C20 32.5 9.5 27 9.5 19.5V11Z" fill="#0A3050"/>'
        '<path d="M20 32.5C20 32.5 9.5 27 9.5 19.5'
        'V25.5C9.5 29 14 32 20 32.5Z" fill="#004E38" opacity="0.55"/>'
        '<rect x="11.5" y="20.5" width="11.5" height="8"'
        ' rx="1.5" fill="#00A87A"/>'
        '<rect x="11.5" y="19" width="11.5" height="3"'
        ' rx="1" fill="#00C896"/>'
        '<rect x="19.5" y="21.5" width="3.5" height="5"'
        ' rx="0.7" fill="#0A3050" opacity="0.65"/>'
        '<rect x="25" y="24.5" width="2" height="4"'
        ' rx="0.4" fill="#7ED8C4"/>'
        '<rect x="28" y="22" width="2" height="6.5"'
        ' rx="0.4" fill="#00C896"/>'
        '<circle cx="17.5" cy="19.5" r="5.5" fill="#F5A623"/>'
        '<circle cx="17.5" cy="19.5" r="4" fill="#F7B83A" opacity="0.4"/>'
        '<text x="17.5" y="22.6" font-size="6.5" font-weight="bold"'
        ' fill="#5A3200" text-anchor="middle"'
        ' font-family="Georgia,serif">£</text>'
        "</svg>"
    )


# ---------------------------------------------------------------------------
# Brand CSS
# ---------------------------------------------------------------------------

_CSS = f"""
<style>
@import url('{_GF}');

/* ── Design tokens ──────────────────────────────────────────────────────── */
:root {{
  --mb-navy:        #0D2218;
  --mb-navy-mid:    #163320;
  --mb-navy-light:  #1F4A2E;
  --mb-teal:        #00A87A;
  --mb-teal-bright: #00C896;
  --mb-teal-pale:   #E0F5EE;
  --mb-gold:        #F5A623;
  --mb-gold-pale:   #FEF3DC;
  --mb-bg:          #F4F7F5;
  --mb-surface:     #FFFFFF;
  --mb-border:      #DDE8E3;
  --mb-text:        #1A2E25;
  --mb-text-mid:    #3D5A4E;
  --mb-text-muted:  #6B8A7F;
  --mb-success-bg:  #E0F5EE;
  --mb-success-txt: #0A6B4A;
  --mb-warn-bg:     #FFF3DC;
  --mb-warn-txt:    #8A5E00;
  --mb-danger-bg:   #FDECEA;
  --mb-danger-txt:  #9B2220;
  --mb-info-bg:     #E8F2FD;
  --mb-info-txt:    #1D5FAE;
  --mb-radius:      14px;
  --mb-shadow:      0 1px 3px rgba(0,0,0,0.06);
}}

/* ── Global ─────────────────────────────────────────────────────────────── */
html {{ scroll-behavior: smooth !important; }}
.stApp {{
    background: var(--mb-bg) !important;
}}
.block-container {{
    padding-top: 1.25rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 1340px !important;
}}
html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', Inter, 'Segoe UI',
        system-ui, -apple-system, sans-serif !important;
    color: var(--mb-text);
    -webkit-font-smoothing: antialiased;
}}

/* ── Hide sidebar entirely ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {{ display: none !important; }}
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {{
    display: none !important;
}}
a {{ color: var(--mb-teal) !important; }}
hr {{
    border-color: var(--mb-border) !important;
    margin: 1.25rem 0 !important;
}}

/* ── Scrollbar (Webkit) ─────────────────────────────────────────────────── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: var(--mb-bg); }}
::-webkit-scrollbar-thumb {{
    background: #C4D4CE;
    border-radius: 10px;
}}
::-webkit-scrollbar-thumb:hover {{ background: #A8BEB6; }}

/* ── Sidebar — dark navy ────────────────────────────────────────────────── */
[data-testid="stSidebar"] > div:first-child {{
    background-color: var(--mb-navy) !important;
    border-right: none !important;
}}
[data-testid="stSidebar"] label {{
    color: rgba(255,255,255,0.65) !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] span {{
    color: rgba(255,255,255,0.65);
}}
[data-testid="stSidebar"] .stSelectbox > div > div {{
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    color: #fff !important;
    border-radius: 10px !important;
}}
[data-testid="stSidebar"] .stSelectbox svg {{
    fill: rgba(255,255,255,0.5) !important;
}}
[data-testid="stSidebar"] .stNumberInput input {{
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    color: #fff !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] .stCheckbox span {{
    color: rgba(255,255,255,0.65) !important;
}}
[data-testid="stSidebar"] .stCheckbox > label:hover span {{
    color: #fff !important;
}}

/* ── Metric cards ───────────────────────────────────────────────────────── */
[data-testid="metric-container"] {{
    background: var(--mb-surface);
    border: 1px solid var(--mb-border);
    border-radius: var(--mb-radius);
    padding: 16px 18px 14px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05),
                0 0 0 0 transparent;
    transition: box-shadow .18s ease;
}}
[data-testid="metric-container"]:hover {{
    box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
}}
[data-testid="metric-container"]::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--mb-teal);
    border-radius: var(--mb-radius) var(--mb-radius) 0 0;
}}
[data-testid="stMetricLabel"] > div {{
    font-size: 10px !important;
    color: var(--mb-text-muted) !important;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 700;
    margin-bottom: 4px !important;
}}
[data-testid="stMetricValue"] > div {{
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    color: var(--mb-navy) !important;
    letter-spacing: -0.025em;
}}
[data-testid="stMetricDelta"] > div {{
    font-size: 0.82rem !important;
}}

/* ── Tab styles: handled via JS injection in _inject_tab_override() ──────── */
/* This approach writes a <style> node directly into the parent document      */
/* after React/Baseweb renders, so it wins the cascade without specificity    */
/* battles. See _TAB_CSS and _inject_tab_override() below inject_brand_css(). */

/* ── Buttons ────────────────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {{
    background: var(--mb-teal) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
    padding: 10px 22px !important;
    font-size: 13px !important;
    transition: opacity .18s ease, transform .18s ease !important;
}}
.stButton > button[kind="primary"]:hover {{
    opacity: 0.87 !important;
    transform: translateY(-1px) !important;
}}
.stButton > button[kind="primary"]:active {{
    transform: translateY(0) !important;
}}
.stDownloadButton > button {{
    border: 1px solid var(--mb-border) !important;
    border-radius: 10px !important;
    color: var(--mb-text-mid) !important;
    background: var(--mb-surface) !important;
    font-weight: 500 !important;
}}
.stDownloadButton > button:hover {{
    border-color: var(--mb-teal) !important;
    color: var(--mb-teal) !important;
}}

/* ── Inputs ─────────────────────────────────────────────────────────────── */
.stTextArea textarea {{
    border: 1px solid var(--mb-border) !important;
    border-radius: 10px !important;
    font-family: inherit !important;
    color: var(--mb-text) !important;
    background: var(--mb-surface) !important;
}}
.stTextArea textarea:focus {{
    border-color: var(--mb-teal) !important;
    box-shadow: 0 0 0 3px rgba(0,168,122,0.12) !important;
}}
.stSelectbox > div > div {{
    border: 1px solid var(--mb-border) !important;
    border-radius: 10px !important;
    background: var(--mb-surface) !important;
}}
.stSelectbox > div > div:focus-within {{
    border-color: var(--mb-teal) !important;
    box-shadow: 0 0 0 3px rgba(0,168,122,0.12) !important;
}}
.stNumberInput > div > div > input {{
    border-radius: 8px !important;
}}

/* ── Expander ───────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {{
    background: var(--mb-surface) !important;
    border: 1px solid var(--mb-border) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    color: var(--mb-text) !important;
}}
.streamlit-expanderHeader:hover {{
    background: var(--mb-bg) !important;
}}

/* ── Alerts ─────────────────────────────────────────────────────────────── */
.stAlert {{
    border-radius: 10px !important;
    font-size: 13px !important;
}}

/* ── Caption / small text ───────────────────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {{
    font-size: 11.5px !important;
    color: var(--mb-text-muted) !important;
}}

/* ── Radio buttons ──────────────────────────────────────────────────────── */
.stRadio label span {{ font-size: 13px; }}

/* ── Plotly chart card wrapper ──────────────────────────────────────────── */
[data-testid="stPlotlyChart"] {{
    background: var(--mb-surface) !important;
    border: 1px solid var(--mb-border) !important;
    border-radius: 14px !important;
    padding: 8px 4px 4px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
}}

/* ── Native alert refinements ───────────────────────────────────────────── */
.stAlert > div, [data-testid="stNotification"] {{
    border-radius: 10px !important;
    font-size: 13px !important;
}}

/* ── Expander refinements ───────────────────────────────────────────────── */
[data-testid="stExpander"] > details {{
    border: 1px solid var(--mb-border) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}}
[data-testid="stExpander"] > details > summary {{
    padding: 12px 16px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    background: var(--mb-surface) !important;
}}
[data-testid="stExpander"] > details > summary:hover {{
    background: var(--mb-bg) !important;
}}
[data-testid="stExpander"] > details[open] > summary {{
    border-bottom: 1px solid var(--mb-border) !important;
}}
[data-testid="stExpander"] > details > div {{
    padding: 14px 16px !important;
}}

/* ── Sticky section nav bar ─────────────────────────────────────────────── */
.mb-nav-wrap {{
    position: sticky;
    top: 0;
    z-index: 998;
    background: var(--mb-bg);
    padding: 8px 0 10px;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--mb-border);
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}}
.mb-nav-bar {{
    display: flex;
    gap: 3px;
    background: #E8EFEC;
    padding: 5px 6px;
    border-radius: 14px;
    border: 1px solid #D4E2DC;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.07);
    width: fit-content;
}}
.mb-nav-bar a {{
    height: 40px;
    padding: 0 20px;
    border-radius: 10px;
    font-size: 13.5px;
    font-weight: 500;
    color: #6B8A7F !important;
    background: transparent;
    text-decoration: none !important;
    display: flex;
    align-items: center;
    white-space: nowrap;
    transition: background .18s ease, color .18s ease;
    border: none;
}}
.mb-nav-bar a:hover {{
    color: #1A2E25 !important;
    background: rgba(255,255,255,0.72) !important;
    text-decoration: none !important;
}}

/* ── Between-section divider ────────────────────────────────────────────── */
.mb-section-sep {{
    border: none;
    border-top: 2px solid #DDE8E3;
    margin: 3rem 0 2rem;
}}

/* ── Control card (household selector) ─────────────────────────────────── */
[data-testid="stSelectbox"] > label,
[data-testid="stCheckbox"] > label {{
    font-size: 12px !important;
    font-weight: 600 !important;
    color: var(--mb-text-muted) !important;
    text-transform: uppercase;
    letter-spacing: .07em;
}}

/* ── Mobile / responsive ─────────────────────────────────────────────────── */
@media (max-width: 768px) {{
  /* Reduce side padding on small screens */
  .block-container {{
    padding-left: 0.6rem !important;
    padding-right: 0.6rem !important;
    padding-top: 0.75rem !important;
  }}

  /* Nav bar: scroll horizontally — hide scrollbar for cleanliness */
  .mb-nav-wrap {{
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    padding-bottom: 6px !important;
    scrollbar-width: none !important;
  }}
  .mb-nav-wrap::-webkit-scrollbar {{ display: none !important; }}
  .mb-nav-bar {{
    min-width: max-content !important;
  }}
  .mb-nav-bar a {{
    padding: 0 14px !important;
    font-size: 12.5px !important;
    height: 36px !important;
  }}

  /* Hero gauge card: gauge centred on top, KPI grid below */
  .mb-hero-card {{
    grid-template-columns: 1fr !important;
    gap: 16px 0 !important;
    padding: 18px 16px !important;
  }}
  /* The thin vertical divider becomes a horizontal rule */
  .mb-hero-divider {{
    height: 1px !important;
    width: 100% !important;
    min-height: 0 !important;
    align-self: auto !important;
  }}

  /* Comparison cards: stack before/after vertically */
  .mb-comparison-grid {{
    grid-template-columns: 1fr !important;
  }}

  /* Scam card: allow inner blocks to stack */
  .mb-scam-card {{
    gap: 14px !important;
  }}
  .mb-scam-divider {{
    display: none !important;
  }}

  /* Section header: tighten spacing */
  .mb-section-sep {{
    margin: 2rem 0 1.25rem !important;
  }}

  /* Streamlit horizontal blocks: allow wrapping so wide layouts reflow */
  [data-testid="stHorizontalBlock"] {{
    flex-wrap: wrap !important;
  }}
  /* Individual columns: allow shrinking below their natural min-width */
  [data-testid="stColumn"] {{
    min-width: 0 !important;
    flex-shrink: 1 !important;
  }}
}}

@media (max-width: 480px) {{
  /* Extra-small phones (iPhone SE etc.) */
  .mb-nav-bar a {{
    padding: 0 11px !important;
    font-size: 12px !important;
  }}
  .mb-hero-card {{
    border-radius: 14px !important;
    padding: 16px 12px !important;
  }}
}}

/* ── Streamlit footer ───────────────────────────────────────────────────── */
footer {{ display: none !important; }}
#MainMenu {{ visibility: hidden; }}
</style>
"""


def inject_brand_css() -> None:
    """Inject MoneyBuffer UK brand CSS into the Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)
    _inject_tab_override()


# ---------------------------------------------------------------------------
# Tab override via JS — bypasses Baseweb CSS-in-JS specificity entirely
# ---------------------------------------------------------------------------

_TAB_CSS = """
.stTabs [data-baseweb="tab-list"],
div[data-testid="stTabs"] [data-baseweb="tab-list"],
div.stTabs div[data-baseweb="tab-list"] {
  background: #E8EFEC !important;
  padding: 5px 6px !important;
  border-radius: 14px !important;
  border: 1px solid #D4E2DC !important;
  gap: 3px !important;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.07) !important;
  overflow: visible !important;
  flex-wrap: nowrap !important;
}
.stTabs [data-baseweb="tab"],
.stTabs button[role="tab"],
div[data-testid="stTabs"] button[role="tab"] {
  height: 42px !important;
  padding: 0 20px !important;
  font-size: 13.5px !important;
  font-weight: 500 !important;
  letter-spacing: -0.01em !important;
  color: #6B8A7F !important;
  background: transparent !important;
  border: none !important;
  border-radius: 10px !important;
  transition: all .2s ease !important;
  white-space: nowrap !important;
  outline: none !important;
}
.stTabs [data-baseweb="tab"]:hover,
.stTabs button[role="tab"]:hover,
div[data-testid="stTabs"] button[role="tab"]:hover {
  color: #1A2E25 !important;
  background: rgba(255,255,255,0.7) !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"],
.stTabs button[role="tab"][aria-selected="true"],
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"],
.stTabs [aria-selected="true"] {
  background: #0D2218 !important;
  color: #ffffff !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
  border: none !important;
  border-bottom: none !important;
  box-shadow: 0 2px 8px rgba(13,34,24,0.25), 0 1px 2px rgba(13,34,24,0.15) !important;
}
.stTabs [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
  opacity: 0 !important;
}
.stTabs [data-baseweb="tab-border"],
div[data-testid="stTabs"] [data-baseweb="tab-border"] {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
  opacity: 0 !important;
}
.stTabs [data-baseweb="tab-panel"],
div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
  padding-top: 1.75rem !important;
  background: transparent !important;
}
@media (max-width: 760px) {
  .stTabs [data-baseweb="tab-list"],
  div[data-testid="stTabs"] [data-baseweb="tab-list"],
  div.stTabs div[data-baseweb="tab-list"] {
    flex-wrap: wrap !important;
    gap: 5px !important;
  }
  .stTabs [data-baseweb="tab"],
  .stTabs button[role="tab"],
  div[data-testid="stTabs"] button[role="tab"] {
    flex: 1 1 calc(50% - 6px) !important;
    min-width: 0 !important;
    padding: 0 8px !important;
    justify-content: center !important;
  }
  .stTabs [data-baseweb="tab"] p,
  .stTabs button[role="tab"] p,
  div[data-testid="stTabs"] button[role="tab"] p {
    overflow: hidden !important;
    text-overflow: ellipsis !important;
  }
}
"""


def _inject_tab_override() -> None:
    """Inject tab pill CSS without adding a visible iframe component."""
    st.markdown(f"<style>{_TAB_CSS}</style>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Page-level components
# ---------------------------------------------------------------------------


def brand_header(version: str) -> None:
    """Render the premium dark-gradient page header."""
    _dot = (
        "position:absolute;inset:0;"
        "background-image:radial-gradient("
        "circle,rgba(0,168,122,0.055) 1px,transparent 1px);"
        "background-size:24px 24px;pointer-events:none"
    )
    _glow = (
        "position:absolute;top:-60px;right:60px;"
        "width:220px;height:220px;"
        "background:radial-gradient("
        "circle,rgba(0,200,150,0.10) 0%,transparent 70%);"
        "pointer-events:none"
    )
    st.markdown(
        f"""
        <div style="background:linear-gradient(
            135deg,#0D2218 0%,#0F3526 60%,#163D2C 100%);
          border-radius:18px;padding:22px 28px;margin-bottom:1.25rem;
          display:flex;align-items:center;gap:18px;flex-wrap:wrap;
          box-shadow:0 4px 24px rgba(13,34,24,0.18);
          border:1px solid rgba(0,168,122,0.18);
          position:relative;overflow:hidden">
          <div style="{_dot}"></div>
          <div style="{_glow}"></div>
          <div style="position:relative;flex-shrink:0">{logo_svg(54, 54)}</div>
          <div style="flex:1;position:relative;min-width:200px">
            <div style="display:flex;align-items:center;gap:9px;
              flex-wrap:wrap;margin-bottom:5px">
              <span style="font-size:21px;font-weight:700;color:#fff;
                letter-spacing:-0.03em;line-height:1">MoneyBuffer UK</span>
              <span style="font-size:10px;font-weight:700;
                background:rgba(0,168,122,0.22);color:#00C896;
                padding:2px 9px;border-radius:20px;letter-spacing:0.04em;
                border:1px solid rgba(0,200,150,0.28)">v{version}</span>
              <span style="font-size:10px;font-weight:600;
                background:rgba(245,166,35,0.14);color:#F5A623;
                padding:2px 9px;border-radius:20px;letter-spacing:0.04em;
                border:1px solid rgba(245,166,35,0.22)">Educational</span>
            </div>
            <div style="font-size:12.5px;color:rgba(255,255,255,0.45)">
              Household financial resilience &amp; scam-risk
              checker&nbsp;·&nbsp;UK
            </div>
          </div>
          <div style="display:flex;gap:8px;flex-shrink:0;position:relative">
            <div style="background:rgba(255,255,255,0.06);
              border:1px solid rgba(255,255,255,0.10);
              border-radius:10px;padding:8px 14px;text-align:center">
              <div style="font-size:20px;font-weight:700;color:#fff;
                line-height:1">5+</div>
              <div style="font-size:9px;color:rgba(255,255,255,0.38);
                text-transform:uppercase;letter-spacing:0.07em;
                margin-top:2px">Scenarios</div>
            </div>
            <div style="background:rgba(255,255,255,0.06);
              border:1px solid rgba(255,255,255,0.10);
              border-radius:10px;padding:8px 14px;text-align:center">
              <div style="font-size:20px;font-weight:700;color:#00C896;
                line-height:1">8+</div>
              <div style="font-size:9px;color:rgba(255,255,255,0.38);
                text-transform:uppercase;letter-spacing:0.07em;
                margin-top:2px">Scam rules</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand(version: str) -> None:
    """Render the sidebar brand block (logo + title + version)."""
    st.sidebar.markdown(
        dedent(
            f"""
        <div style="padding:20px 16px 16px;
          border-bottom:1px solid rgba(255,255,255,0.09)">
          <div style="display:flex;align-items:center;
            gap:10px;margin-bottom:4px">
            {logo_svg(38, 38)}
            <div>
              <div style="font-size:15px;font-weight:700;color:#fff;
                letter-spacing:-0.01em">MoneyBuffer UK</div>
              <div style="display:inline-block;font-size:10px;
                font-weight:700;background:#00A87A;color:#fff;
                padding:2px 8px;border-radius:20px;
                letter-spacing:0.04em;margin-top:3px">v{version}</div>
            </div>
          </div>
          <div style="font-size:11.5px;color:rgba(255,255,255,0.35);
            margin-top:5px">
            Educational MVP &nbsp;·&nbsp; Not financial advice
          </div>
        </div>
        """
        ),
        unsafe_allow_html=True,
    )


def sidebar_disclaimer(text: str) -> None:
    """Render the disclaimer card in the sidebar."""
    st.sidebar.markdown(
        dedent(
            f"""
        <div style="margin:14px;background:rgba(255,255,255,0.05);
          border:1px solid rgba(255,255,255,0.09);border-radius:10px;
          padding:11px 13px;font-size:11.5px;
          color:rgba(255,255,255,0.45);line-height:1.55">
          <strong style="color:rgba(255,255,255,0.65)">
            Educational prototype only.
          </strong>
          {text}
        </div>
        """
        ),
        unsafe_allow_html=True,
    )


def sidebar_section_label(label: str) -> None:
    """Render a small section label in the sidebar."""
    st.sidebar.markdown(
        f'<div style="font-size:10px;font-weight:700;letter-spacing:0.1em;'
        f"color:rgba(255,255,255,0.3);text-transform:uppercase;"
        f'padding:18px 16px 9px">{label}</div>',
        unsafe_allow_html=True,
    )


def section_header(icon: str, title: str, subtitle: str = "") -> None:
    """Render a section heading with a teal icon badge and optional subtitle."""
    sub_html = (
        f'<div style="font-size:12.5px;color:#6B8A7F;margin-top:2px">{subtitle}</div>'
        if subtitle
        else ""
    )
    st.markdown(
        '<div style="margin:1.75rem 0 1rem;padding-bottom:12px;'
        'border-bottom:1px solid #DDE8E3">'
        '<div style="display:flex;align-items:flex-start;gap:10px">'
        '<div style="width:30px;height:30px;background:#E0F5EE;'
        "border-radius:8px;display:flex;align-items:center;"
        "justify-content:center;font-size:14px;flex-shrink:0;"
        'margin-top:1px">'
        f"{icon}</div>"
        "<div>"
        '<div style="font-size:15.5px;font-weight:700;color:#0D2218;'
        f'letter-spacing:-0.015em;line-height:1.3;padding-top:3px">'
        f"{title}</div>"
        f"{sub_html}"
        "</div></div></div>",
        unsafe_allow_html=True,
    )


def page_footer(version: str) -> None:
    """Render the page footer."""
    st.markdown(
        dedent(
            f"""
        <div style="margin-top:3rem;padding:1.25rem 0;
          border-top:1px solid #DDE8E3;font-size:11.5px;
          color:#6B8A7F;text-align:center;line-height:1.6">
          MoneyBuffer UK &nbsp;·&nbsp; Educational prototype
          &nbsp;·&nbsp; v{version} &nbsp;·&nbsp;
          Not financial advice &nbsp;·&nbsp;
          Not a guaranteed scam detector<br>
          Outputs are illustrative only.
          Always verify important information independently.
        </div>
        """
        ),
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Risk & scam band config
# ---------------------------------------------------------------------------

_BAND_CFG: dict[str, tuple[str, str]] = {
    "Stable": ("#E0F5EE", "#0A6B4A"),
    "Watch": ("#FFF3DC", "#8A5E00"),
    "Vulnerable": ("#FDECEA", "#9B2220"),
    "Critical": ("#FDECEA", "#9B2220"),
}

_SCAM_BAND_CFG: dict[str, tuple[str, str]] = {
    "Low": ("#E0F5EE", "#0A6B4A"),
    "Medium": ("#FFF3DC", "#8A5E00"),
    "High": ("#FDECEA", "#9B2220"),
    "Severe": ("#FDECEA", "#9B2220"),
}


def risk_badge(band: str, prefix: str = "Risk band") -> None:
    """Render a coloured risk-band pill badge."""
    bg, fg = _BAND_CFG.get(band, ("#FFF3DC", "#8A5E00"))
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:7px;'
        f"padding:6px 14px;border-radius:100px;font-size:12.5px;"
        f'font-weight:600;background:{bg};color:{fg};margin:4px 0 16px">'
        f'<span style="width:7px;height:7px;border-radius:50%;'
        f'background:{fg};display:inline-block"></span>'
        f"{prefix}: {band}</div>",
        unsafe_allow_html=True,
    )


def scam_badge(band: str) -> None:
    """Render a coloured scam-risk pill badge."""
    bg, fg = _SCAM_BAND_CFG.get(band, ("#FFF3DC", "#8A5E00"))
    st.markdown(
        f'<div style="display:inline-flex;align-items:center;gap:7px;'
        f"padding:6px 14px;border-radius:100px;font-size:12.5px;"
        f'font-weight:600;background:{bg};color:{fg};margin:4px 0 16px">'
        f'<span style="width:7px;height:7px;border-radius:50%;'
        f'background:{fg};display:inline-block"></span>'
        f"Scam-risk: {band}</div>",
        unsafe_allow_html=True,
    )


def warning_banner(text: str) -> None:
    """Render a full-width amber warning notice with left accent border."""
    st.markdown(
        '<div style="background:#FFFBF0;border:1px solid #FDE68A;'
        "border-left:3px solid #D97706;border-radius:10px;"
        "padding:11px 15px;font-size:13px;color:#7A4A00;"
        "margin-bottom:16px;display:flex;gap:10px;"
        'align-items:flex-start">'
        '<span style="flex-shrink:0;font-size:16px;line-height:1.4">⚠️</span>'
        f'<span style="line-height:1.6">{text}</span></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Score gauge (computed in Python, rendered as static SVG)
# ---------------------------------------------------------------------------


def _polar(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def _arc_d(cx: float, cy: float, r: float, start: float, sweep: float) -> str:
    sx, sy = _polar(cx, cy, r, start)
    ex, ey = _polar(cx, cy, r, start + sweep)
    lg = 1 if sweep > 180 else 0
    return f"M {sx:.2f} {sy:.2f} A {r:.0f} {r:.0f} 0 {lg} 1 {ex:.2f} {ey:.2f}"


def gauge_html(score: float, band: str, narrative: str = "") -> str:
    """
    Return HTML for the semi-circular resilience gauge card.

    Geometry: cx=85, cy=79, r=55, start=135°, sweep=270°.
    SVG glow filter applied to the filled arc for a premium look.
    """
    cx, cy, r = 85.0, 79.0, 55.0
    bg_d = _arc_d(cx, cy, r, 135.0, 270.0)
    fill_sweep = max((score / 100.0) * 270.0, 0.5)
    fill_d = _arc_d(cx, cy, r, 135.0, fill_sweep)

    if score >= 70:
        arc_color = "#00A87A"
    elif score >= 50:
        arc_color = "#F5A623"
    else:
        arc_color = "#C0392B"

    bg_badge, fg_badge = _BAND_CFG.get(band, ("#FFF3DC", "#8A5E00"))

    narrative_html = (
        f'<div style="font-size:12.5px;color:#6B8A7F;'
        f"line-height:1.6;margin-top:7px;max-width:420px"
        f">{narrative}</div>"
        if narrative
        else ""
    )

    return f"""
    <div style="background:#fff;border:1px solid #DDE8E3;
      border-radius:16px;padding:22px 26px;margin-bottom:18px;
      display:flex;align-items:center;gap:28px;flex-wrap:wrap;
      box-shadow:0 2px 12px rgba(0,0,0,0.06)">
      <div style="position:relative;flex-shrink:0;width:170px;height:138px">
        <svg width="170" height="138" viewBox="0 0 170 138">
          <defs>
            <filter id="mbGaugeGlow"
              x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3.5" result="blur"/>
              <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          <path d="{bg_d}" stroke="#EEF3F0" stroke-width="16"
            fill="none" stroke-linecap="round"/>
          <path d="{fill_d}" stroke="{arc_color}" stroke-width="16"
            fill="none" stroke-linecap="round"
            filter="url(#mbGaugeGlow)"/>
        </svg>
        <div style="position:absolute;inset:0;display:flex;
          flex-direction:column;align-items:center;
          justify-content:center;padding-top:6px">
          <div style="font-size:38px;font-weight:800;color:#0D2218;
            letter-spacing:-0.035em;line-height:1">{score:.0f}</div>
          <div style="font-size:12px;color:{arc_color};font-weight:600;
            margin-top:2px">/ 100</div>
        </div>
      </div>
      <div style="flex:1;min-width:170px">
        <div style="font-size:10.5px;font-weight:700;color:#6B8A7F;
          text-transform:uppercase;letter-spacing:0.09em;
          margin-bottom:5px">Financial Resilience Score</div>
        <div style="font-size:22px;font-weight:700;color:#0D2218;
          letter-spacing:-0.02em;line-height:1.2;margin-bottom:11px">
          {band} household
        </div>
        <div style="display:inline-flex;align-items:center;gap:6px;
          padding:5px 14px;border-radius:100px;font-size:12.5px;
          font-weight:600;background:{bg_badge};color:{fg_badge}">
          <span style="width:7px;height:7px;border-radius:50%;
            background:{fg_badge};display:inline-block"></span>
          Risk band: {band}
        </div>
        {narrative_html}
      </div>
    </div>"""


# ---------------------------------------------------------------------------
# Gauge hero card (Option D — two-column with 2×2 KPI grid)
# ---------------------------------------------------------------------------


def gauge_hero_html(scored_row: Any) -> str:
    """Return HTML for the premium two-column gauge hero card.

    Left column: animated SVG gauge with score + band pill.
    Right column: 2×2 KPI grid (Emergency Runway, Monthly Surplus,
    Debt Service Ratio, Essential Spending Ratio).
    """
    score = _safe_float(scored_row, "resilience_score")
    band = str(scored_row["risk_band"]) if "risk_band" in scored_row else "Watch"

    cx, cy, r = 85.0, 79.0, 55.0
    bg_d = _arc_d(cx, cy, r, 135.0, 270.0)
    fill_sweep = max((score / 100.0) * 270.0, 0.5)
    fill_d = _arc_d(cx, cy, r, 135.0, fill_sweep)

    if score >= 70:
        arc_color = "#00A87A"
    elif score >= 50:
        arc_color = "#F5A623"
    else:
        arc_color = "#C0392B"

    bg_badge, fg_badge = _BAND_CFG.get(band, ("#FFF3DC", "#8A5E00"))

    # KPI values
    runway = _safe_float(scored_row, "emergency_runway_months")
    surplus = _safe_float(scored_row, "monthly_surplus")
    dsr = _safe_float(scored_row, "debt_service_ratio")
    esr = _safe_float(scored_row, "essential_spending_ratio")

    def _kpi_color(val: float, good: float, bad: float) -> str:
        """Return a semantic colour — green/amber/red relative to thresholds."""
        if good > bad:  # higher is better (runway, surplus)
            if val >= good:
                return "#00A87A"
            if val >= bad:
                return "#D97706"
            return "#C0392B"
        else:  # lower is better (ratios)
            if val <= good:
                return "#00A87A"
            if val <= bad:
                return "#D97706"
            return "#C0392B"

    runway_c = _kpi_color(runway, 3.0, 1.0)
    surplus_c = _kpi_color(surplus, 200.0, 0.0)
    dsr_c = _kpi_color(dsr, 0.25, 0.40)
    esr_c = _kpi_color(esr, 0.50, 0.65)

    def _tile(label: str, value: str, color: str) -> str:
        return (
            '<div style="background:#F4F7F5;border:1px solid #DDE8E3;'
            "border-radius:10px;padding:12px 14px;"
            'box-shadow:0 1px 2px rgba(0,0,0,0.03)">'
            f'<div style="font-size:9.5px;font-weight:700;'
            f"text-transform:uppercase;letter-spacing:0.09em;"
            f'color:#6B8A7F;margin-bottom:5px">{label}</div>'
            f'<div style="font-size:19px;font-weight:700;'
            f'color:{color};letter-spacing:-0.02em;line-height:1">'
            f"{value}</div>"
            "</div>"
        )

    tiles = (
        _tile(
            "Emergency Runway",
            f"{runway:.1f} mo",
            runway_c,
        )
        + _tile(
            "Monthly Surplus",
            f"£{surplus:+,.0f}",
            surplus_c,
        )
        + _tile(
            "Debt Service Ratio",
            f"{dsr * 100:.0f}%",
            dsr_c,
        )
        + _tile(
            "Essential Spending",
            f"{esr * 100:.0f}%",
            esr_c,
        )
    )

    return (
        '<div class="mb-hero-card" style="background:#fff;'
        "border:1px solid #DDE8E3;"
        "border-radius:18px;padding:24px 28px;margin-bottom:18px;"
        "display:grid;"
        "grid-template-columns:auto 1px 1fr;"
        "gap:0 28px;align-items:center;"
        'box-shadow:0 2px 14px rgba(0,0,0,0.07)">'
        # ── Left: gauge SVG ───────────────────────────────────────────────
        '<div style="display:flex;flex-direction:column;'
        'align-items:center;flex-shrink:0">'
        '<div style="position:relative;width:170px;height:138px">'
        '<svg width="170" height="138" viewBox="0 0 170 138">'
        "<defs>"
        '<filter id="mbHeroGlow" x="-20%" y="-20%" width="140%" height="140%">'
        '<feGaussianBlur stdDeviation="3.5" result="blur"/>'
        "<feMerge>"
        '<feMergeNode in="blur"/>'
        '<feMergeNode in="SourceGraphic"/>'
        "</feMerge>"
        "</filter>"
        "</defs>"
        f'<path d="{bg_d}" stroke="#EEF3F0" stroke-width="16"'
        ' fill="none" stroke-linecap="round"/>'
        f'<path d="{fill_d}" stroke="{arc_color}" stroke-width="16"'
        ' fill="none" stroke-linecap="round" filter="url(#mbHeroGlow)"/>'
        "</svg>"
        '<div style="position:absolute;inset:0;display:flex;'
        "flex-direction:column;align-items:center;"
        'justify-content:center;padding-top:6px">'
        f'<div style="font-size:40px;font-weight:800;color:#0D2218;'
        f'letter-spacing:-0.04em;line-height:1">{score:.0f}</div>'
        f'<div style="font-size:12px;color:{arc_color};font-weight:600;'
        f'margin-top:2px">/ 100</div>'
        "</div>"
        "</div>"
        '<div style="font-size:10.5px;font-weight:700;color:#6B8A7F;'
        "text-transform:uppercase;letter-spacing:0.09em;"
        'margin:8px 0 7px;text-align:center">Financial Resilience</div>'
        '<div style="display:inline-flex;align-items:center;gap:6px;'
        f"padding:5px 14px;border-radius:100px;font-size:12px;font-weight:600;"
        f"background:{bg_badge};color:{fg_badge};"
        f'border:1px solid {fg_badge}22">'
        f'<span style="width:7px;height:7px;border-radius:50%;'
        f'background:{fg_badge};display:inline-block"></span>'
        f"{band}"
        "</div>"
        "</div>"
        # ── Vertical divider ──────────────────────────────────────────────
        '<div class="mb-hero-divider" style="height:100%;min-height:130px;'
        'background:#DDE8E3;align-self:stretch"></div>'
        # ── Right: 2×2 KPI grid ───────────────────────────────────────────
        '<div class="mb-hero-kpi-grid" style="display:grid;'
        'grid-template-columns:1fr 1fr;gap:10px;align-content:center">'
        + tiles
        + "</div>"
        "</div>"
    )


def adjust_banner_html(selected_type: str) -> str:
    """Return HTML for the score-adjustment info banner.

    Tells the user they are viewing a demo profile and how to edit inputs.
    """
    return (
        '<div style="background:#E8F2FD;border:1px solid #BAD7F5;'
        "border-left:3px solid #1D5FAE;border-radius:10px;"
        "padding:11px 16px;font-size:13px;color:#1D406B;"
        "margin-bottom:14px;display:flex;gap:10px;"
        'align-items:flex-start">'
        '<span style="flex-shrink:0;font-size:15px;line-height:1.5">ℹ️</span>'
        '<span style="line-height:1.6">'
        f"Viewing the <strong>{selected_type}</strong> demo profile — "
        "fictional data for illustration only. "
        "Tick <strong>✏️ Edit my inputs</strong> below to enter your own "
        "income, bills and savings and see your personalised score."
        "</span>"
        "</div>"
    )


# ---------------------------------------------------------------------------
# Score driver progress bars
# ---------------------------------------------------------------------------


def _safe_float(row: Any, key: str, default: float = 0.0) -> float:
    """Safely extract a float from a Series or dict-like object."""
    try:
        val = row[key]
        return float(val) if val is not None else default
    except (KeyError, TypeError, ValueError):
        return default


def _driver_color(score: float, good_thresh: float = 65.0) -> str:
    if score >= good_thresh:
        return "#00A87A"
    if score >= 35.0:
        return "#F5A623"
    return "#C0392B"


_DRIVER_META: list[tuple[str, str, str]] = [
    ("Emergency Runway", "emergency_runway_score", "🛡️"),
    ("Essential Spending", "essential_spending_score", "🏠"),
    ("Debt Service", "debt_service_score", "💳"),
    ("Monthly Surplus", "surplus_score", "📊"),
    ("Credit Dependency", "credit_dependency_score", "💰"),
]


def driver_bars_html(scored_row: Any) -> str:
    """
    Return HTML for the score-driver progress bars card.

    Reads the five sub-score columns produced by
    ``calculate_resilience_score``.
    """
    rows_html = []
    for name, key, icon in _DRIVER_META:
        score = _safe_float(scored_row, key)
        pct = max(0, min(100, round(score)))
        color = _driver_color(score)
        # 2-char hex opacity suffix: 1A ≈ 10%, 33 ≈ 20%
        pill_bg = f"{color}22"
        rows_html.append(
            f'<div style="margin-bottom:15px">'
            f'<div style="display:flex;justify-content:space-between;'
            f'align-items:center;margin-bottom:5px">'
            f'<div style="display:flex;align-items:center;gap:7px">'
            f'<span style="font-size:15px;line-height:1">{icon}</span>'
            f'<span style="font-size:12.5px;font-weight:500;'
            f'color:#3D5A4E">{name}</span>'
            f"</div>"
            f'<span style="font-size:11.5px;font-weight:700;color:{color};'
            f"background:{pill_bg};padding:2px 9px;"
            f'border-radius:20px">{score:.0f}</span>'
            f"</div>"
            f'<div style="height:8px;background:#F4F7F5;'
            f'border-radius:100px;overflow:hidden">'
            f'<div style="height:8px;border-radius:100px;'
            f"background:linear-gradient(90deg,{color}BB,{color});"
            f'width:{pct}%"></div>'
            f"</div></div>"
        )

    return (
        '<div style="background:#fff;border:1px solid #DDE8E3;'
        "border-radius:14px;padding:20px 22px;margin-bottom:16px;"
        'box-shadow:0 1px 3px rgba(0,0,0,0.05)">'
        '<div style="font-size:13.5px;font-weight:700;color:#0D2218;'
        'margin-bottom:16px;display:flex;align-items:center;gap:8px">'
        "<span>📈</span><span>Score drivers</span></div>"
        + "".join(rows_html)
        + "</div>"
    )


# ---------------------------------------------------------------------------
# Action cards
# ---------------------------------------------------------------------------

# (bg_tint, border_tint, accent_color)
_ACTION_STYLE: dict[str, tuple[str, str, str]] = {
    "urgent": ("#FFF5F5", "#FECACA", "#C53030"),
    "medium": ("#FFFBF0", "#FDE68A", "#D97706"),
    "positive": ("#F0FBF7", "#A7F3D0", "#00A87A"),
}
_ACTION_ICON: dict[str, str] = {
    "urgent": "🔴",
    "medium": "📌",
    "positive": "✅",
}


def action_cards_html(
    actions: list[str],
    style: str = "medium",
    empty_message: str = "No action prompts from the current inputs.",
) -> str:
    """Return HTML for a list of coloured action items."""
    if not actions:
        return (
            '<div style="background:#F4F7F5;border:1px dashed #DDE8E3;'
            "border-radius:10px;padding:13px 15px;font-size:13px;"
            f'color:#6B8A7F">ℹ️ {empty_message}</div>'
        )
    bg_tint, border_tint, accent = _ACTION_STYLE.get(
        style, ("#FFFBF0", "#FDE68A", "#D97706")
    )
    icon = _ACTION_ICON.get(style, "•")
    cards = []
    for action in actions:
        cards.append(
            f'<div style="background:{bg_tint};'
            f"border:1px solid {border_tint};"
            f"border-left:3px solid {accent};border-radius:10px;"
            f"padding:12px 16px;margin-bottom:7px;"
            f"display:flex;align-items:flex-start;gap:10px;"
            f"font-size:13px;color:#1A2E25;line-height:1.55;"
            f'box-shadow:0 1px 2px rgba(0,0,0,0.03)">'
            f'<span style="flex-shrink:0;font-size:15px;'
            f'margin-top:1px">{icon}</span>'
            f"<span>{action}</span></div>"
        )
    return "".join(cards)


# ---------------------------------------------------------------------------
# Support link cards
# ---------------------------------------------------------------------------


def support_link_card_html(
    name: str,
    url: str,
    use_case: str,
    reason: str = "",
) -> str:
    """Return HTML for a support-resource link card."""
    reason_html = (
        f'<div style="font-size:11px;color:#6B8A7F;margin-top:2px">'
        f"Why shown: {reason}</div>"
        if reason
        else ""
    )
    return (
        '<div style="background:#fff;border:1px solid #DDE8E3;'
        "border-radius:10px;padding:12px 15px;margin-bottom:8px;"
        'box-shadow:0 1px 2px rgba(0,0,0,0.03)">'
        '<div style="font-size:13px;font-weight:600">'
        f'<a href="{url}" target="_blank" '
        f'style="color:#00A87A;text-decoration:none">{name}</a>'
        "</div>"
        f'<div style="font-size:12.5px;color:#3D5A4E;'
        f'margin:3px 0 2px">{use_case}</div>'
        f"{reason_html}</div>"
    )


# ---------------------------------------------------------------------------
# Misc HTML helpers
# ---------------------------------------------------------------------------


def cross_alert_html(text: str) -> str:
    """Return HTML for the combined-risk purple alert card."""
    return (
        '<div style="background:#F0E8FD;border:1px solid #C4B5FD;'
        "border-left:4px solid #7C3AED;border-radius:10px;"
        "padding:12px 15px;color:#3B0764;font-size:13px;"
        'margin:0.75rem 0 1rem;line-height:1.6">'
        f"🔮 <strong>Combined risk notice:</strong> {text}</div>"
    )


def hint_html(text: str) -> str:
    """Return HTML for a green improvement-hint card with left accent."""
    return (
        '<div style="background:#E0F5EE;border:1px solid #A3E4CB;'
        "border-left:3px solid #00A87A;border-radius:10px;"
        "padding:12px 16px;font-size:13px;color:#0A6B4A;"
        "margin:6px 0 12px;display:flex;gap:10px;"
        'align-items:flex-start">'
        '<span style="flex-shrink:0;font-size:16px;line-height:1.4">💡</span>'
        f'<span style="line-height:1.6">{text}</span></div>'
    )


def explain_bullets_html(reasons: list[str]) -> str:
    """Return HTML for score-explanation bullet rows."""
    items = []
    for i, r in enumerate(reasons):
        border = "none" if i == len(reasons) - 1 else "1px solid #F4F7F5"
        items.append(
            f'<div style="display:flex;align-items:flex-start;gap:8px;'
            f"padding:7px 0;font-size:13px;color:#3D5A4E;"
            f'line-height:1.55;border-bottom:{border}">'
            f"<span>📊</span><span>{r}</span></div>"
        )
    return "".join(items)


def red_flag_items_html(red_flags: list[dict]) -> str:
    """Return HTML for scam red-flag items."""
    if not red_flags:
        return (
            '<div style="background:#F4F7F5;border:1px dashed #DDE8E3;'
            "border-radius:10px;padding:12px 15px;font-size:13px;"
            'color:#6B8A7F">'
            "✅ No major rule-based red flags were detected.</div>"
        )
    items = []
    for flag in red_flags:
        matches_str = ", ".join(str(m) for m in flag["matches"])
        items.append(
            '<div style="background:#fff;border:1px solid #DDE8E3;'
            "border-left:3px solid #9B2220;border-radius:10px;"
            "padding:10px 14px;margin-bottom:6px;"
            "display:flex;align-items:flex-start;gap:9px;"
            'font-size:13px">'
            "<span>🚩</span>"
            f"<span><strong>{flag['label']}:</strong> "
            f"{matches_str}</span></div>"
        )
    return "".join(items)


def band_comparison_html(baseline_band: str, stressed_band: str) -> str:
    """Return HTML for the baseline vs stressed band chip row."""

    def _chip(label: str, band: str) -> str:
        bg, fg = _BAND_CFG.get(band, ("#FFF3DC", "#8A5E00"))
        return (
            f'<span style="display:inline-flex;align-items:center;gap:6px;'
            f"padding:5px 14px;border-radius:100px;font-size:12px;"
            f'font-weight:600;background:{bg};color:{fg}">'
            f'<span style="font-size:10px;font-weight:700;'
            f"text-transform:uppercase;letter-spacing:.06em;"
            f'margin-right:2px;color:{fg}">{label}</span>'
            f"{band}</span>"
        )

    return (
        '<div style="display:flex;gap:10px;margin:0.75rem 0 1rem;'
        f'flex-wrap:wrap">{_chip("Baseline", baseline_band)}'
        f"{_chip('Stressed', stressed_band)}</div>"
    )


def comparison_cards_html(comparison: Any) -> str:
    """Return a before/after card pair for bill shock comparison.

    ``comparison`` is a Series/dict with keys: baseline_score,
    stressed_score, baseline_monthly_surplus, stressed_monthly_surplus,
    baseline_runway_months, stressed_runway_months.
    """
    b_score = float(comparison["baseline_score"])
    s_score = float(comparison["stressed_score"])
    delta = s_score - b_score
    delta_color = "#00A87A" if delta >= 0 else "#C0392B"
    delta_sign = "+" if delta >= 0 else ""
    delta_icon = "▲" if delta >= 0 else "▼"

    b_sur = float(comparison["baseline_monthly_surplus"])
    s_sur = float(comparison["stressed_monthly_surplus"])
    b_run = float(comparison["baseline_runway_months"])
    s_run = float(comparison["stressed_runway_months"])

    def _m(v: float) -> str:
        return f"GBP {v:,.0f}"

    base_card = (
        '<div style="background:#fff;border:1px solid #DDE8E3;'
        "border-top:3px solid #00A87A;border-radius:14px;"
        'padding:18px 20px;box-shadow:0 1px 4px rgba(0,0,0,0.05)">'
        '<div style="font-size:10px;font-weight:700;letter-spacing:0.08em;'
        'text-transform:uppercase;color:#6B8A7F;margin-bottom:8px">'
        "Before — Baseline</div>"
        f'<div style="font-size:38px;font-weight:800;letter-spacing:-0.03em;'
        f'color:#0D2218;line-height:1">{b_score:.1f}</div>'
        '<div style="font-size:11px;color:#6B8A7F;margin-bottom:12px">'
        "&nbsp;/ 100</div>"
        f'<div style="font-size:12px;color:#6B8A7F;margin-top:4px">'
        f"Surplus: <strong style='color:#0D2218'>{_m(b_sur)}</strong>"
        "</div>"
        f'<div style="font-size:12px;color:#6B8A7F;margin-top:4px">'
        f"Runway: <strong style='color:#0D2218'>{b_run:.1f}&nbsp;mo</strong>"
        "</div></div>"
    )

    arrow = (
        '<div style="display:flex;flex-direction:column;align-items:center;'
        'justify-content:center;gap:4px;padding-top:18px;min-width:52px">'
        f'<div style="font-size:24px;color:{delta_color}">{delta_icon}</div>'
        f'<div style="font-size:13px;font-weight:700;color:{delta_color}">'
        f"{delta_sign}{delta:.1f}</div>"
        '<div style="font-size:9.5px;color:#6B8A7F;text-transform:uppercase;'
        'letter-spacing:.05em">score</div>'
        "</div>"
    )

    stress_card = (
        '<div style="background:#fff;border:1px solid #DDE8E3;'
        f"border-top:3px solid {delta_color};border-radius:14px;"
        'padding:18px 20px;box-shadow:0 1px 4px rgba(0,0,0,0.05)">'
        '<div style="font-size:10px;font-weight:700;letter-spacing:0.08em;'
        f'text-transform:uppercase;color:{delta_color};margin-bottom:8px">'
        "After — Stressed</div>"
        f'<div style="font-size:38px;font-weight:800;letter-spacing:-0.03em;'
        f'color:{delta_color};line-height:1">{s_score:.1f}</div>'
        '<div style="font-size:11px;color:#6B8A7F;margin-bottom:12px">'
        "&nbsp;/ 100</div>"
        f'<div style="font-size:12px;color:#6B8A7F;margin-top:4px">'
        f"Surplus: <strong style='color:#0D2218'>{_m(s_sur)}</strong>"
        "</div>"
        f'<div style="font-size:12px;color:#6B8A7F;margin-top:4px">'
        f"Runway: <strong style='color:#0D2218'>{s_run:.1f}&nbsp;mo</strong>"
        "</div></div>"
    )

    return (
        '<div class="mb-comparison-grid" style="display:grid;'
        "grid-template-columns:1fr auto 1fr;gap:12px;"
        'align-items:start;margin-bottom:16px">'
        + base_card
        + arrow
        + stress_card
        + "</div>"
    )


# ---------------------------------------------------------------------------
# Scam risk visual card
# ---------------------------------------------------------------------------

_SCAM_CARD_CFG: dict[str, tuple[str, str, str, str]] = {
    #            bg          border      fg_main     fg_muted
    "Low": ("#E0F5EE", "#A3E4CB", "#0A6B4A", "#3D9970"),
    "Medium": ("#FFF8E1", "#FFD54F", "#7A4A00", "#AA7800"),
    "High": ("#FFF0F0", "#FECACA", "#9B2220", "#C0392B"),
    "Severe": ("#3D0000", "#7B1414", "#FF9999", "#FF6B6B"),
}


def scam_risk_card_html(scam_result: dict) -> str:
    """Return a large visual scam-risk header card."""
    score = int(scam_result.get("risk_score", 0))
    band = str(scam_result.get("risk_band", "Medium"))
    scam_type = str(scam_result.get("scam_type", "Unknown"))
    red_flags = scam_result.get("red_flags", [])
    n_flags = len(red_flags)

    bg, border, fg, fg_muted = _SCAM_CARD_CFG.get(band, _SCAM_CARD_CFG["Medium"])

    bg_style = (
        "linear-gradient(135deg,#3D0000 0%,#6B0000 100%)" if band == "Severe" else bg
    )

    if band in ("High", "Severe"):
        action_label = "⛔ Stop and verify before acting"
    elif band == "Medium":
        action_label = "⚠️ Be cautious — check before responding"
    else:
        action_label = "✓ Lower risk — but always stay alert"

    flag_word = "flag" if n_flags == 1 else "flags"

    return (
        f'<div class="mb-scam-card" style="background:{bg_style};'
        f"border:1px solid {border};"
        f"border-radius:16px;padding:20px 26px;margin-bottom:20px;"
        f"display:flex;align-items:center;gap:22px;flex-wrap:wrap;"
        f'box-shadow:0 2px 14px rgba(0,0,0,0.09)">'
        f'<div style="text-align:center;flex-shrink:0">'
        f'<div style="font-size:54px;font-weight:800;color:{fg};'
        f'line-height:1;letter-spacing:-0.03em">{score}</div>'
        f'<div style="font-size:10.5px;color:{fg_muted};font-weight:600;'
        f'margin-top:3px;text-transform:uppercase;letter-spacing:0.06em">'
        f"Risk score / 100</div>"
        f"</div>"
        f'<div class="mb-scam-divider" style="width:1px;height:66px;'
        f'background:{fg};opacity:0.18;flex-shrink:0"></div>'
        f'<div style="flex:1;min-width:150px">'
        f'<div style="font-size:20px;font-weight:700;color:{fg};'
        f'letter-spacing:-0.02em;margin-bottom:4px">{band} Risk</div>'
        f'<div style="font-size:12.5px;color:{fg_muted};margin-bottom:12px">'
        f"{scam_type}&nbsp;·&nbsp;{n_flags} red {flag_word} detected</div>"
        f'<div style="display:inline-flex;align-items:center;gap:6px;'
        f"background:{fg}22;border:1px solid {fg}44;border-radius:8px;"
        f'padding:6px 13px;font-size:12px;font-weight:600;color:{fg}">'
        f"{action_label}</div>"
        f"</div>"
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Sticky section navigation bar
# ---------------------------------------------------------------------------

_NAV_SECTIONS = [
    ("section-health", "Financial Health Check"),
    ("section-shock", "Bill Shock Simulator"),
    ("section-scam", "Scam Checker"),
    ("section-actions", "Action Plan"),
    ("section-guide", "How to Use"),
]


def nav_bar_html() -> str:
    """Return the sticky anchor-link navigation bar HTML."""
    links = "".join(
        f'<a href="#{anchor}">{label}</a>' for anchor, label in _NAV_SECTIONS
    )
    return f'<div class="mb-nav-wrap"><div class="mb-nav-bar">{links}</div></div>'


def section_anchor(anchor_id: str) -> None:
    """Inject an invisible anchor ``<div>`` for in-page navigation."""
    st.markdown(
        f'<div id="{anchor_id}" style="position:relative;top:-70px;'
        f'visibility:hidden;pointer-events:none"></div>',
        unsafe_allow_html=True,
    )


def section_divider() -> None:
    """Render a visual horizontal rule between page sections."""
    st.markdown('<hr class="mb-section-sep"/>', unsafe_allow_html=True)
