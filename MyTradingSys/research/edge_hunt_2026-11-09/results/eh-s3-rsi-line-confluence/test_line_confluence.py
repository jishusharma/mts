"""Hand-built tests for line_confluence.py (eh-s3-rsi-line-confluence). Run: python test_line_confluence.py (or pytest)."""
import math
import sys
import tempfile
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import line_confluence as lc  # noqa: E402

H = 3600000


def ms(y, m, d, hh=0):
    import datetime as dt
    return int(dt.datetime(y, m, d, hh, tzinfo=dt.timezone.utc).timestamp() * 1000)


def times(n, tf=H, t0=0):
    return [t0 + i * tf for i in range(n)]


def bar(t, o, h, l, c):
    return {"t": t, "o": float(o), "h": float(h), "l": float(l), "c": float(c)}


# ------------------------------------------------------------------ approach and bounce
def test_bounce_40_basic():
    r = [50, 45, 41, 40, 43, 50]
    ev = lc.find_bounces(r, times(len(r)), H, 40)
    assert [(e["k"], e["j"]) for e in ev] == [(2, 4)], ev


def test_bounce_40_edge_values():
    # 42 exactly is still inside the band; 43 is the first close back above 42
    ev = lc.find_bounces([50, 41, 42, 43], times(4), H, 40)
    assert [(e["k"], e["j"]) for e in ev] == [(1, 3)]
    # band entry needs the previous bar > 42: prev exactly 42 is inside, not an approach from above
    assert lc.find_bounces([42, 41, 43], times(3), H, 40) == []
    # 38 exactly is inside the band (not a break)
    ev = lc.find_bounces([50, 41, 38, 43], times(4), H, 40)
    assert [(e["k"], e["j"]) for e in ev] == [(1, 3)]


def test_bounce_40_break_first_is_no_bounce():
    assert lc.find_bounces([50, 45, 41, 37, 43], times(5), H, 40) == []
    # break (<38) before the bounce, even if it then recovers above 42 within 6 bars
    assert lc.find_bounces([50, 41, 37.9, 44, 45], times(5), H, 40) == []


def test_bounce_window_is_six_bars():
    inside = [41] * 6
    ok = lc.find_bounces([50] + inside + [43], times(8), H, 40)       # k=1, j=7 -> j-k = 6 allowed
    assert [(e["k"], e["j"]) for e in ok] == [(1, 7)]
    late = lc.find_bounces([50] + [41] * 7 + [43], times(9), H, 40)   # j-k = 7 -> none
    assert late == []


def test_approach_from_wrong_side_is_not_an_event():
    # coming from below into 38..42 then up through the band: not an approach from above
    assert lc.find_bounces([30, 39, 43], times(3), H, 40) == []


def test_bounce_60_short_from_below():
    ev = lc.find_bounces([50, 55, 59, 61, 57, 50], times(6), H, 60)
    assert [(e["k"], e["j"]) for e in ev] == [(2, 4)]
    # a close > 62 before dropping back below 58 = break
    assert lc.find_bounces([50, 55, 59, 62.5, 57], times(5), H, 60) == []
    # approach from above into 58..62 is not an event for line 60
    assert lc.find_bounces([70, 61, 57], times(3), H, 60) == []


def test_missing_bar_skips_event():
    t = times(5)
    t[3] += H                                  # a gap between bars 2 and 3
    assert lc.find_bounces([50, 45, 41, 40, 43], t, H, 40) == []


def test_none_rsi_ignored():
    assert lc.find_bounces([None, None, 41, 43], times(4), H, 40) == []


def test_side_of_line():
    assert lc.side_of_line(40) == 1 and lc.side_of_line(60) == -1


# ------------------------------------------------------------------ confluence / HTF bias, no lookahead
def mk_ser():
    four = 4 * H
    return {
        "1h": {"close_t": [h * H for h in range(1, 25)], "rsi": [50.0] * 24, "len": H},
        "4h": {"close_t": [four * i for i in range(1, 7)], "rsi": [41.0, 55.0, 39.0, 50.0, 45.0, 60.0], "len": four},
        "12h": {"close_t": [12 * H, 24 * H], "rsi": [43.0, 52.0], "len": 12 * H},
        "1d": {"close_t": [24 * H], "rsi": [38.5], "len": 24 * H},
    }


