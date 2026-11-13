"""Delivery modes of gemini_queue (operator 2026-11-13): review pushes only gemini-q/<id>, solo ships, review-list shows waiting branches."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import gemini_queue as gq  # noqa: E402


def cp(rc, out="", err=""):
    return subprocess.CompletedProcess([], rc, stdout=out, stderr=err)


class Delivery(unittest.TestCase):
    def run_deliver(self, mode, log_text="x\nCHECKS: pass 3 tests\n"):
        d = Path(tempfile.mkdtemp())
        log = d / "c.log"
        log.write_text(log_text, encoding="utf-8")

        def fake_git(*a, **k):
            if a[0] == "rev-list":
                return cp(0, "2\n")
            if a[0] == "diff":
                return cp(0, "a.md\nb.py\n")
            return cp(0)
        with mock.patch.object(gq, "git", side_effect=fake_git) as g, mock.patch.object(gq, "sh", return_value=cp(0)) as sh:
            gq.deliver("c", d, log, mode)
        return log.read_text(encoding="utf-8").splitlines()[-1], g, sh

    def test_review_pushes_branch_only_and_reports(self):
        line, g, sh = self.run_deliver("review")
        self.assertEqual(line, "REVIEW gemini-q/c files=2 checks=pass 3 tests")
        pushes = [c.args for c in g.call_args_list if c.args[0] == "push"]
        self.assertEqual(pushes, [("push", "origin", "gemini-q/c")])
        self.assertFalse(sh.called)   # no sync.py ship

    def test_solo_ships(self):
        line, g, sh = self.run_deliver("solo")
        self.assertEqual(line, "SOLO SHIPPED c")
        self.assertIn("ship", sh.call_args.args[0])
        self.assertFalse([c for c in g.call_args_list if c.args[0] == "push"])

    def test_missing_checks_line_says_none(self):
        line, _, _ = self.run_deliver("review", "no check line\n")
        self.assertTrue(line.endswith("checks=none"))

    def test_review_list_prints_only_branches_ahead(self):
        def fake_git(*a, **k):
            if a[0] == "for-each-ref":
                return cp(0, "origin/gemini-q/a\norigin/gemini-q/b\n")
            if a[0] == "rev-list":
                return cp(0, "0\n" if a[2].endswith("..origin/gemini-q/a") else "1\n")
            if a[0] == "diff":
                return cp(0, "f.md\n")
            return cp(0)
        with mock.patch.object(gq, "git", side_effect=fake_git), mock.patch("builtins.print") as p:
            gq.review_list()
        out = "\n".join(str(c.args[0]) for c in p.call_args_list)
        self.assertIn("REVIEW gemini-q/b commits=1 files=1", out)
        self.assertNotIn("gemini-q/a", out)

    def test_spec_accepts_mode_token(self):
        calls = []
        with mock.patch.object(gq, "run_job", side_effect=lambda *a: calls.append(a)), mock.patch.object(gq.AGY.__class__, "is_file", return_value=True):
            gq.main(["run", "card1:low:review", "card2"])
        self.assertEqual(calls, [("card1", "low", "flash", "review"), ("card2", "low", "flash", "solo")])


if __name__ == "__main__":
    unittest.main()
