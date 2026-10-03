"""Fixtures for scripts/sched/pick_task.py. Each runs the script as a subprocess against a temp root
(MTS_PICK_ROOT), so no live-tree file is written; tests 21-22 only read the live pipeline and register."""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "sched" / "pick_task.py"

HEAD = "| # | ID | Slug | Status | Blocker | Next |\n|---|---|---|---|---|---|\n"
BUGS_HEAD = "## BUGS\n\n| ID | Opened | Status | Severity | Title | Evidence | Receipt |\n|---|---|---|---|---|---|---|\n"


def make_root(tmp_path, rows=(), bugs=(), items=()):
    (tmp_path / "MyTradingSys" / "runtime").mkdir(parents=True)
    (tmp_path / "MyTradingSys" / "research").mkdir(parents=True)
    (tmp_path / "MyTradingSys" / "items").mkdir(parents=True)
    wave = "## WAVE 4 - ENGINE DEFECTS\n\n" + HEAD + "".join(r + "\n" for r in rows)
    (tmp_path / "MyTradingSys" / "runtime" / "BUILD_PIPELINE.md").write_text("# BUILD PIPELINE\n\n" + wave + "\n# END\n", encoding="utf-8", newline="\n")
    body = BUGS_HEAD + "".join(f"| {b[0]} | 2026-09-27 | {b[1]} | LOW | {b[2] if len(b) > 2 else 't'} | e | - |\n"
                               for b in bugs)
    (tmp_path / "MyTradingSys" / "research" / "BUGS.md").write_text(body, encoding="utf-8", newline="\n")
    for name in items:
        (tmp_path / "MyTradingSys" / "items" / name).write_text("# item\n\nFix it.\n", encoding="utf-8", newline="\n")
    return tmp_path


def run(root, **extra):
    env = {k: v for k, v in os.environ.items() if k != "MTS_PICK_COOLDOWN_H"}
    env.update(MTS_PICK_ROOT=str(root), **extra)
    return subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, env=env, cwd=REPO)


def queue(root):
    return root / "MyTradingSys" / "runtime" / "queue"


def row(n, rid, status="QUEUED", blocker="-", nxt="fix it"):
    return f"| 4.{n} | {rid} | slug words here | {status} | {blocker} | {nxt} |"


def test_1_empty_pipeline_idle(tmp_path):
    root = make_root(tmp_path)
    p = run(root)
    assert p.returncode == 0, p.stderr
    assert p.stdout.startswith("IDLE no pickable row")


def test_2_one_queued_row_writes_three_files(tmp_path):
    root = make_root(tmp_path, [row(1, "B070")], [("B070", "OPEN")], ["B070_x.md"])
    p = run(root)
    assert p.returncode == 0, p.stderr
    assert p.stdout.startswith("PICK B070 wave=4")
    q = queue(root)
    for f in ("next_task.txt", "next_task.json", "pick_log.jsonl"):
        assert (q / f).is_file(), f
    meta = json.loads((q / "next_task.json").read_text(encoding="utf-8"))
    assert meta["id"] == "B070" and meta["wave"] == 4 and meta["surface"] == "App"
    assert "B070_x.md" in meta["item_doc"]
    text = (q / "next_task.txt").read_text(encoding="utf-8")
    assert "== T0" in text and "T5" in text and "P.S : All Access" in text
    assert len((q / "pick_log.jsonl").read_text(encoding="utf-8").splitlines()) == 1


def test_3_blocked_status_skipped(tmp_path):
    root = make_root(tmp_path, [row(1, "B070", status="BLOCKED"), row(2, "B071")],
                     [("B070", "OPEN"), ("B071", "OPEN")], ["B070_x.md", "B071_y.md"])
    assert run(root).stdout.startswith("PICK B071")


def test_4_operator_blocker_skipped(tmp_path):
    root = make_root(tmp_path, [row(1, "B070", blocker="Operator decision"), row(2, "B071")],
                     [("B070", "OPEN"), ("B071", "OPEN")], ["B070_x.md", "B071_y.md"])
    assert run(root).stdout.startswith("PICK B071")


def test_5_bugs_closed_skipped(tmp_path):
    root = make_root(tmp_path, [row(1, "B070"), row(2, "B071")],
                     [("B070", "CLOSED"), ("B071", "IN-FIX")], ["B070_x.md", "B071_y.md"])
    assert run(root).stdout.startswith("PICK B071")


def test_6_wave_only_slug_without_file_skipped(tmp_path):
    root = make_root(tmp_path, [row(1, "R4-T2", nxt="return None for unknown"),
                                row(2, "R4-T3", nxt="htf_context_live.py:88 return None")])
    p = run(root)
    assert p.stdout.startswith("PICK R4-T3"), p.stdout


