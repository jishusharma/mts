"""Tests for live_owner.py (temp dirs only)."""
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import live_owner as lo

NOW = datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc)


def put(d, host, age):
    (Path(d) / "live_owner.json").write_text(
        json.dumps({"host": host, "heartbeat": (NOW - timedelta(seconds=age)).isoformat()}), encoding="utf-8")


def test_fresh_peer_refuses():
    with tempfile.TemporaryDirectory() as d:
        put(d, "jis-nuc", 30)
        ok, msg = lo.check(d, "jis-nb", NOW)
        assert not ok and "jis-nuc" in msg and "30s" in msg
        ok, _ = lo.claim(d, "jis-nb", NOW)
        assert not ok  # claim must not steal


def test_stale_peer_allows():
    with tempfile.TemporaryDirectory() as d:
        put(d, "jis-nuc", 600)
        assert lo.check(d, "jis-nb", NOW)[0]
        assert lo.claim(d, "jis-nb", NOW)[0]
        assert json.loads((Path(d) / "live_owner.json").read_text())["host"] == "jis-nb"


def test_unreadable_marker_fails_closed():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "live_owner.json").write_text("{not json", encoding="utf-8")
        assert not lo.check(d, "jis-nb", NOW)[0]
        (Path(d) / "live_owner.json").write_text(json.dumps({"host": "x", "heartbeat": "2026-10-16T12:00:00"}))
        assert not lo.check(d, "jis-nb", NOW)[0]  # naive timestamp
    assert not lo.check(str(Path(d) / "missing_share"), "jis-nb", NOW)[0]  # unreachable share
    assert not lo.claim(str(Path(d) / "missing_share"), "jis-nb", NOW)[0]


def test_same_host_restart_allowed():
    with tempfile.TemporaryDirectory() as d:
        put(d, "jis-nb", 5)
        assert lo.check(d, "JIS-NB", NOW)[0]
        assert lo.claim(d, "jis-nb", NOW)[0]
    with tempfile.TemporaryDirectory() as d:
        assert lo.check(d, "jis-nb", NOW)[0]  # no marker = no owner


def test_release_clears_owner():
    with tempfile.TemporaryDirectory() as d:
        lo.claim(d, "jis-nb", NOW)
        lo.release(d, "jis-nuc")  # not ours: untouched
        assert (Path(d) / "live_owner.json").exists()
        lo.release(d, "jis-nb")
        assert not (Path(d) / "live_owner.json").exists()
        assert lo.check(d, "jis-nuc", NOW)[0]


if __name__ == "__main__":
    n = 0
    for k, v in sorted(globals().items()):
        if k.startswith("test_"):
            v()
            n += 1
    print(f"ALL TESTS PASSED ({n})")
