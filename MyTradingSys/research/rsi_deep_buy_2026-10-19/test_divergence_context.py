"""Tests for divergence_context.py (RSI deep-buy Step I/J, card rsi-deep-divergence-context).

Expected values come from the card text, SHOT_REVIEW.md (d) K1-K10 (an independent public-data computation by the author of that review,
tolerance +-0.5 RSI) and hand arithmetic, never from the module. The K cases sit in the HOLDOUT window (2026-10), so no bar is loaded here:
each case is the table's pivots (close, RSI, optional wick) fed to the detector, and only detector outputs are asserted. Pivots the table
mentions but gives no price for (e.g. the 13:56 pivot of K1) carry a placeholder price chosen so the table's stated verdict is the only
possible one; they are marked 'placeholder'. Counts the table cannot support (P-any 3/8, 4/7) are not asserted."""
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "backtest" / "layers" / "rsi"))
import divergence_context as dc  # noqa: E402
from rsi_divergence import rsi_divergence  # noqa: E402


def P(i, price, rsi, atr=0.0):
    return {"i": i, "price": float(price), "rsi": float(rsi), "atr": float(atr)}


def fires(piv, rule="anchor", **kw):
    """{pivot position: firing dict} for kind 'div' only."""
    return {f["k"]: f for f in dc.pair_pivots(piv, rule, **kw) if f["kind"] == "div"}


def kinds(piv, rule="anchor", **kw):
    return {f["k"]: f["kind"] for f in dc.pair_pivots(piv, rule, **kw)}


# ------------------------------------------------------------------ stamp: never at the low (OPUS_FRAMING s2.2 item 5)
def _mini_ctx(close, rsi, n):
    c = np.asarray(close[:n], dtype="float64")
    return {"side": "long", "sgn": 1.0, "tf": 1, "n": n, "t": np.arange(n) * 60_000, "day": np.zeros(n, dtype="int64"),
            "open": c.copy(), "high": c + 0.5, "low": c - 0.5, "close": c, "pc": c, "wick": c - 0.5,
            "rsi": np.asarray(rsi[:n], dtype="float64"), "atr": np.full(n, 1.0), "seas": np.full(n, 1.0)}


# RSI path: 40 35 28 22 18 (entry <= 20 at idx 4, after >= 23), pivot lows at idx 5 (rsi 15, close 100) and idx 12 (rsi 20, close 95)
_RSI = [40, 35, 28, 22, 18, 15, 25, 30, 33, 30, 25, 22, 20, 28, 32, 36, 40, 44, 46, 48, 49, 49, 49, 49]
_CL = [110, 108, 106, 104, 102, 100, 103, 105, 106, 104, 100, 98, 95, 99, 101, 103, 105, 106, 107, 108, 108, 108, 108, 108]
_VAR = dc.VARIANTS[0]


def test_event_is_stamped_after_the_low_not_at_it():
    ev, _ = dc.build_variant(_mini_ctx(_CL, _RSI, len(_CL)), 1, "abs20", _VAR, 0)
    div = [e for e in ev if e["kind"] == "div"]
    assert len(div) == 1
    assert div[0]["b"] == 12 and div[0]["c"] == 13            # pivot bar 12, stamp bar 13, fill at the open of bar 14
    assert div[0]["c"] > div[0]["b"]
    assert div[0]["rsi_a"] == 15 and div[0]["rsi_b"] == 20


def test_no_event_until_the_confirming_bar_exists():
    # the series cut at bar 12 has no bar 13: the low is not yet a pivot, so a detector that stamps at the low would already have fired
    ev, _ = dc.build_variant(_mini_ctx(_CL, _RSI, 13), 1, "abs20", _VAR, 0)
    assert [e for e in ev if e["kind"] == "div"] == []


def test_outcome_fills_next_open_after_the_stamp():
    ctx = _mini_ctx(_CL, _RSI, len(_CL))
    ctx["open"] = np.arange(len(_CL), dtype="float64") + 1000.0     # open[i] = 1000 + i
    o = dc.outcome(ctx, 4, 13, 4)                                    # fill open[14] = 1014, exit open[18] = 1018
    assert o["gross"] == pytest.approx(1018 / 1014 - 1)
    assert o["net"] == pytest.approx(1018 / 1014 - 1 - 0.001)


