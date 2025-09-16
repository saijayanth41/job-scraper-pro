from __future__ import annotations
from typing import List, Dict
import logging
from .models import JobPosting, JobFilter
from .db import DatabaseManager
from .notify import EmailNotifier

logger = logging.getLogger(__name__)

class JobRunner:
    def __init__(self, db: DatabaseManager, notifier: EmailNotifier):
        self.db = db
        self.notifier = notifier

    def filter_and_save(self, jobs: List[JobPosting], filt: JobFilter) -> List[JobPosting]:
        saved: List[JobPosting] = []
        for j in jobs:
            try:
                if filt.matches(j):
                    if self.db.save_job(j):
                        saved.append(j)
            except Exception as e:
                logger.exception("Failed processing job %s: %s", j.url, e)
        logger.info("Saved %d new jobs after filtering", len(saved))
        return saved

    def notify_new(self, limit: int | None, recipients: List[str]):
        pending = self.db.list_unnotified(limit=limit)
        if not pending:
            logger.info("No new jobs to notify")
            return 0
        self.notifier.send(recipients, pending)
        self.db.mark_notified([p["hash"] for p in pending])
        logger.info("Emailed and marked %d jobs as notified", len(pending))
        return len(pending)
