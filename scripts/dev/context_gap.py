"""context_gap.py - how much of its context does a session have to go and find? (CONTEXT_FILES_DESIGN.md sections 2, 5)

  python scripts/dev/context_gap.py measure [--hours N | --since <utc>] [--gate] [--runs FILE] [--projects DIR]

Reads the session jsonl files the app already writes (read-only, nothing uploaded). For every main-thread session with 5+ turns
that started in the window it computes six metrics:
  base           context of the first turn (what the app loads before our files; reported, not gated)
  calls_to_edit  tool calls before the first Edit/Write to a repo path (not handover/, not scratchpad)
  ctx_at_edit    context tokens at that edit
  unnamed_reads  files read before that edit whose name the first user prompt never gave (a "miss")
  stale          tool results that showed a card with STATE SHIPPED or STATE STALE (work dispatched that was already done)
  rewrites       turns whose cache write was > 50% of a 50K+ context (full cache rewrite)
One row per run is appended to MyTradingSys/research/mts_doctor/context_gap_runs.jsonl: numbers and session ids only, never
transcript text, paths, or account data (the repo is public). --gate exits 1 when a metric rose against the previous row.
Derived from context_files/coldstart_baseline.py and health24_baseline.py.
"""
import argparse
import glob
import json
import os
import re
import statistics
import sys
from datetime import datetime, timedelta, timezone

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUNS = os.path.join(REPO, "MyTradingSys", "research", "mts_doctor", "context_gap_runs.jsonl")
PROJECTS = os.path.expanduser("~/.claude/projects")
EDIT = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SKIP_PATH = ("scratchpad", "tool-results", ".claude/projects", "handover/")
READ_CMD = re.compile(r"\b(cat|head|sed -n|type|git show)\b")
STATE_RE = re.compile(r"STATE (?:SHIPPED|STALE)")
MIN_TURNS = 5


def _text(c):
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return " ".join(x.get("text", "") for x in c if isinstance(x, dict) and x.get("type") == "text")
    return ""


def _repo_path(p):
    p = p.replace("\\", "/")
    return bool(p) and not any(s in p for s in SKIP_PATH)


def parse_session(path):
    """Metrics dict for one jsonl file, or None when it is not a main-thread session of 5+ turns."""
    prompt, started = None, None
    turns, calls, reads = 0, 0, []
    edit_ctx, rewrites, stale, first = None, 0, 0, None
    edited = False
    try:
        fh = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return None
    with fh:
        for line in fh:
            try:
                m = json.loads(line)
            except ValueError:
                continue
            if m.get("isSidechain"):
                continue
            started = started or m.get("timestamp")
            t = m.get("type")
            if t == "user":
                c = m.get("message", {}).get("content")
                if prompt is None:
                    prompt = _text(c)
                elif isinstance(c, list):
                    for x in c:
                        if isinstance(x, dict) and x.get("type") == "tool_result":
                            body = x.get("content", "")
                            if STATE_RE.search(_text(body) if isinstance(body, list) else str(body)):
                                stale += 1
                continue
            if t != "assistant":
                continue
            msg = m.get("message", {})
            u = msg.get("usage") or {}
            cr, cw = u.get("cache_read_input_tokens", 0), u.get("cache_creation_input_tokens", 0)
            tot = u.get("input_tokens", 0) + cr + cw
            if tot:
                turns += 1
                first = first or tot
                if turns > 1 and cw > 0.5 * tot and tot > 50000:
                    rewrites += 1
            blocks = msg.get("content") if isinstance(msg.get("content"), list) else []
            for b in blocks:
                if b.get("type") != "tool_use" or edited:
                    continue
                name, inp = b.get("name", "?"), b.get("input") or {}
                arg = str(inp.get("file_path") or inp.get("command") or "")
                if name in EDIT and _repo_path(arg):
                    edited, edit_ctx = True, tot
                    continue
                calls += 1
                if name == "Read" or (name == "Bash" and READ_CMD.search(arg)):
                    reads.append(arg)
    if turns < MIN_TURNS or not prompt:
        return None
    named = {os.path.basename(x) for x in re.findall(r"[\w./\\-]+\.(?:md|py|json|java|tsv|csv|txt|yaml|yml|ps1)", prompt)}
    unnamed = [a for a in reads if _repo_path(a) and not any(b in a for b in named)]
    return {"id": os.path.splitext(os.path.basename(path))[0][:36], "started": started or "", "turns": turns, "base": first or 0,
            "calls_to_edit": calls if edited else None, "ctx_at_edit": edit_ctx, "unnamed_reads": len(unnamed) if edited else None,
            "stale": stale, "rewrites": rewrites}


