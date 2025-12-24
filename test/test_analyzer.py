from core.analyzer import niche_opportunity_score, seo_score


def test_niche_opportunity_score_basic():
    score = niche_opportunity_score(avg_seo=50, avg_views=1000, avg_duration_sec=300)
    assert 0 <= score <= 100


def test_seo_score_valid_entry():
    entry = {
        "views": 1000,
        "likes": 50,
        "comments": 5,
        "duration": 600,
        "date": "20250101",
    }
    score = seo_score(entry, subscribers=5000, today_str="20251201")
    assert score is not None
    assert 0 <= score <= 100


def test_seo_score_invalid_date():
    entry = {"views": 100, "likes": 1, "comments": 0, "duration": 100, "date": "notadate"}
    assert seo_score(entry, subscribers=1000) is None
