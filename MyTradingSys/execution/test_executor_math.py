"""
MyTradingSys/execution/test_executor_math.py.new

Hand-computed test for executor.py's live inverse-contract average-fill
formula (FORMULAS.md.new 11.5), derived independently of the code. All
network calls (deribit_orders / journal) are monkeypatched - nothing here
ever touches testnet, mainnet, .env, or .secrets/. Staged .new pending
Opus review - do not promote/rename/commit.

unittest.TestCase (R2 gate-integration fix): must be runnable through
`python -m unittest test_executor_math` via run_staged_tests.py /
run_all_tests.py step 1, so no sys.exit and no import-time side effects -
all monkeypatching happens in setUpClass/tearDownClass, not at module load.
"""
import unittest

import executor
import deribit_orders as do
import journal
from plan_compiler import compile_plan


class TestExecutorInverseAvgFill(unittest.TestCase):
    """FORMULAS.md 11.5: executor's live average-fill price for an inverse
    contract must be the harmonic mean weighted by USD size, NOT the
    notional-weighted arithmetic mean."""

    PLAN = {
        "plan_id": "w2_exec_math_check",
        "account": "a", "instrument": "BTC-PERPETUAL", "side": "LONG",
        "validity": {"start": "2020-01-01T00:00:00Z", "end": "2099-01-01T00:00:00Z"},
        "entry": {"type": "ladder", "range": {"low": 49000, "high": 50000}, "rungs": 2,
                  "size_multipliers": [1, 3]},
        "base_unit": 10,
        "stop": {"type": "fixed_percent", "percent_below_entry": 2.0},
        "targets": [],
        "caps": {"max_notional_usd": 10000, "max_loss_usd": -500, "max_concurrent_orders": 5},
    }

    @classmethod
    def setUpClass(cls):
        cls.compiled = compile_plan(cls.PLAN)
        rung1, rung2 = cls.compiled["entry_orders"]
        # rungs=2 -> rung_prices=[high, low]=[50000,49000]; sizes=[10,30]
        cls.fill_price = {rung1["label"]: 50000.0, rung2["label"]: 49000.0}
        cls.fill_amount = {rung1["label"]: rung1["amount"], rung2["label"]: rung2["amount"]}

        # Hand-computed expectation, FORMULAS.md 11.5:
        # avg_fill = filled_total / sum(amount_i / price_i)
        total = cls.fill_amount[rung1["label"]] + cls.fill_amount[rung2["label"]]  # 10+30=40
        harmonic_sum = (cls.fill_amount[rung1["label"]] / cls.fill_price[rung1["label"]]
                        + cls.fill_amount[rung2["label"]] / cls.fill_price[rung2["label"]])
        # = 10/50000 + 30/49000 = 0.0002 + 0.00061224489... = 0.00081224489...
        cls.expected_avg_fill_harmonic = round(total / harmonic_sum, 2)  # correct (inverse contract)
        cls.expected_avg_fill_arithmetic = round(
            (cls.fill_price[rung1["label"]] * cls.fill_amount[rung1["label"]]
             + cls.fill_price[rung2["label"]] * cls.fill_amount[rung2["label"]]) / total, 2)  # WRONG for inverse, for reference

        order_id_by_label = {rung1["label"]: "ord_1", rung2["label"]: "ord_2"}
        cls.label_by_order_id = {v: k for k, v in order_id_by_label.items()}
        cls.state = {oid: {"filled_amount": 0, "order_state": "open", "average_price": None}
                     for oid in order_id_by_label.values()}
        cls.order_id_by_label = order_id_by_label

        # --- monkeypatched deribit_orders / journal (module-attribute swap) ---
        def fake_authenticate():
            return "fake_token"

        def fake_get_position(token, instrument_name="BTC-PERPETUAL"):
            total_filled = sum(s["filled_amount"] for s in cls.state.values())
            return {"size": total_filled}

        def fake_get_open_orders(token, instrument_name="BTC-PERPETUAL", type_="all"):
            return []

        def fake_get_ticker(instrument_name="BTC-PERPETUAL"):
            return {"mark_price": 49500.0}

        def fake_buy(token, instrument_name, amount, order_type, price=None, label=None, reduce_only=False, **kw):
            l = label.split(":", 1)[1]  # strip "<plan_id>:" prefix
            return {"order_id": order_id_by_label[l]}

        def fake_sell(token, instrument_name, amount, order_type, price=None, label=None, reduce_only=False, **kw):
            return fake_buy(token, instrument_name, amount, order_type, price=price, label=label,
                            reduce_only=reduce_only, **kw)

        def fake_get_order_state(token, order_id):
            # Fill both rungs completely on the FIRST poll pass, at their
            # own fixed limit prices - matches "a limit ladder order fills
            # at its own price".
            label = cls.label_by_order_id[order_id]
            amount = cls.fill_amount[label]
            cls.state[order_id] = {"filled_amount": amount, "order_state": "filled",
                                    "average_price": cls.fill_price[label]}
            return cls.state[order_id]

        def fake_stop_market(token, instrument_name, side, amount, trigger_price, label):
            return {"order": {"order_id": "stop_ord_1"}}

        def fake_edit(token, order_id, amount=None, price=None, trigger_price=None):
            return {}

        def fake_cancel(token, order_id):
            return {}

        def fake_append_event(plan_id, event_type, data):
            pass

        def fake_read_events(plan_id):
            return []  # not previously run

        cls._orig = {
            "authenticate": do.authenticate, "get_position": do.get_position,
            "get_open_orders": do.get_open_orders, "get_ticker": do.get_ticker,
            "buy": do.buy, "sell": do.sell, "get_order_state": do.get_order_state,
            "stop_market": do.stop_market, "edit": do.edit, "cancel": do.cancel,
            "append_event": journal.append_event, "read_events": journal.read_events,
        }
        do.authenticate = fake_authenticate
        do.get_position = fake_get_position
        do.get_open_orders = fake_get_open_orders
        do.get_ticker = fake_get_ticker
        do.buy = fake_buy
        do.sell = fake_sell
        do.get_order_state = fake_get_order_state
        do.stop_market = fake_stop_market
        do.edit = fake_edit
        do.cancel = fake_cancel
        journal.append_event = fake_append_event
        journal.read_events = fake_read_events

        cls.result = executor.execute_plan(cls.compiled, plan=cls.PLAN, max_entry_seconds=5)

    @classmethod
    def tearDownClass(cls):
        for k, v in cls._orig.items():
            setattr(do if k not in ("append_event", "read_events") else journal, k, v)

    def test_avg_fill_is_harmonic_mean(self):
        self.assertEqual(self.result["avg_fill"], self.expected_avg_fill_harmonic)

    def test_avg_fill_is_not_arithmetic_mean(self):
        self.assertNotAlmostEqual(self.result["avg_fill"], self.expected_avg_fill_arithmetic, places=2)


if __name__ == "__main__":
    unittest.main()
