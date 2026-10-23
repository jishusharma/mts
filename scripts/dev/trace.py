#!/usr/bin/env python3
"""trace.py - what did study X lead to? One read-only call, report only (never a gate; T043 was WONTFIX).

    python scripts/dev/trace.py <study_dir | card id | layer id> [--root <repo>]

Prints the chain for a study folder under MyTradingSys/research: task cards that name it (state, lane, claim),
VERDICTS.csv rows, the files in the folder (REPORT / pre-registration first), follow-up cards (depends_on / refs),
last commits touching the folder, LAYERS.md mentions and the open claim. A card id traces every research folder the
card names; a layer id (a layer_index.json family) traces the cards that carry it in their 'layers' field.
Missing links print 'none'. Always exits 0.
"""
import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

NESTED = {"layer_lab"}  # research/<NESTED>/<study>/ is one level deeper
KEY_FILES = ("REPORT", "RESULT", "PRE_REG", "PREREG", "README", "PRE-REG")


def load_cards(root):
    cards = {}
    for p in sorted([*(root / "MyTradingSys/system/tasks").glob("*.json"), *(root / "MyTradingSys/system/tasks").glob("archive/*.json")]):
        try:
            text = p.read_text(encoding="utf-8")
            d = json.loads(text)
        except (OSError, ValueError):
            continue
        d["_text"] = text
        cards[d.get("id", p.stem)] = d
    return cards


def find_folder(root, name):
    """Relative posix path of research folder `name` (basename or path), or None."""
    res = root / "MyTradingSys/research"
    name = name.replace("\\", "/").strip("/")
    name = re.sub(r"^.*MyTradingSys/research/", "", name)
    if not name or not res.is_dir():
        return None
    if (res / name).is_dir():
        return "MyTradingSys/research/" + name
    base = name.split("/")[-1]
    for depth in (1, 2):
        for p in res.glob("/".join(["*"] * depth)):
            if p.is_dir() and p.name == base:
                return p.relative_to(root).as_posix()
    return None


def folders_in_card(root, card):
    found = []
    for m in re.finditer(r"(?:MyTradingSys/)?research/([A-Za-z0-9_.\-]+)(?:/([A-Za-z0-9_.\-]+))?", card["_text"].replace("\\\\", "/")):
        first, second = m.group(1), m.group(2)
        name = first + "/" + second if first in NESTED and second else first
        if "." in first and first not in NESTED and not (root / "MyTradingSys/research" / first).is_dir():
            continue  # a file directly under research/ (VERDICTS.csv, STATUS.md)
        if name not in found:
            found.append(name)
    return found


def card_line(c):
    claim = c.get("claim") or c.get("taken") or "-"
    return "  %s | state=%s | lane=%s | claim=%s | %s" % (c.get("id"), c.get("state"), c.get("lane"),
                                                           str(claim)[:60], str(c.get("title", ""))[:90])


def verdict_rows(root, study):
    p = root / "MyTradingSys/research/VERDICTS.csv"
    if not p.is_file():
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return [r for r in csv.DictReader(f) if r.get("study_dir") == study]


