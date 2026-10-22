"""ci_red_card: red CI on fast-track -> one pinned fix card naming the first failing commit; none when green; never twice."""
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

CI_YML = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ci_red_card as crc
import tasks


def run(i, sha, conclusion, status="completed"):
    return {"databaseId": i, "headSha": sha * 40, "conclusion": conclusion, "status": status, "createdAt": f"2026-10-16T0{i}:00:00Z", "url": f"https://x/{i}"}


class RedCard(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_first_failing_is_oldest_of_the_unbroken_failure_chain(self):
        runs = [run(5, "e", "failure"), run(4, "d", "cancelled"), run(3, "c", "failure"), run(2, "b", "success"), run(1, "a", "failure")]
        self.assertEqual(crc.first_failing(runs)["headSha"], "c" * 40)

    def test_green_or_running_head_files_nothing(self):
        self.assertIsNone(crc.first_failing([run(3, "c", "success"), run(2, "b", "failure")]))
        self.assertIsNone(crc.first_failing([run(3, "c", None, "in_progress"), run(2, "b", "success")]))
        self.assertIsNone(crc.first_failing([]))

    def test_files_one_pinned_card_that_passes_the_definition_of_ready(self):
        runs = [run(3, "c", "failure"), run(2, "b", "failure"), run(1, "a", "success")]
        action, _ = crc.run(self.tmp, True, runs)
        self.assertEqual(action, "FILED")
        card = json.loads((self.tmp / tasks.DIR / "ci-bbbbbbb.json").read_text(encoding="utf-8"))
        self.assertEqual((card["state"], card["prio"], card["pinned"], card["lane"]), ("ready", 0, True, "SONNET"))
        self.assertIn("bbbbbbb", card["title"])
        self.assertEqual(tasks.problems(card), [])
        self.assertEqual(tasks.rank(card) < tasks.rank({**card, "pinned": False, "prio": 1}), True)

    def test_second_look_and_second_failing_push_on_same_break_file_nothing(self):
        runs = [run(2, "b", "failure"), run(1, "a", "success")]
        crc.run(self.tmp, True, runs)
        self.assertEqual(crc.run(self.tmp, True, runs)[0], "EXISTS")
        again = [run(3, "c", "failure")] + runs   # a newer push, same break: same first failing commit
        self.assertEqual(crc.run(self.tmp, True, again)[0], "EXISTS")
        self.assertEqual(len(list((self.tmp / tasks.DIR).glob("*.json"))), 1)

    def test_dry_run_writes_nothing_and_unknown_is_not_red(self):
        self.assertEqual(crc.run(self.tmp, False, [run(2, "b", "failure")])[0], "WOULD_FILE")
        self.assertFalse((self.tmp / tasks.DIR).exists())
        crc.fetch_runs = lambda repo, limit=30: None
        self.assertEqual(crc.run(self.tmp, True)[0], "UNKNOWN")


def cancel_in_progress(ref):
    """Evaluate the cancel-in-progress line of ci.yml's top-level concurrency block for a ref (a true/false literal or one github.ref comparison)."""
    text = CI_YML.read_text(encoding="utf-8")
    block = re.search(r"^concurrency:\n((?:[ \t]+.*\n)+)", text, re.M).group(1)
    val = re.search(r"^\s+cancel-in-progress:\s*(.+?)\s*$", block, re.M).group(1)
    if val in ("true", "false"):
        return val == "true"
    m = re.fullmatch(r"\$\{\{\s*github\.ref\s*(==|!=)\s*'([^']+)'\s*\}\}", val)
    assert m, f"cancel-in-progress is not a literal or a github.ref comparison: {val}"
    return (ref == m.group(2)) == (m.group(1) == "==")


class CiConcurrency(unittest.TestCase):
    """fast-track gets a merge every few minutes and a run takes ~6 min: cancelling the running push job starved mark-green
    (runs 38825243976 and 38824936295 were cancelled). A fast-track run now finishes; GitHub keeps only the newest pending one."""

    def test_running_fast_track_run_is_not_cancelled_but_other_refs_still_are(self):
        self.assertFalse(cancel_in_progress("refs/heads/fast-track"))
        self.assertTrue(cancel_in_progress("refs/pull/123/merge"))
        self.assertTrue(cancel_in_progress("refs/heads/some-branch"))

    def test_group_is_per_sha_on_fast_track_and_per_ref_elsewhere(self):
        text = CI_YML.read_text(encoding="utf-8")
        block = re.search(r"^concurrency:\n((?:[ \t]+.*\n)+)", text, re.M).group(1)
        group = re.search(r"^\s+group:\s*(.+?)\s*$", block, re.M).group(1)
        # CI_SPEED_DIAGNOSIS #1: overlapping fast-track pushes must not queue behind each other (11+ min measured)
        self.assertIn("github.sha", group)
        self.assertIn("github.ref", group)      # a PR run never queues behind (or cancels) a fast-track run
        self.assertIn("refs/heads/fast-track", group)

    def test_mark_green_waits_for_the_gate_and_only_moves_the_pointer_forward(self):
        text = CI_YML.read_text(encoding="utf-8")
        mark = text[text.index("\n  mark-green:"):]
        self.assertIn("needs: offline-gate", mark)
        self.assertIn("github.ref == 'refs/heads/fast-track'", mark)
        self.assertIn("fetch-depth: 0", mark)                       # the ancestor guard needs history
        self.assertIn("scripts/dev/mark_green.sh", mark)            # holds the merge-base --is-ancestor guard (tested in test_ship_speed.py)
        self.assertIn("group: mark-green", mark)                    # one at a time: the check and the push cannot interleave
        self.assertNotIn('run: git push --force', mark)             # the unguarded push is gone


if __name__ == "__main__":
    unittest.main()
