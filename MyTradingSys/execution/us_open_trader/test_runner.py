"""test_runner.py - runner.py (DESIGN v1 section 6 as replaced by V2-8, V2-2 slippage guard, V2-4 parity).
Offline: fake clock, fake sleep, fake klines, fake price feed, fake cotrade module and fake Deribit client.
Expectations are hand-computed from the rule text (numbers in the comments), never read back from runner.py."""
import calendar
import copy
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine  # noqa: E402
import runner  # noqa: E402

ARM = calendar.timegm((2026, 11, 13, 13, 35, 0)) * 1000
MIN = 60000
FLAT_MIN = 15          # test plans flat at 13:50 = ARM + 15 minutes
BASIS = 10.0           # deribit mark = ref close + 10 in the fakes
FILL_SLIP = 5.0        # the fake exchange fills 5 above the mark
POLL = 20              # seconds between polls in the tests


class Crash(BaseException):
    """Simulated process death (not an Exception: the runner must not swallow it)."""


def bar(i, o, h, l, c):
    return {"t": ARM + i * MIN, "o": float(o), "h": float(h), "l": float(l), "c": float(c)}


def quiet(i, px=69700):
    return bar(i, px, px, px, px)


def series(spec, upto=FLAT_MIN + 2, filler=69700):
    """spec: {minute index: (o, h, l, c)}; every other minute is a flat filler bar."""
    return [bar(i, *spec[i]) if i in spec else quiet(i, filler) for i in range(upto)]


def order(oid, side, kind, trigger, sd=250, td=360, arm_after=None):
    return {"id": oid, "side": side, "kind": kind, "trigger": trigger, "stop_dist": sd, "target_dist": td,
            "level": "lvl " + oid, "confluence": ["t:" + oid], "arm_after": arm_after}


def make_plan(orders, **kw):
    p = {"day": "2026-11-13", "frozen_utc": "2026-11-13T13:10Z", "ref_feed": "binance_spot_BTCUSDT",
         "instrument": "BTC-PERPETUAL", "arm_utc": "13:35", "flat_utc": "13:50", "max_entries": 3,
         "amount_usd": 5000, "leverage": 50, "be_at_r": 1.0, "fee_per_side": 0.0005, "orders": orders}
    p.update(kw)
    return p


class Clock:
    def __init__(self, t_ms):
        self.t = t_ms / 1000.0
        self.hooks = []   # (ts_s, fn) run once when the clock passes ts_s

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s
        for h in list(self.hooks):
            if self.t >= h[0]:
                self.hooks.remove(h)
                h[1]()


class World:
    """The fake outside: bars, a fake exchange position, and the call log of every cotrade / client call."""
    def __init__(self, bars, clock):
        self.bars, self.clock = bars, clock
        self.size, self.avg, self.liq = 0, None, "auto"
        self.calls = []
        self.client_calls = []
        self.user_trades = []
        self.place_results = []        # scripted place_order results (popped first)
        self.stop_results = []
        self.close_results = []
        self.fill_px = None            # overrides the default fill (mark + FILL_SLIP)
        self.mark_fails = False
        self.price_fails = []          # list of (from_s, to_s) windows where price_fn raises
        self.kline_fails = []          # same for kline_fn
        self.records = []              # fake cotrade journal records
        self.state_seen_at_place = None
        self.state_dir = None
        self.order_avg = {}
        self.n_orders = 0
        self.ensure_times = []

    # ---- views
    def now_ms(self):
        return int(round(self.clock() * 1000))

    def last_closed(self):
        done = [b for b in self.bars if b["t"] + MIN <= self.now_ms()]
        return done[-1] if done else None

    def ref(self):
        b = self.last_closed()
        return b["c"] if b else self.bars[0]["o"]

    def mark(self):
        return self.ref() + BASIS

    def in_window(self, windows):
        return any(a <= self.clock() < b for a, b in windows)

    # ---- injected feeds
    def price_fn(self):
        if self.in_window(self.price_fails):
            raise RuntimeError("price feed down")
        return self.ref(), self.clock()

    def kline_fn(self, symbol, start_ms, end_ms):
        if self.in_window(self.kline_fails):
            raise RuntimeError("kline feed down")
        return [dict(b) for b in self.bars if start_ms <= b["t"] <= end_ms]

    def calls_named(self, name):
        return [c for c in self.calls if c[0] == name]


class FakeCot:
    """Stands in for the cotrade module: same function names, keyword arguments."""
    def __init__(self, w):
        self.w = w

    def journal_dir(self):
        return Path("fake-journal")

    def _records(self, jdir):
        return list(self.w.records)

    def place_order(self, said, side, order_type, price, amount, stop, **kw):
        w = self.w
        w.calls.append(("place_order", dict(said=said, side=side, order_type=order_type, price=price,
                                            amount=amount, stop=stop, **kw)))
        if w.state_dir is not None:   # write-ahead probe: what is on disk at the moment of the call
            p = Path(w.state_dir) / "state_2026-11-13.json"
            w.state_seen_at_place = json.loads(p.read_text()) if p.exists() else None
        if w.place_results:
            r = w.place_results.pop(0)
            if isinstance(r, BaseException):
                raise r
            if r.get("_fill"):
                self._fill(side, amount)
            return r
        self._fill(side, amount)
        return {"ok": True, "order_id": "O%d" % w.n_orders, "stop_pending": False}

    def _fill(self, side, amount):
        w = self.w
        w.n_orders += 1
        w.size = amount if side == "buy" else -amount
        w.avg = w.fill_px if w.fill_px is not None else w.mark() + FILL_SLIP
        w.order_avg["O%d" % (w.n_orders - 1)] = w.avg

    def ensure_stop(self, **kw):
        self.w.calls.append(("ensure_stop", kw))
        self.w.ensure_times.append(self.w.now_ms())
        if self.w.stop_results:
            return self.w.stop_results.pop(0)
        return {"ok": True, "stop_pending": False}

    def kill(self, **kw):
        self.w.calls.append(("kill", kw))
        self.w.size = 0
        return {"ok": True, "errors": [], "slots": ["main"]}

    def close_trade(self, **kw):
        w = self.w
        w.calls.append(("close_trade", kw))
        if w.close_results:
            r = w.close_results.pop(0)
            if r.get("ok"):
                w.size = 0
            return r
        w.size = 0
        return {"ok": True, "closed_size": 0, "was_flat": False}