def test_existing_module_stamps_one_bar_after_the_second_swing():
    close = [10, 9, 10, 11, 10, 9, 8.5, 9.5, 10]               # swing lows at idx 1 (9) and idx 6 (8.5)
    rsi = [50, 30, 40, 45, 40, 33, 35, 40, 45]                  # RSI higher at the second low
    ts = list(range(100, 109))
    ev = rsi_divergence(close, rsi, ts, 3, 10, "bullish")
    assert len(ev) == 1 and ev[0]["b_i"] == 6 and ev[0]["i"] == 7 and ev[0]["t"] == ts[7] > ts[6]
    assert rsi_divergence(close[:7], rsi[:7], ts[:7], 3, 10, "bullish") == []     # bar 7 absent: nothing yet


# ------------------------------------------------------------------ planted RSI lows 20 -> 30 -> 25 (SPEC Step J example)
def test_planted_20_30_25_price_l3_below_l1():
    piv = [P(0, 100, 20), P(1, 98, 30), P(2, 95, 25)]
    adj, anc, anyr = fires(piv, "adj"), fires(piv, "anchor"), fires(piv, "any")
    assert set(adj) == {1}                      # L3 vs L2: RSI 25 < 30, no divergence
    assert set(anc) == {1, 2} and anc[2]["a"] == 0 and anc[2]["skip"] == 1      # L3 vs the RSI-20 anchor, skipping L2
    assert set(anyr) == {1, 2} and anyr[2]["mult"] == 1 and anyr[2]["a"] == 0
    assert anc[2]["n_anchor"] == 2 and anc[2]["n_decline"] == 2


def test_planted_20_30_25_price_l3_above_l1():
    piv = [P(0, 100, 20), P(1, 102, 30), P(2, 101, 25)]
    for rule in ("adj", "anchor", "any"):
        assert fires(piv, rule) == {}
    assert kinds(piv, "anchor") == {1: "failure_swing", 2: "failure_swing"}      # higher price low + higher RSI low: own label
    assert dc.pair_pivots(piv, "adj") == []
    assert set(fires(piv, "split")) == {2}     # P-anchor-split: price reference may be any swing since the anchor (L2 at 102): permissive by design


def test_detector_that_flags_rsi_only_is_rejected():
    # the price condition is always checked: RSI higher alone must not fire
    assert fires([P(0, 100, 20), P(1, 105, 30)], "anchor") == {}
    assert fires([P(0, 100, 20), P(1, 100, 30)], "anchor") == {}              # equal price needs eps > 0
    assert set(fires([P(0, 100, 20), P(1, 100, 30)], "anchor", eps_pct=0.0005)) == {1}
    assert set(fires([P(0, 100, 20, 1.0), P(1, 100.05, 30, 1.0)], "anchor", eps_atr=0.1)) == {1}


# ------------------------------------------------------------------ K1-K10 (SHOT_REVIEW (d)); tolerance +-0.5 RSI
def case_k1():   # 1m 10-09, A 13:36 c82506.1 r15.4, 13:56 r45.5 (placeholder price above A), B 14:01 c82459.5 r35.4
    return [P(0, 82506.1, 15.4), P(1, 82520.0, 45.5), P(2, 82459.5, 35.4)]


def case_k2():   # 1m 10-09, 13:36 r15.4, A 13:40 c82493.2 r28.3, B 13:42 c82468.0 r30.9
    return [P(0, 82506.1, 15.4), P(1, 82493.2, 28.3), P(2, 82468.0, 30.9)]


def case_k4():   # 30m, A0 10-07 02:00 r19.9 (price placeholder), replaced by A1 14:30 c82978.1 r17.9; 01:30 r38.7; B 10-08 03:30 c82717.3 r31.3
    return [P(0, 83815.6, 19.9), P(1, 82978.1, 17.9), P(2, 83100.0, 38.7), P(3, 82717.3, 31.3)]


