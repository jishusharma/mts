"""health_audit.py - the "is the dev process fast and cheap?" check in one command (MTS_DOCTOR.md; mts_doctor.py wraps it).

  python scripts/dev/health_audit.py [hours] [--no-fetch]      default 72; read-only; exit 1 when a flag fires

Prints: flags, commit mix, gate-bookkeeping share, B4 adoption (release folded into ship), recent CI with the failed step and its
first annotation, stale claims, and the latest workflow-file commits. The METRICS line is what the next run diffs against.
Public GitHub API, unauthenticated (~60 calls/h): one list call plus, per red run (max 3), 1 jobs call and up to 1 annotations call.
"""
import json
import re
import subprocess
import sys
import urllib.request
from collections import Counter
from pathlib import Path

import traffic_report as TR

REPO = Path(__file__).resolve().parents[2]
API = "https://api.github.com/repos/jishusharma/mts/actions"
WORKFLOW_PATHS = ["scripts/dev", "scripts/sched", ".github", "CLAUDE.md", ".claude", "MyTradingSys/system/TRAFFIC_BUSTERS.md",
                  "MyTradingSys/system/PARALLEL.md", "MyTradingSys/system/WORKERS.md", "MyTradingSys/system/RELAY.md"]
# Gate upkeep in non-merge subjects: a registry/wiring/gate declaration, an allowlist row, a size-cap trim, a CI-red fix.
# Anchored on pairs so a feature commit that merely says "register" or "wiring" does not count (upper bound, still a regex).
BOOKKEEPING = re.compile(r"\b(declare|register|registered)\b.*\b(wiring|registry|extra gate|gate)\b|^gate: register|allowlist"
                         r"|\bsize cap\b|\b(under|fit|within) .*\bcap\b|\btrim to\b|\bCI red\b|\bunblocks? the (ship )?gate\b", re.I)
FLAGS = {"overhead_pct": 50, "bookkeeping_pct": 5, "b4_adoption_pct": 50}


def git(*a, timeout=120):
    try:
        return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def fetch_json(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "mts-health-audit"}), timeout=20) as r:
            return json.load(r)
    except Exception as e:  # rate limit, offline: report it, never fail the audit
        return {"_error": str(e)[:120]}


def bookkeeping(hours):
    subs = git("log", TR.TRUNK, f"--since={hours} hours ago", "--no-merges", "--format=%s").splitlines()
    hit = [s for s in subs if BOOKKEEPING.search(s)]
    return len(hit), len(subs), hit


def b4_adoption(hours):
    """Standalone `release <slug>` commits vs releases folded into a ship (body: 'closed with the ship')."""
    log = git("log", TR.TRUNK, f"--since={hours} hours ago", "--no-merges", "--format=%x00%s%n%b").split("\x00")[1:]
    alone = sum(1 for e in log if e.startswith("release ") and "closed with the ship" not in e)
    folded = sum(1 for e in log if "closed with the ship" in e)
    return alone, folded


def ci(limit=30):
    """(counts, error, latest_conclusion, red) - red lists up to 3 failed runs, newest first, with failed steps + first annotation."""
    d = fetch_json(f"{API}/runs?branch=fast-track&per_page={limit}")
    if "workflow_runs" not in d:
        return None, d.get("_error", "no data"), "", []
    runs = d["workflow_runs"]
    counts = Counter(r["conclusion"] or r["status"] for r in runs)
    latest = next((r["conclusion"] for r in runs if r["conclusion"] in ("success", "failure")), "")
    red = []
    for r in [r for r in runs if r["conclusion"] == "failure"][:3]:
        steps, note = [], ""
        for j in fetch_json(f"{API}/runs/{r['id']}/jobs").get("jobs", []):
            if j.get("conclusion") != "failure":
                continue
            steps += [s["name"] for s in j["steps"] if s.get("conclusion") == "failure"]
            if not note:
                ann = fetch_json(f"https://api.github.com/repos/jishusharma/mts/check-runs/{j['id']}/annotations")
                if isinstance(ann, list):
                    note = next((a["message"][:300] for a in ann if a.get("annotation_level") == "failure"
                                 and "exit code" not in a["message"]), "")
        red.append((r["created_at"][5:16], r["head_sha"][:8], sorted(set(steps)), note))
    return counts, "", latest, red


