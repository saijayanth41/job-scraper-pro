from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
from .utils import make_job_hash

@dataclass
class JobPosting:
    title: str
    company: str
    location: str
    description: str
    url: str
    posted_date: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None
    source: Optional[str] = None
    hash: str = field(init=False)

    def __post_init__(self):
        self.hash = make_job_hash(self.title, self.company, self.location, self.url)

@dataclass
class JobFilter:
    keywords: List[str] = None
    locations: List[str] = None
    companies: List[str] = None
    experience_levels: List[str] = None
    job_types: List[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    exclude_keywords: List[str] = None

    def matches(self, job: JobPosting) -> bool:
        text = f"{job.title} {job.company} {job.description}".lower()

        if self.keywords:
            if not any(k.lower() in text for k in self.keywords):
                return False

        if self.exclude_keywords:
            if any(x.lower() in text for x in self.exclude_keywords):
                return False

        if self.locations and job.location:
            if not any(loc.lower() in job.location.lower() for loc in self.locations):
                return False

        if self.companies and job.company:
            if not any(c.lower() in job.company.lower() for c in self.companies):
                return False

        if self.job_types and job.job_type:
            if not any(t.lower() in (job.job_type or "").lower() for t in self.job_types):
                return False

        # Salary checks could be added here after robust parsing
        return True