def test_confluence_within_two_points_and_closed_only():
    s = mk_ser()
    # T = 12h: 4h bars closed by then: close 12h (rsi 39.0) -> within 2 of 40; 12h bar closed at 12h (43.0): 3 away -> no;
    # 1d bar not closed yet (closes 24h)
    got = lc.confluent_tfs(s, "1h", 12 * H, 40)
    assert got == ["4h"], got
    # T = 24h: 4h last closed = 60.0 (idx 5) -> not at 40; 12h = 52 no; 1d = 38.5 (1.5 away) yes
    assert lc.confluent_tfs(s, "1h", 24 * H, 40) == ["1d"]
    # exactly 2 away counts, 2.01 does not
    s["4h"]["rsi"][2] = 42.0
    assert "4h" in lc.confluent_tfs(s, "1h", 12 * H, 40)
    s["4h"]["rsi"][2] = 42.01
    assert "4h" not in lc.confluent_tfs(s, "1h", 12 * H, 40)


def test_confluence_excludes_trade_tf_and_no_lookahead():
    s = mk_ser()
    s["4h"]["rsi"][2] = 40.0
    assert "4h" not in lc.confluent_tfs(s, "4h", 12 * H, 40)      # a TF is never its own confluence
    # a bar closing one hour AFTER T is invisible: T = 11h, the 4h bar closing at 12h (rsi 40) must not count
    assert "4h" not in lc.confluent_tfs(s, "1h", 11 * H, 40)
    # changing a future bar's value never changes the answer at T
    a = lc.confluent_tfs(s, "1h", 11 * H, 40)
    s["4h"]["rsi"][3] = 40.0
    s["12h"]["rsi"][1] = 40.0
    s["1d"]["rsi"][0] = 40.0
    assert lc.confluent_tfs(s, "1h", 11 * H, 40) == a


def test_confluence_stale_value_is_missing():
    s = {"4h": {"close_t": [4 * H], "rsi": [40.0], "len": 4 * H}}
    assert lc.confluent_tfs(s, "1h", 4 * H + 8 * H, 40) == ["4h"]      # exactly 2 bar lengths old: allowed
    assert lc.confluent_tfs(s, "1h", 4 * H + 8 * H + 1, 40) == []      # older than 2 bar lengths: missing


def test_htf_bias_map_and_threshold():
    assert lc.HTF_OF == {"1h": "4h", "4h": "1d"}
    s = mk_ser()
    assert lc.htf_bias(s, "1h", 4 * H) == "down"      # first 4h bar closes at 4h with rsi 41 (< 50)
    assert lc.htf_bias(s, "1h", 8 * H) == "up"        # second 4h bar rsi 55


def test_htf_bias_values():
    s = {"4h": {"close_t": [4 * H, 8 * H, 12 * H], "rsi": [60.0, 50.0, 49.0], "len": 4 * H},
         "1d": {"close_t": [24 * H], "rsi": [30.0], "len": 24 * H}}
    assert lc.htf_bias(s, "1h", 4 * H) == "up"
    assert lc.htf_bias(s, "1h", 8 * H) is None         # exactly 50 = no bias
    assert lc.htf_bias(s, "1h", 12 * H) == "down"
    assert lc.htf_bias(s, "4h", 24 * H) == "down"
    assert lc.htf_bias(s, "4h", 23 * H) is None        # 1d bar not closed yet
    assert lc.htf_bias(s, "1h", 3 * H) is None         # nothing closed


def test_against():
    assert lc.is_against(+1, "down") and not lc.is_against(+1, "up")       # long while down
    assert lc.is_against(-1, "up") and not lc.is_against(-1, "down")       # short while up
    assert not lc.is_against(+1, None) and not lc.is_against(-1, None)


# ------------------------------------------------------------------ stop and exit
def test_structural_stop():
    bars = [bar(0, 50, 52, 48, 49), bar(H, 49, 50, 46, 47), bar(2 * H, 47, 51, 47, 50)]
    assert lc.structural_stop(bars, 0, 2, +1) == 46
    assert lc.structural_stop(bars, 0, 2, -1) == 52
    assert lc.structural_stop(bars, 1, 2, -1) == 51


def flat(n, px=100.0, t0=0):
    return [bar(t0 + i * H, px, px + 0.1, px - 0.1, px) for i in range(n)]


