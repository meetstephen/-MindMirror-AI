# themes.py — MindMirror AI Theme Engine

THEME_NAMES = [
    "🌊 Deep Ocean",
    "🌸 Sakura",
    "🌲 Forest",
    "🔮 Cosmic Purple",
    "☀️ Sunrise",
    "🖤 Midnight",
    "🤍 Clean Light",
]

_THEME_PARAMS = {
    "🌊 Deep Ocean": {
        "bg": "#0a1628", "sidebar": "#0d1b2a", "card": "#162038",
        "text": "#c8d6e5", "accent": "#00d4ff", "accent2": "#0091d5",
        "border": "rgba(0,212,255,0.15)", "input_bg": "#1a2744",
        "shadow": "rgba(0,212,255,0.08)", "good": "#00e676", "bad": "#ff5252",
    },
    "🌸 Sakura": {
        "bg": "#fef0f5", "sidebar": "#fff5f8", "card": "#ffffff",
        "text": "#5c2244", "accent": "#e91e63", "accent2": "#c2185b",
        "border": "rgba(233,30,99,0.15)", "input_bg": "#fff8fa",
        "shadow": "rgba(233,30,99,0.08)", "good": "#4caf50", "bad": "#e53935",
    },
    "🌲 Forest": {
        "bg": "#0b1a10", "sidebar": "#0e1f14", "card": "#162a1c",
        "text": "#b9d6bc", "accent": "#66bb6a", "accent2": "#388e3c",
        "border": "rgba(102,187,106,0.15)", "input_bg": "#1a2d1f",
        "shadow": "rgba(76,175,80,0.08)", "good": "#81c784", "bad": "#ef5350",
    },
    "🔮 Cosmic Purple": {
        "bg": "#140a26", "sidebar": "#1a0e30", "card": "#221440",
        "text": "#d1c4e9", "accent": "#b388ff", "accent2": "#7c4dff",
        "border": "rgba(179,136,255,0.15)", "input_bg": "#2d1b4e",
        "shadow": "rgba(124,77,255,0.08)", "good": "#69f0ae", "bad": "#ff5252",
    },
    "☀️ Sunrise": {
        "bg": "#fffaf0", "sidebar": "#fff5e6", "card": "#ffffff",
        "text": "#4e342e", "accent": "#ff6d00", "accent2": "#e65100",
        "border": "rgba(255,109,0,0.15)", "input_bg": "#fffde7",
        "shadow": "rgba(255,109,0,0.08)", "good": "#66bb6a", "bad": "#e53935",
    },
    "🖤 Midnight": {
        "bg": "#0d0d0d", "sidebar": "#111111", "card": "#1a1a1a",
        "text": "#d4d4d4", "accent": "#e0e0e0", "accent2": "#9e9e9e",
        "border": "rgba(255,255,255,0.08)", "input_bg": "#1e1e1e",
        "shadow": "rgba(255,255,255,0.03)", "good": "#4caf50", "bad": "#ef5350",
    },
    "🤍 Clean Light": {
        "bg": "#f8f9fc", "sidebar": "#ffffff", "card": "#ffffff",
        "text": "#1a1a2e", "accent": "#1976d2", "accent2": "#1565c0",
        "border": "rgba(25,118,210,0.12)", "input_bg": "#f0f4f8",
        "shadow": "rgba(25,118,210,0.06)", "good": "#2e7d32", "bad": "#c62828",
    },
}


