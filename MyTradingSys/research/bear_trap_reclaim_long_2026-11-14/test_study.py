"""Hand-built bars; run: python -m pytest test_study.py (or python test_study.py). Red on a one-bar look-ahead entry (ENTRY_OFFSET = 0)."""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study as S  # noqa: E402

D0 = 32  # epoch day 32 is a Monday (epoch day 0 = Thursday; (32+3)//7 = 5 starts a week)
NDAYS = 21


def bars(mod=None):
    n = NDAYS * 24
    t = (D0 * 24 + np.arange(n)) * S.H
    o = np.full(n, 110.0)
    h = np.full(n, 110.5)
    l = np.full(n, 109.5)
    c = np.full(n, 110.0)
    # day 14 (Monday of week 3, index 14*24): carries the prior-day low 100
    i = 14 * 24 + 10
    l[i] = 100.0
    # day 15: sweep at bar 5 (low 99.8 < 100 * 0.999), reclaim at bar 7 (close 101), entry bar 8
    b = 15 * 24
    o[b + 5], h[b + 5], l[b + 5], c[b + 5] = 110.0, 110.0, 99.8, 99.5
    o[b + 6], h[b + 6], l[b + 6], c[b + 6] = 99.5, 99.9, 99.6, 99.7
    o[b + 7], h[b + 7], l[b + 7], c[b + 7] = 99.7, 101.2, 99.6, 101.0
    o[b + 8], h[b + 8], l[b + 8], c[b + 8] = 101.5, 101.8, 101.2, 101.6
    for k in range(9, 24):
        o[b + k], h[b + k], l[b + k], c[b + k] = 101.5, 102.0, 101.0, 101.5
    for k in range(0, 8):  # keep the next day below the weekly highs so no second event appears
        o[b + 24 + k], h[b + 24 + k], l[b + 24 + k], c[b + 24 + k] = 101.5, 102.0, 101.0, 101.5
    if mod:
        mod(t, o, h, l, c, b)
    return t, o, h, l, c, b


def events_for(mod=None):
    t, o, h, l, c, b = bars(mod)
    dt = S.day_tables(t, o, h, l, c)
    wt = S.week_tables(dt)
    return S.find_events(t, o, h, l, c, dt, wt), (t, o, h, l, c, b)


def test_event_entry_is_next_bar_open():
    ev, (t, o, h, l, c, b) = events_for()
    pdl = [e for e in ev if e["lt"] == "PDL" and e["s"] == b + 5]
    assert len(pdl) == 1
    e = pdl[0]
    assert e["r"] == b + 7 and e["e"] == b + 8          # one-bar look-ahead (entry at r) fails here
    assert o[e["e"]] == 101.5
    assert abs(e["slow"] - 99.6) < 1e-9 and abs(e["level"] - 100.0) < 1e-9


def test_sweep_needs_point_one_percent():
    def m(t, o, h, l, c, b):
        l[b + 5] = l[b + 6] = l[b + 7] = 99.95   # only 0.05 % under 100
    ev, _ = events_for(m)
    assert not [e for e in ev if e["lt"] == "PDL" and e["s"] >= 15 * 24]


def test_reclaim_must_come_within_six_bars():
    def m(t, o, h, l, c, b):
        c[b + 7:b + 12] = 99.9   # first close above 100 is bar 12 = s+7
        c[b + 12] = 101.0
    ev, _ = events_for(m)
    assert not [e for e in ev if e["lt"] == "PDL" and e["s"] >= 15 * 24]


def test_simulate_stop_wins_tie_and_gap_fills():
    o = np.full(40, 100.0); h = np.full(40, 100.5); l = np.full(40, 99.5); c = np.full(40, 100.0)
    h[0], l[0] = 103.0, 98.0                       # same bar touches target 102 and stop 99 -> stop
    assert S.simulate(o, h, l, c, 0, 99.0, 102.0) == (99.0, 1)
    o[1], l[1] = 97.0, 96.0                        # gap below stop -> fills at the open
    h2 = h.copy(); h2[0] = 100.5; l2 = l.copy(); l2[0] = 99.5
    assert S.simulate(o, h2, l2, c, 0, 99.0, 102.0) == (97.0, 2)
    h3 = np.full(40, 100.5); l3 = np.full(40, 99.5); o3 = np.full(40, 100.0)
    assert S.simulate(o3, h3, l3, c, 0, 99.0, 150.0) == (100.0, 24)   # time exit at open of bar 24


def test_cost_in_r():
    assert abs(S.trade_r(100.0, 99.0, 100.0) + S.COST * 100.0) < 1e-12      # flat exit, R = 1 price unit
    assert abs(S.trade_r(100.0, 99.0, 102.0) - (2.0 - S.COST * 100.0)) < 1e-12


def test_trend_flag_uses_only_completed_days():
    n = 40
    t = (D0 * 24 + np.arange(n * 24)) * S.H
    px = np.repeat(np.linspace(200, 100, n), 24)           # falling every day
    o = px.copy(); h = px + 1; l = px - 1; c = px.copy()
    dt = S.day_tables(t, o, h, l, c)
    f = S.coin_trend_by_day(dt)
    day = D0 + 30
    assert f[day]
    c2 = c.copy(); c2[(30) * 24:(31) * 24] = 1e6            # change day `day` itself (the flagged day)
    f2 = S.coin_trend_by_day(S.day_tables(t, o, h, l, c2))
    assert f2[day] == f[day]                                # same-day data must not move the flag
    c3 = c.copy(); c3[(29) * 24:(30) * 24] = 1e6            # change the day before -> may change
    f3 = S.coin_trend_by_day(S.day_tables(t, o, h, l, c3))
    assert not f3[day]


def test_btc_red3_week_needs_three_complete_red_weeks():
    n = 6 * 7 * 24
    t = (D0 * 24 + np.arange(n)) * S.H
    px = np.repeat(np.linspace(300, 100, n // 24), 24)
    wt = S.week_tables(S.day_tables(t, px, px + 1, px - 1, px))
    f = S.btc_red3_by_week(wt)
    w0 = (D0 + 3) // 7
    assert not f[w0 + 2] and f[w0 + 3]


if __name__ == "__main__":
    for k, v in list(globals().items()):
        if k.startswith("test_"):
            v()
            print("ok", k)
