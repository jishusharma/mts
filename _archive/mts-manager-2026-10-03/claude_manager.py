"""Claude manager helper: intake, dedup, budget gate, route, brief, launch, close.
One process, one routing decision, then exit (CLAUDE_MANAGER_SPEC.md). No model call except the
Haiku intake (and the children). Usage: python claude_manager.py go|status|resume|stop|usage ...
Never touches execution/ or layers/alerts/. State lives in Dumps/manager/ (gitignored)."""
import argparse, datetime, json, os, pathlib, re, subprocess, sys

ROOT = pathlib.Path(os.environ.get("MTS_ROOT") or pathlib.Path(__file__).resolve().parents[2])
CAP = 3  # hard cap on children per go call
TYPES = ("fix", "audit", "extraction", "backtest", "question", "status", "build", "docs", "safety")

# task type -> (tier, effort); spec ROUTING TABLE. fix/audit are not in the table: Sonnet/medium (DEFAULT).
ROUTE = {
    "question": ("haiku", "low"), "status": ("haiku", "low"),
    "extraction": ("sonnet", "medium"), "docs": ("sonnet", "medium"),
    "build": ("sonnet", "medium"), "safety": ("opus", "high"),
    "backtest": ("sonnet", "medium"), "fix": ("sonnet", "medium"), "audit": ("sonnet", "medium"),
}
KEYWORDS = [("safety", r"safety|halt|kill|stop.?loss|execution/|position_manager"),
            ("extraction", r"extract|transcript"), ("backtest", r"backtest"),
            ("docs", r"\bdocs?\b|spec\b|readme"), ("audit", r"audit|review"),
            ("build", r"build|implement|add |create"), ("fix", r"fix|bug|broken|error"),
            ("status", r"status|state"), ("question", r"\?|what|why|how|which")]


def paths(root=None):
    r = pathlib.Path(root) if root else ROOT
    d = r / "Dumps" / "manager"
    return dict(root=r, dir=d, usage=d / "usage.json", queue=d / "queue.json", running=d / "running.json",
                model_log=d / "model_log.jsonl",
                handoff=d / "handoff", sessions=r / "MyTradingSys" / "system" / "sessions",
                log=r / "MyTradingSys" / "research" / "fast_track_2026-09-27" / "SUPERVISOR_LOG.md",
                inboxes=[r / "Dumps" / "operator" / "inbox", r / "MyTradingSys" / "system" / "CLOUD_INBOX.md",
                         r / "MyTradingSys" / "research" / "fast_track_2026-09-27" / "SUPERVISOR_INBOX.md"])


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def _rw(p, default):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _w(p, obj):
    p = pathlib.Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1), encoding="utf-8", newline="\n")


# ---- 1. intake -------------------------------------------------------------------------------
def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:20].strip("-") or "task"


def keyword_intake(task):
    low = task.lower()
    t = next((k for k, rx in KEYWORDS if re.search(rx, low)), "question")
    return {"type": t, "slug": slugify(task), "split": []}


def intake(task, haiku=None):
    """Haiku sorts the request. haiku(prompt)->str JSON. Any failure falls back to keywords (fail to Sonnet default)."""
    if haiku is None:
        haiku = _call_haiku
    prompt = ("Classify this task. Reply ONLY JSON {\"type\":one of %s,\"slug\":kebab<=20 chars,"
              "\"split\":[] or list of up to 3 independent sub-task strings}. Task: %s" % (list(TYPES), task))
    try:
        m = re.search(r"\{.*\}", haiku(prompt), re.S)
        o = json.loads(m.group(0))
        if o.get("type") not in TYPES:
            raise ValueError("bad type")
        return {"type": o["type"], "slug": slugify(str(o.get("slug") or task)),
                "split": [str(x) for x in (o.get("split") or [])]}
    except Exception:
        return keyword_intake(task)


def _call_haiku(prompt):
    r = subprocess.run(["claude", "-p", "--model", "haiku"], input=prompt, capture_output=True, text=True, timeout=120)
    if r.returncode:
        raise RuntimeError(r.stderr[:200])
    return r.stdout