class FakeClient:
    """Fake Deribit client: only the reads the runner is allowed. Anything else fails the test."""
    def __init__(self, w, env="test"):
        self.w = w
        self.env = env

    def active_env(self):   # not an exchange call: the module-level environment switch
        return self.env

    def authenticate(self, account=None):
        self.w.client_calls.append("authenticate")
        return "tok"

    def get_ticker(self, instrument_name="BTC-PERPETUAL"):
        self.w.client_calls.append("get_ticker")
        if self.w.mark_fails:
            raise RuntimeError("ticker down")
        return {"mark_price": self.w.mark()}

    def get_position(self, token, instrument_name="BTC-PERPETUAL"):
        self.w.client_calls.append("get_position")
        w = self.w
        liq = w.liq
        if liq == "auto":
            liq = (w.avg * 0.5 if w.size > 0 else w.avg * 1.5) if w.size else None
        return {"size": w.size, "average_price": w.avg, "estimated_liquidation_price": liq}

    def get_order_state(self, token, order_id):
        self.w.client_calls.append("get_order_state")
        return {"average_price": self.w.order_avg.get(order_id), "order_id": order_id}

    def get_user_trades_by_instrument_and_time(self, token, instrument_name, start_ms, end_ms, count=100):
        self.w.client_calls.append("get_user_trades_by_instrument_and_time")
        return list(self.w.user_trades)

    def __getattr__(self, name):
        raise AssertionError("runner touched client.%s (not an allowed read)" % name)


class RecordingClient:
    """Every attribute access is a failure: used to prove paper mode makes zero client calls."""
    def __getattr__(self, name):
        raise AssertionError("paper mode touched client.%s" % name)


def placed_record(ts_ms, side="buy", amount=5000, said="buy the breakout", state="placed"):
    """A fake cotrade journal row for a place made by this run."""
    return {"ts_utc": datetime.fromtimestamp(ts_ms / 1000, timezone.utc).isoformat(), "said": said,
            "action": {"kind": "place", "side": side, "amount_usd": amount}, "result": {"state": state, "order_id": "O9"}}


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.dir = Path(self._td.name)
        self.state_dir = self.dir / "state"
        self.plan_path = self.dir / "plan.json"

    def tearDown(self):
        self._td.cleanup()

    def start(self, plan, bars, clock_ms=None):
        self.plan = plan
        self.plan_path.write_text(json.dumps(plan))
        self.clock = Clock(ARM - MIN if clock_ms is None else clock_ms)
        self.w = World(bars, self.clock)
        self.w.state_dir = self.state_dir
        self.cot = FakeCot(self.w)
        self.client = FakeClient(self.w)
        return self.w

    def go(self, mode="testnet", said="buy the breakout", **over):
        kw = dict(mode=mode, poll_secs=POLL, clock=self.clock, sleep=self.clock.sleep, price_fn=self.w.price_fn,
                  kline_fn=self.w.kline_fn, client=self.client, cot=self.cot, said=said, account=None,
                  journal_dir=self.dir / "journal", halt_path=self.dir / "HALT_UNUSED", env="test",
                  state_dir=self.state_dir, halt_paths=[self.dir / "HALT"], max_polls=3000)
        kw.update(over)
        return runner.run(self.plan_path, **kw)

    def state_file(self):
        return json.loads((self.state_dir / "state_2026-11-13.json").read_text())


A_ONLY = make_plan([order("A", "buy", "breakout", 69620)])
# minute 1 touches A (h 69640 >= 69620), closes 69630; ref 69630, mark 69640, basis 10, fill 69645 -> ref entry 69635
M1 = (69520, 69640, 69510, 69630)
M0 = (69500, 69550, 69480, 69520)


def s1_bars(extra=None):
    spec = {0: M0, 1: M1, 2: (69630, 69700, 69600, 69690), 3: (69690, 69900, 69680, 69880),
            4: (69880, 70000, 69870, 69990)}
    spec.update(extra or {})
    return series(spec)


class TestLong(Base):
    def test_enter_fill_be_target_close(self):
        w = self.start(A_ONLY, s1_bars())
        res = self.go()
        self.assertTrue(res["ok"], res)
        po = w.calls_named("place_order")
        self.assertEqual(len(po), 1)
        a = po[0][1]
        # said verbatim, market order, no price, amount from the plan, stop = mark 69640 - stop_dist 250
        self.assertEqual((a["said"], a["side"], a["order_type"], a["price"], a["amount"], a["stop"]),
                         ("buy the breakout", "buy", "market", None, 5000, 69390.0))
        self.assertEqual(a["env"], "test")
        # engine entry = exchange fill 69645 - basis 10 = 69635; BE level = 69635 + 250 = 69885 (m3 high 69900)
        # BE stop sent to the exchange = engine stop 69635 + basis 10
        es = w.calls_named("ensure_stop")
        self.assertEqual(len(es), 1)
        self.assertEqual(es[0][1]["stop_px"], 69645.0)
        # target = 69635 + 360 = 69995 (m4 high 70000): exit at the target
        t = res["trades"]
        self.assertEqual(len(t), 1)
        self.assertEqual((t[0]["entry"], t[0]["exit"], t[0]["exit_reason"], t[0]["mode"]),
                         (69635.0, 69995.0, "target", "testnet"))
        self.assertAlmostEqual(t[0]["r_gross"], 360 / 250.0, places=9)                       # 1.44
        self.assertAlmostEqual(t[0]["r_net"], 1.44 - 2 * 0.0005 * 69635 / 250.0, places=9)   # 1.16146
        self.assertTrue(t[0]["stop_moved"])
        # close_trade after the target AND unconditionally at flat time
        reasons = [c[1]["reason"] for c in w.calls_named("close_trade")]
        self.assertEqual(reasons, ["target", "flat_time"])

    def test_only_closed_bars_step_the_engine(self):
        # the m1 bar is still open until 13:37:00: no entry at 13:36:40, entry once it has closed
        w = self.start(A_ONLY, s1_bars())
        self.clock.hooks.append((ARM / 1000 + 2 * 60 - 1, lambda: self._assert_no_place()))
        self.go()
        self.assertEqual(len(w.calls_named("place_order")), 1)

    def _assert_no_place(self):
        self.assertEqual(self.w.calls_named("place_order"), [])

    def test_state_file_atomic_temp_then_replace(self):
        self.start(A_ONLY, s1_bars())
        seen = []
        real = os.replace

        def spy(src, dst):
            seen.append((str(src), str(dst)))
            return real(src, dst)
        runner.os.replace = spy
        try:
            self.go()
        finally:
            runner.os.replace = real
        self.assertGreater(len(seen), 3)
        for src, dst in seen:
            self.assertNotEqual(src, dst)
            self.assertEqual(os.path.dirname(src), os.path.dirname(dst))
            self.assertTrue(dst.endswith("state_2026-11-13.json"))
        self.assertEqual([p.name for p in self.state_dir.iterdir()], ["state_2026-11-13.json"])  # no temp left

    def test_state_records_mode_and_trades(self):
        self.start(A_ONLY, s1_bars())
        self.go()
        s = self.state_file()
        self.assertEqual(s["engine"]["mode"], "testnet")
        self.assertTrue(s["engine"]["live"])
        self.assertTrue(s["engine"]["done"])
        self.assertEqual(len(s["engine"]["trades"]), 1)


