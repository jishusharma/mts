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
        self.halt_path = None
        self.halt_seen = {}      # call name -> HALT file existed at that moment
        self.fill_on_cancel = 0  # simulate a fill landing just before the cancel
        self.prefix = ""         # order id prefix (P5: one fake per account)
        self.close_exc = None

    def _see(self, name):
        if self.halt_path is not None:
            self.halt_seen.setdefault(name, Path(self.halt_path).exists())

    def authenticate(self, account=None):
        self._see("authenticate")
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
        return {"order_id": self.prefix + "E1", "filled_amount": amount if self.fill else 0, "order_state": "filled" if self.fill else "open"}

    def stop_market(self, token, instrument_name, side, amount, trigger_price, label, trigger="mark_price"):
        self.calls.append(("stop_market", side, amount, trigger_price, label))
        if self.stop_exc:
            raise self.stop_exc
        n = sum(1 for o in self.orders if o.get("order_type") == "stop_market") + 1
        self.orders.append({"order_id": f"{self.prefix}S{n}", "label": label, "order_type": "stop_market", "reduce_only": True,
                            "amount": amount, "trigger_price": trigger_price})
        return {"order": {"order_id": f"{self.prefix}S{n}"}}

    def cancel(self, token, order_id):
        self.calls.append(("cancel", order_id))
        self.orders = [o for o in self.orders if o.get("order_id") != order_id]
        return {}

    def cancel_by_label(self, token, label, currency="BTC"):
        self._see("cancel_by_label")
        self.calls.append(("cancel_by_label", label))
        if self.fill_on_cancel:
            self.position = -self.fill_on_cancel
        return 1

    def close_position(self, token, instrument_name="BTC-PERPETUAL"):
        self._see("close_position")
        self.calls.append(("close_position",))
        if self.close_exc:
            raise self.close_exc
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

    def test_unknown_not_last_record(self):
        c = FakeClient(place_exc=do.OrderStateUnknown("private/sell", "lbl", 10050))
        self.run_place(c)
        cotrade._append(self.jdir, {"said": "x", "action": {"kind": "place"}, "result": {"state": "error"}})
        cotrade._append(self.jdir, {"said": "k", "action": {"kind": "kill"}, "result": {"state": "kill_errors"}})
        self.assertEqual(self.lines()[-1]["result"]["state"], "kill_errors")
        c3 = FakeClient()
        r = self.run_place(c3)
        self.assertFalse(r["ok"])
        self.assertIn("unknown", " ".join(r["reasons"]).lower())
        self.assertNotIn("place", c3.names())

    def test_unknown_cleared_by_later_kill(self):
        c = FakeClient(place_exc=do.OrderStateUnknown("private/sell", "lbl", 10050))
        self.run_place(c)
        cotrade.kill(client=FakeClient(), account=None, journal_dir=self.jdir, halt_path=self.halt)
        self.halt.unlink()
        self.assertTrue(self.run_place(FakeClient())["ok"])

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

    def test_resting_limit_fills_later_gets_stop(self):
        # the entry rests unfilled: it must be cancelled and refused, never left to fill without a stop
        c = FakeClient(fill=False)
        r = self.run_place(c)
        self.assertFalse(r["ok"])
        self.assertIn("resting", " ".join(r["reasons"]))
        self.assertIn("cancel_by_label", c.names())
        self.assertEqual(self.lines()[-1]["result"]["state"], "resting_refused")
        self.assertEqual(c.position, 0)

    def test_resting_limit_filled_before_cancel_gets_stop(self):
        c = FakeClient(fill=False)
        c.fill_on_cancel = 100
        r = self.run_place(c)
        self.assertFalse(r["ok"])
        self.assertEqual([x for x in c.calls if x[0] == "stop_market"][0][2], 100)
        self.assertLess(c.names().index("cancel_by_label"), c.names().index("stop_market"))

    def test_resting_limit_cancel_failure_flattens_and_halts(self):
        class Bad(FakeClient):
            def cancel_by_label(self, *a, **k):
                raise do.DeribitError("x", {"code": 1, "message": "m"})
        c = Bad(fill=False)
        r = self.run_place(c)
        self.assertFalse(r["ok"])
        self.assertTrue(self.halt.exists())
        self.assertIn("close_position", c.names())

    def test_ensure_stop_after_later_fill(self):
        c = FakeClient(fill=False)
        self.run_place(c)
        c.position = -100  # filled later (manual `stop` command path)
        r = cotrade.ensure_stop(client=c, account=None, journal_dir=self.jdir,
                                halt_path=self.halt, halt_daily_loss_path=self.halt_dl)
        self.assertTrue(r["ok"], r)
        self.assertEqual([x for x in c.calls if x[0] == "stop_market"][0][2], 100)
        n = c.names().count("stop_market")
        cotrade.ensure_stop(client=c, account=None, journal_dir=self.jdir,
                            halt_path=self.halt, halt_daily_loss_path=self.halt_dl)
        self.assertEqual(c.names().count("stop_market"), n)

    def _stop_case(self, amount, trigger):
        c = FakeClient()
        self.run_place(c)                      # position -100, correct stop S1 (100 @ 111000)
        c.orders = [{"order_id": "W1", "label": "cotrade", "order_type": "stop_market", "reduce_only": True,
                     "amount": amount, "trigger_price": trigger}]
        c.calls.clear()
        r = cotrade.ensure_stop(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt)
        return c, r

    def test_stop_wrong_size_or_price_not_counted(self):
        for amount, trigger in ((50, 111000.0), (100, 111500.0)):
            c, r = self._stop_case(amount, trigger)
            self.assertTrue(r["ok"], r)
            self.assertEqual(c.names().count("stop_market"), 1, (amount, trigger))
            self.assertEqual(r["replaced_wrong_stops"], ["W1"])
            # correct stop placed FIRST, then the wrong one cancelled (never unprotected)
            self.assertLess(c.names().index("stop_market"), c.names().index("cancel"))
            sm = [x for x in c.calls if x[0] == "stop_market"][0]
            self.assertEqual((sm[2], sm[3]), (100, 111000.0))

    def test_correct_stop_not_replaced(self):
        c = FakeClient()
        self.run_place(c)
        c.calls.clear()
        r = cotrade.ensure_stop(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt)
        self.assertTrue(r["ok"])
        self.assertNotIn("stop_market", c.names())
        self.assertNotIn("cancel", c.names())

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
        c.halt_path = self.halt
        r = cotrade.kill(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt)
        self.assertTrue(self.halt.exists())
        self.assertEqual(c.names()[1:], ["cancel_by_label", "close_position"])
        self.assertEqual(c.calls[1][1], "cotrade")
        self.assertTrue(r["ok"])
        self.assertEqual(self.lines()[-1]["action"]["kind"], "kill")

    def test_kill_halt_before_cancel_and_close(self):
        c = FakeClient(position=-100)
        c.halt_path = self.halt
        self.assertFalse(self.halt.exists())
        cotrade.kill(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt)
        self.assertEqual(c.halt_seen, {"authenticate": True, "cancel_by_label": True, "close_position": True})

    def test_kill_still_halts_when_exchange_errors(self):
        class Bad(FakeClient):
            def cancel_by_label(self, *a, **k):
                raise do.DeribitError("x", {"code": 1, "message": "m"})
        c = Bad(position=-100)
        r = cotrade.kill(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt)
        self.assertTrue(self.halt.exists())
        self.assertFalse(r["ok"])
        self.assertIn("close_position", c.names())  # keeps going after a failed cancel


