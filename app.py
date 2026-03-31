# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — app.py  CHUNK 5 of 10  (v3 · Full Blueprint)  ║
# ║  Imports · Page Config · Session State · Theme Engine ·         ║
# ║  Plotly Helpers · Crisis Protocol · Consent / Celebration       ║
# ║  Components · Complete Sidebar                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

# ═══════════════════════════════════════════════════════════════════
#  SECTION 1 — IMPORTS
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
import json
import os
import re
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Database ────────────────────────────────────────────────────────
from database import (
    init_db,
    get_or_create_user,
    save_entry,
    get_entries,
    delete_entry,
    entry_count,
    get_sentiments_over_time,
    save_analysis,
    get_analyses,
    save_chat_msg,
    get_chat_msgs,
    get_chat_sessions,
    delete_chat_session,
    save_psyche_profile,
    get_psyche_profile,
    save_mood_checkin,
    get_mood_checkins,
    save_goal,
    get_goals,
    update_goal_progress,
    save_growth_metrics,
    get_growth_metrics,
    log_crisis_event,
    get_crisis_logs,
)

# backup and database imports
from backup import (
    show_persistence_warning,
    show_backup_reminder_if_needed,
    show_restore_widget,
)

# ── Analyzer ────────────────────────────────────────────────────────
from analyzer import (
    sentiment_score,
    detect_emotions,
    detect_granular_emotions,
    detect_cognitive_distortions,
    extract_entities,
    extract_topics,
    word_frequencies,
    detect_time_of_day,
    detect_day_mentions,
    estimate_big_five,
    calculate_growth_metrics,
    detect_mood_trend,
    detect_day_of_week_patterns,
    find_triggers,
    detect_surprise_patterns,
    detect_crisis,
    local_analysis,
    ai_analysis,
    ai_chat,
    ai_reflection_prompts,
    generate_session_summary,
    generate_narrative_summary,
    ai_distortion_analysis,
    ai_mood_forecast,
    generate_micro_celebration,
    get_relevant_community_stat,
    get_proactive_prompt,
    aggregate_distortions,
    compute_topic_sentiment_correlation,
    compute_weekly_heatmap,
    SKILL_MODULES,
    REFLECTION_JOURNEYS,
    GROUNDING_EXERCISES,
    CHAT_MODE_PROMPTS,
    CONSENT_NOTICE_ANALYSIS,
    CONSENT_NOTICE_CHAT,
)

# ── Themes ──────────────────────────────────────────────────────────
from themes import (
    get_theme_css,
    get_plotly_colors,
    get_theme,
    get_theme_recommendation,
    THEME_NAMES,
)


# ═══════════════════════════════════════════════════════════════════
#  SECTION 2 — PAGE CONFIG  (must be the first Streamlit call)
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="MindMirror AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════════════════════
#  SECTION 3 — SESSION STATE DEFAULTS
# ═══════════════════════════════════════════════════════════════════

_DEFAULTS: Dict[str, Any] = {
    # ── Core ─────────────────────────────────────────────────────
    "user_id":               None,
    "username":              "",
    "logged_in":             False,
    "page":                  "📝 Journal",
    "theme":                 "🌊 Deep Ocean",
    "api_key":               "",
    "model":                 "gemini-2.5-flash",
    "chat_session":          "default",
    "current_analysis":      None,

    # ── Onboarding & Profile ─────────────────────────────────────
    "onboarding_complete":   False,
    "psyche_profile":        {},

    # ── Privacy & Consent ────────────────────────────────────────
    "privacy_mode":          "standard",        # standard | local_only
    "consent_ai_processing": True,

    # ── Adaptive UI ──────────────────────────────────────────────
    "adaptive_theme_enabled": True,
    "font_size_scale":       1.0,               # 0.8–1.5
    "high_contrast":         False,
    "reduce_motion":         False,

    # ── Therapeutic AI ───────────────────────────────────────────
    "therapeutic_mode":      "open",            # open | cbt | validation | reflection | homework
    "empathy_level":         0.5,               # 0.0–1.0  (UI shows 1–10)

    # ── Internal Flags ───────────────────────────────────────────
    "_profile_loaded":       False,
}

for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ═══════════════════════════════════════════════════════════════════
#  SECTION 4 — API KEY · DATABASE · AUTO-LOGIN · PROFILE LOAD
# ═══════════════════════════════════════════════════════════════════

# ── Load API key from Streamlit Secrets ──────────────────────────
try:
    _secret_key = st.secrets.get("GEMINI_API_KEY", "")
    if _secret_key and not st.session_state.api_key:
        st.session_state.api_key = _secret_key
except (KeyError, FileNotFoundError, AttributeError):
    pass

# ── Initialise database (idempotent — safe to run on every load) ─
init_db()

# ── Auto-login from URL ?user=... so refresh doesn't log out ────
if not st.session_state.logged_in:
    _params = st.query_params
    if "user" in _params:
        _uname = _params["user"]
        if isinstance(_uname, str) and _uname.strip():
            st.session_state.username = _uname.strip()
            st.session_state.user_id = get_or_create_user(_uname.strip())
            st.session_state.logged_in = True

# ── Load psyche profile from DB (once per session) ──────────────
if (
    st.session_state.logged_in
    and st.session_state.user_id
    and not st.session_state.get("_profile_loaded")
):
    _profile = get_psyche_profile(st.session_state.user_id)
    if _profile:
        st.session_state.psyche_profile = _profile
        st.session_state.onboarding_complete = True
        # Restore saved preferences
        _mode = _profile.get("therapeutic_mode_default", "open")
        if _mode in CHAT_MODE_PROMPTS:
            st.session_state.therapeutic_mode = _mode
        _emp = _profile.get("empathy_level")
        if _emp is not None:
            st.session_state.empathy_level = max(0.0, min(1.0, _emp / 10.0))
    st.session_state._profile_loaded = True


# ═══════════════════════════════════════════════════════════════════
#  SECTION 5 — ADAPTIVE THEME ENGINE
# ═══════════════════════════════════════════════════════════════════

def apply_theme():
    """Apply the user's chosen theme with optional mood-adaptive tinting."""
    base_css = get_theme_css(
        st.session_state.theme,
        font_size_scale=st.session_state.get("font_size_scale", 1.0),
        high_contrast=st.session_state.get("high_contrast", False),
        reduce_motion=st.session_state.get("reduce_motion", False),
    )

    adaptive_css = ""
    if (
        st.session_state.get("adaptive_theme_enabled", True)
        and st.session_state.logged_in
        and st.session_state.user_id
    ):
        try:
            recent = get_entries(st.session_state.user_id, limit=5)
            sents = [
                e["sentiment"]
                for e in recent
                if e.get("sentiment") is not None
            ]
            if sents:
                avg = sum(sents) / len(sents)
                if avg > 0.3:
                    tint = "#4CAF50"   # warm green — thriving
                elif avg > 0.0:
                    tint = "#2196F3"   # calm blue — neutral-positive
                elif avg > -0.3:
                    tint = "#FF9800"   # amber — slightly low
                else:
                    tint = "#9C27B0"   # soft purple — calming for distress
                adaptive_css = f"""
                <style>
                .mm-card {{
                    border-left: 4px solid {tint} !important;
                }}
                .mm-celebration {{
                    border-left: 4px solid {tint} !important;
                }}
                </style>
                """
        except Exception:
            pass

    st.markdown(base_css + adaptive_css, unsafe_allow_html=True)

apply_theme()


# ═══════════════════════════════════════════════════════════════════
#  SECTION 6 — PLOTLY HELPERS
# ═══════════════════════════════════════════════════════════════════

def _plotly_layout(fig, title: str = ""):
    """Apply the current theme to a Plotly figure."""
    pc = get_plotly_colors(st.session_state.theme)
    fig.update_layout(
        title=title,
        plot_bgcolor=pc["paper"],
        paper_bgcolor=pc["paper"],
        font_color=pc["text"],
        title_font_color=pc["text"],
        xaxis=dict(gridcolor=pc["grid"], zerolinecolor=pc["grid"]),
        yaxis=dict(gridcolor=pc["grid"], zerolinecolor=pc["grid"]),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(font=dict(color=pc["text"])),
    )
    return fig


def _pcolors() -> List[str]:
    """Shortcut to get the current theme's Plotly color sequence."""
    return get_plotly_colors(st.session_state.theme)["colors"]


def _accent() -> str:
    """Get the current theme's primary accent color."""
    return get_plotly_colors(st.session_state.theme)["accent"]


# ═══════════════════════════════════════════════════════════════════
#  SECTION 7 — CRISIS SUPPORT COMPONENT
# ═══════════════════════════════════════════════════════════════════

