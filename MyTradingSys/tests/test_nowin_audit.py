import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
import nowin


class NowinAuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.log_file = self.tmp_path / "nowin_spawns.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def test_spawn_logging_opt_in(self):
        """Opt-in spawn diagnostic log records parent, child, creation flags, elapsed."""
        calls = []
        def process_init(proc, *args, **kwargs):
            # Verify the wrapper, without asking a POSIX subprocess to accept
            # Windows-only creationflags or starting a visible console on Windows.
            calls.append((args, kwargs))
            proc.pid = 4000 + len(calls)
            proc._child_created = False

        with mock.patch.object(subprocess.Popen, "__init__", process_init), \
             mock.patch.object(subprocess.Popen, "_mts_nowin", False, create=True), \
             mock.patch.dict(os.environ, {"MTS_NOWIN_LOG": str(self.log_file)}):
            self.assertTrue(nowin.install(force=True))
            subprocess.Popen([sys.executable, "-c", "pass"], creationflags=nowin.CREATE_NO_WINDOW)
            subprocess.Popen([sys.executable, "-c", "pass"], creationflags=0)

        self.assertTrue(self.log_file.is_file())
        rows = [json.loads(line) for line in self.log_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(len(rows), 2)
        for i, row in enumerate(rows):
            self.assertEqual(row["parent_pid"], os.getpid())
            self.assertEqual(row["child_pid"], 4001 + i)
            self.assertEqual(row["cmd"], [sys.executable, "-c", "pass"])
            self.assertGreaterEqual(row["elapsed_ms"], 0)
            self.assertEqual(row["creationflags"], calls[i][1]["creationflags"])
        self.assertEqual(rows[0]["creationflags"], nowin.CREATE_NO_WINDOW)
        self.assertEqual(rows[1]["creationflags"], 0)
        self.assertTrue(rows[0]["has_create_no_window"])
        self.assertFalse(rows[1]["has_create_no_window"])

    def test_dummy_spawn_log_is_rejected(self):
        with mock.patch.object(nowin, "_log_spawn", return_value=None):
            with self.assertRaises(AssertionError):
                self.test_spawn_logging_opt_in()

    def test_audit_subcommand_lists_spawns_without_create_no_window(self):
        """nowin.py audit lists spawns executed without CREATE_NO_WINDOW."""
        log_rows = [
            {
                "utc": "2026-10-18T20:00:00Z",
                "parent_pid": 1000,
                "child_pid": 1001,
                "cmd": ["git", "status"],
                "creationflags": 0x08000000,
                "elapsed_ms": 15.2,
                "has_create_no_window": True
            },
            {
                "utc": "2026-10-18T20:01:00Z",
                "parent_pid": 1000,
                "child_pid": 1002,
                "cmd": ["git", "fetch"],
                "creationflags": 0,
                "elapsed_ms": 120.5,
                "has_create_no_window": False
            },
            {
                "utc": "2026-10-18T20:02:00Z",
                "parent_pid": 1000,
                "child_pid": 1003,
                "cmd": ["python", "script.py"],
                "creationflags": 512,  # Some other flag without CREATE_NO_WINDOW
                "elapsed_ms": 45.0,
                "has_create_no_window": False
            }
        ]
        self.log_file.write_text("\n".join(json.dumps(r) for r in log_rows) + "\n", encoding="utf-8")

        # Programmatic audit function
        flawed = nowin.audit_spawns(log_path=self.log_file)
        self.assertEqual(len(flawed), 2)
        pids = [f["child_pid"] for f in flawed]
        self.assertIn(1002, pids)
        self.assertIn(1003, pids)
        self.assertNotIn(1001, pids)

        # CLI audit
        env = os.environ.copy()
        env["MTS_NOWIN_LOG"] = str(self.log_file)
        r = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "dev" / "nowin.py"), "audit"],
            capture_output=True,
            text=True,
            env=env
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("1002", r.stdout)
        self.assertIn("1003", r.stdout)
        self.assertNotIn("1001", r.stdout)


if __name__ == "__main__":
    unittest.main()
