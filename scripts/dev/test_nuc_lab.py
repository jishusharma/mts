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
elif "codex_run.py tick" in script:
    print("tick: ran lf-rsi-facts")
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

    def test_tick_runs_codex_run_tick_over_the_gate(self):
        self._with_key()
        rc, out = self._run(["tick"])
        self.assertEqual(rc, 0)
        self.assertIn("ran lf-rsi-facts", out)

    def test_gemini_runs_gemini_queue_run_with_the_specs(self):
        self._with_key()
        rc, out = self._run(["gemini", "some-card:medium", "other-card:low"])
        self.assertEqual(rc, 0)
        self.assertIn("gemini_queue.py run some-card:medium other-card:low", out)

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


if __name__ == "__main__":
    unittest.main()
