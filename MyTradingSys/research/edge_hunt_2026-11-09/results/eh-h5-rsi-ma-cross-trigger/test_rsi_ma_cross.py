"""Tests for rsi_ma_cross.py (T06). Hand-built bars for every rule; split refusal; no-lookahead; fee/R arithmetic.

Run: python test_rsi_ma_cross.py   (or pytest on this file)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True

import rsi_ma_cross as M  # noqa: E402

H4 = 4 * 3600 * 1000
D1 = 24 * 3600 * 1000
T0 = 1_500_000_000_000 - (1_500_000_000_000 % H4)  # a 4h-aligned UTC open


def bar(i, o, h, l, c):
    return {"t": T0 + i * H4, "o": float(o), "h": float(h), "l": float(l), "c": float(c)}


def fails(fn, exc):
    try:
        fn()
    except exc:
        return True
    return False


def test_rsi_matches_repo_core():
    closes = [100 + ((i * 37) % 11) - 5 + i * 0.1 for i in range(60)]
    ours = M.rsi14(closes)
    ref = M.REPO_RSI(closes, 14)
    assert ours[:14] == [None] * 14 and ours[14] is not None
    for a, b in zip(ours, ref):
        assert (a is None and b is None) or abs(a - b) < 1e-9


def test_sma_of_rsi_and_none_padding():
    s = M.sma([1, 2, 3, 4, 5], 3)
    assert s == [None, None, 2.0, 3.0, 4.0], s


def test_short_signal_needs_armed_60_and_first_bar_of_run():
    # rsi: armed (>=60) at index 2, signal at index 5 (rsi < ma and < 60), index 6 still true -> not a new event
    rsi = [50, 50, 65, 62, 58, 45, 44, 50, 50, 50]
    ma = [50, 50, 55, 56, 57, 50, 50, 50, 50, 50]
    ev = M.find_events(rsi, ma, "short")
    assert ev == [5], ev


def test_short_not_armed_no_signal():
    rsi = [50, 50, 55, 50, 45, 40, 40, 40, 40, 40]   # never >= 60 in the 6 bars before the signal
    ma = [50, 50, 52, 52, 52, 52, 52, 52, 52, 52]
    assert M.find_events(rsi, ma, "short") == []


def test_armed_window_is_six_bars_only():
    rsi = [65, 50, 50, 50, 50, 50, 50, 35, 35, 35]   # 60+ at index 0; signal at 7 is 7 bars later -> not armed
    ma = [60] + [40] * 9
    assert M.find_events(rsi, ma, "short") == []


def test_signal_needs_below_60_not_just_below_ma():
    rsi = [62, 62, 62, 62, 62, 62, 61, 61]  # never below 60 -> no signal even though rsi < ma
    ma = [70, 70, 70, 70, 70, 70, 70, 70]
    assert M.find_events(rsi, ma, "short") == []


def test_long_mirror():
    rsi = [50, 50, 35, 38, 42, 55, 56, 50]
    ma = [50, 50, 45, 44, 43, 50, 50, 50]
    # armed at idx 2 (<=40), signal idx 5: rsi 55 > ma 50 and > 40 -> long event
    assert M.find_events(rsi, ma, "long") == [5]


def test_short_entry_fill_and_stop_and_target():
    # signal bar 2 open 100; bar 3 low 99 (<100) -> sell stop filled at 100 (open of bar 3 is 100.5 >100 -> min = 100)
    bars = [bar(0, 100, 101, 99, 100), bar(1, 100, 101, 99, 100), bar(2, 100, 105, 99, 99.5),
            bar(3, 100.5, 101, 98.0, 98.5)]
    # stop = max high over bars i-5..i = 105 ; fill = min(open_e=100.5, open_i=100) = 100 ; risk = 5
    # target = 100 - 2.5*5 = 87.5 ; bar 3 low 98 does not reach it; time stop later
    trades = M.simulate(bars, [2], "short", busy_until=-1, n_bars=30)
    assert len(trades) == 1
    tr = trades[0]
    assert tr["fill"] == 100.0 and abs(tr["stop"] - 105.0) < 1e-12 and abs(tr["risk"] - 5.0) < 1e-12
    assert tr["entry_bar"] == 3


def test_no_confirmation_no_trade():
    bars = [bar(0, 100, 101, 99, 100), bar(1, 100, 101, 99, 100), bar(2, 100, 105, 99, 99.5),
            bar(3, 101, 103, 100.0, 102)]   # bar 3 low 100 is NOT below open 100 -> no trade
    assert M.simulate(bars, [2], "short", busy_until=-1, n_bars=30) == []


def test_gap_fill_uses_open_of_next_bar_when_worse():
    # bar 3 opens below the signal open: sell stop fills at that (worse for a short? better) open = min(open_e, open_i)
    bars = [bar(0, 100, 101, 99, 100), bar(1, 100, 101, 99, 100), bar(2, 100, 105, 99, 99.5),
            bar(3, 97, 98, 96, 96.5)]
    tr = M.simulate(bars, [2], "short", busy_until=-1, n_bars=30)[0]
    assert tr["fill"] == 97.0


def test_stop_wins_same_bar_tie_and_target_hit():
    # short fill 100, stop 105 (risk 5), target 87.5. Entry bar 3 high 106 -> stop (gross -1R), not target
    bars = [bar(0, 100, 101, 99, 100), bar(1, 100, 101, 99, 100), bar(2, 100, 105, 99, 99.5),
            bar(3, 100.5, 106, 80, 90)]
    tr = M.simulate(bars, [2], "short", busy_until=-1, n_bars=30)[0]
    assert tr["exit_reason"] == "stop" and abs(tr["gross_r"] + 1.0) < 1e-12
    # now target only: bars that go to 87 with no high >= 105
    bars2 = [bar(0, 100, 101, 99, 100), bar(1, 100, 101, 99, 100), bar(2, 100, 105, 99, 99.5),
             bar(3, 100.5, 101, 87, 88), bar(4, 88, 89, 86, 86)]
    tr2 = M.simulate(bars2, [2], "short", busy_until=-1, n_bars=30)[0]
    assert tr2["exit_reason"] == "target" and abs(tr2["gross_r"] - 2.5) < 1e-12


def test_time_stop_after_30_bars_at_close():
    n = 40
    bars = [bar(0, 100, 101, 99, 100), bar(1, 100, 101, 99, 100), bar(2, 100, 105, 99, 99.5)]
    bars += [bar(3 + k, 100, 101, 99, 99.0 + 0.0) for k in range(n - 3)]
    bars[3] = bar(3, 100.5, 101, 99.5, 99.8)   # entry bar; low 99.5 < 100 confirms, no stop/target
    tr = M.simulate(bars, [2], "short", busy_until=-1, n_bars=30)[0]
    assert tr["exit_reason"] == "time"
    assert tr["exit_bar"] == 3 + 29
    assert abs(tr["exit_px"] - bars[3 + 29]["c"]) < 1e-12
    assert abs(tr["gross_r"] - (100.0 - bars[3 + 29]["c"]) / 5.0) < 1e-12


def test_one_open_trade_per_side_skips_overlapping_signal():
    bars = [bar(0, 100, 101, 99, 100), bar(1, 100, 101, 99, 100), bar(2, 100, 105, 99, 99.5),
            bar(3, 100.5, 101, 98, 98.5), bar(4, 98, 99, 97, 97.5), bar(5, 97, 98, 96, 96.5)]
    # second signal at 3 would enter at bar 4 which is inside trade 2 (open to bar 3+29) -> skipped
    trades = M.simulate(bars, [2, 3], "short", busy_until=-1, n_bars=30)
    assert len(trades) == 1, trades


def test_fee_r_arithmetic():
    # 12 bps round trip over a 200 bps stop = 0.06 R
    assert abs(M.fee_r(stop_bps=200.0) - 0.06) < 1e-12
    assert abs(M.COST_RT_BPS - 12.0) < 1e-12   # 10 bps taker RT + 2 bps slippage (regime A)


def test_funding_sign_short_receives_positive_rate():
    # short, positive funding 0.0001 for one settlement inside the hold: short RECEIVES -> negative cost
    fund = [(T0 + 2 * H4, 0.0001)]
    r = M.funding_r(entry_ms=T0 + 3 * H4, exit_ms=T0 + 10 * H4, fill=100.0, risk=5.0, side="short", funding=fund)
    # settlement at T0+2H4 is before entry -> not counted: zero
    assert r == 0.0
    fund2 = [(T0 + 4 * H4, 0.0001)]
    r2 = M.funding_r(entry_ms=T0 + 3 * H4, exit_ms=T0 + 10 * H4, fill=100.0, risk=5.0, side="short", funding=fund2)
    assert r2 < 0.0   # receiving
    assert abs(r2 - (-0.0001 / (5.0 / 100.0))) < 1e-12


def test_daily_filter_uses_only_closed_daily_bars():
    # daily bar of day D is usable only at t >= D + 1 day (no lookahead)
    d_closes = [(T0 - D1 * 2, 50.0), (T0 - D1, 70.0)]   # open_ms, rsi
    # signal at T0 (4h bar open): day T0-D1 closes at T0 -> usable at t >= T0 (its close time) ; t_close of signal bar = T0+H4
    assert M.daily_value_asof(d_closes, T0) == 70.0
    # a day that opens at T0 would close at T0+D1 and must not be used at T0
    assert M.daily_value_asof([(T0, 99.0)], T0) is None


def test_split_refusal():
    # bars past the split end must be refused by the window guard
    assert fails(lambda: M.guard_window(M.HOLDOUT_START_MS), M.SplitRefusal)
    assert fails(lambda: M.guard_window(M.VAL_END_MS), M.SplitRefusal)
    M.guard_window(M.VAL_END_MS - 1)   # last allowed ms of the frozen range does not raise
    assert fails(lambda: M.dev_only([bar(0, 1, 1, 1, 1), {"t": M.DEV_END_MS + 1, "o": 1, "h": 1, "l": 1, "c": 1}]),
                 M.SplitRefusal)


def test_loader_refuses_holdout_range():
    assert fails(lambda: M.load_spot_4h("BTCUSDT", end_ms=M.HOLDOUT_START_MS + H4), M.SplitRefusal)


def main():
    fns = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    for f in fns:
        f()
        print("ok", f.__name__)
    print("PASSED %d tests" % len(fns))


if __name__ == "__main__":
    main()
