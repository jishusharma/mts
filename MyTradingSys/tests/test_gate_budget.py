import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, "scripts/dev")
import sync
import run_all_tests as rat


def sh(cwd, *args):
    r = subprocess.run(["git", "-C", str(cwd)] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} in {cwd} failed: {r.stderr}")
    return r.stdout


class GateBudgetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gate_budget_test_"))
        self.slots_dir = self.tmp / "host_slots"
        os.environ["MTS_GATE_SLOTS_DIR"] = str(self.slots_dir)
        self.timing_file = self.tmp / "gate_timing.jsonl"
        os.environ["MTS_GATE_TIMING"] = str(self.timing_file)

        # Create origin and two separate clones (not worktrees, separate git dirs)
        self.origin = self.tmp / "origin.git"
        sh(self.tmp, "init", "-q", "--bare", str(self.origin))
        sh(self.origin, "symbolic-ref", "HEAD", "refs/heads/fast-track")

        self.clone1 = self.tmp / "clone1"
        self.clone2 = self.tmp / "clone2"
        for c in (self.clone1, self.clone2):
            sh(self.tmp, "clone", "-q", str(self.origin), str(c))
            sh(c, "config", "user.email", "test@test.local")
            sh(c, "config", "user.name", "Tester")

        # Initial commit on origin
        (self.clone1 / "README.md").write_text("init\n")
        sh(self.clone1, "add", "README.md")
        sh(self.clone1, "commit", "-q", "-m", "init")
        sh(self.clone1, "push", "-q", "origin", "HEAD:fast-track")
        sh(self.clone2, "pull", "-q", "origin", "fast-track")

    def tearDown(self):
        os.environ.pop("MTS_GATE_SLOTS_DIR", None)
        os.environ.pop("MTS_GATE_TIMING", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_two_fake_clones_share_one_slot_set(self):
        """Two separate clones share the machine-wide gate slots; clone2 cannot acquire when clone1 holds 2 slots."""
        class Blocked(Exception):
            pass

        def raise_blocked(_):
            raise Blocked("slot acquisition would block")

        with sync.gate_slot(self.clone1, alive=lambda p: True), sync.gate_slot(self.clone1, alive=lambda p: True):
            # Two slots held by clone1. clone2 must see slots busy and not acquire
            with self.assertRaises(Blocked):
                with sync.gate_slot(self.clone2, alive=lambda p: True, sleep=raise_blocked, timeout=0.1):
                    self.fail("clone2 acquired slot while clone1 held the machine-wide budget")

    def test_dead_pid_reclaim_still_works(self):
        """A stale slot held by a dead PID in the machine-wide slot dir is reclaimed."""
        slot_d = sync.host_gate_slots_dir() if hasattr(sync, "host_gate_slots_dir") else sync.gate_slot(self.clone1)._dir()
        slot_d.mkdir(parents=True, exist_ok=True)
        (slot_d / "slot-0").write_text("9999999\n", encoding="utf-8")
        (slot_d / "slot-1").write_text("8888888\n", encoding="utf-8")

        # alive says 9999999 and 8888888 are dead
        with sync.gate_slot(self.clone1, alive=lambda p: False) as g:
            self.assertTrue(g.path.exists())
            self.assertEqual(g.path.read_text().strip(), str(os.getpid()))

    def test_precheck_counted(self):
        """Precheck takes a precheck slot or counts against the budget during execution."""
        slot_held_during_precheck = []

        class DummyStep:
            def __init__(self, num, desc):
                self.num = str(num)
                self.desc = desc
                self.skip = None
                self.lane = "par"
                self.cmd_text = desc
                self.tail = None

            def run(self):
                # Check if precheck slot is held
                precheck_dir = sync.host_gate_slots_dir("gate-slots-precheck") if hasattr(sync, "host_gate_slots_dir") else (self.slots_dir / "gate-slots-precheck")
                slots_present = list(precheck_dir.glob("slot-*")) if precheck_dir.exists() else []
                slot_held_during_precheck.append(len(slots_present) > 0)
                return True, "ok"

        plan = [DummyStep("3c", "User guide in sync"), DummyStep("4t", "Targeted test"), DummyStep("4b", "Main shard")]
        # Run plan with precheck and slot enabled
        args = ["--quick", "--precheck", "--slot", "--fail-fast"]
        with mock.patch("sys.stdout", io.StringIO()):
            # Use run_all_tests with slot
            res = rat.run_plan(
                plan,
                jobs=2,
                precheck=True,
                slot=lambda: sync.gate_slot(self.clone1),
                precheck_slot=lambda: sync.gate_slot(self.clone1, slots=2, name="gate-slots-precheck") if hasattr(sync, "GATE_PRECHECK_SLOTS") else None,
            )
        self.assertTrue(any(slot_held_during_precheck), "Precheck must hold a precheck slot while running cheap steps")

    def test_ship_timing_logged_wait_run_retry(self):
        """sync.ship logs wait, run and retry seconds into runtime_data/gate_timing.jsonl."""
        (self.clone1 / "work.py").write_text("data = 1\n")
        sh(self.clone1, "add", "work.py")
        sh(self.clone1, "commit", "-q", "-m", "work\n\nResult: done")

        # Fake gate that simulates 0.1s execution
        def fake_gate(repo, files=None):
            time.sleep(0.05)

        with mock.patch("sys.stdout", io.StringIO()):
            sync.ship(self.clone1, gate=fake_gate, docs_gate=fake_gate)

        self.assertTrue(self.timing_file.exists(), f"Timing file {self.timing_file} was not created")
        lines = [json.loads(line) for line in self.timing_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        ship_rows = [r for r in lines if r.get("step") == "ship"]
        self.assertTrue(len(ship_rows) > 0, "No row with step='ship' in gate_timing.jsonl")
        row = ship_rows[-1]
        self.assertIn("wait_s", row)
        self.assertIn("run_s", row)
        self.assertIn("retry_s", row)
        self.assertGreaterEqual(row["run_s"], 0.04)


if __name__ == "__main__":
    unittest.main()
