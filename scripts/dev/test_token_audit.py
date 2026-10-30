import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import token_audit as ta  # noqa: E402


def _row(role, **kw):
    return json.dumps({"timestamp": "2026-10-12T00:00:00Z", "message": dict(role=role, **kw)})


class TokenAuditTest(unittest.TestCase):
    def _write(self, rows):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "proj"))
        p = os.path.join(d, "proj", "s.jsonl")
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(rows) + "\n")
        return d, p

    def test_totals_dedupe_and_label(self):
        u1 = {"input_tokens": 3, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 50, "output_tokens": 5}
        u1b = dict(u1, output_tokens=9)  # streaming repeat of same id: last wins
        u2 = {"input_tokens": 1, "cache_read_input_tokens": 150, "cache_creation_input_tokens": 0, "output_tokens": 7}
        d, p = self._write([
            _row("user", content="[SCHEDULED TASK] mts-dispatcher"),
            _row("assistant", id="a", usage=u1, content=[{"type": "tool_use"}]),
            _row("assistant", id="a", usage=u1b, content=[]),
            _row("user", content=[{"type": "tool_result", "content": "IDLE no work"}]),
            _row("assistant", id="b", usage=u2, content=[]),
        ])
        r = ta.audit_file(p)
        self.assertEqual(r["label"], "dispatcher-idle")
        self.assertEqual(r["turns"], 2)
        self.assertEqual(r["totals"]["output_tokens"], 16)
        self.assertEqual(r["totals"]["cache_read_input_tokens"], 250)
        self.assertEqual(r["first_input"], 153)
        self.assertEqual(r["tools"], 1)
        rows = ta.audit_root(d, 7)
        self.assertEqual(len(rows), 1)
        self.assertIn("dispatcher-idle", ta.render(rows, 7))

    def test_kick_label(self):
        u = {"input_tokens": 1, "output_tokens": 1}
        d, p = self._write([
            _row("user", content="mts-dispatcher run"),
            _row("assistant", id="a", usage=u, content=[]),
            _row("user", content=[{"type": "tool_result", "content": "KICK depth=3 id=x task=y"}]),
        ])
        self.assertEqual(ta.audit_file(p)["label"], "dispatcher-kick")

    def test_thinking_chars_and_load_tokens(self):
        u = {"input_tokens": 2, "cache_read_input_tokens": 10, "cache_creation_input_tokens": 30, "output_tokens": 4}
        th = {"type": "thinking", "thinking": "x" * 40}
        d, p = self._write([
            _row("user", content="hello"),
            _row("assistant", id="a", usage=u, content=[th]),
            _row("assistant", id="a", usage=u, content=[th]),  # streaming repeat: not double counted
            _row("assistant", id="b", usage=u, content=[]),
        ])
        r = ta.audit_file(p)
        self.assertEqual(r["thinking_chars"], 40)
        self.assertEqual(r["load_tokens"], 42)
        out = ta.render(ta.audit_root(d, 7), 7)
        self.assertIn("load_tokens", out)
        self.assertIn("thinking_chars", out)


if __name__ == "__main__":
    unittest.main()