def show_crisis_support(source: str = "unknown"):
    """Display crisis resources. Call from journal, chat, or analysis.
    Optionally log the event (with user consent)."""
    st.markdown(
        '<div class="mm-crisis">',
        unsafe_allow_html=True,
    )
    st.error(
        "🚨 **You matter.** If you're in crisis or thinking about "
        "self-harm, please reach out. You are not alone."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            "**988 Suicide & Crisis Lifeline**\n\n"
            "📞 Call or text **988** (24/7, US)\n\n"
            "[988lifeline.org](https://988lifeline.org)"
        )
    with c2:
        st.markdown(
            "**Crisis Text Line**\n\n"
            "📱 Text **HOME** to **741741**\n\n"
            "[crisistextline.org](https://www.crisistextline.org)"
        )
    with c3:
        st.markdown(
            "**International Resources**\n\n"
            "🌍 Find your country's helpline\n\n"
            "[iasp.info](https://www.iasp.info/resources/Crisis_Centres/)"
        )
    st.caption(
        "MindMirror AI is **not** a crisis service. These organisations "
        "have trained counsellors available right now."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Log the event silently (for follow-up prompts later)
    if st.session_state.logged_in and st.session_state.user_id:
        try:
            log_crisis_event(
                st.session_state.user_id,
                trigger_snippet=f"[{source}]",
                notes=f"auto-detected at {datetime.now().isoformat()}",
            )
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
#  SECTION 8 — REUSABLE UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════

def show_consent_notice(notice_text: str) -> bool:
    """Show a consent notice before an AI call. Returns True if user
    consents (or has already given blanket consent)."""
    if st.session_state.privacy_mode == "local_only":
        st.warning("🔒 AI features are disabled in **Local-only** mode.")
        return False
    if not st.session_state.consent_ai_processing:
        st.warning(
            "🔒 AI consent is revoked. Enable it in **⚙️ Settings** "
            "to use this feature."
        )
        return False
    # Show the notice (informational, not blocking)
    st.caption(notice_text)
    return True


def show_celebrations(entries: List[Dict], goals: Optional[List[Dict]] = None):
    """Display micro-celebrations based on activity."""
    celebrations = generate_micro_celebration(entries, goals)
    if celebrations:
        for c in celebrations[:2]:
            st.markdown(
                f'<div class="mm-celebration">{c}</div>',
                unsafe_allow_html=True,
            )


def show_community_stat(entries: List[Dict]):
    """Show an anonymised 'you're not alone' stat."""
    stat = get_relevant_community_stat(entries)
    if stat:
        st.caption(f"💬 *You're not alone:* {stat}")


def show_proactive_prompt_widget(entries: List[Dict]):
    """Show a context-aware proactive prompt / nudge."""
    pp = get_proactive_prompt(entries)
    if pp:
        icon = {
            "welcome": "🌟",
            "grounding": "🧘",
            "checkin": "🌡️",
            "amplify": "✨",
            "journaling_cue": "💭",
        }.get(pp["type"], "💡")

        with st.container():
            st.markdown(f"**{icon} {pp['message']}**")
            if pp.get("exercise"):
                with st.expander(
                    f"Try: {pp['exercise']['name']}", expanded=False
                ):
                    st.markdown(pp["exercise"]["instruction"])


def format_mode_label(mode_key: str) -> str:
    """Convert internal mode key to display label."""
    return CHAT_MODE_PROMPTS.get(mode_key, {}).get("label", mode_key)


# ═══════════════════════════════════════════════════════════════════
#  SECTION 9 — SIDEBAR
# ═══════════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🧠 MindMirror AI")
        st.caption("*Decode your mind. Discover your patterns.*")
        st.markdown("---")

        # ────────────────────────────────────────────────────────
        #  NOT LOGGED IN → show login form
        # ────────────────────────────────────────────────────────
        if not st.session_state.logged_in:
            st.markdown("#### 👤 Get Started")
            uname = st.text_input(
                "Your name:",
                key="_login_name",
                placeholder="e.g. Alex",
            )
            if st.button(
                "🚀 Enter MindMirror",
                use_container_width=True,
                type="primary",
            ):
                if uname.strip():
                    st.session_state.username = uname.strip()
                    st.session_state.user_id = get_or_create_user(
                        uname.strip()
                    )
                    st.session_state.logged_in = True
                    st.query_params["user"] = uname.strip()
                    st.rerun()
                else:
                    st.warning("Please type a name.")
            return  # nothing else to show when logged out

        # ────────────────────────────────────────────────────────
        #  LOGGED IN
        # ────────────────────────────────────────────────────────
        uid = st.session_state.user_id
        ec = entry_count(uid)

        # ── User identity ────────────────────────────────────────
        st.markdown(f"#### 👤 {st.session_state.username}")
        st.caption(f"📊 {ec} journal entries saved")

                # ── Persistence warning ──────────────────────────────────
        show_persistence_warning()
        show_backup_reminder_if_needed()

        # ── Status badges ────────────────────────────────────────
        badge_cols = st.columns(2)
        with badge_cols[0]:
            if st.session_state.api_key:
                st.caption("🔑 Gemini ✅")
            else:
                st.caption("🔑 Gemini ⚠️")
        with badge_cols[1]:
            pm = st.session_state.privacy_mode
            if pm == "local_only":
                st.caption("🔒 Local-only")
            else:
                st.caption("🌐 Standard")

        st.markdown("---")

        # ── Quick Mood Pulse ─────────────────────────────────────
        with st.expander("🌡️ Quick Mood Pulse", expanded=False):
            st.caption(
                "Rate how you feel right now (0 = not at all, 3 = nearly every day)."
            )
            p_c1, p_c2 = st.columns(2)
            with p_c1:
                q_interest = st.slider(
                    "Interest / pleasure",
                    0, 3, 1,
                    key="_pulse_interest",
                )
            with p_c2:
                q_down = st.slider(
                    "Feeling down",
                    0, 3, 1,
                    key="_pulse_down",
                )
            q_energy = st.slider(
                "Energy level (1–10)",
                1, 10, 5,
                key="_pulse_energy",
            )
            if st.button("💾 Save Pulse", key="_pulse_save"):
                total = q_interest + q_down
                save_mood_checkin(
                    uid,
                    "quick_pulse",
                    [q_interest, q_down, q_energy],
                    total,
                )
                st.success("✅ Pulse saved!")

        # ── Micro-celebration / proactive prompt ─────────────────
        if ec > 0:
            try:
                _recent = get_entries(uid, limit=10)
                _goals = get_goals(uid, status="active")
                _celebrations = generate_micro_celebration(
                    _recent, _goals
                )
                if _celebrations:
                    st.markdown(
                        f'<div class="mm-celebration" '
                        f'style="font-size:0.85em;padding:10px;">'
                        f'{_celebrations[0]}</div>',
                        unsafe_allow_html=True,
                    )
            except Exception:
                pass

        st.markdown("---")

        # ── Active Goal Mini-View ────────────────────────────────
        try:
            _active_goals = get_goals(uid, status="active")
        except Exception:
            _active_goals = []

        if _active_goals:
            with st.expander(
                f"🎯 Active Goals ({len(_active_goals)})",
                expanded=False,
            ):
                for _g in _active_goals[:3]:
                    prog = min(1.0, max(0.0, (_g.get("progress") or 0) / 100.0))
                    st.markdown(f"**{_g['title']}**")
                    st.progress(prog)
                    st.caption(f"{_g.get('progress', 0):.0f}% complete")
        else:
            st.caption("🎯 No active goals — set one in **📊 Dashboard**")

        st.markdown("---")

        # ── Navigation ───────────────────────────────────────────
        st.markdown("#### 📍 Navigate")
        _pages = [
            "📝 Journal",
            "🔬 Analysis",
            "💬 AI Chat",
            "📊 Dashboard",
            "🧘 Skills & Growth",
            "📂 History",
            "⚙️ Settings",
        ]
        for _p in _pages:
            _kind = (
                "primary"
                if st.session_state.page == _p
                else "secondary"
            )
            if st.button(
                _p,
                use_container_width=True,
                type=_kind,
                key=f"nav_{_p}",
            ):
                st.session_state.page = _p
                st.rerun()

        st.markdown("---")

        # ── Theme Selector ───────────────────────────────────────
        st.markdown("#### 🎨 Theme")
        _theme_idx = (
            THEME_NAMES.index(st.session_state.theme)
            if st.session_state.theme in THEME_NAMES
            else 0
        )
        _chosen_theme = st.selectbox(
            "Select theme:",
            THEME_NAMES,
            index=_theme_idx,
            key="_theme_sel",
            label_visibility="collapsed",
        )
        if _chosen_theme != st.session_state.theme:
            st.session_state.theme = _chosen_theme
            st.rerun()

        st.checkbox(
            "🌈 Adaptive tint (shifts with mood)",
            value=st.session_state.adaptive_theme_enabled,
            key="_adaptive_chk",
            on_change=lambda: st.session_state.update(
                {"adaptive_theme_enabled": st.session_state._adaptive_chk}
            ),
        )

        st.markdown("---")

        # ── AI Behavior ──────────────────────────────────────────
        with st.expander("🧠 AI Behavior", expanded=False):
            _mode_keys = list(CHAT_MODE_PROMPTS.keys())
            _mode_labels = [
                CHAT_MODE_PROMPTS[k]["label"] for k in _mode_keys
            ]
            _current_mode_idx = (
                _mode_keys.index(st.session_state.therapeutic_mode)
                if st.session_state.therapeutic_mode in _mode_keys
                else 0
            )
            _selected_label = st.selectbox(
                "Therapeutic mode:",
                _mode_labels,
                index=_current_mode_idx,
                key="_ai_mode_sel",
            )
            _new_mode = _mode_keys[_mode_labels.index(_selected_label)]
            if _new_mode != st.session_state.therapeutic_mode:
                st.session_state.therapeutic_mode = _new_mode

            _emp_display = int(st.session_state.empathy_level * 10)
            _emp_display = max(1, min(10, _emp_display))
            _new_emp = st.slider(
                "Empathy level",
                1, 10, _emp_display,
                key="_emp_slider",
                help="1 = direct & challenging · 10 = deeply nurturing",
            )
            st.session_state.empathy_level = _new_emp / 10.0

            st.caption(
                f"Mode: **{_selected_label}** · "
                f"Empathy: **{_new_emp}/10**"
            )

        # ── Model Selector ───────────────────────────────────────
        st.markdown("#### 🤖 AI Model")
        _models = [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]
        _model_idx = (
            _models.index(st.session_state.model)
            if st.session_state.model in _models
            else 0
        )
        st.session_state.model = st.selectbox(
            "Model:",
            _models,
            index=_model_idx,
            key="_model_sel",
            label_visibility="collapsed",
        )

        st.markdown("---")

        # ── Accessibility ────────────────────────────────────────
        with st.expander("♿ Accessibility", expanded=False):
            _fs = st.slider(
                "Font size",
                0.8, 1.5,
                st.session_state.font_size_scale,
                step=0.1,
                key="_font_scale",
                format="%.1f×",
            )
            if _fs != st.session_state.font_size_scale:
                st.session_state.font_size_scale = _fs
                st.rerun()

            _hc = st.checkbox(
                "High contrast",
                value=st.session_state.high_contrast,
                key="_high_contrast_chk",
            )
            if _hc != st.session_state.high_contrast:
                st.session_state.high_contrast = _hc
                st.rerun()

            _rm = st.checkbox(
                "Reduce motion",
                value=st.session_state.reduce_motion,
                key="_reduce_motion_chk",
            )
            if _rm != st.session_state.reduce_motion:
                st.session_state.reduce_motion = _rm
                st.rerun()

            st.caption(
                "These settings affect theme CSS and respect "
                "the `prefers-reduced-motion` media query."
            )

        st.markdown("---")

        # ── Logout ───────────────────────────────────────────────
        if st.button("🚪 Logout", use_container_width=True):
            st.query_params.clear()
            for _k in list(st.session_state.keys()):
                del st.session_state[_k]
            st.rerun()


# ── Render the sidebar now (runs on every page load) ─────────────
render_sidebar()


# ═══════════════════════════════════════════════════════════════════
#  SECTION 10 — SHARED PAGE HELPERS
# ═══════════════════════════════════════════════════════════════════

def _safe_json_parse(raw, fallback=None):
    """Parse a JSON string or return the original if already parsed."""
    if raw is None:
        return fallback
    if isinstance(raw, (list, dict)):
        return raw
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return fallback


def _entry_mood_icon(sentiment) -> str:
    """Return an emoji for a sentiment score."""
    if sentiment is None:
        return "📝"
    if sentiment > 0.3:
        return "😊"
    if sentiment > 0.0:
        return "🙂"
    if sentiment > -0.3:
        return "😐"
    return "😟"


def _streak(entries: List[Dict]) -> int:
    """Calculate the current consecutive-day journaling streak."""
    dates = sorted(set(
        e.get("entry_date", "")[:10]
        for e in entries
        if e.get("entry_date")
    ))
    if not dates:
        return 0
    streak = 1
    for i in range(len(dates) - 1, 0, -1):
        try:
            d1 = datetime.strptime(dates[i], "%Y-%m-%d")
            d2 = datetime.strptime(dates[i - 1], "%Y-%m-%d")
            if (d1 - d2).days == 1:
                streak += 1
            else:
                break
        except ValueError:
            break
    return streak


def _emotion_tags_html(emotions_raw) -> str:
    """Render emotion data (dict or list) as styled HTML tags."""
    emos = _safe_json_parse(emotions_raw)
    if not emos:
        return ""
    if isinstance(emos, dict):
        items = list(emos.keys())
    elif isinstance(emos, list):
        items = emos
    else:
        return ""
    tags = []
    for em in items[:8]:
        tags.append(
            f'<span class="mm-emotion-tag">{em}</span>'
        )
    return " ".join(tags)


def _distortion_tags_html(dist_raw) -> str:
    """Render distortion tags as styled HTML."""
    dists = _safe_json_parse(dist_raw)
    if not dists:
        return ""
    tags = []
    for d in dists[:5]:
        label = d.get("label", d) if isinstance(d, dict) else d
        tags.append(
            f'<span class="mm-emotion-tag negative">{label}</span>'
        )
    return " ".join(tags)


# ──────────────────────────────────────────────────────────────────
# END OF CHUNK 5 — paste Chunk 6 directly below this line
# ──────────────────────────────────────────────────────────────────
# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — app.py  CHUNK 6 of 10  (v3 · Full Blueprint)  ║
# ║  Onboarding Flow (4 steps) · Enhanced Journal Page              ║
# ║  Guided templates · Mood/Energy sliders · Body zones ·         ║
# ║  Distortion auto-detect · Crisis screening · Batch import      ║
# ╚══════════════════════════════════════════════════════════════════╝


# ═══════════════════════════════════════════════════════════════════
#  ONBOARDING FLOW  (shown once on first login)
# ═══════════════════════════════════════════════════════════════════

def page_onboarding():
    """Four-step personalisation wizard. Saves a psyche profile
    to the database and sets session-state preferences."""

    step = st.session_state.get("_onboard_step", 1)

    st.markdown("# 🌟 Welcome to MindMirror AI")
    st.markdown(
        "Let's personalise your experience — this takes about "
        "**2 minutes** and makes everything smarter."
    )
    st.progress((step - 1) / 4)
    st.caption(f"Step {step} of 4")
    st.markdown("---")

    # ── Step 1: Core Values ──────────────────────────────────────
    if step == 1:
        st.markdown("### 1️⃣ What matters most to you right now?")
        st.caption("Pick up to 3 core values. These shape the insights MindMirror offers.")

        all_values = [
            "Growth", "Connection", "Autonomy", "Security",
            "Joy", "Purpose", "Balance", "Creativity",
            "Health", "Authenticity", "Adventure", "Kindness",
        ]
        selected = st.multiselect(
            "Your values:",
            all_values,
            default=["Growth"],
            max_selections=3,
            key="_onb_values",
        )

        st.markdown("")
        if st.button("Next →", type="primary", key="_onb_next_1"):
            if selected:
                st.session_state.setdefault("_onb_data", {})
                st.session_state._onb_data["values"] = selected
                st.session_state._onboard_step = 2
                st.rerun()
            else:
                st.warning("Pick at least one value.")

    # ── Step 2: Support Style & Therapeutic Mode ─────────────────
    elif step == 2:
        st.markdown("### 2️⃣ How should MindMirror talk to you?")
        st.caption(
            "Everyone processes differently. Choose the style "
            "that feels right — you can change this anytime."
        )

        style = st.select_slider(
            "Support style:",
            options=[
                "Gentle & Validating",
                "Balanced",
                "Direct & Challenging",
            ],
            value="Balanced",
            key="_onb_style",
        )

        st.markdown("")
        st.markdown("**Default therapeutic mode for AI Chat:**")
        _mode_keys = list(CHAT_MODE_PROMPTS.keys())
        _mode_labels = [CHAT_MODE_PROMPTS[k]["label"] for k in _mode_keys]
        mode_label = st.radio(
            "Mode:",
            _mode_labels,
            index=0,
            key="_onb_mode",
            label_visibility="collapsed",
        )
        mode_key = _mode_keys[_mode_labels.index(mode_label)]

        st.markdown("")
        emp = st.slider(
            "Empathy level (1 = minimal warmth · 10 = deeply nurturing):",
            1, 10, 7,
            key="_onb_empathy",
        )

        st.markdown("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back", key="_onb_back_2"):
                st.session_state._onboard_step = 1
                st.rerun()
        with c2:
            if st.button("Next →", type="primary", key="_onb_next_2"):
                data = st.session_state.setdefault("_onb_data", {})
                data["support_style"] = style
                data["therapeutic_mode"] = mode_key
                data["empathy_level"] = emp
                st.session_state._onboard_step = 3
                st.rerun()

    # ── Step 3: Custom Emotion Vocabulary ────────────────────────
    elif step == 3:
        st.markdown("### 3️⃣ Your emotional vocabulary")
        st.caption(
            "MindMirror comes with standard emotions, but you might use "
            "words like *'overwhelmed'*, *'flow'*, or *'meh'*. "
            "Add your own so the app speaks **your** language."
        ) 
            
            
            
        

        default_display = [
            "😊 Joy", "😢 Sadness", "😠 Anger", "😰 Fear",
            "😌 Calm", "🌟 Hope", "😔 Guilt", "😮 Surprise",
        ]
        st.markdown("**Built-in emotions:** " + " · ".join(default_display))

        st.markdown("")
        custom_lexicon = st.session_state.get("_onb_lexicon", {})

        add_col1, add_col2 = st.columns([3, 1])
        with add_col1:
            new_word = st.text_input(
                "Add a custom emotion:",
                key="_onb_emo_input",
                placeholder="e.g. Overwhelmed, Flow, Meh, Grateful",
            )
        with add_col2:
            st.markdown("")
            st.markdown("")
            if st.button("➕ Add", key="_onb_emo_add"):
                if new_word.strip():
                    key = new_word.strip().lower()
                    custom_lexicon[key] = new_word.strip()
                    st.session_state._onb_lexicon = custom_lexicon
                    st.rerun()

        if custom_lexicon:
            st.markdown("**Your custom emotions:**")
            tags_html = " ".join(
                f'<span class="mm-emotion-tag">{v}</span>'
                for v in custom_lexicon.values()
            )
            st.markdown(tags_html, unsafe_allow_html=True)
            if st.button("🗑️ Clear all custom", key="_onb_emo_clear"):
                st.session_state._onb_lexicon = {}
                st.rerun()
        else:
            st.caption("No custom emotions added yet. That's fine — you can always add them later in Settings.")

        st.markdown("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back", key="_onb_back_3"):
                st.session_state._onboard_step = 2
                st.rerun()
        with c2:
            if st.button("Next →", type="primary", key="_onb_next_3"):
                data = st.session_state.setdefault("_onb_data", {})
                data["custom_lexicon"] = custom_lexicon
                st.session_state._onboard_step = 4
                st.rerun()

    # ── Step 4: Privacy & Consent ────────────────────────────────
    elif step == 4:
        st.markdown("### 4️⃣ Privacy & data controls")

        st.info(
            "📦 **All your journal entries, chats, and analyses are stored "
            "locally** in a SQLite database on the server. Nothing is shared "
            "with third parties.\n\n"
            "🤖 **AI features** (Analysis, Chat) send your selected text to "
            "Google Gemini **only when you click the button**. Gemini does not "
            "retain your data after the request."
        )

        consent = st.checkbox(
            "I consent to sending journal entries to Google Gemini "
            "when I explicitly use AI features.",
            value=True,
            key="_onb_consent",
        )

        privacy = st.radio(
            "Privacy mode:",
            [
                "🌐 Standard — AI features enabled (recommended)",
                "🔒 Local-only — all AI features disabled",
            ],
            index=0,
            key="_onb_privacy",
        )
        is_local = "Local" in privacy

        st.markdown("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back", key="_onb_back_4"):
                st.session_state._onboard_step = 3
                st.rerun()
        with c2:
            if st.button("🚀 Finish Setup", type="primary", key="_onb_finish"):
                data = st.session_state.get("_onb_data", {})

                # Save to database
                save_psyche_profile(
                    user_id=st.session_state.user_id,
                    values=data.get("values", ["Growth"]),
                    support_style=data.get("support_style", "Balanced"),
                    therapeutic_mode_default=data.get("therapeutic_mode", "open"),
                    empathy_level=data.get("empathy_level", 7),
                    custom_lexicon=data.get("custom_lexicon"),
                )

                # Update session state
                st.session_state.psyche_profile = {
                    "values": data.get("values", ["Growth"]),
                    "support_style": data.get("support_style", "Balanced"),
                    "therapeutic_mode_default": data.get("therapeutic_mode", "open"),
                    "empathy_level": data.get("empathy_level", 7),
                    "custom_lexicon": data.get("custom_lexicon", {}),
                }
                st.session_state.therapeutic_mode = data.get("therapeutic_mode", "open")
                st.session_state.empathy_level = data.get("empathy_level", 7) / 10.0
                st.session_state.consent_ai_processing = consent
                st.session_state.privacy_mode = "local_only" if is_local else "standard"
                st.session_state.onboarding_complete = True

                # Cleanup
                for k in ["_onb_data", "_onb_lexicon", "_onboard_step"]:
                    st.session_state.pop(k, None)

                st.success("✅ You're all set! Redirecting to your journal…")
                st.balloons()
                st.rerun()


# ═══════════════════════════════════════════════════════════════════
#  GUIDED JOURNAL TEMPLATES
# ═══════════════════════════════════════════════════════════════════

JOURNAL_TEMPLATES = {
    "freeform": {
        "label": "✏️ Freeform",
        "description": "Write whatever comes to mind — no structure required.",
        "placeholder": (
            "Today I felt… / I noticed that… / Something happened that…"
        ),
        "prompts": None,
    },
    "thought_record": {
        "label": "🧠 Thought Record (CBT)",
        "description": (
            "A structured CBT exercise to examine and reframe a thought."
        ),
        "placeholder": None,
        "prompts": [
            ("Situation", "What happened? Where were you? Who was there?"),
            ("Automatic Thought", "What went through your mind? What were you telling yourself?"),
            ("Emotion & Intensity", "What did you feel? Rate it 0–100."),
            ("Evidence For", "What facts support this thought?"),
            ("Evidence Against", "What facts contradict or weaken this thought?"),
            ("Balanced Thought", "What's a more realistic or compassionate way to see this?"),
        ],
    },
    "gratitude": {
        "label": "🙏 Gratitude",
        "description": "Shift attention to what's going well.",
        "placeholder": None,
        "prompts": [
            ("I'm grateful for…", "Name 3 things, big or small, that you appreciate today."),
            ("Someone I appreciate", "Who made a difference recently, and what did they do?"),
            ("A strength I used today", "What personal quality helped you get through the day?"),
        ],
    },
    "evening_review": {
        "label": "🌙 Evening Review",
        "description": "Reflect on the day with clarity and kindness.",
        "placeholder": None,
        "prompts": [
            ("High point", "What was the best moment of your day?"),
            ("Challenge", "What was hard? How did you handle it?"),
            ("Lesson", "What did you learn — about yourself or the world?"),
            ("Tomorrow", "What one thing would make tomorrow good?"),
        ],
    },
    "body_check": {
        "label": "🧘 Body Check-In",
        "description": "Notice where emotions live in your body.",
        "placeholder": None,
        "prompts": [
            ("Right now I feel…", "Name the dominant emotion you're carrying right now."),
            ("In my body", "Where do you notice it? Head, chest, stomach, hands, throat?"),
            ("It feels like…", "Describe the physical sensation — tight, heavy, buzzy, numb, warm?"),
            ("What it might need", "If this sensation could speak, what would it ask for?"),
        ],
    },
}


# ═══════════════════════════════════════════════════════════════════
#  JOURNAL PAGE
# ═══════════════════════════════════════════════════════════════════

def page_journal():
    st.markdown("# 📝 Journal")

    uid = st.session_state.user_id
    entries = get_entries(uid, limit=10)

    # ── Proactive prompt at the top ──────────────────────────────
    show_proactive_prompt_widget(entries)

    st.markdown("---")

    tab_new, tab_batch, tab_entries = st.tabs(
        ["✏️ New Entry", "📋 Batch Import", "📖 My Entries"]
    )

    # ═════════════════════════════════════════════════════════════
    #  TAB 1: NEW ENTRY
    # ═════════════════════════════════════════════════════════════
    with tab_new:

        # ── Date / Time ──────────────────────────────────────────
        meta_col, mood_col = st.columns([3, 1])

        with meta_col:
            date_c, time_c = st.columns(2)
            with date_c:
                entry_date = st.date_input(
                    "Date:", value=datetime.now(), key="_j_date"
                )
            with time_c:
                entry_time = st.time_input(
                    "Time:", value=datetime.now().time(), key="_j_time"
                )

        # ── Mood & Energy sliders ────────────────────────────────
        with mood_col:
            st.markdown("##### 🌡️ Mood & Energy")
            mood_score = st.slider(
                "Mood",
                -1.0, 1.0, 0.0, 0.05,
                key="_j_mood",
                help="−1 = very low · 0 = neutral · +1 = very good",
            )
            energy_level = st.slider(
                "Energy",
                1, 10, 5,
                key="_j_energy",
                help="1 = exhausted · 10 = buzzing",
            )

        st.markdown("---")

        # ── Template selector ────────────────────────────────────
        tmpl_keys = list(JOURNAL_TEMPLATES.keys())
        tmpl_labels = [JOURNAL_TEMPLATES[k]["label"] for k in tmpl_keys]

        st.markdown("##### Choose a journaling style")
        tmpl_cols = st.columns(len(tmpl_keys))
        chosen_tmpl = st.session_state.get("_j_template", "freeform")

        for i, key in enumerate(tmpl_keys):
            with tmpl_cols[i]:
                btn_type = "primary" if chosen_tmpl == key else "secondary"
                if st.button(
                    JOURNAL_TEMPLATES[key]["label"],
                    key=f"_j_tmpl_{key}",
                    use_container_width=True,
                    type=btn_type,
                ):
                    st.session_state._j_template = key
                    st.rerun()

        tmpl = JOURNAL_TEMPLATES[chosen_tmpl]
        st.caption(tmpl["description"])

        # ── Content area ─────────────────────────────────────────
        content_parts = []

        if tmpl["prompts"] is None:
            # Freeform
            content = st.text_area(
                "What's on your mind?",
                height=240,
                key="_j_content_free",
                placeholder=tmpl["placeholder"],
            )
            content_parts.append(content)
        else:
            # Guided prompts
            for idx, (label, hint) in enumerate(tmpl["prompts"]):
                answer = st.text_area(
                    label,
                    height=80,
                    key=f"_j_guided_{chosen_tmpl}_{idx}",
                    placeholder=hint,
                )
                if answer.strip():
                    content_parts.append(f"**{label}:** {answer.strip()}")

        full_content = "\n\n".join(
            p for p in content_parts if p and p.strip()
        )

        st.markdown("---")

        # ── Body zones ───────────────────────────────────────────
        body_col, tag_col = st.columns(2)

        with body_col:
            st.markdown("##### 🫁 Body sensations")
            body_options = [
                "Head / Forehead",
                "Eyes / Face",
                "Throat",
                "Chest / Heart",
                "Stomach / Gut",
                "Shoulders / Neck",
                "Hands / Arms",
                "Legs / Feet",
                "Whole body",
                "None noticed",
            ]
            body_zones = st.multiselect(
                "Where do you feel it?",
                body_options,
                default=["None noticed"],
                key="_j_body",
                label_visibility="collapsed",
            )

        with tag_col:
            st.markdown("##### 🏷️ Tags")
            tags_input = st.text_input(
                "Comma-separated tags:",
                key="_j_tags",
                placeholder="work, sleep, family, exercise",
                label_visibility="collapsed",
            )

        # ── Live distortion preview ──────────────────────────────
        if full_content.strip() and len(full_content) > 20:
            _live_dists = detect_cognitive_distortions(full_content)
            if _live_dists:
                with st.expander(
                    f"🌀 {len(_live_dists)} cognitive pattern"
                    f"{'s' if len(_live_dists) != 1 else ''} detected",
                    expanded=False,
                ):
                    st.caption(
                        "These are common thinking habits, not flaws. "
                        "Awareness is the first step to flexibility."
                    )
                    for d in _live_dists:
                        st.markdown(
                            f"**{d['label']}** — *\"{d['matched']}\"*\n\n"
                            f"↳ {d['description']}\n\n"
                            f"💡 **Reframe:** {d['reframe']}"
                        )
                        st.markdown("---")

        # ── Crisis pre-check ─────────────────────────────────────
        _crisis_detected = False
        if full_content.strip() and detect_crisis(full_content):
            _crisis_detected = True
            show_crisis_support(source="journal_entry")
            st.warning(
                "We noticed some difficult language above. "
                "Please consider reaching out. You can still save "
                "your entry — writing it down can help."
            )

        # ── Save button ──────────────────────────────────────────
        st.markdown("")
        if st.button(
            "💾 Save Entry",
            type="primary",
            use_container_width=True,
            key="_j_save",
        ):
            if not full_content.strip():
                st.warning("Write something first.")
            else:
                dt_str = datetime.combine(
                    entry_date, entry_time
                ).strftime("%Y-%m-%d %H:%M")

                # Sentiment: use slider if user moved it, else auto-detect
                if mood_score != 0.0:
                    final_sentiment = mood_score
                else:
                    final_sentiment = sentiment_score(full_content)

                # Emotions
                emos = detect_emotions(full_content)

                # Cognitive distortions
                dists = detect_cognitive_distortions(full_content)

                # Tags
                user_tags = [
                    t.strip()
                    for t in tags_input.split(",")
                    if t.strip()
                ]
                # Add template type as tag
                if chosen_tmpl != "freeform":
                    user_tags.append(f"template:{chosen_tmpl}")

                # Body zones (clean "None noticed")
                clean_body = [
                    b for b in body_zones if b != "None noticed"
                ] if body_zones else None

                # Save to database
                save_entry(
                    user_id=uid,
                    content=full_content.strip(),
                    entry_date=dt_str,
                    sentiment=final_sentiment,
                    emotions=emos if emos else None,
                    tags=user_tags if user_tags else None,
                    mood_score=mood_score,
                    energy_level=energy_level,
                    body_zones=clean_body if clean_body else None,
                    distortion_tags=dists if dists else None,
                )

                # Log crisis event if detected
                if _crisis_detected:
                    log_crisis_event(
                        uid,
                        trigger_snippet=full_content[:120],
                        notes="detected during journal save",
                    )

                st.success("✅ Entry saved!")
                st.balloons()

                # Show celebration if earned
                updated_entries = get_entries(uid, limit=10)
                _cele = generate_micro_celebration(updated_entries)
                if _cele:
                    for c in _cele[:1]:
                        st.markdown(
                            f'<div class="mm-celebration">{c}</div>',
                            unsafe_allow_html=True,
                        )

    # ═════════════════════════════════════════════════════════════
    #  TAB 2: BATCH IMPORT
    # ═════════════════════════════════════════════════════════════
    with tab_batch:
        st.markdown(
            "Paste multiple entries separated by `---` on its own line. "
            "Optionally prefix each with a date like `2025-03-20:`."
        )
        st.caption(
            "Each entry will be auto-analysed for sentiment, emotions, "
            "and cognitive patterns."
        )

        batch_text = st.text_area(
            "Paste entries:",
            height=300,
            key="_j_batch",
            placeholder=(
                "2025-03-20: I felt great after the morning run…\n"
                "---\n"
                "2025-03-21: Work was overwhelming. I couldn't focus…\n"
                "---\n"
                "Had a good talk with Sarah about everything."
            ),
        )

        if st.button(
            "📥 Import All",
            type="primary",
            key="_j_batch_go",
        ):
            if not batch_text.strip():
                st.warning("Paste some text first.")
            else:
                chunks = [
                    c.strip()
                    for c in batch_text.split("---")
                    if c.strip()
                ]

                if not chunks:
                    st.warning("No entries found. Separate with `---`.")
                else:
                    progress = st.progress(0)
                    imported = 0

                    for i, chunk in enumerate(chunks):
                        progress.progress((i + 1) / len(chunks))

                        # Try to extract date
                        m = re.match(
                            r"^(\d{4}-\d{2}-\d{2})[:\s]*(.*)",
                            chunk, re.S,
                        )
                        if m:
                            dt_str = m.group(1) + " 12:00"
                            text = m.group(2).strip()
                        else:
                            dt_str = datetime.now().strftime(
                                "%Y-%m-%d %H:%M"
                            )
                            text = chunk

                        if not text:
                            continue

                        # Auto-analyse
                        sent = sentiment_score(text)
                        emos = detect_emotions(text)
                        dists = detect_cognitive_distortions(text)
                        topics = extract_topics(text)
                        auto_tags = list(topics.keys())[:5]

                        save_entry(
                            user_id=uid,
                            content=text,
                            entry_date=dt_str,
                            sentiment=sent,
                            emotions=emos if emos else None,
                            tags=auto_tags if auto_tags else None,
                            distortion_tags=dists if dists else None,
                        )
                        imported += 1

                    progress.empty()
                    st.success(
                        f"✅ Imported **{imported}** "
                        f"entr{'ies' if imported != 1 else 'y'} "
                        f"with auto-tagging!"
                    )

                    if imported >= 3:
                        st.info(
                            "💡 Head to **🔬 Analysis** to uncover "
                            "patterns across all your entries."
                        )

    # ═════════════════════════════════════════════════════════════
    #  TAB 3: MY ENTRIES
    # ═════════════════════════════════════════════════════════════
    with tab_entries:
        all_entries = get_entries(uid, limit=200)

        if not all_entries:
            st.info("No entries yet. Start journaling! ✍️")
            return

        # ── Filters ──────────────────────────────────────────────
        filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])

        with filter_col1:
            search = st.text_input(
                "🔍 Search entries:",
                key="_j_search",
                placeholder="Type a keyword…",
                label_visibility="collapsed",
            )
        with filter_col2:
            mood_filter = st.selectbox(
                "Mood filter:",
                ["All", "😊 Positive", "😐 Neutral", "😟 Negative"],
                key="_j_mood_filter",
                label_visibility="collapsed",
            )
        with filter_col3:
            sort_order = st.selectbox(
                "Sort:",
                ["Newest first", "Oldest first", "Most positive", "Most negative"],
                key="_j_sort",
                label_visibility="collapsed",
            )

        # Apply filters
        filtered = all_entries

        if search.strip():
            q = search.strip().lower()
            filtered = [
                e for e in filtered
                if q in e.get("content", "").lower()
            ]

        if mood_filter == "😊 Positive":
            filtered = [
                e for e in filtered
                if (e.get("sentiment") or 0) > 0.15
            ]
        elif mood_filter == "😐 Neutral":
            filtered = [
                e for e in filtered
                if -0.15 <= (e.get("sentiment") or 0) <= 0.15
            ]
        elif mood_filter == "😟 Negative":
            filtered = [
                e for e in filtered
                if (e.get("sentiment") or 0) < -0.15
            ]

        if sort_order == "Oldest first":
            filtered = list(reversed(filtered))
        elif sort_order == "Most positive":
            filtered = sorted(
                filtered,
                key=lambda x: x.get("sentiment") or 0,
                reverse=True,
            )
        elif sort_order == "Most negative":
            filtered = sorted(
                filtered,
                key=lambda x: x.get("sentiment") or 0,
            )

        st.caption(
            f"Showing {len(filtered)} of {len(all_entries)} entries"
        )

        # ── Entry cards ──────────────────────────────────────────
        for e in filtered:
            sent = e.get("sentiment")
            icon = _entry_mood_icon(sent)
            date_str = e.get("entry_date", "")[:16]
            preview = e.get("content", "")[:90].replace("\n", " ")

            # Build expander title
            mood_str = f" ({sent:+.2f})" if sent is not None else ""
            energy = e.get("energy_level")
            energy_str = f"  ⚡{energy}" if energy is not None else ""

            with st.expander(
                f"{icon}  {date_str}{mood_str}{energy_str}  —  {preview}…"
            ):
                # Content
                st.markdown(e["content"])

                st.markdown("---")

                # Metadata row
                info_cols = st.columns(4)

                with info_cols[0]:
                    if sent is not None:
                        color = (
                            "🟢" if sent > 0.15
                            else ("🔴" if sent < -0.15 else "🟡")
                        )
                        st.caption(f"Mood: {color} {sent:+.2f}")

                with info_cols[1]:
                    ms = e.get("mood_score")
                    if ms is not None:
                        st.caption(f"Slider: {ms:+.2f}")

                with info_cols[2]:
                    if energy is not None:
                        st.caption(f"Energy: {energy}/10")

                with info_cols[3]:
                    body = _safe_json_parse(e.get("body_zones"))
                    if body:
                        st.caption(f"Body: {', '.join(body)}")

                # Emotions
                emos_html = _emotion_tags_html(e.get("emotions"))
                if emos_html:
                    st.markdown(
                        f"**Emotions:** {emos_html}",
                        unsafe_allow_html=True,
                    )

                # Tags
                tags = _safe_json_parse(e.get("tags"))
                if tags:
                    st.caption(
                        "Tags: " + ", ".join(f"`{t}`" for t in tags)
                    )

                # Distortions
                dists = _safe_json_parse(e.get("distortion_tags"))
                if dists:
                    st.markdown("**Cognitive patterns detected:**")
                    for d in dists:
                        if isinstance(d, dict):
                            st.caption(
                                f"🌀 {d.get('label', '?')} — "
                                f"*\"{d.get('matched', '')}\"*"
                            )
                        else:
                            st.caption(f"🌀 {d}")

                # Delete
                st.markdown("")
                del_c1, del_c2 = st.columns([3, 1])
                with del_c2:
                    if st.button(
                        "🗑️ Delete",
                        key=f"del_{e['id']}",
                        type="secondary",
                    ):
                        delete_entry(e["id"], uid)
                        st.rerun()


