"""B152: retention keeps what other tools read and never trims irreversibly."""
import gzip
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("retention", ROOT / "scripts" / "dev" / "retention.py")
ret = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ret)


class RetentionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_nuc_done_entries_are_not_deleted_audit_digest_reads_them(self):
        d = self.root / "Dumps" / "workers" / "NUC-QUEUE" / "done" / "old1"
        d.mkdir(parents=True)
        (d / "x.task.json").write_text("{}", encoding="utf-8")
        old = os.path.getmtime(d) - 40 * 86400
        os.utime(d, (old, old))
        self.assertEqual([i for i in ret.plan(str(self.root)) if "NUC-QUEUE" in i[1]], [])

    def test_policy_doc_does_not_promise_deleting_nuc_done(self):
        # the code skips NUC-QUEUE/done on purpose (above); the policy row must say who reads it, not "delete after 14 days"
        text = (ROOT / "MyTradingSys" / "system" / "RETENTION_POLICY.md").read_text(encoding="utf-8")
        rows = [ln for ln in text.splitlines() if ln.startswith("|") and "NUC-QUEUE/done" in ln]
        self.assertEqual(len(rows), 1)
        self.assertNotIn("delete after", rows[0])
        self.assertIn("audit_digest", rows[0])

    def test_subset_check_compares_content_not_only_size(self):
        a, b = self.root / "copy", self.root / "orig"
        a.mkdir(), b.mkdir()
        (a / "f.txt").write_text("abcd", encoding="utf-8")
        (b / "f.txt").write_text("abce", encoding="utf-8")          # same size, different bytes
        self.assertFalse(ret.dup_copy_is_subset(str(a), str(b)))
        (b / "f.txt").write_text("abcd", encoding="utf-8")
        self.assertTrue(ret.dup_copy_is_subset(str(a), str(b)))

    def test_trim_keeps_removed_head_in_a_gzip(self):
        p = self.root / "supervisor_log.txt"
        p.write_text("".join(f"line {i}" + chr(10) for i in range(ret.TAIL_LINES + 10)), encoding="utf-8", newline=chr(10))
        ret.apply([("trim", str(p), p.stat().st_size, "t")])
        kept = p.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(kept), ret.TAIL_LINES)
        gz = list(self.root.glob("supervisor_log.txt.head_*.gz"))
        self.assertEqual(len(gz), 1)
        self.assertEqual(gzip.open(gz[0], "rt", encoding="utf-8").read().splitlines(), [f"line {i}" for i in range(10)])

    def test_trim_keeps_the_logs_mtime_the_canary_reads_it(self):
        # testnet_canary.py check_freshness reads supervisor_log.txt mtime as "last supervisor activity";
        # a daily trim must not turn a dead supervisor into a fresh one
        p = self.root / "supervisor_log.txt"
        p.write_text("".join(f"line {i}" + chr(10) for i in range(ret.TAIL_LINES + 10)), encoding="utf-8", newline=chr(10))
        old = p.stat().st_mtime - 3 * 3600
        os.utime(p, (old, old))
        ret.apply([("trim", str(p), p.stat().st_size, "t")])
        self.assertAlmostEqual(p.stat().st_mtime, old, delta=2)

    def test_deploy_runbook_copies_the_orderflow_state_file(self):
        # af91b21 untracked orderflow _state.json; git merge --ff-only on the live tree aborts or deletes it
        text = (ROOT / "MyTradingSys" / "system" / "DEPLOY_RUNBOOK.md").read_text(encoding="utf-8")
        self.assertIn("_state.json", text)
        self.assertIn("copy", text.lower())


if __name__ == "__main__":
    unittest.main()
