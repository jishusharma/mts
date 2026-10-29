"""Token audit of Claude Code session transcripts (read only).

Sums usage per transcript, labels dispatcher ticks (idle / kick) vs other sessions
by the first user prompt, and reports first-turn input = always-loaded context.
Usage: python scripts/dev/token_audit.py --days 7 [--root DIR] [--out FILE.md]
"""
import argparse
import glob
import json
import os
import sys
import time

FIELDS = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")


def _text(content):
    if isinstance(content, str):
        return content
    out = []
    for b in content or []:
        if isinstance(b, dict):
            t = b.get("text") or b.get("content")
            if isinstance(t, str):
                out.append(t)
            elif isinstance(t, list):
                out.append(_text(t))
    return "\n".join(out)


def audit_file(path):
    """Return dict: label, turns, totals, first_input, tools, started."""
    usage = {}  # message id -> usage (last row wins: streaming repeats)
    order = []
    first_prompt = None
    kick = False
    started = None
    tools = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            msg = d.get("message")
            if not isinstance(msg, dict):
                continue
            if started is None:
                started = d.get("timestamp")
            role = msg.get("role")
            if role == "user":
                txt = _text(msg.get("content"))
                if first_prompt is None and txt and not d.get("isSidechain"):
                    first_prompt = txt
                if "KICK depth=" in txt:
                    kick = True
            elif role == "assistant":
                u = msg.get("usage")
                if isinstance(u, dict):
                    mid = msg.get("id") or d.get("uuid") or str(len(order))
                    if mid not in usage:
                        order.append(mid)
                    usage[mid] = u
                for b in msg.get("content") or []:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        tools += 1
    totals = {f: 0 for f in FIELDS}
    for mid in order:
        for f in FIELDS:
            totals[f] += int(usage[mid].get(f) or 0)
    first = usage[order[0]] if order else {}
    first_input = sum(int(first.get(f) or 0) for f in FIELDS[:3])
    fp = first_prompt or ""
    if "mts-dispatcher" in fp or "MTS dispatcher" in fp:
        label = "dispatcher-kick" if kick else "dispatcher-idle"
    elif "relay" in fp.lower() and "NEXT_SESSION" in fp:
        label = "relay-session"
    else:
        label = "other"
    return {"path": path, "label": label, "turns": len(order), "totals": totals,
            "first_input": first_input, "tools": tools, "started": started}


def audit_root(root, days):
    cutoff = time.time() - days * 86400
    rows = []
    for p in glob.glob(os.path.join(root, "*", "*.jsonl")):
        if os.path.getmtime(p) < cutoff:
            continue
        rows.append(audit_file(p))
    rows.sort(key=lambda r: r["started"] or "")
    return rows


def summarize(rows):
    by = {}
    for r in rows:
        s = by.setdefault(r["label"], {"n": 0, "turns": 0, "first": 0, "read": 0, "write": 0, "inp": 0, "out": 0})
        s["n"] += 1
        s["turns"] += r["turns"]
        s["first"] += r["first_input"]
        s["read"] += r["totals"]["cache_read_input_tokens"]
        s["write"] += r["totals"]["cache_creation_input_tokens"]
        s["inp"] += r["totals"]["input_tokens"]
        s["out"] += r["totals"]["output_tokens"]
    return by


def render(rows, days):
    by = summarize(rows)
    L = [f"# Token audit (last {days} days, this host)", "",
         "Source: ~/.claude/projects/*/*.jsonl usage fields, one row per assistant message id.", "",
         "## By label (means per session)", "",
         "| label | sessions | turns | first-turn input | cache read | cache write | fresh input | output |",
         "|---|---|---|---|---|---|---|---|"]
    for k, s in sorted(by.items()):
        n = s["n"]
        L.append(f"| {k} | {n} | {s['turns']//n} | {s['first']//n} | {s['read']//n} | {s['write']//n} | {s['inp']//n} | {s['out']//n} |")
    L += ["", "## Per session", "",
          "| started | label | turns | tools | first-turn input | cache read | cache write | output |",
          "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        t = r["totals"]
        L.append(f"| {r['started'] or ''} | {r['label']} | {r['turns']} | {r['tools']} | {r['first_input']} | "
                 f"{t['cache_read_input_tokens']} | {t['cache_creation_input_tokens']} | {t['output_tokens']} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    text = render(audit_root(a.root, a.days), a.days)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
