from __future__ import annotations
import argparse, logging, os
import schedule, time
from typing import List
from .config import AppConfig
from .utils import setup_logging
from .db import DatabaseManager
from .notify import EmailNotifier
from .models import JobFilter
from .runner import JobRunner
from .scrapers.indeed import IndeedScraper
from .scrapers.glassdoor import GlassdoorScraper
from .scrapers.linkedin import LinkedInScraper

SITE_REGISTRY = {
    "indeed": IndeedScraper,
    "glassdoor": GlassdoorScraper,
    "linkedin": LinkedInScraper,
}

def run_once(args):
    cfg = AppConfig.from_env()
    db = DatabaseManager(cfg.db_path)
    notifier = EmailNotifier(cfg.email.email, cfg.email.password, cfg.email.smtp_server, cfg.email.smtp_port)
    runner = JobRunner(db, notifier)

    scrapers = [SITE_REGISTRY[s](cfg.user_agent, cfg.accept_language) for s in args.sites]
    all_jobs = []
    for s in scrapers:
        for loc in args.locations:
            for kw in args.keywords:
                jobs = s.collect(kw, loc, pages=args.pages)
                all_jobs.extend(jobs)

    filt = JobFilter(
        keywords=args.keywords or None,
        locations=args.locations or None,
        companies=args.companies or None,
        job_types=args.job_types or None,
        exclude_keywords=args.exclude or None
    )

    new_jobs = runner.filter_and_save(all_jobs, filt)

    recipients = [r.strip() for r in (args.recipients or []) if r.strip()] or cfg.email.recipients
    if args.dry_run:
        logging.info("Dry run: %d new jobs would be emailed to %s", len(new_jobs), recipients)
        return

    runner.notify_new(limit=args.max_email, recipients=recipients)

def main():
    parser = argparse.ArgumentParser(description="Job Scraper Pro")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--schedule", type=int, default=0, help="Run every N minutes")
    parser.add_argument("--dry-run", action="store_true", help="Scrape and filter, but do not save or email")
    parser.add_argument("--sites", nargs="+", default=["indeed"], choices=SITE_REGISTRY.keys())
    parser.add_argument("--keywords", nargs="+", default=["Software Engineer"])
    parser.add_argument("--exclude", nargs="*", default=[])
    parser.add_argument("--locations", nargs="+", default=["Remote"])
    parser.add_argument("--companies", nargs="*", default=[])
    parser.add_argument("--job-types", nargs="*", default=[])
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--max-email", type=int, default=50, help="Max jobs per email notification")
    parser.add_argument("--recipients", type=lambda s: s.split(","), default=None, help="Comma-separated list")
    args = parser.parse_args()

    setup_logging()

    if args.once or args.schedule == 0:
        run_once(args)
        return

    schedule.every(args.schedule).minutes.do(run_once, args=args)
    logging.info("Scheduled to run every %d minutes", args.schedule)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
