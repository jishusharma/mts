"""context_gap: fixture jsonl sessions, in-process."""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import context_gap as G


def asst(ts, tot, cw=0, tool=None):
    blocks = [{"type": "tool_use", "name": tool[0], "input": tool[1]}] if tool else []
    return {"type": "assistant", "timestamp": ts, "message": {"content": blocks, "usage": {"input_tokens": tot - cw, "cache_creation_input_tokens": cw}}}


def session(path, reads, ts="2026-10-25T10:00:00Z"):
    ev = [{"type": "user", "timestamp": ts, "message": {"content": "work on scripts/dev/a.py please"}}]
    for i, r in enumerate(reads):
        ev.append(asst(ts, 70000 + i, tool=("Read", {"file_path": r})))
    ev.append(asst(ts, 90000, cw=60000, tool=("Edit", {"file_path": "scripts/dev/a.py"})))
    ev += [asst(ts, 90000 + i) for i in range(3)]
    ev.insert(3, {"type": "user", "timestamp": ts, "message": {"content": [{"type": "tool_result", "content": "STATE SHIPPED@abc"}]}})
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(json.dumps(e) for e in ev) + "\n")


def proj(tmp, reads):
    d = tmp / "C--Users-E-ngineers-IdeaProjects-BinanceDataFeed"
    d.mkdir()
    session(str(d / "s1.jsonl"), reads)
    return str(tmp)


SINCE = datetime(2026, 10, 25, tzinfo=timezone.utc)


def test_metrics_from_fixture(tmp_path):
    s = G.parse_session(os.path.join(proj(tmp_path, ["scripts/dev/a.py", "STATUS.md", "x/y.py"]), "C--Users-E-ngineers-IdeaProjects-BinanceDataFeed", "s1.jsonl"))
    assert s["calls_to_edit"] == 3 and s["unnamed_reads"] == 2 and s["ctx_at_edit"] == 90000
    assert s["base"] == 70000 and s["stale"] == 1 and s["rewrites"] == 1


def test_gate_fails_when_misses_rose_and_row_has_no_text(tmp_path):
    runs = str(tmp_path / "runs.jsonl")
    p = proj(tmp_path, ["scripts/dev/a.py"])
    row1, bad1 = G.measure(SINCE, runs, p)
    assert bad1 == [] and row1["unnamed_reads_median"] == 0
    import shutil
    shutil.rmtree(os.path.join(p, "C--Users-E-ngineers-IdeaProjects-BinanceDataFeed"))
    p = proj(tmp_path, ["STATUS.md", "b/c.py", "d/e.py"])
    row2, bad2 = G.measure(SINCE, runs, p)
    assert any(b.startswith("unnamed_reads_median") for b in bad2)
    lines = open(runs).read().splitlines()
    open(runs, "w").write(lines[0] + chr(10))
    assert G.main(["measure", "--since", "2026-10-25T00:00:00Z", "--gate", "--runs", runs, "--projects", p, "--no-append"]) == 1
    assert "please" not in open(runs).read()