def test_7_prior_next_task_renamed(tmp_path):
    root = make_root(tmp_path, [row(1, "B070")], [("B070", "OPEN")], ["B070_x.md"])
    q = queue(root)
    q.mkdir(parents=True)
    (q / "next_task.txt").write_text("PRIOR PROMPT\n", encoding="utf-8", newline="\n")
    (q / "next_task.json").write_text(json.dumps({"id": "B000", "composed_utc": "2026-10-03T01:02:03Z"}), encoding="utf-8")
    assert run(root).returncode == 0
    moved = sorted(q.glob("next_task_*.txt"))
    assert len(moved) == 1 and moved[0].read_text(encoding="utf-8") == "PRIOR PROMPT\n"
    assert "20261003T010203Z" in moved[0].name
    assert "PRIOR PROMPT" not in (q / "next_task.txt").read_text(encoding="utf-8")


# ---- B087a: re-pick guard (pick_state.json) ----

def state(root):
    return json.loads((queue(root) / "pick_state.json").read_text(encoding="utf-8"))


def test_8_second_wake_holds_same_row(tmp_path):
    root = make_root(tmp_path, [row(1, "B070"), row(2, "B071")], [("B070", "OPEN"), ("B071", "OPEN")],
                     ["B070_x.md", "B071_y.md"])
    assert run(root).stdout.startswith("PICK B070")
    first = (queue(root) / "next_task.txt").read_text(encoding="utf-8")
    p = run(root)
    assert p.stdout.startswith("HOLD B070"), p.stdout
    assert (queue(root) / "next_task.txt").read_text(encoding="utf-8") == first
    assert not list(queue(root).glob("next_task_2*.txt"))
    assert state(root)["B070"]["count"] == 1
    log = [json.loads(l) for l in (queue(root) / "pick_log.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [e["result"] for e in log] == ["PICK", "HOLD"]


def test_9_cooldown_expiry_repicks_never_starves(tmp_path):
    root = make_root(tmp_path, [row(1, "B070")], [("B070", "OPEN")], ["B070_x.md"])
    assert run(root).stdout.startswith("PICK B070")
    st = state(root)
    st["B070"]["picked_utc"] = "2026-10-01T00:00:00Z"
    (queue(root) / "pick_state.json").write_text(json.dumps(st), encoding="utf-8")
    assert run(root).stdout.startswith("PICK B070")
    assert state(root)["B070"]["count"] == 2


def test_10_landed_row_leaves_state_and_next_row_is_offered(tmp_path):
    root = make_root(tmp_path, [row(1, "B070"), row(2, "B071")], [("B070", "OPEN"), ("B071", "OPEN")],
                     ["B070_x.md", "B071_y.md"])
    assert run(root).stdout.startswith("PICK B070")
    bugs = root / "MyTradingSys" / "research" / "BUGS.md"
    bugs.write_text(bugs.read_text(encoding="utf-8").replace("B070 | 2026-09-27 | OPEN", "B070 | 2026-09-27 | CLOSED"),
                    encoding="utf-8", newline="\n")
    assert run(root).stdout.startswith("PICK B071")
    assert "B070" not in state(root)


def test_11_corrupt_state_never_blocks_a_pick(tmp_path):
    root = make_root(tmp_path, [row(1, "B070")], [("B070", "OPEN")], ["B070_x.md"])
    queue(root).mkdir(parents=True)
    (queue(root) / "pick_state.json").write_text("{not json", encoding="utf-8")
    assert run(root).stdout.startswith("PICK B070")


def test_12_held_row_with_missing_prompt_is_recomposed(tmp_path):
    root = make_root(tmp_path, [row(1, "B070")], [("B070", "OPEN")], ["B070_x.md"])
    assert run(root).stdout.startswith("PICK B070")
    (queue(root) / "next_task.txt").unlink()
    (queue(root) / "next_task.json").unlink()
    assert run(root).stdout.startswith("PICK B070")
    assert (queue(root) / "next_task.txt").is_file()


def test_13_session_slug_within_20_chars(tmp_path):
    root = make_root(tmp_path, [row(1, "B070")], [("B070", "OPEN")], ["B070_x.md"])
    root_rows = (root / "MyTradingSys" / "runtime" / "BUILD_PIPELINE.md")
    root_rows.write_text(root_rows.read_text(encoding="utf-8").replace("slug words here", "alpha bravo charlie delta"),
                         encoding="utf-8", newline="\n")
    run(root)
    assert len(json.loads((queue(root) / "next_task.json").read_text(encoding="utf-8"))["slug"]) <= 20


# ---- B088: one policy surface code; cooldown default sourced from the stale-session window ----

def policy_surfaces():
    text = (REPO / "MyTradingSys" / "system" / "SURFACE_POLICY.md").read_text(encoding="utf-8")
    return re.search(r"(?m)^SURF: ([A-Z ]+)\.", text).group(1).split()


def stale_window():
    sys.path.insert(0, str(SCRIPT.parent))
    import check_sessions
    return check_sessions.MAX_OPEN


def meta(root):
    return json.loads((queue(root) / "next_task.json").read_text(encoding="utf-8"))


def test_14_session_id_surface_code_is_cli_and_in_policy(tmp_path):
    root = make_root(tmp_path, [row(1, "B070")], [("B070", "OPEN")], ["B070_x.md"])
    assert run(root).returncode == 0
    sid = meta(root)["session_id"]
    code = re.fullmatch(r"MTS-\d{4}-\d{2}-\d{2}-\d{4}Z-([A-Z]+)-BLD-[a-z0-9-]+", sid).group(1)
    assert code == "CLI" and code in policy_surfaces(), sid
    assert ("Session ID: " + sid) in (queue(root) / "next_task.txt").read_text(encoding="utf-8")


def test_15_default_cooldown_is_the_stale_session_window(tmp_path):
    # picked one hour inside the check_sessions.py stale window: still held (the unsourced 6h default re-picked it)
    root = make_root(tmp_path, [row(1, "B070"), row(2, "B071")], [("B070", "OPEN"), ("B071", "OPEN")],
                     ["B070_x.md", "B071_y.md"])
    assert run(root).stdout.startswith("PICK B070")
    st = state(root)
    at = datetime.now(timezone.utc) - stale_window() + timedelta(hours=1)
    st["B070"]["picked_utc"] = at.strftime("%Y-%m-%dT%H:%M:%SZ")
    (queue(root) / "pick_state.json").write_text(json.dumps(st), encoding="utf-8")
    p = run(root)
    assert p.stdout.startswith("HOLD B070"), p.stdout
    assert "cooldown %sh" % (stale_window().total_seconds() / 3600) in p.stdout


def test_16_env_override_still_rules(tmp_path):
    root = make_root(tmp_path, [row(1, "B070")], [("B070", "OPEN")], ["B070_x.md"])
    assert run(root).stdout.startswith("PICK B070")
    st = state(root)
    st["B070"]["picked_utc"] = (datetime.now(timezone.utc) - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    (queue(root) / "pick_state.json").write_text(json.dumps(st), encoding="utf-8")
    assert run(root, MTS_PICK_COOLDOWN_H="1").stdout.startswith("PICK B070")
    assert state(root)["B070"]["count"] == 2


# ---- B089: OPEN / IN-FIX register ids with no pipeline row are swept into one wave after the last ----

def test_17_bugs_only_row_shaped_like_b088_is_picked(tmp_path):
    # session-start state of B088: OPEN in BUGS.md, item doc present, no pipeline row. Pre-B089: IDLE.
    root = make_root(tmp_path, [], [("B088", "OPEN", "Session-id surface code split")], ["B088_session_id_surface_code.md"])
    p = run(root)
    assert p.stdout.startswith("PICK B088 wave=1"), p.stdout
    m = meta(root)
    assert m["source"] == "bugs" and m["slug"].startswith("b088-session-id")
    text = (queue(root) / "next_task.txt").read_text(encoding="utf-8")
    assert "MyTradingSys/research/BUGS.md" in text and "B088_session_id_surface_code.md" in text


def test_18_pipeline_rows_first_then_swept_row(tmp_path):
    root = make_root(tmp_path, [row(1, "B070")], [("B070", "OPEN"), ("B088", "OPEN")], ["B070_x.md", "B088_y.md"])
    assert run(root).stdout.startswith("PICK B070 wave=4")
    assert meta(root)["source"] == "pipeline"
    bugs = root / "MyTradingSys" / "research" / "BUGS.md"
    bugs.write_text(bugs.read_text(encoding="utf-8").replace("B070 | 2026-09-27 | OPEN", "B070 | 2026-09-27 | CLOSED"),
                    encoding="utf-8", newline="\n")
    p = run(root)
    assert p.stdout.startswith("PICK B088 wave=5"), p.stdout


def test_19_swept_rows_need_pickable_status_and_item_doc(tmp_path):
    root = make_root(tmp_path, [], [("B090", "CLOSED"), ("B091", "OPEN"), ("T092", "IN-FIX")],
                     ["B090_x.md", "T092_z.md"])
    assert run(root).stdout.startswith("PICK T092"), "B090 closed, B091 has no item doc"


def test_20_id_with_a_pipeline_row_is_never_swept(tmp_path):
    root = make_root(tmp_path, [row(1, "B070", status="BLOCKED")], [("B070", "OPEN")], ["B070_x.md"])
    assert run(root).stdout.startswith("IDLE"), "the pipeline row governs; BLOCKED stays unpicked"


def live_import():
    sys.path.insert(0, str(SCRIPT.parent))
    import pick_task
    pipe = (REPO / "MyTradingSys" / "runtime" / "BUILD_PIPELINE.md").read_text(encoding="utf-8")
    bugs = (REPO / "MyTradingSys" / "research" / "BUGS.md").read_text(encoding="utf-8")
    return pick_task, pick_task.parse_pipeline(pipe), pick_task.parse_bug_rows(bugs)


def test_21_live_tree_every_open_register_id_is_a_candidate():
    pt, rows, bug_rows = live_import()
    cand = {r["id"] for r in rows + pt.sweep_rows(rows, bug_rows)}
    missing = [i for i, s, _ in bug_rows if s in pt.PICKABLE_BUGS and i not in cand]
    assert not missing, missing


def test_22_live_pipeline_records_b088_b089_landed():
    _, rows, _ = live_import()
    got = {r["id"]: r["status"] for r in rows if r["id"] in ("B088", "B089")}
    assert got == {"B088": "LANDED", "B089": "LANDED"}, got
