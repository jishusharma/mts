"""gpt-spec-tests-api-job-1104: 4 spec & mutation tests for api_job.py.

Tests:
1. test_build_cmd_never_contains_key_or_key_path:
   build_cmd never contains the API key or key path under any arguments.
   Planted mutation: inject key into cmd flags -> fails.
2. test_launch_refuses_when_running_jobs_non_empty:
   launch refuses execution (exits with code 2 and prints REFUSED message) when running_jobs() is non-empty.
   Planted mutation: disable busy check in launch -> fails.
3. test_ledger_total_sums_only_spent_rows:
   ledger_total ignores non-Spent table rows (e.g. Budget or Estimated tables before/after ## Spent).
   Planted mutation: remove 'seen' check so all tables are parsed -> fails.
4. test_parse_result_returns_done_false_when_no_result_record:
   parse_result returns done: False when the jsonl file contains records but none of type 'result'.
   Planted mutation: default done to True -> fails.
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import api_job  # noqa: E402


def test_build_cmd_never_contains_key_or_key_path():
    # Verify build_cmd never leaks key or key path into argv
    cmd = api_job.build_cmd(model="claude-opus-5-5", max_usd=10.0, max_turns=150)
    flat = " ".join(cmd).lower()
    assert "key.txt" not in flat
    assert "sk-ant" not in flat
    assert "f:/claudeplaform" not in flat
    assert "f:\\\\claudeplaform" not in flat
    assert "api_key" not in flat
    assert "apikey" not in flat


def test_launch_refuses_when_running_jobs_non_empty(monkeypatch, tmp_path, capsys):
    # launch must refuse when running_jobs() returns active runs
    monkeypatch.setattr(api_job, "running_jobs", lambda: ["active-job-xyz"])
    pf = tmp_path / "p.txt"
    pf.write_text("prompt content", encoding="utf-8")
    args = MagicMock()
    args.slug = "test-job"
    args.card = None
    args.prompt_file = str(pf)
    args.dry_run = False
    with pytest.raises(SystemExit) as exc_info:
        api_job.launch(args)
    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "REFUSED: one job at a time per machine" in captured.err


def test_ledger_total_sums_only_spent_rows(tmp_path):
    # Table before ## Spent has | 2026-11-04 | with 99.00 USD
    # Table after ## Spent has | 2026-11-04 | with 5.50 USD
    content = """# Header
## Budget
| Date | Allocated | Note | Amount |
| 2026-11-04 | budget-1 | test | 99.00 |

## Spent (from the result record of each run)
| Date | Job | Model | Cost USD | Turns | Outcome |
|---|---|---|---|---|---|
| 2026-11-04 | job-a | Sonnet 5.5 | 5.50 | 10 | ok |
"""
    p = tmp_path / "LEDGER.md"
    p.write_text(content, encoding="utf-8")
    assert api_job.ledger_total(p) == pytest.approx(5.50)
    assert api_job.ledger_total(p, date="2026-11-04") == pytest.approx(5.50)


def test_parse_result_returns_done_false_when_no_result_record(tmp_path):
    out = tmp_path / "out.jsonl"
    rows = [
        {"type": "system", "message": "starting"},
        {"type": "assistant", "message": "thinking"},
        {"type": "log", "message": "running turn 1"},
    ]
    out.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    res = api_job.parse_result(out)
    assert res["done"] is False
    assert res["cost"] is None
    assert res["turns"] is None
