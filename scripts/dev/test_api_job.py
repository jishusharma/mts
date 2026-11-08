"""api_job.py: headless Builder jobs on the Claude API credit (PLAN_24H_2026-11-04.md). Stdlib + pytest."""
from __future__ import annotations
import io
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import api_job  # noqa: E402


def test_build_cmd_api_engine_is_default_and_carries_caps(tmp_path):
    cmd = api_job.build_cmd(model="claude-opus-5-5", max_usd=8.0, max_turns=200, cwd="C:/x", out_dir="F:/MTS/api_runs/s")
    flat = " ".join(cmd)
    assert "sk-ant" not in flat and "key.txt" not in flat
    assert cmd[1].endswith("api_agent.py") and "claude" not in Path(cmd[0]).name
    for flag in ("--max-usd", "8.0", "--max-turns", "200", "--model", "claude-opus-5-5", "--cwd", "C:/x", "--out", "F:/MTS/api_runs/s"):
        assert flag in cmd, flag


def test_build_cmd_never_carries_the_key_and_sets_every_guard(tmp_path):
    cmd = api_job.build_cmd(model="claude-opus-5-5", max_usd=8.0, max_turns=200, engine="claude")
    flat = " ".join(cmd)
    assert "sk-ant" not in flat and "key.txt" not in flat
    for flag in ("--max-budget-usd", "8.0", "--max-turns", "200", "--permission-mode", "bypassPermissions",
                 "--output-format", "stream-json", "--model", "claude-opus-5-5", "-p"):
        assert flag in cmd, flag
    assert '"disableAllHooks":true' in flat.replace(" ", "")


def test_child_env_has_key_and_no_oauth(tmp_path):
    kf = tmp_path / "k.txt"
    kf.write_text(" sk-test-abc \r\n", encoding="utf-8")
    env = api_job.child_env({"CLAUDE_CODE_OAUTH_TOKEN": "x", "CLAUDECODE": "1", "PATH": "p"}, kf)
    assert env["ANTHROPIC_API_KEY"] == "sk-test-abc"
    assert "CLAUDE_CODE_OAUTH_TOKEN" not in env and "CLAUDECODE" not in env and env["PATH"] == "p"


def test_prompt_with_secret_path_is_refused():
    with pytest.raises(SystemExit):
        api_job.check_prompt("read .secrets/x and F:/ClaudePlaform/key.txt")
    api_job.check_prompt("build the cbp harness")  # no raise


def test_parse_result_reads_the_last_result_record(tmp_path):
    out = tmp_path / "out.jsonl"
    rows = [{"type": "system"}, {"type": "assistant"},
            {"type": "result", "subtype": "success", "total_cost_usd": 1.2616, "duration_ms": 1020000, "num_turns": 49,
             "result": "Result: shipped 561df2f0"}]
    out.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    r = api_job.parse_result(out)
    assert r["cost"] == pytest.approx(1.2616) and r["turns"] == 49 and r["minutes"] == 17 and r["subtype"] == "success"
    assert r["done"] is True
    (tmp_path / "running.jsonl").write_text('{"type":"system"}\n', encoding="utf-8")
    assert api_job.parse_result(tmp_path / "running.jsonl")["done"] is False


def test_ledger_row_appends_under_spent_table(tmp_path):
    plan = tmp_path / "PLAN.md"
    plan.write_text("# plan\n\n## Spent (from the result record of each run)\n| Date | Job | Model | Cost USD | Turns | Outcome |\n|---|---|---|---|---|---|\n| 2026-11-04 | a | Haiku 5.5 | 0.03 | 23 | x |\n",
                    encoding="utf-8")
    api_job.ledger_append(plan, date="2026-11-05", job="s4-cbp", model="claude-opus-5-5", cost=7.1234, turns=120, outcome="shipped abc; cap was 8")
    text = plan.read_text(encoding="utf-8")
    assert text.rstrip().endswith("| 2026-11-05 | s4-cbp | Opus 5.5 | 7.12 | 120 | shipped abc; cap was 8 |")
    assert api_job.ledger_total(plan) == pytest.approx(7.15, abs=0.01)


def test_compose_prompt_has_preamble_and_brief():
    p = api_job.compose_prompt("CARD BRIEF TEXT", slug="s4-cbp", card="s4-cbp-module-e2e")
    assert p.startswith("You are Builder.")
    assert "sync.py start s4-cbp --worker" in p and "CARD BRIEF TEXT" in p and "Result:" in p and "never ask" in p


def test_launch_wait_line_names_the_harness_tracked_watcher():
    """stall-fix-1104: the printed bg_watch line was run with `&` and woke nobody (L1 idle 09:35Z-12:40Z)."""
    w = api_job.wait_line()
    assert "supervisor.py wait" in w and "run_in_background" in w and "bg_watch" not in w
