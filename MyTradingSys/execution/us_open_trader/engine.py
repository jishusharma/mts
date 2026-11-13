"""engine.py - pure rules for the us_open_trader (no I/O, no clock). One source of rules for replay AND live.

State is a plain JSON-serialisable dict. Every rule is OURS unless a comment says SOURCED.
Interpretations of the DESIGN where it is silent (all conservative):
  - after any exit inside a bar there is no new entry in that same bar;
  - the entry bar never moves the stop to break-even (like the target, it is not counted there);
  - an exit at stop / target is at that price (no gap slippage); time exit is at the flat bar's open.
v2 (V2_CHANGES.md, binding over v1 where they differ):
  - V2-1 live=True: step() never exits on stop (emits stop_hint); the only stop exit is force_exit();
  - V2-2 live entry is two steps: step() emits `enter` (order `entering`) -> fill() / reject();
  - V2-3 an order with arm_after is armed from the bar AFTER that order closed/cancelled/void, and only if that
    bar's open is on the approach side of its trigger; otherwise it is void;
  - trade rows carry `mode` (replay | paper | testnet).
Interpretations where the spec is silent (conservative): a live bar that touches stop AND target is a stop_hint only
(stop wins the tie, as in replay); a flat-time bar leaves an `entering` order untouched (the runner settles it with
fill()/reject()); reject() gives back the entry count.
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


def new_state(plan, live=False, mode=None):
    """Fresh state from a plan dict. Raises ValueError on a malformed plan.

    live=True: the exchange owns stops/fills (V2-1, V2-2). mode labels trade rows: replay (live=False) or paper
    (live=True) by default; the runner passes "testnet" for real testnet runs. Unknown plan keys are ignored.
    """
    if mode is None:
        mode = "paper" if live else "replay"
    if mode not in ("replay", "paper", "testnet"):
        raise ValueError("bad mode %r" % (mode,))
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
        "live": bool(live),
        "mode": mode,
        "entering": None,   # live: {"order_id","t"} between step()'s enter and fill()/reject()
        "released": {},     # order id -> t it became closed/cancelled/void (V2-3)
        "gated": [],        # ids of arm_after orders whose approach-side check is done (V2-3)
        "started": False,   # first armed bar seen (void check done)
        "done": False,
        "entries": 0,
        "status": {o["id"]: "pending" for o in orders},  # pending|entering|open|closed|cancelled|void
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
    if a is None:
        return True
    return state["status"][a] in CLOSED_LIKE and o["id"] in state["gated"]  # V2-3: only after the gate check


def _goes_up(o):
    # buy breakout and sell fade both trigger when price rises to the trigger
    return (o["side"] == "buy") == (o["kind"] == BREAKOUT)


def _touched(o, bar):
    return bar["h"] >= o["trigger"] if _goes_up(o) else bar["l"] <= o["trigger"]


def _crossed_at_open(o, bar):
    return bar["o"] >= o["trigger"] if _goes_up(o) else bar["o"] <= o["trigger"]


def _set(state, oid, status, t):
    """Set an order status; closed/cancelled/void also records the release time for arm_after (V2-3)."""
    state["status"][oid] = status
    if status in CLOSED_LIKE:
        state["released"][oid] = t


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
        "mode": state["mode"],
    })
    events.append(_ev(t, "exit", o["id"], price, reason))
    _set(state, o["id"], "closed", t)
    state["position"] = None
    # Survival rules
    if reason == "target" and o["kind"] == BREAKOUT:
        for x in plan["orders"]:
            if x["kind"] == BREAKOUT and state["status"][x["id"]] == "pending":
                _set(state, x["id"], "cancelled", t)
                events.append(_ev(t, "cancel", x["id"], None, "breakout_target_hit"))
    if state["entries"] >= plan["max_entries"]:
        for x in plan["orders"]:
            if state["status"][x["id"]] == "pending":
                _set(state, x["id"], "cancelled", t)
                events.append(_ev(t, "cancel", x["id"], None, "max_entries"))


def _open_position(state, o, t, entry):
    sign = 1 if o["side"] == "buy" else -1
    state["position"] = {
        "order_id": o["id"], "side": o["side"], "entry": entry, "entry_t": t,
        "stop": entry - sign * o["stop_dist"], "target": entry + sign * o["target_dist"],
        "moved": False,
    }
    _set(state, o["id"], "open", t)


def _enter(state, o, t):
    state["entries"] += 1
    if state["live"]:  # V2-2: wait for the runner's fill()
        _set(state, o["id"], "entering", t)
        state["entering"] = {"order_id": o["id"], "t": t}
    else:
        _open_position(state, o, t, o["trigger"])
    return _ev(t, "enter", o["id"], o["trigger"], o["kind"])


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
                _set(state, x["id"], "cancelled", t)
                events.append(_ev(t, "cancel", x["id"], None, "flat_time"))
        state["done"] = True
        return state, events

    if not state["started"]:
        state["started"] = True
        for o in plan["orders"]:
            if _crossed_at_open(o, bar):
                _set(state, o["id"], "void", t)
                events.append(_ev(t, "void", o["id"], o["trigger"], "crossed_at_arm"))

    # V2-3: first bar after the arm_after order was released: arm only if the bar opens on the approach side
    for o in plan["orders"]:
        a = o.get("arm_after")
        if (a is not None and state["status"][o["id"]] == "pending" and o["id"] not in state["gated"]
                and a in state["released"] and t > state["released"][a]):
            state["gated"].append(o["id"])
            if _crossed_at_open(o, bar):
                _set(state, o["id"], "void", t)
                events.append(_ev(t, "void", o["id"], o["trigger"], "not_on_approach_side"))

    pos = state["position"]
    if pos is not None:
        sign = 1 if pos["side"] == "buy" else -1
        stop_hit = bar["l"] <= pos["stop"] if sign == 1 else bar["h"] >= pos["stop"]
        tgt_hit = bar["h"] >= pos["target"] if sign == 1 else bar["l"] <= pos["target"]
        if stop_hit and state["live"]:  # V2-1: the exchange owns the stop; hint only, no state change
            o = _order(state, pos["order_id"])
            events.append(_ev(t, "stop_hint", o["id"], pos["stop"], "be_stop" if pos["moved"] else "stop"))
        elif stop_hit:  # stop wins a same-bar tie
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

    if state["entering"] is not None or state["entries"] >= plan["max_entries"]:
        return state, events
    cands = [o for o in plan["orders"] if _armed(state, o) and _touched(o, bar)]
    if cands:
        o = min(cands, key=lambda c: abs(c["trigger"] - bar["o"]))  # ties: plan order (min is stable)
        events.append(_enter(state, o, t))
        pos = state["position"]
        if pos is None:  # live: waiting for fill()
            return state, events
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


def fill(state, order_id, t, price):
    """Live (V2-2): the entry order filled at `price` (ref-feed terms: fill - basis). Entry, stop, target and
    break-even level are rebased on the fill. Raises ValueError unless that order is `entering`."""
    ent = state["entering"]
    if ent is None or ent["order_id"] != order_id:
        raise ValueError("order %s is not entering" % (order_id,))
    o = _order(state, order_id)
    _open_position(state, o, t, price)
    state["entering"] = None
    return state, [_ev(t, "fill", order_id, price, "fill")]


def reject(state, order_id, t, reason):
    """Live (V2-2): refusal / failure / slippage guard. The order is cancelled and its entry count given back."""
    ent = state["entering"]
    if ent is None or ent["order_id"] != order_id:
        raise ValueError("order %s is not entering" % (order_id,))
    _set(state, order_id, "cancelled", t)
    state["entering"] = None
    state["entries"] -= 1
    return state, [_ev(t, "cancel", order_id, None, reason)]


def replay(plan, bars):
    state = new_state(plan)
    events = []
    for b in sorted(bars, key=lambda b: b["t"]):
        state, ev = step(state, b)
        events.extend(ev)
    return {"trades": state["trades"], "events": events, "state": state}
