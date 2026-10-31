"""test_cotrade.py - fake client only, no network, no secrets. Testnet co-trade P1."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cotrade  # noqa: E402
import deribit_orders as do  # noqa: E402

SAID = "short 100 at 110500 stop 111000, go!"


class FakeClient:
    def __init__(self, position=0, orders=None, fill=True, place_exc=None, stop_exc=None, order_none=False):
        self.position = position
        self.orders = orders or []
        self.fill = fill
        self.place_exc = place_exc
        self.stop_exc = stop_exc
        self.calls = []

    def authenticate(self, account=None):
        self.calls.append(("authenticate", account))
        return "tok"

    def get_ticker(self, instrument_name="BTC-PERPETUAL"):
        return {"mark_price": 110400.0, "best_bid_price": 110399.0, "best_ask_price": 110401.0}

    def get_position(self, token, instrument_name="BTC-PERPETUAL"):
        return {"size": self.position}

    def get_open_orders(self, token, instrument_name="BTC-PERPETUAL", type_="all"):
        return list(self.orders)

    def place(self, token, side, instrument_name, amount, order_type="limit", price=None, label=None,
              post_only=False, reduce_only=False):
        self.calls.append(("place", side, amount, order_type, price, label))
        if self.place_exc:
            raise self.place_exc
        if self.fill:
            self.position = -amount if side == "sell" else amount
        return {"order_id": "E1", "filled_amount": amount if self.fill else 0, "order_state": "filled" if self.fill else "open"}

    def stop_market(self, token, instrument_name, side, amount, trigger_price, label, trigger="mark_price"):
        self.calls.append(("stop_market", side, amount, trigger_price, label))
        if self.stop_exc:
            raise self.stop_exc
        self.orders.append({"order_id": "S1", "label": label, "order_type": "stop_market", "reduce_only": True})
        return {"order": {"order_id": "S1"}}

    def cancel_by_label(self, token, label, currency="BTC"):
        self.calls.append(("cancel_by_label", label))
        return 1

    def close_position(self, token, instrument_name="BTC-PERPETUAL"):
        self.calls.append(("close_position",))
        self.position = 0
        return {}

    def names(self):
        return [c[0] for c in self.calls]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.halt = self.dir / "HALT"
        self.halt_dl = self.dir / "HALT_DAILY_LOSS"
        self.jdir = self.dir / "journal"

    def tearDown(self):
        self.tmp.cleanup()

    def run_place(self, client, **kw):
        args = dict(said=SAID, side="sell", order_type="limit", price=110500.0, amount=100, stop=111000.0,
                    dry_run=False, client=client, account=None, journal_dir=self.jdir,
                    halt_path=self.halt, halt_daily_loss_path=self.halt_dl, env="test")
        args.update(kw)
        return cotrade.place_order(**args)

    def lines(self):
        out = []
        for p in sorted(self.jdir.glob("*.jsonl")) if self.jdir.exists() else []:
            out += [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
        return out


class TestRefusals(Base):
    def test_refuses_no_stop(self):
        c = FakeClient()
        r = self.run_place(c, stop=None)
        self.assertFalse(r["ok"])
        self.assertNotIn("place", c.names())

    def test_refuses_stop_on_wrong_side(self):
        c = FakeClient()
        r = self.run_place(c, stop=110000.0)  # short with stop below entry
        self.assertFalse(r["ok"])
        self.assertNotIn("place", c.names())

    def test_refuses_not_testnet(self):
        c = FakeClient()
        r = self.run_place(c, env="mainnet")
        self.assertFalse(r["ok"])
        self.assertEqual(c.calls, [])

    def test_refuses_halt_present(self):
        self.halt.write_text("x", encoding="utf-8")
        c = FakeClient()
        r = self.run_place(c)
        self.assertFalse(r["ok"])
        self.assertIn("HALT", " ".join(r["reasons"]))
        self.assertNotIn("place", c.names())

    def test_refuses_daily_loss_halt(self):
        self.halt_dl.write_text("{}", encoding="utf-8")
        c = FakeClient()
        self.assertFalse(self.run_place(c)["ok"])
        self.assertNotIn("place", c.names())

    def test_refuses_over_cap(self):
        c = FakeClient()
        r = self.run_place(c, amount=10010, price=110500.0, stop=110600.0)
        self.assertFalse(r["ok"])
        self.assertNotIn("place", c.names())

    def test_refuses_over_cap_with_existing_position(self):
        c = FakeClient(position=-9950)
        self.assertFalse(self.run_place(c, amount=100)["ok"])
        self.assertNotIn("place", c.names())

    def test_refuses_loss_at_stop_over_limit(self):
        c = FakeClient()
        # 9000 USD, stop 10% away = $900 loss > $500
        r = self.run_place(c, amount=9000, price=110000.0, stop=121000.0)
        self.assertFalse(r["ok"])
        self.assertNotIn("place", c.names())

    def test_refuses_bad_amount_and_side(self):
        for kw in (dict(amount=0), dict(amount=-10), dict(amount=105), dict(side="hold"), dict(order_type="stop")):
            c = FakeClient()
            self.assertFalse(self.run_place(c, **kw)["ok"], kw)
            self.assertNotIn("place", c.names())

    def test_refuses_unreadable_position_fail_closed(self):
        class Bad(FakeClient):
            def get_position(self, *a, **k):
                raise do.DeribitError("private/get_position", {"code": 1, "message": "x"})
        c = Bad()
        self.assertFalse(self.run_place(c)["ok"])
        self.assertNotIn("place", c.names())

    def test_refuses_missing_account_secret(self):
        c = FakeClient()
        r = self.run_place(c, account="jishu_22", secret_exists=lambda a: False)
        self.assertFalse(r["ok"])
        self.assertNotIn("place", c.names())


class TestRestartReconcile(Base):
    def test_open_position_refuses(self):
        c = FakeClient(position=-100)
        r = self.run_place(c)
        self.assertFalse(r["ok"])
        self.assertNotIn("place", c.names())

    def test_open_order_not_in_journal_refuses(self):
        c = FakeClient(orders=[{"order_id": "X9", "label": "cotrade"}])
        r = self.run_place(c)
        self.assertFalse(r["ok"])
        self.assertIn("journal", " ".join(r["reasons"]).lower())
        self.assertNotIn("place", c.names())

    def test_open_order_in_journal_still_refuses_one_at_a_time(self):
        c = FakeClient()
        self.run_place(c, order_type="limit", dry_run=False)  # fills -> position -100
        c2 = FakeClient(position=0, orders=[{"order_id": "E1", "label": "cotrade"}])
        r = self.run_place(c2)
        self.assertFalse(r["ok"])
        self.assertNotIn("place", c2.names())

    def test_unknown_state_in_journal_blocks_next_order(self):
        c = FakeClient(place_exc=do.OrderStateUnknown("private/sell", "lbl", 10050))
        self.run_place(c)
        c2 = FakeClient()
        r = self.run_place(c2)
        self.assertFalse(r["ok"])
        self.assertIn("unknown", " ".join(r["reasons"]).lower())
        self.assertNotIn("place", c2.names())


class TestPlaceFlow(Base):
    def test_happy_path_places_entry_and_stop_and_journals_said_verbatim(self):
        c = FakeClient()
        r = self.run_place(c)
        self.assertTrue(r["ok"], r)
        self.assertEqual(c.names().count("place"), 1)
        stop = [x for x in c.calls if x[0] == "stop_market"][0]
        self.assertEqual(stop[1], "BUY")      # short entry -> buy stop
        self.assertEqual(stop[2], 100)
        self.assertEqual(stop[3], 111000.0)
        recs = self.lines()
        self.assertEqual(recs[-1]["said"], SAID)
        self.assertEqual(recs[-1]["env"], "test")
        self.assertIn("market", recs[-1])
        self.assertIn("heard", recs[-1])
        self.assertEqual(recs[-1]["action"]["stop"], 111000.0)

    def test_resting_limit_has_no_stop_yet_and_says_so(self):
        c = FakeClient(fill=False)
        r = self.run_place(c)
        self.assertTrue(r["ok"])
        self.assertNotIn("stop_market", c.names())
        self.assertTrue(r["stop_pending"])
        self.assertTrue(self.lines()[-1]["result"]["stop_pending"])

    def test_ensure_stop_after_later_fill(self):
        c = FakeClient(fill=False)
        self.run_place(c)
        c.position = -100  # filled later
        r = cotrade.ensure_stop(client=c, account=None, journal_dir=self.jdir,
                                halt_path=self.halt, halt_daily_loss_path=self.halt_dl)
        self.assertTrue(r["ok"], r)
        self.assertEqual([x for x in c.calls if x[0] == "stop_market"][0][2], 100)
        # second call: stop exists, no second stop
        n = c.names().count("stop_market")
        cotrade.ensure_stop(client=c, account=None, journal_dir=self.jdir,
                            halt_path=self.halt, halt_daily_loss_path=self.halt_dl)
        self.assertEqual(c.names().count("stop_market"), n)

    def test_stop_failure_after_fill_flattens_and_halts(self):
        c = FakeClient(stop_exc=do.DeribitError("private/buy", {"code": 1, "message": "no"}))
        r = self.run_place(c)
        self.assertFalse(r["ok"])
        self.assertIn("close_position", c.names())
        self.assertTrue(self.halt.exists())

    def test_order_state_unknown_journaled_no_retry(self):
        c = FakeClient(place_exc=do.OrderStateUnknown("private/sell", "lbl", 10050))
        r = self.run_place(c)
        self.assertFalse(r["ok"])
        self.assertEqual(c.names().count("place"), 1)
        self.assertNotIn("stop_market", c.names())
        self.assertEqual(self.lines()[-1]["result"]["state"], "unknown")

    def test_api_error_on_place_journaled_fail_closed(self):
        c = FakeClient(place_exc=do.DeribitError("private/sell", {"code": 11044, "message": "x"}))
        r = self.run_place(c)
        self.assertFalse(r["ok"])
        self.assertEqual(self.lines()[-1]["result"]["state"], "error")

    def test_dry_run_prints_order_one_journal_line_no_orders(self):
        c = FakeClient()
        r = self.run_place(c, dry_run=True)
        self.assertTrue(r["ok"])
        self.assertNotIn("place", c.names())
        self.assertNotIn("stop_market", c.names())
        recs = self.lines()
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["said"], SAID)
        self.assertEqual(recs[0]["result"]["state"], "dry_run")

    def test_dry_run_does_not_block_next_real_order(self):
        c = FakeClient()
        self.run_place(c, dry_run=True)
        self.assertTrue(self.run_place(c)["ok"])


class TestAccountAndKill(Base):
    def test_account_prefers_jishu_22_else_main(self):
        self.assertEqual(cotrade.pick_account(secret_exists=lambda a: a == "jishu_22"), "jishu_22")
        self.assertIsNone(cotrade.pick_account(secret_exists=lambda a: False))

    def test_kill_halts_first_cancels_and_flattens(self):
        c = FakeClient(position=-100)
        r = cotrade.kill(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt)
        self.assertTrue(self.halt.exists())
        self.assertEqual(c.names()[1:], ["cancel_by_label", "close_position"])
        self.assertEqual(c.calls[1][1], "cotrade")
        self.assertTrue(r["ok"])
        self.assertEqual(self.lines()[-1]["action"]["kind"], "kill")

    def test_kill_still_halts_when_exchange_errors(self):
        class Bad(FakeClient):
            def cancel_by_label(self, *a, **k):
                raise do.DeribitError("x", {"code": 1, "message": "m"})
        c = Bad(position=-100)
        r = cotrade.kill(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt)
        self.assertTrue(self.halt.exists())
        self.assertFalse(r["ok"])
        self.assertIn("close_position", c.names())  # keeps going after a failed cancel


if __name__ == "__main__":
    unittest.main()
