# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — app.py  PART 1 of 3  (v2 · All Fixes)         ║
# ║  Imports · Secrets · Auto-Login · Sidebar                       ║
# ╚══════════════════════════════════════════════════════════════════╝

import streamlit as st
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from database import (
    init_db, get_or_create_user, save_entry, get_entries,
    delete_entry, entry_count, get_sentiments_over_time,
    save_analysis, get_analyses, save_chat_msg, get_chat_msgs,
    get_chat_sessions, delete_chat_session,
)
from analyzer import (
    sentiment_score, detect_emotions, extract_entities,
    extract_topics, word_frequencies, local_analysis,
    ai_analysis, ai_chat, ai_reflection_prompts,
)
from themes import get_theme_css, get_plotly_colors, THEME_NAMES

# ── Page config (MUST be first Streamlit call) ───────────────────
st.set_page_config(
    page_title="MindMirror AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load API key from Streamlit Secrets (set once, persists) ─────
def _load_api_key():
    """Read GEMINI_API_KEY from .streamlit/secrets.toml
       or Streamlit Cloud Secrets dashboard."""
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return ""

# ── Session-state defaults ───────────────────────────────────────
_DEFAULTS = {
    "user_id": None,
    "username": "",
    "logged_in": False,
    "page": "📝 Journal",
    "theme": "🌊 Deep Ocean",
    "api_key": _load_api_key(),
    "model": "gemini-2.5-flash",
    "chat_session": "default",
    "current_analysis": None,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Initialise database ─────────────────────────────────────────
init_db()

# ── Auto-login from URL query params (survives page refresh) ────
if not st.session_state.logged_in:
    params = st.query_params
    if "user" in params:
        uname = params["user"]
        if uname.strip():
            st.session_state.username = uname.strip()
            st.session_state.user_id = get_or_create_user(
                uname.strip()
            )
            st.session_state.logged_in = True

# ── Apply selected theme ────────────────────────────────────────
st.markdown(
    get_theme_css(st.session_state.theme),
    unsafe_allow_html=True,
)

# ── Plotly helpers ───────────────────────────────────────────────
def _plotly_layout(fig, title=""):
    pc = get_plotly_colors(st.session_state.theme)
    fig.update_layout(
        title=title,
        plot_bgcolor=pc["paper"],
        paper_bgcolor=pc["paper"],
        font_color=pc["text"],
        title_font_color=pc["text"],
        xaxis=dict(
            gridcolor=pc["grid"],
            zerolinecolor=pc["grid"],
        ),
        yaxis=dict(
            gridcolor=pc["grid"],
            zerolinecolor=pc["grid"],
        ),
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(font=dict(color=pc["text"])),
    )
    return fig


def _pcolors():
    return get_plotly_colors(st.session_state.theme)["colors"]


# ══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        st.markdown("## 🧠 MindMirror AI")
        st.caption(
            "*Decode your mind. Discover your patterns.*"
        )
        st.markdown("---")

        # ── Not logged in ────────────────────────────────────────
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
                    st.session_state.user_id = (
                        get_or_create_user(uname.strip())
                    )
                    st.session_state.logged_in = True
                    # Save username in URL so refresh works
                    st.query_params["user"] = uname.strip()
                    st.rerun()
                else:
                    st.warning("Please type a name.")
            return

        # ── Logged in ────────────────────────────────────────────
        ec = entry_count(st.session_state.user_id)
        st.markdown(f"#### 👤 {st.session_state.username}")
        st.caption(f"📊 {ec} journal entries saved")

        # API key status (no input field — comes from secrets)
        if st.session_state.api_key:
            st.caption("🔑 Gemini: ✅ Connected")
        else:
            st.caption("🔑 Gemini: ⚠️ Set key in Secrets")

        st.markdown("---")

        # ── Navigation ───────────────────────────────────────────
        st.markdown("#### 📍 Navigate")
        pages = [
            "📝 Journal",
            "🔬 Analysis",
            "💬 AI Chat",
            "📊 Dashboard",
            "📂 History",
            "⚙️ Settings",
        ]
        for p in pages:
            kind = (
                "primary"
                if st.session_state.page == p
                else "secondary"
            )
            if st.button(
                p,
                use_container_width=True,
                type=kind,
                key=f"nav_{p}",
            ):
                st.session_state.page = p
                st.rerun()

        st.markdown("---")

        # ── Theme selector ───────────────────────────────────────
        st.markdown("#### 🎨 Theme")
        idx = (
            THEME_NAMES.index(st.session_state.theme)
            if st.session_state.theme in THEME_NAMES
            else 0
        )
        theme = st.selectbox(
            "Select:",
            THEME_NAMES,
            index=idx,
            key="_theme_sel",
            label_visibility="collapsed",
        )
        if theme != st.session_state.theme:
            st.session_state.theme = theme
            st.rerun()

        st.markdown("---")

        # ── Model selector ───────────────────────────────────────
        st.markdown("#### 🤖 AI Model")
        st.session_state.model = st.selectbox(
            "Model:",
            [
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite",
                "gemini-2.0-flash",
                "gemini-2.0-flash-lite",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
            ],
            index=0,
            key="_model_sel",
            label_visibility="collapsed",
        )

        st.markdown("---")

        # ── Logout ───────────────────────────────────────────────
        if st.button(
            "🚪 Logout", use_container_width=True
        ):
            st.query_params.clear()
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


render_sidebar()

# ──────────────────────────────────────────────────────────────────
# END OF PART 1 — paste Part 2 directly below this line
# ──────────────────────────────────────────────────────────────────
# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — app.py  PART 2 of 3  (v2 · All Fixes)         ║
# ║  Journal · Analysis · AI Chat                                   ║
# ╚══════════════════════════════════════════════════════════════════╝

# ═══════════════════  📝  JOURNAL PAGE  ═══════════════════════════

def page_journal():
    st.markdown("# 📝 Journal")
    st.markdown(
        "Write your thoughts, feelings, and daily reflections. "
        "MindMirror saves everything — even after you close "
        "the browser."
    )
    st.markdown("---")

    tab_new, tab_batch, tab_entries = st.tabs(
        ["✏️ New Entry", "📋 Batch Import", "📖 My Entries"]
    )

    # ── New Entry tab ────────────────────────────────────────────
    with tab_new:
        col1, col2 = st.columns([3, 1])
        with col2:
            entry_date = st.date_input(
                "Date:",
                value=datetime.now(),
                key="_jdate",
            )
            entry_time = st.time_input(
                "Time:",
                value=datetime.now().time(),
                key="_jtime",
            )
        with col1:
            content = st.text_area(
                "What's on your mind?",
                height=200,
                key="_jcontent",
                placeholder=(
                    "Today I felt… / I noticed that… / "
                    "Something happened…"
                ),
            )
        if st.button(
            "💾 Save Entry",
            type="primary",
            use_container_width=True,
            key="_jsave",
        ):
            if content.strip():
                dt = datetime.combine(
                    entry_date, entry_time
                ).strftime("%Y-%m-%d %H:%M")
                sent = sentiment_score(content)
                emos = detect_emotions(content)
                tags = list(extract_topics(content).keys())
                save_entry(
                    st.session_state.user_id,
                    content.strip(),
                    dt,
                    sent,
                    emos if emos else None,
                    tags if tags else None,
                )
                st.success("✅ Entry saved!")
                st.balloons()
            else:
                st.warning("Write something first.")

    # ── Batch Import tab ─────────────────────────────────────────
    with tab_batch:
        st.markdown(
            "Paste multiple entries separated by `---` on its "
            "own line. Optionally start each with a date like "
            "`2025-03-20:`."
        )
        batch = st.text_area(
            "Paste entries:",
            height=300,
            key="_jbatch",
            placeholder=(
                "2025-03-20: I felt great today…\n"
                "---\n"
                "2025-03-21: Not so good…"
            ),
        )
        if st.button(
            "📥 Import All",
            type="primary",
            key="_jbatch_save",
        ):
            if batch.strip():
                import re as _re

                chunks = [
                    c.strip()
                    for c in batch.split("---")
                    if c.strip()
                ]
                count = 0
                for chunk in chunks:
                    m = _re.match(
                        r"^(\d{4}-\d{2}-\d{2})[:\s]*(.*)",
                        chunk,
                        _re.S,
                    )
                    if m:
                        dt = m.group(1) + " 12:00"
                        text = m.group(2).strip()
                    else:
                        dt = datetime.now().strftime(
                            "%Y-%m-%d %H:%M"
                        )
                        text = chunk
                    if text:
                        sent = sentiment_score(text)
                        save_entry(
                            st.session_state.user_id,
                            text, dt, sent,
                        )
                        count += 1
                st.success(f"✅ Imported {count} entries!")
            else:
                st.warning("Paste some text first.")

    # ── My Entries tab ───────────────────────────────────────────
    with tab_entries:
        entries = get_entries(st.session_state.user_id)
        if not entries:
            st.info("No entries yet. Start journaling! ✍️")
            return
        st.caption(
            f"Showing {len(entries)} entries (newest first)"
        )
        for e in entries:
            sent = e.get("sentiment")
            if sent is not None:
                if sent > 0.2:
                    mood = "😊"
                elif sent < -0.2:
                    mood = "😟"
                else:
                    mood = "😐"
            else:
                mood = "📝"

            with st.expander(
                f"{mood}  {e['entry_date']}  —  "
                f"{e['content'][:80]}…"
            ):
                st.markdown(e["content"])
                tags_raw = e.get("tags")
                if tags_raw:
                    try:
                        tl = (
                            json.loads(tags_raw)
                            if isinstance(tags_raw, str)
                            else tags_raw
                        )
                        st.caption(
                            "Tags: "
                            + ", ".join(f"`{t}`" for t in tl)
                        )
                    except Exception:
                        pass
                if sent is not None:
                    st.caption(f"Sentiment: {sent:+.2f}")
                if st.button(
                    "🗑️ Delete", key=f"del_{e['id']}"
                ):
                    delete_entry(
                        e["id"], st.session_state.user_id
                    )
                    st.rerun()


# ═══════════════════  🔬  ANALYSIS PAGE  ═════════════════════════

def page_analysis():
    st.markdown("# 🔬 Pattern Analysis")
    st.markdown(
        "Uncover hidden emotional and behavioral patterns "
        "from your journal."
    )
    st.markdown("---")

    entries = get_entries(st.session_state.user_id)
    if len(entries) < 2:
        st.warning(
            "Write at least 2 journal entries before "
            "running an analysis."
        )
        return

    # ── Slider with safe bounds (FIX for crash) ──────────────────
    max_entries = min(len(entries), 100)
    default_val = min(max_entries, 20)

    # Clear stale cached slider value that exceeds new bounds
    if "_an_n" in st.session_state:
        cached = st.session_state["_an_n"]
        if cached > max_entries or cached < 2:
            del st.session_state["_an_n"]

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if max_entries <= 2:
            # Only 2 entries — skip slider entirely
            n = max_entries
            st.info(f"📋 Analysing all {n} entries")
        else:
            n = st.slider(
                "Entries to analyse:",
                2,
                max_entries,
                default_val,
                key="_an_n",
            )
    with col2:
        run_local = st.button(
            "📊 Local Analysis",
            use_container_width=True,
            key="_an_local",
        )
    with col3:
        run_ai = st.button(
            "🤖 AI Deep Analysis",
            use_container_width=True,
            type="primary",
            key="_an_ai",
            disabled=not st.session_state.api_key,
        )

    target = list(reversed(entries[:n]))

    # ── Local analysis ───────────────────────────────────────────
    if run_local or run_ai:
        la = local_analysis(target)
        if la:
            st.markdown("### 📊 Local Pattern Report")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Entries", la["entry_count"])
            avg = la["avg_sentiment"]
            m2.metric(
                "Avg Sentiment",
                f"{avg:+.2f}",
                delta=(
                    "positive" if avg > 0.1
                    else (
                        "negative" if avg < -0.1
                        else "neutral"
                    )
                ),
            )
            m3.metric(
                "Emotions Found", la["emotion_diversity"]
            )
            m4.metric("Topics", len(la["topics"]))

            # Sentiment timeline
            if la["sentiments"]:
                df_s = pd.DataFrame(la["sentiments"])
                fig = px.line(
                    df_s,
                    x="date",
                    y="score",
                    markers=True,
                    color_discrete_sequence=_pcolors(),
                )
                fig = _plotly_layout(
                    fig, "Sentiment Over Time"
                )
                st.plotly_chart(
                    fig, use_container_width=True
                )

            c1, c2 = st.columns(2)
            with c1:
                if la["emotions"]:
                    emo_c = {
                        k: len(v)
                        for k, v in la["emotions"].items()
                    }
                    fig = px.pie(
                        names=list(emo_c.keys()),
                        values=list(emo_c.values()),
                        color_discrete_sequence=_pcolors(),
                    )
                    fig = _plotly_layout(
                        fig, "Emotion Distribution"
                    )
                    st.plotly_chart(
                        fig, use_container_width=True
                    )
            with c2:
                if la["topics"]:
                    fig = px.bar(
                        x=list(la["topics"].values()),
                        y=list(la["topics"].keys()),
                        orientation="h",
                        color_discrete_sequence=_pcolors(),
                    )
                    fig = _plotly_layout(
                        fig, "Topic Frequency"
                    )
                    st.plotly_chart(
                        fig, use_container_width=True
                    )

            c3, c4 = st.columns(2)
            with c3:
                if la["people"]:
                    st.markdown("**👥 People Mentioned**")
                    for name, cnt in la["people"]:
                        st.markdown(f"- **{name}** × {cnt}")
            with c4:
                if la["words"]:
                    st.markdown("**🔤 Top Words**")
                    wdf = pd.DataFrame(
                        la["words"],
                        columns=["word", "count"],
                    )
                    fig = px.bar(
                        wdf.head(15),
                        x="count",
                        y="word",
                        orientation="h",
                        color_discrete_sequence=_pcolors(),
                    )
                    fig = _plotly_layout(
                        fig, "Word Frequency"
                    )
                    st.plotly_chart(
                        fig, use_container_width=True
                    )

            save_analysis(
                st.session_state.user_id,
                "local",
                json.dumps(la, default=str),
            )

    # ── AI deep analysis ─────────────────────────────────────────
    if run_ai:
        if not st.session_state.api_key:
            st.error(
                "Gemini API key not found. Add it to your "
                "Streamlit Secrets."
            )
            return
        la = local_analysis(target)
        with st.spinner(
            "🧠 MindMirror is reading between the lines…"
        ):
            result = ai_analysis(
                target,
                st.session_state.api_key,
                st.session_state.model,
                la,
            )
        st.markdown("---")
        st.markdown("### 🤖 AI Deep Analysis Report")
        st.markdown(result)
        st.session_state.current_analysis = result
        save_analysis(
            st.session_state.user_id, "ai", result
        )
        st.success("Analysis saved to your history.")


# ═══════════════════  💬  AI CHAT PAGE  ══════════════════════════

def page_chat():
    st.markdown("# 💬 AI Insight Chat")
    st.markdown(
        "Talk with MindMirror about your patterns, feelings, "
        "and what's on your mind. I remember everything."
    )
    st.markdown("---")

    if not st.session_state.api_key:
        st.warning(
            "Gemini API key not found. Add `GEMINI_API_KEY` "
            "to your Streamlit Secrets "
            "(see ⚙️ Settings for instructions)."
        )
        return

    uid = st.session_state.user_id

    # ── Session management ───────────────────────────────────────
    sessions = get_chat_sessions(uid)
    session_labels = (
        [s["session_label"] for s in sessions]
        if sessions
        else []
    )
    if "default" not in session_labels:
        session_labels.insert(0, "default")

    st.markdown("#### 💬 Chat Sessions")
    col_s1, col_s2 = st.columns([3, 1])

    with col_s1:
        current_idx = (
            session_labels.index(
                st.session_state.chat_session
            )
            if st.session_state.chat_session in session_labels
            else 0
        )
        chosen = st.selectbox(
            "Active session:",
            session_labels,
            index=current_idx,
            key="_chat_sess",
            label_visibility="collapsed",
        )
        if chosen != st.session_state.chat_session:
            st.session_state.chat_session = chosen
            st.rerun()

    with col_s2:
        if st.button(
            "🗑️ Clear",
            key="_clr_chat",
            use_container_width=True,
        ):
            delete_chat_session(
                uid, st.session_state.chat_session
            )
            st.rerun()

    # ── Quick-create preset sessions ─────────────────────────────
    st.caption("Start a new conversation:")
    preset_cols = st.columns(5)
    presets = [
        "🌅 Morning Check-in",
        "🌙 Evening Reflection",
        "💭 Deep Dive",
        "🎯 Goal Setting",
        "💚 Mood Check",
    ]
    for i, label in enumerate(presets):
        with preset_cols[i]:
            if st.button(
                label,
                key=f"_pre_{i}",
                use_container_width=True,
            ):
                st.session_state.chat_session = label
                st.rerun()

    # ── Custom session name ──────────────────────────────────────
    custom_col1, custom_col2 = st.columns([3, 1])
    with custom_col1:
        new_label = st.text_input(
            "Or name your own:",
            key="_new_sess",
            placeholder="e.g. March reflections",
            label_visibility="collapsed",
        )
    with custom_col2:
        if st.button(
            "➕ Create",
            key="_new_sess_btn",
            use_container_width=True,
        ):
            if new_label.strip():
                st.session_state.chat_session = (
                    new_label.strip()
                )
                st.rerun()

    st.markdown("---")

    # ── Load & display chat history ──────────────────────────────
    db_msgs = get_chat_msgs(
        uid, st.session_state.chat_session
    )
    entries = get_entries(uid)

    if not db_msgs:
        st.caption(
            f"📎 Session: **{st.session_state.chat_session}**"
            " — Start the conversation below."
        )

    for m in db_msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # ── Chat input ───────────────────────────────────────────────
    if prompt := st.chat_input(
        "Tell me what's on your mind…"
    ):
        with st.chat_message("user"):
            st.markdown(prompt)
        save_chat_msg(
            uid, "user", prompt,
            st.session_state.chat_session,
        )

        history = [
            {"role": m["role"], "content": m["content"]}
            for m in db_msgs
        ]

        with st.chat_message("assistant"):
            with st.spinner("Reflecting…"):
                reply = ai_chat(
                    prompt,
                    entries,
                    history,
                    st.session_state.api_key,
                    st.session_state.model,
                )
            st.markdown(reply)
        save_chat_msg(
            uid, "assistant", reply,
            st.session_state.chat_session,
        )


# ──────────────────────────────────────────────────────────────────
# END OF PART 2 — paste Part 3 directly below this line
# ──────────────────────────────────────────────────────────────────
# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — app.py  PART 3 of 3  (v2 · All Fixes)         ║
# ║  Dashboard · History · Settings · Welcome · Router              ║
# ╚══════════════════════════════════════════════════════════════════╝

# ═══════════════════  📊  DASHBOARD PAGE  ════════════════════════

def page_dashboard():
    st.markdown("# 📊 Insight Dashboard")
    st.markdown(
        "A bird's-eye view of your emotional and "
        "behavioral landscape."
    )
    st.markdown("---")

    uid = st.session_state.user_id
    entries = get_entries(uid)
    if len(entries) < 2:
        st.info(
            "Add more journal entries to unlock "
            "your dashboard."
        )
        return

    la = local_analysis(list(reversed(entries)))
    if not la:
        return

    # ── Top metrics ──────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Entries", la["entry_count"])
    avg = la["avg_sentiment"]
    m2.metric("Avg Mood", f"{avg:+.2f}")
    m3.metric("Emotions Detected", la["emotion_diversity"])
    m4.metric("Topics Covered", len(la["topics"]))

    # Calculate streak
    dates = sorted(set(
        e.get("entry_date", "")[:10]
        for e in entries
        if e.get("entry_date")
    ))
    streak = 0
    if dates:
        streak = 1
        for i in range(len(dates) - 1, 0, -1):
            try:
                d1 = datetime.strptime(
                    dates[i], "%Y-%m-%d"
                )
                d2 = datetime.strptime(
                    dates[i - 1], "%Y-%m-%d"
                )
                if (d1 - d2).days == 1:
                    streak += 1
                else:
                    break
            except ValueError:
                break
    m5.metric(
        "🔥 Streak",
        f"{streak} day{'s' if streak != 1 else ''}",
    )

    st.markdown("---")

    # ── Mood timeline ────────────────────────────────────────────
    if la["sentiments"]:
        df = pd.DataFrame(la["sentiments"])
        fig = px.area(
            df,
            x="date",
            y="score",
            markers=True,
            color_discrete_sequence=_pcolors(),
            labels={"score": "Sentiment", "date": "Date"},
        )
        fig = _plotly_layout(fig, "📈 Mood Over Time")
        fig.add_hline(
            y=0, line_dash="dash",
            line_color="gray", opacity=0.5,
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Emotion and topic charts ─────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        if la["emotions"]:
            emo_c = {
                k: len(v)
                for k, v in la["emotions"].items()
            }
            fig = px.bar(
                x=list(emo_c.keys()),
                y=list(emo_c.values()),
                color=list(emo_c.keys()),
                color_discrete_sequence=_pcolors(),
                labels={"x": "Emotion", "y": "Mentions"},
            )
            fig = _plotly_layout(
                fig, "🎭 Emotion Frequency"
            )
            st.plotly_chart(
                fig, use_container_width=True
            )
    with c2:
        if la["topics"]:
            fig = px.bar(
                x=list(la["topics"].values()),
                y=list(la["topics"].keys()),
                orientation="h",
                color_discrete_sequence=_pcolors(),
                labels={"x": "Mentions", "y": "Topic"},
            )
            fig = _plotly_layout(
                fig, "🏷️ Topics Breakdown"
            )
            st.plotly_chart(
                fig, use_container_width=True
            )

    # ── Day and time charts ──────────────────────────────────────
    c3, c4 = st.columns(2)
    with c3:
        if la["days"]:
            fig = px.bar(
                x=[d[0] for d in la["days"]],
                y=[d[1] for d in la["days"]],
                color_discrete_sequence=_pcolors(),
                labels={"x": "Day", "y": "Mentions"},
            )
            fig = _plotly_layout(fig, "📅 Day Mentions")
            st.plotly_chart(
                fig, use_container_width=True
            )
    with c4:
        if la["times"]:
            fig = px.pie(
                names=[t[0] for t in la["times"]],
                values=[t[1] for t in la["times"]],
                color_discrete_sequence=_pcolors(),
            )
            fig = _plotly_layout(
                fig, "🕐 Time-of-Day Mentions"
            )
            st.plotly_chart(
                fig, use_container_width=True
            )

    # ── Word frequency ───────────────────────────────────────────
    if la["words"]:
        st.markdown("### 🔤 Most Used Words")
        wdf = pd.DataFrame(
            la["words"][:20], columns=["word", "count"]
        )
        fig = px.bar(
            wdf,
            x="count",
            y="word",
            orientation="h",
            color="count",
            color_continuous_scale="Viridis",
        )
        fig = _plotly_layout(fig, "")
        fig.update_layout(
            showlegend=False,
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── People mentioned ─────────────────────────────────────────
    if la["people"]:
        st.markdown("### 👥 People Mentioned Most")
        pcols = st.columns(min(len(la["people"]), 5))
        for i, (name, cnt) in enumerate(
            la["people"][:5]
        ):
            with pcols[i]:
                st.metric(name, f"{cnt}×")

    st.markdown("---")

    # ── AI reflection prompts ────────────────────────────────────
    if st.session_state.api_key and entries:
        st.markdown("### 💡 AI Reflection Prompts")
        st.caption(
            "Personalised prompts based on your "
            "recent entries."
        )
        if st.button(
            "✨ Generate Prompts", key="_dash_prompts"
        ):
            with st.spinner("Crafting thoughtful prompts…"):
                prompts = ai_reflection_prompts(
                    entries,
                    st.session_state.api_key,
                    st.session_state.model,
                )
            st.markdown(prompts)
    elif not st.session_state.api_key:
        st.caption(
            "💡 Add your Gemini key to Secrets to "
            "unlock AI reflection prompts."
        )

    st.markdown("---")

    # ── Mood calendar ────────────────────────────────────────────
    st.markdown("### 🗓️ Mood Calendar")
    sot = get_sentiments_over_time(uid)
    if sot and len(sot) >= 2:
        cal_df = pd.DataFrame(sot)
        cal_df["entry_date"] = pd.to_datetime(
            cal_df["entry_date"]
        )
        cal_df["day"] = cal_df["entry_date"].dt.date
        daily = (
            cal_df.groupby("day")["sentiment"]
            .mean()
            .reset_index()
        )
        daily.columns = ["date", "mood"]
        daily["date"] = pd.to_datetime(daily["date"])
        daily["weekday"] = daily["date"].dt.day_name()
        fig = px.scatter(
            daily,
            x="date",
            y="mood",
            size=[
                abs(m) * 30 + 5 for m in daily["mood"]
            ],
            color="mood",
            color_continuous_scale="RdYlGn",
            labels={
                "mood": "Sentiment", "date": "Date"
            },
            hover_data=["weekday"],
        )
        fig = _plotly_layout(fig, "")
        fig.add_hline(
            y=0, line_dash="dash",
            line_color="gray", opacity=0.4,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption(
            "Not enough data for the mood calendar yet."
        )


# ═══════════════════  📂  HISTORY PAGE  ══════════════════════════

def page_history():
    st.markdown("# 📂 Saved Analyses & Activity")
    st.markdown("Everything is saved — come back anytime.")
    st.markdown("---")

    uid = st.session_state.user_id
    tab_an, tab_ch, tab_ex = st.tabs(
        ["🔬 Analyses", "💬 Chat History", "📤 Export"]
    )

    # ── Analyses tab ─────────────────────────────────────────────
    with tab_an:
        analyses = get_analyses(uid, limit=50)
        if not analyses:
            st.info(
                "No saved analyses yet. Run one from "
                "the 🔬 Analysis page."
            )
        else:
            st.caption(f"{len(analyses)} saved analyses")
            for a in analyses:
                a_type = (
                    "🤖 AI"
                    if a["analysis_type"] == "ai"
                    else "📊 Local"
                )
                with st.expander(
                    f"{a_type}  —  {a['created_at']}"
                ):
                    if a["analysis_type"] == "local":
                        try:
                            st.json(
                                json.loads(a["result"])
                            )
                        except (
                            json.JSONDecodeError,
                            TypeError,
                        ):
                            st.markdown(str(a["result"]))
                    else:
                        st.markdown(a["result"])

    # ── Chat History tab ─────────────────────────────────────────
    with tab_ch:
        sessions = get_chat_sessions(uid)
        if not sessions:
            st.info("No chat sessions yet.")
        else:
            for sess in sessions:
                label = sess["session_label"]
                with st.expander(
                    f"💬 {label}  —  "
                    f"{sess['started'][:16]}  —  "
                    f"{sess['msg_count']} messages"
                ):
                    msgs = get_chat_msgs(
                        uid, label, limit=200
                    )
                    for m in msgs:
                        icon = (
                            "🧑" if m["role"] == "user"
                            else "🤖"
                        )
                        st.markdown(
                            f"**{icon} "
                            f"{m['role'].title()}** "
                            f"({m['created_at'][:16]})"
                        )
                        st.markdown(m["content"])
                        st.markdown("---")

    # ── Export tab ───────────────────────────────────────────────
    with tab_ex:
        st.markdown("### 📤 Export Your Data")
        entries = get_entries(uid)
        if entries:
            export_entries = [
                {
                    "date": e.get("entry_date", ""),
                    "content": e.get("content", ""),
                    "sentiment": e.get("sentiment"),
                    "tags": e.get("tags"),
                }
                for e in entries
            ]
            st.download_button(
                "📥 Journal (JSON)",
                json.dumps(
                    export_entries,
                    indent=2,
                    ensure_ascii=False,
                ),
                file_name=(
                    f"mindmirror_journal_"
                    f"{st.session_state.username}.json"
                ),
                mime="application/json",
                key="_exp_j",
            )
            txt = "\n\n".join(
                f"[{e.get('entry_date', '')}]\n"
                f"{e.get('content', '')}"
                for e in entries
            )
            st.download_button(
                "📥 Journal (TXT)",
                txt,
                file_name=(
                    f"mindmirror_journal_"
                    f"{st.session_state.username}.txt"
                ),
                mime="text/plain",
                key="_exp_jt",
            )
        else:
            st.caption("No entries to export.")

        analyses = get_analyses(uid, limit=100)
        if analyses:
            st.download_button(
                "📥 Analyses (JSON)",
                json.dumps(
                    [
                        {
                            "type": a["analysis_type"],
                            "date": a["created_at"],
                            "result": a["result"],
                        }
                        for a in analyses
                    ],
                    indent=2,
                    ensure_ascii=False,
                ),
                file_name=(
                    f"mindmirror_analyses_"
                    f"{st.session_state.username}.json"
                ),
                mime="application/json",
                key="_exp_a",
            )
        else:
            st.caption("No analyses to export.")


# ═══════════════════  ⚙️  SETTINGS PAGE  ═════════════════════════

def page_settings():
    st.markdown("# ⚙️ Settings")
    st.markdown("---")

    # ── API key status ───────────────────────────────────────────
    st.markdown("### 🔑 Gemini API Key")

    if st.session_state.api_key:
        st.success(
            "✅ Gemini API key is loaded from Secrets "
            "and working."
        )
        st.markdown(
            f"**Model:** `{st.session_state.model}`"
        )
    else:
        st.error(
            "⚠️ No Gemini API key found. "
            "AI features are disabled."
        )
        st.markdown("#### How to set up your key:")
        st.markdown(
            "**On Streamlit Cloud:**\n"
            "1. Go to your app dashboard\n"
            "2. Click **⋮ → Settings → Secrets**\n"
            "3. Paste this:"
        )
        st.code(
            'GEMINI_API_KEY = "AIzaSy-your-key-here"',
            language="toml",
        )
        st.markdown(
            "**Locally:**\n"
            "1. Create a `.streamlit` folder in your "
            "project root\n"
            "2. Create a file `.streamlit/secrets.toml`\n"
            "3. Paste the same line above"
        )
        st.markdown(
            "📎 Get a free key at "
            "[Google AI Studio]"
            "(https://aistudio.google.com/app/apikey)"
        )

    st.markdown("---")

    # ── Theme info ───────────────────────────────────────────────
    st.markdown("### 🎨 Theme")
    st.markdown(
        f"Currently using: **{st.session_state.theme}**"
    )
    st.caption("Change themes from the sidebar dropdown.")

    st.markdown("---")

    # ── Account stats ────────────────────────────────────────────
    st.markdown("### 📊 Account Stats")
    uid = st.session_state.user_id
    entries = get_entries(uid)
    analyses = get_analyses(uid, limit=1000)
    sessions = get_chat_sessions(uid)

    s1, s2, s3 = st.columns(3)
    s1.metric("Journal Entries", len(entries))
    s2.metric("Saved Analyses", len(analyses))
    s3.metric("Chat Sessions", len(sessions))

    if entries:
        dates = [
            e.get("entry_date", "")[:10]
            for e in entries
            if e.get("entry_date")
        ]
        if dates:
            st.caption(
                f"📅 First entry: {min(dates)}  |  "
                f"Latest: {max(dates)}"
            )

    st.markdown("---")

    # ── Danger zone ──────────────────────────────────────────────
    st.markdown("### 🗑️ Danger Zone")
    st.caption("These actions cannot be undone.")

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        if st.button(
            "🗑️ Delete All Entries",
            key="_del_entries",
        ):
            st.session_state["_confirm_del_entries"] = True

        if st.session_state.get("_confirm_del_entries"):
            st.warning(
                "Are you sure? This deletes all "
                "journal entries."
            )
            ca, cb = st.columns(2)
            with ca:
                if st.button("✅ Yes", key="_yes_e"):
                    import sqlite3 as _sq

                    c = _sq.connect(
                        os.path.join(
                            os.path.dirname(
                                os.path.abspath(__file__)
                            ),
                            "mindmirror.db",
                        )
                    )
                    c.execute(
                        "DELETE FROM journal_entries "
                        "WHERE user_id=?",
                        (uid,),
                    )
                    c.commit()
                    c.close()
                    st.session_state[
                        "_confirm_del_entries"
                    ] = False
                    st.success("Deleted.")
                    st.rerun()
            with cb:
                if st.button("❌ Cancel", key="_no_e"):
                    st.session_state[
                        "_confirm_del_entries"
                    ] = False
                    st.rerun()

    with col_d2:
        if st.button(
            "🗑️ Delete All Chats",
            key="_del_chats",
        ):
            st.session_state["_confirm_del_chats"] = True

        if st.session_state.get("_confirm_del_chats"):
            st.warning(
                "Are you sure? This deletes all "
                "chat history."
            )
            ca, cb = st.columns(2)
            with ca:
                if st.button("✅ Yes", key="_yes_c"):
                    import sqlite3 as _sq

                    c = _sq.connect(
                        os.path.join(
                            os.path.dirname(
                                os.path.abspath(__file__)
                            ),
                            "mindmirror.db",
                        )
                    )
                    c.execute(
                        "DELETE FROM chat_messages "
                        "WHERE user_id=?",
                        (uid,),
                    )
                    c.commit()
                    c.close()
                    st.session_state[
                        "_confirm_del_chats"
                    ] = False
                    st.success("Deleted.")
                    st.rerun()
            with cb:
                if st.button("❌ Cancel", key="_no_c"):
                    st.session_state[
                        "_confirm_del_chats"
                    ] = False
                    st.rerun()

    st.markdown("---")

    # ── About ────────────────────────────────────────────────────
    st.markdown("### ℹ️ About")
    st.markdown(
        "MindMirror AI is your personal behavioral analyst "
        "powered by **Google Gemini**. It combines local "
        "sentiment analysis with AI-powered deep pattern "
        "recognition to help you understand yourself better "
        "— your cycles, triggers, habits, and growth."
    )
    st.caption(
        "All data stored locally in SQLite. Journal text "
        "is only sent to Gemini when you explicitly run "
        "AI Analysis or use AI Chat."
    )


# ═══════════════════  🏠  WELCOME PAGE  ══════════════════════════

def page_welcome():
    st.markdown("# 🧠 Welcome to MindMirror AI")
    st.markdown(
        "### *Decode your mind. Discover your patterns.*"
    )
    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="mm-card"><h4>📝 Journal</h4>'
            "<p>Write daily entries, import past notes "
            "in bulk, and build a rich personal dataset "
            "that persists forever.</p></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="mm-card"><h4>🔬 Analyse</h4>'
            "<p>Run local & AI analysis to detect "
            "emotional cycles, triggers, cognitive "
            "patterns, and behavioral loops.</p></div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="mm-card"><h4>💬 Chat</h4>'
            "<p>Talk with a warm, perceptive AI companion "
            "about your patterns — across multiple "
            "saved sessions.</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("")
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(
            '<div class="mm-card"><h4>📊 Dashboard</h4>'
            "<p>Mood timelines, emotion charts, topic "
            "breakdown, streaks, and a mood calendar "
            "heatmap.</p></div>",
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            '<div class="mm-card"><h4>📂 Persistent</h4>'
            "<p>Every entry, analysis, and chat is saved. "
            "Come back days later — everything is "
            "still here.</p></div>",
            unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            '<div class="mm-card"><h4>🎨 7 Themes</h4>'
            "<p>Deep Ocean · Sakura · Forest · Cosmic "
            "Purple · Sunrise · Midnight · Clean "
            "Light</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(
        "👈 **Enter your name in the sidebar to begin.**"
    )


# ═══════════════════  🚦  MAIN ROUTER  ══════════════════════════

def main():
    if not st.session_state.logged_in:
        page_welcome()
        return

    router = {
        "📝 Journal": page_journal,
        "🔬 Analysis": page_analysis,
        "💬 AI Chat": page_chat,
        "📊 Dashboard": page_dashboard,
        "📂 History": page_history,
        "⚙️ Settings": page_settings,
    }
    page_fn = router.get(
        st.session_state.page, page_journal
    )
    page_fn()


if __name__ == "__main__":
    main()
