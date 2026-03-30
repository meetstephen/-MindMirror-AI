# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — themes.py  CHUNK 4 of 10  (v3 · Full)        ║
# ║  8 Complete Themes · WCAG AA · Adaptive Tinting ·             ║
# ║  CSS Custom Properties · Streamlit Overrides ·                ║
# ║  High Contrast · Reduced Motion · Print Styles ·              ║
# ║  Font Scaling · Responsive · Component Classes                ║
# ╚══════════════════════════════════════════════════════════════════╝

import streamlit as st

# ═══════════════════════════════════════════════════════════════════
#  THEME DEFINITIONS  (8 themes)
#
#  Every theme must have ALL of these keys:
#    display_name, description, bg, bg_secondary, card_bg,
#    text, text_secondary, accent, accent_secondary, border,
#    positive, negative, neutral, sidebar_bg, input_bg
# ═══════════════════════════════════════════════════════════════════

THEMES = {

    # ── 1. Midnight Ocean (default) ──────────────────────────────
    "midnight_ocean": {
        "display_name": "🌊 Midnight Ocean",
        "description": "Deep navy tones with teal accents. Calm and focused.",
        "bg":               "#0B1120",
        "bg_secondary":     "#111B2E",
        "card_bg":          "#131D30",
        "text":             "#E2E8F0",
        "text_secondary":   "#94A3B8",
        "accent":           "#64FFDA",
        "accent_secondary": "#7BDFF2",
        "border":           "#1E3048",
        "positive":         "#52D68A",
        "negative":         "#FF7675",
        "neutral":          "#A29BFE",
        "sidebar_bg":       "#0D1526",
        "input_bg":         "#162032",
    },

    # ── 2. Aurora ────────────────────────────────────────────────
    "aurora": {
        "display_name": "🌌 Aurora",
        "description": "Dark purple canvas with shifting green-cyan glow.",
        "bg":               "#0F0A1A",
        "bg_secondary":     "#150F24",
        "card_bg":          "#1A1230",
        "text":             "#E8E0F0",
        "text_secondary":   "#A89BBF",
        "accent":           "#00E5A0",
        "accent_secondary": "#B388FF",
        "border":           "#2A1F45",
        "positive":         "#69F0AE",
        "negative":         "#FF5252",
        "neutral":          "#82B1FF",
        "sidebar_bg":       "#110C1E",
        "input_bg":         "#1E1535",
    },

    # ── 3. Sunset ────────────────────────────────────────────────
    "sunset": {
        "display_name": "🌅 Sunset",
        "description": "Warm amber and rose tones on a dark canvas.",
        "bg":               "#1A110B",
        "bg_secondary":     "#241810",
        "card_bg":          "#2A1D14",
        "text":             "#F0E6DC",
        "text_secondary":   "#BFA68E",
        "accent":           "#FFB74D",
        "accent_secondary": "#FF8A80",
        "border":           "#3D2A1A",
        "positive":         "#AED581",
        "negative":         "#EF5350",
        "neutral":          "#FFCC80",
        "sidebar_bg":       "#1C130D",
        "input_bg":         "#2E2016",
    },

    # ── 4. Forest ────────────────────────────────────────────────
    "forest": {
        "display_name": "🌲 Forest",
        "description": "Deep woodland greens with gold accents.",
        "bg":               "#0A1510",
        "bg_secondary":     "#0F1E16",
        "card_bg":          "#12241A",
        "text":             "#D8EDE0",
        "text_secondary":   "#8CB89A",
        "accent":           "#81C784",
        "accent_secondary": "#FFD54F",
        "border":           "#1C3527",
        "positive":         "#A5D6A7",
        "negative":         "#EF9A9A",
        "neutral":          "#80CBC4",
        "sidebar_bg":       "#0C1812",
        "input_bg":         "#162B1E",
    },

    # ── 5. Minimal Light ─────────────────────────────────────────
    "minimal_light": {
        "display_name": "☀️ Minimal Light",
        "description": "Clean white canvas with crisp blue accents.",
        "bg":               "#FAFBFC",
        "bg_secondary":     "#F0F2F5",
        "card_bg":          "#FFFFFF",
        "text":             "#1A202C",
        "text_secondary":   "#4A5568",
        "accent":           "#3182CE",
        "accent_secondary": "#805AD5",
        "border":           "#E2E8F0",
        "positive":         "#38A169",
        "negative":         "#E53E3E",
        "neutral":          "#718096",
        "sidebar_bg":       "#F7F8FA",
        "input_bg":         "#EDF2F7",
    },

    # ── 6. Lavender Mist ─────────────────────────────────────────
    "lavender_mist": {
        "display_name": "💜 Lavender Mist",
        "description": "Soft lilac light theme. Gentle and soothing.",
        "bg":               "#F8F5FF",
        "bg_secondary":     "#EDE8F5",
        "card_bg":          "#FFFFFF",
        "text":             "#2D2040",
        "text_secondary":   "#6B5B7B",
        "accent":           "#7C3AED",
        "accent_secondary": "#EC4899",
        "border":           "#DDD6FE",
        "positive":         "#10B981",
        "negative":         "#EF4444",
        "neutral":          "#8B5CF6",
        "sidebar_bg":       "#F3EEFA",
        "input_bg":         "#EDE9F8",
    },

    # ── 7. Deep Space ────────────────────────────────────────────
    "deep_space": {
        "display_name": "🚀 Deep Space",
        "description": "Pure black with electric blue. Maximum contrast.",
        "bg":               "#000000",
        "bg_secondary":     "#0A0A0A",
        "card_bg":          "#0F0F0F",
        "text":             "#F0F0F0",
        "text_secondary":   "#888888",
        "accent":           "#00B4D8",
        "accent_secondary": "#E040FB",
        "border":           "#222222",
        "positive":         "#00E676",
        "negative":         "#FF1744",
        "neutral":          "#448AFF",
        "sidebar_bg":       "#050505",
        "input_bg":         "#141414",
    },

    # ── 8. Warm Earth ────────────────────────────────────────────
    "warm_earth": {
        "display_name": "🏜️ Warm Earth",
        "description": "Sandy browns and terracotta. Grounded and calm.",
        "bg":               "#1C1612",
        "bg_secondary":     "#261E18",
        "card_bg":          "#2E241C",
        "text":             "#F0E4D8",
        "text_secondary":   "#B8A08A",
        "accent":           "#D4A574",
        "accent_secondary": "#E07A5F",
        "border":           "#3C3028",
        "positive":         "#A7C957",
        "negative":         "#E76F51",
        "neutral":          "#E9C46A",
        "sidebar_bg":       "#1E1814",
        "input_bg":         "#322820",
    },
}

