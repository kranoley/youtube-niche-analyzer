import types


class DummyYDL:
    def __init__(self, info):
        self.info = info

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def extract_info(self, arg, download=False):
        # Return preset info object or single video info
        if isinstance(self.info, dict) and self.info.get("entries") is not None:
            return self.info
        return self.info


def test_search_youtube_detailed():
    from core import youtube_api

    # Mock search results (flat)
    flat = {"entries": [{"id": "vid1"}]}

    # Mock full video info
    full = {
        "title": "Video 1",
        "uploader": "Author",
        "duration": 120,
        "view_count": 1000,
        "like_count": 10,
        "comment_count": 2,
        "upload_date": "20250101",
        "channel_follower_count": 2000,
    }

    # Save and replace the yt_dlp namespace used in core.youtube_api
    original = getattr(youtube_api, "yt_dlp")

    called = {"count": 0}

    def factory(opts):
        # First use returns flat, subsequent use returns full info (simulate call order)
        if called["count"] == 0:
            called["count"] += 1
            return DummyYDL(flat)
        return DummyYDL(full)

    try:
        setattr(youtube_api, "yt_dlp", types.SimpleNamespace(YoutubeDL=factory))
        results = youtube_api.search_youtube_detailed("test", max_results=1)
        assert len(results) == 1
        r = results[0]
        assert r["title"] == "Video 1"
        assert r["views"] == 1000
    finally:
        setattr(youtube_api, "yt_dlp", original)


def test_search_youtube_detailed_invalid_args():
    from core.youtube_api import search_youtube_detailed

    try:
        search_youtube_detailed("", max_results=0)
    except ValueError:
        # expected
        pass
    else:
        raise AssertionError("Invalid args did not raise ValueError")
