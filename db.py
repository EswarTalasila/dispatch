"""Local SQLite store of matched jobs, read by the web app and Streamlit."""

import os
import sqlite3
from datetime import date

DB_FILE = os.environ.get(
    "JOBS_DB", os.path.join(os.path.dirname(__file__), "jobs.db")
)

# The "active" resume file the scorer reads (filter.py reads resume.txt too).
RESUME_FILE = os.environ.get(
    "RESUME_FILE", os.path.join(os.path.dirname(__file__), "resume.txt")
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

        conn.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                text TEXT,
                active INTEGER DEFAULT 0,
                created TEXT
            )
        """)


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


# --- Resume library -------------------------------------------------------

def _write_active_file(text):
    with open(RESUME_FILE, "w") as f:
        f.write(text or "")


def _seed_resumes(conn):
    """If there are no saved resumes yet but resume.txt has content, adopt it."""
    count = conn.execute("SELECT COUNT(*) FROM resumes").fetchone()[0]
    if count:
        return
    if os.path.exists(RESUME_FILE):
        with open(RESUME_FILE) as f:
            text = f.read().strip()
        if text:
            conn.execute(
                "INSERT INTO resumes (name, text, active, created) VALUES (?, ?, 1, ?)",
                ("My résumé", text, date.today().isoformat()),
            )


def list_resumes():
    init()
    with _connect() as conn:
        _seed_resumes(conn)
        rows = conn.execute(
            "SELECT id, name, active, LENGTH(text) AS chars FROM resumes ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]


def get_resume(resume_id):
    init()
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, name, text FROM resumes WHERE id = ?", (resume_id,)
        ).fetchone()
    return dict(row) if row else None


def add_resume(name, text):
    """Save a new resume, make it active, and write it to the active file."""
    init()
    with _connect() as conn:
        conn.execute("UPDATE resumes SET active = 0")
        cur = conn.execute(
            "INSERT INTO resumes (name, text, active, created) VALUES (?, ?, 1, ?)",
            (name, text, date.today().isoformat()),
        )
        new_id = cur.lastrowid
    _write_active_file(text)
    return new_id


def activate_resume(resume_id):
    init()
    with _connect() as conn:
        row = conn.execute(
            "SELECT text FROM resumes WHERE id = ?", (resume_id,)
        ).fetchone()
        if not row:
            return False
        conn.execute("UPDATE resumes SET active = 0")
        conn.execute("UPDATE resumes SET active = 1 WHERE id = ?", (resume_id,))
    _write_active_file(row["text"])
    return True


def delete_resume(resume_id):
    """Delete a resume; if it was active, fall back to the most recent one."""
    init()
    with _connect() as conn:
        row = conn.execute(
            "SELECT active FROM resumes WHERE id = ?", (resume_id,)
        ).fetchone()
        if not row:
            return None
        was_active = row["active"]
        conn.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
        new_active = None
        if was_active:
            nxt = conn.execute(
                "SELECT id, text FROM resumes ORDER BY id DESC LIMIT 1"
            ).fetchone()
            if nxt:
                conn.execute("UPDATE resumes SET active = 1 WHERE id = ?", (nxt["id"],))
                new_active = nxt["id"]
                _write_active_file(nxt["text"])
    return new_active
