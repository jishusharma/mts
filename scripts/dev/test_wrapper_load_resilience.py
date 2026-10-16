"""B189: the live wrapper must survive a loaded host. A saturated CPU made mvn_snapshot exceed its timeout, the snapshot
went stale and the supervisor restarted the loop over and over. Source-level checks on start-trading-day.ps1."""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = open(os.path.join(ROOT, "scripts", "core", "start-trading-day.ps1"), encoding="utf-8").read()


class WrapperLoad(unittest.TestCase):
    def test_wrapper_runs_above_normal_so_children_inherit(self):
        self.assertRegex(SRC, r"\(Get-Process -Id \$PID\)\.PriorityClass\s*=\s*'AboveNormal'")

    def test_priority_raise_cannot_abort_the_wrapper(self):
        m = re.search(r"try \{ \(Get-Process -Id \$PID\)\.PriorityClass[^\n]*\}", SRC)
        self.assertIsNotNone(m, "the priority raise must sit in try/catch (access denied must not stop the loop)")

    def test_snapshot_timeout_leaves_room_under_load(self):
        m = re.search(r"-TimeoutSec\s+(\d+)\s+-Tag\s+\"mvn_snapshot\"", SRC)
        self.assertIsNotNone(m)
        self.assertGreaterEqual(int(m.group(1)), 180)   # observed 2026-10-16: 90 s timed out 4 times in 25 min at 100% host CPU

    def test_snapshot_runs_java_directly_with_mvn_fallback(self):
        # B191: no Maven JVM start per cycle; a missing classpath or a failed direct run must fall back, never skip the snapshot.
        self.assertIn("function Get-DirectSnapshotCmd", SRC)
        self.assertIn('-Tag "java_snapshot"', SRC)
        self.assertRegex(SRC, r'if \(\$null -eq \$rc\) \{\s*\$rc = Invoke-WithTimeout[^\n]*"mvn_snapshot"')
        self.assertIn("falling back to mvn", SRC)

    def test_classpath_build_failure_is_not_retried_every_cycle(self):
        self.assertIn("$script:CpRetryAfter = (Get-Date).AddMinutes(30)", SRC)

    def test_direct_helper_cannot_throw_into_the_loop(self):
        body = SRC[SRC.index("function Get-DirectSnapshotCmd"):SRC.index("function Invoke-WithTimeout")]
        self.assertIn("} catch { return $null }", body)


if __name__ == "__main__":
    unittest.main()
