"""Core rule tests for study.py (synthetic bars, hand-computed expectations)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study as S


def day(n=288, px=100.0):
    o = np.full(n, px); h = np.full(n, px + 0.1); l = np.full(n, px - 0.1); c = np.full(n, px)
    return o, h, l, c


def build():
    o, h, l, c = day()
    # Europe session 07:00-13:30: low 99.0 at slot 100, high 101.0 at slot 120 -> mid 100.0
    l[100] = 99.0
    h[120] = 101.0
    # US: slot 170 sweeps to 98.5 and closes 98.8 (below), slot 172 closes 99.2 (reclaim); entry open of 173 = 99.3
    l[170] = 98.5; c[170] = 98.8; o[170] = 99.1
    l[171] = 98.7; c[171] = 98.9
    c[172] = 99.2; l[172] = 98.9
    o[173] = 99.3
    return o, h, l, c


def test_levels_and_event():
    o, h, l, c = build()
    EL, EH = S.day_levels(h, l, 0)
    assert (EL, EH) == (99.0, 101.0)
    ev = S.find_event("long", o, h, l, c, 0, EL, EH)
    assert ev["i0"] == 170 and ev["j"] == 172 and ev["S"] == 98.5


def test_no_reclaim_within_60min():
    o, h, l, c = build()
    c[172] = 98.0                          # never closes back above 99.0 for 12 bars from slot 170
    c[170:182] = 98.0
    EL, EH = S.day_levels(h, l, 0)
    assert S.find_event("long", o, h, l, c, 0, EL, EH) is None


def test_taker_trade_2r_and_fee():
    o, h, l, c = build()
    EL, EH = S.day_levels(h, l, 0)
    ev = S.find_event("long", o, h, l, c, 0, EL, EH)
    h[180] = 101.0                          # entry 99.3, stop 98.5, risk 0.8, 2R target 100.9 -> hit at slot 180
    R, rpct, tR = S.fwd_trade("long", ev, "2R", "taker", o, h, l, c, 0)
    fee = S.fees.BINANCE_TAKER * 99.3 + S.fees.BINANCE_TAKER * 100.9
    assert abs(R - ((100.9 - 99.3 - fee) / 0.8)) < 1e-9
    assert abs(tR - 2.0) < 1e-9 and abs(rpct - 0.8 / 99.3) < 1e-12


def test_stop_wins_same_bar_tie():
    o, h, l, c = build()
    EL, EH = S.day_levels(h, l, 0)
    ev = S.find_event("long", o, h, l, c, 0, EL, EH)
    h[175] = 101.0; l[175] = 98.4           # both stop (98.5) and target in one bar
    R, _, _ = S.fwd_trade("long", ev, "2R", "taker", o, h, l, c, 0)
    assert R < -1.0                          # stop at -1R plus fees


def test_time_stop_exit_at_last_close():
    o, h, l, c = build()
    EL, EH = S.day_levels(h, l, 0)
    ev = S.find_event("long", o, h, l, c, 0, EL, EH)
    c[239] = 99.8
    R, _, _ = S.fwd_trade("long", ev, "HIGH", "taker", o, h, l, c, 0)
    fee = S.fees.BINANCE_TAKER * 99.3 + S.fees.BINANCE_TAKER * 99.8
    assert abs(R - ((99.8 - 99.3 - fee) / 0.8)) < 1e-9


def test_mid_target_invalid_when_entry_above_mid():
    o, h, l, c = build()
    EL, EH = S.day_levels(h, l, 0)
    ev = S.find_event("long", o, h, l, c, 0, EL, EH)
    o[173] = 100.5                           # entry above mid 100.0 -> MID cell has no trade
    assert S.fwd_trade("long", ev, "MID", "taker", o, h, l, c, 0) is None


def test_maker_fill_needs_trade_through_and_cancels_on_stop():
    o, h, l, c = build()
    EL, EH = S.day_levels(h, l, 0)
    ev = S.find_event("long", o, h, l, c, 0, EL, EH)
    l[174:200] = 99.0                        # touches 99.0 but does not trade through -> no fill
    assert S.fwd_trade("long", ev, "HIGH", "maker", o, h, l, c, 0) is None
    l[176] = 98.9                            # trade-through of 99.0, stop 98.5 not touched -> fills at 99.0
    r = S.fwd_trade("long", ev, "HIGH", "maker", o, h, l, c, 0)
    assert r is not None and abs(r[1] - 0.5 / 99.0) < 1e-12
    l[174] = 98.4                            # stop level touched first -> cancelled
    assert S.fwd_trade("long", ev, "HIGH", "maker", o, h, l, c, 0) is None


def test_short_mirror():
    o, h, l, c = day()
    l[100] = 99.0; h[120] = 101.0
    h[170] = 101.6; c[170] = 101.3; c[171] = 100.9; o[172] = 100.8
    EL, EH = S.day_levels(h, l, 0)
    ev = S.find_event("short", o, h, l, c, 0, EL, EH)
    assert ev["j"] == 171 and ev["S"] == 101.6
    l[180] = 98.0                            # entry 100.8, stop 101.6, risk 0.8, 2R target 99.2
    R, _, tR = S.fwd_trade("short", ev, "2R", "taker", o, h, l, c, 0)
    fee = S.fees.BINANCE_TAKER * 100.8 + S.fees.BINANCE_TAKER * 99.2
    assert abs(R - ((100.8 - 99.2 - fee) / 0.8)) < 1e-9


def test_bh():
    assert S.bh([0.001, 0.2, 0.9, 0.003]) == {0, 3}
    assert S.bh([0.5, 0.6]) == set()
