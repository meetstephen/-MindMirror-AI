# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — app.py  PART 1 of 3          ║
# ║  Imports · Config · Session State · Sidebar                     ║
# ╚══════════════════════════════════════════════════════════════════╝

import streamlit as st
import json, os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from database import (
    init_db, get_or_create_user, save_entry, get_entries, delete_entry,
    entry_count, get_sentiments_over_time, save_analysis, get_analyses,
    save_chat_msg, get_chat_msgs, get_chat_sessions, delete_chat_session,
)
from analyzer import (
    sentiment_score, detect_emotions, extract_entities, extract_topics,
    word_frequencies, local_analysis, ai_analysis, ai_chat, ai_reflection_prompts,
)
from themes import get_theme_css, get_plotly_colors, THEME_NAMES

# ── Page config (MUST be first Streamlit call) ───────────────────
st.set_page_config(
    page_title="MindMirror AI", page_icon="🧠", layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session-state defaults ───────────────────────────────────────
_DEFAULTS = {
    "user_id": None, "username": "", "logged_in": False,
    "page": "📝 Journal", "theme": "🌊 Deep Ocean",
    "api_key": "", "model": "gemini-2.0-flash",
    "chat_session": "default", "current_analysis": None,
    "batch_mode": False,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Initialise DB ────────────────────────────────────────────────
init_db()

# ── Apply selected theme ────────────────────────────────────────
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# ── Helper: Plotly layout matching theme ─────────────────────────
def _plotly_layout(fig, title=""):
    pc = get_plotly_colors(st.session_state.theme)
    fig.update_layout(
        title=title, plot_bgcolor=pc["paper"], paper_bgcolor=pc["paper"],
        font_color=pc["text"], title_font_color=pc["text"],
        xaxis=dict(gridcolor=pc["grid"], zerolinecolor=pc["grid"]),
        yaxis=dict(gridcolor=pc["grid"], zerolinecolor=pc["grid"]),
        margin=dict(l=40, r=20, t=50, b=40), legend=dict(font=dict(color=pc["text"])),
    )
    return fig

def _pcolors():
    return get_plotly_colors(st.session_state.theme)["colors"]

# ── Sidebar ──────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("## 🧠 MindMirror AI")
        st.caption("*Decode your mind. Discover your patterns.*")
        st.markdown("---")

        # ─ Login / profile ─
        if not st.session_state.logged_in:
            st.markdown("#### 👤 Get Started")
            uname = st.text_input("Your name:", key="_login_name",
                                  placeholder="e.g. Alex")
            if st.button("🚀 Enter MindMirror", use_container_width=True, type="primary"):
                if uname.strip():
                    st.session_state.username = uname.strip()
                    st.session_state.user_id = get_or_create_user(uname.strip())
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.warning("Please type a name.")
            return

        # ─ Logged-in sidebar ─
        ec = entry_count(st.session_state.user_id)
        st.markdown(f"#### 👤 {st.session_state.username}")
        st.caption(f"📊 {ec} journal entries saved")
        st.markdown("---")

        # Navigation
        st.markdown("#### 📍 Navigate")
        pages = ["📝 Journal", "🔬 Analysis", "💬 AI Chat",
                 "📊 Dashboard", "📂 History", "⚙️ Settings"]
        for p in pages:
            kind = "primary" if st.session_state.page == p else "secondary"
            if st.button(p, use_container_width=True, type=kind, key=f"nav_{p}"):
                st.session_state.page = p
                st.rerun()

        st.markdown("---")

        # Theme
        st.markdown("#### 🎨 Theme")
        idx = THEME_NAMES.index(st.session_state.theme) if st.session_state.theme in THEME_NAMES else 0
        theme = st.selectbox("Select:", THEME_NAMES, index=idx, key="_theme_sel",
                             label_visibility="collapsed")
        if theme != st.session_state.theme:
            st.session_state.theme = theme
            st.rerun()

        st.markdown("---")

        # Gemini API key
        st.markdown("#### 🔑 Gemini API Key")
        key = st.text_input("API key:", type="password", value=st.session_state.api_key,
                            key="_api", label_visibility="collapsed",
                            placeholder="AIza...")
        if key != st.session_state.api_key:
            st.session_state.api_key = key
        st.caption("✅ Key set" if st.session_state.api_key else "⚠️ Needed for AI features")

        # Gemini Model
                st.session_state.model = st.selectbox(
            "Model:", [
                "gemini-2.5-flash",
                "gemini-2.5-flash-lite",
                "gemini-2.0-flash",
                "gemini-2.0-flash-lite",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
            ],
            index=0, key="_model_sel",
        )

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

render_sidebar()
# ──────────────────────────────────────────────────────────────────
# END OF PART 1 — continue pasting Part 2 below this line
# ──────────────────────────────────────────────────────────────────
# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — app.py  PART 2 of 3  (Gemini Edition)         ║
# ║  Journal Page · Analysis Page · Chat Page                       ║
# ╚══════════════════════════════════════════════════════════════════╝

# ═══════════════════  📝  JOURNAL PAGE  ═══════════════════════════

def page_journal():
    st.markdown("# 📝 Journal")
    st.markdown("Write your thoughts, feelings, and daily reflections. MindMirror remembers everything for you.")
    st.markdown("---")

    tab_new, tab_batch, tab_entries = st.tabs(["✏️ New Entry", "📋 Batch Import", "📖 My Entries"])

    # ── New single entry ─────────────────────────────────────────
    with tab_new:
        col1, col2 = st.columns([3, 1])
        with col2:
            entry_date = st.date_input("Date:", value=datetime.now(), key="_jdate")
            entry_time = st.time_input("Time:", value=datetime.now().time(), key="_jtime")
        with col1:
            content = st.text_area(
                "What's on your mind?", height=200, key="_jcontent",
                placeholder="Today I felt… / I noticed that… / Something happened…",
            )
        if st.button("💾 Save Entry", type="primary", use_container_width=True, key="_jsave"):
            if content.strip():
                dt = datetime.combine(entry_date, entry_time).strftime("%Y-%m-%d %H:%M")
                sent = sentiment_score(content)
                emos = detect_emotions(content)
                tags = list(extract_topics(content).keys())
                save_entry(st.session_state.user_id, content.strip(), dt, sent,
                           emos if emos else None, tags if tags else None)
                st.success("✅ Entry saved!")
                st.balloons()
            else:
                st.warning("Write something first.")

    # ── Batch import ─────────────────────────────────────────────
    with tab_batch:
        st.markdown("Paste multiple entries separated by `---` on its own line. "
                    "Optionally start each entry with a date like `2025-03-20:`.")
        batch = st.text_area("Paste entries:", height=300, key="_jbatch",
                             placeholder="2025-03-20: I felt great today…\n---\n2025-03-21: Not so good…")
        if st.button("📥 Import All", type="primary", key="_jbatch_save"):
            if batch.strip():
                chunks = [c.strip() for c in batch.split("---") if c.strip()]
                count = 0
                for chunk in chunks:
                    m = __import__("re").match(r"^(\d{4}-\d{2}-\d{2})[:\s]*(.*)", chunk, __import__("re").S)
                    if m:
                        dt = m.group(1) + " 12:00"
                        text = m.group(2).strip()
                    else:
                        dt = datetime.now().strftime("%Y-%m-%d %H:%M")
                        text = chunk
                    if text:
                        sent = sentiment_score(text)
                        save_entry(st.session_state.user_id, text, dt, sent)
                        count += 1
                st.success(f"✅ Imported {count} entries!")
            else:
                st.warning("Paste some text first.")

    # ── Browse entries ───────────────────────────────────────────
    with tab_entries:
        entries = get_entries(st.session_state.user_id)
        if not entries:
            st.info("No entries yet. Start journaling! ✍️")
            return
        st.caption(f"Showing {len(entries)} entries (newest first)")
        for e in entries:
            sent = e.get("sentiment")
            mood = "😊" if sent and sent > 0.2 else ("😟" if sent and sent < -0.2 else "😐") if sent is not None else "📝"
            with st.expander(f"{mood}  {e['entry_date']}  —  {e['content'][:80]}…"):
                st.markdown(e["content"])
                tags_raw = e.get("tags")
                if tags_raw:
                    try:
                        tags_list = json.loads(tags_raw) if isinstance(tags_raw, str) else tags_raw
                        st.caption("Tags: " + ", ".join(f"`{t}`" for t in tags_list))
                    except Exception:
                        pass
                if sent is not None:
                    st.caption(f"Sentiment: {sent:+.2f}")
                if st.button("🗑️ Delete", key=f"del_{e['id']}"):
                    delete_entry(e["id"], st.session_state.user_id)
                    st.rerun()


# ═══════════════════  🔬  ANALYSIS PAGE  ═════════════════════════

def page_analysis():
    st.markdown("# 🔬 Pattern Analysis")
    st.markdown("Uncover hidden behavioral and emotional patterns from your journal.")
    st.markdown("---")

    entries = get_entries(st.session_state.user_id)
    if len(entries) < 2:
        st.warning("Write at least 2 journal entries before running an analysis.")
        return

    # ── Controls ─────────────────────────────────────────────────
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        n = st.slider("Entries to analyse:", 2, min(len(entries), 100),
                       min(len(entries), 20), key="_an_n")
    with col2:
        run_local = st.button("📊 Local Analysis", use_container_width=True, key="_an_local")
    with col3:
        run_ai = st.button("🤖 AI Deep Analysis", use_container_width=True, type="primary",
                           key="_an_ai",
                           disabled=not st.session_state.api_key)

    target = list(reversed(entries[:n]))  # chronological order

    # ── Local analysis ───────────────────────────────────────────
    if run_local or run_ai:
        la = local_analysis(target)
        if la:
            st.markdown("### 📊 Local Pattern Report")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Entries", la["entry_count"])
            avg = la["avg_sentiment"]
            m2.metric("Avg Sentiment", f"{avg:+.2f}",
                      delta="positive" if avg > 0.1 else ("negative" if avg < -0.1 else "neutral"))
            m3.metric("Emotions Found", la["emotion_diversity"])
            m4.metric("Topics", len(la["topics"]))

            # Sentiment chart
            if la["sentiments"]:
                df_s = pd.DataFrame(la["sentiments"])
                fig = px.line(df_s, x="date", y="score", markers=True,
                              color_discrete_sequence=_pcolors())
                fig = _plotly_layout(fig, "Sentiment Over Time")
                st.plotly_chart(fig, use_container_width=True)

            c1, c2 = st.columns(2)

            with c1:
                if la["emotions"]:
                    emo_counts = {k: len(v) for k, v in la["emotions"].items()}
                    fig = px.pie(names=list(emo_counts.keys()), values=list(emo_counts.values()),
                                 color_discrete_sequence=_pcolors())
                    fig = _plotly_layout(fig, "Emotion Distribution")
                    st.plotly_chart(fig, use_container_width=True)

            with c2:
                if la["topics"]:
                    fig = px.bar(x=list(la["topics"].values()), y=list(la["topics"].keys()),
                                 orientation="h", color_discrete_sequence=_pcolors())
                    fig = _plotly_layout(fig, "Topic Frequency")
                    st.plotly_chart(fig, use_container_width=True)

            c3, c4 = st.columns(2)
            with c3:
                if la["people"]:
                    st.markdown("**👥 People Mentioned**")
                    for name, cnt in la["people"]:
                        st.markdown(f"- **{name}** × {cnt}")
            with c4:
                if la["words"]:
                    st.markdown("**🔤 Top Words**")
                    wdf = pd.DataFrame(la["words"], columns=["word", "count"])
                    fig = px.bar(wdf.head(15), x="count", y="word", orientation="h",
                                 color_discrete_sequence=_pcolors())
                    fig = _plotly_layout(fig, "Word Frequency")
                    st.plotly_chart(fig, use_container_width=True)

            save_analysis(st.session_state.user_id, "local",
                          json.dumps(la, default=str))

    # ── AI deep analysis ─────────────────────────────────────────
    if run_ai:
        if not st.session_state.api_key:
            st.error("Please add your Gemini API key in the sidebar.")
            return
        la = local_analysis(target)
        with st.spinner("🧠 Gemini is analysing your patterns… this may take a moment."):
            result = ai_analysis(target, st.session_state.api_key,
                                 st.session_state.model, la)
        st.markdown("---")
        st.markdown("### 🤖 AI Deep Analysis Report")
        st.markdown(f'<div class="mm-card">{result}</div>', unsafe_allow_html=True)
        st.session_state.current_analysis = result
        save_analysis(st.session_state.user_id, "ai", result)
        st.success("Analysis saved to your history.")


# ═══════════════════  💬  AI CHAT PAGE  ══════════════════════════

def page_chat():
    st.markdown("# 💬 AI Insight Chat")
    st.markdown("Talk with MindMirror about your patterns, feelings, and insights.")
    st.markdown("---")

    if not st.session_state.api_key:
        st.warning("Add your Gemini API key in the sidebar to use AI Chat.")
        return

    uid = st.session_state.user_id

    # ── Session management ───────────────────────────────────────
    sessions = get_chat_sessions(uid)
    session_labels = [s["session_label"] for s in sessions] if sessions else ["default"]
    if "default" not in session_labels:
        session_labels.insert(0, "default")

    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        chosen = st.selectbox("Chat session:", session_labels,
                               index=session_labels.index(st.session_state.chat_session)
                               if st.session_state.chat_session in session_labels else 0,
                               key="_chat_sess")
        if chosen != st.session_state.chat_session:
            st.session_state.chat_session = chosen
            st.rerun()
    with col_s2:
        new_label = st.text_input("New session:", key="_new_sess", placeholder="e.g. March reflections")
        if st.button("➕", key="_new_sess_btn") and new_label.strip():
            st.session_state.chat_session = new_label.strip()
            st.rerun()
    with col_s3:
        if st.button("🗑️ Clear Chat", key="_clr_chat"):
            delete_chat_session(uid, st.session_state.chat_session)
            st.rerun()

    # ── Load history ─────────────────────────────────────────────
    db_msgs = get_chat_msgs(uid, st.session_state.chat_session)
    entries = get_entries(uid)

    for m in db_msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # ── Chat input ───────────────────────────────────────────────
    if prompt := st.chat_input("Ask about your patterns…"):
        with st.chat_message("user"):
            st.markdown(prompt)
        save_chat_msg(uid, "user", prompt, st.session_state.chat_session)

        history = [{"role": m["role"], "content": m["content"]} for m in db_msgs]
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                reply = ai_chat(prompt, entries, history,
                                st.session_state.api_key, st.session_state.model)
            st.markdown(reply)
        save_chat_msg(uid, "assistant", reply, st.session_state.chat_session)


# ──────────────────────────────────────────────────────────────────
# END OF PART 2 — continue pasting Part 3 below this line
# ──────────────────────────────────────────────────────────────────
# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — app.py  PART 3 of 3  (Gemini Edition)         ║
# ║  Dashboard · History · Settings · Main Router                   ║
# ╚══════════════════════════════════════════════════════════════════╝

# ═══════════════════  📊  DASHBOARD PAGE  ════════════════════════

def page_dashboard():
    st.markdown("# 📊 Insight Dashboard")
    st.markdown("A bird's-eye view of your emotional and behavioral landscape.")
    st.markdown("---")

    uid = st.session_state.user_id
    entries = get_entries(uid)
    if len(entries) < 2:
        st.info("Add more journal entries to unlock your dashboard.")
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

    dates = sorted(set(
        e.get("entry_date", "")[:10] for e in entries if e.get("entry_date")
    ))
    streak = 0
    if dates:
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
    m5.metric("🔥 Streak", f"{streak} day{'s' if streak != 1 else ''}")

    st.markdown("---")

    # ── Sentiment timeline ───────────────────────────────────────
    if la["sentiments"]:
        df = pd.DataFrame(la["sentiments"])
        fig = px.area(df, x="date", y="score", markers=True,
                      color_discrete_sequence=_pcolors(),
                      labels={"score": "Sentiment", "date": "Date"})
        fig = _plotly_layout(fig, "📈 Mood Over Time")
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        st.plotly_chart(fig, use_container_width=True)

    # ── Two-column charts ────────────────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        if la["emotions"]:
            emo_c = {k: len(v) for k, v in la["emotions"].items()}
            fig = px.bar(x=list(emo_c.keys()), y=list(emo_c.values()),
                         color=list(emo_c.keys()), color_discrete_sequence=_pcolors(),
                         labels={"x": "Emotion", "y": "Mentions"})
            fig = _plotly_layout(fig, "🎭 Emotion Frequency")
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if la["topics"]:
            fig = px.bar(x=list(la["topics"].values()), y=list(la["topics"].keys()),
                         orientation="h", color_discrete_sequence=_pcolors(),
                         labels={"x": "Mentions", "y": "Topic"})
            fig = _plotly_layout(fig, "🏷️ Topics Breakdown")
            st.plotly_chart(fig, use_container_width=True)

    # ── Day-of-week and time-of-day ──────────────────────────────
    c3, c4 = st.columns(2)
    with c3:
        if la["days"]:
            d_names = [d[0] for d in la["days"]]
            d_counts = [d[1] for d in la["days"]]
            fig = px.bar(x=d_names, y=d_counts, color_discrete_sequence=_pcolors(),
                         labels={"x": "Day", "y": "Mentions"})
            fig = _plotly_layout(fig, "📅 Day Mentions")
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        if la["times"]:
            t_names = [t[0] for t in la["times"]]
            t_counts = [t[1] for t in la["times"]]
            fig = px.pie(names=t_names, values=t_counts,
                         color_discrete_sequence=_pcolors())
            fig = _plotly_layout(fig, "🕐 Time-of-Day Mentions")
            st.plotly_chart(fig, use_container_width=True)

    # ── Word frequency ───────────────────────────────────────────
    if la["words"]:
        st.markdown("### 🔤 Most Used Words")
        wdf = pd.DataFrame(la["words"][:20], columns=["word", "count"])
        fig = px.bar(wdf, x="count", y="word", orientation="h",
                     color="count", color_continuous_scale="Viridis")
        fig = _plotly_layout(fig, "")
        fig.update_layout(showlegend=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    # ── People mentioned ─────────────────────────────────────────
    if la["people"]:
        st.markdown("### 👥 People Mentioned Most")
        pcols = st.columns(min(len(la["people"]), 5))
        for i, (name, cnt) in enumerate(la["people"][:5]):
            with pcols[i]:
                st.metric(name, f"{cnt}×")

    # ── AI Reflection Prompts ────────────────────────────────────
    st.markdown("---")
    if st.session_state.api_key and entries:
        st.markdown("### 💡 AI Reflection Prompts")
        st.caption("Personalised writing prompts based on your recent entries.")
        if st.button("✨ Generate Prompts", key="_dash_prompts"):
            with st.spinner("Generating with Gemini…"):
                prompts = ai_reflection_prompts(
                    entries, st.session_state.api_key, st.session_state.model
                )
            st.markdown(f'<div class="mm-card">{prompts}</div>',
                        unsafe_allow_html=True)
    elif not st.session_state.api_key:
        st.caption("💡 Add your Gemini key in the sidebar to unlock AI reflection prompts.")

    # ── Mood calendar heatmap ────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🗓️ Mood Calendar")
    sot = get_sentiments_over_time(uid)
    if sot and len(sot) >= 2:
        cal_df = pd.DataFrame(sot)
        cal_df["entry_date"] = pd.to_datetime(cal_df["entry_date"])
        cal_df["day"] = cal_df["entry_date"].dt.date
        daily = cal_df.groupby("day")["sentiment"].mean().reset_index()
        daily.columns = ["date", "mood"]
        daily["date"] = pd.to_datetime(daily["date"])
        daily["weekday"] = daily["date"].dt.day_name()
        daily["week"] = daily["date"].dt.isocalendar().week.astype(int)

        fig = px.scatter(daily, x="date", y="mood",
                         size=[abs(m) * 30 + 5 for m in daily["mood"]],
                         color="mood", color_continuous_scale="RdYlGn",
                         labels={"mood": "Sentiment", "date": "Date"},
                         hover_data=["weekday"])
        fig = _plotly_layout(fig, "")
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Not enough data for the mood calendar yet.")


# ═══════════════════  📂  HISTORY PAGE  ══════════════════════════

def page_history():
    st.markdown("# 📂 Saved Analyses & Activity")
    st.markdown("All your past analyses are saved here — even if you close the browser and come back days later.")
    st.markdown("---")

    uid = st.session_state.user_id

    tab_an, tab_ch, tab_ex = st.tabs(["🔬 Analyses", "💬 Chat History", "📤 Export"])

    # ── Past analyses ────────────────────────────────────────────
    with tab_an:
        analyses = get_analyses(uid, limit=50)
        if not analyses:
            st.info("No saved analyses yet. Run one from the 🔬 Analysis page.")
        else:
            st.caption(f"{len(analyses)} saved analyses")
            for a in analyses:
                a_type = "🤖 AI Analysis" if a["analysis_type"] == "ai" else "📊 Local Analysis"
                with st.expander(f"{a_type}  —  {a['created_at']}"):
                    result = a["result"]
                    if a["analysis_type"] == "local":
                        try:
                            data = json.loads(result)
                            st.json(data)
                        except (json.JSONDecodeError, TypeError):
                            st.markdown(str(result))
                    else:
                        st.markdown(result)

    # ── Chat history ─────────────────────────────────────────────
    with tab_ch:
        sessions = get_chat_sessions(uid)
        if not sessions:
            st.info("No chat sessions yet. Start a conversation on the 💬 AI Chat page.")
        else:
            for sess in sessions:
                label = sess["session_label"]
                with st.expander(
                    f"💬 {label}  —  {sess['started'][:16]}  —  {sess['msg_count']} messages"
                ):
                    msgs = get_chat_msgs(uid, label, limit=200)
                    for m in msgs:
                        icon = "🧑" if m["role"] == "user" else "🤖"
                        st.markdown(f"**{icon} {m['role'].title()}** ({m['created_at'][:16]})")
                        st.markdown(m["content"])
                        st.markdown("---")

    # ── Export ───────────────────────────────────────────────────
    with tab_ex:
        st.markdown("### 📤 Export Your Data")
        st.caption("Download all your journal entries and analyses.")

        entries = get_entries(uid)
        if entries:
            export_entries = []
            for e in entries:
                export_entries.append({
                    "date": e.get("entry_date", ""),
                    "content": e.get("content", ""),
                    "sentiment": e.get("sentiment"),
                    "tags": e.get("tags"),
                })
            entries_json = json.dumps(export_entries, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Download Journal (JSON)", entries_json,
                file_name=f"mindmirror_journal_{st.session_state.username}.json",
                mime="application/json", key="_exp_journal",
            )
            txt_lines = []
            for e in entries:
                txt_lines.append(f"[{e.get('entry_date','')}]")
                txt_lines.append(e.get("content", ""))
                txt_lines.append("")
            st.download_button(
                "📥 Download Journal (TXT)", "\n".join(txt_lines),
                file_name=f"mindmirror_journal_{st.session_state.username}.txt",
                mime="text/plain", key="_exp_journal_txt",
            )
        else:
            st.caption("No entries to export.")

        analyses = get_analyses(uid, limit=100)
        if analyses:
            an_export = []
            for a in analyses:
                an_export.append({
                    "type": a["analysis_type"],
                    "date": a["created_at"],
                    "result": a["result"],
                })
            an_json = json.dumps(an_export, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Download Analyses (JSON)", an_json,
                file_name=f"mindmirror_analyses_{st.session_state.username}.json",
                mime="application/json", key="_exp_analyses",
            )
        else:
            st.caption("No analyses to export.")


# ═══════════════════  ⚙️  SETTINGS PAGE  ═════════════════════════

def page_settings():
    st.markdown("# ⚙️ Settings")
    st.markdown("---")

    st.markdown("### 🎨 Theme Preview")
    current = st.session_state.theme
    st.markdown(f"Currently using: **{current}**")
    st.caption("Change the theme from the sidebar dropdown to see it applied instantly.")

    st.markdown("---")
    st.markdown("### 🤖 AI Configuration")
    st.markdown(f"**Model:** `{st.session_state.model}`")
    if st.session_state.api_key:
        st.markdown("**Gemini API Key:** ✅ Set (hidden)")
    else:
        st.markdown("**Gemini API Key:** ⚠️ Not set — AI features disabled")
        st.caption("Enter your Google Gemini API key in the sidebar to unlock AI-powered analysis and chat.")
        st.markdown(
            "📎 Get a free key at [Google AI Studio](https://aistudio.google.com/app/apikey)"
        )

    st.markdown("---")
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
        dates = [e.get("entry_date", "")[:10] for e in entries if e.get("entry_date")]
        if dates:
            st.caption(f"📅 First entry: {min(dates)}  |  Latest: {max(dates)}")

    st.markdown("---")
    st.markdown("### 🗑️ Danger Zone")
    st.caption("These actions cannot be undone.")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        if st.button("🗑️ Delete All Journal Entries", key="_del_entries"):
            st.session_state["_confirm_del_entries"] = True
        if st.session_state.get("_confirm_del_entries"):
            st.warning("Are you sure? This will delete all your journal entries.")
            ca, cb = st.columns(2)
            with ca:
                if st.button("✅ Yes, delete", key="_confirm_yes_e"):
                    import sqlite3 as _sq
                    conn = _sq.connect(
                        __import__("os").path.join(
                            __import__("os").path.dirname(
                                __import__("os").path.abspath(__file__)
                            ), "mindmirror.db"
                        )
                    )
                    conn.execute("DELETE FROM journal_entries WHERE user_id=?", (uid,))
                    conn.commit()
                    conn.close()
                    st.session_state["_confirm_del_entries"] = False
                    st.success("All entries deleted.")
                    st.rerun()
            with cb:
                if st.button("❌ Cancel", key="_cancel_del_e"):
                    st.session_state["_confirm_del_entries"] = False
                    st.rerun()

    with col_d2:
        if st.button("🗑️ Delete All Chat History", key="_del_chats"):
            st.session_state["_confirm_del_chats"] = True
        if st.session_state.get("_confirm_del_chats"):
            st.warning("Are you sure? This will delete all your chat history.")
            ca, cb = st.columns(2)
            with ca:
                if st.button("✅ Yes, delete", key="_confirm_yes_c"):
                    import sqlite3 as _sq
                    conn = _sq.connect(
                        __import__("os").path.join(
                            __import__("os").path.dirname(
                                __import__("os").path.abspath(__file__)
                            ), "mindmirror.db"
                        )
                    )
                    conn.execute("DELETE FROM chat_messages WHERE user_id=?", (uid,))
                    conn.commit()
                    conn.close()
                    st.session_state["_confirm_del_chats"] = False
                    st.success("All chats deleted.")
                    st.rerun()
            with cb:
                if st.button("❌ Cancel", key="_cancel_del_c"):
                    st.session_state["_confirm_del_chats"] = False
                    st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ About MindMirror AI")
    st.markdown(
        "MindMirror AI is a personal behavioral analyst powered by **Google Gemini**. "
        "It helps you discover hidden patterns in your thoughts and emotions by combining "
        "local sentiment analysis with AI-powered deep pattern recognition."
    )
    st.caption("All data stored locally in SQLite. Your journal never leaves your machine "
               "unless you run an AI analysis (sent to Google Gemini API).")


# ═══════════════════  🏠  WELCOME PAGE  ══════════════════════════

def page_welcome():
    st.markdown("# 🧠 Welcome to MindMirror AI")
    st.markdown("### *Decode your mind. Discover your patterns.*")
    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="mm-card">'
            "<h4>📝 Journal</h4>"
            "<p>Write daily entries, import past notes in bulk, and build a rich "
            "personal dataset.</p>"
            "</div>", unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="mm-card">'
            "<h4>🔬 Analyse</h4>"
            "<p>Run local & Gemini AI analysis to detect emotional cycles, "
            "triggers, and behavioral loops.</p>"
            "</div>", unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="mm-card">'
            "<h4>💬 Chat</h4>"
            "<p>Talk with your AI analyst about your patterns — it remembers "
            "every conversation.</p>"
            "</div>", unsafe_allow_html=True,
        )

    st.markdown("")
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown(
            '<div class="mm-card">'
            "<h4>📊 Dashboard</h4>"
            "<p>Visualise mood trends, emotion distributions, topic frequency, "
            "streaks, and a mood calendar.</p>"
            "</div>", unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            '<div class="mm-card">'
            "<h4>📂 History</h4>"
            "<p>Every analysis and chat is saved permanently. Come back days "
            "later and everything is still here.</p>"
            "</div>", unsafe_allow_html=True,
        )
    with c6:
        st.markdown(
            '<div class="mm-card">'
            "<h4>🎨 7 Themes</h4>"
            "<p>Deep Ocean, Sakura, Forest, Cosmic Purple, Sunrise, Midnight, "
            "and Clean Light.</p>"
            "</div>", unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("👈 **Enter your name in the sidebar to begin.**")
    st.caption("🔑 Get a free Gemini API key at [Google AI Studio](https://aistudio.google.com/app/apikey)")


# ═══════════════════  🚦  MAIN ROUTER  ══════════════════════════

def main():
    if not st.session_state.logged_in:
        page_welcome()
        return

    router = {
        "📝 Journal":   page_journal,
        "🔬 Analysis":  page_analysis,
        "💬 AI Chat":   page_chat,
        "📊 Dashboard": page_dashboard,
        "📂 History":   page_history,
        "⚙️ Settings":  page_settings,
    }

    page_fn = router.get(st.session_state.page, page_journal)
    page_fn()


# ── Run ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
