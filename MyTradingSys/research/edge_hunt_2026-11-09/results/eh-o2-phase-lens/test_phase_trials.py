"""Tests for phase_trials.py: T14 events, T15 events, exits, fee/R arithmetic, split refusal. Hand-built bars."""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phase_trials as pt  # noqa: E402

H1 = 3_600_000
DAY = 86_400_000
T0 = 1_577_836_800_000  # 2020-01-01 00:00 UTC


def bar(t, o, h, lo, c):
    return (t, float(o), float(h), float(lo), float(c))


def flat_day(day0, price=100.0, hi=101.0, lo=99.0):
    """24 hourly bars, range lo..hi, closes at price."""
    out = []
    for k in range(24):
        h = hi if k == 5 else price + 0.5
        lw = lo if k == 6 else price - 0.5
        out.append(bar(day0 + k * H1, price, h, lw, price))
    return out


# ---------------------------------------------------------------- split refusal / loader
def test_loader_refuses_holdout_end():
    with pytest.raises(pt.SplitViolation):
        pt.load_klines("nowhere", "BTCUSDT", "1h", end=pt.VALIDATION_END_MS + 1)


def test_loader_drops_bars_at_or_after_end():
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "klines"))
    p = os.path.join(d, "klines", "BTCUSDT-1h-2024-06.csv")
    t_last = pt.DEV_END_MS - H1
    with open(p, "w", newline="\n") as f:
        f.write(f"{t_last},1,2,0.5,1.5,1,0,0,0,0,0,0\n")
        f.write(f"{pt.DEV_END_MS},1,2,0.5,1.5,1,0,0,0,0,0,0\n")
    p2 = os.path.join(d, "klines", "BTCUSDT-1h-2024-07.csv")
    with open(p2, "w", newline="\n") as f:
        f.write(f"{pt.DEV_END_MS + H1},1,2,0.5,1.5,1,0,0,0,0,0,0\n")
    bars = pt.load_klines(os.path.join(d, "klines"), "BTCUSDT", "1h", end=pt.DEV_END_MS)
    assert [b[0] for b in bars] == [t_last]


def test_loader_normalises_microseconds():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "BTCUSDT-1d-2025-01.csv")
    with open(p, "w", newline="\n") as f:
        f.write("1735689600000000,1,2,0.5,1.5,1,0,0,0,0,0,0\n")
    bars = pt.load_klines(d, "BTCUSDT", "1d", end=pt.VALIDATION_END_MS)
    assert bars[0][0] == 1735689600000


# ---------------------------------------------------------------- fee / R arithmetic
def test_cost_constant_from_fees_module():
    import importlib
    fees = importlib.import_module("MyTradingSys.backtest.fees")
    assert pt.COST_RT_A == pytest.approx(2 * fees.DERIBIT_TAKER + fees.SLIPPAGE_RT_S13)
    assert pt.COST_RT_A == pytest.approx(0.0012)


def test_net_r_arithmetic():
    # long entry 100, stop 99 (1 % stop): fee_r = 0.0012 / 0.01 = 0.12; funding 0.0004 paid by long = 0.04 R
    r = pt.net_r(gross_r=2.0, side=1, entry=100.0, stop=99.0, funding_sum=0.0004)
    assert r["fee_r"] == pytest.approx(0.12)
    assert r["funding_r"] == pytest.approx(0.04)
    assert r["net_r"] == pytest.approx(2.0 - 0.12 - 0.04)
    # short receives positive funding
    r2 = pt.net_r(gross_r=-1.0, side=-1, entry=100.0, stop=101.0, funding_sum=0.0004)
    assert r2["funding_r"] == pytest.approx(-0.04)
    assert r2["net_r"] == pytest.approx(-1.0 - 0.12 + 0.04)


def test_funding_window_half_open():
    fund = [(T0 + 8 * H1, 0.0001), (T0 + 16 * H1, 0.0003), (T0 + 24 * H1, 0.0005)]
    assert pt.funding_sum(fund, T0 + 8 * H1, T0 + 16 * H1) == pytest.approx(0.0003)
    assert pt.funding_sum(fund, T0, T0 + 16 * H1) == pytest.approx(0.0004)


