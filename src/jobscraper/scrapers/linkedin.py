from __future__ import annotations
from typing import List
from .base import AbstractScraper
from ..models import JobPosting

class LinkedInScraper(AbstractScraper):
    name = "linkedin"

    def collect(self, query: str, location: str, pages: int = 1) -> List[JobPosting]:
        # Placeholder: LinkedIn is aggressive with anti-bot and disallows scraping in ToS.
        # Consider LinkedIn Jobs API partners or RSS/alerts export.
        return []
