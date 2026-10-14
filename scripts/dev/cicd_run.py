import sys; sys.dont_write_bytecode = True
"""cicd_run.py - end-to-end CI/CD runner for MTS (design: MyTradingSys/research/CICD_PIPELINE_2026-10-03.md).

One function per stage (2.1 to 2.9). No stage stops the run: every stage records PASS / WARN / FAIL / SKIP / CRASH
and the next stage runs. The runner never halts, kills, restarts, commits, pushes, merges, deletes or touches
HALT / AUTO_PAUSE / open trades; it writes only receipts. Exit code is data: 0 all PASS/SKIP, 1 any WARN, 2 any
FAIL/CRASH. The release verdict is one printed line and is advisory; the commit stays the operator's action.

Receipts (append only):
  MyTradingSys/runtime/cicd_run_<YYYY-MM-DD>.jsonl   one row per stage: utc, run, profile, stage, name, status, evidence, checks, seconds
  MyTradingSys/runtime/cicd_run_<YYYY-MM-DD>.out.txt full command output (never conclude from a truncated tail)
  MyTradingSys/runtime/cicd_warn.jsonl               one line per WARN/FAIL/CRASH check (stage 2.9)

Usage (repo root):
  python scripts/dev/cicd_run.py --profile desktop|precommit|postclose|cloud [--session ID] [--quick] [--only 2.1,2.4]
  python scripts/dev/cicd_run.py --write-baseline      (re-seed MyTradingSys/system/critical_files.json; operator action)
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PY = sys.executable
TS_FMT = "%Y-%m-%dT%H:%M:%SZ"

PASS, WARN, FAIL, SKIP, CRASH = "PASS", "WARN", "FAIL", "SKIP", "CRASH"
_ORDER = [SKIP, PASS, WARN, FAIL, CRASH]

BUGS_REL = "MyTradingSys/research/BUGS.md"
INDEX_REL = "MyTradingSys/items/INDEX.md"
PIPE_REL = "MyTradingSys/runtime/BUILD_PIPELINE.md"
FILE_INDEX_REL = "MyTradingSys/system/03_FILE_INDEX.md"
CRITICAL_REL = "MyTradingSys/system/critical_files.json"
SUPERVISOR_LOG_REL = "MyTradingSys/research/fast_track_2026-09-27/SUPERVISOR_LOG.md"
BUILD_REPORT_REL = "MyTradingSys/runtime/BUILD_REPORT.md"
SESSIONS_REL = "MyTradingSys/system/sessions"

# DSA_SESSION_PROMPT.md section 6, "Critical files:".
CRITICAL_PATHS = [
    "MyTradingSys/runtime/compiled_engine.md",
    "DSA_SESSION_PROMPT.md",
    "MyTradingSys/system/01_AI_BEHAVIOR.md",
    "MyTradingSys/runtime/mts_math.py",
    "MyTradingSys/runtime/math_object_builder.py",
    "scripts/core/start-trading-day.ps1",
    "scripts/core/mode.ps1",
    "scripts/core/stop-day.ps1",
    "MyTradingSys/PROJECT_VISION.md",
]

# Design 2.7: excluded from every dirty check and never in a pathspec.
DIRTY_ALLOW = (
    "MyTradingSys/runtime/BUILD_REPORT.md",
    "MyTradingSys/runtime/session_log.json",
    "MyTradingSys/execution/pm_heartbeats/",
    "MyTradingSys/runtime/orderflow_live/",
    "MyTradingSys/research/testnet_status/",
    "MyTradingSys/runtime/cicd_",
)

LIVE_EXEC_PREFIX = "MyTradingSys/execution/"
LIVE_EXEC_STATE = ("journal/", "plans/", "halt_history/", "pm_heartbeats/", "__pycache__/", ".secrets/")
LIVE_ALERTS_PREFIX = "MyTradingSys/backtest/layers/alerts/"
LIVE_LOOP_FILES = (
    "MyTradingSys/runtime/math_object_builder.py", "MyTradingSys/runtime/mts_math.py",
    "MyTradingSys/runtime/build_mo_cli.py", "MyTradingSys/runtime/update_market_state.py",
    "MyTradingSys/system/net_rr_floor.json", "MyTradingSys/system/runner_min_distance.json",
)
LIVE_LOOP_PREFIXES = ("scripts/core/", "src/main/java/datafeed/")
LIVE_DISCOVERY_RE = re.compile(r"AUTO_PAUSE|HALT_|halt_history|private/(buy|sell|edit|cancel)|stop_market|trade_ledger|auto_trader_state|pm_heartbeat")
DISCOVERY_SKIP = ("archive", "backup_session", "_archive", "Dumps/", ".pre_", "/test_", "__pycache__")

OPEN_SET = {"OPEN", "IN-FIX", "BLOCKED"}
CLOSED_SET = {"CLOSED", "WONTFIX"}
VALID_STATUS = {"OPEN", "IN-FIX", "BLOCKED", "CLOSED", "WONTFIX"}
VALID_SEVERITY = {"HIGH", "MED", "LOW", "COSMETIC"}
CYR_LO, CYR_HI = 0x0400, 0x04FF  # the Cyrillic block Build-Check scans for
TEXT_EXT = {".md", ".py", ".ps1", ".json", ".java", ".txt", ".csv", ".jsonl", ".xml", ".vbs"}


# ------------------------------------------------------------------ plumbing
def utc_now():
    return datetime.now(timezone.utc)


def default_run(cmd, cwd=None, env=None):
    """Run a command, capture stdout+stderr, record wall seconds, kill nothing. (rc None = tool missing.)"""
    e = dict(os.environ)
    e["PYTHONDONTWRITEBYTECODE"] = "1"
    if env:
        e.update(env)
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=e, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
    except (FileNotFoundError, OSError) as ex:
        return None, "tool not found: %s (%s)" % (cmd[0], ex), round(time.time() - t0, 2)
    return p.returncode, (p.stdout or "") + (p.stderr or ""), round(time.time() - t0, 2)


class Ctx:
    def __init__(self, repo=REPO, profile="desktop", session="", run=None, now=None, out_dir=None,
                 which=None, quick=False, emit=None):
        self.repo = Path(repo)
        self.profile = profile
        self.session = session
        self.run = run or default_run
        self.now = now or utc_now
        self.out_dir = Path(out_dir) if out_dir else self.repo / "MyTradingSys" / "runtime"
        self.which = which or shutil.which
        self.quick = quick
        self.emit = emit or (lambda s: print(s))
        self.run_id = self.now().strftime("%Y%m%dT%H%M%SZ")
        self.rows = []

    def p(self, rel):
        return self.repo / rel

    def read(self, rel):
        try:
            return self.p(rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None

    def git(self, *args):
        rc, out, _ = self.run(["git", "-C", str(self.repo)] + list(args), cwd=self.repo)
        return rc, (out or "").rstrip("\r\n")

    def day_file(self, suffix):
        return self.out_dir / ("cicd_run_%s.%s" % (self.now().strftime("%Y-%m-%d"), suffix))

    def append(self, path, text):
        """Append-only receipt. If it cannot be written, print it: stdout is the last-resort receipt."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8", newline="\n") as f:
                f.write(text)
            return True
        except OSError as ex:
            self.emit("RECEIPT-WRITE-FAILED %s: %s" % (path, ex))
            self.emit(text.rstrip("\n"))
            return False

    def previous_counts(self):
        """Last recorded pytest pass count per check name, from receipts written before this run."""
        counts = {}
        for f in sorted(self.out_dir.glob("cicd_run_*.jsonl")):
            try:
                lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for ln in lines:
                try:
                    row = json.loads(ln)
                except ValueError:
                    continue
                if row.get("run") == self.run_id:
                    continue
                for c in row.get("checks", []):
                    if c.get("count") is not None and c.get("check", "").startswith("build/"):
                        counts[c["check"]] = c["count"]
        return counts


