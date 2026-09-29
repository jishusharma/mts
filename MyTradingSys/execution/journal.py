"""
MyTradingSys/execution/journal.py

Part of Step 5 (T050 roadmap). Append-only log of every intent, order,
and fill. Never rewrites history - only appends. This is the audit trail
an operator uses to reconstruct any moment; it is deliberately dumb
(flat JSONL file, one JSON object per line) rather than a database,
matching the rest of execution/'s stdlib-only convention.

Untested: no live orders have been placed yet (no testnet key exists).
The write path itself (append_event) is trivial and low-risk; what is
UNVERIFIED is whether the event shapes logged here are actually what
executor.py and reconciler.py need at 2am when something has gone wrong.
That only gets proven by a real testnet run.
Intent events carry env; assert_env is the refusal check.
"""
import sys
sys.dont_write_bytecode = True

import json
import time
from pathlib import Path

VALID_ENVS = ("test", "mainnet")


class EnvMismatch(Exception):
    pass


JOURNAL_DIR = Path(__file__).resolve().parent / "journal"


def _journal_path(plan_id: str) -> Path:
    JOURNAL_DIR.mkdir(exist_ok=True)
    return JOURNAL_DIR / f"{plan_id}.jsonl"


def append_event(plan_id: str, event_type: str, data: dict):
    """event_type: one of 'intent', 'order_placed', 'order_filled',
    'order_cancelled', 'order_rejected', 'stop_resized', 'reconciliation',
    'mismatch_halt', 'error'. Never raises on write failure to a
    non-critical path would be wrong here - if the journal can't be
    written, the operator needs to know immediately, not silently lose
    the audit trail."""
    if event_type == "intent" and data.get("env") not in VALID_ENVS:
        raise ValueError(f"intent event needs env in {VALID_ENVS}, got {data.get('env')!r}")
    record = {
        "ts": time.time(),
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "plan_id": plan_id,
        "event_type": event_type,
        "data": data,
    }
    path = _journal_path(plan_id)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def read_events(plan_id: str) -> list:
    path = _journal_path(plan_id)
    if not path.exists():
        return []
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def plan_env(plan_id: str) -> str | None:
    """Returns the environment ('test' or 'mainnet') a plan was journaled in,
    or None if no intent event exists for this plan."""
    events = read_events(plan_id)
    for ev in events:
        if ev.get("event_type") == "intent":
            return (ev.get("data") or {}).get("env", "test")
    return None


def assert_env(plan_id: str, active_env: str) -> None:
    """Raises EnvMismatch if the plan was journaled in a different environment
    than the one currently active."""
    pe = plan_env(plan_id)
    if pe is not None and pe != active_env:
        raise EnvMismatch(f"plan {plan_id} was journaled on {pe!r} but the active environment is {active_env!r} - refusing")


def reconstruct_belief(plan_id: str) -> dict:
    """Replays the journal to derive MTS's current belief about this
    plan's state (cumulative fills, current stop price, halted status).
    This is what reconciler.py compares against Deribit's actual state -
    the whole point of Step 5 is that this belief must never be trusted
    blindly; it exists to be checked, not to be acted on directly."""
    events = read_events(plan_id)
    belief = {
        "plan_id": plan_id,
        "orders": {},       # order_id -> {label, side, amount, filled_amount, state}
        "current_stop_price": None,
        "halted": False,
        "halt_reason": None,
    }
    for ev in events:
        etype = ev["event_type"]
        d = ev["data"]
        if etype == "order_placed":
            belief["orders"][d["order_id"]] = {
                "label": d["label"], "side": d["side"], "amount": d["amount"],
                "filled_amount": 0, "state": "open",
            }
        elif etype == "order_filled":
            oid = d["order_id"]
            if oid in belief["orders"]:
                belief["orders"][oid]["filled_amount"] = d["filled_amount"]
                belief["orders"][oid]["state"] = d.get("order_state", "open")
        elif etype == "order_cancelled":
            oid = d["order_id"]
            if oid in belief["orders"]:
                belief["orders"][oid]["state"] = "cancelled"
        elif etype == "order_rejected":
            oid = d.get("order_id")
            if oid in belief["orders"]:
                belief["orders"][oid]["state"] = "rejected"
        elif etype == "stop_resized":
            belief["current_stop_price"] = d["new_stop_price"]
        elif etype == "mismatch_halt":
            belief["halted"] = True
            belief["halt_reason"] = d.get("reason")
    return belief
