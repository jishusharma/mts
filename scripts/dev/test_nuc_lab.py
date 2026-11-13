"""Tests for nuc_lab.py (tandem-nuc-lab-from-other-devices): a fake `ssh` on PATH stands in for the nuc_gate,
so no real network call happens. Covers: no key -> exit 0 'no gate key'; status/tick/gemini each build the right
one-line PowerShell script and print the fake gate's reply; gemini with no spec is a usage error."""
import io
import contextlib
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nuc_lab

# The fake ssh reads the script from stdin (nuc_lab pipes it the same way nuc_wake.py does) and echoes a
# one-line reply keyed on which real command the script asked for, so a test can tell the three verbs apart.
FAKE_SSH_PY = """import sys
script = sys.stdin.read()
if "codex_run.py status" in script:
    print("Codex allowance (plus): 5-hour window 6% used; week 27% used")
elif "schtasks /run /tn MTS-Wake-codextick" in script:
    print("tick: started in the logged-on session")
elif "gemini_queue.py run" in script:
    print("gemini: " + script.strip().splitlines()[-1])
else:
    print("unknown script: " + script)
"""


def _install_fake_ssh(bindir: Path) -> None:
    py = bindir / "fake_ssh_body.py"
    py.write_text(FAKE_SSH_PY, encoding="utf-8", newline="\n")
    if os.name == "nt":
        (bindir / "ssh.cmd").write_text(f'@"{sys.executable}" "{py}" %*\n', encoding="utf-8", newline="\n")
    else:
        sh = bindir / "ssh"
        sh.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{py}" "$@"\n', encoding="utf-8", newline="\n")
        sh.chmod(sh.stat().st_mode | stat.S_IEXEC)


class NucLabTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.bindir = Path(self._tmp.name)
        _install_fake_ssh(self.bindir)
        self._old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = str(self.bindir) + os.pathsep + self._old_path
        self._old_key = os.environ.get("MTS_NUC_GATE_KEY")

    def tearDown(self):
        os.environ["PATH"] = self._old_path
        if self._old_key is None:
            os.environ.pop("MTS_NUC_GATE_KEY", None)
        else:
            os.environ["MTS_NUC_GATE_KEY"] = self._old_key
        self._tmp.cleanup()

    def _with_key(self):
        key = self.bindir / "nuc_gate"
        key.write_text("fake key\n", encoding="utf-8", newline="\n")
        os.environ["MTS_NUC_GATE_KEY"] = str(key)

    def _no_key(self):
        os.environ["MTS_NUC_GATE_KEY"] = str(self.bindir / "missing_key")

    def _run(self, argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = nuc_lab.main(argv)
        return rc, buf.getvalue()

    def test_no_key_exits_0_and_says_so(self):
        self._no_key()
        rc, out = self._run(["status"])
        self.assertEqual(rc, 0)
        self.assertIn("no gate key", out)

    def test_status_runs_codex_run_status_over_the_gate(self):
        self._with_key()
        rc, out = self._run(["status"])
        self.assertEqual(rc, 0)
        self.assertIn("Codex allowance", out)

    def test_tick_starts_in_the_logged_on_session_not_inside_ssh(self):
        # 2026-11-04: a tick inside the ssh session could not read the saved GitHub login, so every claim push failed.
        self._with_key()
        rc, out = self._run(["tick"])
        self.assertEqual(rc, 0)
        self.assertIn("started in the logged-on session", out)
        self.assertNotIn("codex_run.py tick", nuc_lab.build_script("tick"))

    def test_gemini_runs_gemini_queue_run_with_the_specs(self):
        self._with_key()
        rc, out = self._run(["gemini", "some-card:medium", "other-card:low"])
        self.assertEqual(rc, 0)
        self.assertIn("gemini_queue.py run some-card:medium other-card:low", out)

    def test_gemini_task_registers_one_shot_it_task_as_user(self):
        sc = nuc_lab.build_script("gemini-task", ["c1:low"])
        for need in ("schtasks /Create", "/RU e-ngineers /IT", "schtasks /Run", "Start-Transcript", "--ff-only", "gemini_queue.py run c1:low", "Python314"):
            self.assertIn(need, sc)
        self.assertNotIn("ps-bg", sc)

    def test_gemini_with_no_spec_is_a_usage_error(self):
        self._with_key()
        with self.assertRaises(SystemExit):
            nuc_lab.main(["gemini"])

    def test_never_starts_a_second_run_itself_build_script_is_one_shot(self):
        # nuc_lab relies on codex_run.py's own lab.lock / 20-min gap guard and gemini_queue.py's claim check;
        # it must not add its own lock file or loop. build_script never touches disk and returns one line.
        s = nuc_lab.build_script("tick")
        self.assertEqual(s.count("\n"), 1)
        self.assertNotIn("while", s.lower())


class NucLabTimeoutTest(unittest.TestCase):
    """bg-process-audit 2026-10-28: a NUC verb with no deadline sat silent for 2 h. Every verb now has one."""

    def test_status_has_a_5_minute_deadline_and_prints_timeout(self):
        seen = {}

        def hang(cmd, **kw):
            seen.update(kw)
            raise nuc_lab.subprocess.TimeoutExpired(cmd, kw.get("timeout"))
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as t:
            key = Path(t) / "k"
            key.write_text("k", encoding="utf-8")
            os.environ["MTS_NUC_GATE_KEY"] = str(key)
            try:
                with contextlib.redirect_stdout(buf):
                    rc = nuc_lab.run("status", runner=hang)
            finally:
                os.environ.pop("MTS_NUC_GATE_KEY", None)
        self.assertEqual(seen.get("timeout"), 300)
        self.assertEqual(rc, 124)
        self.assertIn("TIMEOUT nuc_lab status after 300s", buf.getvalue())

    def test_job_verbs_get_the_worker_cap(self):
        self.assertEqual(nuc_lab.VERB_TIMEOUT_S["tick"], 2700)
        self.assertEqual(nuc_lab.VERB_TIMEOUT_S["gemini"], 2700)


class GeminiLauncherTest(unittest.TestCase):
    """gemini-queue-parallel-runs-fight-over-gi: parallel launchers must not show console windows or die on ref locks."""

    def test_launcher_task_runs_hidden(self):
        s = nuc_lab.task_script(["c1:low:flash"])
        self.assertIn("powershell -WindowStyle Hidden -NoProfile", s)

    def test_launcher_retries_fetch_on_ref_lock_before_merge(self):
        s = nuc_lab.task_script(["c1:low:flash"])
        self.assertIn("for ($i = 1; $i -le 6; $i++) { git fetch -q origin", s)
        self.assertIn("git merge -q --ff-only origin/fast-track", s)
        self.assertLess(s.index("git fetch -q origin"), s.index("git merge -q --ff-only"))


if __name__ == "__main__":
    unittest.main()
