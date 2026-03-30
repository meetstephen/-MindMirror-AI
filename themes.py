import streamlit as st

THEMES = {
    "midnight_ocean": {
        "display_name": "🌊 Midnight Ocean",
        "description": "Deep navy with teal accents. Calm and focused.",
        "bg": "#0B1120",
        "bg_secondary": "#111827",
        "card_bg": "#152238",
        "text": "#E5EEF8",
        "text_secondary": "#9FB3C8",
        "accent": "#64FFDA",
        "accent_secondary": "#7BDFF2",
        "border": "#25364D",
        "positive": "#52D68A",
        "negative": "#FF7675",
        "neutral": "#A29BFE",
        "sidebar_bg": "#0A0F1C",
        "input_bg": "#132033",
    },
    "aurora": {
        "display_name": "🌌 Aurora",
        "description": "Cool neon greens and violets on a dark sky.",
        "bg": "#0A0F1F",
        "bg_secondary": "#11172A",
        "card_bg": "#182033",
        "text": "#EAF2FF",
        "text_secondary": "#A7B6CC",
        "accent": "#7AF0B8",
        "accent_secondary": "#B388FF",
        "border": "#28344D",
        "positive": "#6EE7B7",
        "negative": "#FB7185",
        "neutral": "#93C5FD",
        "sidebar_bg": "#080D19",
        "input_bg": "#162235",
    },
    "sunset": {
        "display_name": "🌅 Sunset",
        "description": "Warm coral and gold, like your emotions at golden hour.",
        "bg": "#1A1020",
        "bg_secondary": "#26152A",
        "card_bg": "#2E1C33",
        "text": "#FFF1E8",
        "text_secondary": "#D6B8A8",
        "accent": "#FFB86B",
        "accent_secondary": "#FF7AA2",
        "border": "#4B2B40",
        "positive": "#F6C177",
        "negative": "#FF6B6B",
        "neutral": "#C4B5FD",
        "sidebar_bg": "#140C18",
        "input_bg": "#2B1A2D",
    },
    "forest": {
        "display_name": "🌲 Forest",
        "description": "Grounding greens with earthy balance.",
        "bg": "#0E1512",
        "bg_secondary": "#16201C",
        "card_bg": "#1C2A25",
        "text": "#E8F3EC",
        "text_secondary": "#A6B8AD",
        "accent": "#7CCB92",
        "accent_secondary": "#C9A227",
        "border": "#304239",
        "positive": "#6FCF97",
        "negative": "#EB5757",
        "neutral": "#9CA3AF",
        "sidebar_bg": "#0B110E",
        "input_bg": "#1A2621",
    },
    "minimal_light": {
        "display_name": "☀️ Minimal Light",
        "description": "Bright, clean, and distraction-free.",
        "bg": "#F8FAFC",
        "bg_secondary": "#EEF2F7",
        "card_bg": "#FFFFFF",
        "text": "#1F2937",
        "text_secondary": "#6B7280",
        "accent": "#2563EB",
        "accent_secondary": "#7C3AED",
        "border": "#D6DEE8",
        "positive": "#16A34A",
        "negative": "#DC2626",
        "neutral": "#64748B",
        "sidebar_bg": "#F1F5F9",
        "input_bg": "#FFFFFF",
    },
    "lavender_mist": {
        "display_name": "💜 Lavender Mist",
        "description": "Soft lilac tones for gentler reflection.",
        "bg": "#F7F4FF",
        "bg_secondary": "#EFE9FF",
        "card_bg": "#FFFFFF",
        "text": "#312E45",
        "text_secondary": "#7C7A91",
        "accent": "#8B5CF6",
        "accent_secondary": "#EC4899",
        "border": "#DDD6FE",
        "positive": "#10B981",
        "negative": "#EF4444",
        "neutral": "#A78BFA",
        "sidebar_bg": "#F1ECFF",
        "input_bg": "#FFFFFF",
    },
    "deep_space": {
        "display_name": "🚀 Deep Space",
        "description": "Ultra-dark, high contrast, cosmic clarity.",
        "bg": "#05070D",
        "bg_secondary": "#0B1020",
        "card_bg": "#101728",
        "text": "#F3F7FF",
        "text_secondary": "#AAB7CC",
        "accent": "#38BDF8",
        "accent_secondary": "#A78BFA",
        "border": "#24324A",
        "positive": "#22C55E",
        "negative": "#F43F5E",
        "neutral": "#94A3B8",
        "sidebar_bg": "#03050A",
        "input_bg": "#111B2E",
    },
    "warm_earth": {
        "display_name": "🏜️ Warm Earth",
        "description": "Terracotta warmth and grounded calm.",
        "bg": "#1A1411",
        "bg_secondary": "#241C18",
        "card_bg": "#2E2520",
        "text": "#F4E8DE",
        "text_secondary": "#C5AA98",
        "accent": "#D4A373",
        "accent_secondary": "#E76F51",
        "border": "#4A3B33",
        "positive": "#90BE6D",
        "negative": "#E63946",
        "neutral": "#E9C46A",
        "sidebar_bg": "#15100D",
        "input_bg": "#2B221D",
    },
}

THEME_NAMES = list(THEMES.keys())


def get_theme(theme_name: str) -> dict:
    return THEMES.get(theme_name, THEMES["midnight_ocean"])


