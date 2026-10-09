"""B153: Python and Java net_rr share ONE table of hand-worked vectors (tests/fixtures/net_rr_vectors.json, FORMULAS.md s17).
Java side: src/test/java/datafeed/NetRRParityFixtureTest.java reads the same file. Neither side's expected numbers come from its code."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys" / "runtime"))
import mts_math  # noqa: E402

FIX = ROOT / "MyTradingSys" / "tests" / "fixtures" / "net_rr_vectors.json"


class NetRrParity(unittest.TestCase):
    def test_python_matches_every_vector(self):
        d = json.loads(FIX.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(d["cases"]), 7)
        for c in d["cases"]:
            got = mts_math.calculate_net_rr(c["entry"], c["target"], c["stop"])
            self.assertAlmostEqual(got, c["expected"], delta=d["tolerance"], msg=c["name"])

    def test_java_test_reads_the_same_fixture(self):
        j = (ROOT / "src" / "test" / "java" / "datafeed" / "NetRRParityFixtureTest.java").read_text(encoding="utf-8")
        self.assertIn("net_rr_vectors.json", j)
        self.assertIn("ExecutionMathConstants.netRR", j)


class FloorOwnership(unittest.TestCase):
    """B153: the 1.25 floor is NO-SOURCE; the file must name who decides and by when, so it cannot sit forever on 'restore after P4'
    (P4 is closed as NO REPLICATION and does not trigger anything)."""

    def test_floor_file_names_a_decision_and_a_review_date(self):
        from datetime import date
        d = json.loads((ROOT / "MyTradingSys" / "system" / "net_rr_floor.json").read_text(encoding="utf-8-sig"))
        self.assertTrue(d.get("decision_owner"), "decision_owner missing")
        date.fromisoformat(d["review_by_utc"])   # raises if absent or malformed
        self.assertIn("review", d.get("on_review", ""))

    def test_floor_reader_still_reads_only_the_number(self):
        import net_rr_floor
        self.assertGreater(net_rr_floor.load_floor(), 0)


if __name__ == "__main__":
    unittest.main()