# ---------------------------------------------------------------- exits
def test_exit_target_stop_tie_and_timeout():
    bars = [bar(T0, 100, 100, 100, 100)]
    bars += [bar(T0 + H1, 100, 101, 99.5, 100.5), bar(T0 + 2 * H1, 100.5, 102.1, 100, 102)]
    g = pt.simulate_exit(bars, 0, side=1, entry=100.0, stop=99.0, target_r=2.0, max_bars=24)
    assert g["gross_r"] == pytest.approx(2.0) and g["reason"] == "target" and g["exit_idx"] == 2
    # same bar touches both: stop wins
    tie = [bar(T0, 100, 100, 100, 100), bar(T0 + H1, 100, 103, 98, 100)]
    g = pt.simulate_exit(tie, 0, side=1, entry=100.0, stop=99.0, target_r=2.0, max_bars=24)
    assert g["gross_r"] == pytest.approx(-1.0) and g["reason"] == "stop"
    # time stop at the close of bar entry + max_bars
    ts = [bar(T0 + k * H1, 100, 100.5, 99.5, 100 + 0.01 * k) for k in range(30)]
    g = pt.simulate_exit(ts, 0, side=1, entry=100.0, stop=99.0, target_r=2.0, max_bars=24)
    assert g["reason"] == "time" and g["exit_idx"] == 24
    assert g["gross_r"] == pytest.approx(0.24)
    # short mirror target
    sh = [bar(T0, 100, 100, 100, 100), bar(T0 + H1, 100, 100.2, 97.9, 98)]
    g = pt.simulate_exit(sh, 0, side=-1, entry=100.0, stop=101.0, target_r=2.0, max_bars=24)
    assert g["gross_r"] == pytest.approx(2.0)
    # not enough bars to finish: open trade dropped (None)
    assert pt.simulate_exit(ts[:10], 0, side=1, entry=100.0, stop=99.0, target_r=2.0, max_bars=24) is None


# ---------------------------------------------------------------- T14 events
def test_t14_sweep_high_and_reclaim():
    bars = flat_day(T0)                      # prior day H=101, L=99
    day2 = flat_day(T0 + DAY, hi=100.5, lo=99.5)
    # bar 14 of day 2 sweeps 101 (high 101.8), closes outside 101.2; bar 15 closes back inside 100.6
    day2[14] = bar(T0 + DAY + 14 * H1, 100, 101.8, 99.9, 101.2)
    day2[15] = bar(T0 + DAY + 15 * H1, 101.2, 101.5, 100.4, 100.6)
    bars += day2 + flat_day(T0 + 2 * DAY, hi=100.5, lo=99.5)
    ev = pt.t14_events(bars)
    assert len(ev) == 1
    e = ev[0]
    assert e["side"] == -1 and e["idx"] == 24 + 15
    assert e["entry"] == pytest.approx(100.6) and e["stop"] == pytest.approx(101.8)
    assert e["level"] == "PDH"


def test_t14_no_event_if_reclaim_too_late_or_12_back_outside():
    bars = flat_day(T0)
    day2 = flat_day(T0 + DAY, hi=100.5, lo=99.5)
    for k in (14, 15, 16):
        day2[k] = bar(T0 + DAY + k * H1, 101.2, 101.8, 101.1, 101.3)  # three closes outside
    day2[17] = bar(T0 + DAY + 17 * H1, 101.3, 101.4, 100.2, 100.5)    # 4th bar back inside: too late
    bars += day2 + flat_day(T0 + 2 * DAY, hi=100.5, lo=99.5)
    assert [e for e in pt.t14_events(bars) if e["day"] == T0 + DAY] == []
    # close 12 bars earlier outside the prior-day range -> no event
    bars = flat_day(T0)
    day2 = flat_day(T0 + DAY, hi=100.5, lo=99.5)
    day2[2] = bar(T0 + DAY + 2 * H1, 100, 102.5, 100, 102.0)          # close 102 outside (bar i-12 for i=14)
    day2[14] = bar(T0 + DAY + 14 * H1, 100, 101.8, 99.9, 100.2)        # sweeps and closes inside on the same bar
    bars += day2 + flat_day(T0 + 2 * DAY, hi=100.5, lo=99.5)
    ev = [e for e in pt.t14_events(bars) if e["day"] == T0 + DAY]
    assert all(e["idx"] != 24 + 14 for e in ev)


