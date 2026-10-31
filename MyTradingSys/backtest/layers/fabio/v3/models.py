"""Fabio v3 models A / B / C / D (FABIO_V3_SPEC.md section 4) in two layers.

1. Trade functions (the pending-test contract): model_a_trade, model_b, model_c, model_d_trade take an already
   identified set-up (or scan from an injected balance / IB) and simulate ONE first leg through fill.py + manage.py.
   They return {"arms", "fills", "missed_winners", "trades": [trade dicts]}.
2. Set-up scanners (scan_model_a/b/c/d): replay the section-4 state machine over bars[open_idx..i] causally and report
   the state at bar i (IDLE / IMPULSE / PROBE / ARMED / SIGNAL / IN_TRADE). These feed engine.py. They replay SIGNALS
   and the fill rule only; they do not simulate trade management.

Common (spec section 4): D = max(f * entry, structural); no arm if D > Dmax * entry. Entry (grid): "rest" = maker limit
armed before the touch (5.1); "confirm" = taker at the next open as each model says. Models A, C, D have no target and
are managed by 5.2 + S8; model B has the edge target (target_mode "edge", default) or none ("trail", variant P37).

Provenance labels (spec 7.1): P08 / P09 trigger on the close (FABIO), P30 Dmax 1.0% (NS-fixed, caller), P31 f
(NS-grid, caller), P32 structural stop behind the level +1 TICK (FABIO / NS-fixed), P35 model A LVN, retrace 25%
(NS-fixed), P36 model B reclaim within 5 bars, rest 3 bars, edge target (NS-fixed), P37 model B trail variant
(FABIO), P38 model C IB 30 min (FABIO), P39 model D rest validity 3 bars (NS-fixed), P33 entry cutoff open+330.

Readings of the spec that it does not spell out (open items, also listed in the package README):
 * Model A: the IMPULSE/ARMED step is evaluated at the impulse bar itself (leg profile P([i_b, i]) with i = i_b).
 * Model A confirm: "touching the limit" = l[j] <= P (long) / h[j] >= P (short) in the bar after arming, no fill-through.
 * Model B: probe extreme Xp is taken over the probe bars INCLUDING the reclaim bar; absorbed = any absb[j] == s_b over
   the probe bars up to and including j; after a timeout the scan resumes after the 5-bar window.
 * No entry gate beyond the decision bar: entry_allowed() is applied to the arming / signal bar (as add_allowed does).
"""
from .costs import TICK
from .fill import find_fill, fills_in_bar, missed_winner
from .manage import simulate_trade
from .signals import (balance, big_push, breakout, build_profile, control_level, failed_auction, lvn_levels,
                      select_lvn)

RECLAIM_BARS = 5     # P36 NS-fixed: model B reclaim within 5 bars of the probe bar (spec section 4)
REST_VALID_B = 3     # P36 NS-fixed: model B rest limit valid 3 bars
REST_VALID_D = 3     # P39 NS-fixed: model D rest limit valid 3 bars
IB_MINUTES = 30      # P38 FABIO: model C initial balance = first 30 minutes (LQ:841-843); N bars of 1m


def d_and_stop(s, entry, structural, f, dmax):
    """D = max(f * entry, structural); None (no arm) if D > Dmax * entry. Returns (D, stop0 = entry - s*D)."""
    D = max(f * entry, structural)
    if D > dmax * entry:
        return None
    return D, entry - s * D


def _end(bars, end_idx):
    return len(bars) - 1 if end_idx is None else min(end_idx, len(bars) - 1)


def _new():
    return {"arms": 0, "fills": 0, "missed_winners": 0, "trades": []}


def _arr(a, j):
    return a[j] if a is not None and 0 <= j < len(a) else 0


def _sim_kw(be_k, slip_bps, s8_kw, tick, stop_first):
    return {"be_k": be_k, "slip_bps": slip_bps, "s8_kw": s8_kw, "tick": tick, "stop_first": stop_first}


