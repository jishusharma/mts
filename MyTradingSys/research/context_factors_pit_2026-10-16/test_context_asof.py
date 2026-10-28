"""Tests for context_asof.py: hand arithmetic (angle c), bucket convention, replay == vectorised (angle a), truncation
invariance per factor, and the planted look-ahead versions that the truncation test must catch.

Synthetic tapes only (deterministic random walk), so the gate stays fast. The real-DEV runs are run_compare.py (angle a on
the whole split) and trader_eye.py (angle b). Run: python -m pytest test_context_asof.py -q
"""
import os
import sys
import tempfile

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import context_asof as CA   # noqa: E402
import run_compare as RC    # noqa: E402

SIDES = ("long", "short")
PLANTS = ("ladder_final_day", "bb_partial_close", "candle_partial", "pivot_unconfirmed", "vp_include_today",
          "pct_fullsample", "funding_next")


def synth(days, seed=0, p0=30000.0):
    """Deterministic 1m random-walk tape: O,H,L,C,V with wicks; volume lognormal."""
    rng = np.random.default_rng(seed)
    n = days * 1440
    r = rng.normal(0, 0.0006, n)
    r[::1440 * 7] += 0.03 * rng.choice([-1, 1], size=len(r[::1440 * 7]))     # weekly jumps so swings/levels exist
    C = p0 * np.exp(np.cumsum(r))
    O = np.concatenate(([p0], C[:-1]))
    w1 = np.abs(rng.normal(0, 0.0004, n)) * C
    w2 = np.abs(rng.normal(0, 0.0004, n)) * C
    H = np.maximum(O, C) + w1
    L = np.minimum(O, C) - w2
    V = np.exp(rng.normal(3, 0.8, n))
    return {"O": O, "H": H, "L": L, "C": C, "V": V, "TBV": V * 0.5}


def synth_funding(days, seed=1):
    rng = np.random.default_rng(seed)
    k = days * 3
    t = CA.TS0 + np.arange(k) * 8 * 3600 * 1000
    r = rng.normal(0.0001, 0.00015, k)
    return t.astype(np.int64), r


def ctx(bars, t, side, impl, fund=None):
    return RC.flat(CA.context_at(bars, t, side, impl, fund))


def diff_fields(a, b):
    return sorted(k for k in set(a) | set(b) if not RC.same(a.get(k), b.get(k)))


# ------------------------------------------------------------------ angle c: hand arithmetic
def test_hand_atr_formulas_s12(monkeypatch):
    """FORMULAS.md s.12 worked example: highs [10,11,12,11], lows [9,9,10,9], closes [9.5,10.5,11.5,10] -> ATR(3) = 2.1667.
    Built as four 4h candles out of 1m bars; both builds."""
    monkeypatch.setattr(CA, "ATR_N", 3)
    hs, ls, cs = [10, 11, 12, 11], [9, 9, 10, 9], [9.5, 10.5, 11.5, 10]
    n = 4 * 240
    O = np.full(n, 9.5)
    H = np.full(n, 9.5)
    L = np.full(n, 9.5)
    C = np.full(n, 9.5)
    for k in range(4):
        s = k * 240
        O[s:s + 240] = cs[k]
        C[s:s + 240] = cs[k]
        H[s:s + 240] = cs[k]
        L[s:s + 240] = cs[k]
        H[s + 10] = hs[k]
        L[s + 20] = ls[k]
    bars = {"O": O, "H": H, "L": L, "C": C, "V": np.ones(n), "TBV": np.ones(n)}
    for impl in ("vec", "replay"):
        f = CA.context_at(bars, n - 1, "long", impl)
        assert abs(f["atr4"] - (2 + 2 + 2.5) / 3) < 1e-12, impl


def test_hand_value_area_18_1(monkeypatch):
    """FORMULAS.md 18.1 worked A, B, C (w = 1) on both profile builders."""
    monkeypatch.setattr(CA, "VP_BIN", 1.0)
    A = ([0, 1, 1], [2, 3, 2], [6, 4, 10])
    B = ([0.5, 1.5, 2.5, 3.5, 4.5], [0.5, 1.5, 2.5, 3.5, 4.5], [1, 2, 10, 4, 3])
    Cc = ([0.5, 1.5, 2.5], [0.5, 1.5, 2.5], [3, 10, 3])
    for (L, H, V), want in ((A, (1.5, 1.0, 2.0)), (B, (2.5, 2.0, 4.0)), (Cc, (1.5, 0.0, 2.0))):
        assert CA.profile_replay(L, H, V) == pytest.approx(want)
        assert CA.profile_vec(L, H, V) == pytest.approx(want)


