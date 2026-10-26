import json
import os
import subprocess
import sys
import time
from pathlib import Path

SCRIPT = Path(__file__).with_name("usage_reminder.py")


def run(mode, tool, d, gate=None, stdin=None, extra=()):
    env = dict(os.environ, MTS_USAGE_DIR=str(d))
    env.pop("MTS_USAGE_GATE", None)
    if gate:
        env["MTS_USAGE_GATE"] = gate
    return subprocess.run([sys.executable, str(SCRIPT), mode, *extra],
                          input=json.dumps({"tool_name": tool}) if stdin is None else stdin,
                          capture_output=True, text=True, env=env)


def reading(d, five, el, age=0):
    (d / "usage_reading.json").write_text(
        json.dumps({"ts": time.time() - age, "five": five, "elapsed": el}))


def test_post_prints_reminder(tmp_path):
    for tool in ("Agent", "Task", "Workflow"):
        p = run("post", tool, tmp_path)
        assert p.returncode == 0 and p.stdout.startswith("USAGE:") and "after" in p.stdout


def test_other_tool_silent(tmp_path):
    for mode in ("pre", "post"):
        p = run(mode, "Bash", tmp_path)
        assert p.returncode == 0 and p.stdout == ""


def test_bad_stdin_never_raises(tmp_path):
    p = run("pre", "Agent", tmp_path, stdin="not json")
    assert p.returncode == 0 and p.stdout == ""


def test_blocks_without_reading(tmp_path):
    p = run("pre", "Agent", tmp_path)
    assert p.returncode == 2 and "usage_reminder.py record" in p.stderr


def test_blocks_stale_reading(tmp_path):
    reading(tmp_path, 10, 10, age=700)
    p = run("pre", "Workflow", tmp_path)
    assert p.returncode == 2 and "old" in p.stderr


def test_blocks_overspend(tmp_path):
    reading(tmp_path, 40, 29)
    assert run("pre", "Agent", tmp_path).returncode == 2
    reading(tmp_path, 39, 29)
    assert run("pre", "Agent", tmp_path).returncode == 0


def test_blocks_more_than_two_running(tmp_path):
    reading(tmp_path, 10, 10)
    for _ in range(3):
        assert run("pre", "Agent", tmp_path).returncode == 0
    assert run("pre", "Agent", tmp_path).returncode == 2
    run("post", "Agent", tmp_path)
    assert run("pre", "Agent", tmp_path).returncode == 0


def test_stale_spawns_expire(tmp_path):
    reading(tmp_path, 10, 10)
    old = time.time() - 4000
    (tmp_path / "agent_spawns.json").write_text(json.dumps({"running": [old] * 5}))
    assert run("pre", "Agent", tmp_path).returncode == 0


def test_env_bypass(tmp_path):
    assert run("pre", "Agent", tmp_path, gate="off").returncode == 0


def test_record_writes_reading(tmp_path):
    p = run("record", "Agent", tmp_path, extra=("--five", "12", "--elapsed", "20"))
    assert p.returncode == 0
    r = json.loads((tmp_path / "usage_reading.json").read_text())
    assert r["five"] == 12 and r["elapsed"] == 20
    assert run("pre", "Agent", tmp_path).returncode == 0


def test_internal_error_exits_zero(tmp_path):
    (tmp_path / "usage_reading.json").write_text(
        json.dumps({"ts": time.time(), "five": "x", "elapsed": 1}))
    assert run("pre", "Agent", tmp_path).returncode == 0
