from __future__ import annotations
import sqlite3, os, datetime as dt
from typing import List, Dict, Any, Optional
from .models import JobPosting

SCHEMA = '''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hash TEXT UNIQUE,
    title TEXT,
    company TEXT,
    location TEXT,
    description TEXT,
    url TEXT,
    posted_date TEXT,
    salary TEXT,
    job_type TEXT,
    source TEXT,
    notified INTEGER DEFAULT 0,
    scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_hash ON jobs(hash);
CREATE INDEX IF NOT EXISTS idx_notified ON jobs(notified);
CREATE INDEX IF NOT EXISTS idx_scraped_at ON jobs(scraped_at);
'''

class DatabaseManager:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA)

    def save_job(self, job: JobPosting) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                '''INSERT OR IGNORE INTO jobs 
                   (hash, title, company, location, description, url, posted_date, salary, job_type, source)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (job.hash, job.title, job.company, job.location, job.description, job.url,
                 job.posted_date, job.salary, job.job_type, job.source)
            )
            return conn.total_changes > 0

    def list_unnotified(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            q = "SELECT * FROM jobs WHERE notified = 0 ORDER BY scraped_at DESC"
            if limit:
                q += f" LIMIT {int(limit)}"
            rows = conn.execute(q).fetchall()
            return [dict(r) for r in rows]

    def mark_notified(self, hashes: List[str]):
        if not hashes:
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany("UPDATE jobs SET notified = 1 WHERE hash = ?", [(h,) for h in hashes])
