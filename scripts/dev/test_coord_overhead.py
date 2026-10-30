"""Specification checks for coord_overhead's transcript aggregation and CLI."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("coord_overhead.py")


def run_cli(tmp_path, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        cwd=tmp_path, text=True, capture_output=True,
    )


def write_jsonl(path, records):
    path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
    return path


def assistant(usage=None, tools=None):
    return {"type": "assistant", "message": {
        "usage": usage or {},
        "content": [{"type": "tool_use", **t} for t in (tools or [])],
    }}


def test_equivalent_token_formula_exact_limit():
    from coord_overhead import calc_eq_tokens
    assert calc_eq_tokens({"input_tokens": 10, "cache_creation_input_tokens": 4,
                           "cache_read_input_tokens": 20, "output_tokens": 2}) == 27


@pytest.mark.parametrize("inp, expected", [(9, 9.0), (10, 10.0), (11, 11.0)])
def test_one_below_at_and_one_above_formula_value(inp, expected):
    from coord_overhead import calc_eq_tokens
    assert calc_eq_tokens({"input_tokens": inp}) == expected


def test_empty_input_json_is_zero_summary(tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("", encoding="utf-8")
    r = run_cli(tmp_path, "--json", p)
    assert r.returncode == 0
    assert json.loads(r.stdout) == {"total_turns": 0, "counts": {}, "eq_tokens": {},
                                    "coordination_turns": 0, "spawns": 0,
                                    "coord_turns_per_spawn": 0.0}


def test_malformed_json_is_ignored(tmp_path):
    p = tmp_path / "bad.jsonl"
    p.write_text("{broken\n" + json.dumps(assistant({"input_tokens": 3})) + "\n", encoding="utf-8")
    r = run_cli(tmp_path, "--json", p)
    assert r.returncode == 0
    got = json.loads(r.stdout)
    assert got["total_turns"] == 1
    assert got["counts"] == {"text-only replies to the operator": 1}
    assert got["eq_tokens"] == {"text-only replies to the operator": 3.0}


def test_missing_file_is_error(tmp_path):
    r = run_cli(tmp_path, "missing.jsonl")
    assert r.returncode == 1
    assert r.stdout == "error: file not found: missing.jsonl\n"


def test_spawn_and_coordination_ratio(tmp_path):
    p = write_jsonl(tmp_path / "spawn.jsonl", [assistant(tools=[{"name": "Agent"}]), assistant()])
    got = json.loads(run_cli(tmp_path, "--json", p).stdout)
    assert got["total_turns"] == 2
    assert got["coordination_turns"] == 1
    assert got["spawns"] == 1
    assert got["coord_turns_per_spawn"] == 1.0


def test_table_empty_has_safe_denominator_and_all_categories(tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("", encoding="utf-8")
    r = run_cli(tmp_path, p)
    assert r.returncode == 0
    assert r.stdout.count("| 0 | 0.0% | 0 |") == 8
    assert "Total turns: 1, Spawns: 0, Coordination turns per spawn: 0.0" in r.stdout
