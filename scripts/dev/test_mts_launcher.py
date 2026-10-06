"""Static test for the `mts runner` / `mts orphans` verbs in mts.ps1 (MTS_LAUNCHER_SPEC_2026-10-02.md section 10.1).

mts.ps1 cannot be run off the desktop, so this reads it as text. Run: python scripts/dev/test_mts_launcher.py
"""
import re
import unittest
from pathlib import Path

MTS = (Path(__file__).resolve().parents[2] / "mts.ps1").read_text(encoding="utf-8")


def branch(verb):
    """Body of the `"<verb>" { ... }` switch branch (up to the next top-level verb branch)."""
    m = re.search(r'^    "%s" \{\n(.*?)(?=^    "[a-z-]+"[ ,\w"]*\{|^    default)' % re.escape(verb), MTS, re.M | re.S)
    return m.group(1) if m else ""


class LauncherVerbs(unittest.TestCase):
    def test_verbs_in_table(self):
        table = re.search(r"# VERBS-BEGIN(.*?)# VERBS-END", MTS, re.S).group(1)
        verbs = set(re.findall(r'@\("[^"]+",\s*"([a-z-]+)"', table))
        self.assertIn("runner", verbs)
        self.assertIn("orphans", verbs)

    def test_runner_branch_uses_module_form_and_never_kills(self):
        b = branch("runner")
        self.assertTrue(b, "no switch branch for runner")
        self.assertIn("-m MyTradingSys.backtest.layers.alerts.live_runner_cli", b)
        self.assertNotIn("live_runner_cli.py", b)
        for bad in ("Stop-Process", "Remove-Item", "Move-Item", "mode.ps1"):
            self.assertNotIn(bad, b)

    def test_orphans_branch_maps_exit_codes(self):
        b = branch("orphans")
        self.assertTrue(b, "no switch branch for orphans")
        self.assertIn("orphan_watchdog_cli.py", b)
        for code in ("0 {", "1 {", "3 {"):
            self.assertIn(code, b)
        self.assertIn("exit $LASTEXITCODE", b)
        for bad in ("Stop-Process", "Remove-Item", "Move-Item", "--mainnet", "mode.ps1"):
            self.assertNotIn(bad, b)

    def test_status_block_has_both_lines(self):
        self.assertIn('Say "Layers and watchdogs"', MTS)
        self.assertIn("alert runner", MTS)
        self.assertIn("orphan watchdog", MTS)


if __name__ == "__main__":
    unittest.main()