def ck(check, status, detail="", **extra):
    d = {"check": check, "status": status, "detail": detail}
    d.update(extra)
    return d


def worst(statuses):
    return max(statuses, key=_ORDER.index) if statuses else SKIP


def tail(text, n=20):
    return "\n".join((text or "").splitlines()[-n:])


def norm(path):
    return path.replace("\\", "/")


# ------------------------------------------------------------------ change set
def change_set(ctx):
    """[(xy, path)] from porcelain status, minus the dirty allowlist. Renames report the new path."""
    rc, out = ctx.git("status", "--porcelain", "-z", "-uall")
    if rc != 0:
        return []
    items = out.split("\0")
    res, i = [], 0
    while i < len(items):
        e = items[i]
        i += 1
        if len(e) < 4:
            continue
        xy, path = e[:2], norm(e[3:])
        if xy[0] in "RC":
            i += 1  # skip the old name that follows a rename/copy entry
        if path.startswith(DIRTY_ALLOW):
            continue
        res.append((xy, path))
    return res


def is_live_trigger(path, discovered=()):
    if path.startswith(LIVE_EXEC_PREFIX):
        rest = path[len(LIVE_EXEC_PREFIX):]
        if any(rest.startswith(s) or ("/" + s) in ("/" + rest) for s in LIVE_EXEC_STATE):
            return False
        if ".pre_" in rest or rest.endswith((".jsonl", "AUTO_PAUSE")) or rest.endswith("_state.json"):
            return False
        return True
    if path.startswith(LIVE_ALERTS_PREFIX):
        return True
    if path in LIVE_LOOP_FILES or path.startswith(LIVE_LOOP_PREFIXES):
        return True
    return path in discovered


# ------------------------------------------------------------------ registry parsing
def parse_bugs(text):
    rows, dups, bad = {}, [], []
    for ln in (text or "").splitlines():
        if not re.match(r"^\|\s*[BT]\d+\s*\|", ln):
            continue
        cells = [c.strip() for c in ln.split("|")]
        if len(cells) < 9:
            bad.append(ln[:80])
            continue
        rid = cells[1]
        if rid in rows:
            dups.append(rid)
        rows[rid] = {"opened": cells[2], "status": cells[3], "severity": cells[4], "receipt": cells[7]}
    return rows, dups, bad


def parse_index(text):
    rows = {}
    for ln in (text or "").splitlines():
        m = re.match(r"^([BT]\d+)\s*\|\s*(\S+)\s*\|\s*([^|]+?)\s*\|", ln)
        if m:
            rows[m.group(1)] = {"status": m.group(2), "file": m.group(3)}
    return rows


def parse_pipeline(text):
    rows = []
    for ln in (text or "").splitlines():
        if not re.match(r"^\|\s*\d+\.\d+\s*\|", ln):
            continue
        c = [x.strip() for x in ln.split("|")]
        if len(c) < 8:
            continue
        rows.append({"num": c[1], "id": c[2], "slug": c[3], "status": c[4], "blocker": c[5], "next": c[6]})
    return rows


def sources_missing(ctx, rels):
    return [r for r in rels if ctx.read(r) is None]


# ------------------------------------------------------------------ stage 2.1 intake
def stage_intake(ctx):
    checks = []
    miss = sources_missing(ctx, [BUGS_REL, INDEX_REL, PIPE_REL])
    for m in miss:
        checks.append(ck("intake/source", SKIP, "MISSED: %s absent" % m))
    if BUGS_REL in miss:
        return checks
    bugs, dups, bad = parse_bugs(ctx.read(BUGS_REL))
    index = parse_index(ctx.read(INDEX_REL)) if INDEX_REL not in miss else {}
    pipe = parse_pipeline(ctx.read(PIPE_REL)) if PIPE_REL not in miss else []
    checks.append(ck("intake/counts", PASS, "BUGS rows %d (open %d), INDEX rows %d, pipeline rows %d" % (
        len(bugs), sum(1 for r in bugs.values() if r["status"] in OPEN_SET), len(index), len(pipe))))

    if INDEX_REL not in miss:
        only_index = sorted(i for i in index if i not in bugs)
        checks.append(ck("intake/id-only-in-one-source", WARN if only_index else PASS,
                         "INDEX rows with no BUGS row: %s" % (", ".join(only_index) or "none")))
        open_not_idx = sorted(i for i, r in bugs.items() if r["status"] in OPEN_SET and i not in index)
        checks.append(ck("intake/open-not-in-index", WARN if open_not_idx else PASS,
                         "BUGS open rows with no INDEX row: %s" % (", ".join(open_not_idx) or "none")))
        disagree = []
        for i, r in bugs.items():
            if i in index:
                idx_status = "BLOCKED" if index[i]["status"] == "PARKED" else index[i]["status"]
                if idx_status != r["status"]:
                    disagree.append("%s BUGS=%s INDEX=%s" % (i, r["status"], index[i]["status"]))
        checks.append(ck("intake/status-disagree", WARN if disagree else PASS, "; ".join(disagree) or "none"))

    if PIPE_REL not in miss:
        local = [r["id"] for r in pipe if not re.match(r"^[BT]\d+$", r["id"])]
        checks.append(ck("intake/pipeline-local", PASS, "pipeline-local rows (never orphans): %s" % (", ".join(local) or "none")))
        not_in_bugs = sorted({r["id"] for r in pipe if re.match(r"^[BT]\d+$", r["id"]) and r["id"] not in bugs})
        checks.append(ck("intake/pipeline-id-not-in-bugs", WARN if not_in_bugs else PASS, ", ".join(not_in_bugs) or "none"))
        stale = []
        for r in pipe:
            rid = r["id"]
            if rid in bugs and r["status"] in ("QUEUED", "IN-FLIGHT"):
                if bugs[rid]["status"] in CLOSED_SET:
                    stale.append("%s pipeline %s, BUGS %s (STALE-VS-BUGS)" % (rid, r["status"], bugs[rid]["status"]))
                    continue
                rc, out = ctx.git("log", "-n", "1", "--format=%h %s", "-i", "-E", "--grep=^" + rid + ":")
                if rc == 0 and out.strip():
                    stale.append("%s pipeline %s, history carries %s (STALE-VS-GIT)" % (rid, r["status"], out.strip()[:60]))
        checks.append(ck("intake/stale-pipeline", WARN if stale else PASS, "; ".join(stale) or "none"))
        blocked = [r["id"] for r in pipe if "operator" in r["blocker"].lower()]
        checks.append(ck("intake/blocked-on-operator", PASS, "BLOCKED-ON-OPERATOR (skipped, logged, flow continues): %s" % (", ".join(blocked) or "none")))

    for rel in ("MyTradingSys/research/apparatus_fixes.md", "MyTradingSys/runtime/NEXT_SESSION_HANDOFF.md",
                "Dumps/operator/context/DSA_HANDOFF.md"):
        if ctx.read(rel) is None:
            checks.append(ck("intake/handoff-source", SKIP, "MISSED: %s absent" % rel))
    directives = sorted((ctx.p("MyTradingSys/research")).glob("OPERATOR_DIRECTIVE_*.md")) if ctx.p("MyTradingSys/research").is_dir() else []
    checks.append(ck("intake/directives", PASS, "%d OPERATOR_DIRECTIVE file(s); constraints, not rows" % len(directives)))
    br = ctx.read(BUILD_REPORT_REL)
    if br is not None:
        n_new = sum(1 for ln in br.splitlines() if ".new" in ln)
        checks.append(ck("intake/staged-new", PASS, "BUILD_REPORT lines naming .new files: %d (staged work is pending work)" % n_new))
    sess_dir = ctx.p(SESSIONS_REL)
    open_sessions = []
    if sess_dir.is_dir():
        for f in sorted(sess_dir.glob("MTS-*.md")):
            try:
                body = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if re.search(r"status:\s*open\b", body):
                open_sessions.append(f.stem)
    checks.append(ck("intake/open-sessions", PASS, "session records with status open: %s" % (", ".join(open_sessions) or "none")))
    if dups or bad:
        checks.append(ck("intake/bugs-shape", WARN, "duplicate ids %s; malformed rows %s" % (dups, bad)))
    return checks


