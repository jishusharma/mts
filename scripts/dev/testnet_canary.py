"""Read-only liveness + new-code canary for the live testnet stack.

Tells "no signals" apart from "nothing running", and flags committed code that needs gating / a restart.
Pure stdlib. Never imports anything from MyTradingSys/execution/, never opens .secrets/ or .env, never reads the
contents of HALT / HALT_DAILY_LOSS / AUTO_PAUSE (existence only), never prints ids, keys or balances.

Checks (each OK / WARN / RED, overall verdict = worst):
  1 processes   auto_trader, daily_loss_monitor, live_runner_cli, loop-supervisor, start-trading-day, java -> RED if
                missing; position_manager reported only (expected only while a position is open). Query failure -> RED.
  2 freshness   loop_state.json ts_utc (>5 min RED), supervisor_log / apparatus_log mtime (>10 min RED),
                auto_trades.jsonl last row ts (>6 h WARN), runtime/alerts/*.jsonl mtimes (report only)
  3 tom alerts  runtime_data/alert_counter.txt vs auto_trader_state.json tom_last_alert_no (gap > 2 RED)
  4 brakes      HALT / HALT_DAILY_LOSS / AUTO_PAUSE present -> WARN
  4b journal    every open plan (auto_trades.jsonl trade_attempt entered, no later trade_closed; same rule as
                auto_trader.open_plans_from_log) needs execution/journal/<plan_id>.jsonl -> RED when missing
                (counts only, no ids); auto_trades.jsonl unreadable -> WARN
  5 new code    commits since runtime_data/canary_state.json last_commit touching live-path dirs; optional gates;
                commit newer than the loading process start -> WARN RESTART NEEDED (supervisor only)

Output: first stdout line `CANARY <GREEN|WARN|RED> <ISO UTC now> <reasons>`, plus a markdown block appended to
MyTradingSys/research/testnet_status/CANARY_<YYYY-MM-DD>.md.  Exit code 0 GREEN, 1 WARN, 2 RED.

Usage (repo root): python scripts/dev/testnet_canary.py [--repo .] [--now ISO] [--no-proc] [--proc-json F]
                   [--run-gates] [--write-state] [--out-dir D]
"""
import nowin  # B190: scheduled run (hidden console) must not flash git windows
nowin.install()
import argparse
import json
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

TS_FMT = "%Y-%m-%dT%H:%M:%SZ"
BRAKE_FILES = ("HALT", "HALT_DAILY_LOSS", "AUTO_PAUSE")
RANK = {"OK": 0, "SKIPPED": 0, "WARN": 1, "RED": 2}
LOOP_MAX = timedelta(minutes=5)
LOG_MAX = timedelta(minutes=10)
TRADES_WARN = timedelta(hours=6)
ALERT_GAP_MAX = 2

def _py(name):
    """Python role: `name.py` as a script OR `-m pkg.name` as a module (mts.ps1 starts auto_trader with -m).
    The name must end at whitespace, a quote or end of line, so auto_trader_state.json / auto_trader.log don't match."""
    return re.compile(r"(?<![\w-])" + re.escape(name) + r"(?:\.py)?(?=[\s\"']|$)")


# role, CommandLine substring or compiled regex (None = java rule), required
ROLES = [
    ("auto_trader", _py("auto_trader"), True),
    ("position_manager", _py("position_manager"), False),
    ("daily_loss_monitor", _py("daily_loss_monitor"), True),
    ("live_runner_cli", _py("live_runner_cli"), True),
    ("loop-supervisor", "loop-supervisor.ps1", True),
    ("start-trading-day", "start-trading-day.ps1", True),
    ("java", None, True),
]
# commit-path group -> roles that load it
LOADERS = {
    "execution": ("auto_trader", "daily_loss_monitor", "position_manager", "live_runner_cli"),
    "alerts": ("live_runner_cli", "auto_trader"),
    "java": ("java",),
}
_KW = re.compile(r"(?i)\b(api[_-]?key|client[_-]?id|client[_-]?secret|secret|token|password|passwd|authorization|"
                 r"bearer|key)\b(\s*[:=]\s*|\s+)\S+")
