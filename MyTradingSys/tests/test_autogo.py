"""Fixtures for scripts/sched/autogo.py (B094): enable gate, each auto-disable condition, launch + skips, tick wiring.
go.py is never really run: a stub go.py in a tmp repo records its argv; canary is a stub command."""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "sched" / "autogo.py"
NOW = "2026-10-05T04:00:00Z"
PYX = sys.executable.replace("\\", "/")
OK_CANARY = PYX + ' -c "import sys; sys.exit(0)"'
RED_CANARY = PYX + ' -c "import sys; sys.exit(2)"'


def setup(tmp, rows=(("B074", "2026-10-05T03:00:00Z"),)):
    d = tmp / "MyTradingSys" / "runtime" / "queue" / "slots"
    d.mkdir(parents=True)
    (tmp / "MyTradingSys" / "execution").mkdir(parents=True)
    for rid, comp in rows:
        (d / (rid + ".txt")).write_text("Session ID: x\nTASK: %s\n" % rid, encoding="utf-8", newline="\n")
        (d / (rid + ".json")).write_text(json.dumps({"id": rid, "composed_utc": comp}), encoding="utf-8")
    return tmp


def env_for(tmp, canary=OK_CANARY, extra=None):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    env.update(MTS_PICK_ROOT=str(tmp), MTS_AUTOGO_CANARY=canary, MTS_AUTOGO_NOW=NOW)
    env.update(extra or {})
    return env


def run(tmp, *args, canary=OK_CANARY, extra=None, script=SCRIPT):
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True,
                          env=env_for(tmp, canary, extra), cwd=REPO)


def sched(tmp):
    return tmp / "MyTradingSys" / "runtime" / "sched"


def enable(tmp, script=SCRIPT):
    return run(tmp, "--enable", "--words", "enable it", script=script)


def events(tmp):
    p = sched(tmp) / "autogo_log.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def test_1_disabled_without_flag_launches_nothing(tmp_path):
    setup(tmp_path)
    r = run(tmp_path, "--tick")
    assert r.returncode == 0 and "autogo OK disabled" in r.stdout
    assert not (sched(tmp_path) / "autogo_state.json").exists()


def test_2_enable_needs_operator_words_and_logs_them(tmp_path):
    setup(tmp_path)
    assert run(tmp_path, "--enable").returncode == 2
    assert not (sched(tmp_path) / "autogo_enabled").exists()
    assert enable(tmp_path).returncode == 0
    assert (sched(tmp_path) / "autogo_enabled").exists()
    assert events(tmp_path)[-1]["event"] == "enable" and events(tmp_path)[-1]["words"] == "enable it"


def _disabled_with(tmp, reason_re, **kw):
    r = run(tmp, "--tick", **kw)
    assert r.returncode == 1 and re.search(reason_re, r.stdout), r.stdout + r.stderr
    assert not (sched(tmp) / "autogo_enabled").exists()
    assert events(tmp)[-1]["event"] == "auto_disable" and re.search(reason_re, events(tmp)[-1]["reason"])


def test_3_brake_file_auto_disables(tmp_path):
    setup(tmp_path)
    enable(tmp_path)
    (tmp_path / "MyTradingSys" / "execution" / "AUTO_PAUSE").write_text("", encoding="utf-8")
    _disabled_with(tmp_path, "brake file present: AUTO_PAUSE")


def test_4_canary_red_auto_disables(tmp_path):
    setup(tmp_path)
    enable(tmp_path)
    _disabled_with(tmp_path, "canary RED", canary=RED_CANARY)


def test_5_no_pickable_slot_auto_disables(tmp_path):
    setup(tmp_path, rows=())
    enable(tmp_path)
    _disabled_with(tmp_path, "no pickable slot")


def test_6_stale_unlaunched_slots_auto_disable(tmp_path):
    setup(tmp_path, rows=(("B074", "2026-10-03T03:00:00Z"),))
    enable(tmp_path)
    _disabled_with(tmp_path, "held over 24h")


def stub_tree(tmp):
    """autogo resolves go.py next to itself: copy autogo + _common beside a stub go.py that records argv."""
    d = tmp / "scripts" / "sched"
    d.mkdir(parents=True)
    for n in ("autogo.py", "_common.py"):
        (d / n).write_text((REPO / "scripts" / "sched" / n).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    (d / "go.py").write_text("import json, sys, pathlib\n"
                             "pathlib.Path(__file__).with_name('go.argv').write_text(json.dumps(sys.argv[1:]))\n",
                             encoding="utf-8", newline="\n")
    return d / "autogo.py"


def test_7_enabled_launches_first_slot_headless_once(tmp_path):
    setup(tmp_path)
    script = stub_tree(tmp_path)
    assert enable(tmp_path, script).returncode == 0
    r = run(tmp_path, "--tick", script=script)
    assert r.returncode == 0 and "launched B074" in r.stdout, r.stdout + r.stderr
    argv = script.with_name("go.argv")
    for _ in range(50):
        if argv.exists():
            break
        time.sleep(0.1)
    assert json.loads(argv.read_text()) == ["--id", "B074", "--headless"]
    r2 = run(tmp_path, "--tick", script=script)
    assert r2.returncode == 0 and "already launched" in r2.stdout


def test_8_inside_claude_code_skips_launch(tmp_path):
    setup(tmp_path)
    enable(tmp_path)
    r = run(tmp_path, "--tick", extra={"CLAUDECODE": "1"})
    assert r.returncode == 0 and "skip: inside Claude Code" in r.stdout
    assert (sched(tmp_path) / "autogo_enabled").exists()


def test_9_tick_runs_autogo_check():
    src = (REPO / "scripts" / "sched" / "tick.py").read_text(encoding="utf-8")
    assert '("autogo", [PY, "scripts/sched/autogo.py", "--tick"], "event")' in src
