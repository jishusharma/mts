"""Tests for prints.py (card btc-of-map-prints-1112). Synthetic data only."""
import datetime as dt
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prints as P  # noqa: E402

D0 = dt.date(2022, 1, 1)


def synth_reduced(day, rng, big=None, regular_prints=True):
    """20,000 trades of qty 0.01; regular_prints adds 30 prints of qty 1.0 (0.15 %) at random bins/sides so the 99.9th pct = 1.0.
    big = (bin, side, qty) adds one large print."""
    n = 20000
    t0 = int(np.datetime64(day.isoformat() + 'T00:00', 'ms').astype('int64'))
    ts = t0 + rng.integers(0, 86400000, n)
    qty = np.full(n, 0.01)
    ibm = rng.random(n) < 0.5
    if regular_prints:
        ts = np.append(ts, t0 + rng.integers(0, 86400000, 30))
        qty = np.append(qty, np.full(30, 1.0))
        ibm = np.append(ibm, rng.random(30) < 0.5)
    if big:
        b, side, q = big
        ts = np.append(ts, t0 + b * 300000 + 1000)
        qty = np.append(qty, q)
        ibm = np.append(ibm, side < 0)
    return P.reduce_day(ts, qty, ibm, day)


def build(n_days, big_day=None, big=None, seed=1):
    """Every day has regular prints except the event day (no prints of its own, only the optional big one)."""
    rng = np.random.default_rng(seed)
    red = {}
    for k in range(n_days):
        d = D0 + dt.timedelta(days=k)
        red[d] = synth_reduced(d, rng, big if d == big_day else None, regular_prints=(k != 38))
    return red


def flat_grid(n_days, jump_bar=None, jump_bp=30):
    n = n_days * 1440
    o = np.full(n, 100.0)
    c = np.full(n, 100.0)
    if jump_bar is not None:
        e = (jump_bar + 1) * 5  # entry minute = right after the 5m bar
        o[e:] = 100.0 * (1 + jump_bp / 1e4)
        c[e:] = 100.0 * (1 + jump_bp / 1e4)
        o[e] = 100.0
    return o, c


def test_a1_flags_exactly_the_print_bar_and_forward_return():
    nd = 40
    big_day = D0 + dt.timedelta(days=38)
    red = build(nd, big_day, (100, 1, 50.0))
    ev, trunc, dropped = P.a1_events_from_reduced(red, [big_day])
    g = (big_day - D0).days * 288 + 100
    assert ev == [(g, 1)] and not dropped
    o, c = flat_grid(nd, jump_bar=g, jump_bp=30)
    gross = P.gross_arrays(o, c)
    acc = P.accept(ev, gross)
    assert acc == [(g, 1)]
    assert abs(gross[0, g] - 30) < 1e-6 and abs(gross[1, g] - 30) < 1e-6
    net = 1 * gross[1, g] - P.FEE_BP
    assert abs(net - 20) < 1e-6


def test_a1_day_without_prints_flags_none():
    red = build(40)
    ev, _, dropped = P.a1_events_from_reduced(red, [D0 + dt.timedelta(days=38)])
    assert ev == [] and not dropped


def test_a1_dropped_when_warmup_missing():
    red = build(40)
    del red[D0 + dt.timedelta(days=20)]
    ev, _, dropped = P.a1_events_from_reduced(red, [D0 + dt.timedelta(days=38)])
    assert dropped == [D0 + dt.timedelta(days=38)]


def a2_inputs(d5_today_val, mv_today_val):
    rng = np.random.default_rng(3)
    prev = rng.normal(0, 10, 8640)
    today = np.zeros(288)
    today[50] = d5_today_val
    mv = np.full(288, 0.0002)
    mv[50] = mv_today_val
    return prev, today, mv


def test_a2_needs_delta_tail_and_small_move():
    prev, today, mv = a2_inputs(-500.0, 0.0005)
    assert list(np.nonzero(P.a2_day_events(prev, today, mv))[0]) == [50]
    prev, today, mv = a2_inputs(-500.0, 0.002)  # tail but moved 0.2 %
    assert not P.a2_day_events(prev, today, mv).any()
    prev, today, mv = a2_inputs(5.0, 0.0005)  # small move but delta inside the body
    assert not P.a2_day_events(prev, today, mv).any()


def test_a2_sign_is_against_delta():
    nb = 40 * 288
    d5 = np.zeros(nb)
    d5[39 * 288 + 7] = 900.0
    rng = np.random.default_rng(2)
    d5[:39 * 288] = rng.normal(0, 10, 39 * 288)
    mv = np.full(nb, 0.0001)
    ev = P.a2_events(d5, mv, [D0 + dt.timedelta(days=39)])
    assert ev == [(39 * 288 + 7, -1)]  # buy delta absorbed -> short


def test_decluster_60_min():
    assert P.decluster([0, 5, 11, 12, 30]) == [0, 12, 30]


def test_dev_guard_refuses_validation_day(tmp_path):
    f = tmp_path / 'd.txt'
    f.write_text('2024-07-02 0 event\n')
    try:
        P.main(['--days', str(f), '--analyze-only'])
        assert False
    except SystemExit as e:
        assert 'outside DEV' in str(e)


def test_day_plan_shape():
    plan = P.day_plan()
    assert sum(1 for *_, r in plan if r == 'event') == 60 and sum(1 for *_, r in plan if r == 'warmup') == 6 * 37
    ev = [d for d, _, r in plan if r == 'event']
    assert min(ev) >= P.DEV_START and max(ev) <= P.DEV_END
