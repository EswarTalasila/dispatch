"""Local SQLite store of matched jobs, read by the web app and Streamlit."""

import os
import sqlite3
from datetime import date

DB_FILE = os.environ.get(
    "JOBS_DB", os.path.join(os.path.dirname(__file__), "jobs.db")
)


def _connect():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT,
                company TEXT,
                location TEXT,
                score REAL,
                priority REAL,
                reason TEXT,
                url TEXT,
                role_query TEXT,
                found_date TEXT,
                description TEXT
            )
        """)
        # Migrate older databases that predate the description column.
        cols = [r[1] for r in conn.execute("PRAGMA table_info(jobs)")]
        if "description" not in cols:
            conn.execute("ALTER TABLE jobs ADD COLUMN description TEXT")


def save(jobs):
    """Insert matched jobs. Existing ids are left untouched (keeps first-seen date)."""
    init()
    today = date.today().isoformat()
    with _connect() as conn:
        for j in jobs:
            conn.execute("""
                INSERT OR IGNORE INTO jobs
                (id, title, company, location, score, priority, reason, url,
                 role_query, found_date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                j["id"], j["title"], j["company"], j["location"],
                j["score"], j.get("priority", j["score"]), j["reason"],
                j["url"], j["role_query"], today, j.get("description", ""),
            ))


def update_scores(jobs):
    """Update score/priority/reason for existing jobs (used when re-scoring)."""
    init()
    with _connect() as conn:
        for j in jobs:
            conn.execute(
                "UPDATE jobs SET score = ?, priority = ?, reason = ? WHERE id = ?",
                (j["score"], j.get("priority", j["score"]), j["reason"], j["id"]),
            )


def load():
    """Return all stored jobs as a list of dicts, newest+highest first."""
    init()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM jobs ORDER BY found_date DESC, score DESC"
        ).fetchall()
    return [dict(r) for r in rows]
