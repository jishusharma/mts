"""T02-F3 part b: event-forcing look-ahead (causality) fixtures for wlow_bounce and session_levels.

Why:
  wlow_bounce|bbrsi60|1h and session_levels|session_levels|1m produced 0 events on synthetic random
  bars during the T02 truncation audit (MyTradingSys/research/dsa_backtest_audit_2026-10-16/T02_lookahead_time.md,
  table 3a). This file hand-builds:
    1. A 1h bar series across two ISO weeks forcing a weekly-low break and hold bounce trigger (wlow_bounce).
    2. A 1m bar series across two UTC days forcing a prior-day high failed break event (session_levels).
  Both fixtures are verified under the shared causality harness (assert_causal from test_lookahead_forcing.py),
  confirming 0 lookahead differences and verifying planted peek detection.
"""
import datetime as dt
import unittest

from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
from MyTradingSys.backtest.layers.alerts.live_session_levels import session_levels_layer
from MyTradingSys.backtest.layers.alerts.test_lookahead_forcing import (
    assert_causal,
    causal_report,
    fwd_peek_next_bar_layer,
)
from MyTradingSys.backtest.layers.session_levels.session_levels import DAY_MS, MIN_MS


# --------------------------------------------------------------------------- wlow_bounce|bbrsi60|1h