def _rest_trade(bars, res, k, s, price, D, stop0, fill_end, end, ctrl, absorbed, mgmt, target, kw):
    """Arm a resting limit at the close of bar k; fill via the fill-through rule within [k+1, fill_end]; simulate."""
    res["arms"] += 1
    fl = find_fill(bars, k, s, price, tick=kw["tick"], end_idx=fill_end)
    if fl is None:
        if missed_winner(bars, s, price, D, k + 1, end):
            res["missed_winners"] += 1
        return None
    j, px = fl
    res["fills"] += 1
    t = simulate_trade(bars, j, s, px, D, stop0, entry_kind="maker", ctrl=ctrl, end_idx=end, target=target, mgmt=mgmt,
                       absorbed=absorbed, **kw)
    res["trades"].append(t)
    return t


def _confirm_trade(bars, res, j, s, D, stop0, end, ctrl, absorbed, mgmt, target, kw):
    """Taker entry at o[j]; bar j is the fill bar (spec 5.1)."""
    res["arms"] += 1
    res["fills"] += 1
    t = simulate_trade(bars, j, s, bars[j]["o"], D, stop0, entry_kind="taker", ctrl=ctrl, end_idx=end, target=target,
                       mgmt=mgmt, absorbed=absorbed, **kw)
    res["trades"].append(t)
    return t


# ================================================================ trade functions (contract)
def model_a_trade(bars, k, s, O, lvn, f, dmax, ctrl=None, end_idx=None, mgmt="dist", absorbed=None,
                  entry_mode="rest", be_k=1.0, slip_bps=0.0, s8_kw=None, tick=TICK, stop_first=True,
                  last_entry_idx=None):
    """Model A trade for a set-up armed at the close of bar k (spec section 4): side s, balance edge O, LVN* `lvn`.

    rest: limit at LVN*, structural stop = s*(entry - O) + TICK; confirm: taker at o[j+1] after the first armed bar j
    (j >= k+1) touching the limit with ctrl[j] == s. No target. last_entry_idx bounds the decision bar (open+329).
    """
    res, end, kw = _new(), _end(bars, end_idx), _sim_kw(be_k, slip_bps, s8_kw, tick, stop_first)
    if last_entry_idx is not None and k > last_entry_idx:
        return res
    if entry_mode == "rest":
        plan = d_and_stop(s, lvn, s * (lvn - O) + tick, f, dmax)
        if plan is None:
            return res
        _rest_trade(bars, res, k, s, lvn, plan[0], plan[1], end, end, ctrl, absorbed, mgmt, None, kw)
        return res
    if entry_mode != "confirm":
        raise ValueError("entry_mode must be 'rest' or 'confirm', got %r" % (entry_mode,))
    for j in range(k + 1, end):                                  # j + 1 must exist inside the window
        if last_entry_idx is not None and j > last_entry_idx:
            break
        touch = bars[j]["l"] <= lvn if s > 0 else bars[j]["h"] >= lvn
        if touch and _arr(ctrl, j) == s:
            entry = bars[j + 1]["o"]
            plan = d_and_stop(s, entry, s * (entry - O) + tick, f, dmax)
            if plan is not None:
                _confirm_trade(bars, res, j + 1, s, plan[0], plan[1], end, ctrl, absorbed, mgmt, None, kw)
            return res
    return res


def _b_probe(bars, i0, sb, E, absorbed, end):
    """Model B PROBE from bar i0 (close outside the balance on side sb) -> ("reclaim", j, Xp) | ("timeout", last, Xp) |
    ("open", end, Xp). Reclaim = first bar j <= i0+5 with sb*(c[j]-E) < 0 and absorbed (any absb == sb over [i0, j])."""
    key = "h" if sb > 0 else "l"
    Xp = bars[i0][key]
    absd = _arr(absorbed, i0) == sb
    last = min(i0 + RECLAIM_BARS, end)
    for j in range(i0 + 1, last + 1):
        Xp = max(Xp, bars[j][key]) if sb > 0 else min(Xp, bars[j][key])
        absd = absd or _arr(absorbed, j) == sb
        if sb * (bars[j]["c"] - E) < 0 and absd:
            return ("reclaim", j, Xp)
    if i0 + RECLAIM_BARS <= end:
        return ("timeout", i0 + RECLAIM_BARS, Xp)
    return ("open", end, Xp)


