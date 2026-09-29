"""Static tests for mts.ps1 kill-mainnet (brief 131-SONNET). PowerShell cannot run offline here, so the
verb block and the verb table are checked as text. Derived from the brief, not from the implementation."""
import os
import re
import unittest
from pathlib import Path

MTS = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2]) / "mts.ps1"


def block(text, verb):
    m = re.search(r'^    "' + re.escape(verb) + r'" \{\n(.*?)^    \}\n', text, re.S | re.M)
    return m.group(1) if m else None


class MtsKillMainnetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = MTS.read_text(encoding="utf-8")

    def test_verb_is_in_the_table_next_to_kill(self):
        self.assertRegex(self.text, r'@\("Safety",\s+"kill-mainnet",\s+"[^"]+"\)')

    def test_block_exists_and_runs_kill_switch_with_mainnet(self):
        b = block(self.text, "kill-mainnet")
        self.assertIsNotNone(b, "no kill-mainnet case in the switch")
        self.assertIn("kill_switch.py", b)
        self.assertIn('"--mainnet"', b)
        self.assertIn('"--confirm" "KILL"', b)
        self.assertIn("exit $LASTEXITCODE", b)

    def test_block_clears_stale_account_env_and_asks_for_confirmation(self):
        b = block(self.text, "kill-mainnet")
        self.assertIn("Env:MTS_ACCOUNT", b)
        self.assertIn('Confirm-Word "KILL"', b)
        self.assertIn("MAINNET", b)

    def test_block_does_not_pass_an_account(self):
        b = block(self.text, "kill-mainnet")
        self.assertNotIn("--account", b)

    def test_testnet_kill_untouched(self):
        b = block(self.text, "kill")
        self.assertIsNotNone(b)
        self.assertNotIn("--mainnet", b)
        self.assertIn("testnet", b.lower())

    def test_testnet_kill_points_at_mainnet_verb(self):
        self.assertIn("kill-mainnet", block(self.text, "kill"))


if __name__ == "__main__":
    unittest.main()
