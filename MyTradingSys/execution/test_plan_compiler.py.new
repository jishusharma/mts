"""
MyTradingSys/execution/test_plan_compiler.py.new

Hand-computed tests for plan_compiler.py, derived from
backtest/layers/FORMULAS.md.new section 11 (execution math) AFTER Opus
review R2: 11.1/11.2 are side-aware (never a worse fill than planned for
entries, never a loss above budget for stops, more-likely-to-fill for
targets) and size is FLOORED with a CompileError below the 10 USD
minimum, never forced up. NOT derived from reading plan_compiler.py's own
arithmetic. Staged as .new pending Opus review - do not
promote/rename/commit until then.

unittest.TestCase (R2 gate-integration fix): must be runnable through
`python -m unittest test_plan_compiler` via run_staged_tests.py /
run_all_tests.py step 1, so no sys.exit and no import-time side effects.
"""
import unittest

from plan_compiler import compile_plan, snap_price, round_size, CompileError


class TestSnapPriceDirectional(unittest.TestCase):
    """11.1: matrix of {floor, ceil} x {exact tick, just above tick, just
    below next tick}. Tick = 0.5."""

    def test_floor_exact_tick(self):
        # 50000.0 is already a multiple of 0.5 - both directions no-op.
        self.assertEqual(snap_price(50000.0, "floor"), 50000.0)

    def test_ceil_exact_tick(self):
        self.assertEqual(snap_price(50000.0, "ceil"), 50000.0)

    def test_floor_just_above_tick(self):
        # 50000.1 is just above the 50000.0 tick -> floor -> 50000.0
        self.assertEqual(snap_price(50000.1, "floor"), 50000.0)

    def test_ceil_just_above_tick(self):
        # 50000.1 -> ceil -> up to the next tick, 50000.5
        self.assertEqual(snap_price(50000.1, "ceil"), 50000.5)

    def test_floor_just_below_next_tick(self):
        # 50000.49 is just below the 50000.5 tick -> floor -> 50000.0
        self.assertEqual(snap_price(50000.49, "floor"), 50000.0)

    def test_ceil_just_below_next_tick(self):
        # 50000.49 -> ceil -> up to 50000.5
        self.assertEqual(snap_price(50000.49, "ceil"), 50000.5)

    def test_floor_exact_midpoint(self):
        # The old round-half-to-even ambiguity is NOT special-cased any
        # more: floor always goes down regardless of distance from either tick.
        self.assertEqual(snap_price(50000.25, "floor"), 50000.0)

    def test_ceil_exact_midpoint(self):
        self.assertEqual(snap_price(50000.25, "ceil"), 50000.5)

    def test_unknown_mode_raises(self):
        # Never silently guess a direction.
        with self.assertRaises(ValueError):
            snap_price(50000.0, "nearest")


class TestRoundSizeFloorOnly(unittest.TestCase):
    """11.2: floor only, CompileError below the 10 USD minimum (never
    forced up)."""

    def test_exact_multiple(self):
        self.assertEqual(round_size(30), 30)

    def test_just_above_a_multiple_floors_down(self):
        # 25/10 = 2.5 -> floor -> 2 -> 20 (NOT 30)
        self.assertEqual(round_size(25), 20)

    def test_just_below_next_multiple_floors_down(self):
        self.assertEqual(round_size(29.9), 20)

    def test_below_minimum_raises_compile_error(self):
        with self.assertRaises(CompileError):
            round_size(9)

    def test_well_below_minimum_raises_compile_error(self):
        with self.assertRaises(CompileError):
            round_size(3)


