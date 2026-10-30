#!/usr/bin/env python
"""On-demand fix verifier (ledger A4-18). No scheduler, no daemon.

  python scripts/dev/fix_verifier.py [--hours 24] [--ref origin/fast-track] [--no-run]

Lists every commit of the last N hours on the ref that carries a `Result:` line.
For each, looks for a named check in the commit message and in the task card it names:
  - a tracked test file path (`scripts/dev/test_x.py`, `tests/test_x.py`) -> run read-only
    with `pytest -q` (60 s cap); pass = VERIFIED.
Anything else is CANNOT-VERIFY with the reason (no check named / file gone / failed /
timeout / --no-run). Commands in messages are never executed (could write or deploy).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEP, FIELD = "\x1e", "\x1f"
TEST_RE = re.compile(r"(?<![\w/.-])((?:[\w.-]+/)*test_[\w.-]+\.py)")
CARD_RE = re.compile(r"MyTradingSys/system/tasks/([\w.-]+)\.json")


def parse_log(text):
    """git log output (SEP between commits, FIELD between sha/subject/body) -> commits with a Result: line."""
    out = []
    for rec in text.split(SEP):
        if FIELD not in rec:
            continue
        sha, subj, body = (rec.strip("\n").split(FIELD) + ["", ""])[:3]
        m = re.search(r"^Result:\s*(.+)$", body, re.M)
        if m:
            out.append({"sha": sha.strip()[:9], "subject": subj.strip(), "result": m.group(1).strip(), "body": body})
    return out


def named_tests(*texts):
    seen = []
    for t in texts:
        for p in TEST_RE.findall(t or ""):
            if p not in seen:
                seen.append(p)
    return seen


def card_text(body, root=ROOT):
    parts = []
    for slug in CARD_RE.findall(body):
        f = root / "MyTradingSys" / "system" / "tasks" / (slug + ".json")
        if f.is_file():
            parts.append(f.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def verify(commit, root=ROOT, run=True, runner=None):
    """-> (status, reason). runner(path) -> (ok, tail) is injectable for tests."""
    tests = named_tests(commit["subject"], commit["body"], card_text(commit["body"], root))
    if not tests:
        return "CANNOT-VERIFY", "no test file named in commit or card"
    live = [t for t in tests if (root / t).is_file()]
    if not live:
        return "CANNOT-VERIFY", "named test not on disk: " + tests[0]
    if not run:
        return "CANNOT-VERIFY", "not run (--no-run or --max-run cap): " + live[0]
    runner = runner or (lambda p: _pytest(p, root))
    ok, tail = runner(live[0])
    return ("VERIFIED", live[0]) if ok else ("CANNOT-VERIFY", "test fails/times out now: %s (%s)" % (live[0], tail))


def _pytest(path, root):
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", path],
                           cwd=root, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return False, "timeout 60s"
    last = (r.stdout.strip().splitlines() or [""])[-1][:80]
    return r.returncode == 0, last


def git_log(hours, ref, root=ROOT):
    fmt = SEP + "%H" + FIELD + "%s" + FIELD + "%b"
    r = subprocess.run(["git", "-C", str(root), "log", ref, "--no-merges", "--since=%d hours ago" % hours, "--format=" + fmt],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        raise SystemExit("git log failed: " + r.stderr.strip())
    return r.stdout


def table(rows):
    lines = ["| sha | fix | status | detail |", "|---|---|---|---|"]
    for c, st, why in rows:
        lines.append("| %s | %s | %s | %s |" % (c["sha"], c["result"][:60].replace("|", "/"), st, why.replace("|", "/")))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hours", type=int, default=24)
    ap.add_argument("--ref", default="origin/fast-track")
    ap.add_argument("--no-run", action="store_true")
    ap.add_argument("--max-run", type=int, default=8, help="newest N commits get their test run")
    a = ap.parse_args(argv)
    commits = parse_log(git_log(a.hours, a.ref))
    if not commits:
        print("no commits with a Result: line in the last %d h on %s" % (a.hours, a.ref))
        return 0
    for c in commits:  # test files the commit itself touched count as named
        r = subprocess.run(["git", "-C", str(ROOT), "show", "--name-only", "--format=", c["sha"]],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        c["body"] += chr(10) + r.stdout
    rows = []
    for i, c in enumerate(commits):  # cheap = at most --max-run pytest launches
        rows.append((c,) + verify(c, run=not a.no_run and i < a.max_run))
    print(table(rows))
    ok = sum(1 for _, s, _ in rows if s == "VERIFIED")
    print("\n%d of %d VERIFIED; %d CANNOT-VERIFY" % (ok, len(rows), len(rows) - ok))
    return 0


if __name__ == "__main__":
    sys.exit(main())