class TestEntryGuards(Base):
    def test_slippage_guard_refuses_and_places_nothing(self):
        # ref price at processing time 69720; trigger 69620; 100 beyond > 0.25 * 250 = 62.5 -> reject
        w = self.start(A_ONLY, series({0: M0, 1: (69520, 69650, 69510, 69720)}))
        res = self.go()
        self.assertEqual(w.calls_named("place_order"), [])
        self.assertEqual(res["trades"], [])
        ev = [e for e in res["events"] if e["type"] == "cancel" and e["order_id"] == "A"]
        self.assertEqual(len(ev), 1)
        self.assertIn("slippage", ev[0]["reason"])

    def test_slippage_guard_exact_boundary_allows(self):
        # beyond = 62.5 exactly (ref 69682.5): not MORE than 0.25*stop_dist -> allowed
        w = self.start(A_ONLY, series({0: M0, 1: (69520, 69650, 69510, 69682.5)}))
        self.go()
        self.assertEqual(len(w.calls_named("place_order")), 1)

    def test_sell_side_slippage(self):
        p = make_plan([order("B", "sell", "breakout", 68490)])
        # ref 68400: 90 beyond the sell trigger 68490 -> refused
        w = self.start(p, series({0: (69000, 69010, 68990, 69000), 1: (68600, 68610, 68480, 68400)}))
        self.go()
        self.assertEqual(w.calls_named("place_order"), [])

    def test_cotrade_refusal_cancels_order_no_retry_no_more_entries(self):
        p = make_plan([order("A", "buy", "breakout", 69620), order("B", "sell", "breakout", 68490)])
        spec = {0: M0, 1: M1, 5: (69690, 69700, 68480, 68500)}   # m5 would trigger B
        w = self.start(p, series(spec))
        w.place_results = [{"ok": False, "reasons": ["HALT: manual halt file present"]}]
        res = self.go()
        self.assertEqual(len(w.calls_named("place_order")), 1)          # A once, never retried, B never tried
        cancels = {e["order_id"]: e["reason"] for e in res["events"] if e["type"] == "cancel"}
        self.assertIn("A", cancels)
        self.assertEqual(res["trades"], [])
        self.assertTrue(res["halted_reason"].startswith("cotrade"), res["halted_reason"])
        self.assertEqual(self.state_file()["runner"]["halted_reason"], res["halted_reason"])
        self.assertEqual(self.state_file()["engine"]["status"]["A"], "cancelled")

    def test_refused_place_with_position_left_is_closed(self):
        w = self.start(A_ONLY, s1_bars())
        w.place_results = [{"ok": False, "reasons": ["stop failed"], "_fill": True}]   # fills, then reports failure
        res = self.go()
        self.assertEqual(res["trades"], [])
        self.assertEqual(w.calls_named("close_trade")[0][1]["reason"], "place_failed")
        self.assertEqual(w.size, 0)

    def test_place_exception_is_a_refusal_not_a_crash(self):
        w = self.start(A_ONLY, s1_bars())
        w.place_results = [RuntimeError("boom")]
        res = self.go()
        self.assertTrue(res["ok"])
        self.assertEqual(len(w.calls_named("place_order")), 1)
        self.assertTrue(res["halted_reason"].startswith("cotrade"))

    def test_halt_file_blocks_entries(self):
        w = self.start(A_ONLY, s1_bars())
        (self.dir / "HALT").write_text("x")
        res = self.go()
        self.assertEqual(w.calls_named("place_order"), [])
        self.assertTrue(res["halted_reason"].startswith("halt_file"))
        self.assertEqual(w.calls_named("close_trade"), [])   # F4: this run placed nothing, so it closes nothing

    def test_halt_file_midway_keeps_managing_the_open_position(self):
        w = self.start(A_ONLY, s1_bars())
        self.clock.hooks.append((ARM / 1000 + 2 * 60 + 30, lambda: (self.dir / "HALT").write_text("x")))
        res = self.go()
        self.assertEqual(len(w.calls_named("place_order")), 1)
        self.assertEqual(res["trades"][0]["exit_reason"], "target")   # BE stop move + target exit still happen
        self.assertEqual(len(w.calls_named("ensure_stop")), 1)
        self.assertTrue(res["halted_reason"].startswith("halt_file"))

    def test_stale_price_stops_entries(self):
        w = self.start(A_ONLY, s1_bars())
        w.price_fails = [(ARM / 1000 + 30, ARM / 1000 + 3600)]   # feed dies after 13:35:30, never recovers
        res = self.go()
        self.assertEqual(w.calls_named("place_order"), [])
        self.assertTrue(res["halted_reason"].startswith("stale_price"), res["halted_reason"])

    def test_old_timestamp_from_price_fn_is_stale(self):
        w = self.start(A_ONLY, s1_bars())
        w.price_fn = lambda: (w.ref(), w.clock() - 31)   # every reading is 31 s old
        res = self.go(price_fn=w.price_fn)
        self.assertEqual(w.calls_named("place_order"), [])
        self.assertTrue(res["halted_reason"].startswith("stale_price"))

    def test_one_failed_price_poll_is_not_stale(self):
        w = self.start(A_ONLY, s1_bars())
        w.price_fails = [(ARM / 1000 + 100, ARM / 1000 + 100 + POLL)]   # exactly one poll fails (20 s < 30 s)
        res = self.go()
        self.assertIsNone(res["halted_reason"])
        self.assertEqual(len(w.calls_named("place_order")), 1)

    def test_kline_outage_catches_up_when_it_recovers(self):
        w = self.start(A_ONLY, s1_bars())
        w.kline_fails = [(ARM / 1000 + 100, ARM / 1000 + 120)]   # one poll
        res = self.go()
        self.assertIsNone(res["halted_reason"])
        self.assertEqual(res["trades"][0]["exit_reason"], "target")

    def test_kline_outage_over_30s_halts_entries(self):
        w = self.start(A_ONLY, s1_bars())
        w.kline_fails = [(ARM / 1000 + 30, ARM / 1000 + 3600)]
        res = self.go()
        self.assertEqual(w.calls_named("place_order"), [])
        self.assertTrue(res["halted_reason"].startswith("stale_price"))

    def test_stale_basis_rejects_the_entry(self):
        # mark unreadable from 13:35:30 on: basis (measured 13:35:20) is older than 30 s when A triggers at 13:37:00
        w = self.start(A_ONLY, s1_bars())
        self.clock.hooks.append((ARM / 1000 + 30, lambda: setattr(w, "mark_fails", True)))
        res = self.go()
        self.assertEqual(w.calls_named("place_order"), [])
        self.assertEqual(self.state_file()["engine"]["status"]["A"], "cancelled")
        ev = [e for e in res["events"] if e["type"] == "cancel" and e["order_id"] == "A"]
        self.assertIn("basis", ev[0]["reason"])


