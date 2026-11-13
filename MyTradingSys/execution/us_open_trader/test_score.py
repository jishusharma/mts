"""test_score.py - score.py with injected fetch/bars; never touches the network."""
import calendar
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import score  # noqa: E402

ARM = calendar.timegm((2026, 11, 13, 13, 35, 0)) * 1000
FLAT = calendar.timegm((2026, 11, 13, 16, 30, 0)) * 1000
MIN = 60000
PLAN = {
    "day": "2026-11-13", "frozen_utc": "2026-11-13T13:10Z", "ref_feed": "binance_spot_BTCUSDT",
    "instrument": "BTC-PERPETUAL", "arm_utc": "13:35", "flat_utc": "16:30", "max_entries": 3,
    "amount_usd": 5000, "leverage": 50, "be_at_r": 1.0, "fee_per_side": 0.0005,
    "orders": [
        {"id": "A", "side": "buy", "kind": "breakout", "trigger": 69620, "stop_dist": 250, "target_dist": 360,
         "level": "Europe high", "confluence": ["live_aid:EU_HIGH"], "arm_after": None},
        {"id": "B", "side": "sell", "kind": "breakout", "trigger": 68490, "stop_dist": 250, "target_dist": 370,
         "level": "Europe low", "confluence": ["live_aid:EU_LOW"], "arm_after": None},
    ],
}


def kl(t, o, h, l, c):  # binance kline row: strings, extra fields ignored
    return [t, str(o), str(h), str(l), str(c), "1.0", t + 59999, "0", 1, "0", "0", "0"]


# A enters bar1 (69620), target 69980 hit bar2 -> r_gross 1.44, r_net 1.44 - 0.27848 = 1.16152
ROWS = [kl(ARM, 69000, 69100, 68900, 69000), kl(ARM + MIN, 69500, 69625, 69450, 69600),
        kl(ARM + 2 * MIN, 69800, 69985, 69800, 69900), kl(FLAT, 69900, 69950, 69800, 69900)]


def run_score(plan_path, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = score.score(plan_path, **kw)
    return r, buf.getvalue()


class TestScore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.plan_path = self.dir / "plan.json"
        self.plan_path.write_text(json.dumps(PLAN))
        self.urls = []

    def fetch_ok(self, url):
        self.urls.append(url)
        return ROWS

    def test_score_with_injected_fetch_writes_jsonl_and_prints_table(self):
        r, out = run_score(self.plan_path, out_dir=self.dir / "out", fetch=self.fetch_ok)
        self.assertEqual(len(self.urls), 1)
        self.assertTrue(self.urls[0].startswith("https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m"))
        self.assertIn("startTime=%d" % ARM, self.urls[0])
        self.assertIn("endTime=%d" % (FLAT + MIN), self.urls[0])
        rows = [json.loads(l) for l in Path(r["path"]).read_text().splitlines()]
        self.assertEqual(Path(r["path"]).name, "2026-11-13.jsonl")
        self.assertEqual(len(rows), 2)  # one trade + one summary
        t, s = rows
        self.assertEqual((t["type"], t["mode"], t["day"], t["order_id"], t["exit_reason"]),
                         ("trade", "replay", "2026-11-13", "A", "target"))
        self.assertAlmostEqual(t["r_gross"], 1.44, places=9)
        self.assertAlmostEqual(t["r_net"], 1.16152, places=9)
        self.assertEqual((s["type"], s["mode"], s["n_trades"], s["wins"]), ("summary", "replay", 1, 1))
        self.assertAlmostEqual(s["r_net_sum"], 1.16152, places=9)
        self.assertIn("| A | buy | breakout | Europe high | 69620 | 69980 | target | 1.44 | 1.16 |", out)
        self.assertTrue(r["complete"])

    def test_host_fallback_on_error(self):
        calls = []

        def fetch(url):
            calls.append(url)
            if "data-api.binance.vision" in url:
                raise OSError("down")
            return ROWS

        r, _ = run_score(self.plan_path, out_dir=self.dir / "o", fetch=fetch)
        self.assertEqual(len(calls), 2)
        self.assertIn("api.binance.com", calls[1])
        self.assertEqual(r["summary"]["n_trades"], 1)

    def test_all_hosts_fail_raises(self):
        def fetch(url):
            raise OSError("down")

        with self.assertRaises(RuntimeError):
            run_score(self.plan_path, out_dir=self.dir / "o", fetch=fetch)

    def test_empty_klines_tries_next_host_then_raises(self):
        with self.assertRaises(RuntimeError):
            run_score(self.plan_path, out_dir=self.dir / "o", fetch=lambda url: [])

    def test_explicit_bars_skip_fetch(self):
        def boom(url):
            raise AssertionError("must not fetch")

        bars = [{"t": ARM, "o": 69000, "h": 69100, "l": 68900, "c": 69000}]
        r, out = run_score(self.plan_path, bars=bars, out_dir=self.dir / "o", fetch=boom)
        self.assertEqual(r["trades"], [])
        self.assertFalse(r["complete"])  # flat bar not in data
        self.assertIn("no trade", out)
        rows = [json.loads(l) for l in Path(r["path"]).read_text().splitlines()]
        self.assertEqual([x["type"] for x in rows], ["summary"])

    def test_env_out_dir(self):
        import os
        os.environ["US_OPEN_TRADER_DIR"] = str(self.dir / "envout")
        try:
            self.assertEqual(score.default_out_dir(), self.dir / "envout")
        finally:
            del os.environ["US_OPEN_TRADER_DIR"]
        self.assertEqual(score.default_out_dir().name, "us_open_trader")

    def test_main_network_failure_is_clean_exit_1(self):
        orig = score.http_fetch
        score.http_fetch = lambda url: (_ for _ in ()).throw(OSError("offline"))
        import os
        os.environ["US_OPEN_TRADER_DIR"] = str(self.dir / "o")
        err = io.StringIO()
        try:
            with contextlib.redirect_stderr(err):
                self.assertEqual(score.main([str(self.plan_path)]), 1)
        finally:
            score.http_fetch = orig
            del os.environ["US_OPEN_TRADER_DIR"]
        self.assertIn("score failed", err.getvalue())

    def test_main_usage_error(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(score.main([]), 2)
        self.assertIn("usage", err.getvalue())


if __name__ == "__main__":
    unittest.main()
