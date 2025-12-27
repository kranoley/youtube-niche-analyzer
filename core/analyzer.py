import math
from datetime import datetime
from typing import Optional, Dict, Any
import logging


logger = logging.getLogger(__name__)


AVG_TIME_PER_VIDEO_SEC = 3.81
MAX_RESULTS = 20



def niche_opportunity_score(avg_seo: float, avg_views: float, avg_duration_sec: float, max_possible_views: float = 50000.0) -> float:
    """Return a 0-100 normalized niche opportunity score.

    Defensive: handles invalid or zero inputs gracefully.
    """
    try:
        log_views = math.log10(max(float(avg_views), 1.0))
    except Exception:
        log_views = 0.0
    norm_views = min(1.0, log_views / math.log10(max_possible_views)) if max_possible_views > 1 else 0.0
    try:
        norm_seo = min(1.0, float(avg_seo) / 100.0)
    except Exception:
        norm_seo = 0.0
    try:
        duration_min = float(avg_duration_sec) / 60.0
    except Exception:
        duration_min = 0.0

    if duration_min < 2:
        norm_duration = 0.3
    elif duration_min < 5:
        norm_duration = 0.6
    elif duration_min <= 15:
        norm_duration = 1.0
    else:
        norm_duration = 0.8
    score = 0.5 * norm_seo + 0.3 * norm_views + 0.2 * norm_duration
    return min(100.0, max(0.0, score * 100.0))


def seo_score(entry: Dict[str, Any], subscribers: int, today_str: str = "20251012") -> Optional[float]:
    """Compute a heuristic SEO score for a video entry. Return None for invalid data."""
    try:
        views = int(entry.get("views", 0) or 0)
        likes = int(entry.get("likes", 0) or 0)
        comments = int(entry.get("comments", 0) or 0)
        duration = int(entry.get("duration", 0) or 0)
        upload_date_str = str(entry.get("date", "0") or "0")
    except Exception:
        return None

    try:
        upload_date = datetime.strptime(upload_date_str, "%Y%m%d")
    except Exception:
        logger.debug("seo_score: invalid upload_date %s", upload_date_str)
        return None

    try:
        today = datetime.strptime(today_str, "%Y%m%d")
    except Exception:
        today = datetime.now()

    age_days = max(1, (today - upload_date).days)

    # Avoid divide-by-zero; small smoothing constants
    engagement_raw = (likes + 2 * comments) / (views + 1)
    base_score = min(80.0, 100.0 * engagement_raw * 10.0)

    views_per_day = views / age_days
    expected_views = max(100.0, float(subscribers) * 0.1)
    viral_ratio = views_per_day / expected_views if expected_views > 0 else 0.0
    viral_multiplier = min(2.0, 0.8 + math.log10(1 + max(viral_ratio, 0.0)))

    length_minutes = duration / 60.0
    engagement_rate = (likes + comments) / (views + 1)

    if length_minutes < 3:
        length_bonus = 1.0
    else:
        duration_factor = min(3.0, length_minutes / 10.0)
        engagement_factor = min(1.0, engagement_rate / 0.05)
        length_bonus = 1.0 + 0.2 * duration_factor * engagement_factor

    score = base_score * viral_multiplier * length_bonus
    try:
        return min(100.0, max(0.0, float(score)))
    except Exception:
        return None
