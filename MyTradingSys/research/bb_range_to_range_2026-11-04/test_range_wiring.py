"""Wiring tests for bb_range_to_range_2026-11-04: bands are causal, events are the first bar of an excursion, the bracket is
stop-first, the retest reads only bars after the signal bar, the regime gate drops non-range events, session = research_kit tag."""
import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("bb_r2r_study", HERE / "study.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)
from MyTradingSys.backtest import research_kit as rk  # noqa: E402

HOUR = 3600000
DAY = 86400000


def _bars(closes, t0=0, step=HOUR, spread=0.0):
    return [{"t": t0 + k * step, "o": c, "h": c + spread, "l": c - spread, "c": c} for k, c in enumerate(closes)]


def test_bands_use_only_closes_up_to_bar():
    base = list(100 + np.sin(np.arange(60) / 3.0))
    m1, u1, l1 = study.bb_bands(base)
    m2, u2, l2 = study.bb_bands(base + [500.0])          # planted future bar
    assert np.allclose(np.nan_to_num(u1), np.nan_to_num(u2[:60])) and np.allclose(np.nan_to_num(l1), np.nan_to_num(l2[:60]))
    assert np.isnan(u1[18]) and not np.isnan(u1[19])      # needs 20 closes
    # population std (ddof 0), k = 2: a flat series has zero width
    mm, uu, ll = study.bb_bands([5.0] * 25)
    assert uu[-1] == ll[-1] == 5.0


def test_events_first_bar_of_excursion_and_opposite_band_target():
    c = [100.0 + (0.5 if k % 2 else -0.5) for k in range(30)] + [90.0, 89.0, 100.0, 100.0, 100.0, 120.0, 121.0]
    bars = _bars(c)
    ev = study.find_events(bars)
    longs = [e for e in ev if e["side"] == 1]
    shorts = [e for e in ev if e["side"] == -1]
    assert [e["i"] for e in longs] == [30]                # bar 31 is still below the band: not a second event
    assert [e["i"] for e in shorts] == [35]
    _, u, l = study.bb_bands(c)
    assert abs(longs[0]["level"] - l[30]) < 1e-9 and abs(longs[0]["target"] - u[30]) < 1e-9
    assert abs(shorts[0]["level"] - u[35]) < 1e-9 and abs(shorts[0]["target"] - l[35]) < 1e-9


def test_planted_future_bar_changes_no_earlier_event():
    rng = np.random.default_rng(3)
    c = list(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 300))))
    base = study.find_events(_bars(c))
    more = study.find_events(_bars(c + [1.0]))
    assert len(base) >= 5
    assert [e for e in more if e["i"] < 300] == base


def _flat(n, px=100.0):
    return [(px, px + 0.1, px - 0.1, px)] * n


def test_bracket_target_stop_timeout_and_stop_first():
    # long from 100, target 104 -> stop = 100 - 0.5*4 = 98
    o = _flat(30)
    o[5] = (100.0, 104.5, 99.9, 104.0)
    assert abs(study.bracket_trade(o, 2, 100.0, 1, 104.0, 24, 0.5) - 4.0) < 1e-9
    o = _flat(30)
    o[5] = (100.0, 100.5, 97.5, 98.0)
    assert abs(study.bracket_trade(o, 2, 100.0, 1, 104.0, 24, 0.5) - (-2.0)) < 1e-9
    o = _flat(30)
    o[5] = (100.0, 105.0, 97.0, 100.0)                    # both inside one bar: stop first (conservative)
    assert abs(study.bracket_trade(o, 2, 100.0, 1, 104.0, 24, 0.5) - (-2.0)) < 1e-9
    o = _flat(40)
    o[26] = (100.0, 100.1, 99.9, 101.0)                   # timeout at close of bar j+24 = 26
    assert abs(study.bracket_trade(o, 2, 100.0, 1, 104.0, 24, 0.5) - 1.0) < 1e-9
    # short from 100, target 96, stop 102
    o = _flat(30)
    o[4] = (100.0, 100.2, 95.5, 96.0)
    assert abs(study.bracket_trade(o, 2, 100.0, -1, 96.0, 24, 0.5) - 4.0) < 1e-9
    # bars at or before the fill bar are never read: a dip on bar j itself does not stop the trade
    o = _flat(30)
    o[2] = (100.0, 100.0, 50.0, 100.0)
    assert abs(study.bracket_trade(o, 2, 100.0, 1, 104.0, 24, 0.5)) < 1e-9


def test_retest_entry_reads_only_after_signal_bar_and_fills_at_band():
    c = [100.0 + (0.5 if k % 2 else -0.5) for k in range(30)] + [90.0] + [120.0] * 40
    bars = _bars(c, spread=0.2)
    bars[30]["l"] = 10.0                                   # signal bar's own dip must not fill the retest
    ev = [e for e in study.find_events(bars) if e["side"] == 1]
    assert [e["i"] for e in ev] == [30]
    trs, nsig = study.trades_for(ev, bars, "retest")
    assert nsig == 1 and trs == []                         # price never returns to the lower band: no trade
    bars[34]["l"] = ev[0]["level"] - 1.0
    trs, _ = study.trades_for(ev, bars, "retest")
    assert len(trs) == 1 and trs[0]["entry_px"] == min(bars[34]["o"], ev[0]["level"])


def test_regime_gate_keeps_only_range_and_ungated_keeps_all():
    regs = {10: "bull", 11: "bear", 12: "range", 13: None, 14: "range"}
    ev = [{"t_close": d * DAY + 1, "i": d} for d in regs]
    at = lambda t: regs[int(t // DAY)]
    assert [e["i"] for e in study.gate_events(ev, at, "range")] == [12, 14]
    assert [e["i"] for e in study.gate_events(ev, at, "all")] == [10, 11, 12, 13, 14]
    assert [e["i"] for e in study.gate_events(ev, at, "bull")] == [10]


def test_session_is_research_kit_tag_of_signal_close():
    for hh, want in ((2, "asia"), (9, "london"), (15, "ny"), (22, "late")):
        t = 5 * DAY + hh * HOUR
        assert study.session_of_event({"t_close": t}) == rk.session_tag(t / 1000) == want
