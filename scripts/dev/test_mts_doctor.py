import json
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mts_doctor as D

NL = chr(10)
LONG = "Never push to master and never rebase or force push anything on the shared trunk under any circumstances at all."
DAY = datetime(2026, 10, 17, tzinfo=timezone.utc)


def make_repo(tmp_path, tasks_out="tasks lint: 0 cards OK"):
    def w(rel, text):
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text, encoding="utf-8", newline=NL)
    w("CLAUDE.md", "Boot: run `scripts/dev/gone.py` now" + NL + "Read WHERE.md first" + NL + LONG + NL)
    w("MyTradingSys/system/RULES.md", LONG + NL + "Real: `scripts/dev/here.py`" + NL)
    w("scripts/dev/here.py", "x = 1" + NL)
    w("scripts/dev/tasks.py", f"print({tasks_out!r})" + NL)
    w(".claude/skills/bad/SKILL.md", "no frontmatter here" + NL)
    mem = tmp_path / "mem"
    mem.mkdir()
    (mem / "MEMORY.md").write_text("- [Gone](gone_memory.md) - hook" + NL, encoding="utf-8")
    (mem / "orphan.md").write_text("x", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    return mem


def test_each_detector_fires_on_its_own_input(tmp_path):
    mem = make_repo(tmp_path, "WARN t1 (ready): STALE latest never refreshed")
    _, f = D.run(tmp_path, tmp_path / "out", mem, process=False, now=DAY)
    got = [(k, w.split(":")[0], m) for k, w, m, _ in f]
    assert ("DEAD-REF", "CLAUDE.md", "names scripts/dev/gone.py which is not tracked") in got      # PATH_RE
    assert ("DEAD-REF", "CLAUDE.md", "names WHERE.md which does not exist") in got                  # BARE_DOC_RE
    assert not any("here.py" in m for _, _, m in got)                                              # a tracked path is fine
    assert any(k == "DUPLICATE" and "CLAUDE.md" in w and "RULES.md" in w for k, w, _ in got)
    assert ("MEMORY", "MEMORY.md", "lists gone_memory.md which does not exist") in got
    assert ("MEMORY", "orphan.md", "is not in MEMORY.md (never recalled)") in got
    assert any(k == "SKILL" and w.endswith("SKILL.md") for k, w, _ in got)
    assert any(k == "CARD" and w == "t1" for k, w, _ in got)                                       # tasks.py WARN line


def test_writes_only_the_report_and_names_boot_cost_apart_from_findings(tmp_path):
    mem = make_repo(tmp_path)
    before = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file() and ".git" not in p.parts)
    path, findings = D.run(tmp_path, tmp_path / "out", mem, process=False, now=DAY)
    after = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file() and ".git" not in p.parts)
    assert [p for p in after if p not in before] == [os.path.join("out", "REPORT_2026-10-17.md")]
    text = path.read_text(encoding="utf-8")
    assert "Boot cost: CLAUDE.md" in text and not any(k == "BOOT-COST" for k, *_ in findings)


def test_same_day_run_twice_gives_the_same_report(tmp_path):
    mem = make_repo(tmp_path)
    a = D.run(tmp_path, tmp_path / "out", mem, process=False, now=DAY)[0].read_text(encoding="utf-8")
    b = D.run(tmp_path, tmp_path / "out", mem, process=False, now=DAY)[0].read_text(encoding="utf-8")
    assert a == b


def test_missing_memory_dir_is_reported_as_skipped(tmp_path):
    make_repo(tmp_path)
    assert D.memory_drift(tmp_path / "nope") == [] and D.memory_drift(None) == []
    text = D.run(tmp_path, tmp_path / "out", None, process=False, now=DAY)[0].read_text(encoding="utf-8")
    assert "Memory: skipped" in text


def test_previous_metrics_reads_the_newest_older_report(tmp_path):
    (tmp_path / "REPORT_2026-10-15.md").write_text("METRICS overhead=70 b4=5" + NL, encoding="utf-8")
    (tmp_path / "REPORT_2026-10-16.md").write_text("x" + NL + "METRICS overhead=63 b4=13" + NL, encoding="utf-8")
    (tmp_path / "REPORT_2026-10-17.md").write_text("METRICS overhead=1" + NL, encoding="utf-8")
    assert D.previous_metrics(tmp_path, "2026-10-17") == {"overhead": "63", "b4": "13"}
    assert D.previous_metrics(tmp_path, "2026-10-01") == {}


