"""On random-walk 5m data a real (causal) study has no gross edge; the STUDY_BUG look-ahead variant must show a large one."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study


def synth(seed, days=260):
    rng = np.random.default_rng(seed)
    n = days * 288
    t = 1577836800000 + np.arange(n) * 300000  # 2020-01-01
    r = rng.normal(0, 0.0015, n)
    c = 100 * np.exp(np.cumsum(r))
    o = np.r_[100, c[:-1]]
    h = np.maximum(o, c) * (1 + abs(rng.normal(0, 0.0008, n)))
    l = np.minimum(o, c) * (1 - abs(rng.normal(0, 0.0008, n)))
    v = rng.uniform(1, 10, n)
    return np.c_[t, o, h, l, c, v]


def mean_gross(bug):
    coins = {"S%d" % i: synth(i) for i in range(4)}
    tr = study.run(coins, bug=bug)
    assert len(tr) > 200
    return np.mean([x["ret"][2] / x["R"] for x in tr])


def test_real_has_no_edge_and_bug_has():
    real = mean_gross(False)
    bugged = mean_gross(True)
    assert abs(real) < 0.1, real
    assert bugged > real + 0.15, (real, bugged)


def test_env_switch():
    old = os.environ.get("STUDY_BUG")
    os.environ["STUDY_BUG"] = "1"
    try:
        coins = {"S0": synth(9, 120)}
        a = np.mean([x["ret"][2] / x["R"] for x in study.run(coins)])
    finally:
        if old is None:
            del os.environ["STUDY_BUG"]
        else:
            os.environ["STUDY_BUG"] = old
    b = np.mean([x["ret"][2] / x["R"] for x in study.run(coins, bug=False)])
    assert a > b


def test_default_run_is_causal():
    """fails when STUDY_BUG=1 is set in the environment (look-ahead version)."""
    coins = {"S%d" % i: synth(i) for i in range(4)}
    tr = study.run(coins)
    assert abs(np.mean([x["ret"][2] / x["R"] for x in tr])) < 0.1