def test_t14_low_side_and_one_per_level_per_day():
    bars = flat_day(T0)
    day2 = flat_day(T0 + DAY, hi=100.5, lo=99.5)
    day2[13] = bar(T0 + DAY + 13 * H1, 100, 100.1, 98.2, 99.5)   # sweep low, close inside same bar
    day2[20] = bar(T0 + DAY + 20 * H1, 100, 100.1, 98.0, 99.6)   # second sweep same level same day: ignored
    bars += day2 + flat_day(T0 + 2 * DAY, hi=100.5, lo=99.5)
    ev = [e for e in pt.t14_events(bars) if e["day"] == T0 + DAY]
    assert len(ev) == 1 and ev[0]["side"] == 1 and ev[0]["level"] == "PDL"
    assert ev[0]["stop"] == pytest.approx(98.2) and ev[0]["entry"] == pytest.approx(99.5)


# ---------------------------------------------------------------- T15 events
def test_t15_uses_malkan_and_swing_low():
    # build closes whose RSI stays >= 40 and >= 60 within 20 bars, dips into 40..42 and bounces with a green bar
    import math
    closes = []
    p = 100.0
    for k in range(60):
        p *= 1.01 if k % 3 else 0.995
        closes.append(p)
    rsi = pt.rsi_core(closes, 14)
    # sanity on construction is delegated to malkan; here: helper returns swing low over band run + signal bar
    bars = [(T0 + k * 4 * H1, c * 0.999, c * 1.002, c * 0.99 - (5 if k == 50 else 0), c) for k, c in enumerate(closes)]
    rsi_fake = [None] * 14 + [55.0] * 34 + [41.0, 40.5, 50.0] + [55.0] * 9  # band run idx 48,49; signal 50
    assert pt.swing_low_for_signal(bars, rsi_fake, 50) == pytest.approx(min(b[3] for b in bars[48:51]))
    sig = pt.t15_signals(bars, rsi_fake)
    # regime: min over last 20 RSI >= 40 and max >= 60 needed -> 55 max -> not BULL -> no signal
    assert sig == []
    rsi_fake2 = [None] * 14 + [61.0] * 34 + [41.0, 40.5, 50.0] + [55.0] * 9
    bars2 = list(bars)
    t, o, h, lo, c = bars2[50]
    bars2[50] = (t, c * 0.98, h, lo, c)  # green
    sig = pt.t15_signals(bars2, rsi_fake2)
    assert [s["idx"] for s in sig] == [50]
    bars2[50] = (t, c * 1.01, h, lo, c)  # red candle -> no signal
    assert pt.t15_signals(bars2, rsi_fake2) == []


# ---------------------------------------------------------------- cells / stats
def test_cell_filters():
    assert pt.in_balance("BULL", "MID") and pt.in_balance("TRANSITION", "MID")
    assert not pt.in_balance("PEAK_WINDOW", "MID") and not pt.in_balance("BOTTOM_WINDOW", "MID")
    assert not pt.in_balance("BULL", "HIGH")
    assert pt.in_t15_cell("ACCUMULATION", "MID") and pt.in_t15_cell("BULL", "HIGH")
    assert not pt.in_t15_cell("BULL", "LOW") and not pt.in_t15_cell("BEAR", "HIGH")


def test_stats_screen_and_verdict():
    s = pt.stats([1.0, -0.5, 0.2, 0.3], [1, 1, 2, 3])
    assert s["n"] == 4 and s["mean"] == pytest.approx(0.25)
    assert pt.dev_screen({"n": 29, "mean": 1, "ci_lo": 0.5})is False
    assert pt.dev_screen({"n": 30, "mean": 0.1, "ci_lo": 0.01}) is True
    assert pt.verdict({"n": 100, "mean": -0.1, "ci_hi": 0.05, "mde": 0.2}, None) == "FAIL"
    assert pt.verdict({"n": 100, "mean": -0.1, "ci_hi": 0.25, "mde": 0.2}, None) == "INCONCLUSIVE"


def test_daily_hlc_maps_loader_rows_for_phase_label():
    rows = [(T0, 10.0, 12.0, 9.0, 11.0)]
    assert pt.daily_hlc(rows) == [(T0, 12.0, 9.0, 11.0)]
