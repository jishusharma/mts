"""Fabio v3 management (FABIO_V3_SPEC.md section 5.2): stop moves, S8 exits, adds, single-leg trade walk.

Order at each close i > fill bar: (1) stop check happened intrabar; (2) stop moves per mgmt; (3) S8; (4) add.
Every stop change is recorded in `moves` as (i, new_stop, kind), kind in "be" | "trail" | "opp" | "own". A stop exit's
reason = kind of the last move ("stop" if none); other exits: "s8", "target", "window_end".

Provenance labels (spec 7.1): mgmt "event" (P17 E_opp BE, P18 E_opp ratchet, P19 E_own de-risk by stop, P20 trail
after a defended break; all FABIO) is the v3.1 default; mgmt "dist" (P21 NS-grid be_k {1.0, 2.0}) is a registered
variant. P22 FABIO max 2 adds (3 entries); P23 FABIO add_mode "be" default; P24 FABIO add_mode "day" variant (operator);
P25 NS-fixed add cap q1 and min add 0.25 q1; P11 FABIO S7 add gate; P16 S8(d) on in event mode; P41 SIM stop-first,
tick, fill rules. Function defaults (mgmt "dist", be_k 1.0, add_mode "be", s7 True) keep T01-T50 valid (spec :366) and
are not selected grid values.

Not implemented here (documented in the package README): multi-leg add execution. `add_allowed` / `add_size` are the
decision helpers (T32, T33, T62); simulate_trade manages the FIRST LEG only (the contract's trade dict has one entry).
"""
from .costs import EPS, TICK, leg_r
from .day_gates import entry_allowed
from .signals import control_level, exhaustion

MAX_ADDS = 2          # P22 FABIO: max adds 2 (3 entries)
MIN_ADD_FRAC = 0.25   # P25 NS-fixed: min add 0.25 * q1
ADD_PUSH_M = 15       # P07 NS-fixed: S4 window for adds is 15 (spec 5.2 "S4(i,15,s)")


# ---------------------------------------------------------------- stop helpers
def be_update(s, e1, D, stop, ext, be_k=1.0):
    """mgmt "dist": BE when s*(ext - e1) >= be_k*D -> stop = e1 if tighter (spec 5.2). ext = best price since fill bar+1."""
    if s * (ext - e1) >= be_k * D - EPS and s * (e1 - stop) > 0:
        return e1
    return stop


def trail_update(s, stop, lvl, c, tick=TICK):
    """cand = S6 level - s*TICK; stop -> cand iff s*(cand - stop) > 0 and s*(c - cand) > 0 (spec 5.2). lvl None -> unchanged."""
    if lvl is None:
        return stop
    cand = lvl - s * tick
    if s * (cand - stop) > 0 and s * (c - cand) > 0:
        return cand
    return stop


def opp_stop(s, e1, stop, pb, c, tick=TICK):
    """E_opp (spec 5.2 (i), T51): candidates {e1, pb - s*TICK}; keep those with s*(c - x) > 0; best = max_s of them;
    stop -> best iff s*(best - stop) > 0 (only tightens)."""
    cands = [x for x in (e1, pb - s * tick) if s * (c - x) > 0]
    if not cands:
        return stop
    best = max(cands) if s > 0 else min(cands)
    return best if s * (best - stop) > 0 else stop


# ---------------------------------------------------------------- adds
def add_size(s, legs, stop, pa, q1, budget=0.0):
    """Size of an add taken at pa (spec 5.2, T32, T62). legs = [(q_k, e_k), ...].

    locked = sum_k q_k * s*(stop - e_k); dist = s*(pa - stop); q_add = min(q1, (budget + locked) / dist); 0.0 if
    q_add < 0.25*q1 (skip). add_mode "be": budget 0 (P&L at the stop after the add >= 0); add_mode "day": budget =
    max(0, closed day R) * U (U = q1*D1/r1, section 6), supplied by the caller.
    """
    dist = s * (pa - stop)
    if not dist > 0:
        return 0.0
    locked = sum(q * s * (stop - e) for (q, e) in legs)
    q_add = min(q1, (budget + locked) / dist)
    if q_add < MIN_ADD_FRAC * q1 - EPS:
        return 0.0
    return q_add


