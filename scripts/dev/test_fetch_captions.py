"""Spec-derived tests for scripts/dev/fetch_captions.py components.

Covers:
  - vid_of: 11-char ID extraction from raw IDs, watch URLs, youtu.be links, query params, and validation errors.
  - vtt_to_text: header stripping, timestamp/digit filtering, HTML tag removal, entity decoding,
                consecutive line deduplication, and phrase echo collapsing.
  - pick_track: track selection precedence (manual over auto, language list priority, -orig fallback, unmatched).
  - fetch: exists check, nocaps, error classification (BLOCKED on 429, PRIVATE on private/members), and canonical file output formatting.
"""
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

try:
    import yt_dlp
except ImportError:   # CI has no yt_dlp: stub what the module touches (a whole-file skip is pytest exit 5, a FAIL in run_extra_tests)
    import types
    yt_dlp = types.SimpleNamespace(YoutubeDL=None, utils=types.SimpleNamespace(DownloadError=Exception))
    sys.modules["yt_dlp"] = yt_dlp

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fetch_captions as fc


def test_vid_of_standard_and_variations():
    # Direct 11-char ID
    assert fc.vid_of("6WfTIyJ-YzQ") == "6WfTIyJ-YzQ"
    # Leading hyphen (valid YouTube ID)
    assert fc.vid_of("-a1B2c3D4e5") == "-a1B2c3D4e5"
    # Standard watch URL
    assert fc.vid_of("https://www.youtube.com/watch?v=6WfTIyJ-YzQ") == "6WfTIyJ-YzQ"
    # youtu.be short URL
    assert fc.vid_of("https://youtu.be/6WfTIyJ-YzQ") == "6WfTIyJ-YzQ"
    # URL with additional parameters (timestamps, playlists)
    assert fc.vid_of("https://www.youtube.com/watch?v=6WfTIyJ-YzQ&t=120s&list=xyz") == "6WfTIyJ-YzQ"
    # Embedded / trailing fragments
    assert fc.vid_of("https://www.youtube.com/watch?v=6WfTIyJ-YzQ#t=10") == "6WfTIyJ-YzQ"


def test_vid_of_invalid_raises_value_error():
    with pytest.raises(ValueError, match="no 11-char video id in"):
        fc.vid_of("")
    with pytest.raises(ValueError, match="no 11-char video id in"):
        fc.vid_of("too_short")
    with pytest.raises(ValueError, match="no 11-char video id in"):
        fc.vid_of("https://www.youtube.com/watch?v=invalid_id_length_123")


def test_vtt_to_text_basic_cleaning():
    vtt = """WEBVTT
Kind: captions
Language: en
NOTE This is a commentary block

1
00:00:01.000 --> 00:00:03.500
<c>Bitcoin</c> is testing &amp; holding 68k.

2
00:00:03.500 --> 00:00:05.000
Support at &gt; 67000 &lt;reclaimed&gt;.
"""
    cleaned = fc.vtt_to_text(vtt)
    assert cleaned == "Bitcoin is testing & holding 68k. Support at > 67000 <reclaimed>."


def test_vtt_to_text_dedupe_and_echo_collapse():
    # Rolling captions repeat consecutive lines
    vtt = """WEBVTT

00:00:01.000 --> 00:00:02.000
market is moving up

00:00:02.000 --> 00:00:03.000
market is moving up

00:00:03.000 --> 00:00:04.000
towards resistance
"""
    cleaned = fc.vtt_to_text(vtt)
    assert cleaned == "market is moving up towards resistance"

    # Phrase echo collapse: 2 to 8 repeated words collapsed to 1 instance
    echo_vtt = """WEBVTT
00:00:01.000 --> 00:00:03.000
we expect a sharp retest we expect a sharp retest right here
"""
    assert fc.vtt_to_text(echo_vtt) == "we expect a sharp retest right here"


def test_vtt_to_text_empty_input():
    assert fc.vtt_to_text("") == ""
    assert fc.vtt_to_text("WEBVTT\nKind: captions\nLanguage: en\n") == ""


def test_pick_track_manual_priority_over_auto():
    info = {
        "subtitles": {"en": [{"ext": "vtt"}]},
        "automatic_captions": {"en": [{"ext": "vtt"}]},
    }
    kind, lang = fc.pick_track(info, ["en"])
    assert kind == "manual"
    assert lang == "en"