def test_hand_candle_patterns():
    g = (100, 106, 99, 105)        # green
    r = (105, 107, 98, 99)         # red, closes below the green's open -> bear engulf (operator's words), also outside
    assert CA.candle_patterns(r, g, None) == ("bear_engulf", "outside")
    assert CA.candle_patterns((99, 101, 98.5, 100.5), r, g) == ("inside",)
    pin = (100, 100.5, 94, 100.2)  # range 6.5, lower wick 6 >= 3.9, body 0.2 <= 1.95
    assert "bull_pin" in CA.candle_patterns(pin, g, None)
    assert CA.candle_patterns((100, 101, 99, 100.5), (99, 100.2, 98, 100), (98, 99.5, 97, 99)) == ("three_up",)
    assert CA.candle_patterns((100, 101, 99, 100), (99, 100.2, 98, 100), None) == ("none",)


def test_hand_bb_state():
    # walk: 3 closes at/above the upper band with bandwidth expanding vs 3 bars earlier
    cl, up, lo, bw = [10, 11, 12, 13], [9.5, 10.5, 11.5, 12.5], [8, 8, 8, 8], [0.10, 0.11, 0.12, 0.13]
    assert CA.bb_state_from(cl, up, lo, bw) == "walk_up"
    assert CA.bb_state_from(cl, up, lo, [0.13, 0.11, 0.12, 0.13]) == "outside_up"      # not expanding
    assert CA.bb_state_from([10, 10, 10, 13], up, lo, bw) == "break_up"                 # first close beyond
    assert CA.bb_state_from([10, 10, 7, 9], [12] * 4, [8] * 4, bw) == "reenter_from_lower"
    assert CA.bb_state_from([10, 10, 10, 9], [12] * 4, [8] * 4, bw) == "inside"


def test_hand_ladder():
    # long at 100: prior D low 97 (3.0 % > W 2.5), prior 12h low 98.5 (1.5 %), prior 8h low 99.2 (0.8 %)
    rung, stop, cost_r, below, sd, s12, s8 = CA.ladder("long", 100.0, (99, 101, 97, 100), (99, 101, 98.5, 100), (99, 101, 99.2, 100))
    assert (rung, stop, sd, s12, s8) == ("12h", 1.5, 3.0, 1.5, pytest.approx(0.8))
    assert cost_r == pytest.approx(0.14 / 1.5)
    assert below is False
    # every rung too wide -> the tightest valid one; a prior low above price is not a valid long stop
    rung, stop, *_ = CA.ladder("long", 100.0, (99, 101, 96, 100), (99, 101, 97, 100), (101, 103, 100.5, 102))
    assert (rung, stop) == ("12h", 3.0)
    # short at 100: prior D high 100.4 (0.4 % < floor 0.56)
    rung, stop, cost_r, below, *_ = CA.ladder("short", 100.0, (99, 100.4, 97, 100), None, None)
    assert (rung, below) == ("1d", True) and stop == pytest.approx(0.4)
    assert CA.ladder_cond("long", 100.0, (99, 101, 97, 100)) is True
    assert CA.ladder_cond("short", 100.0, (99, 101, 97, 100)) is False
    assert CA.ladder_cond("short", 100.0, (99, 101, 97, 100), partial_d=(100, 101, 98.5, 100)) is True


def test_bucket_convention():
    bars = synth(3)
    V = CA.VecTables(bars)
    assert V.cur_k(239, "4h") == 0 and V.complete(239, "4h") and V.last_closed(239, "4h") == 0
    assert V.cur_k(240, "4h") == 1 and not V.complete(240, "4h") and V.last_closed(240, "4h") == 0
    assert V.last_closed(238, "4h") == -1
    assert V.last_closed(1439, "1d") == 0 and V.last_closed(1440, "1d") == 0 and V.last_closed(2879, "1d") == 1
    assert V.last_closed(2879, "1w") == -1          # the week starts on Monday (minute 2880)
    assert CA.session_of(0) == "asia" and CA.session_of(8 * 60) == "london" and CA.session_of(13 * 60) == "ny" and CA.session_of(23 * 60) == "late"
    assert CA.is_weekend(0) and CA.is_weekend(1439 + 1440) and not CA.is_weekend(2880)   # Sat, Sun, Mon


def test_loader_refuses_validation_bars(tmp_path):
    p = tmp_path / "BTCUSDT-1m-2024-07.csv"
    p.write_text("open_time,open,high,low,close,volume,close_time,qv,n,tbv,tbqv,ignore\n"
                 f"{CA.DEV_END_MS},1,1,1,1,1,1,1,1,1,1,0\n", encoding="utf-8")
    with pytest.raises(ValueError):
        CA.load_dev([str(p)])


# ------------------------------------------------------------------ angle a: replay == vectorised
def test_replay_equals_vec_synthetic():
    days = 10
    bars = synth(days, seed=3)
    fund = synth_funding(days)
    pts = list(range(59, days * 1440, 60)) + list(range(8 * 1440, 9 * 1440))
    rows_r, rows_v = RC.run(bars, fund, grid_only=False, slice_1m=(8 * 1440, 9 * 1440))
    bad = RC.compare(rows_r, rows_v, "synthetic 10 days")
    assert bad == {}
    assert len(rows_v) == 2 * len(set(pts))


