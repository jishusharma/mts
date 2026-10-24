"""Tests for the layers wired into the live runner (alerts/live_layers.py + build_default_registry).

Real fake-bar fixtures fire: session_momentum, funding_cvd_fade, malkan bull/bear, volume_fvg (swing_legs
stubbed, profile/VA/level real). Escalation and the three cryptocred setups need long hand-built
structure, so their underlying detector is stubbed with a canned event and only the adapter mapping
(t, event, side) is asserted; the detectors have their own tests.
"""
import random
import unittest
from unittest import mock

from MyTradingSys.backtest.layers.alerts import live_layers as ll
from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
from MyTradingSys.backtest.layers.alerts.live_runner_core import run_registry, empty_state, build_registry

H = 3600000
M15 = 900000
DAY = 86400000
T0 = (1790000000000 // DAY) * DAY  # UTC midnight


def walk(seed, n=99, t0=T0, step=H):
    r = random.Random(seed)
    p, out = 100.0, []
    for i in range(n):
        o = p
        c = o * (1 + r.gauss(0, 0.01))
        h = max(o, c) * (1 + abs(r.gauss(0, 0.004)))
        l = min(o, c) * (1 - abs(r.gauss(0, 0.004)))
        v = r.uniform(50, 150) * (1 + 3 * (r.random() < 0.05))
        out.append({"t": t0 + i * step, "o": o, "h": h, "l": l, "c": c, "v": v, "tbv": v * r.uniform(0.2, 0.8)})
        p = c
    return out


class TestSessionMomentum(unittest.TestCase):
    def _bars(self, first_close):
        return [
            {"t": T0, "o": 100.0, "h": 101, "l": 99, "c": 100.0, "v": 1, "tbv": 0.5},
            {"t": T0 + M15, "o": 100.0, "h": 101, "l": 99, "c": first_close, "v": 1, "tbv": 0.5},
            {"t": T0 + 2 * M15, "o": first_close, "h": 101, "l": 99, "c": 100, "v": 1, "tbv": 0.5},
        ]

    def test_long_and_short(self):
        ev = ll.session_momentum_layer(self._bars(101.0))
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]["side"], "long")
        self.assertEqual(ev[0]["t"], T0 + M15)  # entry bar (closes at +30 min)
        ev = ll.session_momentum_layer(self._bars(99.0))
        self.assertEqual(ev[0]["side"], "short")

    def test_too_few_bars(self):
        self.assertEqual(ll.session_momentum_layer(self._bars(101.0)[:1]), [])


class TestFundingFade(unittest.TestCase):
    def _bars(self, closes, deltas):
        return [{"t": T0 + i * H, "o": c, "h": c, "l": c, "c": c, "v": 10.0, "tbv": 5.0 + d / 2.0}
                for i, (c, d) in enumerate(zip(closes, deltas))]

    def _funding(self, last_high):
        # 100 rates, ascending times; the newest one is the extreme (pct 1.0) or the lowest (pct 0.0111)
        rates = [0.0001 + 0.000001 * (i % 7) for i in range(99)]
        rates.append(0.01 if last_high else -0.01)
        return [(T0 - H - (99 - i) * 8 * H, r) for i, r in enumerate(rates)]

    def _run(self, bars, last_high):
        fn = ll.make_funding_layer(lambda symbol, limit: self._funding(last_high))
        return fn(bars)

    def test_short_on_bearish_divergence_with_high_funding(self):
        n = 25
        closes = [10 + i for i in range(n)]  # new price highs...
        deltas = [5] * 21 + [-9, -9, -9, -9]  # ...while cvd falls
        bars = self._bars(closes, deltas)
        ev = self._run(bars, True)
        self.assertTrue(ev)
        self.assertTrue(all(e["side"] == "short" for e in ev))
        self.assertEqual(ev[0]["event"], "funding_fade_bearish")

    def test_long_on_bullish_divergence_with_low_funding(self):
        n = 25
        closes = [100 - i for i in range(n)]
        deltas = [-5] * 21 + [9, 9, 9, 9]
        ev = self._run(self._bars(closes, deltas), False)
        self.assertTrue(ev)
        self.assertTrue(all(e["side"] == "long" for e in ev))

    def test_too_few_bars(self):
        self.assertEqual(self._run(self._bars([1, 2], [1, 1]), True), [])


class TestMalkan(unittest.TestCase):
    def test_bull_long_and_bear_short(self):
        bull = ll.malkan_bull_layer(walk(3))
        bear = ll.malkan_bear_layer(walk(6))
        self.assertTrue(bull and all(e["side"] == "long" and "t" in e for e in bull))
        self.assertTrue(bear and all(e["side"] == "short" and "t" in e for e in bear))

    def test_too_few_bars(self):
        self.assertEqual(ll.malkan_bull_layer(walk(3, n=3)), [])
        self.assertEqual(ll.malkan_bear_layer(walk(6, n=3)), [])