class TestPosition(Base):
    def test_stop_hint_with_position_open_changes_nothing(self):
        # engine stop = 69635 - 250 = 69385; m2 low 69380 touches it. Live: hint only, still in position.
        w = self.start(A_ONLY, s1_bars({2: (69630, 69640, 69380, 69600), 3: (69600, 69640, 69590, 69620),
                                        4: (69620, 69640, 69590, 69620)}))
        snap = {}

        def grab():
            snap["state"] = json.dumps(self.state_file()["engine"], sort_keys=True)
        self.clock.hooks.append((ARM / 1000 + 4 * 60 + 5, grab))   # after m2 closed and was processed
        res = self.go()
        hints = [e for e in res["events"] if e["type"] == "stop_hint"]
        self.assertEqual(len(hints), 1)
        self.assertEqual((hints[0]["price"], hints[0]["reason"]), (69385.0, "stop"))
        eng = json.loads(snap["state"])
        self.assertIsNotNone(eng["position"])
        self.assertEqual(eng["trades"], [])
        # no exchange action for a hint: no ensure_stop, only the flat-time close at the end
        self.assertEqual(w.calls_named("ensure_stop"), [])
        self.assertEqual([c[1]["reason"] for c in w.calls_named("close_trade")], ["flat_time"])

    def test_server_stop_detected_flat_position(self):
        # exchange stop fills at 69380 (ref 69370) at 13:39:30 while the engine only saw a hint
        w = self.start(A_ONLY, s1_bars({2: (69630, 69640, 69380, 69600), 3: (69600, 69640, 69590, 69620),
                                        4: (69620, 69640, 69590, 69620)}))

        def stop_fills():
            w.size = 0
            w.user_trades = [{"price": 69380.0, "amount": 5000, "reduce_only": True, "direction": "sell",
                              "timestamp": w.now_ms()}]
        self.clock.hooks.append((ARM / 1000 + 4 * 60 + 30, stop_fills))
        res = self.go()
        t = res["trades"]
        self.assertEqual(len(t), 1)
        self.assertEqual((t[0]["exit"], t[0]["exit_reason"]), (69370.0, "stop"))   # 69380 - basis 10
        self.assertAlmostEqual(t[0]["r_gross"], (69370 - 69635) / 250.0, places=9)
        self.assertEqual(w.calls_named("close_trade")[0][1]["reason"], "stop")      # cleanup labelled leftovers

    def test_server_stop_without_matching_trade_flags_the_row(self):
        w = self.start(A_ONLY, s1_bars({2: (69630, 69640, 69380, 69600), 3: (69600, 69640, 69590, 69620),
                                        4: (69620, 69640, 69590, 69620)}))
        self.clock.hooks.append((ARM / 1000 + 4 * 60 + 30, lambda: setattr(w, "size", 0)))
        res = self.go()
        t = res["trades"][0]
        self.assertFalse(t["exit_price_known"])
        self.assertIsNone(t["exit"])            # never invented
        self.assertIsNone(t["r_gross"])
        self.assertEqual(t["exit_reason"], "stop")

    def test_be_close_when_stop_would_sit_on_the_wrong_side_of_the_mark(self):
        # m3 reaches +1R (high 69900) but closes 69600: mark 69610; BE trigger 69645 is above it -> be_close
        w = self.start(A_ONLY, s1_bars({3: (69690, 69900, 69590, 69600), 4: (69600, 69610, 69590, 69600)}))
        w.user_trades = [{"price": 69612.0, "amount": 5000, "reduce_only": True, "direction": "sell",
                          "timestamp": ARM + 5 * MIN}]
        res = self.go()
        self.assertEqual(w.calls_named("ensure_stop"), [])
        self.assertEqual(w.calls_named("close_trade")[0][1]["reason"], "be_close")
        t = res["trades"][0]
        self.assertEqual((t["exit"], t["exit_reason"]), (69602.0, "be_close"))     # 69612 - 10
        self.assertAlmostEqual(t["r_gross"], (69602 - 69635) / 250.0, places=9)

    def test_stale_basis_defers_the_stop_move_then_applies_it(self):
        w = self.start(A_ONLY, s1_bars({4: (69880, 69900, 69870, 69890)}))   # no target: position stays open
        # mark dies 13:37:30 (after entry), is back at 13:41:00 (after the BE bar m3 was processed at 13:39:00)
        # (the ref price feed is what re-measures the basis: while it is down the mark is readable but the basis is old)
        w.price_fails = [(ARM / 1000 + 2 * 60 + 30, ARM / 1000 + 6 * 60)]
        self.go()
        es = w.calls_named("ensure_stop")
        self.assertEqual(len(es), 1)                                  # applied once, after the basis was fresh again
        self.assertEqual(es[0][1]["stop_px"], 69645.0)
        self.assertGreaterEqual(w.ensure_times[0], ARM + 6 * MIN)    # not before the mark (basis) came back

    def test_ensure_stop_failure_blocks_new_entries(self):
        p = make_plan([order("A", "buy", "breakout", 69620), order("B", "sell", "breakout", 68490)])
        w = self.start(p, s1_bars({6: (69690, 69700, 68480, 68500)}))
        w.stop_results = [{"ok": False, "reasons": ["stop failed, account flattened and HALT written"]}]
        res = self.go()
        self.assertTrue(res["halted_reason"].startswith("cotrade"))
        self.assertEqual(len(w.calls_named("place_order")), 1)   # B never placed

    def test_liquidation_check_too_close_closes_the_trade(self):
        # long, exchange stop 69390; liq 69000 -> distance 390 < 2 * 250 = 500 -> close, no new entries
        w = self.start(A_ONLY, s1_bars())
        w.liq = 69000.0
        res = self.go()
        self.assertEqual(w.calls_named("close_trade")[0][1]["reason"], "liq_check")
        self.assertEqual(res["trades"][0]["exit_reason"], "liq_check")
        self.assertTrue(res["halted_reason"].startswith("liquidation"))
        self.assertEqual(w.calls_named("ensure_stop"), [])

    def test_liquidation_check_exact_distance_passes(self):
        w = self.start(A_ONLY, s1_bars())
        w.liq = 69390.0 - 500.0     # exactly 2 * stop_dist inside
        res = self.go()
        self.assertIsNone(res["halted_reason"])
        self.assertEqual(res["trades"][0]["exit_reason"], "target")

    def test_liquidation_unreadable_with_open_position_closes(self):
        w = self.start(A_ONLY, s1_bars())
        w.liq = None
        res = self.go()
        self.assertEqual(w.calls_named("close_trade")[0][1]["reason"], "liq_check")
        self.assertTrue(res["halted_reason"].startswith("liquidation"))

    def test_short_liquidation_side(self):
        p = make_plan([order("B", "sell", "breakout", 68490, td=370)])
        w = self.start(p, series({0: (69000, 69010, 68990, 69000), 1: (68600, 68610, 68480, 68470),
                                  2: (68470, 68480, 68460, 68470)}))
        w.liq = 69160.0
        res = self.go()
        # stop sent = mark 68480 + 250 = 68730; liq 69160 is 430 above -> < 500 -> close
        self.assertEqual(w.calls_named("place_order")[0][1]["stop"], 68730.0)
        self.assertEqual(w.calls_named("close_trade")[0][1]["reason"], "liq_check")
        self.assertTrue(res["halted_reason"].startswith("liquidation"))

    def test_flat_time_close_runs_when_this_run_placed_a_trade_in_the_journal(self):
        w = self.start(A_ONLY, series({}))
        w.records = [placed_record(ARM + MIN)]   # e.g. the state file was lost, the journal still knows
        res = self.go()
        self.assertEqual(res["trades"], [])
        self.assertEqual([c[1]["reason"] for c in w.calls_named("close_trade")], ["flat_time"])
        self.assertEqual(res["final_close"], "ok")

    def test_flat_time_close_skipped_when_this_run_placed_nothing(self):
        # F4: a position that is not ours (operator's own cotrade) at flat time is never closed by the runner
        w = self.start(A_ONLY, series({}))
        w.size, w.avg = -300, 69000.0
        res = self.go()
        self.assertEqual(w.calls_named("close_trade"), [])
        self.assertEqual(w.calls_named("ensure_stop"), [])
        self.assertEqual(w.size, -300)
        self.assertEqual(res["final_close"], "ok")

    def test_journal_place_by_other_said_or_before_arm_does_not_count(self):
        w = self.start(A_ONLY, series({}))
        w.records = [placed_record(ARM + MIN, said="the operator's own trade"), placed_record(ARM - 5 * MIN)]
        self.go()
        self.assertEqual(w.calls_named("close_trade"), [])

    def test_flat_time_close_failing_is_retried_until_flat_plus_10_min_then_halt_and_report(self):
        w = self.start(A_ONLY, series({}))
        w.records = [placed_record(ARM + MIN)]
        fail = {"ok": False, "reasons": ["close failed, flatten attempted and HALT written"]}
        w.close_results = [dict(fail) for _ in range(500)]
        res = self.go()
        n = len(w.calls_named("close_trade"))
        self.assertGreaterEqual(n, 25)               # every 20 s poll for 10 minutes (F6), not 3 tries
        self.assertEqual(res["final_close"], "failed")
        self.assertTrue(res["ok"])
        self.assertTrue((self.dir / "HALT_UNUSED").exists())   # HALT written through the cotrade halt path
        self.assertIn("final_close_failed", (self.dir / "HALT_UNUSED").read_text())
        self.assertGreaterEqual(self.clock() * 1000, ARM + FLAT_MIN * MIN + 10 * MIN)

    def test_flat_time_close_fails_once_then_succeeds(self):
        w = self.start(A_ONLY, series({}))
        w.records = [placed_record(ARM + MIN)]
        w.close_results = [{"ok": False, "reasons": ["x"]}]
        res = self.go()
        self.assertEqual(len(w.calls_named("close_trade")), 2)
        self.assertEqual(res["final_close"], "ok")

    def test_open_position_at_flat_time_is_time_exit_and_closed(self):
        w = self.start(A_ONLY, s1_bars({4: (69880, 69890, 69870, 69880), 5: (69880, 69890, 69870, 69880)}))
        res = self.go()
        t = res["trades"][0]
        self.assertEqual(t["exit_reason"], "time")
        self.assertEqual(t["exit"], 69700.0)    # flat bar (13:50) is a filler bar opening 69700
        self.assertEqual(w.calls_named("close_trade")[-1][1]["reason"], "flat_time")


