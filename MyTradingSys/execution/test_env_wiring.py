"""Offline tests for the env/plan-cap wiring in executor.py and position_manager.py (brief 130-SONNET).
Needs journal env helpers (126) and mainnet_plan_check (128) promoted first. Fake exchange only, no network."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import deribit_orders as do
import executor
import journal
import position_manager as pm
from test_s1_cap_offline import FakeExchange, PATCHED_NAMES, _compiled

NOHALT = Path(tempfile.gettempdir()) / "definitely_no_such_halt_file"
RAW_PLAN = {"stop": {"type": "fixed_percent", "percent_below_entry": 2}}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="envwire_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        p = mock.patch.object(journal, "JOURNAL_DIR", self.tmp)
        p.start()
        self.addCleanup(p.stop)
        self.orig = {n: getattr(do, n) for n in PATCHED_NAMES}
        self.addCleanup(self._restore)

    def _restore(self):
        for n, f in self.orig.items():
            setattr(do, n, f)

    def install(self, fake):
        for n in PATCHED_NAMES:
            setattr(do, n, getattr(fake, n))


class ExecutorIntentEnvTests(Base):
    def test_intent_event_records_env_test(self):
        fake = FakeExchange(existing_pos=0)
        self.install(fake)
        executor.execute_plan(_compiled("env_t", 500))
        intent = next(e for e in journal.read_events("env_t") if e["event_type"] == "intent")
        self.assertEqual(intent["data"]["env"], "test")

    def test_intent_event_records_env_from_active_env(self):
        # plan cap is 50 on mainnet; a raw plan with one 50 USD entry passes the new plan check
        fake = FakeExchange(existing_pos=0)
        self.install(fake)
        with mock.patch.object(do, "active_env", return_value="mainnet"), \
                mock.patch.object(executor, "_check_halt_files", return_value=[]):
            try:
                executor.execute_plan(_compiled("env_m", 50), plan=RAW_PLAN)
            except executor.ExecutionHalted:
                pass  # later stages may halt on the fake; only the intent stamp matters
        intent = [e for e in journal.read_events("env_m") if e["event_type"] == "intent"]
        self.assertEqual(len(intent), 1)
        self.assertEqual(intent[0]["data"]["env"], "mainnet")


class ExecutorPlanCapTests(Base):
    def _reasons(self, compiled, plan, env):
        with mock.patch.object(do, "active_env", return_value=env):
            return executor.preflight(compiled, plan, None, NOHALT, NOHALT)

    def test_precompiled_input_refused_on_mainnet(self):
        r = self._reasons(_compiled("pc1", 50), None, "mainnet")
        self.assertTrue(any("pre-compiled" in x for x in r), r)

    def test_precompiled_input_still_fine_on_testnet(self):
        self.assertEqual(self._reasons(_compiled("pc2", 500), None, "test"), [])

    def test_two_rungs_with_understated_max_refused_on_mainnet(self):  # audit R5
        c = _compiled("pc3", 50)
        c["entry_orders"].append(dict(c["entry_orders"][0], label="entry_2"))
        self.assertEqual(c["max_position_size"], 50)
        r = self._reasons(c, RAW_PLAN, "mainnet")
        self.assertTrue(any("sum of entry amounts 100" in x for x in r), r)

    def test_raw_plan_50_ok_on_mainnet_and_100_refused(self):
        self.assertEqual(self._reasons(_compiled("pc4", 50), RAW_PLAN, "mainnet"), [])
        self.assertTrue(self._reasons(_compiled("pc5", 100), RAW_PLAN, "mainnet"))

    def test_execute_plan_precompiled_on_mainnet_places_nothing_and_leaves_no_journal(self):
        fake = FakeExchange(existing_pos=0)
        self.install(fake)
        with mock.patch.object(do, "active_env", return_value="mainnet"):
            with self.assertRaises(executor.ExecutionHalted):
                executor.execute_plan(_compiled("pc6", 50))
        self.assertEqual(fake.buy_calls, [])
        self.assertEqual(journal.read_events("pc6"), [])


class PositionManagerEnvTests(Base):
    def test_manage_refuses_plan_journaled_on_other_env_before_any_exchange_call(self):
        journal.append_event("pmx", "intent", {"env": "mainnet"})
        journal.append_event("pmx", "order_placed", {"order_id": "s1", "label": "stop_order", "side": "SELL",
                                                     "amount": 50, "trigger_price": 79000.0})
        before = (self.tmp / "pmx.jsonl").read_text(encoding="utf-8")

        def boom(*a, **k):
            raise AssertionError("exchange touched before the env check")

        setattr(do, "authenticate", boom)
        with mock.patch.object(do, "active_env", return_value="test"), \
                mock.patch.object(do, "get_position", boom), mock.patch.object(do, "get_order_state", boom):
            with self.assertRaises(pm.ManagerHalted) as c:
                pm.manage("pmx", once=True)
        self.assertIn("mainnet", str(c.exception))
        self.assertEqual((self.tmp / "pmx.jsonl").read_text(encoding="utf-8"), before,
                         "an env refusal must not write to the journal (no mismatch_halt)")


if __name__ == "__main__":
    unittest.main()
