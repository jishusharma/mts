"""Hand-built tests for star_grades.py (eh-h2-malkan-star-grades). Run: python test_star_grades.py"""
import math
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import star_grades as sg  # noqa: E402

DAY = 86400000


def ms(y, m, d):
    import datetime as dt
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000)


def bar(o, h, l, c, day0=0):
    return {"t": day0, "o": float(o), "h": float(h), "l": float(l), "c": float(c)}


def test_split_refusal():
    rows = [{"t": ms(2024, 6, 30), "o": 1, "h": 1, "l": 1, "c": 1},
            {"t": ms(2024, 7, 1), "o": 1, "h": 1, "l": 1, "c": 1}]
    try:
        sg.check_window(rows, ms(2017, 8, 1), sg.DEV_END_EXCL)
    except sg.SplitViolation:
        pass
    else:
        raise AssertionError("DEV loader must refuse a bar at 2024-07-01")
    sg.check_window(rows[:1], ms(2017, 8, 1), sg.DEV_END_EXCL)  # 2024-06-30 is allowed
    try:
        sg.check_window([{"t": ms(2025, 7, 1), "o": 1, "h": 1, "l": 1, "c": 1}], ms(2024, 7, 1), sg.VAL_END_EXCL)
    except sg.SplitViolation:
        pass
    else:
        raise AssertionError("loader must refuse HOLDOUT bars (2025-07-01)")


def test_microsecond_timestamps_normalised():
    assert sg.normalize_ms(1748736000000000) == 1748736000000
    assert sg.normalize_ms(1502928000000) == 1502928000000


def test_monthly_resample_and_no_lookahead():
    # daily bars from 2020-01-30 to 2020-02-02 (open times)
    days = [ms(2020, 1, 30), ms(2020, 1, 31), ms(2020, 2, 1), ms(2020, 2, 2)]
    daily = [dict(t=d, o=10, h=11, l=9, c=10 + i) for i, d in enumerate(days)]
    months = sg.resample(daily, "M")
    jan = [m for m in months if m["t"] == ms(2020, 1, 1)][0]
    assert jan["c"] == 11 and jan["close_ms"] == ms(2020, 2, 1), jan
    # January bar is usable only from the day AFTER it closes (2020-02-01 open onward)
    assert not sg.usable(jan["close_ms"], ms(2020, 1, 30))   # last day of Jan: bar not closed yet
    assert sg.usable(jan["close_ms"], ms(2020, 2, 1))
    weeks = sg.resample(daily, "W")
    w = [x for x in weeks if x["t"] == ms(2020, 1, 27)][0]   # Monday 2020-01-27
    assert w["close_ms"] == ms(2020, 2, 3), w
    assert not sg.usable(w["close_ms"], ms(2020, 2, 1))


def test_last_usable_value():
    closes = [ms(2020, 2, 1), ms(2020, 3, 1), ms(2020, 4, 1)]
    vals = [50.0, 61.0, 70.0]
    assert sg.last_usable(closes, vals, ms(2020, 2, 15)) == 50.0
    assert sg.last_usable(closes, vals, ms(2020, 2, 29)) == 61.0
    assert sg.last_usable(closes, vals, ms(2020, 1, 1)) is None


def test_fee_r_arithmetic():
    # 12 bps round trip (10 taker + 2 slippage) over a 500 bps stop = 0.024 R
    assert abs(sg.fee_r(entry=100.0, stop=95.0) - 0.024) < 1e-12
    assert abs(sg.fee_r(entry=100.0, stop=99.0) - 0.12) < 1e-12


def test_funding_r_sign_and_window():
    rates = [(ms(2020, 1, 1), 0.0001), (ms(2020, 1, 2), 0.0002), (ms(2020, 1, 5), 0.001)]
    # long pays positive funding; window [Jan 1, Jan 3): first two only; risk 5 on entry 100
    r = sg.funding_r(rates, ms(2020, 1, 1), ms(2020, 1, 3), entry=100.0, risk=5.0)
    assert abs(r - (0.0003 * 100.0 / 5.0)) < 1e-12, r


