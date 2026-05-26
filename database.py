# ═══════════════════════════════════════════════════════════════════
#  database.py — MindMirror AI · SQLite persistence layer
# ═══════════════════════════════════════════════════════════════════

import sqlite3
import json
import os
import hashlib
import secrets
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "mindmirror.db"


# ───────────────────────────────────────────────────────────────────
#  Connection helper
# ───────────────────────────────────────────────────────────────────

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


# ───────────────────────────────────────────────────────────────────
#  Schema initialisation (idempotent)
# ───────────────────────────────────────────────────────────────────

def init_db():
    conn = _connect()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            entry_date TEXT,
            sentiment REAL,
            emotions TEXT,
            tags TEXT,
            mood_score REAL,
            energy_level INTEGER,
            body_zones TEXT,
            distortion_tags TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            analysis_type TEXT,
            result TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            session_label TEXT DEFAULT 'default',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS psyche_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            values_json TEXT,
            support_style TEXT,
            therapeutic_mode_default TEXT,
            empathy_level INTEGER,
            custom_lexicon_json TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS mood_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            checkin_type TEXT,
            scores_json TEXT,
            total_score INTEGER,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            progress REAL DEFAULT 0,
            target_metric TEXT,
            target_value REAL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS growth_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resilience REAL,
            self_awareness REAL,
            emotional_regulation REAL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS crisis_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            trigger_snippet TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS rate_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            call_type TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            attempt_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()

    # Run migrations for existing databases
    migrate_db()


# ───────────────────────────────────────────────────────────────────
#  Database Migration (add columns safely to existing tables)
# ───────────────────────────────────────────────────────────────────

def migrate_db():
    """Safely add password_hash column to existing users table if missing."""
    conn = _connect()
    cursor = conn.execute("PRAGMA table_info(users)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "password_hash" not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        conn.commit()
    conn.close()


# ───────────────────────────────────────────────────────────────────
#  Password Hashing Utilities
# ───────────────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a random salt."""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )
    return f"{salt}:{pw_hash.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored PBKDF2 hash."""
    try:
        salt, pw_hash_hex = stored_hash.split(":", 1)
        pw_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        )
        return secrets.compare_digest(pw_hash.hex(), pw_hash_hex)
    except (ValueError, AttributeError):
        return False


# ───────────────────────────────────────────────────────────────────
#  Users
# ───────────────────────────────────────────────────────────────────

def get_or_create_user(username: str) -> int:
    """Get existing user or create one without a password.
    Deprecated: Use create_user/verify_user for new auth flows.
    Kept for backward compatibility with internal operations."""
    conn = _connect()
    row = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if row:
        uid = row["id"]
    else:
        cur = conn.execute(
            "INSERT INTO users (username) VALUES (?)", (username,)
        )
        conn.commit()
        uid = cur.lastrowid
    conn.close()
    return uid


def user_exists(username: str) -> bool:
    """Check if a user with the given username exists."""
    conn = _connect()
    row = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return row is not None


def create_user(username: str, password: str) -> int:
    """Create a new user with a hashed password. Returns the user id."""
    pw_hash = _hash_password(password)
    conn = _connect()
    cur = conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, pw_hash),
    )
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    return uid


