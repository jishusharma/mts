"""`.claude/settings.json` hook wiring (RUN_MODEL.md section 6): which hooks run in the background (`async`) and which must block.
A hook that can deny or block (PreToolUse, Stop, SessionStart context, shot/role_loader injection) must stay synchronous; an async
hook's decision fields are ignored, so making a deny-hook async would silently disable it."""
import json
import re
import unittest
from pathlib import Path

SETTINGS = Path(__file__).resolve().parents[2] / ".claude" / "settings.json"

# (event, script) pairs that run in the background. Everything else is synchronous.
ASYNC = {
    ("PostToolUse", "mts_signal.py"),        # sends signals detached; its output is not needed this turn
}
# Printed context the model must see THIS turn (signals, ACTION REQUIRED, CI RED, hand-off nags) is synchronous, and turn_meter
# is synchronous on PostToolUse because an async run raced the sync UserPromptSubmit run on one state file (lost typed_at/driven).
MUST_BE_SYNC = {("UserPromptSubmit", "mts_signal.py"), ("UserPromptSubmit", "ci_watch.py"), ("PostToolUse", "turn_meter.py"),
                ("Stop", "mts_signal.py")}


def hooks():
    d = json.loads(SETTINGS.read_text(encoding="utf-8"))
    for event, groups in d["hooks"].items():
        for g in groups:
            for h in g["hooks"]:
                m = re.search(r"scripts/dev/(\w+\.py)", h["command"])
                yield event, m.group(1), bool(h.get("async")), h


class HookSettingsTest(unittest.TestCase):
    def test_exactly_the_informational_hooks_are_async(self):
        actual = {(e, s) for e, s, a, _ in hooks() if a}
        self.assertEqual(actual, ASYNC)

    def test_context_printing_hooks_are_synchronous_and_stop_hook_is_wired(self):
        actual = {(e, s): a for e, s, a, _ in hooks()}
        for key in MUST_BE_SYNC:
            self.assertIn(key, actual, key)
            self.assertFalse(actual[key], f"{key} prints context or can block and must not be async")

    def test_deny_and_block_hooks_stay_synchronous(self):
        for event, script, is_async, _ in hooks():
            if event in ("PreToolUse", "Stop", "SessionStart") or script in ("model_guard.py", "stop_guard.py", "shot.py", "role_loader.py"):
                self.assertFalse(is_async, f"{event} {script} can deny, block or inject context and must not be async")

    def test_every_hook_has_a_timeout(self):
        for event, script, _, h in hooks():
            self.assertIn("timeout", h, f"{event} {script}")


if __name__ == "__main__":
    unittest.main()