class MultiClient:
    """One fake exchange: one FakeClient per account, token = account name."""
    def __init__(self, names=("main", "jishu_22", "jishu_1", "jishu_2", "jishu_3", "jishu_4"), **kw):
        self.subs = {n: FakeClient(**kw.get(n, {})) for n in names}
        for n, c in self.subs.items():
            c.prefix = n + "-"
        self.auth_exc = {}
        self.calls = []

    def authenticate(self, account=None):
        n = account or "main"
        self.calls.append(("authenticate", n))
        if n in self.auth_exc:
            raise self.auth_exc[n]
        return n

    def get_ticker(self, instrument_name="BTC-PERPETUAL"):
        return self.subs["main"].get_ticker(instrument_name)

    def __getattr__(self, name):
        def f(tok, *a, **k):
            self.calls.append((name, tok))
            return getattr(self.subs[tok], name)(tok, *a, **k)
        return f

    def set_halt(self, path):
        for c in self.subs.values():
            c.halt_path = path

    def on(self, acct, name):
        return [c for c in self.subs[acct].calls if c[0] == name]


ALL_KEYS = lambda a: True  # noqa: E731


def cotrade_stop(n):
    return [{"order_id": "s", "label": "cotrade", "order_type": "stop_market", "amount": n}]


class HedgeBase(Base):
    def parent(self, mc, amount=70, **kw):
        r = self.run_place(mc, amount=amount, **kw)
        self.assertTrue(r["ok"], r)
        return r

    def run_hedge(self, mc, **kw):
        args = dict(of="last", pct=50, stop=109900.0, at=None, dry_run=False, client=mc, hedge_account="auto",
                    journal_dir=self.jdir, halt_path=self.halt, halt_daily_loss_path=self.halt_dl, env="test",
                    secret_exists=ALL_KEYS, said="hedge half of it on the other account")
        args.update(kw)
        return cotrade.hedge(**args)

    def hedge_lines(self):
        return [x for x in self.lines() if (x.get("action") or {}).get("kind") == "hedge"]


class TestHedgeRefusals(HedgeBase):
    def test_1_refuses_same_account_and_missing_key(self):
        mc = MultiClient()
        self.parent(mc)
        r = self.run_hedge(mc, hedge_account=None)   # None = main = the parent account
        self.assertFalse(r["ok"])
        self.assertIn("second slot", " ".join(r["reasons"]))
        r = self.run_hedge(mc, hedge_account="jishu_2", secret_exists=lambda a: a != "jishu_2")
        self.assertFalse(r["ok"])
        self.assertIn("secret missing", " ".join(r["reasons"]))
        r = self.run_hedge(mc, secret_exists=lambda a: a is None)   # auto, but only the parent has a key
        self.assertFalse(r["ok"])
        self.assertIn("no second existing slot", " ".join(r["reasons"]))
        for n in ("jishu_1", "jishu_2", "jishu_22"):
            self.assertEqual(mc.on(n, "place"), [])
        r = self.run_hedge(mc)   # positive control: same setup, a real second slot with a key places the hedge
        self.assertTrue(r["ok"], r)
        self.assertEqual(len(mc.on("jishu_1", "place")), 1)

    def test_2_testnet_env_asserted_before_any_call(self):
        mc = MultiClient()
        self.parent(mc)
        n_calls, n_lines = len(mc.calls), len(self.lines())
        r = self.run_hedge(mc, env="mainnet")
        self.assertFalse(r["ok"])
        self.assertIn("testnet-only", " ".join(r["reasons"]))
        self.assertEqual(len(mc.calls), n_calls)
        self.assertEqual(len(self.lines()), n_lines)
        self.assertTrue(self.run_hedge(mc)["ok"])   # positive control: env=test places it

    def test_4_refused_while_halt_set(self):
        mc = MultiClient()
        self.parent(mc)
        self.halt.write_text("x", encoding="utf-8")
        r = self.run_hedge(mc)
        self.assertFalse(r["ok"])
        self.assertIn("HALT", " ".join(r["reasons"]))
        self.assertEqual(mc.on("jishu_1", "place"), [])
        self.halt.unlink()
        self.assertTrue(self.run_hedge(mc)["ok"])   # positive control: no HALT places it

    def test_5_sum_of_both_max_losses_capped(self):
        mc = MultiClient()
        self.parent(mc, amount=9000, price=110500.0, stop=116000.0)   # parent loss at stop ~ $448
        r = self.run_hedge(mc, stop=104400.0)                          # hedge 4500, ~ $245: sum > 500
        self.assertFalse(r["ok"])
        self.assertIn("both stops", " ".join(r["reasons"]))
        self.assertEqual(mc.on("jishu_1", "place"), [])
        self.assertTrue(self.run_hedge(mc, stop=110000.0)["ok"])       # tight hedge stop: sum ~ $464, allowed

    def test_13_hedge_at_that_would_rest_is_refused(self):
        mc = MultiClient()
        self.parent(mc)
        r = self.run_hedge(mc, at=110000.0)   # buy hedge below the ask 110401 would rest
        self.assertFalse(r["ok"])
        self.assertIn("rest", " ".join(r["reasons"]))
        self.assertEqual(mc.on("jishu_1", "place"), [])
        r = self.run_hedge(mc, at=110500.0)   # marketable limit is placed
        self.assertTrue(r["ok"], r)
        self.assertEqual(mc.on("jishu_1", "place")[0][3:5], ("limit", 110500.0))

    def test_unprotected_parent_or_busy_slot_refused(self):
        mc = MultiClient()
        self.parent(mc)
        mc.subs["main"].orders = []   # parent stop gone
        self.assertFalse(self.run_hedge(mc)["ok"])
        mc2 = MultiClient(jishu_1=dict(position=40))
        self.parent(mc2)
        self.assertFalse(self.run_hedge(mc2)["ok"])
        self.assertEqual(mc2.on("jishu_1", "place"), [])


