"""Synthetic checks for b1.py (card btc-of-level-auction-b1-run-1112). No F: data needed."""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'btc_orderflow_map_1112'))
import b1  # noqa: E402

DAYS = 60
N = DAYS * 1440
D = 45  # injection day


def synth(seed=3):
    rng = np.random.default_rng(seed)
    o = 100 + np.cumsum(rng.normal(0, .001, N))
    c = o * 1.005            # body 0.5 %: noise bars are never B1 events
    h = np.maximum(o, c) * 1.0001
    l = np.minimum(o, c) * 0.9999
    v = np.full(N, 10.0)
    tb = 5 + rng.normal(0, .3, N)
    return o, h, l, c, v, tb


def levels(o, h, l, c, v, day=D):
    tp = (h + l + c) / 3
    return b1.day_levels(h, l, c, tp, v, day)


def inject(o, h, l, c, tb, bar5, price, delta_per_min, low_off=0.0, high_off=0.0):
    """Flat 5m bar at `price` (body 0.02 %) with the given delta; low/high pushed `off` away from price."""
    m = bar5 * 5
    o[m:m + 5] = price
    c[m:m + 5] = price * 1.0001
    h[m:m + 5] = price * (1.0002 + high_off)
    l[m:m + 5] = price * (0.9999 - low_off)
    tb[m:m + 5] = 5 + delta_per_min / 2


def run(o, h, l, c, v, tb):
    return b1.b1_events(o, h, l, c, v, tb, start_bar5=40 * 288)


def test_value_area_hand_example():
    # w = 0.05 % of 100 = 0.05. Volume by bucket (low->high): 1,2,10,3,2,1 -> total 19, POC idx 2.
    # up pair (3+2=5) vs down pair (2+1=3): add up -> 15 < 13.3? 10+5=15 >= 0.7*19=13.3 stop.
    # area = buckets 2..4 -> VAL = lo+2w, VAH = lo+5w.
    w, lo = 0.05, 99.0
    vols = [1, 2, 10, 3, 2, 1]
    tp = np.array([lo + (i + .5) * w for i in range(6)])
    val, vah = b1.value_area(tp, np.array(vols, float), 100.0)
    assert abs(val - (lo + 2 * w)) < 1e-9 and abs(vah - (lo + 5 * w)) < 1e-9


def test_pdl_long_event_and_delta_at_high_not_event():
    o, h, l, c, v, tb = synth()
    lv = levels(o, h, l, c, v)
    pdl, pdh = lv['PDL'], lv['PDH']
    k_low = D * 288 + 40
    k_hi = D * 288 + 100
    inject(o, h, l, c, tb, k_low, pdl * 1.0005, -8.0)         # delta<0, low within 0.10 % of PDL: long event
    inject(o, h, l, c, tb, k_hi, pdh * 0.9995, -8.0)          # delta<0 at a HIGH: not an at-level event
    ev = run(o, h, l, c, v, tb)
    at = {e['entry']: e['side'] for e in ev['at']}
    assert at.get((k_low + 1) * 5) == 1
    assert (k_hi + 1) * 5 not in at
    assert (k_hi + 1) * 5 in {e['entry'] for e in ev['away']}  # same flow thresholds, not at a matching level


def test_delta_positive_at_high_is_short_and_at_low_is_not_event():
    o, h, l, c, v, tb = synth()
    lv = levels(o, h, l, c, v)
    k1, k2 = D * 288 + 40, D * 288 + 100
    inject(o, h, l, c, tb, k1, lv['PDH'] * 0.9995, 8.0)       # delta>0 at PDH: short
    inject(o, h, l, c, tb, k2, lv['PDL'] * 1.0005, 8.0)       # delta>0 at PDL: not an event
    ev = run(o, h, l, c, v, tb)
    at = {e['entry']: e['side'] for e in ev['at']}
    assert at.get((k1 + 1) * 5) == -1
    assert (k2 + 1) * 5 not in at


def test_touch_band_is_ten_bp():
    o, h, l, c, v, tb = synth()
    lv = levels(o, h, l, c, v)
    k1, k2 = D * 288 + 40, D * 288 + 100
    inject(o, h, l, c, tb, k1, lv['PDL'] * 1.0004, -8.0, low_off=0.0)                   # low = PDL*(1.0003): inside
    inject(o, h, l, c, tb, k2, lv['PDL'] * 1.0030, -8.0, low_off=0.0)                   # low ~0.3 % above: outside
    ev = run(o, h, l, c, v, tb)
    at = {e['entry'] for e in ev['at']}
    assert (k1 + 1) * 5 in at and (k2 + 1) * 5 not in at


def test_big_body_is_not_event():
    o, h, l, c, v, tb = synth()
    lv = levels(o, h, l, c, v)
    k = D * 288 + 40
    inject(o, h, l, c, tb, k, lv['PDL'] * 1.0005, -8.0)
    c[k * 5 + 4] = o[k * 5] * 1.003                            # body 0.3 % > 0.15 %
    ev = run(o, h, l, c, v, tb)
    assert (k + 1) * 5 not in {e['entry'] for e in ev['at'] + ev['away']}


def test_levels_are_point_in_time():
    o, h, l, c, v, tb = synth()
    a = levels(o, h, l, c, v)
    h2, l2, c2, v2 = h.copy(), l.copy(), c.copy(), v.copy()
    s = D * 1440
    h2[s:s + 1440] *= 1.5
    l2[s:s + 1440] *= 0.5
    v2[s:s + 1440] *= 7
    assert a == levels(o, h2, l2, c2, v2)                      # day D bars never change day D levels
    h2[s - 1440:s] *= 1.01
    assert levels(o, h2, l2, c2, v2)['PDH'] != a['PDH']        # day D-1 does


def test_declustering_60_min_per_set():
    o, h, l, c, v, tb = synth()
    lv = levels(o, h, l, c, v)
    b = D * 288 + 40
    for k in (b, b + 6, b + 20):
        inject(o, h, l, c, tb, k, lv['PDL'] * 1.0005, -8.0)
    ent = sorted(e['entry'] for e in run(o, h, l, c, v, tb)['at'])
    assert (b + 1) * 5 in ent and (b + 7) * 5 not in ent and (b + 21) * 5 in ent
