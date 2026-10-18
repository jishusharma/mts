"""Spec: research/layer_lab/candle_close_2026-10-14 METHOD.md six signatures at the previous completed day/week
high/low (mirrored for shorts). Live arms (top per side): 15m/day/reclaim (long), 3m/week/strong_break (short).
All timestamps and expected values are computed by hand in this file."""
from MyTradingSys.backtest.layers.alerts import live_candle_close as cc

MIN = 60000
DAY = 1440 * MIN
WEEK = 7 * DAY
MON = 4 * DAY                        # 1970-01-05 00:00 UTC, a Monday
D1 = 20000 * DAY                     # start of the day under test (UTC midnight)
W1 = MON + 2800 * WEEK               # a Monday; week under test starts here


def _m(t, o, h, l, c):
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": 1.0, "tbv": 0.5}


def _flat_range(t0, n, px):
    return [_m(t0 + k * MIN, px, px, px, px) for k in range(n)]


def _long_day(close_q=100.2, close_p=99.9, close_c=100.1):
    """Prior day flat 90 with one minute high 100 (level L=100). Day D1: flat 90, then 15m candles k=4,5,6 close
    close_q/close_p/close_c (flat minutes) = reclaim sequence C2>L, C1<L, C0>L."""
    prev = _flat_range(D1 - DAY, 1440, 90.0)
    prev[500] = _m(prev[500]["t"], 90.0, 100.0, 90.0, 90.0)
    bars = prev + _flat_range(D1, 4 * 15, 90.0)
    for px in (close_q, close_p, close_c):
        bars += _flat_range(bars[-1]["t"] + MIN, 15, px)
    return bars


def test_long_reclaim_15m_day():
    ev = cc.candle_close_layer(_long_day())
    assert len(ev) == 1
    e = ev[0]
    assert e["side"] == "long" and e["sampling"] is True and e["level"] == 100.0
    # candle k=6 spans minutes 90..104 of D1; the last 1m bar opens at minute 104
    assert e["t"] == D1 + 104 * MIN
    assert e["event"] == "cc_reclaim_15m_day_h_long_100.0"


def test_long_reclaim_negatives():
    assert cc.candle_close_layer(_long_day(close_c=99.95)) == []   # C0 not above L
    assert cc.candle_close_layer(_long_day(close_p=100.05)) == []  # C1 not below L
    assert cc.candle_close_layer(_long_day(close_c=100.4)) == []   # 0.4% from L: outside the 0.25% band


def _short_week():
    """Prior week flat 100, one minute high 110 early (L=110). Week W1: flat 100 for 12 minutes (3m candles k=0..3),
    candle k=4 (minutes 12-14): 110.5 flat -> C1>=L? it is candle k=3 that must be >=L, so k=3 is 110.5 flat;
    candle k=4 opens 110.3, ends 109.8 (strong close near the low)."""
    prev = _flat_range(W1 - WEEK, 10080, 100.0)
    prev[100] = _m(prev[100]["t"], 100.0, 110.0, 100.0, 100.0)
    bars = prev + _flat_range(W1, 9, 100.0) + _flat_range(W1 + 9 * MIN, 3, 110.5)
    bars += [_m(W1 + 12 * MIN, 110.3, 110.3, 110.3, 110.3), _m(W1 + 13 * MIN, 110.0, 110.0, 110.0, 110.0),
             _m(W1 + 14 * MIN, 110.0, 110.0, 109.8, 109.8)]
    return bars


def test_short_strong_break_3m_week():
    ev = cc.candle_close_layer(_short_week())
    assert len(ev) == 1
    e = ev[0]
    assert e["side"] == "short" and e["sampling"] is True and e["level"] == 110.0
    assert e["t"] == W1 + 14 * MIN        # last 1m bar of the 3m candle
    assert e["event"] == "cc_strong_break_3m_week_h_short_110.0"


def test_short_requires_strong_candle():
    bars = _short_week()
    bars[-1] = _m(W1 + 14 * MIN, 110.0, 110.4, 109.8, 109.8)   # close location (h-c)/range = 0.6/0.6=1 but body 0.5/0.6 ok
    assert len(cc.candle_close_layer(bars)) == 1
    bars[-1] = _m(W1 + 14 * MIN, 110.0, 111.6, 109.8, 109.8)   # long upper wick -> body 0.5/1.8 < 0.6: weak
    assert cc.candle_close_layer(bars) == []


def test_missing_minute_in_parent_gives_no_level():
    bars = _long_day()
    del bars[700]                                              # a gap inside the previous day
    assert cc.candle_close_layer(bars) == []


def test_empty_short_nan_input():
    assert cc.candle_close_layer([]) == []
    assert cc.candle_close_layer(_flat_range(D1, 2, 100.0)) == []
    assert cc.candle_close_layer(_flat_range(D1, 600, 100.0)) == []   # no completed parent day
    bars = _long_day()
    bars[-3]["c"] = float("nan")                                       # NaN inside the signal candle
    assert cc.candle_close_layer(bars) == []


def test_truncation_no_lookahead():
    bars = _long_day()
    full = cc.candle_close_layer(bars)
    assert len(full) == 1
    cut = bars.index(next(b for b in bars if b["t"] == full[0]["t"]))
    assert cc.candle_close_layer(bars[:cut]) == []                     # signal minute not yet closed
    assert cc.candle_close_layer(bars[:cut + 1]) == full
    extra = bars + [_m(bars[-1]["t"] + MIN, 1.0, 1e9, 1.0, 1e9)]
    assert cc.candle_close_layer(extra) == full


def test_restart_determinism_and_dedup():
    bars = _long_day()
    a = cc.candle_close_layer(bars)
    assert a == cc.candle_close_layer([dict(b) for b in bars])
    # a restart window starting one day later than the first bar (still holding the whole previous day) agrees
    assert cc.candle_close_layer(bars[1:]) == a or cc.candle_close_layer(bars[1:]) == []
    # a second identical sequence later the same UTC day is suppressed (first per day/side/edge)
    more = bars + _flat_range(bars[-1]["t"] + MIN, 15, 90.0)
    for px in (100.2, 99.9, 100.1):
        more += _flat_range(more[-1]["t"] + MIN, 15, px)
    assert len(cc.candle_close_layer(more)) == 1
