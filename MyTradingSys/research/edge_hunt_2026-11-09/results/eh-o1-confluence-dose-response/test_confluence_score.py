"""Tests for confluence_score.py (T13, eh-o1). Hand-built bars for every rule, split refusal, no-lookahead, fee/R."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import confluence_score as cs  # noqa: E402

H = 3600000
DAY = 86400000


def bars(rows, t0=0, tf=H):
    a = np.asarray(rows, dtype=float)
    n = len(a)
    return {"t": t0 + np.arange(n, dtype=np.int64) * tf, "o": a[:, 0].copy(), "h": a[:, 1].copy(),
            "l": a[:, 2].copy(), "c": a[:, 3].copy(), "tf": tf}


def flat(n, px=100.0):
    return [(px, px + 0.5, px - 0.5, px) for _ in range(n)]


# ---------------- pivots ----------------
def test_pivot5_needs_five_right_bars():
    h = np.array([1, 2, 3, 4, 5, 10, 5, 4, 3, 2, 1], dtype=float)
    l = h - 0.5
    ph, pl = cs.pivots(h, l, 5)
    assert ph[5] and ph.sum() == 1
    # with only 4 right bars the pivot is not marked
    ph2, _ = cs.pivots(h[:10], l[:10], 5)
    assert not ph2.any()


def test_pivot_tie_left_strict():
    h = np.array([0, 1, 2, 3, 4, 10, 10, 5, 4, 3, 2, 1, 0], dtype=float)
    ph, _ = cs.pivots(h, h - 1, 5)
    assert ph[5] and not ph[6]  # first of a tie wins (right side >=, left side strict)


# ---------------- events ----------------
def _level_series():
    # pivot high at bar 5 (110), then price drops, then returns to touch it
    rows = []
    for k, px in enumerate([100, 102, 104, 106, 108, 109, 106, 104, 102, 100, 99, 99, 99]):
        hi = 110.0 if k == 5 else px + 0.5
        rows.append((px, hi, px - 0.5, px))
    return rows


def test_event_touch_within_tolerance():
    rows = _level_series()
    rows.append((105, 109.7, 104.5, 105))  # 109.7 >= 110*(1-0.003)=109.67 -> touch
    ev = cs.find_events(bars(rows))
    sh = [e for e in ev if e["side"] == -1]
    assert len(sh) == 1 and sh[0]["i"] == 13 and sh[0]["level"] == 110.0


def test_event_not_touch_outside_tolerance():
    rows = _level_series()
    rows.append((105, 109.6, 104.5, 105))  # 109.6 < 109.67
    ev = cs.find_events(bars(rows))
    assert not [e for e in ev if e["side"] == -1]


def test_event_not_before_confirmation():
    # touch at bar 10 = pivot+5 is not usable (usable from pivot+6)
    rows = _level_series()[:10] + [(105, 109.9, 104.5, 105)]
    ev = cs.find_events(bars(rows))
    assert not [e for e in ev if e["side"] == -1]


def test_close_beyond_kills_level_and_is_no_event():
    rows = _level_series()
    rows.append((105, 111, 104.5, 110.5))   # closes above 110 -> level dead, no event
    rows.append((105, 109.9, 104.5, 105))   # later touch of a dead level -> nothing
    ev = cs.find_events(bars(rows))
    assert not [e for e in ev if e["side"] == -1 and e["level"] == 110.0]


def test_cooldown_24_bars():
    rows = _level_series()
    rows.append((105, 109.8, 104.5, 105))         # event at 13
    rows += [(104, 109.8, 103.5, 104)] * 23        # touches at 14..36: inside cooldown
    rows.append((104, 109.8, 103.5, 104))         # bar 37 = 13 + 24: allowed again
    ev = [e for e in cs.find_events(bars(rows)) if e["side"] == -1 and e["level"] == 110.0]
    assert [e["i"] for e in ev] == [13, 37]


def test_long_mirror_event():
    rows = []
    for k, px in enumerate([100, 98, 96, 94, 92, 91, 94, 96, 98, 100, 101, 101, 101]):
        lo = 90.0 if k == 5 else px - 0.5
        rows.append((px, px + 0.5, lo, px))
    rows.append((95, 95.5, 89.8, 91))   # sweeps below 90, closes back above -> event + sweep
    b = bars(rows)
    ev = [e for e in cs.find_events(b) if e["side"] == 1]
    assert len(ev) == 1 and ev[0]["level"] == 90.0
    assert cs.s1_sweep(b, ev[0]["i"], 1, 90.0)


# ---------------- layers ----------------
def test_s1_sweep_short():
    b = bars([(100, 111, 99, 109)])
    assert cs.s1_sweep(b, 0, -1, 110.0)
    b2 = bars([(100, 109.9, 99, 109)])
    assert not cs.s1_sweep(b2, 0, -1, 110.0)  # did not trade beyond


def test_s2_line_confluence():
    assert cs.s2_flag(59.0, [70.0, 61.5, 30.0], -1)
    assert not cs.s2_flag(59.0, [70.0, 63.0, 30.0], -1)      # no other TF at 60
    assert not cs.s2_flag(55.0, [60.0, 60.0], -1)            # trade TF not at the line
    assert cs.s2_flag(41.0, [float("nan"), 38.0], 1)
    assert not cs.s2_flag(41.0, [float("nan")], 1)


def test_s3_divergence_wick_and_close():
    n = 30
    h = np.full(n, 100.0)
    c = np.full(n, 99.0)
    rsi = np.full(n, 50.0)
    # pivot3 highs at 10 and 18, later higher wick, RSI lower
    h[10], h[18] = 105.0, 106.0
    rsi[10], rsi[18] = 70.0, 65.0
    l = h - 2
    ph3, _ = cs.pivots(h, l, 3)
    assert ph3[10] and ph3[18]
    # event at 21: p2 confirmed at 21 (18+3) -> yes
    assert cs.s3_divergence(h, l, c, rsi, ph3, None, 21, -1)
    # event at 20: p2 not yet confirmed -> no
    assert not cs.s3_divergence(h, l, c, rsi, ph3, None, 20, -1)
    # event at 28: p2 confirmed at 21 < 28-6 -> stale
    assert not cs.s3_divergence(h, l, c, rsi, ph3, None, 28, -1)
    # RSI higher at the later one -> no divergence
    rsi2 = rsi.copy()
    rsi2[18] = 75.0
    assert not cs.s3_divergence(h, l, c, rsi2, ph3, None, 21, -1)
    # close-only higher high: later wick lower but later close higher
    h3 = h.copy()
    h3[18] = 104.0
    c3 = c.copy()
    c3[10], c3[18] = 100.0, 103.0
    ph3b, _ = cs.pivots(h3, h3 - 2, 3)
    assert cs.s3_divergence(h3, h3 - 2, c3, rsi, ph3b, None, 21, -1)


def test_s3_span_limit():
    n = 40
    h = np.full(n, 100.0)
    c = np.full(n, 99.0)
    rsi = np.full(n, 50.0)
    h[5], h[27] = 105.0, 106.0          # 22 bars apart > 20
    rsi[5], rsi[27] = 70.0, 60.0
    ph3, pl3 = cs.pivots(h, h - 2, 3)
    assert not cs.s3_divergence(h, h - 2, c, rsi, ph3, pl3, 30, -1)


def test_s3_long_mirror():
    n = 30
    l = np.full(n, 100.0)
    c = np.full(n, 101.0)
    rsi = np.full(n, 50.0)
    l[10], l[18] = 95.0, 94.0
    rsi[10], rsi[18] = 30.0, 35.0
    h = l + 2
    _, pl3 = cs.pivots(h, l, 3)
    assert cs.s3_divergence(h, l, c, rsi, None, pl3, 21, 1)


def test_s4_signal_bar():
    rsi = np.array([50, 55, 62, 61, 59, 58], dtype=float)
    ma = np.array([50, 52, 55, 57, 60, 60], dtype=float)
    sig = cs.s4_signals(rsi, ma, -1)
    assert sig[4] and not sig[3]       # 59 < 60 and < MA 60, armed by 62 at bar 2
    assert cs.s4_at(sig, 5) and cs.s4_at(sig, 4) and not cs.s4_at(sig, 3)
    # not armed: no >= 60 within the previous 6 bars
    rsi2 = np.array([62, 50, 50, 50, 50, 50, 50, 55], dtype=float)
    ma2 = np.full(8, 56.0)
    sig2 = cs.s4_signals(rsi2, ma2, -1)
    assert sig2[6] and not sig2[7]     # bar 6 sees bar 0 (k-6); bar 7 does not
    sig3 = cs.s4_signals(np.array([38, 41, 42], dtype=float), np.array([40, 40, 40], dtype=float), 1)
    assert sig3[1] and sig3[2]


def test_s5_htf():
    assert cs.s5_flag((65.0, 59.0), (55.0, 50.0), -1)     # daily < 60 and falling
    assert not cs.s5_flag((55.0, 59.0), (55.0, 50.0), -1)  # daily rising
    assert cs.s5_flag((55.0, 59.0), (61.0, 58.0), -1)      # weekly 61 -> 58
    assert cs.s5_flag((35.0, 41.0), (50.0, 50.0), 1)       # daily > 40 and rising
    assert cs.s5_flag((45.0, 44.0), (39.0, 41.0), 1)       # weekly back over 40
    assert not cs.s5_flag((float("nan"), 41.0), (50.0, 50.0), 1)


# ---------------- higher TF: resample and as-of (no lookahead) ----------------
def test_resample_and_asof_no_lookahead():
    n = 72
    t = np.arange(n, dtype=np.int64) * H
    c = np.arange(n, dtype=float) + 1.0
    ct, cc = cs.resample_close(t, c, H, DAY)
    assert list(ct) == [DAY, 2 * DAY, 3 * DAY] and list(cc) == [24.0, 48.0, 72.0]
    vals = np.array([10.0, 20.0, 30.0])
    # at 1.5 days only day 0 is closed
    assert cs.asof(ct, vals, np.array([DAY + 12 * H]))[0] == 10.0
    assert cs.asof(ct, vals, np.array([DAY]))[0] == 10.0          # usable exactly at its close
    assert math.isnan(cs.asof(ct, vals, np.array([DAY - 1]))[0])
    # changing a future 1h bar does not change the value as of 1.5 days
    c2 = c.copy()
    c2[60] = 1e6
    ct2, cc2 = cs.resample_close(t, c2, H, DAY)
    assert cc2[0] == cc[0] and cc2[1] == cc[1]


def test_weekly_monday_alignment():
    # 1970-01-05 is a Monday (day 4)
    t = np.arange(4, 4 + 14, dtype=np.int64) * DAY
    c = np.arange(14, dtype=float)
    ct, cc = cs.resample_close(t, c, DAY, 7 * DAY, offset=4 * DAY)
    assert list(ct) == [11 * DAY, 18 * DAY] and list(cc) == [6.0, 13.0]


# ---------------- splits ----------------
def test_split_refusal():
    with pytest.raises(cs.SplitViolation):
        cs.check_month("DEV", "2024-07")
    with pytest.raises(cs.SplitViolation):
        cs.check_month("VAL", "2025-07")
    with pytest.raises(cs.SplitViolation):
        cs.check_month("HOLDOUT", "2025-08")
    cs.check_month("DEV", "2024-06")
    cs.check_month("VAL", "2025-06")


def test_loader_months_stop_at_split_end():
    ms = cs.months_for("DEV")
    assert ms[0] == "2017-08" and ms[-1] == "2024-06"
    assert cs.months_for("VAL")[-1] == "2025-06"


def test_loader_drops_rows_past_split_end():
    rows = [(cs.SPLIT_END["DEV"] - H, 1, 2, 0.5, 1.5), (cs.SPLIT_END["DEV"], 1, 2, 0.5, 1.5)]
    kept = cs.clip_rows(rows, "DEV")
    assert len(kept) == 1


# ---------------- trade: fee and R arithmetic ----------------
def test_fee_constant_from_fees_py():
    from MyTradingSys.backtest import fees
    assert abs(cs.FEE_RT - (2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13)) < 1e-15
    assert abs(cs.FEE_RT - 0.0012) < 1e-12


def _trade_bars(after):
    rows = [(100, 100.5, 99.5, 100)] * 5 + [(100, 102, 99.5, 100)]   # i = 5, stop = max(high last 6, L)
    rows += after
    rows += [(100, 100.5, 99.5, 100)] * 40
    return bars(rows)


def test_short_target_and_fee_r():
    b = _trade_bars([(100, 100.5, 94.0, 95)])   # stop 102, sd 2, target 95 -> hit
    r = cs.simulate(b, 5, -1, 101.0, None)
    assert r["exit_kind"] == "target" and abs(r["gross"] - 2.5) < 1e-12
    assert abs(r["fee"] - 0.0012 / 0.02) < 1e-12
    assert abs(r["net"] - (2.5 - 0.06)) < 1e-12


def test_stop_uses_level_when_highs_below_it():
    b = _trade_bars([(100, 100.5, 99.5, 100)])
    r = cs.simulate(b, 5, -1, 103.0, None)     # level above all highs -> stop at the level
    assert abs(r["stop"] - 103.0) < 1e-12


def test_same_bar_tie_stop_wins():
    b = _trade_bars([(100, 102.5, 94.0, 99)])
    r = cs.simulate(b, 5, -1, 101.0, None)
    assert r["exit_kind"] == "stop" and abs(r["gross"] + 1.0) < 1e-12


def test_time_exit_at_bar_30_close():
    after = [(100, 100.5, 99.5, 100)] * 29 + [(100, 100.5, 99.0, 99.0)]
    b = _trade_bars(after)
    r = cs.simulate(b, 5, -1, 101.0, None)
    assert r["exit_kind"] == "time" and abs(r["gross"] - 0.5) < 1e-12


def test_censored_when_hold_runs_past_data():
    b = bars([(100, 100.5, 99.5, 100)] * 5 + [(100, 102, 99.5, 100)] + [(100, 100.5, 99.5, 100)] * 10)
    assert cs.simulate(b, 5, -1, 101.0, None) is None


def test_funding_sign_short_receives_positive():
    b = _trade_bars([(100, 100.5, 94.0, 95)])
    t_entry = int(b["t"][5] + H)
    fund = (np.array([t_entry, t_entry + H], dtype=np.int64), np.array([0.001, 0.0002]))
    r = cs.simulate(b, 5, -1, 101.0, fund)
    # only the record strictly after entry and <= exit counts: +0.0002; short sign -1 -> fund_r = -0.0002/0.02
    assert abs(r["fund"] - (-0.01)) < 1e-12
    assert abs(r["net"] - (2.5 - 0.06 + 0.01)) < 1e-12


def test_long_trade_mirror():
    rows = [(100, 100.5, 99.5, 100)] * 5 + [(100, 100.5, 98, 100)] + [(100, 105.5, 99.5, 105)] + flat(40)
    r = cs.simulate(bars(rows), 5, 1, 99.0, None)
    assert r["exit_kind"] == "target" and abs(r["stop"] - 98.0) < 1e-12 and abs(r["gross"] - 2.5) < 1e-12


# ---------------- statistics ----------------
def test_ols_cluster_exact_line():
    x = np.array([0, 1, 2, 3, 4, 5] * 5, dtype=float)
    y = 0.5 + 0.2 * x
    g = np.arange(30)
    res = cs.ols_cluster(y, x, g)
    assert abs(res["slope"] - 0.2) < 1e-12 and res["se"] < 1e-9


def test_ols_cluster_se_grows_with_clustering():
    rng = np.random.default_rng(1)
    x = np.repeat(rng.integers(0, 6, 100).astype(float), 5)
    y = np.repeat(rng.normal(size=100), 5) + 0.0 * x
    a = cs.ols_cluster(y, x, np.arange(500))
    b = cs.ols_cluster(y, x, np.repeat(np.arange(100), 5))
    assert b["se"] > a["se"]