# ──────────────────────────────────────────────────────────────────
# END OF CHUNK 6 — paste Chunk 7 directly below this line
# ──────────────────────────────────────────────────────────────────
# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — app.py  CHUNK 7 of 10  (v3 · Full Blueprint)  ║
# ║  🔬 Enhanced Analysis Page                                      ║
# ║     Distortions · Growth Metrics · Big Five · Emotion Network   ║
# ║     Triggers · Day-of-Week · Heatmap · Forecast · AI Deep      ║
# ║  💬 Enhanced AI Chat Page                                        ║
# ║     Therapeutic Modes · Empathy · Crisis · Session Summaries    ║
# ╚══════════════════════════════════════════════════════════════════╝


# ═══════════════════════════════════════════════════════════════════
#  🔬  ANALYSIS PAGE
# ═══════════════════════════════════════════════════════════════════

def page_analysis():
    st.markdown("# 🔬 Pattern Analysis")
    st.markdown(
        "Uncover cognitive distortions, growth trajectories, emotional "
        "networks, mood triggers, and more — all from your journal."
    )
    st.markdown("---")

    uid = st.session_state.user_id
    all_entries = get_entries(uid, limit=200)

    if len(all_entries) < 2:
        st.warning(
            "Write at least **2 journal entries** before running "
            "an analysis. The more data, the richer the insights."
        )
        return

    # ── Controls ─────────────────────────────────────────────────
    max_entries = min(len(all_entries), 100)
    default_val = min(max_entries, 20)

    # Guard against stale slider value
    if "_an_n" in st.session_state:
        cached = st.session_state["_an_n"]
        if cached > max_entries or cached < 2:
            del st.session_state["_an_n"]

    ctrl1, ctrl2, ctrl3 = st.columns([2, 1, 1])

    with ctrl1:
        if max_entries <= 2:
            n = max_entries
            st.info(f"📋 Analysing all {n} entries")
        else:
            n = st.slider(
                "Entries to analyse:",
                2, max_entries, default_val,
                key="_an_n",
            )

    with ctrl2:
        run_local = st.button(
            "📊 Local Analysis",
            use_container_width=True,
            key="_an_local",
        )

    with ctrl3:
        can_ai = bool(
            st.session_state.api_key
            and st.session_state.privacy_mode != "local_only"
            and st.session_state.consent_ai_processing
        )
        run_ai = st.button(
            "🤖 AI Deep Analysis",
            use_container_width=True,
            type="primary",
            key="_an_ai",
            disabled=not can_ai,
        )
        if not can_ai and not st.session_state.api_key:
            st.caption("Add API key in ⚙️ Settings")

    # Chronological order for analysis
    target = list(reversed(all_entries[:n]))

    # ─────────────────────────────────────────────────────────────
    #  RUN LOCAL ANALYSIS
    # ─────────────────────────────────────────────────────────────
    la = None

    if run_local or run_ai:
        with st.spinner("🔍 Scanning your patterns…"):
            la = local_analysis(target)

        if la:
            st.session_state["_cached_analysis"] = la
    elif "_cached_analysis" in st.session_state:
        la = st.session_state["_cached_analysis"]

    if not la:
        st.caption(
            "Press **Local Analysis** or **AI Deep Analysis** to begin."
        )
        return

    # ═════════════════════════════════════════════════════════════
    #  DISPLAY LOCAL RESULTS
    # ═════════════════════════════════════════════════════════════

    # ── 1. Top metrics ───────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    avg = la.get("avg_sentiment", 0)
    m1.metric("Entries", la.get("entry_count", 0))
    m2.metric(
        "Avg Mood",
        f"{avg:+.2f}",
        delta=(
            "positive" if avg > 0.1
            else ("negative" if avg < -0.1 else "neutral")
        ),
    )
    m3.metric("Emotions", la.get("emotion_diversity", 0))
    m4.metric("Topics", len(la.get("topics", {})))
    m5.metric("🔥 Streak", f"{_streak(all_entries)}d")

    # ── 2. Mood trend ────────────────────────────────────────────
    trend = la.get("mood_trend", {})
    trend_label = trend.get("label", "stable")
    trend_slope = trend.get("slope", 0)
    trend_display = {
        "improving": "📈 Improving",
        "declining": "📉 Declining",
        "stable": "➡️ Stable",
        "insufficient_data": "⏳ Need more data",
    }.get(trend_label, "➡️ Stable")
    st.markdown(
        f"**Mood Trend:** {trend_display} "
        f"(slope: {trend_slope:+.4f})"
    )

    # ── 3. Surprise events ───────────────────────────────────────
    surprises = la.get("surprises", [])
    if surprises:
        st.markdown("### 🌟 Unexpected Moments")
        for s in surprises[:3]:
            st.info(s)

    st.markdown("---")

    # ── 4. Cognitive Distortions ─────────────────────────────────
    distortions = la.get("distortions", {})
    if distortions:
        st.markdown("### 🌀 Cognitive Distortion Patterns")
        st.caption(
            "These are common thinking habits — not flaws. "
            "Awareness is the first step to cognitive flexibility."
        )

        dist_sorted = sorted(
            distortions.items(),
            key=lambda x: x[1]["count"],
            reverse=True,
        )

        dc1, dc2 = st.columns(2)
        for idx, (dtype, dinfo) in enumerate(dist_sorted[:8]):
            col = dc1 if idx % 2 == 0 else dc2
            with col:
                with st.expander(
                    f"🌀 {dinfo['label']} ({dinfo['count']}×)",
                    expanded=(idx == 0),
                ):
                    st.markdown(f"**What it is:** {dinfo['description']}")
                    st.markdown(f"**💡 Reframe:** {dinfo['reframe']}")
                    if dinfo.get("examples"):
                        st.markdown("**From your journal:**")
                        for ex in dinfo["examples"][:3]:
                            st.caption(f'— *"{ex}"*')

        st.markdown("")

    # ── 5. Growth Metrics ────────────────────────────────────────
    gm = la.get("growth_metrics")
    if gm:
        st.markdown("### 📈 Growth Metrics")

        gm_cols = st.columns(3)
        gm_items = [
            ("emotional_regulation", "Emotional Regulation", "🧘", "#64FFDA"),
            ("resilience",           "Resilience",           "💪", "#7BDFF2"),
            ("self_awareness",       "Self-Awareness",       "🔍", "#A29BFE"),
        ]

        for i, (key, name, icon, color) in enumerate(gm_items):
            score = gm.get(key)
            with gm_cols[i]:
                if score is not None:
                    st.markdown(
                        f'<div style="text-align:center;padding:16px;'
                        f'background:var(--mm-card-bg);border-radius:12px;'
                        f'border:1px solid var(--mm-border);">'
                        f'<div style="font-size:1.4em;">{icon}</div>'
                        f'<div style="font-size:0.8em;color:var(--mm-text-secondary);">'
                        f'{name}</div>'
                        f'<div style="font-size:2em;font-weight:700;color:{color};">'
                        f'{score:.0f}<small style="font-size:0.5em">/100</small></div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    # Before/after snapshot
                    ba = gm.get("before_after", {}).get(key, {})
                    before = ba.get("before")
                    after = ba.get("after")
                    if before is not None and after is not None:
                        diff = after - before
                        arrow = "📈" if diff > 2 else ("📉" if diff < -2 else "➡️")
                        st.caption(
                            f"{arrow} Before: {before:.0f} → Now: {after:.0f} ({diff:+.0f})"
                        )
                else:
                    st.caption(f"{icon} {name}: need more data")

        st.markdown("")

    # ── 6. Big Five Personality Hints ────────────────────────────
    big_five = la.get("big_five", {})
    nonzero_bf = {k: v for k, v in big_five.items() if abs(v) > 0.1}
    if nonzero_bf:
        with st.expander("🧬 Personality Hints (Big Five)", expanded=False):
            st.caption(
                "Estimated tendencies based on language patterns. "
                "Not a formal assessment — just clues to explore."
            )
            bf_labels = {
                "openness": "Openness",
                "conscientiousness": "Conscientiousness",
                "extraversion": "Extraversion",
                "agreeableness": "Agreeableness",
                "neuroticism": "Emotional Sensitivity",
            }
            for trait, score in nonzero_bf.items():
                label = bf_labels.get(trait, trait.title())
                direction = "High" if score > 0 else "Low"
                bar_pct = min(100, abs(score) * 50 + 30)
                bar_color = "#64FFDA" if score > 0 else "#FF7675"
                st.markdown(
                    f'<div style="margin-bottom:10px;">'
                    f'<small><b>{label}</b> ({direction})</small>'
                    f'<div style="background:var(--mm-bg-secondary);'
                    f'border-radius:4px;height:8px;margin-top:3px;">'
                    f'<div style="background:{bar_color};'
                    f'border-radius:4px;height:100%;'
                    f'width:{bar_pct:.0f}%;"></div></div>'
                    f'<small style="color:var(--mm-text-secondary);">'
                    f'{score:+.2f}</small></div>',
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    # ── 7. Sentiment Timeline ────────────────────────────────────
    sents = la.get("sentiments", [])
    if sents:
        st.markdown("### 📈 Sentiment Timeline")
        df_s = pd.DataFrame(sents)
        fig = px.line(
            df_s, x="date", y="score",
            markers=True,
            color_discrete_sequence=_pcolors(),
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=7))
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.4)
        fig = _plotly_layout(fig, "")
        st.plotly_chart(fig, use_container_width=True)

    # ── 8. Emotion Network ───────────────────────────────────────
    network = la.get("emotion_network")
    if network and network.get("nodes"):
        with st.expander("🕸️ Emotion Co-Occurrence Network", expanded=False):
            nodes = network["nodes"]
            edges = network.get("edges", [])

            # Emotion frequency chart
            emo_df = pd.DataFrame(nodes).sort_values("count", ascending=True)
            fig = px.bar(
                emo_df, x="count", y="id",
                orientation="h",
                color_discrete_sequence=[_accent()],
            )
            fig = _plotly_layout(fig, "Emotion Frequency")
            fig.update_layout(showlegend=False, yaxis_autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

            # Co-occurrence table
            if edges:
                st.markdown("**Emotions that often appear together:**")
                edge_data = [
                    {"Emotion A": e["source"], "Emotion B": e["target"], "Times": e["weight"]}
                    for e in edges[:10]
                ]
                st.dataframe(pd.DataFrame(edge_data), use_container_width=True)

    # ── 9. Trigger Radar ─────────────────────────────────────────
    triggers = la.get("triggers", [])
    if triggers:
        st.markdown("### 🎯 Potential Triggers")
        st.caption(
            "Topics that tend to co-occur with lower mood. "
            "Correlation, not causation — just patterns to notice."
        )
        # triggers is a list of (topic, avg_sentiment, count)
        trig_df = pd.DataFrame(
            triggers[:10],
            columns=["Topic", "Avg Sentiment", "Count"],
        )
        trig_df = trig_df.sort_values("Avg Sentiment", ascending=True)
        fig = px.bar(
            trig_df, x="Avg Sentiment", y="Topic",
            orientation="h",
            color="Avg Sentiment",
            color_continuous_scale="RdYlGn",
        )
        fig = _plotly_layout(fig, "")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # ── 10. Day-of-Week Patterns ─────────────────────────────────
    dow = la.get("day_of_week_patterns", {})
    if dow and len(dow) >= 2:
        st.markdown("### 📅 Day-of-Week Mood")
        day_order = [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday",
        ]
        dow_df = pd.DataFrame([
            {"Day": d, "Avg Sentiment": v}
            for d, v in dow.items()
        ])
        dow_df["Day"] = pd.Categorical(
            dow_df["Day"], categories=day_order, ordered=True,
        )
        dow_df = dow_df.sort_values("Day").dropna(subset=["Day"])

        fig = px.bar(
            dow_df, x="Day", y="Avg Sentiment",
            color="Avg Sentiment",
            color_continuous_scale="RdYlGn",
            range_color=[-1, 1],
        )
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.4)
        fig = _plotly_layout(fig, "")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        best = max(dow.items(), key=lambda x: x[1])
        worst = min(dow.items(), key=lambda x: x[1])
        st.caption(
            f"✨ Best: **{best[0]}** ({best[1]:+.2f}) · "
            f"⚠️ Hardest: **{worst[0]}** ({worst[1]:+.2f})"
        )

    # ── 11. Topic-Sentiment Correlation ──────────────────────────
    ts_data = la.get("topic_sentiment", {})
    if ts_data:
        with st.expander("📊 Topic–Mood Correlations", expanded=False):
            ts_df = pd.DataFrame([
                {
                    "Topic": topic,
                    "Avg Sentiment": info["avg_sentiment"],
                    "Trend": info["trend"],
                    "Count": info["count"],
                }
                for topic, info in ts_data.items()
            ]).sort_values("Avg Sentiment", ascending=True)

            fig = px.bar(
                ts_df, x="Avg Sentiment", y="Topic",
                orientation="h",
                color="Trend",
                color_discrete_map={
                    "positive": "#52D68A",
                    "negative": "#FF7675",
                    "neutral": "#A29BFE",
                },
            )
            fig = _plotly_layout(fig, "")
            st.plotly_chart(fig, use_container_width=True)

    # ── 12. Weekly Heatmap ───────────────────────────────────────
    heatmap = la.get("weekly_heatmap", [])
    if heatmap and len(heatmap) >= 3:
        with st.expander("🗓️ Weekly Mood Heatmap", expanded=False):
            hm_df = pd.DataFrame(heatmap)
            pivot = hm_df.pivot_table(
                values="avg_sentiment",
                index="hour",
                columns="day",
                aggfunc="mean",
            ).fillna(0)

            day_order = [
                "Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday",
            ]
            pivot = pivot.reindex(
                columns=[d for d in day_order if d in pivot.columns]
            )

            fig = px.imshow(
                pivot,
                color_continuous_scale="RdYlGn",
                range_color=[-1, 1],
                labels={"x": "Day", "y": "Hour", "color": "Sentiment"},
            )
            fig = _plotly_layout(fig, "")
            st.plotly_chart(fig, use_container_width=True)

    # ── 13. Collapsible charts: words, emotions, topics, people ──
    chart_row1, chart_row2 = st.columns(2)

    with chart_row1:
        # Emotion distribution
        emotions = la.get("emotions", {})
        if emotions:
            with st.expander("🎭 Emotion Distribution", expanded=False):
                emo_counts = {k: len(v) for k, v in emotions.items()}
                fig = px.pie(
                    names=list(emo_counts.keys()),
                    values=list(emo_counts.values()),
                    color_discrete_sequence=_pcolors(),
                    hole=0.4,
                )
                fig = _plotly_layout(fig, "")
                st.plotly_chart(fig, use_container_width=True)

        # Word frequency
        words = la.get("words", [])
        if words:
            with st.expander("🔤 Top Words", expanded=False):
                wdf = pd.DataFrame(words[:25], columns=["word", "count"])
                fig = px.bar(
                    wdf, x="count", y="word",
                    orientation="h",
                    color="count",
                    color_continuous_scale="Viridis",
                )
                fig = _plotly_layout(fig, "")
                fig.update_layout(showlegend=False, yaxis_autorange="reversed")
                st.plotly_chart(fig, use_container_width=True)

    with chart_row2:
        # Topics
        topics = la.get("topics", {})
        if topics:
            with st.expander("🏷️ Topics Breakdown", expanded=False):
                fig = px.bar(
                    x=list(topics.values()),
                    y=list(topics.keys()),
                    orientation="h",
                    color_discrete_sequence=_pcolors(),
                )
                fig = _plotly_layout(fig, "")
                st.plotly_chart(fig, use_container_width=True)

        # People
        people = la.get("people", [])
        if people:
            with st.expander("👥 People Mentioned", expanded=False):
                for name, cnt in people[:10]:
                    st.markdown(f"- **{name}** × {cnt}")

    # Save local analysis
    try:
        save_analysis(uid, "local", json.dumps(la, default=str))
    except Exception:
        pass

    st.markdown("---")

    # ═════════════════════════════════════════════════════════════
    #  AI DEEP ANALYSIS
    # ═════════════════════════════════════════════════════════════
    if run_ai:
        if not st.session_state.api_key:
            st.error("Gemini API key not found. Add it in ⚙️ Settings.")
            return

        # Consent check
        if not show_consent_notice(CONSENT_NOTICE_ANALYSIS):
            return

        with st.spinner("🧠 MindMirror is reading between the lines…"):
            profile = get_psyche_profile(uid)
            result = ai_analysis(
                target,
                st.session_state.api_key,
                st.session_state.model,
                la,
                psyche_profile=profile,
            )

        st.markdown("### 🤖 AI Deep Analysis Report")
        st.markdown(result)
        st.session_state.current_analysis = result
        save_analysis(uid, "ai", result)
        st.success("✅ Analysis saved to your history.")

        # ── Post-analysis AI actions ─────────────────────────────
        st.markdown("")
        pa1, pa2, pa3 = st.columns(3)

        with pa1:
            if st.button(
                "💡 Reflection Prompts",
                use_container_width=True,
                key="_an_prompts",
            ):
                with st.spinner("Crafting prompts…"):
                    prompts = ai_reflection_prompts(
                        all_entries,
                        st.session_state.api_key,
                        st.session_state.model,
                        goals=get_goals(uid),
                        psyche_profile=get_psyche_profile(uid),
                    )
                st.markdown("### 💡 Personalised Reflection Prompts")
                st.markdown(prompts)

        with pa2:
            if st.button(
                "🔮 Mood Forecast",
                use_container_width=True,
                key="_an_forecast",
            ):
                with st.spinner("Forecasting…"):
                    forecast = ai_mood_forecast(
                        all_entries,
                        la,
                        st.session_state.api_key,
                        st.session_state.model,
                    )
                st.markdown("### 🔮 Emotional Weather Forecast")
                st.markdown(forecast)

        with pa3:
            if distortions:
                if st.button(
                    "🌀 Distortion Deep-Dive",
                    use_container_width=True,
                    key="_an_distdive",
                ):
                    with st.spinner("Analysing thinking patterns…"):
                        dist_result = ai_distortion_analysis(
                            target,
                            distortions,
                            st.session_state.api_key,
                            st.session_state.model,
                        )
                    st.markdown("### 🌀 Cognitive Distortion Analysis")
                    st.markdown(dist_result)
            else:
                st.button(
                    "🌀 No distortions found",
                    use_container_width=True,
                    disabled=True,
                    key="_an_distdive_off",
                )

    # ── Community stat ───────────────────────────────────────────
    show_community_stat(all_entries)