_ORDER = re.compile(r"\b[A-Z]{2,}-\d{6,}\b")
_PLAN = re.compile(r"\b[A-Z]-[A-Za-z]+-\d{4}-\d{4}(?:-\d+)?\b")
_DIGITS = re.compile(r"\b\d{8,}\b")
_TOKEN = re.compile(r"(?=[A-Za-z0-9_\-]*\d)(?=[A-Za-z0-9_\-]*[A-Za-z])\b[A-Za-z0-9_\-]{20,}\b")


def scrub(text, limit=200):
    s = str(text)
    s = _KW.sub("[redacted]", s)
    for rx in (_ORDER, _PLAN, _DIGITS, _TOKEN):
        s = rx.sub("[id]", s)
    return " ".join(s.split())[:limit]


def parse_iso(s):
    """Parse many ISO-8601 spellings (Z, offsets, 7-digit fractions) to aware UTC; None on failure."""
    if s is None:
        return None
    t = str(s).strip().replace("Z", "+00:00")
    t = re.sub(r"(\.\d{6})\d+", r"\1", t)
    try:
        d = datetime.fromisoformat(t)
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def fmt(d):
    return d.strftime(TS_FMT)


def age_str(delta):
    s = int(delta.total_seconds())
    if s < 0:
        return "future %ds" % -s
    if s < 3600:
        return "%dm%02ds" % (s // 60, s % 60)
    return "%dh%02dm" % (s // 3600, (s % 3600) // 60)


class Result:
    def __init__(self):
        self.rows = []

    def add(self, check, status, detail):
        self.rows.append((check, status, scrub(detail, 240)))

    def verdict(self):
        worst = max((RANK[r[1]] for r in self.rows), default=0)
        return {0: "GREEN", 1: "WARN", 2: "RED"}[worst]


# ---------------------------------------------------------------- 1 processes
def parse_cim_date(v):
    if isinstance(v, dict):
        v = v.get("value") or v.get("DateTime")
    if v is None:
        return None
    m = re.search(r"/Date\((-?\d+)", str(v))
    if m:
        return datetime.fromtimestamp(int(m.group(1)) / 1000.0, tz=timezone.utc)
    return parse_iso(v)


def query_processes():
    cmd = ["powershell", "-NoProfile", "-Command",
           "Get-CimInstance Win32_Process | Select ProcessId,CreationDate,CommandLine | ConvertTo-Json"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if p.returncode != 0:
        raise RuntimeError("rc=%s" % p.returncode)
    return p.stdout


def load_procs(raw):
    data = json.loads(raw)
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list) or not data:
        raise ValueError("empty process list")
    return data


def check_processes(res, repo, args):
    if args.no_proc:
        res.add("processes", "SKIPPED", "--no-proc")
        return {}
    try:
        if args.proc_json:
            raw = pathlib.Path(args.proc_json).read_text(encoding="utf-8-sig")
        else:
            raw = query_processes()
        procs = load_procs(raw)
    except Exception as e:  # fail closed
        res.add("processes", "RED", "process query failed (%s)" % type(e).__name__)
        return {}
    repo_l = {str(repo).lower(), str(repo).lower().replace("\\", "/")}
    found = {}
    for pr in procs:
        cl = (pr.get("CommandLine") or "") if isinstance(pr, dict) else ""
        if not cl or "testnet_canary" in cl or "Get-CimInstance" in cl:
            continue
        cll = cl.lower()
        start = parse_cim_date(pr.get("CreationDate"))
        for role, sub, _req in ROLES:
            if isinstance(sub, re.Pattern):
                hit = bool(sub.search(cll))
            elif sub is not None:
                hit = sub.lower() in cll
            else:
                hit = "java" in cll and ("mytradingsys" in cll or any(r in cll for r in repo_l))
            if hit:
                found.setdefault(role, []).append(start)
    starts = {}
    for role, sub, req in ROLES:
        lst = found.get(role, [])
        valid = [s for s in lst if s]
        oldest = min(valid) if valid else None
        starts[role] = oldest
        when = " oldest start %s" % fmt(oldest) if oldest else ""
        if lst:
            res.add("proc:" + role, "OK", "%d running%s" % (len(lst), when))
        elif req:
            res.add("proc:" + role, "RED", "not running")
        else:
            res.add("proc:" + role, "OK", "0 running (only expected while a position is open)")
    return starts


# ---------------------------------------------------------------- 2 freshness
def read_json(path):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def mtime(path):
    try:
        return datetime.fromtimestamp(pathlib.Path(path).stat().st_mtime, tz=timezone.utc)
    except OSError:
        return None


def check_freshness(res, repo, now):
    rd = repo / "runtime_data"
    ls = read_json(rd / "loop_state.json")
    ts = parse_iso(ls.get("ts_utc")) if isinstance(ls, dict) else None
    if ts is None:
        res.add("loop_state", "RED", "runtime_data/loop_state.json missing or no parseable ts_utc")
    else:
        a = now - ts
        res.add("loop_state", "RED" if a > LOOP_MAX else "OK", "ts_utc age %s (max 5m)" % age_str(a))
    for name in ("supervisor_log.txt", "apparatus_log.txt"):
        m = mtime(rd / name)
        if m is None:
            res.add(name, "RED", "missing")
        else:
            a = now - m
            res.add(name, "RED" if a > LOG_MAX else "OK", "mtime age %s (max 10m)" % age_str(a))
    f = repo / "MyTradingSys" / "execution" / "auto_trades.jsonl"
    last = None
    try:
        with open(f, "rb") as fh:
            fh.seek(0, 2)
            size = fh.tell()
            fh.seek(max(0, size - 2000000))
            lines = fh.read().decode("utf-8", "replace").splitlines()
        for ln in reversed(lines):
            try:
                row = json.loads(ln)
            except ValueError:
                continue
            t = parse_iso(row.get("ts")) if isinstance(row, dict) else None
            if t:
                last = t
                break
        if last is None:
            res.add("auto_trades", "WARN", "no parseable ts row")
    except OSError:
        res.add("auto_trades", "WARN", "auto_trades.jsonl not found")
    if last:
        a = now - last
        res.add("auto_trades", "WARN" if a > TRADES_WARN else "OK",
                "last row %s age %s (signals can be quiet; WARN >6h)" % (fmt(last), age_str(a)))
    al = sorted((repo / "MyTradingSys" / "runtime" / "alerts").glob("*.jsonl"))
    parts = []
    for p in al:
        m = mtime(p)
        if m:
            parts.append("%s %s" % (p.stem, age_str(now - m)))
    res.add("alerts_files", "OK", "mtime ages: " + (", ".join(parts) if parts else "none found"))


# ---------------------------------------------------------------- 3 tom alerts
def check_alert_counter(res, repo):
    try:
        counter = int((repo / "runtime_data" / "alert_counter.txt").read_text(encoding="utf-8-sig").strip())
    except (OSError, ValueError):
        res.add("tom_alerts", "WARN", "alert_counter.txt missing/unparseable")
        return
    st = read_json(repo / "MyTradingSys" / "execution" / "auto_trader_state.json")
    try:
        consumed = int(st["tom_last_alert_no"])
    except (TypeError, KeyError, ValueError):
        res.add("tom_alerts", "WARN", "auto_trader_state.json tom_last_alert_no missing")
        return
    gap = counter - consumed
    if gap > ALERT_GAP_MAX:
        res.add("tom_alerts", "RED", "%d Tom alerts not seen by auto_trader (counter %d, consumed %d)"
                % (gap, counter, consumed))
    else:
        res.add("tom_alerts", "OK", "gap %d (counter %d, consumed %d)" % (gap, counter, consumed))


# ---------------------------------------------------------------- 4 brakes
def check_brakes(res, repo):
    present = [n for n in BRAKE_FILES if (repo / "MyTradingSys" / "execution" / n).exists()]  # existence only
    if present:
        res.add("brakes", "WARN", "present: " + ", ".join(present))
    else:
        res.add("brakes", "OK", "none present")


# ---------------------------------------------------------------- 4b journal files of open plans
def check_journal(res, repo):
    ex = repo / "MyTradingSys" / "execution"
    try:
        lines = (ex / "auto_trades.jsonl").read_text(encoding="utf-8").splitlines()
    except OSError:
        res.add("journal", "WARN", "auto_trades.jsonl unreadable: open plans not checked")
        return
    entered, closed = set(), set()
    for ln in lines:
        try:
            e = json.loads(ln)
        except ValueError:
            continue
        if not isinstance(e, dict):
            continue
        pid = e.get("plan_id")
        if not pid:
            continue
        if e.get("event") == "trade_attempt" and e.get("outcome") == "entered":
            entered.add(pid)
            closed.discard(pid)
        elif e.get("event") == "trade_closed":
            closed.add(pid)
    open_ids = sorted(entered - closed)
    missing = [p for p in open_ids if not (ex / "journal" / (str(p) + ".jsonl")).is_file()]
    if missing:
        res.add("journal", "RED", "%d of %d open plans have no journal file" % (len(missing), len(open_ids)))
    else:
        res.add("journal", "OK", "%d open, all journaled" % len(open_ids))


# ---------------------------------------------------------------- 5 new code
def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo)] + list(a), capture_output=True, text=True, timeout=60)


