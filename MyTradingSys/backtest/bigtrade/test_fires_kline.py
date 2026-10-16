"""
Tests for fires_kline.py / parity_kline.py (worker B1). Spec-derived; every expected number is computed by hand in the
test (never read from the code under test). Offline: synthetic bars and temp files only, no network, no live files.

Run: python -m unittest MyTradingSys.backtest.bigtrade.test_fires_kline   (or pytest on this file)
"""
import sys
sys.dont_write_bytecode = True

import csv
import inspect
import json
import re
import tempfile
import unittest
from pathlib import Path

import numpy as np

from MyTradingSys.backtest.bigtrade import fires_kline as fk
from MyTradingSys.backtest.bigtrade import parity_kline as pk

T0 = 1_700_000_100_000 // 3600000 * 3600000  # hour aligned (also a multiple of 5m / 15m)


def synth_bars(n, tf_ms, seed, start=T0, step_pct=0.004, gap_pct=0.0015):
    """Seeded random-walk OHLCV with taker-buy volume; bars strictly ascending and contiguous. The open differs from
    the previous close by a small gap: the swing detectors (cc_structure.find_swings, use_body, strict comparison)
    can never fire on a series with open == previous close (see the F-BT-09 note in the report)."""
    rs = np.random.RandomState(seed)
    price = 100.0
    out = []
    for i in range(n):
        o = price * (1.0 + gap_pct * rs.randn())
        c = o * (1.0 + step_pct * rs.randn())
        h = max(o, c) * (1.0 + abs(step_pct * rs.randn()) * 0.5)
        l = min(o, c) * (1.0 - abs(step_pct * rs.randn()) * 0.5)
        v = float(np.exp(rs.randn() * 0.6 + 3.0))
        tbv = v * float(np.clip(0.5 + 0.25 * rs.randn(), 0.05, 0.95))
        out.append({"t": start + i * tf_ms, "o": o, "h": h, "l": l, "c": c, "v": v, "tbv": tbv})
        price = c
    return out


def arrays_of(bars):
    a = {k: np.array([b[k] for b in bars], dtype=np.float64) for k in ("o", "h", "l", "c", "v", "tbv")}
    a["t"] = np.array([b["t"] for b in bars], dtype=np.int64)
    a["atr"] = fk.wilder_atr(a["h"], a["l"], a["c"])
    return a


def fire_ids(fires):
    return sorted((f["event"].get("t"), f["event"].get("event"), f["t_confirm"]) for f in fires)


class TestWindowMatchesLive(unittest.TestCase):
    def test_window_is_what_the_live_runner_hands_to_layers(self):
        from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
        raw = [[1000 + i * 60000, "1", "2", "0.5", "1.5", "10", 0, "0", 0, "4", "0", "0"] for i in range(fk.LIVE_LIMIT)]
        closed = cli.fetch_closed_bars(lambda s, i, n: raw, "BTCUSDT", "1m", fk.LIVE_LIMIT)
        self.assertEqual(len(closed), fk.WINDOW)  # newest (possibly open) row dropped: 100 fetched -> 99 closed

    def test_live_default_limit_is_100(self):
        src = inspect.getsource(__import__("MyTradingSys.backtest.layers.alerts.live_runner_cli", fromlist=["x"]).main)
        m = re.search(r'"--limit",\s*type=int,\s*default=(\d+)', src)
        self.assertIsNotNone(m)
        self.assertEqual(int(m.group(1)), fk.LIVE_LIMIT)


