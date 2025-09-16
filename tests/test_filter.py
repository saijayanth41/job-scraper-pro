from src.jobscraper.models import JobPosting, JobFilter

def test_filter_keywords_and_exclude():
    job = JobPosting("Senior Python Engineer", "Acme", "Chicago, IL", "We use Python and AWS", "http://x")
    filt = JobFilter(keywords=["python"], exclude_keywords=["java"])
    assert filt.matches(job)

    filt2 = JobFilter(keywords=["java"], exclude_keywords=["python"])
    assert not filt2.matches(job)
