"""Tests for of_backfill.py (TF3). No network: the raw aggTrades CSV is pre-placed so process_day never downloads.
Expected numbers are hand arithmetic (is_buyer_maker true = SELL aggressor; thr_days = prior histogram files found)."""
import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from MyTradingSys.backtest.layers.fabio import of_backfill as bf

DAY = date(2026, 10, 1)
T0 = int(datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp() * 1000)


def setup(tmp, prior=True, live_state_day="2026-10-03"):
    tmp = Path(tmp)
    raw, stage, live, off = tmp / "raw", tmp / "stage", tmp / "live", tmp / "off"
    (raw / "aggTrades").mkdir(parents=True)
    stage.mkdir()
    (live / "_qhist").mkdir(parents=True)
    (off).mkdir()
    if live_state_day:
        (live / "_state.json").write_text(json.dumps({"next_ms": 5, "day": live_state_day}))
    if prior:
        (off / "2026-09-30.json").write_text(json.dumps({"100": 50}))   # all qty 0.01
    # id, price, qty, first, last, ts, maker: minute 0 = buy 2.0 @100, sell 1.0 @100 ; minute 1 = buy 0.5 @110
    rows = [(1, 100.0, 2.0, 1, 1, T0 + 1000, "false"), (2, 100.0, 1.0, 2, 2, T0 + 2000, "true"),
            (3, 110.0, 0.5, 3, 3, T0 + 60000 + 5, "false")]
    (raw / "aggTrades" / f"BTCUSDT-aggTrades-{DAY.isoformat()}.csv").write_text(
        "agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker\n"
        + "".join(",".join(str(x) for x in r) + "\n" for r in rows))
    return raw, stage, live, off


class BackfillTest(unittest.TestCase):
    def test_writes_live_schema_and_leaves_state(self):
        with tempfile.TemporaryDirectory() as t:
            raw, stage, live, off = setup(t)
            before = (live / "_state.json").read_text()
            res = bf.backfill_day(DAY, raw, stage, live, off)
            self.assertEqual(res, "ok rows=2 thr_days=1")
            lines = (live / "2026-10-01.csv").read_text().splitlines()
            self.assertEqual(len(lines), 3)                       # header + 2 minutes
            r0 = dict(zip(lines[0].split(","), lines[1].split(",")))
            self.assertEqual(float(r0["buy_vol"]), 2.0)
            self.assertEqual(float(r0["sell_vol"]), 1.0)
            self.assertEqual(float(r0["delta"]), 1.0)
            self.assertEqual(int(r0["thr_days"]), 1)
            self.assertTrue((live / "_qhist" / "2026-10-01.json").exists())
            self.assertEqual((live / "_state.json").read_text(), before)

    def test_refuses_day_owned_by_live_writer(self):
        with tempfile.TemporaryDirectory() as t:
            raw, stage, live, off = setup(t, live_state_day="2026-10-01")
            self.assertTrue(bf.backfill_day(DAY, raw, stage, live, off).startswith("skip: live writer"))
            self.assertFalse((live / "2026-10-01.csv").exists())

    def test_existing_day_not_overwritten(self):
        with tempfile.TemporaryDirectory() as t:
            raw, stage, live, off = setup(t)
            (live / "2026-10-01.csv").write_text("keep\n")
            self.assertEqual(bf.backfill_day(DAY, raw, stage, live, off), "skip: exists")
            self.assertEqual((live / "2026-10-01.csv").read_text(), "keep\n")

    def test_no_prior_histogram_writes_nothing(self):
        with tempfile.TemporaryDirectory() as t:
            raw, stage, live, off = setup(t, prior=False)
            self.assertTrue(bf.backfill_day(DAY, raw, stage, live, off).startswith("refused"))
            self.assertFalse((live / "2026-10-01.csv").exists())


if __name__ == "__main__":
    unittest.main()
