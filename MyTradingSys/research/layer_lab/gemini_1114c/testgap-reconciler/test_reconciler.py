"""Unit tests for MyTradingSys/execution/reconciler.py.

Existing coverage note (Step 1):
  git grep -l reconciler -- scripts MyTradingSys found:
  - MyTradingSys/execution/test_reconciler_env.py (tests --mainnet & EnvMismatch only)
  - MyTradingSys/execution/testnet/offline/test_g1g2_offline.py (integration script)
  - MyTradingSys/execution/testnet/run_testnet_suite_g1g2.py (testnet suite)
  No test file named test_reconciler.py existed.

Mutation test record (Step 4):
  Mutated scratch copy of MyTradingSys/execution/reconciler.py:105:
    Original: if covered < abs(actual_position):
    Mutated:  if covered > abs(actual_position):
  Resulting failure when pointed at the mutated scratch copy:
    test_reconcile_unprotected_position_raises_and_halts failed with:
      Failed: DID NOT RAISE ReconciliationMismatch (1 failed, 4 passed)
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[5]
EXEC = REPO / "MyTradingSys" / "execution"
if str(EXEC) not in sys.path:
    sys.path.insert(0, str(EXEC))

import reconciler  # noqa: E402


def _patch_env(monkeypatch, tmp_path, *, belief, order_states, position, open_orders):
    """Patch reconciler.journal and reconciler.do for offline, zero-network tests."""
    events = []
    monkeypatch.setattr(reconciler.journal, "JOURNAL_DIR", tmp_path)
    monkeypatch.setattr(reconciler.journal, "assert_env", lambda plan_id, env: None)
    monkeypatch.setattr(reconciler.journal, "reconstruct_belief", lambda plan_id: belief)
    monkeypatch.setattr(
        reconciler.journal,
        "append_event",
        lambda plan_id, etype, data: events.append((plan_id, etype, data)),
    )
    monkeypatch.setattr(reconciler.do, "active_env", lambda: "test")
    monkeypatch.setattr(reconciler.do, "authenticate", lambda: "tok_test")
    monkeypatch.setattr(reconciler.do, "get_order_state", lambda tok, oid: order_states[oid])
    monkeypatch.setattr(reconciler.do, "get_position", lambda tok, inst="BTC-PERPETUAL": position)
    monkeypatch.setattr(reconciler.do, "get_open_orders", lambda tok, inst="BTC-PERPETUAL": open_orders)
    return events


def test_norm_normal_and_empty():
    # SOURCED: LIVE = {"open", "untriggered"} (MyTradingSys/execution/reconciler.py:34)
    # SOURCED: return "open" if state in LIVE else state (MyTradingSys/execution/reconciler.py:42)
    # OURS: "open" and "untriggered" normalize to "open"; other/empty/None pass through unchanged.
    assert reconciler._norm("open") == "open"
    assert reconciler._norm("untriggered") == "open"
    assert reconciler._norm("filled") == "filled"
    assert reconciler._norm("") == ""
    assert reconciler._norm(None) is None


def test_reconcile_normal_clean(monkeypatch, tmp_path):
    # SOURCED: believed_position += f if b["side"] == "BUY" else -f (MyTradingSys/execution/reconciler.py:77)
    # SOURCED: covered = sum(int(o.get("amount") or 0) for o in live_stops) (MyTradingSys/execution/reconciler.py:104)
    # SOURCED: return {"status": "reconciled_ok", "believed_position": believed_position, "actual_position": actual_position} (MyTradingSys/execution/reconciler.py:116)
    # OURS: BUY entry filled=100 (+100) and SELL stop filled=0 (-0) -> believed_position=100;
    #       actual_position=100; live stop amount=100 >= abs(100)=100 -> reconciled_ok.
    plan_id = "p_norm"
    belief = {
        "plan_id": plan_id,
        "orders": {
            "o_entry": {"label": "entry_1", "side": "BUY", "amount": 100, "filled_amount": 100, "state": "filled"},
            "o_stop": {"label": "stop_1", "side": "SELL", "amount": 100, "filled_amount": 0, "state": "untriggered"},
        },
        "current_stop_price": 78000,
        "halted": False,
        "halt_reason": None,
    }
    order_states = {
        "o_entry": {"order_id": "o_entry", "filled_amount": 100, "order_state": "filled"},
        "o_stop": {"order_id": "o_stop", "filled_amount": 0, "order_state": "untriggered"},
    }
    open_orders = [
        {
            "order_id": "o_stop",
            "label": f"{plan_id}:stop_1",
            "reduce_only": True,
            "order_state": "untriggered",
            "amount": 100,
        }
    ]
    events = _patch_env(
        monkeypatch,
        tmp_path,
        belief=belief,
        order_states=order_states,
        position={"size": 100},
        open_orders=open_orders,
    )
    res = reconciler.reconcile(plan_id)
    assert res == {"status": "reconciled_ok", "believed_position": 100, "actual_position": 100}
    assert [e[1] for e in events] == ["reconciliation"]


def test_reconcile_empty_journal_flat(monkeypatch, tmp_path):
    # SOURCED: believed_position = 0 (MyTradingSys/execution/reconciler.py:72)
    # SOURCED: actual_position = int(do.get_position(token, instrument).get("size") or 0) (MyTradingSys/execution/reconciler.py:80)
    # OURS: empty orders dict -> believed_position=0; position size=0 -> actual_position=0 -> reconciled_ok.
    plan_id = "p_empty"
    belief = {
        "plan_id": plan_id,
        "orders": {},
        "current_stop_price": None,
        "halted": False,
        "halt_reason": None,
    }
    events = _patch_env(
        monkeypatch,
        tmp_path,
        belief=belief,
        order_states={},
        position={"size": 0},
        open_orders=[],
    )
    res = reconciler.reconcile(plan_id)
    assert res == {"status": "reconciled_ok", "believed_position": 0, "actual_position": 0}
    assert len(events) == 1 and events[0][1] == "reconciliation"


def test_reconcile_malformed_position_size_raises(monkeypatch, tmp_path):
    # SOURCED: actual_position = int(do.get_position(token, instrument).get("size") or 0) (MyTradingSys/execution/reconciler.py:80)
    # OURS: non-numeric string "not_a_number" in position["size"] fails int() conversion with ValueError.
    plan_id = "p_malformed"
    belief = {
        "plan_id": plan_id,
        "orders": {},
        "current_stop_price": None,
        "halted": False,
        "halt_reason": None,
    }
    _patch_env(
        monkeypatch,
        tmp_path,
        belief=belief,
        order_states={},
        position={"size": "not_a_number"},
        open_orders=[],
    )
    with pytest.raises(ValueError):
        reconciler.reconcile(plan_id)


def test_reconcile_unprotected_position_raises_and_halts(monkeypatch, tmp_path):
    # SOURCED: if covered < abs(actual_position): (MyTradingSys/execution/reconciler.py:105)
    # SOURCED: mismatches.append({"type": "unprotected_position", "position": actual_position, "live_stop_amount": covered}) (MyTradingSys/execution/reconciler.py:106-107)
    # SOURCED: raise ReconciliationMismatch(f"plan {plan_id}: {len(mismatches)} mismatch(es): {mismatches}") (MyTradingSys/execution/reconciler.py:115)
    # OURS: believed_position=100, actual_position=100, live stop amount=40 < 100 -> 1 mismatch ("unprotected_position") -> raises ReconciliationMismatch.
    plan_id = "p_unprot"
    belief = {
        "plan_id": plan_id,
        "orders": {
            "o_entry": {"label": "entry_1", "side": "BUY", "amount": 100, "filled_amount": 100, "state": "filled"},
            "o_stop": {"label": "stop_1", "side": "SELL", "amount": 40, "filled_amount": 0, "state": "untriggered"},
        },
        "current_stop_price": 78000,
        "halted": False,
        "halt_reason": None,
    }
    order_states = {
        "o_entry": {"order_id": "o_entry", "filled_amount": 100, "order_state": "filled"},
        "o_stop": {"order_id": "o_stop", "filled_amount": 0, "order_state": "untriggered"},
    }
    open_orders = [
        {
            "order_id": "o_stop",
            "label": f"{plan_id}:stop_1",
            "reduce_only": True,
            "order_state": "untriggered",
            "amount": 40,
        }
    ]
    events = _patch_env(
        monkeypatch,
        tmp_path,
        belief=belief,
        order_states=order_states,
        position={"size": 100},
        open_orders=open_orders,
    )
    with pytest.raises(reconciler.ReconciliationMismatch, match="unprotected_position"):
        reconciler.reconcile(plan_id)
    assert [e[1] for e in events] == ["reconciliation", "mismatch_halt"]