def model_b(bars, start_idx, balance, absorbed, f, dmax, entry_mode="rest", end_idx=None, target_mode="edge", ctrl=None,
            mgmt="dist", be_k=1.0, slip_bps=0.0, s8_kw=None, tick=TICK, stop_first=True, last_entry_idx=None):
    """Model B failed-breakout reclaim (spec section 4) on an injected balance {"H", "L"}, scanning from start_idx.

    PROBE at the first bar i with s_b*(c[i] - E_{s_b}) > 0 (Xp = probe extreme); RECLAIM at the first bar j <= i+5 with
    s_b*(c[j] - E_{s_b}) < 0 and an absorbed bar in the probe; side s = -s_b. rest: limit at c[j], valid 3 bars;
    confirm: taker at o[j+1]. Structural stop = |Xp - entry| + TICK. target_mode "edge": target = E_s (maker,
    fill-through); "trail": no target. No day gate. One filled trade per call.
    """
    if target_mode not in ("edge", "trail"):
        raise ValueError("target_mode must be 'edge' or 'trail', got %r" % (target_mode,))
    if entry_mode not in ("rest", "confirm"):
        raise ValueError("entry_mode must be 'rest' or 'confirm', got %r" % (entry_mode,))
    res, end, kw = _new(), _end(bars, end_idx), _sim_kw(be_k, slip_bps, s8_kw, tick, stop_first)
    H, L = balance["H"], balance["L"]
    i = start_idx
    while i <= end:
        c = bars[i]["c"]
        sb = 1 if c > H else (-1 if c < L else 0)
        if sb == 0:
            i += 1
            continue
        kind, j, Xp = _b_probe(bars, i, sb, H if sb > 0 else L, absorbed, end)
        if kind == "open":
            break
        if kind == "timeout":
            i = j + 1
            continue
        s = -sb
        target = None if target_mode == "trail" else (H if s > 0 else L)
        if last_entry_idx is not None and j > last_entry_idx:
            i = j + 1
            continue
        if entry_mode == "confirm":
            if j + 1 > end:
                break
            entry = bars[j + 1]["o"]
            plan = d_and_stop(s, entry, abs(Xp - entry) + tick, f, dmax)
            if plan is None:
                i = j + 1
                continue
            _confirm_trade(bars, res, j + 1, s, plan[0], plan[1], end, ctrl, absorbed, mgmt, target, kw)
            break
        entry = bars[j]["c"]
        plan = d_and_stop(s, entry, abs(Xp - entry) + tick, f, dmax)
        if plan is None:
            i = j + 1
            continue
        t = _rest_trade(bars, res, j, s, entry, plan[0], plan[1], min(j + REST_VALID_B, end), end, ctrl, absorbed, mgmt,
                        target, kw)
        if t is not None:
            break
        i = j + REST_VALID_B + 1
    return res


