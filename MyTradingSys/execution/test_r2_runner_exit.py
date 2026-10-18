"""R2 runner exit, offline (session MTS-2026-10-03-CLI-BLD-r2-runner-exit).

Chain under test: Tom alert card (with RUNNER_TARGET) -> auto_trader.tom_signal -> new_plan.main -> validator ->
plan_compiler.compile_plan -> executor.execute_plan (fake exchange). 50% of size at TARGET, 50% at RUNNER_TARGET;
no RUNNER_TARGET -> one target, exactly as before.

Expected numbers are derived by hand (FORMULAS.md 11.1/11.2/11.4), not from the code under test:
  short entry 83537.3 -> limit snapped CEIL to the 0.5 tick = 83537.5
  TARGET 82985.43   -> (83537.3-82985.43)/83537.3 = 0.66063 % -> 0.661 (3 dp)
  RUNNER 82000.0    -> (83537.3-82000.0)/83537.3 = 1.84026 % -> 1.84
  target_1 raw 83537.5*(1-0.00661) = 82985.317 -> short target snaps CEIL -> 82985.5
  target_2 raw 83537.5*(1-0.0184)  = 82000.41  -> CEIL -> 82000.5
  size 200 USD, 50/50 -> 100 + 100 (floor to the 10 USD increment; the last target takes the remainder)

Hermetic: journal / plans / HALT paths are redirected to a temp dir, every exchange call is a fake. Run it through
scripts/dev/run_staged_tests.py (run_all_tests.py step 1) so the staged .new modules are the ones imported.
"""
import json
import math
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import auto_trader as at
import deribit_orders as do
import executor
import journal
import new_plan
import plan_compiler
import trade_plan_validator as tpv

NOW = datetime(2026, 9, 29, 0, 0, 0, tzinfo=timezone.utc)


def card(no=44, setup="ct_short", entry=83537.3, stop=83704.37, target=82985.43, runner=None,
         time="2026-09-28T23:58:00Z", rr="gross 3.3 / net 2.48"):
    runner_line = f"RUNNER_TARGET: {runner}\n" if runner is not None else ""
    text = (f"ALERT #{no}\n---\nVERDICT: SETUP_FORMING\nWHY:     proof 5\nTIME:    {time}\nPRICE:   83523.8\n"
            f"SETUP:   {setup}\nZONE:    15m_swing_high @ {entry}\n\nENTRY:   {entry}\nSTOP:    {stop}\n"
            f"TARGET:  {target}\n{runner_line}R:R:     {rr}\n")
    return {"title": f"MTS ALERT #{no}", "card_text": text}


def cfg():
    c = json.loads(json.dumps(at.DEFAULT_CONFIG))
    c["pre_pipeline_sources"] = {"layer:": {"reason": "test fixture", "review_by": "2026-10-23"}, "tom": {"reason": "test fixture", "review_by": "2026-10-23"}}   # fable H1: not testing the promotion gate here
    return c


def signal(**kw):
    s = at.tom_signal(card(**kw), {"tom_last_alert_no": 0}, cfg(), NOW)
    assert "reject" not in s, s
    return s


class FakeExchange:
    """Network boundary for executor.execute_plan: entries (reduce_only False) fill at once at their limit price,
    reduce-only orders rest. Records every placed order."""

    def __init__(self, mark=83540.0, entry_fill=None):
        self.pos, self.n, self.mark = 0, 0, mark
        self.entry_fill = entry_fill          # None = fill the whole entry; int = partial fill, order then cancelled
        self.orders, self.placed = {}, []

    def _new(self, direction, amount, typ, label, reduce_only, price=None, trigger=None):
        self.n += 1
        oid = f"O{self.n}"
        entry = not reduce_only and typ != "stop_market"
        filled = (self.entry_fill if self.entry_fill is not None else amount) if entry else 0
        state = ("cancelled" if filled < amount else "filled") if entry else \
                ("untriggered" if typ == "stop_market" else "open")
        self.orders[oid] = dict(order_id=oid, direction=direction, amount=amount, order_type=typ, label=label,
                                reduce_only=reduce_only, order_state=state, filled_amount=filled,
                                average_price=price if filled else 0, price=price, trigger_price=trigger)
        if filled:
            self.pos += filled if direction == "buy" else -filled
        self.placed.append(dict(self.orders[oid]))
        return {"order": self.orders[oid]}

    def authenticate(self):
        return "tok"

    def get_ticker(self, instrument="BTC-PERPETUAL"):
        return {"mark_price": self.mark}

    def get_position(self, token, instrument="BTC-PERPETUAL"):
        return {"size": self.pos}

    def get_open_orders(self, token, instrument="BTC-PERPETUAL", type_="all"):
        return [dict(o) for o in self.orders.values() if o["order_state"] in ("open", "untriggered")]

    def get_order_state(self, token, oid):
        return dict(self.orders[oid])

    def buy(self, token, instrument, amount, order_type, price=None, label=None, reduce_only=False, **kw):
        return self._new("buy", amount, order_type, label, reduce_only, price)

    def sell(self, token, instrument, amount, order_type, price=None, label=None, reduce_only=False, **kw):
        return self._new("sell", amount, order_type, label, reduce_only, price)

    def stop_market(self, token, instrument, side, amount, trigger_price, label, trigger="mark_price"):
        return self._new(side.lower(), amount, "stop_market", label, True, None, trigger_price)

    def edit(self, token, oid, amount=None, price=None, trigger_price=None):
        return {"order": self.orders[oid]}

    def cancel(self, token, oid):
        return {"order": self.orders[oid]}

    def cancel_by_label(self, token, label, currency="BTC"):
        return 0

    def close_position(self, token, instrument="BTC-PERPETUAL"):
        raise AssertionError("fail_closed must not run in these scenarios")


