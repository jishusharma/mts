import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")))
import rules_lib as R

M15 = 15 * R.MIN


def win(rows):
    a = np.array(rows, float)[None, :, :]  # rows of (o,h,l,c)
    return [a[:, :, k] for k in range(4)]


def walk(side, entry, stop, tp, rows, trail=False, cost=0.0):
    O, H, L, C = win(rows)
    r, hold, _ = R.fwd_walk(side, np.array([entry], float), np.array([stop], float), None if tp is None else np.array([tp], float), O, H, L, C, trail, cost)
    return float(r[0]), int(hold[0])


def test_walk_target_stop_gap_time():
    # long, risk 1: target 102 on bar 2
    assert walk(1, 100, 99, 102, [(100, 100.5, 99.5, 100), (100, 101, 99.5, 100.5), (101, 102.5, 100, 102)]) == (2.0, 3)
    # same bar stop and target -> stop first
    assert walk(1, 100, 99, 101, [(100, 103, 98.5, 100)] * 2) == (-1.0, 1)
    # gap through the stop fills at the open (-2R)
    assert walk(1, 100, 99, None, [(100, 100.5, 99.5, 100), (98, 98.5, 97.5, 98)])[0] == -2.0
    # time exit at last close with 1 bp cost = 0.01 R
    r, h = walk(1, 100, 99, None, [(100, 100.4, 99.5, 100.3), (100, 100.4, 99.5, 100.5)], cost=0.0001)
    assert abs(r - 0.49) < 1e-9 and h == 2
    # short mirror, target 98
    assert walk(-1, 100, 101, 98, [(100, 100.5, 99, 99.5), (99, 99.5, 97.5, 98)]) == (2.0, 2)


def test_trail_uses_previous_bar_low_and_only_ratchets():
    rows = [(100, 101, 99.5, 100.8), (100.8, 102, 100.2, 101.9), (101.9, 102.5, 100.5, 101)]
    # bar2 stop = max(99, low0 99.5, low1 100.2) = 100.2 ; bar2 low 100.5 above it -> time exit at close 101
    r, h = walk(1, 100, 99, None, rows, trail=True)
    assert h == 3 and abs(r - 1.0) < 1e-9
    # bar2 low 100.0 <= 100.2 -> stopped at 100.2 = +0.2R
    rows[2] = (101.9, 102.5, 100.0, 101)
    r, h = walk(1, 100, 99, None, rows, trail=True)
    assert h == 3 and abs(r - 0.2) < 1e-9
    # entry bar low counts only from the second bar: entry bar low 98 (below stop 99) stops out in bar 0
    assert walk(1, 100, 99, None, [(100, 101, 98, 100)] * 2, trail=True) == (-1.0, 1)
    # short trail mirrors: stop 101, bar0 high 100.6 -> bar1 stop 100.6, bar1 high 100.7 -> out at 100.6 = -0.6R
    r, h = walk(-1, 100, 101, None, [(100, 100.6, 99.5, 99.8), (99.8, 100.7, 99.7, 100)], trail=True)
    assert h == 2 and abs(r + 0.6) < 1e-9


