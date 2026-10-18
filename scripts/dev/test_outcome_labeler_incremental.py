"""Tests for outcome_labeler incremental behaviour (synthetic dirs only, never the live tree).

Fail-first proof: OL_MODULE=<path to a copy of the old outcome_labeler.py> python -m pytest this_file
"""
import importlib.util
import json
import os
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
MOD_PATH = os.environ.get("OL_MODULE") or str(REPO / "MyTradingSys" / "runtime" / "outcome_labeler.py")


def load_mod():
    spec = importlib.util.spec_from_file_location("ol_under_test", MOD_PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


BASE = datetime(2026, 1, 1, tzinfo=timezone.utc)


def write_snap(d, i, price=None):
    ts = BASE + timedelta(minutes=10 * i)
    name = f"BTCUSDT_{i:06d}.json"
    (d / name).write_text(json.dumps({
        "timestamp_utc": ts.isoformat(), "current_price": price if price is not None else 100.0 + i,
        "conditions": {"vp_shape": "P", "price_vs_va": "in", "cvd_slope": "up"}}), encoding="utf-8")
    return name


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.snaps = self.root / "snapshots"
        self.snaps.mkdir()
        self.labels = self.root / "outcome_labels.json"
        self.m = load_mod()
        self.m.SNAPS = self.snaps
        self.m.LABELS = self.labels

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self):
        opened = []
        real_open = open

        def counting_open(f, *a, **k):
            if str(f).startswith(str(self.snaps)):
                opened.append(Path(f).name)
            return real_open(f, *a, **k)
        with mock.patch("builtins.open", counting_open):
            self.m.main()
        return opened

    def read_labels(self):
        return json.loads(self.labels.read_text(encoding="utf-8"))["labels"]


