"""scripts/dev/model_guard.py: session and subagent starts without a cheap model (sonnet/haiku) are denied as a PreToolUse hook,
forks pass only from a cheap session, proposals and cloud starts pass, and the hook is registered in .claude/settings.json."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "dev" / "model_guard.py"
START = "mcp__ccd_session__start_session"
SET_MODEL = "mcp__ccd_session_mgmt__set_session_model"


def fire(tool, inp, transcript=None, tasks_dir=None):
    payload = {"session_id": "s1", "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": inp,
               "transcript_path": str(transcript) if transcript else ""}
    env = {k: v for k, v in os.environ.items() if k != "MTS_ALLOW_OPUS"}
    if tasks_dir:
        env["MTS_TASKS_DIR"] = str(tasks_dir)
    r = subprocess.run([sys.executable, str(SCRIPT), "hook"], input=json.dumps(payload), capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    out = r.stdout.strip()
    return json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out else "allow"


class ModelGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def transcript(self, model):
        p = Path(self.tmp.name) / "t.jsonl"
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps({"type": "user", "message": {"content": "hi"}}) + "\n")
            f.write(json.dumps({"type": "assistant", "message": {"model": model, "content": []}}) + "\n")
        return p

    def test_start_session_without_model_is_denied(self):
        # the 2026-10-15 incident: own_initiative proposal without model inherited Opus
        self.assertEqual(fire(START, {"initiation": "own_initiative", "title": "x", "prompt": "p", "background": "b"}), "deny")

    def test_start_session_opus_or_fable_denied_sonnet_haiku_allowed(self):
        base = {"initiation": "own_initiative", "title": "x", "prompt": "p", "background": "b"}
        self.assertEqual(fire(START, {**base, "model": "claude-opus-5-5"}), "deny")
        self.assertEqual(fire(START, {**base, "model": "claude-fable-5-1"}), "deny")
        self.assertEqual(fire(START, {**base, "model": "claude-sonnet-5-5"}), "allow")
        self.assertEqual(fire(START, {**base, "model": "claude-haiku-5-5"}), "allow")

    def test_offer_card_without_model_is_denied_but_starting_a_proposal_passes(self):
        self.assertEqual(fire(START, {"initiation": "offer", "title": "x"}), "deny")
        self.assertEqual(fire(START, {"proposal_id": "task_1"}), "allow")
        self.assertEqual(fire(START, {"proposal_id": "task_1", "prompt": "p", "model": "claude-sonnet-5-5"}), "allow")

    def test_fork_follows_parent_model(self):
        inp = {"initiation": "own_initiative", "title": "x", "prompt": "p", "context": "fork"}
        self.assertEqual(fire(START, inp, self.transcript("claude-opus-5-5")), "deny")
        self.assertEqual(fire(START, inp, self.transcript("claude-sonnet-5-5")), "allow")
        self.assertEqual(fire(START, inp, None), "deny")  # parent unknown: fail closed
        self.assertEqual(fire("Agent", {"subagent_type": "fork", "prompt": "p"}, self.transcript("claude-opus-5-5")), "deny")
        self.assertEqual(fire("Agent", {"subagent_type": "fork", "prompt": "p"}, self.transcript("claude-haiku-5-5")), "allow")

    def test_agent_needs_cheap_model(self):
        self.assertEqual(fire("Agent", {"description": "d", "prompt": "p"}), "deny")
        self.assertEqual(fire("Agent", {"description": "d", "prompt": "p", "model": "opus"}), "deny")
        self.assertEqual(fire("Agent", {"description": "d", "prompt": "p", "model": "sonnet"}), "allow")
        self.assertEqual(fire("Task", {"description": "d", "prompt": "p", "model": "haiku"}), "allow")

    def named_transcript(self, *humans, model="claude-sonnet-5-5"):
        p = Path(self.tmp.name) / "n.jsonl"
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            for h in humans:
                f.write(json.dumps({"type": "user", "message": {"content": h}}) + "\n")
                f.write(json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "content": "opus"}]}}) + "\n")
            f.write(json.dumps({"type": "assistant", "message": {"model": model, "content": []}}) + "\n")
        return p

    def test_operator_naming_opus_lets_the_explicit_model_through(self):
        inp = {"initiation": "user_asked", "title": "x", "prompt": "p", "background": "b", "model": "claude-opus-5-5"}
        self.assertEqual(fire(START, inp, self.named_transcript("spawn an Opus session for this")), "allow")
        self.assertEqual(fire("Agent", {"description": "d", "prompt": "p", "model": "opus"}, self.named_transcript("use Opus")), "allow")
        self.assertEqual(fire(SET_MODEL, {"session_id": "a", "model": "claude-opus-5-5"}, self.named_transcript("use opus")), "allow")

    def test_opus_not_named_or_named_in_an_earlier_message_or_only_in_tool_output_still_denied(self):
        inp = {"initiation": "user_asked", "title": "x", "prompt": "p", "background": "b", "model": "claude-opus-5-5"}
        self.assertEqual(fire(START, inp, self.named_transcript("fix the report")), "deny")
        self.assertEqual(fire(START, inp, self.named_transcript("use opus", "go ahead")), "deny")  # only the latest message counts
        noreply = {k: v for k, v in inp.items() if k != "model"}
        self.assertEqual(fire(START, noreply, self.named_transcript("use opus")), "deny")  # still must give a model, never inherit

    def test_a_session_may_start_opus_only_for_an_approved_crucial_opus_card(self):
        d = Path(self.tmp.name) / "tasks"
        d.mkdir()
        cards = {"ok-card": {"lane": "OPUS", "approved_by": "operator", "crucial": "no-undo design call", "state": "ready"},
                 "no-why": {"lane": "OPUS", "approved_by": "operator", "state": "ready"},
                 "no-approval": {"lane": "OPUS", "crucial": "x", "state": "ready"},
                 "wrong-lane": {"lane": "SONNET", "approved_by": "operator", "crucial": "x", "state": "ready"},
                 "finished": {"lane": "OPUS", "approved_by": "operator", "crucial": "x", "state": "done"}}
        for cid, c in cards.items():
            (d / (cid + ".json")).write_text(json.dumps(c), encoding="utf-8", newline=chr(10))
        quiet = self.named_transcript("fix the report")
        base = {"initiation": "user_asked", "title": "x", "background": "b", "model": "claude-opus-5-5"}
        self.assertEqual(fire(START, {**base, "prompt": "do card ok-card"}, quiet, d), "allow")
        for cid in ("no-why", "no-approval", "wrong-lane", "finished"):
            self.assertEqual(fire(START, {**base, "prompt": f"do card {cid}"}, quiet, d), "deny", cid)
        self.assertEqual(fire(START, {**base, "prompt": "no card cited"}, quiet, d), "deny")

    def test_set_session_model_only_cheap(self):
        self.assertEqual(fire(SET_MODEL, {"session_id": "a", "model": "claude-opus-5-5"}), "deny")
        self.assertEqual(fire(SET_MODEL, {"session_id": "a", "model": "claude-sonnet-5-5"}), "allow")

    def test_cloud_start_and_other_tools_pass(self):
        self.assertEqual(fire(START, {"initiation": "user_asked", "title": "x", "prompt": "p", "target": "cloud"}), "allow")
        self.assertEqual(fire("Bash", {"command": "ls"}), "allow")

    def test_hook_registered_for_every_guarded_tool(self):
        d = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
        entries = [e for e in d["hooks"].get("PreToolUse", []) if "model_guard.py" in json.dumps(e)]
        self.assertEqual(len(entries), 1)
        matcher = entries[0]["matcher"].split("|")
        for tool in ("Agent", "Task", START, SET_MODEL):
            self.assertIn(tool, matcher)


if __name__ == "__main__":
    unittest.main()
