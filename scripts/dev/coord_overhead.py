"""coord_overhead.py - measures coordinator overhead vs own work from session transcripts.

Source: SUPERVISOR.md 'Measured overhead (before), real data':
eq tokens = input 1, cache-write 1.25, cache-read 0.1, output 5.
"""
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Categories defined in SUPERVISOR.md
CAT_STATUS = "status re-derivation (tasks/desk/codex/STATUS/history reads/fetch)"
CAT_SHIP = "ship + claim/release run by the coordinator itself"
CAT_WATCH = "watch loops (sleep, list_sessions, notifications)"
CAT_BOOKKEEPING = "bookkeeping (update_plan, ToolSearch, wrap_up)"
CAT_SPAWN = "spawn (start_session / Agent)"
CAT_VERIFY = "verify (cherry, CI) + steer + cleanup + read + pacing + brief edits"
CAT_OWN_WORK = "own work (edits, tests, scripts)"
CAT_TEXT_ONLY = "text-only replies to the operator"

COORDINATION_CATS = (CAT_STATUS, CAT_SHIP, CAT_WATCH, CAT_BOOKKEEPING, CAT_SPAWN, CAT_VERIFY)

ALL_CATS = (
    CAT_STATUS,
    CAT_SHIP,
    CAT_WATCH,
    CAT_BOOKKEEPING,
    CAT_SPAWN,
    CAT_VERIFY,
    CAT_OWN_WORK,
    CAT_TEXT_ONLY,
)


def calc_eq_tokens(usage: dict) -> float:
    """Calculate equivalent tokens: input*1.0 + cache_write*1.25 + cache_read*0.1 + output*5.0."""
    inp = float(usage.get("input_tokens") or 0)
    cw = float(usage.get("cache_creation_input_tokens") or 0)
    cr = float(usage.get("cache_read_input_tokens") or 0)
    out = float(usage.get("output_tokens") or 0)
    return inp * 1.0 + cw * 1.25 + cr * 0.1 + out * 5.0


def classify_turn(tools: list) -> str:
    """Classify assistant turn into one of the 8 SUPERVISOR.md overhead categories."""
    if not tools:
        return CAT_TEXT_ONLY

    # Inspect all tools used in this turn
    for t in tools:
        name = t.get("name") or ""
        inp = t.get("input") or {}
        cmd = str(inp.get("command") or "")
        path = str(inp.get("path") or inp.get("file") or inp.get("TargetFile") or "")

        # 1. Spawn
        if name in ("start_session", "Agent"):
            return CAT_SPAWN
        if "start_session" in cmd or "codex_run" in cmd:
            return CAT_SPAWN

        # 2. Bookkeeping
        if name in ("update_plan", "ToolSearch", "wrap_up"):
            return CAT_BOOKKEEPING

        # 3. Watch loops
        if name in ("list_sessions", "wait_pid", "notifications"):
            return CAT_WATCH
        if cmd.startswith("sleep ") or "supervisor.py wait" in cmd or "wait_pid" in cmd:
            return CAT_WATCH

        # 4. Ship + claim/release
        if "sync.py ship" in cmd or "sync.py claim" in cmd or "sync.py release" in cmd:
            return CAT_SHIP

        # 5. Status re-derivation
        if any(p in cmd for p in ("tasks.py list", "tasks.py status", "tasks.py dispatch", "desk.py sweep",
                                  "desk.py list", "STATUS.md", "git fetch", "sync.py where", "sync.py health")):
            return CAT_STATUS
        if any(p in path for p in ("STATUS.md", "tasks/", "claims/")):
            return CAT_STATUS

        # 6. Verify
        if any(p in cmd for p in ("git cherry", "ci_watch", "ci_state", "tasks.py brief", "pacing")):
            return CAT_VERIFY

    # 7. Own work (edits, tests, scripts)
    for t in tools:
        name = t.get("name") or ""
        inp = t.get("input") or {}
        cmd = str(inp.get("command") or "")
        if name in ("Edit", "Write", "replace_file_content", "write_to_file", "Read", "Grep", "FindFiles"):
            return CAT_OWN_WORK
        if any(p in cmd for p in ("pytest", "unittest", "git commit", "git add", "python scripts/")):
            return CAT_OWN_WORK

    # Default to own work if tools were run
    return CAT_OWN_WORK


