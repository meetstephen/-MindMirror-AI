# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — themes.py  CHUNK 4 of 10  (v3 · CORRECTED)   ║
# ║  8 Themes · get_theme_css · get_plotly_colors ·                ║
# ║  get_theme · get_theme_recommendation · THEME_NAMES            ║
# ╚══════════════════════════════════════════════════════════════════╝


# ═══════════════════════════════════════════════════════════════════
#  THEME DEFINITIONS
#
#  Keys used by app.py:
#    display_name, description, bg, bg_secondary, card_bg,
#    text, text_secondary, accent, accent_secondary, border,
#    positive, negative, neutral, sidebar_bg, input_bg
# ═══════════════════════════════════════════════════════════════════

THEMES = {

    "🌊 Deep Ocean": {
        "display_name": "🌊 Deep Ocean",
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

    "🌌 Aurora": {
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

    "🌅 Sunset": {
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

    "🌲 Forest": {
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

    "☀️ Minimal Light": {
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

    "💜 Lavender Mist": {
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

    "🚀 Deep Space": {
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

    "🏜️ Warm Earth": {
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

THEME_NAMES = list(THEMES.keys())


# ═══════════════════════════════════════════════════════════════════
#  get_theme(name) → dict
# ═══════════════════════════════════════════════════════════════════

def get_theme(name: str) -> dict:
    """Return the full theme dict. Falls back to Deep Ocean."""
    return THEMES.get(name, THEMES["🌊 Deep Ocean"])


# ═══════════════════════════════════════════════════════════════════
#  get_plotly_colors(name) → dict
#
#  Returns: { paper, text, grid, colors (list), accent }
# ═══════════════════════════════════════════════════════════════════

def get_plotly_colors(name: str) -> dict:
    """Return Plotly-friendly color config for the given theme."""
    t = get_theme(name)
    return {
        "paper":  t["card_bg"],
        "text":   t["text"],
        "grid":   t["border"],
        "accent": t["accent"],
        "colors": [
            t["accent"],
            t["accent_secondary"],
            t["positive"],
            t["negative"],
            t["neutral"],
            "#FFD93D",
            "#FF6B6B",
            "#48DBFB",
            "#FF9FF3",
            "#54A0FF",
        ],
    }


# ═══════════════════════════════════════════════════════════════════
#  get_theme_recommendation(avg_sentiment) → list of display names
# ═══════════════════════════════════════════════════════════════════

def get_theme_recommendation(avg_sentiment: float) -> list:
    """Suggest themes based on recent average mood."""
    if avg_sentiment > 0.3:
        return ["🌌 Aurora", "🚀 Deep Space", "☀️ Minimal Light"]
    elif avg_sentiment > 0.0:
        return ["🌊 Deep Ocean", "🌲 Forest", "💜 Lavender Mist"]
    elif avg_sentiment > -0.3:
        return ["🏜️ Warm Earth", "🌅 Sunset", "🌲 Forest"]
    else:
        return ["💜 Lavender Mist", "🏜️ Warm Earth", "🌅 Sunset"]


# ═══════════════════════════════════════════════════════════════════
#  get_theme_css(name, ...) → str
#
#  Returns the full CSS string (with <style> tags) for injection
#  via st.markdown(css, unsafe_allow_html=True)
# ═══════════════════════════════════════════════════════════════════

def get_theme_css(
    theme_name: str,
    font_size_scale: float = 1.0,
    high_contrast: bool = False,
    reduce_motion: bool = False,
) -> str:
    """Generate complete CSS string for the selected theme."""

    t = get_theme(theme_name)
    is_light = theme_name in ("☀️ Minimal Light", "💜 Lavender Mist")
    base_font = 16 * font_size_scale

    # High contrast overrides
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

    transition = "none" if reduce_motion else "all 0.2s ease"

    css = f"""
<style>

/* ── CSS Custom Properties ─────────────────────────────────── */
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

/* ── Global ────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {{
    background-color: var(--mm-bg) !important;
    color: var(--mm-text) !important;
    font-size: var(--mm-font-base) !important;
}}
[data-testid="stAppViewContainer"] > section > div {{
    background-color: var(--mm-bg) !important;
}}
.main .block-container {{
    max-width: 1100px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}}

/* ── Sidebar ───────────────────────────────────────────────── */
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

/* ── Headings & Text ───────────────────────────────────────── */
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

/* ── .mm-card ──────────────────────────────────────────────── */
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

/* ── .mm-emotion-tag ───────────────────────────────────────── */
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
.mm-emotion-tag.negative {{
    background: {t["negative"]}1A;
    color: {t["negative"]};
    border-color: {t["negative"]}44;
}}

/* ── .mm-celebration ───────────────────────────────────────── */
.mm-celebration {{
    background: linear-gradient(135deg, {t["positive"]}1A, {t["accent"]}1A);
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

/* ── .mm-crisis ────────────────────────────────────────────── */
.mm-crisis {{
    background: {t["negative"]}12;
    border: 2px solid {t["negative"]}66;
    border-radius: var(--mm-radius);
    padding: 20px;
    margin: 12px 0;
}}

/* ── Buttons ───────────────────────────────────────────────── */
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
[data-testid="stBaseButton-secondary"]:hover {{
    border-color: var(--mm-accent) !important;
    color: var(--mm-accent) !important;
}}

/* ── Inputs ────────────────────────────────────────────────── */
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
[data-testid="stTextArea"] textarea:focus {{
    border-color: var(--mm-accent) !important;
    box-shadow: 0 0 0 1px var(--mm-accent) !important;
}}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {{
    color: var(--mm-text-secondary) !important;
    opacity: 0.6;
}}

/* ── Selects ───────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
.stSelectbox > div > div {{
    background-color: var(--mm-input-bg) !important;
    border-color: var(--mm-border) !important;
    color: var(--mm-text) !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] {{
    background-color: var(--mm-input-bg) !important;
}}
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

/* ── Multiselect ───────────────────────────────────────────── */
[data-testid="stMultiSelect"] > div > div {{
    background-color: var(--mm-input-bg) !important;
    border-color: var(--mm-border) !important;
}}
[data-testid="stMultiSelect"] [data-baseweb="tag"] {{
    background-color: {t["accent"]}22 !important;
    border-color: {t["accent"]}44 !important;
    color: var(--mm-accent) !important;
}}

/* ── Sliders ───────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] {{
    background-color: var(--mm-accent) !important;
}}

/* ── Tabs ──────────────────────────────────────────────────── */
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
    font-weight: 600 !important;
}}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
    background-color: var(--mm-accent) !important;
}}

/* ── Expanders ─────────────────────────────────────────────── */
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

/* ── Metrics ───────────────────────────────────────────────── */
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

/* ── Progress Bars ─────────────────────────────────────────── */
[data-testid="stProgress"] > div > div {{
    background-color: var(--mm-bg-secondary) !important;
    border-radius: 6px !important;
}}
[data-testid="stProgress"] > div > div > div {{
    background: linear-gradient(90deg, var(--mm-accent), var(--mm-accent-secondary)) !important;
    border-radius: 6px !important;
}}

/* ── Chat Messages ─────────────────────────────────────────── */
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
[data-testid="stChatInput"] textarea {{
    background-color: var(--mm-input-bg) !important;
    color: var(--mm-text) !important;
}}

/* ── Download Buttons ──────────────────────────────────────── */
[data-testid="stDownloadButton"] button {{
    background-color: var(--mm-accent) !important;
    color: {t["bg"]} !important;
    border: none !important;
    border-radius: var(--mm-radius-sm) !important;
    font-weight: 600 !important;
}}

/* ── Date/Time/Number Inputs ───────────────────────────────── */
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input,
[data-testid="stNumberInput"] input {{
    background-color: var(--mm-input-bg) !important;
    color: var(--mm-text) !important;
    border-color: var(--mm-border) !important;
}}

/* ── Scrollbars ────────────────────────────────────────────── */
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

/* ── Focus Outlines ────────────────────────────────────────── */
*:focus-visible {{
    outline: 2px solid var(--mm-accent) !important;
    outline-offset: 2px !important;
}}

/* ── Responsive ────────────────────────────────────────────── */
@media (max-width: 768px) {{
    .main .block-container {{
        padding-left: 1rem;
        padding-right: 1rem;
    }}
    .mm-card {{
        padding: 14px;
    }}
    [data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap !important;
    }}
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
        min-width: 100% !important;
    }}
}}
@media (max-width: 480px) {{
    h1 {{ font-size: 1.5em !important; }}
    h2 {{ font-size: 1.3em !important; }}
    h3 {{ font-size: 1.15em !important; }}
    .mm-emotion-tag {{
        font-size: 0.75em;
        padding: 2px 8px;
    }}
}}

/* ── Print ─────────────────────────────────────────────────── */
@media print {{
    [data-testid="stSidebar"],
    [data-testid="stToolbar"],
    [data-testid="stStatusWidget"],
    .
