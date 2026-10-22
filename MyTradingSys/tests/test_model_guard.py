"""scripts/dev/model_guard.py (operator rule 2026-10-22): sessions may start/switch to any model, Agent/Task keep the cheap-model rule,
background agents (payload agent_id) may spawn nothing, click cards stay denied, and the hook is registered in .claude/settings.json."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(os.environ.get("MG_SCRIPT") or REPO / "scripts" / "dev" / "model_guard.py")
START = "mcp__ccd_session__start_session"
SET_MODEL = "mcp__ccd_session_mgmt__set_session_model"
SEND = "SendMessage"
SEND_MGMT = "mcp__ccd_session_mgmt__send_message"


def run_hook(tool, inp, transcript=None, tasks_dir=None, claude_home=None, extra=None):
    payload = {"session_id": "s1", "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": inp,
               "transcript_path": str(transcript) if transcript else "", **(extra or {})}
    env = {k: v for k, v in os.environ.items() if k != "MTS_ALLOW_OPUS"}
    if tasks_dir:
        env["MTS_TASKS_DIR"] = str(tasks_dir)
    if claude_home:
        env["MTS_CLAUDE_HOME"] = str(claude_home)
    r = subprocess.run([sys.executable, str(SCRIPT), "hook"], input=json.dumps(payload), capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    out = r.stdout.strip()
    return json.loads(out)["hookSpecificOutput"] if out else None


def fire_full(tool, inp, transcript=None, tasks_dir=None, claude_home=None, extra=None):
    h = run_hook(tool, inp, transcript, tasks_dir, claude_home, extra)
    if not h or "permissionDecision" not in h:
        return "allow", ""
    return h["permissionDecision"], h.get("permissionDecisionReason", "")


def fire(tool, inp, transcript=None, tasks_dir=None, claude_home=None, extra=None):
    return fire_full(tool, inp, transcript, tasks_dir, claude_home, extra)[0]


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

    def test_start_session_any_model_or_none_is_allowed(self):
        # operator 2026-10-22: a child session may run any model, never refused
        base = {"initiation": "user_asked", "title": "x", "prompt": "p", "background": "b"}
        self.assertEqual(fire(START, base), "allow")
        for m in ("claude-opus-5-5", "claude-fable-5-1", "claude-sonnet-5-5", "claude-haiku-5-5"):
            self.assertEqual(fire(START, {**base, "model": m}), "allow", m)

    def test_click_card_without_model_is_denied_but_starting_a_proposal_passes(self):
        self.assertEqual(fire(START, {"initiation": "offer", "title": "x"}), "deny")
        self.assertEqual(fire(START, {"proposal_id": "task_1"}), "allow")
        self.assertEqual(fire(START, {"proposal_id": "task_1", "prompt": "p", "model": "claude-sonnet-5-5"}), "allow")

    def test_click_cards_are_denied_for_every_model_but_user_asked_passes(self):
        # operator 2026-10-18: nobody is at the screen to click "offer" / "own_initiative" cards
        base = {"title": "x", "prompt": "p", "background": "b", "model": "claude-sonnet-5-5"}
        for init in ("offer", "own_initiative", None):
            inp = {**base, **({"initiation": init} if init else {})}
            self.assertEqual(fire(START, inp), "deny", init)
        self.assertEqual(fire(START, {**base, "initiation": "user_asked", "target": "cloud"}), "allow")
        self.assertEqual(fire(START, {**base, "initiation": "offer", "target": "cloud"}), "deny")
        self.assertEqual(fire(START, {**base, "initiation": "own_initiative", "model": "claude-opus-5-5"}), "deny")

    def test_session_fork_allowed_from_any_parent_but_agent_fork_needs_cheap_parent(self):
        inp = {"initiation": "user_asked", "title": "x", "prompt": "p", "context": "fork"}
        self.assertEqual(fire(START, inp, self.transcript("claude-opus-5-5")), "allow")
        self.assertEqual(fire(START, inp, self.transcript("claude-sonnet-5-5")), "allow")
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

    def test_operator_naming_opus_lets_the_explicit_agent_model_through(self):
        self.assertEqual(fire("Agent", {"description": "d", "prompt": "p", "model": "opus"}, self.named_transcript("use Opus")), "allow")

    def test_agent_opus_not_named_or_named_earlier_still_denied(self):
        a = {"description": "d", "prompt": "p", "model": "opus"}
        self.assertEqual(fire("Agent", a, self.named_transcript("fix the report")), "deny")
        self.assertEqual(fire("Agent", a, self.named_transcript("use opus", "go ahead")), "deny")  # only the latest message counts
        self.assertEqual(fire("Agent", {"description": "d", "prompt": "p"}, self.named_transcript("use opus")), "deny")  # model still required

    def test_agent_may_use_opus_only_for_an_approved_crucial_opus_card(self):
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
        base = {"description": "x", "model": "opus"}
        self.assertEqual(fire("Agent", {**base, "prompt": "do card ok-card"}, quiet, d), "allow")
        for cid in ("no-why", "no-approval", "wrong-lane", "finished"):
            self.assertEqual(fire("Agent", {**base, "prompt": f"do card {cid}"}, quiet, d), "deny", cid)
        self.assertEqual(fire("Agent", {**base, "prompt": "no card cited"}, quiet, d), "deny")

    def test_set_session_model_any_model(self):
        for m in ("claude-opus-5-5", "claude-fable-5-1", "claude-sonnet-5-5"):
            self.assertEqual(fire(SET_MODEL, {"session_id": "a", "model": m}), "allow", m)

    def test_background_agent_may_spawn_nothing(self):
        # operator 2026-10-22: a background agent is one-shot; agent_id in the payload marks a call fired inside one
        ok = {
            "Agent": {"description": "d", "prompt": "p", "model": "sonnet"},
            START: {"initiation": "user_asked", "title": "x", "prompt": "p", "model": "claude-sonnet-5-5"},
            SET_MODEL: {"session_id": "a", "model": "claude-sonnet-5-5"},
            SEND: {"to": "local_x", "message": "m"},
            "Workflow": {"script": "x"},
        }
        for tool, inp in ok.items():
            dec, reason = fire_full(tool, inp, extra={"agent_id": "ag1", "agent_type": "general-purpose"})
            self.assertEqual(dec, "deny", tool)
            self.assertIn("one-shot", reason, tool)
        self.assertEqual(fire("Agent", ok["Agent"]), "allow")
        self.assertEqual(fire(START, ok[START]), "allow")
        self.assertEqual(fire(SET_MODEL, ok[SET_MODEL]), "allow")
        self.assertEqual(fire("Agent", {"description": "d", "prompt": "p"}), "deny")  # normal rules still apply without agent_id

    def test_start_above_own_model_adds_set_session_model_hint(self):
        inp = {"initiation": "user_asked", "title": "x", "prompt": "p", "background": "b", "model": "claude-opus-5-5"}
        h = run_hook(START, inp, self.transcript("claude-sonnet-5-5"))
        self.assertIsNotNone(h)
        self.assertNotIn("permissionDecision", h)
        self.assertEqual(h["hookEventName"], "PreToolUse")
        self.assertIn("set_session_model", h["additionalContext"])
        self.assertIsNone(run_hook(START, inp, self.transcript("claude-opus-5-5")))
        self.assertIsNone(run_hook(START, {**inp, "model": "claude-sonnet-5-5"}, self.transcript("claude-opus-5-5")))

    def test_hint_also_when_operator_names_opus(self):
        inp = {"initiation": "user_asked", "title": "x", "prompt": "p", "background": "b", "model": "claude-opus-5-5"}
        h = run_hook(START, inp, self.named_transcript("start an opus session"))
        self.assertIn("set_session_model", (h or {}).get("additionalContext", ""))

    def test_mts_allow_opus_env_is_removed_by_the_harness(self):
        # the harness strips MTS_ALLOW_OPUS so a leaked env var cannot turn the Agent rule off in tests
        os.environ["MTS_ALLOW_OPUS"] = "1"
        try:
            self.assertEqual(fire("Agent", {"description": "d", "prompt": "p", "model": "opus"}), "deny")
        finally:
            del os.environ["MTS_ALLOW_OPUS"]

    def test_cloud_start_and_other_tools_pass(self):
        self.assertEqual(fire(START, {"initiation": "user_asked", "title": "x", "prompt": "p", "target": "cloud"}), "allow")
        self.assertEqual(fire("Bash", {"command": "ls"}), "allow")

    def test_hook_registered_for_every_guarded_tool(self):
        d = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
        entries = [e for e in d["hooks"].get("PreToolUse", []) if "model_guard.py" in json.dumps(e)]
        self.assertEqual(len(entries), 1)
        matcher = entries[0]["matcher"].split("|")
        for tool in ("Agent", "Task", START, SET_MODEL, SEND, SEND_MGMT):
            self.assertIn(tool, matcher)

    def _sv8_env(self):
        ch = Path(self.tmp.name) / "claude"
        proj = ch / "projects" / "proj"
        sess_dir = ch / "sessions"
        proj.mkdir(parents=True)
        sess_dir.mkdir(parents=True)

        # Parent transcript with two started sessions: local_sonnet and local_fable
        parent_t = proj / "parent-uuid.jsonl"
        parent_lines = [
            {"type": "assistant", "message": {"model": "claude-sonnet-5-5", "content": [
                {"type": "tool_use", "id": "tu_1", "name": START, "input": {"title": "w1", "model": "claude-sonnet-5-5"}},
                {"type": "tool_use", "id": "tu_2", "name": START, "input": {"title": "w2", "model": "claude-sonnet-5-5"}},
                {"type": "tool_use", "id": "tu_3", "name": START, "input": {"title": "w3", "model": "claude-sonnet-5-5"}},
                {"type": "tool_use", "id": "tu_other", "name": "Bash", "input": {"command": "echo session_id: local_fake-999"}},
            ]}},
            {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "tu_1", "content": [
                    {"type": "text", "text": 'Started session "w1" (session_id: local_11111111-1111-1111-1111-111111111111, name: w1).'}
                ]},
                {"type": "tool_result", "tool_use_id": "tu_2", "content": [
                    {"type": "text", "text": 'Started session "w2" (session_id: local_22222222-2222-2222-2222-222222222222, name: w2).'}
                ]},
                {"type": "tool_result", "tool_use_id": "tu_3", "content": [
                    {"type": "text", "text": 'Started session "w3" (session_id: local_33333333-3333-3333-3333-333333333333, name: w3).'}
                ]},
                {"type": "tool_result", "tool_use_id": "tu_other", "content": "Started session (session_id: local_fake-999)"},
            ]}},
        ]
        parent_t.write_text("\n".join(json.dumps(x) for x in parent_lines) + "\n", encoding="utf-8", newline="\n")

        # Worker 1: Sonnet worker mapped via ~/.claude/sessions/101.json
        (sess_dir / "101.json").write_text(json.dumps({
            "pid": 101, "sessionId": "cli-sonnet-uuid",
            "hostSessionId": "local_11111111-1111-1111-1111-111111111111"
        }), encoding="utf-8", newline="\n")
        (proj / "cli-sonnet-uuid.jsonl").write_text(
            json.dumps({"type": "assistant", "message": {"model": "claude-sonnet-5-5", "content": []}}) + "\n",
            encoding="utf-8", newline="\n"
        )

        # Worker 2: Fable session mapped via ~/.claude/sessions/102.json
        (sess_dir / "102.json").write_text(json.dumps({
            "pid": 102, "sessionId": "cli-fable-uuid",
            "hostSessionId": "local_22222222-2222-2222-2222-222222222222"
        }), encoding="utf-8", newline="\n")
        (proj / "cli-fable-uuid.jsonl").write_text(
            json.dumps({"type": "assistant", "message": {"model": "claude-fable-5-1", "content": []}}) + "\n",
            encoding="utf-8", newline="\n"
        )
        # Worker 3 (local_33333333...): started by parent, but has no transcript on disk (unresolvable)
        return ch, parent_t

    def test_send_message_allows_own_sonnet_worker(self):
        ch, parent_t = self._sv8_env()
        sid = "local_11111111-1111-1111-1111-111111111111"
        self.assertEqual(fire(SEND, {"to": sid, "message": "status?"}, parent_t, claude_home=ch), "allow")
        self.assertEqual(fire(SEND_MGMT, {"session_id": sid, "message": "status?"}, parent_t, claude_home=ch), "allow")

    def test_send_message_denies_fable_target(self):
        ch, parent_t = self._sv8_env()
        sid = "local_22222222-2222-2222-2222-222222222222"
        dec, reason = fire_full(SEND, {"to": sid, "message": "hi"}, parent_t, claude_home=ch)
        self.assertEqual(dec, "deny")
        self.assertIn("fable", reason.lower())
        dec2, reason2 = fire_full(SEND_MGMT, {"session_id": sid, "message": "hi"}, parent_t, claude_home=ch)
        self.assertEqual(dec2, "deny")
        self.assertIn("fable", reason2.lower())

    def test_send_message_denies_unknown_target_session_id(self):
        ch, parent_t = self._sv8_env()
        for bad_sid in ("local_99999999-9999-9999-9999-999999999999", "local_fake-999", ""):
            dec, reason = fire_full(SEND, {"to": bad_sid, "message": "hi"}, parent_t, claude_home=ch)
            self.assertEqual(dec, "deny", bad_sid)
            self.assertTrue(reason, bad_sid)

    def test_send_message_fails_closed_when_target_transcript_unresolvable(self):
        ch, parent_t = self._sv8_env()
        sid = "local_33333333-3333-3333-3333-333333333333"
        dec, reason = fire_full(SEND, {"to": sid, "message": "hi"}, parent_t, claude_home=ch)
        self.assertEqual(dec, "deny")
        self.assertTrue(reason)
        # Missing parent transcript also fails closed
        dec_no_parent, reason_no_parent = fire_full(SEND, {"to": "local_11111111-1111-1111-1111-111111111111", "message": "hi"}, None, claude_home=ch)
        self.assertEqual(dec_no_parent, "deny")
        self.assertTrue(reason_no_parent)


if __name__ == "__main__":
    unittest.main()
