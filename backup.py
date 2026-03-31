# ═══════════════════════════════════════════════════════════════════
#  backup.py — MindMirror AI · Persistence & Backup/Restore
#  Solves Streamlit Cloud's ephemeral storage problem by letting
#  users export & re-import their full database via JSON.
# ═══════════════════════════════════════════════════════════════════

import json
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from database import (
    get_entries,
    save_entry,
    get_analyses,
    save_analysis,
    get_chat_msgs,
    get_chat_sessions,
    save_chat_msg,
    save_psyche_profile,
    get_psyche_profile,
    get_mood_checkins,
    save_mood_checkin,
    get_goals,
    save_goal,
    update_goal_progress,
    save_growth_metrics,
    get_growth_metrics,
    entry_count,
)


# ───────────────────────────────────────────────────────────────────
#  EXPORT — full user data → JSON dict
# ───────────────────────────────────────────────────────────────────

def _safe_json_loads(value):
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return value


def export_user_data(user_id: int, username: str) -> Dict[str, Any]:
    """Export all user data to a JSON-serialisable dictionary."""
    entries = get_entries(user_id, limit=10000)
    analyses = get_analyses(user_id, limit=1000)
    goals = get_goals(user_id)
    checkins = get_mood_checkins(user_id, limit=5000)
    sessions = get_chat_sessions(user_id)
    profile = get_psyche_profile(user_id)
    growth = get_growth_metrics(user_id)

    # Collect all chat messages
    all_chats = {}
    for s in sessions:
        label = s.get("session_label", "default")
        msgs = get_chat_msgs(user_id, label)
        all_chats[label] = [
            {
                "role": m["role"],
                "content": m["content"],
                "created_at": m.get("created_at", ""),
            }
            for m in msgs
        ]

    return {
        "_mindmirror_backup": True,
        "_version": 1,
        "export_date": datetime.now().isoformat(),
        "username": username,
        "profile": profile,
        "entries": [
            {
                "content": e.get("content", ""),
                "entry_date": e.get("entry_date", ""),
                "sentiment": e.get("sentiment"),
                "emotions": _safe_json_loads(e.get("emotions")),
                "tags": _safe_json_loads(e.get("tags")),
                "mood_score": e.get("mood_score"),
                "energy_level": e.get("energy_level"),
                "body_zones": _safe_json_loads(e.get("body_zones")),
                "distortion_tags": _safe_json_loads(e.get("distortion_tags")),
            }
            for e in entries
        ],
        "analyses": [
            {
                "analysis_type": a.get("analysis_type", ""),
                "result": a.get("result", ""),
                "created_at": a.get("created_at", ""),
            }
            for a in analyses
        ],
        "chat_sessions": all_chats,
        "goals": [
            {
                "title": g.get("title", ""),
                "status": g.get("status", "active"),
                "progress": g.get("progress", 0),
                "target_metric": g.get("target_metric"),
                "target_value": g.get("target_value"),
            }
            for g in (goals or [])
        ],
        "mood_checkins": [
            {
                "checkin_type": c.get("checkin_type", ""),
                "scores": c.get("scores", []),
                "total_score": c.get("total_score", 0),
            }
            for c in checkins
        ],
        "growth_metrics": [
            {
                "resilience": g.get("resilience"),
                "self_awareness": g.get("self_awareness"),
                "emotional_regulation": g.get("emotional_regulation"),
            }
            for g in growth
        ],
    }


# ───────────────────────────────────────────────────────────────────
#  IMPORT — JSON dict → database
# ───────────────────────────────────────────────────────────────────