# ---- 2. dedup --------------------------------------------------------------------------------
def dedup(slug, p):
    """Return path of an OPEN session record (or inbox entry) mentioning the slug, else None.
    Closed records are ignored so a failed task can be retried (fix 2026-10-01)."""
    if p["sessions"].is_dir():
        for f in sorted(p["sessions"].glob("*.md")):
            if not f.name.startswith("MTS-"):
                continue
            if slug in f.name.lower():
                try:
                    if "status: open" in f.read_text(encoding="utf-8", errors="ignore"):
                        return f
                except OSError:
                    pass
    for ib in p["inboxes"]:
        files = [ib] if ib.is_file() else (sorted(ib.glob("*")) if ib.is_dir() else [])
        for f in files:
            try:
                if slug in f.read_text(encoding="utf-8", errors="ignore").lower():
                    return f
            except OSError:
                pass
    return None


# ---- 3. budget gate (SURFACE_POLICY sec 3: 70/85/95) -----------------------------------------
def tier_of(pct):
    return "hold" if pct >= 95 else "85" if pct >= 85 else "70" if pct >= 70 else "ok"


def read_pct(p, today=None):
    """Operator-entered weekly percent (fallback; spec open question 1). Stale (not today) or missing -> None."""
    u = _rw(p["usage"], {})
    today = today or now().strftime("%Y-%m-%d")
    return u["percent"] if u.get("date") == today and isinstance(u.get("percent"), (int, float)) else None


def gate(pct, ptype, tier):
    """Return (allowed, tier_name, reason). Unknown usage fails closed (queue), per 'safety checks fail closed'."""
    if pct is None:
        return False, "unknown", "no usage entered today: run  mts-manager usage <percent>"
    t = tier_of(pct)
    if t == "hold":
        return False, t, "usage %s%% >= 95%%: queued" % pct
    if t in ("70", "85") and ptype != "safety" and tier == "opus":
        return False, t, "Opus only for safety diffs at >=70%"
    if t in ("85",) and tier == "sonnet" and ptype == "build":
        return False, t, "no Sonnet builders at >=85%"
    return True, t, ""


# ---- 4. route + spawn rules ------------------------------------------------------------------
def route(ptype):
    return ROUTE[ptype]


def plan_children(task, o, tname):
    """Default one child. Split only if intake split >=2 pieces, not safety, tier below 85. Cap 3."""
    parts = o["split"]
    if len(parts) >= 2 and o["type"] != "safety" and tname not in ("85", "hold"):
        return parts[:CAP]
    return [task]


# ---- 5. brief --------------------------------------------------------------------------------
def brief(task, ptype, model, effort, sid, files=()):
    """<=20 lines. File ranges come from the task text if the operator wrote them (path:a-b); else none are invented."""
    refs = list(files) or re.findall(r"[\w./\\-]+\.\w+(?::\d+(?:-\d+)?)?", task)
    lines = ["SESSION " + sid, "TASK (%s, %s/%s): %s" % (ptype, model, effort, task.strip().replace("\n", " ")[:400]),
             "FILES (read only these, by line range; nothing else at start): " + (", ".join(refs[:6]) or "none named - ask before reading"),
             "GATES: python scripts/dev/run_all_tests.py --quick; new tests must fail pre-change.",
             "RULES: branch per session; never commit to master; no push/merge/rebase/reset unless the harness says so;",
             "testnet only; never read .secrets/.env/keys; do not touch execution/ or layers/alerts/ live files;",
             "no subagents; one task, then exit; every parameter needs a transcript source or it does not exist.",
             "END: report one line: what ran, files changed, tests."]
    assert len(lines) <= 20
    return "\n".join(lines)


def session_id(slug, ptype, surf="CLI"):
    role = {"fix": "BLD", "build": "BLD", "audit": "ANA", "extraction": "EXT", "backtest": "ANA", "docs": "BLD",
            "safety": "BLD", "question": "ASK", "status": "MON"}[ptype]
    return "MTS-%s-%s-%s-%s" % (now().strftime("%Y-%m-%d-%H%MZ"), surf, role, slug[:20])


