"""Tests for scripts/operator/runaway_check.ps1 (card runaway-process-leak). Fake rows via -ProcessJson."""
import json, os, shutil, subprocess, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PS1 = os.path.join(ROOT, "scripts", "operator", "runaway_check.ps1")
PWSH = shutil.which("powershell") or shutil.which("pwsh")


def run(rows, stop=False):
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "rows.json")
        with open(f, "w", newline="\n") as fh:
            json.dump(rows, fh)
        cmd = [PWSH, "-NoProfile", "-File", PS1, "-ProcessJson", f] + (["-Stop"] if stop else [])
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r.stdout + r.stderr


def row(i, name, cpu=1, handles=100, cmd=""):
    return {"Id": i, "Name": name, "CPU": cpu, "HandleCount": handles, "CommandLine": cmd}


@unittest.skipUnless(PWSH, "powershell not available")
class RunawayCheck(unittest.TestCase):
    def test_clean_is_ok(self):
        out = run([row(1, "python", 5000, 500), row(2, "find", 3, 50)])
        self.assertIn("OK:", out)
        self.assertNotIn("RUNAWAY", out)

    def test_handles_flagged(self):
        out = run([row(7, "java", 10, 100001)])
        self.assertIn("RUNAWAY pid 7 java", out)

    def test_long_find_flagged(self):
        out = run([row(8, "find", 601, 50, "find /")])
        self.assertIn("RUNAWAY pid 8 find", out)
        self.assertIn("FOUND 1", out)

    def test_long_python_not_flagged_by_cpu(self):
        self.assertIn("OK:", run([row(9, "python", 99999, 500)]))

    def test_stop_only_find_grep_sort(self):
        rows = [row(1, "find", 700), row(2, "grep", 700), row(3, "sort", 700),
                row(4, "sed", 700), row(5, "cat", 700), row(6, "java", 10, 200000)]
        out = run(rows, stop=True)
        for pid in (1, 2, 3):
            self.assertIn("would stop pid %d" % pid, out)
        for pid in (4, 5, 6):
            self.assertNotIn("would stop pid %d" % pid, out)


if __name__ == "__main__":
    unittest.main()