def test_pick_track_language_order_and_orig_suffix():
    # Priority order in langs list
    info = {
        "subtitles": {"hi": [{"ext": "vtt"}], "en": [{"ext": "vtt"}]},
    }
    kind, lang = fc.pick_track(info, ["en", "hi"])
    assert kind == "manual"
    assert lang == "en"

    # Fallback to -orig suffix
    info_orig = {
        "subtitles": {"en-orig": [{"ext": "vtt"}]},
    }
    kind, lang = fc.pick_track(info_orig, ["en"])
    assert kind == "manual"
    assert lang == "en-orig"

    # Fallback to automatic captions if manual has no matching language
    info_auto = {
        "subtitles": {"es": [{"ext": "vtt"}]},
        "automatic_captions": {"en": [{"ext": "vtt"}]},
    }
    kind, lang = fc.pick_track(info_auto, ["en"])
    assert kind == "auto"
    assert lang == "en"


def test_pick_track_none_when_unmatched():
    info = {
        "subtitles": {"es": [{"ext": "vtt"}]},
        "automatic_captions": {"de": [{"ext": "vtt"}]},
    }
    kind, lang = fc.pick_track(info, ["en", "hi"])
    assert kind is None
    assert lang is None

    assert fc.pick_track({}, ["en"]) == (None, None)


def test_fetch_returns_exists_if_file_present():
    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td)
        vid = "6WfTIyJ-YzQ"
        (out_dir / f"{vid}_raw.txt").write_text("existing content", encoding="utf-8")

        with patch.object(fc, "OUT", out_dir):
            result = fc.fetch(vid, "TestAnalyst", ["en"])
            assert result == "EXISTS"


def test_fetch_nocaps_when_no_track():
    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td)
        vid = "6WfTIyJ-YzQ"

        mock_ydl = MagicMock()
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.return_value = {"title": "Test Video", "subtitles": {}}

        with patch.object(fc, "OUT", out_dir):
            with patch("yt_dlp.YoutubeDL", return_value=mock_ydl):
                result = fc.fetch(vid, "TestAnalyst", ["en"])
                assert result == "NOCAPS"


def test_fetch_blocked_error_handling():
    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td)
        vid = "6WfTIyJ-YzQ"

        mock_ydl = MagicMock()
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("HTTP Error 429: Too Many Requests")

        with patch.object(fc, "OUT", out_dir):
            with patch("yt_dlp.YoutubeDL", return_value=mock_ydl):
                result = fc.fetch(vid, "TestAnalyst", ["en"])
                assert result == "BLOCKED"


def test_fetch_private_error_handling():
    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td)
        vid = "6WfTIyJ-YzQ"

        mock_ydl = MagicMock()
        mock_ydl.__enter__.return_value = mock_ydl
        mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Private video. Sign in if you've been granted access.")

        with patch.object(fc, "OUT", out_dir):
            with patch("yt_dlp.YoutubeDL", return_value=mock_ydl):
                result = fc.fetch(vid, "TestAnalyst", ["en"])
                assert result == "PRIVATE"


def test_fetch_successful_write():
    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td)
        vid = "6WfTIyJ-YzQ"

        vtt_content = """WEBVTT
00:00:01.000 --> 00:00:04.000
Bitcoin forms a clean support level
"""

        mock_ydl_meta = MagicMock()
        mock_ydl_meta.__enter__.return_value = mock_ydl_meta
        mock_ydl_meta.extract_info.return_value = {
            "title": "Bitcoin Analysis",
            "upload_date": "20261101",
            "uploader": "Test Channel",
            "subtitles": {"en": [{"ext": "vtt"}]},
        }

        class MockYoutubeDL:
            def __init__(self, opts):
                self.opts = opts

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def extract_info(self, url, download=False):
                return mock_ydl_meta.extract_info.return_value

            def download(self, urls):
                outtmpl = self.opts.get("outtmpl", "")
                if outtmpl:
                    parent = Path(outtmpl).parent
                    (parent / f"{vid}.en.vtt").write_text(vtt_content, encoding="utf-8")

        with patch.object(fc, "OUT", out_dir):
            with patch("yt_dlp.YoutubeDL", side_effect=MockYoutubeDL):
                result = fc.fetch(vid, "Doug", ["en"])
                assert result.startswith("OK manual/en 6w")
                dest = out_dir / f"{vid}_raw.txt"
                assert dest.exists()
                text = dest.read_text(encoding="utf-8")
                assert "# Video ID: 6WfTIyJ-YzQ" in text
                assert "# Title: Bitcoin Analysis" in text
                assert "# Published: 2026-11-01" in text
                assert "# Analyst: Doug" in text
                assert "# Word count: 6" in text
                assert "Bitcoin forms a clean support level" in text
