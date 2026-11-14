"""Core-rule test: S3 confirm entry and the time8 exit on a synthetic series (no data needed)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "backtest")))
import exits_lib as X
import rsi_grid_lib as L


def test_time8_and_stop():
    n = 30
    o = np.full(n, 100.0); h = np.full(n, 101.0); l = np.full(n, 99.0); c = np.full(n, 100.0)
    c[9] = 110.0
    G = dict(o=o, h=h, l=l, c=c, rsi=np.full(n, np.nan), sma=np.full(n, np.nan))
    g0 = np.array([0, 0]); entry = np.array([100.0, 100.0]); stop = np.array([98.0, 99.5])
    out = X.fwd_sim(dict(kind="time", n=8), G, g0, entry, stop)
    assert abs(out[0]) < 1e-12
    assert abs(out[1] - (-0.005)) < 1e-12


def test_confirm_needs_green_above_signal_close():
    H = L.HOUR
    ft = np.array([0, 4 * H]); fo = np.array([100.0, 90.0]); fc = np.array([90.0, 95.0]); fh = fc + 1; fl = np.array([88.0, 89.0])
    assert L.confirm_info(ft, fo, fh, fl, fc, 0, 4)["confirm"]
    fc2 = np.array([90.0, 85.0])
    assert not L.confirm_info(ft, fo, fh, fl, fc2, 0, 4)["confirm"]


if __name__ == "__main__":
    test_time8_and_stop(); test_confirm_needs_green_above_signal_close(); print("ok")
