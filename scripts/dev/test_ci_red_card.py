"""ci_red_card: red CI on fast-track -> one pinned fix card naming the first failing commit; none when green; never twice."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
