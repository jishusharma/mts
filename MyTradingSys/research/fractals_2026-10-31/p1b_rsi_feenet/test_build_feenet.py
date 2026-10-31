import importlib.util
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from MyTradingSys.backtest.fees import BINANCE_TAKER  # noqa: E402

_P = Path(__file__).with_name("build_feenet.py")
_S = importlib.util.spec_from_file_location("build_feenet", _P)
bf = importlib.util.module_from_spec(_S)
_S.loader.exec_module(bf)


def bars(rows):
    a = np.array(rows, dtype=float)
    return a[:, 0], a[:, 1], a[:, 2]  # open, high, low


def run(side, o, h, l, c, risk=1.0, horizon=4):
    return bf.simulate_exit(side, np.array(o, float), np.array(h, float), np.array(l, float), np.array(c, float), risk, horizon)


FLAT = dict(o=[100, 100, 100, 100], h=[100.5] * 4, l=[99.5] * 4, c=[100] * 4)


def test_long_target():
    d = dict(FLAT); d["h"] = [100.5, 102.2, 100.5, 100.5]
    ex, why, n = run("long", **d)
    assert (ex, why, n) == (102.0, "target", 2)


def test_long_stop():
    d = dict(FLAT); d["l"] = [99.5, 98.5, 99.5, 99.5]
    ex, why, n = run("long", **d)
    assert (ex, why) == (99.0, "stop")


def test_short_mirror():
    d = dict(FLAT); d["l"] = [99.5, 97.5, 99.5, 99.5]
    assert run("short", **d)[:2] == (98.0, "target")
    d = dict(FLAT); d["h"] = [100.5, 101.5, 100.5, 100.5]
    assert run("short", **d)[:2] == (101.0, "stop")


def test_time_exit_at_last_bar_close():
    d = dict(FLAT); d["c"] = [100, 100, 100, 100.3]
    assert run("long", **d) == (100.3, "time", 4)


def test_same_bar_both_takes_stop():
    d = dict(FLAT); d["h"] = [100.5, 103, 100.5, 100.5]; d["l"] = [99.5, 98, 99.5, 99.5]
    assert run("long", **d)[:2] == (99.0, "stop")


def test_gap_through_stop_fills_at_open():
    d = dict(FLAT); d["o"] = [100, 98.0, 100, 100]; d["l"] = [99.5, 97.5, 99.5, 99.5]; d["h"] = [100.5, 98.2, 100.5, 100.5]
    assert run("long", **d)[:2] == (98.0, "stop")


def test_no_bar_after_exit_used():
    d = dict(FLAT); d["h"] = [100.5, 102.2, 100.5, 100.5]
    a = run("long", **d)
    d2 = {k: list(v) for k, v in d.items()}
    for k in d2:
        d2[k][2] = 1e9 if k != "l" else -1e9
        d2[k][3] = -1e9 if k != "l" else 1e9
    assert run("long", **d2) == a


def test_fee_once_per_side():
    gross, net = bf.net_r("long", 100.0, 100.0, 2.0)
    assert gross == 0.0
    assert abs(net - (-(2 * BINANCE_TAKER * 100.0) / 2.0)) < 1e-12
    # a winner: both sides charged on their own price
    g, n = bf.net_r("long", 100.0, 104.0, 2.0)
    assert g == 2.0 and abs((g - n) - BINANCE_TAKER * 204.0 / 2.0) < 1e-12


def test_dev_cut():
    t = np.array([bf.DEV_END_MS - 3_600_000, bf.DEV_END_MS, bf.DEV_END_MS + 3_600_000])
    assert bf.dev_mask(t).tolist() == [True, False, False]
