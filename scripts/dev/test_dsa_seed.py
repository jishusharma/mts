"""Seed lists the DSA queue and DSA's own filings (card dsa-seed-full-task-list-1107)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dsa  # noqa: E402


def card(cid, lane, state="ready", created="2026-11-01T00:00:00Z", **kw):
    return dict({"id": cid, "title": f"title {cid}", "lane": lane, "state": state, "created": created, "prio": 3}, **kw)


class SeedQueue(unittest.TestCase):
    def repo(self, cards, rows):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        root = Path(d.name)
        (root / "MyTradingSys/system/tasks").mkdir(parents=True)
        (root / "MyTradingSys/system/desk_queue").mkdir(parents=True)
        for c in cards:
            (root / "MyTradingSys/system/tasks" / f"{c['id']}.json").write_text(json.dumps(c), encoding="utf-8")
        for r in rows:
            (root / "MyTradingSys/system/desk_queue" / f"{r['id']}.json").write_text(json.dumps(r), encoding="utf-8")
        return root

    def test_queue_lists_open_dsa_cards_and_desk_rows_of_both_hosts(self):
        root = self.repo(
            [card("c-nb", "DSA-NB"), card("c-nuc", "DSA-NUC", "blocked"), card("c-sh", "DSA"), card("c-done", "DSA", "done"),
             card("c-son", "SONNET")],
            [{"id": "r1", "title": "row one", "target": "DSA-NUC", "status": "pending"},
             {"id": "r2", "title": "row two", "target": "DSA-NB", "status": "taken"},
             {"id": "r3", "title": "fin", "target": "DSA", "status": "done"},
             {"id": "r4", "title": "claude", "target": "JIS-NB", "status": "pending"}])
        t = dsa.seed_text("JIS-NB", repo=root)
        self.assertIn("DSA QUEUE (5 open", t)
        for want in ("c-nb", "c-nuc", "c-sh", "r1", "r2"):
            self.assertIn(want, t)
        for no in ("c-done", "c-son", "r3", "r4"):
            self.assertNotIn(no, t)
        self.assertIn("DSA FILED", t)

    def test_filed_is_the_five_newest_cards_naming_dsa(self):
        cs = [card(f"f{i}", "SONNET", created=f"2026-11-0{i}T00:00:00Z", sources=["DSA chat JIS-NB"]) for i in range(1, 8)]
        cs.append(card("other", "SONNET", created="2026-11-09T00:00:00Z", sources=["operator"]))
        t = dsa.seed_text("JIS-NB", repo=self.repo(cs, []))
        filed = t.split("DSA FILED", 1)[1]
        for want in ("f7", "f6", "f5", "f4", "f3"):
            self.assertIn(want, filed)
        for no in ("f2", "f1", "other"):
            self.assertNotIn(no, filed)

    def test_byte_cap_holds_with_a_long_queue(self):
        cs = [card(f"long-card-id-number-{i:03d}", "DSA", title="x" * 80) for i in range(80)]
        t = dsa.seed_text("JIS-NB", repo=self.repo(cs, []))
        self.assertLessEqual(len(t.encode("ascii")), dsa.SEED_MAX_BYTES)
        self.assertIn("more: python scripts/dev/tasks.py list --lane DSA", t)
        for ln in t.splitlines():
            self.assertLess(len(ln), 200)
            self.assertFalse(ln.startswith("#") and not ln.startswith("# AIRUN"), ln)

    def test_empty_repo_says_none(self):
        t = dsa.seed_text("JIS-NB", repo=self.repo([], []))
        self.assertIn("(none)", t)


if __name__ == "__main__":
    unittest.main()
