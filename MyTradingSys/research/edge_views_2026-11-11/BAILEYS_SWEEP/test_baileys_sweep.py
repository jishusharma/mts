import sys
sys.dont_write_bytecode = True
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import baileys_sweep as B


def synth(days=260, seed=3):
    rng = np.random.default_rng(seed)
    n = days * 1440
    t = (np.arange(n) * 60_000).astype(np.int64)
    # regime-switching drift so both daily biases occur, noisy enough for sweeps
    drift = np.repeat(rng.normal(0, 0.00004, days // 10 + 1), 14400)[:n]
    c = 20000 * np.exp(np.cumsum(drift + rng.normal(0, 0.0007, n)))
    o = np.r_[c[0], c[:-1]]
    h = np.maximum(o, c) * (1 + abs(rng.normal(0, 0.0003, n)))
    l = np.minimum(o, c) * (1 - abs(rng.normal(0, 0.0003, n)))
    return t, o, h, l, c


def build(upto_n=None):
    t, o, h, l, c = synth()
    if upto_n:
        t, o, h, l, c = t[:upto_n], o[:upto_n], h[:upto_n], l[:upto_n], c[:upto_n]
    return (B.resample(t, o, h, l, c, B.M15), B.resample(t, o, h, l, c, B.H1), B.resample(t, o, h, l, c, B.D1))


def test_rule_trades_exist_and_are_sane():
    b15, h1, d1 = build()
    tr = B.run(b15, h1, d1, 0, 1 << 60)
    assert len(tr) >= 5
    for x in tr:
        assert x["entry_px"] == b15["o"][x["entry_i"]]
        assert x["exit_i"] >= x["entry_i"]
        assert x["side"] in (1, -1)


def test_pivot_not_used_before_confirmation():
    b15, _, _ = build()
    for upto in range(50, 400):
        p = B.latest_pivot(b15, upto, "low")
        if p:
            assert p[0] + B.PIV <= upto


def test_no_look_ahead_prefix_invariance():
    """Cutting the data after a trade's entry bar must not change that trade: a look-ahead rule fails this."""
    full = B.run(*build(), 0, 1 << 60)
    assert len(full) >= 5
    n_checked = 0
    for x in full[:6]:
        cut = x["entry_i"] * 15 + 1                 # 1m rows kept: data stops one minute into the entry bar
        b15, h1, d1 = build(cut)
        part = B.run(b15, h1, d1, 0, 1 << 60)
        same = [p for p in part if p["entry_ms"] == x["entry_ms"]]
        assert same and same[0]["entry_px"] == x["entry_px"] and same[0]["stop"] == x["stop"],             "trade depends on data after its entry bar opened"
        n_checked += 1
    assert n_checked >= 5


def test_look_ahead_shifted_version_is_caught():
    """The shifted (peeking) variant must differ from the honest one, so the invariance test has teeth."""
    b15, h1, d1 = build()
    honest = B.run(b15, h1, d1, 0, 1 << 60)
    peek = B.run(b15, h1, d1, 0, 1 << 60, shift=1)
    assert [(x["entry_ms"], x["stop"]) for x in honest] != [(x["entry_ms"], x["stop"]) for x in peek]


def test_look_ahead_version_fails_prefix_invariance():
    full = B.run(*build(), 0, 1 << 60, shift=1)
    failed = False
    for x in full[:6]:
        cut = x["entry_i"] * 15 + 1                 # data stops one minute into the entry bar
        part = B.run(*build(cut), 0, 1 << 60, shift=1)
        if not [p for p in part if p["entry_ms"] == x["entry_ms"] and p["stop"] == x["stop"]]:
            failed = True
    assert failed


def test_stop_wins_tie_and_three_r_target():
    bars = dict(t=np.arange(5) * B.M15, o=np.full(5, 100.0), h=np.array([100, 110, 100, 100, 100.0]),
                l=np.array([100, 90, 100, 100, 100.0]), c=np.full(5, 100.0))
    assert B.simulate(bars, 1, 1, 95.0, 115.0)[2] == "stop"      # both touched: stop counts
    assert B.simulate(bars, 1, -1, 105.0, 85.0)[2] == "stop"
    bars["l"][1] = 99.0
    x = B.simulate(bars, 1, 1, 95.0, 110.0)
    assert x[2] == "tp" and x[1] == 110.0
