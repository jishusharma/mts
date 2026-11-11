"""Synthetic 1m series, taker delta injected only at 08:00Z: the top hour bucket must be 08Z and the shuffled-label placebo must not.
Written before clocks.py existed (fails with ImportError there)."""
import numpy as np

import clocks


def synth(days=60, seed=0):
    rng = np.random.default_rng(seed)
    t = clocks.DEV_START_MS + np.arange(days * 1440, dtype=np.int64) * 60000
    hour = (t // 3600000) % 24
    vol = np.full(len(t), 100.0)
    tb = 50.0 + rng.normal(0, 1, len(t))          # delta ~ 0 everywhere
    tb[hour == 8] = 90.0                           # strong buy delta only at 08Z
    o = 100.0 + np.cumsum(rng.normal(0, 0.01, len(t)))
    c = o + rng.normal(0, 0.01, len(t))
    return t, o, c, vol, tb


def test_top_bucket_is_hour_8_and_placebo_is_not():
    t, o, c, v, tb = synth()
    feat = clocks.features(t, o, c, v, tb)
    res = clocks.run(t, feat, draws=40)
    ds = np.array(res["hour"]["delta_share"])
    assert int(np.argmax(ds)) == 8
    assert res["hour"]["delta_share_z"][8] > 5
    rng = np.random.default_rng(7)
    tops = []
    for _ in range(20):
        lab = clocks.labels(t, hour_off=rng.integers(0, 24, 60))[0]
        tops.append(int(np.argmax(clocks.bucket_stats(feat, lab, 24)["delta_share"])))
    assert tops.count(8) <= 3  # shuffled labels spread the 08Z block over all buckets


def test_funding_window_and_weekday_labels():
    t = clocks.DEV_START_MS + np.arange(3 * 1440, dtype=np.int64) * 60000
    hour, fund, wd = clocks.labels(t)
    assert fund[0] == 0 and fund[29] == 0 and fund[30] == 3 and fund[1440 - 31] == 3 and fund[1440 - 30] == 0
    assert fund[480] == 1 and fund[960] == 2
    assert wd[0] == 1 and wd[1440] == 2  # 2022-02-01 was a Tuesday


def test_forward_net_counts_fee_and_gaps():
    t, o, c, v, tb = synth(days=1)
    c = o * 1.001
    feat = clocks.features(t, o, c, v, tb)
    f = feat["fwd"][15]
    assert np.isnan(f[-15:]).all() and not np.isnan(f[0])
    keep = np.arange(len(t)) != 700               # a missing minute breaks every window across it
    f2 = clocks.features(t[keep], o[keep], c[keep], v[keep], tb[keep])["fwd"][15]
    assert np.isnan(f2[690:700]).all()


def test_validation_split_is_refused():
    assert clocks.main(["--split", "validation"]) == 2