class TestRestart(Base):
    def test_restart_mid_position_resumes_without_re_entering(self):
        w = self.start(A_ONLY, s1_bars())

        def die():
            raise Crash()
        self.clock.hooks.append((ARM / 1000 + 3 * 60 + 5, die))     # position open, BE not yet moved
        with self.assertRaises(Crash):
            self.go()
        self.assertEqual(len(w.calls_named("place_order")), 1)
        saved = self.state_file()
        self.assertIsNotNone(saved["engine"]["position"])
        res = self.go()                                            # restart: same state dir, same exchange
        self.assertEqual(len(w.calls_named("place_order")), 1)       # no second entry
        self.assertEqual(res["trades"][0]["exit_reason"], "target")
        self.assertIsNone(res["halted_reason"])

    def test_restart_with_corrupt_state_means_no_entries(self):
        w = self.start(A_ONLY, s1_bars(), clock_ms=ARM + 90 * 1000)   # mid-session start
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "state_2026-11-13.json").write_text('{"engine": {broken')
        res = self.go()
        self.assertEqual(w.calls_named("place_order"), [])
        self.assertTrue(res["halted_reason"].startswith("state_corrupt"), res["halted_reason"])
        self.assertTrue((self.state_dir / "state_2026-11-13.json.corrupt").exists())   # kept for the audit
        self.assertEqual(w.calls_named("close_trade"), [])   # F4: nothing in the journal says this run placed

    def test_missing_state_mid_session_means_no_entries(self):
        w = self.start(A_ONLY, s1_bars(), clock_ms=ARM + 3 * MIN)
        res = self.go()
        self.assertEqual(w.calls_named("place_order"), [])
        self.assertTrue(res["halted_reason"].startswith("state_missing"), res["halted_reason"])

    def test_missing_state_before_arm_is_a_normal_start(self):
        w = self.start(A_ONLY, s1_bars())
        res = self.go()
        self.assertIsNone(res["halted_reason"])
        self.assertEqual(len(w.calls_named("place_order")), 1)

    def test_exchange_position_without_state_halts_entries(self):
        w = self.start(A_ONLY, s1_bars())
        w.size, w.avg = 5000, 69000.0       # a position the runner never opened
        res = self.go()
        self.assertEqual(w.calls_named("place_order"), [])
        self.assertTrue(res["halted_reason"].startswith("position_without_state"))
        self.assertEqual(w.calls_named("close_trade"), [])   # F4: not ours (this run placed nothing): never touched
        self.assertEqual(w.calls_named("ensure_stop"), [])
        self.assertEqual(w.size, 5000)

    def test_exchange_position_without_state_after_our_place_gets_stop_then_close(self):
        # F1: the journal says we placed today, the engine lost it: stop first, then the close
        w = self.start(A_ONLY, series({}))
        w.records = [placed_record(ARM + MIN)]
        w.size, w.avg = 5000, 69000.0
        res = self.go()
        names = [c[0] for c in w.calls if c[0] in ("ensure_stop", "close_trade")]
        self.assertEqual(names[:2], ["ensure_stop", "close_trade"])
        self.assertEqual(w.calls_named("close_trade")[0][1]["reason"], "position_without_state")
        self.assertEqual(w.size, 0)

    def test_write_ahead_entering_is_on_disk_before_place_order(self):
        w = self.start(A_ONLY, s1_bars())
        self.go()
        seen = w.state_seen_at_place
        self.assertIsNotNone(seen)
        self.assertEqual(seen["engine"]["entering"]["order_id"], "A")
        self.assertEqual(seen["engine"]["status"]["A"], "entering")

    def _crash_in_place(self):
        w = self.start(A_ONLY, s1_bars())
        w.place_results = [Crash()]
        with self.assertRaises(Crash):
            self.go()
        self.assertEqual(self.state_file()["engine"]["entering"]["order_id"], "A")
        return w

    def test_restart_with_entering_and_position_on_exchange_fills(self):
        w = self._crash_in_place()
        # the order did go through before the process died: exchange holds the position, journal has the placed row
        w.size, w.avg = 5000, 69645.0
        w.records = [{"ts_utc": datetime.fromtimestamp(self.clock() - 1, timezone.utc).isoformat(),
                      "action": {"kind": "place", "side": "buy", "amount_usd": 5000},
                      "result": {"state": "placed", "order_id": "O9"}}]
        res = self.go()
        self.assertEqual(len(w.calls_named("place_order")), 1)       # not placed again
        t = res["trades"][0]
        self.assertEqual(t["entry"], 69635.0)                         # 69645 - basis 10
        self.assertEqual(t["exit_reason"], "target")
        self.assertTrue(w.calls_named("ensure_stop"))                 # stop verified/kept for the adopted position

    def test_restart_with_entering_and_flat_exchange_rejects(self):
        w = self._crash_in_place()
        res = self.go()
        self.assertEqual(len(w.calls_named("place_order")), 1)
        self.assertEqual(res["trades"], [])
        self.assertEqual(self.state_file()["engine"]["status"]["A"], "cancelled")
        self.assertIsNone(self.state_file()["engine"]["entering"])


