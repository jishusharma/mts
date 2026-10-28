"""ANNOUNCEMENTS.md ids are unique and the next id for a date is max+1 (card announcements-ids-are-reused)."""
import re
import unittest
from collections import Counter
from pathlib import Path

ANN = Path(__file__).resolve().parents[2] / "MyTradingSys" / "system" / "ANNOUNCEMENTS.md"
ID_RE = re.compile(r"^### (A-(\d{8})-(\d+))\b", re.M)


def ids(text):
    return [m.group(1) for m in ID_RE.finditer(text)]


def next_id(text, yyyymmdd):
    """Next free id for a date: highest existing number for that date + 1 (never a gap-fill, never a reuse)."""
    nums = [int(m.group(3)) for m in ID_RE.finditer(text) if m.group(2) == yyyymmdd]
    return f"A-{yyyymmdd}-{max(nums, default=0) + 1}"


class AnnouncementIds(unittest.TestCase):
    def test_ids_unique(self):
        c = Counter(ids(ANN.read_text(encoding="utf-8")))
        self.assertEqual([i for i, n in c.items() if n > 1], [])
        self.assertTrue(c)

    def test_ids_unique_fixture_catches_repeat(self):
        c = Counter(ids("### A-20261018-1 INFO a\n### A-20261018-2 INFO b\n### A-20261018-1 INFO c\n"))
        self.assertEqual([i for i, n in c.items() if n > 1], ["A-20261018-1"])

    def test_next_id_is_max_plus_one(self):
        t = "### A-20261018-1 INFO a\n### A-20261018-8 INFO b\n### A-20261018-5 HOLD c\n### A-20261019-1 INFO d\n"
        self.assertEqual(next_id(t, "20261018"), "A-20261018-9")
        self.assertEqual(next_id(t, "20261019"), "A-20261019-2")
        self.assertEqual(next_id(t, "20261020"), "A-20261020-1")

    def test_next_id_on_live_file_is_unused(self):
        t = ANN.read_text(encoding="utf-8")
        self.assertNotIn(next_id(t, "20261018"), ids(t))


if __name__ == "__main__":
    unittest.main()