def add_allowed(s, e1, stop, n_adds, i, open_idx, control, push_ok, curve_state, add_mode="be", s7=True):
    """Add gates (spec 5.2, T33, T62): fewer than 2 adds so far, decision bar i < open+330, S3(i).control == s,
    S4(i,15,s) (push_ok), S7 gate (unless s7 off: no long add in premium, no short add in discount), and add_mode "be":
    stop at or beyond e1 (add_mode "day": no BE gate). curve_state None (unknown) with s7 on blocks the add (fail closed).
    """
    if add_mode not in ("be", "day"):
        raise ValueError("add_mode must be 'be' or 'day', got %r" % (add_mode,))
    if n_adds >= MAX_ADDS:
        return False
    if not entry_allowed(i, open_idx):
        return False
    if control != s or not push_ok:
        return False
    if s7:
        if curve_state is None:
            return False
        if (s > 0 and curve_state == "premium") or (s < 0 and curve_state == "discount"):
            return False
    if add_mode == "be" and not s * (stop - e1) >= 0:
        return False
    return True


# ---------------------------------------------------------------- the single-leg walk
def _closed(w, exit_px, exit_idx, reason, exit_kind):
    w.update({"status": "closed", "exit": exit_px, "exit_idx": exit_idx, "reason": reason, "exit_kind": exit_kind})
    return w


def walk_trade(bars, fill_idx, s, entry, D, stop, ctrl=None, absorbed=None, mgmt="dist", be_k=1.0, tick=TICK,
               end_idx=None, target=None, s8_kw=None, stop_first=True, force_close=True):
    """Walk one first leg bar by bar from its fill bar (spec 5.2). Returns a state dict:
    status "closed" (exit, exit_idx, reason, exit_kind) or "open" (force_close False and nothing ended it by end_idx),
    plus stop (the stop in force for the next bar), moves, be_done, dl (event mode defended level or None),
    s8_next (S8 true at the last processed bar: exit taker at the next open), last_idx.
    force_close True (simulate_trade): a trade still open at end_idx exits "window_end" taker at c[end_idx].
    force_close False (engine IN_TRADE read): returns the open state instead.
    """
    if mgmt not in ("dist", "event"):
        raise ValueError("mgmt must be 'dist' or 'event', got %r" % (mgmt,))
    n = len(bars)
    end = n - 1 if end_idx is None else min(end_idx, n - 1)
    if not 0 <= fill_idx <= end:
        raise ValueError("fill_idx %r outside [0, end_idx=%r]" % (fill_idx, end))
    ctrl = ctrl if ctrl is not None else []
    absb = absorbed if absorbed is not None else []
    s8 = dict(s8_kw or {})
    climax = s8.pop("climax", mgmt == "event")      # P16: clause (d) is on in event mode (spec 5.2 (iv))
    cache = {}
    stop0 = stop
    moves, last_kind = [], "stop"
    ext, be_done, dl, dl_i, s8_last = None, False, None, None, False
    w = {"stop0": stop0, "fill_idx": fill_idx, "target": target}

    def note(i, new, kind):
        nonlocal stop, last_kind
        stop = new
        moves.append((i, new, kind))
        last_kind = kind

    for i in range(fill_idx, end + 1):
        b = bars[i]
        if s > 0:
            hit_stop = b["l"] <= stop
            hit_tgt = target is not None and i > fill_idx and b["h"] >= target + tick - EPS
        else:
            hit_stop = b["h"] >= stop
            hit_tgt = target is not None and i > fill_idx and b["l"] <= target - tick + EPS
        if hit_stop and (stop_first or not hit_tgt):                 # P41 SIM stop-first (BP:45-47)
            px = stop
            if i > fill_idx and ((s > 0 and b["o"] < stop) or (s < 0 and b["o"] > stop)):
                px = b["o"]                                          # gap through the stop: exit at the open
            w.update({"stop": stop, "moves": moves, "be_done": be_done, "dl": dl, "s8_next": False, "last_idx": i})
            return _closed(w, px, i, last_kind, "taker")
        if hit_tgt:
            w.update({"stop": stop, "moves": moves, "be_done": be_done, "dl": dl, "s8_next": False, "last_idx": i})
            return _closed(w, target, i, "target", "maker")
        if i == fill_idx:
            continue                                                 # fill bar: only the stop is checked (spec 5.1)
        c_i = b["c"]
        ext = (b["h"] if ext is None else max(ext, b["h"])) if s > 0 else (b["l"] if ext is None else min(ext, b["l"]))
        # (2) stop moves per mgmt
        if mgmt == "dist":
            if s * (ext - entry) >= be_k * D - EPS:
                be_done = True
            new = be_update(s, entry, D, stop, ext, be_k)
            if new != stop:
                note(i, new, "be")
            if be_done:                                              # trail only after BE
                new = trail_update(s, stop, control_level(bars, ctrl, fill_idx, i, s), c_i, tick)
                if new != stop:
                    note(i, new, "trail")
        else:
            a_i = absb[i] if i < len(absb) else 0
            if a_i == -s:                                            # (i) E_opp: other side's absorbed push
                a = fill_idx
                for j in range(i - 1, fill_idx, -1):
                    if j < len(ctrl) and ctrl[j] == s:
                        a = j
                        break
                seg = range(a + 1, i + 1)
                pb = min(bars[j]["l"] for j in seg) if s > 0 else max(bars[j]["h"] for j in seg)
                new = opp_stop(s, entry, stop, pb, c_i, tick)
                if new != stop:
                    note(i, new, "opp")
            elif a_i == s:                                           # (ii) E_own: lower risk by stop, never an exit
                new = trail_update(s, stop, control_level(bars, ctrl, fill_idx, i, s), c_i, tick)
                if new != stop:
                    note(i, new, "own")
                dl, dl_i = (b["h"] if s > 0 else b["l"]), i          # arm DL = S9 at i
            if dl is not None and dl_i < i and s * (c_i - dl) > 0:   # (iii) defended level broken -> S6 trail
                new = trail_update(s, stop, control_level(bars, ctrl, fill_idx, i, s), c_i, tick)
                if new != stop:
                    note(i, new, "trail")
                dl = dl_i = None
        # (3) S8
        lvl = control_level(bars, ctrl, fill_idx, i, s)
        s8_hit = exhaustion(bars, i, {"s": s, "e_i": fill_idx, "lvl": lvl}, climax=climax, cache=cache, **s8)
        if s8_hit and i < end:
            w.update({"stop": stop, "moves": moves, "be_done": be_done, "dl": dl, "s8_next": False, "last_idx": i})
            return _closed(w, bars[i + 1]["o"], i + 1, "s8", "taker")
        s8_last = s8_hit
    w.update({"stop": stop, "moves": moves, "be_done": be_done, "dl": dl, "last_idx": end,
              "s8_next": bool(s8_last)})
    if force_close:
        w["s8_next"] = False
        return _closed(w, bars[end]["c"], end, "window_end", "taker")
    w["status"] = "open"
    return w


