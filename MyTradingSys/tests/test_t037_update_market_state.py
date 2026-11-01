"""T037: update_market_state.py - snapshot discovery, atomic write and main() orchestration. mts_math functions are
stubbed in main() tests so only this module's wiring is under test (mts_math has its own tests)."""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
import update_market_state as ums  # noqa: E402


def test_atomic_write_creates_parent_writes_exact_bytes_and_leaves_no_tmp(tmp_path):
    target = tmp_path / "sub" / "state.md"
    ums.atomic_write(target, "line1\nline2\n")
    assert target.read_bytes() == b"line1\nline2\n"      # newline="" -> no CRLF translation
    assert [p.name for p in target.parent.iterdir()] == ["state.md"]


def test_atomic_write_replaces_existing_content(tmp_path):
    target = tmp_path / "state.md"
    target.write_text("old", encoding="utf-8")
    ums.atomic_write(target, "new")
    assert target.read_text(encoding="utf-8") == "new"


def test_atomic_write_failure_keeps_old_file_and_cleans_tmp(tmp_path, monkeypatch):
    target = tmp_path / "state.md"
    target.write_text("old", encoding="utf-8")

    def boom(src, dst):
        raise OSError("replace failed")

    monkeypatch.setattr(ums.os, "replace", boom)
    with pytest.raises(OSError):
        ums.atomic_write(target, "new")
    assert target.read_text(encoding="utf-8") == "old"
    assert [p.name for p in tmp_path.iterdir()] == ["state.md"]


def test_find_latest_snapshot_is_newest_mtime_btcusdt_only(tmp_path, monkeypatch):
    monkeypatch.setattr(ums, "SNAPSHOT_DIR", tmp_path)
    older, newer, other = tmp_path / "BTCUSDT_1.json", tmp_path / "BTCUSDT_2.json", tmp_path / "ETHUSDT_9.json"
    for p in (older, newer, other):
        p.write_text("{}", encoding="utf-8")
    os.utime(older, (1000, 1000))
    os.utime(newer, (2000, 2000))
    os.utime(other, (3000, 3000))                       # newest overall, but not BTCUSDT
    assert ums.find_latest_snapshot() == str(newer)


def test_find_latest_snapshot_none_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(ums, "SNAPSHOT_DIR", tmp_path)
    with pytest.raises(FileNotFoundError):
        ums.find_latest_snapshot()


def test_load_snapshot_reads_utf8_json(tmp_path):
    p = tmp_path / "s.json"
    word = "caf" + chr(233)
    p.write_text(json.dumps({"k": word}, ensure_ascii=False), encoding="utf-8")
    assert ums.load_snapshot(str(p)) == {"k": word}


def _stub(monkeypatch, tmp_path, existing_state):
    snaps = tmp_path / "snaps"
    snaps.mkdir()
    (snaps / "BTCUSDT_1.json").write_text(json.dumps({"current_price": 100.0}), encoding="utf-8")
    state = tmp_path / "current_market_state.md"
    if existing_state:
        state.write_text("OLD\n", encoding="utf-8")
    calls = {}
    monkeypatch.setattr(ums, "SNAPSHOT_DIR", snaps)
    monkeypatch.setattr(ums, "STATE_FILE", state)

    def parse(p):
        calls["parsed"] = p
        return {"META": {"updated_utc": "T0"}}

    def upd(old, snap):
        calls["old"], calls["snap"] = old, snap
        return {"META": {"updated_utc": "T1"}}

    monkeypatch.setattr(ums, "parse_state", parse)
    monkeypatch.setattr(ums, "diff_state", lambda old, snap: {"changes": [], "price_delta_pct": 0.0})
    monkeypatch.setattr(ums, "update_state", upd)
    monkeypatch.setattr(ums, "fetch_levels", lambda *a, **k: None)
    monkeypatch.setattr(ums, "format_state", lambda s: "NEW-STATE %s\n" % s["META"]["updated_utc"])
    return state, calls


def test_main_fresh_start_writes_formatted_state(tmp_path, monkeypatch, capsys):
    state, calls = _stub(monkeypatch, tmp_path, existing_state=False)
    ums.main()
    assert state.read_text(encoding="utf-8").startswith("NEW-STATE T1\n")
    assert "parsed" not in calls and calls["old"] == {} and calls["snap"] == {"current_price": 100.0}
    assert "no existing state file" in capsys.readouterr().out


