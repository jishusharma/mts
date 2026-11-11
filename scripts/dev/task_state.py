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
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, encoding="utf-8", errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
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


_LC_LOG = {}   # repo -> [(sha, iso, subj, files)] newest first, filled by prefetch_changes (one git call for a whole list)


def prefetch_changes(repo, n=5000):
    """One `git log -n N --name-only` for a whole list: last_change answers from memory (tasks.py list: 1 spawn, not 3 per card).
    A path with no hit in the window falls back to its own git call, unless the card's refresh is newer than the window (see hint)."""
    if is_shallow(repo):
        return
    out = git(repo, "log", "-n", str(n), "-c", "--name-only", "--no-renames", "--format=%x01%H%x09%cI%x09%s")
    rows = []
    for blk in out.split(chr(1))[1:]:
        head, _, files = blk.partition(chr(10))
        sha, iso, subj = head.split(chr(9), 2)
        rows.append((sha, iso, subj, [f for f in files.split(chr(10)) if f.strip()]))
    _LC_LOG[str(repo)] = rows


def _hit(f, p):
    return f == p or f.startswith(p.rstrip("/") + "/")


CARD_RE = re.compile(r"^MyTradingSys/system/tasks/[^/]+\.json$")
CARD_EXCLUDE = ":(exclude)MyTradingSys/system/tasks/*.json"


def _counts(f, p):
    """_hit, except a task card JSON seen through a directory scope path (f != p) is not a scope change: every card commit would re-stale
    each card whose scope_in names MyTradingSys/system/tasks. A scope path naming the card file itself still counts."""
    return _hit(f, p) and not (f != p and CARD_RE.match(f))


def last_change(repo, paths, hint=None):
    """(short sha, utc, subject) of the newest commit touching any of paths, or None.
    hint = (scope_sha, refreshed_utc): when the prefetch window has no hit and the refresh is newer than the window's oldest
    commit, nothing touched the paths since the refresh, so the last change is still scope_sha (returned with empty utc/subject)."""
    if not paths:
        return None
    rows = _LC_LOG.get(str(repo))
    if rows:
        for sha, iso, subj, files in rows:
            if any(_counts(f, p) for f in files for p in paths):
                return sha[:12], utc_of(iso), subj
        if hint and hint[0] and hint[1] and hint[1] > utc_of(rows[-1][1]):
            return hint[0], "", ""
    spec = list(paths)
    if any((Path(repo) / p).is_dir() for p in paths):
        spec.append(CARD_EXCLUDE)    # excluded only when a directory path is in play; an exact card-file path stays counted (its own pathspec)
    row = git(repo, "log", "-1", "--format=%H%x09%cI%x09%s", "--", *spec)
    if not row:
        return None
    sha, iso, subj = row.split(chr(9), 2)
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


_SHALLOW = {}   # repo -> bool: a clone does not change depth inside one process (plan-hang-claims: one git call per card)


def is_shallow(repo):
    """A depth-limited clone (CI checkout) cannot say when a path last changed: git log then reports HEAD for every path."""
    k = str(repo)
    if k not in _SHALLOW:
        _SHALLOW[k] = git(repo, "rev-parse", "--is-shallow-repository") == "true"
    return _SHALLOW[k]


def stale_reason(card, repo):
    """'' when the card's pointers match its scope's newest commit; else why not. Only ready/active cards are judged."""
    if card.get("state") not in ("ready", "active"):
        return ""
    if not card.get("refreshed"):
        return "latest never refreshed (tasks.py tag <id> --refresh)"
    if is_shallow(repo):
        return ""
    lc = last_change(repo, scope_paths(card, repo), hint=(card.get("scope_sha"), card.get("refreshed")))
    if lc and not card.get("scope_sha") and lc[1]:
        # hand-set refreshed (feeder cards): stale only when the change is newer than the refresh
        if lc[1] > (card.get("refreshed") or ""):
            return f"scope changed {lc[0]} {lc[1]} after refresh {card['refreshed']}"
        return ""
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