# ------------------------------------------------------------------ truncation invariance
@pytest.fixture(scope="module")
def tape60():
    return synth(60, seed=7), synth_funding(60)


EXT = 14 * 1440     # the truncation test compares bars[0..t] with bars[0..t+EXT]


def pick_points(n):
    """Decision points in days 31-44 of a 60-day tape: mid-day, a 4h close, a day close, a grid point, two off-grid minutes."""
    e = n - EXT
    return [e - 1 - 1440 * 9 + 700, e - 1 - 1440 * 7, e - 1 - 1440 * 5 + 239, e - 1 - 1440 * 3 + 59,
            e - 1 - 1440 * 2 + 17, e - 1 - 1440 - 1]


def test_truncation_invariance_vec(tape60):
    bars, fund = tape60
    n = len(bars["C"])
    for t in pick_points(n):
        for side in SIDES:
            a = ctx(CA.slice_bars(bars, t + 1), t, side, "vec", fund)   # bars[0..t] only
            b = ctx(CA.slice_bars(bars, t + 1 + EXT), t, side, "vec", fund)
            assert diff_fields(a, b) == [], (t, side)
            # every factor is present and populated on a 60-day tape at these points
            for k in ("pat_4h", "pat_1d", "bb_4h_state", "bb_1d_state", "phase_a", "intraday", "vol_regime",
                      "funding", "near_src", "ladder_rung"):
                assert a[k] != "na" and a[k] is not None, (k, t)
            assert a["near_src"] != "none", t      # ladder_rung may be "none" (price below every prior low for a long)


def test_truncation_invariance_replay():
    bars = synth(12, seed=5)
    fund = synth_funding(12)
    t = 10 * 1440 + 700
    for side in SIDES:
        a = ctx(bars, t, side, "replay", fund)
        b = ctx(CA.slice_bars(bars, t + 1), t, side, "replay", fund)
        assert diff_fields(a, b) == []
        assert diff_fields(a, ctx(bars, t, side, "vec", fund)) == []


@pytest.mark.parametrize("plant", PLANTS)
def test_planted_lookahead_is_caught(tape60, plant):
    """With one planted leak switched on in the VEC build, the truncation test must FAIL (bars[0..t] vs bars[0..t+N]
    disagree at some decision point). Each plant corresponds to one trap in CONTEXT_FACTORS_SPEC.md."""
    bars, fund = tape60
    n = len(bars["C"])
    pts = pick_points(n)
    if plant == "pct_fullsample":           # terciles move slowly: look at every 4h close of days 33-44
        pts = list(range(33 * 1440 + 239, n - EXT, 240))
    if plant == "pivot_unconfirmed":        # the leak shows one 4h bar before a pivot is confirmable
        V = CA.VecTables(bars, fund)
        pts = [(i + CA.PIVOT_N) * 240 - 1 for i, kind, px, avj in V.piv4 if 30 * 6 < i + CA.PIVOT_N < (n - EXT) // 240 - 2][-12:]
    CA.PLANT.clear()
    CA.PLANT[plant] = True
    try:
        caught = []
        for t in pts:
            for side in SIDES:
                a = ctx(CA.slice_bars(bars, t + 1), t, side, "vec", fund)   # bars[0..t] only
                b = ctx(CA.slice_bars(bars, t + 1 + EXT), t, side, "vec", fund)
                caught += diff_fields(a, b)
    finally:
        CA.PLANT.clear()
    assert caught, f"plant {plant} not caught"
    print(plant, "caught via", sorted(set(caught))[:6])


# ------------------------------------------------------------------ angle d: red-team RT-1 (prior bucket at a bucket close)
def test_rt1_day_close_grid_uses_the_day_that_just_closed():
    """At the 23:59 grid point the day that just closed is closed information: the ledger's prior-day high/low and the
    ladder's prior daily candle must be THAT day, in both builds (first draft used the day before it: RT-1 in ANGLES.md)."""
    bars = synth(12, seed=9)
    fund = synth_funding(12)
    t = 9 * 1440 + 1439
    d = slice(9 * 1440, 10 * 1440)
    hi, lo = float(np.max(bars["H"][d])), float(np.min(bars["L"][d]))
    for impl in ("vec", "replay"):
        f = CA.context_at(CA.slice_bars(bars, t + 1), t, "long", impl, fund)
        assert f["c_1d"] == (float(bars["O"][9 * 1440]), hi, lo, float(bars["C"][t])), impl
        assert f["stop_d_pct"] == (f["price"] - lo) / f["price"] * 100 or f["stop_d_pct"] != f["stop_d_pct"], impl
    CA.PRIOR_RULE = "cur_k_minus_1"
    try:
        g = CA.context_at(CA.slice_bars(bars, t + 1), t, "long", "vec", fund)
    finally:
        CA.PRIOR_RULE = "last_closed"
    assert g["stop_d_pct"] != f["stop_d_pct"] or (g["stop_d_pct"] != g["stop_d_pct"]), "the old rule must differ at a day close"