# ------------------------------------------------------------------ stage 2.2 pre-commit
def parse_ps1(ctx, rels):
    """PowerShell parse of changed .ps1 files in one shell call; returns {path: error_count_or_msg} or None."""
    sh = ctx.which("powershell") or ctx.which("pwsh")
    if not sh:
        return None
    script = ("foreach ($f in $args) { $t=$null; $e=$null; "
              "[void][System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path -LiteralPath $f).Path,[ref]$t,[ref]$e); "
              "$m = ''; if ($e -and $e.Count -gt 0) { $m = $e[0].Message }; "
              "Write-Output ('{0}|{1}|{2}' -f $f, @($e).Count, $m) }")
    tmpdir = tempfile.mkdtemp(prefix="cicd_ps_")
    sp = Path(tmpdir) / "parse.ps1"
    sp.write_text(script, encoding="utf-8", newline="\n")
    try:
        rc, out, _ = ctx.run([sh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(sp)] + [str(ctx.p(r)) for r in rels], cwd=ctx.repo)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    if rc is None:
        return None
    res = {}
    for ln in out.splitlines():
        parts = ln.split("|", 2)
        if len(parts) == 3 and parts[1].strip().isdigit():
            res[norm(os.path.relpath(parts[0], ctx.repo))] = (int(parts[1]), parts[2].strip())
    return res


def stage_precommit(ctx):
    checks = []
    changes = change_set(ctx)
    paths = [p for _, p in changes]
    checks.append(ck("precommit/change-set", PASS, "%d path(s) outside the dirty allowlist: %s" % (len(paths), ", ".join(paths[:40]) or "none"),
                     paths=paths))
    # M3 execution/static check, no bytecode written
    bad_py = []
    py_files = [p for p in paths if p.endswith(".py") and ctx.p(p).is_file()]
    for p in py_files:
        try:
            compile(ctx.p(p).read_bytes(), p, "exec")
        except (SyntaxError, ValueError) as ex:
            bad_py.append("%s: %s" % (p, ex))
    checks.append(ck("precommit/python-compile", FAIL if bad_py else PASS,
                     "; ".join(bad_py) if bad_py else "%d changed .py file(s) compile" % len(py_files)))
    ps_files = [p for p in paths if p.endswith(".ps1") and ctx.p(p).is_file()]
    if ps_files:
        res = parse_ps1(ctx, ps_files)
        if res is None:
            checks.append(ck("precommit/powershell-parse", SKIP, "no PowerShell available for %d changed .ps1 file(s)" % len(ps_files)))
        else:
            bad = ["%s: %s" % (p, v[1]) for p, v in res.items() if v[0] > 0]
            checks.append(ck("precommit/powershell-parse", FAIL if bad else PASS,
                             "; ".join(bad) if bad else "%d changed .ps1 file(s) parse" % len(ps_files)))
    else:
        checks.append(ck("precommit/powershell-parse", PASS, "no changed .ps1 file"))
    # M4 fail-before evidence line in the session record
    if ctx.session:
        rec = ctx.read("%s/%s.md" % (SESSIONS_REL, ctx.session))
        if rec is None:
            checks.append(ck("precommit/fail-before-line", WARN, "no session record for %s" % ctx.session))
        elif re.search(r"(?im)^(#+\s*)?T3\b", rec):
            checks.append(ck("precommit/fail-before-line", PASS, "session record carries a T3 line (content not machine-verifiable)"))
        else:
            checks.append(ck("precommit/fail-before-line", WARN, "session record has no T3 line naming the test and its pre-change result"))
    else:
        checks.append(ck("precommit/fail-before-line", SKIP, "no --session given"))
    # M5 changed-file map
    disc = discover_live(ctx)
    crit = [p for p in paths if p in CRITICAL_PATHS]
    live = [p for p in paths if is_live_trigger(p, disc)]
    java = [p for p in paths if p.startswith("src/") and p.endswith(".java")]
    contract = [p for p in paths if p.startswith(("MyTradingSys/items/", "MyTradingSys/system/"))]
    checks.append(ck("precommit/gate-map", PASS,
                     "livepath(2.6)=%s artifact(2.5)=%s java=%s contract(2.4)=%s" % (
                         "yes" if live else "no", "yes" if crit else "no", "yes" if java else "no", "yes" if contract else "no"),
                     livepath=live, artifact=crit))
    return checks


