import unittest
from datetime import datetime, timezone

import dsa_watch

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)


class SummarizeTest(unittest.TestCase):
    def test_old_pending_row_is_stalled(self):
        rows = [{"target": "DSA-NUC", "status": "pending", "posted": "2026-11-01T06:00:00Z"}]
        got = {r[0]: r for r in dsa_watch.summarize(rows, NOW, 3)}
        self.assertEqual(got["DSA-NUC"][4], "STALLED")
        self.assertEqual(got["DSA-NB"][4], "EMPTY")

    def test_fresh_pending_row_is_ok(self):
        rows = [{"target": "DSA-NB", "status": "pending", "posted": "2026-11-01T11:00:00Z"}]
        got = {r[0]: r for r in dsa_watch.summarize(rows, NOW, 3)}
        self.assertEqual(got["DSA-NB"][4], "OK")

    def test_taken_row_is_not_stalled(self):
        rows = [{"target": "DSA", "status": "taken", "posted": "2026-11-01T01:00:00Z"}]
        got = {r[0]: r for r in dsa_watch.summarize(rows, NOW, 3)}
        self.assertEqual(got["DSA"][4], "OK")


if __name__ == "__main__":
    unittest.main()
