"""Tests for confirmations.py (RSI deep-buy Stage 3). Synthetic series; expected numbers are hand-computed from
backtest/layers/FORMULAS.md (s12 plain-SMA ATR, s28.1 z-score vs the prior L bars with population sd, s22 Bollinger
population sd) and from the card text, never from the module."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import confirmations as cf  # noqa: E402


def _ms(s):
    return int(np.datetime64(s, "ms").astype("int64"))


def _csv(path, rows):
    lines = ["open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore"]
    for t, o, h, l, c in rows:
        lines.append(f"{t},{o},{h},{l},{c},10,{t + 59999},1,1,4,1,0")
    Path(path).write_text("\n".join(lines) + "\n", newline="\n")


def test_loader_refuses_bar_at_or_after_dev_cutoff(tmp_path):
    ok = tmp_path / "ok.csv"
    _csv(ok, [(_ms("2024-06-30T23:59"), 1, 1, 1, 1)])
    d = cf.load_klines_ext([ok])
    assert len(d["open_time"]) == 1 and d["volume"][0] == 10 and d["taker_buy_volume"][0] == 4
    bad = tmp_path / "bad.csv"
    _csv(bad, [(_ms("2024-06-30T23:59"), 1, 1, 1, 1), (_ms("2024-07-01T00:00"), 1, 1, 1, 1)])
    with pytest.raises(ValueError):
        cf.load_klines_ext([bad])
    # the VALIDATION pass has its own, later limit (HOLDOUT 2025-07-01)
    assert len(cf.load_klines_ext([bad], cutoff_ms=_ms("2025-07-01T00:00"))["open_time"]) == 2
    late = tmp_path / "late.csv"
    _csv(late, [(_ms("2025-07-01T00:00"), 1, 1, 1, 1)])
    with pytest.raises(ValueError):
        cf.load_klines_ext([late], cutoff_ms=_ms("2025-07-01T00:00"))


def test_atr_is_plain_sma_of_true_range():
    # FORMULAS s12: ATR2[2] = mean(TR1, TR2); TR1 = max(1.0, 1.5, 0.5) = 1.5; TR2 = max(2.0, 2.0, 0.0) = 2.0 -> 1.75
    h = np.array([10.5, 11.5, 13.0]); l = np.array([9.5, 10.5, 11.0]); c = np.array([10.0, 11.0, 12.0])
    a = cf.atr_sma(h, l, c, 2)
    assert np.isnan(a[0]) and np.isnan(a[1])
    assert a[2] == pytest.approx(1.75)


def test_zscore_uses_prior_bars_population_sd():
    # FORMULAS s28.1: x=[1,2,3,4,10], L=4 at i=4: prior mean 2.5, pstdev sqrt(1.25) -> z = 7.5/1.118034 = 6.708204
    z = cf.zscore_prior(np.array([1.0, 2, 3, 4, 10]), 4)
    assert z[4] == pytest.approx(6.708204, abs=1e-5)
    assert np.isnan(z[3])
    assert np.isnan(cf.zscore_prior(np.full(8, 3.0), 4)[6])      # sd 0 -> undefined, never a signal


def test_bollinger_lower_population_sd():
    # FORMULAS s22 with n=3, mult=2: closes 1,2,3 -> mean 2, pop sd sqrt(2/3)=0.816497 -> lower 2-1.632993 = 0.367007
    lo = cf.bollinger_lower(np.array([1.0, 2, 3]), 3, 2.0)
    assert lo[2] == pytest.approx(0.367007, abs=1e-6)
    assert np.isnan(lo[1])


def test_episode_end_stops_at_rearm_and_window_cap():
    rsi = np.array([19.0, 18, 17, 18, 23.5, 15, 14, 13])   # level 20, h=3: rearm at 23.0; 23.5 at index 4
    assert cf.episode_end(rsi, 0, 20.0, 16) == 3
    assert cf.episode_end(rsi, 5, 20.0, 1) == 6              # window cap W=1
    assert cf.episode_end(rsi, 5, 20.0, 16) == 7             # data end


def test_hook_fires_on_plant_not_on_flat():
    # level 20; running min 16; RSI 19.0 is exactly min+3 -> fires at index 5; 18.9 at index 4 does not
    rsi = np.array([20.0, 18, 16, 17, 18.9, 19.0, 19.5])
    assert cf.hook_bar(rsi, 0, 6, 3.0) == 5
    assert cf.hook_bar(rsi, 0, 6, 5.0) == -1                 # b=5 sensitivity never reached
    assert cf.hook_bar(np.full(8, 15.0), 0, 7, 3.0) == -1
    # a new minimum after a near-hook resets the running minimum: min 16 -> 14 at index 4, 17.0 is +3.0 at index 6
    rsi2 = np.array([20.0, 18, 16, 18.5, 14, 15, 17.0])
    assert cf.hook_bar(rsi2, 0, 6, 3.0) == 6


def test_structure_shift_first_close_above_high_of_lowest_bar():
    #            idx0  idx1  idx2  idx3  idx4
    high = np.array([10.5, 10.2, 10.0, 10.1, 10.6])
    low = np.array([10.0, 9.0, 9.5, 9.6, 9.8])
    close = np.array([10.1, 9.4, 9.9, 10.15, 10.3])
    # lowest low so far is bar 1 (low 9.0, high 10.2); first close above 10.2 after it: index 4 (10.3); index 3 (10.15) is not
    assert cf.shift_bar(high, low, close, 0, 4) == 4
    # a new lower low at index 3 moves the reference to that bar (high 10.1): close 10.15 at index 3 is not after it, 10.3 at 4 is
    low2 = low.copy(); low2[3] = 8.5
    close2 = np.array([10.1, 9.4, 9.9, 10.05, 10.12])
    assert cf.shift_bar(high, low2, close2, 0, 4) == 4
    flat = np.full(6, 10.0)
    assert cf.shift_bar(flat, flat, flat, 0, 5) == -1


def test_climax_fires_on_wide_bar_with_long_lower_wick_not_on_flat():
    n = 130
    rng = np.where(np.arange(n) % 2 == 0, 1.0, 2.0)            # prior 100 ranges: mean 1.5, pstdev 0.5
    low = np.full(n, 100.0); high = low + rng; close = low + rng / 2
    low[120] = 95.0; high[120] = 99.0; close[120] = 98.0        # range 4.0 -> z = (4-1.5)/0.5 = 5; close location (98-95)/4 = 0.75 >= 2/3
    cond = cf.cond_climax(high, low, close)
    assert bool(cond[120])
    close[120] = 96.0                                           # location 0.25 -> no climax (still wide)
    assert not bool(cf.cond_climax(high, low, close)[120])
    assert not cf.cond_climax(np.full(n, 101.0), np.full(n, 100.0), np.full(n, 100.5)).any()   # constant ranges: sd 0


def test_fast_fall_in_atr_units():
    # close falls 14 bars: 100 -> 86 (return -14 price units); ATR14 = 2.0 (each bar high-low 2, no gaps) -> -14/2 = -7 <= -3
    n = 40
    close = np.r_[np.full(20, 100.0), 100.0 - np.arange(1, 15), np.full(6, 86.0)]
    high = close + 1.0; low = close - 1.0
    cond = cf.cond_fast_fall(high, low, close)
    assert not cond[19]
    assert cond[33]                                             # i=33: close 86 vs close[19]=100 -> -14 ; ATR at 33 = mean TR(20..33)
    assert not cf.cond_fast_fall(np.full(n, 101.0), np.full(n, 99.0), np.full(n, 100.0)).any()


def test_taker_and_volume_conditions():
    vol = np.r_[np.where(np.arange(100) % 2 == 0, 10.0, 20.0), 40.0, 15.0]    # prior 100: mean 15, pstdev 5 -> z(40) = 5
    tk = np.r_[np.full(100, 7.0), 24.0, 6.0]                                  # share at 100: 0.6 ; at 101: 0.4
    assert bool(cf.cond_vol_spike(vol)[100]) and not bool(cf.cond_vol_spike(vol)[101])
    c = cf.cond_taker_buy(vol, tk)
    assert bool(c[100]) and not bool(c[101])


def test_location_24h_sweep_and_breakdown():
    bars = 12                                                   # 'day' = 12 bars here
    low = np.full(30, 100.0); close = np.full(30, 101.0)
    low[20] = 99.0; close[20] = 100.5                           # pierces the prior-12-bar low 100.0 and closes back above -> sweep
    low[25] = 98.0; close[25] = 98.5                            # prior-12 min is 99.0 (bar 20): pierces and closes BELOW it -> breakdown
    sweep, newlow = cf.cond_location(low, close, bars)
    assert bool(sweep[20]) and bool(newlow[20])
    assert bool(newlow[25]) and not bool(sweep[25])
    assert not newlow[:12].any() and not newlow[21:25].any()    # first 12 bars have no full prior day; flat bars are not new lows


def test_htf_rsi_uses_last_completed_bar_only():
    rng = np.random.default_rng(5)
    n = 24000                                                   # 400 hourly bars, past the 200-bar RSI warm-up
    t = np.arange(n, dtype="int64") * 60_000
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.001, n)))
    d1 = {"open_time": t, "open": np.r_[c[0], c[:-1]], "high": c * 1.001, "low": c * 0.999, "close": c.copy()}
    base = cf.htf_rsi_lastcompleted(d1["open_time"], d1, 60)
    i = 20000 + 17                                              # inside hourly group 333 (bar 20000 starts group 333)
    g0 = (i // 60) * 60
    d2 = {k: v.copy() for k, v in d1.items()}
    for k in ("open", "high", "low", "close"):
        d2[k][g0:] *= 1.5                                       # change the CURRENT (incomplete) HTF bar and everything after
    alt = cf.htf_rsi_lastcompleted(d2["open_time"], d2, 60)
    j = g0 + 59
    assert np.isfinite(base[i]) and alt[i] == base[i]
    assert alt[j] == base[j]                        # every 1m bar of the incomplete hour sees the same value
    d3 = {k: v.copy() for k, v in d1.items()}
    for k in ("open", "high", "low", "close"):
        d3[k][g0 - 60:g0] *= 0.5                                # change the last COMPLETED bar: the value must move
    assert cf.htf_rsi_lastcompleted(d3["open_time"], d3, 60)[i] != base[i]


def test_entry_is_next_bar_open_and_lower_low_is_vs_episode_low():
    o = np.array([10.0, 11, 12, 13, 14, 15, 16, 17])
    low = np.array([9.0, 8.5, 9.5, 9.0, 8.0, 9.9, 9.9, 9.9])
    # confirmation at bar 2, N=3: entry = open[3] = 13, exit = open[6] = 16 -> gross 16/13-1
    entry, exit_, gross = cf.entry_exit(o, 2, 3)
    assert (entry, exit_) == (13.0, 16.0) and gross == pytest.approx(16 / 13 - 1)
    assert cf.entry_exit(o, 6, 3) is None                       # exit bar beyond the data: dropped, not clipped
    # episode low so far at bar 2 is min(low[0..2]) = 8.5; lows of bars 3..5 reach 8.0 < 8.5 -> new lower low
    assert cf.outcome_lower_low(low, 0, 2, 3) is True
    assert cf.outcome_lower_low(low, 0, 2, 1) is False               # only bar 3 (low 9.0)


def test_pair_confirms_at_the_later_of_the_two_bars():
    assert cf.pair_bar(3, 7) == 7 and cf.pair_bar(7, 3) == 7
    assert cf.pair_bar(-1, 3) == -1 and cf.pair_bar(3, -1) == -1