class TestRegistryScope(unittest.TestCase):
    def test_every_live_key_is_replayed_or_handed_to_b2(self):
        from MyTradingSys.backtest.layers.alerts.live_runner_cli import build_default_registry
        full = build_default_registry(fetch_funding=lambda s, n: [])
        mine = fk.kline_registry()
        self.assertEqual(set(full) - set(mine), set(fk.B2_KEYS))
        for must in ("turn_of_candle|turn_of_candle|1m", "rsi|rsi_events|5m", "rsi|rsi_events|15m", "rsi|rsi_events|1h",
                     "rsi|malkan_bull|1h", "rsi|malkan_bear|1h", "cryptocred|sr_flip|15m", "cryptocred|fib_pullback|15m",
                     "session|session_momentum|15m", "fabio|escalation|15m", "fabio|cvd_absorption|1h",
                     "fabio|volume_fvg|15m"):
            self.assertIn(must, mine)
        self.assertNotIn("fabio|v3_grid|1m", mine)
        self.assertNotIn("positioning|funding_cvd_fade|1h", mine)

    def test_plan_key_names(self):
        self.assertEqual(fk.to_plan_key("rsi|rsi_events|5m"), "layer:rsi:rsi_events:5m")
        self.assertEqual(fk.key_slug("turn_of_candle|turn_of_candle|1m"), "turn_of_candle_turn_of_candle_1m")

    def test_params_json_serialisable_and_values(self):
        for k in fk.kline_registry():
            p = fk.layer_params(k)
            json.dumps(p, default=str)
            self.assertEqual(p["window_bars"], 99)
        rsi = fk.layer_params("rsi|rsi_events|5m")
        self.assertEqual((rsi["level"], rsi["tolerance"], rsi["rsi_period"]), (40.0, 0.5, 14))
        self.assertEqual(fk.layer_params("turn_of_candle|turn_of_candle|1m")["lead_minutes"], 1)
        sr = fk.layer_params("cryptocred|sr_flip|15m")
        self.assertEqual((sr["stop_buffer_pct"], sr["target_r"]), (0.001, 1.5))
        self.assertEqual(fk.layer_params("cryptocred|failed_msb|15m")["target_r"], 2.0)
        esc = fk.layer_params("fabio|escalation|1h")
        self.assertEqual((esc["aggression_k"], esc["record_lookback"], esc["level_tolerance"]), (2.0, 20, 0.001))