def make(n=1500, seed=3):
    rng = np.random.default_rng(seed)
    c = 100 + np.cumsum(rng.normal(0, 1, n))
    o = np.r_[c[0], c[:-1]] + rng.normal(0, 0.3, n)
    h = np.maximum(o, c) + rng.random(n)
    l = np.minimum(o, c) - rng.random(n)
    t = (np.arange(n) * M15 + 1700000000000 // M15 * M15).astype(np.int64)
    return t, o, h, l, c


def nk_all(t, o, h, l, c, side=1, window=False):
    rsi = R.wilder_rsi(c)
    sig = R.nk_signals(t, rsi, side, window)
    return R.nk_entries(t, o, h, l, side, sig, M15)


def wrong_lookahead_signals(t, rsi, side, window):
    """Deliberately wrong: judges bar i by the NEXT bar's RSI (one-bar look-ahead)."""
    r2 = np.roll(rsi, -1)
    r2[-1] = np.nan
    return R.nk_signals(t, r2, side, window)


def causal(fn, t, o, h, l, c, cut):
    """Signals computed on data truncated after bar `cut` must equal full-data signals up to cut-1 (a signal at i needs only bars <= i)."""
    full = fn(t, o, h, l, c)
    part = fn(t[:cut + 1], o[:cut + 1], h[:cut + 1], l[:cut + 1], c[:cut + 1])
    return set(int(x) for x in full if x <= cut) == set(int(x) for x in part if x <= cut)


def test_nk_signals_are_causal_and_wrong_version_is_caught():
    t, o, h, l, c = make()
    good = lambda t, o, h, l, c: R.nk_signals(t, R.wilder_rsi(c), 1, False)  # noqa: E731
    bad = lambda t, o, h, l, c: wrong_lookahead_signals(t, R.wilder_rsi(c), 1, False)  # noqa: E731
    ok_all = all(causal(good, t, o, h, l, c, cut) for cut in range(40, 1450, 7))
    bad_all = all(causal(bad, t, o, h, l, c, cut) for cut in range(40, 400))
    assert ok_all and not bad_all


def test_entry_is_next_bar_open_not_signal_close():
    t, o, h, l, c = make()
    e, entry, stop = nk_all(t, o, h, l, c, 1, False)
    sig = R.nk_signals(t, R.wilder_rsi(c), 1, False)
    assert len(e) > 3
    for ee, en in zip(e, entry):
        assert en == o[ee] and ee - 1 in sig
    # signal bar close is NOT the entry price (guards the one-bar look-ahead: entry at close[i])
    assert not np.allclose(entry, c[e - 1])
    assert np.all(stop < entry)


def test_nk_window_first_bar_per_day_and_minutes():
    day0 = 1700000000000 // R.DAY * R.DAY
    t = (day0 + np.arange(192) * M15).astype(np.int64)  # two UTC days
    rsi = np.full(192, 50.0)
    rsi[[38, 39, 40, 134, 135]] = 25.0  # 38 = 09:30, 39 = 09:45, 40 = 10:00 (outside), 134 = day2 09:30... 96+38
    sig = R.nk_signals(t, rsi, 1, True)
    assert sig.tolist() == [38, 134]
    # ALL variant: fresh touch only (39 follows 38, 135 follows 134)
    assert R.nk_signals(t, rsi, 1, False).tolist() == [38, 134]


def test_bollinger_matches_naive():
    t, o, h, l, c = make(120)
    ub = R.bollinger_upper(c)
    for i in (19, 50, 119):
        w = c[i - 19:i + 1]
        assert abs(ub[i] - (w.mean() + 2 * w.std())) < 1e-9
    assert np.isnan(ub[18])


def test_bb_entries_trigger_fill_and_stop():
    n = 40
    t = (np.arange(n) * M15).astype(np.int64)
    c = np.full(n, 100.0) + np.tile([0.0, 0.5], n // 2)
    o, h, l = c.copy(), c + 0.2, c - 0.2
    c[30] = 110.0
    o[30], h[30], l[30] = 100.0, 111.0, 99.0  # breakout candle
    o[31], h[31], l[31], c[31] = 108.0, 109.0, 107.0, 108.0  # no breach
    o[32], h[32], l[32], c[32] = 108.0, 112.0, 107.0, 111.0  # breaches 111 -> fill at max(open 108, 111) = 111
    e, entry, stop = R.bb_entries(t, o, h, l, c, M15)
    assert e.tolist() == [32] and entry[0] == 111.0 and stop[0] == 99.0
    # look-ahead variant (fill at the breakout candle's own high on bar 30) would give idx 30: must differ
    assert 30 not in e.tolist()


def test_fold_weeks_monday_and_mal_third_day():
    mon = (4 + 7 * 2000) * R.DAY  # epoch day 4 is a Monday; 4 + 7k is Monday
    t = np.array([mon - 3 * R.DAY + k * R.DAY for k in range(17)], np.int64)  # starts Friday
    x = np.arange(len(t), dtype=float)
    w = R.fold_weeks(t, x, x + 1, x - 1, x)
    assert len(w["t"]) == 2 and w["t"][0] == mon and w["t"][1] == mon + 7 * R.DAY
    assert (int(w["t"][0]) // R.DAY + 3) % 7 == 0  # Monday
    assert w["c"][0] == 9.0 and w["h"][0] == 10.0 and w["l"][0] == 2.0  # bars 3..9


def test_mal_r05_third_day_target_c_and_colour():
    # 4 weeks, weekly closes: 10, 6, 8, 5 ... craft bearish divergence by a stub divergence_fn
    wk0 = (4 + 7 * 2000) * R.DAY
    wk = dict(t=np.array([wk0 + 7 * k * R.DAY for k in range(6)], np.int64), c=np.array([10, 6, 12, 7, 11, 9], float))
    dt = np.array([wk0 + k * R.DAY for k in range(60)], np.int64)
    do = np.full(60, 100.0)
    dc = do.copy()
    dh, dl = do + 2, do - 2
    # week i = 4 confirms; Wednesday of week 5 = wk0 + 7*4 + 7 + 2 days = day 37
    dc[37] = 99.0  # red
    do[38] = 99.5
    stub = lambda *a, **k: [dict(i=4, a_i=2, b_i=4)]  # noqa: E731
    e, entry, stop, tp = R.mal_r05_entries(dt, do, dh, dl, dc, wk, np.full(6, 50.0), "bearish", 12, stub)
    # point C = lowest weekly close among weeks 2..4 = 7 -> target 7 is below entry 99.5, stop = high of Wed = 102
    assert e.tolist() == [38] and entry[0] == 99.5 and stop[0] == 102.0 and tp[0] == 7.0
    # green Wednesday -> no short
    dc[37] = 101.0
    e, *_ = R.mal_r05_entries(dt, do, dh, dl, dc, wk, np.full(6, 50.0), "bearish", 12, stub)
    assert len(e) == 0
    # wrong-day variant (Tuesday = day 36 as signal) is not what the rule says: ensure Wednesday is day 37 exactly
    assert (dt[37] - wk["t"][4]) == 9 * R.DAY