class TestP5Minors(HedgeBase):
    def test_hedge_of_older_parent_uses_that_parents_stop(self):
        mc = MultiClient()
        self.parent(mc, stop=111000.0)                      # older parent: id main-E1, stop 111000
        mc.subs["main"].position, mc.subs["main"].orders, mc.subs["main"].prefix = 0, [], "p2-"
        self.parent(mc, stop=111500.0)                      # newer parent: id p2-E1, stop 111500
        mc.subs["main"].position = -70                      # exchange: the OLDER parent is the open one
        mc.subs["main"].orders = [{"order_id": "OLD", "label": "cotrade", "order_type": "stop_market",
                                   "reduce_only": True, "amount": 70, "trigger_price": 111000.0}]
        before = len(mc.on("main", "stop_market")) + len(mc.on("main", "cancel"))
        r = self.run_hedge(mc, of="main-E1")
        self.assertTrue(r["ok"], r)
        self.assertEqual(len(mc.on("main", "stop_market")) + len(mc.on("main", "cancel")), before)  # no new stop/cancel
        self.assertEqual([o["trigger_price"] for o in mc.subs["main"].orders], [111000.0])

    def test_kill_net_ensure_stop_refuse_mainnet_env(self):
        mc = MultiClient()
        self.parent(mc)
        n_calls, n_lines = len(mc.calls), len(self.lines())
        for fn in (lambda: cotrade.ensure_stop(client=mc, account=None, journal_dir=self.jdir, halt_path=self.halt,
                                               env="mainnet"),
                   lambda: cotrade.net(client=mc, journal_dir=self.jdir, secret_exists=ALL_KEYS, env="mainnet"),
                   lambda: cotrade.rebuild(client=mc, journal_dir=self.jdir, secret_exists=ALL_KEYS, env="mainnet"),
                   lambda: cotrade.kill(client=mc, account=None, journal_dir=self.jdir, halt_path=self.halt,
                                        secret_exists=ALL_KEYS, env="mainnet")):
            r = fn()
            self.assertFalse(r["ok"])
            self.assertIn("testnet-only", " ".join(r["reasons"]))
            self.assertEqual(len(mc.calls), n_calls)         # no exchange call
            self.assertEqual(len(self.lines()), n_lines)     # no journal line
        self.assertTrue(self.halt.exists())                  # kill: HALT first, even refused
        self.halt.unlink()
        self.assertTrue(cotrade.net(client=mc, journal_dir=self.jdir, secret_exists=ALL_KEYS, env="test")["ok"])
        self.assertTrue(cotrade.kill(client=mc, account=None, journal_dir=self.jdir, halt_path=self.halt,
                                     env="test")["ok"])      # positive control
        self.assertIn("close_position", [c[0] for c in mc.subs["main"].calls])

    def test_hedge_said_required(self):
        mc = MultiClient()
        self.parent(mc)
        n = len(mc.calls)
        for bad in (None, "", "   "):
            r = self.run_hedge(mc, said=bad)
            self.assertFalse(r["ok"])
            self.assertIn("--said is required", " ".join(r["reasons"]))
        self.assertEqual(mc.on("jishu_1", "place"), [])
        for x in self.hedge_lines():
            self.assertNotIn("hedge 50 pct", x["said"] or "")   # no invented text journaled as the operator's words
        r = self.run_hedge(mc, said="hedge half please")
        self.assertTrue(r["ok"], r)
        self.assertEqual(self.hedge_lines()[-1]["said"], "hedge half please")
        self.assertGreater(len(mc.calls), n)

    def test_cli_hedge_requires_said(self):
        with self.assertRaises(SystemExit):
            cotrade.main(["hedge", "--pct", "50", "--stop", "109900"])