# ------------------------------------------------------------------ stage 2.3 build
def stage_build(ctx):
    checks = []
    py = PY
    mvn = ctx.which("mvn") or ctx.which("mvn.cmd")
    ps = ctx.which("powershell") or ctx.which("pwsh")
    cloud = ctx.profile == "cloud"
    prev = ctx.previous_counts()
    outfile = ctx.day_file("out.txt")
    # Both mvn steps write target/, which the live loop also uses: never run two at once, never delete target/.
    steps = [
        ("build/mvn-compile", [mvn, "-q", "-DskipTests", "compile"] if mvn else None, "mvn", None),
        ("build/mvn-test", [mvn, "-q", "test"] if mvn else None, "mvn", None),
        ("build/pytest-math", [py, "-m", "pytest", "MyTradingSys/tests", "--ignore=MyTradingSys/tests/docs", "-q", "-p", "no:cacheprovider"], "pytest", "MyTradingSys/tests"),
        ("build/pytest-docs", [py, "-m", "pytest", "MyTradingSys/tests/docs", "-q", "-p", "no:cacheprovider"], "pytest", "MyTradingSys/tests/docs"),
        ("build/run-all-tests", [py, "scripts/dev/run_all_tests.py"] + (["--quick"] if (ctx.quick or not mvn or cloud) else []), "runall", "scripts/dev/run_all_tests.py"),
        ("build/pytest-root", [py, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"], "pytest", "tests"),
        ("build/build-check", [ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "scripts/Build-Check.ps1", "-Quick", "-ReadOnly"] if ps else None, "buildcheck", "scripts/Build-Check.ps1"),
    ]
    for name, cmd, kind, target in steps:
        if kind in ("mvn", "buildcheck") and cloud:
            checks.append(ck(name, SKIP, "profile cloud: not assumed available"))
            continue
        if kind in ("mvn", "buildcheck") and ctx.quick:
            checks.append(ck(name, SKIP, "--quick"))
            continue
        if cmd is None:
            checks.append(ck(name, SKIP, "tool missing (%s)" % ("mvn" if kind == "mvn" else "powershell")))
            continue
        if target and not ctx.p(target).exists():
            checks.append(ck(name, SKIP, "%s absent" % target))
            continue
        rc, out, secs = ctx.run(cmd, cwd=ctx.repo)
        ctx.append(outfile, "=== %s rc=%s %ss\n%s\n" % (name, rc, secs, out))
        if rc is None:
            checks.append(ck(name, SKIP, "tool missing: %s" % out, seconds=secs))
            continue
        if kind == "pytest":
            m = re.findall(r"(\d+) passed", out)
            n = int(m[-1]) if m else None
            if rc == 5:
                checks.append(ck(name, WARN, "no tests collected", seconds=secs, count=n))
            elif rc != 0:
                checks.append(ck(name, FAIL, "exit %s; last lines: %s" % (rc, tail(out)), seconds=secs, count=n))
            elif prev.get(name) is not None and n is not None and n < prev[name]:
                checks.append(ck(name, WARN, "test count dropped %d -> %d" % (prev[name], n), seconds=secs, count=n))
            else:
                checks.append(ck(name, PASS, "%s passed" % (n if n is not None else "?"), seconds=secs, count=n))
        elif kind == "runall":
            if rc != 0:
                checks.append(ck(name, FAIL, "exit %s; last lines: %s" % (rc, tail(out)), seconds=secs))
            elif "ALL TESTS PASSED" in out:
                checks.append(ck(name, PASS, "ALL TESTS PASSED", seconds=secs))
            else:
                checks.append(ck(name, WARN, "exit 0 but no 'ALL TESTS PASSED' line", seconds=secs))
        elif kind == "buildcheck":
            m = re.findall(r"STATUS:\s*(PASS|FAIL)", out)
            if m and m[-1] == "PASS":
                checks.append(ck(name, PASS, "STATUS: PASS (BUILD_REPORT.md is allowlisted)", seconds=secs))
            else:
                checks.append(ck(name, FAIL, "STATUS: %s; last lines: %s" % (m[-1] if m else "none printed", tail(out)), seconds=secs))
        else:  # mvn
            if rc == 0:
                checks.append(ck(name, PASS, "exit 0", seconds=secs))
            else:
                checks.append(ck(name, FAIL, "exit %s; last lines: %s" % (rc, tail(out)), seconds=secs))
    return checks


# ------------------------------------------------------------------ stage 2.4 contract
def has_bom(data):
    return data[:3] == b"\xef\xbb\xbf"


def file_index_rows_missing(ctx, rels):
    idx = ctx.read(FILE_INDEX_REL)
    if idx is None:
        return None
    return [r for r in rels if r not in idx.replace("\\", "/")]


INDEXABLE_EXT = {".md", ".py", ".ps1", ".java", ".json"}
INDEX_SKIP = re.compile(r"(/runtime/(orderflow_live|sched|cicd)|pm_heartbeats|_qhist|sched_reports|testnet_status|__pycache__|archive|\.new$|\.pre_|\.bak$|\.old$)")


def stage_contract(ctx):
    checks = []
    changes = change_set(ctx)
    paths = [p for _, p in changes if ctx.p(p).is_file()]
    # C1 rule citations
    sh = ctx.which("powershell") or ctx.which("pwsh")
    vrc = "scripts/tools/verify_rule_citations.ps1"
    if ctx.profile == "cloud":
        checks.append(ck("contract/rule-citations", SKIP, "profile cloud: no PowerShell assumed"))
    elif not sh or not ctx.p(vrc).exists():
        checks.append(ck("contract/rule-citations", SKIP, "no PowerShell or %s absent" % vrc))
    else:
        rc, out, secs = ctx.run([sh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", vrc], cwd=ctx.repo)
        ctx.append(ctx.day_file("out.txt"), "=== contract/rule-citations rc=%s\n%s\n" % (rc, out))
        checks.append(ck("contract/rule-citations", PASS if rc == 0 else (SKIP if rc is None else FAIL),
                         "exit 0" if rc == 0 else "exit %s; last lines: %s" % (rc, tail(out)), seconds=secs))
    # C2 BOM, C3 non-ASCII on changed files
    boms, cyr, nonascii = [], [], []
    for p in paths:
        if Path(p).suffix.lower() not in TEXT_EXT:
            continue
        data = ctx.p(p).read_bytes()
        if has_bom(data):
            boms.append(p)
        text = data.decode("utf-8", errors="replace")
        n_cyr = sum(1 for ch in text if CYR_LO <= ord(ch) <= CYR_HI)
        n_non = sum(1 for ch in text if ord(ch) > 127)
        if n_cyr:
            cyr.append("%s:%d" % (p, n_cyr))
        if n_non:
            nonascii.append("%s:%d" % (p, n_non))
    checks.append(ck("contract/bom", FAIL if boms else PASS, ", ".join(boms) or "no BOM in %d changed text file(s)" % len(paths)))
    checks.append(ck("contract/cyrillic", FAIL if cyr else PASS, ", ".join(cyr) or "0 Cyrillic codepoints"))
    checks.append(ck("contract/non-ascii", PASS, "non-ASCII counts (information): %s" % (", ".join(nonascii) or "none")))
    # C4 forbidden phrases: the doc test's own hit lines
    if ctx.p("MyTradingSys/tests/docs/test_integrity.py").exists():
        rc, out, secs = ctx.run([PY, "-m", "pytest", "MyTradingSys/tests/docs/test_integrity.py", "-q", "-p", "no:cacheprovider",
                                 "-k", "test_2_no_forbidden_refs"], cwd=ctx.repo)
        ctx.append(ctx.day_file("out.txt"), "=== contract/forbidden-phrases rc=%s\n%s\n" % (rc, out))
        checks.append(ck("contract/forbidden-phrases", PASS if rc == 0 else (SKIP if rc is None else FAIL),
                         "test_2 passed" if rc == 0 else "test_2 exit %s; hits: %s" % (rc, "; ".join(l.strip() for l in out.splitlines() if re.match(r"^\S+:\d+:", l.strip()))[:600] or tail(out))))
    else:
        checks.append(ck("contract/forbidden-phrases", SKIP, "test_integrity.py absent"))
    # C5 registry contract (Build-Check rules, plus INDEX -> BUGS)
    btxt = ctx.read(BUGS_REL)
    if btxt is None:
        checks.append(ck("contract/registry", SKIP, "MISSED: %s absent" % BUGS_REL))
    else:
        bugs, dups, bad = parse_bugs(btxt)
        problems = ["duplicate id %s" % d for d in dups] + ["malformed row %s" % b for b in bad]
        for rid, r in bugs.items():
            if r["status"] not in VALID_STATUS:
                problems.append("%s bad status %s" % (rid, r["status"]))
            if r["severity"] not in VALID_SEVERITY:
                problems.append("%s bad severity %s" % (rid, r["severity"]))
            if r["status"] == "CLOSED" and r["receipt"] in ("-", ""):
                problems.append("%s CLOSED with no receipt" % rid)
            if r["status"] in OPEN_SET and not list(ctx.p("MyTradingSys/items").glob("%s_*.md" % rid)):
                problems.append("%s %s with no items/ file" % (rid, r["status"]))
        last = [l for l in btxt.splitlines() if l.strip()][-1:]
        if last != ["# END"]:
            problems.append("last non-empty line is not exactly '# END'")
        itxt = ctx.read(INDEX_REL)
        if itxt is not None:
            index = parse_index(itxt)
            problems += ["%s in INDEX but no BUGS row" % i for i in sorted(index) if i not in bugs]
            problems += ["%s open in BUGS, no INDEX row" % i for i, r in bugs.items() if r["status"] in OPEN_SET and i not in index]
        checks.append(ck("contract/registry", FAIL if problems else PASS, "; ".join(problems) or "%d BUGS rows valid" % len(bugs)))
    # C6 file-index row for every added file under MyTradingSys/
    added = [p for xy, p in changes if (xy == "??" or "A" in xy) and p.startswith("MyTradingSys/")
             and Path(p).suffix.lower() in INDEXABLE_EXT and not INDEX_SKIP.search("/" + p) and ctx.p(p).is_file()
             and p != FILE_INDEX_REL and not p.startswith(SESSIONS_REL + "/")]
    missing = file_index_rows_missing(ctx, added)
    if missing is None:
        checks.append(ck("contract/file-index", SKIP, "MISSED: %s absent" % FILE_INDEX_REL))
    else:
        checks.append(ck("contract/file-index", WARN if missing else PASS,
                         ("no 03_FILE_INDEX row for: " + ", ".join(missing)) if missing else "%d added file(s) all indexed" % len(added)))
    # C7 session record
    if ctx.session:
        rec = ctx.read("%s/%s.md" % (SESSIONS_REL, ctx.session))
        if rec is None:
            checks.append(ck("contract/session-record", WARN, "no record %s/%s.md" % (SESSIONS_REL, ctx.session)))
        else:
            miss = [f for f in ("status:", "started:", "model:") if f not in rec]
            checks.append(ck("contract/session-record", WARN if miss else PASS, ("record lacks " + ", ".join(miss)) if miss else "record has status, started, model"))
    else:
        checks.append(ck("contract/session-record", SKIP, "no --session given"))
    return checks


# ------------------------------------------------------------------ stage 2.5 artifact
def eol_of(data):
    crlf, lf = data.count(b"\r\n"), data.count(b"\n")
    if crlf == 0:
        return "LF"
    return "CRLF" if crlf == lf else "MIXED"


def blob_of(ctx, rel):
    rc, out = ctx.git("hash-object", "--", rel)
    return out.strip() if rc == 0 and re.fullmatch(r"[0-9a-f]{40}", out.strip()) else None


def head_blob(ctx, rel):
    rc, out = ctx.git("rev-parse", "HEAD:" + rel)
    return out.strip() if rc == 0 and re.fullmatch(r"[0-9a-f]{40}", out.strip()) else None


def build_baseline(ctx, approved_by="pending"):
    files = []
    for rel in CRITICAL_PATHS:
        fp = ctx.p(rel)
        if not fp.is_file():
            continue
        data = fp.read_bytes()
        files.append({"path": rel, "blob": blob_of(ctx, rel), "sha256_8": hashlib.sha256(data).hexdigest()[:8],
                      "eol": eol_of(data), "approved_by": approved_by, "approved_commit": "pending"})
    return {"updated_utc": ctx.now().strftime(TS_FMT),
            "source": "DSA_SESSION_PROMPT.md section 6 'Critical files:'; blob = git hash-object -- <path>; values OBSERVED until the operator approves",
            "observed_by": ctx.session or "none", "files": files}


def write_baseline(ctx):
    doc = build_baseline(ctx)
    path = ctx.p(CRITICAL_REL)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    return doc


def stage_artifact(ctx):
    checks = []
    raw = ctx.read(CRITICAL_REL)
    if raw is None:
        return [ck("artifact/baseline", WARN, "NO-BASELINE: %s absent; seed with --write-baseline" % CRITICAL_REL)]
    try:
        base = {f["path"]: f for f in json.loads(raw)["files"]}
    except (ValueError, KeyError, TypeError) as ex:
        return [ck("artifact/baseline", FAIL, "baseline unreadable: %s" % ex)]
    changed = {p for _, p in change_set(ctx)}
    baseline_in_set = CRITICAL_REL in changed
    committed_mode = ctx.profile in ("postclose", "cloud")
    for rel in CRITICAL_PATHS:
        name = "artifact/" + rel
        entry = base.get(rel)
        if entry is None:
            checks.append(ck(name, WARN, "NO-BASELINE: %s not in %s" % (rel, CRITICAL_REL)))
            continue
        cur = head_blob(ctx, rel) if committed_mode else blob_of(ctx, rel)
        if cur is None:
            checks.append(ck(name, FAIL if not committed_mode else WARN, "cannot hash %s (file missing or not committed)" % rel))
        elif cur == entry["blob"]:
            checks.append(ck(name, PASS, "MATCH %s" % cur[:12]))
        elif rel in changed and baseline_in_set:
            checks.append(ck(name, WARN, "DRIFT: %s changed with the baseline file, but blob %s != baseline %s" % (rel, cur[:12], entry["blob"][:12])))
        else:
            checks.append(ck(name, FAIL, "DRIFT-UNAPPROVED: blob %s != baseline %s%s" % (
                cur[:12], entry["blob"][:12], " (file is in the change set without a baseline update)" if rel in changed else " (file differs from the baseline, not in the change set)")))
    return checks


# ------------------------------------------------------------------ stage 2.6 live path
def discover_live(ctx):
    rc, out = ctx.git("ls-files")
    if rc != 0:
        return set()
    hits = set()
    for rel in out.splitlines():
        rel = norm(rel)
        if Path(rel).suffix not in (".py", ".ps1", ".vbs", ".java", ".cmd"):
            continue
        if any(s in rel for s in DISCOVERY_SKIP) or Path(rel).name.startswith("test_"):
            continue
        try:
            text = ctx.p(rel).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if LIVE_DISCOVERY_RE.search(text):
            hits.add(rel)
    return hits


def list_processes(ctx):
    sh = ctx.which("powershell") or ctx.which("pwsh")
    if not sh:
        return None
    script = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|pwsh|powershell|java' } | "
              "ForEach-Object { $c=''; try { $c=$_.CreationDate.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ') } catch {}; "
              "'{0}|{1}|{2}' -f $_.ProcessId, $c, $_.CommandLine }")
    rc, out, _ = ctx.run([sh, "-NoProfile", "-Command", script], cwd=ctx.repo)
    if rc != 0:
        return None
    procs = []
    for ln in out.splitlines():
        parts = ln.split("|", 2)
        if len(parts) == 3 and parts[0].strip().isdigit():
            procs.append((parts[0].strip(), parts[1].strip(), parts[2]))
    return procs


def stage_livepath(ctx):
    changes = change_set(ctx)
    paths = [p for _, p in changes]
    disc = discover_live(ctx)
    triggered = [p for p in paths if is_live_trigger(p, disc)]
    if not triggered:
        return [ck("livepath/gate", SKIP, "no live-path file in the change set (%d discovered live-path file(s))" % len(disc))]
    checks = [ck("livepath/gate", PASS, "gate on: %s" % ", ".join(triggered[:20]))]
    sup = ctx.read(SUPERVISOR_LOG_REL)
    rec = ctx.read("%s/%s.md" % (SESSIONS_REL, ctx.session)) if ctx.session else None
    # L1 one writer
    if not ctx.session:
        checks.append(ck("livepath/L1-one-writer", WARN, "no --session given; cannot name the owner"))
    elif sup is None:
        checks.append(ck("livepath/L1-one-writer", WARN, "MISSED: %s absent" % SUPERVISOR_LOG_REL))
    else:
        others = []
        sess_dir = ctx.p(SESSIONS_REL)
        if sess_dir.is_dir():
            for f in sess_dir.glob("MTS-*.md"):
                if f.stem == ctx.session:
                    continue
                body = f.read_text(encoding="utf-8", errors="replace")
                if re.search(r"status:\s*open\b", body) and re.search(r"execution/|layers/alerts", body):
                    others.append(f.stem)
        if ctx.session not in sup:
            checks.append(ck("livepath/L1-one-writer", WARN, "SUPERVISOR_LOG does not name %s against the live area" % ctx.session))
        elif others:
            checks.append(ck("livepath/L1-one-writer", WARN, "other open session(s) name the same area: %s" % ", ".join(others)))
        else:
            checks.append(ck("livepath/L1-one-writer", PASS, "SUPERVISOR_LOG names %s; no other open session on the area" % ctx.session))
    # L2 staging
    inplace = [p for xy, p in changes if p in triggered and not p.endswith(".new") and xy.strip() != "??"]
    if not inplace:
        checks.append(ck("livepath/L2-staging", PASS, "no tracked live-path file edited in place"))
    elif rec and re.search(r"no running process imports", rec, re.I):
        checks.append(ck("livepath/L2-staging", PASS, "session record states no running process imports the edited file(s)"))
    else:
        procs = list_processes(ctx)
        if procs is None:
            checks.append(ck("livepath/L2-staging", WARN, "in-place edit of %s; process list unavailable, builders never edit imported live files" % ", ".join(inplace)))
        else:
            running = [p for p in inplace if any(Path(p).name in c for _, _, c in procs)]
            if running:
                checks.append(ck("livepath/L2-staging", FAIL, "in-place edit of file(s) a running process names: %s" % ", ".join(running)))
            else:
                checks.append(ck("livepath/L2-staging", WARN, "in-place edit of %s; no running command line names it, but builders never edit imported live files" % ", ".join(inplace)))
    # L3 four-step proof: hash, edit, hash, diff
    crit_changed = [p for p in triggered if p in CRITICAL_PATHS]
    proof = bool(rec and re.search(r"hash", rec, re.I) and re.search(r"diff", rec, re.I))
    if crit_changed and not (CRITICAL_REL in paths and proof):
        checks.append(ck("livepath/L3-proof", WARN, "critical file(s) %s changed without both a baseline update and a hash/diff line in the session record" % ", ".join(crit_changed)))
    elif not proof:
        checks.append(ck("livepath/L3-proof", WARN, "session record has no hash-edit-hash-diff proof line"))
    else:
        checks.append(ck("livepath/L3-proof", PASS, "session record carries a hash/diff proof line"))
    # L4 required test classes
    tests = [p for p in paths if re.search(r"(^|/)(test_[^/]*\.py|[^/]*Test\.java)$", p)]
    corpus = ""
    for p in tests:
        try:
            corpus += ctx.p(p).read_text(encoding="utf-8", errors="ignore") + "\n"
        except OSError:
            pass
    stems = [Path(p).stem for p in triggered if not p.endswith(".new")]
    touching = [t for t in tests if any(s in ctx.p(t).read_text(encoding="utf-8", errors="ignore") for s in stems)] if stems else []
    classes = {"restart/reset state": r"restart|reset", "non-trade balance moves": r"deposit|transfer|funding|non[-_ ]trade",
               "API errors": r"URLError|HTTPError|HTTP\s*\d{3}|api[-_ ]error"}
    if not touching:
        checks.append(ck("livepath/L4-tests", WARN, "no changed test file names the changed live module(s)"))
    else:
        text = "".join(ctx.p(t).read_text(encoding="utf-8", errors="ignore") for t in touching)
        missing = [k for k, rx in classes.items() if not re.search(rx, text, re.I)]
        checks.append(ck("livepath/L4-tests", WARN if missing else PASS, ("test class missing: " + ", ".join(missing)) if missing else "restart, non-trade balance move and API error classes present"))
    # L5 Opus review record
    if rec and re.search(r"(?m)^review:\s*\S+", rec):
        checks.append(ck("livepath/L5-review", PASS, "session record carries a review: line"))
    else:
        checks.append(ck("livepath/L5-review", WARN, "no 'review: <session ID>' line in the session record"))
    # L6 AUTO_PAUSE owner and expected end
    if ctx.p("MyTradingSys/execution/AUTO_PAUSE").exists():
        ok = bool(sup and "AUTO_PAUSE" in sup and re.search(r"owner", sup, re.I) and re.search(r"expected end|until", sup, re.I))
        checks.append(ck("livepath/L6-auto-pause", PASS if ok else WARN,
                         "AUTO_PAUSE present; owner and expected end logged" if ok else "AUTO_PAUSE present; SUPERVISOR_LOG lacks owner or expected end (each wake clears or escalates)"))
    else:
        checks.append(ck("livepath/L6-auto-pause", PASS, "no AUTO_PAUSE file"))
    # L7 is a post-close check
    checks.append(ck("livepath/L7-restart", SKIP, "checked at post-close (stage 2.8, P7)"))
    # L8 touch list: runtime state is never part of a change set
    state = [p for p in paths if p.startswith(LIVE_EXEC_PREFIX) and (any(("/" + s) in p for s in ("journal/", "plans/", "halt_history/")) or p.endswith("AUTO_PAUSE"))]
    checks.append(ck("livepath/L8-touch-list", FAIL if state else PASS, ("runtime state in the change set: " + ", ".join(state)) if state else "no journal, plans, halt_history, AUTO_PAUSE in the change set"))
    return checks


# ------------------------------------------------------------------ stage 2.7 release
def release_verdict(rows):
    gating = {"2.3", "2.4", "2.5", "2.6"}
    bad = sorted({r["stage"] for r in rows if r["stage"] in gating and r["status"] in (FAIL, CRASH)})
    warns = sum(1 for r in rows for c in r.get("checks", []) if c["status"] == WARN)
    if bad:
        return "RELEASE: NOT-READY %s" % " ".join(bad)
    if warns:
        return "RELEASE: READY-WITH-WARN %d" % warns
    return "RELEASE: READY"


def stage_release(ctx):
    verdict = release_verdict(ctx.rows)
    changes = change_set(ctx)
    paths = [p for _, p in changes]
    checks = [ck("release/verdict", PASS, verdict, verdict=verdict)]
    ctx.emit(verdict)
    if paths:
        cmd = "git add -- " + " ".join(paths)
        checks.append(ck("release/pathspec", PASS, "explicit pathspec, never add -A or commit -a; operator runs: %s ; then commit with trailer 'MTS-Session: %s'" % (cmd, ctx.session or "<ID>"), pathspec=paths))
    else:
        checks.append(ck("release/pathspec", SKIP, "empty change set (outside the dirty allowlist)"))
    rc, out = ctx.git("status", "--porcelain", "-z", "-uall")
    allow = sorted({norm(e[3:]) for e in out.split("\0") if len(e) > 3 and norm(e[3:]).startswith(DIRTY_ALLOW)})
    checks.append(ck("release/dirty-allowlist", PASS, "allowlisted dirty paths (never in a pathspec): %d" % len(allow)))
    return checks


# ------------------------------------------------------------------ stage 2.8 post-close
def stage_postclose(ctx):
    checks = []
    rc, head = ctx.git("rev-parse", "HEAD")
    if rc != 0 or not head:
        return [ck("postclose/head", SKIP, "no commit in this checkout")]
    # P1 drift
    drift = [p for _, p in change_set(ctx)]
    checks.append(ck("postclose/P1-drift", WARN if drift else PASS,
                     ("uncommitted outside the allowlist (forgotten file, or runtime output not ignored): " + ", ".join(drift[:30])) if drift else "working tree clean outside the allowlist"))
    # P2 artifact, committed bytes
    saved = ctx.profile
    ctx.profile = "postclose"
    try:
        art = stage_artifact(ctx)
    finally:
        ctx.profile = saved
    for c in art:
        c["check"] = c["check"].replace("artifact/", "postclose/P2-artifact/", 1)
    checks += art
    # P3 registry receipts resolve
    rc1, new_txt = ctx.git("show", "HEAD:" + BUGS_REL)
    rc2, old_txt = ctx.git("show", "HEAD~1:" + BUGS_REL)
    if rc1 != 0:
        checks.append(ck("postclose/P3-registry", SKIP, "BUGS.md not committed at HEAD"))
    else:
        new_rows = parse_bugs(new_txt)[0]
        old_rows = parse_bugs(old_txt)[0] if rc2 == 0 else {}
        closed_now = [i for i, r in new_rows.items() if r["status"] in CLOSED_SET and old_rows.get(i, {}).get("status") != r["status"]]
        unresolved = []
        for i in closed_now:
            toks = [t for t in re.findall(r"\b[0-9a-f]{7,40}\b", new_rows[i]["receipt"]) if re.search(r"[a-f]", t) and re.search(r"\d", t)]
            for t in toks:
                crc, _ = ctx.git("cat-file", "-e", t + "^{commit}")
                if crc != 0:
                    unresolved.append("%s receipt %s" % (i, t))
        checks.append(ck("postclose/P3-registry", WARN if unresolved else PASS,
                         ("receipt hash does not resolve: " + ", ".join(unresolved)) if unresolved else "%d row(s) closed in HEAD, every receipt hash resolves" % len(closed_now)))
    # P4 session trailer and record
    rc, body = ctx.git("log", "-n", "1", "--format=%B", "HEAD")
    m = re.search(r"(?m)^MTS-Session:\s*(\S+)", body)
    if not m:
        checks.append(ck("postclose/P4-session", WARN, "HEAD has no 'MTS-Session:' trailer"))
    else:
        rec = ctx.read("%s/%s.md" % (SESSIONS_REL, m.group(1)))
        if rec is None:
            checks.append(ck("postclose/P4-session", WARN, "trailer names %s but no record exists" % m.group(1)))
        else:
            closed = re.search(r"status:\s*closed", rec) is not None
            commits = re.search(r"commits:\s*(\S.*)", rec)
            ok = closed and bool(commits) and "none" not in commits.group(1).lower()
            checks.append(ck("postclose/P4-session", PASS if ok else WARN, "record %s closed with commits populated" % m.group(1) if ok else "record %s: status closed=%s, commits populated=%s" % (m.group(1), closed, bool(commits) and "none" not in commits.group(1).lower())))
    # P5 file index for files added in HEAD
    rc, out = ctx.git("diff-tree", "--root", "--no-commit-id", "--name-status", "-r", "HEAD")
    added = [norm(l.split("\t", 1)[1]) for l in out.splitlines() if l.startswith("A\t")]
    added = [p for p in added if p.startswith("MyTradingSys/") and Path(p).suffix.lower() in INDEXABLE_EXT and not INDEX_SKIP.search("/" + p) and p != FILE_INDEX_REL and not p.startswith(SESSIONS_REL + "/")]
    missing = file_index_rows_missing(ctx, added)
    idx = ctx.read(FILE_INDEX_REL)
    size_note = ""
    if idx is not None:
        sm = re.search(r"# SIZE:\s*~?([\d.]+)KB", idx)
        if sm:
            actual = ctx.p(FILE_INDEX_REL).stat().st_size / 1024.0
            if abs(float(sm.group(1)) - actual) > 1.0:
                size_note = "; SIZE header %sKB vs actual %.1fKB" % (sm.group(1), actual)
    if missing is None:
        checks.append(ck("postclose/P5-file-index", SKIP, "MISSED: %s absent" % FILE_INDEX_REL))
    else:
        checks.append(ck("postclose/P5-file-index", WARN if (missing or size_note) else PASS,
                         (("no row for: " + ", ".join(missing)) if missing else "files added in HEAD all indexed") + size_note))
    # P6 tag
    rc, tag = ctx.git("rev-parse", "--verify", "-q", "last-snapshot")
    if rc != 0 or not tag:
        checks.append(ck("postclose/P6-tag", SKIP, "no last-snapshot tag"))
    elif tag == head:
        checks.append(ck("postclose/P6-tag", PASS, "last-snapshot == HEAD"))
    else:
        rc, n = ctx.git("rev-list", "--count", tag + "..HEAD")
        checks.append(ck("postclose/P6-tag", WARN, "last-snapshot lags HEAD by %s commit(s); the undo function would discard them" % (n or "?")))
    # P7 live-import drift and L7 restart evidence
    procs = list_processes(ctx)
    if procs is None:
        checks.append(ck("postclose/P7-live-import", SKIP, "process list unavailable (needs PowerShell on the desktop)"))
    else:
        stale = []
        for rel in sorted(discover_live(ctx)):
            fp = ctx.p(rel)
            if not fp.is_file():
                continue
            mt = datetime.fromtimestamp(fp.stat().st_mtime, timezone.utc).strftime(TS_FMT)
            for _, created, cmd in procs:
                if Path(rel).name in cmd and created and mt > created:
                    stale.append("%s edited %s after process start %s" % (rel, mt, created))
                    break
        checks.append(ck("postclose/P7-live-import", WARN if stale else PASS, "; ".join(stale) or "no live-imported file newer than its running process (restart is the supervisor's job)"))
    rc, out = ctx.git("diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "HEAD")
    head_paths = [norm(p) for p in out.splitlines()]
    if any(is_live_trigger(p, ()) for p in head_paths):
        sup = ctx.read(SUPERVISOR_LOG_REL) or ""
        ok = re.search(r"restarted\s+\S+\s+\d{4}-\d{2}-\d{2}", sup) is not None
        checks.append(ck("postclose/L7-restart", PASS if ok else WARN, "SUPERVISOR_LOG has a 'restarted <process> <utc>' line" if ok else "HEAD touches the live path; no 'restarted <process> <utc>' line in SUPERVISOR_LOG (only the supervisor restarts)"))
    else:
        checks.append(ck("postclose/L7-restart", SKIP, "HEAD touches no live-path file"))
    # P8 BUILD_REPORT status and age (information)
    br = ctx.read(BUILD_REPORT_REL)
    if br is None:
        checks.append(ck("postclose/P8-build-report", SKIP, "BUILD_REPORT.md absent"))
    else:
        m = re.findall(r"STATUS:\s*(PASS|FAIL)", br)
        age = (ctx.now().timestamp() - ctx.p(BUILD_REPORT_REL).stat().st_mtime) / 3600.0
        checks.append(ck("postclose/P8-build-report", PASS, "STATUS %s, %.1f h old (information only; the RUN receipt is the fresh result)" % (m[-1] if m else "none printed", age)))
    return checks


# ------------------------------------------------------------------ stage 2.9 failure handling
def stage_failures(ctx):
    now = ctx.now().strftime(TS_FMT)
    fails = []
    for r in ctx.rows:
        for c in r.get("checks", []):
            if c["status"] in (WARN, FAIL, CRASH):
                fails.append({"utc": now, "run": ctx.run_id, "stage": r["stage"], "check": c["check"],
                              "severity": c["status"], "detail": c["detail"][:500], "path": str(ctx.day_file("jsonl"))})
        if r["status"] == CRASH and not any(c["status"] == CRASH for c in r.get("checks", [])):
            fails.append({"utc": now, "run": ctx.run_id, "stage": r["stage"], "check": "stage", "severity": CRASH,
                          "detail": r.get("evidence", "")[:500], "path": str(ctx.day_file("jsonl"))})
    if fails:
        warn_path = ctx.out_dir / "cicd_warn.jsonl"
        ctx.append(warn_path, "".join(json.dumps(f, ensure_ascii=True) + "\n" for f in fails))
    n_fail = sum(1 for f in fails if f["severity"] in (FAIL, CRASH))
    n_warn = sum(1 for f in fails if f["severity"] == WARN)
    return [ck("failures/summary", PASS if not fails else WARN,
               "%d FAIL/CRASH, %d WARN this run%s" % (n_fail, n_warn, "; appended to cicd_warn.jsonl" if fails else ""),
               failures=[{"stage": f["stage"], "check": f["check"], "severity": f["severity"]} for f in fails])]


# ------------------------------------------------------------------ runner
STAGES = [
    ("2.1", "intake", stage_intake),
    ("2.2", "precommit", stage_precommit),
    ("2.3", "build", stage_build),
    ("2.4", "contract", stage_contract),
    ("2.5", "artifact", stage_artifact),
    ("2.6", "livepath", stage_livepath),
    ("2.7", "release", stage_release),
    ("2.8", "postclose", stage_postclose),
    ("2.9", "failures", stage_failures),
]
PROFILES = {
    "desktop": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.9"],
    "precommit": ["2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.9"],
    "postclose": ["2.8", "2.9"],
    "cloud": ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "2.9"],
}


def run_stage(ctx, stage_id, name, fn):
    """Run one stage. It never raises: an exception becomes a CRASH row and the run continues."""
    t0 = time.time()
    try:
        checks = fn(ctx)
        status = worst([c["status"] for c in checks])
        bad = [c for c in checks if c["status"] in (WARN, FAIL, CRASH)]
        evidence = "; ".join("%s: %s" % (c["check"], c["detail"][:160]) for c in bad) if bad else "%d check(s), none failing" % len(checks)
    except Exception:
        tb = tail(traceback.format_exc(), 20)
        checks = [ck("%s/crash" % name, CRASH, tb)]
        status, evidence = CRASH, tb
    row = {"utc": ctx.now().strftime(TS_FMT), "run": ctx.run_id, "profile": ctx.profile, "stage": stage_id, "name": name,
           "status": status, "evidence": evidence, "checks": checks, "seconds": round(time.time() - t0, 2)}
    ctx.rows.append(row)
    ctx.append(ctx.day_file("jsonl"), json.dumps(row, ensure_ascii=True) + "\n")
    for c in checks:
        if c["status"] in (WARN, FAIL, CRASH):
            ctx.emit("%s|%s %s/%s: %s" % (c["status"], stage_id, name, c["check"], c["detail"].splitlines()[0][:200] if c["detail"] else ""))
    ctx.emit("STAGE %s %s %s (%ss)" % (stage_id, name, status, row["seconds"]))
    return row


def exit_code(rows):
    st = [r["status"] for r in rows] + [c["status"] for r in rows for c in r.get("checks", [])]
    if FAIL in st or CRASH in st:
        return 2
    return 1 if WARN in st else 0


def run_profile(ctx, only=None):
    wanted = PROFILES[ctx.profile]
    if only:
        wanted = [s for s in wanted if s in only]
    for sid, name, fn in STAGES:
        if sid in wanted:
            run_stage(ctx, sid, name, fn)
    return exit_code(ctx.rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="MTS CI/CD runner: advisory, no stage stops the run")
    ap.add_argument("--profile", choices=sorted(PROFILES), default="desktop")
    ap.add_argument("--session", default="")
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--quick", action="store_true", help="skip mvn and Build-Check")
    ap.add_argument("--only", default="", help="comma list of stage ids, e.g. 2.1,2.4")
    ap.add_argument("--write-baseline", action="store_true", help="re-seed critical_files.json from the working tree")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    ctx = Ctx(repo=a.repo, profile=a.profile, session=a.session, quick=a.quick)
    if a.write_baseline:
        doc = write_baseline(ctx)
        print("baseline written: %s (%d files)" % (CRITICAL_REL, len(doc["files"])))
        return 0
    only = [s.strip() for s in a.only.split(",") if s.strip()]
    code = run_profile(ctx, only or None)
    print("EXIT %d (0 all PASS/SKIP, 1 any WARN, 2 any FAIL/CRASH); the exit code is data, nothing reads it to stop anything" % code)
    return code


if __name__ == "__main__":
    sys.exit(main())
