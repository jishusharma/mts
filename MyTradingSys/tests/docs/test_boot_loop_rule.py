"""A station session (no role line) loops the queue instead of stopping after one task (bug-station-session-stops-after-one-task).

Fail-first: on the pre-change CLAUDE.md / WORKERS.md / ROLES.md these tests fail.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def read(rel):
    return (REPO / rel).read_text(encoding="utf8")


def test_claude_md_points_station_to_loop():
    t = read("CLAUDE.md")
    step3 = re.search(r"^3\. .*$", t, re.M).group(0)
    assert "Station" in step3 and "loop" in step3 and "WORKERS.md rule 10" in step3
    step5 = re.search(r"^5\. SHORT SESSIONS.*$", t, re.M).group(0)
    assert "single-task workers only" in step5
    assert "ONE task" not in step3


def test_workers_rule_10_loop_and_dedupe():
    t = read("MyTradingSys/system/WORKERS.md")
    m = re.search(r"^10\. \*\*Station loop.*$", t, re.M)
    assert m, "rule 10 missing"
    r = m.group(0)
    for need in ("no role line", "Builder", "git fetch", "LENOVO_NEXT_SESSION.md", "login plan",
                 "tasks.py next", "sync.py claims", "mts_signal.py read --hours 1"):
        assert need in r, need


def test_roles_md_mentions_builder_fallback_loop():
    assert "WORKERS.md rule 10" in read("MyTradingSys/system/ROLES.md")
