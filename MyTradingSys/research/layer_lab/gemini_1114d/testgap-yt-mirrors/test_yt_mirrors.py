"""Pure helper, URL-building, mirror-selection, and parse tests for scripts/dev/yt_mirrors.py.

Existing coverage: scripts/dev/test_yt_freedom.py (MirrorLists, lines 273-358) already tests
parse_invidious_list, parse_piped_list, refresh, candidates, probe_invidious, inv_captions,
parse_ttml, classify, and pick_audio. This file adds focused, hand-computed pytest cases for
URL-building (channel_url, inv_audio, piped_list), track/mirror selection (pick_track,
candidates cooldown boundary), and list parsing without network calls.

Scratch mutation check: in a scratch copy of scripts/dev/yt_mirrors.py, mutating
`pick_track` line 315 from `for auto in (False, True):` to `for auto in (True, False):`
caused `test_pick_track_language_and_auto_priority` to fail (AssertionError: '/en-us-auto' != '/en-gb').
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_DEV = ROOT / "scripts" / "dev"
if str(SCRIPTS_DEV) not in sys.path:
    sys.path.append(str(SCRIPTS_DEV))

import yt_mirrors  # noqa: E402


def test_channel_url_and_classify_variants():
    assert yt_mirrors.classify("https://www.youtube.com/shorts/dQw4w9WgXcQ") == ("video", "dQw4w9WgXcQ")
    assert yt_mirrors.classify("PL1234567890") == ("playlist", "PL1234567890")
    assert yt_mirrors.channel_url("@TraderBob") == "https://www.youtube.com/@TraderBob"
    uc = "UC" + "x" * 22
    assert yt_mirrors.channel_url(f"https://www.youtube.com/channel/{uc}") == f"https://www.youtube.com/channel/{uc}"
    assert yt_mirrors.channel_url("https://www.youtube.com/c/MyChannel") == "https://www.youtube.com/c/MyChannel"
    assert yt_mirrors.channel_url("dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_pick_track_language_and_auto_priority():
    tracks = [
        {"code": "fr", "auto": False, "url": "/fr"},
        {"code": "en-US", "auto": True, "url": "/en-us-auto"},
        {"code": "en-GB", "auto": False, "url": "/en-gb"},
        {"code": "hi", "auto": True, "url": "/hi-auto"},
    ]
    # Base-language match for "en" prefers manual ("en-GB") over auto ("en-US")
    assert yt_mirrors.pick_track(tracks, ["en", "fr"])["url"] == "/en-gb"
    # Unmatched wanted language falls back to first manual track
    assert yt_mirrors.pick_track(tracks, ["de"])["url"] == "/fr"
    # Only auto tracks available -> falls back to first track
    auto_only = [{"code": "ja", "auto": True, "url": "/ja"}, {"code": "ko", "auto": True, "url": "/ko"}]
    assert yt_mirrors.pick_track(auto_only, ["de"])["url"] == "/ja"
    assert yt_mirrors.pick_track([], ["en"]) is None


def test_candidates_mirror_selection_and_cooldown(tmp_path, monkeypatch):
    cache_path = tmp_path / "mirrors.json"
    monkeypatch.setenv("YT_MIRRORS_FILE", str(cache_path))
    cache_data = {
        "invidious_list": ["m1.example", "m2.example", "m3.example", "m4.example"],
        "invidious": {
            "m1.example": {"ok_at": "2026-11-14T10:00:00+00:00", "fail_at": "2026-11-14T10:20:00+00:00"},
            "m2.example": {"ok_at": "2026-11-14T10:05:00+00:00"},
            "m3.example": {"ok_at": "2026-11-14T10:15:00+00:00", "fail_at": "2026-11-14T09:50:00+00:00"},
        },
    }
    cache_path.write_text(json.dumps(cache_data), encoding="utf-8")

    t_inside_cooldown = datetime(2026, 11, 14, 10, 40, 0, tzinfo=timezone.utc)
    # m3 (ok 10:15 >= fail 09:50) > m2 (ok 10:05) > m4 (fresh); m1 excluded (20m < 30m cooldown)
    assert yt_mirrors.candidates("invidious", now=t_inside_cooldown) == [
        "m3.example",
        "m2.example",
        "m4.example",
    ]

    t_after_cooldown = datetime(2026, 11, 14, 10, 20, 0, tzinfo=timezone.utc) + timedelta(
        minutes=yt_mirrors.FAIL_COOLDOWN_MIN
    )
    # At exactly FAIL_COOLDOWN_MIN (30m), m1 is no longer in cooldown and appears as fresh
    assert yt_mirrors.candidates("invidious", now=t_after_cooldown) == [
        "m3.example",
        "m2.example",
        "m1.example",
        "m4.example",
    ]


def test_parse_invidious_and_piped_list_ordering():
    inv_raw = [
        ["SLOW.example ", {"type": "https", "api": True, "monitor": {"down": False, "uptime": 95.0}}],
        ["fast.example", {"type": "https", "api": True, "monitor": {"down": False, "uptime": 99.5}}],
        ["noapi.example", {"type": "https", "api": False, "monitor": {"down": False, "uptime": 99.9}}],
        ["down.example", {"type": "https", "api": True, "monitor": {"down": True, "uptime": 100.0}}],
        ["hidden.onion", {"type": "onion", "api": True, "monitor": {"down": False, "uptime": 100.0}}],
    ]
    assert yt_mirrors.parse_invidious_list(inv_raw) == [
        "fast.example",
        "slow.example",
        "noapi.example",
    ]

    piped_md = (
        "| Name | URL | Region |\n"
        "| --- | --- | --- |\n"
        "| A | https://piped.example:8443 | DE |\n"
        "| B | http://insecure.example | US |\n"
        "| C | https://piped.example:8443 | DE |\n"
        "| D | https://pipedapi.adminforge.de | EU |\n"
    )
    assert yt_mirrors.parse_piped_list(piped_md) == [
        "https://piped.example:8443",
        "https://pipedapi.adminforge.de",
    ]


def test_inv_audio_and_piped_list_url_building_no_network(tmp_path, monkeypatch):
    seen_gets = []
    seen_downloads = []

    def fake_get(url, timeout=25, binary=False):
        seen_gets.append(url)
        if url == "https://inv.example/api/v1/videos/vid12345678":
            payload = {
                "adaptiveFormats": [
                    {"itag": "251", "type": "audio/webm", "bitrate": "160000"},
                    {"itag": "140", "type": "audio/mp4; codecs=\"mp4a.40.2\"", "bitrate": "128000"},
                ]
            }
            return 200, json.dumps(payload)
        if url == "https://piped.example/playlists/PLabcdefghij":
            payload = {
                "relatedStreams": [
                    {"url": "/watch?v=aaaaaaaaaaa", "title": "First", "uploaded": 1700000000000},
                    {"url": "/watch?v=bbbbbbbbbbb", "title": "Second", "uploaded": 0},
                    {"url": "/watch?v=ccccccccccc", "title": "Third", "uploaded": 1700000000000},
                ]
            }
            return 200, json.dumps(payload)
        return 404, ""

    def fake_download(url, dest, timeout=60, cap=400 * 1024 * 1024):
        seen_downloads.append((url, Path(dest)))
        return 1024

    monkeypatch.setattr(yt_mirrors, "http_get", fake_get)
    monkeypatch.setattr(yt_mirrors, "http_download", fake_download)

    out_path = yt_mirrors.inv_audio("inv.example", "vid12345678", tmp_path / "audio")
    assert out_path == tmp_path / "audio.m4a"
    assert seen_downloads == [
        ("https://inv.example/latest_version?id=vid12345678&itag=140&local=true", tmp_path / "audio.m4a")
    ]

    items = yt_mirrors.piped_list(
        "https://piped.example", "https://www.youtube.com/playlist?list=PLabcdefghij", limit=2
    )
    assert items == [
        ("aaaaaaaaaaa", "First", "2023-11-14"),
        ("bbbbbbbbbbb", "Second", ""),
    ]
    assert seen_gets == [
        "https://inv.example/api/v1/videos/vid12345678",
        "https://piped.example/playlists/PLabcdefghij",
    ]
