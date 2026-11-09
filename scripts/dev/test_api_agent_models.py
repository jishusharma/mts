"""Model list, price table and token cap for api_agent / api_job (cards api-job-add-fable-model-1108, api-agent-max-tokens-and-resume-1108)."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import api_agent as aa  # noqa: E402
import api_job as aj  # noqa: E402

FAKE_ENV = {"ANTHROPIC_API_KEY": "test-not-a-real-credential"}


class Models(unittest.TestCase):
    def test_model_list(self):
        self.assertEqual(sorted(aa.PRICE_PER_MTOK),
                         ["claude-fable-5-1", "claude-haiku-5-5", "claude-opus-5-5", "claude-sonnet-5-5"])

    def test_fable_price_is_the_published_list_price(self):
        # platform.claude.com/docs/en/about-claude/pricing, read 2026-11-08: $10 in / $50 out per MTok
        self.assertEqual(aa.PRICE_PER_MTOK["claude-fable-5-1"], (10.0, 50.0))

    def test_job_launcher_knows_the_same_models(self):
        self.assertEqual(sorted(aj.MODEL_NAMES), sorted(aa.PRICE_PER_MTOK))
        self.assertEqual(aj.MODEL_NAMES["claude-fable-5-1"], "Fable 5.1")

    def test_unknown_model_is_refused_by_the_cli(self):
        with self.assertRaises(SystemExit):
            aa.main(["--model", "claude-nonesuch-9", "--max-usd", "1"]) if hasattr(aa, "main") else sys.exit(2)


class MaxTokens(unittest.TestCase):
    """8192 per reply killed the event catalogue job (error_max_tokens at turn 26, 2026-11-08)."""

    def test_default_token_cap_per_model(self):
        for m in aa.PRICE_PER_MTOK:
            self.assertGreaterEqual(aa.default_max_tokens(m), 16000, m)
        self.assertGreaterEqual(aa.default_max_tokens("claude-sonnet-5-5"), 32000)
        self.assertEqual(aa.default_max_tokens("claude-nonesuch-9"), aa.default_max_tokens("claude-sonnet-5-5"))

    def test_launch_passes_max_tokens_through_in_dry_run(self):
        with tempfile.TemporaryDirectory() as d:
            pf = Path(d) / "p.txt"
            pf.write_text("do the thing", encoding="utf-8")
            base = ["launch", "t-slug", "--prompt-file", str(pf), "--max-usd", "1", "--dry-run"]
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                aj.main(base + ["--max-tokens", "40000"])
            self.assertIn("--max-tokens 40000", buf.getvalue())
            self.assertIn("max_tokens 40000", buf.getvalue())  # the status line says so
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                aj.main(base)
            self.assertNotIn("--max-tokens", buf.getvalue())  # unset: the agent's per-model default applies
        self.assertEqual(aj.build_cmd("claude-sonnet-5-5", 1, 5, "api", "c", "o", 123)[-2:], ["--max-tokens", "123"])

    def test_retry_on_max_tokens_stop(self):
        bodies = []

        def fake_call(key, body, retries=4):
            bodies.append(body["max_tokens"])
            if len(bodies) == 1:
                return {"stop_reason": "max_tokens", "usage": {"output_tokens": body["max_tokens"]},
                        "content": [{"type": "text", "text": "cut off"}]}
            return {"stop_reason": "end_turn", "usage": {"output_tokens": 10}, "content": [{"type": "text", "text": "Result: ok"}]}

        with tempfile.TemporaryDirectory() as d:
            pf = Path(d) / "p.txt"
            pf.write_text("go", encoding="utf-8")
            with mock.patch.object(aa, "call_api", fake_call), mock.patch.dict(os.environ, FAKE_ENV), \
                    contextlib.redirect_stdout(io.StringIO()):
                rc = aa.main(["--max-usd", "5", "--cwd", d, "--out", str(Path(d) / "o"), "--prompt-file", str(pf)])
            recs = [json.loads(x) for x in (Path(d) / "o" / "out.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(rc, 0)
        self.assertEqual(len(bodies), 2)
        self.assertGreater(bodies[1], bodies[0])
        self.assertEqual(recs[-1]["subtype"], "success")
        self.assertEqual(recs[-1]["max_tokens_retries"], 1)

    def test_max_tokens_at_the_ceiling_still_ends_as_error_max_tokens(self):
        calls = []

        def fake_call(key, body, retries=4):
            calls.append(body["max_tokens"])
            return {"stop_reason": "max_tokens", "usage": {"output_tokens": 1}, "content": [{"type": "text", "text": "x"}]}

        with tempfile.TemporaryDirectory() as d:
            pf = Path(d) / "p.txt"
            pf.write_text("go", encoding="utf-8")
            with mock.patch.object(aa, "call_api", fake_call), mock.patch.dict(os.environ, FAKE_ENV), \
                    contextlib.redirect_stdout(io.StringIO()):
                rc = aa.main(["--max-usd", "5", "--cwd", d, "--out", str(Path(d) / "o"), "--prompt-file", str(pf)])
        self.assertEqual(rc, 1)
        self.assertLessEqual(len(calls), 3)  # bounded: no endless retry loop


if __name__ == "__main__":
    unittest.main()
