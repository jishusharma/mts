"""mts_run.py - the unattended worker runner (RUN_MODEL.md phase 2): a Python loop (0 tokens) that picks a card, claims it, runs one
headless `claude -p` worker in its own worktree, and logs the run. No scheduler: the operator starts it in a foreground shell.

Usage (run from any non-live MTS tree; MTS_LOGIN names the login, default "default"):
  python scripts/dev/mts_run.py once [--card ID] [--dry-run] [--login L] [--timeout S]   # one card, one worker, then exit
  python scripts/dev/mts_run.py loop --hours H [--max-parallel 1] [--login L]            # repeat while time and pace allow;
                                                  # stops on a STOP/HOLD in ANNOUNCEMENTS.md, 3 failures in a row, or when H hours end
                                                  # (empty queue: sleeps 10 min and re-checks)
  python scripts/dev/mts_run.py calibrate --login L --used PCT [--reset ISO]              # operator's app reading (% of week used)
  python scripts/dev/mts_run.py pace --login L                                            # run / slow / stop (RUN_MODEL section 4)
  python scripts/dev/mts_run.py ledger [--week]                                           # per login/model summary
Ledger: runtime_data/mts_run/ledger.jsonl (gitignored). A finished card stays UNVERIFIED (ledger status) until a checker or test gate passes.
Models: lane HAIKU or card model=haiku -> haiku; lane OPUS -> opus only with weight CRUCIAL/CRITICAL (or crucial) AND approved_by, else sonnet.
Units are input-price equivalents: input 1, cache-write 1.25, cache-read 0.1, output 5 (WORKERS.md).
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

RUN_DIR = REPO / "runtime_data" / "mts_run"
LEDGER = RUN_DIR / "ledger.jsonl"
CALIB = RUN_DIR / "calibration.json"
WINGET_CLAUDE = r"C:\Users\e-ngineers\AppData\Local\Microsoft\WinGet\Packages\Anthropic.ClaudeCode_Microsoft.Winget.Source_8wekyb3d8bbwe\claude.exe"
KEEP_ENV = {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH"}
TOOLS = "Bash,Read,Edit,Write,Grep,Glob"
DEFAULT_TURNS = 30
DEFAULT_TIMEOUT = 3600
EMPTY_SLEEP = 600
MAX_FAILS = 3
STOP_PCT = 90.0
WEEK_S = 7 * 86400
ROLE_FILES = {"Builder": "builder.md", "Lab_Guy": "lab_guy.md", "MTS_Doctor": "mts_doctor.md", "Pipeliner": "pipeliner.md"}
HOLD_ID = re.compile(r"^### (A-\d{8}-\d+) (?:HOLD|STOP)(?!.*(?:LIFTED|RETIRED|CLOSED))", re.M)


def utcnow():
    return datetime.now(timezone.utc)


# ---------- command construction ----------
def find_claude():
    return shutil.which("claude") or (WINGET_CLAUDE if os.path.exists(WINGET_CLAUDE) else "claude")


def scrub_env(env=None):
    """Copy of env without ANTHROPIC_* and CLAUDE* variables (the worker logs in by its own stored login), except the spawn-depth guard."""
    src = os.environ if env is None else env
    return {k: v for k, v in src.items()
            if k in KEEP_ENV or not (k.upper().startswith("ANTHROPIC_") or k.upper().startswith("CLAUDE"))}


def is_crucial(card):
    return card.get("weight") in ("CRUCIAL", "CRITICAL") or bool(card.get("crucial"))


def choose_model(card, allow_opus=True):
    m = str(card.get("model") or "").lower()
    lane = card.get("lane")
    if m == "haiku" or lane == "HAIKU":
        return "haiku"
    if (lane == "OPUS" or m == "opus") and allow_opus and is_crucial(card) and card.get("approved_by"):
        return "opus"
    return "sonnet"


def max_turns(card):
    t = card.get("est_turns")
    if isinstance(t, int) and not isinstance(t, bool) and t >= 1:
        return math.ceil(t * 1.5)
    return DEFAULT_TURNS


def role_file(card):
    import tasks
    role = tasks.card_role(card)
    return f"MyTradingSys/system/roles/{ROLE_FILES.get(role, 'builder.md')}"


def build_brief(card, slug, worktree):
    return "\n".join([
        f"You are an unattended MTS worker (one card, headless). Work ONLY in {worktree}.",
        "ONE task: the card below. Commit with a body line `Result: <what works now / the number>`, then run "
        f"`python scripts/dev/sync.py ship --release {slug}`. Never deploy, never touch the live tree, no mainnet.",
        f"Read your role file first: {role_file(card)}. Stop and report if blocked.",
        "CARD:", json.dumps(card, indent=1, sort_keys=True, ensure_ascii=False)])


def build_command(brief, model, turns, exe=None):
    return [exe or find_claude(), "-p", brief, "--model", model, "--permission-mode", "auto", "--permission-prompts", "none",
            "--tools", TOOLS, "--strict-mcp-config", "--max-turns", str(turns), "--output-format", "json"]


def parse_result(text):
    """Worker JSON -> flat dict. Never raises: unparseable output is an error result."""
    try:
        d = json.loads(text)
        if isinstance(d, list):   # verbose format: take the last result object
            d = next((x for x in reversed(d) if isinstance(x, dict) and x.get("type") == "result"), {})
        u = d.get("usage") or {}
        return {"is_error": bool(d.get("is_error")) or str(d.get("subtype", "success")).startswith("error"),
                "turns": int(d.get("num_turns") or 0), "cost": float(d.get("total_cost_usd") or 0.0),
                "in": int(u.get("input_tokens") or 0), "cache_w": int(u.get("cache_creation_input_tokens") or 0),
                "cache_r": int(u.get("cache_read_input_tokens") or 0), "out": int(u.get("output_tokens") or 0),
                "result": str(d.get("result") or ""), "session_id": d.get("session_id", "")}
    except (ValueError, TypeError, AttributeError):
        return {"is_error": True, "turns": 0, "cost": 0.0, "in": 0, "cache_w": 0, "cache_r": 0, "out": 0,
                "result": "unparseable output: " + str(text)[:200], "session_id": ""}


def units(row):
    return row.get("in", 0) + 1.25 * row.get("cache_w", 0) + 0.1 * row.get("cache_r", 0) + 5 * row.get("out", 0)


# ---------- ledger / calibration ----------
def append_ledger(row, path=None):
    p = Path(path or LEDGER)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def read_ledger(path=None):
    p = Path(path or LEDGER)
    rows = []
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    except OSError:
        pass
    return rows


def load_calib(path=None):
    try:
        return json.loads(Path(path or CALIB).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def parse_iso(s):
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def week_bounds(reset, now):
    """(start, end) of the weekly window that contains now, given any one reset instant."""
    k = math.floor((now - reset).total_seconds() / WEEK_S)
    end = reset + timedelta(seconds=WEEK_S * (k + 1))
    return end - timedelta(seconds=WEEK_S), end


def default_reset(now):
    mon = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    return mon


def week_units(rows, login, start):
    return sum(units(r) for r in rows if r.get("login") == login and r.get("ts") and parse_iso(r["ts"]) >= start)


def calibrate(login, used, reset=None, now=None, path=None, ledger=None):
    now = now or utcnow()
    cal = load_calib(path)
    rs = parse_iso(reset) if reset else (parse_iso(cal[login]["reset"]) if login in cal and cal[login].get("reset") else default_reset(now))
    start, _ = week_bounds(rs, now)
    u = week_units(read_ledger(ledger), login, start)
    cal[login] = {"used_pct": float(used), "reset": rs.isoformat(), "at": now.isoformat(), "units_at": u}
    p = Path(path or CALIB)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cal, indent=1, sort_keys=True), encoding="utf-8", newline="\n")
    return cal[login]


def pace(login, now=None, rows=None, cal=None):
    """RUN_MODEL section 4. Returns dict(decision run|slow|stop, used_pct, elapsed_pct, units, calibrated)."""
    now = now or utcnow()
    rows = read_ledger() if rows is None else rows
    cal = load_calib() if cal is None else cal
    c = cal.get(login)
    rs = parse_iso(c["reset"]) if c and c.get("reset") else default_reset(now)
    start, end = week_bounds(rs, now)
    elapsed = 100.0 * (now - start).total_seconds() / WEEK_S
    u = week_units(rows, login, start)
    if c and c.get("used_pct") is not None and parse_iso(c["at"]) >= start:
        base, base_u = c["used_pct"], c.get("units_at", 0.0)
        per_pct = (base_u / base) if base > 0 and base_u > 0 else None
        used = base + ((u - base_u) / per_pct if per_pct else 0.0)
        calibrated = True
    else:
        used, calibrated = 0.0, False   # no reading this week: ledger units alone cannot be turned into a share
    decision = "stop" if used > STOP_PCT else ("slow" if used > elapsed else "run")
    return {"decision": decision, "used_pct": round(used, 2), "elapsed_pct": round(elapsed, 2), "units": round(u), "calibrated": calibrated}


# ---------- announcements ----------
def active_stop(repo=None):
    """Ids of ACTIVE STOP/HOLD announcements (same pattern as tasks.active_holds)."""
    try:
        text = ((repo or REPO) / "MyTradingSys" / "system" / "ANNOUNCEMENTS.md").read_text(encoding="utf-8")
    except OSError:
        return set()
    return set(HOLD_ID.findall(text))


# ---------- selection and run ----------
def pick_card(card_id=None, repo=None):
    import tasks
    repo = repo or REPO
    if card_id:
        return tasks.get(repo, card_id)
    cs, _ = tasks.ready_cards(repo)
    cs = [c for c in cs if c.get("lane") in tasks.CODE_LANES]
    held = tasks.open_claims(repo)
    free = [c for c in cs if not tasks.claim_of(c, held)]
    return free[0] if free else None


def sync(*args, cwd=None):
    return subprocess.run([sys.executable, str(HERE / "sync.py"), *args], cwd=str(cwd or REPO), capture_output=True, text=True, timeout=600)


def start_worktree(slug):
    r = sync("start", slug)
    m = re.search(r"^WORKTREE: (.+)$", r.stdout, re.M)
    if m:
        return Path(m.group(1).strip())
    if r.returncode == 0:
        return REPO
    raise RuntimeError("sync start failed: " + (r.stderr or r.stdout)[-300:])


def refresh_tree(repo=None):
    """Bring the runner tree up to date from origin/fast-track the way `sync.py start` does (fetch + merge, never rebase), so a
    card made ready elsewhere is seen. Any failure logs one line and the local cards are used. MTS_RUN_NO_REFRESH=1 skips it."""
    if os.environ.get("MTS_RUN_NO_REFRESH") == "1":
        return
    try:
        import sync as S
        n = S.merge_trunk(repo or REPO)
        print(f"refresh: pulled {n} commit(s) from origin/fast-track")
    except Exception as e:
        print(f"refresh failed, using local cards: {type(e).__name__}: {str(e)[:150]}")


def run_once(card_id=None, dry=False, login=None, timeout=DEFAULT_TIMEOUT, allow_opus=True, runner=None):
    """Returns (status, ledger_row_or_None). status: ok | fail | empty | dry."""
    import tasks
    import sync as S
    login = login or os.environ.get("MTS_LOGIN", "default")
    refresh_tree()
    card = pick_card(card_id)
    if not card:
        return "empty", None
    cid = card["id"]
    slug = S.slugify(cid)
    model = choose_model(card, allow_opus)
    turns = max_turns(card)
    if dry:
        wt = f"<worktree from sync.py start {slug}>"
        cmd = build_command(build_brief(card, slug, wt), model, turns)
        print("COMMAND:", json.dumps(cmd[:1] + cmd[1:2] + ["<brief>"] + cmd[3:]))
        print("ENV removed:", sorted(k for k in os.environ if k not in scrub_env()))
        print("BRIEF:\n" + cmd[2])
        return "dry", None
    c = sync("claim", cid)
    if c.returncode != 0:
        print("claim refused:", (c.stderr or c.stdout)[-200:])
        return "fail", None
    t0 = time.time()
    res = {"is_error": True, "turns": 0, "cost": 0.0, "in": 0, "cache_w": 0, "cache_r": 0, "out": 0, "result": "", "session_id": ""}
    code = -1
    try:
        wt = start_worktree(slug)
        cmd = build_command(build_brief(card, slug, wt), model, turns)
        p = (runner or subprocess.run)(cmd, cwd=str(wt), env=scrub_env(), stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
        code = p.returncode
        res = parse_result(p.stdout)
        if code != 0:
            res["is_error"] = True
    except subprocess.TimeoutExpired:
        res["result"] = f"timeout after {timeout}s"
    except Exception as e:   # claim must not leak on any launcher failure
        res["result"] = f"launcher error: {type(e).__name__}: {e}"
    ok = not res["is_error"]
    row = {"ts": utcnow().isoformat(), "login": login, "host": os.environ.get("COMPUTERNAME", ""), "card": cid, "model": model,
           "turns": res["turns"], "in": res["in"], "cache_w": res["cache_w"], "cache_r": res["cache_r"], "out": res["out"],
           "cost": res["cost"], "wall_s": round(time.time() - t0, 1), "exit": code, "status": "UNVERIFIED" if ok else "FAILED",
           "session_id": res["session_id"], "result": res["result"][:300]}
    append_ledger(row)
    if not ok:
        sync("release", slug)
    return ("ok" if ok else "fail"), row


def guard_tick():
    """Once per cycle: the C: drive guard's hook (once-a-day and low-space runs; stamp file keeps it cheap). Best effort, never raises."""
    try:
        subprocess.run([sys.executable, str(Path(__file__).resolve().parent / "c_drive_guard.py"), "hook"],
                       capture_output=True, timeout=30)
    except Exception:
        pass


