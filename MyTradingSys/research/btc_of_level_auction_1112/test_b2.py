"""Synthetic checks for b2.py (card btc-of-level-auction-b2-fetch-run-1112). No D: or F: data needed.
Expected numbers are computed here by hand / plain numpy, not by calling b2 helpers.
B2_DIR env var points the import at a mutated copy of b2.py (used once to show the tests fail on a wrong implementation)."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'btc_orderflow_map_1112'))
sys.path.insert(0, os.environ.get('B2_DIR', HERE))
import b2  # noqa: E402

NB = 3840                       # 40 days of 15m bars
K = 3000                        # injection bar
BASE_TOPV = 1.0


def grid():
    """Quiet baseline: highs strictly falling and lows strictly rising, so no baseline bar is a 24h extreme."""
    k = np.arange(NB, dtype=float)
    hi, lo = 100 - 1e-4 * k, 90 + 1e-4 * k
    tb, ts = np.full(NB, .5), np.full(NB, .5)
    bb, bs = np.full(NB, .5), np.full(NB, .5)
    n1 = NB * 15
    o1 = np.full(n1, 95.0)
    return hi, lo, tb, ts, bb, bs, o1, o1.copy(), np.full(n1, 10.0), np.full(n1, 5.0)


def run(hi, lo, tb, ts, bb, bs, o1, c1, v1, t1, start=0):
    return b2.b2_events(hi, lo, tb, ts, bb, bs, o1, c1, v1, t1, start_bar=start)


def test_bucket_assignment_by_hand():
    # open 100 -> w = 0.01, buckets floor(p / 0.01). High 100.507 is bucket 10050 (100.50..100.51); 100.502 shares it; 100.512 does not.
    price = np.array([100.0, 100.502, 100.507, 100.512, 99.0])
    buy = np.array([1.0, 2.0, 4.0, 8.0, 16.0])
    sell = np.array([0.0, 1.0, 3.0, 5.0, 7.0])
    r = b2.bar_row(7, 100.0, 100.507, 99.0, 99.0, price, buy, sell)
    assert r[5] == 2 + 4 and r[6] == 1 + 3          # top bucket buy / sell
    assert r[7] == 16 and r[8] == 7                 # bottom bucket (99.0 alone)
    assert r[9] == 1 + 2 + 4 + 8 + 16 + 1 + 3 + 5 + 7


def test_reducer_chunking_and_aggressor():
    # buyer_aggr True = taker buy. Bar 0 = ts < 900000. Same result in one chunk or one trade per chunk.
    p = np.array([100.0, 100.5, 100.5, 99.0, 100.2])
    q = np.array([1.0, 2.0, 3.0, 1.0, 1.0])
    t = np.array([0, 1000, 2000, 3000, 900000])
    ag = np.array([True, False, True, False, True])
    outs = []
    for step in (5, 1):
        red, rows = b2.Reducer(), []
        for i in range(0, 5, step):
            rows += red.feed(p[i:i + step], q[i:i + step], t[i:i + step], ag[i:i + step])
        rows += red.finish()
        outs.append(rows)
    assert outs[0] == outs[1]
    b0 = outs[0][0]
    assert b0[1:5] == [100.0, 100.5, 99.0, 99.0]      # open high low close
    assert b0[5] == 3.0 and b0[6] == 2.0              # top bucket: taker buy 3, taker sell 2
    assert b0[7] == 0.0 and b0[8] == 1.0              # bottom bucket: only a taker sell of 1


def inj_high(a, vb=5.0, vs=5.0, hi=200.0):
    a[0][K], a[2][K], a[3][K] = hi, vb, vs


def test_high_event_short_and_entry():
    a = grid()
    inj_high(a)
    ev = run(*a)
    assert len(ev) == 1 and ev[0]['side'] == -1 and ev[0]['entry'] == (K + 1) * 15 and ev[0]['ext'] == 200.0


def test_both_aggressors_required():
    for vb, vs in ((5.0, 0.0), (0.0, 5.0)):
        a = grid()
        inj_high(a, vb, vs)
        assert run(*a) == []


def test_low_event_long():
    a = grid()
    a[1][K], a[4][K], a[5][K] = 10.0, 5.0, 5.0
    ev = run(*a)
    assert len(ev) == 1 and ev[0]['side'] == 1 and ev[0]['ext'] == 10.0


def test_bar_both_high_and_low_event_dropped():
    a = grid()
    inj_high(a)
    a[1][K], a[4][K], a[5][K] = 10.0, 5.0, 5.0
    assert run(*a) == []


def test_percentile_95_over_previous_30_days_only():
    a = grid()
    topv = np.full(NB, BASE_TOPV)
    topv[K - 2880:K:10] = 5.0                        # 288 of 2880 previous bars (10 %) hold 5.0 -> 95th pct of the window = 5.0
    a[2][:] = topv / 2
    a[3][:] = topv / 2
    assert np.percentile(topv[K - 2880:K], 95) == 5.0
    spike = K + 5                                    # a future spike must not move the threshold at K
    a[2][spike], a[3][spike] = 500.0, 500.0
    inj_high(a, 2.45, 2.45)                          # topv 4.9 < 5.0: no event
    assert [e for e in run(*a) if e['bar'] == K] == []
    inj_high(a, 2.5, 2.5)                            # topv 5.0 >= 5.0: event
    assert [e['bar'] for e in run(*a) if e['bar'] == K] == [K]
    # an old spike outside the 30-day window must not count: put 10 % of bars at 5.0 only BEFORE K-2880
    b = grid()
    t2 = np.full(NB, BASE_TOPV)
    t2[K - 2880 - 400:K - 2880:3] = 50.0
    b[2][:] = t2 / 2
    b[3][:] = t2 / 2
    inj_high(b, 1.0, 1.0)                            # topv 2 >= 95th pct of the window (= 1.0): event
    assert [e['bar'] for e in run(*b) if e['bar'] == K] == [K]


def test_missing_data_drops():
    a = grid()
    inj_high(a)
    a[0][K - 10] = np.nan                            # one missing bar inside the 96-bar lookback
    assert run(*a) == []
    a = grid()
    inj_high(a)
    a[6][(K + 1) * 15 + 30] = np.nan                 # a missing 1m open inside the 60 min after entry
    assert run(*a) == []
    a = grid()
    inj_high(a)
    a[6][K * 15 + 3] = np.nan                        # missing 1m bar inside the event bar
    assert run(*a) == []


def test_not_a_24h_high_is_no_event():
    a = grid()
    inj_high(a, hi=99.0)                             # 99.0 < max of previous 96 highs (about 99.7)
    assert run(*a) == []


def test_decluster_60_minutes():
    a = grid()
    for k in (K, K + 2, K + 4):                      # 30 min and 60 min after the first accepted one
        a[0][k], a[2][k], a[3][k] = 200.0 + k, 5.0, 5.0
    assert [e['bar'] for e in run(*a)] == [K, K + 4]


def test_revisit():
    h = np.full(3000, 100.0)
    l = np.full(3000, 90.0)
    assert b2.revisit(h, l, 10, -1, 100.0) is True
    assert b2.revisit(h, l, 10, -1, 100.5) is False
    assert b2.revisit(h, l, 10, 1, 90.0) is True
    assert b2.revisit(h, l, 10, 1, 89.5) is False
    assert b2.revisit(h, l, 2000, -1, 100.0) is None  # window runs past the data


def test_dev_only_loader_rejects_other_months():
    assert b2.month_ok('2022-01') and b2.month_ok('2024-05')
    assert not b2.month_ok('2024-06') and not b2.month_ok('2025-01') and not b2.month_ok('2021-12')
