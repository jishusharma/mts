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


# ---- fold (C2) ----
import subprocess


def _git(root, *a):
    return subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, check=True).stdout


def fold_repo(tmp_path):
    root = tmp_path / "repo"
    (root / "MyTradingSys/system/tasks").mkdir(parents=True)
    (root / "scripts/dev").mkdir(parents=True)
    (root / "MyTradingSys/system/tasks/card-a.json").write_text(json.dumps({"id": "card-a", "state": "ready"}) + chr(10), encoding="utf-8")
    for f in ("scripts/dev/desk.py", "scripts/dev/lease.py", "scripts/dev/named.py"):
        (root / f).write_text("x=1" + chr(10), encoding="utf-8")
    _git(root, "init", "-q", "-b", "work")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
    _git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base")
    _git(root, "update-ref", "refs/remotes/origin/fast-track", "HEAD")
    return root


def fold_transcript(path, root):
    ab = lambda r: str(root / r)
    ts = "2026-10-25T10:00:00Z"
    ev = [{"type": "user", "timestamp": ts, "message": {"content": "You are Builder. Card: card-a. Edit scripts/dev/named.py"}}]
    reads = [ab("scripts/dev/desk.py"), ab("scripts/dev/lease.py"), ab("scripts/dev/desk.py"), ab("scripts/dev/named.py"),
             ab("scripts/dev/not_on_trunk.py"), "C:/tmp/scratchpad/x.py"]
    for i, r in enumerate(reads):
        ev.append(asst(ts, 70000 + i, tool=("Read", {"file_path": r})))
    ev.append(asst(ts, 80000, tool=("Edit", {"file_path": ab("scripts/dev/named.py")})))
    ev.append(asst(ts, 80001, tool=("Read", {"file_path": ab("scripts/dev/after_edit.py")})))
    path.write_text(chr(10).join(json.dumps(e) for e in ev) + chr(10), encoding="utf-8")
    return str(path)


def test_fold_writes_trunk_reads_only_into_the_card_and_commits_it(tmp_path):
    root = fold_repo(tmp_path)
    tp = fold_transcript(tmp_path / "s.jsonl", root)
    assert G.fold(tp, str(root), now=SINCE) == ("folded", "card-a")
    card = json.load(open(root / "MyTradingSys/system/tasks/card-a.json"))
    assert card["context"]["reads"] == ["scripts/dev/desk.py", "scripts/dev/lease.py"]   # most-read first; named, off-trunk, scratchpad, post-edit dropped
    assert card["context"]["calls_to_edit"] == 6 and card["context"]["folded"] == "2026-10-25T00:00:00Z"
    assert _git(root, "status", "--short").strip() == "" and "fold context into card card-a" in _git(root, "log", "-1", "--format=%B")
    assert "Builder" not in json.dumps(card)   # paths only, never transcript text
    assert G.fold(tp, str(root), now=SINCE)[0] == "folded" and len(json.load(open(root / "MyTradingSys/system/tasks/card-a.json"))["context"]["reads"]) == 2   # replace, never append


def test_fold_without_card_or_transcript_is_unfolded_not_an_error(tmp_path):
    root = fold_repo(tmp_path)
    assert G.fold(str(tmp_path / "missing.jsonl"), str(root))[0] == "unfolded"
    p = tmp_path / "s.jsonl"
    p.write_text(json.dumps({"type": "user", "message": {"content": "no card here"}}) + chr(10), encoding="utf-8")
    assert G.fold(str(p), str(root))[0] == "unfolded"


def test_ship_hook_folds_and_never_blocks(tmp_path):
    import preship
    root = fold_repo(tmp_path)
    tp = fold_transcript(tmp_path / "s.jsonl", root)
    out = json.loads(preship.hook_commit({"cwd": str(root), "transcript_path": tp, "tool_input": {"command": "python scripts/dev/sync.py ship --release x"}}))
    assert "folded: card-a" in out["hookSpecificOutput"]["additionalContext"] and "permissionDecision" not in out["hookSpecificOutput"]
    bad = json.loads(preship.hook_commit({"cwd": str(root), "transcript_path": str(tmp_path / "none"), "tool_input": {"command": "python sync.py ship"}}))
    assert "unfolded" in bad["hookSpecificOutput"]["additionalContext"]
    assert preship.hook_commit({"cwd": str(root), "tool_input": {"command": "python scripts/dev/sync.py shipped"}}) == ""


def test_fold_reads_a_subagent_file_and_finds_the_card_by_branch_slug(tmp_path):
    root = fold_repo(tmp_path)
    _git(root, "checkout", "-q", "-b", "host/card-a-2")
    sub = tmp_path / "sess" / "subagents"
    sub.mkdir(parents=True)
    tp = fold_transcript(sub / "agent-x.jsonl", root)
    lines = [json.loads(x) for x in open(tp).read().splitlines()]
    for e in lines:
        e["isSidechain"] = True
    lines[0]["message"]["content"] = "You are Builder. no card id here"
    open(tp, "w").write(chr(10).join(json.dumps(e) for e in lines) + chr(10))
    assert G.fold(tp, str(root), now=SINCE) == ("folded", "card-a")


def test_ship_hook_follows_a_leading_cd(tmp_path):
    import preship
    root = fold_repo(tmp_path)
    tp = fold_transcript(tmp_path / "s.jsonl", root)
    out = json.loads(preship.hook_commit({"cwd": str(tmp_path), "transcript_path": tp, "tool_input": {"command": f"cd {root} && python scripts/dev/sync.py ship"}}))
    assert "folded: card-a" in out["hookSpecificOutput"]["additionalContext"]