# ═══════════════════════════════════════════════════════════════════
#  💬  AI CHAT PAGE
# ═══════════════════════════════════════════════════════════════════

def page_chat():
    st.markdown("# 💬 AI Insight Chat")
    st.markdown(
        "Talk with MindMirror about your patterns, feelings, "
        "and what's on your mind. Choose your therapeutic mode "
        "and adjust the empathy level in the sidebar."
    )
    st.markdown("---")

    uid = st.session_state.user_id

    # ── Gate checks ──────────────────────────────────────────────
    if not st.session_state.api_key:
        st.warning(
            "⚠️ Gemini API key not found. Add `GEMINI_API_KEY` "
            "to your Streamlit Secrets (see ⚙️ Settings)."
        )
        return

    if st.session_state.privacy_mode == "local_only":
        st.warning("🔒 AI Chat is disabled in **Local-only** mode.")
        st.caption("Change this in ⚙️ Settings → Privacy.")
        return

    if not st.session_state.consent_ai_processing:
        st.warning(
            "🔒 AI consent is revoked. Enable it in "
            "⚙️ Settings to use Chat."
        )
        return

    entries = get_entries(uid, limit=50)

    # ── Session Management ───────────────────────────────────────
    st.markdown("#### 💬 Chat Sessions")

    sessions = get_chat_sessions(uid)
    session_labels = (
        [s["session_label"] for s in sessions]
        if sessions
        else []
    )
    if "default" not in session_labels:
        session_labels.insert(0, "default")

    sess_c1, sess_c2 = st.columns([3, 1])

    with sess_c1:
        current_idx = (
            session_labels.index(st.session_state.chat_session)
            if st.session_state.chat_session in session_labels
            else 0
        )
        chosen_session = st.selectbox(
            "Active session:",
            session_labels,
            index=current_idx,
            key="_chat_sess_sel",
            label_visibility="collapsed",
        )
        if chosen_session != st.session_state.chat_session:
            st.session_state.chat_session = chosen_session
            st.rerun()

    with sess_c2:
        if st.button(
            "🗑️ Clear",
            key="_chat_clear",
            use_container_width=True,
        ):
            delete_chat_session(uid, st.session_state.chat_session)
            st.rerun()

    # ── Preset quick-start sessions ──────────────────────────────
    st.caption("Quick-start a new topic:")
    pre_cols = st.columns(5)
    presets = [
        "🌅 Morning Check-in",
        "🌙 Evening Reflection",
        "💭 Deep Dive",
        "🎯 Goal Setting",
        "💚 Mood Check",
    ]
    for i, label in enumerate(presets):
        with pre_cols[i]:
            if st.button(
                label,
                key=f"_chat_pre_{i}",
                use_container_width=True,
            ):
                st.session_state.chat_session = label
                st.rerun()

    # ── Custom session creator ───────────────────────────────────
    custom_c1, custom_c2 = st.columns([3, 1])
    with custom_c1:
        new_label = st.text_input(
            "Or name your own:",
            key="_chat_new_label",
            placeholder="e.g. Work stress deep-dive",
            label_visibility="collapsed",
        )
    with custom_c2:
        if st.button(
            "➕ Create",
            key="_chat_new_btn",
            use_container_width=True,
        ):
            if new_label.strip():
                st.session_state.chat_session = new_label.strip()
                st.rerun()

    st.markdown("---")

    # ── Mode & Empathy (inline, mirrors sidebar for visibility) ──
    mode_c1, mode_c2, mode_c3 = st.columns([2, 2, 1])

    mode_keys = list(CHAT_MODE_PROMPTS.keys())
    mode_labels = [CHAT_MODE_PROMPTS[k]["label"] for k in mode_keys]
    current_mode = st.session_state.therapeutic_mode
    current_mode_idx = (
        mode_keys.index(current_mode)
        if current_mode in mode_keys
        else 0
    )

    with mode_c1:
        sel_label = st.selectbox(
            "🎭 Mode:",
            mode_labels,
            index=current_mode_idx,
            key="_chat_mode_inline",
        )
        active_mode = mode_keys[mode_labels.index(sel_label)]
        if active_mode != st.session_state.therapeutic_mode:
            st.session_state.therapeutic_mode = active_mode

    with mode_c2:
        emp_int = max(1, min(10, int(st.session_state.empathy_level * 10)))
        new_emp = st.slider(
            "💗 Empathy:",
            1, 10, emp_int,
            key="_chat_emp_inline",
            help="1 = direct · 10 = deeply nurturing",
        )
        active_empathy = new_emp / 10.0
        if abs(active_empathy - st.session_state.empathy_level) > 0.05:
            st.session_state.empathy_level = active_empathy

    with mode_c3:
        want_summary = st.button(
            "📋 Summary",
            key="_chat_summary_btn",
            use_container_width=True,
        )

    # Mode description
    mode_descs = {
        "open": "Natural conversation with warm, perceptive responses.",
        "cbt": "Structured CBT: thought records, distortion spotting, evidence examination.",
        "validation": "Maximum empathy and validation — making you feel heard first.",
        "reflection": "Socratic questions guiding you to your own insights.",
        "homework": "Review goals and progress, set gentle next steps.",
    }
    st.caption(f"*{mode_descs.get(active_mode, '')}*")

    st.markdown("---")

    # ── Load & display chat history ──────────────────────────────
    db_msgs = get_chat_msgs(uid, st.session_state.chat_session)

    if not db_msgs:
        st.caption(
            f"📎 Session: **{st.session_state.chat_session}** · "
            f"Mode: **{sel_label}** · "
            "Start the conversation below."
        )
    else:
        for m in db_msgs:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

    # ── Session summary ──────────────────────────────────────────
    if want_summary and db_msgs:
        with st.spinner("Generating session summary…"):
            summary = generate_session_summary(
                db_msgs,
                st.session_state.api_key,
                st.session_state.model,
            )
        st.markdown("---")
        st.markdown("### 📋 Session Summary")
        st.markdown(summary)

        # Save summary as a message in the session
        save_chat_msg(
            uid,
            "assistant",
            f"**📋 Session Summary**\n\n{summary}",
            st.session_state.chat_session,
        )
        st.rerun()
    elif want_summary and not db_msgs:
        st.info("No messages to summarise yet.")

    # ── Chat input ───────────────────────────────────────────────
    if prompt := st.chat_input("Tell me what's on your mind…"):

        # ── Crisis detection ─────────────────────────────────────
        is_crisis = detect_crisis(prompt)
        if is_crisis:
            show_crisis_support(source="chat_input")
            log_crisis_event(
                uid,
                trigger_snippet=prompt[:120],
                notes=f"detected in chat session '{st.session_state.chat_session}'",
            )

        # Show user message
        with st.chat_message("user"):
            st.markdown(prompt)
        save_chat_msg(
            uid, "user", prompt,
            st.session_state.chat_session,
        )

        # Build history for context
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in db_msgs
        ]

        # Call AI
        with st.chat_message("assistant"):
            with st.spinner("Reflecting…"):
                reply = ai_chat(
                    prompt,
                    entries if entries else [],
                    history,
                    st.session_state.api_key,
                    st.session_state.model,
                    chat_mode=active_mode,
                    empathy_level=(
                        0.9 if is_crisis  # max empathy in crisis
                        else active_empathy
                    ),
                    psyche_profile=get_psyche_profile(uid),
                )
            st.markdown(reply)

        save_chat_msg(
            uid, "assistant", reply,
            st.session_state.chat_session,
        )

    # ── Context panel ────────────────────────────────────────────
    with st.expander("📊 Your Recent Context (visible to AI)", expanded=False):
        if entries:
            st.caption(
                f"The AI sees your last {min(len(entries), 10)} entries "
                "for personalised responses."
            )
            for e in entries[:5]:
                date = e.get("entry_date", "")[:16]
                sent = e.get("sentiment")
                preview = e.get("content", "")[:150].replace("\n", " ")
                sent_str = f" · sent: {sent:+.2f}" if sent is not None else ""
                st.caption(f"**[{date}]**{sent_str}")
                st.caption(f"*{preview}…*")
                st.markdown("")
        else:
            st.info(
                "No journal entries yet. Write some to give the AI "
                "richer context for your conversations."
            )

    # ── Proactive prompt when chat is empty ──────────────────────
    if not db_msgs and entries:
        st.markdown("")
        show_proactive_prompt_widget(entries)


