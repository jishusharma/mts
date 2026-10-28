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
    monkeypatch.setattr(ums, "format_state", lambda s: "NEW-STATE %s\n" % s["META"]["updated_utc"])
    return state, calls


def test_main_fresh_start_writes_formatted_state(tmp_path, monkeypatch, capsys):
    state, calls = _stub(monkeypatch, tmp_path, existing_state=False)
    ums.main()
    assert state.read_text(encoding="utf-8") == "NEW-STATE T1\n"
    assert "parsed" not in calls and calls["old"] == {} and calls["snap"] == {"current_price": 100.0}
    assert "no existing state file" in capsys.readouterr().out


def test_main_existing_state_is_parsed_and_passed_as_old(tmp_path, monkeypatch):
    state, calls = _stub(monkeypatch, tmp_path, existing_state=True)
    ums.main()
    assert calls["parsed"] == str(state)
    assert calls["old"] == {"META": {"updated_utc": "T0"}}
    assert state.read_text(encoding="utf-8") == "NEW-STATE T1\n"


def test_main_without_snapshots_raises_and_writes_nothing(tmp_path, monkeypatch):
    state, _ = _stub(monkeypatch, tmp_path, existing_state=False)
    (tmp_path / "snaps" / "BTCUSDT_1.json").unlink()
    with pytest.raises(FileNotFoundError):
        ums.main()
    assert not state.exists()