def test_shared_line_in_per_skill_files_is_not_a_duplicate(tmp_path):
    for n in ("a", "b"):
        f = tmp_path / f"relay/{n}.SKILL.md"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(LONG + NL, encoding="utf-8", newline=NL)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    assert D.duplicates(tmp_path, ["relay/a.SKILL.md", "relay/b.SKILL.md"]) == []


def test_stale_main_checkout_hooks_are_reported(tmp_path):
    """Hooks and env load from the main checkout, not the worktree: seen 2026-10-21, a main checkout 1858 commits behind ran
    the old turn_meter.py and a removed auto-compact override, so the trunk policy was not live (review item 1)."""
    for rel in D.HOOK_FILES:
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("trunk" + NL, encoding="utf-8", newline=NL)
    git = lambda *a: subprocess.run(["git", *a], cwd=tmp_path, check=True, capture_output=True)
    git("init", "-q")
    git("add", "-A")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "x")
    git("update-ref", "refs/remotes/origin/fast-track", "HEAD")
    assert D.hook_drift(tmp_path) == []
    (tmp_path / D.HOOK_FILES[0]).write_text("old" + NL, encoding="utf-8", newline=NL)
    got = D.hook_drift(tmp_path)
    assert [(k, w) for k, w, _, _ in got] == [("HOOKS", str(tmp_path / D.HOOK_FILES[0]))]



def test_twin_cards_are_reported(tmp_path):
    make_repo(tmp_path)
    (tmp_path / "scripts/dev/tasks.py").write_text(
        "import sys" + NL + "print('TWIN a b (title 0.31)' if sys.argv[1:] == ['twins'] else 'tasks lint: 0 cards OK')" + NL,
        encoding="utf-8", newline=NL)
    got = D.dup_cards(tmp_path)
    assert [(k, w) for k, w, _, _ in got] == [("DUP-CARD", "a + b")]
    assert "DUP-CARD" in D.KINDS


# ---- checklist (2026-10-25): one test per check, fixture inputs
def _w(tmp_path, rel, text):
    f = tmp_path / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(text.encode())
    return f


def _size_repo(tmp_path, claude_bytes, role_bytes):
    _w(tmp_path, "CLAUDE.md", "x" * claude_bytes)
    _w(tmp_path, "MyTradingSys/tests/docs/test_integrity.py", 'SIZE_CAPS = {"CLAUDE.md": 1000}')
    _w(tmp_path, "MyTradingSys/system/roles/a.md", "y" * role_bytes)
    _w(tmp_path, "MyTradingSys/tests/test_role_budget.py",
       'BUDGET = {"a.md": 500}\ndef crlf_size(d):\n    lf = d.replace(b"\\r\\n", b"\\n")\n    return len(lf) + lf.count(b"\\n")\n')


def test_size_headroom_ok_warn_and_unavailable(tmp_path):
    _size_repo(tmp_path, 900, 400)
    assert D.size_headroom(tmp_path)[0] == "OK"
    _size_repo(tmp_path, 990, 400)                       # 1% headroom under SIZE_CAPS
    st, msg = D.size_headroom(tmp_path)
    assert st == "WARN" and "CLAUDE.md 990/1000" in msg
    _size_repo(tmp_path, 900, 400)
    _w(tmp_path, "MyTradingSys/system/roles/a.md", "\n".join(["z" * 8] * 55))   # 54 LF -> 54 more CRLF bytes: 494 + 54 > 485 limit
    st, msg = D.size_headroom(tmp_path)
    assert st == "WARN" and "roles/a.md" in msg and "BUDGET" in msg
    st, msg = D.size_headroom(tmp_path / "nope")
    assert st == "unavailable" and "caps not readable" in msg


def _run(sha, conclusion, minute):
    return {"head_sha": sha * 8, "conclusion": conclusion, "created_at": f"2026-10-25T10:{minute:02d}:00Z"}