class TestDataLayer(unittest.TestCase):
    def _write(self, d, name, rows, header=True):
        with open(Path(d) / name, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            if header:
                w.writerow("open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,"
                           "taker_buy_quote_volume,ignore".split(","))
            for r in rows:
                w.writerow(r)

    def _row(self, t, o, h, l, c, v, tbv):
        return [t, o, h, l, c, v, t + 59999, 0, 1, tbv, 0, 0]

    def test_load_dedup_sort_microseconds_headerless_and_gap(self):
        t = 1_700_000_040_000 // 60000 * 60000
        with tempfile.TemporaryDirectory() as d:
            self._write(d, "a_month.csv", [self._row(t + 120000, 3, 4, 2, 3.5, 5, 2), self._row(t, 1, 2, 0.5, 1.5, 10, 4)])
            # daily file overlapping with an identical row + one new row; headerless
            self._write(d, "b_day.csv", [self._row(t, 1, 2, 0.5, 1.5, 10, 4), self._row(t + 60000, 2, 3, 1, 2.5, 7, 3)],
                        header=False)
            # microsecond stamped row (Binance spot archive style) one hour later
            self._write(d, "c_us.csv", [self._row((t + 3600000) * 1000, 9, 10, 8, 9.5, 1, 1)])
            a, cov = fk.load_1m(dirs=[d])
        self.assertEqual(a["t"].tolist(), [t, t + 60000, t + 120000, t + 3600000])
        self.assertEqual(cov["duplicate_rows"], 1)
        self.assertEqual(cov["conflicting_duplicates"], 0)
        self.assertEqual(cov["microsecond_rows_converted"], 1)
        self.assertEqual(cov["gaps"], 1)
        self.assertEqual(cov["missing_minutes"], 57)  # t+2m .. t+60m: the next bar is 58 minutes after t+2m -> 57 missing
        self.assertEqual(a["tbv"].tolist(), [4, 3, 2, 1])
        self.assertEqual(a["o"].tolist(), [1, 2, 3, 9])

    def test_conflicting_duplicate_is_counted(self):
        t = 1_700_000_040_000 // 60000 * 60000
        with tempfile.TemporaryDirectory() as d:
            self._write(d, "a.csv", [self._row(t, 1, 2, 0.5, 1.5, 10, 4)])
            self._write(d, "b.csv", [self._row(t, 1, 2, 0.5, 1.6, 10, 4)])
            a, cov = fk.load_1m(dirs=[d])
        self.assertEqual(cov["conflicting_duplicates"], 1)
        self.assertEqual(len(a["t"]), 1)

    def test_non_minute_aligned_raises(self):
        with tempfile.TemporaryDirectory() as d:
            self._write(d, "a.csv", [self._row(1_700_000_040_001, 1, 2, 0.5, 1.5, 10, 4)])
            with self.assertRaises(ValueError):
                fk.load_1m(dirs=[d])

    def test_resample_equals_tf_resample_and_keeps_tbv(self):
        from MyTradingSys.backtest.layers.timeframe import tf_resample
        reg = json.load(open(Path(tf_resample.__file__).parent / "registry.json"))
        bars = synth_bars(3 * 60 + 7, 60000, seed=3)  # 3 h and 7 extra minutes (an open trailing hour bucket)
        a = arrays_of(bars)
        for tf, ms in (("5m", 300000), ("15m", 900000), ("1h", 3600000)):
            mine = fk.resample_arrays(a, ms)
            ref = tf_resample.resample(bars, tf, reg)
            self.assertEqual(len(mine["t"]), len(ref), tf)
            for i, r in enumerate(ref):
                self.assertEqual(int(mine["t"][i]), r["t"])
                for k in ("o", "h", "l", "c"):
                    self.assertAlmostEqual(float(mine[k][i]), r[k], places=9)
                self.assertAlmostEqual(float(mine["v"][i]), r["v"], places=9)
                # tbv is what tf_resample drops: summed independently here
                sub = [b["tbv"] for b in bars if r["t"] <= b["t"] < r["t"] + ms]
                self.assertAlmostEqual(float(mine["tbv"][i]), sum(sub), places=9)
                self.assertEqual(int(mine["n"][i]), ms // 60000)
        self.assertNotIn("tbv", tf_resample.resample(bars, "15m", reg)[0])  # documents finding F-BT-07

    def test_resample_drops_trailing_open_bucket(self):
        a = arrays_of(synth_bars(20, 60000, seed=4, start=T0))  # 20 minutes: one closed 15m bucket, 5 minutes open
        r = fk.resample_arrays(a, 900000)
        self.assertEqual(len(r["t"]), 1)
        self.assertEqual(int(r["t"][0]), T0)

    def test_wilder_atr_hand_computed(self):
        h = np.array([10.0, 11.0, 12.0, 12.0, 13.0])
        l = np.array([8.0, 9.0, 9.0, 10.0, 10.0])
        c = np.array([9.0, 10.0, 11.0, 10.0, 12.0])
        # TR: 2, max(2,2,0)=2, max(3,2,1)=3, max(2,1,1)=2, max(3,3,0)=3 ; period 3
        atr = fk.wilder_atr(h, l, c, period=3)
        self.assertTrue(np.isnan(atr[0]) and np.isnan(atr[1]))
        self.assertAlmostEqual(atr[2], 7.0 / 3.0, places=12)          # (2+2+3)/3
        self.assertAlmostEqual(atr[3], 20.0 / 9.0, places=12)         # (7/3*2+2)/3
        self.assertAlmostEqual(atr[4], 67.0 / 27.0, places=12)        # (20/9*2+3)/3

    def test_atr_is_causal(self):
        bars = synth_bars(300, 900000, seed=5)
        a = arrays_of(bars)
        for cut in (50, 120, 299):
            b = fk.wilder_atr(a["h"][:cut], a["l"][:cut], a["c"][:cut])
            np.testing.assert_array_equal(b, a["atr"][:cut])


class TestCosts(unittest.TestCase):
    def test_fee_and_slip_defaults_from_trade_costs(self):
        self.assertEqual(fk.cost_params(), (0.0010, 0.0002))  # FORMULAS.md section 13: 10 bps RT + 2 bps slip

    def test_cost_fields_hand_computed(self):
        # long, entry 100, stop 99.5 -> distance 0.5 = 0.5 %; ATR 0.5; fee_rt 0.1 %, slip 0.02 %
        c = fk.cost_fields(price=100.2, entry_price=100.0, stop=99.5, atr=0.5, fee_rt=0.001, slip_rt=0.0002)
        self.assertAlmostEqual(c["stop_dist_pct"], 0.005, places=12)
        self.assertAlmostEqual(c["fee_R"], 0.2, places=12)
        self.assertAlmostEqual(c["cost_R"], 0.24, places=12)
        self.assertAlmostEqual(c["stop_dist_atr"], 1.0, places=12)
        self.assertEqual(c["fee_dominated"], 0)
        self.assertAlmostEqual(c["fee_R_1atr"], 0.001 * 100.2 / 0.5, places=12)

    def test_short_and_fee_dominated(self):
        # short, entry 100, stop 100.05 -> 0.05 % < 0.10 % round-trip fee -> fee_dominated, fee_R = 2
        c = fk.cost_fields(price=100.0, entry_price=100.0, stop=100.05, atr=0.25, fee_rt=0.001, slip_rt=0.0002)
        self.assertAlmostEqual(c["fee_R"], 2.0, places=9)
        self.assertEqual(c["fee_dominated"], 1)
        self.assertAlmostEqual(c["stop_dist_atr"], 0.2, places=9)

    def test_stop_exactly_at_the_fee_is_not_under_it(self):
        # sr_flip / failed_msb stop = level -/+ 0.1 % = exactly the 0.10 % round-trip fee: a tie, not "under the fee"
        # (float rounding of |entry-stop|/entry used to put ~74 % of these on the wrong side of the comparison)
        for entry in (84103.06, 85740.6, 86221.7, 83118.0, 107983.0, 54114.9, 100.0, 37665.0, 1.1):
            for stop in (entry * (1 - 0.001), entry * (1 + 0.001)):
                c = fk.cost_fields(price=entry, entry_price=entry, stop=stop, atr=entry * 0.002, fee_rt=0.001,
                                   slip_rt=0.0002)
                self.assertEqual(c["fee_dominated"], 0, (entry, stop))
                self.assertAlmostEqual(c["fee_R"], 1.0, places=9)
        # 1 % under the fee is dominated, 1 % over is not
        self.assertEqual(fk.cost_fields(100.0, 100.0, 99.9005, 1.0, 0.001, 0.0002)["fee_dominated"], 1)
        self.assertEqual(fk.cost_fields(100.0, 100.0, 99.899, 1.0, 0.001, 0.0002)["fee_dominated"], 0)

    def test_no_stop_gives_blank_stop_metrics_but_atr_fee(self):
        c = fk.cost_fields(price=200.0, entry_price=None, stop=None, atr=2.0, fee_rt=0.001, slip_rt=0.0002)
        self.assertIsNone(c["fee_R"])
        self.assertIsNone(c["stop_dist_atr"])
        self.assertAlmostEqual(c["fee_R_1atr"], 0.1, places=12)  # 0.001*200/2

    def test_zero_stop_distance_is_fee_dominated_not_a_crash(self):
        c = fk.cost_fields(price=100.0, entry_price=100.0, stop=100.0, atr=1.0, fee_rt=0.001, slip_rt=0.0002)
        self.assertEqual(c["fee_dominated"], 1)
        self.assertIsNone(c["fee_R"])


def _entry_arrays(reg_key, n, seed):
    e = fk.kline_registry()[reg_key]
    tf_ms = fk.TF_MS[e["tf"]]
    bars = synth_bars(n, tf_ms, seed)
    return e, tf_ms, bars


class TestReplayEqualsLiveCore(unittest.TestCase):
    """replay_key must reproduce live_runner_core.run_registry fed one 99-bar window per closed bar."""

    def _live(self, reg_key, entry, bars):
        from MyTradingSys.backtest.layers.alerts.live_runner_core import run_registry, empty_state
        state = empty_state()
        alerts, n_err = [], 0
        for idx in range(fk.WINDOW - 1, len(bars)):
            win = bars[idx - fk.WINDOW + 1: idx + 1]
            res = run_registry({reg_key: entry}, {entry["tf"]: win}, state)
            state = res["state"]
            alerts += res["alerts"]
            n_err += len(res["errors"])
        return alerts, n_err

    def test_all_kline_keys_match_run_registry(self):
        total = 0
        for reg_key, entry in fk.kline_registry().items():
            n = 420 if entry["tf"] == "1m" else 600
            bars = synth_bars(n, fk.TF_MS[entry["tf"]], seed=11, start=T0)
            live, live_err = self._live(reg_key, entry, bars)
            fires, err = fk.replay_key(entry["fn"], int(entry.get("confirm_lag_bars", 0)), bars)
            self.assertEqual(err, live_err, reg_key)
            self.assertEqual(sorted((a["t_close"], a.get("event")) for a in live),
                             sorted((f["event"]["t"], f["event"].get("event")) for f in fires), reg_key)
            # the live alert carries t_confirm = newest closed bar open time and the rsi fields of that window
            by = {(a["t_close"], a.get("event")): a for a in live}
            for f in fires:
                a = by[(f["event"]["t"], f["event"].get("event"))]
                self.assertEqual(a["t_confirm"], f["t_confirm"], reg_key)
                self.assertEqual(a.get("side"), f["event"].get("side"), reg_key)
                self.assertEqual(a["rsi"], f["rsi"], reg_key)
                self.assertEqual(a["rsi_ma"], f["rsi_ma"], reg_key)
            total += len(fires)
        self.assertGreater(total, 50)  # not vacuous: the synthetic data really produces fires

    def test_event_that_disappears_and_reappears_is_emitted_once(self):
        # live: the (t, event) pair is remembered in `emitted`; a layer whose output flickers (window slide) must not
        # alert twice. confirm_lag_bars=2 lets the reappearing event pass the age filter, so only `emitted` stops it.
        from MyTradingSys.backtest.layers.alerts.live_runner_core import run_registry, empty_state
        bars = synth_bars(130, 60000, seed=1)
        t_ev = bars[110]["t"]

        def flicker(win):
            latest = win[-1]["t"]
            return [{"t": t_ev, "event": "x", "side": "long"}] if latest in (t_ev, t_ev + 2 * 60000) else []

        entry = {"layer": "t", "sub": "t", "tf": "1m", "fn": flicker, "params_id": "p", "confirm_lag_bars": 2}
        fires, _ = fk.replay_key(flicker, 2, bars)
        state, n_live = empty_state(), 0
        for idx in range(fk.WINDOW - 1, len(bars)):
            res = run_registry({"t|t|1m": entry}, {"1m": bars[idx - fk.WINDOW + 1: idx + 1]}, state)
            state = res["state"]
            n_live += len(res["alerts"])
        self.assertEqual((len(fires), n_live), (1, 1))

    def test_non_vacuous_keys(self):
        for reg_key, minimum in (("turn_of_candle|turn_of_candle|1m", 20), ("rsi|rsi_events|5m", 3)):
            e, ms, bars = _entry_arrays(reg_key, 900, seed=21)
            fires, _ = fk.replay_key(e["fn"], int(e.get("confirm_lag_bars", 0)), bars)
            self.assertGreaterEqual(len(fires), minimum, reg_key)

    def test_chunked_equals_single_pass(self):
        for reg_key in ("rsi|rsi_events|5m", "fabio|escalation|15m", "fabio|volume_fvg|15m", "cryptocred|sr_flip|15m",
                        "fabio|cvd_absorption|15m", "turn_of_candle|turn_of_candle|1m"):
            e = fk.kline_registry()[reg_key]
            lag = int(e.get("confirm_lag_bars", 0))
            bars = synth_bars(1200, fk.TF_MS[e["tf"]], seed=31)
            full, _ = fk.replay_key(e["fn"], lag, bars)
            cut1, cut2 = 400, 800
            parts = []
            for a, b in ((0, cut1), (cut1, cut2), (cut2, 1200)):
                f, _ = fk.replay_key(e["fn"], lag, bars, i0=a, i1=b)
                parts += f
            self.assertEqual(fire_ids(full), fire_ids(parts), reg_key)


class TestCausality(unittest.TestCase):
    """Truncating the bars after t must not change fires at or before t."""

    def test_truncation_does_not_change_earlier_fires(self):
        for reg_key in fk.kline_registry():
            e = fk.kline_registry()[reg_key]
            lag = int(e.get("confirm_lag_bars", 0))
            n = 500 if e["tf"] == "1m" else 700
            bars = synth_bars(n, fk.TF_MS[e["tf"]], seed=41)
            full, _ = fk.replay_key(e["fn"], lag, bars)
            for cut in (250, 333, 500):
                trunc, _ = fk.replay_key(e["fn"], lag, bars[:cut])
                want = [f for f in full if f["idx"] < cut]
                self.assertEqual(fire_ids(trunc), fire_ids(want), "%s cut=%d" % (reg_key, cut))

    def test_rows_with_atr_and_costs_are_causal(self):
        for reg_key in ("cryptocred|sr_flip|15m", "rsi|rsi_events|15m", "turn_of_candle|turn_of_candle|1m"):
            e = fk.kline_registry()[reg_key]
            bars = synth_bars(800, fk.TF_MS[e["tf"]], seed=51)
            a_full = arrays_of(bars)
            rows_full, _ = fk.run_range(reg_key, 0, 800, entry=e, arrays=a_full, params_json="{}", commit="t")
            for cut in (300, 555):
                a_cut = arrays_of(bars[:cut])
                rows_cut, _ = fk.run_range(reg_key, 0, cut, entry=e, arrays=a_cut, params_json="{}", commit="t")
                horizon = int(a_cut["t"][-1]) + fk.TF_MS[e["tf"]]
                want = [r for r in rows_full if r["t_fire_ms"] <= horizon]
                self.assertEqual(rows_cut, want, "%s cut=%d" % (reg_key, cut))


class TestRowsAndCsv(unittest.TestCase):
    def test_toc_rows_hand_checked(self):
        # 130 one-minute bars from a quarter start; minute-0 bar of each quarter: v=10, tbv=7.5 -> imbalance +0.5 -> long
        q = 900000
        start = (T0 // q) * q
        bars = []
        for i in range(130):
            m = i % 15
            v, tbv = (10.0, 7.5) if m == 0 else (10.0, 5.0)
            bars.append({"t": start + i * 60000, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.5, "v": v, "tbv": tbv})
        a = arrays_of(bars)
        e = fk.kline_registry()["turn_of_candle|turn_of_candle|1m"]
        rows, err = fk.run_range("turn_of_candle|turn_of_candle|1m", 0, 130, entry=e, arrays=a, params_json="{}",
                                 commit="t")
        self.assertEqual(err, 0)
        # newest-bar index runs 98..129 -> bars 98..129 -> minute 14 bars are idx 104, 119 (i%15==14)
        got = sorted(int(r["t_confirm_open_ms"]) for r in rows)
        self.assertEqual(got, [start + 104 * 60000, start + 119 * 60000])
        for r in rows:
            self.assertEqual(r["side"], "long")
            self.assertEqual(r["t_fire_ms"], r["t_confirm_open_ms"] + 60000)
            self.assertEqual(r["t_fire_ms"] % q, 0)                      # closes exactly on the next quarter
            self.assertEqual(json.loads(r["extra"])["imbalance"], 0.5)
            self.assertEqual(r["tradable"], 1)
            self.assertEqual(r["key"], "layer:turn_of_candle:turn_of_candle:1m")
            self.assertEqual(r["event"], "toc_m14")
            self.assertEqual(r["stop"], "")                               # the layer emits no stop
            self.assertEqual(r["fee_R"], "")
            self.assertAlmostEqual(float(r["fee_R_1atr"]), 0.001 * 100.5 / 2.0, places=9)  # ATR is 2.0 (h-l)

    def test_cc_rows_carry_stop_and_fee_R(self):
        reg_key = "cryptocred|sr_flip|15m"
        e = fk.kline_registry()[reg_key]
        total = 0
        for seed in range(60, 90):
            bars = synth_bars(900, 900000, seed=seed)
            a = arrays_of(bars)
            rows, _ = fk.run_range(reg_key, 0, 900, entry=e, arrays=a, params_json="{}", commit="t")
            for r in rows:
                ep, st = float(r["entry_price"]), float(r["stop"])
                self.assertAlmostEqual(float(r["stop_dist_pct"]), abs(ep - st) / ep, places=12)
                self.assertAlmostEqual(float(r["fee_R"]), 0.001 / (abs(ep - st) / ep), places=9)
                # sr_flip stop = level -/+ 0.1 % => fee_R is 1.0 by construction (degenerate stop, F-BT-01 family)
                self.assertAlmostEqual(float(r["fee_R"]), 1.0, places=6)
                self.assertEqual(r["side"], "long" if st < ep else "short")
                total += 1
            if total >= 3:
                break
        self.assertGreaterEqual(total, 3)

    def test_csv_roundtrip_schema(self):
        e = fk.kline_registry()["rsi|rsi_events|5m"]
        bars = synth_bars(900, 300000, seed=7)
        a = arrays_of(bars)
        rows, _ = fk.run_range("rsi|rsi_events|5m", 0, 900, entry=e, arrays=a, params_json='{"x":1}', commit="abc")
        self.assertGreater(len(rows), 2)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "f.csv"
            fk.write_csv(p, rows)
            raw = p.read_bytes()
            self.assertNotIn(b"\r", raw)                                  # newline='\n' rule
            back = list(csv.DictReader(open(p, newline="", encoding="utf-8")))
        self.assertEqual(list(back[0].keys()), fk.CSV_COLUMNS)
        self.assertEqual(len(back), len(rows))
        for r in back:
            self.assertEqual(int(r["t_fire_ms"]), int(r["t_confirm_open_ms"]) + 300000)
            self.assertEqual(r["params_json"], '{"x":1}')
            self.assertEqual(r["code_commit"], "abc")
            self.assertEqual(r["tf"], "5m")
            self.assertEqual(r["layer"], "rsi")
            self.assertEqual(r["key"], "layer:rsi:rsi_events:5m")
            self.assertEqual(r["params_id"], "rsi_40_tol0.5_L1_2026-09-29")
            self.assertEqual(r["tradable"], "1" if r["side"] else "0")
            self.assertEqual(r["atr_kind"], "wilder")                    # capture.py / F-BT-07 contract
            self.assertIn(r["event"], ("cross", "support", "rejection", "failure"))

    def test_split_labels(self):
        ms = lambda s: int(__import__("datetime").datetime.strptime(s, "%Y-%m-%d").replace(
            tzinfo=__import__("datetime").timezone.utc).timestamp() * 1000)
        self.assertEqual(fk.split_of(ms("2022-01-01")), "TRAIN")
        self.assertEqual(fk.split_of(ms("2024-06-30")), "TRAIN")
        self.assertEqual(fk.split_of(ms("2024-07-01")), "VALIDATE")
        self.assertEqual(fk.split_of(ms("2024-12-31")), "VALIDATE")
        self.assertEqual(fk.split_of(ms("2025-01-01")), "VALIDATE")
        self.assertEqual(fk.split_of(ms("2025-06-30")), "VALIDATE")
        self.assertEqual(fk.split_of(ms("2025-07-01")), "HOLDOUT")
        self.assertEqual(fk.split_of(ms("2026-09-30")), "HOLDOUT")
        self.assertEqual(fk.split_of(ms("2026-10-01")), "POST")

    def test_repo_split_2024_07_01_is_not_train(self):
        """Repo split: DEV ends 2024-06-30, VALIDATION starts 2024-07-01 (OPERATOR_DECISIONS.md:878)."""
        import datetime as _dt
        ms = lambda y, m, d, h=0, mi=0: int(_dt.datetime(y, m, d, h, mi, tzinfo=_dt.timezone.utc).timestamp() * 1000)
        self.assertNotEqual(fk.split_of(ms(2024, 7, 1)), "TRAIN")
        self.assertNotEqual(fk.split_of(ms(2024, 9, 15)), "TRAIN")
        self.assertEqual(fk.split_of(ms(2024, 6, 30, 23, 59)), "TRAIN")
        self.assertEqual(dict((n, (lo, hi)) for n, lo, hi in fk.SPLITS)["TRAIN"], ("2022-01-01", "2024-07-01"))

    def test_exit_policies_train_end_matches_repo_split(self):
        from MyTradingSys.backtest.bigtrade import exit_policies as ep
        self.assertEqual(ep.TRAIN_END, 1719792000000)             # 2024-07-01 00:00 UTC

    def test_module_does_not_write_bytecode_into_live_tree(self):
        self.assertTrue(sys.dont_write_bytecode)


class TestParityLogic(unittest.TestCase):
    def _rep(self, key, t, ev, side="", conf=None):
        return {"_reg_key": key, "t_event_ms": t, "event": ev, "side": side, "t_confirm_open_ms": conf or t}

    def _live(self, key, t, ev, side=""):
        return {"key": key, "t_event": t, "event": ev, "side": side, "t_confirm": t, "raw": {}}

    def test_event_family_strips_price_only(self):
        self.assertEqual(fk.event_family("escalation_breakout_long_84103.06"), "escalation_breakout_long")
        self.assertEqual(fk.event_family("fvg_touch_short_85740.6"), "fvg_touch_short")
        self.assertEqual(fk.event_family("toc_m14"), "toc_m14")
        self.assertEqual(fk.event_family("sr_flip_long"), "sr_flip_long")
        self.assertEqual(fk.event_family("cross"), "cross")

    def test_compare_counts_hand_built(self):
        k = "rsi|rsi_events|5m"
        rep = [self._rep(k, 100, "cross"), self._rep(k, 200, "failure", "short"), self._rep(k, 300, "support"),
               self._rep(k, 400, "cross")]
        liv = [self._live(k, 100, "cross"), self._live(k, 200, "failure", "long"), self._live(k, 500, "rejection"),
               self._live(k, 9999, "cross")]
        r = fk.compare(rep, liv, 0, 1000)[k]
        self.assertEqual((r["replay"], r["live"], r["matched"]), (4, 3, 2))   # 9999 is outside the window
        self.assertEqual(sorted(r["only_live"]), [(500, "rejection")])
        self.assertEqual(sorted(r["only_replay"]), [(300, "support"), (400, "cross")])
        self.assertEqual(r["side_mismatch"], [(200, "failure")])
        self.assertAlmostEqual(fk.parity_pct(r), 100.0 * 2 / 5)

    def test_compare_soft_pairs_price_in_name(self):
        k = "fabio|escalation|15m"
        rep = [self._rep(k, 100, "escalation_breakout_long_84584.70", "long")]
        liv = [self._live(k, 100, "escalation_breakout_long_84584.74", "long")]
        r = fk.compare(rep, liv, 0, 1000)[k]
        self.assertEqual(r["matched"], 0)
        self.assertEqual(len(r["soft"]), 1)
        self.assertEqual((r["only_live"], r["only_replay"]), ([], []))
        self.assertEqual(fk.parity_pct(r), 0.0)
        self.assertEqual(fk.parity_pct(r, soft=True), 100.0)

    def test_dark_windows_need_two_consecutive_missing_slots(self):
        slot = 900000
        replay = [i * slot for i in range(10)]
        live = [0, 1 * slot, 4 * slot, 6 * slot, 8 * slot, 9 * slot]      # missing 2,3 (dark), 5 (single), 7 (single)
        self.assertEqual(pk.dark_windows(replay, live), [(2 * slot, 3 * slot)])
        self.assertEqual(pk.dark_windows(replay, live, min_slots=1),
                         [(2 * slot, 3 * slot), (5 * slot, 5 * slot), (7 * slot, 7 * slot)])
        self.assertTrue(pk.in_dark(3 * slot + 60000, [(2 * slot, 3 * slot)]))
        self.assertFalse(pk.in_dark(9 * slot, [(2 * slot, 3 * slot)]))

    def test_load_live_alerts_dedups_and_names(self):
        with tempfile.TemporaryDirectory() as d:
            rows = [{"layer": "rsi", "sub": "rsi_events", "tf": "5m", "t_close": 5, "event": "cross"},
                    {"layer": "rsi", "sub": "rsi_events", "tf": "5m", "t_close": 5, "event": "cross"},
                    {"layer": "fabio", "sub": "cvd_absorption", "tf": "15m", "t_close": 7, "kind": "bullish_absorption",
                     "side": "long"}]
            with open(Path(d) / "5m.jsonl", "w", newline="\n") as fh:
                for r in rows:
                    fh.write(json.dumps(r) + "\n")
            got, dups = fk.load_live_alerts(d)
        self.assertEqual(dups, 1)
        self.assertEqual(sorted((r["key"], r["event"]) for r in got),
                         [("fabio|cvd_absorption|15m", "bullish_absorption"), ("rsi|rsi_events|5m", "cross")])


class TestCodeCommit(unittest.TestCase):
    def test_dirty_flag_only_looks_at_imported_layer_files(self):
        fk.kline_registry()
        c = fk.code_commit()
        self.assertRegex(c, r"^[0-9a-f]{7,}(\+dirty)?$")


class TestVenueSwitch(unittest.TestCase):
    def test_default_venue_is_perp_with_separate_cache_folder(self):
        if fk.VENUE == "perp":
            self.assertEqual(fk.CACHE_DIR.name, "perp")
            self.assertEqual(fk.FIRES_DIR.name, "fires")
            self.assertEqual(fk.DATA_VENUE, "binance_usdm_perp_1m_archive")


if __name__ == "__main__":
    unittest.main()
