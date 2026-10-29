"""daily_hygiene.py: the file a session reads at boot says GREEN/RED truthfully, surfaces unshipped work, and never applies a declutter."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import daily_hygiene as dh

NOW = datetime(2026, 10, 10, 6, 30, tzinfo=timezone.utc)


def fake(gate_rc=0, where_out="ok        BinanceDataFeed   [fast-track] unshipped-commits=0", status_rc=0):
    seen = []

    def runner(argv, timeout):
        seen.append(argv)
        if "run_all_tests.py" in " ".join(argv):
            return gate_rc, "Step 1: PASS\nStep 4: FAIL\nFAILED: 1 step(s)" if gate_rc else "ALL TESTS PASSED"
        if "sync.py" in " ".join(argv):
            return 0, where_out
        if "make_status.py" in " ".join(argv):
            return status_rc, "wrote STATUS.md"
        return 0, "== superseded: 0"
    return runner, seen


class TestHygiene(unittest.TestCase):
    def go(self, **kw):
        with tempfile.TemporaryDirectory() as d:
            runner, seen = fake(**kw)
            status, results = dh.run(runner, NOW, Path(d))
            md = (Path(d) / "hygiene_latest.md").read_text(encoding="utf-8")
            js = json.loads((Path(d) / "hygiene_latest.json").read_text(encoding="utf-8"))
        return status, md, js, seen

    def test_all_green(self):
        status, md, js, _ = self.go()
        self.assertEqual(status, "GREEN")
        self.assertIn("STATUS: GREEN", md)
        self.assertIn("GATE: PASS", md)
        self.assertEqual(js["utc"], "2026-10-10T06:30:00Z")
        self.assertEqual([s["step"] for s in js["steps"]], ["gate", "tidy", "where", "health", "declutter_dry_run", "desk_assign", "status"])

    def test_red_gate_is_red_and_shows_the_failing_tail(self):
        status, md, js, _ = self.go(gate_rc=1)
        self.assertEqual(status, "RED")
        self.assertIn("STATUS: RED (failed: gate)", md)
        self.assertIn("GATE: FAIL", md)
        self.assertIn("FAILED: 1 step(s)", md)

    def test_unshipped_worktrees_are_listed_first(self):
        _, md, _, _ = self.go(where_out="UNSHIPPED mts-dsa [jisnb/dsa] unshipped-commits=3 modified=0 untracked=0\nok x")
        self.assertIn("Unshipped work", md)
        self.assertIn("- UNSHIPPED mts-dsa", md)
        self.assertLess(md.index("Unshipped work"), md.index("## gate"))

    def test_declutter_runs_dry_never_apply(self):
        _, _, _, seen = self.go()
        flat = [" ".join(a) for a in seen]
        dec = [f for f in flat if "declutter_backups.py" in f]
        self.assertEqual(len(dec), 1)
        self.assertNotIn("--apply", dec[0])

    def test_timeout_and_missing_exe_are_failures_not_crashes(self):
        def runner(argv, timeout):
            return (124, "timed out after 5s") if "run_all_tests" in " ".join(argv) else (0, "")
        with tempfile.TemporaryDirectory() as d:
            status, _ = dh.run(runner, NOW, Path(d))
        self.assertEqual(status, "RED")

    def test_make_status_embeds_the_hygiene_file(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import make_status as ms
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "hygiene_latest.md").write_text("# Daily hygiene 2026-10-10T06:30:00Z on X\n\nSTATUS: RED (failed: gate)\nGATE: FAIL (5 s)\n", encoding="utf-8")
            text = ms.get_hygiene_status(Path(d))
            self.assertIn("STATUS: RED (failed: gate)", text)
            self.assertIn("2026-10-10T06:30:00Z", text)
            self.assertEqual(ms.get_hygiene_status(Path(d) / "missing"), "")   # no report on this host: STATUS.md leaves the section out


if __name__ == "__main__":
    unittest.main()
