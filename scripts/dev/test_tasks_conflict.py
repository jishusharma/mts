"""tasks.py conflict: one deduplicated bug-conflict-<hash> card per pair of contradicting instructions (seen count),
the doctor CONFLICT-OPEN check, and the role_loader hint. Fail-first: the subcommand is absent on the old code."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tasks as T
import mts_doctor as D
import role_loader as RL


class ConflictCardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def cards(self):
        return sorted((self.repo / T.DIR).glob("bug-conflict-*.json"))

    def test_same_pair_twice_and_swapped_is_one_card_seen_2(self):
        T.log_conflict(self.repo, "Hand off after 10 turns", "Keep working", "s1")
        cid, seen = T.log_conflict(self.repo, "  KEEP   working ", "hand off after 10 TURNS", "s2")
        self.assertEqual(seen, 2)
        self.assertEqual(len(self.cards()), 1)
        c = json.loads(self.cards()[0].read_text(encoding="utf-8"))
        self.assertEqual((c["id"], c["seen"], c["prio"], c["lane"], c["last_session"]), (cid, 2, 1, "SONNET", "s2"))

    def test_done_closes_raw_conflict_card(self):
        cid, _ = T.log_conflict(self.repo, "Hand off", "Keep working", "s")
        old, T.REPO = T.REPO, self.repo
        try:
            T.cmd_done(type("A", (), {"id": cid, "result": "operator chose: keep working"}))
        finally:
            T.REPO = old
        c = json.loads((self.repo / T.DIR / f"{cid}.json").read_text(encoding="utf-8"))
        self.assertEqual(c["state"], "done")

    def test_conflict_card_not_refinable(self):
        cid, _ = T.log_conflict(self.repo, "Hand off", "Keep working", "s")
        c = json.loads((self.repo / T.DIR / f"{cid}.json").read_text(encoding="utf-8"))
        self.assertTrue(c["asks"].startswith("Which holds:") and len(c["asks"]) <= 300)
        self.assertFalse(T.refinable(c))

    def test_different_pair_makes_second_card(self):
        T.log_conflict(self.repo, "A", "B")
        T.log_conflict(self.repo, "A", "C")
        self.assertEqual(len(self.cards()), 2)

    def test_cli_subcommand(self):
        old, T.REPO = T.REPO, self.repo
        try:
            rc = T.cmd_conflict(type("A", (), {"text": ["x | y"], "session": "s"}))
        finally:
            T.REPO = old
        self.assertIsNone(rc)
        self.assertEqual(len(self.cards()), 1)
        self.assertEqual(T.conflict_key("x", "y"), T.conflict_key("Y", "x"))


class DoctorAndHintTest(unittest.TestCase):
    def test_doctor_warns_over_three_open(self):
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            for i in range(4):
                T.log_conflict(repo, f"a{i}", f"b{i}")
            self.assertEqual(D.conflict_open(repo)[0], "WARN")
            for p in (repo / T.DIR).glob("bug-conflict-*.json"):
                c = json.loads(p.read_text(encoding="utf-8"))
                c["state"] = "done"
                p.write_text(json.dumps(c), encoding="utf-8")
            self.assertEqual(D.conflict_open(repo)[0], "OK")
        self.assertIn("CONFLICT-OPEN", D.CHECK_NAMES)

    def test_role_loader_text_carries_conflict_hint(self):
        old = RL._build_text
        RL._build_text = lambda *x, **k: "FIXTURE ROLE BODY\n"
        try:
            out = RL.build_text("Fixture", Path("."), True)
        finally:
            RL._build_text = old
        self.assertIn("FIXTURE ROLE BODY", out)
        self.assertIn("tasks.py conflict", out)

    def test_claude_md_precedence_puts_hard_rules_first(self):
        t = (Path(__file__).resolve().parents[2] / "CLAUDE.md").read_text(encoding="utf-8")
        line = next(l for l in t.splitlines() if l.startswith("- Precedence:"))
        self.assertLess(line.index("Hard rules"), line.index("operator order"))
        self.assertIn("outrank", line)
        self.assertIn("TRAFFIC_BUSTERS B20", line)


if __name__ == "__main__":
    unittest.main()
