"""INDEX.md and BUGS.md must agree on the status of every id they both list (offline, no network).

items/INDEX.md allows a wider status vocabulary than research/BUGS.md (OPEN, IN-FIX, BLOCKED, CLOSED, WONTFIX).
INDEX_TO_BUGS maps the INDEX-only words onto the BUGS word they mean; an unmapped INDEX word is itself a failure.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "MyTradingSys"
INDEX = ROOT / "items" / "INDEX.md"
BUGS = ROOT / "research" / "BUGS.md"

BUGS_STATUSES = {"OPEN", "IN-FIX", "BLOCKED", "CLOSED", "WONTFIX"}
INDEX_TO_BUGS = {
    "PARKED": "BLOCKED",   # operator parked = blocked until lifted (T051)
    "DONE": "CLOSED",
}
ID_RE = re.compile(r"^[BT]\d{3}$")


def norm(status):
    return INDEX_TO_BUGS.get(status, status)


def parse_index(text):
    out = {}
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 3 and ID_RE.match(cells[0]):
            out[cells[0]] = cells[1]
    return out


def parse_bugs(text):
    out = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 5 and cells[0] == "" and ID_RE.match(cells[1]):
            out[cells[1]] = cells[3]
    return out


class RegistryConsistencyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = parse_index(INDEX.read_text(encoding="utf-8"))
        cls.bugs = parse_bugs(BUGS.read_text(encoding="utf-8"))

    def test_parsers_find_rows(self):
        self.assertGreater(len(self.index), 50)
        self.assertGreater(len(self.bugs), 50)

    def test_parser_units(self):
        self.assertEqual(parse_index("T051 | PARKED  | f.md | x\n# B001 | OPEN | f | x"), {"T051": "PARKED"})
        self.assertEqual(parse_bugs("| T051 | 2026-09-26 | BLOCKED | MED | t | e | - |"), {"T051": "BLOCKED"})

    def test_bugs_statuses_in_vocabulary(self):
        bad = {i: s for i, s in self.bugs.items() if s not in BUGS_STATUSES}
        self.assertEqual(bad, {}, "BUGS.md status outside OPEN/IN-FIX/BLOCKED/CLOSED/WONTFIX")

    def test_shared_ids_agree(self):
        diff = {i: (self.index[i], self.bugs[i]) for i in sorted(set(self.index) & set(self.bugs))
                if norm(self.index[i]) != self.bugs[i]}
        self.assertEqual(diff, {}, "INDEX vs BUGS status differs (id: (INDEX, BUGS))")


if __name__ == "__main__":
    unittest.main()