def stale_claims():
    try:
        out = subprocess.run([sys.executable, str(REPO / "scripts" / "dev" / "sync.py"), "claims"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", cwd=REPO, timeout=120).stdout.splitlines()
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [ln.strip() for ln in out if "STALE" in ln]


def workflow_commits(hours):
    return git("log", TR.TRUNK, f"--since={hours} hours ago", "--no-merges", "--format=%h %s", "--", *WORKFLOW_PATHS).splitlines()


def pct(n, d):
    return 100 * n / d if d else 0.0


def audit(hours=72, fetch=True):
    """(markdown, flags). flags is empty when nothing needs action."""
    fetched = "skipped (--no-fetch)"
    if fetch:
        fetched = "ok" if subprocess.run(["git", "-C", str(REPO), "fetch", "origin", "-q"], capture_output=True,
                                         timeout=120).returncode == 0 else "FAILED: numbers may be stale"
    mixline = TR.report(hours)
    lines = [f"# health audit, last {hours} h (git fetch: {fetched})", "", "## Commit mix", mixline]
    flags = []
    m = re.search(r"overhead \d+ \((\d+)%\)", mixline)
    overhead = int(m.group(1)) if m else 0
    if overhead > FLAGS["overhead_pct"]:
        flags.append(f"OVERHEAD {overhead}% > {FLAGS['overhead_pct']}%: see B4 adoption and merge share (one ship per task)")
    n, total, hit = bookkeeping(hours)
    book = pct(n, total)
    lines += ["", "## Gate bookkeeping (registry/allowlist/size-cap/CI-red commits)", f"{n} of {total} non-merge commits ({book:.0f}%)"]
    lines += [f"- {s[:110]}" for s in hit[:12]]
    if book > FLAGS["bookkeeping_pct"]:
        flags.append(f"BOOKKEEPING {book:.0f}% > {FLAGS['bookkeeping_pct']}%: find the hand-kept list that keeps failing and auto-discover it")
    alone, folded = b4_adoption(hours)
    b4 = pct(folded, alone + folded)
    lines += ["", "## B4 adoption (release folded into ship)", f"standalone release commits {alone}, folded {folded}"]
    if alone + folded and b4 < FLAGS["b4_adoption_pct"]:
        flags.append(f"B4 ADOPTION {b4:.0f}% < {FLAGS['b4_adoption_pct']}%: enforce in sync.py, docs alone do not change behaviour")
    counts, err, latest, red = ci()
    lines += ["", "## CI on fast-track"]
    if counts is None:
        lines.append(f"unavailable: {err}")
    else:
        lines.append(f"{sum(counts.values())} runs: " + ", ".join(f"{k} {v}" for k, v in counts.most_common()) + f" | newest finished: {latest or '?'}")
        lines += [f"- RED {t} {sha}: failed {', '.join(st) or '?'} | {note}" for t, sha, st, note in red]
        if latest == "failure":
            flags.append("CI RED on the newest finished run: fix the step named above first (CLAUDE.md boot step 2)")
    stale = stale_claims()
    lines += ["", "## Stale claims"] + ([f"- {s}" for s in stale] or ["none"])
    if stale:
        flags.append(f"{len(stale)} STALE CLAIM(S): release or escalate")
    wf = workflow_commits(hours)
    lines += ["", f"## Workflow-file commits ({len(wf)} in window, newest 10)"] + [f"- {s[:120]}" for s in wf[:10]]
    lines += ["", f"METRICS overhead={overhead} bookkeeping={book:.0f} b4={b4:.0f} stale_claims={len(stale)} ci_latest={latest or '?'}"]
    lines[2:2] = ["## Flags"] + ([f"- {f}" for f in flags] or ["- none"]) + [""]
    return "\n".join(lines), flags


def build(hours=72, fetch=True):
    return audit(hours, fetch)[0]


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if re.fullmatch(r"\d+", a)]
    sys.stdout.reconfigure(errors="replace")
    text, flags = audit(int(args[0]) if args else 72, "--no-fetch" not in sys.argv)
    print(text)
    sys.exit(1 if flags else 0)