def test_main_existing_state_is_parsed_and_passed_as_old(tmp_path, monkeypatch):
    state, calls = _stub(monkeypatch, tmp_path, existing_state=True)
    ums.main()
    assert calls["parsed"] == str(state)
    assert calls["old"] == {"META": {"updated_utc": "T0"}}
    assert state.read_text(encoding="utf-8").startswith("NEW-STATE T1\n")


def test_main_without_snapshots_raises_and_writes_nothing(tmp_path, monkeypatch):
    state, _ = _stub(monkeypatch, tmp_path, existing_state=False)
    (tmp_path / "snaps" / "BTCUSDT_1.json").unlink()
    with pytest.raises(FileNotFoundError):
        ums.main()
    assert not state.exists()


# ---- ANALYST_LEVELS note layer (display only) ----
from datetime import datetime, timezone

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)


def _data(**kw):
    d = {"asof": "2026-11-01T11:50:00+00:00", "price": 100000.0, "levels": [
        {"level": 105000, "analyst": "A1", "published": "2026-10-30", "hit": False, "expired": False},
        {"level": 103000, "analyst": "A2", "published": "2026-10-29", "hit": True, "expired": False},
        {"level": 98000, "analyst": "A3", "published": "2026-10-28", "hit": False, "expired": False},
        {"level": 99500, "analyst": "A4", "published": "2026-10-20", "hit": False, "expired": True}]}
    d.update(kw)
    return d


def test_levels_section_nearest_above_below_skips_expired():
    out = ums.levels_section(_data(), NOW)
    assert "nearest_above: 103000 | A2 | published 2026-10-29 | hit" in out
    assert "nearest_below: 98000 | A3 | published 2026-10-28 | open" in out
    assert "not a trade input" in out


@pytest.mark.parametrize("bad", [None, {}, "x", _data(levels=[]), _data(price=None),
                                 _data(asof="2026-10-01T00:00:00+00:00"), _data(asof="garbage")])
def test_levels_section_fails_closed_to_no_levels(bad):
    out = ums.levels_section(bad, NOW)
    assert "levels: no levels" in out and "nearest_" not in out


def test_fetch_levels_error_nonzero_timeout_and_garbage_give_none(monkeypatch):
    import subprocess

    class R:
        def __init__(self, rc, out):
            self.returncode, self.stdout = rc, out

    monkeypatch.setattr(ums.subprocess, "run", lambda *a, **k: R(1, "{}"))
    assert ums.fetch_levels() is None
    monkeypatch.setattr(ums.subprocess, "run", lambda *a, **k: R(0, "not json"))
    assert ums.fetch_levels() is None
    monkeypatch.setattr(ums.subprocess, "run", lambda *a, **k: R(0, "[1]"))
    assert ums.fetch_levels() is None

    def boom(*a, **k):
        raise subprocess.TimeoutExpired("x", 1)

    monkeypatch.setattr(ums.subprocess, "run", boom)
    assert ums.fetch_levels() is None
    monkeypatch.setattr(ums.subprocess, "run", lambda *a, **k: R(0, json.dumps(_data())))
    assert ums.fetch_levels()["price"] == 100000.0


def test_main_writes_ladder_section_from_stub_levels(tmp_path, monkeypatch):
    state, _ = _stub(monkeypatch, tmp_path, existing_state=False)
    d = _data(asof=datetime.now(timezone.utc).isoformat(timespec="seconds"))
    monkeypatch.setattr(ums, "fetch_levels", lambda *a, **k: d)
    ums.main()
    txt = state.read_text(encoding="utf-8")
    assert txt.startswith("NEW-STATE T1\n") and "## ANALYST_LEVELS" in txt
    assert "nearest_above: 103000" in txt and "nearest_below: 98000" in txt


def test_main_levels_failure_still_writes_state_with_no_levels(tmp_path, monkeypatch):
    state, _ = _stub(monkeypatch, tmp_path, existing_state=False)

    def boom(*a, **k):
        raise RuntimeError("api down")

    monkeypatch.setattr(ums, "fetch_levels", boom)
    ums.main()
    txt = state.read_text(encoding="utf-8")
    assert txt.startswith("NEW-STATE T1\n") and "levels: no levels" in txt


def test_main_restart_drops_old_levels_section_before_diff(tmp_path, monkeypatch):
    state, calls = _stub(monkeypatch, tmp_path, existing_state=True)
    monkeypatch.setattr(ums, "parse_state", lambda p: {"META": {}, "ANALYST_LEVELS": {"price": "1"}})
    seen = {}
    monkeypatch.setattr(ums, "update_state", lambda old, snap: seen.update(old=old) or {"META": {"updated_utc": "T1"}})
    ums.main()
    assert "ANALYST_LEVELS" not in seen["old"]
