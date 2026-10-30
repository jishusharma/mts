"""Status dashboard: `python scripts/dev/status_board.py` prints the operator's whole status as markdown tables, to be pasted inline in chat.

Operator 2026-10-28 (d-status-is-inline-dashboard): "status" means this board, in the chat, no links. Stdlib only. Every section runs in its
own try/except, so one failure prints `NOT_IN_DATA: <why>` and the rest still print. Reads only: git log, task cards, signal lines,
disk_usage, top-level Temp entries (no tree scans). Numbers come from commands run now; what cannot be measured says NOT_IN_DATA.
"""
import functools
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
ND = "NOT_IN_DATA"
STUCK_H = 24
STALE_MIN = 30   # a reading older than this prints as STALE, never as a plain % (operator 2026-10-30: GPT "36%" was 2.3 h old and spent)


def age_text(hours):
    return f"{hours * 60:.0f} min" if hours < 1 else f"{hours:.1f} h"


def aged(value, hours):
    """A number with its age; over STALE_MIN it reads 'STALE <value> (<age> old)'."""
    if hours is None:
        return f"{value} (age {ND})"
    return ("STALE " if hours * 60 > STALE_MIN else "") + f"{value} ({age_text(hours)} old)"


def table(headers, rows):
    """Markdown table lines; cells are stringified, pipes escaped."""
    cell = lambda v: str(v).replace("|", "/").replace("\n", " ")
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return out


def nd(why):
    return f"{ND}: {why}"


def run(cmd, timeout=15, cwd=None):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(cwd or REPO), encoding="utf-8", errors="replace")
    return p.stdout


# ---- pure parsers / formatters (tested with fake inputs) ---------------------------------------------------------------------------

BUDGET_RE = re.compile(r"^(\d{4})Z\s+\S+\s+\[note\]\s+BUDGET login=(\w+) 5h=(\d+)% week=(\d+)%(?: reset=(\S+))?")


def parse_budget(text):
    """Newest BUDGET line per login (by HHMM time, ties: later line) from `mts_signal.py read` text. {login: (hhmm, five, week, reset)}."""
    out, key, day, prev = {}, {}, 0, None
    for ln in text.splitlines():
        t = re.match(r"(\d{4})Z", ln.strip())
        if t:   # lines carry HHMM only: a drop of over 12 h means the file crossed midnight
            mins = int(t.group(1)[:2]) * 60 + int(t.group(1)[2:])
            day += 1 if prev is not None and mins < prev - 720 else 0
            prev = mins
        m = BUDGET_RE.match(ln.strip())
        if m and t and (m.group(2) not in key or (day, mins) >= key[m.group(2)]):   # newest by time, not file order
            key[m.group(2)] = (day, mins)
            out[m.group(2)] = (m.group(1), int(m.group(3)), int(m.group(4)), m.group(5) or "?")
    return out


def hhmm_age_h(hhmm, now):
    """Hours since a signal line's HHMM (UTC): today's time, or yesterday's when that would be in the future."""
    try:
        t = now.replace(hour=int(hhmm[:2]), minute=int(hhmm[2:4]), second=0, microsecond=0)
    except (ValueError, TypeError):
        return None
    if t > now + timedelta(minutes=1):
        t -= timedelta(days=1)
    return (now - t).total_seconds() / 3600


def fmt_budget(budget, closed_today, closed_yday, commits_today, commits_yday, now=None):
    now = now or datetime.now(timezone.utc)
    lines = []
    if budget:
        rows = []
        for k, v in sorted(budget.items()):
            h = hhmm_age_h(v[0], now)
            rows.append([k, aged(f"{v[1]}%", h), aged(f"{v[2]}%", h), v[0][:2] + ":" + v[0][2:] + (f" ({age_text(h)} ago)" if h is not None else ""), v[3]])
        lines += table(["Login", "5h used", "Week used", "Seen (UTC)", "Week resets"], rows)
    else:
        lines.append(nd("no BUDGET lines in the signal read"))
    lines += table(["What it bought", "Today", "Yesterday"], [["Cards closed", closed_today, closed_yday], ["Commits on trunk", commits_today, commits_yday]])
    lines.append("Spend vs output per login: NOT_IN_DATA (cards carry no login; a `closed_by_login` field would measure it).")
    return lines


