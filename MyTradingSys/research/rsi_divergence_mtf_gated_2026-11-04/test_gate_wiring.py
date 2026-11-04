"""Gate wiring for rsi_divergence_mtf_gated_2026-11-04: events outside the gated regime are dropped; as-of causality
(a planted future bar changes nothing); retest entry reads only the bars after the signal bar."""
import importlib.util
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("rsi_gated_study", HERE / "study.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)

DAY = study.DAY


def _ev(day):
    return {"t_close": day * DAY + 1, "i": day, "close_b": 100.0}


def test_gate_drops_events_outside_regime():
    regs = {10: "bull", 11: "bear", 12: "range", 13: None, 14: "bull"}
    ev = [_ev(d) for d in regs]
    at = lambda t: regs[int(t // DAY)]
    assert [e["i"] for e in study.gate_events(ev, at, "bullish", "aligned")] == [10, 14]
    assert [e["i"] for e in study.gate_events(ev, at, "bearish", "aligned")] == [11]
    assert [e["i"] for e in study.gate_events(ev, at, "bullish", "counter")] == [11]
    assert [e["i"] for e in study.gate_events(ev, at, "bullish", "range")] == [12]
    assert [e["i"] for e in study.gate_events(ev, at, "bullish", "all")] == [10, 11, 12, 14]   # None-regime always dropped


def _ctx(extra=False):
    n = 400
    td = [(k + 1) * DAY for k in range(n)]           # daily bar k closes at (k+1) days
    cd = [100.0 + k for k in range(n)]               # steady rise: above SMA200
    tw = [(7 * k + 7) * DAY for k in range(n // 7)]
    rw = [70.0] * len(tw)
    tm = [(30 * k + 30) * DAY for k in range(n // 30)]
    rm = [70.0] * len(tm)
    if extra:                                        # future bars: crash, RSI 10, all closing AFTER t
        td += [(n + 1) * DAY, (n + 2) * DAY]
        cd += [1.0, 1.0]
        tw += [(n + 7) * DAY]
        rw += [10.0]
        tm += [(n + 30) * DAY]
        rm += [10.0]
    return (td, cd), (tw, rw), (tm, rm)


def test_planted_future_bar_changes_nothing():
    t = 300 * DAY + 5
    base = study.make_regime_at(*_ctx(False))(t)
    assert base == "bull"
    assert study.make_regime_at(*_ctx(True))(t) == base
    # the planted bars do flip a read taken after they close (the plant is live, not inert)
    assert study.make_regime_at(*_ctx(True))((400 + 40) * DAY) != "bull"


def _bars(n, shock=None):
    import random
    rnd = random.Random(7)
    out, c = [], 100.0
    for k in range(n):
        c = c * (1 + rnd.gauss(0, 0.01))
        out.append({"t": k * 3600000, "o": c, "h": c + 1, "l": c - 1, "c": c})
    if shock is not None:
        out.append({"t": n * 3600000, "o": shock, "h": shock, "l": shock, "c": shock})
    return out


def test_event_detection_ignores_future_bars():
    base = study.find_events(_bars(400), "bullish", "W12", "1h")
    more = study.find_events(_bars(400, shock=1.0), "bullish", "W12", "1h")
    assert len(base) >= 3
    # an event stamped on bar i may only depend on bars <= i: every base event is reproduced unchanged
    assert [e for e in more if e["i"] < 400] == base


def test_retest_fill_reads_only_after_signal_bar():
    bars = [{"t": k * 3600000, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0} for k in range(40)]
    bars[5]["l"] = 50.0                              # the signal bar's own dip must not fill the retest
    ev = [{"t_close": 6 * 3600000, "i": 5, "close_b": 98.0}]
    trs, nsig = study.trades_for(ev, bars, "bullish", "retest", h=10, n=10)
    assert nsig == 1 and trs == []                   # no pullback to 98 in bars 6..15: skipped, not filled on bar 5
    bars[8]["l"] = 97.0                              # retest at bar 8: fills at 98.0
    trs, _ = study.trades_for(ev, bars, "bullish", "retest", h=10, n=10)
    assert len(trs) == 1 and abs(trs[0]["gross"] - (100.0 - 98.0) / 98.0 * 100) < 1e-9
