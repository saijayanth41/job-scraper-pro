from __future__ import annotations
from typing import List
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ..models import JobPosting
from ..utils import polite_sleep

class AbstractScraper:
    name: str = "abstract"

    def __init__(self, user_agent: str, accept_language: str):
        self.session = requests.Session()
        retry = Retry(
            total=3, backoff_factor=0.6,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({
            "User-Agent": user_agent,
            "Accept-Language": accept_language,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Connection": "keep-alive",
        })

    def collect(self, query: str, location: str, pages: int = 1) -> List[JobPosting]:
        raise NotImplementedError

    @staticmethod
    def _soup(html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "html5lib")
