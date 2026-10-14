"""scripts/dev/turn_meter.py: the SHORT SESSIONS cap (15 tool / 5 operator turns, CLAUDE.md) fires as a hook, resets on compact."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "dev" / "turn_meter.py"


def fire(home, event, sid="s1", extra=None, env=None):
    payload = {"session_id": sid, "hook_event_name": event, "cwd": "C:/x", **(extra or {})}
    e = {k: v for k, v in os.environ.items() if not k.startswith("MTS_TURN_METER")}
    e.update({"MTS_TURN_METER_HOME": str(home), **(env or {})})
    r = subprocess.run([sys.executable, str(SCRIPT), "hook"], input=json.dumps(payload), capture_output=True, text=True, env=e)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


class TurnMeterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_tool_cap_fires_at_15_then_every_5(self):
        fired = [n for n in range(1, 26) if fire(self.home, "PostToolUse")]
        self.assertEqual(fired, [15, 20, 25])

    def test_post_tool_output_is_additional_context_json(self):
        for _ in range(14):
            fire(self.home, "PostToolUse")
        out = json.loads(fire(self.home, "PostToolUse"))
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PostToolUse")
        self.assertIn("15 tool turns", ctx)
        self.assertIn("relay.py handoff", ctx)

    def test_operator_turns_over_5_fire(self):
        fired = [n for n in range(1, 8) if fire(self.home, "UserPromptSubmit")]
        self.assertEqual(fired, [6, 7])

    def test_prompt_after_tool_cap_fires(self):
        for _ in range(15):
            fire(self.home, "PostToolUse")
        self.assertIn("[TURN METER]", fire(self.home, "UserPromptSubmit"))

    def test_compact_resets(self):
        for _ in range(16):
            fire(self.home, "PostToolUse")
        fire(self.home, "SessionStart", extra={"source": "compact"})
        self.assertEqual(fire(self.home, "UserPromptSubmit"), "")
        self.assertEqual([n for n in range(1, 16) if fire(self.home, "PostToolUse")], [15])

    def test_resume_keeps_counts(self):
        for _ in range(15):
            fire(self.home, "PostToolUse")
        fire(self.home, "SessionStart", extra={"source": "resume"})
        self.assertIn("[TURN METER]", fire(self.home, "UserPromptSubmit"))

    def test_sessions_are_separate(self):
        for _ in range(15):
            fire(self.home, "PostToolUse", sid="a")
        self.assertEqual(fire(self.home, "UserPromptSubmit", sid="b"), "")

    def test_off_and_garbage_never_fail(self):
        self.assertEqual(fire(self.home, "UserPromptSubmit", env={"MTS_TURN_METER": "off", "MTS_TURN_METER_USER_CAP": "0"}), "")
        e = {**os.environ, "MTS_TURN_METER_HOME": str(self.home)}
        r = subprocess.run([sys.executable, str(SCRIPT), "hook"], input="not json", capture_output=True, text=True, env=e)
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        (self.home / "s1.json").write_text("{broken", encoding="utf-8")
        self.assertEqual(fire(self.home, "PostToolUse"), "")


if __name__ == "__main__":
    unittest.main()
