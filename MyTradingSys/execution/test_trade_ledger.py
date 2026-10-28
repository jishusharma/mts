"""Offline tests for trade_ledger.py (fake exchange fills, temp files). Expected numbers are hand-computed for the
inverse perpetual: long gross USD = q*(X/E-1), short = q*(1-X/E), fee_usd = fee_btc * fill price."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import trade_ledger as tl  # noqa: E402

T0 = 1_790_000_000_000
MIN = 60_000


def fill(ts_min, direction, price, amount, label, fee=0.0):
    return {"timestamp": T0 + int(ts_min * MIN), "direction": direction, "price": price, "amount": amount,
            "label": label, "fee": fee, "fee_currency": "BTC"}


ATT = {"event": "trade_attempt", "plan_id": "P1", "source": "layer:rsi:x:15m", "key": "k1", "outcome": "entered",
       "ts": "2026-09-29T02:00:46Z"}


class BuildRowTest(unittest.TestCase):
    def test_long_target_with_fees_and_funding(self):
        trades = [fill(0, "buy", 80000, 100, "P1:entry1", 0.0000015), fill(30, "sell", 81600, 100, "P1:target1", 0.0000015)]
        r = tl.build_row(ATT, trades, [], {}, "jishu_2", 0, funding_btc=-0.000001)
        self.assertEqual(r["side"], "long")
        self.assertAlmostEqual(r["gross_pnl_usd"], 2.0, places=4)              # 100*(81600/80000-1)
        self.assertAlmostEqual(r["fees_usd"], 0.2424, places=4)                # 0.12 + 0.1224
        self.assertAlmostEqual(r["funding_usd"], -0.0816, places=4)            # -1e-6 * 81600
        self.assertAlmostEqual(r["net_pnl_usd"], 1.676, places=4)              # 2 - 0.2424 - 0.0816
        self.assertEqual(r["exit_reason"], "target")
        self.assertEqual(r["hold_minutes"], 30.0)
        self.assertEqual((r["source"], r["account"], r["alert_key"], r["plan_id"]), ("layer:rsi:x:15m", "jishu_2", "k1", "P1"))
        self.assertEqual(r["entry"]["price"], 80000)

    def test_short_stop_loss(self):
        trades = [fill(0, "sell", 80000, 100, "P1:entry1"), fill(5, "buy", 80800, 100, "P1:stop")]
        r = tl.build_row(ATT, trades)
        self.assertEqual(r["side"], "short")
        self.assertAlmostEqual(r["gross_pnl_usd"], -1.0, places=4)             # 100*(1-80800/80000)
        self.assertEqual(r["exit_reason"], "stop")
        self.assertIsNone(r["funding_usd"])
        self.assertAlmostEqual(r["net_pnl_usd"], -1.0, places=4)

    def test_multiple_exit_fills_use_vwap(self):
        trades = [fill(0, "buy", 80000, 100, "P1:entry1"), fill(1, "sell", 81000, 60, "P1:target1"),
                  fill(2, "sell", 82000, 40, "P1:target2")]
        r = tl.build_row(ATT, trades)
        self.assertEqual(len(r["exits"]), 2)
        self.assertAlmostEqual(r["gross_pnl_usd"], 1.75, places=4)             # X = 81400 -> 100*(81400/80000-1)

    def test_exit_reason_from_journal_and_hold_time(self):
        trades = [fill(0, "buy", 80000, 100, "P1:entry1"), fill(10, "sell", 80100, 100, None)]
        self.assertEqual(tl.build_row(ATT, trades, [{"event_type": "time_exit", "data": {}}])["exit_reason"], "time_exit")
        halt = [{"event_type": "mismatch_halt", "data": {"reason": "position sign flipped"}}]
        self.assertEqual(tl.build_row(ATT, trades, halt)["exit_reason"], "flatten_halt")
        manual = [{"event_type": "mismatch_halt", "data": {"reason": "position flat but no stop trigger / target fill explains it"}}]
        self.assertEqual(tl.build_row(ATT, trades, manual)["exit_reason"], "manual")
        r = tl.build_row(ATT, trades, [], {"max_hold_minutes": 10})           # unlabeled close at the time limit
        self.assertEqual((r["exit_reason"], r["exit_reason_src"]), ("time_exit", "hold_time"))
        self.assertEqual(tl.build_row(ATT, trades, [], {"max_hold_minutes": 120})["exit_reason"], "manual")

    def test_triggered_by_fills_stop_is_not_labelled_target(self):
        # position_manager sets target_filled = reduce-side fills on the triggered_by_fills fallback (the stop's own fill)
        ev = [{"event_type": "reconciliation", "data": {"result": "position_closed", "stop_state": "triggered_by_fills",
                                                        "target_filled": 100}}]
        stop = [fill(0, "sell", 80000, 100, "P1:entry1"), fill(5, "buy", 80800, 100, "P1:stop_order_pending_fill")]
        r = tl.build_row(ATT, stop, ev)
        self.assertLess(r["gross_pnl_usd"], 0)
        self.assertEqual((r["exit_reason"], r["exit_reason_src"]), ("stop", "journal"))
        tgt = [fill(0, "sell", 80000, 100, "P1:entry1"), fill(5, "buy", 79000, 100, "P1:target_1")]
        self.assertEqual(tl.build_row(ATT, tgt, ev)["exit_reason"], "target")
        ev2 = [{"event_type": "reconciliation", "data": {"stop_state": "filled", "target_filled": 100}}]
        self.assertEqual(tl.build_row(ATT, tgt, ev2)["exit_reason"], "target")     # normal journal path unchanged

    def test_open_position_is_not_a_row_unless_forced(self):
        trades = [fill(0, "buy", 80000, 100, "P1:entry1"), fill(5, "sell", 81000, 40, "P1:target1")]
        self.assertIsNone(tl.build_row(ATT, trades))
        r = tl.build_row(ATT, trades, force=True)
        self.assertTrue(r["partial"])
        self.assertIsNone(tl.build_row(ATT, [fill(0, "sell", 1, 1, "OTHER:entry1")]))   # other plan's fills ignored


class SummaryTest(unittest.TestCase):
    def test_per_source(self):
        rows = [{"source": "a", "net_pnl_usd": 1.0}, {"source": "a", "net_pnl_usd": -0.5},
                {"source": "a", "net_pnl_usd": 2.0}, {"source": "b", "net_pnl_usd": -1.0}]
        s = tl.summarize(rows)
        self.assertEqual(s["a"]["n"], 3)
        self.assertAlmostEqual(s["a"]["win_rate"], 2 / 3)
        self.assertAlmostEqual(s["a"]["mean_net"], 0.8333, places=4)
        self.assertAlmostEqual(s["a"]["sum_net"], 2.5)
        self.assertEqual((s["b"]["n"], s["b"]["wins"]), (1, 0))


class RecordAndBackfillTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.ledger, self.log = d / "ledger.jsonl", d / "auto.jsonl"
        self.log.write_text("\n".join(json.dumps(x) for x in [
            ATT, {"event": "trade_closed", "plan_id": "P1", "manager_rc": 0},
            {**ATT, "plan_id": "P2", "key": "k2"}, {**ATT, "plan_id": "P3", "outcome": "no_fill"}]) + "\n", encoding="utf-8")
        self.calls = []
        good = [fill(0, "buy", 80000, 100, "P1:entry1"), fill(9, "sell", 81600, 100, "P1:target1")]

        def fetcher(plan_id, account, t_from):
            self.calls.append((plan_id, account))
            return (good, None) if (plan_id == "P1" and account == "b") else ([], None)
        self.fetcher = fetcher

    def tearDown(self):
        self.tmp.cleanup()

    def rows(self):
        return [json.loads(l) for l in self.ledger.read_text(encoding="utf-8").splitlines()]

    def test_record_closed_is_idempotent_and_takes_source_from_log(self):
        r = tl.record_closed("P1", None, "b", 0, self.fetcher, self.ledger, self.log, events=[], plan={})
        self.assertEqual(r["source"], "layer:rsi:x:15m")
        self.assertIsNone(tl.record_closed("P1", None, "b", 0, self.fetcher, self.ledger, self.log, events=[], plan={}))
        self.assertEqual(len(self.rows()), 1)

    def test_backfill_probes_accounts_and_reports_unresolved(self):
        orig = tl._journal_events, tl._plan
        tl._journal_events, tl._plan = (lambda pid: []), (lambda pid: {})
        try:
            added, unresolved = tl.backfill(self.fetcher, self.ledger, self.log, candidates=lambda hint: [None, "a", "b"])
        finally:
            tl._journal_events, tl._plan = orig
        self.assertEqual([r["plan_id"] for r in added], ["P1"])
        self.assertEqual(added[0]["account"], "b")
        self.assertEqual(unresolved, ["P2"])                # P3 was never entered: not considered
        self.assertEqual([(r["plan_id"], bool(r.get("unresolved"))) for r in self.rows()],
                         [("P1", False), ("P2", True)])     # unresolved plans still get a row


class UnresolvedRowTest(RecordAndBackfillTest):
    def test_named_account_is_used_and_row_carries_it(self):
        r = tl.record_closed("P1", None, "b", 0, self.fetcher, self.ledger, self.log, events=[], plan={})
        self.assertEqual(r["account"], "b")
        self.assertIn(("P1", "b"), self.calls)
        self.assertNotIn(("P1", None), self.calls)

    def test_unresolved_still_writes_row(self):
        r = tl.record_closed("P2", None, "b", 1, self.fetcher, self.ledger, self.log, events=[], plan={})
        self.assertTrue(r["unresolved"])
        self.assertEqual((r["plan_id"], r["account"], r["manager_rc"]), ("P2", "b", 1))
        self.assertEqual(len(self.rows()), 1)

    def test_fetch_error_still_writes_row_and_resolved_supersedes(self):
        def boom(plan_id, account, t_from):
            raise RuntimeError("auth")
        r = tl.record_closed("P1", None, "b", 1, boom, self.ledger, self.log, events=[], plan={})
        self.assertIn("auth", r["unresolved"])
        r2 = tl.record_closed("P1", None, "b", 1, self.fetcher, self.ledger, self.log, events=[], plan={})
        self.assertIsNone(r2.get("unresolved"))
        self.assertEqual(tl.summarize(self.rows())["layer:rsi:x:15m"]["n"], 1)
        self.assertIsNone(tl.record_closed("P1", None, "b", 1, self.fetcher, self.ledger, self.log, events=[], plan={}))


if __name__ == "__main__":
    unittest.main(verbosity=1)