def get_theme_css(theme_name: str) -> str:
    t = _THEME_PARAMS.get(theme_name, _THEME_PARAMS["🌊 Deep Ocean"])
    return f"""<style>
    .stApp {{ background-color: {t['bg']}; color: {t['text']}; }}
    section[data-testid="stSidebar"] {{ background-color: {t['sidebar']}; border-right: 1px solid {t['border']}; }}
    h1,h2,h3,h4 {{ color: {t['accent']} !important; }}
    [data-testid="stMetric"] {{ background: {t['card']}; border:1px solid {t['border']}; border-radius:12px; padding:14px; box-shadow:0 4px 12px {t['shadow']}; }}
    [data-testid="stMetricValue"] {{ color: {t['accent']} !important; }}
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {{ background-color: {t['input_bg']}; color: {t['text']}; border:1px solid {t['border']}; border-radius:8px; }}
    .stButton>button {{ border-radius:8px; font-weight:600; transition:all .2s; }}
    .stButton>button:hover {{ transform:translateY(-1px); box-shadow:0 4px 14px {t['shadow']}; }}
    .stChatMessage {{ background:{t['card']}; border:1px solid {t['border']}; border-radius:12px; }}
    .stTabs [data-baseweb="tab"] {{ background:{t['card']}; border:1px solid {t['border']}; border-radius:8px 8px 0 0; color:{t['text']}; }}
    .stTabs [aria-selected="true"] {{ background:{t['accent']}; color:{t['bg']}; }}
    .stExpander {{ border:1px solid {t['border']}; border-radius:10px; }}
    div[data-testid="stExpander"] details {{ border:1px solid {t['border']}; border-radius:10px; }}
    ::-webkit-scrollbar {{ width:7px; }}
    ::-webkit-scrollbar-track {{ background:{t['bg']}; }}
    ::-webkit-scrollbar-thumb {{ background:{t['accent2']}; border-radius:4px; }}
    .mm-card {{ background:{t['card']}; border:1px solid {t['border']}; border-radius:14px; padding:22px; margin:10px 0; box-shadow:0 4px 14px {t['shadow']}; }}
    .mm-accent {{ color:{t['accent']}; font-weight:700; }}
    .mm-good {{ color:{t['good']}; }} .mm-bad {{ color:{t['bad']}; }}
    </style>"""


def get_plotly_colors(theme_name: str) -> dict:
    palettes = {
        "🌊 Deep Ocean":    {"bg":"#0a1628","paper":"#162038","text":"#c8d6e5","grid":"#1e3050","colors":["#00d4ff","#0091d5","#00e676","#ffab40","#ff5252","#b388ff","#18ffff"]},
        "🌸 Sakura":        {"bg":"#fef0f5","paper":"#ffffff","text":"#5c2244","grid":"#f5d5e0","colors":["#e91e63","#f06292","#f48fb1","#ad1457","#c2185b","#ff80ab","#ff4081"]},
        "🌲 Forest":        {"bg":"#0b1a10","paper":"#162a1c","text":"#b9d6bc","grid":"#203a26","colors":["#66bb6a","#43a047","#81c784","#a5d6a7","#2e7d32","#00c853","#1b5e20"]},
        "🔮 Cosmic Purple": {"bg":"#140a26","paper":"#221440","text":"#d1c4e9","grid":"#322050","colors":["#b388ff","#7c4dff","#ea80fc","#ce93d8","#aa00ff","#d500f9","#651fff"]},
        "☀️ Sunrise":       {"bg":"#fffaf0","paper":"#ffffff","text":"#4e342e","grid":"#ffe0b2","colors":["#ff6d00","#ff9800","#ffa726","#e65100","#f57c00","#ffb74d","#ff5722"]},
        "🖤 Midnight":      {"bg":"#0d0d0d","paper":"#1a1a1a","text":"#d4d4d4","grid":"#2a2a2a","colors":["#e0e0e0","#bdbdbd","#9e9e9e","#ffffff","#757575","#b0b0b0","#cccccc"]},
        "🤍 Clean Light":   {"bg":"#f8f9fc","paper":"#ffffff","text":"#1a1a2e","grid":"#e0e0e0","colors":["#1976d2","#42a5f5","#1565c0","#64b5f6","#0d47a1","#90caf9","#1e88e5"]},
    }
    return palettes.get(theme_name, palettes["🌊 Deep Ocean"])
