"""RU5: Lab pre-check zero-token checks in tasks.py check (formula id, holdout path, split dates)."""
from argparse import Namespace
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
import tasks


def valid_card(cid="lab-card-1", **kw):
    c = {
        "id": cid,
        "title": "Lab Card Test",
        "state": "ready",
        "lane": "SONNET",
        "prio": 3,
        "size": "S",
        "est_turns": 10,
        "worker": "agent",
        "goal": "Test goal",
        "done_when": "Test passes",
        "steps": ["Step 1"],
        "scope_in": ["scripts/dev/tasks.py"],
        "tests": "MyTradingSys/tests/test_tasks_lab_precheck.py",
        "created": "2026-10-18T10:00:00Z",
        "depends_on": [],
        "note": "",
        "weight": "",
        "live_path": False,
    }
    c.update(kw)
    return c


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(tasks, "REPO", tmp_path)
    # Create minimal FORMULAS.md
    f_path = tmp_path / tasks.FORMULAS
    f_path.parent.mkdir(parents=True, exist_ok=True)
    f_path.write_text("# Section 15\nFormula details\n## Section 22.1\nAnother formula\n", encoding="utf-8")
    # Create empty tasks directory
    (tmp_path / "MyTradingSys" / "system" / "tasks").mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_missing_formula_id_reported_in_problems(repo):
    card = valid_card("card-bad-formula", formula_id="s9999")
    probs = tasks.problems(card, repo=repo)
    assert any("formula id 's9999' not found" in p for p in probs)


def test_valid_formula_id_passes_in_problems(repo):
    card = valid_card("card-good-formula", formula_id="s15")
    probs = tasks.problems(card, repo=repo)
    assert not any("formula id" in p for p in probs)


def test_missing_holdout_path_reported_in_problems(repo):
    card = valid_card("card-bad-holdout", holdout_path="data/missing_holdout.csv", split_dates=["2024-01-01", "2024-07-01"])
    probs = tasks.problems(card, repo=repo)
    assert any("holdout path 'data/missing_holdout.csv' not found" in p for p in probs)


def test_valid_holdout_path_and_split_dates_pass(repo):
    h = repo / "data" / "clean_holdout.csv"
    h.parent.mkdir(parents=True, exist_ok=True)
    h.write_text("t,open,close\n1,10,11\n", encoding="utf-8")
    card = valid_card("card-good-holdout", holdout_path="data/clean_holdout.csv", split_dates=["2024-01-01", "2024-07-01"])
    probs = tasks.problems(card, repo=repo)
    assert not any("holdout path" in p for p in probs)
    assert not any("split dates" in p for p in probs)


def test_missing_split_dates_when_holdout_path_specified(repo):
    h = repo / "data" / "clean_holdout.csv"
    h.parent.mkdir(parents=True, exist_ok=True)
    h.write_text("t,open,close\n1,10,11\n", encoding="utf-8")
    card = valid_card("card-no-split", holdout_path="data/clean_holdout.csv")
    probs = tasks.problems(card, repo=repo)
    assert any("split dates is empty" in p for p in probs)


def test_empty_split_dates_field_reported(repo):
    card = valid_card("card-empty-split", split_dates=[])
    probs = tasks.problems(card, repo=repo)
    assert any("split dates is empty" in p for p in probs)


def test_cmd_check_fails_with_exit_1_on_missing_formula_id(repo):
    card = valid_card("card-formula-fail", formula_id="s9999")
    tasks.save(repo, card)
    rc = tasks.cmd_check(Namespace(id=card["id"], demote=False))
    assert rc == 1


def test_cmd_check_fails_with_exit_1_on_missing_holdout(repo):
    card = valid_card("card-holdout-fail", holdout_path="nonexistent/holdout.csv", split_dates=["2024-01-01"])
    tasks.save(repo, card)
    rc = tasks.cmd_check(Namespace(id=card["id"], demote=False))
    assert rc == 1


def test_cmd_check_passes_with_exit_0_on_valid_card(repo):
    h = repo / "data" / "clean_holdout.csv"
    h.parent.mkdir(parents=True, exist_ok=True)
    h.write_text("t,open,close\n1,10,11\n", encoding="utf-8")
    card = valid_card("card-valid", formula_id="s15", holdout_path="data/clean_holdout.csv", split_dates=["2024-01-01", "2024-07-01"])
    tasks.save(repo, card)
    rc = tasks.cmd_check(Namespace(id=card["id"], demote=False))
    assert rc == 0
