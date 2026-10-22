"""Hook bench: how long the hooks in .claude/settings.json take, against the budgets of RUN_MODEL.md section 6.

Runs every configured hook N times with a realistic payload, state dirs pointed at a temp folder (nothing real is touched), and prints
the median per hook and the wall time per event. Hooks of one event run in parallel, so the wall time of an event is the slowest
SYNCHRONOUS hook; `async` hooks run in the background and are listed but do not add to it. A tool call = PreToolUse + PostToolUse.
A report tool: exit code 0 always.

  python scripts/dev/hook_bench.py [-n 5] [--settings PATH] [--repo PATH] [--json]
"""
import argparse
import json
import os
import re
import shlex
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUDGETS = {"tool call": 0.5, "prompt": 0.8, "stop": 1.0}          # RUN_MODEL.md section 6, seconds
EVENT_OF = {"PreToolUse": "tool call", "PostToolUse": "tool call", "UserPromptSubmit": "prompt", "Stop": "stop"}
BENCH_EVENTS = ("PreToolUse", "PostToolUse", "UserPromptSubmit", "Stop")     # SessionStart is once per session and sends signals
TOOL = "Bash"


def payload_for(event, cwd, sid="bench-session"):
    p = {"session_id": sid, "cwd": str(cwd), "hook_event_name": event, "transcript_path": ""}
    if event in ("PreToolUse", "PostToolUse"):
        p.update(tool_name=TOOL, tool_input={"command": "git status"}, tool_use_id="toolu_bench")
    if event == "PostToolUse":
        p["tool_response"] = {"stdout": "", "stderr": ""}
    if event == "UserPromptSubmit":
        p["prompt"] = "continue"
    if event == "Stop":
        p["stop_hook_active"] = False
    return p


def argv_for(command, repo):
    """The hook command as an argv: $CLAUDE_PROJECT_DIR expanded, `python` -> this interpreter."""
    parts = shlex.split(command.replace("$CLAUDE_PROJECT_DIR", str(repo).replace("\\", "/")), posix=True)
    if parts and parts[0] in ("python", "python3"):
        parts[0] = sys.executable
    return parts


def hooks_for(settings, event, tool=TOOL):
    """[(name, command, is_async)] of the hooks of `event` whose matcher applies to `tool` (no matcher = all)."""
    out = []
    for group in (settings.get("hooks") or {}).get(event, []):
        m = group.get("matcher")
        if m and m != "*" and not re.fullmatch(m, tool):
            continue
        for h in group.get("hooks", []):
            if h.get("type", "command") != "command":
                continue
            name = re.search(r"([\w.-]+\.py)", h["command"])
            out.append((name.group(1) if name else h["command"][:30], h["command"], bool(h.get("async"))))
    return out


def median(xs):
    return statistics.median(xs) if xs else 0.0


def aggregate(rows):
    """rows: [{event, name, async, median}] -> {"tool call"|"prompt"|"stop": wall seconds}.
    Per event the wall time is the slowest synchronous hook (they run in parallel); a tool call is PreToolUse + PostToolUse."""
    per_event = {}
    for r in rows:
        if r["async"]:
            continue
        per_event[r["event"]] = max(per_event.get(r["event"], 0.0), r["median"])
    walls = {}
    for event, wall in per_event.items():
        key = EVENT_OF.get(event)
        if key:
            walls[key] = walls.get(key, 0.0) + wall
    for key in set(EVENT_OF.values()):
        walls.setdefault(key, 0.0)
    return walls


def verdicts(walls, budgets=BUDGETS):
    return {k: ("OK" if walls.get(k, 0.0) <= b else "OVER") for k, b in budgets.items()}


