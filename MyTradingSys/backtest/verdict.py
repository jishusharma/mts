import sys
sys.dont_write_bytecode = True
"""
MyTradingSys/backtest/verdict.py

Python port of Compute-Verdict from scripts/core/start-trading-day.ps1
(function at lines 150-248 as of 2026-09-26). Pure function of one snapshot
plus proof_direction_status from math_object_builder.build_math_object.

Parity (parity.py, 2026-09-26): 541 of 544 verdict lines in
runtime_data/apparatus_log.txt reproduced exactly (verdict AND proof dir).
The 3 misses are live-side, not port errors: at 2026-09-24 18:54-19:06 the
wrapper logged "'python' is not recognized", build_mo_cli never ran, and the
wrapper's $pd silently defaulted to "aligned". One of those produced a live
SETUP_FORMING that the rules say is WATCH (proof contradicted).

PowerShell -eq on strings is case-insensitive; the port lowercases to match.
If Compute-Verdict changes, this file must change with it - parity.py is the
guard.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys" / "runtime"))
from math_object_builder import build_math_object  # noqa: E402
from net_rr_floor import load_floor  # noqa: E402


def _d(x):
    if x is None or x == "":
        return 0.0
    return float(x)


def _g(obj, *keys):
    for k in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(k)
    return obj


VALID_PD = ("aligned", "contradiction")


def proof_dir_of(snap, fail_closed=False):
    """Same source as the live loop (build_mo_cli.py). fail_closed=False
    (default) replays live's pre-B071 behaviour for parity.py against
    archived logs. fail_closed=True is the B071 fix (CORE_READINESS_PLAN.md
    task B1): any non-(aligned|contradiction) result becomes "error", which
    compute_verdict caps at WAIT_PROOF instead of letting WATCH/SETUP_FORMING
    through unchecked. An executor must always pass fail_closed=True."""
    try:
        mo = build_math_object(snap)
        pd = mo.get("proof_direction_status")
    except Exception:
        return "error" if fail_closed else "aligned"
    if pd in VALID_PD:
        return pd
    if pd is None and not (snap.get("setup_candidates") or []):
        return "aligned"
    return "error" if fail_closed else (pd or "aligned")


def compute_verdict(snap, pd="aligned", floor=None):
    # The net_rr floor is read from MyTradingSys/system/net_rr_floor.json on every call (the wrapper does the
    # same each cycle). `floor` overrides it for a replay of a log recorded under another floor. An unreadable
    # file raises NetRrFloorError: a backtest must not silently pick a number.
    floor = load_floor() if floor is None else float(floor)
    price = _d(snap.get("current_price"))
    cond = snap.get("conditions") or {}
    cands = snap.get("setup_candidates") or []
    # D3 guard (CORE_READINESS_PLAN.md, operator ruling 2026-09-27, task C2): the
    # Java-side fix moves ExtraSetupBuilder output to module_candidates, but this
    # guard also protects against any archived/older snapshot where setup_candidates
    # still mixes SetupCandidatesBuilder ranks 1-3 with ExtraSetupBuilder extras
    # (rank 11+) - top must always be the first candidate with rank <= 3.
    top = None
    for c in cands:
        if c is not None and int(c.get("rank") or 999) <= 3:
            top = c
            break
    if top is None:
        return dict(verdict="NO_TRADE", reason="no candidates", top=None,
                    mode="normal", direction="", price=price, net_rr=0.0, proof=0)
    m = top.get("math") or {}
    net_rr = _d(m.get("net_rr"))
    net_ok = net_rr >= floor  # not Java's net_rr_sanity, which has its own copy of the number
    tier = str(m.get("tier")).lower()
    proof = int(_g(top, "score", "proof_count") or 0)
    sdir = str(top.get("direction") or "").lower()

    mode = "normal"
    try:
        prox = 0.0015
        val = _d(_g(snap, "daily_vp", "val")); vah = _d(_g(snap, "daily_vp", "vah"))
        sl1h = _d(_g(snap, "structure", "1h", "swing_low")); sh1h = _d(_g(snap, "structure", "1h", "swing_high"))
        sl15 = _d(_g(snap, "structure", "15m", "swing_low")); sh15 = _d(_g(snap, "structure", "15m", "swing_high"))
        nf = any(lv > 0 and abs(price - lv) / price < prox for lv in (val, sl1h, sl15))
        nc = any(lv > 0 and abs(price - lv) / price < prox for lv in (vah, sh1h, sh15))
        md = "normal"
        if sdir == "long" and nf:
            md = "floor_reaction"
        if sdir == "short" and nc:
            md = "ceiling_reaction"
        mode = md
    except Exception:
        pass
    # D1(a) (CORE_READINESS_PLAN.md, operator ruling 2026-09-27): the net_rr
    # hard stop from compiled_engine.md sec 6 applies always, no floor/ceiling
    # exception. suspend_rr path removed; mode is still computed and returned
    # for display/logging only, per the operator's ruling.

    if not net_ok:
        v, r = "WAIT_RR", "net_rr %.2f < %.2f" % (net_rr, floor)
    elif tier == "ignore":
        v, r = "WAIT_FAR", "tier=ignore"
    elif tier == "conditional":
        v, r = "WAIT_TRIGGER", "price not at zone"
    elif proof < 3:
        v, r = "WAIT_PROOF", "proof %d" % proof
    elif proof < 5:
        v, r = "WATCH", "proof %d" % proof
    else:
        v, r = "SETUP_FORMING", "proof %d" % proof
    if str(pd).lower() == "contradiction" and v == "SETUP_FORMING":
        v, r = "WATCH", "proof %d contradicted" % proof
    if str(pd).lower() not in VALID_PD and v in ("WATCH", "SETUP_FORMING"):
        v, r = "WAIT_PROOF", "proof_dir error"

    pv = str(cond.get("price_vs_va") or "").lower()
    cs = str(cond.get("cvd_slope") or "").lower()
    if pv == "below_val" and cs == "falling" and sdir == "long" and v in ("SETUP_FORMING", "SETUP_CONFIRMED"):
        v, r = "WAIT_RR", "broken below_val + CVD falling vs LONG"
    if pv == "above_vah" and cs == "rising" and sdir == "short" and v in ("SETUP_FORMING", "SETUP_CONFIRMED"):
        v, r = "WAIT_RR", "broken above_vah + CVD rising vs SHORT"
    if v in ("WATCH", "SETUP_FORMING"):
        if sdir == "long" and cs == "falling":
            v, r = "WAIT_PROOF", "flow contradiction"
        if sdir == "short" and cs == "rising":
            v, r = "WAIT_PROOF", "flow contradiction"
    return dict(verdict=v, reason=r, top=top, mode=mode, direction=sdir,
                price=price, net_rr=net_rr, proof=proof)