def import_user_data(user_id: int, data: Dict[str, Any]) -> Dict[str, int]:
    """Import user data from a previously exported JSON backup.
    Returns a summary dict with counts of imported items."""

    counts = {
        "entries": 0,
        "analyses": 0,
        "chat_messages": 0,
        "goals": 0,
        "checkins": 0,
        "growth_metrics": 0,
        "profile": 0,
    }

    # ── Profile ──────────────────────────────────────────────────
    profile = data.get("profile")
    if profile and isinstance(profile, dict):
        values = profile.get("values")
        if isinstance(values, str):
            try:
                values = json.loads(values)
            except Exception:
                values = ["Growth"]

        custom_lexicon = profile.get("custom_lexicon")
        if isinstance(custom_lexicon, str):
            try:
                custom_lexicon = json.loads(custom_lexicon)
            except Exception:
                custom_lexicon = {}

        save_psyche_profile(
            user_id=user_id,
            values=values or ["Growth"],
            support_style=profile.get("support_style", "Balanced"),
            therapeutic_mode_default=profile.get("therapeutic_mode_default", "open"),
            empathy_level=profile.get("empathy_level", 7),
            custom_lexicon=custom_lexicon,
        )
        counts["profile"] = 1

    # ── Entries ──────────────────────────────────────────────────
    for entry in data.get("entries", []):
        if not entry.get("content", "").strip():
            continue
        save_entry(
            user_id=user_id,
            content=entry["content"],
            entry_date=entry.get("entry_date"),
            sentiment=entry.get("sentiment"),
            emotions=entry.get("emotions"),
            tags=entry.get("tags"),
            mood_score=entry.get("mood_score"),
            energy_level=entry.get("energy_level"),
            body_zones=entry.get("body_zones"),
            distortion_tags=entry.get("distortion_tags"),
        )
        counts["entries"] += 1

    # ── Analyses ─────────────────────────────────────────────────
    for a in data.get("analyses", []):
        if a.get("result"):
            save_analysis(
                user_id,
                a.get("analysis_type", "imported"),
                a["result"],
            )
            counts["analyses"] += 1

    # ── Chat Sessions ────────────────────────────────────────────
    chat_sessions = data.get("chat_sessions", {})
    for label, messages in chat_sessions.items():
        for msg in messages:
            if msg.get("role") and msg.get("content"):
                save_chat_msg(
                    user_id,
                    msg["role"],
                    msg["content"],
                    label,
                )
                counts["chat_messages"] += 1

    # ── Goals ────────────────────────────────────────────────────
    for g in data.get("goals", []):
        if g.get("title"):
            save_goal(
                user_id,
                g["title"],
                target_metric=g.get("target_metric"),
                target_value=g.get("target_value"),
            )
            counts["goals"] += 1

    # ── Mood Check-ins ───────────────────────────────────────────
    for c in data.get("mood_checkins", []):
        if c.get("checkin_type"):
            save_mood_checkin(
                user_id,
                c["checkin_type"],
                c.get("scores", []),
                c.get("total_score", 0),
            )
            counts["checkins"] += 1

    # ── Growth Metrics ───────────────────────────────────────────
    for g in data.get("growth_metrics", []):
        res = g.get("resilience")
        sa = g.get("self_awareness")
        er = g.get("emotional_regulation")
        if res is not None and sa is not None and er is not None:
            save_growth_metrics(user_id, res, sa, er)
            counts["growth_metrics"] += 1

    return counts


def validate_backup_file(data: Any) -> bool:
    """Check if uploaded JSON looks like a valid MindMirror backup."""
    if not isinstance(data, dict):
        return False
    if data.get("_mindmirror_backup") is True:
        return True
    # Also accept exports from the History page (no _mindmirror_backup flag)
    if "entries" in data and "username" in data:
        return True
    return False


# ───────────────────────────────────────────────────────────────────
#  PERSISTENCE WARNING BANNER
# ───────────────────────────────────────────────────────────────────

