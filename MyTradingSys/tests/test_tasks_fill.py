"""Tests for tasks.py fill subcommand promoting raw cards via CLI flags."""
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
import tasks


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(tasks, "REPO", tmp_path)
    (tmp_path / "MyTradingSys" / "system" / "tasks").mkdir(parents=True, exist_ok=True)
    (tmp_path / "scripts" / "dev").mkdir(parents=True, exist_ok=True)
    (tmp_path / "scripts" / "dev" / "tasks.py").write_text("# code\n", encoding="utf-8")
    return tmp_path


def test_fill_raw_card_with_all_flags_promotes_to_ready(repo, capsys):
    # Create raw card
    card = tasks.blank("raw-card-1", "A Raw Card", lane="SONNET")
    tasks.save(repo, card)
    assert tasks.get(repo, "raw-card-1")["state"] == "raw"

    # Fill card via CLI main()
    argv = [
        "fill", "raw-card-1",
        "--size", "S",
        "--worker", "agent",
        "--est-turns", "10",
        "--goal", "Implement feature X cleanly",
        "--done-when", "Feature X passes tests",
        "--tests", "scripts/dev/tasks.py",
        "--scope-in", "scripts/dev/tasks.py",
        "--step", "First step",
        "--step", "Second step",
    ]
    rc = tasks.main(argv)
    assert rc == 0

    c = tasks.get(repo, "raw-card-1")
    assert c["state"] == "ready"
    assert c["size"] == "S"
    assert c["worker"] == "agent"
    assert c["est_turns"] == 10
    assert c["goal"] == "Implement feature X cleanly"
    assert c["done_when"] == "Feature X passes tests"
    assert c["scope_in"] == ["scripts/dev/tasks.py"]
    assert c["steps"] == ["First step", "Second step"]

    out = capsys.readouterr().out
    assert "READY (promoted)" in out


def test_fill_with_missing_fields_fails_and_prints_not_ready(repo, capsys):
    card = tasks.blank("raw-card-2", "Another Raw Card", lane="SONNET")
    tasks.save(repo, card)

    argv = ["fill", "raw-card-2", "--size", "S", "--goal", "Only goal set"]
    rc = tasks.main(argv)
    assert rc == 1

    c = tasks.get(repo, "raw-card-2")
    assert c["state"] == "raw"
    assert c["goal"] == "Only goal set"

    out = capsys.readouterr().out
    assert "NOT READY" in out or "raw:" in out


def test_fill_with_bad_worker_fails(repo, capsys):
    card = tasks.blank("raw-card-3", "Third Raw Card", lane="SONNET")
    tasks.save(repo, card)

    # In worker_problems: agent only for size S and est_turns <= 15
    # If est_turns=30 with agent, it fails
    argv = [
        "fill", "raw-card-3",
        "--size", "S",
        "--worker", "agent",
        "--est-turns", "30",
        "--goal", "Feature",
        "--done-when", "Done",
        "--tests", "scripts/dev/tasks.py",
        "--scope-in", "scripts/dev/tasks.py",
        "--step", "Step",
    ]
    rc = tasks.main(argv)
    assert rc == 1
    c = tasks.get(repo, "raw-card-3")
    assert c["state"] == "raw"


def test_fill_repeatable_list_flags(repo):
    card = tasks.blank("raw-card-4", "Fourth Raw Card", lane="SONNET")
    tasks.save(repo, card)

    argv = [
        "fill", "raw-card-4",
        "--size", "S",
        "--worker", "agent",
        "--est-turns", "10",
        "--goal", "Feature",
        "--done-when", "Done",
        "--tests", "scripts/dev/tasks.py",
        "--scope-in", "scripts/dev/tasks.py",
        "--scope-out", "other.py",
        "--step", "Step 1",
        "--step", "Step 2",
        "--command", "echo test",
        "--source", "spec.md:10",
        "--ref", "B100",
    ]
    rc = tasks.main(argv)
    assert rc == 0
    c = tasks.get(repo, "raw-card-4")
    assert c["scope_out"] == ["other.py"]
    assert c["commands"] == ["echo test"]
    assert c["sources"] == ["spec.md:10"]
    assert c["refs"] == ["B100"]