class TestLadderHarmonicMean(unittest.TestCase):
    """11.4: ladder harmonic-mean avg entry (unchanged by the R2 review,
    re-verified against the new directional snap). valid_ladder_four_rung
    by hand: low=49750 high=50200 rungs=4 mults=[1,1,2,3] base_unit=10 ->
    sizes [10,10,20,30]; step=(50200-49750)/3=150; LONG rung_prices =
    [50200,50050,49900,49750], all already 0.5-multiples."""

    LADDER_PLAN = {
        "plan_id": "w2_ladder_check",
        "account": "subaccount_1",
        "instrument": "BTC-PERPETUAL",
        "side": "LONG",
        "validity": {"start": "2026-09-27T10:00:00Z", "end": "2026-09-27T14:00:00Z"},
        "entry": {"type": "ladder", "range": {"low": 49750, "high": 50200}, "rungs": 4,
                  "size_multipliers": [1, 1, 2, 3]},
        "base_unit": 10,
        "stop": {"type": "fixed_percent", "percent_below_entry": 2.0},
        "targets": [{"amount_percent": 50, "pnl_target_percent": 2.0},
                    {"amount_percent": 50, "pnl_target_percent": 5.0}],
        "caps": {"max_notional_usd": 1000, "max_loss_usd": -50, "max_concurrent_orders": 7},
    }

    @classmethod
    def setUpClass(cls):
        cls.compiled = compile_plan(cls.LADDER_PLAN)
        rung_prices = [50200, 50050, 49900, 49750]
        sizes = [10, 10, 20, 30]
        cls.total_size = sum(sizes)  # 70
        harmonic_sum = sum(s / p for s, p in zip(sizes, rung_prices))
        cls.correct_avg_entry = round(cls.total_size / harmonic_sum, 2)  # 49899.49

    def test_avg_entry_is_harmonic_mean(self):
        self.assertEqual(self.compiled["entry_avg_if_ladder_fills"], self.correct_avg_entry)

    def test_worst_case_loss_long_stop_snapped_ceil(self):
        # 11.6: LONG stop snaps CEIL (toward entry, loss <= budget)
        raw_stop = self.correct_avg_entry * (1 - 0.02)
        snapped_stop = snap_price(raw_stop, "ceil")
        expected_loss = -round(abs(self.correct_avg_entry - snapped_stop) * self.total_size / self.correct_avg_entry, 2)
        self.assertEqual(self.compiled["worst_case_loss_usd"], expected_loss)

    def test_target_prices_long_snapped_floor(self):
        # 11.7: LONG target snaps FLOOR (toward entry, more likely to fill)
        t1_expected = snap_price(self.correct_avg_entry * 1.02, "floor")
        t2_expected = snap_price(self.correct_avg_entry * 1.05, "floor")
        actual = {t["label"]: t["price"] for t in self.compiled["target_orders"]}
        self.assertEqual(actual["target_1"], t1_expected)
        self.assertEqual(actual["target_2"], t2_expected)


class TestSideAwareEndToEnd(unittest.TestCase):
    """Side-aware entry/stop/target snap exercised end-to-end through
    compile_plan for BOTH sides, with prices deliberately off-tick so the
    direction actually matters."""

    def test_long_limit_entry_snaps_floor(self):
        plan = {
            "plan_id": "w2_long_limit", "account": "a", "instrument": "BTC-PERPETUAL", "side": "LONG",
            "validity": {"start": "2026-09-27T10:00:00Z", "end": "2026-09-27T14:00:00Z"},
            "entry": {"type": "limit", "price": 50000.37}, "base_unit": 50,
            "stop": {"type": "fixed_percent", "percent_below_entry": 2.0},
            "targets": [{"amount_percent": 100, "pnl_target_percent": 3.0}],
            "caps": {"max_notional_usd": 1000, "max_loss_usd": -50, "max_concurrent_orders": 3},
        }
        c = compile_plan(plan)
        # entry_mode=floor: 50000.37 -> floor -> 50000.0 (BUY never pays more than planned)
        self.assertEqual(c["entry_orders"][0]["price"], 50000.0)
        # stop: LONG -> ceil. raw = 50000.0*0.98 = 49000.0 (already exact)
        self.assertEqual(c["stop_order"]["price"], 49000.0)
        # target: LONG -> floor. raw = 50000.0*1.03 = 51500.0 (already exact)
        self.assertEqual(c["target_orders"][0]["price"], 51500.0)

    def test_short_limit_entry_snaps_ceil(self):
        plan = {
            "plan_id": "w2_short_limit", "account": "a", "instrument": "BTC-PERPETUAL", "side": "SHORT",
            "validity": {"start": "2026-09-27T10:00:00Z", "end": "2026-09-27T14:00:00Z"},
            "entry": {"type": "limit", "price": 50000.12}, "base_unit": 50,
            "stop": {"type": "fixed_percent", "percent_below_entry": 2.0},
            "targets": [{"amount_percent": 100, "pnl_target_percent": 3.0}],
            "caps": {"max_notional_usd": 1000, "max_loss_usd": -50, "max_concurrent_orders": 3},
        }
        c = compile_plan(plan)
        # entry_mode=ceil: 50000.12 -> ceil -> 50000.5 (SELL never for less than planned)
        self.assertEqual(c["entry_orders"][0]["price"], 50000.5)
        # stop: SHORT -> floor (toward entry, caps the loss). raw = 50000.5*1.02 = 51000.51
        raw_short_stop = 50000.5 * 1.02
        self.assertEqual(c["stop_order"]["price"], snap_price(raw_short_stop, "floor"))
        # target: SHORT -> ceil (toward entry, more likely to fill). raw = 50000.5*0.97 = 48500.485
        raw_short_target = 50000.5 * 0.97
        self.assertEqual(c["target_orders"][0]["price"], snap_price(raw_short_target, "ceil"))


