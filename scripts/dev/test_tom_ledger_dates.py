"""Ledger date column: observed trade date or empty (RV01 D4). Red on 2868d6c-era CSV."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tom_ledger_dates as t  # noqa: E402


def row(id_, date="", status="NOT_IN_DATA", inferred="", rec="", gid=None):
    return {"id": id_, "date": date, "trade_date_status": status, "trade_date_inferred": inferred,
            "recording_date_observed": rec, "canonical_id": gid or id_}


class Fixture(unittest.TestCase):
    def test_flags_iso_date_with_not_in_data(self):
        self.assertTrue(t.violations([row("A", "2026-05-19")]))

    def test_flags_prose_date(self):
        self.assertTrue(t.violations([row("A", "2026-06-08 (recording clock)")]))

    def test_flags_group_disagreement(self):
        v = t.violations([row("A", inferred="2026-05-18", gid="G"), row("B", inferred="2026-05-19", gid="G")])
        self.assertTrue(any("group G" in x for x in v))

    def test_clean_rows_pass(self):
        self.assertEqual(t.violations([row("A"), row("B", "2026-05-01", "OBSERVED order frame")]), [])

    def test_fix_moves_value_and_is_idempotent(self):
        rows = [row("A", "2026-05-19", "ASSUMED same day"), row("B", "2026-06-02(x)", "NOT_IN_DATA")]
        t.fix_rows(rows)
        self.assertEqual((rows[0]["date"], rows[0]["trade_date_inferred"]), ("", "2026-05-19"))
        self.assertEqual((rows[1]["date"], rows[1]["trade_date_inferred"], rows[1]["date_legacy_unverified"]),
                         ("", "", "2026-06-02"))
        snap = [dict(r) for r in rows]
        t.fix_rows(rows)
        self.assertEqual(rows, snap)
        self.assertEqual(t.violations(rows), [])


class Committed(unittest.TestCase):
    def test_committed_ledger_has_zero_violations(self):
        rows, _ = t.read(t.LEDGER)
        groups, _ = t.read(t.GROUPS)
        self.assertEqual(t.violations(rows, groups), [])


if __name__ == "__main__":
    unittest.main()
