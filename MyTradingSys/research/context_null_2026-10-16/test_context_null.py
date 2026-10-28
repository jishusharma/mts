"""Tests for context_null.py (synthetic tapes only, no market data). Run: python test_context_null.py  (or pytest).

Every test has a deliberately broken counterpart that the same check must reject; expected numbers come from the plant
arithmetic written in each test, never from the code under test.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import context_null as CN  # noqa: E402

SIGMA = 0.0005                      # iid log-return sd per 5m bar
CFG = dict(bar_min=5, K=20)


def tape(ndays, seed, plant=None, sigma=SIGMA, sig_ramp=None):
    """5m tape: iid N(0, sigma) log returns; plant(r) may add drift in place. Returns closes (start 100)."""
    rng = np.random.default_rng(seed)
    n = ndays * 288
    s = np.full(n, sigma) if sig_ramp is None else np.linspace(sig_ramp[0], sig_ramp[1], n)
    r = rng.standard_normal(n) * s
    r[0] = 0.0
    if plant is not None:
        plant(r)
    return 100.0 * np.exp(np.cumsum(r))


def hours(n, cfg):
    return CN.hour_of(np.arange(n), cfg)


def pick_events(rng, pool, k, cd):
    ev = rng.choice(pool, size=k, replace=False)
    return [t for t, _ in CN.screen.apply_cooldown([(int(t), 0) for t in ev], cd)]


# ---------------------------------------------------------------- 1. context-only effect
MU = 0.0005                         # planted: the bar after an hour-13 bar returns +0.05 % extra (log)


def context_fixture():
    cfg = CN.Config(cooldown=3, seed=1, **CFG)
    n = 400 * 288

    def plant(r):
        h13 = np.flatnonzero(hours(n, cfg) == 13)
        h13 = h13[h13 + 1 < n]
        r[h13 + 1] += MU

    C = tape(400, seed=11, plant=plant)
    rng = np.random.default_rng(5)
    allb = np.arange(9000, n - 5)
    in13 = allb[hours(n, cfg)[allb] == 13]
    out13 = allb[hours(n, cfg)[allb] != 13]
    ev = sorted(set(pick_events(rng, in13, 150, 3) + pick_events(rng, out13, 40, 3)))
    return C, ev, cfg


def check_context_only(res, ev, n, cfg):
    """Trigger effect ~ 0 (|t| < 2) and a positive context effect near its planted arithmetic."""
    assert abs(res["trigger_t"]) < 2.0, f"trigger t {res['trigger_t']}"
    frac13 = np.mean(hours(n, cfg)[np.array(ev)] == 13)
    exp_ctx = 100.0 * MU * (frac13 - 1.0 / 24.0)          # controls of an hour-13 event are hour-13 bars: +MU; uncond: MU/24
    assert res["context_effect"] > 0 and res["context_t"] > 5.0, res["context_effect"]
    assert res["control_reuse"] < CN.REUSE_WARN, res["control_reuse"]        # pool thick enough for the SE to be honest
    assert abs(res["context_effect"] - exp_ctx) < 3 * res["context_se"] + 0.002, (res["context_effect"], exp_ctx)


def test_context_only_effect_rejected():
    C, ev, cfg = context_fixture()
    res = CN.run(C, ev, h=1, d=0, cfg=cfg)
    print(CN.format_report(res))
    check_context_only(res, ev, len(C), cfg)
    # identity: event mean - unconditional mean = context effect + trigger effect
    assert abs((res["event_mean"] - res["uncond_mean"]) - (res["context_effect"] + res["trigger_effect"])) < 1e-9
    assert res["n_matched"] + res["n_unmatched"] == res["n_events"]


def test_context_only_broken_no_matching_is_caught():
    C, ev, cfg = context_fixture()
    broken = CN.Config(cooldown=3, seed=1, match=(), **CFG)       # controls drawn from anywhere: context leaks into "trigger"
    res = CN.run(C, ev, h=1, d=0, cfg=broken)
    try:
        check_context_only(res, ev, len(C), cfg)
    except AssertionError:
        return
    raise AssertionError("broken (unmatched) controls passed the context-only check")


# ---------------------------------------------------------------- 2. planted trigger effect
X_PCT = 0.1                         # +0.1 % simple return over the h bars after entry, regardless of context
H, D, CD = 6, 1, 10


def trigger_fixture():
    cfg = CN.Config(cooldown=CD, seed=2, **CFG)
    n = 200 * 288
    rng = np.random.default_rng(8)
    ev = pick_events(rng, np.arange(9000, n - 20), 1000, CD)
    xl = np.log(1.0 + X_PCT / 100.0)

    def plant(r):
        for t in ev:
            r[t + D + 1:t + D + H + 1] += xl / H

    return tape(200, seed=12, plant=plant), ev, cfg


def check_trigger_recovered(res):
    assert res["trigger_t"] > 10.0, res["trigger_t"]
    assert abs(res["trigger_effect"] - X_PCT) < 2 * res["trigger_se"], (res["trigger_effect"], res["trigger_se"])


def test_trigger_effect_recovered():
    C, ev, cfg = trigger_fixture()
    res = CN.run(C, ev, h=H, d=D, cfg=cfg)
    print(CN.format_report(res))
    check_trigger_recovered(res)
    assert abs(res["context_effect"]) < 3 * res["context_se"] + 1e-9      # no planted context -> none reported


def test_trigger_broken_forward_window_is_caught():
    C, ev, cfg = trigger_fixture()
    real = CN.fwd_returns

    def shifted(C_, d_, h_):                 # broken: the forward window is read 50 bars late
        out = np.full(len(C_), np.nan)
        out[:-50] = real(C_, d_, h_)[50:]
        return out

    CN.fwd_returns = shifted
    try:
        res = CN.run(C, ev, h=H, d=D, cfg=cfg)
    finally:
        CN.fwd_returns = real
    try:
        check_trigger_recovered(res)
    except AssertionError:
        return
    raise AssertionError("broken forward window passed the recovery check")


# ---------------------------------------------------------------- 3. truncation invariance, 4. look-ahead detected
def vol_bucket_lookahead(rv, t, cut_win):
    """Planted look-ahead: tercile cut points from the FULL sample instead of the window ending at t."""
    w = rv[~np.isnan(rv)]
    c1, c2 = np.quantile(w, [1.0 / 3.0, 2.0 / 3.0])
    if np.isnan(rv[t]):
        return None
    return int(rv[t] > c1) + int(rv[t] > c2)


def truncation_mismatches(C, ts, cfg, level=None, vol_fn=CN.vol_bucket):
    """Bars t where the context key computed on bars[0..t] differs from the key computed on the full array."""
    bad = []
    for t in ts:
        k_cut = CN.context_key(C[:t + 1], t, cfg, level=None if level is None else level[:t + 1], vol_fn=vol_fn)
        k_full = CN.context_key(C, t, cfg, level=level, vol_fn=vol_fn)
        if k_cut != k_full:
            bad.append(t)
    return bad


def truncation_fixture():
    cfg = CN.Config(seed=3, **CFG)
    C = tape(120, seed=13, sig_ramp=(0.0002, 0.001))            # vol ramps up: full-sample cuts differ from trailing cuts
    ts = list(np.random.default_rng(4).integers(9000, len(C) - 1, 40))
    level = np.random.default_rng(6).integers(0, 3, len(C))
    return C, [int(t) for t in ts], cfg, level


def test_truncation_invariance():
    C, ts, cfg, level = truncation_fixture()
    keys = {CN.context_key(C, t, cfg, level=level) for t in ts}
    assert len(keys) > 5                                         # keys really vary, so the comparison is not vacuous
    assert truncation_mismatches(C, ts, cfg, level=level) == []


def test_lookahead_vol_detected_by_truncation_check():
    C, ts, cfg, level = truncation_fixture()
    bad = truncation_mismatches(C, ts, cfg, level=level, vol_fn=vol_bucket_lookahead)
    assert len(bad) >= 5, bad


# ---------------------------------------------------------------- extras
def test_trend_tag_is_tom_bt_causal_tag():
    """ret30 here equals tom_bt.regime_features' ret30 and the tag comes from tom_bt.trend_tag."""
    rng = np.random.default_rng(9)
    n = 30 * 1440 + 2000
    C = 100.0 * np.exp(np.cumsum(rng.standard_normal(n) * 0.0003))

    class B:                                                      # the two attributes regime_features reads
        c = C

        @staticmethod
        def idx(ms):
            return ms // 60000

    cfg = CN.Config(bar_min=1)
    for t in (30 * 1440 + 5, 30 * 1440 + 1500):
        ret30, _ = CN.tom_bt.regime_features(B, (t + 1) * 60.0)          # t_s -> i = t (last closed bar)
        assert abs(ret30 - CN.ret_trailing(C, t, 30 * 1440)) < 1e-12
        assert CN.trend_code(C, t, cfg) == CN.TREND_CODE[CN.tom_bt.trend_tag(ret30)]
    assert CN.trend_code is not None and CN.tom_bt.trend_tag(0.1) == "trend_up"


