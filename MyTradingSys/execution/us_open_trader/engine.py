"""engine.py - pure rules for the us_open_trader (no I/O, no clock). One source of rules for replay AND live.

State is a plain JSON-serialisable dict. Every rule is OURS unless a comment says SOURCED.
Interpretations of the DESIGN where it is silent (all conservative):
  - after any exit inside a bar there is no new entry in that same bar;
  - the entry bar never moves the stop to break-even (like the target, it is not counted there);
  - an exit at stop / target is at that price (no gap slippage); time exit is at the flat bar's open.
"""
import json
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True

BREAKOUT = "breakout"
FADE = "fade"
CLOSED_LIKE = ("closed", "cancelled", "void")  # OURS: states that release a fade's arm_after


def _ms(day, hhmm):
    h, m = hhmm.split(":")
    d = datetime.strptime(day, "%Y-%m-%d").replace(hour=int(h), minute=int(m), tzinfo=timezone.utc)
    return int(d.timestamp() * 1000)


def new_state(plan):
    """Fresh state from a plan dict. Raises ValueError on a malformed plan."""
    orders = plan["orders"]
    ids = [o["id"] for o in orders]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate order ids")
    for o in orders:
        if o["side"] not in ("buy", "sell") or o["kind"] not in (BREAKOUT, FADE):
            raise ValueError("bad side/kind for order %s" % o["id"])
        if o["stop_dist"] <= 0 or o["target_dist"] <= 0:
            raise ValueError("stop_dist/target_dist must be > 0 for order %s" % o["id"])
        if o.get("arm_after") is not None and o["arm_after"] not in ids:
            raise ValueError("arm_after of %s names an unknown order" % o["id"])
    arm = _ms(plan["day"], plan["arm_utc"])
    flat = _ms(plan["day"], plan["flat_utc"])
    if flat <= arm:
        raise ValueError("flat_utc must be after arm_utc")
    return {
        "plan": json.loads(json.dumps(plan)),
        "arm_ms": arm,
        "flat_ms": flat,
        "started": False,   # first armed bar seen (void check done)
        "done": False,
        "entries": 0,
        "status": {o["id"]: "pending" for o in orders},  # pending|open|closed|cancelled|void
        "position": None,
        "trades": [],
    }


def _order(state, oid):
    for o in state["plan"]["orders"]:
        if o["id"] == oid:
            return o
    raise KeyError(oid)


def _ev(t, typ, oid, price, reason):
    return {"t": t, "type": typ, "order_id": oid, "price": price, "reason": reason}


def _armed(state, o):
    if state["status"][o["id"]] != "pending":
        return False
    a = o.get("arm_after")
    return a is None or state["status"][a] in CLOSED_LIKE


def _goes_up(o):
    # buy breakout and sell fade both trigger when price rises to the trigger
    return (o["side"] == "buy") == (o["kind"] == BREAKOUT)


def _touched(o, bar):
    return bar["h"] >= o["trigger"] if _goes_up(o) else bar["l"] <= o["trigger"]


def _crossed_at_open(o, bar):
    return bar["o"] >= o["trigger"] if _goes_up(o) else bar["o"] <= o["trigger"]


def _close(state, t, price, reason, events):
    p = state["position"]
    o = _order(state, p["order_id"])
    plan = state["plan"]
    sd = o["stop_dist"]
    sign = 1 if p["side"] == "buy" else -1
    r_gross = sign * (price - p["entry"]) / sd
    r_net = r_gross - 2 * plan["fee_per_side"] * p["entry"] / sd
    state["trades"].append({
        "order_id": o["id"], "side": o["side"], "kind": o["kind"], "level": o.get("level"),
        "confluence": list(o.get("confluence") or []),
        "entry_t": p["entry_t"], "entry": p["entry"], "exit_t": t, "exit": price,
        "exit_reason": reason, "r_gross": r_gross, "r_net": r_net, "stop_moved": p["moved"],
    })
    events.append(_ev(t, "exit", o["id"], price, reason))
    state["status"][o["id"]] = "closed"
    state["position"] = None
    # Survival rules
    if reason == "target" and o["kind"] == BREAKOUT:
        for x in plan["orders"]:
            if x["kind"] == BREAKOUT and state["status"][x["id"]] == "pending":
                state["status"][x["id"]] = "cancelled"
                events.append(_ev(t, "cancel", x["id"], None, "breakout_target_hit"))
    if state["entries"] >= plan["max_entries"]:
        for x in plan["orders"]:
            if state["status"][x["id"]] == "pending":
                state["status"][x["id"]] = "cancelled"
                events.append(_ev(t, "cancel", x["id"], None, "max_entries"))


