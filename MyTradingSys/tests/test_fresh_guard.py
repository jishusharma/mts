"""scripts/dev/fresh_guard.py: a Stop hook that blocks a long reply stating repo facts when the turn read nothing from disk."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "dev" / "fresh_guard.py"

CLAIM = ("The model_guard.py hook denies Opus starts unless the operator names it, and the rule lives in CLAUDE.md. "
         "Each worker runs on Sonnet and the budget is tracked per login, so nothing needs changing here for now. " * 2)
PLAIN = ("Sure, here is a friendly answer with plenty of words but nothing about the system at all. "
         "The weather is nice today and a walk would be pleasant, so take a break and breathe. " * 3)


def user(text):
    return {"type": "user", "message": {"content": text}}


def assistant(text=None, tool=None):
    c = []
    if text:
        c.append({"type": "text", "text": text})
    if tool:
        c.append({"type": "tool_use", "id": "t1", "name": tool, "input": {}})
    return {"type": "assistant", "message": {"content": c}}


def result():
    return {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]}}


class FreshGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def fire(self, entries, message=CLAIM, **extra):
        p = Path(self.tmp.name) / "t.jsonl"
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        return self.run_payload({"transcript_path": str(p), "last_assistant_message": message, **extra})

    def run_payload(self, payload):
        env = {k: v for k, v in os.environ.items() if k != "MTS_FRESH_GUARD"}
        r = subprocess.run([sys.executable, str(SCRIPT), "hook"], input=json.dumps(payload), capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)["decision"] if r.stdout.strip() else "allow"

    def test_claim_reply_with_zero_reads_is_blocked(self):
        self.assertEqual(self.fire([user("what is the rule?"), assistant(CLAIM)]), "block")

    def test_read_after_last_operator_message_allows(self):
        es = [user("what is the rule?"), assistant(tool="Read"), result(), assistant(CLAIM)]
        self.assertEqual(self.fire(es), "allow")

    def test_read_before_last_operator_message_does_not_count(self):
        es = [user("first"), assistant(tool="Grep"), result(), assistant("done"), user("and the rule now?"), assistant(CLAIM)]
        self.assertEqual(self.fire(es), "block")

    def test_short_or_claim_free_reply_allows(self):
        es = [user("q"), assistant("x")]
        self.assertEqual(self.fire(es, message="see model_guard.py, short"), "allow")
        self.assertEqual(self.fire(es, message=PLAIN), "allow")

    def test_app_ui_words_alone_do_not_block(self):
        # false positives measured on a real transcript: "click card", lowercase "workers", backticked app identifiers
        ui = ("The app shows a card when the session asks for a bigger model, so you click it once. Workers should be "
              "subagents, never child sessions, and `user_asked` starts at once while `own_initiative` always asks first. " * 2)
        self.assertEqual(self.fire([user("q"), assistant(ui)], message=ui), "allow")

    def test_task_card_claim_still_blocks(self):
        msg = ("The task card status moves to claimed after the worker runs the claim step, and the branch is then pinned. " * 3)
        self.assertEqual(self.fire([user("q"), assistant(msg)], message=msg), "block")

    def test_stop_hook_active_allows(self):
        self.assertEqual(self.fire([user("q"), assistant(CLAIM)], stop_hook_active=True), "allow")

    def test_agent_id_allows(self):
        self.assertEqual(self.fire([user("q"), assistant(CLAIM)], agent_id="a1"), "allow")

    def test_event_only_user_message_is_not_the_turn_boundary(self):
        event = user("<task-notification>\n<task-id>x</task-id>\nworker finished\n</task-notification>")
        es = [user("what is the rule?"), assistant(tool="Read"), result(), event, assistant(CLAIM)]
        self.assertEqual(self.fire(es), "allow")

    def test_unreadable_transcript_allows(self):
        missing = str(Path(self.tmp.name) / "nope.jsonl")
        self.assertEqual(self.run_payload({"transcript_path": missing, "last_assistant_message": CLAIM}), "allow")

    def test_message_falls_back_to_last_assistant_text(self):
        p = Path(self.tmp.name) / "t.jsonl"
        p.write_text(json.dumps(user("q")) + "\n" + json.dumps(assistant(CLAIM)) + "\n", encoding="utf-8", newline="\n")
        self.assertEqual(self.run_payload({"transcript_path": str(p)}), "block")


if __name__ == "__main__":
    unittest.main()