def test_level_column_matching():
    """Planted LEVEL context: returns after level-1 bars are higher; events fire in level 1. Matching on level removes it."""
    cfg = CN.Config(cooldown=3, seed=4, match=("hour", "vol", "trend", "level"), **CFG)
    n = 400 * 288
    level = (np.random.default_rng(1).random(n) < 0.1).astype(int)       # 10 % of bars are level 1

    def plant(r):
        idx = np.flatnonzero(level[:-1] == 1)
        r[idx + 1] += MU

    C = tape(400, seed=14, plant=plant)
    rng = np.random.default_rng(2)
    ev = pick_events(rng, np.flatnonzero(level[9000:n - 5] == 1) + 9000, 150, 3)
    with_lvl = CN.run(C, ev, h=1, d=0, cfg=cfg, level=level)
    no_lvl = CN.run(C, ev, h=1, d=0, cfg=CN.Config(cooldown=3, seed=4, match=("hour", "vol", "trend"), **CFG))
    assert abs(with_lvl["trigger_t"]) < 2.0, with_lvl["trigger_t"]
    assert no_lvl["trigger_effect"] > 100 * MU * 0.8 and no_lvl["trigger_t"] > 3.0      # context leaks into the "trigger"


def test_early_events_unmatched_and_dev_guard():
    cfg = CN.Config(cooldown=3, seed=5, **CFG)
    C = tape(60, seed=15)
    res = CN.run(C, [100, 200, 17000], h=1, d=0, cfg=cfg)               # first two: < 30 d of history -> no context
    assert res["unmatched"]["no_context"] == 2 and res["n_unmatched"] >= 2
    late = CN.Config(bar_min=5, ts0_ms=CN.DEV_END_MS - 10 * 86_400_000)    # tape reaching past 2024-06-30 is refused
    try:
        CN.run(tape(40, seed=16), [20], h=1, d=0, cfg=late)
    except ValueError:
        return
    raise AssertionError("bars past the DEV cutoff were accepted")


def test_controls_avoid_event_windows():
    """No chosen control may sit inside any event window: plant a huge move in event windows, controls must not see it."""
    C, ev, cfg = trigger_fixture()
    res = CN.run(C, ev, h=H, d=D, cfg=cfg)
    assert abs(res["control_mean"]) < 0.01, res["control_mean"]        # event windows carry +0.1 %; controls ~ 0


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except Exception as e:           # noqa: BLE001
                fails += 1
                print("FAIL", name, repr(e))
    print("ALL TESTS PASSED" if not fails else f"{fails} FAILED")
    sys.exit(1 if fails else 0)
