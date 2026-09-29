"""Offline tests for journal env recording (spec 126). Derived from the spec, not from the implementation."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import journal


class JournalEnvTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="jenv_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        p = mock.patch.object(journal, "JOURNAL_DIR", self.tmp)
        p.start()
        self.addCleanup(p.stop)

    def test_intent_without_env_is_refused_and_writes_nothing(self):
        with self.assertRaises(ValueError):
            journal.append_event("p1", "intent", {"compiled": {}})
        self.assertEqual(journal.read_events("p1"), [])

    def test_intent_with_bad_env_is_refused(self):
        for bad in (None, "", "prod", "TEST", 1):
            with self.assertRaises(ValueError):
                journal.append_event("p1", "intent", {"env": bad})
        self.assertEqual(journal.read_events("p1"), [])

    def test_intent_with_valid_env_is_recorded(self):
        journal.append_event("p1", "intent", {"env": "mainnet", "compiled": {}})
        journal.append_event("p2", "intent", {"env": "test"})
        self.assertEqual(journal.plan_env("p1"), "mainnet")
        self.assertEqual(journal.plan_env("p2"), "test")

    def test_other_event_types_do_not_need_env(self):
        journal.append_event("p3", "order_placed", {"order_id": "o", "label": "l", "side": "BUY", "amount": 10})
        self.assertEqual(len(journal.read_events("p3")), 1)
        self.assertIsNone(journal.plan_env("p3"))  # no intent event

    def test_plan_env_unknown_plan_is_none(self):
        self.assertIsNone(journal.plan_env("nope"))

    def test_legacy_intent_without_env_counts_as_test(self):
        # journals written before env recording existed: write the raw line, bypassing append_event
        (self.tmp / "old.jsonl").write_text(
            '{"ts": 1.0, "plan_id": "old", "event_type": "intent", "data": {"compiled": {}}}\n', encoding="utf-8")
        self.assertEqual(journal.plan_env("old"), "test")

    def test_assert_env_match_passes(self):
        journal.append_event("p1", "intent", {"env": "mainnet"})
        journal.assert_env("p1", "mainnet")  # no raise
        journal.assert_env("never_ran", "mainnet")  # no journal -> nothing to contradict

    def test_assert_env_mismatch_raises_both_directions(self):
        journal.append_event("m", "intent", {"env": "mainnet"})
        journal.append_event("t", "intent", {"env": "test"})
        with self.assertRaises(journal.EnvMismatch) as c:
            journal.assert_env("m", "test")
        self.assertIn("mainnet", str(c.exception))
        with self.assertRaises(journal.EnvMismatch):
            journal.assert_env("t", "mainnet")

    def test_legacy_journal_refused_on_mainnet(self):
        (self.tmp / "old.jsonl").write_text(
            '{"ts": 1.0, "plan_id": "old", "event_type": "intent", "data": {}}\n', encoding="utf-8")
        with self.assertRaises(journal.EnvMismatch):
            journal.assert_env("old", "mainnet")

    def test_assert_env_writes_nothing(self):
        journal.append_event("m", "intent", {"env": "mainnet"})
        before = (self.tmp / "m.jsonl").read_text(encoding="utf-8")
        with self.assertRaises(Exception):
            journal.assert_env("m", "test")
        self.assertEqual((self.tmp / "m.jsonl").read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
