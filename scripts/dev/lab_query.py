#!/usr/bin/env python3
"""On-demand lab queries for Gemini/Codex/Claude sessions (read-only; never writes, never touches the live tree).

  python scripts/dev/lab_query.py changes   <family> [--n 10]   recent commits on the family's spec/code/ledger/result paths
  python scripts/dev/lab_query.py rulings   <family> [--n 10]   BUGS.md bug rows that name the family (newest first)
  python scripts/dev/lab_query.py backtests <family> [--n 10]   layer_map.json backtests of the family + TRIAL_LEDGER status
  python scripts/dev/lab_query.py layers    [<family>]          every layer: status (layer_map.json) + latest commit on its module
Add `--format md` for markdown (default json). `<family>` is an id from MyTradingSys/system/layer_index.json (tom, fabio, ...).
Sources: layer_index.json, layer_map.json, research/BUGS.md, research/TRIAL_LEDGER.csv, git log. Option `--root` = another checkout.
"""
import argparse
import csv
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

SYS = "MyTradingSys/system/"
FIELDS = ("sha", "date", "subject")


def _json(root, rel):
    return json.loads((root / rel).read_text(encoding="utf-8"))


def _git(root, *args):
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8")
    return p.stdout


def _commits(root, paths, n):
    if not paths:
        return []
    out = _git(root, "log", f"-{n}", "--format=%H\x1f%aI\x1f%s", "--", *paths)
    rows = [line.split("\x1f") for line in out.splitlines() if line.strip()]
    return [dict(zip(FIELDS, r)) for r in rows]


def _family(root, fam):
    for f in _json(root, SYS + "layer_index.json")["families"]:
        if f["id"] == fam:
            return f
    raise SystemExit(f"unknown family '{fam}'; see {SYS}layer_index.json")


def _module_paths(module):
    """layer_map 'module' text -> git pathspecs ('a.py; b/c*.py (note)' -> two globs, anywhere in the tree)."""
    toks = [re.sub(r"\(.*?\)", "", t).strip() for t in (module or "").split(";")]
    return [f":(glob)**/{t}" for t in toks if t and " " not in t]


def _latest_for(root, module):
    best = None
    for spec in _module_paths(module):
        out = _git(root, "log", "-1", "--format=%ct\x1f%H\x1f%aI\x1f%s", "--", spec).strip()
        if not out:
            continue
        ct, sha, date, subj = out.split("\x1f", 3)
        if best is None or int(ct) > best[0]:
            best = (int(ct), {"sha": sha, "date": date, "subject": subj})
    return best[1] if best else None


def q_changes(root, fam, n):
    f = _family(root, fam)
    paths = []
    for k in ("spec", "code", "ledger", "results", "roadmap"):
        paths += f.get(k, [])
    lm = {l["id"]: l for l in _json(root, SYS + "layer_map.json")["layers"]}
    for lid in f.get("layers", []):
        paths += [s for s in _module_paths(lm.get(lid, {}).get("module"))]
    return {"family": fam, "commits": _commits(root, list(dict.fromkeys(paths)), n)}


def q_rulings(root, fam, n):
    _family(root, fam)
    text = (root / "MyTradingSys/research/BUGS.md").read_text(encoding="utf-8")
    word = re.compile(rf"\b{re.escape(fam)}\b", re.I)
    rows = []
    for line in text.splitlines():
        m = re.match(r"\| (B\d+) \| ([^|]*)\| ([^|]*)\| ([^|]*)\| ([^|]*)\|", line)
        if m and word.search(line):
            rows.append({"id": m[1], "opened": m[2].strip(), "status": m[3].strip(),
                         "severity": m[4].strip(), "title": m[5].strip()})
    rows.sort(key=lambda r: int(r["id"][1:]), reverse=True)
    return {"family": fam, "rulings": rows[:n]}


def q_backtests(root, fam, n):
    f = _family(root, fam)
    lm = _json(root, SYS + "layer_map.json")
    mine = set(f.get("layers", []))
    bts = sorted((b for b in lm["backtests"] if mine & set(b.get("layers", []))),
                 key=lambda b: b["date"], reverse=True)
    keep = ("id", "title", "date", "layers", "n", "verdict", "report")
    with open(root / "MyTradingSys/research/TRIAL_LEDGER.csv", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    audit = {"rows": len(rows), "by_status": dict(Counter(r["status"] for r in rows)),
             "latest_run": max((r["run_utc"] for r in rows), default=None),
             "source": "MyTradingSys/research/TRIAL_LEDGER.csv"}
    return {"family": fam, "layer_map_asof": lm.get("asof"),
            "backtests": [{k: b.get(k) for k in keep} for b in bts[:n]], "trial_audit": audit}


def q_layers(root, fam=None):
    fam_of = {l: f["id"] for f in _json(root, SYS + "layer_index.json")["families"] for l in f.get("layers", [])}
    if fam:
        _family(root, fam)
    out = []
    for l in _json(root, SYS + "layer_map.json")["layers"]:
        if fam and fam_of.get(l["id"]) != fam:
            continue
        out.append({"id": l["id"], "family": fam_of.get(l["id"]), "name": l.get("name"), "status": l.get("status"),
                    "module": l.get("module"), "latest_commit": _latest_for(root, l.get("module"))})
    return {"layers": out}


def _c(c):
    return f"{c['sha'][:7]} {c['date'][:10]} {c['subject']}" if c else "none"


def to_md(kind, d):
    L = []
    if kind == "changes":
        L.append(f"## {d['family']}: recent commits")
        L += [f"- {_c(c)}" for c in d["commits"]]
    elif kind == "rulings":
        L.append(f"## {d['family']}: bug rulings (BUGS.md)")
        L += [f"- {r['id']} {r['opened']} {r['status']} {r['severity']}: {r['title']}" for r in d["rulings"]]
    elif kind == "backtests":
        L.append(f"## {d['family']}: backtests (layer_map asof {d['layer_map_asof']})")
        L += [f"- {b['date']} `{b['id']}` n={b['n']}: {b['verdict']} | {b['report']}" for b in d["backtests"]]
        a = d["trial_audit"]
        L.append(f"- trial audit: {a['rows']} rows, by status {a['by_status']}, latest run {a['latest_run']}")
    else:
        L.append("## layers")
        L += [f"- `{x['id']}` ({x['family']}): {x['status']} | last: {_c(x['latest_commit'])}" for x in d["layers"]]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--format", choices=("json", "md"), default="json")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("kind", choices=("changes", "rulings", "backtests", "layers"))
    ap.add_argument("family", nargs="?")
    a = ap.parse_args(argv)
    root = Path(a.root)
    if a.kind != "layers" and not a.family:
        ap.error(f"{a.kind} needs a family id")
    d = {"changes": q_changes, "rulings": q_rulings, "backtests": q_backtests}[a.kind](root, a.family, a.n) \
        if a.kind != "layers" else q_layers(root, a.family)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(to_md(a.kind, d) if a.format == "md" else json.dumps(d, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
