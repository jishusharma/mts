"""Test tasks.py done --next validation and tasks.py drop subcommand.

Done when:
1. done --next none exits nonzero with the same message ship gives
2. free text creates no card
3. tasks.py drop sets state dropped with reason
"""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tasks as T
import sync


def good_card(cid="B900", **kw):
    c = T.blank(cid, "Card for next tag testing")
    c.update(
        lane="SONNET",
        size="S",
        goal="Valid goal",
        scope_in=["scripts/dev/tasks.py"],
        steps=["step 1", "step 2"],
        tests="test_tasks_next_tag.py",
        done_when="done",
        state="ready",
        est_turns=5,
        worker="agent",
    )
    c.update(kw)
    return c


def run_cli(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            rc = T.main(list(argv))
        except SystemExit as e:
            rc = e.code if isinstance(e.code, int) else 1
            if isinstance(e.code, str):
                out.write(e.code)
    return rc, out.getvalue()


class TasksNextTagTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.old_repo = T.REPO
        T.REPO = self.repo
        (self.repo / T.DIR).mkdir(parents=True, exist_ok=True)
        c = good_card("B900")
        T.save(self.repo, c)

    def tearDown(self):
        T.REPO = self.old_repo
        self.tmp.cleanup()

    def test_done_next_none_exits_nonzero_with_ship_message(self):
        expected_msg = (
            f'ship refused: Next card none does not exist; file it '
            f'(tasks.py new "<title>" --id none) or {sync.NEXT_FIX}'
        )
        rc, out = run_cli("done", "B900", "--result", "done result", "--next", "none")
        self.assertNotEqual(rc, 0)
        self.assertIn(expected_msg, out)

    def test_done_next_none_fails_even_if_none_card_exists(self):
        expected_msg = (
            f'ship refused: Next card none does not exist; file it '
            f'(tasks.py new "<title>" --id none) or {sync.NEXT_FIX}'
        )
        none_card = good_card("none")
        T.save(self.repo, none_card)
        rc, out = run_cli("done", "B900", "--result", "done result", "--next", "none")
        self.assertNotEqual(rc, 0)
        self.assertIn(expected_msg, out)

    def test_free_text_creates_no_card(self):
        cards_before = set(self.repo.glob(f"{T.DIR}/*.json"))
        rc, out = run_cli("done", "B900", "--result", "done result", "--next", "fix the broken parser")
        self.assertNotEqual(rc, 0)
        cards_after = set(self.repo.glob(f"{T.DIR}/*.json"))
        self.assertEqual(cards_before, cards_after, "free text --next must not create junk cards")
        expected_msg = (
            f'ship refused: Next card fix does not exist; file it '
            f'(tasks.py new "<title>" --id fix) or {sync.NEXT_FIX}'
        )
        self.assertIn(expected_msg, out)

    def test_tasks_drop_sets_state_dropped_with_reason(self):
        rc, out = run_cli("drop", "B900", "--reason", "obsolete duplicate card")
        self.assertEqual(rc, 0, f"tasks.py drop failed: {out}")
        c = T.get(self.repo, "B900")
        self.assertEqual(c["state"], "dropped")
        self.assertTrue(
            "obsolete duplicate card" in c.get("note", "") or c.get("reason") == "obsolete duplicate card",
            f"expected reason in card, got note={c.get('note')} reason={c.get('reason')}",
        )

    def test_tasks_drop_requires_reason(self):
        rc, out = run_cli("drop", "B900")
        self.assertNotEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
