"""Tests for outcome_labeler incremental behaviour (synthetic dirs only, never the live tree).

Fail-first proof: OL_MODULE=<path to a copy of the old outcome_labeler.py> python -m pytest this_file
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
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
        self.m.SLOW_WARN_S = 1e9              # wall-clock under a loaded gate is not under test (exit 3 flaked step 4f)

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
        for _ in range(10):                   # a 3000 backlog drains over bounded cycles; run until converged
            before = len(self.labels.read_text(encoding="utf-8")) if self.labels.exists() else 0
            self.run_main()
            if self.labels.stat().st_size == before:
                break
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


class ColdBacklog(Base):
    """A cold or corrupt-labels backlog must drain over bounded cycles (30 s kill in start-trading-day.ps1)."""

    def labels_by_file(self):
        return {l["file"]: l for l in self.read_labels()}

    def test_cold_backlog_drains_within_budget(self):
        n, budget = 400, 50
        for i in range(n):
            write_snap(self.snaps, i)
        self.m.MAX_OPEN_PER_CYCLE = budget
        opened = self.run_main()              # first cycle of a cold backlog
        # budget + the +120 min lookahead window (12 snapshots at 10 min spacing) + 1; the old code opens all 400
        self.assertLessEqual(len(opened), budget + 13, f"opened {len(opened)} of {n} in one cycle")
        self.assertGreaterEqual(len(self.read_labels()), 1, "a bounded cycle must still write labels")
        for _ in range(60):                   # later cycles converge
            before = len(self.read_labels())
            self.run_main()
            if len(self.read_labels()) == before:
                break
        bounded = self.labels_by_file()
        self.labels.unlink()                  # independent unbounded run on the same snapshots
        self.m.MAX_OPEN_PER_CYCLE = 10 ** 9
        self.run_main()
        self.assertEqual(bounded, self.labels_by_file())
        self.assertEqual(len(bounded), n - 12)

    def test_budget_never_labels_with_a_reference_beyond_the_opened_window(self):
        # every label of a truncated cycle must equal the unbounded one (price = 100+i, so +30m/+60m/+120m are i+3/i+6/i+12)
        for i in range(200):
            write_snap(self.snaps, i)
        self.m.MAX_OPEN_PER_CYCLE = 20
        opened = self.run_main()
        self.assertLessEqual(len(opened), 20 + 13)   # truncated: the old code opens and labels all 188 at once
        self.assertTrue(0 < len(self.read_labels()) < 188)
        for f, l in self.labels_by_file().items():
            i = int(f[len("BTCUSDT_"):-len(".json")])
            p = 100.0 + i
            self.assertEqual(l["fwd_return_pct"], {f"{h}m": round((100.0 + i + h // 10 - p) / p * 100, 4)
                                                   for h in (30, 60, 120)}, f)

    def test_time_budget_stops_opening_but_still_writes(self):
        for i in range(300):
            write_snap(self.snaps, i)
        self.m.OPEN_BUDGET_S = 0.0            # out of time at once: must stop early, never hang or raise
        self.m.MAX_OPEN_PER_CYCLE = 10 ** 9
        with self.assertRaises(SystemExit) as cm:   # one file opened, nothing labelable yet: reported as no progress (4)
            self.run_main()
        self.assertEqual(cm.exception.code, 4)
        self.assertTrue(self.labels.exists())

    def test_zero_time_budget_stops_after_one_file_on_a_frozen_clock(self):
        # Windows CI clock ticks ~15 ms: a whole cycle can read the same monotonic value, so elapsed == budget == 0.0 must stop
        for i in range(300):
            write_snap(self.snaps, i)
        self.m.OPEN_BUDGET_S = 0.0
        self.m.MAX_OPEN_PER_CYCLE = 10 ** 9
        with mock.patch.object(self.m.time, "monotonic", return_value=1000.0):
            with self.assertRaises(SystemExit) as cm:
                self.run_main()
        self.assertEqual(cm.exception.code, 4)

    def test_budget_spent_on_unreadable_files_is_reported_not_silent(self):
        for i in range(30):                   # the oldest names are all unreadable: a cycle that makes no progress exits 4
            (self.snaps / f"BTCUSDT_{i:06d}.json").write_text("{bad", encoding="utf-8")
        for i in range(100, 160):
            write_snap(self.snaps, i)
        self.m.MAX_OPEN_PER_CYCLE = 10
        with self.assertRaises(SystemExit) as cm:
            self.run_main()
        self.assertEqual(cm.exception.code, 4)

    def test_killed_bounded_cycle_loses_nothing_and_restart_resumes(self):
        for i in range(300):
            write_snap(self.snaps, i)
        self.m.MAX_OPEN_PER_CYCLE = 40
        self.assertLessEqual(len(self.run_main()), 40 + 13)
        kept = self.labels.read_text(encoding="utf-8")
        with mock.patch("os.replace", side_effect=OSError("disk")):
            with self.assertRaises(OSError):  # IO error mid-backlog
                self.m.main()
        self.assertEqual(self.labels.read_text(encoding="utf-8"), kept)
        self.assertGreater(len(self.read_labels()), 0)
        for _ in range(60):                   # a fresh process (restart) resumes from the file
            before = len(self.read_labels())
            self.run_main()
            if len(self.read_labels()) == before:
                break
        self.assertEqual(len(self.read_labels()), 300 - 12)


LAUNCHER = REPO / "scripts" / "core" / "start-trading-day.ps1"


def _ps_exe():
    return shutil.which("pwsh") or shutil.which("powershell")


BLOCK_RE = re.compile(r"^[ \t]*try \{\s*\n[ \t]*\$olCmd = .*?\n[ \t]*\} catch \{\}", re.S | re.M)


class Launcher(unittest.TestCase):
    def run_block(self, rc):
        ps = _ps_exe()
        if not ps:
            self.skipTest("no PowerShell on this host")
        text = LAUNCHER.read_text(encoding="utf-8")
        m = BLOCK_RE.search(text)
        self.assertIsNotNone(m, "outcome_labeler call block not found in start-trading-day.ps1")
        # run only the launcher's own labeler block, with the process runner and logger stubbed
        script = ("$R = 'C:\\nowhere'\n"
                  "function Invoke-WithTimeout { param($File, $ArgList, $TimeoutSec, $Tag, $WorkDir) return " + str(rc) + " }\n"
                  "function Log-Line { param([string]$msg) Write-Output ('LOGLINE ' + $msg) }\n" + m.group(0))
        out = subprocess.run([ps, "-NoProfile", "-NonInteractive", "-Command", script],
                             capture_output=True, text=True, timeout=60)
        return [l for l in out.stdout.splitlines() if l.startswith("LOGLINE")]

    def test_launcher_logs_labeler_rc(self):
        lines = self.run_block(3)             # 3 = SLOW (>20 s)
        self.assertEqual(len(lines), 1, lines)
        self.assertIn("outcome_labeler", lines[0])
        self.assertIn("3", lines[0])
        self.assertEqual(len(self.run_block(-1)), 1)   # a timeout kill (-1) is also logged
        self.assertEqual(self.run_block(0), [])        # a healthy run stays silent


if __name__ == "__main__":
    unittest.main()