# ---- 6. launch -------------------------------------------------------------------------------
def launch(model, text, timeout=1800, runner=None, on_start=None):
    """claude -p, brief on stdin. Effort stated in the brief; ceiling = wall-clock timeout. on_start(pid) fires
    the moment the child starts so mstop can find it (2026-10-01 fix)."""
    cmd = ["claude", "-p", "--model", model, "--permission-mode", "acceptEdits"]
    if runner is not None:
        if on_start:
            on_start(None)
        try:
            r = runner(cmd, input=text, capture_output=True, text=True, timeout=timeout)
            return r.returncode, (r.stdout or "")[-2000:]
        except subprocess.TimeoutExpired:
            return 124, "timeout"
        except FileNotFoundError:
            return 127, "claude CLI not on PATH"
    try:
        pr = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    except FileNotFoundError:
        return 127, "claude CLI not on PATH"
    if on_start:
        on_start(pr.pid)
    try:
        out, _ = pr.communicate(input=text, timeout=timeout)
        return pr.returncode, (out or "")[-2000:]
    except subprocess.TimeoutExpired:
        pr.kill()
        out, _ = pr.communicate()
        return 124, "timeout"


# ---- 7. close --------------------------------------------------------------------------------
def open_record(p, sid, ptype, tier, task):
    p["sessions"].mkdir(parents=True, exist_ok=True)
    f = p["sessions"] / (sid + ".md")
    f.write_text("# %s\nstatus: open\nstarted: %s\ntype: %s\ntier: %s\ntask: %s\nowner: mts-manager\n" % (
        sid, now().isoformat(timespec="seconds"), ptype, tier, task.replace("\n", " ")[:200]), encoding="utf-8", newline="\n")
    return f


def close_record(p, sid, rc, tail):
    f = p["sessions"] / (sid + ".md")
    txt = f.read_text(encoding="utf-8") if f.exists() else "# %s\n" % sid
    new_status = "status: staged" if rc == "staged" else "status: closed rc=%s" % rc
    txt = txt.replace("status: open", new_status)
    f.write_text(txt + "ended: %s\nresult: %s\n" % (now().isoformat(timespec="seconds"), tail.strip().replace("\n", " ")[:300]),
                 encoding="utf-8", newline="\n")


def log_line(p, sid, ptype, model, rc):
    p["log"].parent.mkdir(parents=True, exist_ok=True)
    with open(p["log"], "a", encoding="utf-8", newline="\n") as f:
        f.write("\n## %s mts-manager\n- %s: %s via %s, rc=%s\n" % (now().strftime("%Y-%m-%d %H:%M UTC"), sid, ptype, model, rc))