# Ordered list for UI selectors
THEME_NAMES = [
    "midnight_ocean",
    "aurora",
    "sunset",
    "forest",
    "minimal_light",
    "lavender_mist",
    "deep_space",
    "warm_earth",
]


# ═══════════════════════════════════════════════════════════════════
#  PUBLIC API
# ═══════════════════════════════════════════════════════════════════

def get_theme(name: str) -> dict:
    """Return the full theme dict. Falls back to midnight_ocean."""
    return THEMES.get(name, THEMES["midnight_ocean"])


def get_theme_recommendation(avg_sentiment: float) -> list:
    """Suggest themes based on recent average mood.

    Returns a list of theme display_name strings (best first).
    """
    if avg_sentiment > 0.3:
        # Thriving — energetic or expansive themes
        keys = ["aurora", "deep_space", "minimal_light"]
    elif avg_sentiment > 0.0:
        # Mildly positive — balanced, warm themes
        keys = ["midnight_ocean", "forest", "lavender_mist"]
    elif avg_sentiment > -0.3:
        # Mildly low — warm, grounding themes
        keys = ["warm_earth", "sunset", "forest"]
    else:
        # Distressed — gentle, soothing themes
        keys = ["lavender_mist", "warm_earth", "sunset"]

    return [THEMES[k]["display_name"] for k in keys if k in THEMES]


def get_adaptive_tint(avg_sentiment: float) -> str:
    """Return a subtle RGBA border tint based on mood.

    Used when adaptive_theme_enabled is True.
    The returned color is applied to card borders at low opacity.
    """
    if avg_sentiment > 0.3:
        # Thriving — soft green glow
        return "rgba(82, 214, 138, 0.25)"
    elif avg_sentiment > 0.0:
        # Mildly positive — teal
        return "rgba(100, 255, 218, 0.15)"
    elif avg_sentiment > -0.3:
        # Mildly low — warm amber
        return "rgba(255, 183, 77, 0.20)"
    else:
        # Distressed — soft purple (calming, not alarming)
        return "rgba(162, 155, 254, 0.25)"


