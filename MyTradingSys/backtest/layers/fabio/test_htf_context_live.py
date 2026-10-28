"""Tests for htf_context_live.py (R4 HTF context writer). Stub feeds, temp dirs, no network.
Expected numbers are hand arithmetic from the stub feed (every normal bar o=c=84525, h=84529, l=84521; spikes below),
balance rule from signals.py:183 (R <= 0.8*sqrt(N)*ATR, |c-poc| <= 0.25*R, 50 USD profile bins) - none computed by the
code under test."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from MyTradingSys.backtest.layers.fabio import htf_context_live as hc

H4 = 4 * 3600 * 1000
MIN = 60000
B = int(datetime(2026, 10, 3, 8, 0, tzinfo=timezone.utc).timestamp() * 1000)   # a 4H close boundary
NORMAL = (84525.0, 84529.0, 84521.0, 84525.0)                                   # o, h, l, c


def feed(overrides=None, first_t=None):
    """fetch_klines stub: 1m rows for any [start, end]; overrides = {open_t_ms: (o, h, l, c)}."""
    ov = overrides or {}

    def fetch(start_ms, end_ms):
        rows = []
        t = (start_ms // MIN) * MIN
        if t < start_ms:
            t += MIN
        while t <= end_ms:
            if first_t is None or t >= first_t:
                o, h, l, c = ov.get(t, NORMAL)
                rows.append([t, str(o), str(h), str(l), str(c), "10", t + MIN - 1, "0", 1, "6", "0", "0"])
            t += MIN
        return rows
    return fetch


def spikes(bnd):
    """High spike 84560 at bnd-6h, low spike 84490 at bnd-7h: both inside the previous 4H window and the 1D window."""
    return {bnd - 6 * 3600000: (84525.0, 84560.0, 84521.0, 84525.0),
            bnd - 7 * 3600000: (84525.0, 84529.0, 84490.0, 84525.0)}


def oi_ok(pct):
    return lambda end_ms: pct


def oi_boom(end_ms):
    raise OSError("boom")


class RowTests(unittest.TestCase):
    def run_once(self, now, fetch, oi=None, out=None):
        d = out or tempfile.mkdtemp()
        res = hc.run_once(now, fetch, oi or oi_ok(0.5), d)
        return res, Path(d)

    def test_row_shape_and_values(self):
        ov = spikes(B)
        # the spike bars sit in [B-8h, B-4h): put copies inside the current window too so 4H and 1D both see H/L
        ov[B - 3 * 3600000] = (84525.0, 84560.0, 84521.0, 84525.0)
        ov[B - 2 * 3600000] = (84525.0, 84529.0, 84490.0, 84525.0)
        res, d = self.run_once(B + 5 * MIN, feed(ov))
        rows = [json.loads(x) for x in (d / "2026-10-03.jsonl").read_text().splitlines()]
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(set(r), {"timestamp", "bal_4h", "bal_1d", "failed_breakout", "oi_delta_1h_pct"})
        self.assertEqual(r["timestamp"], "2026-10-03T08:00:00Z")
        want = {"H": 84560.0, "L": 84490.0, "R": 70.0, "poc": 84525.0}
        self.assertEqual(r["bal_4h"], want)
        self.assertEqual(r["bal_1d"], want)
        self.assertIs(r["failed_breakout"], False)
        self.assertEqual(r["oi_delta_1h_pct"], 0.5)

    def test_boundary_uses_last_closed_4h(self):
        for now, closed in ((B + 4 * 3600000 - 1, "2026-10-03T08:00:00Z"), (B + 4 * 3600000, "2026-10-03T12:00:00Z"),
                            (B - 1, "2026-10-03T04:00:00Z"), (B, "2026-10-03T08:00:00Z")):
            res, d = self.run_once(now, feed())
            f = next(d.glob("*.jsonl"))
            self.assertEqual(json.loads(f.read_text().splitlines()[0])["timestamp"], closed, now)

    def test_no_future_bars_read(self):
        asked = []
        base = feed()

        def spy(s, e):
            asked.append(e)
            return base(s, e)
        self.run_once(B + 90 * MIN, spy)
        self.assertTrue(asked and max(asked) <= B - 1)       # nothing at or after the 4H close

    def test_failed_breakout_true_on_reclaim(self):
        ov = spikes(B)                                        # previous 4H balance: H 84560, L 84490
        for k in (3, 2):                                      # two closes above H inside the current window
            ov[B - k * 3600000] = (84525.0, 84575.0, 84521.0, 84570.0)
        # last bar of the window is normal (close 84525, back inside [L, H]) -> reclaim
        res, d = self.run_once(B + MIN, feed(ov))
        self.assertIs(json.loads((d / "2026-10-03.jsonl").read_text())["failed_breakout"], True)

    def test_failed_breakout_false_when_breakout_holds(self):
        ov = spikes(B)
        for k in (3, 2):
            ov[B - k * 3600000] = (84525.0, 84575.0, 84521.0, 84570.0)
        ov[B - MIN] = (84570.0, 84575.0, 84565.0, 84570.0)    # final close stays above H -> held, not failed
        res, d = self.run_once(B + MIN, feed(ov))
        self.assertIs(json.loads((d / "2026-10-03.jsonl").read_text())["failed_breakout"], False)

    def test_failed_breakout_false_without_probe(self):
        res, d = self.run_once(B + MIN, feed(spikes(B)))
        self.assertIs(json.loads((d / "2026-10-03.jsonl").read_text())["failed_breakout"], False)

    def test_oi_error_fails_closed_no_row(self):
        res, d = self.run_once(B + MIN, feed(spikes(B)), oi=oi_boom)
        self.assertIsNone(res)
        self.assertEqual(list(d.iterdir()), [])               # no row, no summary

    def test_first_day_no_prior_data(self):
        # exchange history starts 100 minutes before the close: no balance is computable, flag is unknown (null)
        res, d = self.run_once(B + MIN, feed(first_t=B - 100 * MIN))
        r = json.loads((d / "2026-10-03.jsonl").read_text())
        self.assertIsNone(r["bal_4h"])
        self.assertIsNone(r["bal_1d"])
        self.assertIsNone(r["failed_breakout"])
        self.assertEqual(r["oi_delta_1h_pct"], 0.5)

    def test_failed_breakout_null_when_previous_window_not_balanced(self):
        # a 179-point bar in the previous 4H window (R > 0.8*sqrt(240)*ATR ~ 108) leaves no balance to probe: unknown, not False
        ov = {B - 7 * 3600000: (84525.0, 84700.0, 84521.0, 84525.0)}
        for k in (3, 2):                                      # closes beyond any edge would be a probe if a balance existed
            ov[B - k * 3600000] = (84525.0, 84575.0, 84521.0, 84570.0)
        res, d = self.run_once(B + MIN, feed(ov))
        r = json.loads((d / "2026-10-03.jsonl").read_text())
        self.assertIsNotNone(r["bal_4h"])                     # the current window is still balanced
        self.assertIsNone(r["failed_breakout"])

    def test_failed_breakout_function_none_vs_false(self):
        bars = [{"c": 84525.0}] * hc.N_4H
        self.assertIsNone(hc.failed_breakout(bars, hc.N_4H - 1, None))
        self.assertIs(hc.failed_breakout(bars, hc.N_4H - 1, {"H": 84560.0, "L": 84490.0}), False)

    def test_no_bars_at_all_no_row(self):
        res, d = self.run_once(B + MIN, lambda s, e: [])
        self.assertIsNone(res)
        self.assertEqual(list(d.iterdir()), [])

    def test_idempotent_per_close(self):
        d = tempfile.mkdtemp()
        hc.run_once(B + MIN, feed(), oi_ok(0.5), d)
        hc.run_once(B + 2 * MIN, feed(), oi_ok(0.7), d)
        self.assertEqual(len((Path(d) / "2026-10-03.jsonl").read_text().splitlines()), 1)
        hc.run_once(B + H4 + MIN, feed(), oi_ok(0.7), d)
        self.assertEqual(len((Path(d) / "2026-10-03.jsonl").read_text().splitlines()), 2)

    def test_daily_summary(self):
        res, d = self.run_once(B + MIN, feed(spikes(B)))
        s = json.loads((d / "2026-10-03_summary.json").read_text())
        self.assertEqual(s, {"date": "2026-10-03", "open": 84525.0, "close": 84525.0, "high": 84560.0, "low": 84490.0})

    def test_midnight_close_belongs_to_the_day_just_ended(self):
        mid = int(datetime(2026, 10, 4, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
        res, d = self.run_once(mid + MIN, feed())
        self.assertTrue((d / "2026-10-03.jsonl").exists())
        self.assertFalse((d / "2026-10-04.jsonl").exists())


class OiParseTests(unittest.TestCase):
    def test_delta_pct(self):
        rows = [{"sumOpenInterest": "100.0", "timestamp": 1}, {"sumOpenInterest": "101.0", "timestamp": 2}]
        self.assertAlmostEqual(hc.oi_delta_pct(rows), 1.0)
        rows = [{"sumOpenInterest": "200", "timestamp": 1}, {"sumOpenInterest": "190", "timestamp": 2}]
        self.assertAlmostEqual(hc.oi_delta_pct(rows), -5.0)

    def test_needs_two_rows(self):
        with self.assertRaises(ValueError):
            hc.oi_delta_pct([{"sumOpenInterest": "100", "timestamp": 1}])
        with self.assertRaises(ValueError):
            hc.oi_delta_pct([])

    def test_zero_base_rejected(self):
        with self.assertRaises(ValueError):
            hc.oi_delta_pct([{"sumOpenInterest": "0", "timestamp": 1}, {"sumOpenInterest": "5", "timestamp": 2}])


class RowWrittenRetryTest(unittest.TestCase):
    """2026-10-15: one OI hiccup left the 20:00Z row missing for 4 h (loop slept to the next close). The loop now asks
    row_written() and retries after RETRY_MS."""

    def test_row_written_false_until_row_exists_then_true(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(hc.row_written(B + 5 * MIN, d))
            row = hc.run_once(B + 5 * MIN, feed(), lambda end: 1.5, d)
            self.assertIsNotNone(row)
            self.assertTrue(hc.row_written(B + 5 * MIN, d))
            self.assertFalse(hc.row_written(B + H4 + 5 * MIN, d))

    def test_retry_is_two_minutes(self):
        self.assertEqual(hc.RETRY_MS, 120000)


if __name__ == "__main__":
    unittest.main()