def test_ci_revert_fast_slow_and_red_now():
    now = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
    assert D.ci_revert([_run("a", "success", 0), _run("b", "failure", 5), _run("c", "success", 12)], now)[0] == "OK"
    st, msg = D.ci_revert([_run("b", "failure", 5), _run("c", "success", 30)], now)
    assert st == "WARN" and "25 min" in msg
    st, msg = D.ci_revert([_run("a", "success", 0), _run("b", "failure", 5)], now)
    assert st == "WARN" and "red now" in msg
    assert D.ci_revert([], now)[0] == "unavailable"


def test_ship_time_median_max_missing_log(tmp_path):
    now = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
    assert D.ship_time(tmp_path / "none.jsonl", now)[0] == "unavailable"
    log = tmp_path / "t.jsonl"
    row = lambda step, secs, utc, sha: json.dumps({"step": step, "secs": secs, "utc": utc, "sha": sha})
    log.write_text("\n".join([row("ship_wall", 60, "2026-10-25T10:00:00Z", "a"), row("ship_wall", 110, "2026-10-25T10:10:00Z", "b"),
                              row("4", 300, "2026-10-25T10:20:00Z", "c"), row("5b", 100, "2026-10-25T10:21:00Z", "c"),
                              row("ship_wall", 9999, "2026-10-24T10:00:00Z", "old"), row("ship", 9999, "2026-10-25T10:00:00Z", "z"), "not json"]) + "\n", encoding="utf-8")
    st, msg = D.ship_time(log, now)
    assert st == "OK" and "ship_wall n=2 median 85s p90 110s" in msg and "gate n=1" in msg      # gate wall: 10:15 -> 10:21 = 6 min
    log.write_text(row("ship_wall", 130, "2026-10-25T10:00:00Z", "a") + "\n", encoding="utf-8")
    st, msg = D.ship_time(log, now)
    assert st == "WARN" and "120s" in msg                                                  # 2-minute ship: median over 120 s warns
    log.write_text("\n".join(row("ship_wall", s, "2026-10-25T10:00:00Z", "a") for s in [50] * 8 + [200, 200]) + "\n", encoding="utf-8")
    assert D.ship_time(log, now)[0] == "WARN"                                                  # median fine, p90 over 120 s warns
    log.write_text(row("ship", 16 * 60, "2026-10-25T10:00:00Z", "a") + "\n", encoding="utf-8")
    assert D.ship_time(log, now)[0] == "unavailable"                                                    # the old per-sync row no longer decides


