import logging
import time
from typing import List, Dict, Any
from urllib.parse import urlencode

try:
    import yt_dlp
except Exception:  # pragma: no cover - runtime optional dependency
    yt_dlp = None

logger = logging.getLogger(__name__)


def _validate_search_args(query: str, max_results: int):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if not isinstance(max_results, int) or max_results <= 0 or max_results > 50:
        raise ValueError("max_results must be an integer between 1 and 50")


def _retry(fn, retries=3, backoff=1.0):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            wait = backoff * (2 ** (attempt - 1))
            logger.warning("Attempt %s failed: %s — retrying in %.1fs", attempt, e, wait)
            time.sleep(wait)
    logger.error("All %s attempts failed", retries)
    raise last_exc


def search_youtube_detailed(query: str, max_results: int = 20, last_week_only: bool = False) -> List[Dict[str, Any]]:
    
    _validate_search_args(query, max_results)

    base_url = "https://www.youtube.com/results"
    params = {"search_query": query}
    if last_week_only:
        params["sp"] = "EgIIAw"
    url = base_url + "?" + urlencode(params)

    ydl_opts_flat = {
        "quiet": True,
        "extract_flat": True,
        "playlistend": max_results,
    }

    def _get_search_entries():
        with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl:
            return ydl.extract_info(url, download=False)

    info = _retry(_get_search_entries)

    video_ids = []
    for entry in (info or {}).get("entries", [])[:max_results]:
        if entry and entry.get("id"):
            video_ids.append(entry["id"])

    results = []
    ydl_opts_full = {
        "quiet": True,
        "skip_download": True,
        "ignoreerrors": True,
    }

    def _extract_video(vid):
        with yt_dlp.YoutubeDL(ydl_opts_full) as ydl:
            return ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)

    for vid in video_ids:
        try:
            full_info = _retry(lambda: _extract_video(vid))
            if not full_info:
                continue
            results.append({
                "title": full_info.get("title"),
                "author": full_info.get("uploader"),
                "duration": full_info.get("duration"),
                "views": full_info.get("view_count"),
                "likes": full_info.get("like_count"),
                "comments": full_info.get("comment_count"),
                "date": full_info.get("upload_date"),
                "followers": full_info.get("channel_follower_count") or 1000,
            })
        except Exception as e:
            logger.warning("Failed to extract video %s: %s", vid, e)
            continue

    return results