class TestVolumeFvg(unittest.TestCase):
    def _bars(self):
        bars = []
        for i in range(60):
            c = 100.0 + (i % 5)
            bars.append({"t": T0 + i * H, "o": c, "h": c + 1, "l": c - 1, "c": c, "v": 10.0 + (i % 7), "tbv": 5.0})
        return bars

    def test_touch_fires_with_side(self):
        bars = self._bars()
        leg = {"a_i": 0, "b_i": 30, "a_price": 100, "b_price": 104, "confirmed_i": 31}
        with mock.patch.object(ll, "swing_legs", return_value=[leg]):
            ev = ll.volume_fvg_layer(bars)
        self.assertEqual(len(ev), 1)
        self.assertIn(ev[0]["side"], ("long", "short"))
        self.assertEqual(ev[0]["event"], "fvg_touch_%s_%s" % (ev[0]["side"], ev[0]["level"]))
        mid = ev[0]["level"]
        expected = "long" if bars[31]["c"] > mid else "short"   # run_backtest.py:199,202 'bounce'
        self.assertEqual(ev[0]["side"], expected)

    def _flat_close_bars(self, close, n=40):
        return [{"t": T0 + i * H, "o": 10.0, "h": 11.0, "l": 9.0, "c": close, "v": 1.0, "tbv": 0.5}
                for i in range(n)]

    def _fvg_events(self, bars, confirmed_i=20):
        leg = {"a_i": 0, "b_i": 20, "confirmed_i": confirmed_i}
        with mock.patch.object(ll, "swing_legs", return_value=[leg]),                 mock.patch.object(ll, "build_profile", return_value=object()),                 mock.patch.object(ll, "value_area", return_value=object()),                 mock.patch.object(ll, "lowest_volume_level", return_value={"price_lo": 9.9, "price_hi": 10.1}):
            return ll.volume_fvg_layer(bars)

    def test_volume_fvg_side_matches_backtest(self):
        """close at confirmation above the level (mid 10.0) -> long; below -> short (run_fvg bounce)."""
        up = self._fvg_events(self._flat_close_bars(10.5))
        dn = self._fvg_events(self._flat_close_bars(9.5))
        self.assertEqual([e["side"] for e in up], ["long"])
        self.assertEqual([e["side"] for e in dn], ["short"])

    def test_volume_fvg_scan_starts_after_confirmation(self):
        """run_fvg scans range(start+1, ...): a touch on the confirmation bar itself is not an event (F7)."""
        bars = self._flat_close_bars(10.5)
        for i, b in enumerate(bars):
            if i != 20:
                b["l"], b["h"] = 12.0, 13.0      # never touches mid 10.0 except on bar 20
        self.assertEqual(self._fvg_events(bars), [])
        bars[21]["l"], bars[21]["h"] = 9.0, 11.0
        ev = self._fvg_events(bars)
        self.assertEqual([e["t"] for e in ev], [bars[21]["t"]])

    def test_volume_fvg_restart_same_bars_same_events(self):
        bars = self._bars()
        leg = {"a_i": 0, "b_i": 30, "a_price": 100, "b_price": 104, "confirmed_i": 31}
        with mock.patch.object(ll, "swing_legs", return_value=[leg]):
            first = ll.volume_fvg_layer(bars)
            second = ll.volume_fvg_layer(bars)
        self.assertEqual(first, second)

    def test_volume_fvg_degenerate_inputs_return_empty(self):
        self.assertEqual(ll.volume_fvg_layer([]), [])
        self.assertEqual(ll.volume_fvg_layer(self._flat_close_bars(10.0, n=3)), [])
        self.assertEqual(ll.volume_fvg_layer(self._flat_close_bars(10.0, n=39)), [])   # < 2*n_bins=40
        self.assertEqual(ll.volume_fvg_layer(self._flat_close_bars(10.0, n=60)), [])   # flat: no legs / no profile

    def test_too_few_bars(self):
        self.assertEqual(ll.volume_fvg_layer(self._bars()[:3]), [])


