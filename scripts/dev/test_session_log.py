"""session_log.py: claim..release pairs become session rows; a pair with no work commit in its window is EMPTY;
bookkeeping commits are not 'shipped'; a claim with no release stays open; a release whose claim is outside the window is skipped."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session_log as sl


def c(epoch, subject, result=""):
    return {"h": f"h{epoch}", "epoch": epoch, "subject": subject, "result": result}


class GroupTest(unittest.TestCase):
    def rows(self):
        return [
            c(100, "claim tom-ledger", "sharma on JIS-NUC works on: Tom ledger"),
            c(160, "tom ledger: repairs", "37 rows keyed"),
            c(220, "release tom-ledger", "claim tom-ledger closed"),
            c(300, "claim lab-dax", "sharma on JIS-NUC works on: lab-dax"),
            c(301, "release lab-dax", "claim lab-dax closed"),
            c(400, "claim live-read", "jishusharma on JIS-NB works on: live read"),
            c(450, "desk: taken 2026-row"),
            c(460, "docs: note with no result line"),
            c(500, "release old-claim", "claim old-claim closed"),
        ]

    def test_pairs_empty_open_and_skipped(self):
        g = sl.group(self.rows(), now_epoch=1000)
        by = {u["slug"]: u for u in g["units"]}
        self.assertEqual(set(by), {"tom-ledger", "lab-dax", "live-read"})        # old-claim has no claim in the window
        self.assertFalse(by["tom-ledger"]["empty"])
        self.assertEqual(by["tom-ledger"]["minutes"], 2)
        self.assertEqual(by["tom-ledger"]["host"], "JIS-NUC")
        self.assertTrue(by["lab-dax"]["empty"])                                    # nothing shipped between claim and release
        self.assertIsNone(by["live-read"]["closed"])                               # still open
        self.assertFalse(by["live-read"]["empty"])                                 # an open session is never called empty
        self.assertEqual(by["live-read"]["host"], "JIS-NB")
        self.assertEqual(by["live-read"]["minutes"], 10)

    def test_stats_and_shipped_drop_bookkeeping(self):
        g = sl.group(self.rows(), now_epoch=1000)
        s = g["stats"]
        self.assertEqual((s["sessions"], s["closed"], s["open"], s["empty"]), (3, 2, 1, 1))
        self.assertEqual(s["commits"], 9)
        self.assertEqual(s["bookkeeping"], 7)                                      # 3 claims, 3 releases, 1 desk row
        self.assertEqual(s["no_result"], 1)
        self.assertEqual([w["subject"] for w in g["shipped"]], ["docs: note with no result line", "tom ledger: repairs"])

    def test_no_rows(self):
        g = sl.group([], now_epoch=1)
        self.assertEqual(g["units"], [])
        self.assertIsNone(g["stats"]["median_min"])

    def test_view_shape_is_page_safe(self):
        v = sl.view(Path("Z:/no/such/repo"), hours=1)                              # git fails -> empty page data, no exception
        self.assertEqual(v["units"], [])
        self.assertEqual(v["stats"]["sessions"], 0)


if __name__ == "__main__":
    unittest.main()
