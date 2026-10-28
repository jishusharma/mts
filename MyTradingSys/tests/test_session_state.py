"""test_session_state.py - 8 tests for session_state helper."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "runtime"))
sys.dont_write_bytecode = True

import session_state as ss

def _fresh(tmp_path, monkeypatch):
    monkeypatch.setattr(ss, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(ss, "LOG_FILE", tmp_path / "log.json")

def test_write_read_roundtrip(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    d = dict(ss.DEFAULT_STATE)
    d["thesis"] = {"direction": "short", "confidence": "high", "text": "test"}
    ss.write_state(d)
    r = ss.read_state()
    assert r["thesis"]["direction"] == "short"
    assert r["version"] == ss.VERSION

def test_missing_file_returns_default(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    r = ss.read_state()
    assert r["thesis"]["direction"] == "neutral"
    assert r["version"] == ss.VERSION

def test_corrupt_json_returns_default(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    (tmp_path / "state.json").write_text("{not json")
    r = ss.read_state()
    assert r["version"] == ss.VERSION

def test_version_mismatch_logged(tmp_path, monkeypatch, capsys):
    _fresh(tmp_path, monkeypatch)
    (tmp_path / "state.json").write_text('{"version":"0.9.9"}')
    r = ss.read_state()
    assert r["version"] == "0.9.9"

def test_atomic_no_tmp_left(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    ss.write_state(dict(ss.DEFAULT_STATE))
    tmps = list(tmp_path.glob(".sst_*"))
    assert tmps == []

def test_append_log_order(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    ss.append_log({"type": "alert", "alert_id": 1})
    ss.append_log({"type": "alert", "alert_id": 2})
    lg = ss.read_log()
    assert len(lg["events"]) == 2
    assert lg["events"][0]["alert_id"] == 1
    assert lg["events"][1]["alert_id"] == 2

def test_schema_rejects_wrong_type(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    bad = dict(ss.DEFAULT_STATE)
    bad["mode"] = 123
    try:
        ss.write_state(bad)
        assert False, "should have raised"
    except TypeError:
        pass

def test_session_start_preserved(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    d1 = dict(ss.DEFAULT_STATE)
    ss.write_state(d1)
    first = ss.read_state()["session_start_utc"]
    d2 = ss.read_state()
    d2["notes"] = "update"
    ss.write_state(d2)
    second = ss.read_state()["session_start_utc"]
    assert first == second
