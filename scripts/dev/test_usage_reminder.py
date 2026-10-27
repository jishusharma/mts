import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("usage_reminder.py")


@pytest.fixture
def env(tmp_path):
    e = dict(os.environ)
    e["MTS_USAGE_STATE"] = str(tmp_path / "state.json")
    return e


def run(env, mode, tool="Agent", *extra):
    return subprocess.run([sys.executable, str(SCRIPT), mode, *extra],
                          input=json.dumps({"tool_name": tool}),
                          capture_output=True, text=True, env=env)


def record(env, five, elapsed):
    p = run(env, "record", "Bash", "--five", str(five), "--elapsed", str(elapsed))
    assert p.returncode == 0, p.stderr


def test_agent_call_prints_reminder_when_gate_open(env):
    for tool in ("Agent", "Task", "Workflow"):
        record(env, 20, 30)
        p = run(env, "pre", tool)
        assert p.returncode == 0 and p.stdout.startswith("USAGE:") and "before" in p.stdout
        p = run(env, "post", tool)
        assert p.returncode == 0 and "after" in p.stdout


def test_other_tool_silent(env):
    assert run(env, "pre", "Bash").stdout == "" and run(env, "pre", "Bash").returncode == 0
    assert run(env, "post", "Bash").stdout == ""


def test_bad_stdin_never_raises(env):
    p = subprocess.run([sys.executable, str(SCRIPT), "pre"], input="not json",
                       capture_output=True, text=True, env=env)
    assert p.returncode == 0 and p.stdout == ""


def test_no_reading_refuses(env):
    p = run(env, "pre")
    assert p.returncode == 2 and "no get_usage reading" in p.stderr


def test_stale_reading_refuses(env):
    sp = Path(env["MTS_USAGE_STATE"])
    sp.write_text(json.dumps({"reading": {"five": 10, "elapsed": 50, "ts": 1.0}}))
    p = run(env, "pre")
    assert p.returncode == 2 and "stale" in p.stderr


def test_over_pace_refuses_and_boundary_passes(env):
    record(env, 41, 30)
    p = run(env, "pre")
    assert p.returncode == 2 and "above elapsed" in p.stderr
    record(env, 40, 30)
    assert run(env, "pre").returncode == 0


def test_third_agent_refused_until_one_finishes(env):
    record(env, 10, 30)
    assert run(env, "pre").returncode == 0
    assert run(env, "pre").returncode == 0
    p = run(env, "pre")
    assert p.returncode == 2 and "already run" in p.stderr
    assert run(env, "post").returncode == 0
    assert run(env, "pre").returncode == 0


def test_corrupt_state_fails_closed(env):
    Path(env["MTS_USAGE_STATE"]).write_text("{not json")
    assert run(env, "pre").returncode == 2


def test_gateway_machine_never_refuses_and_registers_nothing(env, tmp_path):
    flag = tmp_path / "flag"
    flag.write_text("on", encoding="utf-8")
    env["MTS_GATEWAY_FLAG"] = str(flag)
    for _ in range(5):
        p = run(env, "pre", "Agent")
        assert p.returncode == 0 and p.stdout == ""
    assert not (tmp_path / "state.json").exists()
    env["MTS_GATEWAY_FLAG"] = str(tmp_path / "absent")
    assert run(env, "pre", "Agent").returncode == 2
