# ╔══════════════════════════════════════════════════════════════════╗
# ║  MindMirror AI — database.py  (v3 · Enhanced)                  ║
# ║  CHUNK 1 of 10                                                  ║
# ║  Full database layer: users, entries, analyses, chat, goals,    ║
# ║  wellbeing check-ins, cognitive distortions, growth metrics,    ║
# ║  feedback, skill completions, and privacy settings              ║
# ╚══════════════════════════════════════════════════════════════════╝

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "mindmirror.db"
)


# ── Connection helper ────────────────────────────────────────────
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _row_to_dict(row):
    """Convert sqlite3.Row to plain dict."""
    if row is None:
        return None
    return dict(row)


def _rows_to_dicts(rows):
    return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════════
#  SCHEMA INITIALISATION & MIGRATION
# ══════════════════════════════════════════════════════════════════

def init_db():
    conn = _conn()
    c = conn.cursor()

    # ── Users ────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            username            TEXT UNIQUE NOT NULL,
            created_at          TEXT DEFAULT (datetime('now')),
            psyche_profile      TEXT,
            preferred_tone      TEXT DEFAULT 'balanced',
            empathy_level       REAL DEFAULT 0.5,
            onboarding_complete INTEGER DEFAULT 0,
            custom_emotions     TEXT,
            privacy_settings    TEXT DEFAULT '{}',
            last_active         TEXT
        )
    """)

    # ── Journal entries ──────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id               INTEGER NOT NULL,
            content               TEXT NOT NULL,
            entry_date            TEXT NOT NULL,
            sentiment             REAL,
            emotions              TEXT,
            tags                  TEXT,
            mood_score            REAL,
            energy_level          REAL,
            body_sensations       TEXT,
            entry_type            TEXT DEFAULT 'freeform',
            cognitive_distortions TEXT,
            created_at            TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Analyses ─────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            analysis_type TEXT NOT NULL,
            result        TEXT,
            created_at    TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Chat messages ────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            role          TEXT NOT NULL,
            content       TEXT NOT NULL,
            session_label TEXT DEFAULT 'default',
            chat_mode     TEXT DEFAULT 'open',
            created_at    TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Goals ────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            goal_text    TEXT NOT NULL,
            category     TEXT DEFAULT 'general',
            target_date  TEXT,
            status       TEXT DEFAULT 'active',
            created_at   TEXT DEFAULT (datetime('now')),
            completed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Goal check-ins ───────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS goal_checkins (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id        INTEGER NOT NULL,
            user_id        INTEGER NOT NULL,
            progress_note  TEXT,
            progress_value REAL,
            created_at     TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (goal_id) REFERENCES goals(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Wellbeing check-ins (PHQ-9 / GAD-7 style) ───────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS wellbeing_checkins (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            checkin_type   TEXT NOT NULL,
            scores         TEXT NOT NULL,
            total_score    REAL,
            interpretation TEXT,
            created_at     TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Growth metrics (resilience, regulation, awareness) ───────
    c.execute("""
        CREATE TABLE IF NOT EXISTS growth_metrics (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            metric_type  TEXT NOT NULL,
            score        REAL NOT NULL,
            details      TEXT,
            period_start TEXT,
            period_end   TEXT,
            created_at   TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── User feedback on insights ────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            feedback_type TEXT NOT NULL,
            target_id     INTEGER,
            rating        INTEGER,
            comment       TEXT,
            created_at    TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Skill / module completions ───────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS skill_completions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            skill_id     TEXT NOT NULL,
            skill_name   TEXT NOT NULL,
            category     TEXT DEFAULT 'general',
            completed_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Surprise / pattern-break events ──────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS surprise_events (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            description TEXT NOT NULL,
            entry_id    INTEGER,
            dismissed   INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (entry_id) REFERENCES journal_entries(id)
        )
    """)

    # Run migrations for existing databases
    _migrate(conn)

    conn.commit()
    conn.close()


def _migrate(conn):
    """Add new columns to existing tables for backward compat."""
    c = conn.cursor()

    # -- journal_entries migrations --
    existing = {
        row[1]
        for row in c.execute(
            "PRAGMA table_info(journal_entries)"
        ).fetchall()
    }
    je_cols = {
        "mood_score": "REAL",
        "energy_level": "REAL",
        "body_sensations": "TEXT",
        "entry_type": "TEXT DEFAULT 'freeform'",
        "cognitive_distortions": "TEXT",
    }
    for col, dtype in je_cols.items():
        if col not in existing:
            try:
                c.execute(
                    f"ALTER TABLE journal_entries "
                    f"ADD COLUMN {col} {dtype}"
                )
            except sqlite3.OperationalError:
                pass

    # -- users migrations --
    existing_u = {
        row[1]
        for row in c.execute(
            "PRAGMA table_info(users)"
        ).fetchall()
    }
    u_cols = {
        "psyche_profile": "TEXT",
        "preferred_tone": "TEXT DEFAULT 'balanced'",
        "empathy_level": "REAL DEFAULT 0.5",
        "onboarding_complete": "INTEGER DEFAULT 0",
        "custom_emotions": "TEXT",
        "privacy_settings": "TEXT DEFAULT '{}'",
        "last_active": "TEXT",
    }
    for col, dtype in u_cols.items():
        if col not in existing_u:
            try:
                c.execute(
                    f"ALTER TABLE users ADD COLUMN {col} {dtype}"
                )
            except sqlite3.OperationalError:
                pass

    # -- chat_messages migrations --
    existing_cm = {
        row[1]
        for row in c.execute(
            "PRAGMA table_info(chat_messages)"
        ).fetchall()
    }
    if "chat_mode" not in existing_cm:
        try:
            c.execute(
                "ALTER TABLE chat_messages "
                "ADD COLUMN chat_mode TEXT DEFAULT 'open'"
            )
        except sqlite3.OperationalError:
            pass

    conn.commit()


# ══════════════════════════════════════════════════════════════════
#  USER FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def get_or_create_user(username):
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    row = c.fetchone()
    if row:
        uid = row["id"]
        c.execute(
            "UPDATE users SET last_active=? WHERE id=?",
            (datetime.now().isoformat(), uid),
        )
    else:
        c.execute(
            "INSERT INTO users (username, last_active) VALUES (?,?)",
            (username, datetime.now().isoformat()),
        )
        uid = c.lastrowid
    conn.commit()
    conn.close()
    return uid


def get_user(user_id):
    conn = _conn()
    row = conn.execute(
        "SELECT * FROM users WHERE id=?", (user_id,)
    ).fetchone()
    conn.close()
    return _row_to_dict(row)


def save_psyche_profile(user_id, profile_data):
    conn = _conn()
    conn.execute(
        "UPDATE users SET psyche_profile=?, onboarding_complete=1 WHERE id=?",
        (json.dumps(profile_data), user_id),
    )
    conn.commit()
    conn.close()


def get_psyche_profile(user_id):
    conn = _conn()
    row = conn.execute(
        "SELECT psyche_profile FROM users WHERE id=?", (user_id,)
    ).fetchone()
    conn.close()
    if row and row["psyche_profile"]:
        try:
            return json.loads(row["psyche_profile"])
        except (json.JSONDecodeError, TypeError):
            return None
    return None


def is_onboarding_complete(user_id):
    conn = _conn()
    row = conn.execute(
        "SELECT onboarding_complete FROM users WHERE id=?",
        (user_id,),
    ).fetchone()
    conn.close()
    return bool(row and row["onboarding_complete"])


def update_user_preferences(user_id, **kwargs):
    """Update user columns: preferred_tone, empathy_level,
    custom_emotions, privacy_settings."""
    conn = _conn()
    allowed = {
        "preferred_tone", "empathy_level",
        "custom_emotions", "privacy_settings",
    }
    for key, val in kwargs.items():
        if key in allowed:
            if isinstance(val, (dict, list)):
                val = json.dumps(val)
            conn.execute(
                f"UPDATE users SET {key}=? WHERE id=?",
                (val, user_id),
            )
    conn.commit()
    conn.close()


def get_privacy_settings(user_id):
    conn = _conn()
    row = conn.execute(
        "SELECT privacy_settings FROM users WHERE id=?",
        (user_id,),
    ).fetchone()
    conn.close()
    if row and row["privacy_settings"]:
        try:
            return json.loads(row["privacy_settings"])
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


def get_custom_emotions(user_id):
    conn = _conn()
    row = conn.execute(
        "SELECT custom_emotions FROM users WHERE id=?",
        (user_id,),
    ).fetchone()
    conn.close()
    if row and row["custom_emotions"]:
        try:
            return json.loads(row["custom_emotions"])
        except (json.JSONDecodeError, TypeError):
            return []
    return []


# ══════════════════════════════════════════════════════════════════
#  JOURNAL ENTRY FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def save_entry(
    user_id, content, entry_date, sentiment,
    emotions=None, tags=None,
    mood_score=None, energy_level=None,
    body_sensations=None, entry_type="freeform",
    cognitive_distortions=None,
):
    conn = _conn()
    conn.execute(
        """INSERT INTO journal_entries
           (user_id, content, entry_date, sentiment,
            emotions, tags, mood_score, energy_level,
            body_sensations, entry_type, cognitive_distortions)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            user_id,
            content,
            entry_date,
            sentiment,
            json.dumps(emotions) if emotions else None,
            json.dumps(tags) if isinstance(tags, list) else tags,
            mood_score,
            energy_level,
            json.dumps(body_sensations)
            if isinstance(body_sensations, (dict, list))
            else body_sensations,
            entry_type,
            json.dumps(cognitive_distortions)
            if isinstance(cognitive_distortions, (dict, list))
            else cognitive_distortions,
        ),
    )
    conn.commit()
    entry_id = conn.execute(
        "SELECT last_insert_rowid()"
    ).fetchone()[0]
    conn.close()
    return entry_id


