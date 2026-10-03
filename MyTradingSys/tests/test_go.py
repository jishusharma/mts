"""Fixtures for scripts/sched/go.py (the body of `mts go`): B086 one-writer guard, B087c session naming, B088 surface code.
A fake claude executable records its argv, so no live writer is ever started by these tests."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "sched" / "go.py"
PROMPT = "Session ID: MTS-2026-10-03-1000Z-CLI-BLD-b070-demo\nTASK: B070\n"
LEGACY = "Session ID: MTS-2026-10-03-1000Z-CL-BLD-b070-demo\nTASK: B070\n"


def setup(tmp_path, prompt=PROMPT):
    sid = prompt.splitlines()[0].split(": ", 1)[1] if prompt.startswith("Session ID: ") else None
    q = tmp_path / "MyTradingSys" / "runtime" / "queue"
    q.mkdir(parents=True)
    (q / "next_task.txt").write_text(prompt, encoding="utf-8", newline="\n")
    (q / "next_task.json").write_text(json.dumps({"id": "B070", "session_id": sid}),
                                      encoding="utf-8")
    fake = tmp_path / "fake_claude.py"
    fake.write_text("import json, sys\nopen(sys.argv[0] + '.argv', 'w').write(json.dumps(sys.argv[1:]))\n",
                    encoding="utf-8", newline="\n")
    wrapper = tmp_path / ("fake_claude.cmd" if os.name == "nt" else "fake_claude.sh")
    if os.name == "nt":
        wrapper.write_text('@echo off\r\n"%s" "%s" %%*\r\n' % (sys.executable, fake), encoding="utf-8", newline="")
    else:
        wrapper.write_text('#!/bin/sh\nexec "%s" "%s" "$@"\n' % (sys.executable, fake), encoding="utf-8", newline="\n")
        wrapper.chmod(0o755)
    return wrapper, Path(str(fake) + ".argv")


def go(tmp_path, wrapper, args=(), claudecode=False):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    env.update(MTS_PICK_ROOT=str(tmp_path), MTS_CLAUDE_BIN=str(wrapper))
    if claudecode:
        env["CLAUDECODE"] = "1"
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env, cwd=REPO)


def test_1_inside_claude_code_is_dry_no_launch(tmp_path):
    wrapper, argv = setup(tmp_path)
    p = go(tmp_path, wrapper, claudecode=True)
    assert p.returncode == 0, p.stderr
    assert "DRY RUN" in p.stdout and "TASK: B070" in p.stdout
    assert not argv.exists(), "a live claude was launched from inside a Claude Code session"


def test_2_operator_terminal_launches_live(tmp_path):
    wrapper, argv = setup(tmp_path)
    p = go(tmp_path, wrapper)
    assert p.returncode == 0, p.stderr
    got = json.loads(argv.read_text(encoding="utf-8"))
    assert got[0] == "--name" and got[1] == "MTS-2026-10-03-1000Z-CLI-BLD-b070-demo"
    assert got[2].startswith("Session ID: MTS-2026-10-03-1000Z")  # cmd.exe wrapper keeps line 1 of the prompt only


def test_3_dry_flag_forces_no_launch(tmp_path):
    wrapper, argv = setup(tmp_path)
    p = go(tmp_path, wrapper, ["--dry"])
    assert "DRY RUN" in p.stdout and not argv.exists()


def test_4_slug_derives_policy_session_id_and_rewrites_prompt(tmp_path):
    wrapper, argv = setup(tmp_path)
    p = go(tmp_path, wrapper, ["fix-dispatcher"])
    assert p.returncode == 0, p.stderr
    got = json.loads(argv.read_text(encoding="utf-8"))
    assert re.fullmatch(r"MTS-\d{4}-\d{2}-\d{2}-\d{4}Z-CLI-BLD-fix-dispatcher", got[1]), got[1]
    assert got[2].startswith("Session ID: " + got[1])


def test_5_bad_slug_rejected_nothing_launched(tmp_path):
    wrapper, argv = setup(tmp_path)
    for bad in ("Fix_Dispatcher", "a" * 21, "-x", "x--y"):
        p = go(tmp_path, wrapper, [bad])
        assert p.returncode == 2, bad
    assert not argv.exists()


def test_6_idle_queue_prints_idle(tmp_path):
    wrapper, argv = setup(tmp_path, "IDLE no pickable row\n")
    p = go(tmp_path, wrapper)
    assert p.returncode == 0 and "IDLE" in p.stdout and not argv.exists()


def test_7_mts_go_verb_delegates_to_go_py():
    text = (REPO / "mts.ps1").read_text(encoding="utf-8")
    body = text[text.index('    "go" {'):text.index('    "guide" {')]
    assert "go.py" in body and "& claude" not in body
    assert "[switch]$Dry" in text


# ---- B088: one surface code (CLI, SURFACE_POLICY section 4) ----

def test_8_inherited_legacy_cl_name_launches_as_cli(tmp_path):
    # next_task.* composed before B088 carries -CL-; the launch name and the prompt line are normalised to -CLI-
    wrapper, argv = setup(tmp_path, LEGACY)
    p = go(tmp_path, wrapper)
    assert p.returncode == 0, p.stderr
    got = json.loads(argv.read_text(encoding="utf-8"))
    assert got[1] == "MTS-2026-10-03-1000Z-CLI-BLD-b070-demo", got[1]
    assert got[2] == "Session ID: " + got[1]


def test_9_go_and_pick_share_the_policy_surface_code(tmp_path):
    wrapper, _ = setup(tmp_path)
    p = go(tmp_path, wrapper, ["demo-slug", "--dry"])
    code = re.search(r"session name: MTS-\d{4}-\d{2}-\d{2}-\d{4}Z-([A-Z]+)-BLD-demo-slug", p.stdout).group(1)
    policy = (REPO / "MyTradingSys" / "system" / "SURFACE_POLICY.md").read_text(encoding="utf-8")
    assert code in re.search(r"(?m)^SURF: ([A-Z ]+)\.", policy).group(1).split()
    sys.path.insert(0, str(SCRIPT.parent))
    import pick_task
    assert pick_task.SURF == code