def test_long_target_hit():
    bars = [bar(100, 101, 99, 100), bar(100, 121, 99, 120)]
    ex_i, ex_p, why, gross = sg.simulate_long(bars, 0, stop=95.0, target=120.0, max_bars=40)
    assert (ex_i, ex_p, why) == (1, 120.0, "target") and abs(gross - 4.0) < 1e-12, (ex_i, ex_p, why, gross)


def test_stop_wins_same_bar_tie():
    bars = [bar(100, 101, 99, 100), bar(100, 130, 90, 100)]
    ex_i, ex_p, why, gross = sg.simulate_long(bars, 0, stop=95.0, target=120.0, max_bars=40)
    assert why == "stop" and ex_p == 95.0 and abs(gross + 1.0) < 1e-12, (why, ex_p, gross)


def test_time_stop_closes_at_bar_close():
    bars = [bar(100, 101, 99, 100 + k * 0.1) for k in range(45)]
    ex_i, ex_p, why, gross = sg.simulate_long(bars, 0, stop=50.0, target=500.0, max_bars=40)
    assert why == "time" and ex_i == 39 and abs(ex_p - bars[39]["c"]) < 1e-12, (ex_i, why)


def test_divergence_event_and_span_stop():
    # swing lows at idx 2 (close 10, RSI 25) and idx 6 (close 9, RSI 30); divergence confirmed at idx 7
    close = [12, 11, 10, 11, 12, 11, 9, 10, 11, 12]
    rsi = [50.0] * 10
    rsi[2], rsi[6], rsi[7] = 25.0, 30.0, 35.0
    low = [c - 0.5 for c in close]
    low[2], low[6] = 9.0, 8.5
    ts = list(range(10))
    evs = sg.bullish_divergences(close, rsi, ts)
    sig = [e for e in evs if e["i"] == 7]
    assert len(sig) == 1, evs
    assert sig[0]["a_i"] == 2 and sig[0]["b_i"] == 6, sig
    assert sg.span_low(low, sig[0]["a_i"], sig[0]["i"]) == 8.5


def test_green_rule():
    bars = [bar(10, 11, 9, 10.5), bar(10, 11, 9, 10.4), bar(10, 11, 9, 9.9)]
    bars[0]["c"], bars[0]["o"] = 10.5, 10.0
    assert sg.is_green(bars, 0) is False   # no prior close
    bars[1]["o"], bars[1]["c"] = 10.0, 10.4
    assert sg.is_green(bars, 1) is False   # close 10.4 < prior close 10.5
    bars[2]["o"], bars[2]["c"] = 9.8, 10.6
    assert sg.is_green(bars, 2) is True    # close > open and close > prior close 10.4


def test_overlap_skip_counted():
    sigs = [5, 6, 9]
    taken, skipped = sg.apply_overlap(sigs, exit_idx_of=lambda i: 8 if i == 5 else i + 1)
    # trade from 5 exits at 8; 6 sits inside it (skipped); 9 is after the exit
    assert taken == [5, 9] and skipped == 1, (taken, skipped)


def test_cluster_se_matches_hand_calc():
    vals = [1.0, -1.0, 2.0, 2.0]
    keys = ["w1", "w1", "w2", "w2"]
    mean, se, n = sg.cluster_mean_se(vals, keys)
    assert n == 4 and abs(mean - 1.0) < 1e-12
    # group sums of deviations: w1 = 0, w2 = 2 -> sqrt(0+4)/4 = 0.5
    assert abs(se - math.sqrt(8) / 4) < 1e-12, se


def test_costs_constant_is_regime_a():
    assert abs(sg.rt_cost_bps() - 12.0) < 1e-12


if __name__ == "__main__":
    fns = [v for k, v in list(globals().items()) if k.startswith("test_") and callable(v)]
    fails = 0
    for f in fns:
        try:
            f()
        except Exception:
            fails += 1
            print("FAIL", f.__name__)
            traceback.print_exc()
    print(f"{len(fns) - fails} passed, {fails} failed")
    sys.exit(1 if fails else 0)
