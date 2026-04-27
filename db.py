import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Optional
 
DATABASE_URL = os.environ["DATABASE_URL"]
 
 
def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
 
 
def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id         SERIAL PRIMARY KEY,
                    user_id    BIGINT NOT NULL,
                    emoji      TEXT   NOT NULL,
                    text       TEXT   DEFAULT '',
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_entries_user_month
                ON entries (user_id, created_at)
            """)
        conn.commit()
 
 
def add_entry(user_id: int, emoji: str, text: str = "", dt=None) -> int:
    if dt is None:
        dt = datetime.now()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO entries (user_id, emoji, text, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
                (user_id, emoji, text, dt)
            )
            row = cur.fetchone()
        conn.commit()
        return row["id"]
 
 
def get_entry(entry_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM entries WHERE id = %s", (entry_id,))
            return cur.fetchone()
 
 
def update_entry_text(entry_id: int, text: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE entries SET text = %s WHERE id = %s", (text, entry_id))
        conn.commit()
 
 
def delete_entry(entry_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM entries WHERE id = %s", (entry_id,))
        conn.commit()
 
 
def get_entries_for_month(user_id: int, year: int, month: int) -> list:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM entries
                WHERE user_id = %s
                  AND EXTRACT(YEAR  FROM created_at) = %s
                  AND EXTRACT(MONTH FROM created_at) = %s
                ORDER BY created_at
            """, (user_id, year, month))
            return cur.fetchall()
 
 
def get_entries_for_day(user_id: int, year: int, month: int, day: int) -> list:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM entries
                WHERE user_id = %s
                  AND EXTRACT(YEAR  FROM created_at) = %s
                  AND EXTRACT(MONTH FROM created_at) = %s
                  AND EXTRACT(DAY   FROM created_at) = %s
                ORDER BY created_at
            """, (user_id, year, month, day))
            return cur.fetchall()
