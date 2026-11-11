"""Synthetic checks for events.py (card btc-of-map-events-1112). No F: data needed."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import events  # noqa: E402

DAYS = 60
N = DAYS * 1440


def synth(seed=3):
    rng = np.random.default_rng(seed)
    o = 100 + np.cumsum(rng.normal(0, .001, N))
    c = o * 1.005   # every noise bar moves >= 0.1 %, so only injected bars can be A2 events
    v = np.full(N, 10.0)
    tb = 5 + rng.normal(0, .3, N)
    return o, c, v, tb


def inject(o, c, tb, bar5, delta_per_min, move=0.0):
    m = bar5 * 5
    tb[m:m + 5] = 5 + delta_per_min / 2
    c[m + 4] = o[m] * (1 + move)


def test_a2_needs_big_delta_and_small_move():
    o, c, v, tb = synth()
    big = 40 * 288 + 7
    inject(o, c, tb, big, -8.0, move=0.0003)          # top delta, tiny move: event, long (delta < 0)
    inject(o, c, tb, big + 50, 8.0, move=0.002)       # top delta but 0.2 % move: no event
    ev = events.a2_events(o, c, v, tb)
    idx = {e['entry'] for e in ev}
    assert (big + 1) * 5 in idx
    assert (big + 51) * 5 not in idx
    assert [e['side'] for e in ev if e['entry'] == (big + 1) * 5] == [1]


def test_declustering_drops_second_event_within_60_min():
    o, c, v, tb = synth()
    b = 40 * 288 + 7
    inject(o, c, tb, b, 8.0, 0.0001)
    inject(o, c, tb, b + 6, 8.0, 0.0001)      # 30 min later: dropped
    inject(o, c, tb, b + 20, 8.0, 0.0001)     # 100 min after first: kept
    ev = events.a2_events(o, c, v, tb)
    ent = sorted(e['entry'] for e in ev)
    assert (b + 1) * 5 in ent and (b + 7) * 5 not in ent and (b + 21) * 5 in ent


def test_missing_1m_bar_drops_event():
    o, c, v, tb = synth()
    b = 40 * 288 + 7
    inject(o, c, tb, b, 8.0, 0.0001)
    v[b * 5 + 2] = np.nan
    assert (b + 1) * 5 not in {e['entry'] for e in events.a2_events(o, c, v, tb)}


def test_a3_sign_against_payers():
    n = 400
    rate = np.full(n, 0.0001)
    rate[300] = 0.003    # extreme positive -> short
    rate[330] = -0.003   # extreme negative -> long
    ev = events.a3_signals(rate)
    d = dict(ev)
    assert d[300] == -1 and d[330] == 1
    assert min(d) >= 270


def test_a3_needs_270_history():
    rate = np.full(300, 0.0001)
    rate[100] = 0.01
    assert 100 not in dict(events.a3_signals(rate))
    assert all(i >= 270 for i, _ in events.a3_signals(rate))


def test_split_other_than_dev_refused():
    with pytest.raises(SystemExit):
        events.main(['--split', 'validation'])


def test_cost_comes_from_fees_module():
    import fees
    assert abs(events.COST_PCT - 2 * fees.BINANCE_TAKER * 100) < 1e-12


def test_forward_return_net_math():
    o, c, v, tb = synth()
    o[1000] = 100.0
    c[1014] = 101.0                  # h=15 -> bar e+14
    g = events.fwd_gross_pct(o, c, 1000, 15)
    assert abs(g - 1.0) < 1e-9
    assert events.net_pct(g, -1) == pytest.approx(-1.0 - events.COST_PCT)


def test_insufficient_n_label():
    assert events.cell_stats(np.array([0.1] * 10), 180)['label'] == 'INSUFFICIENT_N'
    assert events.cell_stats(np.array([0.1, -0.2] * 100), 180)['label'] == ''
