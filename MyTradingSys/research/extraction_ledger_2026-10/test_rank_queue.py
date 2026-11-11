"""Fixture: two ON_DISK ids, one titled 'absorption delta'; it must rank first and the row count must hold."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rank_queue as rq  # noqa: E402

GAPS = """# gaps
## Transcript but no extract (3)

- AAAAAAAAAAA
- BBBBBBBBBBB
- CCCCCCCCCCC

## Priority id with no transcript (2)

- DDDDDDDDDDD
- EEEEEEEEEEE

## Extract with no id (0)
"""


def tr(d, vid, title, body="x"):
    (d / f"{vid}_raw.txt").write_text(f"# Video ID: {vid}\n# Title: {title}\n# ---\n{body}\n", encoding="utf-8")


class RankTest(unittest.TestCase):
    def test_rank_and_counts(self):
        d = Path(tempfile.mkdtemp())
        tr(d, "AAAAAAAAAAA", "Plain chat", "nothing")
        tr(d, "BBBBBBBBBBB", "absorption delta", "x")
        (d / "CCCCCCCCCCC_raw.txt").write_text("no header here\n", encoding="utf-8")
        prio = {"DDDDDDDDDDD": ("Footprint basics", "Tom"), "EEEEEEEEEEE": ("Footprint basics", "Krown")}
        on, fetch, nt = rq.build(GAPS, d, prio, {})
        self.assertEqual(on[0]["id"], "BBBBBBBBBBB")
        self.assertEqual(len(on) + len(nt), 3)
        self.assertEqual([nt[0][0]], ["CCCCCCCCCCC"])
        self.assertEqual([r["id"] for r in fetch], ["DDDDDDDDDDD", "EEEEEEEEEEE"])  # tie: Tom first
        out = rq.render(on, fetch, nt)
        self.assertIn("## ON_DISK (2)", out)
        self.assertIn("## TO_FETCH (2)", out)

    def test_body_keywords_count(self):
        d = Path(tempfile.mkdtemp())
        tr(d, "AAAAAAAAAAA", "Chat", "delta delta liquidation")
        tr(d, "BBBBBBBBBBB", "Chat2", "nothing")
        on, _, _ = rq.build(GAPS, d, {}, {})
        self.assertEqual((on[0]["id"], on[0]["score"]), ("AAAAAAAAAAA", 3))


if __name__ == "__main__":
    unittest.main()