class TestModes(Base):
    def test_paper_mode_makes_zero_client_calls(self):
        w = self.start(A_ONLY, s1_bars())
        res = self.go(mode="paper", client=RecordingClient(), cot=None, said=None)
        self.assertTrue(res["ok"], res)
        self.assertEqual(w.calls, [])
        self.assertEqual(w.client_calls, [])
        self.assertEqual(len(res["trades"]), 1)
        self.assertEqual(res["trades"][0]["mode"], "paper")

    def test_paper_fill_is_the_next_bars_open_and_a_simulated_stop_closes(self):
        # m1 touches A; paper fills at the open of m2 = 69630; stop = 69630 - 250 = 69380; m3 low 69370 -> sim stop
        w = self.start(A_ONLY, series({0: M0, 1: M1, 2: (69630, 69650, 69600, 69640), 3: (69640, 69650, 69370, 69400)}))
        res = self.go(mode="paper", client=RecordingClient(), cot=None, said=None)
        t = res["trades"][0]
        self.assertEqual((t["entry"], t["exit"], t["exit_reason"]), (69630.0, 69380.0, "stop"))
        self.assertAlmostEqual(t["r_gross"], -1.0, places=9)

    def test_testnet_without_said_refuses_with_zero_calls(self):
        w = self.start(A_ONLY, s1_bars())
        res = self.go(said=None)
        self.assertFalse(res["ok"])
        self.assertEqual(w.calls, [])
        self.assertEqual(w.client_calls, [])
        self.assertFalse((self.state_dir / "state_2026-11-13.json").exists())
        res2 = self.go(said="   ")
        self.assertFalse(res2["ok"])

    def test_unknown_mode_refused(self):
        self.start(A_ONLY, s1_bars())
        with self.assertRaises(ValueError):
            self.go(mode="mainnet")

    def test_non_testnet_env_is_refused_before_any_call(self):
        w = self.start(A_ONLY, s1_bars())
        res = self.go(env="live")
        self.assertFalse(res["ok"])
        self.assertEqual(w.calls, [])
        self.assertEqual(w.client_calls, [])

    def test_cli_testnet_without_said_exits_2_and_has_no_mainnet_flag(self):
        self.start(A_ONLY, s1_bars())
        self.assertEqual(runner.main([str(self.plan_path), "--mode", "testnet"]), 2)
        with self.assertRaises(SystemExit):
            runner.main([str(self.plan_path), "--mode", "testnet", "--mainnet"])
        self.assertNotIn("mainnet", " ".join(runner.build_parser().format_help().split()).replace("no mainnet", ""))

    def test_cli_defaults_to_paper(self):
        ns = runner.build_parser().parse_args(["plan.json"])
        self.assertEqual((ns.mode, ns.poll, ns.said), ("paper", 5, None))

    def test_runner_only_uses_allowed_client_reads(self):
        # FakeClient raises AssertionError for any attribute outside its read set; a whole session must pass.
        w = self.start(A_ONLY, s1_bars())
        self.go()
        self.assertTrue(set(w.client_calls) <= {"authenticate", "get_ticker", "get_position", "get_order_state",
                                                "get_user_trades_by_instrument_and_time"})


class TestParity(Base):
    def test_paper_runner_equals_replay_on_the_same_bars(self):
        p = make_plan([order("A", "buy", "breakout", 69620),
                       order("B", "sell", "breakout", 68490, td=370),
                       order("C", "sell", "fade", 69980, td=500, arm_after="A")])
        spec = {0: M0,
                1: (69520, 69640, 69510, 69630),        # touches A at 69620; entry bar low stays above the stop
                2: (69630, 69640, 69360, 69400),        # stop 69620 - 250 = 69370 -> A stopped at 69370
                3: (69900, 69990, 69880, 69960),        # opens on the approach side of C, high 69990 >= 69980 -> C
                4: (69960, 69970, 69470, 69500)}        # C target 69980 - 500 = 69480 -> exit
        bars = series(spec)
        self.start(p, bars)
        res = self.go(mode="paper", client=RecordingClient(), cot=None, said=None, paper_fill="trigger")
        rep = engine.replay(p, bars)["trades"]
        self.assertEqual([t["exit_reason"] for t in rep], ["stop", "target"])    # the scenario is what we think
        strip = lambda rows: [{k: v for k, v in r.items() if k != "mode"} for r in rows]   # noqa: E731
        self.assertEqual(strip(res["trades"]), strip(rep))
        self.assertEqual({t["mode"] for t in res["trades"]}, {"paper"})
        self.assertEqual({t["mode"] for t in rep}, {"replay"})


# ---------------------------------------------------------------------------------------------------------------
# Safety review fixes F1..F10 (US_OPEN_TRADER_SAFETY_REVIEW). Real cotrade + test_cotrade.FakeClient where marked.

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cotrade  # noqa: E402
import deribit_orders as do  # noqa: E402
from test_cotrade import FakeClient as CotFakeClient  # noqa: E402
from unittest import mock  # noqa: E402