def simulate_trade(bars, fill_idx, s, entry, D, stop, q1=1.0, entry_kind="maker", be_k=1.0, ctrl=None, tick=TICK,
                   end_idx=None, target=None, slip_bps=0.0, mgmt="dist", absorbed=None, s8_kw=None, stop_first=True):
    """One first leg from its fill bar to its exit (spec 5.1, 5.2, 5.3). Returns the contract trade dict
    {entry, D, stop0, stop, exit, reason, gross_r, fee_r, net_r, fill_idx, exit_idx, target, moves} plus slip_r, s, q1,
    entry_kind, mgmt, exit_kind. R unit = q1*D. Exits: stop (taker, at the stop or at the open if gapped through),
    target (maker, fill-through), S8 (taker at o[i+1]), window end (taker at c[end_idx]).

    stop_first True (default, P41 SIM): stop wins a bar where the target is also touched; False reports target-first.
    ctrl / absorbed = S3 control / absorbed arrays (index = bar index); None = no control / no absorption known.
    s8_kw = optional dict of exhaustion() keyword args (k_bal, tier, bin_size, z_hi, p, climax); climax defaults to
    True in event mode and False in dist mode.
    """
    w = walk_trade(bars, fill_idx, s, entry, D, stop, ctrl=ctrl, absorbed=absorbed, mgmt=mgmt, be_k=be_k, tick=tick,
                   end_idx=end_idx, target=target, s8_kw=s8_kw, stop_first=stop_first, force_close=True)
    r = leg_r(s, q1, entry, w["exit"], entry_kind, w["exit_kind"], q1 * D, slip_bps)
    return {"entry": entry, "D": D, "stop0": w["stop0"], "stop": w["stop"], "exit": w["exit"], "reason": w["reason"],
            "gross_r": r["gross_r"], "fee_r": r["fee_r"], "slip_r": r["slip_r"], "net_r": r["net_r"],
            "fill_idx": fill_idx, "exit_idx": w["exit_idx"], "target": target, "moves": w["moves"], "s": s, "q1": q1,
            "entry_kind": entry_kind, "mgmt": mgmt, "exit_kind": w["exit_kind"]}
