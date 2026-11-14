import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core2  # noqa: E402

BAR = 3600000


def mk(n=10):
    t = np.arange(n) * BAR
    return t, np.full(n, 100.0), np.full(n, 101.0), np.full(n, 99.0), np.full(n, 100.0), np.full(n, 1.0)


def test_capitulation_needs_range_and_low_close():
    t, o, h, l, c, a = mk()
    h[3], l[3], c[3] = 106.0, 99.0, 99.5   # range 7 >= 3*1, close in lower 25%
    h[5], l[5], c[5] = 106.0, 99.0, 105.0  # big but closes high
    cap = core2.capitulation(h, l, c, a)
    assert cap[3] and not cap[5] and not cap[4]


def test_stop_fill_and_fee():
    t, o, h, l, c, a = mk()
    ft, cs = np.array([10 ** 15]), np.array([0.0, 0.0])
    # setup i=2 low 99 stop 98.75; entry close[3]=100; bar 5 low 90 hits stop, open 100 -> filled at stop
    l[5] = 90.0
    ret, xj = core2.fwd_trades(t, o, l, c, a, 4, BAR, ft, cs)
    assert xj[2] == 5
    assert abs(ret[2] - (98.75 / 100 - 1 - core2.RT_FEE)) < 1e-12


def test_time_exit_and_funding():
    t, o, h, l, c, a = mk()
    c[6] = 102.0
    ft, cs = np.array([4 * BAR + 1]), np.array([0.0, 0.001])
    ret, xj = core2.fwd_trades(t, o, l, c, a, 3, BAR, ft, cs)
    assert xj[2] == 6   # i+1+hold
    assert abs(ret[2] - (0.02 - core2.RT_FEE - 0.001)) < 1e-12
