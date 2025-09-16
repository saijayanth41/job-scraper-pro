# Job Scraper Pro

A production-grade job scraping and alerting pipeline with:
- Robust deduplication (canonical URL + normalized text hashing)
- Flexible filtering (keywords, locations, companies, job types, excludes)
- SQLite persistence
- HTML email digests with safe escaping
- Retries with backoff, polite throttling
- CLI (`--once`, `--schedule`) and simple scheduler
- Extensible scraper architecture (base + per-site modules)

## Quick Start

```bash
git clone <your-repo-url>
cd job-scraper-pro
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env with your SMTP creds and recipients

python -m src.jobscraper.cli --once --sites indeed glassdoor --keywords "Software Engineer,DevOps" --locations "Chicago,Remote"
```

### Run continuously (every 60 minutes by default)
```bash
python -m src.jobscraper.cli --schedule 60 --sites indeed glassdoor --keywords "Software Engineer" --locations "Chicago"
```

### Options
- `--once` run a single cycle and exit
- `--schedule N` run every N minutes
- `--dry-run` scrape + filter, but do not save or email
- `--sites` space-separated sites (indeed glassdoor linkedin)
- `--keywords`, `--exclude`, `--locations`, `--companies`, `--job-types`
- `--recipients` override recipients (comma-separated)

## Project Layout
```
src/jobscraper/
  config.py      # Pydantic settings from .env
  models.py      # JobPosting, JobFilter (with .matches)
  db.py          # DatabaseManager (INSERT OR IGNORE)
  notify.py      # EmailNotifier (HTML escape, Jinja2 template)
  utils.py       # URL normalization, hashing, logging
  runner.py      # Orchestrates scraping -> filter -> save -> email
  scrapers/
    base.py      # AbstractScraper
    indeed.py    # Requests + BS4 implementation
    glassdoor.py # (skeleton placeholder)
    linkedin.py  # (skeleton placeholder)
  cli.py         # Argparse entrypoint, scheduler (schedule)
tests/
  test_hashing.py
  test_filter.py
```

## Adding a new scraper
Create `src/jobscraper/scrapers/<site>.py` implementing `AbstractScraper.collect()` returning `List[JobPosting]`, then register it in `cli.py` `SITE_REGISTRY`.

## Docker (optional)
```
docker build -t job-scraper-pro .
docker run --env-file .env job-scraper-pro --once --sites indeed --keywords "Python"
```
