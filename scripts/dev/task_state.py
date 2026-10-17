"""Task-card state tag and LATEST pointers (TASK_REFINEMENT.md "State tag"): a session working a card reads where its newest
ship / report / audit lives instead of searching. Pure helpers on a card dict plus git; tasks.py wires them to commands.

Card fields (both optional, written only by `tasks.py tag|check|done|stale --refresh`):
  latest     list of {kind: ship|report|audit|decision|signal, ref: sha or path, utc, line, auto?}; newest first, max KEEP
  scope_sha  short sha of the newest commit touching the card's scope paths when `latest` was last refreshed
  refreshed  UTC of that refresh
`state_tag` is derived, never trusted from the file: READY | ACTIVE@<who> | SHIPPED@<sha> | STALE:<why> | <STATE>.
"""
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

KINDS = ("ship", "report", "audit", "decision", "signal")
KEEP = 6                   # stored entries per card
SHOW = 3                   # entries the brief prints
GRACE_H = 24               # a ready card may lag a scope change this long before lint fails (the refiner refreshes hourly)
REPORT_DIRS = ("MyTradingSys/research", "MyTradingSys/system")
LINE_MAX = 90


def git(repo, *a):
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout.strip() if r.returncode == 0 else ""


def utc_of(iso):
    """git %cI (any offset) -> UTC 'YYYY-MM-DDTHH:MM:SSZ'."""
    return datetime.fromisoformat(iso).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def scope_paths(card, repo):
    """Existing repo paths named by scope_in (first token of each entry, ':lines' and '(..)' notes dropped)."""
    out = []
    for s in card.get("scope_in", []):
        t = str(s).split()[0].rstrip(",;") if str(s).strip() else ""
        t = re.sub(r":\d[\d,\-]*$", "", t).rstrip("/")
        if t and ("/" in t or "." in t):
            if (Path(repo) / t).exists() and t not in out:
                out.append(t)
    return out


def last_change(repo, paths):
    """(short sha, utc, subject) of the newest commit touching any of paths, or None."""
    if not paths:
        return None
    row = git(repo, "log", "-1", "--format=%H%x09%cI%x09%s", "--", *paths)
    if not row:
        return None
    sha, iso, subj = row.split("\t", 2)
    return sha[:12], utc_of(iso), subj


def newest_doc(card, repo):
    """Newest committed .md whose file name carries the card id or one of its refs (report/audit), as (path, sha, utc, subject)."""
    keys = {str(k).lower() for k in [card.get("id", ""), *card.get("refs", [])] if k}
    best = None
    for d in REPORT_DIRS:
        root = Path(repo) / d
        if not root.is_dir():
            continue
        for p in root.rglob("*.md"):
            n = p.name.lower()
            if any(k in n for k in keys):
                rel = p.relative_to(repo).as_posix()
                lc = last_change(repo, [rel])
                if lc and (best is None or lc[1] > best[2]):
                    best = (rel, lc[0], lc[1], lc[2])
    return best


def auto_latest(card, repo):
    """Entries derivable from git alone: last ship over the scope paths, newest doc naming the card, newest doc inside scope."""
    out = []
    paths = scope_paths(card, repo)
    lc = last_change(repo, paths)
    if lc:
        out.append({"kind": "ship", "ref": lc[0], "utc": lc[1], "line": lc[2][:LINE_MAX], "auto": True})
    nd = newest_doc(card, repo)
    docs = [(p, *last_change(repo, [p])) for p in paths if p.endswith(".md") and last_change(repo, [p])]
    if nd:
        docs.append((nd[0], nd[1], nd[2], nd[3]))
    if docs:
        p, sha, utc, subj = max(docs, key=lambda d: d[2])
        kind = "audit" if "audit" in p.lower() else "report"
        out.append({"kind": kind, "ref": p, "utc": utc, "line": f"{sha} {subj}"[:LINE_MAX], "auto": True})
    return out


def merged_latest(card, repo):
    """Manual entries kept, auto entries recomputed; newest first."""
    keep = [e for e in card.get("latest", []) if not e.get("auto")]
    return sorted(keep + auto_latest(card, repo), key=lambda e: e.get("utc", ""), reverse=True)[:KEEP]


def refresh(card, repo, now_utc):
    """Recompute `latest`, record the scope sha it was computed against. Mutates and returns card."""
    lc = last_change(repo, scope_paths(card, repo))
    card["latest"] = merged_latest(card, repo)
    card["scope_sha"] = lc[0] if lc else ""
    card["refreshed"] = now_utc
    return card


def add_entry(card, kind, ref, utc, line):
    if kind not in KINDS:
        raise ValueError(f"kind {kind!r} not one of {', '.join(KINDS)}")
    card["latest"] = sorted([*card.get("latest", []), {"kind": kind, "ref": ref, "utc": utc, "line": line[:LINE_MAX]}],
                            key=lambda e: e.get("utc", ""), reverse=True)[:KEEP]
    return card


def is_shallow(repo):
    """A depth-limited clone (CI checkout) cannot say when a path last changed: git log then reports HEAD for every path."""
    return git(repo, "rev-parse", "--is-shallow-repository") == "true"


def stale_reason(card, repo):
    """'' when the card's pointers match its scope's newest commit; else why not. Only ready/active cards are judged."""
    if card.get("state") not in ("ready", "active"):
        return ""
    if not card.get("refreshed"):
        return "latest never refreshed (tasks.py tag <id> --refresh)"
    if is_shallow(repo):
        return ""
    lc = last_change(repo, scope_paths(card, repo))
    if lc and lc[0] != card.get("scope_sha"):
        return f"scope changed {lc[0]} {lc[1]} after refresh {card['refreshed']}"
    return ""


def overdue(card, repo, now=None):
    """stale_reason that has outlived GRACE_H (lint fails on this; the shorter lag only shows as STALE in tags and briefs)."""
    why = stale_reason(card, repo)
    if not why or not card.get("refreshed"):
        return why
    if is_shallow(repo):
        return ""
    lc = last_change(repo, scope_paths(card, repo))
    now = now or datetime.now(timezone.utc)
    age = (now - datetime.strptime(lc[1], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)).total_seconds() / 3600
    return why if age > GRACE_H else ""


def state_tag(card, repo, claim=None, reg=None):
    st = card.get("state", "")
    if st == "done":
        sha = git(repo, "log", "-1", "--format=%h", "--", f"MyTradingSys/system/tasks/{card['id']}.json")
        return f"SHIPPED@{sha}" if sha else "SHIPPED"
    if st == "dropped":
        return "DROPPED"
    if st in ("ready", "active"):
        why = stale_reason(card, repo)
        if not why and card.get("refs") and reg and all(reg.get(r) in ("CLOSED", "WONTFIX") for r in card["refs"]):
            why = "all refs closed (tasks.py sweep)"
        if why:
            return f"STALE:{why.split(' (')[0]}"
    if st == "active":
        who = (claim or {}).get("host") or card.get("claim") or "?"
        return f"ACTIVE@{who}"
    return st.upper()


def latest_block(card, repo, tag):
    """Lines for `tasks.py brief`: the tag, the newest SHOW pointers (stored + fresh auto), nothing to search."""
    L = [f"STATE {tag}"]
    for e in merged_latest(card, repo)[:SHOW]:
        L.append(f"LATEST {e['kind']} {e['ref']} {e.get('utc', '')[:10]} {e.get('line', '')}".rstrip())
    return L