def test_simulate_long_target_stop_tie_gap_time():
    bars = flat(60)
    # target: entry 100, stop 98 -> target 105
    bars[5] = bar(5 * H, 100, 106, 99, 105)
    ex, px, why, g = lc.simulate(bars, 3, +1, 100.0, 98.0)
    assert (ex, why) == (5, "target") and abs(px - 105) < 1e-9 and abs(g - 2.5) < 1e-9
    # same bar touches both: stop wins
    bars = flat(60)
    bars[4] = bar(4 * H, 100, 106, 97, 100)
    ex, px, why, g = lc.simulate(bars, 3, +1, 100.0, 98.0)
    assert (ex, why) == (4, "stop") and abs(g + 1.0) < 1e-9
    # gap through the stop fills at the open (worse than -1R)
    bars = flat(60)
    bars[4] = bar(4 * H, 96, 97, 95, 96)
    ex, px, why, g = lc.simulate(bars, 3, +1, 100.0, 98.0)
    assert why == "stop" and px == 96 and abs(g + 2.0) < 1e-9
    # time stop: close of the 48th bar after the entry bar (bars j+1 .. j+48)
    bars = flat(80)
    ex, px, why, g = lc.simulate(bars, 3, +1, 100.0, 98.0)
    assert (ex, why) == (3 + 48, "time") and abs(g) < 1e-9
    # entering on bar 3 means bar 3 itself is NOT scanned (entry at its close)
    bars = flat(60)
    bars[3] = bar(3 * H, 100, 200, 1, 100)
    assert lc.simulate(bars, 3, +1, 100.0, 98.0)[2] == "time"


def test_simulate_short_and_censored():
    bars = flat(60)
    bars[5] = bar(5 * H, 100, 101, 94, 95)          # entry 100, stop 102 -> risk 2, target 95
    ex, px, why, g = lc.simulate(bars, 3, -1, 100.0, 102.0)
    assert (ex, why) == (5, "target") and abs(g - 2.5) < 1e-9
    bars = flat(60)
    bars[4] = bar(4 * H, 100, 103, 99, 101)
    ex, px, why, g = lc.simulate(bars, 3, -1, 100.0, 102.0)
    assert why == "stop" and abs(g + 1.0) < 1e-9
    assert lc.simulate(flat(20), 3, +1, 100.0, 98.0)[2] == "censored"


# ------------------------------------------------------------------ fee / funding / R arithmetic
def test_costs_regime_a():
    assert abs(lc.rt_cost_bps() - 12.0) < 1e-9
    assert abs(lc.fee_r(100.0, 99.0) - 0.12) < 1e-9          # stop 100 bps -> 12/100
    assert abs(lc.fee_r(100.0, 101.0) - 0.12) < 1e-9          # short: same distance


def test_funding_sign_and_window():
    rates = [(100, 0.0001), (200, 0.0002), (300, -0.0001)]
    # t_in < calc_time <= t_out : record at 100 excluded when t_in = 100, included at t_out = 300
    f_long = lc.funding_r(rates, 100, 300, +1, 100.0, 1.0)
    assert abs(f_long - (0.0002 - 0.0001) * 100.0 / 1.0) < 1e-12
    f_short = lc.funding_r(rates, 100, 300, -1, 100.0, 1.0)
    assert abs(f_short + f_long) < 1e-12


def test_evaluate_entry_net_r():
    # long: k=1 low 98 -> stop 98, entry close of bar j=3 at 100 -> risk 2, target 105
    bars = [bar(0, 101, 102, 100, 101), bar(H, 101, 101, 98, 99), bar(2 * H, 99, 100, 99, 99.5),
            bar(3 * H, 99.5, 100.5, 99.4, 100)] + flat(60, 100.0, 4 * H)
    bars[6] = bar(6 * H, 100, 106, 100, 105)
    rates = [(4 * H + 1, 0.0005)]                              # inside (entry close 4h, exit close 7h]
    res = lc.evaluate_entry(bars, 1, 3, +1, H, rates)
    assert res["why"] == "target" and abs(res["gross"] - 2.5) < 1e-9
    assert abs(res["fee_r"] - 12.0 / 200.0) < 1e-9
    assert abs(res["funding_r"] - 0.0005 * 100.0 / 2.0) < 1e-9
    assert abs(res["net"] - (2.5 - 0.06 - 0.025)) < 1e-9
    assert res["stop"] == 98 and res["exit_idx"] == 6
    # stop equal to the entry is invalid
    bad = [bar(0, 100, 101, 100, 100), bar(H, 100, 100, 100, 100), bar(2 * H, 100, 101, 100, 100)] + flat(60, 100, 3 * H)
    assert lc.evaluate_entry(bad, 0, 2, +1, H, []) == "invalid"
    # censored
    assert lc.evaluate_entry(bars[:6], 1, 3, +1, H, []) == "censored"


