import json
import pytest
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
SCRIPTS_DEV = REPO / "scripts" / "dev"
if str(SCRIPTS_DEV) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DEV))

import supervisor
import tasks
import role_loader


def test_supervisor_brief_format_and_security(tmp_path):
    """Verify supervisor.py brief <card> contains 'You are Builder.', the card ID, and no secrets path."""
    card = {
        "id": "fixture-card-1",
        "title": "Fixture Card for Testing",
        "lane": "SONNET",
        "goal": "Test goal for fixture",
        "scope_in": ["scripts/dev/supervisor.py"],
        "scope_out": [".secrets/", ".env"],
        "steps": ["Step 1: do something"],
        "tests": "test_something",
        "done_when": "done when passing",
    }
    card_path = tmp_path / "fixture-card-1.json"
    card_path.write_text(json.dumps(card), encoding="utf-8")

    out = supervisor.brief("fixture-card-1", repo=tmp_path, card=card)
    lines = out.strip().splitlines()

    # Line 1: You are <Role>. (defaults to Builder)
    assert lines[0] == "You are Builder."
    # Line 2: Card: <card_id>[, <chained_ids>...]. Boot: python <main_checkout>/scripts/dev/sync.py start <slug>; work only in the printed WORKTREE.
    assert lines[1].startswith("Card: fixture-card-1. Boot: python ")
    assert "scripts/dev/sync.py start fixture-card-1; work only in the printed WORKTREE." in lines[1]
    
    # Must contain card id
    assert "fixture-card-1" in out
    # Must contain stop lines
    assert "Run with zero operator input: never ask; take the conservative default, log DECISION (OURS), continue" in out
    assert "Your final report starts with your ROLE LOADED banner line, then Result: and the content sha, at most 6 lines." in out

    # Must not contain paths to secret files or leak secret tokens
    assert ".secrets" not in out
    assert ".env" not in out


def test_supervisor_brief_explicit_role(tmp_path):
    """Verify supervisor.py brief supports --role override."""
    card = {
        "id": "doc-audit-card",
        "title": "Audit Card",
        "lane": "SONNET",
        "goal": "Audit something",
        "scope_in": ["MyTradingSys/system/ROLES.md"],
    }
    out = supervisor.brief("doc-audit-card", role="MTS_Doctor", repo=tmp_path, card=card)
    lines = out.strip().splitlines()
    assert lines[0] == "You are MTS_Doctor."
    assert "Card: doc-audit-card." in lines[1]


def test_tasks_dispatch_role_field():
    """Verify tasks.py dispatch output includes role field for dispatched cards."""
    # Test card mapping
    cards = [
        {"id": "c-build", "state": "ready", "lane": "SONNET", "kind": "build", "title": "Build card", "scope_in": ["scripts/test.py"]},
        {"id": "c-codex", "state": "ready", "lane": "CODEX", "kind": "run", "title": "Codex card", "scope_in": ["research/lab/"]},
        {"id": "c-audit", "state": "ready", "lane": "SONNET", "kind": "audit", "title": "Audit card", "scope_in": ["scripts/audit.py"]},
        {"id": "c-net", "state": "ready", "lane": "SONNET", "title": "Network: nowin fix", "scope_in": ["scripts/dev/nowin.py"]},
        {"id": "c-explicit", "state": "ready", "lane": "SONNET", "role": "Custom_Role", "title": "Explicit role", "scope_in": ["scripts/foo.py"]},
    ]
    # Check card_role helper directly and dispatch output
    assert tasks.card_role(cards[0]) == "Builder"
    assert tasks.card_role(cards[1]) == "Lab_Guy"
    assert tasks.card_role(cards[2]) == "MTS_Doctor"
    assert tasks.card_role(cards[3]) == "Network_Admin_Guy"
    assert tasks.card_role(cards[4]) == "Custom_Role"


def test_role_loader_check_with_builder():
    """Verify role_loader.py check passes with Builder."""
    assert "Builder" in role_loader.KNOWN_ROLES
    rc = role_loader.check()
    assert rc == 0
