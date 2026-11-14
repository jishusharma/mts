"""Wiring tests for bb_range_retest_10sym_2026-11-15: window constants, ten symbols, the OOS window filter on signal closes, and a planted
excursion -> re-entry close -> retest that must produce one long trade filled AFTER the re-entry bar (not at the next open)."""
import calendar
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
_spec = importlib.util.spec_from_file_location("bb10_study", HERE / "study.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)

M15 = 900000


def _ms(y, m, d):
    return calendar.timegm((y, m, d, 0, 0, 0)) * 1000


def _bars(t0, plant_at, n=400):
    """Flat ~100 market with a +-0.2 wiggle; at bar `plant_at` a close of 95 (below the lower band, signal), then a close back at 100
    (re-entry), then a bar whose low reaches the old lower band area (retest), then drift up to the opposite band (target)."""
    bars = []
    for i in range(n):
        c = 100.0 + (0.2 if i % 2 else -0.2)
        o, h, lo = c, c + 0.3, c - 0.3
        if i == plant_at:
            c, lo, h = 95.0, 94.5, 100.2
        elif i == plant_at + 1:
            c, h, lo = 100.0, 100.5, 94.8
        elif i == plant_at + 2:
            o, c, h, lo = 100.0, 100.0, 100.3, 98.0
        elif plant_at + 3 <= i <= plant_at + 8:
            o, c, h, lo = 100.5, 101.5, 102.5, 100.4
        bars.append({"t": t0 + i * M15, "o": o, "h": h, "l": lo, "c": c})
    return bars


def _run(t0, plant_at):
    bars = _bars(t0, plant_at)
    study.load = lambda sym, iv: bars
    out, inwin, gaps, nb = study.symbol_trades("BTC", lambda t: "range", study.OOS_START, study.OOS_END)
    return out, inwin


def test_constants_are_the_stated_dates_and_ten_symbols():
    assert study.OOS_START == _ms(2024, 1, 1) and study.SPLIT_MS == _ms(2025, 7, 1) and study.OOS_END == _ms(2026, 11, 15)
    assert len(study.SYMS) == 10 and len(set(study.SYMS)) == 10 and study.K_GRID == (0.25, 0.5, 1.0)


def test_signal_before_oos_start_makes_no_trade_after_start_makes_trade():
    out_pre, ev_pre = _run(_ms(2023, 11, 1), 40)          # signal near 2023-11-01: outside the window
    assert ev_pre == [] and all(len(v) == 0 for v in out_pre.values())
    out_in, ev_in = _run(_ms(2024, 3, 1), 40)             # same shape inside the window
    assert len(ev_in) >= 1 and any(len(v) >= 1 for v in out_in.values())


def test_fill_is_after_reentry_bar_not_next_open():
    t0 = _ms(2024, 3, 1)
    out, _ = _run(t0, 40)
    trs = [x for x in out[1.0] if x["side"] == 1]
    assert trs, "planted retest must fill at k=1.0"
    reentry_open = t0 + 41 * M15
    assert all(x["t"] > reentry_open for x in trs)         # fill bar is strictly after the re-entry bar (bar 41)
