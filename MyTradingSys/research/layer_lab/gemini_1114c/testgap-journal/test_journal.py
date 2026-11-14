"""Hand-computed unit tests for MyTradingSys/execution/journal.py.

Existing coverage check:
- MyTradingSys/execution/test_journal_env.py covers append_event (intent env
  validation), plan_env, and assert_env, but does not test reconstruct_belief
  or malformed JSONL handling in read_events.

Mutation verification (broken scratch copy of MyTradingSys/execution/journal.py):
- Mutated line 127: `belief["current_stop_price"] = d["new_stop_price"]` ->
  `belief["current_stop_price"] = None`.
- Rerunning pytest failed `test_reconstruct_belief_normal_lifecycle`
  (1 failed, 4 passed: `{'current_stop_price': None} != {'current_stop_price': 94500.0}`).
"""
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[5]
_EXEC_DIR = _REPO_ROOT / "MyTradingSys" / "execution"
if str(_EXEC_DIR) not in sys.path:
    sys.path.insert(0, str(_EXEC_DIR))

import journal  # noqa: E402


def test_reconstruct_belief_empty_plan(tmp_path, monkeypatch):
    """Empty/nonexistent plan returns empty belief and None plan_env."""
    monkeypatch.setattr(journal, "JOURNAL_DIR", tmp_path)

    assert journal.read_events("empty_plan") == []
    assert journal.plan_env("empty_plan") is None
    assert journal.reconstruct_belief("empty_plan") == {
        "plan_id": "empty_plan",
        "orders": {},
        "current_stop_price": None,
        "halted": False,
        "halt_reason": None,
    }


def test_reconstruct_belief_normal_lifecycle(tmp_path, monkeypatch):
    """Normal lifecycle replays order_placed, order_filled, stop_resized, order_cancelled."""
    monkeypatch.setattr(journal, "JOURNAL_DIR", tmp_path)

    journal.append_event("plan_norm", "intent", {"env": "test"})
    journal.append_event(
        "plan_norm",
        "order_placed",
        {"order_id": "ord_1", "label": "entry", "side": "buy", "amount": 100},
    )
    journal.append_event(
        "plan_norm",
        "order_placed",
        {"order_id": "ord_2", "label": "stop", "side": "sell", "amount": 100},
    )
    journal.append_event(
        "plan_norm",
        "order_filled",
        {"order_id": "ord_1", "filled_amount": 100, "order_state": "filled"},
    )
    journal.append_event("plan_norm", "stop_resized", {"new_stop_price": 94500.0})
    journal.append_event("plan_norm", "order_cancelled", {"order_id": "ord_2"})

    belief = journal.reconstruct_belief("plan_norm")
    assert belief == {
        "plan_id": "plan_norm",
        "orders": {
            "ord_1": {
                "label": "entry",
                "side": "buy",
                "amount": 100,
                "filled_amount": 100,
                "state": "filled",
            },
            "ord_2": {
                "label": "stop",
                "side": "sell",
                "amount": 100,
                "filled_amount": 0,
                "state": "cancelled",
            },
        },
        "current_stop_price": 94500.0,
        "halted": False,
        "halt_reason": None,
    }


def test_reconstruct_belief_rejected_and_mismatch_halt(tmp_path, monkeypatch):
    """order_rejected, unknown order_filled no-op, and mismatch_halt are reflected."""
    monkeypatch.setattr(journal, "JOURNAL_DIR", tmp_path)

    journal.append_event(
        "plan_halt",
        "order_placed",
        {"order_id": "ord_r", "label": "tp", "side": "sell", "amount": 50},
    )
    journal.append_event("plan_halt", "order_rejected", {"order_id": "ord_r"})
    journal.append_event(
        "plan_halt",
        "order_filled",
        {"order_id": "ord_unknown", "filled_amount": 10, "order_state": "filled"},
    )
    journal.append_event(
        "plan_halt",
        "mismatch_halt",
        {"reason": "exchange position 200 != belief 100"},
    )

    belief = journal.reconstruct_belief("plan_halt")
    assert belief == {
        "plan_id": "plan_halt",
        "orders": {
            "ord_r": {
                "label": "tp",
                "side": "sell",
                "amount": 50,
                "filled_amount": 0,
                "state": "rejected",
            }
        },
        "current_stop_price": None,
        "halted": True,
        "halt_reason": "exchange position 200 != belief 100",
    }


def test_read_events_malformed_jsonl_raises(tmp_path, monkeypatch):
    """Malformed JSONL line raises json.JSONDecodeError in read_events and reconstruct_belief."""
    monkeypatch.setattr(journal, "JOURNAL_DIR", tmp_path)
    (tmp_path / "bad_json.jsonl").write_text("{not valid json\n", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        journal.read_events("bad_json")
    with pytest.raises(json.JSONDecodeError):
        journal.reconstruct_belief("bad_json")


def test_reconstruct_belief_malformed_event_missing_data_raises(tmp_path, monkeypatch):
    """Valid JSON missing the 'data' key raises KeyError in reconstruct_belief."""
    monkeypatch.setattr(journal, "JOURNAL_DIR", tmp_path)
    (tmp_path / "bad_shape.jsonl").write_text(
        '{"event_type": "order_placed"}\n', encoding="utf-8"
    )

    with pytest.raises(KeyError):
        journal.reconstruct_belief("bad_shape")
