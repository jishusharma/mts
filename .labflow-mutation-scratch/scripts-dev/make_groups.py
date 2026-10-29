"""Project map: every registry row and every file belongs to one of ten groups, so "which section is this" has one answer.

  python scripts/dev/make_groups.py             # write MyTradingSys/system/PROJECT_MAP.md (generated, do not hand-edit)
  python scripts/dev/make_groups.py --check     # list UNGROUPED rows and files nobody claims; exit 1 if any
  python scripts/dev/make_groups.py --line      # one line per group (STATUS.md uses this)
  python scripts/dev/make_groups.py --of B146   # which group a row belongs to, and why

Definitions live in MyTradingSys/system/groups.json (edit there). Rows come from MyTradingSys/research/BUGS.md.
A row is placed by groups.json "assign" first, then by the group whose keywords match its title + evidence best
(ties go to the earlier group), else UNGROUPED. A file belongs to the group with the longest matching "paths" entry.
Counts are counts of registry rows, not percentages: a closed bug is not a measure of how finished a group is.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
GROUPS = REPO / "MyTradingSys" / "system" / "groups.json"
BUGS = REPO / "MyTradingSys" / "research" / "BUGS.md"
MAP = REPO / "MyTradingSys" / "system" / "PROJECT_MAP.md"
ROW = re.compile(r"^\|\s*([BT]\d{3})\s*\|")
OPEN = ("OPEN", "IN-FIX", "BLOCKED")
SEV_ORDER = {"HIGH": 0, "MED": 1, "LOW": 2, "COSMETIC": 3}


def load_cfg():
    return json.loads(GROUPS.read_text(encoding="utf-8"))


def load_rows():
    rows = []
    for line in BUGS.read_text(encoding="utf-8").splitlines():
        if not ROW.match(line):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) >= 6:
            rows.append({"id": c[0], "opened": c[1], "status": c[2], "sev": c[3], "title": c[4], "evidence": c[5]})
    return rows


def classify(row, cfg):
    """(group code or 'UNGROUPED', reason)."""
    if row["id"] in cfg["assign"]:
        return cfg["assign"][row["id"]], "assigned"
    title, evidence = row["title"].lower(), row["evidence"].lower()
    best, best_score, best_hits = None, 0, []
    for g in cfg["groups"]:
        hits, score = [], 0
        for k in g["keywords"]:
            rx = re.compile(r"(?<![a-z0-9_])" + re.escape(k.lower()) + r"(?![a-z0-9_])")
            t, e = bool(rx.search(title)), bool(rx.search(evidence))
            if t or e:
                hits.append(k)
                score += 3 if t else 1  # the title says what the row is about; the evidence column wanders
        if score > best_score:
            best, best_score, best_hits = g["code"], score, hits
    return (best, "keywords: " + ", ".join(best_hits)) if best else ("UNGROUPED", "no keyword matched")


def owner_of(path, cfg):
    best, best_len = None, -1
    for g in cfg["groups"]:
        for p in g["paths"]:
            if (path == p or (p.endswith("/") and path.startswith(p))) and len(p) > best_len:
                best, best_len = g["code"], len(p)
    return best


def tracked_files():
    r = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, text=True)
    return [f for f in r.stdout.splitlines() if f]


def summarize(cfg, rows):
    by = defaultdict(list)
    for r in rows:
        code, why = classify(r, cfg)
        by[code].append({**r, "group": code, "why": why})
    files = Counter()
    unclaimed = Counter()
    for f in tracked_files():
        o = owner_of(f, cfg)
        if o:
            files[o] += 1
        else:
            unclaimed["/".join(f.split("/")[:2]) if "/" in f else f] += 1
    return by, files, unclaimed


def counts(items):
    c = Counter(r["status"] for r in items)
    open_ = [r for r in items if r["status"] in OPEN]
    return {"open": len(open_), "high": sum(1 for r in open_ if r["sev"] == "HIGH"),
            "closed": c["CLOSED"], "wontfix": c["WONTFIX"], "total": len(items)}


def line(cfg, by, files):
    parts = []
    for g in cfg["groups"]:
        n = counts(by.get(g["code"], []))
        parts.append(f"{g['code']} open {n['open']} (HIGH {n['high']}) closed {n['closed']}")
    ung = len(by.get("UNGROUPED", []))
    return "GROUPS " + " | ".join(parts) + (f" | UNGROUPED {ung}" if ung else "")


DIAGRAM = """```
 SRC   what the traders said ── rules ──►  CORE  Tom engine ── verdicts ──┐
                                             ▲                            ▼
 DATA  feeds and snapshot ── snapshot ───────┤                          EXEC  testnet orders, risk
                                             │                            ▲
 DATA  candles, OI, order flow ──────────►  LAYR  modules ── fires ───────┘
                                             (never gate CORE)

 EVID  replays CORE and LAYR fires on DATA history: do they catch big, profitable moves?
 VIS   charts and screenshots: checks DATA, CORE and LAYR against what the operator sees
 DESK  the operator's window onto all of it     OPS  sessions, workers, process     INFRA  machines, plumbing
```"""


def render(cfg, by, files, unclaimed):
    out = [f"# PROJECT MAP (generated {date.today().isoformat()}, definitions as of {cfg['asof']}; do not hand-edit)",
           "# Source of truth: MyTradingSys/system/groups.json (definitions, path claims, row assignments, focus lines) + MyTradingSys/research/BUGS.md (rows).",
           "# Regenerate: python scripts/dev/make_groups.py. Which group is a row in: python scripts/dev/make_groups.py --of B146.",
           "# Purpose: one answer to \"which section does this belong to\". Counts are registry rows, not percentages; they are not a measure of how finished a group is.",
           "# Counts are frozen at generation time; the live one-line version is the GROUPS line in research/STATUS.md.",
           "", "## How the groups fit", DIAGRAM, "",
           "## Progress at a glance",
           "| Group | What it is | Open (HIGH) | Closed | Won't fix | Files | Live path |",
           "|---|---|---|---|---|---|---|"]
    for g in cfg["groups"]:
        n = counts(by.get(g["code"], []))
        out.append(f"| **{g['code']}** | {g['name']} | {n['open']} ({n['high']}) | {n['closed']} | {n['wontfix']} | {files.get(g['code'], 0)} | {'yes' if g['live_path'] else 'no'} |")
    tot = counts([r for v in by.values() for r in v])
    out += [f"| | all rows | {tot['open']} ({tot['high']}) | {tot['closed']} | {tot['wontfix']} | {sum(files.values())} | |", ""]
    for g in cfg["groups"]:
        items = by.get(g["code"], [])
        out += [f"## {g['code']} - {g['name']}", g["scope"], "",
                f"- Operator's words: \"{g['operator_words']}\"",
                f"- Start reading: {', '.join('`' + f + '`' for f in g['front'])}",
                f"- Who works on it: {g['surface']}",
                f"- Where it lives: {', '.join('`' + p + '`' for p in g['paths'])}",
                f"- Progress is tracked in: {g['tracker']}",
                f"- Focus (hand-written, as of {cfg['asof']}): {g['focus']}", ""]
        open_ = sorted((r for r in items if r["status"] in OPEN), key=lambda r: (SEV_ORDER.get(r["sev"], 9), r["id"]))
        if open_:
            out += ["| Open item | Sev | Status | Title |", "|---|---|---|---|"]
            out += [f"| {r['id']} | {r['sev']} | {r['status']} | {r['title'][:110]} |" for r in open_]
        else:
            out.append("No open registry items.")
        out.append("")
    ung = by.get("UNGROUPED", [])
    out += ["## Checks", f"- UNGROUPED registry rows: {len(ung)}" + (" -> " + ", ".join(r["id"] for r in ung[:20]) if ung else ""),
            f"- Tracked files no group claims: {sum(unclaimed.values())}" + (" -> " + ", ".join(f"{k} ({v})" for k, v in unclaimed.most_common(12)) if unclaimed else ""),
            "- Fix either by adding an \"assign\" entry or a keyword / path in groups.json.", ""]
    return "\n".join(out)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--check", action="store_true")
    p.add_argument("--line", action="store_true")
    p.add_argument("--of", metavar="ID")
    a = p.parse_args(argv)
    cfg, rows = load_cfg(), load_rows()
    if a.of:
        row = next((r for r in rows if r["id"] == a.of.upper()), None)
        if not row:
            print(f"{a.of}: not in BUGS.md", file=sys.stderr)
            return 2
        code, why = classify(row, cfg)
        print(f"{row['id']} -> {code} ({why}) | {row['status']} {row['sev']} | {row['title'][:100]}")
        return 0
    by, files, unclaimed = summarize(cfg, rows)
    if a.line:
        print(line(cfg, by, files))
        return 0
    if a.check:
        ung = by.get("UNGROUPED", [])
        for r in ung:
            print(f"UNGROUPED {r['id']} {r['title'][:90]}")
        for k, v in unclaimed.most_common():
            print(f"UNCLAIMED {k} ({v} files)")
        gone = [(g["code"], f) for g in cfg["groups"] for f in g["front"] if not (REPO / f).exists()]
        for code, f in gone:
            print(f"MISSING-FRONT {code} {f}")
        bad = [k for k in cfg["assign"] if k not in {r["id"] for r in rows}]
        for k in bad:
            print(f"ASSIGN-UNKNOWN-ROW {k}")
        problems = bool(ung or unclaimed or gone or bad)
        print("" if problems else f"OK {len(rows)} rows, 0 ungrouped, 0 unclaimed files, all front pages exist")
        return 1 if problems else 0
    MAP.write_text(render(cfg, by, files, unclaimed), encoding="utf-8", newline="\n")
    print(f"wrote {MAP.relative_to(REPO)}: {len(rows)} rows in {len(cfg['groups'])} groups, {len(by.get('UNGROUPED', []))} ungrouped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