def _enter(state, o, t):
    sign = 1 if o["side"] == "buy" else -1
    entry = o["trigger"]
    state["position"] = {
        "order_id": o["id"], "side": o["side"], "entry": entry, "entry_t": t,
        "stop": entry - sign * o["stop_dist"], "target": entry + sign * o["target_dist"],
        "moved": False,
    }
    state["status"][o["id"]] = "open"
    state["entries"] += 1
    return _ev(t, "enter", o["id"], entry, o["kind"])


def step(state, bar):
    """Feed one bar. Returns (state, events). State is mutated in place and returned."""
    events = []
    t = bar["t"]
    if state["done"] or t < state["arm_ms"]:
        return state, events
    plan = state["plan"]

    if t >= state["flat_ms"]:
        if state["position"] is not None:
            _close(state, t, bar["o"], "time", events)
        for x in plan["orders"]:
            if state["status"][x["id"]] == "pending":
                state["status"][x["id"]] = "cancelled"
                events.append(_ev(t, "cancel", x["id"], None, "flat_time"))
        state["done"] = True
        return state, events

    if not state["started"]:
        state["started"] = True
        for o in plan["orders"]:
            if _crossed_at_open(o, bar):
                state["status"][o["id"]] = "void"
                events.append(_ev(t, "void", o["id"], o["trigger"], "crossed_at_arm"))

    pos = state["position"]
    if pos is not None:
        sign = 1 if pos["side"] == "buy" else -1
        stop_hit = bar["l"] <= pos["stop"] if sign == 1 else bar["h"] >= pos["stop"]
        tgt_hit = bar["h"] >= pos["target"] if sign == 1 else bar["l"] <= pos["target"]
        if stop_hit:  # stop wins a same-bar tie
            _close(state, t, pos["stop"], "be_stop" if pos["moved"] else "stop", events)
        elif tgt_hit:
            _close(state, t, pos["target"], "target", events)
        elif not pos["moved"]:
            o = _order(state, pos["order_id"])
            fav = (bar["h"] - pos["entry"]) if sign == 1 else (pos["entry"] - bar["l"])
            if fav >= plan["be_at_r"] * o["stop_dist"]:
                pos["stop"] = pos["entry"]
                pos["moved"] = True
                events.append(_ev(t, "move_stop", o["id"], pos["entry"], "be"))
        return state, events

    if state["entries"] >= plan["max_entries"]:
        return state, events
    cands = [o for o in plan["orders"] if _armed(state, o) and _touched(o, bar)]
    if cands:
        o = min(cands, key=lambda c: abs(c["trigger"] - bar["o"]))  # ties: plan order (min is stable)
        events.append(_enter(state, o, t))
        pos = state["position"]
        sign = 1 if pos["side"] == "buy" else -1
        adverse = bar["l"] <= pos["stop"] if sign == 1 else bar["h"] >= pos["stop"]
        if adverse:  # target not counted on the entry bar
            _close(state, t, pos["stop"], "stop", events)
    return state, events


def force_exit(state, t, price, reason):
    """External exit (live): e.g. server-side stop fill. No-op without an open position."""
    events = []
    if state["position"] is not None:
        _close(state, t, price, reason, events)
    return state, events


def replay(plan, bars):
    state = new_state(plan)
    events = []
    for b in sorted(bars, key=lambda b: b["t"]):
        state, ev = step(state, b)
        events.extend(ev)
    return {"trades": state["trades"], "events": events, "state": state}
