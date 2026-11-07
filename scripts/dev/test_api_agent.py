"""api_agent.py: tool sandbox, cost arithmetic and the loop (fake API). Fails on the pre-change tree (no module)."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import api_agent  # noqa: E402


class ToolsAndCost(unittest.TestCase):
    def test_usd_list_price(self):
        # Sonnet: 1M input at 3 + 1M output at 15 = 18 USD; cache reads at a tenth
        self.assertAlmostEqual(api_agent.usd("claude-sonnet-5-5", {"input_tokens": 1_000_000, "output_tokens": 1_000_000}), 18.0)
        self.assertAlmostEqual(api_agent.usd("claude-haiku-5-5", {"cache_read_input_tokens": 1_000_000}), 0.1)

    def test_secret_paths_refused(self):
        for bad in ("F:/ClaudePlaform/key.txt", ".secrets/x", "a\\.env", "F:/AIBridge/src/config.json"):
            self.assertTrue(api_agent.blocked(bad), bad)
        self.assertFalse(api_agent.blocked("MyTradingSys/research/x.md"))

    def test_tools_in_cwd(self):
        with tempfile.TemporaryDirectory() as d:
            cwd = Path(d)
            self.assertIn("wrote", api_agent.run_tool("write_file", {"path": "a/b.txt", "content": "hi\n"}, cwd))
            self.assertEqual(api_agent.run_tool("read_file", {"path": "a/b.txt"}, cwd), "hi\n")
            self.assertIn("a/", api_agent.run_tool("list_dir", {"path": "."}, cwd))
            out = api_agent.run_tool("run_cmd", {"cmd": f'"{sys.executable}" -c "print(7)"'}, cwd)
            self.assertIn("rc=0", out)
            self.assertIn("7", out)
            self.assertTrue(api_agent.run_tool("read_file", {"path": "key.txt"}, cwd).startswith("REFUSED"))


class Loop(unittest.TestCase):
    def test_tool_turn_then_answer(self):
        calls = []

        def fake(key, body, retries=4):
            calls.append(body)
            if len(calls) == 1:
                return {"stop_reason": "tool_use", "usage": {"input_tokens": 100, "output_tokens": 10},
                        "content": [{"type": "tool_use", "id": "t1", "name": "write_file", "input": {"path": "x.txt", "content": "ok"}}]}
            return {"stop_reason": "end_turn", "usage": {"input_tokens": 100, "output_tokens": 10},
                    "content": [{"type": "text", "text": "Result: done"}]}

        with tempfile.TemporaryDirectory() as d:
            prompt = Path(d) / "p.txt"
            prompt.write_text("do it", encoding="utf-8")
            old = api_agent.call_api
            api_agent.call_api = fake
            os.environ["ANTHROPIC_API_KEY"] = "test-key-not-real"
            try:
                rc = api_agent.main(["--model", "claude-haiku-5-5", "--max-usd", "1", "--cwd", d, "--out", d, "--prompt-file", str(prompt)])
            finally:
                api_agent.call_api = old
                os.environ.pop("ANTHROPIC_API_KEY", None)
            self.assertEqual(rc, 0)
            self.assertEqual((Path(d) / "x.txt").read_text(encoding="utf-8"), "ok")
            recs = [json.loads(l) for l in (Path(d) / "out.jsonl").read_text(encoding="utf-8").splitlines()]
            res = [r for r in recs if r["type"] == "result"][0]
            self.assertEqual(res["num_turns"], 2)
            self.assertEqual(res["subtype"], "success")
            self.assertAlmostEqual(res["total_cost_usd"], 2 * (100 * 1.0 + 10 * 5.0) / 1e6, places=6)
            # one cache breakpoint in messages per request, never more
            for body in calls:
                marks = sum(1 for m in body["messages"] if isinstance(m["content"], list) for b in m["content"] if "cache_control" in b)
                self.assertEqual(marks, 1)
            # the claude-code beta is never sent: the credit refuses it
            self.assertNotIn("anthropic-beta", json.dumps(calls))

    def test_usd_cap_stops(self):
        def fake(key, body, retries=4):
            return {"stop_reason": "tool_use", "usage": {"input_tokens": 1_000_000, "output_tokens": 0},
                    "content": [{"type": "tool_use", "id": "t", "name": "list_dir", "input": {"path": "."}}]}

        with tempfile.TemporaryDirectory() as d:
            prompt = Path(d) / "p.txt"
            prompt.write_text("loop", encoding="utf-8")
            old = api_agent.call_api
            api_agent.call_api = fake
            os.environ["ANTHROPIC_API_KEY"] = "test-key-not-real"
            try:
                rc = api_agent.main(["--model", "claude-haiku-5-5", "--max-usd", "1.5", "--cwd", d, "--out", d, "--prompt-file", str(prompt)])
            finally:
                api_agent.call_api = old
                os.environ.pop("ANTHROPIC_API_KEY", None)
            self.assertEqual(rc, 1)
            recs = [json.loads(l) for l in (Path(d) / "out.jsonl").read_text(encoding="utf-8").splitlines()]
            res = [r for r in recs if r["type"] == "result"][0]
            self.assertEqual(res["subtype"], "error_max_budget_usd")
            self.assertEqual(res["num_turns"], 2)  # 1 USD per turn: the second turn crosses 1.5


if __name__ == "__main__":
    unittest.main()