class TestHedgePlace(HedgeBase):
    def test_3_hedge_has_its_own_stop_amount_and_trigger_match(self):
        mc = MultiClient()
        self.parent(mc)
        r = self.run_hedge(mc)
        self.assertTrue(r["ok"], r)
        sm = mc.on("jishu_1", "stop_market")
        self.assertEqual(len(sm), 1)
        self.assertEqual(sm[0][1:], ("SELL", 30, 109900.0, "cotrade"))   # buy hedge -> sell reduce-only stop
        o = mc.subs["jishu_1"].orders[0]
        self.assertTrue(o["reduce_only"] and o["amount"] == 30 and o["trigger_price"] == 109900.0)
        self.assertEqual(len(mc.subs["main"].orders), 1)                 # parent keeps its own stop

    def test_6_hedge_place_fails_no_naked_leg_journal_hedge_failed(self):
        mc = MultiClient()
        self.parent(mc)
        mc.subs["jishu_1"].place_exc = do.DeribitError("private/buy", {"code": 1, "message": "x"})
        r = self.run_hedge(mc)
        self.assertFalse(r["ok"])
        self.assertEqual(self.hedge_lines()[-1]["result"]["state"], "hedge_failed")
        self.assertEqual(mc.subs["jishu_1"].position, 0)
        self.assertEqual(mc.subs["main"].position, 0)   # card default: second-leg failure flattens both
        self.assertTrue(self.halt.exists())

    def test_hedge_stop_failure_flattens_both_and_halts(self):
        mc = MultiClient()
        self.parent(mc)
        mc.subs["jishu_1"].stop_exc = do.DeribitError("private/sell", {"code": 1, "message": "no"})
        r = self.run_hedge(mc)
        self.assertFalse(r["ok"])
        self.assertTrue(self.halt.exists())
        self.assertEqual((mc.subs["jishu_1"].position, mc.subs["main"].position), (0, 0))

    def test_hedge_unfilled_flattens_both(self):
        mc = MultiClient()
        self.parent(mc)
        mc.subs["jishu_1"].fill = False
        r = self.run_hedge(mc)
        self.assertFalse(r["ok"])
        self.assertTrue(self.halt.exists())
        self.assertIn("close_position", [c[0] for c in mc.subs["main"].calls])

    def test_hedge_unflattenable_is_unknown(self):
        mc = MultiClient()
        self.parent(mc)
        mc.subs["jishu_1"].place_exc = do.OrderStateUnknown("private/buy", "lbl", 10050)
        mc.subs["main"].close_exc = do.DeribitError("x", {"code": 1, "message": "m"})
        self.assertFalse(self.run_hedge(mc)["ok"])
        self.assertEqual(self.hedge_lines()[-1]["result"]["state"], "unknown")

    def test_7_child_journal_record_carries_parent_order_id(self):
        mc = MultiClient()
        self.parent(mc)
        self.assertTrue(self.run_hedge(mc)["ok"])
        placed = [x for x in self.hedge_lines() if x["result"]["state"] == "hedge_placed"][0]
        self.assertEqual(placed["parent_order_id"], "main-E1")
        self.assertEqual(placed["result"]["parent_order_id"], "main-E1")
        self.assertEqual(placed["account"], "jishu_1")
        self.assertEqual(placed["parent_account"], "main")

    def test_14_size_is_pct_of_parent_filled_floored_to_step_and_opposite_side(self):
        self.assertEqual(cotrade._hedge_size(70, 50), 30)    # 35 -> floor to the 10 USD step = 30
        self.assertEqual(cotrade._hedge_size(70, 100), 70)
        self.assertEqual(cotrade._hedge_size(70, 10), 0)
        mc = MultiClient()
        self.parent(mc, amount=70)
        self.assertTrue(self.run_hedge(mc, pct=50)["ok"])
        pl = mc.on("jishu_1", "place")
        self.assertEqual((pl[0][1], pl[0][2]), ("buy", 30))   # parent was a sell

    def test_14b_rounds_to_zero_refused(self):
        mc = MultiClient()
        self.parent(mc, amount=70)
        r = self.run_hedge(mc, pct=10)
        self.assertFalse(r["ok"])
        self.assertEqual(mc.on("jishu_1", "place"), [])


class TestHedgeDryRunAndViews(HedgeBase):
    def test_11_dry_run_prints_both_legs_and_net_no_call(self):
        self.parent(MultiClient())
        mc = MultiClient()
        r = self.run_hedge(mc, dry_run=True)
        self.assertTrue(r["ok"], r)
        self.assertEqual(mc.calls, [])
        self.assertEqual([(x["role"], x["account"], x["side"], x["amount_usd"]) for x in r["legs"]],
                         [("parent", "main", "sell", 70.0), ("hedge", "jishu_1", "buy", 30)])
        self.assertEqual(r["net_usd"], -40.0)
        json.dumps(r)

    def test_12_net_view_two_positions_plus30_minus10(self):
        mc = MultiClient(jishu_22=dict(position=-10, orders=cotrade_stop(10)),
                         jishu_1=dict(position=30, orders=cotrade_stop(30)))
        r = cotrade.net(client=mc, journal_dir=self.jdir, secret_exists=ALL_KEYS)
        self.assertEqual(r["net_usd"], 20.0)
        self.assertEqual(r["net_side"], "long")

    def test_9_rebuild_pair_from_exchange_not_only_journal(self):
        mc = MultiClient(jishu_22=dict(position=-70, orders=cotrade_stop(70)),
                         jishu_1=dict(position=30, orders=cotrade_stop(30)),
                         jishu_2=dict(position=500))   # not ours: no cotrade order, not in the journal
        self.assertFalse(self.jdir.exists())            # empty journal
        r = cotrade.rebuild(client=mc, journal_dir=self.jdir, secret_exists=ALL_KEYS)
        self.assertEqual(r["pair"], {"parent": "jishu_22", "hedge": "jishu_1"})
        self.assertEqual(r["net_usd"], -40.0)
        self.assertEqual(r["unowned_positions"], [{"account": "jishu_2", "size": 500.0}])
        self.assertTrue(r["ok"])

    def test_10_half_placed_hedge_is_unknown(self):
        self.parent(MultiClient())
        cotrade._append(self.jdir, {"said": "h", "account": "jishu_1", "action": {"kind": "hedge"},
                                    "result": {"state": "hedge_pending"}})
        r = self.run_hedge(MultiClient())
        self.assertFalse(r["ok"])
        self.assertIn("unknown", " ".join(r["reasons"]).lower())
        r2 = self.run_place(MultiClient())
        self.assertFalse(r2["ok"])
        self.assertIn("half-placed", " ".join(r2["reasons"]))


