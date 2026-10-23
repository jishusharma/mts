"""prereq_guard.py: a session may not end by handing the operator pre-run to-dos that no card carries (operator 2026-10-22)."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prereq_guard as G


def transcript(path, reply):
    rows = [{"type": "user", "message": {"role": "user", "content": "design the run"}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "old reply: before you start, stamp it"}]}},
            {"type": "user", "message": {"role": "user", "content": "next"}},
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {}}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "content": "ok"}]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": reply}]}}]
    Path(path).write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")


class PrereqGuardTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        os.environ["MTS_STOP_GUARD_HOME"] = self.d.name
        self.t = Path(self.d.name) / "t.jsonl"

    def tearDown(self):
        os.environ.pop("MTS_STOP_GUARD_HOME", None)
        self.d.cleanup()

    def run_hook(self, reply, sid="s1", active=False):
        transcript(self.t, reply)
        return G.hook(json.dumps({"session_id": sid, "transcript_path": str(self.t), "stop_hook_active": active}))

    def test_operator_todo_without_card_blocks_once(self):
        reply = "Done.\nBefore you start it: the cards need a Lab_Guy stamp.\nSteps 2-5 must run on DESKTOP-F7IU69N."
        out = json.loads(self.run_hook(reply))
        self.assertEqual(out["decision"], "block")
        self.assertIn("tasks.py need", out["reason"])
        self.assertEqual(self.run_hook(reply), "")             # same reply, same session: never twice
        self.assertEqual(self.run_hook(reply, sid="s2", active=True), "")

    def test_lines_naming_a_card_or_operator_only_pass(self):
        reply = ("Before you start: nothing; card `confluence-s1-context-counts-need-lab-guy-review-stamp` holds the stamp.\n"
                 "OPERATOR-ONLY: you need to run defender_exclusions.ps1 as admin (needs your admin login).")
        self.assertEqual(self.run_hook(reply), "")

    def test_only_the_last_reply_is_read(self):
        self.assertEqual(G.last_reply(self.t) if self.t.exists() else "", "")
        transcript(self.t, "All shipped.")
        self.assertEqual(G.last_reply(self.t), "All shipped.")
        self.assertEqual(self.run_hook("All shipped."), "")

    def test_last_assistant_message_field_and_off_switch(self):
        data = {"session_id": "s3", "last_assistant_message": "Remember to paste the prompt after S1 ships."}
        self.assertEqual(json.loads(G.hook(json.dumps(data)))["decision"], "block")
        os.environ["MTS_PREREQ_GUARD"] = "off"
        try:
            self.assertEqual(G.hook(json.dumps(dict(data, session_id="s4"))), "")
        finally:
            os.environ.pop("MTS_PREREQ_GUARD")

    def test_garbage_input_never_raises(self):
        self.assertEqual(G.hook("not json"), "")
        self.assertEqual(G.hook(json.dumps({"transcript_path": "/no/such/file"})), "")


if __name__ == "__main__":
    unittest.main()