def case_k5():   # 30m, anchor A1; 7 planted firings (incl. K4's B and 15:30 r25.8), then B 10-08 17:00 c80700.0 r26.9 as firing #9
    mid = [(82717.3, 31.3), (82600, 30.0), (82500, 29.0), (82400, 28.0), (82300, 27.0), (82200, 26.5), (82150, 26.0), (82100, 25.8)]
    return [P(0, 83815.6, 19.9), P(1, 82978.1, 17.9)] + [P(2 + i, p, r) for i, (p, r) in enumerate(mid)] + [P(10, 80700.0, 26.9)]


def case_k6():   # 5m 10-15, A 13:25 c80192.6 r29.1, B 13:50 c79842.4 r30.7
    return [P(0, 80192.6, 29.1), P(1, 79842.4, 30.7)]


def case_k8():   # 15m 10-18, A 14:45 c81060.2 r23.2; 15:30 r26 and 16:45 r27 (with an r30 placeholder pivot between), 19:30, 20:00 r28.2, B 20:30 c80818.5 r31.5
    return [P(0, 81060.2, 23.2), P(1, 81000.0, 26.0), P(2, 81080.0, 30.0), P(3, 80950.0, 27.0), P(4, 80900.0, 27.5),
            P(5, 80880.0, 28.2), P(6, 80818.5, 31.5)]


def case_k9(basis):   # 5m 10-19, A 10:30 c82118.3 r24.6 (wick 82058.0), 11:10 r32.7 (placeholder), B 11:30 c82115.8 r32.3 (wick 82089.0)
    a, x, b = (82118.3, 82120.0, 82115.8) if basis == "close" else (82058.0, 82100.0, 82089.0)
    return [P(0, a, 24.6), P(1, x, 32.7), P(2, b, 32.3)]


def bear(pivots):
    return dc.mirror(pivots)


def test_k1_anchor_true_adj_false_any_true():
    p = case_k1()
    assert 2 in fires(p, "anchor") and fires(p, "anchor")[2]["a"] == 0
    assert 2 not in fires(p, "adj")                                  # 13:56 r45.5 is the previous pivot
    assert 2 in fires(p, "any")


def test_k2_chain_and_adjacent():
    p = case_k2()
    assert 2 in fires(p, "adj") and 2 in fires(p, "anchor")
    assert fires(p, "any")[2]["mult"] == 2                           # diverges from both earlier lows
    assert 1 in fires(p, "adj")                                      # 13:36 -> 13:40 is the first link of the chain


def test_k3_bearish_non_adjacent():
    p = bear([P(0, 83180.8, 74.5), P(1, 83100.0, 66.6), P(2, 83266.0, 70.0)])   # 14:30 r66.6 is previous: placeholder price below A
    assert 2 in fires(p, "anchor") and 2 not in fires(p, "adj")


def test_k4_anchor_replacement_and_firing_number():
    p = case_k4()
    f = fires(p, "anchor")
    assert 1 not in f                                                # A1 has a LOWER RSI than A0: not a divergence, it replaces the anchor
    assert f[3]["a"] == 1 and f[3]["n_anchor"] == 1                  # firing #1 against the 14:30 anchor
    assert 3 not in fires(p, "adj")                                  # previous pivot r38.7


def test_k5_adj_true_and_firing_number_depends_on_episode_reset():
    p = case_k5()
    f = fires(p, "anchor")
    assert f[10]["n_anchor"] == 9 and f[10]["a"] == 1                # #9 when the episode does not end at RSI 50.9
    assert 10 in fires(p, "adj")                                     # previous pivot 15:30 r25.8
    # with the episode cut at 10-08 09:30 (RSI 50.9) the later pivots form a NEW episode whose anchor is the first RSI low in it
    later = [P(0, 82100.0, 25.8), P(1, 80700.0, 26.9)]
    assert dc.pair_pivots(later, "anchor") == [] or fires(later, "anchor")[1]["n_anchor"] == 1


def test_episode_bounds_reset_rule():
    # RSI: dips under 20, rebounds to 50.9, falls back under 20: end 50 -> 2 episodes, end 60 -> the second start is inside the first
    rsi = np.array([40, 30, 18, 25, 35, 50.9, 45, 30, 19, 25, 35, 45])
    starts = [2, 8]
    assert dc.episode_bounds(rsi, starts, 50.0) == [(2, 5), (8, 12)]
    assert dc.episode_bounds(rsi, starts, 60.0) == [(2, 12)]
    assert dc.episode_bounds(rsi, starts, 40.0) == [(2, 5), (8, 11)]       # 35 is not above 40, so the first episode still ends at 50.9; the second ends at 45


