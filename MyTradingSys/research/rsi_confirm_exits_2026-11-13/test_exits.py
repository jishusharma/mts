"""Core-function test for the exit engine (toy bars, hand-computed)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exits_lib as X


def mk(rows):
    # rows: (o,h,l,c) per bar; bar 0 = entry bar (never read)
    a = np.array(rows, float)
    n = len(a)
    return dict(o=a[:, 0], h=a[:, 1], l=a[:, 2], c=a[:, 3], rsi=np.full(n, 25.0), sma=np.full(n, 105.0))


def run(name, rows, entry=100.0, stop=90.0):
    G = mk(rows)
    rule = dict(X.RULES)[name]
    return X.fwd_sim(rule, G, np.array([0]), np.array([entry]), np.array([stop]))[0]


PAD = [(100, 100, 100, 100)] * 200


def test_stop_first_same_bar():
    # bar1 spans both stop (90) and 0.5R target (105): stop first -> -10%
    assert abs(run("tgt0.5R", [(100,) * 4, (100, 106, 89, 100)] + PAD) + 0.10) < 1e-9


def test_target_fill_and_gap_stop():
    assert abs(run("tgt0.5R", [(100,) * 4, (100, 106, 99, 104)] + PAD) - 0.05) < 1e-9
    assert abs(run("base_1R", [(100,) * 4, (85, 86, 84, 85)] + PAD) + 0.15) < 1e-9  # gap below stop fills at open


def test_time_exit_close():
    assert abs(run("time2", [(100,) * 4, (100, 101, 99, 101), (101, 103, 100, 102)] + PAD) - 0.02) < 1e-9


def test_be_after_half_r():
    # bar1 hits +0.5R (105) -> BE stop from bar2; bar2 dips to 99 -> exit at 100 (0%)
    assert abs(run("be_tgt2", [(100,) * 4, (100, 106, 99.5, 104), (104, 105, 99, 100)] + PAD)) < 1e-9


def test_half_trail():
    # bar1 arms (half sold at +5%); bar2 trails prior low 99.5 -> bar2 low 99 <= 99.5 exits rest at 99.5: 0.5*.05 + 0.5*(-0.005)
    r = run("half_trail", [(100,) * 4, (100, 106, 99.5, 104), (104, 105, 99, 100)] + PAD)
    assert abs(r - (0.025 - 0.0025)) < 1e-9


def test_ma_touch_uses_prior_bar_level():
    G = mk([(100,) * 4, (100, 104, 99, 103), (103, 106, 102, 105)] + PAD)
    r = X.fwd_sim(dict(X.RULES)["ma20touch"], G, np.array([0]), np.array([100.0]), np.array([90.0]))[0]
    assert abs(r - 0.05) < 1e-9
