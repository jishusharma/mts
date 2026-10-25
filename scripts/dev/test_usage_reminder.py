import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("usage_reminder.py")


def run(mode, tool):
    p = subprocess.run([sys.executable, str(SCRIPT), mode],
                       input=json.dumps({"tool_name": tool}),
                       capture_output=True, text=True)
    assert p.returncode == 0
    return p.stdout


def test_agent_call_prints_reminder():
    for mode, word in (("pre", "before"), ("post", "after")):
        for tool in ("Agent", "Task", "Workflow"):
            out = run(mode, tool)
            assert out.startswith("USAGE:") and "get_usage" in out and word in out


def test_other_tool_silent():
    assert run("pre", "Bash") == ""
    assert run("post", "Bash") == ""


def test_bad_stdin_never_raises():
    p = subprocess.run([sys.executable, str(SCRIPT), "pre"], input="not json",
                       capture_output=True, text=True)
    assert p.returncode == 0 and p.stdout == ""
