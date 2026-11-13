"""Unit tests for scripts/dev/task_state.py.

Mutation test record (Step 3):
Mutated copy created in scratch file with flipped branch:
  File: scripts/dev/task_state.py:151
  Original: if kind not in KINDS:
  Mutated:  if kind in KINDS:
Resulting failure when pointed at mutated copy:
  scripts/dev/test_task_state.py::test_add_entry_normal failed with:
    task_state_broken.py:152: in add_entry
      raise ValueError(f"kind {kind!r} not one of {', '.join(KINDS)}")
    ValueError: kind 'ship' not one of ship, report, audit, decision, signal
  scripts/dev/test_task_state.py::test_add_entry_malformed_kind_raises failed with:
    Failed: DID NOT RAISE ValueError
"""
import sys
import tempfile
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import task_state as ts


def test_utc_of_normal():
    # SOURCED: git %cI (any offset) -> UTC 'YYYY-MM-DDTHH:MM:SSZ' (scripts/dev/task_state.py:29)
    # OURS: 05:00 with +02:00 offset worked by hand is 03:00 UTC
    assert ts.utc_of("2026-11-14T05:00:00+02:00") == "2026-11-14T03:00:00Z"


def test_scope_paths_normal_and_empty():
    # SOURCED: Existing repo paths named by scope_in (scripts/dev/task_state.py:34)
    with tempfile.TemporaryDirectory() as td:
        # Empty input: card with no scope_in
        # OURS: empty card returns empty list []
        assert ts.scope_paths({}, td) == []
        # Card with empty list
        assert ts.scope_paths({"scope_in": []}, td) == []
        # Malformed input: non-existent files or tokens without dots/slashes
        assert ts.scope_paths({"scope_in": ["", "   ", "nodots", "missing/file.py:10"]}, td) == []
        # Normal input: existing file with line range and note
        dummy = Path(td) / "dummy.txt"
        dummy.write_text("hello", encoding="utf-8")
        assert ts.scope_paths({"scope_in": ["dummy.txt:10-20 (note)"]}, td) == ["dummy.txt"]


def test_add_entry_normal():
    # SOURCED: KINDS = ("ship", "report", "audit", "decision", "signal") (scripts/dev/task_state.py:15)
    # OURS: 1 valid entry added to empty latest list
    card = {"latest": []}
    res = ts.add_entry(card, "ship", "c0ffee1", "2026-11-14T01:00:00Z", "fix bug")
    assert res["latest"] == [{"kind": "ship", "ref": "c0ffee1", "utc": "2026-11-14T01:00:00Z", "line": "fix bug"}]


def test_add_entry_malformed_kind_raises():
    # SOURCED: if kind not in KINDS: raise ValueError(...) (scripts/dev/task_state.py:151-152)
    card = {"latest": []}
    with pytest.raises(ValueError, match="not one of"):
        ts.add_entry(card, "invalid_kind", "ref", "2026-11-14T01:00:00Z", "line")


def test_state_tag_empty_and_dropped():
    # SOURCED: if st == "dropped": return "DROPPED" (scripts/dev/task_state.py:206-207)
    # Empty card returns ""
    assert ts.state_tag({}, repo="/nonexistent") == ""
    # Dropped card returns "DROPPED"
    assert ts.state_tag({"state": "dropped"}, repo="/nonexistent") == "DROPPED"


def test_latest_block_empty_and_normal():
    # SOURCED: L = [f"STATE {tag}"] (scripts/dev/task_state.py:222)
    # OURS: Empty latest produces exactly 1 line "STATE READY"
    assert ts.latest_block({"latest": [], "scope_in": []}, "/nonexistent", "READY") == ["STATE READY"]
    # Normal input with 1 entry
    card = {
        "latest": [{"kind": "ship", "ref": "c0ffee1", "utc": "2026-11-14T01:00:00Z", "line": "fix bug", "auto": False}],
        "scope_in": []
    }
    # SOURCED: f"LATEST {e['kind']} {e['ref']} {e.get('utc', '')[:10]} {e.get('line', '')}".rstrip() (scripts/dev/task_state.py:224)
    assert ts.latest_block(card, "/nonexistent", "READY") == ["STATE READY", "LATEST ship c0ffee1 2026-11-14 fix bug"]