def test_hook_reg_missing_hooks_and_behind(tmp_path):
    git = lambda *a: subprocess.run(["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True, capture_output=True)
    git("init", "-q")
    assert D.hook_reg(tmp_path)[0] == "WARN"                                       # no settings.json
    _w(tmp_path, ".claude/settings.json", '{"hooks": "role_loader.py ci_watch.py"}')
    git("add", "-A")
    git("commit", "-qm", "x")
    assert D.hook_reg(tmp_path)[0] == "OK"
    _w(tmp_path, ".claude/settings.json", '{"hooks": "role_loader.py"}')
    st, msg = D.hook_reg(tmp_path)
    assert st == "WARN" and "ci_watch not registered" in msg
    D.HOOKS_BEHIND_MAX, old = -1, D.HOOKS_BEHIND_MAX                              # force the behind rule with one commit of lag
    try:
        git("commit", "-qam", "y")
        git("update-ref", "refs/remotes/origin/fast-track", "HEAD~1")
        git("tag", "t")
        git("reset", "-q", "--hard", "HEAD~1")
        git("update-ref", "refs/remotes/origin/fast-track", "t")
        _w(tmp_path, ".claude/settings.json", '{"hooks": "role_loader.py ci_watch.py"}')
        assert "behind" in D.hook_reg(tmp_path)[1]
    finally:
        D.HOOKS_BEHIND_MAX = old


def test_disk_warns_under_limit(tmp_path):
    assert D.disk(tmp_path, free_gb=14.9)[0] == "WARN"
    assert D.disk(tmp_path, free_gb=15.1)[0] == "OK"


def test_health_line_and_report_top(tmp_path):
    assert D.health_line([("A", "OK", ""), ("B", "unavailable", "")]) == "HEALTH: GREEN"
    assert D.health_line([("A", "WARN", ""), ("B", "OK", ""), ("C", "WARN", "")]) == "HEALTH: 2 WARN: A, C"
    mem = make_repo(tmp_path)
    text = D.run(tmp_path, tmp_path / "out", mem, process=False, now=DAY)[0].read_text(encoding="utf-8")
    assert text.splitlines()[0].startswith("HEALTH: ") and "CI-REVERT: skipped" in text
    assert [n for n, _, _ in D.checklist(tmp_path, process=False)] == list(D.CHECK_NAMES)


def test_context_gap_warns_when_unnamed_reads_rose(tmp_path):
    f = tmp_path / "runs.jsonl"
    f.write_text(json.dumps({"utc": "a", "unnamed_reads_median": 1}) + NL + json.dumps({"utc": "b", "unnamed_reads_median": 3}) + NL)
    assert D.context_gap(tmp_path, f)[0] == "WARN"
    f.write_text(json.dumps({"utc": "a", "unnamed_reads_median": 3}) + NL + json.dumps({"utc": "b", "unnamed_reads_median": 3}) + NL)
    assert D.context_gap(tmp_path, f)[0] == "OK"


def test_waiting_on_operator_lists_old_cards_and_questions(tmp_path):
    d = tmp_path / "MyTradingSys" / "system" / "tasks"
    d.mkdir(parents=True)
    card = lambda i, **k: (d / f"{i}.json").write_text(json.dumps({"id": i, "state": "raw", "created": "2026-10-10T00:00:00Z", **k}))
    card("old-wait", note="waits: ask the operator first")
    card("old-fine", note="plain")
    card("new-wait", note="needs approval", created="2026-10-17T00:00:00Z")
    qs = [{"utc": "2026-10-10T00:00:00Z", "id": "Q1"}, {"utc": "2026-10-17T00:00:00Z", "id": "Q2"}]
    st, detail = D.waiting_on_operator(tmp_path, DAY, qs)
    assert st == "WARN" and "old-wait" in detail and "old-fine" not in detail and "new-wait" not in detail
    assert "Q1" in detail and "Q2" not in detail and "live-tree change wait for him" in detail
    assert D.waiting_on_operator(tmp_path, DAY, [])[0] == "WARN"
    (d / "old-wait.json").unlink()
    assert D.waiting_on_operator(tmp_path, DAY, [])[0] == "OK"


def test_broadcast_warns_on_unacked_and_expired_told_for_a_seen_host():
    import mts_signal as S
    now = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)

    def t(h):
        return (now.replace(tzinfo=None) - __import__("datetime").timedelta(hours=h)).strftime("%Y%m%dT%H%M%SZ")
    b = {"t": t(30), "from": "jis-nuc/C", "to": "all", "kind": "broadcast", "prio": "high", "id": "b-aaaaaa", "cmd": "x", "text": "t"}
    seen = {"t": t(1), "from": "desktop-lenovo/C", "to": "all", "kind": "note", "text": "loop"}
    told = {"t": t(25), "from": "jis-nb/B", "kind": "ack", "id": "b-aaaaaa", "state": "told", "host": "jis-nb", "note": "no admin"}
    nb = {"t": t(2), "from": "jis-nb/B", "to": "all", "kind": "note", "text": "hi"}
    status, detail = D.broadcast_check(".", rows=[b, seen, told, nb], now=now)
    assert status == "WARN" and "desktop-lenovo b-aaaaaa" in detail and "jis-nb b-aaaaaa" in detail
    done = {**told, "state": "done", "t": t(3)}
    assert D.broadcast_check(".", rows=[b, seen, told, nb, done], now=now)[0] == "WARN"   # lenovo still none
    ack_l = {"t": t(1), "from": "desktop-lenovo/C", "kind": "ack", "id": "b-aaaaaa", "state": "done", "host": "desktop-lenovo"}
    assert D.broadcast_check(".", rows=[b, seen, told, nb, done, ack_l], now=now)[0] == "OK"
    fresh = {**b, "t": t(5)}                                                                 # under 6 h: not yet
    assert D.broadcast_check(".", rows=[fresh, seen], now=now)[0] == "OK"
