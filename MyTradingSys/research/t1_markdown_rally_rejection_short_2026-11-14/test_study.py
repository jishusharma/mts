"""Synthetic-only tests for study.py (no F:\\ cache reads, no scripts/sched). Expected numbers are worked by hand from FORMULAS.md and PRE_REG.md.
Causality tests must FAIL with STUDY_BUG=1 (pivots, VWAP, phase leak) and PHASE_LAG=0 (phase leaks): see test_runs.txt."""
import sys
import json
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import study as s  # noqa: E402

D0 = 18000  # epoch day number of the first synthetic UTC day (midnight aligned)
BASE = D0 * s.DAY


def synth15(days=40, seed=1, drift=0.0, vol=0.004):
    """15m random-walk bars from UTC midnight of day D0."""
    rng = np.random.default_rng(seed)
    n = days * 96
    t = BASE + np.arange(n, dtype=np.int64) * s.MIN15
    r = rng.normal(drift, vol, n)
    c = 100.0 * np.exp(np.cumsum(r))
    o = np.r_[100.0, c[:-1]]
    h = np.maximum(o, c) * (1 + np.abs(rng.normal(0, 0.0015, n)))
    l = np.minimum(o, c) * (1 - np.abs(rng.normal(0, 0.0015, n)))
    v = rng.lognormal(3, 0.5, n)
    return t, o, h, l, c, v


def ptab_all(days, label=s.MD, cyc=3):
    d = np.arange(D0 - 2, D0 + days + 2)
    return d, np.full(len(d), label, dtype=np.int8), np.full(len(d), cyc, dtype=np.int8)


def cut(bars, k):
    return tuple(a[:k] for a in bars)


# ------------------------------------------------------------------ formulas by hand (FORMULAS.md worked examples)
def test_formula_worked_examples():
    r = s.rsi_wilder(np.array([10.0, 12, 11, 14]), 3)
    assert np.isnan(r[:3]).all() and r[3] == pytest.approx(100 - 100 / 6, abs=1e-9)        # s1: 83.3333
    e = s.ema_series(np.array([50.0, 55, 45, 60]), 3)
    assert e[2] == pytest.approx(50.0) and e[3] == pytest.approx(55.0)                    # s4
    w = s.wma_series(np.array([50.0, 55, 45]), 3)
    assert w[2] == pytest.approx(295 / 6)                                                  # s5: 49.1667
    h, l, c = np.array([10.0, 11, 12, 11]), np.array([9.0, 9, 10, 9]), np.array([9.5, 10.5, 11.5, 10])
    assert s.atr_sma(h, l, c, 3)[3] == pytest.approx((2 + 2 + 2.5) / 3)                    # s12: 2.1667
    assert s.rsi_wilder(np.full(6, 5.0), 3)[3] == 50.0                                     # flat -> 50 (FORMULAS deviation)


def test_resample_utc_aligned_and_complete_only():
    t, o, h, l, c, v = synth15(days=2)
    k = np.ones(len(t), bool)
    k[5] = False                                    # one missing 15m bar -> its 1h bucket (bars 4..7) is dropped
    th, to, thh, tl, tc, tv = s.resample(t[k], o[k], h[k], l[k], c[k], v[k], 4)
    assert len(th) == 48 - 1 and (th % s.HOUR == 0).all() and BASE + s.HOUR not in th
    j = int(np.flatnonzero(th == BASE + 2 * s.HOUR)[0])
    assert to[j] == o[8] and tc[j] == c[11] and thh[j] == h[8:12].max() and tl[j] == l[8:12].min() and tv[j] == pytest.approx(v[8:12].sum())


def test_vwap_anchored_midnight_by_hand():
    t = BASE + np.arange(192, dtype=np.int64) * s.MIN15
    h = np.full(192, 10.0); l = np.full(192, 8.0); c = np.full(192, 9.0)   # typical price 9
    c[1] = 12.0; h[1] = 12.0                                              # bar 1: tp = (12+8+12)/3
    v = np.ones(192)
    vw, st, ln = s.vwap_15m(t, h, l, c, v)
    assert vw[0] == pytest.approx(9.0) and vw[1] == pytest.approx((9 + 32 / 3) / 2)
    assert vw[96] == pytest.approx(9.0) and vw[97] == pytest.approx(9.0)  # reset at 00:00 UTC of day 2: no memory of day 1's spike


