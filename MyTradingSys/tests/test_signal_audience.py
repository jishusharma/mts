"""exhaust-phase-tooling step 3: a HIGH broadcast sent with --audience top is not shown to, and does not block the stop of,
a subagent or embedded worker (EXHAUST_PHASE.md: subagents ignore it)."""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
import mts_signal  # noqa: E402

B = {"kind": "broadcast", "prio": "high", "id": "b-aaaaaa", "to": "all", "aud": "top", "t": "99991231T000000Z", "text": "x", "cmd": "y"}


class AudienceTest(unittest.TestCase):
    def test_top_level_session_sees_it(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("MTS_SUBAGENT", None)
            os.environ.pop("MTS_ROLE", None)
            self.assertFalse(mts_signal.is_worker_env())
            self.assertIn("b-aaaaaa", mts_signal.action_block([B], "UserPromptSubmit"))

    def test_subagent_does_not(self):
        with mock.patch.dict(os.environ, {"MTS_SUBAGENT": "1"}):
            self.assertTrue(mts_signal.is_worker_env())
            self.assertEqual(mts_signal.action_block([B], "UserPromptSubmit"), "")

    def test_embedded_role_is_a_subagent(self):
        with mock.patch.dict(os.environ, {"MTS_ROLE": "Builder"}):
            self.assertTrue(mts_signal.is_worker_env())


class BudgetModelsTest(unittest.TestCase):
    def test_line_carries_per_model_windows(self):
        line = mts_signal.budget_line("C", 13, 99, "2026-10-23T09:00Z", {"opus": 10, "fable": 3})
        self.assertEqual(line, "BUDGET login=C 5h=13% week=99% reset=2026-10-23T09:00Z models=opus:10,fable:3")

    def test_line_without_models_is_unchanged(self):
        self.assertEqual(mts_signal.budget_line("A", 1, 2, "2026-10-23T09:00Z", {}), "BUDGET login=A 5h=1% week=2% reset=2026-10-23T09:00Z")


class StopGuardSubagentTest(unittest.TestCase):
    def test_subagent_stop_is_never_blocked(self):
        p = {"session_id": "s", "hook_event_name": "Stop", "agent_id": "a1", "last_assistant_message": "done"}
        self.assertEqual(mts_signal.handle(p), "")


if __name__ == "__main__":
    unittest.main()
