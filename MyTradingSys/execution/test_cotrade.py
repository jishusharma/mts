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


if __name__ == "__main__":
    unittest.main()
