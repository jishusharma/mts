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
SEND = "SendMessage"
SEND_MGMT = "mcp__ccd_session_mgmt__send_message"


def fire_full(tool, inp, transcript=None, tasks_dir=None, claude_home=None):
    payload = {"session_id": "s1", "hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": inp,
               "transcript_path": str(transcript) if transcript else ""}
    env = {k: v for k, v in os.environ.items() if k != "MTS_ALLOW_OPUS"}
    if tasks_dir:
        env["MTS_TASKS_DIR"] = str(tasks_dir)
    if claude_home:
        env["MTS_CLAUDE_HOME"] = str(claude_home)
    r = subprocess.run([sys.executable, str(SCRIPT), "hook"], input=json.dumps(payload), capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    out = r.stdout.strip()
    if not out:
        return "allow", ""
    h = json.loads(out)["hookSpecificOutput"]
    return h["permissionDecision"], h.get("permissionDecisionReason", "")


def fire(tool, inp, transcript=None, tasks_dir=None, claude_home=None):
    return fire_full(tool, inp, transcript, tasks_dir, claude_home)[0]


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
        self.assertEqual(fire(START, {"initiation": "user_asked", "title": "x", "prompt": "p", "background": "b"}), "deny")

    def test_start_session_opus_or_fable_denied_sonnet_haiku_allowed(self):
        base = {"initiation": "user_asked", "title": "x", "prompt": "p", "background": "b"}
        self.assertEqual(fire(START, {**base, "model": "claude-opus-5-5"}), "deny")
        self.assertEqual(fire(START, {**base, "model": "claude-fable-5-1"}), "deny")
        self.assertEqual(fire(START, {**base, "model": "claude-sonnet-5-5"}), "allow")
        self.assertEqual(fire(START, {**base, "model": "claude-haiku-5-5"}), "allow")

    def test_offer_card_without_model_is_denied_but_starting_a_proposal_passes(self):
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

    def test_fork_follows_parent_model(self):
        inp = {"initiation": "user_asked", "title": "x", "prompt": "p", "context": "fork"}
        self.assertEqual(fire(START, inp, self.transcript("claude-opus-5-5")), "deny")
        self.assertEqual(fire(START, inp, self.transcript("claude-sonnet-5-5")), "allow")
        self.assertEqual(fire(START, inp, None), "deny")  # parent unknown: fail closed
        self.assertEqual(fire("Agent", {"subagent_type": "fork", "prompt": "p"}, self.transcript("claude-opus-5-5")), "deny")
        self.assertEqual(fire("Agent", {"subagent_type": "fork", "prompt": "p"}, self.transcript("claude-haiku-5-5")), "allow")

    def test_a_started_session_starts_workers_as_agents_not_sessions(self):
        # E2E run 2026-10-22: a Supervisor started by the super session called start_session for two Builders;
        # the app asked the operator to approve each one and the run stalled until he came back
        p = Path(self.tmp.name) / "child.jsonl"
        brief = ("<system-reminder>\nYou are operating in a git worktree.\n</system-reminder>\n\n"
                 "Background (from the session that started this one):\nE2E run.\n\nYou are Supervisor. Login B.")
        p.write_text(json.dumps({"type": "user", "message": {"content": brief}}) + "\n", encoding="utf-8")
        inp = {"initiation": "user_asked", "title": "Builder", "prompt": "You are Builder.", "background": "b" * 90,
               "model": "claude-sonnet-5-5"}
        decision, reason = fire_full(START, inp, p)
        self.assertEqual(decision, "deny")
        self.assertIn("Agent tool", reason)
        self.assertEqual(fire("Agent", {"description": "d", "prompt": "You are Builder.", "model": "sonnet"}, p), "allow")
        self.assertEqual(fire(START, inp, self.transcript("claude-sonnet-5-5")), "allow")   # a plain session (no role line): unchanged
        # operator 2026-10-22: the login B Supervisor he started himself on the NUC got the same approval card
        role = Path(self.tmp.name) / "role.jsonl"
        role.write_text(json.dumps({"type": "user", "message": {"content": "You are Supervisor. Login B. Continue."}}) + "\n",
                        encoding="utf-8")
        decision, reason = fire_full(START, inp, role)
        self.assertEqual(decision, "deny")
        self.assertIn("Agent tool", reason)

    def test_his_typed_turn_in_a_role_session_may_start_a_session_without_the_word_session(self):
        # operator 2026-10-23 15:16: "if I ask a super session to start a thinker, why it is making me click? ... I can say that,
        # okay, start a thinker and do this, so that it is ready." 3d54646f6 allowed it only when his message said "session".
        p = Path(self.tmp.name) / "sup_typed.jsonl"
        start = {"type": "user", "message": {"content": '<pasted_content id="1">\nYou are Supervisor. Login C.\n</pasted_content>'}}
        reply = {"type": "assistant", "message": {"model": "claude-opus-5-5", "content": []}}
        inp = {"initiation": "user_asked", "title": "Thinker", "prompt": "You are Thinker.\nTopic: x", "background": "b" * 90,
               "model": "claude-sonnet-5-5"}

        def put(*rows):
            p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

        put(start, reply, {"type": "user", "message": {"content": "start a thinker and do this, so that it is ready"}})
        self.assertEqual(fire(START, inp, p), "allow")
        put(start)                                              # the pasted start line itself: its first turn, no typed ask yet
        self.assertEqual(fire(START, inp, p), "deny")
        put(start, reply, {"type": "user", "message": {"content": "start a thinker"}}, reply,
            {"type": "user", "message": {"content": "<task-notification>\n<task-id>a1</task-id>\n</task-notification>"}})
        self.assertEqual(fire(START, inp, p), "deny")           # an event opened this turn: the app shows a card
        brief = {"type": "user", "message": {"content": "Background (from the session that started this one): x\n\nTask:\nYou are Builder."}}
        put(brief, reply, {"type": "user", "message": {"content": "start a thinker"}})
        self.assertEqual(fire(START, inp, p), "allow")          # a started session he types into is his turn too
        put(brief)
        self.assertEqual(fire(START, inp, p), "deny")
        # replay 2026-10-23: a /compact echo or an interrupt note is not his ask, and a compaction since his ask brings the card back
        ask = {"type": "user", "message": {"content": "start a thinker"}}
        for tail in ({"type": "user", "message": {"content": "<command-name>/compact</command-name>\n<command-message>compact"}},
                     {"type": "user", "message": {"content": "[Request interrupted by user for tool use]"}},
                     {"type": "system", "subtype": "compact_boundary", "compactMetadata": {"postTokens": 9}}):
            put(start, reply, ask, reply, tail)
            self.assertEqual(fire(START, inp, p), "deny" if tail.get("type") == "system" or "compact" in str(tail) else "allow", tail)
        put(start, reply, ask, reply, {"type": "user", "message": {"content": "This session is being continued from a previous conversation"}})
        self.assertEqual(fire(START, inp, p), "deny")           # an unflagged compaction summary (diff review finding 3)
        # odd lines never crash the hook (diff review finding 1): a non-dict line, a string message, an int text block
        for odd in ([1], {"type": "user", "message": "hi"}, {"type": "user", "message": {"content": [{"type": "text", "text": 5}]}}):
            put(start, reply, ask, odd)
            self.assertEqual(fire(START, inp, p), "allow", odd)

    def test_operator_typed_mid_turn_session_ask_reaches_the_guard(self):
        # operator 2026-10-23, typed while a Supervisor turn ran: "issue another Opus session ... start a new session which I can see".
        # The app stores such a message as a queued_command attachment; the guard read only user entries and denied the start.
        sup = Path(self.tmp.name) / "sup_mid.jsonl"
        rows = [{"type": "user", "message": {"content": "You are Supervisor. Login C."}},
                {"type": "assistant", "message": {"model": "claude-opus-5-5", "content": []}},
                {"type": "attachment", "attachment": {"type": "queued_command",
                                                      "prompt": "So issue another Opus session. Start a new session which I can see."}}]
        sup.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        inp = {"initiation": "user_asked", "title": "Opus review", "prompt": "You are Builder.\nStandby.", "background": "b" * 90,
               "model": "claude-opus-5-5"}
        self.assertEqual(fire(START, inp, sup), "allow")
        # a background task-notification queued after his message does not turn his typed turn into an event turn
        rows.append({"type": "attachment", "attachment": {"type": "queued_command",
                                                          "prompt": "<task-notification>\n<task-id>a1</task-id>\n</task-notification>"}})
        sup.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        self.assertEqual(fire(START, inp, sup), "allow")
        rows[2]["attachment"]["prompt"] = "fix the report"         # no session asked, no Opus named: still denied
        sup.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        self.assertEqual(fire(START, inp, sup), "deny")

    def test_interactive_role_starts_as_a_session_from_a_role_session_and_never_as_an_agent(self):
        # operator 2026-10-23: a Supervisor could not start Eagle_Eyes as a session and was told to use a background Agent
        sup = Path(self.tmp.name) / "sup.jsonl"
        sup.write_text(json.dumps({"type": "user", "message": {"content": "You are Supervisor. Login B."}}) + "\n", encoding="utf-8")
        inp = {"initiation": "user_asked", "title": "Eagle", "prompt": "You are Eagle_Eyes.\nRead the screenshots.",
               "background": "b" * 90, "model": "claude-sonnet-5-5"}
        self.assertEqual(fire(START, inp, sup), "allow")
        self.assertEqual(fire(START, dict(inp, prompt="You are Builder.\nCard x."), sup), "deny")
        decision, reason = fire_full("Agent", {"description": "d", "prompt": "You are Eagle_Eyes.", "model": "sonnet"}, sup)
        self.assertEqual(decision, "deny")
        self.assertIn("never background Agents", reason)

    def first(self, name, text):
        p = Path(self.tmp.name) / name
        p.write_text(json.dumps({"type": "user", "message": {"content": text}}) + "\n", encoding="utf-8")
        return p

    def test_a_role_session_never_shows_the_operator_buttons(self):
        # operator 2026-10-22: the login A Supervisor on the laptop showed him buttons to click
        role = self.first("role.jsonl", "You are Supervisor. Login A. Week is 97%.")
        brief = self.first("brief.jsonl", "Background (from the session that started this one):\nx\n\nYou are Builder. Card e2e.")
        ask = {"questions": [{"question": "Which?", "header": "h", "multiSelect": False, "options": []}]}
        for t in (role, brief):
            decision, reason = fire_full("AskUserQuestion", ask, t)
            self.assertEqual(decision, "deny")
            self.assertIn("Do not ask", reason)
            self.assertEqual(fire("mcp__ccd_turn__wrap_up", {"recap": "r", "ask": "Ship it?", "actions": [{"label": "Yes"}]}, t), "deny")
            self.assertEqual(fire("mcp__ccd_turn__wrap_up", {"recap": "r", "actions": [{"action": "commit"}]}, t), "deny")
            self.assertEqual(fire("mcp__ccd_turn__wrap_up", {"recap": "r"}, t), "allow")
            self.assertEqual(fire("mcp__ccd_directory__propose_branch", {"branch": "x"}, t), "deny")
        plain = self.transcript("claude-sonnet-5-5")     # an ordinary session (no role line) keeps its cards
        self.assertEqual(fire("AskUserQuestion", ask, plain), "allow")
        self.assertEqual(fire("mcp__ccd_turn__wrap_up", {"recap": "r", "ask": "Ship it?"}, plain), "allow")
        mention = self.first("mention.jsonl", "what does the Supervisor do? You are Supervisor-ish only in a quote")
        self.assertEqual(fire("AskUserQuestion", ask, mention), "allow")

    def test_start_session_on_an_event_turn_is_denied_even_user_asked(self):
        # operator 2026-10-23: "when i am away, this happens" - a coordinator woken by two child messages called start_session
        # (user_asked, sonnet) and the app showed him an Allow card; typed turns keep starting at once
        inp = {"initiation": "user_asked", "title": "x", "prompt": "p", "background": "b", "model": "sonnet"}
        p = Path(self.tmp.name) / "ev.jsonl"
        rows = [{"type": "user", "message": {"content": "start the CBP fetcher worker"}},
                {"type": "assistant", "message": {"model": "claude-sonnet-5-5", "content": []}},
                {"type": "user", "message": {"content": "<cross-session-message from=\"w\">shipped</cross-session-message>"}},
                {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t", "content": "ok"}]}}]
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write("".join(json.dumps(r) + "\n" for r in rows))
        decision, reason = fire_full(START, inp, p)
        self.assertEqual(decision, "deny")
        self.assertIn("Agent", reason)
        self.assertEqual(fire(START, inp, self.transcript("claude-sonnet-5-5")), "allow")
        self.assertEqual(fire(START, {**inp, "proposal_id": "p1"}, p), "allow")

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
        for tool in ("Agent", "Task", START, SET_MODEL, SEND, SEND_MGMT, "AskUserQuestion", "mcp__ccd_turn__wrap_up",
                     "mcp__ccd_directory__propose_branch"):
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
