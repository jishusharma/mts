"""Rumers DEV runner: synthetic 1m bars. Fails on a tree without run_dev.py (module missing), passes after.

Rule 2 (PDH/PDL fade) must trigger exactly once; the +1 shift must enter on the LATER bar's open, never the unshifted one;
fee per round trip equals fees.py BINANCE_TAKER * 2.
"""
import importlib.util
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
RUN_DEV = REPO / "MyTradingSys" / "research" / "rumers_2026-11-01" / "run_dev.py"
sys.path.insert(0, str(REPO))


def _load():
    spec = importlib.util.spec_from_file_location("rumers_run_dev", RUN_DEV)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _bars(mod):
    """Day 0: range 100..110. Day 1: flat 105, one 5m bar (min 600-604) pokes to 111 and closes 108, then 107, then falls."""
    base = (mod.START_MS // mod.DAY_MS) * mod.DAY_MS
    n = 2 * 1440
    ts = base + np.arange(n, dtype=np.int64) * mod.MIN_MS
    px = np.full(n, 105.0)
    o, h, l, c = px.copy(), px.copy(), px.copy(), px.copy()
    h[720], l[721] = 110.0, 100.0                    # day-0 extremes: PDH 110, PDL 100
    d1 = 1440
    h[d1 + 601] = 111.0                              # sweep: pierces PDH 110, closes 108 inside the range
    for k in range(d1 + 601, d1 + 610):
        o[k] = c[k] = 108.0
        h[k] = max(h[k], 108.0)
        l[k] = 108.0
    o[d1 + 601] = 105.0
    o[d1 + 600] = c[d1 + 600] = h[d1 + 600] = l[d1 + 600] = 106.0   # -1 shift entry bar opens 106
    for k in range(d1 + 610, d1 + 700):              # +1 shift entry bar (min 610) opens 107
        o[k] = c[k] = h[k] = l[k] = 107.0
    for k in range(d1 + 700, d1 + 720):              # price falls through the 105 midpoint target
        o[k] = c[k] = h[k] = 104.0
        l[k] = 104.0
        h[k] = 107.0 if k == d1 + 700 else 104.0
    v = np.ones(n)
    return ts, o, h, l, c, v


def test_rule2_triggers_once_and_shift_uses_later_bar():
    mod = _load()
    V = mod.build_views(*_bars(mod))
    sigs = mod.RULES["R2"](V)
    assert len(sigs) == 1 and sigs[0]["side"] == -1
    base = (mod.START_MS // mod.DAY_MS) * mod.DAY_MS
    assert sigs[0]["sig_ms"] == base + (1440 + 605) * mod.MIN_MS          # known at the CLOSE of the 5m bar
    assert abs(sigs[0]["stop"] - 111.2) < 1e-9 and abs(sigs[0]["target"] - 105.0) < 1e-9
    t0, _ = mod.run_rule(V, "R2", 0, sigs)
    tp, _ = mod.run_rule(V, "R2", 1, sigs)
    tm, _ = mod.run_rule(V, "R2", -1, sigs)
    assert len(t0) == len(tp) == len(tm) == 1
    assert t0[0]["entry"] == 108.0 and t0[0]["entry_ms"] == sigs[0]["sig_ms"]
    assert tp[0]["entry"] == 107.0 and tp[0]["entry_ms"] == sigs[0]["sig_ms"] + 5 * mod.MIN_MS   # +1: later bar, not the unshifted one
    assert tp[0]["entry"] != t0[0]["entry"]
    assert tm[0]["entry_ms"] == sigs[0]["sig_ms"] - 5 * mod.MIN_MS         # -1 enters before the signal bar closed
    assert t0[0]["kind"] == "T" and abs(t0[0]["gross_r"] - 3.0 / 3.2) < 1e-9


def test_fee_is_fees_py_taker_round_trip():
    mod = _load()
    from MyTradingSys.backtest.fees import BINANCE_TAKER
    V = mod.build_views(*_bars(mod))
    tr, _ = mod.run_rule(V, "R2", 0)
    t = tr[0]
    assert abs((t["gross_r"] - t["net_r"]) - BINANCE_TAKER * 2 / t["stop_pct"]) < 1e-12
    assert t["net_r_stress"] < t["net_r"]