# ------------------------------------------------------------------ exit hand cases
def win(kw=None):
    n = s.HOLD
    o, h, l = np.full((1, n), 100.0), np.full((1, n), 100.5), np.full((1, n), 99.5)
    for (name, k), val in (kw or {}).items():
        {"o": o, "h": h, "l": l}[name][0, k] = val
    return o, h, l


def run(o, h, l, close=99.0, stop=102.0, target=96.0):
    off, px, why = s.sim_windows(o, h, l, np.array([close]), np.array([stop]), np.array([target]))
    return int(off[0]), float(px[0]), int(why[0])


def test_exit_stop_touch():
    o, h, l = win({("h", 3): 102.5})
    assert run(o, h, l) == (3, 102.0, 1)


def test_exit_stop_gap_fills_at_open():
    o, h, l = win({("o", 2): 104.0, ("h", 2): 105.0})
    assert run(o, h, l) == (2, 104.0, 1)


def test_exit_tie_stop_wins():
    o, h, l = win({("h", 1): 103.0, ("l", 1): 95.0})
    assert run(o, h, l) == (1, 102.0, 1)


def test_exit_target_and_target_gap_fill_at_level():
    o, h, l = win({("l", 5): 95.5})
    assert run(o, h, l) == (5, 96.0, 2)
    o, h, l = win({("o", 4): 94.0, ("l", 4): 93.0, ("h", 4): 94.5})
    assert run(o, h, l) == (4, 96.0, 2)                    # PRE_REG: target "fills at the level"


def test_exit_time_at_close_of_24th_bar():
    o, h, l = win()
    assert run(o, h, l, close=99.0) == (23, 99.0, 0)


# ------------------------------------------------------------------ trade construction by hand
def hand_coin(h5=103.0, c5=99.0, P=101.0, atr=1.0, extra=None, n=40):
    th = BASE + np.arange(n, dtype=np.int64) * s.HOUR
    o, c = np.full(n, 100.0), np.full(n, 100.0)
    h, l = np.full(n, 100.4), np.full(n, 99.8)
    h[5], l[5], c[5] = h5, 99.5, c5
    o[6] = 99.5
    for k, v in (extra or {}).items():
        arr, idx = k
        {"o": o, "h": h, "l": l, "c": c}[arr][idx] = v
    return dict(th=th, o=o, h=h, l=l, c=c, P=np.full(n, P), R1=np.full(n, 105.0), S1=np.full(n, 95.0), atr=np.full(n, atr), hm=np.ones(n, bool),
                vw=np.full(n, 1e9), ph=np.full(n, s.MD, dtype=np.int8), cy=np.full(n, 3, dtype=np.int8))


def test_hand_trade_target_stop_distance_and_fee():
    pc = hand_coin(extra={("l", 8): 94.5})
    cd = s.coin_candidates(pc, 0, s.FAR)
    assert list(cd["i"]) == [5] and cd["lvl"][0] == 0                                    # P rejection (R1 untouched)
    entry, D = 99.5, max(103.0 - 99.5, 1.0, 0.012 * 99.5)                                  # D = signal-bar high - entry = 3.5
    assert cd["tk_entry"][0] == entry and cd["tk_D"][0] == pytest.approx(D) and cd["tk_ok"][0]
    assert (cd["tk_off"][0], cd["tk_why"][0]) == (2, 2)                                     # target S1 = 95 touched on the third bar
    assert cd["tk_gross"][0] == pytest.approx((99.5 - 95.0) / 3.5)
    assert cd["tk_cost"][0] == pytest.approx(0.0012 * 99.5 / 3.5)                          # fee formula: 12 bp of notional in R
    tr = s.trades_for({"X": cd}, "main")
    assert len(tr["t"]) == 1
    assert s.summarize(tr, ci=False)["net"] == pytest.approx((99.5 - 95.0) / 3.5 - 0.0012 * 99.5 / 3.5)