def test_k6_small_difference():
    p = case_k6()
    assert 1 in fires(p, "anchor") and 1 in fires(p, "adj") and 1 in fires(p, "any")
    assert 1 not in fires(p, "anchor", min_diff=2.0)                 # RSI difference 1.6 < 2
    assert 1 in fires(p, "anchor", min_diff=1.5)


def test_k7_basis_decides_bearish():
    close = bear([P(0, 81250.4, 76.9), P(1, 81270.0, 69.1)])
    wick = bear([P(0, 81390.5, 76.9), P(1, 81325.4, 69.1)])           # wick high is LOWER at B
    assert 1 in fires(close, "anchor")
    assert 1 not in fires(wick, "anchor")


def test_k8_multiplicity_firing_count_and_adjacency():
    p = case_k8()
    f = fires(p, "anchor")
    assert f[6]["n_anchor"] == 5 and set(f) == {1, 3, 4, 5, 6}        # 15:30, 16:45, 19:30, 20:00, 20:30 against the 14:45 anchor
    assert 5 in fires(p, "adj") and 6 in fires(p, "adj")             # 20:00 -> 20:30 adjacent
    assert 3 not in fires(p, "adj")                                  # 16:45 is P-adj false (previous pivot r30)


def test_k9_equal_low():
    assert 2 in fires(case_k9("close"), "anchor")                    # close lower by 2.5 USD, eps 0
    assert 2 not in fires(case_k9("close"), "adj")                   # 11:10 r32.7 is previous
    assert 2 not in fires(case_k9("wick"), "anchor")                 # wick low is HIGHER: no divergence on the wick basis


def test_k10_failure_swing_not_divergence():
    p = bear([P(0, 83090.1, 73.1), P(1, 83037.3, 62.9)])
    for rule in ("adj", "anchor", "any", "split"):
        assert fires(p, rule) == {}
    assert kinds(p, "anchor") == {1: "failure_swing"}


def test_mirror_is_an_involution_and_flips_the_pairing():
    p = [P(0, 100, 20), P(1, 98, 30)]
    assert dc.mirror(dc.mirror(p)) == p
    bull = fires(p, "anchor")
    assert set(bull) == {1} and set(fires(dc.mirror(p), "anchor")) == set()


# ------------------------------------------------------------------ tolerance: +-0.5 RSI must not change a verdict unless the margin is < 1
CASES = {
    "K1": (case_k1, [("anchor", {}, 2, True), ("adj", {}, 2, False)]),
    "K2": (case_k2, [("anchor", {}, 2, True), ("adj", {}, 2, True)]),
    "K4": (case_k4, [("anchor", {}, 3, True), ("adj", {}, 3, False)]),
    "K6": (case_k6, [("anchor", {}, 1, True), ("anchor", {"min_diff": 2.0}, 1, False)]),
    "K8": (case_k8, [("anchor", {}, 6, True), ("adj", {}, 3, False)]),
    "K9": (lambda: case_k9("close"), [("anchor", {}, 2, True), ("adj", {}, 2, False)]),
}
INSIDE_TOLERANCE = {("K6", "min_diff"), ("K9", "adj")}     # margins 0.4 RSI (diff 1.6 vs 2; 32.3 vs 32.7): the table cannot call these


@pytest.mark.parametrize("name", sorted(CASES))
def test_verdicts_stable_under_half_point_rsi_error(name):
    make, checks = CASES[name]
    for rule, kw, k, expected in checks:
        flipped = False
        for sgn in (+0.5, -0.5):
            piv = make()
            for j, q in enumerate(piv):
                q["rsi"] += sgn if j < k else -sgn          # adversarial: earlier pivots one way, the tested pivot the other
            if (k in fires(piv, rule, **kw)) != expected:
                flipped = True
        key = (name, "min_diff" if "min_diff" in kw else rule)
        assert flipped == (key in INSIDE_TOLERANCE), (name, rule, kw)


