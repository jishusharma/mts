"""tc2: a lab runner (gemini_queue.py, codex_run.py) whose card runs a singleton role exports MTS_ROLE and
MTS_LEASE_SESSION so lease.py guards its desk/sync writes. Fails on the code before this change: the runners
passed no such env (2026-10-18 the Lenovo Gemini ran Pipeliner unguarded)."""
import sys
import unittest
from pathlib import Path

DEV = Path(__file__).resolve().parents[2] / "scripts" / "dev"
sys.path.insert(0, str(DEV))
import codex_run  # noqa: E402
import gemini_queue  # noqa: E402
import lease  # noqa: E402

PIPE = "TASK gemini-yt-pipeliner-x: You are the Pipeliner. Run the YouTube pipeline for the queued URLs."
PLAIN = "TASK tc3-budget-lines: add budget lines. Mentions pipeliner only as a file name (pipeliner.md)."


class RunnerEnv(unittest.TestCase):
    def test_pipeliner_card_gets_both_vars(self):
        self.assertEqual(lease.runner_env(PIPE, "gemini-q-123"), {"MTS_ROLE": "Pipeliner", "MTS_LEASE_SESSION": "gemini-q-123"})

    def test_card_role_field_wins(self):
        self.assertEqual(lease.runner_env("no role words", "r1", role="Pipeliner")["MTS_ROLE"], "Pipeliner")

    def test_normal_card_gets_none(self):
        self.assertEqual(lease.runner_env(PLAIN, "r1"), {})

    def test_non_singleton_role_gets_none(self):
        self.assertEqual(lease.runner_env("You are the Thinker.", "r1"), {})

    def test_gemini_child_env(self):
        env = gemini_queue.child_env("gemini-yt-pipeliner-x", PIPE, base={"A": "1"})
        self.assertEqual((env["MTS_ROLE"], env["A"]), ("Pipeliner", "1"))
        self.assertTrue(env["MTS_LEASE_SESSION"].startswith("gemini-q-gemini-yt-pipeliner-x"))
        self.assertNotIn("MTS_ROLE", gemini_queue.child_env("tc3", PLAIN, base={}))

    def test_codex_child_env(self):
        card = {"id": "lab-x"}
        env = codex_run.child_env(card, PIPE, {"CODEX_HOME": "h"})
        self.assertEqual((env["MTS_ROLE"], env["CODEX_HOME"]), ("Pipeliner", "h"))
        self.assertIn("MTS_LEASE_SESSION", env)
        self.assertNotIn("MTS_ROLE", codex_run.child_env(card, PLAIN, {}))


if __name__ == "__main__":
    unittest.main()