class TestTwoSlotKill(HedgeBase):
    def _pair(self):
        mc = MultiClient()
        self.parent(mc)
        self.assertTrue(self.run_hedge(mc)["ok"])
        mc.set_halt(self.halt)
        return mc

    def test_8_kill_flattens_both_even_if_first_flatten_raises(self):
        mc = self._pair()
        mc.subs["main"].close_exc = do.DeribitError("x", {"code": 1, "message": "m"})
        r = cotrade.kill(client=mc, account=None, journal_dir=self.jdir, halt_path=self.halt)
        self.assertFalse(r["ok"])
        self.assertEqual(mc.subs["jishu_1"].position, 0)
        self.assertEqual(mc.subs["main"].halt_seen["cancel_by_label"], True)   # HALT before the first cancel
        self.assertEqual(mc.subs["jishu_1"].halt_seen["cancel_by_label"], True)
        last = self.lines()[-1]
        self.assertEqual(last["result"]["state"], "kill_errors")
        self.assertEqual([e["account"] for e in last["result"]["errors"]], ["main"])
        self.assertEqual(last["result"]["slots"], ["main", "jishu_1"])

    def test_8b_kill_second_slot_flattened_when_first_authenticate_raises(self):
        mc = self._pair()
        mc.auth_exc["main"] = do.DeribitError("auth", {"code": 1, "message": "m"})
        r = cotrade.kill(client=mc, account=None, journal_dir=self.jdir, halt_path=self.halt)
        self.assertFalse(r["ok"])
        self.assertTrue(self.halt.exists())
        self.assertEqual(mc.subs["jishu_1"].position, 0)
        self.assertEqual(r["errors"][0]["account"], "main")

    def test_8c_kill_finds_hedge_slot_from_exchange_when_journal_lost_it(self):
        mc = MultiClient(jishu_1=dict(position=30, orders=cotrade_stop(30)), jishu_2=dict(position=500))
        r = cotrade.kill(client=mc, account=None, journal_dir=self.jdir, halt_path=self.halt, secret_exists=ALL_KEYS)
        self.assertTrue(r["ok"], r)
        self.assertEqual(mc.subs["jishu_1"].position, 0)
        self.assertEqual(mc.subs["jishu_2"].position, 500)   # not ours: never touched


# ------------------------------------------------------------------ P2: doubling-total ladder

def _expected_loss(side, sizes, prices, stop):
    """Independent of repo code: ladder_math.py formula (linear USD loss == inverse-contract loss in USD)."""
    if side == "sell":
        return sum(s * (stop / p - 1) for s, p in zip(sizes, prices))
    return sum(s * (1 - stop / p) for s, p in zip(sizes, prices))


class LadderClient(FakeClient):
    """Resting limit rungs with distinct ids; fill(n) fills rung n (1-based) into the position."""
    def __init__(self, *a, fail_on=None, fail_exc=None, **kw):
        super().__init__(*a, **kw)
        self.n = 0
        self.fail_on = fail_on
        self.fail_exc = fail_exc
        self.pos_exc = None

    def place(self, token, side, instrument_name, amount, order_type="limit", price=None, label=None,
              post_only=False, reduce_only=False):
        self.calls.append(("place", side, amount, order_type, price, label))
        self.n += 1
        if self.fail_on == self.n:
            raise self.fail_exc
        self.orders.append({"order_id": f"R{self.n}", "label": label, "order_type": "limit", "amount": amount,
                            "price": price, "side": side})
        return {"order_id": f"R{self.n}", "filled_amount": 0, "order_state": "open"}

    def fill_rung(self, n):
        o = next(o for o in self.orders if o["order_id"] == f"R{n}")
        self.orders.remove(o)
        self.position += -o["amount"] if o["side"] == "sell" else o["amount"]

    def get_position(self, token, instrument_name="BTC-PERPETUAL"):
        if self.pos_exc:
            raise self.pos_exc
        return super().get_position(token, instrument_name)

    def hit_stop(self):
        self.orders = [o for o in self.orders if o.get("order_type") != "stop_market"]
        self.position = 0


LSAID = "short 100 doubling from 110500 to 111500, 5 steps"