# ------------------------------------------------------------------ pipeline helpers
def test_match_controls_one_to_one_nearest_atr_within_rsi_tolerance():
    ev = [{"rsi_b": 20.0, "atr_pct": 0.010}, {"rsi_b": 20.5, "atr_pct": 0.010}]
    pool = [{"rsi_b": 21.0, "atr_pct": 0.0101}, {"rsi_b": 22.0, "atr_pct": 0.0099}, {"rsi_b": 30.0, "atr_pct": 0.010}]
    m = dc.match_controls(ev, pool)
    assert m[0] is pool[0] and m[1] is pool[1]                       # nearest ATR first, then the remaining one in tolerance; the r30 never
    assert dc.match_controls(ev + [{"rsi_b": 21.0, "atr_pct": 0.01}], pool)[2] is None   # pool exhausted for the third event


def test_fit_logit_intercept_only_is_the_logit_of_the_mean():
    y = np.array([1.0] * 30 + [0.0] * 70)
    w = dc.fit_logit(np.zeros((100, 1)), y)
    assert w[0] == pytest.approx(np.log(0.3 / 0.7), abs=1e-6)


def test_logloss_hand_value():
    assert dc.logloss(np.array([0.8]), np.array([1.0]))[0] == pytest.approx(-np.log(0.8))
    assert dc.logloss(np.array([0.8]), np.array([0.0]))[0] == pytest.approx(-np.log(0.2))


def test_level_only_p_uses_only_resolved_entries():
    rt, win = np.array([10, 20, 30]), np.array([1.0, 0.0, 1.0])
    assert dc.level_only_p(rt, win, 5) == pytest.approx(1 / 2)          # none resolved: (0+1)/(0+2)
    assert dc.level_only_p(rt, win, 20) == pytest.approx((1 + 1) / (2 + 2))
    assert dc.level_only_p(rt, win, 99) == pytest.approx((2 + 1) / (3 + 2))


def test_walk_forward_ignores_the_future():
    rng = np.random.default_rng(3)
    base = 1_700_000_000_000
    ev = []
    for i in range(120):
        ev.append({"kind": "div", "c": i, "t": base + i * 3_600_000 * 7, "tf": 15, "day": (base + i * 3_600_000 * 7) // dc.DAY_MS,
                   **{f: float(rng.normal()) for f in dc.MODEL_FEATURES},
                   "o16": {"gross": float(rng.normal() * 0.01), "net": 0.0}})
    rtw = (np.array([base]), np.array([1.0]))
    a = dc.walk_forward(ev, rtw, 16, 0, 10 ** 15)
    ev2 = [dict(e) for e in ev]
    ev2[-1]["o16"] = {"gross": 99.0, "net": 98.9}                         # change only the LAST outcome
    ev2[-1]["ret24"] = 50.0
    b = dc.walk_forward(ev2, rtw, 16, 0, 10 ** 15)
    assert len(a) == len(b) == 120
    assert [r["p_model"] for r in a[:-1]] == [r["p_model"] for r in b[:-1]]
    assert [r["p_div"] for r in a[:-1]] == [r["p_div"] for r in b[:-1]]


# ------------------------------------------------------------------ causality of the context vector (planted future bars)
def _synthetic_1m(days, seed=11):
    rng = np.random.default_rng(seed)
    n = days * 1440
    t0 = int(np.datetime64("2022-01-03T00:00", "ms").astype("int64"))
    t = t0 + np.arange(n, dtype="int64") * 60_000
    close = 40_000 * np.exp(np.cumsum(rng.normal(0, 0.0007, n)))
    op = np.r_[close[0], close[:-1]]
    hi = np.maximum(op, close) * (1 + np.abs(rng.normal(0, 0.0003, n)))
    lo = np.minimum(op, close) * (1 - np.abs(rng.normal(0, 0.0003, n)))
    vol = rng.uniform(5, 15, n)
    return {"open_time": t, "open": op, "high": hi, "low": lo, "close": close, "volume": vol, "taker_buy_volume": vol * rng.uniform(0.3, 0.7, n)}


def _cut(d, n):
    return {k: v[:n].copy() for k, v in d.items()}