class TestWlowBounceCausal(unittest.TestCase):
    H = 3600000

    @classmethod
    def setUpClass(cls):
        cls.BARS = cls._build_bars()

    @classmethod
    def _build_bars(cls):
        # Start Monday 2024-01-01 00:00 UTC
        t0 = int(dt.datetime(2024, 1, 1, 0, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)
        flat_c = 95.80
        dip_c = 94.50
        bounce_step = 0.050

        bars = []
        # Week 0: 168 bars. Flat at 95.80; bar 50 low = 95.0 establishes prior ISO weekly low W = 95.0
        for i in range(168):
            t = t0 + i * cls.H
            l = 95.0 if i == 50 else flat_c
            bars.append({"t": t, "o": flat_c, "h": flat_c + 0.1, "l": l, "c": flat_c, "v": 10.0, "tbv": 5.0})

        # Week 1: bars 168..190
        for i in range(168, 190):
            t = t0 + i * cls.H
            bars.append({"t": t, "o": flat_c, "h": flat_c + 0.1, "l": flat_c, "c": flat_c, "v": 10.0, "tbv": 5.0})

        # Bar 170 dips below prior weekly low 95.0
        bars[170]["l"] = 94.0
        bars[170]["c"] = dip_c

        # Bar 171 bounces back above 95.0
        bars[171]["c"] = 95.9
        bars[171]["h"] = 96.0
        bars[171]["l"] = 95.2

        # Bars 172..189 rise steadily by bounce_step satisfying hold_ok on bar 175
        for k in range(172, 190):
            bars[k]["c"] = bars[k - 1]["c"] + bounce_step
            bars[k]["h"] = bars[k]["c"] + 0.1
            bars[k]["l"] = bars[k]["c"] - 0.1

        return bars

    @staticmethod
    def _make_scanner():
        box = {"bars": None}
        layer = cli.make_wlow_bounce_layer(
            fetch_candles=lambda: box["bars"],
            fetch_oi=lambda K: (None, None),
            log_path=None,
        )

        def scanner(b):
            events = []
            for j in range(168, len(b)):
                box["bars"] = b[:j + 1]
                try:
                    evs = layer(b[:j + 1])
                    if evs:
                        events.extend(evs)
                except Exception:
                    pass
            return events

        return scanner

    def test_fixture_forces_the_expected_event(self):
        scanner = self._make_scanner()
        evs = scanner(self.BARS)
        self.assertEqual(len(evs), 1, evs)
        ev = evs[0]
        self.assertEqual(ev["t"], self.BARS[175]["t"])
        self.assertEqual(ev["event"], "wlow_bounce_bbrsi60_active")
        self.assertEqual(ev["prior_weekly_low"], 95.0)
        self.assertEqual(ev.get("side"), "long")

    def test_no_look_ahead_with_events(self):
        scanner = self._make_scanner()
        rep = assert_causal(scanner, self.BARS, range(170, 185))
        self.assertEqual(rep["events_full"], 1)
        self.assertGreaterEqual(rep["compared"], 1)
        self.assertEqual([rep[k] for k in ("late", "repaint", "nan", "x10")], [[], [], [], []])

    def test_planted_peek_is_detected(self):
        # 1. Harness next-bar peek
        with self.assertRaises(AssertionError):
            assert_causal(fwd_peek_next_bar_layer, self.BARS, range(170, 185))

        # 2. Leaky scanner requiring future bar
        box = {"bars": None}
        layer = cli.make_wlow_bounce_layer(
            fetch_candles=lambda: box["bars"],
            fetch_oi=lambda K: (None, None),
            log_path=None,
        )

        def leaky_wlow(b):
            events = []
            for j in range(168, len(b)):
                if j + 1 < len(b):  # peek: requires future bar to be present
                    box["bars"] = b[:j + 1]
                    try:
                        evs = layer(b[:j + 1])
                        if evs:
                            events.extend(evs)
                    except Exception:
                        pass
            return events

        rep = causal_report(leaky_wlow, self.BARS, range(170, 185))
        self.assertTrue(rep["late"])
        with self.assertRaises(AssertionError):
            assert_causal(leaky_wlow, self.BARS, range(170, 185))

        # 3. Vacuous check fails on zero events
        with self.assertRaises(AssertionError):
            assert_causal(lambda b: [], self.BARS, range(170, 185))


# --------------------------------------------------------------------------- session_levels|session_levels|1m

class TestSessionLevelsCausal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.BARS = cls._build_bars()

    @classmethod
    def _build_bars(cls):
        d0 = 20000
        t_start = d0 * DAY_MS
        bars = []

        # Day 0: 1440 1m bars. High 100.0, low 90.0, close 95.0 -> establishes PDH = 100.0, PDL = 90.0
        for m in range(1440):
            bars.append({
                "t": t_start + m * MIN_MS,
                "o": 95.0,
                "h": 100.0,
                "l": 90.0,
                "c": 95.0,
                "v": 10.0,
                "tbv": 5.0,
            })

        # Day 1: 200 1m bars
        t_day1 = (d0 + 1) * DAY_MS
        for m in range(200):
            t = t_day1 + m * MIN_MS
            if m == 100:
                # Poke above PDH (100.0) in Asia session
                o, h, l, c = 95.0, 105.0, 95.0, 102.0
            elif m == 101:
                # Fail back below PDH within fail window
                o, h, l, c = 101.0, 101.0, 98.0, 99.0
            else:
                o, h, l, c = 95.0, 96.0, 94.0, 95.0
            bars.append({"t": t, "o": o, "h": h, "l": l, "c": c, "v": 10.0, "tbv": 5.0})

        return bars

    def test_fixture_forces_the_expected_event(self):
        evs = session_levels_layer(self.BARS)
        self.assertEqual(len(evs), 1, evs)
        ev = evs[0]
        expected_t = self.BARS[1440 + 101]["t"]
        self.assertEqual(ev["t"], expected_t)
        self.assertEqual(ev["event"], "sess_pdh_failed_break")
        self.assertEqual(ev["side"], "short")
        self.assertEqual(ev["level"], 100.0)

    def test_no_look_ahead_with_events(self):
        # 20 cuts spanning before, on, and after the event bar (index 1541)
        cuts = range(1440 + 95, 1440 + 115)
        rep = assert_causal(session_levels_layer, self.BARS, cuts)
        self.assertEqual(rep["events_full"], 1)
        self.assertGreaterEqual(rep["compared"], 1)
        self.assertEqual([rep[k] for k in ("late", "repaint", "nan", "x10")], [[], [], [], []])

    def test_planted_peek_is_detected(self):
        cuts = range(1440 + 95, 1440 + 115)

        # 1. Harness next-bar peek
        with self.assertRaises(AssertionError):
            assert_causal(fwd_peek_next_bar_layer, self.BARS, cuts)

        # 2. Leaky session_levels requiring next bar to exist before emitting
        def leaky_sl(b):
            evs = session_levels_layer(b)
            ts = [x["t"] for x in b]
            return [e for e in evs if ts.index(e["t"]) + 1 < len(b)]

        rep = causal_report(leaky_sl, self.BARS, cuts)
        self.assertTrue(rep["late"])
        with self.assertRaises(AssertionError):
            assert_causal(leaky_sl, self.BARS, cuts)

        # 3. Vacuous check fails on zero events
        with self.assertRaises(AssertionError):
            assert_causal(lambda b: [], self.BARS, cuts)


if __name__ == "__main__":
    unittest.main()