# ──────────────────────────────────────────────────────────────────
# END OF CHUNK 7 — paste Chunk 8 directly below this line
# ──────────────────────────────────────────────────────────────────
# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — app.py  CHUNK 8 of 10  (v3 · Full Blueprint)  ║
# ║  📊 Enhanced Dashboard                                          ║
# ║     Welcome · Quick Stats · Mood/Energy Timeline · Forecast ·  ║
# ║     Emotional Fingerprint Radar · Growth Metrics Radar ·       ║
# ║     Goal Tracker · Mood Calendar · PHQ-9/GAD-7 Check-ins ·    ║
# ║     Narrative Summary · Community Stats                         ║
# ╚══════════════════════════════════════════════════════════════════╝


# ═══════════════════════════════════════════════════════════════════
#  PHQ-9 & GAD-7 DEFINITIONS
# ═══════════════════════════════════════════════════════════════════

PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself — or that you are a failure",
    "Trouble concentrating on things",
    "Moving or speaking slowly — or being fidgety and restless",
    "Thoughts that you would be better off dead, or of hurting yourself",
]

GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge",
    "Not being able to stop or control worrying",
    "Worrying too much about different things",
    "Trouble relaxing",
    "Being so restless that it's hard to sit still",
    "Becoming easily annoyed or irritable",
    "Feeling afraid, as if something awful might happen",
]

PHQ9_SEVERITY = [
    (0, 4, "Minimal", "🟢"),
    (5, 9, "Mild", "🟡"),
    (10, 14, "Moderate", "🟠"),
    (15, 19, "Moderately Severe", "🔴"),
    (20, 27, "Severe", "🔴"),
]

GAD7_SEVERITY = [
    (0, 4, "Minimal Anxiety", "🟢"),
    (5, 9, "Mild Anxiety", "🟡"),
    (10, 14, "Moderate Anxiety", "🟠"),
    (15, 21, "Severe Anxiety", "🔴"),
]

SCORE_OPTIONS = {
    0: "Not at all",
    1: "Several days",
    2: "More than half the days",
    3: "Nearly every day",
}


def _severity_label(total, scale):
    for low, high, label, icon in scale:
        if low <= total <= high:
            return f"{icon} {label} ({total})"
    return f"Score: {total}"


# ═══════════════════════════════════════════════════════════════════
#  📊  DASHBOARD PAGE
# ═══════════════════════════════════════════════════════════════════

