# ═══════════════════════════════════════════════════════════════════
#  themes.py — MindMirror AI · Theme engine & CSS generator
# ═══════════════════════════════════════════════════════════════════

from typing import List, Dict, Optional

# ───────────────────────────────────────────────────────────────────
#  Theme Definitions
# ───────────────────────────────────────────────────────────────────

THEMES: Dict[str, Dict] = {
    "🌊 Deep Ocean": {
        "display_name": "🌊 Deep Ocean",
        "description": "Calm, deep blues — focused and serene.",
        "bg": "#0B1120",
        "bg_secondary": "#111B2E",
        "card_bg": "#14203A",
        "border": "#1E3A5F",
        "text": "#E0E7FF",
        "text_secondary": "#8899BB",
        "accent": "#64FFDA",
        "accent_secondary": "#7BDFF2",
        "positive": "#52D68A",
        "negative": "#FF7675",
        "warning": "#FFD93D",
        "sidebar_bg": "#0D1526",
        "input_bg": "#162040",
    },
    "🌸 Cherry Blossom": {
        "display_name": "🌸 Cherry Blossom",
        "description": "Soft pinks and warm whites — gentle and warm.",
        "bg": "#1A1215",
        "bg_secondary": "#221A1E",
        "card_bg": "#2A1F24",
        "border": "#5C3A47",
        "text": "#FFE4EC",
        "text_secondary": "#C9929F",
        "accent": "#FF8FAB",
        "accent_secondary": "#FFB3C6",
        "positive": "#A8E6CF",
        "negative": "#FF6B6B",
        "warning": "#FFE66D",
        "sidebar_bg": "#150E12",
        "input_bg": "#2E2228",
    },
    "🌲 Forest": {
        "display_name": "🌲 Forest",
        "description": "Earthy greens and browns — grounded and natural.",
        "bg": "#0E1A0E",
        "bg_secondary": "#142014",
        "card_bg": "#1A2B1A",
        "border": "#2E5E2E",
        "text": "#D4E8D4",
        "text_secondary": "#88AA88",
        "accent": "#4CAF50",
        "accent_secondary": "#81C784",
        "positive": "#66BB6A",
        "negative": "#EF5350",
        "warning": "#FFC107",
        "sidebar_bg": "#0B140B",
        "input_bg": "#1E301E",
    },
    "🌅 Sunset": {
        "display_name": "🌅 Sunset",
        "description": "Warm oranges and magentas — vibrant and expressive.",
        "bg": "#1A100D",
        "bg_secondary": "#221610",
        "card_bg": "#2C1D16",
        "border": "#6B3A28",
        "text": "#FFE8D6",
        "text_secondary": "#C49A7E",
        "accent": "#FF6B35",
        "accent_secondary": "#FF9F1C",
        "positive": "#7DCE82",
        "negative": "#FF4757",
        "warning": "#FFBE0B",
        "sidebar_bg": "#15100A",
        "input_bg": "#30221A",
    },
    "🌙 Midnight": {
        "display_name": "🌙 Midnight",
        "description": "Deep purples and indigo — contemplative and restful.",
        "bg": "#0D0B1A",
        "bg_secondary": "#131024",
        "card_bg": "#1A1530",
        "border": "#2E2660",
        "text": "#E0DCFF",
        "text_secondary": "#9990CC",
        "accent": "#A29BFE",
        "accent_secondary": "#C4B5FD",
        "positive": "#6BCB77",
        "negative": "#FF6B6B",
        "warning": "#FFD93D",
        "sidebar_bg": "#0A0818",
        "input_bg": "#1E1838",
    },
    "☁️ Cloud": {
        "display_name": "☁️ Cloud",
        "description": "Light grays and sky blues — clean and airy.",
        "bg": "#F5F7FA",
        "bg_secondary": "#E8ECF1",
        "card_bg": "#FFFFFF",
        "border": "#D1D9E6",
        "text": "#2D3748",
        "text_secondary": "#718096",
        "accent": "#4299E1",
        "accent_secondary": "#63B3ED",
        "positive": "#48BB78",
        "negative": "#FC8181",
        "warning": "#ECC94B",
        "sidebar_bg": "#EDF2F7",
        "input_bg": "#FFFFFF",
    },
    "🔥 Ember": {
        "display_name": "🔥 Ember",
        "description": "Dark with warm amber highlights — bold and intense.",
        "bg": "#1A1210",
        "bg_secondary": "#221812",
        "card_bg": "#2A1E18",
        "border": "#5C3D2E",
        "text": "#FFE4CC",
        "text_secondary": "#C4977A",
        "accent": "#FF9800",
        "accent_secondary": "#FFB74D",
        "positive": "#66BB6A",
        "negative": "#EF5350",
        "warning": "#FFD54F",
        "sidebar_bg": "#16100C",
        "input_bg": "#30241C",
    },
    "💜 Lavender": {
        "display_name": "💜 Lavender",
        "description": "Soft purples and lilacs — soothing and creative.",
        "bg": "#14101A",
        "bg_secondary": "#1C1626",
        "card_bg": "#221C30",
        "border": "#3D3060",
        "text": "#E8E0F0",
        "text_secondary": "#A898C8",
        "accent": "#B388FF",
        "accent_secondary": "#CE93D8",
        "positive": "#69F0AE",
        "negative": "#FF8A80",
        "warning": "#FFE57F",
        "sidebar_bg": "#110D16",
        "input_bg": "#281E3A",
    },
}