def per_day(dates, days):
    """[(day, count)] for the given ISO day strings, in the order given."""
    return [(d, sum(1 for x in dates if x == d)) for d in days]


def gate_summary(rows, last=5, gap_s=300):
    """Wall seconds of each ship: rows sorted by utc, a new ship starts after a gap over gap_s; (median, [secs] of the last N) or None."""
    stamps = []
    for r in rows:
        try:
            stamps.append((datetime.fromisoformat(r["utc"].replace("Z", "+00:00")).timestamp(), float(r["secs"])))
        except (KeyError, ValueError, TypeError):
            pass
    ships, prev = [], None
    for ts, secs in sorted(stamps):
        if prev is None or ts - prev > gap_s:
            ships.append(0.0)
        ships[-1] += secs
        prev = ts
    ships = ships[-last:]
    return (statistics.median(ships), [round(x) for x in ships]) if ships else None


def red_minutes(runs, now=None):
    """Minutes the newest finished CI run has been red (since the oldest run of the current failing streak); 0 when green."""
    now = now or datetime.now(timezone.utc)
    first = None
    for r in (r for r in runs if r.get("conclusion") in ("success", "failure", "timed_out", "startup_failure")):
        if r["conclusion"] == "success":
            break
        first = r
    if not first:
        return 0
    return int((now - datetime.fromisoformat(first["created_at"].replace("Z", "+00:00"))).total_seconds() // 60)


def fmt_speed(commit_days, ci_runs, red_min, gate, ships):
    lines = ["Trunk commits per UTC day: " + ", ".join(f"{d[5:]} {n}" for d, n in commit_days)]
    if ci_runs:
        lines.append("CI last 6 (newest first): " + ", ".join(f"{r.get('head_sha', '')[:7]} {r.get('conclusion') or 'running'}" for r in ci_runs[:6])
                     + (f"; red now {red_min} min" if red_min else "; red now 0 min (green)"))
    else:
        lines.append(nd("CI runs unavailable (offline or rate limited)"))
    lines.append(f"Gate wall time, median of last {len(gate[1])} ships: {gate[0]:.0f} s {gate[1]}" if gate else "Gate wall time: " + nd("no gate_timing.jsonl rows"))
    lines.append(ships)
    return lines


def old_hours(utc, now):
    try:
        return (now - datetime.fromisoformat(utc.replace("Z", "+00:00"))).total_seconds() / 3600
    except (ValueError, AttributeError):
        return 0.0


def fmt_value(done_titles, cleanup, stuck, stale_claims):
    lines = table(["Solved today (top 3)"], [[t[:90]] for t in done_titles[:3]]) if done_titles else ["Solved today: none yet"]
    lines += [f"Dedupe/cleanup commits today: {len(cleanup)}" + ("  top 3: " + "; ".join(c[:50] for c in cleanup[:3]) if cleanup else ""),
              f"Stuck: {len(stuck)} active card(s) older than {STUCK_H} h" + ("  " + ", ".join(stuck[:3]) if stuck else ""),
              f"Stale claims (over {STUCK_H} h): {len(stale_claims)}" + ("  " + "; ".join(s[:70] for s in stale_claims[:3]) if stale_claims else "")]
    return lines


CLEAN_RE = re.compile(r"dedupe|dedup|clean-?up|declutter|retire|prune|temp leak", re.I)


def cleanup_commits(subjects):
    return [s for s in subjects if CLEAN_RE.search(s)]


GPT_JSON = "MyTradingSys/system/codex_usage.json"
LANE_JSON = "MyTradingSys/system/lane_state.json"   # lane_health: GPT down for window/limit/credits/auth = spent, whatever the % says
SPENT_REASONS = ("window", "limit", "credits", "auth")
GEM_FACTS = ("Gemini facts on trunk: plan Google AI Pro (MyTradingSys/system/GEMINI_START.md:1); lane CODEX cards only (GEMINI_START.md:5); "
             "Flash models via agy queue (scripts/dev/gemini_queue.py:10); queue logs F:/MTS/gq/*.log live on the NUC, not on trunk (gemini_queue.py:20).")


def _epoch(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def spent_until(d, lane, now):
    """'EXHAUSTED until <reset>' (or 'EXHAUSTED, reset unknown') when codex_usage.json's flag or lane_state.json says GPT is spent, else ''."""
    ts = now.timestamp()
    hits = []
    ex = (d or {}).get("exhausted") or {}
    if ex.get("flag") and (not ex.get("until") or _epoch(ex["until"]) > ts):
        hits.append(ex.get("until") or "")
    ln = lane or {}
    if ln.get("status") == "down" and ln.get("reason") in SPENT_REASONS and (not ln.get("until") or _epoch(ln["until"]) > ts):
        hits.append(ln.get("until") or "")
    if not hits:
        return ""
    known = sorted(h for h in hits if h)
    return f"EXHAUSTED until {known[-1][:16]}Z" if known else "EXHAUSTED, reset unknown"


def _pct(v):
    return f"{v:g}%" if isinstance(v, (int, float)) else ND


def gpt_row(d, now, src, lane=None):
    """Table row for the GPT/Codex account from codex_usage.json content (+ lane_state.json): every % carries its age, a spent lane
    prints EXHAUSTED until <reset>, a 5-hour window whose reset passed since the reading says so instead of the old %."""
    al = d.get("allowance") or {}
    at = d.get("at", "")
    age = old_hours(at, now) if at else None
    when = f"{at[:16]}Z, {age_text(age)} old" + (" STALE" if age * 60 > STALE_MIN else "") if at else ND
    spent = spent_until(d, lane, now)
    if spent:
        return ["GPT (Codex)", al.get("plan") or ND, spent, spent, when, src + (" + " + LANE_JSON if lane and lane.get("status") == "down" else "")]
    five = aged(_pct(al.get("window_used")), age) if at else ND
    if at and 0 < (al.get("window_resets") or 0) <= now.timestamp():
        five = f"window reset since the reading (was {_pct(al.get('window_used'))}, {age_text(age)} old)"
    week = aged(_pct(al.get("week_used")), age) if at else ND
    return ["GPT (Codex)", al.get("plan") or ND, five, week, when, src]


def fmt_gpt_gemini(gpt):
    gem = ["Gemini (Antigravity)", "Google AI Pro", ND, ND, ND, "GEMINI_START.md:1"]
    return table(["Provider", "Account/plan", "5h used", "Week used", "Reading (UTC), age", "Source"], [gpt, gem]) + [
        "Gemini usage: NOT_IN_DATA (no Gemini usage file on trunk: `gemini_queue.py run` writes one <card>.log per job under F:/MTS/gq on the "
        "NUC (gemini_queue.py:20, :99) and nothing reaches trunk, so runs/day cannot be counted here)", GEM_FACTS]


def _tree_and_trunk(rel):
    cands = []
    try:
        cands.append((json.loads((REPO / rel).read_text(encoding="utf-8")), rel + " (tree)"))
    except (OSError, ValueError):
        pass
    try:
        cands.append((json.loads(run(["git", "show", "origin/fast-track:" + rel])), rel + " (origin/fast-track)"))
    except ValueError:
        pass
    return cands


LANE_STAMPS = ("since", "last_error", "last_ok", "resumed", "last_probe")


def newest_gpt(now):
    """codex_usage.json from the tree or origin/fast-track, whichever has the newer `at`; lane_state.json likewise (newest stamp)."""
    cands = _tree_and_trunk(GPT_JSON)
    if not cands:
        raise FileNotFoundError(GPT_JSON)
    d, src = max(cands, key=lambda c: c[0].get("at", ""))
    lanes = _tree_and_trunk(LANE_JSON)
    lane = max(lanes, key=lambda c: max(str(c[0].get(k) or "") for k in LANE_STAMPS))[0] if lanes else None
    return gpt_row(d, now, src, lane)


def sec_gpt_gemini():
    return fmt_gpt_gemini(newest_gpt(datetime.now(timezone.utc)))


def stale_claims(text):
    """['owner: task (Nh)'] from `sync.py claims` lines ending STALE."""
    out = []
    for ln in text.splitlines():
        m = re.match(r"claim (\S+): (\S+) / \S+ - .*?(\d+)h old STALE", ln)
        if m:
            out.append(f"{m.group(2)}: {m.group(1)} ({m.group(3)}h)")
    return out


def count_open(cards, weights=("CRITICAL", "CRUCIAL")):
    openc = [c for c in cards if c.get("state") not in ("done", "dropped")]
    return {w: sum(1 for c in openc if c.get("weight") == w) for w in weights}


def fmt_missing(open_w, parked, raw, blocked):
    return [f"Open CRITICAL {open_w.get('CRITICAL', 0)}, open CRUCIAL {open_w.get('CRUCIAL', 0)}, parked (need review / no tries left) {parked}, raw {raw}, blocked {blocked}"]


def fmt_hygiene(disks, temp_n, mts_run, bundle, trees, strays):
    free = ", ".join(f"{d} {g:.1f} GB" if g is not None else f"{d} {ND}" for d, g in disks)
    return [f"{free}; Temp entries {temp_n}; mts_run_* leftovers {mts_run}; stray processes {strays}",
            f"Worktrees: {trees}", f"VM bundle: {bundle}"]


def fmt_sessions():
    return ["Sessions running/idle/archived: NOT_IN_DATA (coordinator adds)",
            "Compaction count: NOT_IN_DATA (would measure: count compaction events in the session transcript .jsonl)",
            "Sonnet vs Opus value: NOT_IN_DATA (would measure: cards closed per login 5h-% by model)"]


def fmt_asks(asks, high):
    """Asks and HIGH broadcasts still owed a reply (operator 2026-10-30: mandatory reply). asks = `mts_signal.py asks --json`,
    high = `mts_signal.py pending --json`. OVERDUE rows first, each with its age."""
    rows = [("OVERDUE" if a["overdue"] else "open", a["id"], f"{a['from']} -> {a['to']}", a["state"], age_text(a["age_min"] / 60),
             a.get("esc") or "-", a["text"][:60]) for a in asks]
    rows += [("OVERDUE" if h["hours"] * 60 > 120 else "open", h["id"], f"HIGH -> {h['host']}", h["state"], age_text(h["hours"]), "-",
              (h.get("note") or "")[:60]) for h in high]
    if not rows:
        return ["No ask or HIGH broadcast waits for a reply."]
    rows.sort(key=lambda r: r[0] != "OVERDUE")
    n = sum(1 for r in rows if r[0] == "OVERDUE")
    return [f"{n} OVERDUE of {len(rows)} waiting"] + table(["", "id", "who", "state", "age", "escalated to", "text"], rows)


SUP_IDLE_MIN = 60     # bug-supervisor-idles-after-wake-retired (card: 60 min): READY work and no dispatch/worker this long = RED
BUDGET_IDLE_MODES = ("STOP", "SUPERVISOR-ONLY")   # the budget itself says no Claude worker: idle by design, not RED (OURS)
NON_CLAUDE_LANES = ("CODEX", "GEMINI", "OPUS")    # other vendors; OPUS only when the operator names it (OURS)
HB_LOGIN_RE = re.compile(r"\bBUDGET login=(\w+)\b")
HB_HOURS = 24


def claude_ready(cards):
    """READY cards a Supervisor dispatches to a Claude worker on its own: not CODEX/GEMINI, not OPUS (operator names it), not DSA-*
    (run-and-report). Cards carry no login, so every login sees the same fleet-wide count (OURS)."""
    lane = lambda c: str(c.get("lane", "")).upper()
    return sum(1 for c in cards if c.get("state") == "ready" and lane(c) not in NON_CLAUDE_LANES and not lane(c).startswith("DSA"))


def beats_from_rows(rows, now, hours=HB_HOURS):
    """[(utc datetime, text)] of the signal records (mts_signal.load) in the last `hours` that are BUDGET lines."""
    out = []
    for r in rows:
        try:
            t = datetime.strptime(str(r.get("t", "")), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if "BUDGET login=" in str(r.get("text", "")) and now - timedelta(hours=hours) <= t <= now + timedelta(minutes=5):
            out.append((t, str(r["text"])))
    return out


def supervisor_rows(beats, ready_n, now, idle_min=SUP_IDLE_MIN):
    """Per login from Supervisor heartbeats [(utc datetime, text)] (BUDGET lines carrying sup=; plain budget lines are skipped):
    the newest mode and its age (a later beat replaces ENDED), last dispatch (a beat whose run rose over the previous one, or the
    first with run > 0), last worker seen (newest run > 0), idle minutes since that (else since the login's first beat), and
    red = READY Claude work and idle >= idle_min outside a budget STOP / SUPERVISOR-ONLY."""
    per = {}
    for t, x in sorted(beats, key=lambda b: b[0]):
        m = HB_LOGIN_RE.search(x)
        if not m or " sup=" not in x or t > now + timedelta(minutes=5):
            continue
        kv = dict(re.findall(r"(\w+)=(\S+)", x))
        run_n = int(kv["run"]) if str(kv.get("run", "")).isdigit() else 0
        r = per.setdefault(m.group(1), {"first": t, "prev": None, "last_dispatch": None, "last_worker": None})
        if run_n > 0 and (r["prev"] is None or run_n > r["prev"]):
            r["last_dispatch"] = t
        if run_n > 0:
            r["last_worker"] = t
        r.update(prev=run_n, mode=kv.get("mode", "?"), mode_at=t)
    out = []
    for lg, r in sorted(per.items()):
        idle = int((now - (r["last_worker"] or r["first"])).total_seconds() // 60)
        out.append({"login": lg, "mode": r["mode"], "mode_age_min": int((now - r["mode_at"]).total_seconds() // 60),
                    "last_dispatch": r["last_dispatch"], "last_worker": r["last_worker"], "idle_min": idle,
                    "red": ready_n > 0 and idle >= idle_min and r["mode"] not in BUDGET_IDLE_MODES})
    return out


def fmt_supervisors(rows, ready_n, now):
    """Per-login table (mode, last dispatch, last worker, idle) plus one RED line per login idle with ready work."""
    if not rows:
        return [nd(f"no Supervisor heartbeat in the last {HB_HOURS} h of signals")] + (
            [f"RED idle with ready work: no Supervisor of any login, {ready_n} READY Claude card(s)"] if ready_n else [])
    ago = lambda t: age_text((now - t).total_seconds() / 3600) + " ago" if t else "none seen"
    lines = table(["Login", "Mode (age)", "Last dispatch", "Last worker seen", "Idle"],
                  [[r["login"], f"{r['mode']} ({age_text(r['mode_age_min'] / 60)} old)", ago(r["last_dispatch"]), ago(r["last_worker"]),
                    age_text(r["idle_min"] / 60)] for r in rows])
    red = [r for r in rows if r["red"]]
    lines += [f"RED idle with ready work: login {r['login']} idle {r['idle_min']} min (no dispatch or worker; mode {r['mode']}), "
              f"{ready_n} READY Claude card(s)" for r in red]
    return lines + ([] if red else [f"No login idle with ready work ({ready_n} READY Claude card(s); RED after {SUP_IDLE_MIN} min)"])


def result_line(budget, red_min, open_w, failures, idle=()):
    wk = max((v[2] for v in budget.values()), default=None)
    bits = [f"week budget up to {wk}%" if wk is not None else "budget " + ND, f"CI red {red_min} min" if red_min else "CI green",
            f"{open_w.get('CRITICAL', 0) + open_w.get('CRUCIAL', 0)} CRITICAL/CRUCIAL cards open"]
    if idle:
        bits.append("RED idle with ready work: login " + ", ".join(idle))
    if failures:
        bits.append(f"{failures} section(s) NOT_IN_DATA")
    return "**Status: " + "; ".join(bits) + "**"


# ---- collectors (touch the machine) ------------------------------------------------------------------------------------------------

@functools.lru_cache(maxsize=None)
def signal_text():
    return run([sys.executable, str(HERE / "mts_signal.py"), "read"], 20)


@functools.lru_cache(maxsize=None)
def ci_runs():
    import ci_watch
    return ci_watch.fetch()


@functools.lru_cache(maxsize=None)
def cards():
    out = []
    for f in (REPO / "MyTradingSys" / "system" / "tasks").glob("*.json"):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass
    return out


def utc_day(offset=0):
    return (datetime.now(timezone.utc) + timedelta(days=offset)).strftime("%Y-%m-%d")


def parse_commit_utc_day(iso_ts: str) -> str:
    """Parse an offset-bearing git ISO timestamp (%cI) and return YYYY-MM-DD in UTC."""
    try:
        dt = datetime.fromisoformat(iso_ts.strip())
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return ""


@functools.lru_cache(maxsize=None)
def git_days():
    lines = run(["git", "log", "origin/fast-track", "--no-merges", "--since=9.days", "--format=%cI"], 30).splitlines()
    days = []
    for ln in lines:
        d = parse_commit_utc_day(ln)
        if d:
            days.append(d)
    return days


def common_dir():
    p = Path(run(["git", "rev-parse", "--git-common-dir"]).strip() or ".git")
    return str(p if p.is_absolute() else REPO / p)


def sec_budget():
    cs, t, y, d = cards(), utc_day(), utc_day(-1), git_days()
    closed = [str(c.get("closed", ""))[:10] for c in cs if c.get("state") == "done"]
    return fmt_budget(parse_budget(signal_text()), closed.count(t), closed.count(y), d.count(t), d.count(y))


def sec_speed():
    runs = []
    try:
        runs = ci_runs()
    except Exception:
        pass
    rows = []
    for base in (REPO, Path(common_dir()).resolve().parent):
        p = base / "runtime_data" / "gate_timing.jsonl"
        if p.exists():
            for ln in p.read_text(encoding="utf-8", errors="replace").splitlines()[-400:]:
                try:
                    rows.append(json.loads(ln))
                except ValueError:
                    pass
            break
    import host_health as hh
    now = time.time()
    ships = [p for p in hh.snapshot() if "sync.py" in p["cmd"] and " ship" in p["cmd"] and p["name"].lower().startswith("python")]
    stalled = [p for p in ships if p["created"] and now - p["created"] > 1800]
    return fmt_speed(per_day(git_days(), [utc_day(-i) for i in range(6)]), runs, red_minutes(runs), gate_summary(rows),
                     f"Ships running now: {len(ships)}; stalled over 30 min: {len(stalled)}")


def sec_value():
    now = datetime.now(timezone.utc)
    t_utc = utc_day()
    done = sorted((c for c in cards() if c.get("state") == "done" and str(c.get("closed", ""))[:10] == t_utc), key=lambda c: c.get("closed", ""), reverse=True)
    raw_log = run(["git", "log", "origin/fast-track", "--no-merges", "--since=2.days", "--format=%cI %s"], 30).splitlines()
    subj = []
    for ln in raw_log:
        if not ln.strip():
            continue
        parts = ln.strip().split(" ", 1)
        if parse_commit_utc_day(parts[0]) == t_utc:
            subj.append(parts[1] if len(parts) > 1 else "")
    clean = cleanup_commits(subj)
    stuck = [c["id"] for c in cards() if c.get("state") == "active" and old_hours(c.get("taken", ""), now) > STUCK_H]
    stale = stale_claims(run([sys.executable, str(HERE / "sync.py"), "claims"], 30))
    return fmt_value([c.get("title", c["id"]) for c in done], clean, stuck, stale)


@functools.lru_cache(maxsize=None)
def supervisors():
    """(rows, ready_n, now) from the signals branch (fetched) and the tree's cards."""
    import mts_signal
    h = mts_signal.ensure(REPO)
    if h is None:
        raise RuntimeError("no signals clone")
    now = datetime.now(timezone.utc)
    ready = claude_ready(cards())
    return supervisor_rows(beats_from_rows(mts_signal.load(h), now), ready, now), ready, now


def sec_supervisors():
    return fmt_supervisors(*supervisors())


def sec_missing():
    cs = cards()
    m = re.search(r"parked=(\d+)", run([sys.executable, str(HERE / "tasks.py"), "status"], 20))
    return fmt_missing(count_open(cs), m.group(1) if m else nd("tasks.py status has no parked="),
                       sum(1 for c in cs if c.get("state") == "raw"), sum(1 for c in cs if c.get("state") == "blocked"))


def sec_asks():
    load = lambda *a: json.loads(run([sys.executable, str(HERE / "mts_signal.py"), *a, "--json"], 30) or "[]")
    return fmt_asks(load("asks"), load("pending"))


def sec_hygiene():
    disks = []
    for d in ("C:\\", "D:\\", "F:\\"):
        try:
            disks.append((d[:2] + " free", shutil.disk_usage(d).free / 1e9))
        except OSError:
            disks.append((d[:2] + " free", None))
    temp = Path(os.environ.get("TEMP") or os.environ.get("TMP") or "")
    names = os.listdir(temp) if temp.is_dir() else []
    vm = Path(os.environ.get("LOCALAPPDATA", "")) / "Claude-Data" / "claude_pzs8sxrjxfjjc" / "vm_bundles"
    if vm.exists() or vm.is_symlink():
        real = os.path.realpath(vm)
        bundle = f"{vm} (real folder, not a junction)" if os.path.normcase(real) == os.path.normcase(str(vm)) else f"junction {vm} -> {real}"
    else:
        bundle = nd("vm_bundles path not present")
    n_trees = len([ln for ln in run(["git", "worktree", "list"]).splitlines() if ln.strip()])
    report = Path(common_dir()).resolve().parent / "Dumps" / "worktree_report.txt"
    try:
        m = re.search(r"worktree report (\S+ \S+).*?: (\d+)", report.read_text(encoding="utf-8"), re.S)
        trees = f"{n_trees} ({m.group(2)} with unshipped work, report {m.group(1)})" if m else nd("worktree_report.txt unparsed")
    except OSError:
        trees = f"{n_trees} (unshipped count {ND}: no Dumps/worktree_report.txt)"
    try:
        import c_drive_guard
        m2 = re.match(r"(\d+) KILL", c_drive_guard.procs_summary())
        strays = f"{m2.group(1)} kill candidate(s)" if m2 else nd("procs_summary unavailable")
    except Exception as e:
        strays = nd(type(e).__name__)
    return fmt_hygiene(disks, len(names), sum(1 for n in names if n.startswith("mts_run_")), bundle, trees, strays)


SECTIONS = [("Resources: budget and what it bought", sec_budget), ("Speed and health", sec_speed),
            ("Supervisors: mode, last dispatch, idle with ready work", sec_supervisors), ("Value added", sec_value),
            ("GPT and Gemini", sec_gpt_gemini), ("Still missing", sec_missing), ("Asks waiting for a reply", sec_asks), ("Hygiene", sec_hygiene)]


def build(sections=None):
    """(failure count, body lines); a failing section prints NOT_IN_DATA and the rest still run."""
    body, fails = [], 0
    for title, fn in (SECTIONS if sections is None else sections):
        try:
            lines = fn()
        except Exception as e:
            fails += 1
            lines = [nd(f"{type(e).__name__}: {str(e)[:100]}")]
        body += [f"**{title}**"] + lines
    return fails, body + ["**Sessions and measurement**"] + fmt_sessions()


def main():
    t0 = time.time()
    fails, body = build()
    try:
        red = red_minutes(ci_runs())
    except Exception:
        red = 0
    try:
        idle = [r["login"] for r in supervisors()[0] if r["red"]]
    except Exception:
        idle = []
    print(result_line(parse_budget(signal_text()), red, count_open(cards()), fails, idle))
    print("\n".join(body))
    print(f"\n(board built in {time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
