"""Tests for phase_label.py (PHASE_LABEL: cycle phase x weekly RSI zone, closed bars only). Hand-built daily bars."""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phase_label as pl  # noqa: E402

DAY = 86_400_000


def ms(y, m, d):
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp() * 1000)


def mk_daily(start, closes, highs=None, lows=None):
    """daily bars (t_open_ms, high, low, close)."""
    out = []
    for k, c in enumerate(closes):
        h = highs[k] if highs else c
        lo = lows[k] if lows else c
        out.append((start + k * DAY, float(h), float(lo), float(c)))
    return out


HALV = [ms(2020, 1, 1), ms(2024, 1, 1)]


def test_zone_lines():
    assert pl.zone_of(60.01) == "HIGH"
    assert pl.zone_of(60.0) == "MID"
    assert pl.zone_of(40.0) == "MID"
    assert pl.zone_of(39.99) == "LOW"
    assert pl.zone_of(None) is None


def test_bull_then_peak_window_by_clock():
    start = HALV[0]
    closes = [100 + k for k in range(560)]  # rises every day: no peak known
    d = mk_daily(start, closes)
    assert pl.cycle_phase(start + 10 * DAY, d, HALV) == "BULL"
    assert pl.cycle_phase(start + 371 * DAY, d, HALV) == "BULL"
    assert pl.cycle_phase(start + 372 * DAY, d, HALV) == "PEAK_WINDOW"
    assert pl.cycle_phase(start + 548 * DAY, d, HALV) == "PEAK_WINDOW"
    # after 548 d the clock says the peak is behind: post-peak with the provisional peak = yesterday's high
    assert pl.cycle_phase(start + 549 * DAY, d, HALV) == "BEAR"


def test_peak_known_only_after_363_days_and_bottom_window():
    start = HALV[0]
    # up to day 100 (peak 300 at day 100), then down slowly forever
    closes = [200 + k for k in range(101)] + [300 - 0.1 * k for k in range(1, 700)]
    d = mk_daily(start, closes)
    peak_day = start + 100 * DAY
    # day 462 = peak + 362: peak not yet known, dH < 548 -> PEAK_WINDOW by clock
    assert pl.cycle_phase(peak_day + 362 * DAY + DAY // 2, d, HALV) == "PEAK_WINDOW"
    assert not pl.peak_known(peak_day + 363 * DAY - 1, d, HALV)
    # peak + 363: known -> bottom window
    assert pl.peak_known(peak_day + 363 * DAY, d, HALV)
    assert pl.cycle_phase(peak_day + 363 * DAY, d, HALV) == "BOTTOM_WINDOW"
    assert pl.cycle_phase(peak_day + 406 * DAY, d, HALV) == "BOTTOM_WINDOW"
    assert pl.cycle_phase(peak_day + 407 * DAY, d, HALV) == "TRANSITION"


def test_bottom_known_after_100pct_rally_then_accumulation_until_halving():
    start = HALV[0]
    # peak day 400 (500), down to 100 at day 800, then rally to 250 by day 875, flat
    closes = [100 + k for k in range(401)]                         # 0..400 -> 500 at day 400
    closes += [500 - k for k in range(1, 401)]                    # day 401..800 -> 100
    closes += [100 + 2 * k for k in range(1, 76)]                 # day 801..875 -> 250
    closes += [250] * (1461 - len(closes) + 20)
    d = mk_daily(start, closes)
    # close >= 200 first at day 850 (100 + 2*50); usable from day 851 (day 850 closes at 851 00:00)
    assert pl.cycle_phase(start + 850 * DAY, d, HALV) != "ACCUMULATION"
    assert pl.cycle_phase(start + 851 * DAY, d, HALV) == "ACCUMULATION"
    assert pl.cycle_phase(HALV[1] - DAY, d, HALV) == "ACCUMULATION"
    assert pl.cycle_phase(HALV[1], d, HALV) == "BULL"


def test_no_lookahead_future_bars_do_not_change_label():
    start = HALV[0]
    closes = [200 + k for k in range(101)] + [300 - 0.1 * k for k in range(1, 700)]
    d = mk_daily(start, closes)
    t = start + 500 * DAY + 3_600_000
    full = pl.cycle_phase(t, d, HALV)
    cut = [b for b in d if b[0] + DAY <= t]
    assert pl.cycle_phase(t, cut, HALV) == full
    # a crash after t cannot change the label at t
    d2 = [b if b[0] + DAY <= t else (b[0], 1.0, 1.0, 1.0) for b in d]
    assert pl.cycle_phase(t, d2, HALV) == full


def test_incremental_series_equals_reference():
    start = HALV[0] - 200 * DAY
    import math
    closes = [1000 + 600 * math.sin(k / 150.0) + 3 * k for k in range(1900)]
    d = mk_daily(start, closes, [c * 1.01 for c in closes], [c * 0.99 for c in closes])
    hv = [HALV[0] - 1461 * DAY] + HALV
    lab = pl.PhaseLabeler(d, hv)
    seen = set()
    for k in range(0, 1900, 7):
        t = start + k * DAY + 5 * 3_600_000
        ph = pl.cycle_phase(t, d, hv)
        seen.add(ph)
        assert lab.phase(t) == ph, k
    assert len(seen) >= 3, seen


def test_weekly_rsi_only_after_week_close():
    # Monday 2024-01-01
    start = ms(2024, 1, 1)
    closes = [100 + (k % 7) + (k // 7) for k in range(7 * 30)]
    d = mk_daily(start, closes)
    wt, wr = pl.weekly_rsi(d)
    assert wt[0] == start + 7 * DAY  # usable time = week close
    lab = pl.PhaseLabeler(d, HALV)
    w16_close = start + 16 * 7 * DAY
    i = wt.index(w16_close)
    assert lab.weekly_rsi_at(w16_close) == wr[i]
    assert lab.weekly_rsi_at(w16_close - 1) == wr[i - 1]


def test_phase_label_returns_pair():
    start = HALV[0]
    d = mk_daily(start, [100 + k for k in range(200)])
    lab = pl.PhaseLabeler(d, HALV)
    ph, z = lab.label(start + 150 * DAY)
    assert ph == "BULL" and z == "HIGH"
    assert lab.label(start + 3 * DAY)[1] is None  # RSI warm-up


def test_real_halvings_and_turns_sourced():
    assert pl.HALVINGS[1:4] == [ms(2016, 7, 9), ms(2020, 5, 11), ms(2024, 4, 20)]
    assert (pl.PEAK_WIN_LO, pl.PEAK_WIN_HI, pl.BOTTOM_WIN_LO, pl.BOTTOM_WIN_HI) == (372, 548, 363, 406)
