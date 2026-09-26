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


def proof_dir_of(snap):
    """Same source as the live loop (build_mo_cli.py). Replay default on
    failure is 'aligned' to match live behaviour for parity. An executor must
    NOT copy this default - it must fail closed (see T050)."""
    try:
        mo = build_math_object(snap)
        return mo.get("proof_direction_status") or "aligned"
    except Exception:
        return "aligned"


def compute_verdict(snap, pd="aligned"):
    price = _d(snap.get("current_price"))
    cond = snap.get("conditions") or {}
    cands = snap.get("setup_candidates") or []
    if len(cands) == 0 or cands[0] is None:
        return dict(verdict="NO_TRADE", reason="no candidates", top=None,
                    mode="normal", direction="", price=price, net_rr=0.0, proof=0)
    top = cands[0]
    m = top.get("math") or {}
    net_rr = _d(m.get("net_rr"))
    net_ok = bool(m.get("net_rr_sanity"))
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
    suspend = mode in ("floor_reaction", "ceiling_reaction")

    if (not net_ok) and (not suspend):
        v, r = "WAIT_RR", "net_rr %.2f < 2.0" % net_rr
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
