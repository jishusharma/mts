"""RU6: Content-bound review receipts in tasks.py (hash bound, void on change, no self-review)."""
from argparse import Namespace
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
import tasks


def make_card(cid="card-c2-review", **kw):
    c = {
        "id": cid,
        "title": "Review Receipt Test Card",
        "state": "ready",
        "lane": "SONNET",
        "prio": 3,
        "size": "S",
        "est_turns": 10,
        "worker": "agent",
        "weight": "CRUCIAL",
        "goal": "Test goal for review receipt",
        "done_when": "Test passes",
        "steps": ["Step 1: implement", "Step 2: verify"],
        "scope_in": ["src/my_code.py", "docs/my_spec.md", "data/my_data.csv"],
        "tests": "MyTradingSys/tests/test_review_receipts.py",
        "created": "2026-10-18T10:00:00Z",
        "depends_on": [],
        "note": "",
        "live_path": False,
        "producer": "alice",
    }
    c.update(kw)
    return c


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(tasks, "REPO", tmp_path)
    (tmp_path / "MyTradingSys" / "system" / "tasks").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "data").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / "my_code.py").write_text("def solve(): return 42\n", encoding="utf-8")
    (tmp_path / "docs" / "my_spec.md").write_text("# Spec\nReturn 42\n", encoding="utf-8")
    (tmp_path / "data" / "my_data.csv").write_text("id,val\n1,42\n", encoding="utf-8")
    return tmp_path


def test_make_review_receipt_records_hashes(repo):
    card = make_card()
    receipt = tasks.make_review_receipt(card, reviewer="bob", repo=repo)
    assert receipt["reviewer"] == "bob"
    assert "card_hash" in receipt
    assert "scope_hash" in receipt
    assert "code_hash" in receipt
    assert "spec_hash" in receipt
    assert "data_hash" in receipt


def test_unchanged_card_keeps_review_stamp(repo):
    card = make_card()
    receipt = tasks.make_review_receipt(card, reviewer="bob", repo=repo)
    card["review_receipt"] = receipt
    card["note"] = f"REVIEWED: bob 2026-10-18 scope={receipt['scope_hash']}"
    tasks.save(repo, card)
    assert tasks.stamp_kind(card, repo=repo) == "real"
    assert tasks.review_gate(card, repo=repo) == []


def test_changing_code_scope_voids_stamp(repo):
    card = make_card()
    receipt = tasks.make_review_receipt(card, reviewer="bob", repo=repo)
    card["review_receipt"] = receipt
    card["note"] = f"REVIEWED: bob 2026-10-18 scope={receipt['scope_hash']}"
    tasks.save(repo, card)
    assert tasks.stamp_kind(card, repo=repo) == "real"

    # Modify code file in scope
    (repo / "src" / "my_code.py").write_text("def solve(): return 999\n", encoding="utf-8")
    assert tasks.stamp_kind(card, repo=repo) == ""
    assert any("review" in p.lower() for p in tasks.review_gate(card, repo=repo))


def test_changing_spec_scope_voids_stamp(repo):
    card = make_card()
    receipt = tasks.make_review_receipt(card, reviewer="bob", repo=repo)
    card["review_receipt"] = receipt
    tasks.save(repo, card)
    assert tasks.stamp_kind(card, repo=repo) == "real"

    # Modify spec file in scope
    (repo / "docs" / "my_spec.md").write_text("# Spec\nChanged spec\n", encoding="utf-8")
    assert tasks.stamp_kind(card, repo=repo) == ""


def test_changing_data_scope_voids_stamp(repo):
    card = make_card()
    receipt = tasks.make_review_receipt(card, reviewer="bob", repo=repo)
    card["review_receipt"] = receipt
    tasks.save(repo, card)
    assert tasks.stamp_kind(card, repo=repo) == "real"

    # Modify data file in scope
    (repo / "data" / "my_data.csv").write_text("id,val\n1,999\n", encoding="utf-8")
    assert tasks.stamp_kind(card, repo=repo) == ""


def test_changing_card_contract_voids_stamp(repo):
    card = make_card()
    receipt = tasks.make_review_receipt(card, reviewer="bob", repo=repo)
    card["review_receipt"] = receipt
    tasks.save(repo, card)
    assert tasks.stamp_kind(card, repo=repo) == "real"

    # Modify card goal
    card["goal"] = "Completely altered goal"
    assert tasks.stamp_kind(card, repo=repo) == ""


def test_producer_cannot_self_review(repo):
    card = make_card(producer="alice")
    # Reviewer matches producer
    receipt = tasks.make_review_receipt(card, reviewer="alice", repo=repo)
    card["review_receipt"] = receipt
    card["note"] = f"REVIEWED: alice 2026-10-18 scope={receipt['scope_hash']}"
    tasks.save(repo, card)

    assert tasks.stamp_kind(card, repo=repo) == ""
    probs = tasks.problems(card, repo=repo)
    assert any("self-review" in p.lower() or "producer" in p.lower() for p in probs)


def test_cmd_take_rejects_voided_stamp(repo):
    card = make_card()
    receipt = tasks.make_review_receipt(card, reviewer="bob", repo=repo)
    card["review_receipt"] = receipt
    tasks.save(repo, card)

    # Change code to void stamp
    (repo / "src" / "my_code.py").write_text("def solve(): return 0\n", encoding="utf-8")
    tasks.save(repo, card)

    with pytest.raises(SystemExit):
        tasks.cmd_take(Namespace(id=card["id"], claim="worker1"))


def test_cmd_take_rejects_producer_self_review(repo):
    card = make_card(producer="alice")
    receipt = tasks.make_review_receipt(card, reviewer="alice", repo=repo)
    card["review_receipt"] = receipt
    card["note"] = f"REVIEWED: alice 2026-10-18"
    tasks.save(repo, card)

    with pytest.raises(SystemExit):
        tasks.cmd_take(Namespace(id=card["id"], claim="worker1"))


def test_note_embedded_hashes_void_on_scope_change(repo):
    card = make_card()
    hashes = tasks.review_hashes(card, repo=repo)
    card["note"] = f"REVIEWED: bob 2026-10-18 scope={hashes['scope']} card={hashes['card']}"
    tasks.save(repo, card)
    assert tasks.stamp_kind(card, repo=repo) == "real"

    # Modify code
    (repo / "src" / "my_code.py").write_text("def solve(): return 123\n", encoding="utf-8")
    assert tasks.stamp_kind(card, repo=repo) == ""