def test_hand_trade_stop_floor_and_stop_exit():
    pc = hand_coin(h5=101.1, c5=100.8, atr=0.5, extra={("o", 6): 100.8, ("h", 7): 103.0})
    cd = s.coin_candidates(pc, 0, s.FAR)
    D = 0.012 * 100.8                                                                      # floor beats (h - entry = 0.3) and ATR 0.5
    assert cd["tk_D"][0] == pytest.approx(D)
    assert (cd["tk_off"][0], cd["tk_why"][0]) == (1, 1) and cd["tk_gross"][0] == pytest.approx(-1.0)   # stop at entry + D = 102.0096 < 103
    assert cd["tk_cost"][0] == pytest.approx(0.0012 / 0.012)                              # floor trade: 0.10 R


def test_hand_trade_atr_dominates():
    pc = hand_coin(h5=100.9, c5=100.3, P=100.5, atr=2.0, extra={("o", 6): 100.7})
    cd = s.coin_candidates(pc, 0, s.FAR)
    assert cd["tk_D"][0] == pytest.approx(2.0)


def test_skip_rules():
    pc = hand_coin(extra={("o", 6): 95.5})                                                # target 95 only 0.5 away < 0.5 x D(=7.5)
    cd = s.coin_candidates(pc, 0, s.FAR)
    assert not cd["tk_ok"][0]
    pc = hand_coin(extra={("o", 6): 94.0})                                                # entry below the target
    assert not s.coin_candidates(pc, 0, s.FAR)["tk_ok"][0]


def test_r1_rejection_targets_pivot_and_higher_level_wins():
    pc = hand_coin(h5=106.0, c5=100.5, P=101.0)                                           # high > R1 (105), close < P and < R1 -> R1 wins, target P
    cd = s.coin_candidates(pc, 0, s.FAR)
    assert cd["lvl"][0] == 1 and cd["tk_tgt"][0] == 101.0


def test_one_position_per_coin():
    cd = dict(i=np.array([10, 12, 16, 17]), tk_ok=np.ones(4, bool), tk_off=np.array([5, 0, 3, 0]))
    # trade at 10 exits on bar 16 -> signal 12 ignored, signal 16 (close after the exit) allowed, then exits bar 20 -> 17 ignored
    assert list(s.pick_trades(cd, np.ones(4, bool), "tk")) == [0, 2]


def test_dev_window_has_no_bar_outside_it():
    pc = s.prepare_coin(*synth15(days=60), ptab_all(60))
    lo, hi = BASE + 10 * s.DAY, BASE + 30 * s.DAY
    cd = s.coin_candidates(pc, lo, hi)
    assert len(cd["t"]) > 10 and cd["t"].min() >= lo and cd["t"].max() < hi


# ------------------------------------------------------------------ causality
CAUSAL_KEYS = ["P", "R1", "S1", "atr", "vw", "hm", "ph", "cy"]


def same(a, b):
    return np.array_equal(a, b) if a.dtype == bool or a.dtype.kind in "iu" else np.allclose(a, b, equal_nan=True)