def model_log_line(p, sid, ptype, tier, rc):
    p["model_log"].parent.mkdir(parents=True, exist_ok=True)
    rec = {"ts": now().isoformat(timespec="seconds"), "sid": sid, "type": ptype, "tier": tier, "rc": str(rc)}
    with open(p["model_log"], "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec) + "\n")


def refresh_status(p):
    s = p["root"] / "scripts" / "dev" / "make_status.py"
    if s.exists():
        subprocess.run([sys.executable, str(s)], cwd=str(p["root"]), capture_output=True, timeout=300,
                       encoding="utf-8", errors="replace")


# ---- today spend (primary: local transcript totals; tokens only - no price table is sourced) ---
def today_tokens(home=None):
    base = pathlib.Path(home) if home else pathlib.Path.home() / ".claude" / "projects"
    day, tot = now().strftime("%Y-%m-%d"), 0
    for f in base.rglob("*.jsonl") if base.is_dir() else []:
        try:
            for ln in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                if day not in ln or '"usage"' not in ln:
                    continue
                u = (json.loads(ln).get("message") or {}).get("usage") or {}
                tot += sum(int(u.get(k) or 0) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens"))
        except (OSError, ValueError, AttributeError):
            pass
    return tot


# ---- commands --------------------------------------------------------------------------------
def cmd_go(task, root=None, haiku=None, runner=None, transcripts=None):
    p = paths(root); o = intake(task, haiku)
    hit = dedup(o["slug"], p)
    if hit:
        return "resume-existing: %s (%s) - not launched" % (o["slug"], hit.name)
    tier, effort = route(o["type"])
    pct = read_pct(p)
    ok, tname, why = gate(pct, o["type"], tier)
    if not ok:
        q = _rw(p["queue"], []); q.append({"task": task, "slug": o["slug"], "type": o["type"], "at": now().isoformat(timespec="seconds")})
        _w(p["queue"], q)
        return "QUEUED %s (%s); %d in queue" % (o["slug"], why, len(q))
    kids = plan_children(task, o, tname)
    out, run = [], _rw(p["running"], {})
    for i, sub in enumerate(kids):
        slug = o["slug"] if len(kids) == 1 else "%s-%d" % (o["slug"][:17], i + 1)
        sid = session_id(slug, o["type"]); text = brief(sub, o["type"], tier, effort, sid)
        open_record(p, sid, o["type"], tier, sub)
        run[sid] = {"model": tier, "pid": None}; _w(p["running"], run)
        def _on_start(pid, _sid=sid):
            _r = _rw(p["running"], {}); _r[_sid] = {"model": tier, "pid": pid}; _w(p["running"], _r)
        rc, tail = launch(tier, text, runner=runner, on_start=_on_start)
        _r = _rw(p["running"], {}); _r.pop(sid, None); _w(p["running"], _r)
        close_record(p, sid, rc, tail); log_line(p, sid, o["type"], tier, rc); model_log_line(p, sid, o["type"], tier, rc)
        out.append("%s %s rc=%s" % (sid, tier, rc))
    if not transcripts == "skip":
        refresh_status(p)
    return "ran %d child(ren): %s | tokens today %d" % (len(kids), "; ".join(out), today_tokens(transcripts))


def cmd_status(root=None, transcripts=None):
    p = paths(root); pct = read_pct(p)
    opens = [f.name for f in sorted(p["sessions"].glob("MTS-*.md")) if "status: open" in f.read_text(encoding="utf-8", errors="ignore")] if p["sessions"].is_dir() else []
    q = _rw(p["queue"], [])
    last = "none"
    if p["model_log"].exists():
        rows = p["model_log"].read_text(encoding="utf-8").strip().splitlines()
        if rows:
            try:
                r = json.loads(rows[-1]); last = "%s %s" % (r.get("tier"), r.get("sid"))
            except ValueError:
                pass
    return "open sessions: %s | tokens today: %d | usage: %s | tier: %s | queued: %d | last: %s" % (
        opens or "none", today_tokens(transcripts), "unknown (enter: usage <pct>)" if pct is None else "%s%%" % pct,
        "unknown" if pct is None else tier_of(pct), len(q), last)


def cmd_resume(root=None, **kw):
    p = paths(root); q = _rw(p["queue"], [])
    pct = read_pct(p)
    if pct is None or pct >= 95:
        return "not released: usage %s (need entry today and <95%%); %d still queued" % ("unknown" if pct is None else "%s%%" % pct, len(q))
    _w(p["queue"], [])
    res, keep = [], []
    for it in q:
        out = cmd_go(it["task"], root=root, **kw)
        res.append(out)
        if out.startswith("resume-existing") or out.startswith("QUEUED"):
            keep.append(it)  # do not lose a task that was already open or re-gated
    if keep:
        _w(p["queue"], _rw(p["queue"], []) + keep)
    return "released %d, kept %d: %s" % (len(q) - len(keep), len(keep), " | ".join(res))


def cmd_stop(slug, root=None):
    p = paths(root); n = 0
    for sid, info in _rw(p["running"], {}).items():
        if slug in sid and info.get("pid"):
            try:
                os.kill(info["pid"], 15); n += 1
            except OSError:
                pass
    return "stopped %d child(ren) matching %s" % (n, slug)


def cmd_usage(pct, root=None):
    _w(paths(root)["usage"], {"date": now().strftime("%Y-%m-%d"), "percent": float(pct)})
    return "usage %s%% recorded for today -> tier %s" % (pct, tier_of(float(pct)))


def main(argv=None):
    a = argparse.ArgumentParser(); a.add_argument("verb", choices=["go", "status", "resume", "stop", "usage"])
    a.add_argument("arg", nargs="?", default="")
    n = a.parse_args(argv)
    if n.verb in ("go", "stop", "usage") and not n.arg:
        a.error("%s needs an argument" % n.verb)
    print({"go": lambda: cmd_go(n.arg), "status": cmd_status, "resume": cmd_resume,
           "stop": lambda: cmd_stop(n.arg), "usage": lambda: cmd_usage(n.arg)}[n.verb]())


if __name__ == "__main__":
    main()
