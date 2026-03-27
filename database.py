import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "mindmirror.db"
)


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init_db():
    c = _conn()
    cur = c.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            entry_date TEXT,
            sentiment REAL,
            emotions TEXT,
            tags TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            analysis_type TEXT NOT NULL,
            result TEXT NOT NULL,
            entry_ids TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_label TEXT DEFAULT 'default',
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE INDEX IF NOT EXISTS idx_je_user
            ON journal_entries(user_id);
        CREATE INDEX IF NOT EXISTS idx_an_user
            ON analyses(user_id);
        CREATE INDEX IF NOT EXISTS idx_cm_user
            ON chat_messages(user_id);
    """)
    c.commit()
    c.close()


# ── Users ────────────────────────────────────────────────────────

def get_or_create_user(username: str) -> int:
    c = _conn()
    row = c.execute(
        "SELECT id FROM users WHERE username=?", (username,)
    ).fetchone()
    if row:
        uid = row["id"]
    else:
        cur = c.execute(
            "INSERT INTO users(username) VALUES(?)", (username,)
        )
        c.commit()
        uid = cur.lastrowid
    c.close()
    return uid


# ── Journal Entries ──────────────────────────────────────────────

def save_entry(user_id, content, entry_date=None,
               sentiment=None, emotions=None, tags=None):
    c = _conn()
    if entry_date is None:
        entry_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute(
        "INSERT INTO journal_entries"
        "(user_id, content, entry_date, sentiment, emotions, tags) "
        "VALUES(?,?,?,?,?,?)",
        (
            user_id, content, entry_date, sentiment,
            json.dumps(emotions) if emotions else None,
            json.dumps(tags) if tags else None,
        ),
    )
    c.commit()
    eid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    c.close()
    return eid


def get_entries(user_id, limit=None):
    c = _conn()
    q = ("SELECT * FROM journal_entries "
         "WHERE user_id=? ORDER BY entry_date DESC")
    if limit:
        q += f" LIMIT {int(limit)}"
    rows = c.execute(q, (user_id,)).fetchall()
    c.close()
    return [dict(r) for r in rows]


def delete_entry(entry_id, user_id):
    c = _conn()
    c.execute(
        "DELETE FROM journal_entries WHERE id=? AND user_id=?",
        (entry_id, user_id),
    )
    c.commit()
    c.close()


def entry_count(user_id):
    c = _conn()
    n = c.execute(
        "SELECT COUNT(*) FROM journal_entries WHERE user_id=?",
        (user_id,),
    ).fetchone()[0]
    c.close()
    return n


def get_sentiments_over_time(user_id):
    c = _conn()
    rows = c.execute(
        "SELECT entry_date, sentiment FROM journal_entries "
        "WHERE user_id=? AND sentiment IS NOT NULL "
        "ORDER BY entry_date",
        (user_id,),
    ).fetchall()
    c.close()
    return [dict(r) for r in rows]


# ── Analyses ─────────────────────────────────────────────────────

def save_analysis(user_id, analysis_type, result, entry_ids=None):
    c = _conn()
    c.execute(
        "INSERT INTO analyses"
        "(user_id, analysis_type, result, entry_ids) "
        "VALUES(?,?,?,?)",
        (
            user_id, analysis_type,
            result if isinstance(result, str) else json.dumps(result),
            json.dumps(entry_ids) if entry_ids else None,
        ),
    )
    c.commit()
    c.close()


def get_analyses(user_id, limit=20):
    c = _conn()
    rows = c.execute(
        "SELECT * FROM analyses WHERE user_id=? "
        "ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    c.close()
    return [dict(r) for r in rows]


# ── Chat Messages ────────────────────────────────────────────────

def save_chat_msg(user_id, role, content, session_label="default"):
    c = _conn()
    c.execute(
        "INSERT INTO chat_messages"
        "(user_id, session_label, role, content) "
        "VALUES(?,?,?,?)",
        (user_id, session_label, role, content),
    )
    c.commit()
    c.close()


def get_chat_msgs(user_id, session_label="default", limit=100):
    c = _conn()
    rows = c.execute(
        "SELECT role, content, created_at FROM chat_messages "
        "WHERE user_id=? AND session_label=? "
        "ORDER BY created_at ASC LIMIT ?",
        (user_id, session_label, limit),
    ).fetchall()
    c.close()
    return [dict(r) for r in rows]


def get_chat_sessions(user_id):
    c = _conn()
    rows = c.execute(
        "SELECT DISTINCT session_label, "
        "MIN(created_at) as started, "
        "COUNT(*) as msg_count "
        "FROM chat_messages WHERE user_id=? "
        "GROUP BY session_label "
        "ORDER BY started DESC",
        (user_id,),
    ).fetchall()
    c.close()
    return [dict(r) for r in rows]


def delete_chat_session(user_id, session_label="default"):
    c = _conn()
    c.execute(
        "DELETE FROM chat_messages "
        "WHERE user_id=? AND session_label=?",
        (user_id, session_label),
    )
    c.commit()
    c.close()