def parse_transcript(path: Path) -> dict:
    """Parse a single JSONL transcript and return aggregated overhead statistics."""
    path = Path(path)
    counts = Counter()
    eq_tokens = Counter()
    total_turns = 0

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue

            # Check if this record represents an assistant turn
            if rec.get("type") == "assistant" or rec.get("source") == "MODEL" or rec.get("type") == "PLANNER_RESPONSE":
                total_turns += 1
                msg = rec.get("message") or rec
                usage = msg.get("usage") or rec.get("usage") or {}
                eq = calc_eq_tokens(usage)

                # Collect tool calls
                tools = []
                content = msg.get("content") or rec.get("content") or []
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "tool_use":
                            tools.append(item)
                # Also check tool_calls top-level
                for tc in rec.get("tool_calls") or []:
                    if isinstance(tc, dict):
                        tools.append(tc)

                cat = classify_turn(tools)
                counts[cat] += 1
                eq_tokens[cat] += eq

    coord_turns = sum(counts[c] for c in COORDINATION_CATS)
    spawns = counts[CAT_SPAWN]
    coord_per_spawn = (coord_turns / spawns) if spawns > 0 else float(coord_turns)

    return {
        "file": str(path),
        "total_turns": total_turns,
        "counts": dict(counts),
        "eq_tokens": dict(eq_tokens),
        "coordination_turns": coord_turns,
        "spawns": spawns,
        "coord_turns_per_spawn": coord_per_spawn,
    }


def format_table(summary: dict) -> str:
    """Render summary table in SUPERVISOR.md format."""
    total = max(1, summary.get("total_turns", 0))
    counts = summary.get("counts", {})
    eq = summary.get("eq_tokens", {})
    total_eq = sum(eq.values())

    lines = [
        "| Category | Turns | Share | eq tokens |",
        "|---|---|---|---|",
    ]
    for cat in ALL_CATS:
        c = counts.get(cat, 0)
        e = eq.get(cat, 0.0)
        share = (c / total) * 100.0
        lines.append(f"| {cat} | {c} | {share:.1f}% | {e:,.0f} |")

    coord_turns = summary.get("coordination_turns", 0)
    coord_share = (coord_turns / total) * 100.0
    coord_eq = sum(eq.get(c, 0.0) for c in COORDINATION_CATS)
    lines.append(f"| **coordination total** | **{coord_turns}** | **{coord_share:.1f}%** | **{coord_eq:,.0f}** |")

    lines.append("")
    spawns = summary.get("spawns", 0)
    cps = summary.get("coord_turns_per_spawn", 0.0)
    lines.append(f"Total turns: {total}, Spawns: {spawns}, Coordination turns per spawn: {cps:.1f}")
    return "\n".join(lines)


def run_cli(argv: list) -> tuple[int, str]:
    """Execute CLI and return (exit_code, output_str)."""
    if not argv or "-h" in argv or "--help" in argv:
        out = "usage: coord_overhead.py [--json] <transcript.jsonl ...>\n"
        return 0, out

    as_json = "--json" in argv
    files = [Path(a) for a in argv if a != "--json"]

    combined_counts = Counter()
    combined_eq = Counter()
    total_turns = 0
    spawns = 0

    for f in files:
        if not f.exists():
            return 1, f"error: file not found: {f}\n"
        s = parse_transcript(f)
        total_turns += s["total_turns"]
        spawns += s["spawns"]
        for k, v in s["counts"].items():
            combined_counts[k] += v
        for k, v in s["eq_tokens"].items():
            combined_eq[k] += v

    coord_turns = sum(combined_counts[c] for c in COORDINATION_CATS)
    summary = {
        "total_turns": total_turns,
        "counts": dict(combined_counts),
        "eq_tokens": dict(combined_eq),
        "coordination_turns": coord_turns,
        "spawns": spawns,
        "coord_turns_per_spawn": (coord_turns / spawns) if spawns > 0 else float(coord_turns),
    }

    if as_json:
        return 0, json.dumps(summary, indent=2) + "\n"
    return 0, format_table(summary) + "\n"


def main():
    rc, out = run_cli(sys.argv[1:])
    sys.stdout.write(out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
