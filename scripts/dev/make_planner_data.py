#!/usr/bin/env python3
"""Regenerate the DATA line of MyTradingSys/system/artifacts/session_planner.html from the task cards.

Usage: python scripts/dev/make_planner_data.py [--worktree] [--ref origin/fast-track] [--html PATH] [--dry]
Default reads cards from origin/fast-track (git); --worktree reads MyTradingSys/system/tasks/*.json on disk.
Keeps states ready/refined/blocked/active/raw. Drops done/dropped but keeps a map id->state for ALL cards.
"""
import argparse, json, re, subprocess, sys, datetime, pathlib

KEEP = ("ready", "refined", "blocked", "active", "raw")
TASK_DIR = "MyTradingSys/system/tasks"
HTML = "MyTradingSys/system/artifacts/session_planner.html"
CLAUDE_LANES_NOTE = "everything that is not CODEX or DSA*"


def git(root, *args, text=True):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if r.returncode:
        raise SystemExit("git %s failed: %s" % (" ".join(args), r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8") if text else r.stdout


def load_cards(root, ref, worktree):
    cards = []
    if worktree:
        for p in sorted((root / TASK_DIR).glob("*.json")):
            cards.append(json.loads(p.read_text(encoding="utf-8")))
        return cards, "worktree"
    names = [n for n in git(root, "ls-tree", "--name-only", ref, TASK_DIR + "/").split("\n") if n.endswith(".json")]
    for n in names:
        cards.append(json.loads(git(root, "show", "%s:%s" % (ref, n))))
    return cards, git(root, "rev-parse", "--short", ref).strip()


def group_of(lane):
    lane = (lane or "").upper()
    if lane == "CODEX":
        return "GPT lab"
    if lane in ("DSA-NB", "DSA-NUC", "DSA"):
        return "DSA"
    return "Claude"


def clip(s, n):
    s = s or ""
    return s if len(s) <= n else s[: n - 1] + "…"


def block_reason(c):
    """Why a blocked card is blocked: the note sentences that say so, else the note head; plus open asks."""
    note = (c.get("note") or "").strip()
    parts = re.split(r"(?<=[.;])\s+", note)
    hits = [x for x in parts if re.search(r"block|wait|paus|fix.first|needs|until|held|hold", x, re.I)]
    why = " ".join(hits) if hits else note
    asks = c.get("asks") or []
    if asks:
        why += " Open asks: " + "; ".join(str(a) for a in asks)
    return clip(why.strip() or "state is blocked (no reason written on the card)", 320)


def build(cards):
    states = {c["id"]: c.get("state", "") for c in cards}
    kept = [c for c in cards if c.get("state") in KEEP]
    open_ids = {c["id"] for c in kept}
    unblocks = {}
    for c in kept:
        for d in c.get("depends_on") or []:
            if states.get(d) != "done":
                unblocks[d] = unblocks.get(d, 0) + 1
    by_id = {c["id"]: c for c in cards}

    def blocked_up(i, seen):
        """Open ancestors of i (excluding i) whose state is blocked."""
        out = []
        for d in by_id.get(i, {}).get("depends_on") or []:
            if d in seen or states.get(d) == "done":
                continue
            seen.add(d)
            if states.get(d) == "blocked":
                out.append(d)
            out += blocked_up(d, seen)
        return out

    tasks = []
    for c in kept:
        deps = [{"id": d, "state": states.get(d, "missing")} for d in (c.get("depends_on") or [])]
        blockers = [d["id"] for d in deps if d["state"] != "done"]
        tasks.append({
            "id": c["id"], "title": c.get("title") or clip(c.get("goal", ""), 90),
            "state": c["state"], "lane": c.get("lane", ""), "group": group_of(c.get("lane")),
            "prio": c.get("prio"), "size": c.get("size", ""),
            "deps": deps, "blockers": blockers,
            "blocked": c["state"] == "blocked",
            "block_reason": block_reason(c) if c["state"] == "blocked" else "",
            "waits_on_blocked": [{"id": d, "reason": block_reason(by_id[d])} for d in blocked_up(c["id"], set())],
            "isolated": not blockers and c["state"] != "blocked",
            "unblocks": unblocks.get(c["id"], 0),
            "goal": clip(c.get("goal"), 900), "done_when": clip(c.get("done_when"), 700),
            "scope_in": [clip(x, 200) for x in (c.get("scope_in") or [])][:10],
            "scope_out": [clip(x, 200) for x in (c.get("scope_out") or [])][:10],
            "note": clip(c.get("note"), 600),
            "layers": c.get("layers") or [], "live_path": bool(c.get("live_path")),
            "kind": c.get("kind", ""), "crucial": bool(c.get("crucial")),
            "model": c.get("model", ""), "effort": c.get("effort", ""),
            "commands": [clip(x, 220) for x in (c.get("commands") or [])][:4],
        })
    tasks.sort(key=lambda t: (t["prio"] if isinstance(t["prio"], int) else 9, t["id"]))
    return tasks, states


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worktree", action="store_true")
    ap.add_argument("--ref", default="origin/fast-track")
    ap.add_argument("--html", default=None)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    root = pathlib.Path(__file__).resolve().parents[2]
    cards, sha = load_cards(root, a.ref, a.worktree)
    tasks, states = build(cards)
    data = {
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "sha": sha, "source": "worktree" if a.worktree else a.ref,
        "total_cards": len(cards),
        "state_counts_all": {s: list(states.values()).count(s) for s in sorted(set(states.values()))},
        "tasks": tasks,
    }
    line = "const DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
    html_path = pathlib.Path(a.html) if a.html else root / HTML
    txt = html_path.read_text(encoding="utf-8")
    lines = txt.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("const DATA = ")]
    if len(idx) != 1:
        raise SystemExit("expected exactly one 'const DATA = ' line, found %d" % len(idx))
    lines[idx[0]] = line
    if not a.dry:
        with open(html_path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines))
    from collections import Counter
    c = Counter((t["group"], t["state"]) for t in tasks)
    print("cards=%d open=%d source=%s sha=%s" % (len(cards), len(tasks), data["source"], sha))
    for g in ("GPT lab", "DSA", "Claude"):
        print("  %-8s %s" % (g, {s: c[(g, s)] for s in KEEP if c[(g, s)]}))
    print("  isolated=%d dependent=%d" % (sum(t["isolated"] for t in tasks), sum(not t["isolated"] for t in tasks)))


if __name__ == "__main__":
    main()