class TestSizeBelowMinimumRejection(unittest.TestCase):
    """11.2 at the plan level: a plan whose base_unit floors below 10 must
    refuse to compile, never silently trade the 10 USD minimum instead."""

    def test_plan_with_too_small_base_unit_is_rejected(self):
        plan = {
            "plan_id": "w2_too_small", "account": "a", "instrument": "BTC-PERPETUAL", "side": "LONG",
            "validity": {"start": "2026-09-27T10:00:00Z", "end": "2026-09-27T14:00:00Z"},
            "entry": {"type": "limit", "price": 50000.0}, "base_unit": 7,  # floors to 0 < 10
            "stop": {"type": "fixed_percent", "percent_below_entry": 2.0},
            "targets": [],
            "caps": {"max_notional_usd": 1000, "max_loss_usd": -50, "max_concurrent_orders": 3},
        }
        with self.assertRaises(CompileError):
            compile_plan(plan)


class TestR2RunnerPlan(unittest.TestCase):
    """R2 runner exit (2026-10-03). The compiler already emits one order per plan target, so the 50/50 split needs no
    compiler change: it comes from the plan's two targets. Hand numbers (FORMULAS.md 11.1/11.2): SHORT limit
    83537.3 -> entry snaps CEIL 83537.5; 0.661 % -> raw 82985.317 -> CEIL 82985.5; 1.84 % -> raw 82000.41 -> CEIL
    82000.5; 200 USD at 50/50 -> 100 + 100."""

    def plan(self, **kw):
        p = {
            "plan_id": "r2_short", "account": "a", "instrument": "BTC-PERPETUAL", "side": "SHORT",
            "validity": {"start": "2026-09-27T10:00:00Z", "end": "2026-09-27T14:00:00Z"},
            "entry": {"type": "limit", "price": 83537.3}, "base_unit": 200,
            "stop": {"type": "fixed_percent", "percent_below_entry": 0.2},
            "targets": [{"amount_percent": 50, "pnl_target_percent": 0.661},
                        {"amount_percent": 50, "pnl_target_percent": 1.84}],
            "caps": {"max_notional_usd": 1000, "max_loss_usd": -50, "max_concurrent_orders": 4},
        }
        p.update(kw)
        return p

    def test_two_targets_compile_to_two_reduce_only_orders_50_50(self):
        c = compile_plan(self.plan())
        self.assertEqual([(o["label"], o["amount"], o["price"]) for o in c["target_orders"]],
                         [("target_1", 100, 82985.5), ("target_2", 100, 82000.5)])
        self.assertTrue(all(o["reduce_only"] and o["side"] == "BUY" for o in c["target_orders"]))

    def test_breakeven_flag_changes_no_order(self):
        base, flagged = compile_plan(self.plan()), compile_plan(self.plan(breakeven_after_first_target=True))
        self.assertEqual(flagged["target_orders"], base["target_orders"])
        self.assertEqual(flagged["stop_order"], base["stop_order"])
        self.assertEqual(flagged["entry_orders"], base["entry_orders"])
        self.assertEqual(flagged["stop_order"]["order_type"], "stop_market")   # initial stop is the ordinary fixed stop

    def test_breakeven_flag_with_one_target_refuses_to_compile(self):
        one = [{"amount_percent": 100, "pnl_target_percent": 0.661}]
        with self.assertRaises(CompileError):
            compile_plan(self.plan(breakeven_after_first_target=True, targets=one))

    def test_breakeven_flag_must_be_true(self):
        for bad in (False, "true", 1):
            with self.assertRaises(CompileError, msg=repr(bad)):
                compile_plan(self.plan(breakeven_after_first_target=bad))

    def test_a_leg_below_the_minimum_still_refuses_rather_than_forcing_up(self):
        with self.assertRaises(CompileError):      # 10 USD at 50% = 5 -> floors to 0 < 10
            compile_plan(self.plan(base_unit=10))


if __name__ == "__main__":
    unittest.main()