def test_context_arrays_do_not_see_future_bars():
    d = _synthetic_1m(60)
    full = dc.build_context(d, 15, "long")
    n_cut = 45 * 1440 + 7 * 60                                            # cut at 07:00 of day 46
    part = dc.build_context(_cut(d, n_cut), 15, "long")
    m = int((n_cut // 15) - 1)                                            # every complete 15m bar of the cut series
    keys = ["rsi", "atr", "a1", "volpct", "rangez", "rangez_prev", "volz", "takerz", "htf_break_a", "htf_break_b", "seas",
            "zz_s_dir", "zz_s_dist", "zz_s_brk", "zz_m_dir", "zz_m_dist", "zz_l_dir", "zz_l_dist"]
    for k in keys:
        a, b = full[k][:m], part[k][:m]
        assert np.array_equal(a, b, equal_nan=True), k
    assert np.isfinite(full["a1"][m - 1]) and np.isfinite(full["rangez"][m - 1])      # the comparison is not vacuous


def test_event_features_unchanged_when_future_bars_are_replaced():
    d = _synthetic_1m(60)
    c = 40 * 96 + 30                                                      # a 15m bar on day 40
    t_end = int(d["open_time"][0]) + (c + 1) * 15 * 60_000
    n_keep = (t_end - int(d["open_time"][0])) // 60_000                   # 1m bars up to the close of bar c
    d2 = {k: v.copy() for k, v in d.items()}
    rng = np.random.default_rng(99)
    for k in ("open", "high", "low", "close"):
        d2[k][n_keep:] = d[k][n_keep:] * (1 + rng.normal(0.05, 0.05, len(d[k]) - n_keep))
    d2["volume"][n_keep:] *= 9.0
    a, b = dc.build_context(d, 15, "long"), dc.build_context(d2, 15, "long")
    fa, fb = dc.event_features(a, c - 40, c - 1, c), dc.event_features(b, c - 40, c - 1, c)
    assert set(fa) == set(fb)
    for k in fa:
        assert (np.isnan(fa[k]) and np.isnan(fb[k])) or fa[k] == fb[k], k
    assert np.isfinite(fa["ret24"]) and np.isfinite(fa["rangez"]) and np.isfinite(fa["volpct"]), "vacuous: features must be finite"


def test_event_features_hand_values():
    # ret over 1h in 1h-ATR units, drawdown from the 24h high, sweep depth: hand arithmetic on a tiny planted context
    n = 400
    tf = 15
    pc = np.full(n, 100.0)
    pc[300] = 120.0                                                       # the high, 24h window = 96 bars -> inside the window at c = 380
    pc[376:381] = [110.0, 108.0, 106.0, 104.0, 102.0]
    ctx = {"tf": tf, "a1": np.full(n, 2.0), "pc": pc, "far": pc + 1.0, "wick": pc - 0.5, "rangez": np.zeros(n), "rangez_prev": np.zeros(n),
           "volpct": np.zeros(n), "atr": np.full(n, 1.0), "close": np.full(n, 100.0), "volz": np.zeros(n), "takerz": np.zeros(n),
           "session": np.zeros(n, dtype=int), "rsi": np.full(n, 40.0), "htf_break_a": np.zeros(n), "htf_break_b": np.zeros(n), "seas": np.ones(n)}
    for tag in "sml":
        for k in ("dir", "dist", "brk"):
            ctx[f"zz_{tag}_{k}"] = np.zeros(n)
    f = dc.event_features(ctx, 370, 379, 380)
    assert f["ret1"] == pytest.approx((102.0 - 110.0) / 2.0)           # close[380] - close[376], bars of 15m: 4 bars = 1h
    assert f["dd"] == pytest.approx((121.0 - 102.0) / 2.0)               # far = pc + 1 at the high bar 300: (121 - 102) / ATR1h
    assert f["hours_since_high"] == pytest.approx((380 - 300) * 15 / 60.0)
    assert f["speed"] == pytest.approx(f["dd"] / f["hours_since_high"])
    assert f["sweep"] == pytest.approx((99.5 - 103.5) / 2.0)             # min of prior 24h wick lows 99.5 vs wick low at b=379 (104.0 - 0.5)
