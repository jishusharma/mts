"""tasks-done-refuses-raw-card-with-finished-work-1112: `tasks.py done <raw card> --sha <shipped sha>` closes the card in one command.

Done when:
1. a raw card whose --sha is on origin/fast-track closes to done (fails on the old cmd_done, which refused every raw card)
2. the same card with a sha that is not on trunk is refused
3. a raw card with no --sha is still refused with the old message
"""
import argparse
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "dev"))
import tasks as T  # noqa: E402


def raw_card(cid="routine-test-raw-1113"):
    return {"id": cid, "title": "raw card with finished work", "state": "raw", "lane": "HAIKU", "prio": 3}


def args(cid, sha=""):
    return argparse.Namespace(id=cid, result="work is on trunk", next="END: test", sha=sha)


class DoneRawCardTest(unittest.TestCase):
    def _run(self, card, sha, on_trunk):
        saved = {}
        with mock.patch.object(T, "get", return_value=card), \
                mock.patch.object(T, "on_trunk", return_value=on_trunk), \
                mock.patch.object(T, "review_gate", return_value=[]), \
                mock.patch.object(T, "mark_shared_bases", return_value=None), \
                mock.patch.object(T, "route_next", side_effect=lambda c, n: n), \
                mock.patch.object(T.TS, "git", return_value="abc1234"), \
                mock.patch.object(T, "save", side_effect=lambda repo, c: saved.update(c) or "p"), \
                mock.patch("builtins.print"):
            T.cmd_done(args(card["id"], sha))
        return saved

    def test_raw_card_with_shipped_sha_closes_in_one_command(self):
        saved = self._run(raw_card(), "41ee83dba", on_trunk=True)
        self.assertEqual(saved["state"], "done")
        self.assertEqual(saved["result"], "work is on trunk")

    def test_raw_card_with_sha_not_on_trunk_is_refused(self):
        with self.assertRaises(SystemExit) as cm:
            self._run(raw_card(), "deadbeef", on_trunk=False)
        self.assertIn("not on origin/fast-track", str(cm.exception))

    def test_raw_card_without_sha_is_still_refused(self):
        with self.assertRaises(SystemExit) as cm:
            self._run(raw_card(), "", on_trunk=True)
        self.assertIn("only a ready or active card can be marked done", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
