"""scripts/sched/check_live_health.py against a temp root and a fixture process list (no live tree, no popup)."""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "sched" / "check_live_health.py"
NOW = 2_000_000_000.0
FILES = {  # path -> stale limit (s), from the script docstring sources
    "runtime_data/snapshots/BTCUSDT_1.json": 300,
    "MyTradingSys/runtime/state_code.json": 300,
    "MyTradingSys/runtime/orderflow_live/2033-05-18.csv": 300,
    "MyTradingSys/runtime/oi_live/oi_1m.csv": 300,
    "MyTradingSys/research/htf_context/2033-05-18.jsonl": 15000,
}
CMDS = [
    "java -cp x com.mts.statemachine.Main",
    "powershell -File scripts\\core\\loop-supervisor.ps1",
    "python -m MyTradingSys.execution.auto_trader",
    "python -m MyTradingSys.backtest.layers.alerts.live_runner_cli",
    "python -m MyTradingSys.backtest.layers.fabio.orderflow_live --loop",
    "python MyTradingSys\\execution\\daily_loss_monitor.py",
    "python -m MyTradingSys.backtest.layers.fabio.htf_context_live --loop",
]


def make_root(tmp_path, age=10, ages=None):
    for rel, _ in FILES.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x\n", encoding="utf-8")
        a = (ages or {}).get(rel, age)
        os.utime(p, (NOW - a, NOW - a))
    return tmp_path


def procs_file(tmp_path, cmds=CMDS, extra=()):
    rows = [{"pid": 100 + i, "ppid": 1, "cmd": c} for i, c in enumerate(cmds)] + list(extra)
    f = tmp_path / "procs.json"
    f.write_text(json.dumps(rows), encoding="utf-8")
    return f


def check(root, procs):
    p = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--procs-json", str(procs),
                        "--now", str(NOW)], capture_output=True, text=True)
    return p.returncode, p.stdout.splitlines()[0]


def test_all_fresh_and_running_is_ok(tmp_path):
    root = make_root(tmp_path)
    code, line = check(root, procs_file(tmp_path))
    assert code == 0 and line.startswith("live_health OK"), line


def test_each_file_goes_red_just_past_its_limit(tmp_path):
    for rel, limit in FILES.items():
        root = make_root(tmp_path, ages={rel: limit + 5})
        code, line = check(root, procs_file(tmp_path))
        assert code == 2 and "RED" in line, (rel, line)
        root = make_root(tmp_path, ages={rel: limit - 5})
        code, line = check(root, procs_file(tmp_path))
        assert code == 0, (rel, line)


def test_missing_file_is_red(tmp_path):
    root = make_root(tmp_path)
    (root / "MyTradingSys/runtime/oi_live/oi_1m.csv").unlink()
    code, line = check(root, procs_file(tmp_path))
    assert code == 2 and "oi_1m: no file" in line


def test_every_generated_input_absent_is_red_never_ok(tmp_path):
    """oi_live csv and htf_context are untracked (card move-live-host-generated-files): read from the working tree, absent = RED."""
    for rel in ("MyTradingSys/runtime/oi_live/oi_1m.csv", "MyTradingSys/research/htf_context/2033-05-18.jsonl"):
        root = make_root(tmp_path)
        (root / rel).unlink()
        code, line = check(root, procs_file(tmp_path))
        assert code == 2 and ": no file" in line, (rel, line)


def test_untracked_generated_inputs_in_a_git_checkout_read_fine(tmp_path):
    root = make_root(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    (root / ".gitignore").write_text((REPO / ".gitignore").read_text(encoding="utf-8"), encoding="utf-8")
    code, line = check(root, procs_file(tmp_path))
    assert code == 0 and line.startswith("live_health OK"), line


def test_each_dropped_process_is_red(tmp_path):
    root = make_root(tmp_path)
    for i in range(len(CMDS)):
        code, line = check(root, procs_file(tmp_path, CMDS[:i] + CMDS[i + 1:]))
        assert code == 2 and "process not running" in line, (CMDS[i], line)


def test_launcher_shim_and_child_count_once_but_two_copies_warn(tmp_path):
    root = make_root(tmp_path)
    child = {"pid": 900, "ppid": 106, "cmd": CMDS[6]}  # child of the htf process (pid 106)
    code, line = check(root, procs_file(tmp_path, extra=[child]))
    assert code == 0, line
    second = {"pid": 901, "ppid": 1, "cmd": CMDS[6]}
    code, line = check(root, procs_file(tmp_path, extra=[child, second]))
    assert code == 1 and "htf_context_live: 2 copies" in line, line


def test_stop_flag_is_warn_not_red(tmp_path):
    root = make_root(tmp_path, age=99999)
    (root / "runtime_data" / "loop_stop.flag").write_text("", encoding="utf-8")
    code, line = check(root, procs_file(tmp_path, []))
    assert code == 1 and "stopped by flag" in line
