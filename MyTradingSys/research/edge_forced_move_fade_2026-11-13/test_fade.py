import numpy as np, fade as F
B = F.BAR
def mk(rows):
    a = np.array(rows, float); t = np.arange(len(a)) * B
    return t, a[:, 0], a[:, 1], a[:, 2], a[:, 3]
def test_stop_first_and_fee():
    # bar0 entry close 100; bar1 hits both stop 99 and target 101 -> stop wins (short->long side=+1)
    t, o, h, l, c = mk([(100, 100, 100, 100), (100, 101.5, 98.5, 100)] + [(100, 100, 100, 100)] * 40)
    r = F.fwd_sim(t, o, h, l, c, [], [], 0, 1, 99.0, 101.0, 8)
    assert abs(r - (-0.01 - F.RT_FEE)) < 1e-9
def test_short_target():
    t, o, h, l, c = mk([(100, 100, 100, 100), (100, 100.2, 98.9, 99.5)] + [(100, 100, 100, 100)] * 40)
    r = F.fwd_sim(t, o, h, l, c, [], [], 0, -1, 101.0, 99.0, 8)
    assert abs(r - (0.01 - F.RT_FEE)) < 1e-9
def test_atr_prior_excludes_current():
    h = np.r_[np.full(30, 101.0), 500.0]; l = np.r_[np.full(30, 99.0), 1.0]; c = np.full(31, 100.0)
    a = F.atr_prior(h, l, c)
    assert abs(a[30] - 2.0) < 1e-9
if __name__ == "__main__":
    test_stop_first_and_fee(); test_short_target(); test_atr_prior_excludes_current(); print("ok")