THEME_NAMES: List[str] = list(THEMES.keys())


# ───────────────────────────────────────────────────────────────────
#  get_theme — returns the raw theme dict
# ───────────────────────────────────────────────────────────────────

def get_theme(name: str) -> Dict:
    return THEMES.get(name, THEMES[THEME_NAMES[0]])


# ───────────────────────────────────────────────────────────────────
#  get_plotly_colors — returns Plotly-specific color config
# ───────────────────────────────────────────────────────────────────

def get_plotly_colors(name: str) -> Dict:
    t = get_theme(name)
    return {
        "paper": t["card_bg"],
        "text": t["text"],
        "grid": t["border"],
        "accent": t["accent"],
        "colors": [
            t["accent"],
            t["accent_secondary"],
            t["positive"],
            t["negative"],
            t["warning"],
            t["text_secondary"],
            "#FF6B6B",
            "#48DBFB",
            "#FECA57",
            "#FF9FF3",
        ],
    }


# ───────────────────────────────────────────────────────────────────
#  get_theme_recommendation — suggest themes by mood
# ───────────────────────────────────────────────────────────────────

def get_theme_recommendation(avg_sentiment: float) -> Optional[List[str]]:
    if avg_sentiment > 0.3:
        return ["🌅 Sunset", "🌸 Cherry Blossom", "🔥 Ember"]
    elif avg_sentiment > 0.0:
        return ["🌊 Deep Ocean", "☁️ Cloud", "🌲 Forest"]
    elif avg_sentiment > -0.3:
        return ["💜 Lavender", "🌙 Midnight", "🌊 Deep Ocean"]
    else:
        return ["🌙 Midnight", "💜 Lavender", "🌲 Forest"]


# ───────────────────────────────────────────────────────────────────
#  get_theme_css — generates full CSS for Streamlit injection
# ───────────────────────────────────────────────────────────────────