class TestStubbedDetectors(unittest.TestCase):
    def test_escalation_adapter(self):
        bars = walk(1, n=10)
        raw = [{"t": 0, "i": 6, "level_i": 2, "level_price": 100.0, "side": "short",
                "kind": "escalation_breakout"}]
        with mock.patch.object(ll, "escalation_events", return_value=raw):
            ev = ll.escalation_layer(bars)
        self.assertEqual(ev[0]["t"], bars[6]["t"])
        self.assertEqual(ev[0]["side"], "short")
        self.assertTrue(ev[0]["event"].startswith("escalation_breakout_short"))

    def test_escalation_too_few_bars(self):
        self.assertEqual(ll.escalation_layer(walk(1, n=3)), [])

    def test_cc_adapters(self):
        bars = walk(1, n=10)
        sig = [{"side": "long", "entry_price": 100.0, "entry_t": bars[5]["t"], "stop": 99.0,
                "targets": [(101.0, 1.0)], "meta": {}}]
        for name, fn_name in (("sr_flip", "setup1_sr_flip"), ("fib_pullback", "setup2_fib_pullback"),
                              ("failed_msb", "setup3_failed_msb_reversal")):
            fn = ll._cc_layer(lambda b, _s=sig: _s, name)
            ev = fn(bars)
            self.assertEqual(ev[0]["side"], "long")
            self.assertEqual(ev[0]["t"], bars[5]["t"])
            self.assertEqual(ev[0]["event"], name + "_long")

    def test_cc_too_few_bars_and_real_error_propagates(self):
        for fn in (ll.cc_sr_flip_layer, ll.cc_fib_pullback_layer, ll.cc_failed_msb_layer):
            self.assertEqual(fn(walk(1, n=2)), [])

        def boom(bars):
            raise ValueError("something else")
        with self.assertRaises(ValueError):
            ll._cc_layer(boom, "x")(walk(1, n=2))


class TestRegistry(unittest.TestCase):
    NEW_KEYS = {
        "fabio|escalation|1h", "fabio|volume_fvg|1h", "session|session_momentum|15m",
        "positioning|funding_cvd_fade|1h", "rsi|malkan_bull|1h", "rsi|malkan_bear|1h",
        "cryptocred|sr_flip|1h", "cryptocred|fib_pullback|1h", "cryptocred|failed_msb|1h",
    }

    def test_keys_and_tfs(self):
        reg = cli.build_default_registry(fetch_funding=lambda s, n: [])
        self.assertTrue(self.NEW_KEYS <= set(reg))
        self.assertTrue({e["tf"] for e in reg.values()} <= {"1h", "15m", "5m", "1m"})

    def test_registry_entries_fire_with_side_through_run_registry(self):
        funding = TestFundingFade()
        n = 25
        fbars = funding._bars([10 + i for i in range(n)], [5] * 21 + [-9] * 4)
        reg = cli.build_default_registry(fetch_funding=lambda s, k: funding._funding(True))
        sm = TestSessionMomentum()._bars(101.0)
        res = run_registry(reg, {"1h": fbars, "15m": sm}, empty_state())
        # the pre-existing rsi_events entry raises on 3 bars (15m here); only the new layers must be clean
        self.assertEqual([e for e in res["errors"] if not e["key"].startswith("rsi|rsi_events")], [])
        by = {}
        for a in res["alerts"]:
            by.setdefault((a["layer"], a["sub"]), []).append(a)
        for k in (("positioning", "funding_cvd_fade"), ("session", "session_momentum")):
            self.assertIn(k, by)
            self.assertTrue(all(a["side"] in ("long", "short") and "t_close" in a for a in by[k]))
        self.assertEqual(by[("session", "session_momentum")][0]["side"], "long")
        self.assertEqual(by[("positioning", "funding_cvd_fade")][0]["side"], "short")

    def test_failing_layer_does_not_stop_others(self):
        def boom(bars):
            raise RuntimeError("layer down")
        reg = build_registry([
            {"layer": "bad", "sub": "b", "tf": "1h", "fn": boom, "params_id": "p"},
            {"layer": "ok", "sub": "o", "tf": "1h",
             "fn": lambda bars: [{"t": bars[-1]["t"], "event": "e", "side": "long"}], "params_id": "p"},
        ])
        res = run_registry(reg, {"1h": walk(1, n=5)}, empty_state())
        self.assertEqual(len(res["errors"]), 1)
        self.assertEqual(res["errors"][0]["key"], "bad|b|1h")
        self.assertEqual(res["alerts"][0]["side"], "long")

    def test_too_few_bars_whole_registry_no_events_no_errors(self):
        reg = cli.build_default_registry(fetch_funding=lambda s, n: [])
        res = run_registry(reg, {"1h": walk(1, n=3), "15m": walk(1, n=3, step=M15)}, empty_state())
        self.assertEqual([e for e in res["errors"] if not e["key"].startswith("rsi|rsi_events")], [])
        self.assertTrue(all("side" in a for a in res["alerts"] if a["layer"] != "rsi"))


if __name__ == "__main__":
    unittest.main()
