"""scripts/dev/turn_meter.py: the SHORT SESSIONS cap (40 tool / 10 operator turns, CLAUDE.md) fires as a hook, resets on compact,
skips subagents (shared session_id), counts parallel tool calls of one assistant message once, and nags in <= 250 bytes."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "dev" / "turn_meter.py"


sys.path.insert(0, str(SCRIPT.parent))
import turn_meter  # noqa: E402


def hook_env(home, env=None):
    e = {k: v for k, v in os.environ.items() if not k.startswith("MTS_TURN_METER")}
    e.update({"MTS_TURN_METER_HOME": str(home), **(env or {})})
    return e


def fire(home, event, sid="s1", extra=None, env=None):
    """One hook call, in-process (GATE_SPEED D7, 2026-10-18: a python process per call made this the slowest file of shard 4, 195 s
    of ~1400 calls); fire_proc keeps the real `turn_meter.py hook` stdin/stdout path covered."""
    payload = {"session_id": sid, "hook_event_name": event, "cwd": "C:/x", **(extra or {})}
    with mock.patch.dict(os.environ, hook_env(home, env), clear=True):
        return turn_meter.handle(payload).strip()


def fire_proc(home, event, sid="s1", extra=None, env=None):
    payload = {"session_id": sid, "hook_event_name": event, "cwd": "C:/x", **(extra or {})}
    r = subprocess.run([sys.executable, str(SCRIPT), "hook"], input=json.dumps(payload), capture_output=True, text=True,
                       env=hook_env(home, env))
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def write_transcript(path, messages, pad=0):
    """Transcript lines as Claude Code writes them: one assistant line per content block (parallel tool calls share the
    message id), then the tool_result user lines. messages: [(message_id, [tool_use_id, ...])]. pad: filler bytes after."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for mid, ids in messages:
            f.write(json.dumps({"type": "assistant", "message": {"id": mid, "content": [{"type": "thinking", "thinking": ""}]}}) + "\n")
            for tid in ids:
                f.write(json.dumps({"type": "assistant", "message": {"id": mid, "content": [
                    {"type": "tool_use", "id": tid, "name": "Bash", "input": {}}]}}) + "\n")
            for tid in ids:
                f.write(json.dumps({"type": "user", "message": {"content": [
                    {"type": "tool_result", "tool_use_id": tid, "content": "x" * pad}]}}) + "\n")


class TurnMeterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def counts(self, sid="s1"):
        return json.loads((self.home / f"{sid}.json").read_text(encoding="utf-8"))

    def test_subagent_calls_are_not_counted_or_nagged(self):
        # workflow subagents share the parent's session_id; Claude Code marks their hooks with agent_id
        for _ in range(30):
            self.assertEqual(fire(self.home, "PostToolUse", extra={"agent_id": "a1", "agent_type": "workflow-subagent"}), "")
        self.assertFalse((self.home / "s1.json").exists())
        fired = [n for n in range(1, 41) if fire(self.home, "PostToolUse")]
        self.assertEqual(fired, [40])  # the parent's own counter was untouched by the 30 subagent calls

    def test_subagent_detected_by_transcript_path(self):
        for tp in ("C:/u/.claude/projects/p/s1/subagents/workflows/wf_1/agent-a1.jsonl",
                   "C:\\u\\.claude\\projects\\p\\s1\\subagents\\agent-a1.jsonl"):
            for _ in range(20):
                self.assertEqual(fire(self.home, "PostToolUse", extra={"transcript_path": tp}), "")
        self.assertFalse((self.home / "s1.json").exists())

    def test_agent_type_alone_is_the_main_thread(self):
        # a session started with --agent sends agent_type on the main thread, without agent_id: it must still be metered
        fired = [n for n in range(1, 41) if fire(self.home, "PostToolUse", extra={"agent_type": "reviewer"})]
        self.assertEqual(fired, [40])

    def test_parallel_calls_in_one_message_count_once(self):
        tp = self.home / "t.jsonl"
        msgs = [(f"msg_{m}", [f"toolu_{m}_{k}" for k in range(3)]) for m in range(1, 43)]
        write_transcript(tp, msgs)
        fired = []
        for m, (mid, ids) in enumerate(msgs, 1):
            for tid in ids:
                if fire(self.home, "PostToolUse", extra={"tool_use_id": tid, "transcript_path": str(tp)}):
                    fired.append((m, tid))
        self.assertEqual(fired, [(40, "toolu_40_0")])  # 126 calls = 42 turns; the 3 calls of message 40 are one turn
        self.assertEqual(self.counts()["tool"], 42)

    def test_message_beyond_first_tail_window_is_found(self):
        tp = self.home / "t.jsonl"
        write_transcript(tp, [("msg_a", ["toolu_a0", "toolu_a1"])], pad=200_000)  # big results push the tool_use out of 128 KB
        for _ in range(3):
            fire(self.home, "PostToolUse", extra={"tool_use_id": "toolu_a0", "transcript_path": str(tp)})
            fire(self.home, "PostToolUse", extra={"tool_use_id": "toolu_a1", "transcript_path": str(tp)})
        self.assertEqual(self.counts()["tool"], 1)

    def test_unreadable_transcript_counts_every_call(self):
        # fail open: no way to tell which message a call belongs to -> one turn per call, as before
        tp = self.home / "t.jsonl"
        write_transcript(tp, [("msg_a", ["toolu_a0"])])
        cases = {"id_not_in_transcript": {"tool_use_id": "toolu_zz", "transcript_path": str(tp)},
                 "transcript_missing": {"tool_use_id": "toolu_a0", "transcript_path": str(self.home / "missing.jsonl")},
                 "no_transcript_path": {"tool_use_id": "toolu_a0"}}
        for sid, extra in cases.items():
            for _ in range(2):
                fire(self.home, "PostToolUse", sid=sid, extra=extra)
        self.assertEqual({sid: self.counts(sid)["tool"] for sid in cases}, {sid: 2 for sid in cases})

    def test_nag_is_short_and_names_the_handoff(self):
        for name, state in (("s1", {"tool": 39, "user": 0}), ("s2", {"tool": 1999, "user": 99})):
            (self.home / f"{name}.json").write_text(json.dumps(state), encoding="utf-8")
        post = json.loads(fire(self.home, "PostToolUse", sid="s1"))["hookSpecificOutput"]["additionalContext"]
        prompt = fire(self.home, "UserPromptSubmit", sid="s2")
        worst = json.loads(fire(self.home, "PostToolUse", sid="s2"))["hookSpecificOutput"]["additionalContext"]
        for text in (post, prompt, worst):
            self.assertLessEqual(len(text.encode("utf-8")), 250, text)
            self.assertIn("RELAY.md", text)
            self.assertIn("relay.py handoff", text)

    def test_tool_cap_fires_at_40_then_every_5(self):
        fired = [n for n in range(1, 51) if fire(self.home, "PostToolUse")]
        self.assertEqual(fired, [40, 45, 50])

    def test_post_tool_output_is_additional_context_json(self):
        for _ in range(39):
            fire(self.home, "PostToolUse")
        out = json.loads(fire_proc(self.home, "PostToolUse"))   # the real hook process prints the same JSON
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "PostToolUse")
        self.assertIn("cap 40 / 10", ctx)
        self.assertIn("relay.py handoff", ctx)

    def test_operator_turns_over_10_fire(self):
        fired = [n for n in range(1, 13) if fire(self.home, "UserPromptSubmit")]
        self.assertEqual(fired, [11, 12])

    def test_prompt_after_tool_cap_fires(self):
        for _ in range(40):
            fire(self.home, "PostToolUse")
        self.assertIn("[TURN METER]", fire(self.home, "UserPromptSubmit"))

    def test_clear_resets(self):
        for _ in range(41):
            fire(self.home, "PostToolUse")
        fire(self.home, "SessionStart", extra={"source": "clear"})
        self.assertEqual(fire(self.home, "UserPromptSubmit"), "")
        self.assertEqual([n for n in range(1, 41) if fire(self.home, "PostToolUse")], [40])

    def model_transcript(self, model, ctx):
        tp = self.home / f"{model}.jsonl"
        tp.write_text(json.dumps({"type": "assistant", "message": {"id": "m1", "model": f"claude-{model}-5", "content": [], "usage": {
            "input_tokens": 10, "cache_creation_input_tokens": 0, "cache_read_input_tokens": ctx - 10}}}) + "\n", encoding="utf-8")
        return {"transcript_path": str(tp)}

    def test_default_models_get_fewer_turns_as_context_grows(self):
        # 4M read budget / context: 250k -> 16 turns; a small context keeps the flat 40
        big = self.model_transcript("sonnet", 250_000)
        self.assertEqual([n for n in range(1, 30) if fire(self.home, "PostToolUse", sid="a", extra=big)][:2], [16, 21])
        small = self.model_transcript("sonnet", 50_000)
        self.assertEqual([n for n in range(1, 50) if fire(self.home, "PostToolUse", sid="b", extra=small)][:1], [40])

    def test_opus_has_no_turn_cap_only_a_500k_context_cap(self):
        under = self.model_transcript("opus", 400_000)
        for _ in range(60):
            self.assertEqual(fire(self.home, "PostToolUse", sid="o", extra=under), "")
        for _ in range(12):
            self.assertEqual(fire(self.home, "UserPromptSubmit", sid="o", extra=under), "")
        over = self.model_transcript("opus", 520_000)
        self.assertIn("Opus context 520k", fire(self.home, "UserPromptSubmit", sid="o", extra=over))

    def test_fable_gets_one_message_hard_even_with_the_switch_off(self):
        f = self.model_transcript("fable", 800_000)
        self.assertEqual(fire(self.home, "UserPromptSubmit", sid="f"), "")      # first message: model not known yet, allowed
        for _ in range(80):
            self.assertEqual(fire(self.home, "PostToolUse", sid="f", extra=f), "")   # no tool-turn cap
        for env in (None, {"MTS_TURN_METER": "off", "MTS_TURN_METER_USER_CAP": "99"}):
            out = json.loads(fire(self.home, "UserPromptSubmit", sid="f", extra=f, env=env))
            self.assertEqual(out["decision"], "block")
            self.assertIn("new Fable session", out["reason"])

    def test_fable_block_survives_synthetic_lines_and_lost_transcript(self):
        f = self.model_transcript("fable", 300_000)
        fire(self.home, "UserPromptSubmit", sid="g")
        fire(self.home, "PostToolUse", sid="g", extra=f)
        with open(f["transcript_path"], "a", encoding="utf-8") as fh:      # an API-error line: <synthetic>, zero usage
            fh.write(json.dumps({"type": "assistant", "message": {"id": "m2", "model": "<synthetic>", "content": [], "usage": {"input_tokens": 1}}}) + chr(10))
        self.assertIn("block", fire(self.home, "UserPromptSubmit", sid="g", extra=f))
        fire(self.home, "UserPromptSubmit", sid="h", extra=f)
        self.assertIn("block", fire(self.home, "UserPromptSubmit", sid="h", extra=f))   # tier now remembered
        self.assertIn("block", fire(self.home, "UserPromptSubmit", sid="h"))            # transcript unreadable: still blocked

    def test_resume_keeps_counts(self):
        for _ in range(40):
            fire(self.home, "PostToolUse")
        fire(self.home, "SessionStart", extra={"source": "resume"})
        self.assertIn("[TURN METER]", fire(self.home, "UserPromptSubmit"))

    def test_sessions_are_separate(self):
        for _ in range(40):
            fire(self.home, "PostToolUse", sid="a")
        self.assertEqual(fire(self.home, "UserPromptSubmit", sid="b"), "")

    def test_fire_runs_in_process(self):
        with mock.patch.object(subprocess, "run", side_effect=AssertionError("no process per hook call")):
            self.assertEqual(fire(self.home, "PostToolUse"), "")
        self.assertEqual(self.counts()["tool"], 1)

    def test_off_and_garbage_never_fail(self):
        self.assertEqual(fire(self.home, "UserPromptSubmit", env={"MTS_TURN_METER": "off", "MTS_TURN_METER_USER_CAP": "0"}), "")
        e = {**os.environ, "MTS_TURN_METER_HOME": str(self.home)}
        r = subprocess.run([sys.executable, str(SCRIPT), "hook"], input="not json", capture_output=True, text=True, env=e)
        self.assertEqual((r.returncode, r.stdout), (0, ""))
        self.assertIn("Traceback", (self.home / "hook_errors.log").read_text(encoding="utf-8"))
        (self.home / "s1.json").write_text("{broken", encoding="utf-8")
        self.assertEqual(fire(self.home, "PostToolUse"), "")


if __name__ == "__main__":
    unittest.main()
