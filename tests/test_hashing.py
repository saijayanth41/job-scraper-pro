from src.jobscraper.utils import make_job_hash, normalize_url, canonicalize

def test_normalize_url():
    assert normalize_url("https://Example.com/Path/?utm=abc#frag") == "https://example.com/Path"

def test_make_job_hash_stable():
    a = make_job_hash("Title","Company","NY","https://example.com/x?utm=1")
    b = make_job_hash("title "," company"," ny ","https://example.com/x#frag")
    assert a == b
