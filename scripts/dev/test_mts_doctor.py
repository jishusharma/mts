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