def _p90(v):
    v = sorted(v)
    return v[min(len(v) - 1, int(0.9 * len(v)))]


def summarize(sessions):
    def col(k):
        return [s[k] for s in sessions if s.get(k) is not None]
    out = {"sessions": len(sessions)}
    for k in ("base", "calls_to_edit", "ctx_at_edit", "unnamed_reads"):
        v = col(k)
        out[k + "_median"] = round(statistics.median(v)) if v else None
        if k in ("calls_to_edit", "unnamed_reads"):
            out[k + "_p90"] = _p90(v) if v else None
    out["stale"] = sum(s["stale"] for s in sessions)
    out["rewrites_per_session"] = round(sum(s["rewrites"] for s in sessions) / len(sessions), 2) if sessions else None
    return out


def collect(since, projects=PROJECTS):
    """Sessions that started at or after `since` (aware datetime)."""
    out = []
    for f in glob.glob(os.path.join(projects, "C--Users-E-ngineers-IdeaProjects-BinanceDataFeed*", "*.jsonl")):
        if os.path.getmtime(f) < since.timestamp():
            continue
        s = parse_session(f)
        if not s:
            continue
        try:
            when = datetime.fromisoformat(s["started"].replace("Z", "+00:00"))
        except ValueError:
            continue
        if when >= since:
            out.append(s)
    return sorted(out, key=lambda s: s["started"])


# compared run over run (a rise is a regression)
GATED = ("calls_to_edit_median", "calls_to_edit_p90", "unnamed_reads_median", "unnamed_reads_p90", "ctx_at_edit_median", "stale",
         "rewrites_per_session")


def regressions(row, prev):
    """Metrics that rose against the previous row ([] when there is none)."""
    bad = []
    for k in GATED:
        a, b = row.get(k), (prev or {}).get(k)
        if a is not None and b is not None and a > b:
            bad.append(f"{k} {b} -> {a}")
    return bad


def rows(path=RUNS):
    try:
        return [json.loads(x) for x in open(path, encoding="utf-8").read().splitlines() if x.strip()]
    except (OSError, ValueError):
        return []


def measure(since, runs=RUNS, projects=PROJECTS, append=True, now=None):
    sessions = collect(since, projects)
    prev = (rows(runs) or [None])[-1]
    row = {"utc": (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ"), "since": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
           **summarize(sessions),
           "per_session": [{k: s[k] for k in ("id", "base", "calls_to_edit", "ctx_at_edit", "unnamed_reads", "stale", "rewrites")} for s in sessions]}
    bad = regressions(row, prev)
    if append:
        os.makedirs(os.path.dirname(runs), exist_ok=True)
        with open(runs, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    return row, bad


def render(row, bad):
    L = [f"context_gap {row['since']} .. {row['utc']}: {row['sessions']} sessions",
         "session                                 base  calls  ctx@edit  unnamed  stale  rewrites"]
    for s in row["per_session"]:
        L.append(f"{s['id']:<36} {s['base']:>8} {str(s['calls_to_edit']):>6} {str(s['ctx_at_edit']):>9} {str(s['unnamed_reads']):>8} {s['stale']:>6} {s['rewrites']:>9}")
    L.append(f"median base {row['base_median']} | calls_to_edit median {row['calls_to_edit_median']} p90 {row['calls_to_edit_p90']} | "
             f"ctx_at_edit median {row['ctx_at_edit_median']} | unnamed_reads median {row['unnamed_reads_median']} p90 {row['unnamed_reads_p90']} | "
             f"stale {row['stale']} | rewrites/session {row['rewrites_per_session']}")
    L.append("GATE: " + ("FAIL: " + "; ".join(bad) if bad else "PASS (no metric rose against the previous row)"))
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="context_gap.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure")
    g = m.add_mutually_exclusive_group()
    g.add_argument("--hours", type=float, default=24)
    g.add_argument("--since", help="UTC start, e.g. 2026-10-25T08:00:00Z")
    m.add_argument("--gate", action="store_true", help="exit 1 when a metric rose against the previous row")
    m.add_argument("--runs", default=RUNS)
    m.add_argument("--projects", default=PROJECTS)
    m.add_argument("--no-append", action="store_true")
    a = ap.parse_args(argv)
    since = datetime.fromisoformat(a.since.replace("Z", "+00:00")) if a.since else datetime.now(timezone.utc) - timedelta(hours=a.hours)
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    row, bad = measure(since, a.runs, a.projects, append=not a.no_append)
    sys.stdout.reconfigure(errors="replace")
    print(render(row, bad))
    return 1 if (a.gate and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
