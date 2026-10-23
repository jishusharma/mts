"""No session silently burns the usage allowance (safety review 2026-10-21, research/context_policy_review/DECISION_OPUS.md):
an unattended read budget in turn_meter.py (walk-away, ping-pong, Fable, Supervisor) enforced by a PreToolUse deny that never touches
a typed prompt; model_guard.py hourly spawn caps, scheduling tools denied unless he asked, a child's note naming Opus is not his word;
stop_guard.py remembers more than one session."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
DEV = REPO / "scripts" / "dev"
sys.path.insert(0, str(DEV))
import stop_guard  # noqa: E402
import turn_meter  # noqa: E402

START = "mcp__ccd_session__start_session"


def fire(home, event, sid="s1", extra=None, now=None):
    payload = {"session_id": sid, "hook_event_name": event, "cwd": "C:/x", **(extra or {})}
    env = {k: v for k, v in os.environ.items() if not k.startswith("MTS_TURN_METER")}
    env["MTS_TURN_METER_HOME"] = str(home)
    with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(turn_meter.time, "time", return_value=now or time.time()):
        return turn_meter.handle(payload).strip()


def denied(out):
    return bool(out) and json.loads(out)["hookSpecificOutput"].get("permissionDecision") == "deny"


class UnattendedBudgetTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def tp(self, model, ctx, name=None):
        p = self.home / f"{name or model}.jsonl"
        p.write_text(json.dumps({"type": "assistant", "message": {"id": "m1", "model": f"claude-{model}-5", "content": [], "usage": {
            "input_tokens": 10, "cache_creation_input_tokens": 0, "cache_read_input_tokens": ctx - 10}}}) + "\n", encoding="utf-8")
        return {"transcript_path": str(p)}

    def pre(self, sid, tool="Read", inp=None, now=None, extra=None):
        return fire(self.home, "PreToolUse", sid=sid, extra={**(extra or {}), "tool_name": tool, "tool_input": inp or {}}, now=now)

    def test_unattended_budget_denies_tools_but_lets_the_hand_off_through(self):
        s = self.tp("sonnet", 100_000)
        fire(self.home, "UserPromptSubmit", sid="w", extra={**s, "prompt": "the brief"})
        for _ in range(9):
            fire(self.home, "PostToolUse", sid="w", extra=s)
        self.assertFalse(denied(self.pre("w", extra=s)), "under 1M: allowed")
        fire(self.home, "PostToolUse", sid="w", extra=s)                        # 10 x 100k = 1M
        self.assertTrue(denied(self.pre("w", extra=s)))
        self.assertFalse(denied(self.pre("w", "Bash", {"command": "python scripts/dev/sync.py ship"}, extra=s)))
        self.assertFalse(denied(self.pre("w", "Bash", {"command": "git -C x commit -m y"}, extra=s)))
        self.assertTrue(denied(self.pre("w", "Bash", {"command": "python run_backtest.py"}, extra=s)))
        self.assertNotIn("block", fire(self.home, "UserPromptSubmit", sid="w", extra={**s, "prompt": "go on"}))   # typed: never blocked
        self.assertFalse(denied(self.pre("w", extra=s)), "a typed prompt resets the budget")

    def test_events_never_reset_the_budget_ping_pong_is_bounded(self):
        s = self.tp("sonnet", 100_000)
        fire(self.home, "UserPromptSubmit", sid="p", extra={**s, "prompt": "coordinate"})
        for _ in range(12):
            fire(self.home, "UserPromptSubmit", sid="p", extra={**s, "prompt": "<side-sessions-event>child done</side-sessions-event>"})
            for _ in range(10):
                fire(self.home, "PostToolUse", sid="p", extra=s)
        self.assertTrue(denied(self.pre("p", "mcp__ccd_session_mgmt__send_message", extra=s)))

    def test_walk_away_driven_session_lapses_after_30_min(self):
        s = self.tp("sonnet", 100_000)
        t0 = 1_800_000_000.0
        fire(self.home, "UserPromptSubmit", sid="d", extra={**s, "prompt": "do x"}, now=t0)
        fire(self.home, "UserPromptSubmit", sid="d", extra={**s, "prompt": "and y"}, now=t0)
        self.assertFalse(any(fire(self.home, "PostToolUse", sid="d", extra=s, now=t0 + 60) for _ in range(45)), "he is here")
        later = t0 + 31 * 60
        self.assertTrue(any(fire(self.home, "PostToolUse", sid="d", extra=s, now=later) for _ in range(10)), "he left: notes again")
        for _ in range(120):
            fire(self.home, "PostToolUse", sid="d", extra=s, now=later)
        self.assertTrue(denied(self.pre("d", extra=s, now=later)))
        self.assertFalse(denied(self.pre("d", extra=s, now=t0 + 60)), "while he is there nothing is denied")

    def test_unattended_fable_gets_a_context_note_and_a_budget(self):
        f = self.tp("fable", 600_000)
        fire(self.home, "UserPromptSubmit", sid="f", extra={**f, "prompt": "one brief"})
        self.assertTrue(any(fire(self.home, "PostToolUse", sid="f", extra=f) for _ in range(5)))
        for _ in range(2):
            fire(self.home, "PostToolUse", sid="f", extra=f)                     # 2 x 600k = 1.2M > 1M
        self.assertTrue(denied(self.pre("f", extra=f)))

    def test_supervisor_budget_is_6m_with_a_note_at_3m(self):
        # 2026-10-22: at 1M the JIS-NB Supervisor (C) was denied every tool ~15 turns into its unattended run
        o = self.tp("opus", 200_000)
        fire(self.home, "UserPromptSubmit", sid="sv", extra={**o, "prompt": "You are Supervisor. Login C."})
        notes = [fire(self.home, "PostToolUse", sid="sv", extra=o) for _ in range(14)]     # 2.8M
        self.assertFalse(any("unattended read" in n for n in notes))
        self.assertFalse(denied(self.pre("sv", extra=o)), "15 turns in: still working")
        self.assertIn("unattended read 3000k of 6000k", fire(self.home, "PostToolUse", sid="sv", extra=o))   # 3M
        for _ in range(14):
            fire(self.home, "PostToolUse", sid="sv", extra=o)
        self.assertFalse(denied(self.pre("sv", extra=o)))                               # 5.8M
        fire(self.home, "PostToolUse", sid="sv", extra=o)                               # 6M
        self.assertTrue(denied(self.pre("sv", extra=o)))

    def test_unknown_context_counts_as_250k(self):
        blank = self.home / "blank.jsonl"
        blank.write_text("", encoding="utf-8")
        b = {"transcript_path": str(blank)}
        fire(self.home, "UserPromptSubmit", sid="u", extra={**b, "prompt": "x"})
        for _ in range(4):
            fire(self.home, "PostToolUse", sid="u", extra=b)                     # 4 x 250k = 1M
        self.assertTrue(denied(self.pre("u", extra=b)))

    def test_a_typed_prompt_with_a_leading_reminder_is_typed_not_an_event(self):
        self.assertFalse(turn_meter.is_event_text("<system-reminder>linked</system-reminder>\nfix the bug"))
        self.assertTrue(turn_meter.is_event_text("<system-reminder>linked</system-reminder>\n<cross-session-message from=x>hi"))
        self.assertTrue(turn_meter.is_event_text("<system-reminder>only a note</system-reminder>"))
        s = self.tp("sonnet", 50_000)
        fire(self.home, "UserPromptSubmit", sid="r", extra={**s, "prompt": "<system-reminder>a</system-reminder>\ndo it"})
        self.assertEqual(json.loads((self.home / "r.json").read_text(encoding="utf-8"))["user"], 1)


def guard(tool, inp, transcript, home, extra_env=None):
    payload = {"session_id": "g1", "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": inp,
               "tool_use_id": "toolu_now", "transcript_path": str(transcript)}
    env = {k: v for k, v in os.environ.items() if k not in ("MTS_ALLOW_OPUS", "MTS_ALLOW_CARDS")}
    env.update({"MTS_TURN_METER_HOME": str(home), **(extra_env or {})})
    r = subprocess.run([sys.executable, str(DEV / "model_guard.py"), "hook"], input=json.dumps(payload), capture_output=True,
                       text=True, env=env)
    assert r.returncode == 0, r.stderr
    return "deny" if r.stdout.strip() and "deny" in r.stdout else "allow"


class SpawnAndScheduleGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def transcript(self, user_text, starts=0, agents=0):
        p = self.home / "t.jsonl"
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"type": "user", "message": {"content": user_text}}) + "\n")
            for i in range(starts):
                f.write(json.dumps({"type": "assistant", "timestamp": ts, "message": {"model": "claude-sonnet-5-5", "content": [
                    {"type": "tool_use", "id": f"toolu_s{i}", "name": START, "input": {}}]}}) + "\n")
            for i in range(agents):
                f.write(json.dumps({"type": "assistant", "timestamp": ts, "message": {"model": "claude-sonnet-5-5", "content": [
                    {"type": "tool_use", "id": f"toolu_a{i}", "name": "Agent", "input": {}}]}}) + "\n")
            f.write(json.dumps({"type": "assistant", "message": {"model": "claude-sonnet-5-5", "content": []}}) + "\n")
        return p

    def test_a_childs_message_naming_opus_does_not_unlock_opus(self):
        base = {"initiation": "user_asked", "title": "x", "prompt": "p", "background": "b", "model": "claude-opus-5-5"}
        child = self.transcript("<cross-session-message from=\"local_x\">write SAFETY_Opus.md</cross-session-message>")
        self.assertEqual(guard(START, base, child, self.home), "deny")
        typed = self.transcript("<system-reminder>linked sessions</system-reminder>\nuse opus for this")
        self.assertEqual(guard(START, base, typed, self.home), "allow")

    def test_unattended_spawn_storm_is_capped_per_hour(self):
        inp = {"initiation": "user_asked", "title": "x", "prompt": "p", "background": "b", "model": "claude-sonnet-5-5"}
        self.assertEqual(guard(START, inp, self.transcript("brief", starts=3), self.home), "allow")
        self.assertEqual(guard(START, inp, self.transcript("brief", starts=4), self.home), "deny")
        ag = {"subagent_type": "general-purpose", "model": "sonnet", "prompt": "p", "description": "d"}
        self.assertEqual(guard("Agent", ag, self.transcript("brief", agents=7), self.home), "allow")
        self.assertEqual(guard("Agent", ag, self.transcript("brief", agents=8), self.home), "deny")

    def test_attended_session_may_spawn_more(self):
        sid_state = self.home / "g1.json"
        sid_state.write_text(json.dumps({"tool": 0, "user": 2, "driven": 1, "typed_at": time.time()}), encoding="utf-8")
        inp = {"initiation": "user_asked", "title": "x", "prompt": "p", "background": "b", "model": "claude-sonnet-5-5"}
        self.assertEqual(guard(START, inp, self.transcript("more workers", starts=6), self.home), "allow")
        self.assertEqual(guard("Workflow", {"script": "x"}, self.transcript("use a workflow"), self.home), "allow")

    def test_workflow_denied_when_unattended(self):
        self.assertEqual(guard("Workflow", {"script": "x"}, self.transcript("brief"), self.home), "deny")

    def test_scheduling_tools_denied_unless_he_asked(self):
        inp = {"delaySeconds": 600, "prompt": "x", "reason": "r"}
        for tool in ("ScheduleWakeup", "CronCreate", "RemoteTrigger", "mcp__scheduled-tasks__create_scheduled_task"):
            self.assertEqual(guard(tool, inp, self.transcript("fix the bug"), self.home), "deny", tool)
        self.assertEqual(guard("ScheduleWakeup", inp, self.transcript("/loop check the deploy"), self.home), "allow")

    def test_hooks_registered(self):
        d = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))["hooks"]["PreToolUse"]
        mg = [e for e in d if "model_guard.py" in json.dumps(e)][0]["matcher"].split("|")
        for tool in ("Workflow", "ScheduleWakeup", "CronCreate", "RemoteTrigger", "mcp__scheduled-tasks__create_scheduled_task"):
            self.assertIn(tool, mg)
        self.assertTrue([e for e in d if "turn_meter.py" in json.dumps(e) and e.get("matcher") in ("*", "")])


class StopGuardMemoryTest(unittest.TestCase):
    def test_interleaved_sessions_are_each_blocked_once(self):
        with tempfile.TemporaryDirectory() as h, mock.patch.dict(os.environ, {"MTS_STOP_GUARD_HOME": h}):
            self.assertFalse(stop_guard.seen_before("A", "1 file"))
            self.assertFalse(stop_guard.seen_before("B", "2 files"))
            self.assertTrue(stop_guard.seen_before("A", "1 file"), "B must not erase A")


if __name__ == "__main__":
    unittest.main()
