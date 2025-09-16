from __future__ import annotations
from typing import List
from urllib.parse import urlencode
from .base import AbstractScraper
from ..models import JobPosting
from ..utils import polite_sleep

class IndeedScraper(AbstractScraper):
    name = "indeed"

    def collect(self, query: str, location: str, pages: int = 1) -> List[JobPosting]:
        jobs: List[JobPosting] = []
        for page in range(pages):
            params = {"q": query, "l": location, "start": page * 10}
            url = f"https://www.indeed.com/jobs?{urlencode(params)}"
            resp = self.session.get(url, timeout=20)
            resp.raise_for_status()
            soup = self._soup(resp.text)

            # Selector fallbacks — Indeed changes often
            cards = soup.select("a.tapItem") or soup.select("div.job_seen_beacon a")
            for a in cards:
                title = (a.select_one("h2.jobTitle span") or a.select_one("h2 span") or a).get_text(strip=True)
                company = (a.select_one("span.companyName") or a.select_one(".companyName")).get_text(strip=True) if a.select_one(".companyName") else "N/A"
                location_el = a.select_one(".companyLocation")
                location_txt = location_el.get_text(strip=True) if location_el else location
                href = a.get("href", "")
                job_url = href if href.startswith("http") else f"https://www.indeed.com{href}"

                summary_el = a.select_one(".job-snippet") or a.select_one(".jobCardShelfContainer")
                desc = summary_el.get_text(" ", strip=True) if summary_el else ""

                jobs.append(JobPosting(
                    title=title, company=company, location=location_txt,
                    description=desc, url=job_url, source=self.name
                ))
            polite_sleep(1.0, 2.0)
        return jobs