class TestLadderMath(unittest.TestCase):
    def test_double_total_sizes(self):
        self.assertEqual(cotrade.double_total_sizes(100, 5), [100, 200, 300, 600, 1200])
        self.assertEqual(cotrade.double_total_sizes(100, 7), [100, 200, 300, 600, 1200, 2400, 4800])
        self.assertEqual(sum(cotrade.double_total_sizes(100, 7)), 9600)

    def test_rungs_from_to_both_sides(self):
        self.assertEqual(cotrade.rung_prices("sell", 110500, to=111500, steps=5),
                         [110500, 110750, 111000, 111250, 111500])
        self.assertEqual(cotrade.rung_prices("buy", 111500, to=110500, steps=5),
                         [111500, 111250, 111000, 110750, 110500])

    def test_rungs_pct_and_points(self):
        self.assertEqual(cotrade.rung_prices("sell", 100000, spacing_pct=0.4, steps=3), [100000, 100400, 100800])
        self.assertEqual(cotrade.rung_prices("buy", 100000, spacing_pct=0.4, steps=3), [100000, 99600, 99200])
        self.assertEqual(cotrade.rung_prices("sell", 110500, spacing_pts=100, steps=3), [110500, 110600, 110700])
        self.assertEqual(cotrade.rung_prices("buy", 110500, spacing_pts=100, steps=3), [110500, 110400, 110300])

    def test_rungs_wrong_direction_or_missing_spacing_refused(self):
        with self.assertRaises(ValueError):
            cotrade.rung_prices("sell", 111500, to=110500, steps=5)   # short ladder must climb
        with self.assertRaises(ValueError):
            cotrade.rung_prices("sell", 110500, steps=5)              # no to / spacing

    def test_worst_case_matches_ladder_math(self):
        pl = cotrade.ladder_plan("sell", 110500, 5, 100, 112000, to=111500)
        self.assertTrue(pl["ok"], pl)
        prices = [110500, 110750, 111000, 111250, 111500]
        sizes = [100, 200, 300, 600, 1200]
        self.assertEqual([r["amount"] for r in pl["rungs"]], sizes)
        self.assertEqual([r["price"] for r in pl["rungs"]], prices)
        self.assertEqual(pl["total"], 2400)
        self.assertAlmostEqual(pl["worst_loss_usd"], _expected_loss("sell", sizes, prices, 112000), places=6)
        self.assertEqual(pl["margin_usd"], {"10x": 240.0, "20x": 120.0})

    def test_worst_case_design_table_example(self):
        # DESIGN.md s2: P0 100000, +0.4 % rungs, stop 0.4 % over the last rung, 5 rungs filled -> $18.38
        last = 100000 * (1 + 0.004 * 4)
        stop = round(last * 1.004 * 2) / 2   # tick-aligned stop
        pl = cotrade.ladder_plan("sell", 100000, 5, 100, stop, spacing_pct=0.4)
        self.assertTrue(pl["ok"], pl)
        self.assertAlmostEqual(pl["worst_loss_usd"], 18.38, places=2)
        pl3 = cotrade.ladder_plan("sell", 100000, 3, 100, round(100800 * 1.004 * 2) / 2, spacing_pct=0.4)
        self.assertAlmostEqual(pl3["worst_loss_usd"], 4.00, places=2)
        self.assertEqual(pl3["total"], 600)

    def test_worst_case_long_side(self):
        pl = cotrade.ladder_plan("buy", 111500, 5, 100, 110000, to=110500)
        sizes = [100, 200, 300, 600, 1200]
        prices = [111500, 111250, 111000, 110750, 110500]
        self.assertAlmostEqual(pl["worst_loss_usd"], _expected_loss("buy", sizes, prices, 110000), places=6)

    def test_caps_refuse(self):
        self.assertFalse(cotrade.ladder_plan("sell", 110500, 8, 100, 112000, to=111500)["ok"])        # > 7 rungs
        big = cotrade.ladder_plan("sell", 110500, 5, 500, 112000, to=111500)                          # 12000 > 10000
        self.assertFalse(big["ok"])
        self.assertTrue(any("cap" in r for r in big["reasons"]))
        far = cotrade.ladder_plan("sell", 110500, 5, 100, 140000, to=111500)                          # loss > 500
        self.assertFalse(far["ok"])
        self.assertTrue(any("loss at stop" in r for r in far["reasons"]))

    def test_stop_must_be_beyond_last_rung(self):
        self.assertFalse(cotrade.ladder_plan("sell", 110500, 5, 100, 111500, to=111500)["ok"])
        self.assertFalse(cotrade.ladder_plan("buy", 111500, 5, 100, 110500, to=110500)["ok"])
        self.assertFalse(cotrade.ladder_plan("sell", 110500, 5, 100, None, to=111500)["ok"])

    def test_non_tick_stop_refused(self):
        pl = cotrade.ladder_plan("sell", 110500, 5, 100, 112000.3, to=111500)
        self.assertFalse(pl["ok"])
        self.assertTrue(any("tick" in r for r in pl["reasons"]))
        self.assertTrue(cotrade.ladder_plan("sell", 110500, 5, 100, 112000.5, to=111500)["ok"])

    def test_bad_x_refused(self):
        self.assertFalse(cotrade.ladder_plan("sell", 110500, 5, 105, 112000, to=111500)["ok"])
        self.assertFalse(cotrade.ladder_plan("sell", 110500, 5, 0, 112000, to=111500)["ok"])