def get_theme_recommendation(avg_sentiment: float) -> list[str]:
    if avg_sentiment >= 0.35:
        return ["aurora", "minimal_light", "deep_space"]
    if avg_sentiment >= 0.05:
        return ["midnight_ocean", "forest", "lavender_mist"]
    if avg_sentiment >= -0.25:
        return ["warm_earth", "sunset", "forest"]
    return ["lavender_mist", "warm_earth", "midnight_ocean"]


def get_plotly_colors(theme_name: str) -> dict:
    t = get_theme(theme_name)
    return {
        "paper": t["card_bg"],
        "plot": t["card_bg"],
        "text": t["text"],
        "grid": t["border"],
        "accent": t["accent"],
        "colors": [
            t["accent"],
            t["accent_secondary"],
            t["positive"],
            t["negative"],
            t["neutral"],
            "#FFD166",
            "#06D6A0",
            "#EF476F",
        ],
    }


def get_theme_css(
    theme_name: str,
    font_size_scale: float = 1.0,
    high_contrast: bool = False,
    reduce_motion: bool = False,
) -> str:
    t = get_theme(theme_name)
    is_light = theme_name in ("minimal_light", "lavender_mist")

    if high_contrast:
        text_main = "#000000" if is_light else "#FFFFFF"
        text_secondary = "#1F2937" if is_light else "#E5E7EB"
        border = "#6B7280"
    else:
        text_main = t["text"]
        text_secondary = t["text_secondary"]
        border = t["border"]

    transition = "none" if reduce_motion else "all 0.2s ease"
    base_font = 16 * font_size_scale

    return f"""
<style>
:root {{
    --mm-bg: {t["bg"]};
    --mm-bg-secondary: {t["bg_secondary"]};
    --mm-card-bg: {t["card_bg"]};
    --mm-text: {text_main};
    --mm-text-secondary: {text_secondary};
    --mm-accent: {t["accent"]};
    --mm-accent-secondary: {t["accent_secondary"]};
    --mm-border: {border};
    --mm-positive: {t["positive"]};
    --mm-negative: {t["negative"]};
    --mm-neutral: {t["neutral"]};
    --mm-sidebar-bg: {t["sidebar_bg"]};
    --mm-input-bg: {t["input_bg"]};
    --mm-font-base: {base_font}px;
    --mm-transition: {transition};
}}

html, body, [data-testid="stAppViewContainer"] {{
    background: var(--mm-bg) !important;
    color: var(--mm-text) !important;
    font-size: var(--mm-font-base) !important;
}}

[data-testid="stSidebar"] {{
    background: var(--mm-sidebar-bg) !important;
}}

[data-testid="stSidebar"] * {{
    color: var(--mm-text) !important;
}}

.main .block-container {{
    padding-top: 2rem;
    padding-bottom: 3rem;
}}

h1, h2, h3, h4, h5, h6, p, label, div, span {{
    color: var(--mm-text);
}}

small, .stCaption, [data-testid="stCaptionContainer"] {{
    color: var(--mm-text-secondary) !important;
}}

a {{
    color: var(--mm-accent) !important;
}}

hr {{
    border-color: var(--mm-border) !important;
}}

.mm-card {{
    background: var(--mm-card-bg);
    border: 1px solid var(--mm-border);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    transition: var(--mm-transition);
}}

.mm-card:hover {{
    border-color: var(--mm-accent);
}}

.mm-emotion-tag {{
    display: inline-block;
    background: {t["accent"]}22;
    color: var(--mm-accent);
    border: 1px solid {t["accent"]}44;
    border-radius: 999px;
    padding: 2px 10px;
    margin: 2px 4px 2px 0;
    font-size: 0.85em;
}}

.mm-celebration {{
    background: {t["positive"]}18;
    border: 1px solid {t["positive"]}55;
    border-radius: 12px;
    padding: 12px 16px;
    margin: 10px 0;
}}

.mm-crisis {{
    background: {t["negative"]}12;
    border: 1px solid {t["negative"]}66;
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
}}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input,
.stTimeInput input {{
    background: var(--mm-input-bg) !important;
    color: var(--mm-text) !important;
    border: 1px solid var(--mm-border) !important;
    border-radius: 10px !important;
}}

div[data-baseweb="select"] > div {{
    background: var(--mm-input-bg) !important;
    color: var(--mm-text) !important;
    border-color: var(--mm-border) !important;
}}

div[data-baseweb="popover"] {{
    background: var(--mm-card-bg) !important;
    color: var(--mm-text) !important;
}}

.stButton > button,
.stDownloadButton > button {{
    border-radius: 10px !important;
    transition: var(--mm-transition) !important;
}}

[data-testid="stMetric"] {{
    background: var(--mm-card-bg);
    border: 1px solid var(--mm-border);
    border-radius: 12px;
    padding: 12px;
}}

[data-testid="stExpander"] {{
    background: var(--mm-card-bg) !important;
    border: 1px solid var(--mm-border) !important;
    border-radius: 12px !important;
}}

[data-testid="stTabs"] [data-baseweb="tab"] {{
    color: var(--mm-text-secondary) !important;
}}

[data-testid="stTabs"] [aria-selected="true"] {{
    color: var(--mm-accent) !important;
}}

[data-testid="stChatMessage"] {{
    background: var(--mm-card-bg) !important;
    border: 1px solid var(--mm-border) !important;
    border-radius: 12px !important;
}}

[data-testid="stDataFrame"] {{
    border: 1px solid var(--mm-border) !important;
    border-radius: 12px !important;
}}

* {{
    {"animation: none !important; transition: none !important;" if reduce_motion else ""}
}}
</style>
"""