def git_log(root, rel, n=5):
    try:
        out = subprocess.run(["git", "-C", str(root), "log", "-n", str(n), "--format=%h %ad %s", "--date=short", "--", rel],
                             capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    except OSError:
        return []
    return [l for l in out.splitlines() if l.strip()]


def layers_mentions(root, study, ids):
    p = root / "MyTradingSys/system/LAYERS.md"
    if not p.is_file():
        return []
    out, section = [], ""
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        if study in line or any(re.search(r"(^|[^\w-])%s($|[^\w-])" % re.escape(i), line) for i in ids if i):
            out.append("  [%s] %s" % (section, line.strip()[:160]))
    return out


def open_claims(root, study, card_ids):
    d = root / "MyTradingSys/system/claims"
    out = []
    for p in sorted(d.glob("*.md")) if d.is_dir() else []:
        body = p.read_text(encoding="utf-8")
        if (study and study in body) or any(i and (i in p.stem or i in body) for i in card_ids):
            kv = dict(l.split(": ", 1) for l in body.splitlines() if ": " in l)
            out.append("  %s: %s / %s - %s [area: %s]" % (p.stem, kv.get("host", "?"), kv.get("account", "?"),
                                                           kv.get("task", "?"), kv.get("area", "-")))
    return out


def other_mentions(root, study, limit=8):
    """System files (desk queue, handover, docs) that name the study; cards, claims and generated pages excluded."""
    sysd = root / "MyTradingSys/system"
    out = []
    if not sysd.is_dir():
        return out
    for p in sorted(sysd.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if (not p.is_file() or p.suffix not in (".md", ".json", ".csv") or p.stat().st_size > 2_000_000
                or any(x in rel for x in ("/tasks/", "/claims/", "/artifacts/", "LAYERS.md"))):
            continue
        try:
            if study in p.read_text(encoding="utf-8", errors="replace"):
                out.append("  " + rel)
        except OSError:
            continue
    return out[:limit]


def trace_study(root, cards, study_arg):
    rel = find_folder(root, study_arg)
    study = (rel or study_arg).split("/")[-1]
    key = study_arg if rel is None else rel.replace("MyTradingSys/research/", "")
    needles = {study, key}
    primary = [c for c in cards.values() if any(n and n in c["_text"].replace("\\\\", "/") for n in needles)]
    pids = {c["id"] for c in primary}
    follow = {}
    for c in cards.values():
        if c["id"] in pids:
            for r in list(c.get("depends_on") or []) + list(c.get("refs") or []):
                if r in cards and r not in pids:
                    follow[r] = cards[r]
        elif pids & set(c.get("depends_on") or []) or pids & set(c.get("refs") or []):
            follow[c["id"]] = c
    lines = ["== study %s ==" % study, "folder: %s" % (rel or "none (not under MyTradingSys/research)")]
    lines.append("cards: " + ("%d name this folder" % len(primary) if primary else "none"))
    lines += [card_line(c) for c in primary]
    lines.append("follow-up cards (depends_on / refs): " + ("" if follow else "none"))
    lines += [card_line(c) for c in follow.values()]
    rows = verdict_rows(root, study)
    lines.append("verdicts: " + ("%d row(s) in VERDICTS.csv" % len(rows) if rows else "none"))
    for r in rows:
        lines.append("  %s | %s | split=%s n=%s gross=%s se=%s cost=%s | commit=%s %s" % (
            r.get("arm"), r.get("family", "")[:70], r.get("split_read"), r.get("n"), r.get("gross_mean_pct"),
            r.get("se_pct"), r.get("cost_pct"), r.get("commit"), r.get("date")) + " | verdict=" + str(r.get("verdict")))
    files = []
    if rel and (root / rel).is_dir():
        files = sorted([p for p in (root / rel).iterdir() if p.is_file()],
                       key=lambda p: (not any(k in p.name.upper() for k in KEY_FILES), p.name))
    lines.append("files: " + ("%d in %s" % (len(files), rel) if files else "none"))
    lines += ["  " + p.name for p in files[:25]] + (["  ... +%d more" % (len(files) - 25)] if len(files) > 25 else [])
    commits = git_log(root, rel) if rel else []
    lines.append("commits: " + ("" if commits else "none"))
    lines += ["  " + c for c in commits]
    lm = layers_mentions(root, study, [])
    lines.append("LAYERS.md: " + ("" if lm else "none"))
    lines += lm
    om = other_mentions(root, study)
    lines.append("other system mentions (desk queue, handover, docs): " + ("" if om else "none"))
    lines += om
    cl = open_claims(root, study, sorted(pids))
    lines.append("claim: " + ("" if cl else "none"))
    lines += cl
    return lines


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("target", help="study dir name, card id or layer family id")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    a = ap.parse_args(argv)
    root = Path(a.root)
    cards = load_cards(root)
    out = []
    target = a.target.strip()
    layer_ids = set()
    try:
        idx = json.loads((root / "MyTradingSys/system/layer_index.json").read_text(encoding="utf-8"))
        layer_ids = {f.get("id") for f in idx.get("families", [])}
    except (OSError, ValueError):
        pass
    if find_folder(root, target) or verdict_rows(root, target):
        out = trace_study(root, cards, target)
    elif target in cards:
        c = cards[target]
        out = ["== card %s ==" % target, card_line(c)]
        for name in folders_in_card(root, c) or []:
            out += [""] + trace_study(root, cards, name)
        if not folders_in_card(root, c):
            out.append("research folders named by the card: none")
        else:
            out.append("")
        out += ["card links: depends_on=%s refs=%s" % (c.get("depends_on") or "none", c.get("refs") or "none")]
        out += ["claim: " + ("" if open_claims(root, "", [target]) else "none")] + open_claims(root, "", [target])
    elif target in layer_ids or any(target in (c.get("layers") or []) for c in cards.values()):
        mine = [c for c in cards.values() if target in (c.get("layers") or [])]
        out = ["== layer %s ==" % target, "cards: " + ("%d carry this layer" % len(mine) if mine else "none")]
        out += [card_line(c) for c in mine]
        lm = layers_mentions(root, "", [target])
        out += ["LAYERS.md: " + ("" if lm else "none")] + lm[:12]
        seen = []
        for c in mine:
            for f in folders_in_card(root, c):
                if f not in seen and (root / "MyTradingSys/research" / f).is_dir():
                    seen.append(f)
        out.append("research folders named by those cards: " + (", ".join(seen[:20]) if seen else "none"))
    else:
        out = trace_study(root, cards, target)
        out.insert(0, "(%r is not a research folder, card id or layer id; treated as a study name)" % target)
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