PATCHED = ("authenticate", "get_ticker", "get_position", "get_open_orders", "get_order_state", "buy", "sell",
           "stop_market", "edit", "cancel", "cancel_by_label", "close_position")


class Hermetic(unittest.TestCase):
    """Temp journal/plans dir, HALT files redirected, deribit_orders patched with the fake."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="r2_runner_"))
        self.fake = FakeExchange()
        for n in PATCHED:
            p = mock.patch.object(do, n, getattr(self.fake, n))
            p.start()
            self.addCleanup(p.stop)
        for obj, name, val in ((journal, "JOURNAL_DIR", self.tmp / "journal"),
                               (new_plan, "HERE", self.tmp / "x" / "y"),          # parents[1] == self.tmp
                               (new_plan, "PLANS_DIR", self.tmp / "plans"),
                               (new_plan, "JOURNAL_DIR", self.tmp / "journal"),
                               (executor, "HALT_PATH", self.tmp / "HALT"),
                               (executor, "HALT_DAILY_LOSS_PATH", self.tmp / "HALT_DAILY_LOSS"),
                               (executor, "HALT_DAILY_LOSS_PATH_MAINNET", self.tmp / "HALT_DAILY_LOSS_MAINNET")):
            p = mock.patch.object(obj, name, val)
            p.start()
            self.addCleanup(p.stop)

    def make_plan(self, sig):
        """Run the exact argv auto_trader would hand to new_plan.py; return the saved plan dict."""
        with mock.patch("builtins.print"):
            rc = new_plan.main([*sig["plan_args"], "--yes"])
        self.assertEqual(rc, 0)
        files = list((self.tmp / "plans").glob("*.json"))
        self.assertEqual(len(files), 1)
        return json.loads(files[0].read_text(encoding="utf-8"))

    def run_executor(self, plan):
        return executor.execute_plan(plan_compiler.compile_plan(plan), plan)

    def target_orders(self):
        return [o for o in self.fake.placed if o["reduce_only"] and o["order_type"] == "limit"]


class AlertCarriesRunner(unittest.TestCase):
    def test_card_regex_reads_runner_and_keeps_target_distinct(self):
        p = at.parse_tom_alert(card(runner=82000.0))
        self.assertEqual(p["target"], 82985.43)
        self.assertEqual(p["runner_target"], 82000.0)
        self.assertEqual(p["alert_no"], 44)

    def test_absent_zero_garbage_and_nan_runner_all_read_as_none(self):
        for raw in (None, 0, "0.0", "abc", "nan", "inf", -5):
            self.assertIsNone(at.parse_tom_alert(card(runner=raw))["runner_target"], raw)

    def test_runner_line_does_not_shadow_the_target_line(self):
        # RUNNER_TARGET sits right after TARGET; the TARGET field must still be the TARGET line
        text = card(runner=81000.0)["card_text"]
        self.assertLess(text.index("TARGET:  "), text.index("RUNNER_TARGET:"))
        self.assertEqual(at.parse_tom_alert(card(runner=81000.0))["target"], 82985.43)


class TwoLegPlan(Hermetic):
    def test_short_alert_becomes_50_50_plan_with_breakeven_flag(self):
        sig = signal(runner=82000.0)
        a = sig["plan_args"]
        self.assertEqual(a[a.index("--targets") + 1], "50@0.661,50@1.84")
        self.assertIn("--breakeven-after-first-target", a)
        self.assertEqual(sig["log"], {"runner_target": 82000.0})
        plan = self.make_plan(sig)
        self.assertEqual(plan["targets"], [{"amount_percent": 50.0, "pnl_target_percent": 0.661},
                                           {"amount_percent": 50.0, "pnl_target_percent": 1.84}])
        self.assertIs(plan["breakeven_after_first_target"], True)
        self.assertEqual(plan["stop"]["type"], "fixed_percent")        # the unsupported stop types stay unused

    def test_long_alert_exact_percentages(self):
        # (81200-80000)/80000 = 1.5 %, (83000-80000)/80000 = 3.75 %
        sig = signal(setup="tf_long", entry=80000.0, stop=79600.0, target=81200.0, runner=83000.0)
        a = sig["plan_args"]
        self.assertEqual(a[a.index("--targets") + 1], "50@1.5,50@3.75")

    def test_compile_emits_two_target_orders_50_50_at_target_and_runner(self):
        compiled = plan_compiler.compile_plan(self.make_plan(signal(runner=82000.0)))
        t = compiled["target_orders"]
        self.assertEqual([o["label"] for o in t], ["target_1", "target_2"])
        self.assertEqual([o["amount"] for o in t], [100, 100])
        self.assertEqual([o["price"] for o in t], [82985.5, 82000.5])
        self.assertTrue(all(o["reduce_only"] and o["side"] == "BUY" for o in t))     # short exits are buys
        self.assertEqual(compiled["entry_orders"][0]["price"], 83537.5)

    def test_executor_places_both_legs_and_the_runner_gets_the_rest(self):
        plan = self.make_plan(signal(runner=82000.0))
        res = self.run_executor(plan)
        self.assertEqual(res["status"], "entry_filled_stop_placed")
        self.assertEqual(len(res["target_order_ids"]), 2)
        legs = self.target_orders()
        self.assertEqual([(o["label"].split(":")[1], o["amount"], o["price"]) for o in legs],
                         [("target_1", 100, 82985.5), ("target_2", 100, 82000.5)])
        stop = [o for o in self.fake.placed if o["order_type"] == "stop_market"]
        self.assertEqual([(o["amount"], o["trigger_price"]) for o in stop], [(200, 83704.5)])
        # journal: the position manager rebuilds its targets from these order_placed events
        labels = [e["data"]["label"] for e in journal.read_events(plan["plan_id"])
                  if e["event_type"] == "order_placed" and e["data"].get("label", "").startswith("target")]
        self.assertEqual(labels, ["target_1", "target_2"])

    def test_partial_entry_fill_keeps_every_contract_covered(self):
        # 150 of 200 filled: target_1 = floor10(150*50%) = floor10(75) = 70, runner = remainder 80
        self.fake.entry_fill = 150
        res = self.run_executor(self.make_plan(signal(runner=82000.0)))
        self.assertEqual([o["amount"] for o in self.target_orders()], [70, 80])
        self.assertEqual(res["filled_total"], 150)


class NoRunnerKeepsOneTarget(Hermetic):
    def test_absent_runner_is_single_target_no_flag(self):
        sig = signal()
        a = sig["plan_args"]
        self.assertEqual(a[a.index("--targets") + 1], "0.661")
        self.assertNotIn("--breakeven-after-first-target", a)
        self.assertEqual(sig["log"], {"runner_skipped": "no RUNNER_TARGET"})
        plan = self.make_plan(sig)
        self.assertEqual(len(plan["targets"]), 1)
        self.assertNotIn("breakeven_after_first_target", plan)
        self.run_executor(plan)
        legs = self.target_orders()
        self.assertEqual([(o["amount"], o["price"]) for o in legs], [(200, 82985.5)])

    def test_runner_not_beyond_target_falls_back_to_one_target(self):
        for runner, side_kw in ((83000.0, {}),                                   # short: runner above target
                                (82985.43, {}),                                  # equal to target
                                (80500.0, dict(setup="tf_long", entry=80000.0, stop=79600.0, target=81200.0))):
            sig = signal(runner=runner, **side_kw)
            self.assertNotIn("--breakeven-after-first-target", sig["plan_args"], runner)
            self.assertIn("not beyond target", sig["log"]["runner_skipped"])

    def test_leg_pct_zero_switches_r2_off(self):
        c = cfg()
        c["tom"]["runner_leg_pct"] = 0
        s = at.tom_signal(card(runner=82000.0), {"tom_last_alert_no": 0}, c, NOW)
        self.assertNotIn("--breakeven-after-first-target", s["plan_args"])
        self.assertEqual(s["plan_args"][s["plan_args"].index("--targets") + 1], "0.661")

    def test_size_too_small_to_split_in_10_usd_legs_falls_back(self):
        c = cfg()
        c["tom"]["size_usd"] = 10            # 50% of 10 floors to 0 < 10 USD minimum
        s = at.tom_signal(card(runner=82000.0), {"tom_last_alert_no": 0}, c, NOW)
        self.assertNotIn("--breakeven-after-first-target", s["plan_args"])
        self.assertIn("too small", s["log"]["runner_skipped"])

    def test_default_split_is_50(self):
        self.assertEqual(at.DEFAULT_CONFIG["tom"]["runner_leg_pct"], 50)


class PlanFieldValidation(unittest.TestCase):
    PLAN = {"plan_id": "r2_val", "account": "a", "instrument": "BTC-PERPETUAL", "side": "SHORT",
            "validity": {"start": "2026-09-27T10:00:00Z", "end": "2026-09-27T14:00:00Z"},
            "entry": {"type": "limit", "price": 50000.0}, "base_unit": 200,
            "stop": {"type": "fixed_percent", "percent_below_entry": 0.2},
            "targets": [{"amount_percent": 50, "pnl_target_percent": 1.0},
                        {"amount_percent": 50, "pnl_target_percent": 2.0}],
            "caps": {"max_notional_usd": 1000, "max_loss_usd": -50, "max_concurrent_orders": 4}}

    def plan(self, **kw):
        return {**json.loads(json.dumps(self.PLAN)), **kw}

    def test_true_with_two_targets_is_valid(self):
        self.assertEqual(tpv.validate(self.plan(breakeven_after_first_target=True)), (True, "OK"))

    def test_absent_field_is_still_valid(self):
        self.assertEqual(tpv.validate(self.plan()), (True, "OK"))

    def test_non_true_values_are_refused(self):
        for bad in (False, "true", 1, None):
            ok, why = tpv.validate(self.plan(breakeven_after_first_target=bad))
            self.assertFalse(ok, bad)
            self.assertIn("breakeven_after_first_target", why)

    def test_one_target_is_refused_there_is_no_runner(self):
        one = self.plan(breakeven_after_first_target=True, targets=[{"amount_percent": 100, "pnl_target_percent": 1.0}])
        ok, why = tpv.validate(one)
        self.assertFalse(ok)
        self.assertIn("at least 2 targets", why)
        no_targets = self.plan(breakeven_after_first_target=True)
        del no_targets["targets"]
        self.assertFalse(tpv.validate(no_targets)[0])

    def test_executor_still_refuses_the_ladder_rung_breakeven_stop_type(self):
        # R2 does NOT lift breakeven_after_fills (ladder-rung semantics, never implemented): still refused pre-flight
        self.assertIn("breakeven_after_fills", executor.UNSUPPORTED_STOPS)
        plan = self.plan(stop={"type": "breakeven_after_fills", "percent_below_entry": 0.2, "min_fills_for_breakeven": 1})
        compiled = {"plan_id": "r2_val", "stop_order": {"order_type": "breakeven_metadata_only"},
                    "caps_check": {"within_max_loss": True, "max_notional_usd": 1000}, "max_position_size": 200}
        reasons = executor.preflight(compiled, plan, mark=50000.0, halt_path=Path(tempfile.gettempdir()) / "nohalt1",
                                     halt_daily_loss_path=Path(tempfile.gettempdir()) / "nohalt2")
        self.assertTrue(any("not implemented" in r for r in reasons), reasons)


# --- runner minimum distance (session MTS-2026-10-02-2055Z-CLI-SUP-r2-promote, T1/T2) -------------------------------
# runner = next node beyond the target at least runner_min_distance_pct percent of the TARGET price away; none -> no runner.
# Values: MyTradingSys/system/runner_min_distance.json (0.25, NO-SOURCE). All expected numbers are hand arithmetic.
_REPO = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
sys.path.append(str(_REPO / "MyTradingSys" / "runtime"))   # appended: the staged execution modules keep priority
import math_object_builder as mob  # noqa: E402
import runner_min_distance as rmd  # noqa: E402


class RunnerMinDistancePick(unittest.TestCase):
    # LONG zone 1000, stop 990 (risk 10), floor 1.25: node 1020 = 2.0R gross, net 1.5 -> the target.
    def pick(self, nodes, pct, zone=1000.0, stop=990.0, short=False):
        return mob.pick_target(nodes, zone, stop, short, 1.25, pct)

    def test_close_node_is_skipped_to_the_next_that_clears(self):
        # 1022.5: 2.5/1020 = 0.2451 % < 0.25 -> skipped; 1030: 10/1020 = 0.9804 % -> runner
        self.assertEqual(self.pick([1020.0, 1022.5, 1030.0], 0.25), (1020.0, 1030.0))

    def test_zero_minimum_keeps_the_old_next_node(self):
        self.assertEqual(self.pick([1020.0, 1022.5, 1030.0], 0.0), (1020.0, 1022.5))

    def test_just_above_the_minimum_qualifies(self):
        # 1022.6: 2.6/1020 = 0.2549 % >= 0.25
        self.assertEqual(self.pick([1020.0, 1022.6], 0.25), (1020.0, 1022.6))

    def test_skip_to_none_returns_no_runner_and_keeps_the_target(self):
        # 1022.0: 0.1961 %, 1022.4: 0.2353 % -> both under 0.25 -> no runner
        self.assertEqual(self.pick([1020.0, 1022.0, 1022.4], 0.25), (1020.0, None))

    def test_short_side_measures_from_the_target(self):
        # SHORT zone 1000, stop 1010; 980 = 2.0R -> target. 977.6: 2.4/980 = 0.2449 % skipped; 970: 10/980 = 1.0204 %
        self.assertEqual(self.pick([980.0, 977.6, 970.0], 0.25, stop=1010.0, short=True), (980.0, 970.0))

    def test_nan_minimum_qualifies_nothing(self):
        self.assertEqual(self.pick([1020.0, 1030.0], float("nan")), (1020.0, None))

    def test_min_distance_never_changes_the_target(self):
        for pct in (0.0, 0.25, 5.0, float("nan")):
            self.assertEqual(self.pick([1010.0, 1020.0, 1030.0], pct)[0], 1020.0)   # 1010 = 1.0R gross, net 0.75 < 1.25


class RunnerMinDistanceFile(unittest.TestCase):
    ZONE = {"name": "daily_vah", "price": 87064.0, "type": "daily_vah"}

    def write(self, text):
        d = tempfile.mkdtemp(prefix="rmd_")
        f = Path(d) / "runner_min_distance.json"
        f.write_text(text, encoding="utf-8")
        return f

    def norm(self, hvns):   # SHORT: swing high 87238 -> stop, risk 174; 86600 = 464/174 = 2.667R gross, fee-model net (464 - 87.064) / 261.064 = 1.444 -> target
        return {"current_price": 87000.0, "daily_vp": {"poc": 0, "hvns": hvns}, "weekly_vp": {}, "intraday_4h_vp": {},
                "vwap": {}, "prior_day": {}, "structure": {"15m": {"swing_high": 87238.0, "swing_low": 86000.0}}}

    def run_pick(self, path, hvns):
        with mock.patch.object(mob, "load_floor", return_value=1.25), mock.patch.object(rmd, "PATH", path):
            return mob._pick_stop_target_runner(self.ZONE, 87000.0, self.norm(hvns))

    def test_shipped_file_is_valid_and_positive(self):
        self.assertGreater(rmd.load_runner_min_distance_pct(), 0.0)

    def test_builder_reads_the_file_each_call(self):
        nodes = [86600.0, 86599.0, 83851.0]   # 86599: 1/86600 = 0.0012 % beyond the target
        self.assertEqual(self.run_pick(self.write('{"runner_min_distance_pct": 0.25}'), nodes), (87238.0, 86600.0, 83851.0))
        self.assertEqual(self.run_pick(self.write('{"runner_min_distance_pct": 0}'), nodes), (87238.0, 86600.0, 86599.0))

    def test_unreadable_file_fails_closed_to_no_runner(self):
        nodes = [86600.0, 83851.0]
        for bad in ('{"runner_min_distance_pct": "x"}', '{"runner_min_distance_pct": -1}', '{"runner_min_distance_pct": true}',
                    '{"other": 1}', "not json", "[]"):
            self.assertEqual(self.run_pick(self.write(bad), nodes), (87238.0, 86600.0, None), bad)
        self.assertEqual(self.run_pick(Path(tempfile.gettempdir()) / "rmd_missing.json", nodes), (87238.0, 86600.0, None))

    def test_loader_raises_on_bad_values_and_accepts_zero(self):
        for bad in ('{"runner_min_distance_pct": -0.1}', '{"runner_min_distance_pct": null}', '{"runner_min_distance_pct": 1e999}'):
            with self.assertRaises(rmd.RunnerMinDistanceError, msg=bad):
                rmd.load_runner_min_distance_pct(self.write(bad))
        self.assertEqual(rmd.load_runner_min_distance_pct(self.write('{"runner_min_distance_pct": 0}')), 0.0)
        self.assertTrue(math.isfinite(rmd.load_runner_min_distance_pct()))


if __name__ == "__main__":
    unittest.main()
