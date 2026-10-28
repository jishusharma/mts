"""Live validation store/doubts/hook. Expected values are hand-set (categories, case numbers), not read from code."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest.layers.alerts import live_validation as lv  # noqa: E402

SIG = dict(symbol="BTCUSDT", tf="1d", code="K-HBEAR", date_A="2026-01-23", date_B="2026-01-28",
           price_A=89558.7, price_B=89261.7, rsi_A=43.65, rsi_B=45.65, bars_A_to_B=6)


def sig(**kw):
    return dict(SIG, **kw)


class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.s = lv.Store(self.d.name)
        self.sent = []

    def tearDown(self):
        self.d.cleanup()

    def send(self, text, chart):
        self.sent.append((text, chart))

    def chart(self, s):
        return "c.png"

    def test_category_key(self):
        self.assertEqual(lv.category_key(SIG), "BTCUSDT|1d|hidden|bear")
        self.assertEqual(lv.category_key(sig(code="R-BULL", tf="1w")), "BTCUSDT|1w|regular|bull")

    def test_lookalike_inherits_case_n(self):
        n = self.s.correct(SIG, "VALID", "yes this is a hidden bear", "2026-10-28", "c.png")
        self.assertEqual(n, 1)
        other = sig(date_A="2026-05-21", date_B="2026-05-25", price_A=77586.2, price_B=77281.5,
                    rsi_A=47.89, rsi_B=48.12, bars_A_to_B=5)
        self.assertEqual(lv.match(self.s, other), "matches validated case #1")

    def test_different_geometry_is_doubt_no_verdict(self):
        self.s.correct(SIG, "VALID", "ok", "2026-10-28")
        diff = sig(date_A="2026-06-01", rsi_A=70.0, rsi_B=72.0, bars_A_to_B=6)   # other RSI zone
        self.assertEqual(lv.match(self.s, diff), "DOUBT")
        self.assertEqual([d["status"] for d in self.s.doubts()], ["open"])
        self.assertEqual(len(self.s.cases()), 1)   # no verdict written

    def test_out_of_window_and_seed_never_match(self):
        self.s.add_case(SIG, None, None, "2026-10-28", "c.png", "seed")
        self.assertEqual(lv.match(self.s, SIG), "DOUBT")   # unreviewed seed gives no verdict
        self.s.correct(sig(date_A="x"), "VALID", "ok", "d")
        self.assertEqual(lv.match(self.s, sig(date_A="y", bars_A_to_B=12)), "DOUBT")

    def test_correction_moves_doubt(self):
        lv.match(self.s, SIG)
        n = self.s.correct(SIG, "WRONG", "not a divergence", "2026-10-28")
        d = self.s.doubts()
        self.assertEqual((d[0]["status"], d[0]["resolved_by_case"]), ("closed", n))

    def test_restart_keeps_store_and_no_duplicate_send(self):
        self.s.correct(SIG, "VALID", "ok", "d")
        self.assertEqual(lv.process_signal(self.s, SIG, self.chart, self.send), "SENT")
        s2 = lv.Store(self.d.name)   # restart / reset: new objects, same files
        self.assertEqual(len(s2.cases()), 1)
        self.assertEqual(lv.process_signal(s2, SIG, self.chart, self.send), "DUPLICATE")
        self.assertEqual(len(self.sent), 1)
        self.assertIn("matches validated case #1", self.sent[0][0])

    def test_send_error_leaves_pending_then_retry(self):
        def boom(t, c):
            raise ConnectionError("api")
        self.assertEqual(lv.process_signal(self.s, SIG, self.chart, boom), "PENDING")
        st = self.s.state()
        self.assertEqual(st["sent"], [])
        self.assertEqual(len(st["pending"]), 1)
        self.assertEqual(list(lv.retry_pending(self.s, self.chart, self.send).values()), ["SENT"])
        self.assertEqual(self.s.state()["pending"], {})

    def test_chart_error_fails_closed(self):
        def bad(s):
            raise OSError("render")
        self.assertEqual(lv.process_signal(self.s, SIG, bad, self.send), "PENDING")
        self.assertEqual(self.sent, [])
        self.assertEqual(self.s.cases(), [])

    def test_non_signal_events_rejected(self):
        for ev in ({"type": "deposit", "amount": 5}, {"code": "K-HBEAR", "tf": "1d"}, None,
                   sig(rsi_A=float("nan"))):
            self.assertEqual(lv.process_signal(self.s, ev, self.chart, self.send), "REJECTED")
        self.assertEqual(self.sent, [])
        self.assertEqual(self.s.cases(), [])

    def test_corrupt_store_fails_closed(self):
        Path(self.s.p_store).write_text("{not json", encoding="utf-8")
        self.assertEqual(lv.match(self.s, SIG), "DOUBT")
        Path(self.s.p_state).write_text("{bad", encoding="utf-8")
        self.assertEqual(lv.process_signal(self.s, SIG, self.chart, self.send), "PENDING")
        self.assertEqual(self.sent, [])

    def test_seed_from_history_one_per_type(self):
        csvp = REPO / "MyTradingSys/research/malkan_div_flags_2026-10-28/BTCUSDT_divergences.csv"
        made = lv.seed_from_history(self.s, csvp, "MyTradingSys/research/malkan_div_flags_2026-10-28", "2026-10-28")
        keys = sorted(c["category"] for c in self.s.cases())
        self.assertEqual(len(made), 8)
        self.assertEqual(keys, sorted(set(keys)))
        self.assertTrue(all(c["verdict"] is None for c in self.s.cases()))
        self.assertEqual(lv.seed_from_history(self.s, csvp, "x", "d"), [])   # idempotent


if __name__ == "__main__":
    unittest.main()
