"""hook_bench.py: aggregation logic only (no timing asserts)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hook_bench as B


def row(event, name, median, is_async=False):
    return {"event": event, "name": name, "async": is_async, "median": median}


def test_event_wall_is_the_slowest_sync_hook_and_async_hooks_do_not_count():
    rows = [row("PreToolUse", "turn_meter.py", 0.6),
            row("PostToolUse", "turn_meter.py", 0.5, True), row("PostToolUse", "mts_signal.py", 0.9, True),
            row("UserPromptSubmit", "shot.py", 0.4), row("UserPromptSubmit", "role_loader.py", 0.7),
            row("UserPromptSubmit", "ci_watch.py", 2.0, True),
            row("Stop", "stop_guard.py", 1.5)]
    w = B.aggregate(rows)
    assert w == {"tool call": 0.6, "prompt": 0.7, "stop": 1.5}


def test_tool_call_adds_pre_and_post_and_missing_paths_are_zero():
    w = B.aggregate([row("PreToolUse", "a.py", 0.3), row("PostToolUse", "b.py", 0.4), row("PostToolUse", "c.py", 0.2)])
    assert abs(w["tool call"] - 0.7) < 1e-9 and w["prompt"] == 0.0 and w["stop"] == 0.0


def test_verdicts_compare_with_the_budgets():
    v = B.verdicts({"tool call": 0.5, "prompt": 0.81, "stop": 0.0})
    assert v == {"tool call": "OK", "prompt": "OVER", "stop": "OK"}


def test_matcher_selects_hooks_for_the_tool():
    settings = {"hooks": {"PreToolUse": [
        {"matcher": "Agent|Task", "hooks": [{"type": "command", "command": 'python "$CLAUDE_PROJECT_DIR/scripts/dev/model_guard.py" hook'}]},
        {"matcher": "*", "hooks": [{"type": "command", "command": 'python "$CLAUDE_PROJECT_DIR/scripts/dev/turn_meter.py" hook', "async": True}]}]}}
    assert B.hooks_for(settings, "PreToolUse", "Bash") == [("turn_meter.py", 'python "$CLAUDE_PROJECT_DIR/scripts/dev/turn_meter.py" hook', True)]
    assert [h[0] for h in B.hooks_for(settings, "PreToolUse", "Agent")] == ["model_guard.py", "turn_meter.py"]


def test_argv_expands_project_dir_and_python():
    argv = B.argv_for('python "$CLAUDE_PROJECT_DIR/scripts/dev/shot.py" hook', "C:/repo")
    assert argv == [sys.executable, "C:/repo/scripts/dev/shot.py", "hook"]


def test_payloads_carry_event_fields():
    assert B.payload_for("PreToolUse", "x")["tool_name"] == "Bash"
    assert B.payload_for("UserPromptSubmit", "x")["prompt"]
    assert B.payload_for("Stop", "x")["stop_hook_active"] is False


def test_median_of_nothing_is_zero():
    assert B.median([]) == 0.0 and B.median([1.0, 3.0, 2.0]) == 2.0