def show_persistence_warning():
    """Show a dismissible warning about ephemeral storage.
    Only shown once per session, and only if data exists."""

    if st.session_state.get("_persistence_warning_dismissed"):
        return

    uid = st.session_state.get("user_id")
    if not uid:
        return

    count = entry_count(uid)
    if count == 0:
        return

    # Check if user has ever been warned this session
    last_backup_hint = st.session_state.get("_last_backup_hint")
    if last_backup_hint:
        return

    st.session_state._last_backup_hint = True

    st.warning(
        f"💾 **You have {count} journal entries.** Streamlit Cloud storage "
        f"can reset on redeploy. Download a backup from **📂 History → Export** "
        f"or use the **Restore** tab to re-import one.",
        icon="💾",
    )


def show_backup_reminder_if_needed():
    """Show a gentle backup reminder if the user has enough data
    and hasn't backed up recently."""

    if st.session_state.get("_backup_reminded"):
        return

    uid = st.session_state.get("user_id")
    if not uid:
        return

    count = entry_count(uid)

    # Remind at milestones: 5, 15, 30, 50, 100
    milestones = {5, 15, 30, 50, 100}
    if count not in milestones:
        return

    st.session_state._backup_reminded = True

    st.info(
        f"📦 **Milestone: {count} entries!** Great progress. "
        f"Consider downloading a backup from **📂 History → Export** "
        f"to keep your data safe across deploys.",
        icon="📦",
    )


# ───────────────────────────────────────────────────────────────────
#  RESTORE WIDGET  (drop into Settings or History page)
# ───────────────────────────────────────────────────────────────────

def show_restore_widget(user_id: int):
    """Render a file uploader + restore button for importing backups."""

    st.markdown("### 📥 Restore from Backup")
    st.caption(
        "Upload a previously exported MindMirror JSON file to restore "
        "your entries, analyses, chats, goals, and profile. "
        "This **adds** data — it won't delete anything already here."
    )

    uploaded = st.file_uploader(
        "Upload your MindMirror backup (.json):",
        type=["json"],
        key="_restore_upload",
    )

    if uploaded is not None:
        try:
            raw = uploaded.read().decode("utf-8")
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            st.error("❌ Invalid JSON file. Please upload a valid MindMirror export.")
            return

        if not validate_backup_file(data):
            st.error(
                "❌ This doesn't look like a MindMirror backup. "
                "Expected a JSON file with 'entries' and 'username' keys."
            )
            return

        # Show preview
        st.success("✅ Valid backup file detected!")

        preview_cols = st.columns(4)
        preview_cols[0].metric("Entries", len(data.get("entries", [])))
        preview_cols[1].metric("Analyses", len(data.get("analyses", [])))
        preview_cols[2].metric("Goals", len(data.get("goals", [])))

        chat_count = sum(
            len(msgs) for msgs in data.get("chat_sessions", {}).values()
        )
        preview_cols[3].metric("Chat Msgs", chat_count)

        export_date = data.get("export_date", "unknown")
        st.caption(f"Exported: {export_date}")

        backup_user = data.get("username", "unknown")
        current_user = st.session_state.get("username", "")
        if backup_user != current_user:
            st.warning(
                f"⚠️ This backup was created by **{backup_user}** "
                f"but you're logged in as **{current_user}**. "
                f"Data will be imported into your current account."
            )

        st.markdown("")
        if st.button(
            "📥 Restore All Data",
            type="primary",
            key="_restore_go",
            use_container_width=True,
        ):
            with st.spinner("Restoring your data…"):
                counts = import_user_data(user_id, data)

            st.success(
                f"✅ Restore complete!\n\n"
                f"📝 {counts['entries']} entries · "
                f"📊 {counts['analyses']} analyses · "
                f"💬 {counts['chat_messages']} chat messages · "
                f"🎯 {counts['goals']} goals · "
                f"🩺 {counts['checkins']} check-ins · "
                f"📈 {counts['growth_metrics']} growth snapshots"
            )

            # Reload profile if restored
            if counts["profile"]:
                profile = get_psyche_profile(user_id)
                if profile:
                    st.session_state.psyche_profile = profile
                    st.session_state.onboarding_complete = True

            st.balloons()
            st.rerun()