def verify_user(username: str, password: str) -> Optional[int]:
    """Verify username and password. Returns user id if valid, None otherwise."""
    conn = _connect()
    row = conn.execute(
        "SELECT id, password_hash FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    stored_hash = row["password_hash"]
    if not stored_hash:
        # Legacy user without password - cannot authenticate via password
        return None
    if _verify_password(password, stored_hash):
        return row["id"]
    return None


# ───────────────────────────────────────────────────────────────────
#  Journal Entries
# ───────────────────────────────────────────────────────────────────

def save_entry(
    user_id,
    content,
    entry_date=None,
    sentiment=None,
    emotions=None,
    tags=None,
    mood_score=None,
    energy_level=None,
    body_zones=None,
    distortion_tags=None,
):
    conn = _connect()
    conn.execute(
        """INSERT INTO entries
           (user_id, content, entry_date, sentiment, emotions,
            tags, mood_score, energy_level, body_zones, distortion_tags)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            user_id,
            content,
            entry_date or datetime.now().strftime("%Y-%m-%d %H:%M"),
            sentiment,
            json.dumps(emotions, default=str) if emotions is not None else None,
            json.dumps(tags, default=str) if tags is not None else None,
            mood_score,
            energy_level,
            json.dumps(body_zones, default=str) if body_zones is not None else None,
            json.dumps(distortion_tags, default=str) if distortion_tags is not None else None,
        ),
    )
    conn.commit()
    conn.close()


def get_entries(user_id, limit=50) -> List[Dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM entries WHERE user_id = ? ORDER BY entry_date DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_entry(entry_id, user_id):
    conn = _connect()
    conn.execute(
        "DELETE FROM entries WHERE id = ? AND user_id = ?",
        (entry_id, user_id),
    )
    conn.commit()
    conn.close()


def entry_count(user_id) -> int:
    conn = _connect()
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM entries WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return row["cnt"] if row else 0


def get_sentiments_over_time(user_id) -> List[Dict]:
    conn = _connect()
    rows = conn.execute(
        """SELECT entry_date, sentiment FROM entries
           WHERE user_id = ? AND sentiment IS NOT NULL
           ORDER BY entry_date ASC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [
        {"date": r["entry_date"][:10], "score": r["sentiment"]}
        for r in rows
    ]


# ───────────────────────────────────────────────────────────────────
#  Analyses
# ───────────────────────────────────────────────────────────────────

def save_analysis(user_id, analysis_type, result):
    conn = _connect()
    conn.execute(
        "INSERT INTO analyses (user_id, analysis_type, result) VALUES (?, ?, ?)",
        (user_id, analysis_type, result),
    )
    conn.commit()
    conn.close()


def get_analyses(user_id, limit=20) -> List[Dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_analysis(user_id, analysis_type="ai") -> Optional[str]:
    """Get the most recent analysis of a given type."""
    conn = _connect()
    row = conn.execute(
        "SELECT result FROM analyses WHERE user_id = ? AND analysis_type = ? ORDER BY created_at DESC LIMIT 1",
        (user_id, analysis_type),
    ).fetchone()
    conn.close()
    return row["result"] if row else None


def get_recent_entries_text(user_id, limit=5) -> str:
    """Get concatenated recent entry content for quick context building."""
    conn = _connect()
    rows = conn.execute(
        "SELECT content FROM entries WHERE user_id = ? ORDER BY entry_date DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return " ".join(r["content"] for r in rows) if rows else ""


# ───────────────────────────────────────────────────────────────────
#  Chat Messages
# ───────────────────────────────────────────────────────────────────

def save_chat_msg(user_id, role, content, session_label="default"):
    conn = _connect()
    conn.execute(
        """INSERT INTO chat_messages (user_id, role, content, session_label)
           VALUES (?, ?, ?, ?)""",
        (user_id, role, content, session_label),
    )
    conn.commit()
    conn.close()


def get_chat_msgs(user_id, session_label="default") -> List[Dict]:
    conn = _connect()
    rows = conn.execute(
        """SELECT * FROM chat_messages
           WHERE user_id = ? AND session_label = ?
           ORDER BY created_at ASC""",
        (user_id, session_label),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_chat_sessions(user_id) -> List[Dict]:
    conn = _connect()
    rows = conn.execute(
        """SELECT session_label,
                  COUNT(*) AS message_count,
                  MAX(created_at) AS last_message_at
           FROM chat_messages
           WHERE user_id = ?
           GROUP BY session_label
           ORDER BY last_message_at DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_chat_session(user_id, session_label):
    conn = _connect()
    conn.execute(
        "DELETE FROM chat_messages WHERE user_id = ? AND session_label = ?",
        (user_id, session_label),
    )
    conn.commit()
    conn.close()


# ───────────────────────────────────────────────────────────────────
#  Psyche Profiles
# ───────────────────────────────────────────────────────────────────

def save_psyche_profile(
    user_id,
    values=None,
    support_style=None,
    therapeutic_mode_default=None,
    empathy_level=None,
    custom_lexicon=None,
):
    conn = _connect()
    existing = conn.execute(
        "SELECT id FROM psyche_profiles WHERE user_id = ?", (user_id,)
    ).fetchone()

    values_json = json.dumps(values) if values is not None else None
    lexicon_json = json.dumps(custom_lexicon) if custom_lexicon is not None else None

    if existing:
        conn.execute(
            """UPDATE psyche_profiles
               SET values_json = ?,
                   support_style = ?,
                   therapeutic_mode_default = ?,
                   empathy_level = ?,
                   custom_lexicon_json = ?,
                   updated_at = datetime('now')
               WHERE user_id = ?""",
            (values_json, support_style, therapeutic_mode_default,
             empathy_level, lexicon_json, user_id),
        )
    else:
        conn.execute(
            """INSERT INTO psyche_profiles
               (user_id, values_json, support_style,
                therapeutic_mode_default, empathy_level, custom_lexicon_json)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, values_json, support_style,
             therapeutic_mode_default, empathy_level, lexicon_json),
        )
    conn.commit()
    conn.close()


def get_psyche_profile(user_id) -> Optional[Dict]:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM psyche_profiles WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    d = dict(row)

    try:
        d["values"] = json.loads(d.get("values_json") or "[]")
    except (json.JSONDecodeError, TypeError):
        d["values"] = []

    try:
        d["custom_lexicon"] = json.loads(d.get("custom_lexicon_json") or "{}")
    except (json.JSONDecodeError, TypeError):
        d["custom_lexicon"] = {}

    return d


# ───────────────────────────────────────────────────────────────────
#  Mood Check-ins
# ───────────────────────────────────────────────────────────────────

def save_mood_checkin(user_id, checkin_type, scores, total_score):
    conn = _connect()
    conn.execute(
        """INSERT INTO mood_checkins (user_id, checkin_type, scores_json, total_score)
           VALUES (?, ?, ?, ?)""",
        (user_id, checkin_type, json.dumps(scores, default=str), total_score),
    )
    conn.commit()
    conn.close()


def get_mood_checkins(user_id, limit=30) -> List[Dict]:
    conn = _connect()
    rows = conn.execute(
        """SELECT * FROM mood_checkins
           WHERE user_id = ?
           ORDER BY created_at DESC LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        try:
            d["scores"] = json.loads(d.get("scores_json") or "[]")
        except (json.JSONDecodeError, TypeError):
            d["scores"] = []
        results.append(d)
    return results


# ───────────────────────────────────────────────────────────────────
#  Goals
# ───────────────────────────────────────────────────────────────────

def save_goal(user_id, title, target_metric=None, target_value=None):
    conn = _connect()
    conn.execute(
        """INSERT INTO goals (user_id, title, target_metric, target_value)
           VALUES (?, ?, ?, ?)""",
        (user_id, title, target_metric, target_value),
    )
    conn.commit()
    conn.close()


def get_goals(user_id, status=None) -> List[Dict]:
    conn = _connect()
    if status:
        rows = conn.execute(
            """SELECT * FROM goals
               WHERE user_id = ? AND status = ?
               ORDER BY created_at DESC""",
            (user_id, status),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_goal_progress(goal_id, progress, status="active"):
    conn = _connect()
    conn.execute(
        """UPDATE goals
           SET progress = ?, status = ?, updated_at = datetime('now')
           WHERE id = ?""",
        (progress, status, goal_id),
    )
    conn.commit()
    conn.close()


# ───────────────────────────────────────────────────────────────────
#  Growth Metrics
# ───────────────────────────────────────────────────────────────────

def save_growth_metrics(user_id, resilience, self_awareness, emotional_regulation):
    conn = _connect()
    conn.execute(
        """INSERT INTO growth_metrics
           (user_id, resilience, self_awareness, emotional_regulation)
           VALUES (?, ?, ?, ?)""",
        (user_id, resilience, self_awareness, emotional_regulation),
    )
    conn.commit()
    conn.close()


def get_growth_metrics(user_id) -> List[Dict]:
    conn = _connect()
    rows = conn.execute(
        """SELECT * FROM growth_metrics
           WHERE user_id = ?
           ORDER BY created_at DESC LIMIT 30""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ───────────────────────────────────────────────────────────────────
#  Crisis Logs
# ───────────────────────────────────────────────────────────────────

def log_crisis_event(user_id, trigger_snippet=None, notes=None):
    conn = _connect()
    conn.execute(
        """INSERT INTO crisis_logs (user_id, trigger_snippet, notes)
           VALUES (?, ?, ?)""",
        (user_id, trigger_snippet, notes),
    )
    conn.commit()
    conn.close()


def get_crisis_logs(user_id) -> List[Dict]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM crisis_logs WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ───────────────────────────────────────────────────────────────────
#  Daily Check-In Helpers
# ───────────────────────────────────────────────────────────────────

def has_checked_in_today(user_id) -> bool:
    """Return True if the user has a daily_checkin for today (UTC)."""
    conn = _connect()
    row = conn.execute(
        "SELECT id FROM mood_checkins WHERE user_id = ? AND checkin_type = 'daily_checkin' AND date(created_at) = date('now')",
        (user_id,),
    ).fetchone()
    conn.close()
    return row is not None


def get_today_checkin(user_id) -> Optional[Dict]:
    """Return the user's daily check-in for today (UTC), or None."""
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM mood_checkins WHERE user_id = ? AND checkin_type = 'daily_checkin' AND date(created_at) = date('now') ORDER BY created_at DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()
    if row:
        d = dict(row)
        try:
            d["scores"] = json.loads(d.get("scores_json") or "[]")
        except (json.JSONDecodeError, TypeError):
            d["scores"] = []
        return d
    return None


# ───────────────────────────────────────────────────────────────────
#  Rate Limiting (server-side, per-user)
# ───────────────────────────────────────────────────────────────────

def record_ai_call(user_id) -> None:
    """Record an AI call timestamp for the given user."""
    conn = _connect()
    conn.execute(
        "INSERT INTO rate_limits (user_id, call_type) VALUES (?, 'ai_call')",
        (user_id,),
    )
    conn.commit()
    conn.close()


def count_recent_ai_calls(user_id, minutes: int = 10) -> int:
    """Count AI calls by a user within the last N minutes."""
    conn = _connect()
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM rate_limits WHERE user_id = ? AND call_type = 'ai_call' AND created_at > datetime('now', ?)",
        (user_id, f"-{minutes} minutes"),
    ).fetchone()
    conn.close()
    return row["cnt"] if row else 0


# ───────────────────────────────────────────────────────────────────
#  Login Attempt Tracking (brute-force protection)
# ───────────────────────────────────────────────────────────────────

def record_login_attempt(username: str) -> None:
    """Record a failed login attempt for the given username."""
    conn = _connect()
    conn.execute(
        "INSERT INTO login_attempts (username) VALUES (?)",
        (username,),
    )
    conn.commit()
    conn.close()


def count_recent_login_attempts(username: str, minutes: int = 15) -> int:
    """Count failed login attempts for a username within the last N minutes."""
    conn = _connect()
    row = conn.execute(
        "SELECT COUNT(*) AS cnt FROM login_attempts WHERE username = ? AND attempt_at > datetime('now', ?)",
        (username, f"-{minutes} minutes"),
    ).fetchone()
    conn.close()
    return row["cnt"] if row else 0
