"""
post_queue.py
SQLite-backed queue for storing, scheduling, and tracking posts.
"""

import sqlite3
from datetime import datetime
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                tone        TEXT    NOT NULL,
                content     TEXT    NOT NULL,
                scheduled_at TEXT,
                status      TEXT    NOT NULL DEFAULT 'pending',
                tweet_id    TEXT,
                posted_at   TEXT,
                error       TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        conn.commit()
    print(f"[post_queue] Database ready: {DB_PATH}")


def add_posts(posts: list[dict], scheduled_times: list[str] = None):
    """
    Insert posts into the queue.

    Args:
        posts: List of {"tone": str, "content": str}
        scheduled_times: List of ISO datetime strings (one per post)
    """
    with get_conn() as conn:
        for i, post in enumerate(posts):
            sched = scheduled_times[i] if scheduled_times and i < len(scheduled_times) else None
            conn.execute(
                "INSERT INTO posts (tone, content, scheduled_at, status) VALUES (?, ?, ?, 'pending')",
                (post["tone"], post["content"], sched)
            )
        conn.commit()
    print(f"[post_queue] Added {len(posts)} posts to queue.")


def get_due_posts() -> list[dict]:
    """Return all pending posts whose scheduled_at time has passed."""
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM posts WHERE status='pending' AND scheduled_at <= ? ORDER BY scheduled_at",
            (now,)
        ).fetchall()
    return [dict(row) for row in rows]


def get_pending_posts() -> list[dict]:
    """Return all pending posts (for display)."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM posts WHERE status='pending' ORDER BY scheduled_at"
        ).fetchall()
    return [dict(row) for row in rows]


def get_all_posts(limit: int = 50) -> list[dict]:
    """Return recent posts for dashboard/review."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM posts ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def mark_posted(post_id: int, tweet_id: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE posts SET status='posted', tweet_id=?, posted_at=? WHERE id=?",
            (tweet_id, datetime.utcnow().isoformat(), post_id)
        )
        conn.commit()


def mark_failed(post_id: int, error: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE posts SET status='failed', error=? WHERE id=?",
            (error, post_id)
        )
        conn.commit()


def delete_post(post_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM posts WHERE id=?", (post_id,))
        conn.commit()


def update_content(post_id: int, new_content: str):
    with get_conn() as conn:
        conn.execute("UPDATE posts SET content=? WHERE id=?", (new_content, post_id))
        conn.commit()


def update_schedule(post_id: int, new_time: str):
    with get_conn() as conn:
        conn.execute("UPDATE posts SET scheduled_at=? WHERE id=?", (new_time, post_id))
        conn.commit()


def print_queue():
    """Pretty-print the current queue to console."""
    posts = get_pending_posts()
    if not posts:
        print("[post_queue] Queue is empty.")
        return
    print(f"\n{'='*70}")
    print(f"PENDING QUEUE ({len(posts)} posts)")
    print(f"{'='*70}")
    for p in posts:
        sched = p["scheduled_at"] or "unscheduled"
        print(f"  ID:{p['id']:3}  [{p['tone']:20}]  {sched}  |  {p['content'][:50]}...")
    print(f"{'='*70}\n")
