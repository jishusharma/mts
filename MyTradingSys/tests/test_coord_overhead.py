import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "dev"))
import coord_overhead as co


class CoordOverheadTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.transcript_file = self.tmp / "sample_transcript.jsonl"

    def _write_records(self, records):
        with open(self.transcript_file, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

    def test_eq_tokens_calculation(self):
        # eq tokens = input 1, cache-write 1.25, cache-read 0.1, output 5
        usage = {
            "input_tokens": 1000,
            "cache_creation_input_tokens": 2000,
            "cache_read_input_tokens": 10000,
            "output_tokens": 100,
        }
        # 1000*1 + 2000*1.25 (2500) + 10000*0.1 (1000) + 100*5 (500) = 5000
        self.assertAlmostEqual(co.calc_eq_tokens(usage), 5000.0)

    def test_classify_turn_categories(self):
        # 1. Text only (no tools)
        self.assertEqual(co.classify_turn([]), "text-only replies to the operator")

        # 2. Spawn
        self.assertEqual(
            co.classify_turn([{"name": "start_session", "input": {"role": "Builder"}}]),
            "spawn (start_session / Agent)",
        )
        self.assertEqual(
            co.classify_turn([{"name": "Agent", "input": {}}]),
            "spawn (start_session / Agent)",
        )

        # 3. Ship + claim/release
        self.assertEqual(
            co.classify_turn([{"name": "Bash", "input": {"command": "python scripts/dev/sync.py ship"}}]),
            "ship + claim/release run by the coordinator itself",
        )
        self.assertEqual(
            co.classify_turn([{"name": "Bash", "input": {"command": "python scripts/dev/sync.py claim foo"}}]),
            "ship + claim/release run by the coordinator itself",
        )

        # 4. Watch loops
        self.assertEqual(
            co.classify_turn([{"name": "Bash", "input": {"command": "sleep 10"}}]),
            "watch loops (sleep, list_sessions, notifications)",
        )
        self.assertEqual(
            co.classify_turn([{"name": "list_sessions", "input": {}}]),
            "watch loops (sleep, list_sessions, notifications)",
        )

        # 5. Bookkeeping
        self.assertEqual(
            co.classify_turn([{"name": "update_plan", "input": {}}]),
            "bookkeeping (update_plan, ToolSearch, wrap_up)",
        )
        self.assertEqual(
            co.classify_turn([{"name": "ToolSearch", "input": {}}]),
            "bookkeeping (update_plan, ToolSearch, wrap_up)",
        )

        # 6. Status re-derivation
        self.assertEqual(
            co.classify_turn([{"name": "Bash", "input": {"command": "python scripts/dev/tasks.py list"}}]),
            "status re-derivation (tasks/desk/codex/STATUS/history reads/fetch)",
        )
        self.assertEqual(
            co.classify_turn([{"name": "Bash", "input": {"command": "git fetch origin fast-track"}}]),
            "status re-derivation (tasks/desk/codex/STATUS/history reads/fetch)",
        )

        # 7. Verify
        self.assertEqual(
            co.classify_turn([{"name": "Bash", "input": {"command": "git cherry origin/fast-track HEAD"}}]),
            "verify (cherry, CI) + steer + cleanup + read + pacing + brief edits",
        )
        self.assertEqual(
            co.classify_turn([{"name": "Bash", "input": {"command": "python scripts/dev/ci_watch.py"}}]),
            "verify (cherry, CI) + steer + cleanup + read + pacing + brief edits",
        )

        # 8. Own work
        self.assertEqual(
            co.classify_turn([{"name": "Edit", "input": {"file": "foo.py"}}]),
            "own work (edits, tests, scripts)",
        )
        self.assertEqual(
            co.classify_turn([{"name": "Bash", "input": {"command": "python -m pytest test_foo.py"}}]),
            "own work (edits, tests, scripts)",
        )

    def test_parse_fixture_transcript(self):
        records = [
            # User turn
            {"type": "user", "message": {"content": "Hello"}},
            # Turn 1: text-only
            {
                "type": "assistant",
                "message": {
                    "id": "m1",
                    "content": [{"type": "text", "text": "Hi"}],
                    "usage": {"input_tokens": 100, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 10},
                },
            },
            # Turn 2: status
            {
                "type": "assistant",
                "message": {
                    "id": "m2",
                    "content": [{"type": "tool_use", "name": "Bash", "input": {"command": "python scripts/dev/tasks.py list"}}],
                    "usage": {"input_tokens": 200, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 20},
                },
            },
            # Turn 3: spawn
            {
                "type": "assistant",
                "message": {
                    "id": "m3",
                    "content": [{"type": "tool_use", "name": "start_session", "input": {"role": "Builder"}}],
                    "usage": {"input_tokens": 300, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 30},
                },
            },
            # Turn 4: own work
            {
                "type": "assistant",
                "message": {
                    "id": "m4",
                    "content": [{"type": "tool_use", "name": "Edit", "input": {"path": "scripts/foo.py"}}],
                    "usage": {"input_tokens": 400, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 40},
                },
            },
        ]
        self._write_records(records)

        summary = co.parse_transcript(self.transcript_file)
        self.assertEqual(summary["total_turns"], 4)
        self.assertEqual(summary["counts"]["text-only replies to the operator"], 1)
        self.assertEqual(summary["counts"]["status re-derivation (tasks/desk/codex/STATUS/history reads/fetch)"], 1)
        self.assertEqual(summary["counts"]["spawn (start_session / Agent)"], 1)
        self.assertEqual(summary["counts"]["own work (edits, tests, scripts)"], 1)
        self.assertEqual(summary["coordination_turns"], 2)  # status + spawn
        self.assertEqual(summary["spawns"], 1)
        self.assertAlmostEqual(summary["coord_turns_per_spawn"], 2.0)

    def test_cli_output(self):
        records = [
            {
                "type": "assistant",
                "message": {
                    "id": "m1",
                    "content": [{"type": "text", "text": "Ok"}],
                    "usage": {"input_tokens": 100, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 10},
                },
            }
        ]
        self._write_records(records)
        rc, out = co.run_cli([str(self.transcript_file)])
        self.assertEqual(rc, 0)
        self.assertIn("text-only replies to the operator", out)


if __name__ == "__main__":
    unittest.main()