def page_dashboard():
    uid = st.session_state.user_id
    entries = get_entries(uid, limit=200)

    # ─────────────────────────────────────────────────────────────
    #  1. WELCOME BANNER
    # ─────────────────────────────────────────────────────────────
    profile = st.session_state.get("psyche_profile", {})
    name = st.session_state.username
    hour = datetime.now().hour
    if hour < 12:
        greeting = f"Good morning, {name} ☀️"
    elif hour < 18:
        greeting = f"Good afternoon, {name} 🌤️"
    else:
        greeting = f"Good evening, {name} 🌙"

    st.markdown(f"# 📊 {greeting}")

    if not entries:
        st.info(
            "Your dashboard will come alive once you start journaling. "
            "Head to **📝 Journal** and write your first entry! ✨"
        )
        return

    # Celebrations
    goals = get_goals(uid)
    show_celebrations(entries, goals)

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────
    #  2. QUICK STATS ROW
    # ─────────────────────────────────────────────────────────────
    streak = _streak(entries)
    recent_sents = [
        e["sentiment"] for e in entries[:7]
        if e.get("sentiment") is not None
    ]
    avg_recent = sum(recent_sents) / len(recent_sents) if recent_sents else 0
    recent_energies = [
        e["energy_level"] for e in entries[:7]
        if e.get("energy_level") is not None
    ]
    avg_energy = (
        sum(recent_energies) / len(recent_energies)
        if recent_energies else 0
    )

    # Count unique emotions across recent entries
    all_emos = set()
    for e in entries[:20]:
        parsed = _safe_json_parse(e.get("emotions"))
        if isinstance(parsed, dict):
            all_emos.update(parsed.keys())
        elif isinstance(parsed, list):
            all_emos.update(parsed)

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("📝 Entries", len(entries))
    s2.metric("🔥 Streak", f"{streak}d")
    s3.metric(
        "😊 Avg Mood (7d)",
        f"{avg_recent:+.2f}",
        delta=(
            "up" if avg_recent > 0.1
            else ("down" if avg_recent < -0.1 else "flat")
        ),
    )
    s4.metric("⚡ Avg Energy (7d)", f"{avg_energy:.1f}/10")
    s5.metric("🎨 Emotions", len(all_emos))

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────
    #  3. MOOD & ENERGY TIMELINE  (+  FORECAST OVERLAY)
    # ─────────────────────────────────────────────────────────────
    st.markdown("### 📈 Mood & Energy Over Time")

    # Build dataframe from entries (chronological)
    timeline_data = []
    for e in reversed(entries):
        date = e.get("entry_date", "")[:10]
        sent = e.get("sentiment")
        energy = e.get("energy_level")
        if date and (sent is not None or energy is not None):
            row = {"date": date}
            if sent is not None:
                row["Sentiment"] = sent
            if energy is not None:
                # Normalise energy 1–10 to roughly −1 to +1 for overlay
                row["Energy (norm)"] = (energy - 5.5) / 4.5
            timeline_data.append(row)

    if timeline_data:
        tl_df = pd.DataFrame(timeline_data)

        fig = go.Figure()

        if "Sentiment" in tl_df.columns:
            fig.add_trace(go.Scatter(
                x=tl_df["date"],
                y=tl_df["Sentiment"],
                mode="lines+markers",
                name="Sentiment",
                line=dict(color=_accent(), width=3),
                marker=dict(size=7),
            ))

        if "Energy (norm)" in tl_df.columns:
            fig.add_trace(go.Scatter(
                x=tl_df["date"],
                y=tl_df["Energy (norm)"],
                mode="lines+markers",
                name="Energy",
                line=dict(
                    color=get_theme(st.session_state.theme)["accent_secondary"],
                    width=2,
                    dash="dot",
                ),
                marker=dict(size=5),
            ))

        # ── Simple linear forecast overlay (3 days) ──────────────
        if "Sentiment" in tl_df.columns and len(tl_df) >= 5:
            recent_scores = tl_df["Sentiment"].dropna().values[-14:]
            if len(recent_scores) >= 5:
                x = np.arange(len(recent_scores))
                A = np.vstack([x, np.ones(len(x))]).T
                try:
                    m_slope, c_intercept = np.linalg.lstsq(
                        A, recent_scores, rcond=None
                    )[0]
                    last_date_str = tl_df["date"].iloc[-1]
                    try:
                        last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
                    except ValueError:
                        last_date = datetime.now()

                    forecast_dates = [
                        (last_date + timedelta(days=d)).strftime("%Y-%m-%d")
                        for d in range(1, 4)
                    ]
                    forecast_vals = [
                        float(m_slope * (len(recent_scores) + d) + c_intercept)
                        for d in range(3)
                    ]
                    # Clamp to [-1, 1]
                    forecast_vals = [
                        max(-1.0, min(1.0, v)) for v in forecast_vals
                    ]

                    fig.add_trace(go.Scatter(
                        x=forecast_dates,
                        y=forecast_vals,
                        mode="lines+markers",
                        name="Forecast",
                        line=dict(
                            color="#FFD93D", width=2, dash="dash",
                        ),
                        marker=dict(
                            size=8, symbol="diamond",
                        ),
                    ))
                except (np.linalg.LinAlgError, ValueError):
                    pass

        fig.add_hline(
            y=0, line_dash="dash",
            line_color="gray", opacity=0.3,
        )
        fig = _plotly_layout(fig, "")
        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom",
                y=1.02, xanchor="right", x=1,
            ),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption(
            "Not enough mood/energy data yet. "
            "Use the sliders when journaling!"
        )

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────
    #  4. EMOTIONAL FINGERPRINT  (Radar Chart)
    # ─────────────────────────────────────────────────────────────
    st.markdown("### 🎭 Emotional Fingerprint")
    st.caption(
        "Your unique emotional profile based on recent entries. "
        "A wider shape means greater emotional diversity."
    )

    # Aggregate emotion counts
    emo_counts = {}
    for e in entries[:30]:
        parsed = _safe_json_parse(e.get("emotions"))
        if isinstance(parsed, dict):
            for k, v in parsed.items():
                emo_counts[k] = emo_counts.get(k, 0) + (v if isinstance(v, (int, float)) else 1)
        elif isinstance(parsed, list):
            for em in parsed:
                emo_counts[em] = emo_counts.get(em, 0) + 1

    if emo_counts and len(emo_counts) >= 3:
        # Take top 8 emotions for the radar
        top_emos = sorted(
            emo_counts.items(), key=lambda x: x[1], reverse=True
        )[:8]
        labels = [e[0].title() for e in top_emos]
        values = [e[1] for e in top_emos]
        # Normalise to 0–1
        max_val = max(values) if values else 1
        norm_values = [v / max_val for v in values]
        # Close the polygon
        labels_closed = labels + [labels[0]]
        values_closed = norm_values + [norm_values[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=labels_closed,
            fill="toself",
            fillcolor=f"{_accent()}33",
            line=dict(color=_accent(), width=2),
            name="Your Fingerprint",
        ))
        fig = _plotly_layout(fig, "")
        fig.update_layout(
            polar=dict(
                bgcolor=get_theme(st.session_state.theme)["card_bg"],
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor=get_theme(st.session_state.theme)["border"],
                    tickfont=dict(size=10),
                ),
                angularaxis=dict(
                    gridcolor=get_theme(st.session_state.theme)["border"],
                    tickfont=dict(
                        color=get_theme(st.session_state.theme)["text"],
                    ),
                ),
            ),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    elif emo_counts:
        st.caption(
            f"Detected {len(emo_counts)} emotion(s) so far. "
            "Write a few more entries for the full fingerprint."
        )
    else:
        st.caption("No emotions detected yet. Keep journaling!")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────
    #  5. GROWTH METRICS RADAR
    # ─────────────────────────────────────────────────────────────
    st.markdown("### 🌱 Growth Radar")

    # Compute growth metrics from entries
    chrono_entries = list(reversed(entries))
    gm = calculate_growth_metrics(chrono_entries)

    if gm:
        reg = gm.get("emotional_regulation")
        res = gm.get("resilience")
        awa = gm.get("self_awareness")

        # Cache to database
        if reg is not None and res is not None and awa is not None:
            save_growth_metrics(uid, res, awa, reg)

        gm_labels = [
            "Emotional\nRegulation",
            "Resilience",
            "Self-Awareness",
        ]
        gm_values = [
            (reg or 0) / 100,
            (res or 0) / 100,
            (awa or 0) / 100,
        ]
        gm_closed_l = gm_labels + [gm_labels[0]]
        gm_closed_v = gm_values + [gm_values[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=gm_closed_v,
            theta=gm_closed_l,
            fill="toself",
            fillcolor="#7BDFF233",
            line=dict(color="#7BDFF2", width=2),
            name="Growth",
        ))
        fig = _plotly_layout(fig, "")
        fig.update_layout(
            polar=dict(
                bgcolor=get_theme(st.session_state.theme)["card_bg"],
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor=get_theme(st.session_state.theme)["border"],
                ),
                angularaxis=dict(
                    gridcolor=get_theme(st.session_state.theme)["border"],
                    tickfont=dict(
                        color=get_theme(st.session_state.theme)["text"],
                    ),
                ),
            ),
            showlegend=False,
        )

        radar_col, score_col = st.columns([2, 1])
        with radar_col:
            st.plotly_chart(fig, use_container_width=True)
        with score_col:
            st.markdown(
                f'<div class="mm-card">'
                f'<h4>🧘 Regulation</h4>'
                f'<p style="font-size:1.5em;font-weight:700;">'
                f'{reg:.0f}/100</p></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="mm-card">'
                f'<h4>💪 Resilience</h4>'
                f'<p style="font-size:1.5em;font-weight:700;">'
                f'{res:.0f}/100</p></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="mm-card">'
                f'<h4>🔍 Awareness</h4>'
                f'<p style="font-size:1.5em;font-weight:700;">'
                f'{awa:.0f}/100</p></div>',
                unsafe_allow_html=True,
            )
    else:
        st.caption(
            "Need more journal entries to compute growth metrics. "
            "Keep writing — every entry teaches MindMirror about your patterns."
        )

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────
    #  6. GOAL TRACKER
    # ─────────────────────────────────────────────────────────────
    st.markdown("### 🎯 Goals")

    tab_active, tab_completed, tab_new = st.tabs([
        "Active", "Completed", "➕ New Goal",
    ])

    with tab_active:
        active_goals = get_goals(uid, status="active")
        if not active_goals:
            st.caption(
                "No active goals. Set one in the **➕ New Goal** tab!"
            )
        else:
            for g in active_goals:
                gid = g["id"]
                prog = g.get("progress", 0)
                with st.expander(
                    f"🎯 {g['title']}  —  {prog:.0f}%",
                    expanded=False,
                ):
                    # Progress bar
                    st.progress(min(1.0, max(0.0, prog / 100.0)))

                    # Update controls
                    up_c1, up_c2, up_c3 = st.columns([2, 1, 1])
                    with up_c1:
                        new_prog = st.slider(
                            "Update progress:",
                            0, 100, int(prog),
                            key=f"_goal_prog_{gid}",
                        )
                    with up_c2:
                        if st.button(
                            "💾 Save",
                            key=f"_goal_save_{gid}",
                        ):
                            status = (
                                "completed" if new_prog >= 100
                                else "active"
                            )
                            update_goal_progress(gid, new_prog, status)
                            if new_prog >= 100:
                                st.success("🎉 Goal completed!")
                                st.balloons()
                            else:
                                st.success("✅ Updated!")
                            st.rerun()
                    with up_c3:
                        if st.button(
                            "⏸️ Pause",
                            key=f"_goal_pause_{gid}",
                        ):
                            update_goal_progress(
                                gid, prog, "paused"
                            )
                            st.rerun()

                    # Metadata
                    st.caption(
                        f"Created: {g.get('created_at', '?')[:10]} · "
                        f"Updated: {g.get('updated_at', '?')[:10]}"
                    )
                    if g.get("target_metric"):
                        st.caption(
                            f"Target metric: {g['target_metric']} "
                            f"→ {g.get('target_value', '?')}"
                        )

    with tab_completed:
        done_goals = get_goals(uid, status="completed")
        if not done_goals:
            st.caption("No completed goals yet. Keep going! 💪")
        else:
            for g in done_goals:
                st.markdown(
                    f"✅ ~~{g['title']}~~ — completed "
                    f"{g.get('updated_at', '')[:10]}"
                )

    with tab_new:
        st.markdown("**Set a new emotional or behavioral goal:**")

        ng_title = st.text_input(
            "Goal title:",
            key="_goal_new_title",
            placeholder="e.g. Practice gratitude 3× per week",
        )

        ng_c1, ng_c2 = st.columns(2)
        with ng_c1:
            ng_metric = st.selectbox(
                "Target metric (optional):",
                [
                    "None",
                    "mood", "energy", "resilience",
                    "regulation", "awareness", "journaling_days",
                ],
                key="_goal_new_metric",
            )
        with ng_c2:
            ng_value = st.number_input(
                "Target value:",
                min_value=0.0,
                max_value=100.0,
                value=50.0,
                key="_goal_new_value",
            )

        if st.button(
            "🎯 Create Goal",
            type="primary",
            key="_goal_create",
        ):
            if ng_title.strip():
                save_goal(
                    uid,
                    ng_title.strip(),
                    target_metric=(
                        ng_metric if ng_metric != "None" else None
                    ),
                    target_value=(
                        ng_value if ng_metric != "None" else None
                    ),
                )
                st.success(f"🎯 Goal created: *{ng_title.strip()}*")
                st.rerun()
            else:
                st.warning("Give your goal a title.")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────
    #  7. MOOD CALENDAR
    # ─────────────────────────────────────────────────────────────
    st.markdown("### 📅 Mood Calendar")

    # Build daily sentiment map
    daily_mood = {}
    for e in entries:
        date = e.get("entry_date", "")[:10]
        sent = e.get("sentiment")
        if date and sent is not None:
            if date not in daily_mood:
                daily_mood[date] = []
            daily_mood[date].append(sent)

    # Average per day
    daily_avg = {
        d: sum(vals) / len(vals)
        for d, vals in daily_mood.items()
    }

    if daily_avg and len(daily_avg) >= 3:
        cal_df = pd.DataFrame([
            {"date": d, "sentiment": v}
            for d, v in sorted(daily_avg.items())
        ])
        cal_df["date"] = pd.to_datetime(cal_df["date"])
        cal_df["week"] = cal_df["date"].dt.isocalendar().week.astype(int)
        cal_df["weekday"] = cal_df["date"].dt.day_name()

        # Pivot for heatmap
        day_order = [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday",
        ]
        cal_pivot = cal_df.pivot_table(
            values="sentiment",
            index="weekday",
            columns="week",
            aggfunc="mean",
        )
        cal_pivot = cal_pivot.reindex(
            [d for d in day_order if d in cal_pivot.index]
        )

        fig = px.imshow(
            cal_pivot,
            color_continuous_scale="RdYlGn",
            range_color=[-1, 1],
            labels={"x": "Week #", "y": "Day", "color": "Mood"},
            aspect="auto",
        )
        fig = _plotly_layout(fig, "")
        fig.update_layout(
            xaxis_title="Week Number",
            yaxis_title="",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption(
            "Journal for a few more days to see your mood calendar."
        )

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────
    #  8. PHQ-9 / GAD-7 CHECK-INS
    # ─────────────────────────────────────────────────────────────
    st.markdown("### 🩺 Structured Check-Ins")
    st.caption(
        "These are standard screening tools used worldwide. "
        "They are **not** diagnostic — use them to track trends "
        "and share with a professional if needed."
    )

    checkin_tab1, checkin_tab2, checkin_tab3 = st.tabs([
        "PHQ-9 (Depression)",
        "GAD-7 (Anxiety)",
        "📊 Check-In History",
    ])

    with checkin_tab1:
        st.markdown(
            "**PHQ-9 Patient Health Questionnaire**\n\n"
            "*Over the last 2 weeks, how often have you been "
            "bothered by the following?*"
        )

        phq_scores = []
        for i, q in enumerate(PHQ9_QUESTIONS):
            # Special handling for question 9 (self-harm)
            if i == 8:
                st.markdown("---")
                st.caption(
                    "⚠️ This question asks about sensitive thoughts. "
                    "Answer honestly — your privacy is protected."
                )

            score = st.radio(
                f"**{i + 1}.** {q}",
                options=list(SCORE_OPTIONS.keys()),
                format_func=lambda x: SCORE_OPTIONS[x],
                horizontal=True,
                key=f"_phq_{i}",
            )
            phq_scores.append(score)

        if st.button(
            "📊 Score PHQ-9",
            type="primary",
            key="_phq_submit",
        ):
            total = sum(phq_scores)
            label = _severity_label(total, PHQ9_SEVERITY)

            st.markdown(f"### Result: {label}")
            st.progress(min(1.0, total / 27.0))

            # Crisis check on question 9
            if phq_scores[8] >= 2:
                st.warning(
                    "Your response to question 9 suggests you may "
                    "be experiencing difficult thoughts. Please "
                    "reach out to someone who can help."
                )
                show_crisis_support(source="phq9_q9")

            save_mood_checkin(uid, "phq9", phq_scores, total)
            st.success("✅ Check-in saved.")

    with checkin_tab2:
        st.markdown(
            "**GAD-7 Generalized Anxiety Disorder Scale**\n\n"
            "*Over the last 2 weeks, how often have you been "
            "bothered by the following?*"
        )

        gad_scores = []
        for i, q in enumerate(GAD7_QUESTIONS):
            score = st.radio(
                f"**{i + 1}.** {q}",
                options=list(SCORE_OPTIONS.keys()),
                format_func=lambda x: SCORE_OPTIONS[x],
                horizontal=True,
                key=f"_gad_{i}",
            )
            gad_scores.append(score)

        if st.button(
            "📊 Score GAD-7",
            type="primary",
            key="_gad_submit",
        ):
            total = sum(gad_scores)
            label = _severity_label(total, GAD7_SEVERITY)

            st.markdown(f"### Result: {label}")
            st.progress(min(1.0, total / 21.0))

            save_mood_checkin(uid, "gad7", gad_scores, total)
            st.success("✅ Check-in saved.")

    with checkin_tab3:
        checkins = get_mood_checkins(uid, limit=30)
        if not checkins:
            st.caption("No check-ins recorded yet.")
        else:
            # Separate by type
            phq_history = [
                c for c in checkins if c["checkin_type"] == "phq9"
            ]
            gad_history = [
                c for c in checkins if c["checkin_type"] == "gad7"
            ]
            pulse_history = [
                c for c in checkins if c["checkin_type"] == "quick_pulse"
            ]

            if phq_history:
                st.markdown("**PHQ-9 History:**")
                phq_df = pd.DataFrame([
                    {
                        "Date": c["created_at"][:16],
                        "Score": c["total_score"],
                    }
                    for c in reversed(phq_history)
                ])
                fig = px.line(
                    phq_df, x="Date", y="Score",
                    markers=True,
                    color_discrete_sequence=["#FF7675"],
                )
                fig = _plotly_layout(fig, "PHQ-9 Over Time")
                # Add severity bands
                fig.add_hrect(y0=0, y1=4, fillcolor="#2ECC71", opacity=0.1)
                fig.add_hrect(y0=5, y1=9, fillcolor="#F1C40F", opacity=0.1)
                fig.add_hrect(y0=10, y1=14, fillcolor="#E67E22", opacity=0.1)
                fig.add_hrect(y0=15, y1=27, fillcolor="#E74C3C", opacity=0.1)
                st.plotly_chart(fig, use_container_width=True)

            if gad_history:
                st.markdown("**GAD-7 History:**")
                gad_df = pd.DataFrame([
                    {
                        "Date": c["created_at"][:16],
                        "Score": c["total_score"],
                    }
                    for c in reversed(gad_history)
                ])
                fig = px.line(
                    gad_df, x="Date", y="Score",
                    markers=True,
                    color_discrete_sequence=["#A29BFE"],
                )
                fig = _plotly_layout(fig, "GAD-7 Over Time")
                fig.add_hrect(y0=0, y1=4, fillcolor="#2ECC71", opacity=0.1)
                fig.add_hrect(y0=5, y1=9, fillcolor="#F1C40F", opacity=0.1)
                fig.add_hrect(y0=10, y1=14, fillcolor="#E67E22", opacity=0.1)
                fig.add_hrect(y0=15, y1=21, fillcolor="#E74C3C", opacity=0.1)
                st.plotly_chart(fig, use_container_width=True)

            if pulse_history:
                st.markdown("**Quick Pulse History:**")
                for p in pulse_history[:5]:
                    scores = p.get("scores", [])
                    if len(scores) >= 3:
                        st.caption(
                            f"📅 {p['created_at'][:16]} — "
                            f"Interest: {scores[0]}/3 · "
                            f"Feeling down: {scores[1]}/3 · "
                            f"Energy: {scores[2]}/10"
                        )

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────
    #  9. NARRATIVE SUMMARY  (AI)
    # ─────────────────────────────────────────────────────────────
    st.markdown("### 📖 Your Story")
    st.caption(
        "An AI-generated narrative of your emotional journey — "
        "a compassionate letter from MindMirror to you."
    )

    narr_c1, narr_c2 = st.columns(2)
    with narr_c1:
        narr_period = st.selectbox(
            "Period:",
            ["week", "month"],
            key="_narr_period",
            label_visibility="collapsed",
        )
    with narr_c2:
        can_narr = bool(
            st.session_state.api_key
            and st.session_state.privacy_mode != "local_only"
            and st.session_state.consent_ai_processing
        )
        gen_narr = st.button(
            "📖 Generate Narrative",
            type="primary",
            disabled=not can_narr,
            key="_narr_gen",
        )

    if gen_narr:
        if not show_consent_notice(CONSENT_NOTICE_ANALYSIS):
            pass
        else:
            # Filter entries by period
            now = datetime.now()
            if narr_period == "week":
                cutoff = now - timedelta(days=7)
            else:
                cutoff = now - timedelta(days=30)

            period_entries = []
            for e in entries:
                try:
                    edate = datetime.strptime(
                        e["entry_date"][:10], "%Y-%m-%d"
                    )
                    if edate >= cutoff:
                        period_entries.append(e)
                except ValueError:
                    continue

            if len(period_entries) < 2:
                st.warning(
                    f"Not enough entries in the past {narr_period}. "
                    f"Found {len(period_entries)} — need at least 2."
                )
            else:
                chrono = list(reversed(period_entries))
                la = local_analysis(chrono)

                with st.spinner(
                    f"✍️ Writing your {narr_period}ly story…"
                ):
                    narrative = generate_narrative_summary(
                        chrono,
                        st.session_state.api_key,
                        st.session_state.model,
                        local_data=la,
                        period=narr_period,
                    )

                st.markdown(
                    f'<div class="mm-card">'
                    f'<h4>📖 Your {narr_period.title()} in Review</h4>'
                    f'{narrative}</div>',
                    unsafe_allow_html=True,
                )

                save_analysis(
                    uid,
                    f"narrative_{narr_period}",
                    narrative,
                )

    # ── Saved narrative display ──────────────────────────────────
    recent_analyses = get_analyses(uid, limit=5)
    narrative_analyses = [
        a for a in recent_analyses
        if a.get("analysis_type", "").startswith("narrative_")
    ]
    if narrative_analyses and not gen_narr:
        latest = narrative_analyses[0]
        period_type = latest["analysis_type"].replace("narrative_", "")
        with st.expander(
            f"📖 Latest {period_type.title()} Narrative "
            f"({latest['created_at'][:10]})",
            expanded=False,
        ):
            st.markdown(latest["result"])

    st.markdown("---")

    # ─────────────────────────────────────────────────────────────
    #  10. COMMUNITY STAT + PROACTIVE PROMPT
    # ─────────────────────────────────────────────────────────────
    stat_col, prompt_col = st.columns(2)

    with stat_col:
        show_community_stat(entries)

    with prompt_col:
        show_proactive_prompt_widget(entries)


# ──────────────────────────────────────────────────────────────────
# END OF CHUNK 8 — paste Chunk 9 directly below this line
# ──────────────────────────────────────────────────────────────────
# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — app.py  CHUNK 9 of 10  (v3 · Full Blueprint)  ║
# ║  🧘 Skills & Growth Page                                        ║
# ║     4 Skill Module Categories · Interactive Exercises ·        ║
# ║     4 Reflection Journeys · Journey Progress · Quick Tools     ║
# ║  📂 History Page                                                 ║
# ║     Saved Analyses · Chat Session Browser · Full Data Export   ║
# ╚══════════════════════════════════════════════════════════════════╝


# ═══════════════════════════════════════════════════════════════════
#  🧘  SKILLS & GROWTH PAGE
# ═══════════════════════════════════════════════════════════════════

def page_skills():
    st.markdown("# 🧘 Skills & Growth")
    st.markdown(
        "Evidence-based exercises, guided reflection journeys, "
        "and quick grounding tools — all in one place."
    )
    st.markdown("---")

    uid = st.session_state.user_id

    tab_modules, tab_journeys, tab_quick = st.tabs([
        "📚 Skill Modules",
        "🗺️ Reflection Journeys",
        "⚡ Quick Tools",
    ])

    # ═════════════════════════════════════════════════════════════
    #  TAB 1: SKILL MODULES
    # ═════════════════════════════════════════════════════════════
    with tab_modules:
        st.markdown(
            "Browse evidence-based skills from CBT, DBT, ACT, "
            "and self-compassion traditions. Each includes an "
            "interactive exercise you can try right now."
        )
        st.markdown("")

        # Category selector
        cat_keys = list(SKILL_MODULES.keys())
        cat_titles = [SKILL_MODULES[k]["title"] for k in cat_keys]

        cat_cols = st.columns(len(cat_keys))
        current_cat = st.session_state.get("_skill_category", cat_keys[0])

        for i, key in enumerate(cat_keys):
            with cat_cols[i]:
                btn_type = (
                    "primary" if current_cat == key else "secondary"
                )
                if st.button(
                    SKILL_MODULES[key]["title"],
                    key=f"_skill_cat_{key}",
                    use_container_width=True,
                    type=btn_type,
                ):
                    st.session_state._skill_category = key
                    st.rerun()

        st.markdown("---")

        # Display skills in selected category
        cat_data = SKILL_MODULES.get(current_cat)
        if cat_data:
            skills = cat_data.get("skills", [])

            for skill in skills:
                sid = skill["id"]
                completed_key = f"_skill_done_{sid}"

                # Check if completed this session
                is_done = st.session_state.get(completed_key, False)
                done_badge = " ✅" if is_done else ""

                with st.expander(
                    f"**{skill['name']}**  ·  "
                    f"⏱️ {skill['duration']}{done_badge}",
                    expanded=False,
                ):
                    st.markdown(skill["description"])
                    st.markdown("---")
                    st.markdown("#### 🎯 Try It Now")
                    st.markdown(skill["exercise"])

                    st.markdown("")

                    ex_c1, ex_c2 = st.columns([1, 1])

                    with ex_c1:
                        # Reflection text area
                        reflection = st.text_area(
                            "How did that feel? (optional)",
                            height=80,
                            key=f"_skill_ref_{sid}",
                            placeholder=(
                                "Jot down what you noticed…"
                            ),
                        )

                    with ex_c2:
                        st.markdown("")
                        st.markdown("")
                        if st.button(
                            "✅ Mark Complete",
                            key=f"_skill_complete_{sid}",
                            use_container_width=True,
                            type="primary",
                        ):
                            st.session_state[completed_key] = True

                            # Save reflection as journal entry if provided
                            if reflection.strip():
                                dt_str = datetime.now().strftime(
                                    "%Y-%m-%d %H:%M"
                                )
                                content = (
                                    f"**Skill Exercise: {skill['name']}**\n\n"
                                    f"Category: {cat_data['title']}\n\n"
                                    f"Reflection: {reflection.strip()}"
                                )
                                sent = sentiment_score(content)
                                save_entry(
                                    user_id=uid,
                                    content=content,
                                    entry_date=dt_str,
                                    sentiment=sent,
                                    tags=[
                                        "skill_exercise",
                                        current_cat,
                                        skill["name"].lower().replace(" ", "_"),
                                    ],
                                )

                            st.success(
                                f"🎉 Completed **{skill['name']}**!"
                            )
                            st.rerun()

            # Session summary
            completed_count = sum(
                1 for s in skills
                if st.session_state.get(f"_skill_done_{s['id']}", False)
            )
            if completed_count > 0:
                st.markdown("")
                st.markdown(
                    f'<div class="mm-celebration">'
                    f'🌟 You\'ve completed {completed_count} of '
                    f'{len(skills)} exercises in '
                    f'{cat_data["title"]} today!</div>',
                    unsafe_allow_html=True,
                )

    # ═════════════════════════════════════════════════════════════
    #  TAB 2: REFLECTION JOURNEYS
    # ═════════════════════════════════════════════════════════════
    with tab_journeys:
        st.markdown(
            "Multi-day guided reflection series for specific "
            "life challenges. Each journey saves your writing "
            "as journal entries so you can track your progress."
        )
        st.markdown("")

        # Journey selector
        journey_keys = list(REFLECTION_JOURNEYS.keys())
        active_journey = st.session_state.get(
            "_active_journey", None
        )

        if active_journey is None:
            # ── Journey selection grid ───────────────────────────
            st.markdown("### Choose a Journey")

            jgrid = st.columns(2)
            for i, jkey in enumerate(journey_keys):
                jdata = REFLECTION_JOURNEYS[jkey]
                col = jgrid[i % 2]
                with col:
                    st.markdown(
                        f'<div class="mm-card">'
                        f'<h4>{jdata["title"]}</h4>'
                        f'<p>{jdata["description"]}</p>'
                        f'<p style="font-size:0.8em;'
                        f'color:var(--mm-text-secondary);">'
                        f'{len(jdata["days"])} days</p>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        f"Start {jdata['title']}",
                        key=f"_journey_start_{jkey}",
                        use_container_width=True,
                        type="primary",
                    ):
                        st.session_state._active_journey = jkey
                        st.session_state._journey_day = 1
                        st.rerun()

            # ── Previously completed entries ─────────────────────
            journey_entries = get_entries(uid, limit=200)
            journey_tagged = [
                e for e in journey_entries
                if any(
                    "journey:" in t
                    for t in (_safe_json_parse(e.get("tags")) or [])
                )
            ]
            if journey_tagged:
                with st.expander(
                    f"📖 Past Journey Entries ({len(journey_tagged)})",
                    expanded=False,
                ):
                    for e in journey_tagged[:10]:
                        tags = _safe_json_parse(e.get("tags")) or []
                        journey_tag = next(
                            (t for t in tags if t.startswith("journey:")),
                            "unknown",
                        )
                        date = e.get("entry_date", "")[:10]
                        preview = e.get("content", "")[:120]
                        st.caption(
                            f"**[{date}]** `{journey_tag}` — {preview}…"
                        )

        else:
            # ── Active journey: show current day ─────────────────
            jdata = REFLECTION_JOURNEYS[active_journey]
            current_day = st.session_state.get("_journey_day", 1)
            total_days = len(jdata["days"])

            st.markdown(f"### {jdata['title']}")
            st.progress((current_day - 1) / total_days)
            st.caption(f"Day {current_day} of {total_days}")

            # Day data
            if current_day <= total_days:
                day_data = jdata["days"][current_day - 1]

                st.markdown(f"## Day {day_data['day']}: {day_data['title']}")
                st.markdown("")

                # Prompt
                st.markdown(
                    f'<div class="mm-card">'
                    f'<h4>📝 Your Prompt</h4>'
                    f'<p style="font-size:1.1em;line-height:1.6;">'
                    f'{day_data["prompt"]}</p></div>',
                    unsafe_allow_html=True,
                )

                st.markdown("")

                # Writing area
                response = st.text_area(
                    "Your reflection:",
                    height=200,
                    key=f"_journey_resp_{active_journey}_{current_day}",
                    placeholder="Take your time. There's no wrong answer.",
                )

                st.markdown("")

                # Buttons
                btn_c1, btn_c2, btn_c3 = st.columns([2, 1, 1])

                with btn_c1:
                    if st.button(
                        "💾 Save & Continue →",
                        type="primary",
                        key="_journey_save",
                        use_container_width=True,
                    ):
                        if not response.strip():
                            st.warning("Write something before continuing.")
                        else:
                            # Save as journal entry
                            dt_str = datetime.now().strftime(
                                "%Y-%m-%d %H:%M"
                            )
                            content = (
                                f"**{jdata['title']} — "
                                f"Day {current_day}: {day_data['title']}**"
                                f"\n\n"
                                f"*Prompt: {day_data['prompt']}*"
                                f"\n\n"
                                f"{response.strip()}"
                            )
                            sent = sentiment_score(content)
                            emos = detect_emotions(content)

                            save_entry(
                                user_id=uid,
                                content=content,
                                entry_date=dt_str,
                                sentiment=sent,
                                emotions=emos if emos else None,
                                tags=[
                                    f"journey:{active_journey}",
                                    f"day:{current_day}",
                                    day_data["title"].lower().replace(
                                        " ", "_"
                                    ),
                                ],
                            )

                            # Show insight
                            st.success(
                                f"✅ Day {current_day} saved!"
                            )
                            st.info(
                                f"💡 *{day_data.get('insight', '')}*"
                            )

                            # Advance or complete
                            if current_day >= total_days:
                                st.balloons()
                                st.markdown(
                                    f'<div class="mm-celebration">'
                                    f'🎉 You completed '
                                    f'**{jdata["title"]}**! '
                                    f'All {total_days} days are saved '
                                    f'in your journal.</div>',
                                    unsafe_allow_html=True,
                                )
                                st.session_state._active_journey = None
                                st.session_state.pop(
                                    "_journey_day", None
                                )
                            else:
                                st.session_state._journey_day = (
                                    current_day + 1
                                )
                            st.rerun()

                with btn_c2:
                    if current_day > 1:
                        if st.button(
                            "← Previous",
                            key="_journey_back",
                            use_container_width=True,
                        ):
                            st.session_state._journey_day = (
                                current_day - 1
                            )
                            st.rerun()

                with btn_c3:
                    if st.button(
                        "❌ Exit Journey",
                        key="_journey_exit",
                        use_container_width=True,
                    ):
                        st.session_state._active_journey = None
                        st.session_state.pop("_journey_day", None)
                        st.rerun()

            else:
                # Journey complete
                st.success(
                    f"🎉 You've completed all {total_days} days "
                    f"of **{jdata['title']}**!"
                )
                if st.button("← Back to Journeys"):
                    st.session_state._active_journey = None
                    st.session_state.pop("_journey_day", None)
                    st.rerun()

    # ═════════════════════════════════════════════════════════════
    #  TAB 3: QUICK TOOLS
    # ═════════════════════════════════════════════════════════════
    with tab_quick:
        st.markdown(
            "Grounding and regulation tools you can use anytime. "
            "No setup, no commitment — just immediate support."
        )
        st.markdown("")

        # ── Grounding exercises grid ─────────────────────────────
        st.markdown("### 🧘 Grounding Exercises")

        ge_cols = st.columns(2)
        for i, ex in enumerate(GROUNDING_EXERCISES):
            col = ge_cols[i % 2]
            with col:
                with st.expander(
                    f"🌿 {ex['name']}",
                    expanded=False,
                ):
                    st.markdown(ex["instruction"])
                    st.markdown("")
                    if st.button(
                        "✅ Done",
                        key=f"_ground_done_{i}",
                    ):
                        st.success("Great job! 🌟")

        st.markdown("---")

        # ── Quick emotional check-in ─────────────────────────────
        st.markdown("### 🌡️ Quick Emotional Check-In")
        st.caption(
            "A rapid self-assessment. Takes 30 seconds."
        )

        qe_c1, qe_c2 = st.columns(2)

        with qe_c1:
            qe_feeling = st.selectbox(
                "Right now I feel:",
                [
                    "😊 Good / Content",
                    "😐 Neutral / Meh",
                    "😰 Anxious / Worried",
                    "😢 Sad / Down",
                    "😠 Frustrated / Angry",
                    "😴 Tired / Drained",
                    "🤯 Overwhelmed",
                    "🥰 Grateful / Warm",
                    "🌟 Energized / Excited",
                ],
                key="_quick_feeling",
            )

        with qe_c2:
            qe_intensity = st.slider(
                "Intensity:",
                1, 10, 5,
                key="_quick_intensity",
                help="1 = barely noticeable · 10 = very intense",
            )

        qe_note = st.text_input(
            "One sentence about why (optional):",
            key="_quick_note",
            placeholder="e.g. Had a tough meeting…",
        )

        if st.button(
            "💾 Log Check-In",
            key="_quick_log",
            type="primary",
        ):
            # Parse feeling to sentiment
            feeling_map = {
                "😊": 0.6, "😐": 0.0, "😰": -0.4,
                "😢": -0.5, "😠": -0.4, "😴": -0.2,
                "🤯": -0.6, "🥰": 0.7, "🌟": 0.8,
            }
            emoji = qe_feeling[:2]
            sent = feeling_map.get(emoji, 0.0)

            # Save as mini journal entry
            dt_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            content = (
                f"Quick check-in: {qe_feeling} "
                f"(intensity: {qe_intensity}/10)"
            )
            if qe_note.strip():
                content += f"\n\n{qe_note.strip()}"

            save_entry(
                user_id=uid,
                content=content,
                entry_date=dt_str,
                sentiment=sent,
                mood_score=sent,
                energy_level=qe_intensity,
                tags=["quick_checkin"],
            )

            # Also save as mood checkin
            save_mood_checkin(
                uid,
                "quick_checkin",
                [emoji, qe_intensity],
                int(sent * 10),
            )

            st.success("✅ Check-in logged!")

        st.markdown("---")

        # ── Breathing timer ──────────────────────────────────────
        st.markdown("### 🌬️ Breathing Guide")
        st.caption(
            "Box breathing: 4 counts in, 4 hold, 4 out, 4 hold. "
            "Follow the visual cue."
        )

        breath_phases = [
            ("Breathe In…", "🫁"),
            ("Hold…", "⏸️"),
            ("Breathe Out…", "💨"),
            ("Hold…", "⏸️"),
        ]
        phase_idx = st.session_state.get("_breath_phase", 0)
        current_phase = breath_phases[phase_idx % 4]

        st.markdown(
            f'<div style="text-align:center;padding:24px;'
            f'background:var(--mm-card-bg);border-radius:16px;'
            f'border:1px solid var(--mm-border);">'
            f'<div style="font-size:3em;">{current_phase[1]}</div>'
            f'<div style="font-size:1.3em;margin-top:8px;'
            f'color:var(--mm-accent);">{current_phase[0]}</div>'
            f'<div style="font-size:0.8em;margin-top:4px;'
            f'color:var(--mm-text-secondary);">'
            f'Phase {(phase_idx % 4) + 1} of 4 · '
            f'Cycle {(phase_idx // 4) + 1}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        breath_col1, breath_col2 = st.columns(2)
        with breath_col1:
            if st.button(
                "Next Phase →",
                key="_breath_next",
                use_container_width=True,
                type="primary",
            ):
                st.session_state._breath_phase = phase_idx + 1
                st.rerun()

        with breath_col2:
            if st.button(
                "Reset",
                key="_breath_reset",
                use_container_width=True,
            ):
                st.session_state._breath_phase = 0
                st.rerun()

        # Community stat at the bottom
        entries = get_entries(uid, limit=10)
        if entries:
            st.markdown("---")
            show_community_stat(entries)


# ═══════════════════════════════════════════════════════════════════
#  📂  HISTORY PAGE
# ═══════════════════════════════════════════════════════════════════

def page_history():
    st.markdown("# 📂 History & Export")
    st.markdown(
        "Browse your saved analyses, review chat sessions, "
        "and export your data."
    )
    st.markdown("---")

    uid = st.session_state.user_id

    tab_analyses, tab_chats, tab_export, tab_restore = st.tabs([
        "📊 Saved Analyses",
        "💬 Chat Sessions",
        "📥 Export Data",
        "📥 Restore Backup",
    ])
        
        # ═════════════════════════════════════════════════════════════
    #  TAB 4: RESTORE FROM BACKUP
    # ═════════════════════════════════════════════════════════════
    with tab_restore:
        show_restore_widget(uid)    
        
    

    # ═════════════════════════════════════════════════════════════
    #  TAB 1: SAVED ANALYSES
    # ═════════════════════════════════════════════════════════════
    with tab_analyses:
        analyses = get_analyses(uid, limit=50)

        if not analyses:
            st.info(
                "No analyses saved yet. Run one from the "
                "**🔬 Analysis** page."
            )
        else:
            st.caption(f"Showing {len(analyses)} saved analyses")

            # Group by type
            type_icons = {
                "local": "📊",
                "ai": "🤖",
                "narrative_week": "📖",
                "narrative_month": "📖",
            }

            for a in analyses:
                atype = a.get("analysis_type", "unknown")
                icon = type_icons.get(atype, "📋")
                date = a.get("created_at", "")[:16]

                with st.expander(
                    f"{icon} {atype.replace('_', ' ').title()} "
                    f"— {date}",
                    expanded=False,
                ):
                    result = a.get("result", "")

                    if atype == "local":
                        # Parse and show key stats
                        parsed = _safe_json_parse(result)
                        if isinstance(parsed, dict):
                            lc1, lc2, lc3 = st.columns(3)
                            lc1.metric(
                                "Entries",
                                parsed.get("entry_count", "?"),
                            )
                            lc2.metric(
                                "Avg Sentiment",
                                f"{parsed.get('avg_sentiment', 0):+.2f}",
                            )
                            trend_info = parsed.get("mood_trend", {})
                            lc3.metric(
                                "Trend",
                                trend_info.get("label", "?"),
                            )

                            # Show topics
                            topics = parsed.get("topics", {})
                            if topics:
                                top_5 = list(topics.items())[:5]
                                st.caption(
                                    "Top topics: "
                                    + ", ".join(
                                        f"`{t}` ({c})"
                                        for t, c in top_5
                                    )
                                )

                            # Show distortions
                            dists = parsed.get("distortions", {})
                            if dists:
                                st.caption(
                                    "Distortions: "
                                    + ", ".join(
                                        f"{d['label']} ({d['count']}×)"
                                        for d in dists.values()
                                    )
                                )
                        else:
                            st.text(str(result)[:2000])

                    else:
                        # AI / narrative — show as markdown
                        st.markdown(str(result)[:5000])

    # ═════════════════════════════════════════════════════════════
    #  TAB 2: CHAT SESSIONS
    # ═════════════════════════════════════════════════════════════
    with tab_chats:
        sessions = get_chat_sessions(uid)

        if not sessions:
            st.info(
                "No chat sessions yet. Start a conversation "
                "from the **💬 AI Chat** page."
            )
        else:
            st.caption(f"{len(sessions)} chat session(s) found")

            for s in sessions:
                label = s.get("session_label", "unknown")
                count = s.get("message_count", 0)
                last = s.get("last_message_at", "")[:16]

                with st.expander(
                    f"💬 {label}  ·  {count} messages  ·  "
                    f"Last: {last}",
                    expanded=False,
                ):
                    msgs = get_chat_msgs(uid, label)
                    if msgs:
                        for m in msgs:
                            role_icon = (
                                "👤" if m["role"] == "user"
                                else "🤖"
                            )
                            ts = m.get("created_at", "")[:16]
                            st.markdown(
                                f"**{role_icon} "
                                f"{'You' if m['role'] == 'user' else 'MindMirror'}** "
                                f"*({ts})*"
                            )
                            st.markdown(m["content"][:1000])
                            st.markdown("")

                        # Generate summary button
                        can_summary = bool(
                            st.session_state.api_key
                            and st.session_state.privacy_mode != "local_only"
                            and st.session_state.consent_ai_processing
                        )
                        if can_summary and count >= 4:
                            if st.button(
                                "📋 Generate Summary",
                                key=f"_hist_sum_{label}",
                            ):
                                with st.spinner("Summarising…"):
                                    summary = generate_session_summary(
                                        msgs,
                                        st.session_state.api_key,
                                        st.session_state.model,
                                    )
                                st.markdown("### 📋 Session Summary")
                                st.markdown(summary)
                    else:
                        st.caption("No messages in this session.")

    # ═════════════════════════════════════════════════════════════
    #  TAB 3: EXPORT DATA
    # ═════════════════════════════════════════════════════════════
    with tab_export:
        st.markdown(
            "Download your MindMirror data. **Your data belongs to you.**"
        )
        st.markdown("")

        entries = get_entries(uid, limit=10000)
        analyses = get_analyses(uid, limit=100)
        goals = get_goals(uid)
        checkins = get_mood_checkins(uid, limit=500)
        sessions = get_chat_sessions(uid)
        profile = get_psyche_profile(uid)

        # ── Stats overview ───────────────────────────────────────
        exp_c1, exp_c2, exp_c3, exp_c4 = st.columns(4)
        exp_c1.metric("Journal Entries", len(entries))
        exp_c2.metric("Analyses", len(analyses))
        exp_c3.metric("Goals", len(goals) if goals else 0)
        exp_c4.metric("Check-ins", len(checkins))

        st.markdown("---")

        # ── JSON Export ──────────────────────────────────────────
        st.markdown("#### 📦 Full Export (JSON)")
        st.caption(
            "Complete export of all your data: journal entries, "
            "analyses, chat messages, goals, check-ins, and profile."
        )

        if st.button(
            "🔄 Prepare JSON Export",
            key="_export_json_prep",
        ):
            # Collect all chat messages
            all_chats = {}
            for s in sessions:
                label = s.get("session_label", "default")
                msgs = get_chat_msgs(uid, label)
                all_chats[label] = [
                    {
                        "role": m["role"],
                        "content": m["content"],
                        "created_at": m.get("created_at", ""),
                    }
                    for m in msgs
                ]

            export_data = {
                "export_date": datetime.now().isoformat(),
                "username": st.session_state.username,
                "profile": profile,
                "entries": [
                    {
                        "id": e["id"],
                        "content": e["content"],
                        "entry_date": e.get("entry_date", ""),
                        "sentiment": e.get("sentiment"),
                        "emotions": _safe_json_parse(
                            e.get("emotions")
                        ),
                        "tags": _safe_json_parse(e.get("tags")),
                        "mood_score": e.get("mood_score"),
                        "energy_level": e.get("energy_level"),
                        "body_zones": _safe_json_parse(
                            e.get("body_zones")
                        ),
                        "distortion_tags": _safe_json_parse(
                            e.get("distortion_tags")
                        ),
                    }
                    for e in entries
                ],
                "analyses": [
                    {
                        "type": a.get("analysis_type", ""),
                        "result": a.get("result", ""),
                        "created_at": a.get("created_at", ""),
                    }
                    for a in analyses
                ],
                "chat_sessions": all_chats,
                "goals": [
                    {
                        "title": g.get("title", ""),
                        "status": g.get("status", ""),
                        "progress": g.get("progress", 0),
                        "target_metric": g.get("target_metric"),
                        "target_value": g.get("target_value"),
                        "created_at": g.get("created_at", ""),
                        "updated_at": g.get("updated_at", ""),
                    }
                    for g in (goals or [])
                ],
                "mood_checkins": [
                    {
                        "type": c.get("checkin_type", ""),
                        "scores": c.get("scores", []),
                        "total": c.get("total_score", 0),
                        "created_at": c.get("created_at", ""),
                    }
                    for c in checkins
                ],
            }

            json_str = json.dumps(export_data, indent=2, default=str)

            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"mindmirror_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                key="_download_json",
            )

            st.success(
                f"✅ Export ready: {len(entries)} entries, "
                f"{len(analyses)} analyses, "
                f"{sum(len(v) for v in all_chats.values())} chat messages."
            )

        st.markdown("---")

        # ── CSV Export (entries only) ────────────────────────────
        st.markdown("#### 📄 Journal Entries (CSV)")
        st.caption(
            "Tabular export of journal entries for use in "
            "spreadsheets or data analysis tools."
        )

        if entries:
            csv_data = []
            for e in entries:
                csv_data.append({
                    "date": e.get("entry_date", ""),
                    "content": e.get("content", "").replace(
                        "\n", " "
                    )[:500],
                    "sentiment": e.get("sentiment", ""),
                    "mood_score": e.get("mood_score", ""),
                    "energy_level": e.get("energy_level", ""),
                    "emotions": json.dumps(
                        _safe_json_parse(e.get("emotions")),
                        default=str,
                    ),
                    "tags": json.dumps(
                        _safe_json_parse(e.get("tags")),
                        default=str,
                    ),
                })

            csv_df = pd.DataFrame(csv_data)
            csv_str = csv_df.to_csv(index=False)

            st.download_button(
                label="📥 Download CSV",
                data=csv_str,
                file_name=f"mindmirror_entries_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="_download_csv",
            )
        else:
            st.caption("No entries to export.")

        st.markdown("---")

        # ── Privacy dashboard ────────────────────────────────────
        st.markdown("#### 🔒 Privacy Dashboard")

        priv_c1, priv_c2 = st.columns(2)

        with priv_c1:
            st.markdown("**Data stored locally:**")
            st.markdown(
                f"- 📝 {len(entries)} journal entries\n"
                f"- 📊 {len(analyses)} analyses\n"
                f"- 💬 {len(sessions)} chat sessions\n"
                f"- 🎯 {len(goals) if goals else 0} goals\n"
                f"- 🩺 {len(checkins)} check-ins"
            )

        with priv_c2:
            st.markdown("**Privacy settings:**")
            pm = st.session_state.privacy_mode
            consent = st.session_state.consent_ai_processing
            st.markdown(
                f"- Mode: **{pm}**\n"
                f"- AI consent: **{'✅ Yes' if consent else '❌ No'}**\n"
                f"- Data location: **Local SQLite**\n"
                f"- Third-party storage: **None**"
            )

        # Crisis log (if any)
        crisis_logs = get_crisis_logs(uid)
        if crisis_logs:
            with st.expander(
                f"⚠️ Crisis Events ({len(crisis_logs)})",
                expanded=False,
            ):
                st.caption(
                    "These events were logged when crisis "
                    "language was detected. They help MindMirror "
                    "provide better follow-up support."
                )
                for cl in crisis_logs[:10]:
                    st.caption(
                        f"📅 {cl.get('created_at', '')[:16]} — "
                        f"Source: {cl.get('trigger_snippet', '?')[:60]}"
                    )


# ──────────────────────────────────────────────────────────────────
# END OF CHUNK 9 — paste Chunk 10 directly below this line
# ──────────────────────────────────────────────────────────────────
# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — app.py  CHUNK 10 of 10  (v3 · Full Blueprint) ║
# ║  ⚙️ Settings Page                                               ║
# ║     API Config · Privacy · Profile Editor · Theme Preview ·    ║
# ║     Accessibility · Data Management                             ║
# ║  🚦 Main Router                                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import sqlite3   # for delete_all_user_data helper


# ═══════════════════════════════════════════════════════════════════
#  DATA DELETION HELPER
# ═══════════════════════════════════════════════════════════════════

def _delete_all_user_data(user_id: int):
    """Remove ALL data for a user from every table.
    The user row itself is kept so they can start fresh."""
    db_path = "mindmirror.db"
    tables_and_cols = [
        ("entries", "user_id"),
        ("analyses", "user_id"),
        ("chat_messages", "user_id"),
        ("goals", "user_id"),
        ("mood_checkins", "user_id"),
        ("growth_metrics", "user_id"),
        ("crisis_logs", "user_id"),
        ("psyche_profiles", "user_id"),
    ]
    conn = sqlite3.connect(db_path)
    try:
        for table, col in tables_and_cols:
            try:
                conn.execute(
                    f"DELETE FROM {table} WHERE {col} = ?",
                    (user_id,),
                )
            except sqlite3.OperationalError:
                pass  # table may not exist yet
        conn.commit()
    finally:
        conn.close()


# ═══════════════════════════════════════════════════════════════════
#  ⚙️  SETTINGS PAGE
# ═══════════════════════════════════════════════════════════════════

def page_settings():
    st.markdown("# ⚙️ Settings")
    st.markdown(
        "Configure your AI, privacy preferences, profile, "
        "appearance, and data."
    )
    st.markdown("---")

    uid = st.session_state.user_id

    tab_ai, tab_privacy, tab_profile, tab_appearance, tab_data = st.tabs([
        "🤖 AI Config",
        "🔒 Privacy",
        "👤 Profile",
        "🎨 Appearance",
        "💾 Data",
    ])

    # ═════════════════════════════════════════════════════════════
    #  TAB 1: AI CONFIGURATION
    # ═════════════════════════════════════════════════════════════
    with tab_ai:
        st.markdown("### 🔑 Gemini API Key")
        st.caption(
            "Your API key is stored **only in your browser session** "
            "and is never saved to the database. For persistent storage, "
            "add it to `.streamlit/secrets.toml`."
        )

        st.code(
            '# .streamlit/secrets.toml\n'
            'GEMINI_API_KEY = "your-key-here"',
            language="toml",
        )

        current_key = st.session_state.api_key
        masked = (
            f"{current_key[:8]}…{current_key[-4:]}"
            if current_key and len(current_key) > 12
            else ("(set)" if current_key else "(not set)")
        )
        st.caption(f"Current key: `{masked}`")

        new_key = st.text_input(
            "Enter or update API key:",
            type="password",
            key="_set_api_key",
            placeholder="AIza…",
        )

        if st.button("💾 Save API Key", key="_set_save_key"):
            if new_key.strip():
                st.session_state.api_key = new_key.strip()
                st.success("✅ API key updated for this session.")
            else:
                st.warning("Key cannot be empty.")

        st.markdown("---")

        st.markdown("### 🤖 Model Selection")
        models = [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]
        current_idx = (
            models.index(st.session_state.model)
            if st.session_state.model in models
            else 0
        )
        new_model = st.selectbox(
            "Choose model:",
            models,
            index=current_idx,
            key="_set_model",
        )
        if new_model != st.session_state.model:
            st.session_state.model = new_model
            st.success(f"✅ Model changed to **{new_model}**")

        st.caption(
            "**gemini-2.5-flash** — best balance of speed and quality\n\n"
            "**gemini-1.5-pro** — most capable, slower\n\n"
            "**-lite** variants — fastest, lower quality"
        )

        st.markdown("---")

        st.markdown("### 🎭 Default Therapeutic Mode")
        mode_keys = list(CHAT_MODE_PROMPTS.keys())
        mode_labels = [CHAT_MODE_PROMPTS[k]["label"] for k in mode_keys]
        current_mode_idx = (
            mode_keys.index(st.session_state.therapeutic_mode)
            if st.session_state.therapeutic_mode in mode_keys
            else 0
        )
        new_mode_label = st.selectbox(
            "Mode:",
            mode_labels,
            index=current_mode_idx,
            key="_set_mode",
        )
        new_mode_key = mode_keys[mode_labels.index(new_mode_label)]
        if new_mode_key != st.session_state.therapeutic_mode:
            st.session_state.therapeutic_mode = new_mode_key

        st.markdown("")
        emp_int = max(1, min(10, int(st.session_state.empathy_level * 10)))
        new_emp = st.slider(
            "Default empathy level:",
            1, 10, emp_int,
            key="_set_empathy",
            help="1 = direct, analytical · 10 = deeply nurturing",
        )
        if abs(new_emp / 10.0 - st.session_state.empathy_level) > 0.05:
            st.session_state.empathy_level = new_emp / 10.0

    # ═════════════════════════════════════════════════════════════
    #  TAB 2: PRIVACY & CONSENT
    # ═════════════════════════════════════════════════════════════
    with tab_privacy:
        st.markdown("### 🔒 Privacy Mode")

        st.info(
            "📦 **All data is stored locally** in a SQLite database "
            "on this server. Nothing is shared with third parties.\n\n"
            "🤖 **AI features** send text to Google Gemini only when "
            "you explicitly click an AI button. Google does not retain "
            "your data after the API call."
        )

        new_privacy = st.radio(
            "Choose your privacy level:",
            [
                "🌐 Standard — AI features enabled",
                "🔒 Local-only — all AI features disabled",
            ],
            index=(
                1 if st.session_state.privacy_mode == "local_only"
                else 0
            ),
            key="_set_privacy",
        )
        is_local = "Local" in new_privacy
        new_pm = "local_only" if is_local else "standard"

        if new_pm != st.session_state.privacy_mode:
            st.session_state.privacy_mode = new_pm
            st.success(
                f"✅ Privacy mode changed to **{new_pm}**"
            )

        st.markdown("---")

        st.markdown("### ✅ AI Processing Consent")

        new_consent = st.checkbox(
            "I consent to sending journal text to Google Gemini "
            "when I explicitly use AI features "
            "(Analysis, Chat, Reflections, Forecasts).",
            value=st.session_state.consent_ai_processing,
            key="_set_consent",
        )
        if new_consent != st.session_state.consent_ai_processing:
            st.session_state.consent_ai_processing = new_consent
            st.success(
                f"✅ Consent {'granted' if new_consent else 'revoked'}."
            )

        if not new_consent:
            st.warning(
                "With consent revoked, all AI features are disabled. "
                "Local analysis (sentiment, emotions, distortions) "
                "still works."
            )

        st.markdown("---")

        st.markdown("### 📋 What Data Goes Where")

        col_local, col_api = st.columns(2)

        with col_local:
            st.markdown(
                "**🏠 Stays Local (always)**\n\n"
                "Journal entries, emotions, sentiment scores, "
                "cognitive distortions, mood/energy scores, body zones, "
                "tags, goals, check-ins, growth metrics, "
                "chat history, analyses, profile, crisis logs"
            )

        with col_api:
            st.markdown(
                "**☁️ Sent to Gemini (only on click)**\n\n"
                "Selected journal text (for AI Analysis), "
                "chat messages (for AI Chat), "
                "context entries (last ~10 for relevance). "
                "Never sent automatically. Never stored by Google."
            )

    # ═════════════════════════════════════════════════════════════
    #  TAB 3: PROFILE EDITOR
    # ═════════════════════════════════════════════════════════════
    with tab_profile:
        st.markdown("### 👤 Your Profile")
        st.caption(
            "Update the preferences you set during onboarding. "
            "Changes are saved to the database."
        )

        profile = st.session_state.get("psyche_profile", {})

        # ── Values ───────────────────────────────────────────────
        st.markdown("#### 🌟 Core Values")
        all_values = [
            "Growth", "Connection", "Autonomy", "Security",
            "Joy", "Purpose", "Balance", "Creativity",
            "Health", "Authenticity", "Adventure", "Kindness",
        ]
        current_values = profile.get("values", ["Growth"])
        if isinstance(current_values, str):
            try:
                current_values = json.loads(current_values)
            except (json.JSONDecodeError, TypeError):
                current_values = ["Growth"]

        new_values = st.multiselect(
            "Your values (up to 3):",
            all_values,
            default=[
                v for v in current_values if v in all_values
            ] or ["Growth"],
            max_selections=3,
            key="_set_values",
        )

        # ── Support Style ────────────────────────────────────────
        st.markdown("#### 💬 Support Style")
        style_options = [
            "Gentle & Validating",
            "Balanced",
            "Direct & Challenging",
        ]
        current_style = profile.get("support_style", "Balanced")
        style_idx = (
            style_options.index(current_style)
            if current_style in style_options
            else 1
        )
        new_style = st.select_slider(
            "Support style:",
            options=style_options,
            value=style_options[style_idx],
            key="_set_style",
        )

        # ── Custom Emotion Vocabulary ────────────────────────────
        st.markdown("#### 🎨 Custom Emotions")

        current_lexicon = profile.get("custom_lexicon", {})
        if isinstance(current_lexicon, str):
            try:
                current_lexicon = json.loads(current_lexicon)
            except (json.JSONDecodeError, TypeError):
                current_lexicon = {}

        if current_lexicon:
            tags_html = " ".join(
                f'<span class="mm-emotion-tag">{v}</span>'
                for v in current_lexicon.values()
            )
            st.markdown(tags_html, unsafe_allow_html=True)
        else:
            st.caption("No custom emotions defined.")

        lex_c1, lex_c2 = st.columns([3, 1])
        with lex_c1:
            new_emo = st.text_input(
                "Add emotion:",
                key="_set_new_emo",
                placeholder="e.g. Overwhelmed, Flow, Meh",
            )
        with lex_c2:
            st.markdown("")
            st.markdown("")
            if st.button("➕ Add", key="_set_add_emo"):
                if new_emo.strip():
                    current_lexicon[new_emo.strip().lower()] = (
                        new_emo.strip()
                    )
                    st.rerun()

        if current_lexicon and st.button(
            "🗑️ Clear All Custom Emotions",
            key="_set_clear_lex",
        ):
            current_lexicon = {}
            st.rerun()

        # ── Save Profile ─────────────────────────────────────────
        st.markdown("---")
        if st.button(
            "💾 Save Profile",
            type="primary",
            key="_set_save_profile",
            use_container_width=True,
        ):
            save_psyche_profile(
                user_id=uid,
                values=new_values,
                support_style=new_style,
                therapeutic_mode_default=st.session_state.therapeutic_mode,
                empathy_level=max(
                    1,
                    min(10, int(st.session_state.empathy_level * 10)),
                ),
                custom_lexicon=current_lexicon if current_lexicon else None,
            )
            st.session_state.psyche_profile = {
                "values": new_values,
                "support_style": new_style,
                "therapeutic_mode_default": st.session_state.therapeutic_mode,
                "empathy_level": max(
                    1,
                    min(10, int(st.session_state.empathy_level * 10)),
                ),
                "custom_lexicon": current_lexicon,
            }
            st.success("✅ Profile saved!")

        # ── Re-run Onboarding ────────────────────────────────────
        st.markdown("")
        if st.button(
            "🔄 Re-Run Onboarding Wizard",
            key="_set_rerun_onboard",
        ):
            st.session_state.onboarding_complete = False
            st.session_state._profile_loaded = False
            st.session_state.pop("_onboard_step", None)
            st.session_state.pop("_onb_data", None)
            st.rerun()

    # ═════════════════════════════════════════════════════════════
    #  TAB 4: APPEARANCE
    # ═════════════════════════════════════════════════════════════
    with tab_appearance:
        st.markdown("### 🎨 Theme")

        # Theme preview cards
        st.markdown("#### Preview All Themes")

        preview_cols = st.columns(4)
        for i, tname in enumerate(THEME_NAMES):
            t = get_theme(tname)
            col = preview_cols[i % 4]
            is_current = (tname == st.session_state.theme)
            border_style = (
                f"3px solid {t['accent']}"
                if is_current
                else f"1px solid {t['border']}"
            )

            with col:
                st.markdown(
                    f'<div style="'
                    f'background:{t["bg"]};'
                    f'border:{border_style};'
                    f'border-radius:12px;'
                    f'padding:12px;'
                    f'margin-bottom:8px;'
                    f'min-height:120px;'
                    f'">'
                    f'<div style="color:{t["text"]};'
                    f'font-weight:700;font-size:0.9em;">'
                    f'{t["display_name"]}</div>'
                    f'<div style="color:{t["text_secondary"]};'
                    f'font-size:0.75em;margin-top:4px;">'
                    f'{t["description"]}</div>'
                    f'<div style="margin-top:8px;">'
                    f'<span style="display:inline-block;'
                    f'width:16px;height:16px;border-radius:50%;'
                    f'background:{t["accent"]};margin-right:4px;">'
                    f'</span>'
                    f'<span style="display:inline-block;'
                    f'width:16px;height:16px;border-radius:50%;'
                    f'background:{t["accent_secondary"]};'
                    f'margin-right:4px;"></span>'
                    f'<span style="display:inline-block;'
                    f'width:16px;height:16px;border-radius:50%;'
                    f'background:{t["positive"]};margin-right:4px;">'
                    f'</span>'
                    f'<span style="display:inline-block;'
                    f'width:16px;height:16px;border-radius:50%;'
                    f'background:{t["negative"]};"></span>'
                    f'</div>'
                    f'{"<div style=&quot;color:" + t["accent"] + ";font-size:0.75em;margin-top:6px;&quot;>✓ Active</div>" if is_current else ""}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Apply" if not is_current else "Active ✓",
                    key=f"_set_theme_{i}",
                    use_container_width=True,
                    disabled=is_current,
                    type="primary" if not is_current else "secondary",
                ):
                    st.session_state.theme = tname
                    st.rerun()

        st.markdown("---")

        # Adaptive theme
        st.markdown("### 🌈 Adaptive Theming")
        st.caption(
            "When enabled, card borders subtly shift color based on "
            "your recent mood: green (thriving), blue (neutral), "
            "amber (low), purple (distressed)."
        )
        adapt = st.checkbox(
            "Enable adaptive mood tinting",
            value=st.session_state.adaptive_theme_enabled,
            key="_set_adaptive",
        )
        if adapt != st.session_state.adaptive_theme_enabled:
            st.session_state.adaptive_theme_enabled = adapt
            st.rerun()

        # Mood-based recommendation
        if entries := get_entries(uid, limit=10):
            sents = [
                e["sentiment"] for e in entries
                if e.get("sentiment") is not None
            ]
            if sents:
                avg = sum(sents) / len(sents)
                recs = get_theme_recommendation(avg)
                if recs:
                    st.caption(
                        f"💡 Based on your recent mood ({avg:+.2f}), "
                        f"we'd suggest: **{recs[0]}**"
                    )

        st.markdown("---")

        # Accessibility
        st.markdown("### ♿ Accessibility")

        new_fs = st.slider(
            "Font size scale:",
            0.8, 1.5,
            st.session_state.font_size_scale,
            step=0.1,
            format="%.1f×",
            key="_set_font",
        )
        if new_fs != st.session_state.font_size_scale:
            st.session_state.font_size_scale = new_fs
            st.rerun()

        new_hc = st.checkbox(
            "High contrast mode (forces maximum text contrast)",
            value=st.session_state.high_contrast,
            key="_set_hc",
        )
        if new_hc != st.session_state.high_contrast:
            st.session_state.high_contrast = new_hc
            st.rerun()

        new_rm = st.checkbox(
            "Reduce motion (disables transitions and animations)",
            value=st.session_state.reduce_motion,
            key="_set_rm",
        )
        if new_rm != st.session_state.reduce_motion:
            st.session_state.reduce_motion = new_rm
            st.rerun()

    # ═════════════════════════════════════════════════════════════
    #  TAB 5: DATA MANAGEMENT
    # ═════════════════════════════════════════════════════════════
    with tab_data:
        st.markdown("### 💾 Data Management")

        ec = entry_count(uid)
        analyses = get_analyses(uid, limit=1000)
        goals = get_goals(uid)
        checkins = get_mood_checkins(uid, limit=1000)
        sessions = get_chat_sessions(uid)

        st.markdown(
            f"**Your data footprint:**\n\n"
            f"📝 {ec} journal entries\n\n"
            f"📊 {len(analyses)} saved analyses\n\n"
            f"💬 {len(sessions)} chat sessions\n\n"
            f"🎯 {len(goals) if goals else 0} goals\n\n"
            f"🩺 {len(checkins)} check-ins"
        )

        st.markdown("---")

        st.markdown("### ⚠️ Delete All Data")
        st.warning(
            "This will **permanently delete** all your journal "
            "entries, analyses, chat sessions, goals, check-ins, "
            "growth metrics, crisis logs, and profile. "
            "Your username will be kept so you can start fresh. "
            "**This cannot be undone.**"
        )

        # Two-step confirmation
        confirm_text = st.text_input(
            f'Type **{st.session_state.username}** to confirm:',
            key="_del_confirm",
            placeholder="Type your username exactly…",
        )

        if st.button(
            "🗑️ Delete Everything",
            type="primary",
            key="_del_all",
        ):
            if confirm_text.strip() == st.session_state.username:
                _delete_all_user_data(uid)

                # Reset session state
                st.session_state.psyche_profile = {}
                st.session_state.onboarding_complete = False
                st.session_state._profile_loaded = False
                st.session_state.current_analysis = None
                st.session_state.pop("_cached_analysis", None)

                st.success(
                    "✅ All data deleted. You can start fresh."
                )
                st.balloons()
                st.rerun()
            else:
                st.error(
                    "Username doesn't match. "
                    "Type it exactly to confirm deletion."
                )


# ═══════════════════════════════════════════════════════════════════
#  🚦  MAIN ROUTER
# ═══════════════════════════════════════════════════════════════════

def main():
    """Main application router. Called once per page load."""

    # ── Not logged in ────────────────────────────────────────────
    if not st.session_state.logged_in:
        st.markdown("# 🧠 MindMirror AI")
        st.markdown("### Decode your mind. Discover your patterns.")
        st.markdown("")

        st.markdown(
            '<div class="mm-card">'
            "<h4>Welcome to MindMirror AI</h4>"
            "<p>MindMirror is your private, AI-powered emotional "
            "intelligence journal. It helps you:</p>"
            "<p>"
            "📝 Journal with guided templates and mood tracking<br>"
            "🔬 Discover cognitive patterns and emotional triggers<br>"
            "💬 Talk with an empathetic AI that adapts to you<br>"
            "📊 Track growth with clinical assessments and radars<br>"
            "🧘 Build skills with CBT, DBT, and self-compassion tools<br>"
            "🔒 Keep full control of your data — everything stays local"
            "</p>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown("")
        st.info("👈 Enter your name in the sidebar to get started.")
        return

    # ── Onboarding not complete ──────────────────────────────────
    if not st.session_state.onboarding_complete:
        page_onboarding()
        return

    # ── Route to selected page ───────────────────────────────────
    page = st.session_state.page

    routes = {
        "📝 Journal":        page_journal,
        "🔬 Analysis":       page_analysis,
        "💬 AI Chat":        page_chat,
        "📊 Dashboard":      page_dashboard,
        "🧘 Skills & Growth": page_skills,
        "📂 History":        page_history,
        "⚙️ Settings":       page_settings,
    }

    page_fn = routes.get(page, page_journal)
    page_fn()


# ═══════════════════════════════════════════════════════════════════
#  🏁  ENTRY POINT
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
else:
    # Streamlit runs the file directly, not as __main__
    main()
