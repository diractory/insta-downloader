"""
#RADHEY — Lightweight SQLite Database
--------------------------------------
Tracks users (for /broadcast) and groups (for /gbroadcast + stats),
plus per-user warning counts per chat. Uses only the Python standard
library sqlite3 module, so there is nothing extra to install.
"""

import sqlite3
import threading
from config import DATABASE_FILE

_lock = threading.Lock()
_conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
_conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT
)
""")
_conn.execute("""
CREATE TABLE IF NOT EXISTS chats (
    chat_id INTEGER PRIMARY KEY,
    title TEXT
)
""")
_conn.execute("""
CREATE TABLE IF NOT EXISTS warns (
    chat_id INTEGER,
    user_id INTEGER,
    count INTEGER DEFAULT 0,
    PRIMARY KEY (chat_id, user_id)
)
""")
_conn.commit()


def add_user(user_id: int, username: str, first_name: str):
    with _lock:
        _conn.execute(
            "INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, first_name=excluded.first_name",
            (user_id, username or "", first_name or ""),
        )
        _conn.commit()


def add_chat(chat_id: int, title: str):
    with _lock:
        _conn.execute(
            "INSERT INTO chats (chat_id, title) VALUES (?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET title=excluded.title",
            (chat_id, title or ""),
        )
        _conn.commit()


def all_users():
    with _lock:
        return [row[0] for row in _conn.execute("SELECT user_id FROM users").fetchall()]


def all_chats():
    with _lock:
        return [row[0] for row in _conn.execute("SELECT chat_id FROM chats").fetchall()]


def stats():
    with _lock:
        u = _conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        c = _conn.execute("SELECT COUNT(*) FROM chats").fetchone()[0]
        return u, c


def add_warn(chat_id: int, user_id: int) -> int:
    with _lock:
        _conn.execute(
            "INSERT INTO warns (chat_id, user_id, count) VALUES (?, ?, 1) "
            "ON CONFLICT(chat_id, user_id) DO UPDATE SET count = count + 1",
            (chat_id, user_id),
        )
        _conn.commit()
        row = _conn.execute(
            "SELECT count FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id)
        ).fetchone()
        return row[0] if row else 1


def reset_warn(chat_id: int, user_id: int):
    with _lock:
        _conn.execute("DELETE FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        _conn.commit()


def get_warn(chat_id: int, user_id: int) -> int:
    with _lock:
        row = _conn.execute(
            "SELECT count FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id)
        ).fetchone()
        return row[0] if row else 0