def model_c(bars, open_idx, ib_len, m, f, dmax, entry_mode="rest", tier="99", gate_open=True, ctrl=None, end_idx=None,
            mgmt="dist", absorbed=None, be_k=1.0, slip_bps=0.0, s8_kw=None, tick=TICK, stop_first=True,
            last_entry_idx=None):
    """Model C IVB (spec section 4): IB = bars [open, open+ib_len); IBH / IBL / mid. At the first bar i >= open+ib_len
    with s*(c[i] - IB_s) > 0 and S4(i, m, s) and the day gate open: rest = limit at IB_s armed at the close of i
    (valid until end_idx); confirm = taker at o[i+1]. Structural stop = s*(entry - mid) + TICK. One IVB set-up per day:
    the first qualifying bar is the only attempt (it may not arm if D > Dmax). gate_open: bool, or callable(i) -> bool.
    """
    if entry_mode not in ("rest", "confirm"):
        raise ValueError("entry_mode must be 'rest' or 'confirm', got %r" % (entry_mode,))
    res, end, kw = _new(), _end(bars, end_idx), _sim_kw(be_k, slip_bps, s8_kw, tick, stop_first)
    ib = bars[open_idx:open_idx + ib_len]
    if len(ib) < ib_len or open_idx + ib_len - 1 > end:
        return res
    IBH, IBL = max(b["h"] for b in ib), min(b["l"] for b in ib)
    mid = (IBH + IBL) / 2.0
    for i in range(open_idx + ib_len, end + 1):
        if last_entry_idx is not None and i > last_entry_idx:
            break
        if not (gate_open(i) if callable(gate_open) else gate_open):
            continue
        for s in (1, -1):
            IBs = IBH if s > 0 else IBL
            if s * (bars[i]["c"] - IBs) > 0 and big_push(bars, i, m, s, tier):
                if entry_mode == "rest":
                    plan = d_and_stop(s, IBs, s * (IBs - mid) + tick, f, dmax)
                    if plan is not None:
                        _rest_trade(bars, res, i, s, IBs, plan[0], plan[1], end, end, ctrl, absorbed, mgmt, None, kw)
                elif i + 1 <= end:
                    entry = bars[i + 1]["o"]
                    plan = d_and_stop(s, entry, s * (entry - mid) + tick, f, dmax)
                    if plan is not None:
                        _confirm_trade(bars, res, i + 1, s, plan[0], plan[1], end, ctrl, absorbed, mgmt, None, kw)
                return res
    return res


def model_d_trade(bars, k, s, edge, lvl, f, dmax, entry_mode="rest", ctrl=None, absorbed=None, end_idx=None,
                  mgmt="dist", be_k=1.0, slip_bps=0.0, s8_kw=None, tick=TICK, stop_first=True, last_entry_idx=None):
    """Model D failed-auction breakout trade for an S5D output injected as (s, edge, lvl) at bar k (spec section 4, T58).

    rest: limit at `edge` armed at the close of k, valid bars k+1..k+3, cancelled if a close before the fill has
    s*(c - lvl) < 0 (the level failed); confirm: taker at o[k+1]. Structural stop = s*(entry - lvl) + TICK. No target.
    """
    if entry_mode not in ("rest", "confirm"):
        raise ValueError("entry_mode must be 'rest' or 'confirm', got %r" % (entry_mode,))
    res, end, kw = _new(), _end(bars, end_idx), _sim_kw(be_k, slip_bps, s8_kw, tick, stop_first)
    if last_entry_idx is not None and k > last_entry_idx:
        return res
    if entry_mode == "rest":
        plan = d_and_stop(s, edge, s * (edge - lvl) + tick, f, dmax)
        if plan is None:
            return res
        fill_end = min(k + REST_VALID_D, end)
        for t in range(k + 1, fill_end + 1):             # cancel: a close with s*(c - lvl) < 0 stops later fills
            if s * (bars[t]["c"] - lvl) < 0:
                fill_end = t
                break
        _rest_trade(bars, res, k, s, edge, plan[0], plan[1], fill_end, end, ctrl, absorbed, mgmt, None, kw)
        return res
    if k + 1 > end:
        return res
    entry = bars[k + 1]["o"]
    plan = d_and_stop(s, entry, s * (entry - lvl) + tick, f, dmax)
    if plan is not None:
        _confirm_trade(bars, res, k + 1, s, plan[0], plan[1], end, ctrl, absorbed, mgmt, None, kw)
    return res


# ================================================================ set-up scanners (feed engine.py)
def _touch(bar, s, price):
    return bar["l"] <= price if s > 0 else bar["h"] >= price


def _setup(model, state, s, **kw):
    d = {"model": model, "state": state, "s": s}
    d.update(kw)
    return d


