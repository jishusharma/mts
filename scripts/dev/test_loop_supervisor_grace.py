"""Restart-storm guard (2026-10-15: 8-14 loop restarts/hour, canary RED each time): the supervisor must not
treat a just-started wrapper as dead. Static checks on loop-supervisor.ps1; the PowerShell parser must accept it."""
import pathlib
import re
import shutil
import subprocess
import unittest

SUP = pathlib.Path(__file__).resolve().parents[1] / "core" / "loop-supervisor.ps1"


class LoopSupervisorGrace(unittest.TestCase):
    def setUp(self):
        self.src = SUP.read_text(encoding="utf-8")

    def test_grace_covers_slow_startup(self):
        m = re.search(r"\$RestartGraceSec\s*=\s*(\d+)", self.src)
        self.assertGreaterEqual(int(m.group(1)), 360)

    def test_started_wrapper_alive_is_not_dead(self):
        self.assertIn("$startedPid = $nid", self.src)
        self.assertRegex(self.src, r"if \(\$inGrace -or \$starting\)")

    def test_parses(self):
        ps = shutil.which("pwsh") or shutil.which("powershell")
        if not ps:
            self.skipTest("no PowerShell")
        cmd = "$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile('%s',[ref]$null,[ref]$e);if($e){$e;exit 1}" % SUP
        r = subprocess.run([ps, "-NoProfile", "-Command", cmd], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