class TestLadderPlace(Base):
    def run_ladder(self, client, **kw):
        args = dict(said=LSAID, side="sell", frm=110500.0, steps=5, x=100, stop=112000.0, to=111500.0,
                    dry_run=False, client=client, account=None, journal_dir=self.jdir,
                    halt_path=self.halt, halt_daily_loss_path=self.halt_dl, env="test")
        args.update(kw)
        return cotrade.place_ladder(**args)

    def test_places_all_rungs_as_resting_limits(self):
        c = LadderClient()
        r = self.run_ladder(c)
        self.assertTrue(r["ok"], r)
        pl = [x for x in c.calls if x[0] == "place"]
        self.assertEqual([(x[1], x[2], x[3], x[4], x[5]) for x in pl],
                         [("sell", a, "limit", p, "cotrade") for a, p in
                          zip([100, 200, 300, 600, 1200], [110500, 110750, 111000, 111250, 111500])])
        self.assertNotIn("stop_market", c.names())      # flat: nothing to protect yet
        rec = self.lines()[-1]
        self.assertEqual(rec["said"], LSAID)
        self.assertEqual(rec["result"]["state"], "ladder_placed")
        self.assertEqual(rec["result"]["order_ids"], ["R1", "R2", "R3", "R4", "R5"])
        self.assertEqual(rec["action"]["kind"], "ladder")
        self.assertEqual(r["total"], 2400)
        self.assertAlmostEqual(r["worst_loss_usd"], _expected_loss(
            "sell", [100, 200, 300, 600, 1200], [110500, 110750, 111000, 111250, 111500], 112000), places=6)

    def test_over_cap_places_nothing_not_even_auth(self):
        for kw in (dict(x=500), dict(steps=8), dict(stop=140000.0), dict(stop=None), dict(stop=111000.0)):
            c = LadderClient()
            r = self.run_ladder(c, **kw)
            self.assertFalse(r["ok"], kw)
            self.assertNotIn("place", c.names(), kw)
            self.assertNotIn("authenticate", c.names(), kw)
            self.assertEqual(self.lines()[-1]["result"]["state"], "refused", kw)

    def test_refuses_mainnet_and_halt_and_open_state(self):
        c = LadderClient()
        self.assertFalse(self.run_ladder(c, env="live")["ok"])
        self.assertEqual(c.calls, [])
        self.assertFalse(self.lines())
        self.halt.write_text("x")
        self.assertFalse(self.run_ladder(c)["ok"])
        self.assertNotIn("place", c.names())
        self.halt.unlink()
        for c2 in (LadderClient(position=-100), LadderClient(orders=[{"order_id": "Z9", "label": "cotrade"}])):
            self.assertFalse(self.run_ladder(c2)["ok"])
            self.assertNotIn("place", c2.names())

    def test_second_ladder_refused_while_rungs_rest(self):
        c = LadderClient()
        self.assertTrue(self.run_ladder(c)["ok"])
        n = len([x for x in c.calls if x[0] == "place"])
        r = self.run_ladder(c)
        self.assertFalse(r["ok"])
        self.assertEqual(len([x for x in c.calls if x[0] == "place"]), n)

    def test_dry_run_prints_table_places_nothing(self):
        c = LadderClient()
        r = self.run_ladder(c, dry_run=True)
        self.assertTrue(r["ok"] and r["dry_run"])
        self.assertEqual(c.calls, [])
        self.assertEqual(len(r["rungs"]), 5)
        self.assertIn("worst_loss_usd", r)
        self.assertEqual(self.lines()[-1]["result"]["state"], "dry_run")

    def test_api_error_midway_cancels_rest_and_journals(self):
        c = LadderClient(fail_on=3, fail_exc=RuntimeError("boom"))
        r = self.run_ladder(c)
        self.assertFalse(r["ok"])
        self.assertIn(("cancel_by_label", "cotrade"), c.calls)
        self.assertEqual(self.lines()[-1]["result"]["state"], "ladder_failed")
        self.assertFalse(self.halt.exists())

    def test_unknown_state_midway_halts_and_blocks_new_ladder(self):
        c = LadderClient(fail_on=2, fail_exc=do.OrderStateUnknown("private/buy", "cotrade", "timeout"))
        r = self.run_ladder(c)
        self.assertFalse(r["ok"])
        self.assertEqual(self.lines()[-1]["result"]["state"], "unknown")
        self.assertTrue(self.halt.exists())
        self.halt.unlink()
        c2 = LadderClient()
        self.assertFalse(self.run_ladder(c2)["ok"])
        self.assertNotIn("place", c2.names())

    def test_cancel_failure_midway_halts_and_flattens(self):
        c = LadderClient(fail_on=2, fail_exc=RuntimeError("boom"))

        def bad_cancel(token, label, currency="BTC"):
            raise RuntimeError("cancel down")
        c.cancel_by_label = bad_cancel
        r = self.run_ladder(c)
        self.assertFalse(r["ok"])
        self.assertTrue(self.halt.exists())
        self.assertIn("close_position", c.names())


class TestLadderPending(Base):
    def run_ladder(self, client, **kw):
        args = dict(said=LSAID, side="sell", frm=110500.0, steps=5, x=100, stop=112000.0, to=111500.0,
                    client=client, account=None, journal_dir=self.jdir, halt_path=self.halt,
                    halt_daily_loss_path=self.halt_dl, env="test")
        args.update(kw)
        return cotrade.place_ladder(**args)

    def test_pending_record_written_before_first_rung(self):
        seen = {}

        class C(LadderClient):
            def place(s, *a, **k):
                seen.setdefault("lines", [x["result"]["state"] for x in self.lines()])
                return super().place(*a, **k)
        self.assertTrue(self.run_ladder(C())["ok"])
        self.assertEqual(seen["lines"], ["ladder_pending"])

    def _crash_after_two(self):
        class Crash(BaseException):
            pass
        c = LadderClient(fail_on=3, fail_exc=Crash())
        with self.assertRaises(Crash):
            self.run_ladder(c)
        c.fail_on = None
        return c

    def test_crash_mid_ladder_blocks_next_ladder_and_sync_cancels_orphans(self):
        c = self._crash_after_two()
        self.assertEqual(len(c.orders), 2)
        r = self.run_ladder(c)
        self.assertFalse(r["ok"])
        self.assertEqual(len([x for x in c.calls if x[0] == "place"]), 3)   # no new rung
        s = cotrade.ladder_sync(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt, env="test")
        self.assertFalse(s["ok"])
        self.assertTrue(s.get("orphan"))
        self.assertIn(("cancel_by_label", "cotrade"), c.calls)
        self.assertEqual(self.lines()[-1]["result"]["state"], "ladder_failed")
        c.orders = []
        self.assertTrue(self.run_ladder(c)["ok"])   # reconciled: a new ladder may go

    def test_orphan_with_fill_gets_a_stop(self):
        c = self._crash_after_two()
        c.fill_rung(1)
        s = cotrade.ladder_sync(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt, env="test")
        self.assertFalse(s["ok"])
        self.assertIn("stop_market", c.names())

    def test_placed_ladder_blocks_journal_even_after_stop_and_empty_book(self):
        c = LadderClient()
        self.assertTrue(self.run_ladder(c)["ok"])
        c.fill_rung(1)
        cotrade.ladder_sync(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt, env="test")
        c.orders = []
        c.position = 0     # exchange looks clean, journal still says the ladder is live
        r = self.run_ladder(c)
        self.assertFalse(r["ok"])
        self.assertTrue(any("journal" in x for x in r["reasons"]))