# ------------------------------------------------------------------ resampling, no lookahead
def test_resample_complete_buckets_only():
    h1 = [bar(i * H, 10 + i, 20 + i, 5 + i, 11 + i) for i in range(48)]
    d = lc.resample_complete(h1, 24 * H)
    assert len(d) == 2 and d[0]["t"] == 0 and d[0]["o"] == 10 and d[0]["c"] == 11 + 23
    assert d[0]["h"] == 20 + 23 and d[0]["l"] == 5
    h1_gap = [b for b in h1 if b["t"] != 30 * H]
    d2 = lc.resample_complete(h1_gap, 24 * H)
    assert len(d2) == 1 and d2[0]["t"] == 0                  # the incomplete second day is dropped
    d12 = lc.resample_complete(h1, 12 * H)
    assert len(d12) == 4 and d12[1]["t"] == 12 * H
    # a still-forming bucket at the end of the data is not emitted
    assert len(lc.resample_complete(h1[:47], 24 * H)) == 1


def test_series_close_time_is_open_plus_length():
    h1 = [bar(i * H, 100 + (i % 3), 101 + (i % 3), 99, 100 + (i % 5)) for i in range(60)]
    ser = lc.build_series_from(h1, [bar(i * 4 * H, 100, 101, 99, 100) for i in range(15)])
    assert ser["1h"]["close_t"][0] == H
    assert ser["4h"]["close_t"][0] == 4 * H
    assert ser["12h"]["close_t"][0] == 12 * H
    assert ser["1d"]["close_t"][0] == 24 * H


# ------------------------------------------------------------------ splits
def test_split_refusal():
    rows = [{"t": ms(2024, 6, 30)}, {"t": ms(2024, 7, 1)}]
    try:
        lc.check_window(rows, lc.DEV_LO, lc.DEV_END_EXCL)
    except lc.SplitViolation:
        pass
    else:
        raise AssertionError("DEV window must refuse a bar at 2024-07-01")
    lc.check_window(rows[:1], lc.DEV_LO, lc.DEV_END_EXCL)
    try:
        lc.check_window([{"t": ms(2025, 7, 1)}], lc.DEV_LO, lc.VAL_END_EXCL)
    except lc.SplitViolation:
        pass
    else:
        raise AssertionError("loader must refuse HOLDOUT bars")


def test_loader_refuses_holdout_and_never_opens_late_files():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "BTCUSDT" / "1h" / "klines"
        p.mkdir(parents=True)
        (p / "BTCUSDT-1h-2025-06.csv").write_text(f"{ms(2025, 6, 30, 23)},1,1,1,1,1,0,0,0,0,0,0\n")
        (p / "BTCUSDT-1h-2025-07.csv").write_text("THIS FILE MUST NOT BE READ\n")
        rows = lc.load_spot("BTCUSDT", "1h", lc.VAL_END_EXCL, root=d)
        assert len(rows) == 1
        # a 2025-06 named file that holds a 2025-07-01 row is a violation
        (p / "BTCUSDT-1h-2025-06.csv").write_text(f"{ms(2025, 7, 1)},1,1,1,1,1,0,0,0,0,0,0\n")
        try:
            lc.load_spot("BTCUSDT", "1h", lc.VAL_END_EXCL, root=d)
        except lc.SplitViolation:
            pass
        else:
            raise AssertionError("row at 2025-07-01 must be refused")
        # data_end past the VALIDATION end is refused outright
        try:
            lc.load_spot("BTCUSDT", "1h", ms(2025, 8, 1), root=d)
        except lc.SplitViolation:
            pass
        else:
            raise AssertionError("data_end beyond 2025-07-01 must be refused")


def test_load_filters_to_data_end_and_microseconds():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "ETHUSDT" / "1h" / "klines"
        p.mkdir(parents=True)
        (p / "ETHUSDT-1h-2024-06.csv").write_text(
            f"{ms(2024, 6, 30, 22)},1,1,1,1,1,0,0,0,0,0,0\n{ms(2024, 6, 30, 23) * 1000},2,2,2,2,1,0,0,0,0,0,0\n")
        (p / "ETHUSDT-1h-2024-07.csv").write_text(f"{ms(2024, 7, 1)},3,3,3,3,1,0,0,0,0,0,0\n")
        rows = lc.load_spot("ETHUSDT", "1h", lc.DEV_END_EXCL, root=d)
        assert [r["c"] for r in rows] == [1.0, 2.0]               # the 2024-07 file is not DEV; us stamps normalised
        assert rows[1]["t"] == ms(2024, 6, 30, 23)