def get_theme_css(
    name: str,
    font_size_scale: float = 1.0,
    high_contrast: bool = False,
    reduce_motion: bool = False,
) -> str:
    t = get_theme(name)

    # High-contrast overrides
    text_color = "#FFFFFF" if high_contrast else t["text"]
    text_secondary = "#CCCCCC" if high_contrast else t["text_secondary"]
    bg_color = "#000000" if (high_contrast and t["bg"][1:3] < "33") else t["bg"]

    base_font = round(16 * font_size_scale, 1)
    motion_css = ""
    if reduce_motion:
        motion_css = """
        *, *::before, *::after {
            animation-duration: 0s !important;
            animation-delay: 0s !important;
            transition-duration: 0s !important;
            transition-delay: 0s !important;
        }
        """

    css = f"""
    <style>
    /* ══════════════════════════════════════════════════════════
       MindMirror AI — Theme: {t['display_name']}
       ══════════════════════════════════════════════════════════ */

    :root {{
        --mm-bg: {bg_color};
        --mm-bg-secondary: {t['bg_secondary']};
        --mm-card-bg: {t['card_bg']};
        --mm-border: {t['border']};
        --mm-text: {text_color};
        --mm-text-secondary: {text_secondary};
        --mm-accent: {t['accent']};
        --mm-accent-secondary: {t['accent_secondary']};
        --mm-positive: {t['positive']};
        --mm-negative: {t['negative']};
        --mm-warning: {t['warning']};
    }}

    {motion_css}

    /* ── Global overrides ──────────────────────────────────── */
    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
        font-size: {base_font}px !important;
    }}

    /* ── Sidebar ───────────────────────────────────────────── */
    section[data-testid="stSidebar"] {{
        background-color: {t['sidebar_bg']} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {text_color} !important;
    }}

    /* ── Headers ───────────────────────────────────────────── */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: {text_color} !important;
    }}

    /* ── Text ──────────────────────────────────────────────── */
    p, span, label, .stMarkdown {{
        color: {text_color} !important;
    }}

    /* ── Inputs ────────────────────────────────────────────── */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select,
    .stNumberInput input {{
        background-color: {t['input_bg']} !important;
        color: {text_color} !important;
        border: 1px solid {t['border']} !important;
        border-radius: 8px !important;
    }}
    .stTextInput input:focus,
    .stTextArea textarea:focus {{
        border-color: {t['accent']} !important;
        box-shadow: 0 0 0 2px {t['accent']}33 !important;
    }}

    /* ── Buttons ────────────────────────────────────────────── */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {{
        background-color: {t['accent']} !important;
        color: {bg_color} !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {{
        opacity: 0.85 !important;
    }}
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"] {{
        background-color: {t['bg_secondary']} !important;
        color: {text_color} !important;
        border: 1px solid {t['border']} !important;
        border-radius: 8px !important;
    }}

    /* ── Tabs ──────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {t['bg_secondary']} !important;
        color: {text_secondary} !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 16px !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {t['card_bg']} !important;
        color: {t['accent']} !important;
        border-bottom: 2px solid {t['accent']} !important;
    }}

    /* ── Expanders ─────────────────────────────────────────── */
    .streamlit-expanderHeader {{
        background-color: {t['bg_secondary']} !important;
        color: {text_color} !important;
        border-radius: 8px !important;
        border: 1px solid {t['border']} !important;
    }}
    .streamlit-expanderContent {{
        background-color: {t['card_bg']} !important;
        border: 1px solid {t['border']} !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }}

    /* ── Metrics ────────────────────────────────────────────── */
    [data-testid="stMetric"] {{
        background-color: {t['card_bg']} !important;
        border: 1px solid {t['border']} !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {text_secondary} !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {t['accent']} !important;
    }}

    /* ── Progress bars ─────────────────────────────────────── */
    .stProgress > div > div {{
        background-color: {t['accent']} !important;
    }}
    .stProgress {{
        background-color: {t['bg_secondary']} !important;
    }}

    /* ── Alerts ─────────────────────────────────────────────── */
    .stAlert {{
        border-radius: 8px !important;
    }}

    /* ── Sliders ────────────────────────────────────────────── */
    .stSlider [data-baseweb="slider"] div {{
        color: {text_color} !important;
    }}

    /* ── Chat messages ─────────────────────────────────────── */
    [data-testid="stChatMessage"] {{
        background-color: {t['card_bg']} !important;
        border: 1px solid {t['border']} !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
    }}

    /* ── Dataframes ────────────────────────────────────────── */
    .stDataFrame {{
        border: 1px solid {t['border']} !important;
        border-radius: 8px !important;
    }}

    /* ══════════════════════════════════════════════════════════
       Custom MindMirror Components
       ══════════════════════════════════════════════════════════ */

    .mm-card {{
        background: {t['card_bg']};
        border: 1px solid {t['border']};
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        color: {text_color};
    }}
    .mm-card h4 {{
        color: {t['accent']} !important;
        margin-top: 0;
    }}
    .mm-card p {{
        color: {text_color};
        line-height: 1.6;
    }}

    .mm-celebration {{
        background: linear-gradient(135deg, {t['card_bg']}, {t['bg_secondary']});
        border: 1px solid {t['accent']}55;
        border-left: 4px solid {t['accent']};
        border-radius: 12px;
        padding: 16px 20px;
        margin: 12px 0;
        color: {text_color};
        font-size: 0.95em;
    }}

    .mm-crisis {{
        background: {t['card_bg']};
        border: 2px solid {t['negative']};
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
    }}

    .mm-emotion-tag {{
        display: inline-block;
        background: {t['accent']}22;
        color: {t['accent']};
        border: 1px solid {t['accent']}44;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 2px 4px;
        font-size: 0.82em;
        font-weight: 500;
    }}

    .mm-emotion-tag.negative {{
        background: {t['negative']}22;
        color: {t['negative']};
        border-color: {t['negative']}44;
    }}

    /* ── Scrollbar ─────────────────────────────────────────── */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: {t['bg_secondary']};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {t['border']};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {t['accent']}88;
    }}

    /* ── Selection ─────────────────────────────────────────── */
    ::selection {{
        background: {t['accent']}44;
        color: {text_color};
    }}

    /* ── Reduced-motion media query ────────────────────────── */
    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            animation-duration: 0s !important;
            transition-duration: 0s !important;
        }}
    }}

    </style>
    """
    return css