class TestLadderSync(Base):
    def setUp(self):
        super().setUp()
        self.c = LadderClient()
        args = dict(said=LSAID, side="sell", frm=110500.0, steps=5, x=100, stop=112000.0, to=111500.0,
                    client=self.c, account=None, journal_dir=self.jdir, halt_path=self.halt,
                    halt_daily_loss_path=self.halt_dl, env="test")
        self.assertTrue(cotrade.place_ladder(**args)["ok"])

    def sync(self):
        return cotrade.ladder_sync(client=self.c, account=None, journal_dir=self.jdir,
                                   halt_path=self.halt, env="test")

    def stops(self):
        return [o for o in self.c.orders if o.get("order_type") == "stop_market"]

    def test_nothing_filled_waits_no_stop_no_cancel(self):
        r = self.sync()
        self.assertTrue(r["ok"])
        self.assertTrue(r.get("waiting"))
        self.assertNotIn("stop_market", self.c.names())
        self.assertNotIn("cancel_by_label", self.c.names())

    def test_stop_covers_filled_size_and_follows_fills(self):
        self.c.fill_rung(1)
        self.assertTrue(self.sync()["ok"])
        self.assertEqual([(o["amount"], o["trigger_price"]) for o in self.stops()], [(100, 112000.0)])
        self.c.fill_rung(2)
        self.assertTrue(self.sync()["ok"])
        self.assertEqual([(o["amount"], o["trigger_price"]) for o in self.stops()], [(300, 112000.0)])
        self.assertTrue(self.stops()[0]["reduce_only"])

    def test_stop_hit_cancels_unfilled_rungs(self):
        self.c.fill_rung(1)
        self.c.fill_rung(2)
        self.sync()
        self.c.hit_stop()
        r = self.sync()
        self.assertTrue(r["ok"])
        self.assertIn(("cancel_by_label", "cotrade"), self.c.calls)
        self.assertEqual(self.lines()[-1]["result"]["state"], "ladder_stopped")
        n = len(self.c.calls)
        self.assertTrue(self.sync().get("done"))     # idempotent
        self.assertEqual(len(self.c.calls), n)

    def test_restart_mid_ladder_rebuilds_from_exchange_and_journal(self):
        self.c.fill_rung(1)
        self.sync()
        self.c.fill_rung(2)
        # "restart": a brand-new call with nothing in memory, only the journal dir and the exchange
        r = cotrade.ladder_sync(client=self.c, account=None, journal_dir=self.jdir, halt_path=self.halt, env="test")
        self.assertTrue(r["ok"])
        self.assertEqual([o["amount"] for o in self.stops()], [300])

    def test_position_unreadable_fails_closed(self):
        self.c.pos_exc = RuntimeError("api down")
        r = self.sync()
        self.assertFalse(r["ok"])
        self.assertTrue(self.halt.exists())
        self.assertIn(("cancel_by_label", "cotrade"), self.c.calls)

    def test_flat_without_a_stop_is_not_a_stop_hit(self):
        # a non-trade balance move (deposit / funding) changes nothing in position or orders: no cancel
        r = self.sync()
        self.assertTrue(r.get("waiting"))
        self.assertEqual(len(self.c.orders), 5)

    def test_stop_failure_flattens_and_halts(self):
        self.c.fill_rung(1)
        self.c.stop_exc = RuntimeError("stop rejected")
        r = self.sync()
        self.assertFalse(r["ok"])
        self.assertTrue(self.halt.exists())
        self.assertIn("close_position", self.c.names())

    def test_dead_ladder_terminal_after_unreadable(self):
        self.c.pos_exc = RuntimeError("api down")
        self.sync()
        self.c.pos_exc = None
        r = self.sync()
        self.assertTrue(r.get("done"))
        self.assertEqual(self.lines()[-1]["result"]["state"], "ladder_failed")

    def test_dead_ladder_terminal_after_stop_failure(self):
        self.c.fill_rung(1)
        self.c.stop_exc = RuntimeError("stop rejected")
        self.sync()
        self.c.stop_exc = None
        self.assertTrue(self.sync().get("done"))
        self.assertIn("ladder_failed", [x["result"].get("state") for x in self.lines()])

    def test_mainnet_refused(self):
        r = cotrade.ladder_sync(client=self.c, account=None, journal_dir=self.jdir, halt_path=self.halt, env="live")
        self.assertFalse(r["ok"])


class TestLadderCli(unittest.TestCase):
    def test_dry_run_cli_prints_table(self):
        import contextlib
        import io
        import os
        with tempfile.TemporaryDirectory() as d:
            os.environ["COTRADE_JOURNAL_DIR"] = d
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    rc = cotrade.main(["ladder", "--said", LSAID, "--side", "sell", "--from", "110500",
                                       "--to", "111500", "--steps", "5", "--x", "100", "--stop", "112000",
                                       "--dry-run"])
            finally:
                os.environ.pop("COTRADE_JOURNAL_DIR", None)
        out = json.loads(buf.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual([r["amount"] for r in out["rungs"]], [100, 200, 300, 600, 1200])


if __name__ == "__main__":
    unittest.main()