def scan_model_a(bars, open_idx, i, N, k_bal, p, m, tier, bin_size, f, dmax, entry_mode, ctrl, absb, gate=None,
                 last_entry_idx=None, tick=TICK):
    """Replay model A over bars[open_idx..i]. State at the close of bar i:
    IDLE | IMPULSE | ARMED (rest: limit `price` live from bar i+1; confirm: touch level, waiting for a touch with
    ctrl == s) | SIGNAL (confirm: taker at o[i+1]; entry_ref = c[i]) | IN_TRADE (an earlier order would have filled).
    """
    if last_entry_idx is None:
        last_entry_idx = open_idx + 329
    state, s, i_b, O, armed = "IDLE", 0, None, None, None
    for b in range(open_idx, i + 1):
        bar = bars[b]
        if state == "ARMED" and entry_mode == "rest" and armed and fills_in_bar(bar, s, armed["price"], tick):
            return _setup("A", "IN_TRADE", s, fill_idx=b, armed_idx=armed["k"], price=armed["price"], i_b=i_b, O=O)
        if state == "IDLE":
            if b <= last_entry_idx and (gate is None or gate(b)):
                s_new = breakout(bars, b, N, k_bal, p, m, tier, bin_size)
                if s_new:
                    bal = balance(bars, b - 1, N, k_bal, bin_size)
                    s, i_b, O, armed, state = s_new, b, (bal["H"] if s_new > 0 else bal["L"]), None, "IMPULSE"
        if state in ("IMPULSE", "ARMED"):
            lvl_c = control_level(bars, ctrl, i_b, b, s)
            if (b > last_entry_idx or s * (bar["c"] - O) < 0
                    or (lvl_c is not None and _arr(ctrl, b) == -s and s * (bar["c"] - lvl_c) < 0)):
                state, armed, s = "IDLE", None, 0
                continue
            if entry_mode == "confirm" and state == "ARMED" and armed and _touch(bar, s, armed["price"]) \
                    and _arr(ctrl, b) == s:
                if b == i:
                    ref = bar["c"]
                    plan = d_and_stop(s, ref, s * (ref - O) + tick, f, dmax)
                    if plan is not None:
                        return _setup("A", "SIGNAL", s, entry_ref=ref, D=plan[0], stop=plan[1], anchor=O, i_b=i_b,
                                      armed_idx=armed["k"], price=armed["price"])
                else:
                    entry = bars[b + 1]["o"]
                    if d_and_stop(s, entry, s * (entry - O) + tick, f, dmax) is not None:
                        return _setup("A", "IN_TRADE", s, fill_idx=b + 1, armed_idx=armed["k"], price=entry, i_b=i_b, O=O)
                state, armed = "IMPULSE", None
            X = max(bars[j]["h"] for j in range(i_b, b + 1)) if s > 0 else min(bars[j]["l"] for j in range(i_b, b + 1))
            lv = select_lvn(lvn_levels(build_profile(bars, i_b, b, bin_size), bin_size), s, X, O, bar["c"])
            plan = None if lv is None else d_and_stop(s, lv, s * (lv - O) + tick, f, dmax)
            if plan is None:
                state, armed = "IMPULSE", None
            else:
                state, armed = "ARMED", {"price": lv, "D": plan[0], "stop": plan[1], "k": b}
    if state == "ARMED":
        return _setup("A", "ARMED", s, price=armed["price"], D=armed["D"], stop=armed["stop"], anchor=O, i_b=i_b,
                      armed_idx=armed["k"])
    return _setup("A", state, s, i_b=i_b, O=O)


