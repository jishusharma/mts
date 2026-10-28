"""gateway_run.py - run one headless Opus card on the API gateway, in the background, on the station that holds the key.

Why: the operator wants the gateway key used from the background while the app runs a subscription login (GATEWAY_NUC.md).
How: the key and base URL never leave this machine and never reach a prompt, argument, log or the repo:
  key  = ~/.mts_gateway/key (one line, user-only file, outside the repo) if present, else the operator's .reg file;
  base = inferenceGatewayBaseUrl in ~/Documents/claude-gateway/Claude-good.reg.
The child `claude -p` gets them as env only (subscription OAuth vars dropped), runs in its own gw-<card> worktree
marked .gateway_owner, and every output file is redacted. `start` registers ONE one-shot task that deletes itself
when the child exits (SCHEDULING_POLICY.md 4b2 pattern), so the run survives the ssh disconnect.
Usage (on the key station):
  python scripts/dev/gateway_run.py probe [--auth api-key|bearer]
  python scripts/dev/gateway_run.py start --card <id> --run <O1|O2|O3>
  python scripts/dev/gateway_run.py status
  python scripts/dev/gateway_run.py tick     # a watching session calls this every few minutes
Recovery (operator 2026-10-28: "if it hangs, first compact, then resume"): `tick` finds a run whose task is no
longer Running without a `done` (station restart) or whose stream has been silent HANG_MIN (hung; its own child is
killed), then relaunches it: `claude -p /compact --resume <sid>`, then the RESUME_PROMPT on the same session.
At most MAX_RESUMES per run, then `done` says gave-up.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

HOME = Path.home()
KEY_FILE = HOME / ".mts_gateway" / "key"
REG_FILE = HOME / "Documents" / "claude-gateway" / "Claude-good.reg"
RUNS = Path("F:/MTS/gateway_runs")
MODEL = "claude-opus-5-5"
DROP = re.compile(r"^(ANTHROPIC_|CLAUDE_CODE_OAUTH|CLAUDE_CODE_USE_)")
HANG_MIN = 45     # OURS: no stream event for 45 min = hung (long backtests print tool events, not silence)
MAX_RESUMES = 2   # OURS
MAX_QUOTA_WAITS = 6  # OURS: the gateway has its own 5-hour quota (10-28: O1+O2 in parallel spent it in ~1 h)
LIMIT_RE = re.compile(r"reached 100% of your|usage limit|quota|rate.?limit|429|try again later", re.I)
RESUME_PROMPT = (
    "You were interrupted (station restart or hang) and your context was compacted. Same rules as before. "
    "Check git status, the files you changed and git cherry, then finish OPUS_RUNS.md {run} from where you stopped; "
    "never redo shipped work."
)

CHILD_PROMPT = (
    "You run on the MTS gateway, headless. Public tracked files only (GATEWAY_NUC.md rules 1-7): never read .secrets, "
    ".env, keys, ~/.mts_gateway, runtime data, the live tree or F:/ backups, and never print environment variables. "
    "You are already in your own worktree; skip sync.py start. Run MyTradingSys/system/handover/OPUS_RUNS.md {run} in full. "
    "Skip get_usage: write 'gateway: no meter'. Commit body adds 'Model: {model} via gateway'. "
    "Never ask; take the conservative default and log DECISION (OURS)."
)


def read_reg(path: Path) -> dict:
    raw = path.read_bytes()
    text = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    out = {}
    for line in text.splitlines():
        m = re.match(r'^"([^"]+)"="((?:[^"\\]|\\.)*)"', line.strip())
        if m:
            out[m.group(1)] = m.group(2).replace('\\"', '"').replace("\\\\", "\\")
    return out


def load_secret(key_file: Path = KEY_FILE, reg_file: Path = REG_FILE) -> tuple:
    reg = read_reg(reg_file) if reg_file.exists() else {}
    base = reg.get("inferenceGatewayBaseUrl", "")
    key = key_file.read_text(encoding="utf-8").strip() if key_file.exists() else reg.get("inferenceGatewayApiKey", "")
    if not base or not key:
        raise SystemExit("gateway_run: no base URL or key on this machine (names checked only)")
    return base, key


def child_env(base: str, key: str, auth: str, environ=None) -> dict:
    env = {k: v for k, v in (environ if environ is not None else os.environ).items() if not DROP.match(k)}
    env["ANTHROPIC_BASE_URL"] = base
    env["ANTHROPIC_AUTH_TOKEN" if auth == "bearer" else "ANTHROPIC_API_KEY"] = key
    env["MTS_GATEWAY"] = "1"
    return env


def redact(text: str, secret: str) -> str:
    return text.replace(secret, "<redacted>") if secret else text


def last_result(stdout: str):
    """The result object of a json run, or the last type=result line of a stream-json run."""
    try:
        return json.loads(stdout)
    except ValueError:
        pass
    for line in reversed(stdout.splitlines()):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if isinstance(d, dict) and d.get("type") == "result":
            return d
    return None


def summary(stdout: str, key: str) -> dict:
    d = last_result(stdout)
    if not isinstance(d, dict):
        return {"is_error": True, "result": redact(stdout[-400:], key)}
    res = str(d.get("result", ""))
    # the CLI reports is_error false on an auth failure; the text is the only signal
    limit = bool(LIMIT_RE.search(res))
    bad = bool(d.get("is_error")) or limit or bool(re.search(r"Invalid API key|API Error|authentication_error|401|403", res))
    m = re.search(r"reset in (\d+) (minute|hour)", res)
    wait = (int(m.group(1)) * (60 if m.group(2) == "hour" else 1)) if m else (60 if limit else 0)
    return {"is_error": bad, "limit_wait_min": wait if limit else None, "num_turns": d.get("num_turns"),
            "models": sorted((d.get("modelUsage") or {}).keys()), "result": redact(str(d.get("result", ""))[-400:], key)}


def claude_exe() -> str:
    p = HOME / ".local" / "bin" / "claude.exe"
    return str(p) if p.exists() else "claude"


def probe(auth: str) -> int:
    base, key = load_secret()
    r = subprocess.run([claude_exe(), "-p", "Reply with the single word OK.", "--model", MODEL, "--output-format", "json"],
                       env=child_env(base, key, auth), capture_output=True, text=True, timeout=180)
    s = summary(r.stdout, key)
    s["auth"], s["exit"], s["stderr"] = auth, r.returncode, redact(r.stderr[-300:], key)
    print(json.dumps(s))
    return 0 if r.returncode == 0 and not s["is_error"] else 1


def repo_root(cwd: Path = None) -> Path:
    # old git (the NUC) has no --path-format; --git-common-dir may be relative to cwd
    cwd = Path(cwd or Path.cwd())
    out = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=cwd,
                         capture_output=True, text=True, check=True).stdout.strip()
    return (cwd / out).resolve().parent


def task_name(card: str) -> str:
    return "MTS-GW-" + re.sub(r"[^A-Za-z0-9-]", "-", card)[:40]


def start(card: str, run: str, auth: str) -> int:
    load_secret()  # fail early, names only
    repo = repo_root()
    wt = repo / ".claude" / "worktrees" / f"gw-{card}"
    subprocess.run(["git", "-C", str(repo), "fetch", "-q", "origin", "fast-track"], check=True)
    if not wt.exists():
        subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", str(wt), "-b", f"gateway/{card}", "origin/fast-track"], check=True)
    (wt / ".gateway_owner").write_text(f"gateway_run {card}\n", encoding="utf-8", newline="\n")
    d = RUNS / card
    d.mkdir(parents=True, exist_ok=True)
    for f in ("done", "started", "out.json", "out.jsonl", "err.log", "summary.json", "killed"):
        (d / f).unlink(missing_ok=True)
    (d / "sid").write_text(str(uuid.uuid4()), encoding="utf-8", newline="\n")
    for f in ("resumes", "pid"):
        (d / f).unlink(missing_ok=True)
    launch(card, run, auth, wt, resume=False)
    print(f"started {card} ({run}) task={task_name(card)} tree={wt} logs={d}")
    return 0


def launch(card: str, run: str, auth: str, wt: Path, resume: bool) -> None:
    d = RUNS / card
    (d / "meta.json").write_text(json.dumps({"run": run, "auth": auth, "cwd": str(wt)}), encoding="utf-8", newline="\n")
    me = Path(__file__).resolve()
    # schtasks /TR caps at 261 chars: the task runs a short run.cmd holding the long line
    cmd = d / "run.cmd"
    line = f'@"{sys.executable}" "{me}" child --card {card} --run {run} --auth {auth} --cwd "{wt}"' + (" --resume" if resume else "")
    cmd.write_text(line + chr(13) + chr(10), encoding="utf-8", newline="")
    tn = task_name(card)
    subprocess.run(["schtasks", "/Create", "/TN", tn, "/SC", "ONCE", "/ST", "00:00", "/TR", f'"{cmd}"', "/IT", "/F"],
                   check=True, capture_output=True)
    subprocess.run(["schtasks", "/Run", "/TN", tn], check=True, capture_output=True)
    (d / "started").write_text(tn + chr(10), encoding="utf-8", newline=chr(10))


def claude_args(prompt: str, sid: str, resume: bool) -> list:
    """First run pins --session-id so a resume can find it; runs started before that use --continue (own worktree)."""
    a = [claude_exe(), "-p", prompt, "--model", MODEL, "--permission-mode", "bypassPermissions",
         "--output-format", "stream-json", "--verbose"]
    if resume:
        return a + (["--resume", sid] if sid else ["--continue"])
    return a + (["--session-id", sid] if sid else [])


def child(card: str, run: str, auth: str, cwd: str, resume: bool = False) -> int:
    d = RUNS / card
    rc, key = 1, ""
    sid = (d / "sid").read_text().strip() if (d / "sid").exists() else ""
    out = d / "out.jsonl"
    (d / "killed").unlink(missing_ok=True)  # this is the relaunch a tick asked for
    try:
        base, key = load_secret()
        env = child_env(base, key, auth)
        if resume:  # operator order: compact first, then resume on the same session
            subprocess.run(claude_args("/compact", sid, True), cwd=cwd, env=env, capture_output=True, text=True, timeout=1800)
        prompt = (RESUME_PROMPT if resume else CHILD_PROMPT).format(run=run, model=MODEL)
        with open(out, "a", encoding="utf-8", newline="\n") as fo, open(d / "err.log", "a", encoding="utf-8") as fe:
            p = subprocess.Popen(claude_args(prompt, sid, resume), cwd=cwd, env=env, stdout=fo, stderr=fe, text=True)
            (d / "pid").write_text(str(p.pid), encoding="utf-8", newline="\n")
            try:
                rc = p.wait(timeout=6 * 3600)
            except subprocess.TimeoutExpired:
                subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
                rc = 124
        text = redact(out.read_text(encoding="utf-8", errors="replace"), key)
        out.write_text(text, encoding="utf-8", newline="\n")
        (d / "summary.json").write_text(json.dumps(summary(text, key)), encoding="utf-8", newline="\n")
    except Exception as e:  # the task must still delete itself
        with open(d / "err.log", "a", encoding="utf-8") as fe:
            fe.write(redact(repr(e), key) + "\n")
    finally:
        if not (d / "killed").exists():  # a tick that killed a hung child relaunches it; no done marker then
            (d / "done").write_text(f"exit={rc}\n", encoding="utf-8", newline="\n")
            subprocess.run(["schtasks", "/Delete", "/TN", task_name(card), "/F"], capture_output=True)
    return rc


def task_running(card: str) -> bool:
    r = subprocess.run(["schtasks", "/Query", "/TN", task_name(card), "/FO", "CSV", "/NH"], capture_output=True, text=True)
    return r.returncode == 0 and "Running" in r.stdout


def last_activity(d: Path) -> float:
    return max([(d / f).stat().st_mtime for f in ("out.jsonl", "out.json", "started") if (d / f).exists()] or [0])


def verdict(has_done: bool, started: bool, running: bool, idle_min: float, streams: bool, resumes: int) -> str:
    """What tick does with one run: done | idle | running | resume | kill-resume | gave-up."""
    if has_done:
        return "done"
    if not started:
        return "idle"
    stuck = not running or (streams and idle_min >= HANG_MIN)
    if not stuck:
        return "running"
    if resumes >= MAX_RESUMES:
        return "gave-up"
    return "resume" if not running else "kill-resume"


def quota_pass(now: float) -> set:
    """Runs that ended on the gateway quota: clear their done marker once the reset time is past and no other run
    is going (one run at a time after a quota hit, DECISION OURS), so the normal resume below relaunches them.
    Returns the cards still waiting."""
    dirs = sorted(RUNS.glob("*")) if RUNS.exists() else []
    waiting, busy = set(), any((d / "started").exists() and not (d / "done").exists() for d in dirs)
    for d in dirs:
        if not ((d / "done").exists() and (d / "summary.json").exists()):
            continue
        s = json.loads((d / "summary.json").read_text())
        if s.get("limit_wait_min") is None:
            continue
        waits = int((d / "quota_waits").read_text()) if (d / "quota_waits").exists() else 0
        if waits >= MAX_QUOTA_WAITS:
            continue
        due = (d / "done").stat().st_mtime + (s["limit_wait_min"] + 5) * 60
        if now < due or busy:
            waiting.add(d.name)
            continue
        (d / "quota_waits").write_text(str(waits + 1), encoding="utf-8", newline=chr(10))
        (d / "done").unlink()
        (d / "summary.json").unlink()
        busy = True
    return waiting


def tick() -> int:
    """One pass: report every run, relaunch dead or hung ones (compact, then resume). Prints one line per run."""
    waiting = quota_pass(time.time())
    for d in sorted(RUNS.glob("*")) if RUNS.exists() else []:
        card = d.name
        if card in waiting:
            print(f"{card}: quota-wait (gateway 5-hour quota; resumes after reset, one run at a time)")
            continue
        resumes = int((d / "resumes").read_text()) if (d / "resumes").exists() else 0
        idle = (time.time() - last_activity(d)) / 60
        v = verdict((d / "done").exists(), (d / "started").exists(), task_running(card), idle,
                    (d / "out.jsonl").exists(), resumes)
        if v in ("resume", "kill-resume"):
            meta = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
            run = meta.get("run") or {"opus-o1-self-heal-loop": "O1", "opus-o2-r6-review": "O2", "opus-o3-overhead-cut": "O3"}.get(card)
            wt = Path(meta.get("cwd") or repo_root() / ".claude" / "worktrees" / f"gw-{card}")
            if not run or not wt.exists():
                v = "gave-up"
            else:
                if v == "kill-resume" and (d / "pid").exists():
                    (d / "killed").write_text("hung\n", encoding="utf-8")
                    subprocess.run(["taskkill", "/PID", (d / "pid").read_text().strip(), "/T", "/F"], capture_output=True)
                    for _ in range(12):  # the wrapper sees `killed`, skips done, and exits
                        if not task_running(card):
                            break
                        time.sleep(5)
                (d / "resumes").write_text(str(resumes + 1), encoding="utf-8", newline="\n")
                launch(card, run, meta.get("auth", "api-key"), wt, resume=True)
        if v == "gave-up" and not (d / "done").exists():
            (d / "done").write_text("exit=gave-up\n", encoding="utf-8", newline="\n")
        s = (d / "summary.json").read_text()[:300] if (d / "summary.json").exists() else ""
        if v in ("done", "gave-up"):
            bad = json.loads(s).get("is_error", True) if s.startswith("{") else True
            v = "done " + (d / "done").read_text().strip() + (" FAIL" if bad else " OK")
        print(f"{card}: {v} idle={idle:.0f}m resumes={resumes} {s}")
    return 0


def status() -> int:
    for d in sorted(RUNS.glob("*")) if RUNS.exists() else []:
        done = (d / "done").read_text().strip() if (d / "done").exists() else ("running" if (d / "started").exists() else "not started")
        s = (d / "summary.json").read_text() if (d / "summary.json").exists() else ""
        print(f"{d.name}: {done} {s[:600]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["probe", "start", "child", "status", "tick"])
    ap.add_argument("--card")
    ap.add_argument("--run")
    ap.add_argument("--cwd")
    ap.add_argument("--auth", choices=["api-key", "bearer"], default="api-key")
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    if a.cmd == "probe":
        return probe(a.auth)
    if a.cmd == "start":
        return start(a.card, a.run, a.auth)
    if a.cmd == "child":
        return child(a.card, a.run, a.auth, a.cwd, a.resume)
    if a.cmd == "tick":
        return tick()
    return status()


if __name__ == "__main__":
    sys.exit(main())
