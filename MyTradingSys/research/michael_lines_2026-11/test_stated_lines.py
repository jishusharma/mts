"""Tests for stated_lines.py (card tl-michael-lines-detect-alert). Fail before the extractor exists (ImportError)."""
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stated_lines as sl  # noqa: E402

TRANSCRIPTS = HERE.parent / "yt_feed_2026-10-31" / "transcripts_michael-pizzino-new10"


def _tmp(name):
    d = Path(tempfile.mkdtemp(prefix="stated_lines_"))
    return d / name


def test_finds_known_quote_with_timestamp():
    rows = sl.extract(TRANSCRIPTS / "7wl0C1lVfRE_timed.txt")
    hit = [r for r in rows if r["ts"] == "00:03:51"]
    assert len(hit) == 1
    assert "our trend line, our 50% level" in hit[0]["quote"]
    assert hit[0]["video"] == "7wl0C1lVfRE" and hit[0]["asset"] == "NASDAQ"


def test_rejects_line_without_timestamp():
    p = _tmp("x_timed.txt")
    p.write_text("# Video ID: x\nwe see a trend line here and it holds\n[00:00:01]\n", encoding="utf-8")
    assert sl.extract(p) == []


def test_stamped_line_is_kept_and_phrase_split_across_captions():
    p = _tmp("y_timed.txt")
    p.write_text("# Video ID: y\n[00:00:05] watch the bitcoin trend\n[00:00:07] line which is support\n", encoding="utf-8")
    rows = sl.extract(p)
    assert len(rows) == 1 and rows[0]["ts"] == "00:00:05" and rows[0]["asset"] == "BTC" and rows[0]["kind"] == "support"


def test_all_ten_videos_every_row_stamped():
    rows = sl.extract_dir(TRANSCRIPTS)
    assert len(rows) >= 10
    assert all(r["ts"] and len(r["ts"]) == 8 for r in rows)
    assert {r["video"] for r in rows} >= {"7wl0C1lVfRE", "avnJKLxX4FY"}
