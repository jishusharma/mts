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

    def test_auto_trader_python_is_resolved_not_hardcoded_and_fails_closed(self):
        b = branch("auto")
        self.assertTrue(b, "no switch branch for auto")
        self.assertNotRegex(b, r"(?i)[a-z]:[\/]+users[\/]", "auto-trader launch line hard-codes a user path")
        self.assertIn("Get-Command python.exe", b)
        # the missing-python refusal comes before the window opens
        self.assertLess(b.index("if (-not $autoPy)"), b.index("Open-Window"))
        self.assertIn("exit 1", b[b.index("if (-not $autoPy)"):b.index("Open-Window")])

    def test_market_verb_runs_read_only_guide(self):
        table = re.search(r"# VERBS-BEGIN(.*?)# VERBS-END", MTS, re.S).group(1)
        self.assertIn("market", set(re.findall(r'@\("[^"]+",\s*"([a-z-]+)"', table)))
        b = branch("market")
        self.assertTrue(b, "no switch branch for market")
        self.assertIn("market_guide.py", b)
        for bad in ("Stop-Process", "Remove-Item", "Move-Item", "mode.ps1", "auto_trader"):
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

    # Spec (wiring audit F4, 2026-10-07): status reports live_runner_cli and orphan_watchdog_cli; `mts runner`
    # starts live_runner_cli like `mts guard` does and honours the single-instance check.

    def test_status_verb_reports_runner_running_or_not(self):
        s = branch("status")
        self.assertTrue(s, "no switch branch for status")
        self.assertIn('Say ""; Say "Layers and watchdogs" Cyan', s)
        self.assertRegex(s, r'Ok "alert runner running')
        self.assertRegex(s, r'Warn "alert runner not running - start it with: mts runner"')

    def test_status_runner_line_sees_pythonw_and_python(self):
        # the runner is launched hidden under pythonw.exe by the scheduled launcher (a4a657a) or by hand under python.exe
        s = branch("status")
        m = re.search(r'\$runner = Get-Procs "([^"]*live_runner_cli[^"]*)" "([^"]*)"', s)
        self.assertTrue(m, "status does not look the runner process up")
        self.assertIn("python.exe", m.group(2))
        self.assertIn("pythonw.exe", m.group(2))

    def test_status_verb_reports_orphan_watchdog_outcomes(self):
        s = branch("status")
        for text in ("orphan watchdog never run - run it with: mts orphans",
                     "orphan watchdog last run",
                     "no orphans",
                     "HALT is set"):
            self.assertIn(text, s)

    def test_runner_verb_is_single_instance(self):
        b = branch("runner")
        start = b.index("Open-Window")
        check = b.index("already running")
        self.assertLess(check, start, "the already-running check must come before the start")
        self.assertIn("break", b[check:start])
        self.assertIn("pythonw.exe", b[:start], "a hidden (pythonw) runner must count as running")

    def test_runner_and_guard_start_the_same_module_in_a_window(self):
        mod = "-m MyTradingSys.backtest.layers.alerts.live_runner_cli"
        for verb in ("runner", "guard"):
            b = branch(verb)
            self.assertRegex(b, r'Open-Window "[^"]*" "python %s' % re.escape(mod), verb)

    def test_guard_does_not_start_a_second_runner_when_one_runs_hidden(self):
        # the guard's already-running check for the runner must see pythonw.exe too, or it starts a duplicate
        b = branch("guard")
        m = re.search(r'if \(\(Get-Procs "[^"]*live_runner_cli[^"]*" "([^"]*)"\)\.Count\)', b)
        self.assertTrue(m, "guard has no already-running check for live_runner_cli")
        self.assertIn("pythonw.exe", m.group(1))


class WiredToolVerbs(unittest.TestCase):
    """Wiring ledger 2026-10-08: tools that only tests referenced are now reachable through mts verbs."""

    def test_verbs_in_table(self):
        table = re.search(r"# VERBS-BEGIN(.*?)# VERBS-END", MTS, re.S).group(1)
        verbs = set(re.findall(r'@\("[^"]+",\s*"([a-z-]+)"', table))
        for v in ("missed", "soak", "wiring", "desk"):
            self.assertIn(v, verbs)

    def test_each_verb_runs_its_script_and_returns_the_exit_code(self):
        for verb, script in (("missed", "observation" + chr(92) + "missed.py"), ("soak", "soak_report.py"),
                             ("wiring", "wiring_scan.py"), ("desk", "desk.py")):
            b = branch(verb)
            self.assertTrue(b, "no switch branch for " + verb)
            self.assertIn(script, b)
            self.assertIn("exit $LASTEXITCODE", b)

    def test_read_only_verbs_never_delete_stop_or_trade(self):
        for verb in ("missed", "soak", "wiring", "desk"):
            b = branch(verb)
            for bad in ("Stop-Process", "Remove-Item", "Move-Item", "Set-Content", "--mainnet", "executor"):
                self.assertNotIn(bad, b, verb)

    def test_wiring_verb_runs_the_check_mode(self):
        self.assertIn('"--check"', branch("wiring"))

    def test_missed_verb_passes_horizon_through(self):
        self.assertIn("--horizon-h", branch("missed"))


if __name__ == "__main__":
    unittest.main()


def test_launch_scripts_do_not_hardcode_the_dev_checkout():
    """The live tree must run itself, not the dev checkout (host move 2026-10-22: mts start in C:/MTS/mts-live ran the dev tree)."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    old = r"IdeaProjects\BinanceDataFeed"
    files = [*root.glob("scripts/core/*.ps1"), *root.glob("scripts/live/*.ps1"), *root.glob("scripts/monitor/*.ps1"), *root.glob("runtime_data/*.vbs")]
    bad = [str(f.relative_to(root)) for f in files if old in f.read_text(encoding="utf-8-sig", errors="replace")]
    assert not bad, bad


def test_launchers_do_not_hardcode_a_python_interpreter_path():
    """A per-host interpreter path (pythoncore-3.14-64 exists on JIS-NB only) silently stopped every AUX process on the laptop (2026-10-22)."""
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    bad = [str(f.relative_to(root)) for f in root.glob("runtime_data/*.vbs") if "pythoncore" in f.read_text(encoding="utf-8-sig", errors="replace")]
    assert not bad, bad