class RealClient(CotFakeClient):
    """test_cotrade.FakeClient plus the reads the runner needs. Prices follow the World's bars."""
    def __init__(self, w, **kw):
        super().__init__(**kw)
        self.w = w
        self.avg = None
        self.fill_then_unknown = False

    def active_env(self):
        return "test"

    def get_ticker(self, instrument_name="BTC-PERPETUAL"):
        m = self.w.mark()
        return {"mark_price": m, "best_bid_price": m - 0.5, "best_ask_price": m + 0.5}

    def get_position(self, token, instrument_name="BTC-PERPETUAL"):
        liq = None
        if self.position and self.avg:
            liq = self.avg * (0.5 if self.position > 0 else 1.5)
        return {"size": self.position, "average_price": self.avg, "estimated_liquidation_price": liq}

    def get_order_state(self, token, order_id):
        return {"average_price": self.avg, "order_id": order_id}

    def cancel_by_label(self, token, label, currency="BTC"):
        self.orders = [o for o in self.orders if o.get("label") != label]
        return super().cancel_by_label(token, label, currency)

    def get_user_trades_by_instrument_and_time(self, token, instrument_name, start_ms, end_ms, count=100):
        return []

    def place(self, token, side, instrument_name, amount, order_type="limit", price=None, label=None,
              post_only=False, reduce_only=False):
        self.avg = self.w.mark() + FILL_SLIP
        if self.fill_then_unknown:   # the order fills at the exchange, the answer never arrives
            self.calls.append(("place", side, amount, order_type, price, label))
            self.position = amount if side == "buy" else -amount
            raise do.OrderStateUnknown("private/buy", label, "timeout")
        return super().place(token, side, instrument_name, amount, order_type, price, label, post_only, reduce_only)


