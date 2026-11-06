"""Fail-first: flow_state_pairs_1m case rules on synthetic bars, plus a spot-check of three cases (first A, B, C)
recomputed from the raw cached 1m klines and 5m OI when the cache is on this machine."""
import glob, json, os, sys
import pytest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flow_state_pairs_1m as fs


def test_cases_on_synthetic_bars():
    thr = 100.0
    assert fs.classify(dict(o=10, c=9, d=-150), 0.001, -50, thr) == 'A'
    assert fs.classify(dict(o=10, c=11, d=150), 0.001, 50, thr) == 'B'
    assert fs.classify(dict(o=10, c=11, d=150), 0.001, -50, thr) is None   # CVD not up: not all-positive
    assert fs.classify(dict(o=10, c=9, d=150), 0.001, 50, thr) is None     # red bar: not all-positive
    assert fs.classify(dict(o=10, c=11, d=150), -0.001, 50, thr) == 'C'
    assert fs.classify(dict(o=10, c=9, d=-150), -0.001, -50, thr) is None
    assert fs.classify(dict(o=10, c=9, d=-50), 0.001, -50, thr) is None    # below burst size
    assert fs.classify(dict(o=10, c=9, d=-150), 0.0002, -50, thr) is None  # OI flat
    assert fs.classify(dict(o=10, c=9, d=-150), None, -50, thr) is None


def test_oi_bucket_and_forward():
    oi = {600: 1000.0, 900: 1002.0}
    assert abs(fs.oi_change(oi, 840) - 0.002) < 1e-12   # bar 840 closes at 900: bucket 600 -> 900
    assert fs.oi_change(oi, 660) is None                # closes at 720: last bucket 300 -> 600, 300 missing
    assert fs.oi_change(oi, 600) is None                # closes at 660: the 600 -> 900 bucket ends after it (look-ahead)
    assert abs(fs.oi_change(oi, 900) - 0.002) < 1e-12   # closes at 960: 600 -> 900 is the last finished bucket
    bars = [dict(t=60 * i, c=100.0 + i) for i in range(20)]
    assert abs(fs.forward(bars, 0, 15) - 0.15) < 1e-12
    gap = bars[:5] + bars[6:]
    assert fs.forward(gap, 0, 15) is None               # missing minute -> no forward value


def test_spot_check_three_cases_against_raw():
    files = glob.glob(fs.CACHE + '/BTCUSDT_v2_*.json')
    if not files:
        pytest.skip('raw cache not on this machine')
    raw = json.load(open(files[0]))
    kl = {int(k[0]) // 1000: k for k in raw['klines']}
    oi = {int(k): v for k, v in raw['oi'].items()}
    bars = [dict(t=k[0] // 1000, o=float(k[1]), c=float(k[4]), d=2 * float(k[9]) - float(k[5])) for k in raw['klines']]
    _, ev = fs.run(bars, oi)
    for case in 'ABC':
        e = next(x for x in ev if x['case'] == case)
        k = kl[e['t']]
        assert abs(e['d'] - (2 * float(k[9]) - float(k[5]))) < 1e-6
        s = (e['t'] + 60) // 300 * 300
        assert abs(e['doi'] - (oi[s] / oi[s - 300] - 1)) < 1e-12
        assert abs(e['fw'][60] - (float(kl[e['t'] + 3600][4]) / float(k[4]) - 1)) < 1e-12
