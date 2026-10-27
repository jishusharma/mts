"""PreToolUse/PostToolUse hook: GATE on Agent/Task/Workflow spawns.

pre  refuses (exit 2, reason on stderr) when the last get_usage reading is missing or stale, when MAX_RUNNING agents
     already run, or when 5 h use is above elapsed% + MARGIN. Otherwise it registers the spawn and prints a reminder.
post unregisters the spawn and prints the reminder.
record --five P --elapsed E   stores a get_usage reading (P = 5 h use %, E = % of the 5 h window elapsed).

A hook cannot call MCP, so the agent records the reading after calling get_usage. State file: $MTS_USAGE_STATE or
~/.claude/mts_usage_gate.json (outside the repo). Thresholds are OURS (hygiene card 1, PLAN_5H_2026-10-26b).
Gateway machine (env MTS_GATEWAY=1 or the flag file ~/.claude/mts_gateway_on, env MTS_GATEWAY_FLAG overrides the path):
no meter exists, so pre never refuses and registers nothing (GATEWAY_NUC.md "Unrestricted mode").
Bad stdin or other tools: silent exit 0. Missing/corrupt state counts as stale (fail closed).
Usage: usage_reminder.py pre|post|record  (hook JSON on stdin for pre/post)
"""
import json
import os
import sys
import time

TOOLS = {"Agent", "Task", "Workflow"}
STALE_S = 600       # OURS: reading older than 10 min is stale
MAX_RUNNING = 2     # OURS: a spawn is refused when 2 already run (a 3rd would be "more than 2")
MARGIN = 10.0       # OURS: 5 h use may exceed elapsed% by at most 10 points
RUN_TTL_S = 3600    # OURS: a registered spawn that never reported post expires after 1 h


def gateway_on():
    if os.environ.get("MTS_GATEWAY") == "1":
        return True
    return os.path.exists(os.environ.get("MTS_GATEWAY_FLAG") or os.path.join(os.path.expanduser("~"), ".claude", "mts_gateway_on"))


def state_path():
    return os.environ.get("MTS_USAGE_STATE") or os.path.join(os.path.expanduser("~"), ".claude", "mts_usage_gate.json")


def load():
    try:
        with open(state_path(), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save(d):
    p = state_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f)


def running(d, now):
    return [t for t in d.get("running", []) if isinstance(t, (int, float)) and now - t < RUN_TTL_S]


def check(d, now):
    """Refusal reason or None."""
    r = d.get("reading")
    try:
        five, elapsed, ts = float(r["five"]), float(r["elapsed"]), float(r["ts"])
    except (KeyError, TypeError, ValueError):
        return "no get_usage reading recorded: call get_usage, then usage_reminder.py record --five P --elapsed E"
    if now - ts > STALE_S or ts > now + 60:
        return f"get_usage reading is stale (>{STALE_S // 60} min): call get_usage and record it again"
    n = len(running(d, now))
    if n >= MAX_RUNNING:
        return f"{n} agents already run (max {MAX_RUNNING}): wait for one to finish"
    if five > elapsed + MARGIN:
        return f"5 h use {five:g}% is above elapsed {elapsed:g}% + {MARGIN:g}: pause spawning"
    return None


def main(argv, now=None):
    now = time.time() if now is None else now
    try:
        mode = argv[1] if len(argv) > 1 else "pre"
        if mode == "record":
            a = dict(zip(argv[2::2], argv[3::2]))
            d = load()
            d["reading"] = {"five": float(a["--five"]), "elapsed": float(a["--elapsed"]), "ts": now}
            save(d)
            print("usage reading recorded")
            return 0
        data = json.loads(sys.stdin.read() or "{}")
        if data.get("tool_name") not in TOOLS or gateway_on():
            return 0
        d = load()
        if mode == "post":
            run = sorted(running(d, now))
            if run:
                run.pop(0)
            d["running"] = run
            save(d)
            print("USAGE: call get_usage then usage_log.py after <card>")
            return 0
        reason = check(d, now)
        if reason:
            print(f"USAGE GATE: spawn refused: {reason}", file=sys.stderr)
            return 2
        d["running"] = running(d, now) + [now]
        save(d)
        print("USAGE: call get_usage then usage_log.py before <card>")
    except Exception as e:
        if mode == "record":
            print(f"record failed: {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