def scan_model_b(bars, open_idx, i, N, k_bal, entry_mode, f, dmax, absb, target_mode="edge", last_entry_idx=None,
                 bin_size=50.0, tick=TICK):
    """Replay model B over bars[open_idx..i] with the balance S1(b-1) re-evaluated whenever the machine is IDLE.
    State: IDLE | PROBE (a probe is running, no reclaim yet) | ARMED (rest limit at c[j], live for bar i+1) |
    SIGNAL (confirm: taker at o[i+1]; entry_ref = c[i]) | IN_TRADE (an earlier order would have filled)."""
    if last_entry_idx is None:
        last_entry_idx = open_idx + 329
    b = open_idx
    while b <= i:
        bal = balance(bars, b - 1, N, k_bal, bin_size) if b >= 1 else None
        if bal is None:
            b += 1
            continue
        c = bars[b]["c"]
        sb = 1 if c > bal["H"] else (-1 if c < bal["L"] else 0)
        if sb == 0:
            b += 1
            continue
        kind, j, Xp = _b_probe(bars, b, sb, bal["H"] if sb > 0 else bal["L"], absb, i)
        if kind == "open":
            return _setup("B", "PROBE", -sb, probe_idx=b, Xp=Xp)
        if kind == "timeout":
            b = j + 1
            continue
        s = -sb
        target = None if target_mode == "trail" else (bal["H"] if s > 0 else bal["L"])
        if j > last_entry_idx:
            b = j + 1
            continue
        if entry_mode == "confirm":
            if j == i:
                ref = bars[j]["c"]
                plan = d_and_stop(s, ref, abs(Xp - ref) + tick, f, dmax)
                if plan is None:
                    b = j + 1
                    continue
                return _setup("B", "SIGNAL", s, entry_ref=ref, D=plan[0], stop=plan[1], target=target, anchor=Xp,
                              reclaim_idx=j)
            entry = bars[j + 1]["o"]
            if d_and_stop(s, entry, abs(Xp - entry) + tick, f, dmax) is None:
                b = j + 1
                continue
            return _setup("B", "IN_TRADE", s, fill_idx=j + 1, reclaim_idx=j, probe_idx=b, bal={"H": bal["H"], "L": bal["L"]})
        price = bars[j]["c"]
        plan = d_and_stop(s, price, abs(Xp - price) + tick, f, dmax)
        if plan is None:
            b = j + 1
            continue
        fl = find_fill(bars, j, s, price, tick=tick, end_idx=min(j + REST_VALID_B, i))
        if fl is not None:
            return _setup("B", "IN_TRADE", s, fill_idx=fl[0], reclaim_idx=j, price=price, probe_idx=b,
                          bal={"H": bal["H"], "L": bal["L"]})
        if i < j + REST_VALID_B:
            return _setup("B", "ARMED", s, price=price, D=plan[0], stop=plan[1], target=target, anchor=Xp,
                          armed_idx=j, valid_through=j + REST_VALID_B)
        b = j + REST_VALID_B + 1
    return _setup("B", "IDLE", 0)


