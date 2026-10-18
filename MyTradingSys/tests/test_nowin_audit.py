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
        orig_init = subprocess.Popen.__init__
        try:
            # When MTS_NOWIN_LOG is set, spawns are logged
            with mock.patch.dict(os.environ, {"MTS_NOWIN_LOG": str(self.log_file)}):
                # uninstall / reinstall to ensure hook is active
                subprocess.Popen._mts_nowin = False
                nowin.install(force=True)

                # Spawn with CREATE_NO_WINDOW
                p1 = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(0.01)"], creationflags=0x08000000)
                p1.wait()

                # Spawn without CREATE_NO_WINDOW
                p2 = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(0.01)"], creationflags=0)
                p2.wait()

            self.assertTrue(self.log_file.is_file())
            rows = [json.loads(line) for line in self.log_file.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertEqual(len(rows), 2)

            r1, r2 = rows[0], rows[1]
            self.assertIn("parent_pid", r1)
            self.assertIn("child_pid", r1)
            self.assertIn("cmd", r1)
            self.assertIn("creationflags", r1)
            self.assertIn("elapsed_ms", r1)

            self.assertEqual(r1["creationflags"], 0x08000000)
            self.assertEqual(r2["creationflags"], 0)
        finally:
            subprocess.Popen.__init__ = orig_init
            subprocess.Popen._mts_nowin = False

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
