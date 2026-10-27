"""T02-F3 part c: event-forcing look-ahead (causality) fixture for fabio v3_grid.

Why:
  fabio|v3_grid|1m produced 0 events on random synthetic bars during the T02 truncation audit
  (MyTradingSys/research/dsa_backtest_audit_2026-10-16/T02_lookahead_time.md, table 3a).
  This file hand-builds a 1m order-flow fixture with footprint, delta, and 99th-percentile volume
  fields across the NY open window that forces a real Model C breakout SIGNAL, and tests it
  under the four-way truncation harness (assert_causal from test_lookahead_forcing.py).

Method:
  35 1m bars starting at NY cash open (2024-01-08 14:30 UTC):
  - Bars 0..29: flat Initial Balance (IB) range at 100.0 (high 100.1, low 99.9).
  - Bar 30+: breakout to 100.5 with high buy volume and b99_buy_vol = 10.0.
  - Model C detects IB breakout confirmation and triggers SIGNAL.
  - The live runner evaluates each minute as a discrete window; a scanning layer runs
    make_fabio_v3_layer across all valid prefixes.
  - Full vs cut vs NaN-tail vs x10-tail comparisons prove 0 look-ahead differences.
  - Harness self-tests verify that planted peeks (fwd_peek_next_bar_layer and leaky prefix)
    fail assert_causal cleanly.
"""
import datetime as dt
import unittest

from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
from MyTradingSys.backtest.layers.alerts.test_lookahead_forcing import (
    assert_causal,
    causal_report,
    fwd_peek_next_bar_layer,
)
from MyTradingSys.backtest.layers.fabio.v3.day_gates import ny_open_utc


def _make_scanner(layer_fn, min_bars=30):
    """Wrap a window-evaluating layer into a sequential bar-by-bar emitter."""
    def _scan(bars):
        events = []
        for j in range(min_bars, len(bars)):
            try:
                evs = layer_fn(bars[:j + 1])
                if evs:
                    events.extend(evs)
            except Exception:
                pass
        return events
    return _scan


class TestLookaheadForcingFabioV3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 2024-01-08 is a Monday; NY open is 14:30 UTC = 09:30 EST
        d = dt.date(2024, 1, 8)
        cls.T0 = int(ny_open_utc(d).timestamp() * 1000)
        cls.BARS = cls._build_bars()

    @classmethod
    def _build_bars(cls, n_bars=35):
        bars = []
        for i in range(n_bars):
            t = cls.T0 + i * 60000
            if i < 30:
                c, h, l, o, b99 = 100.0, 100.1, 99.9, 100.0, 0.0
            else:
                c, h, l, o, b99 = 100.5, 100.6, 100.2, 100.3, 10.0
            bars.append({
                "t": t,
                "o": o,
                "h": h,
                "l": l,
                "c": c,
                "v": 100.0,
                "tbv": 50.0,
                "buy_vol": 50.0,
                "sell_vol": 50.0,
                "b99_buy_vol": b99,
                "b99_sell_vol": 0.0,
                "thr_days": 10,
                "fp": [{"p": c, "buy": 50.0, "sell": 50.0}],
            })
        return bars

    def test_fixture_forces_expected_events(self):
        """Fixture produces Model C long breakout signals on bar 30."""
        layer = cli.make_fabio_v3_layer()
        scanner = _make_scanner(layer)
        events = scanner(self.BARS)
        self.assertGreater(len(events), 0)
        target_t = self.BARS[30]["t"]
        for ev in events:
            self.assertEqual(ev["t"], target_t)
            self.assertEqual(ev["model"], "C")
            self.assertEqual(ev.get("side") or ev.get("shadow_side"), "long")

    def test_single_cell_fixture_forces_one_event(self):
        """A single-cell grid produces exactly 1 event and passes assert_causal."""
        single_grid = {"N": (60,), "p": (0.05,), "z_hi": (2.0,), "m_c": (5,), "f": (0.003,)}
        layer = cli.make_fabio_v3_layer(grid=single_grid)
        scanner = _make_scanner(layer)
        events = scanner(self.BARS)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["t"], self.BARS[30]["t"])

        rep = assert_causal(scanner, self.BARS, range(20, len(self.BARS)), min_events=1)
        self.assertEqual(rep["events_full"], 1)
        self.assertGreaterEqual(rep["compared"], 1)
        self.assertEqual([rep[k] for k in ("late", "repaint", "nan", "x10")], [[], [], [], []])

    def test_assert_causal_passes_full_grid(self):
        """Full default grid (72 cells) passes causal comparison across cuts with 0 differences."""
        layer = cli.make_fabio_v3_layer()
        scanner = _make_scanner(layer)
        rep = assert_causal(scanner, self.BARS, range(20, len(self.BARS)))
        self.assertGreater(rep["events_full"], 0)
        self.assertGreater(rep["compared"], 0)
        self.assertEqual([rep[k] for k in ("late", "repaint", "nan", "x10")], [[], [], [], []])

    def test_planted_peek_is_detected(self):
        """Look-ahead detection verifies that synthetic future peeks trigger AssertionError."""
        # 1. Harness next-bar peek
        with self.assertRaises(AssertionError):
            assert_causal(fwd_peek_next_bar_layer, self.BARS, range(20, len(self.BARS)))

        # 2. Leaky fabio layer requiring next bar to exist before emitting
        base_layer = cli.make_fabio_v3_layer()

        def leaky_fabio(b):
            evs = []
            for j in range(30, len(b)):
                if j + 1 < len(b):  # peek: requires future bar to be present
                    try:
                        res = base_layer(b[:j + 1])
                        if res:
                            evs.extend(res)
                    except Exception:
                        pass
            return evs

        rep = causal_report(leaky_fabio, self.BARS, range(20, len(self.BARS)))
        self.assertTrue(rep["late"])
        with self.assertRaises(AssertionError):
            assert_causal(leaky_fabio, self.BARS, range(20, len(self.BARS)))

        # 3. Vacuous check fails on zero events
        with self.assertRaises(AssertionError):
            assert_causal(lambda b: [], self.BARS, range(20, len(self.BARS)))


if __name__ == "__main__":
    unittest.main()