def scan_model_c(bars, open_idx, i, ib_len, m, tier, entry_mode, f, dmax, gate=None, last_entry_idx=None, tick=TICK):
    """Replay model C over bars[open_idx..i]. State: IDLE (IB incomplete / no qualifying bar yet) | ARMED (rest limit at
    IB_s, live until the window end) | SIGNAL (confirm: taker at o[i+1]; entry_ref = c[i]) | IN_TRADE (the order would
    have filled earlier) | DONE (the one IVB set-up of the day did not arm: D > Dmax)."""
    if last_entry_idx is None:
        last_entry_idx = open_idx + 329
    if i < open_idx + ib_len - 1:
        return _setup("C", "IDLE", 0, reason="IB incomplete")
    ib = bars[open_idx:open_idx + ib_len]
    IBH, IBL = max(x["h"] for x in ib), min(x["l"] for x in ib)
    mid = (IBH + IBL) / 2.0
    for b in range(open_idx + ib_len, i + 1):
        if b > last_entry_idx:
            break
        if gate is not None and not gate(b):
            continue
        for s in (1, -1):
            IBs = IBH if s > 0 else IBL
            if not (s * (bars[b]["c"] - IBs) > 0 and big_push(bars, b, m, s, tier)):
                continue
            if entry_mode == "rest":
                plan = d_and_stop(s, IBs, s * (IBs - mid) + tick, f, dmax)
                if plan is None:
                    return _setup("C", "DONE", s, reason="no arm: D > Dmax*entry", trigger_idx=b)
                fl = find_fill(bars, b, s, IBs, tick=tick, end_idx=i)
                if fl is not None:
                    return _setup("C", "IN_TRADE", s, fill_idx=fl[0], armed_idx=b, price=IBs)
                return _setup("C", "ARMED", s, price=IBs, D=plan[0], stop=plan[1], anchor=mid, armed_idx=b, IBH=IBH,
                              IBL=IBL)
            if b == i:
                plan = d_and_stop(s, bars[b]["c"], s * (bars[b]["c"] - mid) + tick, f, dmax)
                if plan is None:
                    return _setup("C", "DONE", s, reason="no arm: D > Dmax*entry", trigger_idx=b)
                return _setup("C", "SIGNAL", s, entry_ref=bars[b]["c"], D=plan[0], stop=plan[1], anchor=mid,
                              armed_idx=b, IBH=IBH, IBL=IBL)
            entry = bars[b + 1]["o"]
            if d_and_stop(s, entry, s * (entry - mid) + tick, f, dmax) is None:
                return _setup("C", "DONE", s, reason="no arm: D > Dmax*entry", trigger_idx=b)
            return _setup("C", "IN_TRADE", s, fill_idx=b + 1, armed_idx=b)
    return _setup("C", "IDLE", 0, IBH=IBH, IBL=IBL)


def scan_model_d(bars, open_idx, i, N, k_bal, p, m, tier, bin_size, entry_mode, f, dmax, absb, gate=None,
                 last_entry_idx=None, tick=TICK):
    """Replay model D over bars[open_idx..i]. State: IDLE | ARMED (rest limit at the S5D edge, valid k+1..k+3) |
    SIGNAL (confirm: taker at o[i+1]; entry_ref = c[i]) | IN_TRADE (an earlier order would have filled)."""
    if last_entry_idx is None:
        last_entry_idx = open_idx + 329
    state, order = "IDLE", None
    for b in range(open_idx, i + 1):
        bar = bars[b]
        if state == "ARMED":
            if fills_in_bar(bar, order["s"], order["price"], tick):
                return _setup("D", "IN_TRADE", order["s"], fill_idx=b, armed_idx=order["k"], price=order["price"])
            if order["s"] * (bar["c"] - order["lvl"]) < 0 or b >= order["k"] + REST_VALID_D:
                state, order = "IDLE", None                    # level failed or the 3 bars are used up
            continue
        if b > last_entry_idx or (gate is not None and not gate(b)):
            continue
        fa = failed_auction(bars, b, N, k_bal, p, m, absb, tier, bin_size)
        if fa is None:
            continue
        s, edge, lvl = fa["s"], fa["edge"], fa["lvl"]
        if entry_mode == "confirm":
            if b == i:
                ref = bar["c"]
                plan = d_and_stop(s, ref, s * (ref - lvl) + tick, f, dmax)
                if plan is None:
                    continue
                return _setup("D", "SIGNAL", s, entry_ref=ref, D=plan[0], stop=plan[1], anchor=lvl, edge=edge,
                              armed_idx=b)
            entry = bars[b + 1]["o"]
            if d_and_stop(s, entry, s * (entry - lvl) + tick, f, dmax) is None:
                continue
            return _setup("D", "IN_TRADE", s, fill_idx=b + 1, armed_idx=b)
        plan = d_and_stop(s, edge, s * (edge - lvl) + tick, f, dmax)
        if plan is None:
            continue
        state, order = "ARMED", {"s": s, "price": edge, "lvl": lvl, "k": b, "D": plan[0], "stop": plan[1]}
    if state == "ARMED":
        return _setup("D", "ARMED", order["s"], price=order["price"], D=order["D"], stop=order["stop"], anchor=order["lvl"],
                      edge=order["price"], armed_idx=order["k"], valid_through=order["k"] + REST_VALID_D)
    return _setup("D", "IDLE", 0)
