"""health_audit.py - the whole "is the dev process fast and cheap?" check in one command (AUDIT_RUNBOOK.md).

  python scripts/dev/health_audit.py [hours]      default 72; fetches origin first; read-only

Prints: commit mix, gate-bookkeeping share, B4 adoption (release folded into ship), recent CI with the failed step and its
first annotation, stale claims, and the workflow-file commits of the window. Flags use the thresholds in FLAGS, so a person
(or a model) reads verdicts, not raw numbers. Public GitHub API, unauthenticated (~60 calls/h): it uses 2 + one per red run.
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
# gate upkeep: registries, allowlists, size caps, "fix CI" commits (subjects of non-merge commits)
BOOKKEEPING = re.compile(r"register|allowlist|wiring|CI red|gate entries|unblock|size cap|under .*cap|fit .*cap|\btrim\b", re.I)
FLAGS = {"overhead_pct": 50, "bookkeeping_pct": 5, "b4_adoption_pct": 50, "ci_red_runs": 1}


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout


def fetch_json(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "mts-health-audit"}), timeout=20) as r:
            return json.load(r)
    except Exception as e:  # rate limit, offline: report it, never fail the audit
        return {"_error": str(e)[:120]}


def mix(hours):
    return TR.report(hours)


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
    d = fetch_json(f"{API}/runs?branch=fast-track&per_page={limit}")
    if "workflow_runs" not in d:
        return None, d.get("_error", "no data"), []
    runs = d["workflow_runs"]
    counts = Counter(r["conclusion"] or r["status"] for r in runs)
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
    return counts, "", red


def stale_claims():
    out = subprocess.run([sys.executable, str(REPO / "scripts" / "dev" / "sync.py"), "claims"], capture_output=True,
                         text=True, cwd=REPO).stdout.splitlines()
    return [ln.strip() for ln in out if "STALE" in ln]


def workflow_commits(hours):
    return git("log", TR.TRUNK, f"--since={hours} hours ago", "--no-merges", "--format=%h %s", "--", *WORKFLOW_PATHS).splitlines()


def pct(n, d):
    return 100 * n / d if d else 0.0


def build(hours=72):
    git("fetch", "origin", "-q")
    lines = [f"# health audit, last {hours} h", "", "## Commit mix", mix(hours)]
    m = re.search(r"overhead \d+ \((\d+)%\)", lines[-1])
    flags = []
    if m and int(m.group(1)) > FLAGS["overhead_pct"]:
        flags.append(f"OVERHEAD {m.group(1)}% > {FLAGS['overhead_pct']}%: see B4 adoption and merge share (one ship per task)")
    n, total, hit = bookkeeping(hours)
    lines += ["", "## Gate bookkeeping (registry/allowlist/size-cap/unblock commits)",
              f"{n} of {total} non-merge commits ({pct(n, total):.0f}%)"] + [f"- {s[:110]}" for s in hit[:12]]
    if pct(n, total) > FLAGS["bookkeeping_pct"]:
        flags.append(f"BOOKKEEPING {pct(n, total):.0f}% > {FLAGS['bookkeeping_pct']}%: find the hand-kept list that keeps failing and auto-discover it")
    alone, folded = b4_adoption(hours)
    lines += ["", "## B4 adoption (release folded into ship)", f"standalone release commits {alone}, folded {folded}"]
    if alone + folded and pct(folded, alone + folded) < FLAGS["b4_adoption_pct"]:
        flags.append(f"B4 ADOPTION {pct(folded, alone + folded):.0f}% < {FLAGS['b4_adoption_pct']}%: enforce in sync.py, docs alone do not change behaviour")
    counts, err, red = ci()
    lines += ["", "## CI on fast-track (last 30 runs)"]
    if counts is None:
        lines.append(f"unavailable: {err}")
    else:
        lines.append(", ".join(f"{k} {v}" for k, v in counts.most_common()))
        lines += [f"- RED {t} {sha}: failed {', '.join(st) or '?'} | {note}" for t, sha, st, note in red]
        if counts.get("failure", 0) >= FLAGS["ci_red_runs"]:
            flags.append(f"CI RED {counts['failure']} of 30 runs: fix the step named above first (CLAUDE.md boot step 2)")
    stale = stale_claims()
    lines += ["", "## Stale claims"] + ([f"- {s}" for s in stale] or ["none"])
    if stale:
        flags.append(f"{len(stale)} STALE CLAIM(S): release or escalate")
    wf = workflow_commits(hours)
    lines += ["", f"## Workflow-file commits ({len(wf)}, newest first, 40 shown)"] + [f"- {s[:120]}" for s in wf[:40]]
    lines[2:2] = ["## Flags"] + ([f"- {f}" for f in flags] or ["- none"]) + [""]
    return "\n".join(lines)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if re.fullmatch(r"\d+", a)]
    sys.stdout.reconfigure(errors="replace")
    print(build(int(args[0]) if args else 72))
