"""Spec-derived tests for imb.py (expected numbers worked by hand, not taken from the code). Run: python <this file>."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import imb  # noqa: E402


def test_resample_hour():
    t0 = 1_700_000_000_000 // 3_600_000 * 3_600_000
    t = t0 + np.arange(61) * 60_000          # one full hour + 1 minute of the next (incomplete, dropped)
    df = pd.DataFrame({"t": t, "o": np.arange(61) + 100.0, "h": np.arange(61) + 101.0, "l": np.arange(61) + 99.0,
                       "c": np.arange(61) + 100.5, "v": np.ones(61)})
    b = imb.resample(df, "1h")
    assert len(b) == 1
    r = b.iloc[0]
    assert (r.t, r.o, r.h, r.l, r.c, r.v) == (t0, 100.0, 160.0, 99.0, 159.5, 60.0)


def test_rel_volume():
    rv = imb.rel_volume([1.0] * 50 + [3.0], n=50)
    assert np.isnan(rv[:50]).all() and rv[50] == 3.0


def test_body_frac():
    assert imb.body_frac([10], [12], [8], [11])[0] == 0.25
    assert np.isnan(imb.body_frac([10], [10], [10], [10])[0])


def test_level_match():
    # range: 65400 inside [65000, 65200*(1.004)=65460.8] -> True; 65500 not
    assert imb.level_match([65200], [65000], 65400, "range")[0]
    assert not imb.level_match([65200], [65000], 65500, "range")[0]
    # mid: (64000+63800)/2 = 63900, level 64000 off by 0.156% (<0.25%) -> True; 64100 off by 0.31% -> False
    assert imb.level_match([64000], [63800], 64000, "mid")[0]
    assert not imb.level_match([64000], [63800], 64100, "mid")[0]


def test_prob_at_least():
    assert abs(imb.prob_at_least([0.5, 0.5], 2) - 0.25) < 1e-12
    assert abs(imb.prob_at_least([0.5, 0.5], 1) - 0.75) < 1e-12
    assert imb.prob_at_least([0.2], 0) == 1.0


def test_resolve_and_fee():
    hi, lo, cl = np.array([101.0, 102.5]), np.array([99.5, 100.5]), np.array([100.8, 102.0])
    px, oc = imb.resolve(1, 100.0, 99.0, 102.0, hi, lo, cl)
    assert (px, oc) == (102.0, "target")
    g, c, n = imb.trade_r(1, 100.0, 99.0, 102.0)
    assert g == 2.0 and abs(c - 0.101) < 1e-12 and abs(n - 1.899) < 1e-12      # 0.0005*(100+102)/1
    # stop and target in the same minute -> stop first: -1R - 0.0005*(100+99) = -1.0995
    px, oc = imb.resolve(1, 100.0, 99.0, 102.0, np.array([102.5]), np.array([98.5]), np.array([100.0]))
    assert (px, oc) == (99.0, "stop")
    assert abs(imb.trade_r(1, 100.0, 99.0, 99.0)[2] + 1.0995) < 1e-12
    # neither touched -> time exit at the last close; short side mirrors
    px, oc = imb.resolve(-1, 100.0, 101.0, 98.0, np.array([100.5]), np.array([99.0]), np.array([99.5]))
    assert (px, oc) == (99.5, "time")
    assert abs(imb.trade_r(-1, 100.0, 101.0, 99.5)[0] - 0.5) < 1e-12


def test_classify():
    n = 60
    o = np.full(n, 100.0); c = np.full(n, 100.5); h = np.full(n, 101.0); l = np.full(n, 99.0); v = np.ones(n)
    # bar 55: new 20-bar low, 3x volume, body 0.2 of range -> imb_small long
    o[55], c[55], h[55], l[55], v[55] = 98.0, 98.2, 98.5, 97.5, 3.0
    # bar 58: new 20-bar high, 3x volume, body 0.8 of range -> imb_large short
    o[58], c[58], h[58], l[58], v[58] = 100.1, 101.7, 101.8, 99.8, 3.0
    b = pd.DataFrame({"t": np.arange(n), "o": o, "h": h, "l": l, "c": c, "v": v})
    cls, side = imb.classify(b, 2.0)
    assert (cls[55], side[55]) == ("imb_small", 1)
    assert (cls[58], side[58]) == ("imb_large", -1)
    # bar 54: volume 1x (< 1.2) and body 0.5/2 = 0.25 (<= 0.30) -> control class; not an extreme, side 0
    assert (cls[54], side[54]) == ("normal_small", 0)


def test_classify_control():
    n = 60
    b = pd.DataFrame({"t": np.arange(n), "o": np.full(n, 100.0), "h": np.full(n, 101.0), "l": np.full(n, 99.0),
                      "c": np.full(n, 100.2), "v": np.ones(n)})
    cls, side = imb.classify(b, 2.0)
    assert cls[55] == "normal_small" and side[55] == 0


def test_microseconds():
    import io
    csv = "1735689600000000,1,2,0.5,1.5,10,0,0,0,0,0,0\n"
    df = imb._read_kline_csv(io.StringIO(csv))
    assert int(df.t[0]) == 1735689600000


def test_labels_verbatim():
    for lab in imb.load_labels():
        assert imb.locate_quote(lab["video"], lab["quote"]), lab["id"]


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok  ", name)
            except Exception as e:  # report every failure
                fails += 1
                print("FAIL", name, repr(e))
    sys.exit(1 if fails else 0)
