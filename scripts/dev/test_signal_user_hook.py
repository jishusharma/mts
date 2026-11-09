"""signal_user_hook: sessions outside a clone still get MTS signals (operator 2026-11-09: NUC missed 7 asks)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import signal_user_hook as U  # noqa: E402

FAKE_SIGNAL = (
    "import json, sys\n"
    "d = json.loads(sys.stdin.read())\n"
    "if d.get('hook_event_name') == 'Stop':\n"
    "    print(json.dumps({'decision': 'block', 'reason': 'q-1 open'}))\n"
    "else:\n"
    "    print('SIGNALS cwd=' + d['cwd'])\n"
)


class UserHookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.keep = {k: os.environ.get(k) for k in ("MTS_USER_HOOK_HOME", "MTS_USER_HOOK_SETTINGS", "MTS_USER_HOOK",
                                                    "MTS_SIGNALS_HOME")}
        os.environ["MTS_USER_HOOK_HOME"] = str(self.tmp / "mts")
        os.environ["MTS_USER_HOOK_SETTINGS"] = str(self.tmp / "claude" / "settings.json")
        os.environ.pop("MTS_USER_HOOK", None)
        self.clone = self.tmp / "clone"
        (self.clone / "scripts" / "dev").mkdir(parents=True)
        (self.clone / "scripts" / "dev" / "mts_signal.py").write_text(FAKE_SIGNAL, encoding="utf-8")
        (self.clone / ".claude").mkdir()
        (self.clone / ".claude" / "settings.json").write_text('{"hooks": "python mts_signal.py hook"}', encoding="utf-8")
        self.outside = self.tmp / "IdeaProjects"
        self.outside.mkdir()

    def tearDown(self):
        for k, v in self.keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def settings(self):
        return json.loads(U.claude_settings().read_text(encoding="utf-8"))

    def run_runner(self, cwd, ev="UserPromptSubmit"):
        payload = json.dumps({"hook_event_name": ev, "session_id": "s1", "cwd": str(cwd)})
        r = subprocess.run([sys.executable, str(U.runner_path())], input=payload.encode(), capture_output=True,
                           timeout=30)
        return r.stdout.decode().strip()

    def test_install_merges_keeps_other_settings_and_is_idempotent(self):
        sf = U.claude_settings()
        sf.parent.mkdir(parents=True)
        sf.write_text(json.dumps({"permissions": {"allow": ["Bash"]},
                                  "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "other"}]}]}}),
                      encoding="utf-8")
        self.assertEqual(U.install(str(self.clone)), ["runner", "clone", "settings"])
        s = self.settings()
        self.assertEqual(s["permissions"], {"allow": ["Bash"]})
        self.assertIn("other", json.dumps(s["hooks"]["Stop"]))
        for ev in U.EVENTS:
            self.assertEqual(json.dumps(s["hooks"][ev]).count(U.MARK), 1, ev)
        self.assertTrue(sf.with_name("settings.json.bak").is_file())
        self.assertEqual(U.install(str(self.clone)), [])
        self.assertEqual(U.status(), 0)

    def test_duplicate_runner_entries_collapse_to_one(self):
        cmd = U.command()
        s = {"hooks": {"Stop": [{"hooks": [{"command": cmd}]}, {"hooks": [{"command": cmd}]}]}}
        s, changed = U.merge_settings(s, cmd)
        self.assertTrue(changed)
        self.assertEqual(json.dumps(s["hooks"]["Stop"]).count(U.MARK), 1)

    def test_unparseable_settings_never_overwritten(self):
        sf = U.claude_settings()
        sf.parent.mkdir(parents=True)
        sf.write_text("{broken", encoding="utf-8")
        with self.assertRaises(ValueError):
            U.install(str(self.clone))
        self.assertEqual(sf.read_text(encoding="utf-8"), "{broken")

    def test_session_outside_clone_gets_signals_from_the_clone(self):
        U.install(str(self.clone))
        out = self.run_runner(self.outside)
        self.assertEqual(out, "SIGNALS cwd=" + self.clone.resolve().as_posix())

    def test_stop_block_json_passes_through(self):
        U.install(str(self.clone))
        self.assertEqual(json.loads(self.run_runner(self.outside, "Stop"))["decision"], "block")

    def test_session_inside_clone_is_not_served_twice(self):
        U.install(str(self.clone))
        (self.clone / "sub").mkdir()
        self.assertEqual(self.run_runner(self.clone / "sub"), "")

    def test_removed_clone_falls_back_to_the_next(self):
        gone = self.tmp / "gone"
        U.install(str(self.clone))
        U.remember(str(gone))          # newest first, but it does not exist
        self.assertIn("cwd=" + self.clone.resolve().as_posix(), self.run_runner(self.outside))

    def test_ensure_installed_skips_in_signal_tests_and_when_off(self):
        os.environ["MTS_USER_HOOK"] = "off"
        self.assertEqual(U.ensure_installed(str(HERE)), [])
        os.environ.pop("MTS_USER_HOOK")
        os.environ.pop("MTS_USER_HOOK_HOME")
        os.environ["MTS_SIGNALS_HOME"] = str(self.tmp / "sig")
        self.assertEqual(U.ensure_installed(str(HERE)), [])
        self.assertFalse((self.tmp / "mts").exists())


if __name__ == "__main__":
    unittest.main()
