from __future__ import annotations
from typing import List
from urllib.parse import urlencode
from .base import AbstractScraper
from ..models import JobPosting
from ..utils import polite_sleep

class GlassdoorScraper(AbstractScraper):
    name = "glassdoor"

    def collect(self, query: str, location: str, pages: int = 1) -> List[JobPosting]:
        # NOTE: Glassdoor often blocks scraping and changes its HTML. Treat as best-effort example.
        jobs: List[JobPosting] = []
        for page in range(1, pages + 1):
            params = {"sc.keyword": query, "locT": "C", "locId": "", "locKeyword": location, "p": page}
            url = f"https://www.glassdoor.com/Job/jobs.htm?{urlencode(params)}"
            resp = self.session.get(url, timeout=20)
            if resp.status_code >= 400:
                break
            soup = self._soup(resp.text)
            cards = soup.select("li.react-job-listing") or soup.select("article.job-card")
            for c in cards:
                title_el = c.select_one("a.jobLink span") or c.select_one("a.job-title")
                title = title_el.get_text(strip=True) if title_el else "N/A"
                company = (c.select_one("a.employerName") or c.select_one("div.jobEmpolyerName") or c.select_one(".job-info")).get_text(strip=True) if (c.select_one("a.employerName") or c.select_one("div.jobEmpolyerName") or c.select_one(".job-info")) else "N/A"
                loc_el = c.select_one("span.pr-xxsm") or c.select_one(".job-location")
                location_txt = loc_el.get_text(strip=True) if loc_el else location
                href = (c.select_one("a.jobLink") or c.select_one("a")).get("href", "") if (c.select_one("a.jobLink") or c.select_one("a")) else ""
                job_url = href if href.startswith("http") else f"https://www.glassdoor.com{href}"
                desc_el = c.select_one(".job-snippet") or c.select_one(".jobDesc")
                desc = desc_el.get_text(" ", strip=True) if desc_el else ""
                jobs.append(JobPosting(title, company, location_txt, desc, job_url, source=self.name))
            polite_sleep(1.0, 2.0)
        return jobs