class TestF1RealCotrade(Base):
    def go_real(self, rc, **over):
        kw = dict(cot=cotrade, client=rc, journal_dir=self.dir / "journal", halt_path=self.dir / "HALT_C",
                  secret_exists=lambda a: False)
        kw.update(over)
        return self.go(**kw)

    def states(self):
        out = []
        for p in sorted((self.dir / "journal").glob("*.jsonl")):
            out += [json.loads(x)["result"].get("state") for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
        return out

    def test_place_unknown_but_filled_gets_a_stop_then_is_closed(self):
        w = self.start(A_ONLY, s1_bars())
        rc = RealClient(w)
        rc.halt_path = self.dir / "HALT_C"
        rc.fill_then_unknown = True
        res = self.go_real(rc)
        self.assertEqual(rc.position, 0)                                  # not left open
        names = [c[0] for c in rc.calls if c[0] in ("stop_market", "close_position")]
        self.assertEqual(names[:2], ["stop_market", "close_position"])    # stop first, close second
        self.assertEqual(self.states()[:3], ["unknown", "stop_placed", "closed"])
        self.assertEqual(res["trades"], [])
        self.assertEqual(res["final_close"], "ok")

    def test_ensure_stop_failure_after_unknown_place_flattens_and_halts(self):
        w = self.start(A_ONLY, s1_bars())
        rc = RealClient(w, stop_exc=RuntimeError("stop api down"))
        rc.halt_path = self.dir / "HALT_C"
        rc.fill_then_unknown = True
        self.go_real(rc)
        self.assertEqual(rc.position, 0)
        self.assertTrue((self.dir / "HALT_C").exists())

    def test_close_refused_use_kill_is_killed_not_retried_forever(self):
        w = self.start(A_ONLY, series({0: M0, 1: M1}, filler=69630))
        rc = RealClient(w)
        rc.halt_path = self.dir / "HALT_C"
        jdir = self.dir / "journal"

        def poison():   # an unreconciled place state appears in the journal while the trade is open
            cotrade._append(jdir, {"said": "x", "heard": "x", "env": "test", "account": "main", "market": {},
                                   "action": {"kind": "place", "side": "buy", "amount_usd": 5000, "stop": 69000.0},
                                   "result": {"state": "unknown"}})
        self.clock.hooks.append((ARM / 1000 + 4 * 60, poison))
        res = self.go_real(rc)
        self.assertEqual(rc.position, 0)                       # kill flattened it, no endless refusals
        self.assertIn("killed", self.states())
        self.assertTrue((self.dir / "HALT_C").exists())
        self.assertEqual(res["final_close"], "ok")
        self.assertLess(self.states().count("refused"), 3)


class TestF1FakeCot(Base):
    USE_KILL = "journal: an order state is unknown - close_trade does not handle this: use kill"

    def test_refusal_with_use_kill_calls_kill_once(self):
        w = self.start(A_ONLY, s1_bars())
        w.close_results = [{"ok": False, "reasons": [self.USE_KILL]}]
        res = self.go()
        self.assertEqual(len(w.calls_named("kill")), 1)
        self.assertEqual(res["trades"][0]["exit_reason"], "target")   # the engine exit still booked
        self.assertEqual(w.size, 0)

    def test_foreign_slot_refusal_is_not_killed(self):
        w = self.start(A_ONLY, series({}))
        w.records = [placed_record(ARM + MIN)]
        text = "another co-trade slot holds a position (['jishu_1']): use kill"
        w.close_results = [{"ok": False, "reasons": [text]} for _ in range(500)]
        self.go()
        self.assertEqual(w.calls_named("kill"), [])

    def test_position_after_failed_place_is_secured_before_close(self):
        w = self.start(A_ONLY, s1_bars())
        w.place_results = [{"ok": False, "reasons": ["order state unknown"], "_fill": True}]
        self.go()
        order_ = [c[0] for c in w.calls if c[0] in ("ensure_stop", "close_trade")]
        self.assertEqual(order_[:2], ["ensure_stop", "close_trade"])
        self.assertIsNone(w.calls_named("ensure_stop")[0][1]["stop_px"])


class TestF3StaleEntryBars(Base):
    BARS = series({0: M0, 1: M1}, filler=69630)   # A triggers on minute 1; price sits at 69630 afterwards

    def _restart_at(self, minutes_after_arm):
        w = self.start(A_ONLY, self.BARS)
        self.go(max_polls=8)                       # processes minute 0 only, leaves state last_bar_t = ARM
        self.assertEqual(self.state_file()["runner"]["last_bar_t"], ARM)
        self.clock.t = (ARM + minutes_after_arm * MIN) / 1000.0
        res = self.go()
        return w, res

    def test_restart_after_flat_time_never_places(self):
        w, res = self._restart_at(FLAT_MIN + 1)     # state last_bar_t 13:35, restart 13:51 (flat 13:50)
        self.assertEqual(w.calls_named("place_order"), [])
        ev = [e for e in res["events"] if e["type"] == "cancel" and e["order_id"] == "A"]
        self.assertIn("after_flat_time", ev[0]["reason"])

    def test_restart_mid_session_with_old_entry_bar_never_places(self):
        w, res = self._restart_at(9)                # entry bar closed 13:37, now 13:44: 7 minutes old
        self.assertEqual(w.calls_named("place_order"), [])
        ev = [e for e in res["events"] if e["type"] == "cancel" and e["order_id"] == "A"]
        self.assertIn("stale_entry_bar", ev[0]["reason"])

    def test_entry_bar_two_polls_old_still_trades(self):
        w = self.start(A_ONLY, self.BARS)
        self.go()
        self.assertEqual(len(w.calls_named("place_order")), 1)


class TestF5AdverseGuards(Base):
    def test_price_already_reversed_against_the_trade_is_refused(self):
        # buy breakout 69620, stop_dist 250: ref 69550 is 70 below the trigger > 0.25 * 250 = 62.5
        w = self.start(A_ONLY, series({0: M0, 1: (69520, 69640, 69400, 69550)}, filler=69550))
        res = self.go()
        self.assertEqual(w.calls_named("place_order"), [])
        ev = [e for e in res["events"] if e["type"] == "cancel" and e["order_id"] == "A"]
        self.assertIn("adverse_guard", ev[0]["reason"])

    def test_entry_bar_that_already_reached_the_stop_level_is_refused(self):
        # low 69360 <= 69620 - 250 = 69370: replay would stop this entry in its own bar; price is back at the trigger
        w = self.start(A_ONLY, series({0: M0, 1: (69520, 69640, 69360, 69625)}, filler=69625))
        res = self.go()
        self.assertEqual(w.calls_named("place_order"), [])
        ev = [e for e in res["events"] if e["type"] == "cancel" and e["order_id"] == "A"]
        self.assertIn("entry_bar_hit_stop", ev[0]["reason"])

    def test_sell_side_mirror(self):
        p = make_plan([order("B", "sell", "breakout", 68490)])
        # high 68740 >= 68490 + 250: the entry bar reached the stop level
        w = self.start(p, series({0: (69000, 69010, 68990, 69000), 1: (68700, 68740, 68480, 68480)}, filler=68480))
        self.go()
        self.assertEqual(w.calls_named("place_order"), [])


class TestF6MainExitCode(Base):
    def _main(self, final_close, halted):
        self.start(A_ONLY, series({}))
        res = {"ok": True, "how": "finished", "trades": [], "halted_reason": halted, "final_close": final_close,
               "polls": 1}
        with mock.patch.object(runner, "run", return_value=res):
            return runner.main([str(self.plan_path), "--mode", "paper"])

    def test_ok_exits_zero(self):
        self.assertEqual(self._main("ok", None), 0)

    def test_failed_final_close_exits_nonzero(self):
        self.assertNotEqual(self._main("failed", "cotrade: close_trade failed"), 0)

    def test_position_without_state_exits_nonzero(self):
        self.assertNotEqual(self._main("ok", "position_without_state: exchange holds 5000"), 0)


class TestF7F8Settle(Base):
    def _crashed(self):
        w = self.start(A_ONLY, s1_bars())
        w.place_results = [Crash()]
        with self.assertRaises(Crash):
            self.go()
        self.assertEqual(self.state_file()["runner"]["intent"]["side"], "buy")
        return w

    def _rec(self, **kw):
        return placed_record(self.clock() * 1000 - 1000, **kw)

    def test_position_on_the_other_side_is_not_adopted(self):
        w = self._crashed()
        w.size, w.avg = -5000, 69645.0
        w.records = [self._rec()]
        res = self.go()
        self.assertEqual(res["trades"], [])
        self.assertTrue(res["halted_reason"].startswith("position_without_state"), res["halted_reason"])

    def test_position_of_another_size_is_not_adopted(self):
        w = self._crashed()
        w.size, w.avg = 3000, 69645.0
        w.records = [self._rec()]
        res = self.go()
        self.assertEqual(res["trades"], [])
        self.assertTrue(res["halted_reason"].startswith("position_without_state"))

    def test_placed_record_of_another_side_or_amount_or_age_does_not_match(self):
        for rec in (lambda: self._rec(side="sell"), lambda: self._rec(amount=1000),
                    lambda: placed_record(ARM - 30 * MIN)):
            self.tearDown()
            self.setUp()
            w = self._crashed()
            w.size, w.avg = 5000, 69645.0
            w.records = [rec()]
            res = self.go()
            self.assertEqual(res["trades"], [], rec)

    def test_no_intent_means_no_order_and_nothing_is_adopted(self):
        w = self._crashed()
        d = self.state_file()
        d["runner"]["intent"] = None            # crash between the engine save and the intent save
        (self.state_dir / "state_2026-11-13.json").write_text(json.dumps(d))
        w.size, w.avg = 5000, 69645.0
        w.records = [self._rec()]
        res = self.go()
        self.assertEqual(res["trades"], [])
        self.assertTrue(res["halted_reason"].startswith("restart: entering without an intent"))
        self.assertEqual(self.state_file()["engine"]["status"]["A"], "cancelled")

    def test_filled_then_stopped_out_while_down_keeps_the_entry_with_unknown_exit(self):
        w = self._crashed()
        w.size = 0
        w.order_avg["O9"] = 69645.0
        w.records = [self._rec()]
        res = self.go()
        self.assertEqual(len(w.calls_named("place_order")), 1)
        self.assertEqual(len(res["trades"]), 1)
        t = res["trades"][0]
        self.assertEqual(t["entry"], 69635.0)           # 69645 - basis 10
        self.assertIsNone(t["exit"])
        self.assertFalse(t["exit_price_known"])
        self.assertEqual(self.state_file()["engine"]["entries"], 1)    # the entry count is kept


class TestF9EnvFromClient(Base):
    def test_client_on_mainnet_refuses_even_when_env_test_is_passed(self):
        w = self.start(A_ONLY, s1_bars())
        self.client.env = "mainnet"
        res = self.go(env="test")
        self.assertFalse(res["ok"])
        self.assertEqual((w.calls, w.client_calls), ([], []))

    def test_client_on_mainnet_refuses_with_no_env_passed(self):
        w = self.start(A_ONLY, s1_bars())
        self.client.env = "mainnet"
        res = self.go(env=None)
        self.assertFalse(res["ok"])
        self.assertEqual((w.calls, w.client_calls), ([], []))

    def test_env_is_read_from_the_client_when_not_passed(self):
        w = self.start(A_ONLY, s1_bars())
        res = self.go(env=None)
        self.assertTrue(res["ok"])
        self.assertEqual(w.calls_named("place_order")[0][1]["env"], "test")


class TestF10CorruptState(Base):
    def _write(self, text):
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "state_2026-11-13.json").write_text(text)

    def test_valid_json_with_wrong_inner_types_is_corrupt_not_a_crash(self):
        w = self.start(A_ONLY, s1_bars(), clock_ms=ARM + 90 * 1000)
        self._write(json.dumps({"engine": {"plan": "not a dict"}, "runner": {}, "mode": "testnet"}))
        res = self.go()
        self.assertTrue(res["ok"])
        self.assertTrue(res["halted_reason"].startswith("state_corrupt"), res["halted_reason"])
        self.assertEqual(w.calls_named("place_order"), [])

    def test_move_aside_failure_halts_and_continues(self):
        w = self.start(A_ONLY, s1_bars(), clock_ms=ARM + 90 * 1000)
        self._write('{"engine": {broken')
        real = os.replace

        def locked(src, dst):
            if str(dst).endswith(".corrupt"):
                raise PermissionError("file is locked")
            return real(src, dst)
        with mock.patch.object(runner.os, "replace", side_effect=locked):
            res = self.go()
        self.assertTrue(res["ok"])
        self.assertIn("could not move it aside", res["halted_reason"])
        self.assertEqual(w.calls_named("place_order"), [])


if __name__ == "__main__":
    unittest.main()