def loop(hours, login=None, max_parallel=1, sleep=time.sleep, clock=time.time, runner=None):
    login = login or os.environ.get("MTS_LOGIN", "default")
    end = clock() + hours * 3600
    fails = 0
    while clock() < end:
        if runner is None:
            guard_tick()
        stops = active_stop()
        if stops:
            print("STOP/HOLD active:", ", ".join(sorted(stops)))
            return "stopped"
        pc = pace(login)
        if pc["decision"] == "stop":
            print("pace: stop", pc)
            return "pace-stop"
        status, row = run_once(login=login, allow_opus=(pc["decision"] == "run"), runner=runner)
        if status == "empty":
            if clock() + EMPTY_SLEEP >= end:
                return "empty"
            sleep(EMPTY_SLEEP)
            continue
        fails = 0 if status == "ok" else fails + 1
        if fails >= MAX_FAILS:
            print(f"{MAX_FAILS} failures in a row: stopping")
            return "failures"
        if pc["decision"] == "slow":
            sleep(60)
    return "time"


def summary(rows, week_start=None):
    out = {}
    for r in rows:
        if week_start and parse_iso(r["ts"]) < week_start:
            continue
        k = (r.get("login", "?"), r.get("model", "?"))
        s = out.setdefault(k, {"runs": 0, "turns": 0, "units": 0.0, "cost": 0.0, "fail": 0})
        s["runs"] += 1
        s["turns"] += r.get("turns", 0)
        s["units"] += units(r)
        s["cost"] += r.get("cost", 0.0)
        s["fail"] += r.get("status") == "FAILED"
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="mts_run.py")
    sp = ap.add_subparsers(dest="cmd", required=True)
    o = sp.add_parser("once")
    o.add_argument("--card")
    o.add_argument("--dry-run", action="store_true")
    o.add_argument("--login")
    o.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    lp = sp.add_parser("loop")
    lp.add_argument("--hours", type=float, required=True)
    lp.add_argument("--max-parallel", type=int, default=1)
    lp.add_argument("--login")
    c = sp.add_parser("calibrate")
    c.add_argument("--login", required=True)
    c.add_argument("--used", type=float, required=True)
    c.add_argument("--reset")
    pc = sp.add_parser("pace")
    pc.add_argument("--login", required=True)
    lg = sp.add_parser("ledger")
    lg.add_argument("--week", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "once":
        st, row = run_once(a.card, a.dry_run, a.login, a.timeout)
        if st == "empty":
            print("NO_READY_CARD")
        elif row:
            print(json.dumps(row, indent=1))
        return 0 if st in ("ok", "dry", "empty") else 1
    if a.cmd == "loop":
        print("loop ended:", loop(a.hours, a.login, a.max_parallel))
        return 0
    if a.cmd == "calibrate":
        print(json.dumps(calibrate(a.login, a.used, a.reset), indent=1))
        return 0
    if a.cmd == "pace":
        r = pace(a.login)
        print(f"{a.login}: units this week {r['units']}, used {r['used_pct']}% "
              f"({'calibrated' if r['calibrated'] else 'NOT calibrated: run calibrate'}), week elapsed {r['elapsed_pct']}% -> {r['decision'].upper()}")
        return 0
    if a.cmd == "ledger":
        now = utcnow()
        ws = week_bounds(default_reset(now), now)[0] if a.week else None
        for (lo, m), s in sorted(summary(read_ledger(), ws).items()):
            print(f"{lo}/{m}: runs {s['runs']} fail {s['fail']} turns {s['turns']} units {round(s['units'])} cost ${s['cost']:.3f}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