def isolated_env(tmp, repo):
    tmp = Path(tmp)
    (tmp / "mts-signals-state").mkdir(parents=True, exist_ok=True)
    (tmp / "mts-signals-state" / "last_fetch").write_text("0", newline="\n")      # fresh gate: the steady state, no network or clone
    (tmp / "mts-ci-watch.json").write_text(json.dumps({"at": time.time() + 86400, "runs": []}), newline="\n")   # cache hit
    env = dict(os.environ)
    env.update({
        "CLAUDE_PROJECT_DIR": str(repo),
        "MTS_TURN_METER_HOME": str(tmp / "turn"), "MTS_SHOT_DIR": str(tmp / "shots"), "MTS_SHOT_TEMP": str(tmp / "shottmp"),
        "MTS_CLAUDE_HOME": str(tmp / "claude"), "MTS_CI_WATCH_HOME": str(tmp), "MTS_STOP_GUARD_HOME": str(tmp / "stop"),
        "MTS_SIGNALS_HOME": str(tmp / "mts-signals"), "MTS_SIGNALS_ORIGIN": str(tmp / "no-such-origin"),
        "MTS_ROLES_HOME": str(tmp / "roles"), "MTS_GUARD_TEMP": str(tmp / "gt"),
    })
    return env


def time_hook(argv, payload, env, cwd):
    t0 = time.perf_counter()
    subprocess.run(argv, input=json.dumps(payload), capture_output=True, text=True, env=env, cwd=str(cwd), timeout=60)
    return time.perf_counter() - t0


def clean_tree(tmp):
    """A throwaway clean git tree one commit in, origin/fast-track at HEAD: what the Stop hook sees after a ship (the common stop)."""
    d = Path(tmp) / "clean_tree"
    d.mkdir(exist_ok=True)

    def git(*args):
        subprocess.run(["git", "-C", str(d), "-c", "user.name=bench", "-c", "user.email=bench@example.invalid", *args],
                       capture_output=True, text=True, check=True)
    git("init", "-q")
    (d / "README.md").write_text("bench\n", newline="\n")
    git("add", "README.md")
    git("commit", "-q", "-m", "init")
    git("checkout", "-q", "-b", "bench/work")
    git("update-ref", "refs/remotes/origin/fast-track", "HEAD")
    return d


def bench(settings, repo, n):
    rows = []
    with tempfile.TemporaryDirectory(prefix="hook_bench_") as tmp:
        env = isolated_env(tmp, repo)
        clean = clean_tree(tmp)
        for event in BENCH_EVENTS:
            payload = payload_for(event, clean if event == "Stop" else repo)
            for name, command, is_async in hooks_for(settings, event):
                argv = argv_for(command, repo)
                times = [time_hook(argv, payload, env, repo) for _ in range(n)]   # cwd stays the repo: that is where the scripts are
                rows.append({"event": event, "name": name, "async": is_async, "median": median(times), "times": times})
    return rows


def report(rows, out=print):
    out(f"{'event':18} {'hook':20} {'median s':>9}  mode")
    for r in rows:
        out(f"{r['event']:18} {r['name']:20} {r['median']:9.2f}  {'async (background)' if r['async'] else 'sync'}")
    walls = aggregate(rows)
    res = verdicts(walls)
    out("")
    out(f"{'path':10} {'wall s':>7} {'budget s':>9}")
    for k, b in BUDGETS.items():
        out(f"{k:10} {walls[k]:7.2f} {b:9.1f}  {res[k]}")
    return walls


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("-n", type=int, default=5, help="runs per hook (default 5)")
    p.add_argument("--settings", default=None)
    p.add_argument("--repo", default=None, help="repo root whose scripts/dev hooks run (default: this one)")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    repo = Path(a.repo).resolve() if a.repo else REPO
    settings = json.loads(Path(a.settings or repo / ".claude" / "settings.json").read_text(encoding="utf-8"))
    rows = bench(settings, repo, max(1, a.n))
    if a.json:
        print(json.dumps({"rows": rows, "walls": aggregate(rows)}, indent=1))
    else:
        report(rows)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:      # a report tool never fails the caller
        print(f"hook_bench: {e}", file=sys.stderr)
        sys.exit(0)