# ------------------------------------------------------------------ overlap and statistics
def test_overlap_one_trade_at_a_time():
    exits = {10: 15, 12: 20, 15: 18, 30: 31}
    taken, skipped = lc.apply_overlap([10, 12, 15, 30], lambda j: exits[j])
    assert taken == [10, 15, 30] and skipped == 1                 # 12 < busy-until 15; 15 == exit bar is allowed


def test_cluster_se_and_screen():
    mean, se, n = lc.cluster_mean_se([1, 1, -1, -1], ["a", "a", "b", "b"])
    assert n == 4 and abs(mean) < 1e-12 and abs(se - math.sqrt(8) / 4) < 1e-12


def test_summarize_cluster_key_day_vs_week():
    t1 = {"net": 1.0, "gross": 1.0, "fee_r": 0.0, "funding_r": 0.0, "tf": "1h", "day": "d1", "week": "w1"}
    t2 = {"net": 1.0, "gross": 1.0, "fee_r": 0.0, "funding_r": 0.0, "tf": "1h", "day": "d2", "week": "w1"}
    t3 = {"net": -1.0, "gross": -1.0, "fee_r": 0.0, "funding_r": 0.0, "tf": "4h", "day": "d3", "week": "w1"}
    assert lc.cluster_key([t1, t2]) == "day"
    assert lc.cluster_key([t1, t3]) == "week"
    s = lc.summarize([t1, t2, t3])
    assert s["n"] == 3 and abs(s["net"] - 1 / 3) < 1e-12 and s["hit"] == 2 / 3


def test_dev_screen_and_holm():
    assert lc.dev_screen({"n": 30, "net": 0.1, "lo": 0.01})
    assert not lc.dev_screen({"n": 29, "net": 0.1, "lo": 0.01})
    assert not lc.dev_screen({"n": 30, "net": 0.1, "lo": -0.01})
    h = lc.holm_adjust({"T11": 0.001, "T12": 0.02}, 15)
    assert abs(h["T11"] - 0.015) < 1e-12 and abs(h["T12"] - 0.28) < 1e-12
    h = lc.holm_adjust({"T11": 0.02, "T12": 0.001}, 15)
    assert abs(h["T12"] - 0.015) < 1e-12 and abs(h["T11"] - 0.28) < 1e-12
    h = lc.holm_adjust({"T11": 0.0001, "T12": 0.0002}, 15)       # monotone: second >= first
    assert h["T12"] >= h["T11"]


def test_verdict_rules():
    dev_ok = {"n": 100, "net": 0.2, "lo": 0.05, "hi": 0.35, "mde": 0.3, "se": 0.08}
    assert lc.verdict("T11", dev_ok, None, None) == "INCONCLUSIVE"     # screened in, validation missing
    assert lc.verdict("T11", dev_ok, {"net": 0.1}, 0.04) == "PASS"
    assert lc.verdict("T11", dev_ok, {"net": 0.1}, 0.06) == "INCONCLUSIVE"
    assert lc.verdict("T11", dev_ok, {"net": -0.1}, 0.01) == "INCONCLUSIVE"
    dev_neg = {"n": 500, "net": -0.1, "lo": -0.15, "hi": -0.05, "mde": 0.2, "se": 0.03}
    assert lc.verdict("T12", dev_neg, None, None) == "FAIL"
    dev_neg2 = {"n": 40, "net": -0.1, "lo": -0.9, "hi": 0.7, "mde": 0.5, "se": 0.4}
    assert lc.verdict("T12", dev_neg2, None, None) == "INCONCLUSIVE"


def test_asof_regime_helper():
    assert lc.asof_val([10, 20, 30], [1.0, None, 3.0], 25) == 1.0     # latest non-None value
    assert lc.asof_val([10, 20, 30], [1.0, 2.0, 3.0], 20) == 2.0
    assert lc.asof_val([10, 20, 30], [1.0, 2.0, 3.0], 9) is None


def main():
    fails = 0
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for name, fn in tests:
        try:
            fn()
        except Exception:
            fails += 1
            print("FAIL", name)
            traceback.print_exc()
    print(f"{len(tests) - fails} passed, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