def find_java_tree(repo):
    """Most-populated src/main/java tree among tracked *.java files; None -> caller uses the global '*.java'."""
    files = [x for x in git(repo, "ls-files", "*.java").stdout.splitlines() if x]
    groups = {}
    for f in files:
        if f.startswith("src/main/java/"):
            key = "src/main/java"
        elif "/src/main/java/" in f:
            key = f.split("/src/main/java/")[0] + "/src/main/java"
        else:
            continue
        groups[key] = groups.get(key, 0) + 1
    return max(groups, key=groups.get) if groups else None


def classify(files, java_tree):
    kinds = set()
    for f in files:
        if f.startswith("MyTradingSys/execution/"):
            kinds.add("execution")
        if f.startswith("MyTradingSys/backtest/layers/alerts/"):
            kinds.add("alerts")
        if f.endswith(".java") and (java_tree is None or f.startswith(java_tree + "/")):
            kinds.add("java")
    return kinds


def run_gate(repo, cmd):
    try:
        p = subprocess.run(cmd, cwd=str(repo), capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return False, "timeout 900s"
    lines = [x for x in (p.stdout + "\n" + p.stderr).splitlines() if x.strip()]
    return p.returncode == 0, (lines[-1].strip() if lines else "no output") + " (rc=%d)" % p.returncode


def check_new_code(res, repo, args, starts):
    state_path = repo / "runtime_data" / "canary_state.json"
    st = read_json(state_path)
    last = st.get("last_commit") if isinstance(st, dict) else None
    if git(repo, "rev-parse", "--git-dir").returncode != 0:
        res.add("new_code", "WARN", "not a git repo")
        return
    head = git(repo, "rev-parse", "HEAD").stdout.strip()
    java_tree = find_java_tree(repo)
    paths = ["MyTradingSys/execution/", "MyTradingSys/backtest/layers/alerts/", "MyTradingSys/backtest/layers/fabio/",
             "MyTradingSys/backtest/", java_tree if java_tree else "*.java"]
    note = ""
    if last and git(repo, "cat-file", "-e", last + "^{commit}").returncode == 0:
        base = [last + "..HEAD"]
    else:
        base = ["-20"]
        note = " (first run / unknown last_commit: last 20)"
    p = git(repo, "log", "--format=@@%H\t%cI\t%s", "--name-only", *base, "--", *paths)
    if p.returncode != 0:
        res.add("new_code", "WARN", "git log failed")
        return
    commits = []
    cur = None
    for ln in p.stdout.splitlines():
        if ln.startswith("@@"):
            h, ci, subj = (ln[2:].split("\t", 2) + ["", ""])[:3]
            cur = {"sha": h[:10], "when": parse_iso(ci), "subj": subj, "files": []}
            commits.append(cur)
        elif ln.strip() and cur is not None:
            cur["files"].append(ln.strip())
    state_ok = True
    if not commits:
        res.add("new_code", "OK", "no new live-path commits%s" % note)
    else:
        res.add("new_code", "OK", "%d live-path commit(s)%s: %s" % (
            len(commits), note, "; ".join("%s %s" % (c["sha"], scrub(c["subj"], 50)) for c in commits[:5])))
        if args.run_gates:
            ok1, d1 = run_gate(repo, [sys.executable, "scripts/dev/run_all_tests.py", "--quick"])
            ok2, d2 = run_gate(repo, [sys.executable, "-m", "pytest",
                                      "MyTradingSys/backtest/layers/fabio/v3/tests", "-q"])
            res.add("gate:run_all_tests", "OK" if ok1 else "RED", ("PASS: " if ok1 else "FAIL: ") + d1)
            res.add("gate:fabio_v3", "OK" if ok2 else "RED", ("PASS: " if ok2 else "FAIL: ") + d2)
            state_ok = ok1 and ok2
        need = {}
        for c in commits:
            for kind in classify(c["files"], java_tree):
                for role in LOADERS[kind]:
                    t0 = starts.get(role)
                    if t0 and c["when"] and c["when"] > t0:
                        need.setdefault(role, c["sha"])
        for role, sha in sorted(need.items()):
            res.add("restart:" + role, "WARN",
                    "RESTART NEEDED (supervisor only): %s (commit %s newer than process start)" % (role, sha))
    if args.write_state:
        if state_ok:
            state_path.parent.mkdir(parents=True, exist_ok=True)
            with open(state_path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump({"last_commit": head}, fh)
                fh.write("\n")
        else:
            res.add("state", "WARN", "gates failed: canary_state.json not updated")


# ---------------------------------------------------------------- output
def render(res, now, verdict):
    out = ["## %s %s" % (fmt(now), verdict), "", "| check | status | detail |", "|---|---|---|"]
    for c, s, d in res.rows:
        out.append("| %s | %s | %s |" % (c, s, d.replace("|", "/")))
    return "\n".join(out) + "\n\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=str(pathlib.Path(__file__).resolve().parents[2]))
    ap.add_argument("--now")
    ap.add_argument("--no-proc", action="store_true")
    ap.add_argument("--proc-json")
    ap.add_argument("--run-gates", action="store_true")
    ap.add_argument("--write-state", action="store_true")
    ap.add_argument("--out-dir")
    args = ap.parse_args(argv)
    repo = pathlib.Path(args.repo).resolve()
    now = parse_iso(args.now) if args.now else datetime.now(timezone.utc)
    if now is None:
        print("bad --now")
        return 2
    out_dir = pathlib.Path(args.out_dir) if args.out_dir else repo / "MyTradingSys" / "research" / "testnet_status"
    res = Result()
    starts = check_processes(res, repo, args)
    check_freshness(res, repo, now)
    check_alert_counter(res, repo)
    check_brakes(res, repo)
    check_journal(res, repo)
    try:
        check_new_code(res, repo, args, starts)
    except Exception as e:
        res.add("new_code", "WARN", "check failed (%s)" % type(e).__name__)
    verdict = res.verdict()
    reasons = "; ".join("%s: %s" % (c, d) for c, s, d in res.rows if s in ("WARN", "RED"))
    print("CANARY %s %s %s" % (verdict, fmt(now), scrub(reasons, 300) if reasons else "all checks OK"))
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / ("CANARY_%s.md" % now.strftime("%Y-%m-%d")), "a", encoding="utf-8", newline="\n") as fh:
        fh.write(render(res, now, verdict))
    return {"GREEN": 0, "WARN": 1, "RED": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