def test_pivots_use_only_prior_complete_day():
    bars = synth15(days=6)
    pc = s.prepare_coin(*bars, ptab_all(6))
    t, o, h, l, c, v = bars
    d = (t // s.DAY) - D0
    # hand pivot of day 2 applies to every 1h bar of day 3
    m2 = d == 2
    H, L, C = h[m2].max(), l[m2].min(), c[m2][-1]
    P = (H + L + C) / 3
    day3 = (pc["th"] // s.DAY) - D0 == 3
    assert np.allclose(pc["P"][day3], P) and np.allclose(pc["R1"][day3], 2 * P - L) and np.allclose(pc["S1"][day3], 2 * P - H)
    # poke day 3 (the signal day) -> its pivots must not move; poke day 2 -> they must
    for k, expect_same in ((3, True), (2, False)):
        t2, o2, h2, l2, c2, v2 = (a.copy() for a in bars)
        m = d == k
        h2[m] *= 1.07; l2[m] *= 0.93
        pc2 = s.prepare_coin(t2, o2, h2, l2, c2, v2, ptab_all(6))
        assert same(pc["P"][day3], pc2["P"][day3]) == expect_same


@pytest.mark.parametrize("k", [96 * 3 + 40, 96 * 5 + 8, 96 * 8 + 52])
def test_indicators_unchanged_when_future_bars_removed_or_poked(k):
    bars = synth15(days=12, seed=7)
    full = s.prepare_coin(*bars, ptab_all(12))
    k = (k // 4) * 4                                                                       # cut on a 1h boundary
    part = s.prepare_coin(*cut(bars, k), ptab_all(12))
    nb = k // 4
    poked = [a.copy() for a in bars]
    for a in poked[1:5]:
        a[k:] *= 1.0 + np.random.default_rng(3).uniform(-0.1, 0.1, len(a) - k)
    pk = s.prepare_coin(*poked, ptab_all(12))
    assert nb > 40
    for key in CAUSAL_KEYS:
        assert same(full[key][:nb], part[key][:nb]), f"{key} depends on bars after the signal (truncation)"
        assert same(full[key][:nb], pk[key][:nb]), f"{key} depends on bars after the signal (poke)"


def test_hm_and_vwap_read_at_signal_close():
    bars = synth15(days=10, seed=11)
    pc = s.prepare_coin(*bars, ptab_all(10))
    t, o, h, l, c, v = bars
    i = 96 * 6 + 4 * 9 + 0                                                                # 1h bar 09:00 of day 6 starts at 15m index i; closes at i+4
    j = int(np.flatnonzero(pc["th"] == t[i])[0])
    # VWAP through the signal close = bars 96*6 .. i+3 (the 15m bar opening 45 min after the 1h open is the last one)
    sl = slice(96 * 6, i + 4)
    tp = (h[sl] + l[sl] + c[sl]) / 3
    assert pc["vw"][j] == pytest.approx((tp * v[sl]).sum() / v[sl].sum())
    # HM from the 30m bar that closes with the 1h bar: recompute on 30m closes sliced to end there
    t30, _, _, _, c30, _ = s.resample(t, o, h, l, c, v, 2)
    e = int(np.flatnonzero(t30 == t[i] + s.HOUR // 2)[0])
    rs = s.rsi_wilder(c30[:e + 1], 9)
    assert pc["hm"][j] == bool(s.wma_series(rs, 21)[-1] > rs[-1] and s.wma_series(rs, 21)[-1] > s.ema_series(rs, 3)[-1])


def test_phase_for_day_uses_closes_through_prior_day_only():
    rng = np.random.default_rng(5)
    r = np.r_[rng.normal(0.001, 0.02, 300), rng.normal(-0.012, 0.02, 200), rng.normal(0.002, 0.02, 200)]
    c = 100 * np.exp(np.cumsum(r))
    dn = np.arange(len(c)) + D0
    hits, tested = 0, 0
    for d in range(D0 + 210, D0 + 690, 7):
        full = s.markdown_for_day(dn, c, d)
        trunc = s.markdown_for_day(dn[dn <= d - 1], c[dn <= d - 1], d)
        assert full == trunc, f"label for day {d} changes when day {d}'s own close is removed"
        hits += bool(full); tested += 1
    assert 3 < hits < tested - 3                                                          # the sample really contains both labels


def test_phase_flip_hand_case():
    c = np.full(300, 100.0)
    c[-1] = 40.0                                                                          # only the last day's close breaks below SMA50 / SMA200
    dn = np.arange(300) + D0
    d = D0 + 299
    assert s.markdown_for_day(dn, c, d, lag=0) is True                                    # same-day close would have flagged MARKDOWN
    assert s.markdown_for_day(dn[:-1], c[:-1], d, lag=1) is False                         # but at the prior close nothing was visible
    assert s.markdown_for_day(dn, c, d, lag=1) is False
    assert s.markdown_for_day(dn[:-1], c[:-1], d, lag=0) is None                          # lag 0 cannot even be evaluated on truncated data


# ------------------------------------------------------------------ planted edge and zero-drift harness
def harness(drift, seed, variant="neither"):
    bars = synth15(days=420, seed=seed, drift=drift)
    pc = s.prepare_coin(*bars, ptab_all(420))
    cd = s.coin_candidates(pc, BASE + 5 * s.DAY, s.FAR)
    return s.trades_for({"X": cd}, variant), cd


def test_zero_drift_gross_zero_net_minus_fee_and_planted_drift_reads():
    gs, ns, costs = [], [], []
    for seed in range(1, 7):
        tr, _ = harness(0.0, seed)
        g, c = tr["gross"], tr["cost"]
        gs.append(g); costs.append(c)
        assert (np.isclose(tr["cost"], 0.0012 * tr["entry"] / tr["D"])).all()
    g, c = np.concatenate(gs), np.concatenate(costs)
    assert len(g) > 400
    se = g.std(ddof=1) / np.sqrt(len(g))
    assert abs(g.mean()) < 4 * se + 0.02, (g.mean(), se)                                  # zero drift, no look-ahead: gross ~ 0
    assert (g - c).mean() == pytest.approx(g.mean() - c.mean())                           # net = gross - fee
    assert (g - c).mean() < -0.03 and c.mean() > 0.04                                     # net ~ -fee
    dr = np.concatenate([harness(-0.0004, seed)[0]["gross"] for seed in range(1, 7)])     # planted downward drift
    assert dr.mean() > g.mean() + 0.15 and dr.mean() > 0.1


def test_placebo_zero_drift_is_not_significant_and_returns_fields():
    bars = synth15(days=300, seed=21)
    pc = s.prepare_coin(*bars, ptab_all(300))
    preps = {"X": pc}
    cd = s.coin_candidates(pc, BASE + 5 * s.DAY, s.FAR)
    tr = s.trades_for({"X": cd}, "neither")
    pb = s.placebo(tr, preps, BASE + 5 * s.DAY, s.FAR, draws=100)
    assert pb["n"] > 100 and 0 < pb["p"] <= 1 and abs(pb["excess"]) < 0.4


def test_boot_days_ci_brackets_mean_and_is_seeded():
    rng = np.random.default_rng(0)
    day = np.repeat(np.arange(200), 3)
    net = rng.normal(0.1, 1.0, 600)
    a = s.boot_days(day, net)
    assert a == s.boot_days(day, net) and a[0] < net.mean() < a[1]


def test_summary_ex_best5_and_breakeven_by_hand():
    tr = s.empty_trades()
    tr.update(t=np.arange(8, dtype=np.int64), day=np.arange(8, dtype=np.int64), gross=np.array([10.0, 8, 6, 4, 2, -1, -1, -1]), cost=np.zeros(8), hold=np.zeros(8),
              why=np.zeros(8, dtype=np.int8))
    sm = s.summarize(tr, ci=False)
    assert sm["exbest5"] == pytest.approx(-1.0) and sm["net"] == pytest.approx(27 / 8)
    assert sm["win"] == pytest.approx(5 / 8) and sm["be_win"] == pytest.approx(1 / (6 + 1))


def test_verdict_rules():
    ok = dict(n=500, days=100, net=0.1, ci_lo=0.01, exbest5=0.05)
    assert s.verdict(ok, dict(excess=0.1, p=0.01)) == "PASS"
    assert s.verdict(ok, dict(excess=0.1, p=0.2)) == "FAIL"
    assert s.verdict(dict(ok, n=149), dict(excess=0.1, p=0.01)) == "UNDERPOWERED"
    assert s.verdict(dict(ok, days=39), dict(excess=0.1, p=0.01)) == "UNDERPOWERED"


# ------------------------------------------------------------------ protocol
def test_val_refuses_without_committed_frozen_json(tmp_path, monkeypatch):
    monkeypatch.setattr(s, "HERE", tmp_path)
    assert "missing" in s.check_frozen()


def test_load_npz_truncates_at_hi_and_reads_either_time_key(tmp_path):
    t = BASE + np.arange(50, dtype=np.int64) * s.MIN15
    a = np.linspace(1, 2, 50)
    np.savez(tmp_path / "a.npz", ts=t, o=a, h=a, l=a, c=a, v=a)
    got = s.load_npz(tmp_path / "a.npz", hi=int(t[30]))
    assert len(got[0]) == 30 and got[0][-1] < t[30]
