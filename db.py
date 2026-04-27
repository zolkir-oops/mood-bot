import sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = "mood.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                emoji    TEXT    NOT NULL,
                text     TEXT    DEFAULT '',
                created_at TEXT  NOT NULL
            )
        """)
        conn.commit()


def add_entry(emoji: str, text: str = "", dt: Optional[datetime] = None) -> int:
    if dt is None:
        dt = datetime.now()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO entries (emoji, text, created_at) VALUES (?, ?, ?)",
            (emoji, text, dt.isoformat())
        )
        conn.commit()
        return cur.lastrowid


def get_entry(entry_id: int):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM entries WHERE id = ?", (entry_id,)
        ).fetchone()


def update_entry_text(entry_id: int, text: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE entries SET text = ? WHERE id = ?", (text, entry_id)
        )
        conn.commit()


def delete_entry(entry_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()


def get_entries_for_month(year: int, month: int) -> list:
    start = f"{year:04d}-{month:02d}-01"
    # last day: next month minus 1 day
    if month == 12:
        end = f"{year + 1:04d}-01-01"
    else:
        end = f"{year:04d}-{month + 1:02d}-01"

    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM entries WHERE created_at >= ? AND created_at < ? ORDER BY created_at",
            (start, end)
        ).fetchall()
    return rows


def get_entries_for_day(year: int, month: int, day: int) -> list:
    prefix = f"{year:04d}-{month:02d}-{day:02d}"
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM entries WHERE created_at LIKE ? ORDER BY created_at",
            (prefix + "%",)
        ).fetchall()
    return rows
