"""Unit tests for scripts/dev/traffic_report.py.

Verifies commit classification (merge, claim, release, other), overhead calculation,
percent formatting without zero-division, and custom hours parsing. Offline (mocked runner).
"""
import pathlib
import sys
import unittest
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import traffic_report as tr  # noqa: E402


class FakeCompletedProcess:
    def __init__(self, stdout):
        self.stdout = stdout


class TrafficReportTest(unittest.TestCase):
    def test_classify_merge_with_multiple_parents(self):
        self.assertEqual(tr.classify("Merge branch 'fast-track' into foo", 2), "merge")
        self.assertEqual(tr.classify("Merge remote-tracking branch", 3), "merge")

    def test_classify_merge_takes_precedence_over_claim_or_release_keyword(self):
        # A merge commit whose subject starts with claim or release is still classified as a merge
        self.assertEqual(tr.classify("claim task-x", 2), "merge")
        self.assertEqual(tr.classify("release task-x", 2), "merge")

    def test_classify_claim_keyword(self):
        self.assertEqual(tr.classify("claim ask-p0-12", 1), "claim")
        self.assertEqual(tr.classify("CLAIM ask-p0-12", 1), "claim")
        self.assertEqual(tr.classify("claim", 0), "claim")

    def test_classify_release_keyword(self):
        self.assertEqual(tr.classify("release ask-p0-12", 1), "release")
        self.assertEqual(tr.classify("RELEASE ask-p0-12", 1), "release")
        self.assertEqual(tr.classify("release", 1), "release")

    def test_classify_other_commit_subjects(self):
        self.assertEqual(tr.classify("Result: add net_longs flags", 1), "other")
        self.assertEqual(tr.classify("claimed something", 1), "other")
        self.assertEqual(tr.classify("releasing something", 1), "other")
        self.assertEqual(tr.classify("", 1), "other")

    def test_report_empty_log_returns_zero_percent_and_no_division_by_zero(self):
        def fake_runner(cmd, capture_output=True, text=True):
            return FakeCompletedProcess("")

        expected = (
            "last 24 h on origin/fast-track: 0 commits | "
            "merge 0 (0%) | claim 0 (0%) | release 0 (0%) | other 0 (0%) | "
            "overhead 0 (0%)"
        )
        self.assertEqual(tr.report(hours=24, runner=fake_runner), expected)

    def test_report_mix_of_all_kinds(self):
        lines = [
            "p1 p2|Merge branch 'feat'",
            "p1|claim task-foo",
            "p1|release task-foo",
            "p1|Result: completed task",
        ]

        def fake_runner(cmd, capture_output=True, text=True):
            return FakeCompletedProcess("\n".join(lines))

        expected = (
            "last 24 h on origin/fast-track: 4 commits | "
            "merge 1 (25%) | claim 1 (25%) | release 1 (25%) | other 1 (25%) | "
            "overhead 3 (75%)"
        )
        self.assertEqual(tr.report(hours=24, runner=fake_runner), expected)

    def test_report_respects_custom_hours_argument_and_passes_to_git(self):
        called_cmd = []

        def fake_runner(cmd, capture_output=True, text=True):
            called_cmd.append(cmd)
            return FakeCompletedProcess("p1|Result: work")

        res = tr.report(hours=72, runner=fake_runner)
        self.assertEqual(len(called_cmd), 1)
        self.assertEqual(
            called_cmd[0],
            ["git", "log", "origin/fast-track", "--since=72 hours ago", "--format=%P|%s"],
        )
        self.assertTrue(res.startswith("last 72 h on origin/fast-track: 1 commits"))

    def test_report_rounding_and_counts(self):
        lines = [
            "p1 p2|Merge remote-tracking branch",
            "p1|Result: part 1",
            "p1|Result: part 2",
        ]

        def fake_runner(cmd, capture_output=True, text=True):
            return FakeCompletedProcess("\n".join(lines))

        expected = (
            "last 12 h on origin/fast-track: 3 commits | "
            "merge 1 (33%) | claim 0 (0%) | release 0 (0%) | other 2 (67%) | "
            "overhead 1 (33%)"
        )
        self.assertEqual(tr.report(hours=12, runner=fake_runner), expected)


if __name__ == "__main__":
    unittest.main()
