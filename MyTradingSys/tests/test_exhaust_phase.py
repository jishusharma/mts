"""exhaust-phase-tooling step 1 (EXHAUST_PHASE.md): scripts/dev/exhaust.py plan picks the phase from minutes to the weekly
reset and orders models by headroom; the window opens at 120 min, exhaust starts at 60 min."""
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
import exhaust  # noqa: E402

RESET = datetime(2026, 10, 23, 9, 0, tzinfo=timezone.utc)


def at(minutes_to_reset):
    return RESET - timedelta(minutes=minutes_to_reset)


class ExhaustPlanTest(unittest.TestCase):
    def test_phase_boundaries(self):
        cases = [(121, "none"), (120, "plan"), (61, "plan"), (60, "exhaust"), (1, "exhaust"), (0, "done"), (-5, "done")]
        for m, want in cases:
            self.assertEqual(exhaust.plan("C", 99, 13, RESET, {}, now=at(m))["phase"], want, m)

    def test_full_weekly_is_done(self):
        self.assertEqual(exhaust.plan("C", 100, 13, RESET, {}, now=at(30))["phase"], "done")

    def test_model_order_most_headroom_first_and_full_skipped(self):
        p = exhaust.plan("C", 90, 10, RESET, {"sonnet": 40, "opus": 10, "fable": 100, "haiku": 70}, now=at(50))
        self.assertEqual(p["models"], ["opus", "sonnet", "haiku"])

    def test_minutes_to_reset(self):
        self.assertEqual(exhaust.plan("A", 50, 5, RESET, {}, now=at(75))["minutes_to_reset"], 75)


class ExhaustClaimTest(unittest.TestCase):
    CLAIMS = [("exhaust-login-c", {"host": "desktop-f7iu69n"}), ("other-task", {"host": "jis-nb"})]

    def test_second_session_on_same_login_sees_holder(self):
        self.assertEqual(exhaust.holder("C", self.CLAIMS), "desktop-f7iu69n")

    def test_other_login_is_free(self):
        self.assertEqual(exhaust.holder("A", self.CLAIMS), "")
        self.assertEqual(exhaust.holder("B", []), "")


if __name__ == "__main__":
    unittest.main()
