from __future__ import annotations
from urllib.parse import urlparse
import hashlib
import logging
import random
import time

logger = logging.getLogger(__name__)

def canonicalize(s: str | None) -> str:
    return (s or "").strip().lower()

def normalize_url(u: str | None) -> str:
    u = (u or "").strip()
    if not u:
        return ""
    p = urlparse(u)
    base = f"{p.scheme}://{p.netloc.lower()}{p.path}".rstrip("/")
    return base

def make_job_hash(title: str, company: str, location: str, url: str) -> str:
    unique = f"{canonicalize(title)}|{canonicalize(company)}|{canonicalize(location)}|{normalize_url(url)}"
    return hashlib.md5(unique.encode("utf-8")).hexdigest()

def polite_sleep(min_s: float = 1.0, max_s: float = 2.5):
    time.sleep(random.uniform(min_s, max_s))

def setup_logging():
    from logging.handlers import RotatingFileHandler
    import os
    os.makedirs("logs", exist_ok=True)
    handlers = [
        RotatingFileHandler("logs/job_scraper.log", maxBytes=2_000_000, backupCount=5),
        logging.StreamHandler()
    ]
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", handlers=handlers)