def get_entries(user_id, limit=200):
    conn = _conn()
    rows = conn.execute(
        """SELECT * FROM journal_entries
           WHERE user_id=?
           ORDER BY entry_date DESC, id DESC
           LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_entry_by_id(entry_id, user_id):
    conn = _conn()
    row = conn.execute(
        "SELECT * FROM journal_entries WHERE id=? AND user_id=?",
        (entry_id, user_id),
    ).fetchone()
    conn.close()
    return _row_to_dict(row)


def delete_entry(entry_id, user_id):
    conn = _conn()
    conn.execute(
        "DELETE FROM journal_entries WHERE id=? AND user_id=?",
        (entry_id, user_id),
    )
    conn.commit()
    conn.close()


def entry_count(user_id):
    conn = _conn()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM journal_entries WHERE user_id=?",
        (user_id,),
    ).fetchone()
    conn.close()
    return row["cnt"] if row else 0


def get_sentiments_over_time(user_id, limit=500):
    conn = _conn()
    rows = conn.execute(
        """SELECT entry_date, sentiment, mood_score, energy_level
           FROM journal_entries
           WHERE user_id=? AND sentiment IS NOT NULL
           ORDER BY entry_date ASC
           LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_entries_in_range(user_id, start_date, end_date):
    conn = _conn()
    rows = conn.execute(
        """SELECT * FROM journal_entries
           WHERE user_id=?
             AND entry_date >= ?
             AND entry_date <= ?
           ORDER BY entry_date ASC""",
        (user_id, start_date, end_date),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_recent_mood_scores(user_id, limit=30):
    conn = _conn()
    rows = conn.execute(
        """SELECT entry_date, mood_score, energy_level, sentiment
           FROM journal_entries
           WHERE user_id=? AND mood_score IS NOT NULL
           ORDER BY entry_date DESC
           LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


# ══════════════════════════════════════════════════════════════════
#  ANALYSIS FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def save_analysis(user_id, analysis_type, result):
    conn = _conn()
    conn.execute(
        """INSERT INTO analyses (user_id, analysis_type, result)
           VALUES (?,?,?)""",
        (user_id, analysis_type, result),
    )
    conn.commit()
    conn.close()


def get_analyses(user_id, limit=50):
    conn = _conn()
    rows = conn.execute(
        """SELECT * FROM analyses
           WHERE user_id=?
           ORDER BY created_at DESC
           LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


# ══════════════════════════════════════════════════════════════════
#  CHAT FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def save_chat_msg(user_id, role, content, session_label="default",
                  chat_mode="open"):
    conn = _conn()
    conn.execute(
        """INSERT INTO chat_messages
           (user_id, role, content, session_label, chat_mode)
           VALUES (?,?,?,?,?)""",
        (user_id, role, content, session_label, chat_mode),
    )
    conn.commit()
    conn.close()


def get_chat_msgs(user_id, session_label="default", limit=100):
    conn = _conn()
    rows = conn.execute(
        """SELECT * FROM chat_messages
           WHERE user_id=? AND session_label=?
           ORDER BY created_at ASC
           LIMIT ?""",
        (user_id, session_label, limit),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_chat_sessions(user_id):
    conn = _conn()
    rows = conn.execute(
        """SELECT session_label,
                  MIN(created_at) as started,
                  COUNT(*) as msg_count
           FROM chat_messages
           WHERE user_id=?
           GROUP BY session_label
           ORDER BY started DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def delete_chat_session(user_id, session_label):
    conn = _conn()
    conn.execute(
        "DELETE FROM chat_messages WHERE user_id=? AND session_label=?",
        (user_id, session_label),
    )
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════════
#  GOAL FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def save_goal(user_id, goal_text, category="general",
              target_date=None):
    conn = _conn()
    conn.execute(
        """INSERT INTO goals
           (user_id, goal_text, category, target_date)
           VALUES (?,?,?,?)""",
        (user_id, goal_text, category, target_date),
    )
    conn.commit()
    goal_id = conn.execute(
        "SELECT last_insert_rowid()"
    ).fetchone()[0]
    conn.close()
    return goal_id


def get_goals(user_id, active_only=True):
    conn = _conn()
    query = "SELECT * FROM goals WHERE user_id=?"
    if active_only:
        query += " AND status='active'"
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, (user_id,)).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def update_goal_status(goal_id, user_id, status):
    conn = _conn()
    extra = ""
    params = [status, goal_id, user_id]
    if status == "completed":
        extra = ", completed_at=?"
        params = [status, datetime.now().isoformat(),
                  goal_id, user_id]
    conn.execute(
        f"UPDATE goals SET status=?{extra} WHERE id=? AND user_id=?",
        params,
    )
    conn.commit()
    conn.close()


def save_goal_checkin(goal_id, user_id, progress_note,
                      progress_value=None):
    conn = _conn()
    conn.execute(
        """INSERT INTO goal_checkins
           (goal_id, user_id, progress_note, progress_value)
           VALUES (?,?,?,?)""",
        (goal_id, user_id, progress_note, progress_value),
    )
    conn.commit()
    conn.close()


def get_goal_checkins(goal_id, limit=50):
    conn = _conn()
    rows = conn.execute(
        """SELECT * FROM goal_checkins
           WHERE goal_id=?
           ORDER BY created_at DESC
           LIMIT ?""",
        (goal_id, limit),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


# ══════════════════════════════════════════════════════════════════
#  WELLBEING CHECK-IN FUNCTIONS (PHQ-9 / GAD-7 style)
# ══════════════════════════════════════════════════════════════════

def save_wellbeing_checkin(user_id, checkin_type, scores,
                           total_score, interpretation=""):
    conn = _conn()
    conn.execute(
        """INSERT INTO wellbeing_checkins
           (user_id, checkin_type, scores, total_score, interpretation)
           VALUES (?,?,?,?,?)""",
        (
            user_id,
            checkin_type,
            json.dumps(scores),
            total_score,
            interpretation,
        ),
    )
    conn.commit()
    conn.close()


def get_wellbeing_checkins(user_id, checkin_type=None, limit=50):
    conn = _conn()
    if checkin_type:
        rows = conn.execute(
            """SELECT * FROM wellbeing_checkins
               WHERE user_id=? AND checkin_type=?
               ORDER BY created_at DESC LIMIT ?""",
            (user_id, checkin_type, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT * FROM wellbeing_checkins
               WHERE user_id=?
               ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


# ══════════════════════════════════════════════════════════════════
#  GROWTH METRICS
# ══════════════════════════════════════════════════════════════════

def save_growth_metric(user_id, metric_type, score,
                       details=None, period_start=None,
                       period_end=None):
    conn = _conn()
    conn.execute(
        """INSERT INTO growth_metrics
           (user_id, metric_type, score, details,
            period_start, period_end)
           VALUES (?,?,?,?,?,?)""",
        (
            user_id,
            metric_type,
            score,
            json.dumps(details) if isinstance(details, dict) else details,
            period_start,
            period_end,
        ),
    )
    conn.commit()
    conn.close()


def get_growth_metrics(user_id, metric_type=None, limit=50):
    conn = _conn()
    if metric_type:
        rows = conn.execute(
            """SELECT * FROM growth_metrics
               WHERE user_id=? AND metric_type=?
               ORDER BY created_at DESC LIMIT ?""",
            (user_id, metric_type, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT * FROM growth_metrics
               WHERE user_id=?
               ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


# ══════════════════════════════════════════════════════════════════
#  USER FEEDBACK
# ══════════════════════════════════════════════════════════════════

def save_feedback(user_id, feedback_type, target_id=None,
                  rating=None, comment=None):
    conn = _conn()
    conn.execute(
        """INSERT INTO user_feedback
           (user_id, feedback_type, target_id, rating, comment)
           VALUES (?,?,?,?,?)""",
        (user_id, feedback_type, target_id, rating, comment),
    )
    conn.commit()
    conn.close()


def get_feedback(user_id, feedback_type=None, limit=100):
    conn = _conn()
    if feedback_type:
        rows = conn.execute(
            """SELECT * FROM user_feedback
               WHERE user_id=? AND feedback_type=?
               ORDER BY created_at DESC LIMIT ?""",
            (user_id, feedback_type, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT * FROM user_feedback
               WHERE user_id=?
               ORDER BY created_at DESC LIMIT ?""",
            (user_id, limit),
        ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


# ══════════════════════════════════════════════════════════════════
#  SKILL COMPLETIONS
# ══════════════════════════════════════════════════════════════════

def save_skill_completion(user_id, skill_id, skill_name,
                          category="general"):
    conn = _conn()
    conn.execute(
        """INSERT INTO skill_completions
           (user_id, skill_id, skill_name, category)
           VALUES (?,?,?,?)""",
        (user_id, skill_id, skill_name, category),
    )
    conn.commit()
    conn.close()


def get_skill_completions(user_id, category=None):
    conn = _conn()
    if category:
        rows = conn.execute(
            """SELECT * FROM skill_completions
               WHERE user_id=? AND category=?
               ORDER BY completed_at DESC""",
            (user_id, category),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT * FROM skill_completions
               WHERE user_id=?
               ORDER BY completed_at DESC""",
            (user_id,),
        ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def is_skill_completed(user_id, skill_id):
    conn = _conn()
    row = conn.execute(
        """SELECT id FROM skill_completions
           WHERE user_id=? AND skill_id=?""",
        (user_id, skill_id),
    ).fetchone()
    conn.close()
    return row is not None


# ══════════════════════════════════════════════════════════════════
#  SURPRISE / PATTERN-BREAK EVENTS
# ══════════════════════════════════════════════════════════════════

def save_surprise_event(user_id, description, entry_id=None):
    conn = _conn()
    conn.execute(
        """INSERT INTO surprise_events
           (user_id, description, entry_id)
           VALUES (?,?,?)""",
        (user_id, description, entry_id),
    )
    conn.commit()
    conn.close()


def get_surprise_events(user_id, undismissed_only=True, limit=20):
    conn = _conn()
    query = "SELECT * FROM surprise_events WHERE user_id=?"
    if undismissed_only:
        query += " AND dismissed=0"
    query += " ORDER BY created_at DESC LIMIT ?"
    rows = conn.execute(query, (user_id, limit)).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def dismiss_surprise_event(event_id, user_id):
    conn = _conn()
    conn.execute(
        "UPDATE surprise_events SET dismissed=1 WHERE id=? AND user_id=?",
        (event_id, user_id),
    )
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════════
#  AGGREGATE / ANALYTICS HELPERS
# ══════════════════════════════════════════════════════════════════

def get_emotion_cooccurrence(user_id, limit=200):
    """Return entries with parsed emotion lists for network graph."""
    conn = _conn()
    rows = conn.execute(
        """SELECT emotions, entry_date FROM journal_entries
           WHERE user_id=? AND emotions IS NOT NULL
           ORDER BY entry_date DESC LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    results = []
    for r in rows:
        try:
            emos = json.loads(r["emotions"])
            if isinstance(emos, dict):
                emos = list(emos.keys())
            results.append({
                "emotions": emos,
                "date": r["entry_date"],
            })
        except (json.JSONDecodeError, TypeError):
            pass
    return results


def get_entries_with_distortions(user_id, limit=100):
    conn = _conn()
    rows = conn.execute(
        """SELECT id, entry_date, content, cognitive_distortions
           FROM journal_entries
           WHERE user_id=? AND cognitive_distortions IS NOT NULL
           ORDER BY entry_date DESC LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    results = []
    for r in rows:
        try:
            dist = json.loads(r["cognitive_distortions"])
            if dist:
                results.append({
                    "id": r["id"],
                    "date": r["entry_date"],
                    "content": r["content"],
                    "distortions": dist,
                })
        except (json.JSONDecodeError, TypeError):
            pass
    return results


def get_entry_cadence(user_id, days=30):
    """Return daily entry counts for the last N days."""
    conn = _conn()
    rows = conn.execute(
        """SELECT DATE(entry_date) as day, COUNT(*) as cnt
           FROM journal_entries
           WHERE user_id=?
             AND entry_date >= DATE('now', ?)
           GROUP BY DATE(entry_date)
           ORDER BY day ASC""",
        (user_id, f"-{days} days"),
    ).fetchall()
    conn.close()
    return _rows_to_dicts(rows)


def get_topic_sentiment_correlation(user_id, limit=200):
    """Return entries with both tags and sentiment for correlation."""
    conn = _conn()
    rows = conn.execute(
        """SELECT tags, sentiment, entry_date
           FROM journal_entries
           WHERE user_id=?
             AND tags IS NOT NULL
             AND sentiment IS NOT NULL
           ORDER BY entry_date DESC LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    results = []
    for r in rows:
        try:
            tags = json.loads(r["tags"])
            if isinstance(tags, list) and tags:
                results.append({
                    "tags": tags,
                    "sentiment": r["sentiment"],
                    "date": r["entry_date"],
                })
        except (json.JSONDecodeError, TypeError):
            pass
    return results


# ══════════════════════════════════════════════════════════════════
#  BULK / DANGER ZONE
# ══════════════════════════════════════════════════════════════════

def delete_all_entries(user_id):
    conn = _conn()
    conn.execute(
        "DELETE FROM journal_entries WHERE user_id=?",
        (user_id,),
    )
    conn.commit()
    conn.close()


def delete_all_chats(user_id):
    conn = _conn()
    conn.execute(
        "DELETE FROM chat_messages WHERE user_id=?",
        (user_id,),
    )
    conn.commit()
    conn.close()


def delete_all_user_data(user_id):
    """Nuclear option — deletes everything for a user."""
    conn = _conn()
    tables = [
        "journal_entries", "analyses", "chat_messages",
        "goals", "goal_checkins", "wellbeing_checkins",
        "growth_metrics", "user_feedback",
        "skill_completions", "surprise_events",
    ]
    for t in tables:
        conn.execute(
            f"DELETE FROM {t} WHERE user_id=?", (user_id,)
        )
    conn.commit()
    conn.close()


def export_all_data(user_id):
    """Export everything as a dict (for JSON download)."""
    conn = _conn()
    data = {}
    tables = [
        "journal_entries", "analyses", "chat_messages",
        "goals", "goal_checkins", "wellbeing_checkins",
        "growth_metrics", "user_feedback",
        "skill_completions", "surprise_events",
    ]
    for t in tables:
        rows = conn.execute(
            f"SELECT * FROM {t} WHERE user_id=?",
            (user_id,),
        ).fetchall()
        data[t] = _rows_to_dicts(rows)

    user_row = conn.execute(
        "SELECT * FROM users WHERE id=?", (user_id,)
    ).fetchone()
    data["user"] = _row_to_dict(user_row)
    conn.close()
    return data