# ═══════════════════════════════════════════════════════════════════
#  CSS GENERATION & INJECTION
# ═══════════════════════════════════════════════════════════════════

def apply_theme(
    theme_name: str,
    font_size_scale: float = 1.0,
    high_contrast: bool = False,
    reduce_motion: bool = False,
):
    """Generate and inject the full CSS for the selected theme.

    Covers:
      - CSS custom properties (--mm-* variables)
      - Body, sidebar, main area backgrounds
      - .mm-card, .mm-emotion-tag, .mm-celebration, .mm-crisis-banner
      - Streamlit component overrides (buttons, inputs, sliders,
        expanders, tabs, metrics, dataframes, chat, etc.)
      - Scrollbar styling
      - Font size scaling
      - High contrast mode
      - Reduced motion mode
      - Print stylesheet
      - Responsive breakpoints
    """

    t = get_theme(theme_name)

    # Detect light vs dark for template-level decisions
    is_light = theme_name in ("minimal_light", "lavender_mist")

    # ── Font scale ───────────────────────────────────────────────
    base_font = 16 * font_size_scale

    # ── High contrast overrides ──────────────────────────────────
    if high_contrast:
        if is_light:
            text_main = "#000000"
            text_sec = "#1A1A1A"
            border_c = "#999999"
        else:
            text_main = "#FFFFFF"
            text_sec = "#DDDDDD"
            border_c = "#666666"
    else:
        text_main = t["text"]
        text_sec = t["text_secondary"]
        border_c = t["border"]

    # ── Transition value ─────────────────────────────────────────
    transition = "none" if reduce_motion else "all 0.2s ease"

    # ── Build CSS ────────────────────────────────────────────────
    css = f"""
<style>

/* ═══════════════════════════════════════════════════════════════
   CSS CUSTOM PROPERTIES
   Referenced throughout app.py with var(--mm-*)
   ═══════════════════════════════════════════════════════════════ */

:root {{
    --mm-bg:              {t["bg"]};
    --mm-bg-secondary:    {t["bg_secondary"]};
    --mm-card-bg:         {t["card_bg"]};
    --mm-text:            {text_main};
    --mm-text-secondary:  {text_sec};
    --mm-accent:          {t["accent"]};
    --mm-accent-secondary:{t["accent_secondary"]};
    --mm-border:          {border_c};
    --mm-positive:        {t["positive"]};
    --mm-negative:        {t["negative"]};
    --mm-neutral:         {t["neutral"]};
    --mm-sidebar-bg:      {t["sidebar_bg"]};
    --mm-input-bg:        {t["input_bg"]};
    --mm-transition:      {transition};
    --mm-font-base:       {base_font}px;
    --mm-radius:          12px;
    --mm-radius-sm:       8px;
}}


/* ═══════════════════════════════════════════════════════════════
   GLOBAL / BODY
   ═══════════════════════════════════════════════════════════════ */

html, body, [data-testid="stAppViewContainer"] {{
    background-color: var(--mm-bg) !important;
    color: var(--mm-text) !important;
    font-size: var(--mm-font-base) !important;
}}

[data-testid="stAppViewContainer"] > section > div {{
    background-color: var(--mm-bg) !important;
}}

/* Main content area */
.main .block-container {{
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}}


/* ═══════════════════════════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════════════════════════ */

[data-testid="stSidebar"] {{
    background-color: var(--mm-sidebar-bg) !important;
    border-right: 1px solid var(--mm-border) !important;
}}

[data-testid="stSidebar"] * {{
    color: var(--mm-text) !important;
}}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li {{
    color: var(--mm-text-secondary) !important;
}}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] .stMarkdown h4 {{
    color: var(--mm-text) !important;
}}

[data-testid="stSidebar"] hr {{
    border-color: var(--mm-border) !important;
}}


/* ═══════════════════════════════════════════════════════════════
   HEADINGS & TEXT
   ═══════════════════════════════════════════════════════════════ */

h1, h2, h3, h4, h5, h6 {{
    color: var(--mm-text) !important;
}}

p, li, span, label, div {{
    color: var(--mm-text);
}}

a {{
    color: var(--mm-accent) !important;
}}

a:hover {{
    color: var(--mm-accent-secondary) !important;
}}

hr {{
    border-color: var(--mm-border) !important;
}}

small, .stCaption, [data-testid="stCaptionContainer"] {{
    color: var(--mm-text-secondary) !important;
}}

code {{
    background-color: var(--mm-bg-secondary) !important;
    color: var(--mm-accent) !important;
    border: 1px solid var(--mm-border) !important;
    border-radius: 4px;
    padding: 2px 6px;
}}


/* ═══════════════════════════════════════════════════════════════
   CUSTOM COMPONENT CLASSES
   Used in app.py via st.markdown(unsafe_allow_html=True)
   ═══════════════════════════════════════════════════════════════ */

/* ── Cards ────────────────────────────────────────────────────── */
.mm-card {{
    background: var(--mm-card-bg);
    border: 1px solid var(--mm-border);
    border-radius: var(--mm-radius);
    padding: 20px;
    margin-bottom: 16px;
    transition: var(--mm-transition);
}}

.mm-card:hover {{
    border-color: var(--mm-accent);
    box-shadow: 0 0 12px {t["accent"]}18;
}}

.mm-card h4 {{
    margin-top: 0;
    margin-bottom: 8px;
    color: var(--mm-accent) !important;
}}

.mm-card p {{
    margin-bottom: 8px;
    color: var(--mm-text-secondary) !important;
    line-height: 1.6;
}}

/* ── Emotion Tags ─────────────────────────────────────────────── */
.mm-emotion-tag {{
    display: inline-block;
    background: {t["accent"]}1A;
    color: var(--mm-accent);
    border: 1px solid {t["accent"]}44;
    border-radius: 20px;
    padding: 3px 12px;
    margin: 2px 4px 2px 0;
    font-size: 0.82em;
    font-weight: 500;
    transition: var(--mm-transition);
}}

.mm-emotion-tag:hover {{
    background: {t["accent"]}33;
    border-color: {t["accent"]}88;
}}

/* ── Celebration Banner ───────────────────────────────────────── */
.mm-celebration {{
    background: linear-gradient(
        135deg,
        {t["positive"]}1A,
        {t["accent"]}1A
    );
    border: 1px solid {t["positive"]}44;
    border-radius: var(--mm-radius);
    padding: 14px 20px;
    margin: 12px 0;
    text-align: center;
    font-weight: 600;
    color: var(--mm-text) !important;
    animation: {"none" if reduce_motion else "mm-glow 2s ease-in-out infinite alternate"};
}}

@keyframes mm-glow {{
    from {{ box-shadow: 0 0 4px {t["positive"]}22; }}
    to   {{ box-shadow: 0 0 16px {t["positive"]}44; }}
}}

/* ── Crisis Banner ────────────────────────────────────────────── */
.mm-crisis-banner {{
    background: {t["negative"]}12;
    border: 2px solid {t["negative"]}66;
    border-radius: var(--mm-radius);
    padding: 20px;
    margin: 12px 0;
}}

.mm-crisis-banner h4 {{
    color: {t["negative"]} !important;
    margin-top: 0;
}}

.mm-crisis-banner p,
.mm-crisis-banner a {{
    line-height: 1.7;
}}

.mm-crisis-banner a {{
    color: {t["accent"]} !important;
    font-weight: 600;
}}


/* ═══════════════════════════════════════════════════════════════
   STREAMLIT COMPONENT OVERRIDES
   ═══════════════════════════════════════════════════════════════ */

/* ── Buttons ──────────────────────────────────────────────────── */
button[kind="primary"],
.stButton > button[kind="primary"],
[data-testid="stBaseButton-primary"] {{
    background-color: var(--mm-accent) !important;
    color: {t["bg"]} !important;
    border: none !important;
    border-radius: var(--mm-radius-sm) !important;
    font-weight: 600 !important;
    transition: var(--mm-transition) !important;
}}

button[kind="primary"]:hover,
.stButton > button[kind="primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {{
    opacity: 0.85 !important;
    box-shadow: 0 0 16px {t["accent"]}44 !important;
}}

button[kind="secondary"],
.stButton > button[kind="secondary"],
[data-testid="stBaseButton-secondary"] {{
    background-color: var(--mm-bg-secondary) !important;
    color: var(--mm-text) !important;
    border: 1px solid var(--mm-border) !important;
    border-radius: var(--mm-radius-sm) !important;
    transition: var(--mm-transition) !important;
}}

button[kind="secondary"]:hover,
.stButton > button[kind="secondary"]:hover,
[data-testid="stBaseButton-secondary"]:hover {{
    border-color: var(--mm-accent) !important;
    color: var(--mm-accent) !important;
}}

/* ── Text Inputs & Text Areas ─────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
.stTextInput input,
.stTextArea textarea {{
    background-color: var(--mm-input-bg) !important;
    color: var(--mm-text) !important;
    border: 1px solid var(--mm-border) !important;
    border-radius: var(--mm-radius-sm) !important;
    transition: var(--mm-transition) !important;
}}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
.stTextInput input:focus,
.stTextArea textarea:focus {{
    border-color: var(--mm-accent) !important;
    box-shadow: 0 0 0 1px var(--mm-accent) !important;
}}

[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {{
    color: var(--mm-text-secondary) !important;
    opacity: 0.6;
}}

/* ── Select Boxes ─────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
.stSelectbox > div > div {{
    background-color: var(--mm-input-bg) !important;
    border-color: var(--mm-border) !important;
    color: var(--mm-text) !important;
}}

[data-testid="stSelectbox"] [data-baseweb="select"] {{
    background-color: var(--mm-input-bg) !important;
}}

/* Dropdown menu */
[data-baseweb="popover"] {{
    background-color: var(--mm-card-bg) !important;
    border: 1px solid var(--mm-border) !important;
}}

[data-baseweb="popover"] li {{
    color: var(--mm-text) !important;
}}

[data-baseweb="popover"] li:hover {{
    background-color: var(--mm-bg-secondary) !important;
}}

/* ── Multiselect ──────────────────────────────────────────────── */
[data-testid="stMultiSelect"] > div > div {{
    background-color: var(--mm-input-bg) !important;
    border-color: var(--mm-border) !important;
}}

[data-testid="stMultiSelect"] [data-baseweb="tag"] {{
    background-color: {t["accent"]}22 !important;
    border-color: {t["accent"]}44 !important;
    color: var(--mm-accent) !important;
}}

/* ── Sliders ──────────────────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] div {{
    color: var(--mm-text) !important;
}}

[data-testid="stSlider"] [role="slider"] {{
    background-color: var(--mm-accent) !important;
}}

/* Slider track */
[data-testid="stSlider"] > div > div > div > div {{
    background: linear-gradient(
        to right,
        var(--mm-accent),
        var(--mm-accent-secondary)
    ) !important;
}}

/* ── Radio & Checkbox ─────────────────────────────────────────── */
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label {{
    color: var(--mm-text) !important;
}}

[data-testid="stRadio"] label:hover,
[data-testid="stCheckbox"] label:hover {{
    color: var(--mm-accent) !important;
}}

/* ── Tabs ──────────────────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    background-color: transparent !important;
    gap: 4px;
}}

[data-testid="stTabs"] [data-baseweb="tab"] {{
    background-color: var(--mm-bg-secondary) !important;
    color: var(--mm-text-secondary) !important;
    border-radius: var(--mm-radius-sm) var(--mm-radius-sm) 0 0 !important;
    border: 1px solid var(--mm-border) !important;
    border-bottom: none !important;
    transition: var(--mm-transition) !important;
    padding: 8px 16px !important;
}}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {{
    color: var(--mm-text) !important;
    background-color: var(--mm-card-bg) !important;
}}

[data-testid="stTabs"] [aria-selected="true"] {{
    background-color: var(--mm-card-bg) !important;
    color: var(--mm-accent) !important;
    border-color: var(--mm-accent) !important;
    border-bottom: 2px solid var(--mm-card-bg) !important;
    font-weight: 600 !important;
}}

[data-testid="stTabs"] [data-baseweb="tab-panel"] {{
    background-color: transparent !important;
    padding-top: 16px;
}}

/* Tab bottom highlight strip */
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
    background-color: var(--mm-accent) !important;
}}

/* ── Expanders ────────────────────────────────────────────────── */
[data-testid="stExpander"] {{
    background-color: var(--mm-card-bg) !important;
    border: 1px solid var(--mm-border) !important;
    border-radius: var(--mm-radius) !important;
    margin-bottom: 8px;
}}

[data-testid="stExpander"] summary {{
    color: var(--mm-text) !important;
}}

[data-testid="stExpander"] summary:hover {{
    color: var(--mm-accent) !important;
}}

[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
    border-top: 1px solid var(--mm-border) !important;
}}

/* ── Metrics ──────────────────────────────────────────────────── */
[data-testid="stMetric"] {{
    background-color: var(--mm-card-bg);
    border: 1px solid var(--mm-border);
    border-radius: var(--mm-radius);
    padding: 12px 16px;
}}

[data-testid="stMetric"] label {{
    color: var(--mm-text-secondary) !important;
}}

[data-testid="stMetric"] [data-testid="stMetricValue"] {{
    color: var(--mm-text) !important;
    font-weight: 700;
}}

[data-testid="stMetric"] [data-testid="stMetricDelta"] svg {{
    display: none;
}}

/* ── Progress Bars ────────────────────────────────────────────── */
[data-testid="stProgress"] > div > div {{
    background-color: var(--mm-bg-secondary) !important;
    border-radius: 6px !important;
}}

[data-testid="stProgress"] > div > div > div {{
    background: linear-gradient(
        90deg,
        var(--mm-accent),
        var(--mm-accent-secondary)
    ) !important;
    border-radius: 6px !important;
}}

/* ── Alerts (info, warning, error, success) ───────────────────── */
[data-testid="stAlert"] {{
    border-radius: var(--mm-radius-sm) !important;
}}

/* ── Dataframes ───────────────────────────────────────────────── */
[data-testid="stDataFrame"],
.stDataFrame {{
    border: 1px solid var(--mm-border) !important;
    border-radius: var(--mm-radius-sm) !important;
}}

/* ── Chat Messages ────────────────────────────────────────────── */
[data-testid="stChatMessage"] {{
    background-color: var(--mm-card-bg) !important;
    border: 1px solid var(--mm-border) !important;
    border-radius: var(--mm-radius) !important;
    margin-bottom: 8px;
    padding: 12px 16px;
}}

[data-testid="stChatMessage"] p {{
    color: var(--mm-text) !important;
}}

/* Chat input */
[data-testid="stChatInput"] {{
    border-color: var(--mm-border) !important;
}}

[data-testid="stChatInput"] textarea {{
    background-color: var(--mm-input-bg) !important;
    color: var(--mm-text) !important;
}}

/* ── Download Buttons ─────────────────────────────────────────── */
[data-testid="stDownloadButton"] button {{
    background-color: var(--mm-accent) !important;
    color: {t["bg"]} !important;
    border: none !important;
    border-radius: var(--mm-radius-sm) !important;
    font-weight: 600 !important;
}}

/* ── Date / Time Inputs ───────────────────────────────────────── */
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input {{
    background-color: var(--mm-input-bg) !important;
    color: var(--mm-text) !important;
    border-color: var(--mm-border) !important;
}}

/* ── Number Input ─────────────────────────────────────────────── */
[data-testid="stNumberInput"] input {{
    background-color: var(--mm-input-bg) !important;
    color: var(--mm-text) !important;
    border-color: var(--mm-border) !important;
}}

/* ── Plotly Charts (transparent wrapper) ──────────────────────── */
.js-plotly-plot .plotly {{
    border-radius: var(--mm-radius) !important;
}}


/* ═══════════════════════════════════════════════════════════════
   SCROLLBARS
   ═══════════════════════════════════════════════════════════════ */

::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: var(--mm-bg-secondary);
}}

::-webkit-scrollbar-thumb {{
    background: var(--mm-border);
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: var(--mm-accent);
}}


/* ═══════════════════════════════════════════════════════════════
   TOOLTIPS & POPOVERS
   ═══════════════════════════════════════════════════════════════ */

[data-baseweb="tooltip"] {{
    background-color: var(--mm-card-bg) !important;
    color: var(--mm-text) !important;
    border: 1px solid var(--mm-border) !important;
    border-radius: var(--mm-radius-sm) !important;
}}


/* ═══════════════════════════════════════════════════════════════
   FOCUS OUTLINES (Accessibility)
   ═══════════════════════════════════════════════════════════════ */

*:focus-visible {{
    outline: 2px solid var(--mm-accent) !important;
    outline-offset: 2px !important;
}}


/* ═══════════════════════════════════════════════════════════════
   RESPONSIVE BREAKPOINTS
   ═══════════════════════════════════════════════════════════════ */

@media (max-width: 768px) {{
    .main .block-container {{
        padding-left: 1rem;
        padding-right: 1rem;
    }}

    .mm-card {{
        padding: 14px;
    }}

    [data-testid="stMetric"] {{
        padding: 8px 10px;
    }}

    /* Stack columns on mobile */
    [data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap !important;
    }}

    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
        min-width: 100% !important;
    }}
}}

@media (max-width: 480px) {{
    h1 {{
        font-size: 1.5em !important;
    }}
    h2 {{
        font-size: 1.3em !important;
    }}
    h3 {{
        font-size: 1.15em !important;
    }}

    .mm-emotion-tag {{
        font-size: 0.75em;
        padding: 2px 8px;
    }}
}}


/* ═══════════════════════════════════════════════════════════════
   PRINT STYLES
   ═══════════════════════════════════════════════════════════════ */

@media print {{
    [data-testid="stSidebar"],
    [data-testid="stToolbar"],
    [data-testid="stStatusWidget"],
    .stButton,
    .stDownloadButton,
    [data-testid="stChatInput"] {{
        display: none !important;
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        background: white !important;
        color: black !important;
    }}

    .mm-card {{
        background: white !important;
        border: 1px solid #ccc !important;
        box-shadow: none !important;
        break-inside: avoid;
    }}

    .mm-celebration {{
        background: #f0f0f0 !important;
        border: 1px solid #ccc !important;
        animation: none !important;
    }}

    .mm-crisis-banner {{
        border: 2px solid #cc0000 !important;
        background: #fff0f0 !important;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: black !important;
    }}

    a {{
        color: #0066cc !important;
    }}

    /* Show link URLs in print */
    a[href]::after {{
        content: " (" attr(href) ")";
        font-size: 0.8em;
        color: #666;
    }}
}}

"""

    # ── High Contrast additions ──────────────────────────────────
    if high_contrast:
        css += f"""

/* ═══════════════════════════════════════════════════════════════
   HIGH CONTRAST OVERRIDES
   ═══════════════════════════════════════════════════════════════ */

.mm-card {{
    border-width: 2px !important;
}}

.mm-emotion-tag {{
    border-width: 2px !important;
    font-weight: 700 !important;
}}

[data-testid="stExpander"] {{
    border-width: 2px !important;
}}

[data-testid="stMetric"] {{
    border-width: 2px !important;
}}

button[kind="primary"],
[data-testid="stBaseButton-primary"] {{
    font-weight: 800 !important;
    letter-spacing: 0.02em;
}}

button[kind="secondary"],
[data-testid="stBaseButton-secondary"] {{
    border-width: 2px !important;
    font-weight: 700 !important;
}}

/* Force maximum contrast on text */
p, li, span, div, label {{
    color: {text_main} !important;
}}

small, .stCaption, [data-testid="stCaptionContainer"] {{
    color: {text_sec} !important;
    font-weight: 500 !important;
}}

"""

    # ── Reduced Motion additions ─────────────────────────────────
    if reduce_motion:
        css += """

/* ═══════════════════════════════════════════════════════════════
   REDUCED MOTION
   ═══════════════════════════════════════════════════════════════ */

*, *::before, *::after {
    animation-duration: 0s !important;
    animation-delay: 0s !important;
    transition-duration: 0s !important;
    transition-delay: 0s !important;
}

.mm-celebration {
    animation: none !important;
    box-shadow: none !important;
}

"""

    css += "\n</style>"

    # ── Inject ───────────────────────────────────────────────────
    st.markdown(css, unsafe_allow_html=True)