class Incremental(Base):
    def test_labeled_snapshots_are_not_reopened(self):
        n = 3000
        for i in range(n):
            write_snap(self.snaps, i)
        # first cycle is setup: 3000 files through the counting open() can pass SLOW_WARN_S (exit 3) on a loaded
        # machine (ship gate, 2026-10-18); the speed claim under test is the second cycle, bounded below at 3 s
        with mock.patch.object(self.m, "SLOW_WARN_S", 1e9):
            self.run_main()                   # first cycle labels everything labelable
        labeled = {l["file"] for l in self.read_labels()}
        self.assertGreater(len(labeled), 2000)
        t0 = time.monotonic()
        opened = self.run_main()              # second cycle: only the unlabeled tail may be opened
        dt = time.monotonic() - t0
        self.assertEqual([f for f in opened if f in labeled], [])
        self.assertLess(dt, 3.0)
        print(f"second cycle, {len(labeled)} labeled of {n}: {dt:.3f}s, opened {len(opened)}")

    def test_restart_state_is_idempotent_and_matches_full_scan(self):
        for i in range(60):
            write_snap(self.snaps, i)
        self.run_main()
        first = self.read_labels()
        self.run_main()                       # "restart": new process, same files
        self.assertEqual(self.read_labels(), first)
        # new snapshots arrive later; unlabeled tail gets labeled using labeled ones as forward refs
        for i in range(60, 120):
            write_snap(self.snaps, i)
        self.run_main()
        got = {l["file"]: l["fwd_return_pct"] for l in self.read_labels()}
        # independent expectation: price = 100+i, ts = 10 min * i, +30m => i+3, +60m => i+6, +120m => i+12
        for i in range(0, 120):
            f = f"BTCUSDT_{i:06d}.json"
            if i + 12 < 120:
                p = 100.0 + i
                exp = {"30m": round((100.0 + i + 3 - p) / p * 100, 4),
                       "60m": round((100.0 + i + 6 - p) / p * 100, 4),
                       "120m": round((100.0 + i + 12 - p) / p * 100, 4)}
                self.assertEqual(got.get(f), exp, f)

    def test_unreadable_snapshot_skipped_not_fatal(self):
        for i in range(40):
            write_snap(self.snaps, i)
        (self.snaps / "BTCUSDT_999999.json").write_text("{not json", encoding="utf-8")
        self.run_main()
        self.assertTrue(self.read_labels())

    def test_corrupt_labels_kept_and_rebuilt(self):
        for i in range(40):
            write_snap(self.snaps, i)
        self.labels.write_text("{broken", encoding="utf-8")
        self.run_main()
        kept = list(self.root.glob("outcome_labels.json.corrupt*"))
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0].read_text(encoding="utf-8"), "{broken")
        self.assertTrue(self.read_labels())

    def test_second_corrupt_copy_does_not_overwrite_first(self):
        for i in range(40):
            write_snap(self.snaps, i)
        self.labels.write_text("{first", encoding="utf-8")
        self.run_main()
        self.labels.write_text("{second", encoding="utf-8")
        self.run_main()
        texts = sorted(p.read_text(encoding="utf-8") for p in self.root.glob("outcome_labels.json.corrupt*"))
        self.assertEqual(texts, ["{first", "{second"])

    def test_label_entry_without_price_is_reopened_and_used_as_reference(self):
        for i in range(40):
            write_snap(self.snaps, i)
        # snapshot 3 (+30m reference for snapshot 0) has a malformed label entry (no price)
        self.labels.write_text(json.dumps({"version": "1.0.0", "labels": [
            {"file": "BTCUSDT_000003.json", "ts": (BASE + timedelta(minutes=30)).isoformat()}]}), encoding="utf-8")
        opened = self.run_main()
        self.assertIn("BTCUSDT_000003.json", opened)
        got = {l["file"]: l for l in self.read_labels()}
        p = 100.0
        self.assertEqual(got["BTCUSDT_000000.json"]["fwd_return_pct"]["30m"], round((103.0 - p) / p * 100, 4))
        self.assertEqual(len([l for l in self.read_labels() if l["file"] == "BTCUSDT_000003.json"]), 1)

    def test_equal_timestamp_reference_is_ordered_by_filename(self):
        # two snapshots share the +30m timestamp; the lower filename must win, labeled or not
        write_snap(self.snaps, 0, price=100.0)
        a = write_snap(self.snaps, 3, price=110.0)
        d = json.loads((self.snaps / a).read_text(encoding="utf-8"))
        (self.snaps / "BTCUSDT_000003b.json").write_text(json.dumps(dict(d, current_price=120.0)), encoding="utf-8")
        for i in range(4, 40):
            write_snap(self.snaps, i)
        # the lower filename (...03.json, 110) is the LABELED one: the unlabeled ...03b (120) must not jump ahead of it
        self.labels.write_text(json.dumps({"version": "1.0.0", "labels": [
            {"file": "BTCUSDT_000003.json", "ts": d["timestamp_utc"], "price": 110.0}]}), encoding="utf-8")
        self.run_main()
        got = {l["file"]: l for l in self.read_labels()}
        self.assertEqual(got["BTCUSDT_000000.json"]["fwd_return_pct"]["30m"], 10.0)  # ...03.json (110) before ...03b (120)

    def test_write_error_leaves_existing_labels_intact(self):
        for i in range(40):
            write_snap(self.snaps, i)
        self.run_main()
        before = self.labels.read_text(encoding="utf-8")
        for i in range(40, 80):
            write_snap(self.snaps, i)
        with mock.patch("os.replace", side_effect=OSError("disk")):
            with self.assertRaises(OSError):
                self.m.main()
        self.assertEqual(self.labels.read_text(encoding="utf-8"), before)

    def test_slow_input_is_reported_not_silent(self):
        for i in range(40):
            write_snap(self.snaps, i)
        self.m.SLOW_WARN_S = -1.0             # any run counts as slow
        with mock.patch("sys.stdout") as out:
            with self.assertRaises(SystemExit) as cm:
                self.m.main()
        self.assertNotEqual(cm.exception.code, 0)
        text = "".join(c.args[0] for c in out.write.call_args_list)
        self.assertIn("SLOW", text)


if __name__ == "__main__":
    unittest.main()
